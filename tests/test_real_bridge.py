"""Hermetic Package005 oracles: all tensors, approvals and prices are test fixtures."""

from __future__ import annotations

import csv
import json
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
import torch

from lstm_data.baseline_ridge import windows
from lstm_data.config import digest, fingerprint
from lstm_data.ft0_transforms import identity
from lstm_data.neural_data import IndexedOrigin
from lstm_data.neural_engine import SharedLSTM, batch_prediction, optimizer, session_losses
from lstm_data.pretraining_policy import PreparationAuthority
from lstm_data.pretraining_tables import BaseTables, CanonicalHistory, ProxyPanel
from lstm_data.real_bridge_authority import (
    CONTRACT,
    BridgeReview,
    TrainingAuthority,
    load_review,
    require_training,
    validate_training_binding,
)
from lstm_data.real_bridge_data import (
    RealInputView,
    check_bridge_window,
    supervised_status,
    tensor_hash,
)
from lstm_data.real_bridge_run import (
    daily_ic,
    epoch_pass,
    journal_rows,
    load_real_checkpoint,
    rank_ic,
    save_real_checkpoint,
)
from lstm_data.stock_source import StockCalendar


def fixture_view() -> RealInputView:
    w = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))[0]
    values = torch.arange(240 * 16, dtype=torch.float32).reshape(240, 16) / 1000
    indices = tuple(tuple(range(i * 48, (i + 1) * 48)) for i in range(5))
    rows = (
        IndexedOrigin("2023-03-29", 1, indices, (1.0,) * 5),
        IndexedOrigin("2023-03-29", 2, indices, (3.0,) * 5),
        IndexedOrigin("2023-03-30", 1, indices, (5.0,) * 5),
    )
    sessions = ("2023-03-29", "2023-03-30")
    meta = identity(["SYN:REVIEW", "SYN:PREP", w, rows, sessions, ()])
    return RealInputView(
        "SYN:REVIEW", "SYN:PREP", w, values, rows, sessions, tensor_hash(values), meta, ()
    )


def forged(root: Path) -> TrainingAuthority:
    a = PreparationAuthority(root, {}, {}, {}, {})
    review = BridgeReview(root, {}, {}, {}, a, object())
    return TrainingAuthority(review, {}, {}, object())


def test_session_axes_masks_and_independent_objective():
    v = fixture_view()
    b = v.batch((0, 1))
    assert b.inputs.shape == (2, 2, 5, 48, 16)
    assert b.inputs.dtype == torch.float32
    assert b.origins.tolist() == [[True, True], [True, False]]
    assert torch.count_nonzero(b.inputs[1, 1]) == 0
    assert torch.equal(b.inputs[0, 0, 2, 0], v.values[96])
    # Independent equal-session oracle: (1+9)/2 then25 -> mean15, not35/3.
    assert session_losses(torch.zeros_like(b.targets), b.targets, b.origins).tolist() == [5.0, 25.0]
    assert float(session_losses(torch.zeros_like(b.targets), b.targets, b.origins).mean()) == 15.0


@pytest.mark.parametrize("positions", [(0, 0), (-1,), (2,), ()])
def test_session_indices_fail_closed(positions):
    with pytest.raises(ValueError, match="SESSION_POSITIONS"):
        fixture_view().batch(positions)


def test_mutated_tensor_and_target_metadata_rejected():
    v = fixture_view()
    v.values[0, 0] += 1
    with pytest.raises(ValueError, match="CONTENT_OR_IDENTITY"):
        v.batch((0,))
    v = fixture_view()
    changed = replace(v, rows=(replace(v.rows[0], targets=(99.0,) * 5), *v.rows[1:]))
    with pytest.raises(ValueError, match="CONTENT_OR_IDENTITY"):
        changed.verify()
    with pytest.raises(ValueError):
        replace(v, values=torch.zeros(10, 21)).verify()


@pytest.mark.parametrize("change", ["stop", "phase", "synthetic", "confirmation"])
def test_wrong_stage_cutoff_and_confirmation_window(change):
    w = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))[0]
    w = {
        "stop": replace(w, stop=w.stop + pd.Timedelta(days=1)),
        "phase": replace(w, phase="REFIT"),
        "synthetic": replace(w, window_id="SYNTHETIC:" + w.window_id),
        "confirmation": replace(
            w, start=pd.Timestamp("2024-07-01T04:00Z"), stop=pd.Timestamp("2025-07-01T04:00Z")
        ),
    }[change]
    with pytest.raises(ValueError, match="EXACT_FROZEN"):
        check_bridge_window(w)


def test_asof_own_step_and_boundary_purge(tmp_path):
    cal = StockCalendar("2023-03-01", "2023-04-05")
    day = "2023-04-03"
    end = cal.steps[cal._positions[day, 1]].end
    panel = ProxyPanel(
        day,
        1,
        end,
        end + pd.Timedelta(minutes=2),
        end + pd.Timedelta(minutes=3),
        end + pd.Timedelta(minutes=243),
        (100.0,) * 5,
        (101.0,) * 5,
        (True,) * 5,
        (True,) * 5,
        (0.01,) * 5,
        (("SYN:ENTRY", "SYN:EXIT"),) * 5,
        end + pd.Timedelta(minutes=243),
    )
    pos = cal._positions[day, 1]
    history = CanonicalHistory(
        cal, {}, PreparationAuthority(tmp_path, {}, {}, {}, {}), "SYN:S", "SYN:A"
    )
    base = BaseTables(
        history, {}, {(day, 1): panel}, {}, {(day, 1): tuple(range(pos - 47, pos + 1))}
    )
    w = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))[1]
    assert supervised_status(
        base, day, 1, w, pd.Timestamp("2023-03-31T04:00Z"), asof=True
    ).startswith("SCALER_")
    assert supervised_status(base, day, 1, w, w.start, asof=False) == "ELIGIBLE"
    base.panels[day, 1] = replace(panel, maturity=w.stop)
    assert supervised_status(base, day, 1, w, w.start, asof=False).startswith("LABEL_")


@pytest.mark.parametrize(
    "activity",
    ["START_PAIR", "CALIBRATION", "REFIT", "CHECKPOINT", "CONFIRMATION", "MC0", "SECOND_PAIR"],
)
def test_forged_and_preparation_permissions_never_fit(tmp_path, activity):
    a = forged(tmp_path)
    with pytest.raises(ValueError, match="AUTHORITY"):
        require_training(a, activity, "SYN:INPUT")
    with pytest.raises(ValueError, match="BINDING_REQUIRED"):
        validate_training_binding(a.review, {"status": "PENDING"})


def test_forged_epoch_rejects_before_optimizer_step(tmp_path):
    model = SharedLSTM()
    opt = optimizer(model)
    before = {k: v.clone() for k, v in model.state_dict().items()}
    with pytest.raises(ValueError, match="AUTHORITY"):
        epoch_pass(
            forged(tmp_path), "SYN:INPUT", model, fixture_view(), 1, opt, time.monotonic() + 10
        )
    assert not opt.state
    assert all(torch.equal(before[k], v) for k, v in model.state_dict().items())


@pytest.fixture
def sealed_fixture(tmp_path, monkeypatch):
    # A wholly synthetic file graph. Production hard pins are replaced only inside
    # this hermetic test; the factory never touches real archives or authorizations.
    import lstm_data.real_bridge_authority as module

    class FixturePreparation(PreparationAuthority):
        def ensure(self, activity: str) -> None:
            assert activity == "FEATURE_TARGET_PREPARATION"

    def put(name: str, body: str) -> dict:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        return {"path": name, "sha256": digest(p)}

    code = put("src/lstm_data/SYNTHETIC_fixture.py", "# SYNTHETIC TEST ONLY\n")
    raw = put("data/raw/SYNTHETIC_fixture.bin", "NOT MARKET DATA")
    pre = put(
        "release/preflight.json",
        json.dumps(
            {
                "protected": {
                    code["path"]: {"sha256": code["sha256"]},
                    raw["path"]: {"sha256": raw["sha256"]},
                }
            }
        ),
    )
    inv = tmp_path / "release/inventory.csv"
    with inv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["path", "sha256"])
        writer.writeheader()
        writer.writerows([pre, code])
    source = put("source.json", "{}")
    protocol = put("protocol.json", "{}")
    store = put("SYNTHETIC_store.bin", "NO REAL COMPONENTS")
    prep = put("SYNTHETIC_prep.json", "{}")
    modules = {code["path"]: code["sha256"]}
    manifest = put(
        "release/manifest.json",
        json.dumps(
            {
                "universe": CONTRACT["universe"],
                "MODEL_FIT_FORBIDDEN": True,
                "production_migrated": False,
                "code_sha256": identity(modules),
                "authority": {"policy_ref": {}, "approval_ref": {}},
                "canonical_store": store,
                "preparations": {"SYN": prep},
            }
        ),
    )
    producer = put(
        "producer.json",
        json.dumps(
            {
                "inventory": {"path": "release/inventory.csv", "sha256": digest(inv)},
                "manifest": manifest,
                "modules": modules,
                "source_manifest": source,
                "original_protocol": protocol,
            }
        ),
    )
    monkeypatch.setattr(module, "RELEASE_SHA", manifest["sha256"])
    monkeypatch.setattr(module, "INVENTORY_SHA", digest(inv))
    monkeypatch.setattr(
        module, "load_authority", lambda *args: FixturePreparation(tmp_path, {}, {}, {}, {})
    )
    return (
        tmp_path,
        producer,
        {
            "source": raw,
            "code": code,
            "overlay": store,
            "prep": prep,
            "order": manifest,
            "old_universe": manifest,
        },
    )


@pytest.mark.parametrize("kind", ["source", "code", "overlay", "prep", "order", "old_universe"])
def test_actual_bound_file_tampering_rejected(sealed_fixture, kind):
    root, ref, files = sealed_fixture
    review = load_review(root, ref)
    p = root / files[kind]["path"]
    if kind in {"order", "old_universe"}:
        d = json.loads(p.read_text())
        d["universe"] = list(reversed(d["universe"])) if kind == "order" else ["O"] * 5
        p.write_text(json.dumps(d))
    else:
        p.write_bytes(p.read_bytes() + b"changed")
    with pytest.raises(ValueError):
        review.ensure()
    if kind == "source":
        with pytest.raises(ValueError, match="RAW_SOURCE_HASH"):
            load_review(root, ref)


@pytest.mark.parametrize("change", ["stale_code", "wrong_order", "wrong_shape", "pending_go"])
def test_input_metadata_and_pending_go_cannot_authorize_fit(sealed_fixture, change):
    import lstm_data.real_bridge_authority as module

    root, ref, _ = sealed_fixture
    review = load_review(root, ref)
    dataset = {
        "input_id": "SYN:TEST_ONLY",
        "status": "BRIDGE_READY",
        "code_sha256": module.bridge_code(root),
        "review_binding": review.binding,
        "producer": review.producer_ref,
        "contract": CONTRACT,
        "shape": [5, 48, 16],
    }
    if change == "stale_code":
        dataset["code_sha256"] = "0" * 64
    if change == "wrong_shape":
        dataset["shape"] = [5, 48, 21]
    if change == "wrong_order":
        dataset["contract"] = {**CONTRACT, "universe": ["OLD"] * 5}
    p = root / "SYNTHETIC_dataset.json"
    p.write_text(json.dumps(dataset))
    proposal = {
        "contract": CONTRACT,
        "review_binding": review.binding,
        "code_sha256": module.bridge_code(root),
        "input_id": "SYN:TEST_ONLY",
        "dataset_input_binding": {"path": p.name, "sha256": digest(p)},
    }
    p = root / "SYNTHETIC_proposal.json"
    p.write_text(json.dumps(proposal))
    proposal_ref = {"path": p.name, "sha256": digest(p)}
    d = root / "SYNTHETIC_pending.json"
    d.write_text(json.dumps({"status": "PENDING"}))
    pending = {"path": d.name, "sha256": digest(d)}
    binding = {
        "proposal": proposal_ref,
        "input_id": "SYN:TEST_ONLY",
        "researcher_decision": pending,
        "local_use_rights": pending,
        "shared_clock": pending,
        "gates": pending,
    }
    with pytest.raises(
        ValueError,
        match="ACTUAL_EXACT_RESEARCHER_GO"
        if change == "pending_go"
        else "INDEPENDENT_VERIFIED_BRIDGE",
    ):
        validate_training_binding(review, binding)


def test_single_pair_chain_counts_failure_and_rejects_restart(tmp_path):
    p = tmp_path / "synthetic_journal.jsonl"
    rows = []
    for state in ("STARTED", "CALIBRATED", "REFITTING", "FAILED"):
        rows.append(
            {
                "sequence": len(rows) + 1,
                "status": state,
                "pair_key": "SYN:UNIT_ONLY",
                "previous": fingerprint(rows),
                "contract": CONTRACT,
            }
        )
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert len([r for r in journal_rows(p) if r["status"] == "STARTED"]) == 1
    extra = {
        "sequence": 5,
        "status": "STARTED",
        "pair_key": "SYN:UNIT_ONLY",
        "previous": fingerprint(rows),
        "contract": CONTRACT,
    }
    p.write_text(p.read_text() + json.dumps(extra) + "\n")
    with pytest.raises(ValueError, match="MONOTONIC"):
        journal_rows(p)


def test_synthetic_gradient_checkpoint_smoke_and_real_refusal(tmp_path):
    old = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        model = SharedLSTM()
        opt = optimizer(model)
        b = fixture_view().batch((0,))
        opt.zero_grad(set_to_none=True)
        session_losses(batch_prediction(model, b), b.targets, b.origins).mean().backward()
        assert all(
            p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in model.parameters()
        )
        opt.step()
        model.eval()
        path = tmp_path / "SYNTHETIC_ONLY.pt"
        save_real_checkpoint(path, model, "SYN:PAIR", "SYN:PREP", "SYNTHETIC_SMOKE", 1)
        loaded = SharedLSTM()
        load_real_checkpoint(path, loaded, "SYN:PAIR", "SYN:PREP", "SYNTHETIC_SMOKE")
        assert torch.equal(batch_prediction(model, b), batch_prediction(loaded, b))
        with pytest.raises(ValueError, match="AUTHORITY"):
            save_real_checkpoint(tmp_path / "no_real.pt", model, "REAL", "REAL", "REFIT_FINAL", 1)
        with pytest.raises(ValueError, match="BINDING_CHANGED"):
            load_real_checkpoint(path, loaded, "SYN:OTHER", "SYN:PREP", "SYNTHETIC_SMOKE")
        path.write_bytes(path.read_bytes() + b"corrupt")
        with pytest.raises(ValueError, match="BINDING_CHANGED"):
            load_real_checkpoint(path, loaded, "SYN:PAIR", "SYN:PREP", "SYNTHETIC_SMOKE")
    finally:
        torch.set_num_threads(old)


@pytest.mark.parametrize(
    "pred,target,expected,status",
    [
        ((1.0, 2.0, 3.0, 4.0, 5.0), (1.0, 2.0, 3.0, 4.0, 5.0), 1.0, "DEFINED"),
        ((5.0, 4.0, 3.0, 2.0, 1.0), (1.0, 2.0, 3.0, 4.0, 5.0), -1.0, "DEFINED"),
        ((1.0,) * 5, (1.0, 2.0, 3.0, 4.0, 5.0), 0.0, "PREDICTION_CONSTANT"),
        ((1.0, 2.0, 3.0, 4.0, 5.0), (0.0,) * 5, None, "TARGET_CONSTANT"),
    ],
)
def test_frozen_rank_ties_constants_and_project_zero(pred, target, expected, status):
    value, flag = rank_ic(pred, target)
    assert value == pytest.approx(expected) if expected is not None else value is None
    assert flag.startswith(status)
    assert rank_ic((1.0, 1.0, 2.0, 3.0, 4.0), (1.0, 1.0, 2.0, 3.0, 4.0))[0] == pytest.approx(1.0)


def test_rank_daily_aggregation_equal_session_and_defined_only():
    rows = (("A", 0.8, True), ("A", 0.0, False), ("B", -0.2, True), ("C", None, False))
    assert daily_ic(rows, defined_only=False) == pytest.approx(0.1)
    assert daily_ic(rows, defined_only=True) == pytest.approx(0.3)
