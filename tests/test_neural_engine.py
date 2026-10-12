"""Independent mathematical and tensor oracles for synthetic TM0."""

import math

import pytest
import torch

from lstm_data.neural_engine import (
    SessionBatch,
    SharedLSTM,
    batch_prediction,
    clip,
    optimizer,
    seed_all,
    session_batches,
    session_losses,
)


@pytest.fixture(autouse=True)
def small_cpu():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def test_exact_model_independence_dropout_and_gradient():
    seed_all(42)
    model = SharedLSTM()
    assert sum(p.numel() for p in model.parameters()) == 4 * 32 * (16 + 32 + 2) + 33 == 6433
    assert sum(p.numel() for p in SharedLSTM(21).parameters()) == 7073
    model.eval()
    x = torch.randn(5, 48, 16)
    expected = model(x[:1])
    assert torch.allclose(expected, model(x)[:1], atol=1e-6, rtol=1e-6)
    other = x.clone()
    other[1:] *= 100
    assert torch.allclose(expected, model(other)[:1], atol=1e-6, rtol=1e-6)
    assert torch.equal(model(x), model(x))
    model.train()
    assert not torch.equal(model(x), model(x))
    model(x).square().mean().backward()
    assert all(p.grad is not None and bool(p.grad.abs().sum() > 0) for p in model.parameters())
    for shape in [(5, 47, 16), (5, 16, 48), (5, 48, 15)]:
        with pytest.raises(ValueError):
            model(torch.zeros(shape))
    with pytest.raises(ValueError):
        model(x.double())
    with pytest.raises(ValueError):
        model(x * math.nan)


def test_unequal_origin_oracle_and_gradient():
    pred = torch.tensor([[[math.sqrt(2)] * 5, [math.sqrt(6)] * 5],
                         [[math.sqrt(10)] * 5, [0.] * 5]], requires_grad=True)
    mask = torch.tensor([[True, True], [True, False]])
    losses = session_losses(pred, torch.zeros_like(pred), mask)
    assert losses.tolist() == pytest.approx([4, 10])
    assert float(losses.mean().detach()) == pytest.approx(7)
    assert (2 + 6 + 10) / 3 == 6  # Deliberately wrong pooled-origin oracle.
    losses.mean().backward()
    assert pred.grad is not None
    manual = torch.zeros_like(pred)
    manual[0] = pred.detach()[0] / 10
    manual[1, 0] = pred.detach()[1, 0] / 5
    assert torch.allclose(pred.grad, manual)


def test_sampler_and_16_plus_remainder_epoch_mean():
    groups = tuple(session_batches(19, 42, 1, shuffle=True))
    assert list(map(len, groups)) == [16, 3]
    assert sorted(i for group in groups for i in group) == list(range(19))
    assert groups == tuple(session_batches(19, 42, 1, shuffle=True))
    assert groups != tuple(session_batches(19, 42, 2, shuffle=True))
    assert tuple(session_batches(19, 42, 1, shuffle=False)) == (tuple(range(16)), (16, 17, 18))
    values = list(range(19))
    exact = sum(sum(values[i] for i in g) for g in groups) / 19
    naive = sum(sum(values[i] for i in g) / len(g) for g in groups) / 2
    assert exact == 9 and naive != exact


def test_optimizer_groups_and_global_clip():
    model = SharedLSTM()
    opt = optimizer(model)
    assert [g['weight_decay'] for g in opt.param_groups] == [.01, 0]
    members = [id(p) for g in opt.param_groups for p in g['params']]
    assert len(members) == len(set(members)) == len(tuple(model.parameters()))
    assert set(members) == {id(p) for p in model.parameters()}
    assert all(p.ndim == 2 for p in opt.param_groups[0]['params'])
    assert all(p.ndim == 1 for p in opt.param_groups[1]['params'])
    for p in model.parameters():
        p.grad = torch.full_like(p, 2)
    before = tuple(p.grad.clone() for p in model.parameters() if p.grad is not None)
    norm = clip(model)
    after = tuple(p.grad for p in model.parameters() if p.grad is not None)
    assert norm > 1
    assert math.sqrt(sum(float(g.square().sum()) for g in after)) == pytest.approx(1, abs=1e-6)
    assert all(torch.allclose(a, b / norm, atol=1e-6) for a, b in zip(after, before))
    for p in model.parameters():
        p.grad = torch.zeros_like(p)
    assert clip(model) == 0
    model.head.bias.grad = torch.full_like(model.head.bias, math.inf)
    with pytest.raises(RuntimeError):
        clip(model)


def test_complete_batch_and_bounded_planted_learning():
    seed_all(42)
    x = torch.zeros(1, 2, 5, 48, 16)
    values = torch.linspace(-1, 1, 5)
    x[0, 0, :, :, 0] = values[:, None]
    batch = SessionBatch(('SYN:DAY',), x, values.reshape(1, 1, 5).repeat(1, 2, 1),
                         torch.tensor([[True, False]]))
    model = SharedLSTM()
    opt = optimizer(model)
    model.eval()
    initial = float(session_losses(batch_prediction(model, batch), batch.targets,
                                   batch.origins).mean().detach())
    for _ in range(60):
        model.train()
        opt.zero_grad(set_to_none=True)
        loss = session_losses(batch_prediction(model, batch), batch.targets, batch.origins).mean()
        loss.backward()
        clip(model)
        opt.step()
    model.eval()
    final = float(session_losses(batch_prediction(model, batch), batch.targets,
                                 batch.origins).mean().detach())
    assert final < initial * .25
    with pytest.raises(ValueError):
        SessionBatch(batch.ids, x[:, :, :4], batch.targets, batch.origins).validate()
