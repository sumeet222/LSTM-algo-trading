"""Independent peer law/coordinate/clock regressions; no repeated health fits."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.e5_deep_audit import original_oracle
from lstm_data.e5_fixture_v2 import B2, planted_returns, step_values
from lstm_data.neural_engine import SessionBatch, batch_prediction, seed_all
from lstm_data.neural_models import create_model
from lstm_data.p3_domain import UniverseSpec
from lstm_data.peer_inputs import peer_summaries


def test_v1_failure_and_independent_all_step_graph_remain_failed():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        evidence = original_oracle()
    finally:
        torch.set_num_threads(previous)
    assert evidence["unchanged_gate"]["both_failed"]
    assert evidence["optimizer_updates"] == 0
    assert evidence["nonzero_peer_gradient_steps"] == 48
    assert evidence["local_sensitivity"]["absolute_error"] < 1e-7
    assert evidence["hypothetical_TG0_center_identity_error"] < 1e-14


def test_own_prefix_cannot_identify_target_and_peer_perturbation_excludes_own():
    at = pd.Timestamp("2023-03-01T15:30Z")
    a = np.zeros((5, 16))
    a[0, B2] = 1
    a[1:, 0] = (1, 2, 3, 4)
    b = a.copy()
    b[1:, 0] *= -1
    assert np.array_equal(a[0], b[0])
    assert planted_returns(a, at)[0] == pytest.approx(2.5e-4)
    assert planted_returns(b, at)[0] == pytest.approx(-2.5e-4)
    # This intervention changes ranking of recipient vs four unchanged zero labels.
    assert np.median(planted_returns(a, at)) == 0
    assert np.median(np.abs(planted_returns(a, at))) == 0
    for wrong in (a[:4], a * np.nan):
        with pytest.raises(ValueError):
            planted_returns(wrong, at)


def test_timestamp_keyed_consistency_null_and_normalized_peer_identity():
    at = pd.Timestamp("2023-03-01T15:30Z")
    a = step_values(at)
    assert np.array_equal(a, step_values(at))
    assert not np.array_equal(a, step_values(at + pd.Timedelta(hours=1)))
    assert a[:, B2].sum() == 1 and set(a[:, B2]) == {0, 1}
    assert np.isfinite(a).all() and a.shape == (5, 16)
    assert not np.array_equal(planted_returns(a, at), planted_returns(a, at, null=True))
    # Independent arbitrary affine normalization: no duplicate peer scaling.
    center, scale = 0.4, 1.7
    inputs = np.repeat(a[:, None], 48, axis=1)
    inputs[..., 0] = (inputs[..., 0] - center) / scale
    peers = peer_summaries(inputs)
    formula = a[:, B2] * (scale * peers[:, -1, 0] + center)
    np.testing.assert_allclose(formula, planted_returns(a, at) / 1e-4, atol=1e-14)
    others = inputs[1:, 0, 0]
    assert peers[0, 0, 0] == pytest.approx(others.mean())
    assert peers[0, 0, 1] == pytest.approx(np.sqrt(((others - others.mean()) ** 2).sum() / 4))
    for bad in (pd.Timestamp("NaT"), pd.Timestamp("2023-03-01")):
        with pytest.raises(ValueError):
            step_values(bad)


def test_renamed_permuted_order_equivariance_exact_MC0_prefix_and_missing_rejection():
    seed_all(42)
    values = step_values(pd.Timestamp("2023-03-01T15:30Z"))
    raw = np.repeat(values[:, None], 48, axis=1)
    prefix = np.concatenate((raw, np.zeros((5, 48, 5))), axis=-1).astype(np.float32)
    peers = peer_summaries(prefix[..., :16]).astype(np.float32)
    x = torch.tensor(np.concatenate((prefix, peers), axis=-1))
    assert torch.equal(x[..., :21], torch.tensor(prefix))
    perm = np.array([4, 2, 0, 3, 1])
    alternate = np.concatenate((prefix[perm], peer_summaries(raw[perm])), axis=-1)
    model = create_model("E5")
    model.eval()
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        with torch.no_grad():
            np.testing.assert_allclose(
                model(torch.tensor(alternate, dtype=torch.float32)).numpy(),
                model(x).numpy()[perm],
                atol=1e-7,
                rtol=1e-6,
            )
    finally:
        torch.set_num_threads(previous)
    u = UniverseSpec("SYN:ORDER_A", ("A", "B", "C", "D", "E"))
    renamed = UniverseSpec("SYN:ORDER_B", ("V", "W", "X", "Y", "Z"))
    assert u.universe_id != renamed.universe_id
    batch = SessionBatch(
        ("SYN:DAY",),
        x[None, None].expand(1, 2, -1, -1, -1),
        torch.zeros(1, 2, 5),
        torch.tensor([[True, True]]),
    )
    batch.validate()
    with pytest.raises(ValueError):
        replace(batch, inputs=batch.inputs[:, :, :4]).validate()
    bad = batch.inputs.clone()
    bad[0, 0, 0, 0, 21] += 1
    with pytest.raises(ValueError, match="CANONICAL_E5"):
        replace(batch, inputs=bad).validate()
    assert batch_prediction(model, batch).shape == (1, 2, 5)
