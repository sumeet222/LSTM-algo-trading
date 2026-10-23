"""Independent mathematical and temporal-boundary oracles for P022; zero fits."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.objective_screen_audit import average_precision, month_ci, origin_ic, threshold_bins
from lstm_data.objective_screen_authority import ensure, validate_history
from lstm_data.objective_screen_loss import ARMS, RUNS, Objective, classes, fit_recipe, model_for
from lstm_data.objective_screen_metrics import regression
from lstm_data.objective_screen_run import Selector
from lstm_data.objective_screen_source import prefix_array, scoped_view
from lstm_data.visualization.hf1m_long import LongStudy


def recipe() -> dict:
    return dict(scale=1.0, q95_abs_y=2.0, q95_abs_z=1.0, class_weights=[4.0, 1.0, 3.0])


@pytest.mark.parametrize("arm", ARMS)
def test_independent_objective_session_and_pair_accounting(arm: str) -> None:
    y = np.linspace(-3, 4, 80).reshape(2, 2, 20)
    mask = np.array([[True, False], [True, True]])
    output = np.cos(np.arange(80)).reshape(2, 2, 20)
    if arm == "E1":
        output = np.stack([output, -output, output / 2], axis=-1)
    tensor = torch.tensor(output, dtype=torch.float64, requires_grad=True)
    terms = Objective(arm, recipe()).contributions(tensor, torch.tensor(y), torch.tensor(mask))
    expected = []
    for day in range(2):
        row_loss = []
        coeff = []
        pairs = []
        for origin in range(2):
            if not mask[day, origin]:
                continue
            for stock in range(20):
                target = y[day, origin, stock]
                p = output[day, origin, stock]
                if arm == "E1":
                    label = 0 if target < -2 else 2 if target > 2 else 1
                    logsum = float(np.log(np.exp(p).sum()))
                    row_loss.append(logsum - p[label])
                    coeff.append([4.0, 1.0, 3.0][label])
                else:
                    error = np.arcsinh(target) - p
                    row_loss.append(
                        error**2 if arm != "H2" or abs(error) <= 1 else 2 * abs(error) - 1
                    )
                    coeff.append(2.0 if arm == "W1" and abs(np.arcsinh(target)) > 1 else 1.0)
            if arm == "R1":
                pl = []
                for i in range(20):
                    for j in range(i + 1, 20):
                        sign = np.sign(y[day, origin, i] - y[day, origin, j])
                        if sign:
                            pl.append(
                                np.logaddexp(
                                    0, -sign * (output[day, origin, i] - output[day, origin, j])
                                )
                            )
                assert len(pl) == 190
                pairs.append(np.mean(pl))
        expected.append(
            np.average(row_loss, weights=coeff) + (0.5 * np.mean(pairs) if pairs else 0)
        )
    actual = terms["total"].sum(dim=(1, 2))
    np.testing.assert_allclose(actual.detach(), expected, rtol=1e-13)
    np.testing.assert_allclose(terms["normalized_weight"].sum(dim=(1, 2)), [1, 1])
    np.testing.assert_allclose(
        terms["total"].detach(), (terms["pointwise"] + terms["pairwise"]).detach()
    )
    assert not bool(terms["total"][0, 1].any())
    actual.mean().backward()
    assert tensor.grad is not None and bool(torch.isfinite(tensor.grad).all())
    assert bool(tensor.grad[mask].abs().sum() > 0)


def test_rank_symmetry_ties_and_gradients() -> None:
    y = torch.arange(20, dtype=torch.float64).reshape(1, 1, 20)
    p = torch.zeros_like(y, requires_grad=True)
    m = torch.ones((1, 1), dtype=torch.bool)
    policy = Objective("R1", recipe())
    loss = policy.contributions(p, y, m)
    assert loss["pair_losses"].shape[-1] == 190
    assert float(loss["pairwise"].sum().detach()) == pytest.approx(0.5 * np.log(2))
    loss["pairwise"].sum().backward()
    assert p.grad is not None and p.grad[0, 0, 0] > 0 and p.grad[0, 0, -1] < 0
    torch.testing.assert_close(policy.loss(p, y, m), policy.loss(-p, -y, m))
    ties = policy.contributions(p, torch.zeros_like(y), m)
    assert float(ties["pairwise"].sum().detach()) == 0


def test_events_and_fitting_prefix() -> None:
    np.testing.assert_array_equal(classes(np.array([-3.0, -2, 0, 2, 3]), 2), [0, 1, 1, 1, 2])
    y = np.arange(-100, 101, dtype=float)
    w = np.full(len(y), 1 / len(y))
    r = fit_recipe(y, w, 1.0)
    assert r["q95_abs_y"] == np.quantile(abs(y), 0.95)
    assert sum(r["counts"]) == 201
    assert r["class_weights"][1] == 1
    with pytest.raises(ValueError, match="ABSENT_CLASS"):
        fit_recipe(np.arange(1, 101, dtype=float), np.full(100, 0.01), 1.0)


def test_backbone_and_parameter_parity() -> None:
    models = {arm: model_for(arm) for arm in ARMS}
    for arm, model in models.items():
        assert sum(p.numel() for p in model.parameters()) == (6499 if arm == "E1" else 6433)
        for key, value in models["H2"].lstm.state_dict().items():
            assert torch.equal(value, model.lstm.state_dict()[key])


def test_prefix_does_not_decode_later_values(tmp_path: Path) -> None:
    p = tmp_path / "components.npz"
    a = np.arange(240).reshape(10, 4, 6)
    np.savez_compressed(p, values=a)
    np.testing.assert_array_equal(prefix_array(p, "values", 3), a[:3])
    with pytest.raises(ValueError):
        prefix_array(p, "values", 11)
    f = tmp_path / "fortran.npz"
    np.savez_compressed(f, values=np.asfortranarray(a))
    with pytest.raises(ValueError):
        prefix_array(f, "values", 3)


def test_stage_guard_before_access() -> None:
    with patch.object(Path, "read_text", side_effect=AssertionError("read")):
        empty = LongStudy(Path("."), {}, {}, Path("."), {}, "test")
        for name in ["development", "refit", "2026", "confirmation", "unknown"]:
            with pytest.raises(ValueError, match="ROLE_NOT_AUTHORIZED"):
                scoped_view(empty, name, stage=1)


def test_ties_bins_ap_and_month_resampling() -> None:
    np.testing.assert_array_equal(
        threshold_bins(np.array([-1, 0, 1, 2, 5, 6, np.nan]), [0, 1, 2, 3, 4, 5]),
        [0, 1, 1, 2, 5, 6, 7],
    )
    y = np.array([False, True, False, True])
    w = np.full(4, 0.25)
    assert average_precision(y, np.zeros(4), w) == 0.5
    assert average_precision(y, y.astype(float), w) == 1.0
    assert np.isnan(origin_ic(np.zeros(40), np.arange(40))).all()
    np.testing.assert_allclose(origin_ic(np.arange(40), np.arange(40)), [1, 1])
    d = pd.Series([0.2, 0.2, 0.2], index=["2020-01-01", "2020-01-02", "2020-02-03"])
    np.testing.assert_allclose(month_ci(d), [0.2, 0.2])


def test_selector_boundary_and_no_extra_start() -> None:
    s = Selector()
    assert s.observe(1.0)
    assert s.observe(0.999)
    for _ in range(10):
        assert not s.observe(1.0)
    assert s.epoch == 12 and s.selected == 2 and s.status == "PATIENCE_STOP"
    with pytest.raises(ValueError):
        s.observe(0.5)
    with pytest.raises(ValueError, match="LIVE_FOUR_RUN_APPROVAL"):
        ensure(Path("not-read"), None, RUNS[0])
    history = []
    for arm, run in enumerate(RUNS):
        for status in ["STARTED", "CALIBRATED", "REFITTING", "COMPLETED"]:
            history.append(
                dict(
                    sequence=len(history) + 1,
                    previous=fingerprint(history),
                    run_id=run,
                    status=status,
                    global_started_pairs=37 + arm,
                    effective_ceiling=200,
                )
            )
    assert validate_history(history) == history
    extra = dict(
        sequence=len(history) + 1,
        previous=fingerprint(history),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=41,
        effective_ceiling=200,
    )
    with pytest.raises(ValueError, match="NO_EXTRA_RETRY"):
        validate_history(history + [extra])
    failed = history[:1]
    failed.append(
        dict(
            sequence=2,
            previous=fingerprint(failed),
            run_id=RUNS[0],
            status="FAILED",
            global_started_pairs=37,
            effective_ceiling=200,
        )
    )
    validate_history(failed)
    with pytest.raises(ValueError, match="PRIOR_MUST_COMPLETE"):
        validate_history(
            failed
            + [
                dict(
                    sequence=3,
                    previous=fingerprint(failed),
                    run_id=RUNS[1],
                    status="STARTED",
                    global_started_pairs=38,
                    effective_ceiling=200,
                )
            ]
        )


def test_float32_online_metrics_use_float64_conservation() -> None:
    y = np.linspace(-20, 20, 80, dtype=np.float32)
    p = np.cos(y).astype(np.float32)
    days = np.repeat(["2020-01-02", "2020-01-03"], 40)
    result = regression(y, p, days)
    w = np.full(80, 1 / 80)
    assert result["mse"] == pytest.approx(w @ ((p.astype(float) - y.astype(float)) ** 2))
    assert result["excess_mse"] == pytest.approx(
        result["prediction_energy"] - result["twice_y_pred"], abs=1e-12
    )


def test_rank_supervision_preserves_true_float64_near_ties() -> None:
    y = torch.arange(20, dtype=torch.float64).reshape(1, 1, 20)
    y[0, 0, 1] = 1.0 + 1e-9
    y[0, 0, 2] = 1.0
    rounded = y.float()
    assert rounded[0, 0, 1] == rounded[0, 0, 2]
    p = torch.arange(20, dtype=torch.float32).reshape(1, 1, 20)
    m = torch.ones((1, 1), dtype=torch.bool)
    terms = Objective("R1", recipe()).contributions(p, rounded, m, y)
    expected = []
    for i in range(20):
        for j in range(i + 1, 20):
            d = np.sign(float(y[0, 0, i] - y[0, 0, j]))
            if d:
                expected.append(np.logaddexp(0, -d * float(p[0, 0, i] - p[0, 0, j])))
    assert float(terms["pairwise"].sum()) == pytest.approx(0.5 * np.mean(expected), rel=1e-6)
