"""Independent MC1 algebra, matched-core identity and actual gradient oracles."""

import math

import pytest
import torch

from lstm_data.neural_engine import clip, optimizer, seed_all
from lstm_data.neural_models import EndpointGate, EndpointGatedLSTM, create_model, gate_diagnostics


@pytest.fixture(scope="module", autouse=True)
def cpu_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def inputs():
    seed_all(42)
    stock = torch.randn(2, 5, 48, 16)
    market = torch.randn(2, 48, 5)
    market[:, 4] = 0
    return torch.cat((stock, market[:, None].expand(-1, 5, -1, -1)), dim=-1).reshape(10, 48, 21)


def test_algebra_count_and_matched_core_identity():
    x = inputs()
    mc0 = create_model("MC0")
    mc1 = create_model("MC1")
    assert isinstance(mc1, EndpointGatedLSTM)
    mc1.core.load_state_dict(mc0.state_dict())
    mc0.eval()
    mc1.eval()
    composed, a = mc1.compose(x)
    assert torch.equal(a, torch.ones(2, 16)) and torch.equal(composed, x)
    assert torch.equal(mc1(x), mc0(x))
    assert sum(p.numel() for p in mc0.parameters()) == 7073
    assert sum(p.numel() for p in mc1.parameters()) == 7169
    diag = gate_diagnostics(a)
    assert diag["entropy_mean"] == pytest.approx(math.log(16), abs=1e-6)
    assert diag["constant_gate_warning"] and diag["positive"]
    gate = EndpointGate()
    logits = torch.linspace(-20, 20, 16)
    with torch.no_grad():
        gate.linear.bias.copy_(logits)
    a = gate(torch.tensor([[1e4] * 5, [1e4] * 5]))
    independent = 16 * torch.exp(logits - logits.max()) / torch.exp(logits - logits.max()).sum()
    assert torch.allclose(a[0], independent, atol=2e-6)
    assert (a > 0).all() and (a < 1).any() and (a > 1).any()
    assert torch.allclose(a.sum(-1), torch.full((2,), 16.0))
    with torch.no_grad():
        gate.linear.bias[0] = 1e6
    with pytest.raises(ValueError, match="POSITIVE"):
        gate(torch.zeros(1, 5))


def test_endpoint_shared_gate_and_historical_direct_inputs():
    x = inputs()
    model = EndpointGatedLSTM()
    with torch.no_grad():
        model.gate.linear.weight.copy_(torch.arange(80).reshape(16, 5) * 0.01)
    z, a = model.compose(x)
    historical = x.reshape(2, 5, 48, 21).clone()
    historical[0, :, 3, 16:] += 1
    zh, ah = model.compose(historical.reshape(10, 48, 21))
    assert torch.equal(a, ah)
    assert torch.equal(z[..., :16], zh[..., :16])
    assert not torch.equal(z[..., 16:], zh[..., 16:])
    endpoint = x.reshape(2, 5, 48, 21).clone()
    endpoint[0, :, -1, 16:] += 0.5
    ze, ae = model.compose(endpoint.reshape(10, 48, 21))
    assert not torch.equal(a[0], ae[0]) and torch.equal(a[1], ae[1])
    expected = x.reshape(2, 5, 48, 21)[..., :16] * ae[:, None, None, :]
    assert torch.equal(ze.reshape(2, 5, 48, 21)[..., :16], expected)
    assert torch.equal(ze.reshape(2, 5, 48, 21)[..., 16:], endpoint[..., 16:])
    assert torch.equal(zh.reshape(2, 5, 48, 21)[:, :, 4, 16:], torch.zeros(2, 5, 5))
    # Neutral history does not create an MC2 identity gate at that step.
    assert torch.equal(
        z.reshape(2, 5, 48, 21)[:, :, 4, :16], x.reshape(2, 5, 48, 21)[:, :, 4, :16] * a[:, None, :]
    )
    peer_bad = x.clone()
    peer_bad[1, 2, 16:] += 1
    with pytest.raises(ValueError, match="SHARED"):
        model(peer_bad)
    with pytest.raises(ValueError):
        model(x[:4])


def test_actual_gradient_optimizer_global_clip_and_short_update():
    x = inputs().requires_grad_()
    model = EndpointGatedLSTM()
    opt = optimizer(model)
    before = model.gate.linear.weight.detach().clone()
    loss = (model(x) - torch.linspace(-2, 3, 10)).square().mean() * 100
    loss.backward()
    parameters = dict(model.named_parameters())
    for name in (
        "gate.linear.weight",
        "gate.linear.bias",
        "core.lstm.weight_ih_l0",
        "core.head.weight",
    ):
        p = parameters[name]
        assert p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum() > 0
    assert x.grad is not None and torch.isfinite(x.grad).all() and x.grad.abs().sum() > 0
    params = [p for group in opt.param_groups for p in group["params"]]
    assert len({id(p) for p in params}) == len(params) == len(list(model.parameters()))
    assert sum(p.numel() for p in params) == 7169
    assert id(model.gate.linear.weight) in {id(p) for p in opt.param_groups[0]["params"]}
    assert id(model.gate.linear.bias) in {id(p) for p in opt.param_groups[1]["params"]}
    pre = clip(model)
    assert pre > 1
    norm = torch.sqrt(
        sum(
            (p.grad.square().sum() for p in model.parameters() if p.grad is not None),
            torch.tensor(0.0),
        )
    )
    assert norm <= 1.000001
    opt.step()
    assert not torch.equal(before, model.gate.linear.weight)
    assert gate_diagnostics(model.compose(x.detach())[1])["positive"]
    p = model.gate.linear.weight
    assert p.grad is not None
    p.grad[0, 0] = float("nan")
    with pytest.raises(RuntimeError):
        clip(model)
    for bad in (
        torch.zeros(2, 4),
        torch.zeros(2, 5, dtype=torch.float64),
        torch.full((2, 5), float("nan")),
    ):
        with pytest.raises(ValueError):
            model.gate(bad)


@pytest.mark.parametrize("seed", [42, 123, 2026])
def test_registered_fresh_initialization(seed):
    for arch in ("MC0", "MC1"):
        seed_all(seed)
        a = create_model(arch)
        seed_all(seed)
        b = create_model(arch)
        assert all(torch.equal(a.state_dict()[k], v) for k, v in b.state_dict().items())
        assert not optimizer(b).state
        if isinstance(b, EndpointGatedLSTM):
            assert torch.equal(b.gate.linear.weight, torch.zeros(16, 5))
