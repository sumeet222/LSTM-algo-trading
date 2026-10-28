"""Focused source, fixed-mask gradient and main-task invariants for C-A."""

import io

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_s2c_ca as s
from lstm_data import hf20_stage2_bcd as clock


def test_heads_share_identical_clock_main_initialization_and_reload() -> None:
    old = clock.model_for_clock()
    new = s.model_for_components()
    for key, value in old.state_dict().items():
        torch.testing.assert_close(value, new.state_dict()[key], rtol=0, atol=0)
    x = torch.zeros(4, 48, 16)
    known = torch.zeros(4, 10)
    new.eval()
    with torch.no_grad():
        main, aux = new.all_heads(x, known)
        torch.testing.assert_close(main, new(x, known), rtol=0, atol=0)
    assert aux.shape == (4, 3) and main.shape == (4,) and torch.isfinite(aux).all()
    stream = io.BytesIO()
    torch.save(new.state_dict(), stream)
    stream.seek(0)
    reload = s.model_for_components()
    reload.load_state_dict(torch.load(stream, weights_only=True))
    reload.eval()
    with torch.no_grad():
        torch.testing.assert_close(main, reload(x, known), rtol=0, atol=0)


def test_masked_cells_and_empty_batch_have_zero_aux_gradient_no_nan_fill() -> None:
    u = torch.ones(2, 20, 3, requires_grad=True)
    labels = torch.full_like(u, float("nan"))
    labels[0, 0] = torch.tensor([0.1, -0.1, 0.2])
    mask = torch.zeros(2, 20, dtype=torch.bool)
    mask[0, 0] = True
    w = torch.full((2, 20), 1 / 40)
    loss = s.masked_aux_loss(u, labels, mask, w, 0.1, 2)
    assert torch.isfinite(loss)
    loss.backward()
    assert u.grad is not None
    assert torch.count_nonzero(u.grad[~mask]) == 0
    assert torch.count_nonzero(u.grad[mask]) > 0
    empty = torch.ones(1, 20, 3, requires_grad=True)
    value = s.masked_aux_loss(
        empty,
        torch.full_like(empty, float("nan")),
        torch.zeros(1, 20, dtype=torch.bool),
        torch.zeros(1, 20),
        0.1,
        2,
    )
    value.backward()
    assert empty.grad is not None and torch.count_nonzero(empty.grad) == 0


def test_global_weights_and_complete_session_sampling_equal_full_gradient() -> None:
    rows = pd.DataFrame(
        dict(
            session_date_et=["a", "b", "b", "c"],
            category=["INTRADAY", "OVERNIGHT", "OVERNIGHT", "OVERNIGHT"],
        )
    )
    mask = np.ones((4, 20), bool)
    mask[0] = False
    mask[1, 0] = False
    w, receipt = s.phase_aux_weights(rows, np.arange(4), mask)
    assert w.sum() == pytest.approx(1)
    assert receipt["global_masked_base_mass"] == pytest.approx(1 - 1 / 80)
    # Removing one label does not give that origin the same mass as a full origin.
    assert w[1].sum() < w[2].sum()
    labels = torch.ones(4, 20, 3)
    full = torch.zeros(4, 20, 3, requires_grad=True)
    loss = s.masked_aux_loss(full, labels, torch.from_numpy(mask), torch.from_numpy(w), 1.0, 1.0)
    expected = torch.autograd.grad(loss, full)[0]
    candidate = torch.zeros(4, 20, 3, requires_grad=True)
    pieces = []
    for ix in [np.array([0]), np.array([1, 2]), np.array([3])]:
        pieces.append(
            s.masked_aux_loss(
                candidate[ix],
                labels[ix],
                torch.from_numpy(mask[ix]),
                torch.from_numpy(w[ix]),
                1.0,
                3.0,
            )
            / 3
        )
    got = torch.autograd.grad(pieces[0] + pieces[1] + pieces[2], candidate)[0]
    torch.testing.assert_close(got, expected, rtol=1e-7, atol=1e-8)
    main = s.prior.weighted_loss(
        torch.zeros(4, 20),
        torch.ones(4, 20),
        1.0,
        s.b.origin_weights(rows.session_date_et.to_numpy()),
    )
    assert float(main) == pytest.approx(float(torch.log(torch.tensor(2.0)).square()))


def test_true_signed_additivity_and_main_target_stays_absolute_total() -> None:
    pieces = np.log(np.array([102 / 100, 99 / 102, 101 / 99]))
    assert pieces.sum() == pytest.approx(np.log(101 / 100), abs=1e-12)
    assert abs(pieces.sum()) != pytest.approx(abs(pieces).sum())
    selector = s.b.Selector()
    assert selector.observe(1.0)
    assert not selector.observe(0.9995)
    assert selector.selected == 1 and selector.raw_epoch == 2
