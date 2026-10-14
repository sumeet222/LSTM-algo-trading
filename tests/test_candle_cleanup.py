"""Hand-controlled universes: placeholders never become volume, labels or execution."""

from dataclasses import replace
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from lstm_data.aggregation import aggregate_session_hours
from lstm_data.calendar import schedule
from lstm_data.candle_cleanup import MODE, PriceUnitSegment, cleanup
from lstm_data.engineering_profile import EngineeringSelection
from lstm_data.p3_domain import Permission, PriceReference, UniverseSpec
from lstm_data.validation import normalize, require_valid


def source(start="2021-03-11", stop="2021-03-16", symbols=("ALPHA",)):
    rows = []
    for symbol in symbols:
        for _, c in schedule(start, stop).iterrows():
            for t in pd.date_range(c.open, c.close, freq="30min", inclusive="left"):
                rows.append(
                    dict(
                        symbol=symbol,
                        timestamp=t,
                        open=100.0,
                        high=101.0,
                        low=99.0,
                        close=100.0,
                        volume=0.0,
                        trade_count=0,
                        vwap=100.0,
                        source_timeframe="30Min",
                    )
                )
    return pd.DataFrame(rows)


def segments(symbols=("ALPHA",), verified=True):
    return tuple(
        PriceUnitSegment(
            s,
            pd.Timestamp("2020-01-01T00:00Z"),
            pd.Timestamp("2022-01-01T00:00Z"),
            "SYN:UNITS",
            verified,
            "SYN:UNIT_PROOF" if verified else "",
        )
        for s in symbols
    )


def build(f, start="2021-03-11", stop="2021-03-16", symbols=("ALPHA",), segs=None):
    return cleanup(
        f,
        symbols,
        start,
        stop,
        profile_id="ENG:TEST",
        source_binding="SYN:SOURCE_SHA",
        segments=segments(symbols) if segs is None else segs,
    )


@pytest.mark.parametrize("length", [1, 2, 3, 12, 13, 26, 39])
def test_all_gap_lengths_actual_anchor_only_unknown_volume(length):
    f = source()
    removed = f.iloc[13 : 13 + length].timestamp
    kept = f[~f.timestamp.isin(removed)].copy()
    v = build(kept)
    assert len(v.fills) == length and v.unresolved.empty
    assert set(v.fills.timestamp) == set(removed)
    assert (
        v.fills.volume.isna().all()
        and v.fills.trade_count.isna().all()
        and v.fills.vwap.isna().all()
    )
    assert v.fills.volume_unknown.all() and not v.fills.genuine_t2_eligible.any()
    assert (v.fills.open == v.fills.high).all() and (v.fills.low == v.fills.close).all()
    assert set(pd.to_datetime(v.fills.anchor_timestamp, utc=True)).issubset(set(kept.timestamp))
    for r in v.fills.itertuples():
        assert isinstance(r.anchor_end, str) and isinstance(r.timestamp, pd.Timestamp)
        assert pd.Timestamp(r.anchor_end) < r.timestamp
    assert v.fills.calendar_run_length.max() == length
    ages = v.fills.elapsed_age_minutes.tolist()
    assert ages == sorted(ages)
    result = v.materialize_engineering(mode=MODE)
    pd.testing.assert_frame_equal(
        result[result.is_observed][kept.columns].reset_index(drop=True),
        kept.reset_index(drop=True),
        check_dtype=False,
    )
    assert (
        result[result.is_observed].volume.eq(0).all()
        and not result[result.is_observed].volume_unknown.any()
    )
    assert len(result) == len(f)


def test_strictly_prior_excludes_equal_end_and_never_uses_future_or_imputed():
    f = source("2021-03-15", "2021-03-15")
    f.loc[0, "close"] = 100.5
    v = build(f.drop(index=[1, 2, 3]), start="2021-03-15", stop="2021-03-15")
    assert (
        len(v.unresolved) == 1 and v.unresolved.iloc[0].reason == "NO_GENUINE_STRICTLY_PRIOR_ANCHOR"
    )
    assert len(v.fills) == 2 and v.fills.anchor_close.eq(100.5).all()
    assert set(v.fills.anchor_timestamp) == {f.iloc[0].timestamp.isoformat()}
    changed = f.drop(index=[1, 2, 3]).copy()
    changed.loc[4, "close"] = 100.75
    second = build(changed, start="2021-03-15", stop="2021-03-15")
    pd.testing.assert_frame_equal(v.fills, second.fills)


def test_terminal_placeholder_and_confirmed_halt_scenario_are_not_execution_or_t2():
    f = source()
    v = build(f.drop(index=[25]))
    assert len(v.fills) == 1 and v.fills.iloc[0].is_terminal
    assert not v.fills.iloc[0].genuine_t2_eligible
    for activity in (
        "T2_DAILY_CLOSE",
        "TG0_LABEL",
        "HALT_EXECUTION",
        "FT0",
        "P3_TRADING",
        "P4_FIT",
    ):
        with pytest.raises(ValueError, match="FORBIDDEN_FOR_SCIENCE"):
            v.require_scientific(activity)


@pytest.mark.parametrize(
    "day,count,opening",
    [("2020-11-27", 7, "14:30"), ("2021-03-12", 13, "14:30"), ("2021-03-15", 13, "13:30")],
)
def test_early_close_dst_first_session_and_no_missing_overnight(day, count, opening):
    f = source(day, day)
    v = build(f, start=day, stop=day)
    assert len(v.expected_keys) == count and v.fills.empty and v.unresolved.empty
    result = v.materialize_engineering(mode=MODE)
    assert result.timestamp.iloc[0].strftime("%H:%M") == opening
    pd.testing.assert_frame_equal(result[f.columns], f)
    first = build(f.iloc[1:], start=day, stop=day)
    assert len(first.unresolved) == 1 and first.unresolved.iloc[0].is_opening


def test_split_and_unknown_units_fail_closed_instead_of_reusing_price():
    f = source()
    boundary = f.iloc[13].timestamp
    a = PriceUnitSegment(
        "ALPHA", pd.Timestamp("2020-01-01T00:00Z"), boundary, "SYN:OLD", True, "SYN:PROOF"
    )
    b = PriceUnitSegment(
        "ALPHA", boundary, pd.Timestamp("2022-01-01T00:00Z"), "SYN:NEW", True, "SYN:PROOF"
    )
    v = build(f.drop(index=13), segs=(a, b))
    assert v.fills.empty and v.unresolved.iloc[0].reason == "PRICE_UNIT_SEGMENT_DISCONTINUITY"
    unknown = build(f.drop(index=13), segs=segments(verified=False))
    assert unknown.fills.empty and unknown.unresolved.iloc[0].reason == "SPLIT_UNITS_UNVERIFIED"
    with pytest.raises(ValueError, match="OVERLAPPING"):
        build(f, segs=(a, replace(b, start=boundary - pd.Timedelta(minutes=1))))


def test_bad_source_duplicate_nonfinite_offgrid_and_wrong_population_rejected():
    f = source()
    for bad in (pd.concat([f, f.iloc[:1]]), f.assign(close=np.inf), f.assign(symbol="OTHER")):
        with pytest.raises(ValueError):
            build(bad)
    bad = f.copy()
    first = bad.loc[0, "timestamp"]
    assert isinstance(first, pd.Timestamp)
    bad.loc[0, "timestamp"] = first + pd.Timedelta(minutes=1)
    with pytest.raises(ValueError, match="OFF_GRID"):
        build(bad)
    bad = f.copy()
    bad.loc[0, "volume"] = -1
    with pytest.raises(ValueError):
        build(bad)


def test_five_and_larger_ordered_universes_idempotence_and_stock_segment_calendar():
    names = ("ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA", "ZETA")
    f = source(symbols=names)
    v = build(f, symbols=names)
    second = build(f, symbols=names)
    assert v.content_id == second.content_id and len(v.expected_keys) == len(f)
    reverse = build(f, symbols=names[::-1])
    assert reverse.content_id != v.content_id
    assert tuple(reverse.materialize_engineering(mode=MODE).symbol.unique()) == names[::-1]
    active = {
        s: ((pd.Timestamp("2021-03-15T13:30Z"), pd.Timestamp("2021-03-17T00:00Z")),) for s in names
    }
    part = cleanup(
        f,
        names,
        "2021-03-11",
        "2021-03-16",
        profile_id="ENG:SEGMENTS",
        source_binding="SYN:SHA",
        segments=segments(names),
        active_intervals=active,
    )
    assert len(part.expected_keys) == 6 * 26 and part.fills.empty and part.unresolved.empty


def test_every_engineering_row_is_quarantined_even_zero_fill_and_attrs_stripped():
    f = source()
    v = build(f)
    result = v.materialize_engineering(mode=MODE)
    assert (
        result.is_observed.all() and not result.is_synthetic.any() and result.engineering_only.all()
    )
    result.attrs.clear()
    with pytest.raises(ValueError, match="NOT_GENUINE_SOURCE"):
        require_valid(normalize(result, stocks=True), stocks=True)
    with pytest.raises(ValueError, match="NOT_GENUINE_SOURCE"):
        aggregate_session_hours(result, ["ALPHA"], "2021-03-11", "2021-03-16")
    with pytest.raises(ValueError, match="EXPLICIT_ENGINEERING"):
        v.materialize_engineering(mode="SCIENTIFIC")
    v.observed.loc[0, "close"] = 100.5
    with pytest.raises(ValueError, match="OBSERVATIONS_MUTATED"):
        v.materialize_engineering(mode=MODE)


def test_p3_p4_geometry_binding_changes_and_no_fit_trading_reference_adapter():
    names = ("ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA")
    v = build(source(symbols=names), symbols=names)
    u = UniverseSpec("ENG:PROVISIONAL_TEST", names)
    selection = EngineeringSelection(u, v, "profile_sha", "source_sha")
    assert selection.for_activity("DATA_SHAPE").is_observed.all()
    assert selection.cache_binding() != selection.cache_binding(floor_id="new_floor")
    assert selection.cache_binding() != selection.cache_binding(target_id="new_target")
    assert selection.cache_binding() != selection.cache_binding(preparation_id="new_preparation")
    assert (
        selection.cache_binding()
        != replace(selection, profile_sha256="new_policy_profile").cache_binding()
    )
    for activity in ("P4_FIT", "P3_TRADING", "FT0", "TG0", "T2"):
        with pytest.raises(ValueError, match="FORBIDDEN_FOR_SCIENCE"):
            selection.for_activity(activity)
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        Permission(MODE).ensure()
    with pytest.raises(ValueError, match="SYNTHETIC_ID_REQUIRED"):
        PriceReference(
            u,
            "ALPHA",
            Decimal(100),
            pd.Timestamp("2021-03-15T14:30Z"),
            None,
            "ENG:FAKE_TERMINAL",
            "MARK",
        )


def test_profile_loader_sha_code_order_and_mode_bindings(tmp_path, monkeypatch):
    import json
    from pathlib import Path

    from lstm_data.candle_cleanup import POLICY
    from lstm_data.config import digest, write_json
    from lstm_data.engineering_profile import load_engineering_profile
    from lstm_data.remediation_transport import StorageLimit, publish_chunk
    from lstm_data.store import chunk_paths

    monkeypatch.chdir(tmp_path)
    names = ("ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA")
    frame = source("2021-03-15", "2021-03-15", names).assign(feed="sip", adjustment="split")
    p = dict(
        symbols=",".join(names),
        start="2021-03-15T04:00Z",
        end="2021-03-16T03:59:59.999999999Z",
        timeframe="30Min",
        feed="sip",
        currency="USD",
        asof="2025-06-30",
        adjustment="split",
        limit=10000,
        sort="asc",
    )
    store = Path("data/raw/alpaca/synthetic_profile")
    publish_chunk(store, frame, p, [], kind="FULL_NATIVE", limit=StorageLimit((store,)))
    data, meta = chunk_paths(store, p)
    ref = dict(
        data=str(data),
        manifest=str(meta),
        sha256=digest(data),
        manifest_sha256=digest(meta),
        params=p,
    )
    manifest = Path("source_manifest.json")
    write_json(manifest, dict(ordered_universe=names, source_by_stock={s: [ref] for s in names}))
    code = Path("code_identity.txt")
    code.write_text("SYNTHETIC_CODE_IDENTITY")
    profile = dict(
        mode=MODE,
        policy_id=POLICY,
        scientific_activation=False,
        universe_version="ENG:TEST",
        symbols=names,
        sectors=[dict(symbol=s, sector=str(i)) for i, s in enumerate(names)],
        source_manifest=str(manifest),
        source_manifest_sha256=digest(manifest),
        code_bindings=[dict(path=str(code), sha256=digest(code))],
        start="2021-03-15",
        stop="2021-03-15",
        price_unit_segments=[
            dict(
                symbol=s.symbol,
                start=s.start.isoformat(),
                stop=s.stop.isoformat(),
                unit_id=s.unit_id,
                verified=s.verified,
                evidence_ref=s.evidence_ref,
            )
            for s in segments(names)
        ],
    )
    path = Path("profile.json")
    write_json(path, profile)
    selection = load_engineering_profile(path, mode=MODE)
    assert selection.universe.symbols == names and selection.view.fills.empty
    assert len(selection.for_activity("CANDLE_QA")) == 65
    with pytest.raises(ValueError, match="QUARANTINED"):
        load_engineering_profile(path, mode="ENGINEERING_SYNTHETIC_ONLY")
    code.write_text("CHANGED_CODE")
    with pytest.raises(ValueError, match="CODE_CHANGED"):
        load_engineering_profile(path, mode=MODE)
    code.write_text("SYNTHETIC_CODE_IDENTITY")
    altered = dict(profile, symbols=names[::-1])
    Path("reordered.json").write_text(json.dumps(altered))
    with pytest.raises(ValueError):
        load_engineering_profile(Path("reordered.json"), mode=MODE)
    manifest.write_text(manifest.read_text() + " ")
    with pytest.raises(ValueError, match="MANIFEST_CHANGED"):
        load_engineering_profile(path, mode=MODE)


def test_entire_first_session_cannot_borrow_a_future_anchor():
    f = source()
    v = build(f.iloc[13:])
    assert v.fills.empty and len(v.unresolved) == 13
    assert v.unresolved.reason.eq("NO_GENUINE_STRICTLY_PRIOR_ANCHOR").all()
    assert v.unresolved.calendar_run_length.eq(13).all()
    assert len(v.expected_keys) == len(f)
