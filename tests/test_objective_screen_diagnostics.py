"""Independent accounting, cohort and matched-role tests; no model fitting."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.objective_screen_attribution import allocations, cohort_masks, cohort_table
from lstm_data.objective_screen_diagnostics import canonical, daily_scores


def panel() -> pd.DataFrame:
    y = np.linspace(-8, 9, 1000)
    return pd.DataFrame(
        dict(
            origin_id=np.repeat(np.arange(50), 20),
            ticker=list(SYMBOLS) * 50,
            session_date_et=np.repeat([f"2020-01-{i // 2 + 1:02d}" for i in range(50)], 20),
            TG20=y,
            numerator=y / 100,
            cross_section_mad=np.repeat(np.linspace(0.01, 0.1, 50), 20),
            raw_net_output=np.sin(y),
            logit_NEG=np.sin(y),
            logit_NORMAL=np.cos(y),
            logit_POS=-np.sin(y),
        )
    )


@pytest.mark.parametrize("arm", ["H2", "W1", "E1", "R1"])
def test_complete_accounting_and_disjoint_cohorts(arm: str) -> None:
    f = panel()
    recipe = dict(scale=1.0, q95_abs_z=2.0, q95_abs_y=7.0, class_weights=[4.0, 1.0, 4.0])
    f, pairs = allocations(f, arm, recipe)
    np.testing.assert_allclose(f.total.sum(), f.pointwise.sum() + f.pairwise.sum())
    np.testing.assert_allclose(f.ordinary_weight.sum(), 1)
    masks, thresholds = cohort_masks(f, f)
    result = cohort_table(f, masks, thresholds)
    assert masks["TARGET_RANK_TOP1"].sum() == 10
    assert masks["TARGET_RANK_TOP5"].sum() == 50
    assert masks["RANGE_ABS_0.99"].sum() != 10
    for pct in (1, 5):
        np.testing.assert_array_equal(masks[f"TARGET_RANK_TOP{pct}"], masks[f"Z_RANK_TOP{pct}"])
    assert float(
        result.loc[result.cohort.eq("ALL"), "weighted_loss_share_pct"].iloc[0]
    ) == pytest.approx(100)
    if arm == "R1":
        assert len(pairs) == 50 * 190 and pairs.valid.all()
        assert pairs.weighted_pair_loss.sum() == pytest.approx(f.pairwise.sum(), rel=1e-6)
    else:
        assert pairs.empty and f.pairwise.sum() == 0
    shifted = f.copy()
    shifted["TG20"] = f.TG20 * 100
    _, fixed = cohort_masks(shifted, f)
    assert fixed["RANGE_ABS_0.99"] == thresholds["RANGE_ABS_0.99"]


def test_canonical_population_and_undefined_zero_rank() -> None:
    f = panel()
    pd.testing.assert_frame_equal(canonical(f.iloc[::-1], f), f)
    with pytest.raises(AssertionError):
        canonical(f.iloc[:-1], f)
    d = daily_scores(f, np.zeros(len(f)), True)
    assert d.ic.isna().all() and d.top4_recall.isna().all()
    d = daily_scores(f, f.TG20.to_numpy(), True)
    np.testing.assert_allclose(d.ic, 1)
    np.testing.assert_allclose(d.top4_recall, 1)
    assert d.mse.eq(0).all()
