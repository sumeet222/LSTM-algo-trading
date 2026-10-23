"""Research-critical P019B action, quarantine and causal mask oracles."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_action_masks import full_window, load_hours, no_boundary_crossing, origin_masks
from lstm_data.hf1m_action_source import (
    NAMESPACE,
    adjust_prices,
    derive_month,
    event_dispositions,
    price_factors,
    publish_json,
    publish_table,
)
from lstm_data.hf_minute_long_qa import calendar_frame


def facts():
    return json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]


def minute_fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start = pd.Timestamp("2020-11-02T14:30Z")
    times = pd.date_range(start, periods=60, freq="min")
    rows, originals = [], []
    for symbol in SYMBOLS:
        values = 100 + np.arange(60) / 100
        rows.append(
            pd.DataFrame(
                {
                    "ticker": symbol,
                    "timestamp": times,
                    "open": values,
                    "high": values + 0.02,
                    "low": values - 0.02,
                    "close": values,
                    "volume": 100.0,
                    "is_rth": True,
                }
            )
        )
        originals.append(
            {
                "ticker": symbol,
                "session_date_et": "2020-11-02",
                "hour_id": symbol + ":2020-11-02:0",
                "hour_start_utc": start,
                "hour_end_utc": start + pd.Timedelta(hours=1),
                "expected_minutes": 60,
                "genuine_minutes": 60,
                "is_stub": False,
                "open": 100.0,
                "close": 100.59,
                "high": 100.61,
                "low": 99.98,
                "volume": 6000.0,
                "observed_volume": 6000.0,
                "absent_minutes": 0,
                "ambiguous_minutes": 0,
                "action_uncertainty": False,
                "quality_tier": "STRICT_GENUINE",
            }
        )
    original = pd.DataFrame(originals)
    sensitivity = original[["hour_id"]].assign(filled_cap5=0, filled_cap2=0)
    return pd.concat(rows, ignore_index=True), original, sensitivity


def test_split_composition_asof_and_no_double_adjustment():
    dates = pd.Series(["2013-01-02", "2015-01-02", "2021-01-04"])
    np.testing.assert_allclose(price_factors("AAPL", dates, facts()), [1 / 28, 1 / 4, 1])
    np.testing.assert_allclose(price_factors("AAPL", dates, facts(), "2015-01-02"), [1 / 7, 1, 1])
    frame = pd.DataFrame(
        {
            "ticker": "AAPL",
            "timestamp": pd.to_datetime(dates, utc=True),
            "open": 280.0,
            "high": 300.0,
            "low": 270.0,
            "close": 290.0,
            "volume": [0.0, 100.0, 200.0],
            "is_rth": True,
        }
    )
    adjusted = adjust_prices(frame, facts())
    assert adjusted.open.iloc[0] == 10
    np.testing.assert_array_equal(adjusted.volume, frame.volume)
    pd.testing.assert_frame_equal(adjust_prices(adjusted, facts()), adjusted)
    assert "price_adjustment_version" not in frame


@pytest.mark.parametrize(
    "ticker,date,n",
    [
        ("KO", "2012-08-13", 2),
        ("MA", "2014-01-22", 10),
        ("AAPL", "2014-06-09", 7),
        ("SBUX", "2015-04-09", 2),
        ("AAPL", "2020-08-31", 4),
        ("TSLA", "2020-08-31", 5),
        ("AMZN", "2022-06-06", 20),
        ("TSLA", "2022-08-25", 3),
        ("AVGO", "2024-07-15", 10),
    ],
)
def test_each_verified_split_factor_direction(ticker, date, n):
    before = str((pd.Timestamp(date) - pd.Timedelta(days=1)).date())
    factors = price_factors(ticker, pd.Series([before, date]), facts())
    assert factors[1] / factors[0] == pytest.approx(n)


def test_spinoff_never_becomes_invented_split_factor():
    np.testing.assert_array_equal(
        price_factors("COP", pd.Series(["2012-04-30", "2012-05-01"]), facts()), [1, 1]
    )
    basis = np.array([["pre"], ["post"], ["post"]])
    assert not no_boundary_crossing(basis, np.array([0]), np.array([1]))[0, 0]
    assert no_boundary_crossing(basis, np.array([1]), np.array([2]))[0, 0]


def test_high_quarantine_keeps_independent_close_and_genuine_volume_only():
    canonical, original, sensitivity = minute_fixture()
    key = canonical.ticker.eq("AAPL") & canonical.timestamp.eq(pd.Timestamp("2020-11-02T14:35Z"))
    canonical.loc[key, "high"] = 1000000
    event = {
        "event_id": "SYNTHETIC",
        "ticker": "AAPL",
        "timestamp_utc": "2020-11-02T14:35Z",
        "disposition": "UNVERIFIED_RTH_LOCAL_QUARANTINE",
    }
    output, safe, receipt = derive_month(
        canonical, original, pd.DataFrame(), sensitivity, "2020-11", facts(), [event]
    )
    row = output.loc[output.ticker.eq("AAPL")].iloc[0]
    assert pd.isna(row.high) and pd.isna(row.low)
    assert row.genuine_close and row.close == 100.59
    assert row.observed_volume == 5900 and not row.observed_volume_complete
    assert row.quarantine_count == 1 and row.proxy_count == 0
    assert safe.loc[safe.ticker.eq("AAPL"), "high"].max() < 101
    assert receipt["observed_volume_conserved"]


def test_no_eh_or_previous_session_input_can_supply_an_open():
    canonical, original, sensitivity = minute_fixture()
    original.loc[original.ticker.eq("AAPL"), ["genuine_minutes", "volume", "observed_volume"]] = [
        59,
        5900.0,
        5900.0,
    ]
    canonical = canonical.loc[
        ~(canonical.ticker.eq("AAPL") & canonical.timestamp.eq(pd.Timestamp("2020-11-02T14:30Z")))
    ]
    eh = canonical.iloc[[0]].copy()
    eh["timestamp"] = pd.Timestamp("2020-11-02T13:00Z")
    eh["ticker"] = "AAPL"
    eh["is_rth"] = False
    eh[["open", "high", "low", "close"]] = 999999.0
    output, _, _ = derive_month(
        pd.concat([canonical, eh]), original, pd.DataFrame(), sensitivity, "2020-11", facts(), []
    )
    row = output.loc[output.ticker.eq("AAPL")].iloc[0]
    assert pd.isna(row.open) and not row.genuine_open
    assert row.genuine_close and row.close == 100.59
    assert row.observed_high < 101
    with pytest.raises(ValueError, match="EH_PRICE_INPUT_FORBIDDEN"):
        adjust_prices(eh, facts())


def test_proxy_cannot_cross_a_quarantined_minute_or_supply_a_label():
    canonical, original, sensitivity = minute_fixture()
    canonical = canonical.loc[
        ~(canonical.ticker.eq("AAPL") & canonical.timestamp.eq(pd.Timestamp("2020-11-02T15:29Z")))
    ]
    original.loc[original.ticker.eq("AAPL"), ["genuine_minutes", "volume", "observed_volume"]] = [
        59,
        5900.0,
        5900.0,
    ]
    proxy = pd.DataFrame(
        {
            "hour_id": ["AAPL:2020-11-02:0"],
            "timestamp": [pd.Timestamp("2020-11-02T15:29Z")],
            "close": [100.58],
            "is_genuine": [False],
            "is_imputed": [True],
        }
    )
    event = {
        "event_id": "SYNTHETIC",
        "ticker": "AAPL",
        "timestamp_utc": "2020-11-02T14:35Z",
        "disposition": "UNVERIFIED_RTH_LOCAL_QUARANTINE",
    }
    output, _, _ = derive_month(
        canonical, original, proxy, sensitivity, "2020-11", facts(), [event]
    )
    row = output.loc[output.ticker.eq("AAPL")].iloc[0]
    assert pd.isna(row.close_input_cap5) and not row.hour_usable_price_endpoints


def test_all67_accounted_ko_three_separate_from_nine_split_events():
    path = Path(
        "reports/data_audit/ta019_hf1m_actions_2026-10-22_193000_v3/P019_PRICE_JUMP_EVIDENCE.json"
    )
    source = json.loads(path.read_text())
    events = event_dispositions(source)
    assert {e["event_id"] for e in events} == {e["event_id"] for e in source}
    ko = [e["event_id"] for e in events if e["disposition"] == "KO_MIXED_BASIS_PREMARKET"]
    assert ko == ["P019-044", "P019-045", "P019-046"]
    assert sum(e["disposition"] == "UNVERIFIED_RTH_LOCAL_QUARANTINE" for e in events) == 18
    assert (
        len(
            {
                e["canonical_event_id"]
                for e in events
                if e["disposition"] == "VERIFIED_SPLIT_ADJUSTED"
            }
        )
        == 9
    )
    with pytest.raises(ValueError, match="STOP_REGISTER_INCOMPLETE"):
        event_dispositions(source[:-1])


def test_dst_holidays_early_close_are_real_exchange_positions():
    october = calendar_frame("2020-10")
    november = calendar_frame("2020-11")
    assert october.loc[october.session_date_et.eq("2020-10-30"), "timestamp"].min().hour == 13
    assert november.loc[november.session_date_et.eq("2020-11-02"), "timestamp"].min().hour == 14
    assert not november.session_date_et.eq("2020-11-26").any()
    early = november.loc[november.session_date_et.eq("2020-11-27")]
    assert len(early) == 210
    assert early.hour_start_utc.nunique() == 4
    assert len(early.loc[early.hour_slot.eq(3)]) == 30


def test_scheduled_positions_not_compressed_and_future_cannot_change_past():
    valid = np.ones((100, 20), dtype=bool)
    first = full_window(valid, 48)
    valid[80, 0] = False
    second = full_window(valid, 48)
    np.testing.assert_array_equal(first[:80], second[:80])
    assert not second[90, 0] and second[90, 1:].all()
    assert not second[90].all()


@pytest.mark.parametrize("namespace", ["Alpaca", "HF20_TWELVEDATA", "HF20_HF1M_LONG_v1"])
def test_loader_rejects_every_old_source_namespace(tmp_path, namespace):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"namespace": namespace}))
    with pytest.raises(ValueError, match="ACTION_SOURCE_NAMESPACE_REQUIRED"):
        load_hours(path)


def test_loader_rejects_legacy_path_even_with_new_namespace(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"namespace": NAMESPACE, "private_root": "data/raw/alpaca"}))
    with pytest.raises(ValueError, match="ACTION_SOURCE_PATH_REQUIRED"):
        load_hours(path)


def test_idempotent_atomic_artifacts_refuse_changed_evidence(tmp_path):
    path = tmp_path / "frame.parquet"
    table = pd.DataFrame({"observed_volume": [0.0, np.nan], "genuine": [True, False]})
    first = publish_table(path, table)
    assert publish_table(path, table) == first
    with pytest.raises(ValueError, match="IMMUTABLE_TABLE_CHANGED"):
        publish_table(path, pd.DataFrame({"observed_volume": [1.0, 2.0]}))
    publish_json(tmp_path / "receipt.json", first)
    with pytest.raises(ValueError, match="IMMUTABLE_OUTPUT_CHANGED"):
        publish_json(tmp_path / "receipt.json", {"changed": True})


def test_proxy_masks_do_not_construct_returns_or_use_future_for_inputs():
    calendar = pd.concat([calendar_frame(f"2011-{m:02d}") for m in range(1, 13)])
    grid = calendar[["hour_start_utc", "hour_end_utc", "session_date_et"]].drop_duplicates()
    grid["is_stub"] = (grid.hour_end_utc - grid.hour_start_utc) < pd.Timedelta(hours=1)
    grid["genuine_close"] = True
    grid["hour_proxy_price_usable"] = True
    grid["genuine_open"] = True
    grid["hour_field_usable_open"] = True
    grid["hour_field_usable_high"] = True
    grid["hour_field_usable_low"] = True
    grid["observed_volume_complete"] = True
    grid["genuine_minutes"] = 60
    grid["price_basis_id"] = "constant"
    hours = pd.concat([grid.assign(ticker=s) for s in SYMBOLS], ignore_index=True)
    first, meta, _ = origin_masks(hours)
    origin = meta.iloc[-2]
    changed = hours.copy()
    hit = changed.ticker.eq("AAPL") & changed.hour_end_utc.eq(origin.exit_end_utc)
    changed.loc[hit, ["genuine_close", "hour_proxy_price_usable"]] = False
    second, _, _ = origin_masks(changed)
    a = first.loc[first.origin_id.eq(origin.origin_id)]
    b = second.loc[second.origin_id.eq(origin.origin_id)]
    np.testing.assert_array_equal(a.origin_input_48_eligible, b.origin_input_48_eligible)
    assert a.origin_cross_section_20_eligible.all()
    assert not b.origin_cross_section_20_eligible.any()
