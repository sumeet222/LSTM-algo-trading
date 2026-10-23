"""P025 frozen-math, exact-state, phase and approval-barrier regression oracles."""

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.branch_replication_authority import ensure, predecessor_gate, require_gate, validate
from lstm_data.branch_replication_diagnostics import exact_optimizer, verify_magnitude_order
from lstm_data.branch_replication_engine import (
    contributions,
    epoch_pass,
    model_for,
    save_checkpoint,
)
from lstm_data.branch_replication_metrics import (
    binary_curve,
    corrected,
    event_metrics,
    paired_month_blocks,
)
from lstm_data.branch_replication_run import lifecycle
from lstm_data.branch_replication_spec import RUNS
from lstm_data.branch_replication_states import (
    inverse_quantiles,
    plots,
    state_analysis,
    state_cutoffs,
)
from lstm_data.config import digest, fingerprint, write_json
from lstm_data.dm_quantile_loss import model_for as qr_model
from lstm_data.dm_quantile_loss import outputs, terms
from lstm_data.hf1m_ft16_source import ref
from lstm_data.neural_engine import optimizer
from lstm_data.neural_lifecycle import state_hash
from lstm_data.objective_screen_loss import Objective, classes
from lstm_data.objective_screen_loss import model_for as event_model
from lstm_data.objective_screen_run import Selector, record_epoch
from lstm_data.objective_screen_source import scoped_view


@pytest.mark.parametrize("arm,reference", [("E1", event_model), ("QR1", qr_model)])
def test_reference_initialization_seed_only(arm, reference):
    assert state_hash(model_for(arm, 42)) == state_hash(reference(arm))
    assert state_hash(model_for(arm)) == state_hash(model_for(arm, 123))
    assert state_hash(model_for(arm)) != state_hash(reference(arm))
    m = model_for(arm)
    assert m.lstm.input_size == 16 and m.lstm.hidden_size == 32 and m.lstm.num_layers == 1
    assert m.lstm.dropout == 0
    assert sum(p.numel() for p in m.parameters()) == 6499
    exact_optimizer(m, optimizer(m))


@pytest.mark.parametrize("arm", ["E1", "QR1"])
def test_objective_scalar_and_gradient_oracles(arm):
    torch.manual_seed(100)
    y = torch.randn(2, 2, 20)
    y[0, 0, :4] = torch.tensor([-2.0, 2.0, -2.01, 2.01])
    mask = torch.tensor([[True, False], [True, True]])
    raw = torch.randn(2, 2, 20, 3, requires_grad=True)
    recipe = dict(scale=0.9, q95_abs_y=2.0, class_weights=[4.0, 1.0, 3.0])
    result = contributions(raw, y, mask, arm, recipe)
    loss = result["session_loss"].mean()
    frozen = (
        Objective("E1", recipe).loss(raw, y, mask).mean()
        if arm == "E1"
        else terms(raw, y, mask, arm, 0.9)["session_loss"].mean()
    )
    torch.testing.assert_close(loss, frozen, rtol=0, atol=0)
    torch.testing.assert_close(
        torch.autograd.grad(loss, raw, retain_graph=True)[0],
        torch.autograd.grad(frozen, raw)[0],
        rtol=0,
        atol=0,
    )
    a = raw.detach().numpy().astype(float)
    yy = y.numpy().astype(float)
    values = []
    for day in range(2):
        selected = mask[day].numpy()
        aa, bb = a[day, selected], yy[day, selected]
        if arm == "E1":
            label = classes(bb, 2.0)
            ce = (
                np.logaddexp.reduce(aa, axis=-1)
                - np.take_along_axis(aa, label[..., None], axis=-1)[..., 0]
            )
            c = np.array([4.0, 1.0, 3.0])[label]
            values.append(float((ce * c).sum() / c.sum()))
        else:
            z = np.arcsinh(bb / 0.9)
            q = np.stack(
                [
                    aa[..., 0] - np.logaddexp(0, aa[..., 1]),
                    aa[..., 0],
                    aa[..., 0] + np.logaddexp(0, aa[..., 2]),
                ],
                axis=-1,
            )
            error = z[..., None] - q
            values.append(
                float(
                    np.maximum(
                        error * np.array([0.05, 0.5, 0.95]), error * np.array([-0.95, -0.5, -0.05])
                    ).mean()
                )
            )
    np.testing.assert_allclose(float(loss.detach()), np.mean(values), rtol=3e-5, atol=2e-6)


def test_threshold_ties_and_once_only_monotone_inverse():
    np.testing.assert_array_equal(
        classes(np.array([-2.01, -2.0, 0.0, 2.0, 2.01]), 2.0), [0, 1, 1, 1, 2]
    )
    result = outputs(torch.tensor([[0.3, 2.0, -2.0]]), "QR1", 0.9)
    q = result["quantiles_z"].numpy()
    assert (np.diff(q, axis=1) >= 0).all()
    np.testing.assert_allclose(result["quantiles_y"], 0.9 * np.sinh(q), rtol=7e-7, atol=1e-7)


def test_magnitude_order_allows_representational_ties_but_never_reversal():
    y = np.array([1.0, np.nextafter(1.0, 2.0), 3.0])
    assert verify_magnitude_order(y, np.array([0.5, 0.5, 1.0])) == 1
    with pytest.raises(ValueError, match="REVERSAL"):
        verify_magnitude_order(y, np.array([0.5, 0.49, 1.0]))


def test_progress_is_mutable_only_at_snapshot(tmp_path):
    records = []
    for phase, count in [("calibration", 12), ("refit", 2)]:
        for epoch in range(1, count + 1):
            records.append(
                dict(phase=phase, training=dict(epoch=epoch, nested=dict(lr=[0.001], eps=1e-8)))
            )
            record_epoch(tmp_path, records)
    assert json.loads((tmp_path / "epochs_progress.json").read_text()) == records
    with pytest.raises(FileExistsError):
        record_epoch(tmp_path, records)
    assert len(list((tmp_path / "epoch_receipts").iterdir())) == 14


def test_selector_inclusive_and_minimum():
    s = Selector()
    assert s.observe(1.0) and s.observe(0.999)
    assert s.selected == 2
    while s.status == "CALIBRATING":
        s.observe(0.999)
    assert s.epoch == 12 and s.selected == 2


def test_checkpoint_reload_preserves_rng_and_weights(tmp_path):
    m = model_for("E1")
    rng = torch.get_rng_state().clone()
    before = state_hash(m)
    _, loaded = save_checkpoint(tmp_path / "a.pt", m, "E1", dict(test=True))
    assert torch.equal(rng, torch.get_rng_state())
    assert state_hash(loaded) == before
    with pytest.raises(FileExistsError):
        save_checkpoint(tmp_path / "a.pt", m, "E1", {})


def test_optimizer_exact_nested_floats_and_fresh_state():
    m = model_for("E1")
    opt = optimizer(m)
    assert not opt.state
    exact_optimizer(m, opt)
    opt.param_groups[0]["lr"] = 0.0010000000000001
    with pytest.raises(ValueError, match="FLOATS"):
        exact_optimizer(m, opt)


def test_inverse_weight_correction_and_tie_ap_roc():
    p = np.array([[0.2, 0.6, 0.2]])
    np.testing.assert_allclose(
        corrected(p, dict(class_weights=[4.0, 1.0, 4.0])), [[1 / 14, 12 / 14, 1 / 14]]
    )
    curve = binary_curve(np.array([True, False]), np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    assert len(curve) == 1 and curve.precision.iloc[0] == 0.5 and curve.recall.iloc[0] == 1


def test_train_weighted_tercile_ties():
    np.testing.assert_array_equal(
        inverse_quantiles(np.array([1.0, 2.0, 3.0]), np.array([0.4, 0.4, 0.2]), (1 / 3, 2 / 3)),
        [1.0, 2.0],
    )
    with pytest.raises(ValueError):
        inverse_quantiles(np.array([np.nan]), np.ones(1), (1 / 3, 2 / 3))


def test_protected_role_guard_before_reader():
    with patch("pandas.read_parquet", side_effect=AssertionError("must not read")):
        with pytest.raises(ValueError, match="ROLE_NOT_AUTHORIZED"):
            scoped_view(MagicMock(), "confirmation", stage=7)


def test_approval_required_before_files_or_step(tmp_path):
    with pytest.raises(ValueError, match="APPROVAL"):
        ensure(tmp_path / "missing", None, RUNS[0])
    plan = tmp_path / "plan.json"
    write_json(plan, {})
    with pytest.raises(ValueError, match="APPROVAL"):
        lifecycle(plan, "E1", tmp_path / "run")
    assert not (tmp_path / "run").exists()
    with pytest.raises(ValueError, match="AUTHORITY"):
        epoch_pass(
            model_for("E1"), MagicMock(), "E1", {}, 1, None, tmp_path / "updates", update=True
        )


def test_actual_next_model_barrier_missing_incomplete_rehearsal_stale(tmp_path):
    plan = tmp_path / "proposal.json"
    write_json(plan, {})
    history = [dict(run_id=RUNS[0], status="COMPLETED")]
    with pytest.raises(ValueError, match="ORDER"):
        predecessor_gate(plan, RUNS[1], [])
    with pytest.raises(FileNotFoundError):
        predecessor_gate(plan, RUNS[1], history)
    gate = tmp_path / "E1_immediate_gate.json"
    valid = dict(
        status="PASS_E1_S123",
        scope="RESEARCH_CANDIDATE",
        all_roles=4,
        objective_reconciled=True,
        reload_reconciled=True,
        evidence=[],
        proposal_sha256=digest(plan),
    )
    for change in [
        dict(all_roles=3),
        dict(objective_reconciled=False),
        dict(scope="REHEARSAL_ONLY"),
        dict(proposal_sha256="wrong"),
    ]:
        gate.write_text(json.dumps(dict(valid, **change)))
        with pytest.raises(ValueError):
            predecessor_gate(plan, RUNS[1], history)
    gate.write_text(json.dumps(valid))
    predecessor_gate(plan, RUNS[1], history)
    evidence = tmp_path / "evidence"
    evidence.write_text("bound")
    valid["evidence"] = [ref(evidence)]
    gate.write_text(json.dumps(valid))
    evidence.write_text("changed")
    with pytest.raises(ValueError):
        require_gate(gate, "E1")


def test_journal_charges_failed_and_rejects_retry_or_reorder():
    history = []
    for name, status in [(RUNS[0], "STARTED"), (RUNS[0], "FAILED")]:
        history.append(
            dict(
                sequence=len(history) + 1,
                previous=fingerprint(history),
                run_id=name,
                status=status,
                global_started_pairs=52,
                effective_ceiling=200,
            )
        )
    validate(history)
    for name in RUNS:
        extra = dict(
            sequence=3,
            previous=fingerprint(history),
            run_id=name,
            status="STARTED",
            global_started_pairs=53,
            effective_ceiling=200,
        )
        with pytest.raises(ValueError):
            validate(history + [extra])


def test_month_bootstrap_recomputes_full_day_panels():
    days = np.repeat(["2025-07-01", "2025-08-01", "2025-09-01"], 20)

    def stat(indices, pseudo):
        assert len(indices) == len(pseudo) and len(indices) % 20 == 0
        return float(len(np.unique(pseudo)))

    first = paired_month_blocks(days, stat)
    assert first == paired_month_blocks(days, stat)
    assert [x["block_months"] for x in first] == [1, 2]


def test_full_event_metric_maps_use_existing_dependencies():
    y = np.tile(np.linspace(-3.0, 3.0, 20), 2)
    p = np.column_stack([0.15 + 0.02 * np.sin(y), np.full(40, 0.7), 0.15 - 0.02 * np.sin(y)])
    f = pd.DataFrame(
        dict(
            TG20=y,
            session_date_et=np.repeat(["2025-07-01", "2025-07-02"], 20),
            p_NEG=p[:, 0],
            p_NORMAL=p[:, 1],
            p_POS=p[:, 2],
        )
    )
    recipe = dict(q95_abs_y=2.0, class_weights=[4.0, 1.0, 4.0], prevalence=[0.05, 0.9, 0.05])
    for inverse in (False, True):
        m, curve = event_metrics(f, recipe, inverse=inverse)
        assert m["ANY_AP"] > 0 and len(curve) > 0
        assert len([x for x in m["reliability"] if x["event"] == "ANY"]) == 10
        assert np.isfinite(m["ANY_AUROC"])
        assert m["constant_fit_prior"]["ANY_AP"] == pytest.approx(0.4)


def test_quantile_state_empty_ties_and_three_plots(tmp_path):
    names = [str(i) for i in range(20)]
    f = pd.DataFrame(
        dict(
            origin_id=np.repeat([1, 2], 20),
            ticker=names * 2,
            session_date_et=np.repeat(["2025-07-01", "2025-07-02"], 20),
            TG20=np.tile(np.linspace(-3.0, 3.0, 20), 2),
            quantiles_z_05=-1.0,
            quantiles_z_50=0.0,
            quantiles_z_95=1.0,
        )
    )
    states = f[["origin_id", "ticker"]].copy()
    for channel in ("V1", "M2", "Q2"):
        states[channel] = 1.0
        states["market_" + channel] = 1.0
        states[channel + "_fallback"] = False
    cut = state_cutoffs(f, states)
    table, _, response = state_analysis(
        f, states, cut, dict(scale=0.9, quantiles_z=[-2.0, 0.0, 2.0])
    )
    assert response["predicted_width_z"]["sd"] == 0
    assert table.loc[table.state.eq("V1") & table.group.eq("HIGH"), "rows"].iloc[0] == 0
    assert np.isnan(response["negative_control"]["statistic"])
    plots(table, tmp_path)
    assert len(list(tmp_path.glob("*.html"))) == 3
