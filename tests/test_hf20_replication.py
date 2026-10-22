"""Small Package017 authority/identity checks; no neural optimizer or real fit."""

import json
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.config import digest, fingerprint
from lstm_data.hf20_replication_authority import IDS, code_binding, read_rows, validate_approval
from lstm_data.hf20_training_authority import IDS as OLD_IDS
from lstm_data.hf20_training_run import checkpoint, reload_checkpoint
from lstm_data.neural_engine import SharedLSTM, seed_all
from lstm_data.neural_lifecycle import state_hash


def test_exact_seed_initialization_and_checkpoint(tmp_path):
    seed_all(123)
    model = SharedLSTM()
    seed_all(123)
    assert state_hash(model) == state_hash(SharedLSTM())
    seed_all(42)
    assert state_hash(model) != state_hash(SharedLSTM())
    binding = dict(seed=123, run_id=IDS[0], stage="REFIT_FINAL", inverse="IDENTITY")
    path = tmp_path / "model.pt"
    manifest = checkpoint(path, model, binding)
    assert state_hash(reload_checkpoint(path, binding, manifest)) == state_hash(model)
    for changed in (
        dict(seed=42),
        dict(run_id=OLD_IDS[0]),
        dict(stage="CALIBRATION_SELECTED"),
        dict(inverse="SCALE_TIMES_SINH_ONCE"),
    ):
        with pytest.raises(ValueError, match="DENIED"):
            reload_checkpoint(path, dict(binding, **changed), manifest)


def approval_files(tmp_path):
    p = dict(
        scope=dict(seed=123),
        input_contract="EXACT",
        scales="SEPARATE_TRAIN_ONLY",
        fit_deadline=(pd.Timestamp.now(tz="UTC") + pd.Timedelta(hours=1)).isoformat(),
    )
    plan, receipt = tmp_path / "plan.json", tmp_path / "receipt.json"
    plan.write_text(json.dumps(p))
    a = dict(
        status="APPROVED",
        actor_type="human",
        response_text="exact synthetic fixture",
        response_provenance="LIVE_USER_RESPONSE_IN_THIS_SESSION",
        approved_runs=list(IDS),
        proposal_sha256=digest(plan),
        code_sha256=fingerprint(code_binding()),
        input_contract=p["input_contract"],
        scales=p["scales"],
        scope=p["scope"],
    )
    receipt.write_text(json.dumps(a))
    return p, a, plan, receipt


def test_no_live_authority_no_steps(tmp_path):
    with pytest.raises(ValueError, match="LIVE_APPROVAL"):
        validate_approval(tmp_path / "absent.json", None)


@pytest.mark.parametrize(
    "field,value",
    [
        ("approved_runs", list(OLD_IDS)),
        ("actor_type", "agent"),
        ("response_provenance", "COPIED_PRIOR_APPROVAL"),
        ("proposal_sha256", "stale"),
        ("code_sha256", "stale"),
        ("input_contract", "different"),
        ("scope", dict(seed=42)),
        ("scales", "wrong_inverse"),
    ],
)
def test_consumed_or_mismatched_approval_rejected(tmp_path, field, value):
    _, a, plan, receipt = approval_files(tmp_path)
    a[field] = value
    receipt.write_text(json.dumps(a))
    with pytest.raises(ValueError, match="FRESH_TWO_PAIR"):
        validate_approval(plan, receipt)


def test_expired_authority_rejected(tmp_path):
    p, a, plan, receipt = approval_files(tmp_path)
    p["fit_deadline"] = "2020-01-01T00:00:00Z"
    plan.write_text(json.dumps(p))
    a["proposal_sha256"] = digest(plan)
    receipt.write_text(json.dumps(a))
    with pytest.raises(ValueError, match="EXPIRED"):
        validate_approval(plan, receipt)


def test_journal_chain_duplicates_order_and_failures(tmp_path):
    path = tmp_path / "journal.jsonl"
    rows = []

    def event(name, status):
        starts = sum(r["status"] == "STARTED" for r in rows) + int(status == "STARTED")
        rows.append(
            dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                run_id=name,
                status=status,
                global_started_pairs=30 + starts,
                effective_ceiling=200,
            )
        )
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))

    event(IDS[0], "STARTED")
    event(IDS[0], "FAILED")
    assert read_rows(path)[-1]["global_started_pairs"] == 31
    event(IDS[0], "STARTED")
    with pytest.raises(ValueError, match="DUPLICATE"):
        read_rows(path)
    rows.clear()
    event(IDS[1], "STARTED")
    with pytest.raises(ValueError, match="REORDER"):
        read_rows(path)
    rows.clear()
    for name in IDS:
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            event(name, status)
    assert read_rows(path)[-1]["global_started_pairs"] == 32
    path.write_bytes(path.read_bytes().rstrip(b"\n"))
    with pytest.raises(ValueError, match="TRUNCATED"):
        read_rows(path)


def test_historical_numerical_code_unchanged():
    pointer = json.loads(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_text())
    if pointer["schema"] == 7:
        pointer = json.loads(Path(pointer["previous_pointer"]["path"]).read_text())
    baseline = json.loads(Path(pointer["plan"]["path"]).read_text())
    current = code_binding()
    assert all(current[k] == v for k, v in baseline["code"].items())


def test_actual_exact_mask_and_recomputed_baseline_metrics():
    from lstm_data.hf20_replication_review import matched_frames, stock_diagnostics, summarize
    from lstm_data.visualization.hf20 import handoff, table

    root = Path.cwd()
    h = handoff(root)
    f = table(root, h, "matched_predictions_development.csv")
    matched_frames(f, f.copy())
    with pytest.raises(ValueError, match="MASK"):
        matched_frames(f, f.iloc[:-20])
    swapped = f.copy()
    swapped.iloc[[0, 1]] = swapped.iloc[[1, 0]].to_numpy()
    with pytest.raises(ValueError, match="ORDER"):
        matched_frames(f, swapped)
    _, _, metrics = summarize(f)
    old = table(root, h, "matched_metrics.csv").set_index("arm").to_dict("index")
    for row in metrics.to_dict("records"):
        assert row["MSE"] == pytest.approx(old[row["arm"]]["MSE"], abs=2e-12)
        if row["arm"] != "ZERO":
            assert row["Rank_IC"] == pytest.approx(old[row["arm"]]["Rank_IC"], abs=2e-12)
    contributions = stock_diagnostics(f, 42).groupby("arm").cross_sectional_IC_contribution.sum()
    for arm, value in contributions.items():
        assert value == pytest.approx(old[arm]["Rank_IC"], abs=2e-12)


@pytest.mark.parametrize(
    "start,end,seed,run_id",
    [
        ("2026-01-07", "2026-10-15", 123, IDS[0]),
        ("2024-07-01", "2024-07-02", 123, IDS[0]),
        ("2025-04-10", "2025-04-10", 42, IDS[0]),
        ("2025-04-10", "2025-04-10", 123, OLD_IDS[0]),
    ],
)
def test_seed123_ui_preio_guards(monkeypatch, start, end, seed, run_id):
    from lstm_data.visualization.hf20 import predictions
    from lstm_data.visualization.loaders import ViewUnavailable

    def forbidden(*args, **kwargs):
        raise AssertionError("Numerical read before guard")

    monkeypatch.setattr(pd, "read_csv", forbidden)
    with pytest.raises(ViewUnavailable):
        predictions(Path("/absent"), start, end, "AAPL", run_id, seed=seed)


def test_released_seed123_matches_and_real_dashboard():
    import numpy as np
    from streamlit.testing.v1 import AppTest

    from lstm_data.visualization.hf20 import REPLICATION_CONFIG, handoff, predictions

    root = Path.cwd()
    if not (root / REPLICATION_CONFIG).is_file():
        pytest.skip("Seed123 not yet completed/released; no fabricated model is substituted")
    h = handoff(root, 123)
    assert h["seed"] == 123 and h["runs"] == list(IDS)
    for arm, name in zip(("C0", "T2"), IDS):
        _, full, _ = predictions(root, "2025-03-31", "2026-01-06", "AAPL", name, seed=123)
        result = root / h["run_artifacts"][arm]["run_result"]["path"]
        saved = pd.read_csv(
            result.parent / "predictions_development.csv", float_precision="round_trip"
        )
        assert np.array_equal(full[arm], saved.score)
    app = AppTest.from_file(str(root / "apps/track_a_dashboard.py"), default_timeout=60).run()
    assert not app.exception
    app.button(key="start_hf20_replication").click().run()
    assert not app.exception
    assert app.selectbox(key="hf20_seed").value == 123
    for name in IDS:
        app.selectbox(key="hf20_run").set_value(name).run()
        assert not app.exception and len(app.get("plotly_chart")) >= 14
    example = h["example"]
    app.selectbox(key="hf20_stock").set_value(example["symbol"]).run()
    app.selectbox(key="hf20_tail_mode").set_value("Train-q99 tails").run()
    event_box = app.selectbox(key="hf20_event")
    index = next(
        i
        for i, value in enumerate(event_box.options)
        if value.startswith(f"{example['session']} / origin{example['origin']} /")
    )
    event_box.set_value(index).run()
    app.button(key="hf20_load_features").click().run()
    assert not app.exception and len(app.get("plotly_chart")) >= 18
    assert not any("SOURCE/CHRONOLOGY HOLD" in w.value for w in app.warning)
    app.selectbox(key="hf20_channel").set_value("M2").run()
    assert not app.exception
    app.selectbox(key="hf20_seed").set_value(42).run()
    assert not app.exception
    assert set(app.selectbox(key="hf20_run").options) == set(OLD_IDS)
