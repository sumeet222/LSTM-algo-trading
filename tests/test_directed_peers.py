"""Independent formation/lag48/direction/sham oracles, no historical data or LL fit."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from lstm_data.baseline_authority import replay_permission
from lstm_data.calendar import schedule
from lstm_data.directed_peers import (
    FormationRow,
    directed_ridge_fit,
    directed_window,
    formation_pair,
    ridge_layout_status,
    target_flags,
    timing_destroy,
)
from lstm_data.e5_audit import fake_antecedent, fake_formation
from lstm_data.m2 import ScheduledCalendar
from lstm_data.p3_domain import MODE, Permission, UniverseSpec
from lstm_data.regime_peer_audit import fabricated_case


@pytest.fixture(scope="module")
def case():
    data, history, prep, val, permission = fabricated_case()
    calendar = ScheduledCalendar("2020-07-01", "2023-06-30")
    row = data.origins[-2].inputs
    pair = fake_formation(row.universe, permission)
    antecedent = fake_antecedent(row, prep, calendar)
    window = directed_window(row, prep, history, permission, calendar, pair, antecedent)
    return row, prep, history, permission, calendar, pair, antecedent, window


def formation_rows(u):
    result = []
    for day, clock in schedule("2020-01-01", "2020-06-30").iloc[-60:].iterrows():
        assert isinstance(day, pd.Timestamp)
        for i, symbol in enumerate(u.symbols):
            result.append(
                FormationRow(
                    symbol,
                    day.date().isoformat(),
                    100.0,
                    (i + 1) * 1e6,
                    clock.close,
                    "SYN:FORM:" + symbol + str(day.date()),
                )
            )
    return tuple(result)


def test_formation_60_actual_sessions_sha_unique_extremes_ties_and_no_hindsight():
    permission = replay_permission(Permission(MODE))
    u = UniverseSpec("SYN:FIVE_FICTIONAL", ("NOVA", "ORBIT", "PULSE", "QUARK", "RUNE"))
    rows = formation_rows(u)
    pair = formation_pair(u, rows, permission)
    assert pair.highest == "RUNE" and pair.lowest == "NOVA"
    assert pair.means == (1e8, 2e8, 3e8, 4e8, 5e8)
    assert formation_pair(u, rows[::-1], permission).pair_id == pair.pair_id
    np.testing.assert_array_equal(target_flags(pair), [[0, 1], [0, 0], [0, 0], [0, 0], [1, 0]])
    for bad in (
        rows[:-1],
        rows + (rows[0],),
        (replace(rows[0], available_at=pair.decision_at),) + rows[1:],
        (replace(rows[0], available_at=pd.NaT),) + rows[1:],
        (replace(rows[0], units_verified=False),) + rows[1:],
        (replace(rows[0], source_id="OBSERVED:PRICE"),) + rows[1:],
    ):
        with pytest.raises(ValueError):
            formation_pair(u, bad, permission)
    tied = tuple(replace(r, volume=1e6) for r in rows)
    with pytest.raises(ValueError, match="HL_TIE_UNRESOLVED"):
        formation_pair(u, tied, permission)
    with pytest.raises(ValueError):
        formation_pair(u, rows, Permission("SCIENTIFIC_REAL"))
    switched = replace(u, symbols=u.symbols[::-1])
    assert formation_pair(switched, rows, permission).highest == pair.highest
    assert formation_pair(switched, rows, permission).pair_id != pair.pair_id


def test_directed_hand_values_all_targets_four_channels_and_lagged_mean(case):
    _, _, _, _, calendar, pair, _, window = case
    h, low = pair.universe.symbols.index(pair.highest), pair.universe.symbols.index(pair.lowest)
    window.validate(calendar)
    for j in (0, 24, 47):
        a, b = window.samples[j : j + 2]
        for i in range(5):
            expected = [
                b.z[h] if i == low else 0,
                a.z[h] if i == low else 0,
                b.z[low] if i == h else 0,
                a.z[low] if i == h else 0,
                sum(a.z[k] for k in range(5) if k != i) / 4,
            ]
            np.testing.assert_allclose(window.signals[i, j], expected, rtol=0, atol=1e-15)
    trace = window.trace(calendar)
    assert trace["cross_session"] and trace["wall_lag_minutes"] == 1140
    assert window.processed.stock.steps == tuple(s.step for s in window.samples[1:])
    assert window.signals.shape == (5, 48, 5) and window.flags.shape == (5, 2)


@pytest.mark.parametrize(
    "fault",
    [
        "future",
        "nat",
        "missing",
        "grid",
        "stub",
        "source",
        "action",
        "scaler",
        "units",
        "order",
        "real",
        "label",
    ],
)
def test_antecedent_rejects_every_causal_unit_source_order_violation(case, fault):
    row, prep, history, permission, calendar, pair, a, _ = case
    if fault == "future":
        a = replace(a, available_at=(a.step.end + pd.Timedelta(nanoseconds=1),) * 5)
    elif fault == "nat":
        a = replace(a, available_at=(pd.NaT,) * 5)
    elif fault == "missing":
        a = replace(a, raw_m1=a.raw_m1[:4])
    elif fault == "grid":
        a = replace(a, step=calendar.steps[calendar.steps.index(a.step) - 1])
    elif fault == "stub":
        a = replace(a, step=replace(a.step, end=a.step.end + pd.Timedelta(minutes=30)))
    elif fault in {"source", "action", "scaler"}:
        field = {"source": "source_binding", "action": "action_binding", "scaler": "scaler_ref"}[
            fault
        ]
        a = replace(a, **{field: "SYN:WRONG"})
    elif fault == "units":
        a = replace(a, units_verified=False)
    elif fault == "order":
        a = replace(a, universe=replace(a.universe, symbols=a.universe.symbols[::-1]))
    elif fault == "label":
        a = replace(a, source_ids=tuple("SYN:LABEL:" + str(i) for i in range(5)))
    else:
        a = replace(a, basis="DOCUMENTED")
    with pytest.raises(ValueError):
        directed_window(row, prep, history, permission, calendar, pair, a)


def test_directed_array_and_formation_mutation_invalidate_binding(case):
    _, _, _, _, calendar, pair, _, window = case
    changed = window.signals.copy()
    changed[0, 0, 0] += 1
    with pytest.raises(ValueError):
        replace(window, signals=changed).validate(calendar)
    with pytest.raises(ValueError):
        replace(window, pair=replace(pair, table_sha="f" * 64)).validate(calendar)
    with pytest.raises(ValueError):
        replace(window, samples=window.samples[1:]).validate(calendar)


@pytest.mark.parametrize(
    "day,minutes", [("2021-03-15", 3960), ("2020-11-30", 4200), ("2021-03-16", 1140)]
)
def test_calendar_predecessor_dst_earlyclose_and_overnight_no_stubs(day, minutes):
    c = ScheduledCalendar("2020-07-01", "2021-03-16")
    current = next(s for s in c.steps if s.session == day and s.slot == 1)
    previous = c.steps[c.steps.index(current) - 1]
    assert (current.end - previous.end).total_seconds() / 60 == minutes
    assert (previous.end - previous.start).total_seconds() == 3600
    if day == "2020-11-30":
        assert previous.session == "2020-11-27" and previous.slot == 3
    if day == "2021-03-15":
        assert previous.end.hour == 20 and current.end.hour == 14
    second = next(s for s in c.steps if s.session == day and s.slot == 2)
    assert (second.end - current.end).total_seconds() / 60 == 60


def test_ten_eligible_sessions_same_slot_and_common_origin_mask(case):
    _, _, _, _, calendar, _, _, window = case
    eligible = tuple(str(d.date()) for d in schedule("2023-03-01", "2023-06-30").index)
    base = window.samples[0]
    table = tuple(
        replace(
            base,
            step=s,
            z=(s.slot,) * 5,
            available_at=(s.end,) * 5,
            source_ids=tuple(
                "SYN:SHIFT:" + s.session + str(s.slot) + name for name in base.universe.symbols
            ),
        )
        for s in calendar.steps
        if s.session in eligible
    )
    result = timing_destroy(window, table, eligible, calendar)
    assert result.matched and result.shifted_signals is not None
    assert result.shifted_signals.shape == window.signals.shape
    for now, previous in result.timestamp_pairs:
        d, p = pd.Timestamp(now), pd.Timestamp(previous)
        actual = d.tz_convert("America/New_York").date().isoformat()
        earlier = p.tz_convert("America/New_York").date().isoformat()
        assert eligible.index(actual) - eligible.index(earlier) == 10
        assert d.tz_convert("America/New_York").time() == p.tz_convert("America/New_York").time()
    incomplete = timing_destroy(window, (), eligible, calendar)
    assert not incomplete.matched and incomplete.shifted_signals is None
    assert incomplete.exclusions == {"SAME_SLOT_SOURCE_ABSENT": 49}
    for bad in (eligible[::-1], eligible + (eligible[-1],)):
        with pytest.raises(ValueError):
            timing_destroy(window, table, bad, calendar)
    with pytest.raises(ValueError):
        timing_destroy(window, table + (table[0],), eligible, calendar)


def test_ridge_layout_silence_stops_production_and_no_new_solver():
    decision = ridge_layout_status()
    assert decision["approved_prefix"] == 161
    assert decision["flags_once"] == {"LL0_R": 163, "LL1_R": 198}
    assert decision["flags_each_lag"] == {"LL0_R": 175, "LL1_R": 210}
    with pytest.raises(ValueError, match="REQUIRES_HUMAN_DECISION"):
        directed_ridge_fit()
