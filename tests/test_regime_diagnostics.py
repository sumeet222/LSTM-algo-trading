"""Independent fabricated regime/MC2 boundary and provenance oracles."""

from dataclasses import replace

import pandas as pd
import pytest

from lstm_data.calendar import schedule
from lstm_data.clocks import execution_plan
from lstm_data.m2 import ScheduledCalendar, scheduled_window
from lstm_data.market_features import MarketWindow
from lstm_data.neural_market import MarketStamp
from lstm_data.regime_diagnostics import (
    DiagnosticWindow,
    PairedRecord,
    Regime,
    U2Threshold,
    classify,
    mc2_readiness,
    occupancy,
    paired_report,
    variation,
)

CALENDAR = ScheduledCalendar("2020-07-01", "2021-06-30")


def oracle_window(
    day="2020-10-05",
    origin=1,
    *,
    changes=12,
    missing=0,
    u1_only=False,
    delta=1.0,
    endpoint=(0.0, 0.0, 0.0, 0.0, 1.0),
):
    steps = scheduled_window(CALENDAR, day, origin)
    vectors = [endpoint for _ in steps]
    for i in range(changes):
        values = list(endpoint)
        values[0 if u1_only else 1] += delta
        vectors[i] = tuple(values)
    mask = [True] * 48
    for i in range(45 - missing, 45):
        vectors[i] = (0.0,) * 5
        mask[i] = False
    sources = tuple(
        ("SYN:M:" + s.end.isoformat(),) if valid else () for s, valid in zip(steps, mask)
    )
    stamps = tuple(
        MarketStamp(s.end, s.end if v else None, s.end if v else None, ids)
        for s, v, ids in zip(steps, mask, sources)
    )
    market = MarketWindow(
        tuple(vectors),
        tuple(mask),
        "SYNTHETIC_PREPARED",
        (),
        scheduled_ends=tuple(s.end for s in steps),
        source_ids=sources,
        scaler_ref="SYN:SCALER",
        floor_ref="SYN:FLOOR",
    )
    return DiagnosticWindow(day, origin, market, stamps, "SYN:REGIME", "SYN:INPUT", "TRAINING")


def threshold():
    return U2Threshold(
        0.0, "SYN:SCALER", "SYN:REGIME", pd.Timestamp("2020-08-01T04:00Z"), "SYN:TRAIN"
    )


@pytest.mark.parametrize(
    "u2,u5,trend,vol",
    [
        (0.0, 0.0, "NEUTRAL", "LOW"),
        (1.0, 1.0, "BULL", "HIGH"),
        (-1.0, -1.0, "BEAR", "LOW"),
        (0.0, 1.0, "BULL", "LOW"),
    ],
)
def test_sign_and_equality(u2, u5, trend, vol):
    w = oracle_window(endpoint=(0.0, u2, 0.0, 0.0, u5))
    state = classify(w, threshold())
    assert (state.trend, state.volatility) == (trend, vol)
    assert state.window_id == w.window_id


@pytest.mark.parametrize("changes,missing,expected", [(11, 2, False), (12, 2, True), (12, 0, True)])
def test_valid_denominator_inclusive_change(changes, missing, expected):
    w = oracle_window(changes=changes, missing=missing)
    result = variation(w)
    assert result["valid_steps"] == 48 - missing
    assert result["changed_steps"] == changes
    assert result["A_t"] == changes / (48 - missing)
    assert result["qualifies"] is expected


def test_u1_never_counts_and_invalid_zero_is_not_change():
    assert variation(oracle_window(changes=30, u1_only=True))["changed_steps"] == 0
    assert variation(oracle_window(changes=30, delta=0.999999))["changed_steps"] == 0
    assert (
        variation(oracle_window(changes=0, missing=2, endpoint=(0.0, 2.0, 0.0, 0.0, 2.0)))[
            "changed_steps"
        ]
        == 0
    )


@pytest.mark.parametrize(
    "case", ["unknown", "nat", "future", "stale", "source", "nonfinite", "mask", "endpoint", "grid"]
)
def test_market_negative_publication_mask_and_grid(case):
    w = oracle_window(missing=2)
    assert w.market.values is not None
    if case in {"unknown", "nat", "future", "stale", "source"}:
        s = w.stamps[0]
        values = {
            "unknown": {"available_at": None},
            "nat": {"available_at": pd.NaT},
            "future": {"available_at": s.timestamp + pd.Timedelta(nanoseconds=1)},
            "stale": {"period_end": s.timestamp - pd.Timedelta(seconds=5401)},
            "source": {"evidence_ids": ("SYN:OTHER",)},
        }
        kwargs = {"stamps": (replace(s, **values[case]),) + w.stamps[1:]}
    elif case == "nonfinite":
        kwargs = {
            "market": replace(
                w.market, values=((0.0, float("nan"), 0.0, 0.0, 0.0),) + w.market.values[1:]
            )
        }
    elif case == "mask":
        kwargs = {"market": replace(w.market, valid_mask=(False,) + w.market.valid_mask[1:])}
    elif case == "endpoint":
        kwargs = {"market": replace(w.market, valid_mask=w.market.valid_mask[:-1] + (False,))}
    else:
        kwargs = {
            "market": replace(
                w.market,
                scheduled_ends=(w.market.scheduled_ends[0] + pd.Timedelta(hours=1),)
                + w.market.scheduled_ends[1:],
            )
        }
    with pytest.raises(ValueError):
        replace(w, **kwargs)
    with pytest.raises(ValueError):
        classify(w, replace(threshold(), scaler_id="SYN:WRONG"))
    with pytest.raises(ValueError):
        classify(w, replace(threshold(), fitted_at=pd.Timestamp("2021-01-01T00:00Z")))


def test_first_eligible_anchor_missing_day_breaks_episode_and_support():
    days = tuple(str(d.date()) for d in schedule("2020-08-03", "2020-12-31").index)[:100]
    states = tuple(
        Regime((day, 2), "BULL", "HIGH", "SYN:W", "SYN:THRESHOLD")
        for i, day in enumerate(days)
        if i not in (10, 21)
    )
    # Three10-session episodes followed by70-session episode; >=30 and>=3.
    result = occupancy(states, days)
    bull = result["states"]["trend:BULL"]
    assert (bull["sessions"], bull["episodes"]) == (98, 3)
    assert bull["support"] == "SUPPORTED_DESCRIPTIVE_ONLY"
    assert result["unavailable_sessions"] == 2 and result["origin_observations"] == 98
    changed = states + (Regime((days[0], 1), "BEAR", "LOW", "SYN:OTHER", "SYN:THRESHOLD"),)
    report = occupancy(changed, days)
    assert report["anchors"][days[0]] == 1 and report["within_day_changes"] == [days[0]]
    assert report["states"]["trend:BULL"]["sessions"] == 97
    with pytest.raises(ValueError, match="UNIQUE"):
        occupancy(states + (states[0],), days)
    with pytest.raises(ValueError, match="CONTIGUOUS"):
        occupancy(states, days[:1] + days[2:])


@pytest.mark.parametrize("n,episodes,supported", [(29, 3, False), (30, 2, False), (30, 3, True)])
def test_exact_thirty_sessions_three_episodes(n, episodes, supported):
    days = tuple(str(d.date()) for d in schedule("2020-08-03", "2020-12-31").index)[:40]
    chosen = list(range(n))
    # Put gaps after10 and20; maintain exactly n observed sessions.
    if episodes >= 2:
        chosen = [i if i < 10 else i + 1 for i in chosen]
    if episodes >= 3:
        chosen = [i if i < 21 else i + 1 for i in chosen]
    states = tuple(Regime((days[i], 1), "BULL", "HIGH", "SYN:W", "SYN:T") for i in chosen)
    row = occupancy(states, days)["states"]["trend:BULL"]
    assert (row["sessions"], row["episodes"]) == (n, episodes)
    assert (row["support"] == "SUPPORTED_DESCRIPTIVE_ONLY") is supported


def test_mc2_twenty_percent_and_sessions_no_activation_order_invariant():
    days = tuple(
        str(d.date())
        for d in schedule("2020-08-03", "2021-01-29").index
        if execution_plan(CALENDAR.clock(str(d.date())), 1).calendar_valid
    )[:100]
    windows = tuple(oracle_window(day, changes=12 if i < 20 else 0) for i, day in enumerate(days))
    result = mc2_readiness(windows)
    assert result == mc2_readiness(tuple(reversed(windows)))
    assert result["fraction"] == 0.2 and len(result["qualifying_sessions"]) == 20
    assert result["synthetic_structural_condition"] is True
    assert result["activation"] == "MC2_NOT_ACTIVATED"
    assert not mc2_readiness(windows[:19] + (oracle_window(days[19], changes=0),) + windows[20:])[
        "synthetic_structural_condition"
    ]
    with pytest.raises(ValueError):
        mc2_readiness(windows + (windows[0],))
    with pytest.raises(ValueError):
        mc2_readiness((replace(windows[0], phase="DISCLOSURE"),))
    # 20 qualifying origins from only10 days don't satisfy20 distinct sessions.
    same_days = tuple(
        oracle_window(day, origin, changes=12) for day in days[:10] for origin in (1, 2)
    )
    assert not mc2_readiness(same_days)["synthetic_structural_condition"]


def test_calendar_dst_earlyclose_overnight_stamps():
    with pytest.raises(ValueError, match="STRUCTURALLY_INELIGIBLE"):
        oracle_window("2020-11-27")
    for day in ("2020-11-30", "2021-03-15", "2020-11-02"):
        w = oracle_window(day)
        assert len(w.stamps) == 48 and all(s.available_at == s.timestamp for s in w.stamps)
        plan = execution_plan(CALENDAR.clock(day), 1)
        assert w.market.scheduled_ends[-1] == plan.cutoff
        assert any(
            (b - a) > pd.Timedelta(hours=1)
            for a, b in zip(w.market.scheduled_ends, w.market.scheduled_ends[1:])
        )


def test_paired_only_matured_same_source_fit_target_state_and_no_inference():
    state = classify(oracle_window(), threshold())
    t = pd.Timestamp("2020-10-05T14:30Z")
    a = PairedRecord(
        "MC0",
        state,
        (0.0,) * 5,
        (1.0,) * 5,
        "SYN:S",
        "SYN:Y",
        "SYN:FIT",
        t - pd.Timedelta(days=1),
        t,
        t + pd.Timedelta(minutes=2),
        t + pd.Timedelta(hours=4),
        t + pd.Timedelta(hours=5),
    )
    b = replace(a, architecture="MC1", scores=(1.0,) * 5)
    result = paired_report((a, b))
    assert result["daily_mean_delta_MSE"] == -1 and result["net_cost"] == "NOT_AVAILABLE"
    assert result["inference"] == "NO_INFERENCE"
    for bad in (
        replace(b, source_id="SYN:OTHER"),
        replace(b, labels=(2.0,) * 5),
        replace(b, fit_id="SYN:OTHER"),
        replace(b, cutoff=t - pd.Timedelta(minutes=1)),
        replace(b, state=replace(state, trend="BEAR")),
        replace(b, evaluated_at=t),
    ):
        with pytest.raises(ValueError):
            paired_report((a, bad))
    with pytest.raises(ValueError, match="DUPLICATE"):
        paired_report((a, b, b))
    with pytest.raises(ValueError, match="MISSING"):
        paired_report((a,))


def test_threshold_exact_training_population_and_fit_identity():
    from lstm_data.baseline_authority import replay_permission
    from lstm_data.market_features import MarketFitWindow, MarketVector, fit_synthetic_scaler
    from lstm_data.neural_market import MarketEvidence
    from lstm_data.p3_domain import MODE, Permission
    from lstm_data.regime_diagnostics import training_threshold

    permission = replay_permission(Permission(MODE))
    times = tuple(pd.Timestamp(f"2020-07-0{i}T15:30Z") for i in (1, 2, 6))
    rows = tuple(
        MarketVector(
            t, (0.0, float(i), 0.0, 0.0, 0.0), "VECTOR_VALID", ("SYN:T:" + str(i),), "SYNTHETIC"
        )
        for i, t in enumerate(times)
    )
    window = MarketFitWindow(
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        pd.Timestamp("2020-08-01T04:00Z"),
        "INNER_TRAIN",
    )
    scaler = fit_synthetic_scaler(rows, window, "SYN:TRAIN", allow_synthetic=True)
    history = MarketEvidence(
        "SYN:REGIME",
        rows,
        tuple(MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids) for v in rows),
    )
    threshold = training_threshold(history, scaler, permission)
    assert threshold.value == 0.0
    assert threshold.scaler_id and threshold.training_trace
    later = MarketVector(
        pd.Timestamp("2020-08-20T14:30Z"),
        (0.0, 1e12, 0.0, 0.0, 0.0),
        "VECTOR_VALID",
        ("SYN:LATER",),
        "SYNTHETIC",
    )
    extended = replace(
        history,
        vectors=history.vectors + (later,),
        stamps=history.stamps
        + (MarketStamp(later.timestamp, later.timestamp, later.timestamp, later.evidence_ids),),
    )
    assert training_threshold(extended, scaler, permission).value == threshold.value
    with pytest.raises(ValueError):
        training_threshold(history, scaler, Permission("SCIENTIFIC_REAL"))
    with pytest.raises(ValueError):
        replace(history, stamps=history.stamps + (history.stamps[0],)).validate()
