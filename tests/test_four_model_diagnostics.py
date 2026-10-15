"""Independent tiny audit oracles; no fitting or empirical data access."""

from pathlib import Path

import numpy as np
import pytest
import torch

from lstm_data.config import digest
from lstm_data.four_model_diagnostics import (
    legal_key,
    paired_blocks,
    pairwise_accuracy,
    safe_model,
    session_concentration,
)
from lstm_data.neural_engine import SharedLSTM
from lstm_data.pretraining_tables import target_moments, tg0
from lstm_data.real_bridge_run import daily_ic, rank_ic


def test_rank_midranks_constants_and_equal_day_weight():
    value, status = rank_ic((1, 1, 3, 4, 5), (1, 2, 3, 4, 5))
    assert value == pytest.approx(np.sqrt(0.95))
    assert status == "DEFINED"
    assert rank_ic((0,) * 5, (1, 2, 3, 4, 5))[0] == 0
    assert rank_ic((1, 2, 3, 4, 5), (1,) * 5)[0] is None
    rows = (("a", 1.0, True), ("a", -1.0, True), ("b", 1.0, True))
    assert daily_ic(rows, defined_only=False) == 0.5


def test_session_concentration_weights_origins_before_days_and_ceil():
    r = session_concentration(["a", "a", "b"], np.array([2.0, 6.0, 10.0]))
    assert r["equal_day_MSE"] == 7
    assert r["shares"]["0.1"]["k"] == 1
    assert r["shares"]["0.1"]["share"] == pytest.approx(10 / 14)
    with pytest.raises(ValueError):
        session_concentration(["a"], np.array([1.0, 2.0]))


def test_tg0_unscaled_mad_additive_floor():
    assert target_moments((0.0, 1.0, 2.0, 3.0, 4.0)) == (2.0, 1.0)
    assert tg0((0.0, 0.0, 0.0, 0.0, 0.01), 0.0001) == (0.0, 0.0, 0.0, 0.0, 100.0)
    assert tg0((0.0, 1.0, 2.0, 3.0, 4.0), 0.0001)[0] == pytest.approx(-2 / 1.0001)


def test_pairwise_ties_and_direction():
    target = np.arange(5.0)
    assert pairwise_accuracy(target, target) == 1
    assert pairwise_accuracy(-target, target) == 0
    assert pairwise_accuracy(np.zeros(5), target) == 0.5


def test_block_reproducibility_does_not_bridge_missing_exchange_session():
    positions = np.r_[np.arange(6), np.arange(10, 16)]
    values = np.arange(12.0)
    a = paired_blocks(values, positions, 5, samples=100)
    assert a == paired_blocks(values, positions, 5, samples=100)
    assert a["eligible_starts"] == 4
    assert a["status"] == "EXPLORATORY_NOT_FULL_G8"
    assert paired_blocks(values, positions, 10)["status"] == "NO_CONTIGUOUS_BLOCKS"


@pytest.mark.parametrize("day,origin", [("2024-07-01", 1), ("2025-06-30", 2), ("2023-08-01", 3)])
def test_confirmation_and_wrong_origin_rejected_before_access(day, origin):
    with pytest.raises(ValueError, match="NO_CONFIRMATION"):
        legal_key(day, origin)


def test_safe_checkpoint_identity_eval_only(tmp_path: Path):
    model = SharedLSTM(16)
    contract = {"architecture": "TM0", "channels": 16, "parameters": 6433}
    body = {
        "contract": contract,
        "pair_key": "FABRICATED_PAIR",
        "preparation_id": "FABRICATED_PREP",
        "stage": "REFIT_FINAL",
        "epoch": 1,
        "model": model.state_dict(),
    }
    path = tmp_path / "fabricated.pt"
    torch.save(body, path)
    manifest = {
        "sha256": digest(path),
        "preparation_id": "FABRICATED_PREP",
        "stage": "REFIT_FINAL",
        "epoch": 1,
    }
    loaded = safe_model(path, manifest, contract, "FABRICATED_PAIR")
    assert not loaded.training and all(not p.requires_grad for p in loaded.parameters())
    with pytest.raises(ValueError, match="IDENTITY"):
        safe_model(path, {**manifest, "preparation_id": "WRONG"}, contract, "FABRICATED_PAIR")
    with pytest.raises(ValueError, match="HASH"):
        safe_model(path, {**manifest, "sha256": "WRONG"}, contract, "FABRICATED_PAIR")
