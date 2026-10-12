"""Structural universe diagnostics preserve math, order, union losses and causal scope."""

import pandas as pd
import pytest

from lstm_data.config import fingerprint
from lstm_data.labels import UNIVERSE
from lstm_data.remediation_overlay import history_from_view
from lstm_data.stock_features import FeatureCalculator
from lstm_data.stock_source import StockCalendar
from lstm_data.universe_screen import (
    BACKUPS,
    FULL_MASK,
    counterfactuals,
    diagnostic_history,
    panels,
    validate_panel,
)


def native(symbols=UNIVERSE):
    cal = StockCalendar("2020-06-01", "2020-06-02")
    rows = []
    for day, clock in cal._sessions.items():
        assert clock.open is not None and clock.close is not None
        for s in symbols:
            for at in pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"):
                rows.append(
                    dict(
                        symbol=s,
                        timestamp=at,
                        open=10.0,
                        high=11.0,
                        low=9.0,
                        close=10.0,
                        volume=100.0,
                        feed="sip",
                        adjustment="split",
                        source_timeframe="30Min",
                        native_source_id=fingerprint([s, at.isoformat()]),
                    )
                )
    return pd.DataFrame(rows)


def test_original_formula_equivalence_and_separate_identity():
    f = native()
    original, _ = history_from_view(f, "2020-06-01", view="SOURCE_ONLY", end="2023-06-30")
    adapter, _ = diagnostic_history(f, UNIVERSE, "2020-06-01", "2023-06-30")
    a, b = FeatureCalculator(original), FeatureCalculator(adapter)
    for symbol in UNIVERSE:
        for step in original.calendar.steps[:12]:
            x, y = (
                a.components(symbol, step, source_only=True),
                b.components(symbol, step, source_only=True),
            )
            assert x.values == y.values and x.coverage == y.coverage
    assert original.binding != adapter.binding and not adapter.synthetic
    assert all(r.available_at is None and not r.action_verified for r in adapter.bars.values())
    alt, qa = diagnostic_history(native(BACKUPS), BACKUPS, "2020-06-01", "2023-06-30")
    assert alt.binding != adapter.binding and qa["identity"]["symbols"] == BACKUPS
    assert set(k[0] for k in alt.bars) == set(UNIVERSE)


def test32_diagnostic_combinations_overlap_union_and_no_recovered_sample():
    assert len(panels()) == 32 and panels()[0] == UNIVERSE and panels()[-1] == BACKUPS
    rows = [
        {
            "id": str(i),
            "session": f"d{i // 2}",
            "origin": i % 2 + 1,
            "masks": {s: FULL_MASK for s in UNIVERSE},
        }
        for i in range(1502)
    ]
    rows[0]["masks"]["JPM"] = 0
    rows[0]["masks"]["JNJ"] = 0
    rows[1]["masks"]["JPM"] = 0
    bounds = counterfactuals(rows)
    no = next(b for b in bounds if b["count"] == 0)
    jpm = next(b for b in bounds if b["removed_masks"] == ("JPM",))
    assert no["upper_numerator"] == 1500 and jpm["upper_numerator"] == 1501
    assert all(not b["recovered_or_trainable"] for b in bounds)
    with pytest.raises(ValueError):
        counterfactuals(rows[:-1])


def test_invalid_order_duplicates_source_grid_and_confirmation():
    for symbols in (UNIVERSE[::-1], UNIVERSE[:-1], ("AAPL",) * 5):
        with pytest.raises(ValueError):
            validate_panel(symbols)
    f = native()
    with pytest.raises(ValueError):
        diagnostic_history(pd.concat([f, f.iloc[:1]]), UNIVERSE, "2020-06-01", "2023-06-30")
    bad = f.copy()
    bad.loc[0, "timestamp"] = pd.Timestamp("2020-06-01T13:31Z")
    with pytest.raises(ValueError):
        diagnostic_history(bad, UNIVERSE, "2020-06-01", "2023-06-30")
    with pytest.raises(ValueError):
        diagnostic_history(f, UNIVERSE, "2020-06-01", "2025-06-30")


def test_candidate_identity_can_use_original_p3_contract_without_trading():
    from lstm_data.baseline_fixtures import feature_input
    from lstm_data.baseline_inputs import forecast_adapter, momentum
    from lstm_data.p3_domain import MODE, Permission, UniverseSpec

    for names in (UNIVERSE, BACKUPS):
        u = UniverseSpec("SYN:SCREEN:" + fingerprint(names), names)
        row = feature_input(u)
        f = forecast_adapter(
            momentum(row, Permission(MODE), allow_synthetic=True),
            Permission(MODE),
            allow_synthetic=True,
        )
        assert f.universe == u and f.pair == (names[0], names[-1])


def test_known_absence_bound_has_independent_daily_and_48_step_oracle():
    from lstm_data.clocks import execution_plan
    from lstm_data.m2 import scheduled_window
    from lstm_data.universe_screen import t2_absence_bound

    cal = StockCalendar("2019-12-18", "2023-06-30")
    gaps = ("2021-04-19", "2021-10-25", "2022-03-08")
    bad_days = set()
    for day in gaps:
        index = cal.days.index(day)
        # A missing interior price removes two of20 adjacent sign observations;
        # the first/last edge loses only one and remains19/20.
        bad_days.update(cal.days[index + 2 : index + 21])
    expected = set()
    for day, clock in cal._sessions.items():
        if not "2020-07-01" <= day < "2023-07-01":
            continue
        for origin in (1, 2):
            if execution_plan(clock, origin).calendar_valid and any(
                step.session in bad_days for step in scheduled_window(cal, day, origin)
            ):
                expected.add((day, origin))
    got = t2_absence_bound(cal, gaps)
    assert {(r["session"], r["origin"]) for r in got} == expected and len(got) == 162
    assert len(t2_absence_bound(cal, gaps + ("2022-01-24",))) == 216
    assert not t2_absence_bound(cal, ())
    with pytest.raises(ValueError):
        t2_absence_bound(cal, ("2024-07-01",))
