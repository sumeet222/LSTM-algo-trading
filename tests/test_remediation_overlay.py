"""Realistic tiny native archives: exact-key recovery, conflicts and no false provenance."""

from dataclasses import replace

import pandas as pd
import pytest

from lstm_data.config import fingerprint
from lstm_data.labels import UNIVERSE
from lstm_data.remediation_overlay import NativeAddition, history_from_view, resolve_native
from lstm_data.stock_source import StockCalendar


def panel():
    cal = StockCalendar("2020-06-01", "2020-06-02")
    rows = []
    for day, clock in cal._sessions.items():
        assert clock.open is not None and clock.close is not None
        for symbol in UNIVERSE:
            for time in pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"):
                rows.append(
                    {
                        "symbol": symbol,
                        "timestamp": time,
                        "open": 10.0,
                        "high": 11.0,
                        "low": 9.0,
                        "close": 10.0,
                        "volume": 100.0,
                        "feed": "sip",
                        "adjustment": "split",
                        "source_timeframe": "30Min",
                        "provenance_id": fingerprint([symbol, day]),
                    }
                )
    whole = pd.DataFrame(rows)
    absent = (whole.symbol == "AAPL") & (whole.timestamp == pd.Timestamp("2020-06-01T14:00Z"))
    original = whole[~absent].copy()
    control = NativeAddition(
        whole[whole.timestamp.dt.date == pd.Timestamp("2020-06-02").date()],
        "ALPACA",
        "BASIS_CONTROL",
        fingerprint("control"),
        fingerprint("body1"),
    )
    gap = NativeAddition(
        whole[
            (whole.symbol == "AAPL")
            & (whole.timestamp.dt.date == pd.Timestamp("2020-06-01").date())
        ],
        "ALPACA",
        "GAP_RETRY",
        fingerprint("gap"),
        fingerprint("body2"),
    )
    return cal, original, control, gap


def test_exact_key_genuine_alpaca_recovery_original_precedence_and_unknown_publication():
    cal, original, control, gap = panel()
    before = original.copy(deep=True)
    frame, selection = resolve_native(original, (control, gap), cal, view="GAP_ONLY")
    pd.testing.assert_frame_equal(original, before)
    assert len(frame) == len(original) + 1 and selection["added_RTH_rows"] == 1
    assert all(c["result"] == "IDENTICAL" for c in selection["overlap_checks"])
    assert selection["selected_rows"][0]["provider"] == "ALPACA"
    assert selection["selected_rows"][0]["availability_basis"] == "UNKNOWN"
    history, qa = history_from_view(frame, "2020-06-01", view="GAP_ONLY", end="2020-06-02")
    assert qa["missing_source_bars"] == 0
    bar = history.bars["AAPL", "2020-06-01", 1]
    assert bar.volume == 200 and bar.available_at is None and bar.basis == "UNKNOWN"
    assert not bar.action_verified
    assert history.daily["AAPL", "2020-06-01"].volume == 1300


def test_unrecovered_hole_preserved_and_conflicting_neighbor_blocks_entire_gap_partition():
    cal, original, control, gap = panel()
    raw, meta = resolve_native(original, (control,), cal, view="GAP_ONLY")
    history, qa = history_from_view(raw, "2020-06-01", view="GAP_ONLY", end="2020-06-02")
    assert meta["added_RTH_rows"] == 0 and qa["missing_source_bars"] == 1
    assert ("AAPL", "2020-06-01", 1) not in history.bars
    assert history.daily["AAPL", "2020-06-01"].volume is None
    changed = gap.frame.copy()
    first = changed.index[0]
    changed.loc[first, ["open", "high", "low", "close"]] += 1
    _, meta = resolve_native(original, (control, replace(gap, frame=changed)), cal, view="GAP_ONLY")
    assert meta["added_RTH_rows"] == 0
    assert meta["rejected_partitions"][0]["reason"] == "GAP_NEIGHBOR_OHLCV_CONFLICT"
    assert any(r["result"] == "CONFLICT_ORIGINAL_PRESERVED" for r in meta["overlap_checks"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider", "MASSIVE"),
        ("adjustment", "raw"),
        ("volume_unit", "UNADJUSTED_SHARES"),
        ("entity_asof", "2026-10-11"),
    ],
)
def test_secondary_or_incompatible_basis_cannot_masquerade_as_alpaca(field, value):
    cal, original, control, gap = panel()
    wrong = replace(gap, **{field: value})
    _, meta = resolve_native(original, (control, wrong), cal, view="GAP_ONLY")
    assert meta["added_RTH_rows"] == 0 and meta["rejected_partitions"]
    assert not meta["scientific_readiness"]


def test_off_grid_duplicate_inconsistent_additions_and_unapproved_view_rejected():
    cal, original, control, gap = panel()
    changed = gap.frame[gap.frame.timestamp == pd.Timestamp("2020-06-01T14:00Z")].copy()
    changed["timestamp"] += pd.Timedelta(minutes=1)
    with pytest.raises(ValueError, match="OFF_NATIVE_GRID"):
        resolve_native(original, (control, replace(gap, frame=changed)), cal, view="GAP_ONLY")
    changed["timestamp"] -= pd.Timedelta(minutes=1)
    changed["volume"] += 5
    with pytest.raises(ValueError, match="CONFLICTING_ADDITIONAL"):
        resolve_native(original, (control, gap, replace(gap, frame=changed)), cal, view="GAP_ONLY")
    with pytest.raises(ValueError, match="EXPLICIT_CANDIDATE"):
        resolve_native(original, (control, gap), cal, view="SILENT_FALLBACK")
    with pytest.raises(ValueError, match="PUBLICATION_MUST_REMAIN_UNKNOWN"):
        replace(gap, availability_basis="DOCUMENTED")


def test_secondary_control_and_minute_diagnostics_never_authorize_native_insertion():
    cal, original, control, gap = panel()
    _, meta = resolve_native(
        original, (replace(control, provider="MASSIVE"), gap), cal, view="GAP_ONLY"
    )
    assert meta["added_RTH_rows"] == 0
    minute = gap.frame.copy()
    minute["source_timeframe"] = "1Min"
    with pytest.raises(ValueError, match="NATIVE_30MIN"):
        resolve_native(original, (control, replace(gap, frame=minute)), cal, view="GAP_ONLY")
