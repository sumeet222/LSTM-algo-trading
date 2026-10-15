"""Bounded fabricated WF2 authority, observer and calendar oracles; no real fit."""

import csv
import json
import runpy
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
import torch

from lstm_data.baseline_ridge import windows
from lstm_data.batch_telemetry import BatchTelemetry
from lstm_data.config import digest
from lstm_data.ft0_transforms import identity
from lstm_data.labels import FitWindow
from lstm_data.neural_data import IndexedOrigin
from lstm_data.neural_engine import SharedLSTM, optimizer, seed_all
from lstm_data.pretraining_policy import PreparationAuthority
from lstm_data.real_bridge_authority import BridgeReview, TrainingAuthority, require_training
from lstm_data.real_bridge_data import RealInputView, check_bridge_window, tensor_hash
from lstm_data.real_bridge_run import epoch_pass
from lstm_data.wf2_replication import (
    SEAL,
    WF2PairAuthority,
    approval_scope,
    contract,
    journal_rows,
    numeric_recipe,
)


def test_module_entry_delegates_to_canonical_authority_module(monkeypatch):
    import lstm_data.wf2_replication as canonical

    calls = []

    def entry() -> int:
        calls.append(canonical.WF2PairAuthority)
        return 0

    monkeypatch.setattr(canonical, "main", entry)
    with pytest.raises(SystemExit) as result:
        runpy.run_module("lstm_data.wf2_replication", run_name="__main__")
    assert result.value.code == 0
    assert calls == [WF2PairAuthority]


def fabricated_view() -> RealInputView:
    w = windows("WF2", pd.Timestamp("2024-01-01T05:00Z"))[0]
    x = torch.arange(240 * 16, dtype=torch.float32).reshape(240, 16) / 1000
    indices = tuple(tuple(range(i * 48, (i + 1) * 48)) for i in range(5))
    rows = (
        IndexedOrigin("2023-09-27", 1, indices, (1.0, 2.0, 3.0, 4.0, 5.0)),
        IndexedOrigin("2023-09-27", 2, indices, (3.0, 4.0, 5.0, 6.0, 7.0)),
        IndexedOrigin("2023-09-28", 1, indices, (20.0, 21.0, 22.0, 23.0, 24.0)),
    )
    sessions = ("2023-09-27", "2023-09-28")
    meta = identity(["SYN:R", "SYN:P", w, rows, sessions, ()])
    return RealInputView("SYN:R", "SYN:P", w, x, rows, sessions, tensor_hash(x), meta, ())


def decision() -> dict:
    return {
        "actor_type": "human",
        "owner": "Track A researcher",
        "status": "APPROVED",
        "proposal_sha256": "SYN:PLAN",
        "approved_runs": ["TA009-TM0-S42-WF2", "TA009-MC0-S42-WF2"],
        "extend_qualified_stock_SPY_attestation_to_WF2": True,
        "approve_linked_registry_v3": True,
        "approve_batch_telemetry_v1": True,
        "response_text": "FABRICATED TEST ONLY",
        "response_provenance": "TEST",
    }


def test_scoped_decision_refuses_old_wrong_hash_or_extra_run():
    approval_scope({"sha256": "SYN:PLAN"}, decision())
    for change in (
        {"proposal_sha256": "OLD"},
        {"approved_runs": ["MC0"]},
        {"extend_qualified_stock_SPY_attestation_to_WF2": False},
        {"approve_batch_telemetry_v1": False},
    ):
        with pytest.raises(ValueError, match="ACTUAL_EXACT"):
            approval_scope({"sha256": "SYN:PLAN"}, {**decision(), **change})


def test_wrong_authority_rejected_before_engine():
    with pytest.raises(ValueError, match="CONCRETE_WF2"):
        require_training(object.__new__(WF2PairAuthority), "CALIBRATION", "SYN:I")
    with pytest.raises(ValueError):
        contract("E5")


def test_fixed_december_window_tail_and_confirmation_negative():
    inner, tail, full = windows("WF2", pd.Timestamp("2024-01-01T05:00Z"))
    assert inner.stop == tail.start == pd.Timestamp("2023-10-02T04:00Z")
    assert full.stop == tail.stop == pd.Timestamp("2024-01-01T05:00Z")
    check_bridge_window(full)
    check_bridge_window(
        FitWindow(
            "BRIDGE_REVIEW:WF2",
            full.stop,
            pd.Timestamp("2024-07-01T04:00Z"),
            pd.Timestamp("2024-07-01T04:00Z"),
            "INNER_VALIDATION",
        )
    )
    with pytest.raises(ValueError, match="FROZEN"):
        check_bridge_window(replace(full, stop=pd.Timestamp("2024-07-02T04:00Z")))
    assert full.stop != windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))[2].stop


def test_recipe_timestamps_are_not_numeric_parameters():
    a = {
        "constructed_at": "A",
        "window": {"start": "2020", "stop": "2024", "fitted_at": "A"},
        "floor": 1.0,
    }
    b = {
        "constructed_at": "B",
        "window": {"start": "2020", "stop": "2024", "fitted_at": "B"},
        "floor": 1.0,
    }
    assert numeric_recipe(a) == numeric_recipe(b)
    assert numeric_recipe(a) != numeric_recipe({**b, "floor": 2.0})


def test_actual_epoch_one_update_is_bitwise_identical_with_observer(tmp_path: Path, monkeypatch):
    # This local synthetic-only fixture bypasses only epoch admission; the actual
    # central WF2 authority rejection has an independent negative test above.
    monkeypatch.setattr("lstm_data.real_bridge_run.require_training", lambda *args: None)
    view = fabricated_view()
    model_states = []
    optimizers = []
    rng = []
    for enabled in (False, True):
        seed_all(42)
        model = SharedLSTM(16)
        opt = optimizer(model)
        observer = (
            BatchTelemetry(tmp_path / "batch.csv", "SYN:ONE_BATCH", "TM0", "CALIBRATION")
            if enabled
            else None
        )
        result = epoch_pass(
            object.__new__(TrainingAuthority),
            "SYN:I",
            model,
            view,
            1,
            opt,
            time.monotonic() + 30,
            observer.record if observer else None,
        )
        assert result["steps"] == 1
        model_states.append({k: v.detach().clone() for k, v in model.state_dict().items()})
        optimizers.append(opt.state_dict())
        rng.append(torch.get_rng_state().clone())
    assert all(torch.equal(v, model_states[1][k]) for k, v in model_states[0].items())
    assert optimizers[0]["param_groups"] == optimizers[1]["param_groups"]
    for key, state in optimizers[0]["state"].items():
        assert all(torch.equal(v, optimizers[1]["state"][key][k]) for k, v in state.items())
    assert torch.equal(rng[0], rng[1])
    rows = list(csv.DictReader((tmp_path / "batch.csv").open()))
    assert len(rows) == 1
    r = rows[0]
    assert r["number_sessions"] == "2" and r["number_origins"] == "3"
    assert float(r["effective_weight_sum"]) == 1
    norm = float(r["preclip_global_grad_norm"])
    assert float(r["clip_multiplier"]) == min(1.0, 1.0 / (norm + 1e-6))
    assert r["optimizer_step_id"] == "1" and r["finite_flag"] == "True"
    assert r["session_ids"] == "2023-09-27|2023-09-28"


def test_two_pair_linked_accounting_atomic_and_no_retry(tmp_path: Path, monkeypatch):
    (tmp_path / "configs").mkdir()
    (tmp_path / "reports/audit").mkdir(parents=True)
    pointer = tmp_path / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
    pointer.write_text('{"SYNTHETIC":true}')
    initial = digest(pointer)
    prep = PreparationAuthority(tmp_path, {}, {}, {}, {})
    review = BridgeReview(tmp_path, {}, {}, {}, prep, object())
    plan = {
        "prior_pointer_snapshot": {"path": "SYN:OLD", "sha256": initial},
        "registry_definition": {"path": "SYN:DEF", "sha256": "SYN:DEF"},
        "prior_v1_journal": {"path": "SYN:V1", "sha256": "SYN:V1"},
        "prior_v2_journal": {"path": "SYN:V2", "sha256": "SYN:V2"},
        "runs": [
            {"architecture": name, "run_id": f"TA009-{name}-S42-WF2", "input_id": "SYN:I"}
            for name in ("TM0", "MC0")
        ],
    }
    monkeypatch.setattr(WF2PairAuthority, "ensure", lambda *args: None)
    tokens = [
        WF2PairAuthority(review, {"sha256": "SYN:PLAN"}, plan, {}, decision(), name, SEAL)
        for name in ("TM0", "MC0")
    ]
    for i, token in enumerate(tokens):
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            token.append(status, {"synthetic": True})
        assert (
            journal_rows(tmp_path / "reports/audit/track_a_real_pairs_v3.jsonl")[-1][
                "global_started_pairs"
            ]
            == 5 + i
        )
    with pytest.raises(ValueError, match="NO_DUPLICATE"):
        tokens[0].append("STARTED", {})
    assert json.loads(pointer.read_text())["schema"] == 3
