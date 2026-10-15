"""Small fabricated join/authority/journal oracles; no neural fits or source access."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import digest
from lstm_data.ft0_transforms import identity
from lstm_data.labels import FitWindow
from lstm_data.neural_data import IndexedOrigin
from lstm_data.pretraining_policy import PreparationAuthority
from lstm_data.real_batch_authority import (
    QUEUE,
    BatchPairAuthority,
    approval_scope,
    journal_rows_v2,
)
from lstm_data.real_batch_baseline import market_lags
from lstm_data.real_batch_data import ConditionedView
from lstm_data.real_bridge_authority import BridgeReview, require_training
from lstm_data.real_bridge_data import RealInputView, tensor_hash


def stock_view() -> RealInputView:
    window = FitWindow(
        "SYN:TEST",
        pd.Timestamp("2023-01-01T00:00Z"),
        pd.Timestamp("2023-02-01T00:00Z"),
        pd.Timestamp("2023-02-01T00:00Z"),
        "INNER_TRAIN",
    )
    values = torch.arange(240 * 16, dtype=torch.float32).reshape(240, 16) / 100
    rows = (
        IndexedOrigin(
            "2023-01-10",
            1,
            tuple(tuple(range(i * 48, (i + 1) * 48)) for i in range(5)),
            (1.0, 2.0, 3.0, 4.0, 5.0),
        ),
    )
    sessions = ("2023-01-10",)
    meta = identity(["SYN:R", "SYN:P", window, rows, sessions, ()])
    return RealInputView(
        "SYN:R", "SYN:P", window, values, rows, sessions, tensor_hash(values), meta, ()
    )


def joined(channels: int = 21) -> ConditionedView:
    table = torch.arange(48 * 5, dtype=torch.float32).reshape(48, 5) / 10
    return ConditionedView(
        stock_view(),
        table,
        ((("2023-01-10", 1), tuple(range(48))),),
        tensor_hash(table),
        "SYN:M",
        channels,
    )


def test_exact_market_prefix_and_independent_population_four_peers():
    a, b = joined(), joined(23)
    x, y = a.batch((0,)), b.batch((0,))
    assert torch.equal(x.inputs, y.inputs[..., :21])
    assert torch.equal(x.inputs[0, 0, 0, :, 16:], a.market)
    assert torch.equal(x.inputs[0, 0, 4, :, 16:], a.market)
    z = x.inputs[0, 0, :, -1, 0].numpy()
    for i in range(5):
        peers = np.delete(z.astype(float), i)
        np.testing.assert_allclose(
            y.inputs[0, 0, i, -1, 21:].numpy(), [peers.mean(), peers.std(ddof=0)], rtol=1e-7
        )
    assert not y.origins[0, 1] and torch.count_nonzero(y.inputs[0, 1]) == 0


def test_market_ridge_keeps_stock112_then_market35_lag_order():
    x = np.arange(5 * 48 * 21).reshape(5, 48, 21)
    actual = market_lags(x)
    assert actual.shape == (5, 147)
    for j, lag in enumerate((0, 1, 2, 5, 11, 23, 47)):
        np.testing.assert_array_equal(actual[:, j * 16 : (j + 1) * 16], x[:, 47 - lag, :16])
        np.testing.assert_array_equal(
            actual[:, 112 + j * 5 : 112 + (j + 1) * 5], x[:, 47 - lag, 16:]
        )


def test_mutation_missing_endpoint_and_stale_index_identity_fail():
    v = joined()
    bad = replace(v, market=v.market.clone())
    bad.market[0, 0] += 1
    with pytest.raises(ValueError, match="BOUND_FINITE"):
        bad.batch((0,))
    missing = replace(v, market_indices=((("2023-01-10", 1), tuple(range(47)) + (-1,)),))
    with pytest.raises(ValueError, match="ENDPOINT"):
        missing.batch((0,))
    changed = replace(v, market_indices=((("2023-01-10", 1), tuple(reversed(range(48)))),))
    assert changed.version != v.version
    with pytest.raises(ValueError, match="BOUND_FINITE"):
        replace(v, channels=22).batch((0,))


def decision(plan_ref: dict, selected: tuple[str, ...] = QUEUE) -> dict:
    return {
        "actor_type": "human",
        "owner": "Track A researcher",
        "status": "APPROVED",
        "response_text": "SYNTHETIC TEST APPROVAL ONLY",
        "response_provenance": "test",
        "recorded_at": "test",
        "plan_sha256": plan_ref["sha256"],
        "approved_runs": list(selected),
        "extend_researcher_attestation_to_named_batch": True,
        "accept_qualified_spy_fitting": True,
        "accept_existing_engineering_for_named_batch": True,
        "approve_linked_registry_v2": True,
        "maximum_wall_seconds": 7200,
    }


def test_all_pair_grants_subset_and_old_or_unscoped_approval_refused():
    plan_ref = {"path": "SYN:PLAN", "sha256": "SYN:SHA"}
    assert approval_scope(plan_ref, decision(plan_ref)) == QUEUE
    assert approval_scope(plan_ref, decision(plan_ref, ("MC0", "E5"))) == ("MC0", "E5")
    for changed in (
        {"plan_sha256": "old"},
        {"approved_runs": ["TM0"]},
        {"approved_runs": ["MC1", "MC0"]},
        {"extend_researcher_attestation_to_named_batch": False},
    ):
        with pytest.raises(ValueError, match="ACTUAL_EXACT"):
            approval_scope(plan_ref, {**decision(plan_ref), **changed})


def test_forged_concrete_batch_authority_is_rejected_before_forward():
    forged = object.__new__(BatchPairAuthority)
    with pytest.raises(ValueError, match="CONCRETE_EXACT"):
        require_training(forged, "CALIBRATION", "SYN:INPUT")


def test_tiny_serial_three_pair_journal_and_no_retry(tmp_path: Path, monkeypatch):
    # Lease checks are tested separately; this fixture isolates the actual writer
    # and atomic linked-pointer transition in a disposable synthetic directory.
    (tmp_path / "configs").mkdir()
    (tmp_path / "reports/audit").mkdir(parents=True)
    pointer = tmp_path / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
    pointer.write_text(json.dumps({"SYNTHETIC": True}))
    plan_ref = {"path": "SYN:PLAN", "sha256": "SYN:SHA"}
    plan = {
        "prior_pointer_snapshot": {"path": "SYN:SNAP", "sha256": digest(pointer)},
        "prior_real_journal": {"path": "SYN:V1", "sha256": "SYN:OLD"},
        "registry_definition": {"path": "SYN:DEF", "sha256": "SYN:DEF"},
        "runs": [{"architecture": a, "run_id": "SYN:" + a, "input_id": "SYN:" + a} for a in QUEUE],
    }
    prep = PreparationAuthority(tmp_path, {}, {}, {}, {})
    review = BridgeReview(tmp_path, {}, {}, {}, prep, object())
    monkeypatch.setattr(BatchPairAuthority, "ensure", lambda *args: None)
    tokens = [
        BatchPairAuthority(review, plan_ref, plan, {}, decision(plan_ref), a, object())
        for a in QUEUE
    ]
    path = tmp_path / "reports/audit/track_a_real_pairs_v2.jsonl"
    for a in tokens:
        for stage in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            a.append(stage, {"test": True})
    rows = journal_rows_v2(path)
    assert len(rows) == 12
    assert [r["global_started_pairs"] for r in rows if r["status"] == "STARTED"] == [2, 3, 4]
    assert json.loads(pointer.read_text())["schema"] == 2
    with pytest.raises(ValueError, match="NO_RETRY"):
        tokens[0].append("STARTED", {})
    raw = path.read_text()
    path.write_text(raw.replace('"architecture": "MC1"', '"architecture": "E5"', 1))
    with pytest.raises(ValueError):
        journal_rows_v2(path)
