"""Small S1/S2 numerical/rehearsal oracles. No real dataset or real fit."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.hf20_ranking import (
    RankSelector,
    daily_ic,
    linear_pair_value_gradient,
    origin_ic,
    origin_weights,
    pair_terms,
    rank_targets,
    ranks,
    ridge,
    row_loss,
)
from lstm_data.hf20_ranking_data import FoldData, fold_masks, metadata
from lstm_data.neural_engine import SharedLSTM, optimizer, seed_all


def test_ranks_ties_and_monotone_units():
    y = np.array([[2.0, 2.0, 4.0, 1.0], [1.0, 2.0, 3.0, 4.0]])
    np.testing.assert_array_equal(ranks(y)[0], [2.5, 2.5, 4, 1])
    np.testing.assert_array_equal(ranks(y), ranks(np.arcsinh((y - 1) / 0.3)))
    assert np.isnan(origin_ic(y, np.zeros_like(y))).all()
    np.testing.assert_allclose(rank_targets(y).sum(1), 0, atol=1e-7)
    perm = [3, 0, 2, 1]
    np.testing.assert_array_equal(rank_targets(y[:, perm]), rank_targets(y)[:, perm])


def test_session_weights_not_origin_count():
    days = np.array(["a", "a", "b"])
    np.testing.assert_array_equal(origin_weights(days), [0.25, 0.25, 0.5])
    y = np.tile(np.arange(4), (3, 1)).astype(float)
    p = y.copy()
    p[-1] *= -1
    assert daily_ic(y, p, days) == pytest.approx(0)


def test_pair_loss_manual_gradient_and_endpoint_allocation():
    score = torch.tensor([[0.0, 0.2, -0.1]], dtype=torch.float64, requires_grad=True)
    actual = torch.tensor([[1.0, 3.0, 2.0]], dtype=torch.float64)
    raw, allocated = pair_terms(score, actual)
    direction = np.array([-1.0, -1.0, 1.0])
    gap = np.array([-0.2, 0.1, 0.3])
    expected = np.logaddexp(0, -direction * gap)
    np.testing.assert_allclose(raw.detach(), expected[None, :], rtol=1e-14)
    expected_allocation = np.array(
        [
            (expected[0] + expected[1]) / 6,
            (expected[0] + expected[2]) / 6,
            (expected[1] + expected[2]) / 6,
        ]
    )
    np.testing.assert_allclose(allocated.detach(), expected_allocation[None, :])
    allocated.sum().backward()
    eps = 1e-6
    for k in range(3):
        a = score.detach().clone()
        b = a.clone()
        a[0, k] += eps
        b[0, k] -= eps
        finite = (pair_terms(a, actual)[1].sum() - pair_terms(b, actual)[1].sum()) / (2 * eps)
        assert score.grad is not None
        assert float(score.grad[0, k]) == pytest.approx(float(finite), abs=1e-9)
    raw20, a20 = pair_terms(torch.zeros(1, 20), torch.arange(20)[None, :].float())
    assert raw20.shape == (1, 190)
    assert float(a20.sum()) == pytest.approx(np.log(2), abs=1e-7)


def test_true_pair_ties_and_empty_fail_closed():
    raw, a = pair_terms(torch.zeros(1, 4), torch.tensor([[1.0, 1.0, 2.0, 3.0]]))
    assert raw.shape == (1, 6) and float(raw[0, 0]) == 0
    assert float(a.sum()) == pytest.approx(np.log(2), abs=1e-7)
    with pytest.raises(ValueError, match="NO_VALID"):
        pair_terms(torch.zeros(1, 20), torch.zeros(1, 20))


def test_selector_negative_values_raw_and_qualification_are_separate():
    s = RankSelector()
    assert s.observe(1, -0.2)
    assert not s.observe(2, s.best + 0.001)
    assert s.raw_epoch == 2 and s.selected == 1
    assert s.observe(3, -0.198)
    for epoch in range(4, 14):
        s.observe(epoch, -0.3)
    assert not s.stop(11) and s.stop(13)
    with pytest.raises(ValueError, match="UNDEFINED"):
        s.observe(14, float("nan"))


def test_linear_penalty_mean_objective_and_matrix_free_gradient():
    rng = np.random.default_rng(42)
    x = rng.normal(size=(3, 4, 768)) * 0.02
    y = np.tile(np.arange(4), (3, 1)).astype(float)
    w = np.array([0.25, 0.25, 0.5])

    def stream():
        yield x, y, w

    coef = ridge(stream, 0.1)
    a = np.column_stack([x.reshape(-1, 768), np.ones(12)])
    weight = np.repeat(w / 4, 4)
    q = rank_targets(y).reshape(-1)
    penalty = np.diag(np.r_[np.repeat(0.1, 768), 0.0])
    np.testing.assert_allclose(
        (a.T @ (weight[:, None] * a) + penalty) @ coef, a.T @ (weight * q), atol=1e-10
    )
    c = rng.normal(size=768) * 0.001
    value, gradient = linear_pair_value_gradient(c, stream, 0.1)
    assert np.isfinite(value)
    for k in (0, 1, 67):
        a = c.copy()
        b = c.copy()
        a[k] += 1e-6
        b[k] -= 1e-6
        finite = (
            linear_pair_value_gradient(a, stream, 0.1)[0]
            - linear_pair_value_gradient(b, stream, 0.1)[0]
        ) / 2e-6
        assert gradient[k] == pytest.approx(finite, abs=1e-8)


@pytest.mark.parametrize("year", [2025, 2026, 2020, 0])
def test_protected_year_rejected_before_any_file_access(year):
    with patch.object(Path, "read_text", side_effect=AssertionError("IO_BEFORE_GUARD")):
        with pytest.raises(ValueError, match="BEFORE_IO"):
            metadata(year)


def test_live_source_prefix_fitting_cannot_start_without_approval():
    with patch.object(Path, "read_text", side_effect=AssertionError("IO_BEFORE_APPROVAL")):
        with pytest.raises(ValueError, match="LIVE_APPROVAL_REQUIRED"):
            FoldData(live_approved=False)


def test_empty_fold_is_not_padded_or_silently_repaired():
    g = pd.DataFrame(dict(session_date_et=["2020-06-30", "2020-07-01", "2020-12-31"]))
    f = pd.DataFrame(
        dict(
            first_step=[0],
            session_date_et=["2020-06-30"],
            source_input_eligible=[False],
            label_eligible=[False],
            origin_id=["x"],
        )
    )
    with pytest.raises(ValueError, match="EMPTY"):
        fold_masks(2021, f, g)


@pytest.mark.parametrize("arm", ["NR", "PW"])
def test_synthetic_lstm_rank_learning_and_fresh_state(arm):
    torch.set_num_threads(4)
    seed_all(42)
    model = SharedLSTM()
    initial = {k: v.detach().clone() for k, v in model.state_dict().items()}
    r = np.tile(np.linspace(-1, 1, 20), (2, 1))
    x = torch.zeros(40, 48, 16)
    x[:, :, 0] = torch.tensor(r.reshape(-1, 1), dtype=torch.float32)
    actual = torch.tensor(r, dtype=torch.float64)
    opt = optimizer(model)
    model.eval()
    before = float(
        row_loss(arm, model(x).reshape(2, 20), actual, actual.float(), 1.0).sum().detach()
    )
    for _ in range(20):
        model.train()
        opt.zero_grad()
        objective = row_loss(arm, model(x).reshape(2, 20), actual, actual.float(), 1.0).sum() / 2
        objective.backward()
        assert any(p.grad is not None and float(p.grad.abs().max()) > 0 for p in model.parameters())
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        opt.step()
    model.eval()
    score = model(x).detach().numpy().reshape(2, 20)
    after = float(row_loss(arm, torch.from_numpy(score), actual, actual.float(), 1.0).sum())
    assert after < before and daily_ic(r, score, np.array(["a", "b"])) > 0.8
    # A new seed42 refit has no calibration weights/optimizer moments or persistent h/c.
    seed_all(42)
    fresh = SharedLSTM()
    assert all(torch.equal(v, initial[k]) for k, v in fresh.state_dict().items())
    fresh_opt = optimizer(fresh)
    assert not fresh_opt.state and opt.state


def test_authority_and_journal_barriers_before_io():
    from lstm_data.config import fingerprint
    from lstm_data.hf20_ranking import RUNS
    from lstm_data.hf20_ranking_authority import validate
    from lstm_data.hf20_ranking_run import authorize

    with patch.object(Path, "read_text", side_effect=AssertionError("BEFORE_AUTHORITY")):
        with pytest.raises(ValueError, match="LIVE_APPROVAL_REQUIRED"):
            authorize(Path("NOT_OPENED"), None)
    history = []

    def add(run, status, count):
        row = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            run_id=run,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
        )
        validate(history + [row])
        history.append(row)

    add(RUNS[0], "STARTED", 63)
    add(RUNS[0], "FAILED", 63)
    with pytest.raises(ValueError, match="NO_RETRY"):
        add(RUNS[0], "STARTED", 64)
    with pytest.raises(ValueError, match="NO_RETRY"):
        add(RUNS[1], "STARTED", 64)


def test_rank_checkpoint_and_complete_epoch_rehearsal(tmp_path):
    import io

    from lstm_data.hf20_ranking_run import epoch, predict

    seed_all(42)
    data = FoldData.__new__(
        FoldData
    )  # Disposable SYN fixture; never calls a real source constructor.
    data.rows = pd.DataFrame(dict(session_date_et=["SYN_A", "SYN_B"]))
    data.recipe = {"t2_scale": 1.0}
    r = np.tile(np.linspace(-1, 1, 20), (2, 1))
    x = np.zeros((2, 20, 48, 16), np.float32)
    x[:, :, :, 0] = r[:, :, None]
    positions = np.arange(2)
    model = SharedLSTM()
    opt = optimizer(model)
    with patch.object(data, "arrays", side_effect=lambda pos: (x[pos], r[pos], r[pos])):
        receipt = epoch(model, opt, data, positions, "NR", 1, "SYN_calibration", tmp_path)
        assert receipt["steps"] == 1
        p = predict(data, positions, model)
        assert np.isfinite(p).all()
        memory = io.BytesIO()
        torch.save(model.state_dict(), memory)
        memory.seek(0)
        loaded = SharedLSTM()
        loaded.load_state_dict(torch.load(memory, weights_only=True))
        np.testing.assert_array_equal(p, predict(data, positions, loaded))
        seed_all(42)
        refit = SharedLSTM()
        fresh = optimizer(refit)
        assert not fresh.state
        epoch(refit, fresh, data, positions, "NR", 1, "SYN_refit", tmp_path)
        assert fresh.state


@pytest.mark.parametrize("arm", ["T2R", "NR", "PW", "N0"])
def test_complete_synthetic_export_with_truthful_units(tmp_path, arm):
    import hashlib
    import json

    from lstm_data.hf20_ranking_diagnostics import export_diagnostics, verify_exports

    dest = tmp_path / "SYN_MODEL"
    dest.mkdir()
    data = FoldData.__new__(FoldData)
    data.symbols = tuple(f"S{i}" for i in range(20))
    data.contract = {"revision": "SYN_ONLY"}
    data.rows = pd.DataFrame(
        dict(
            origin_id=["SYN1", "SYN2"],
            session_date_et=["2020-01-02", "2020-01-03"],
            entry_end_utc=["2020-01-02T15:30Z", "2020-01-03T16:30Z"],
            exit_end_utc=["2020-01-02T19:30Z", "2020-01-03T20:30Z"],
            label_maturity_utc=["2020-01-02T19:32Z", "2020-01-03T20:32Z"],
        )
    )
    data.returns = np.tile(np.linspace(-0.01, 0.01, 20), (2, 1))
    data.recipe = {"epsilon": 0.001, "t2_scale": 1.0}
    (tmp_path / "F21_inner_recipe.json").write_text(json.dumps(data.recipe))
    data.rows[["origin_id"]].to_csv(tmp_path / "F21_inner_train_indices.csv", index=False)
    dummy = tmp_path / "SYN_BINDING_ONLY.txt"
    dummy.write_text("SYNTHETIC_NO_WEIGHTS")
    (dest / "calibration_binding.json").write_text(
        json.dumps(
            dict(
                checkpoint=str(dummy),
                checkpoint_sha256=hashlib.sha256(dummy.read_bytes()).hexdigest(),
            )
        )
    )
    score = data.returns * 4 if arm != "N0" else np.zeros((2, 20))
    quality = {
        k: np.zeros(40)
        for k in [
            "assumed_zero_minute_count",
            "price_proxy_minute_count",
            "feature_fallback_cells",
            "max_terminal_price_age_minutes",
        ]
    }
    with (
        patch.object(
            torch.optim.AdamW, "step", side_effect=AssertionError("NO_OPTIMIZER_STEP")
        ) as blocked,
        patch.object(data, "positions", return_value=np.arange(2)),
        patch.object(data, "quality_fields", return_value=quality),
    ):
        result = export_diagnostics(data, 2021, "inner_train", arm, score, dest)
        assert len(verify_exports(tmp_path, [dest / "inner_train_scores.parquet"])) == 1
        assert blocked.call_count == 0
    f = pd.read_parquet(dest / "inner_train_scores.parquet")
    assert len(f) == 40
    assert ("original_squared_error" in f) == (arm == "T2R")
    assert (result["daily_ic"] is None) == (arm == "N0")
    f.loc[0, "weight"] = float(f["weight"].iloc[0]) * 2
    f.to_parquet(dest / "inner_train_scores.parquet", index=False)
    with pytest.raises(AssertionError):
        verify_exports(tmp_path, [dest / "inner_train_scores.parquet"])


def test_future_fitted_recipe_and_protected_role_rejected_before_assembly():
    data = FoldData.__new__(FoldData)
    data.rows = pd.DataFrame(dict(session_date_et=["2020-01-02"]))
    data.cache_key = (2021, "inner")
    data.recipe = {"fit_stop_inclusive": "2023-01-23"}
    data.plans = {
        2021: (
            {"inner_stop": "2020-06-30"},
            {"inner_train": np.array([True]), "inner_validation": np.array([False])},
        )
    }
    with patch(
        "lstm_data.hf20_ranking_data.assemble", side_effect=AssertionError("NO_LOOKUP")
    ) as blocked:
        with pytest.raises(ValueError, match="FUTURE_FITTED"):
            data.arrays(np.array([0]))
        with pytest.raises(ValueError, match="PROTECTED_OR_UNKNOWN_ROLE"):
            data.positions(2021, "confirmation_2026")
        assert blocked.call_count == 0


def test_linear_solvers_recover_synthetic_rank_information():
    from lstm_data.hf20_ranking import linear_pair

    rng = np.random.default_rng(42)
    x = rng.normal(size=(24, 4, 768)) * 0.01
    x[:, :, 0] = rng.normal(size=(24, 4))
    y = x[:, :, 0].copy()

    def stream():
        yield x, y, np.repeat(1 / len(x), len(x))

    lr = ridge(stream, 0.1)
    lp, receipt = linear_pair(stream, 0.1)
    future = rng.normal(size=(8, 4, 768)) * 0.01
    future[:, :, 0] = rng.normal(size=(8, 4))
    assert np.mean(origin_ic(future[:, :, 0], future @ lp)) > 0.9
    assert np.mean(origin_ic(future[:, :, 0], future @ lr[:-1] + lr[-1])) > 0.9
    assert receipt["gradient_max"] <= 1e-5


def test_shared_model_stock_permutation_and_zero_state():
    seed_all(42)
    model = SharedLSTM().eval()
    x = torch.randn(2, 20, 48, 16)
    permutation = np.random.default_rng(42).permutation(20)
    with torch.no_grad():
        a = model(x.reshape(-1, 48, 16)).reshape(2, 20)
        b = model(x[:, permutation].reshape(-1, 48, 16)).reshape(2, 20)
        again = model(x.reshape(-1, 48, 16)).reshape(2, 20)
    torch.testing.assert_close(a[:, permutation], b, rtol=3e-7, atol=1e-7)
    torch.testing.assert_close(a, again, rtol=0, atol=0)


def test_actual_journal_writer_uses_only_disposable_synthetic_tree(tmp_path, monkeypatch):
    import json

    from lstm_data.hf20_ranking import RUNS
    from lstm_data.hf20_ranking_authority import append_neural
    from lstm_data.hf20_ranking_run import sha

    monkeypatch.chdir(tmp_path)
    Path("configs").mkdir()
    Path("reports/audit").mkdir(parents=True)
    out = Path("reports/experiments/SYN_ONLY")
    out.mkdir(parents=True)
    Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").write_text("{}")
    Path("reports/audit/SYN_prior.jsonl").write_text("SYNTHETIC_PRIOR\n")
    (out / "proposal.json").write_text("{}")
    approval_path = out / "SYN_approval.json"
    approval_path.write_text("{}")
    approval = dict(
        execution_sha256="SYN",
        neural_runs=list(RUNS),
        _approval_path=str(approval_path),
        _approval_sha256=sha(approval_path),
    )
    previous = dict(real_journal="reports/audit/SYN_prior.jsonl", budget_amendment={"SYN": True})
    with patch("lstm_data.hf20_ranking_run.code_hash", return_value="SYN"):
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            assert append_neural(out, approval, previous, RUNS[0], status, {}) == 63
        with pytest.raises(FileNotFoundError):
            append_neural(out, approval, previous, RUNS[1], "STARTED", {})
        gate = out / RUNS[0]
        gate.mkdir()
        (gate / "PASS.json").write_text(json.dumps(dict(status="PASS_TECHNICAL", files={})))
        assert append_neural(out, approval, previous, RUNS[1], "STARTED", {}) == 64
    history = [
        json.loads(x)
        for x in Path("reports/audit/track_a_real_pairs_v19_hf20_ranking.jsonl")
        .read_text()
        .splitlines()
    ]
    assert len(history) == 5


def test_exact_baseline_job_cap_and_no_extra_fit(tmp_path):
    from lstm_data.hf20_ranking_run import Journal

    journal = Journal.__new__(Journal)
    journal.out = tmp_path
    journal.baseline_jobs = 0
    journal.pending_baseline = None
    for n in range(64):
        journal.baseline(f"SYN_JOB_{n}")
        journal.baseline_done("COMPLETED")
    with pytest.raises(ValueError, match="CAP"):
        journal.baseline("SYN_UNAUTHORIZED_65")
    assert journal.baseline_jobs == 64


def test_four_fold_synthetic_report_closeout_smoke(tmp_path):
    import json

    from lstm_data.hf20_ranking_diagnostics import closeout, export_diagnostics
    from lstm_data.hf20_ranking_run import code_hash

    (tmp_path / "proposal.json").write_text(
        json.dumps(dict(execution_sha256=code_hash(), preserve_refs=[]))
    )
    jobs = [dict(status=status) for _ in range(64) for status in ("STARTED", "COMPLETED")]
    (tmp_path / "baseline_fit_jobs.jsonl").write_text("\n".join(json.dumps(j) for j in jobs))
    for year in (2021, 2022, 2023, 2024):
        data = FoldData.__new__(FoldData)
        data.symbols = tuple(f"S{i}" for i in range(20))
        data.contract = {"revision": "SYN_ONLY"}
        data.rows = pd.DataFrame(
            dict(
                origin_id=[f"SYN_{year}"],
                session_date_et=[f"{year}-02-01"],
                entry_end_utc=[f"{year}-02-01T15:30Z"],
                exit_end_utc=[f"{year}-02-01T19:30Z"],
                label_maturity_utc=[f"{year}-02-01T19:32Z"],
            )
        )
        data.returns = np.linspace(-0.01, 0.01, 20)[None, :]
        data.recipe = {"epsilon": 0.001, "t2_scale": 1.0}
        (tmp_path / f"F{year % 100}_refit_recipe.json").write_text(json.dumps(data.recipe))
        data.rows[["origin_id"]].to_csv(tmp_path / f"F{year % 100}_oos_indices.csv", index=False)
        quality = {
            k: np.zeros(20)
            for k in (
                "assumed_zero_minute_count",
                "price_proxy_minute_count",
                "feature_fallback_cells",
                "max_terminal_price_age_minutes",
            )
        }
        for arm in ("N0", "N1", "N2", "P", "LR", "LP"):
            dest = tmp_path / f"F{year % 100}_S1_{arm}"
            dest.mkdir()
            (dest / "selection.json").write_text(json.dumps({"selected": {"penalty": 1.0}}))
            np.save(dest / "refit_coefficients.npy", np.zeros(768))
            score = data.returns * (1 if arm != "N2" else -1) if arm != "N0" else np.zeros((1, 20))
            with (
                patch.object(data, "positions", return_value=np.array([0])),
                patch.object(data, "quality_fields", return_value=quality),
            ):
                export_diagnostics(data, year, "oos", arm, score, dest)
    closeout(tmp_path)
    assert len(pd.read_csv(tmp_path / "four_fold_models.csv")) == 24
    assert (tmp_path / "annual_rank_ic.html").is_file()
    assert (tmp_path / "completed_reports_v1/TRAINING_AND_SELECTION_TRACE.md").is_file()
    assert "No model promotion" in (tmp_path / "FINAL_RESEARCH_DECISION.md").read_text()
