"""Independent clock, missing-price, display-rank and no-IO boundary oracles."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf20_rank_visuals import display_ranks, transitions
from lstm_data.hf20_s4_clock import complete_prices, endpoint, month_guard, sessions


@pytest.mark.parametrize(
    "hour,expected",
    [
        (9, "2024-06-17 13:30"),
        (10, "2024-06-17 14:30"),
        (11, "2024-06-17 15:30"),
        (12, "2024-06-18 10:00"),
        (13, "2024-06-18 11:00"),
        (14, "2024-06-18 12:00"),
        (15, "2024-06-18 13:00"),
    ],
)
def test_normal_calendar_oracle(hour, expected):
    c = sessions("2024-06-17", "2024-06-21")
    t = pd.Timestamp(f"2024-06-17 {hour}:30", tz="America/New_York")
    assert endpoint(t, c) == pd.Timestamp(expected, tz="America/New_York")
    # Independent enumeration:240 real minute intervals, including15:30–16:00.
    actual = pd.DatetimeIndex([])
    for o, e in c.itertuples(index=False, name=None):
        actual = actual.append(pd.date_range(o, e, freq="min", inclusive="left"))
    selected = actual[actual >= t][:240]
    assert selected[-1] + pd.Timedelta(minutes=1) == endpoint(t, c)
    if hour == 12:
        assert (
            sum(
                (selected >= pd.Timestamp("2024-06-17 15:30", tz="America/New_York"))
                & (selected < pd.Timestamp("2024-06-17 16:00", tz="America/New_York"))
            )
            == 30
        )


@pytest.mark.parametrize(
    "origin,expected",
    [
        ("2024-11-29 12:30", "2024-12-02 13:00"),
        ("2024-03-08 15:30", "2024-03-11 13:00"),
        ("2024-11-01 15:30", "2024-11-04 13:00"),
        ("2024-05-24 15:30", "2024-05-28 13:00"),
    ],
)
def test_early_close_dst_weekend_holiday(origin, expected):
    t = pd.Timestamp(origin, tz="America/New_York")
    c = sessions(str(t.date()), str((t + pd.Timedelta(days=7)).date()))
    assert endpoint(t, c) == pd.Timestamp(expected, tz="America/New_York")


def test_closed_origin_rejected():
    with pytest.raises(ValueError, match="REGULAR_SESSION"):
        endpoint(
            pd.Timestamp("2024-06-17 16:00", tz="America/New_York"),
            sessions("2024-06-17", "2024-06-21"),
        )


def test_missing_one_stock_not_filled():
    p = np.ones((2, 20))
    p[1, 3] = np.nan
    np.testing.assert_array_equal(complete_prices(p), [True, False])
    with pytest.raises(ValueError, match="COMPLETE20"):
        complete_prices(p[:, :19])


@pytest.mark.parametrize("month", ["2010-06", "2025-01", "2026-01", "2026-03"])
def test_guard_before_any_file_io(month):
    with patch.object(Path, "open", side_effect=AssertionError("IO_FORBIDDEN")) as guard:
        with pytest.raises(ValueError, match="BEFORE_IO"):
            month_guard(month)
        assert guard.call_count == 0


def test_ties_best_rank_and_transition_gaps():
    values = np.arange(20)[None, :].repeat(3, axis=0).astype(float)
    values[2] = 0
    d = display_ranks(values)
    assert d[0, -1] == 1 and d[0, 0] == 20
    assert np.all(d[2] == 10.5)
    frame = pd.DataFrame(
        dict(
            score=values.ravel(),
            ticker=np.tile(SYMBOLS, 3),
            origin_id=np.repeat(
                [
                    "2024-01-04T15:30:00+00:00",
                    "2024-01-04T16:30:00+00:00",
                    "2024-01-08T15:30:00+00:00",
                ],
                20,
            ),
            session_date_et=np.repeat(["2024-01-04", "2024-01-04", "2024-01-08"], 20),
        )
    )
    m, s = transitions(frame, 2024, "N0")
    assert set(m.relation) == {"WITHIN_SESSION_ADJACENT", "ACROSS_SESSION"}
    assert s.loc[s.relation.eq("ACROSS_SESSION"), "jaccard"].isna().all()


def test_opening_inputs_cannot_see_current_hour_or_future():
    from lstm_data.hf1m_ft16_source import COMMON, ORDER
    from lstm_data.hf20_s4_witnesses import assemble

    rng = np.random.default_rng(11)
    common = rng.normal(size=(60, 20, 15)).astype(np.float32)
    m2 = rng.normal(size=(60, 20, 7)).astype(np.float32)
    rows = pd.DataFrame(
        dict(session_date_et=["2024-06-18"], first_step=[0], entry_index=[47], context=[6])
    )
    before = assemble(rows, common, m2)
    common[48:] = 1e10
    m2[48:] = 1e10
    np.testing.assert_array_equal(before, assemble(rows, common, m2))
    np.testing.assert_array_equal(
        before[0, :, :, ORDER.index("M1")], common[:48, :, COMMON.index("M1")].T
    )
    np.testing.assert_array_equal(before[0, :, :, ORDER.index("M2")], m2[:48, :, 6].T)
    with pytest.raises(ValueError, match="CONTEXT48"):
        assemble(rows.assign(first_step=1), common, m2)


def test_exact_objectives_hierarchical_weights_and_selector():
    import torch

    from lstm_data.hf20_ranking import (
        RankSelector,
        origin_ic,
        origin_weights,
        rank_targets,
        row_loss,
    )

    returns = np.arange(80).reshape(4, 20).astype(float)
    returns[0, :2] = 1
    q = rank_targets(returns)
    assert q[0, 0] == q[0, 1]
    weights = origin_weights(np.array(["A", "A", "A", "B"]))
    np.testing.assert_allclose(weights[:3].sum(), 0.5)
    assert weights[3] == 0.5
    s = torch.zeros((4, 20), dtype=torch.float32)
    r = torch.tensor(returns)
    y = torch.tensor(returns / 20, dtype=torch.float32)
    np.testing.assert_allclose(row_loss("NR", s, r, y, 2).numpy(), q**2 / 20, rtol=3e-7, atol=1e-8)
    np.testing.assert_allclose(
        row_loss("T2R", s, r, y, 2).numpy(),
        np.arcsinh(y.numpy() / 2) ** 2 / 20,
        rtol=3e-7,
        atol=1e-8,
    )
    assert np.isnan(origin_ic(returns, np.zeros_like(returns))).all()
    selector = RankSelector()
    assert selector.observe(1, -0.01)
    assert not selector.observe(2, selector.best + 0.001)
    assert selector.observe(3, -0.0089)
    assert selector.selected == 3


def test_missing_authority_blocks_before_source_or_training(tmp_path):
    from lstm_data.hf20_s4_authority import authorize

    with pytest.raises(ValueError, match="LIVE_AUTHORITY_MISSING"):
        authorize(tmp_path)


def test_sequential_ledger_no_retry_or_skipped_gate():
    from lstm_data.config import fingerprint
    from lstm_data.hf20_s4_authority import RUNS, validate

    history = []

    def row(run, status, count):
        return dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            run_id=run,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
        )

    history.append(row(RUNS[0], "STARTED", 107))
    with pytest.raises(ValueError, match="PREVIOUS_PASS"):
        validate(history + [row(RUNS[1], "STARTED", 108)])
    with pytest.raises(ValueError, match="ILLEGAL_TRANSITION"):
        validate(history + [row(RUNS[0], "COMPLETED", 107)])
    failed = history + [row(RUNS[0], "FAILED", 107)]
    validate(failed)
    history = failed
    with pytest.raises(ValueError, match="PREVIOUS_PASS"):
        validate(history + [row(RUNS[0], "STARTED", 108)])
    history = history[:1]
    for status in ("CALIBRATED", "REFITTING", "COMPLETED"):
        history.append(row(RUNS[0], status, 107))
    history.append(row(RUNS[1], "STARTED", 108))
    validate(history)


def test_visual_and_numerical_evidence_both_required(tmp_path):
    from lstm_data.hf20_s4_diagnostics import gate

    with pytest.raises(ValueError, match="NUMERICAL"):
        gate(tmp_path, {})
    (tmp_path / "NUMERICAL_DIAGNOSTICS_PASS.json").write_text('{"status":"PASS_NUMERICAL"}')
    with pytest.raises(ValueError, match="VISUAL"):
        gate(tmp_path, {})


def test_genuine_component_join_conserves_and_rejects_missing_endpoint():
    from lstm_data.hf20_s4_diagnostics import join_components

    f = pd.DataFrame(dict(origin_id=["x", "y"], ticker=["A", "A"], return_4h=[0.03, 0.04]))
    c = pd.DataFrame(
        dict(
            origin_id=["x", "y"],
            ticker=["A", "A"],
            direct_return=[0.03, 0.04],
            origin_to_close=[0.01, np.nan],
            close_to_next_open=[0.005, np.nan],
            next_open_to_exit=[0.015, np.nan],
            decomposition_supported=[True, False],
            decomposition_status=["SUPPORTED", "UNAVAILABLE"],
        )
    )
    result = join_components(f, c)
    assert len(result) == 2 and np.isnan(result.origin_to_close.iloc[1])
    with pytest.raises(AssertionError):
        join_components(f, c.iloc[:1])
    bad = c.copy()
    bad.loc[0, "close_to_next_open"] = 0.5
    with pytest.raises(AssertionError):
        join_components(f, bad)
