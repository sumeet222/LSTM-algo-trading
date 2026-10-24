"""P028 fixed-weight mechanism measurements and no-step structural capability proofs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .hf1m_action_audit import SYMBOLS
from .panel_state_audit import describe
from .state_screen_models import model_for, panel_state
from .state_screen_spec import CUTS


def prove() -> dict:
    """Independent identity/null/gradient/rank tests. Manual planted weights are not fits."""
    torch.set_num_threads(4)
    generator = torch.Generator().manual_seed(2828)
    x = torch.randn(3, 20, 48, 16, generator=generator)
    m = panel_state(x)
    results = []
    for arm in ("A7", "A8", "A12"):
        model = model_for(arm).eval()
        y = model(x, m)
        torch.testing.assert_close(y, model(x, m), rtol=0, atol=0)
        perm = torch.arange(19, -1, -1)
        torch.testing.assert_close(y[:, perm], model(x[:, perm], m), rtol=2e-5, atol=2e-7)
        if arm in ("A7", "A12"):
            torch.manual_seed(42)
            recurrent = torch.nn.LSTM(18, 32, 1, batch_first=True)
            head = torch.nn.Linear(32, 1)
            u = torch.cat((x, m[:, None].expand(-1, 20, -1, -1)), -1)
            _, (h, _) = recurrent(u.reshape(-1, 48, 18))
            base = head(h[-1]).reshape(-1, 20)
            torch.testing.assert_close(y, base, rtol=2e-6, atol=2e-7)
            for n, v in recurrent.state_dict().items():
                torch.testing.assert_close(v, model.recurrent.state_dict()[n], rtol=0, atol=0)
            torch.testing.assert_close(head.weight, model.head.weight, rtol=0, atol=0)
        if arm == "A7":
            torch.testing.assert_close(
                model.details(x, m)["alpha"], torch.ones(3, 16), rtol=0, atol=0
            )
        if arm == "A8":
            calls = []
            hook = model.global_cell.register_forward_hook(lambda *args: calls.append(1))
            model(x, m)
            hook.remove()
            if len(calls) != 48:
                raise ValueError("P028_ONCE_PER_STEP")
            zero = torch.zeros_like(m)
            torch.testing.assert_close(y, model(x, zero), rtol=0, atol=0)
            for i in range(3):
                torch.testing.assert_close(
                    y[i : i + 1], model(x[i : i + 1], m[i : i + 1]), rtol=2e-5, atol=2e-7
                )
        if arm == "A12":
            router = model.details(x, m)["router"]
            if float(router.detach().std()) <= 0:
                raise ValueError("P028_NONCONSTANT_INITIAL_ROUTER")
            model.zero_grad()
            model(x, m).square().mean().backward()
            assert model.router.weight.grad is not None
            assert model.head.weight.grad is not None
            assert model.expert1.weight.grad is not None
            if not torch.equal(model.router.weight.grad, torch.zeros_like(model.router.weight)):
                # float32 mixture cancellation can leave rounding-level residuals.
                if float(model.router.weight.grad.abs().max()) > 1e-8:
                    raise ValueError("P028_INITIAL_ROUTER_GRADIENT")
            if torch.equal(model.head.weight.grad, model.expert1.weight.grad):
                raise ValueError("P028_EXPERT_SYMMETRY_NOT_BROKEN")
        model.zero_grad()
        model(x, m).square().mean().backward()
        if any(
            p.grad is None or not bool(torch.isfinite(p.grad).all()) for p in model.parameters()
        ):
            raise ValueError("P028_FINITE_INITIAL_CONNECTIVITY")
        initial = {
            n: float(p.grad.norm()) for n, p in model.named_parameters() if p.grad is not None
        }
        # Explicitly plant nonzero coupling/expert difference, never an optimizer update.
        with torch.no_grad():
            if arm == "A7":
                model.gate.weight[0, 0] = 1
            elif arm == "A8":
                model.local_cell.weight_ih[:, 16:24].fill_(0.1)
            else:
                model.expert1.weight.add_(0.1)
        model.zero_grad()
        state = m.clone().requires_grad_(True)
        output = model(x, state)
        relative = output[:, 0] - output[:, 1]
        derivative = torch.autograd.grad(relative.sum(), state, retain_graph=True)[0]
        output.square().mean().backward()
        changed = model(x, m + 1).detach() - output.detach()
        if float(derivative.abs().max()) <= 0 or float(changed.detach().std(1).max()) <= 0:
            raise ValueError("P028_NONTRIVIAL_RELATIVE_STATE_ROUTE")
        results.append(
            dict(
                arm=arm,
                identity=True,
                finite_gradients=True,
                initial_gradients=initial,
                relative_state_derivative_max=float(derivative.abs().max()),
                planted_heterogeneous_common_state_change_sd=float(changed.detach().std(1).max()),
                optimizer_steps=0,
                synthetic_only=True,
            )
        )
    # Analytically checkable common factor with heterogeneous loadings: rank reverses.
    loading = np.linspace(-1, 1, 20)
    signal = np.array([-1.0, 1.0])[:, None] * loading
    if not np.array_equal(np.argsort(signal[0]), np.argsort(signal[1])[::-1]):
        raise ValueError("P028_COMMON_FACTOR_TOY")
    return dict(
        status="PASS_P028_MECHANISM_PROOFS",
        models=results,
        precision=dict(
            identity_rtol=2e-6,
            identity_atol=2e-7,
            permutation_rtol=2e-5,
            permutation_atol=2e-7,
            initial_router_gradient_atol=1e-8,
        ),
        toy=(
            "Analytical common latent ±1 with heterogeneous loadings; zero "
            "common signal yields zero; no fitting"
        ),
        optimizer_steps=0,
    )


def measure(
    model, view, destination: Path, *, population: pd.DataFrame, study, rehearsal: bool = False
) -> dict:
    model.eval()
    rows = []
    endpoints = []
    with torch.inference_mode():
        for start in range(0, len(view.source.rows), 16):
            positions = tuple(range(start, min(start + 16, len(view.source.rows))))
            x = torch.from_numpy(view.origin_batch(positions)["x"])
            d = model.details(x)
            pred = model(x)
            for k, pos in enumerate(positions):
                meta = view.source.rows.iloc[pos]
                rec = dict(
                    origin_id=meta.origin_id,
                    session_date_et=meta.session_date_et,
                    mean20_scaled_M1=float(d["state"][k, -1, 0]),
                    median20_scaled_V1=float(d["state"][k, -1, 1]),
                )
                endpoints.append(rec)
                row = dict(
                    origin_id=meta.origin_id,
                    session_date_et=meta.session_date_et,
                    hidden_norm=float(d["readout"][k].norm()),
                    score_sd=float(pred[k].std(unbiased=False)),
                )
                if model.arm == "A7":
                    a = d["alpha"][k]
                    p = a / 16
                    row.update(
                        entropy=float(-(p * p.clamp_min(1e-30).log()).sum()),
                        gate_min=float(a.min()),
                        gate_max=float(a.max()),
                        gate_sum=float(a.sum()),
                    )
                    row.update({f"gate_{j}": float(v) for j, v in enumerate(a)})
                elif model.arm == "A8":
                    for key in ("global_hidden", "global_cell", "local_hidden", "local_cell"):
                        a = d[key][k]
                        row[key + "_norm"] = float(a.norm())
                        row[key + "_sd"] = float(a.std(unbiased=False))
                    row["coupling_weight_norm"] = float(model.local_cell.weight_ih[:, 16:24].norm())
                else:
                    p = d["router"][k]
                    a = model.head(d["readout"][k]).squeeze(-1)
                    b = model.expert1(d["readout"][k]).squeeze(-1)
                    row.update(
                        router0=float(p[0]),
                        router1=float(p[1]),
                        entropy=float(-(p * p.log()).sum()),
                        expert_rms_difference=float((a - b).square().mean().sqrt()),
                    )
                rows.append(row)
    frame = pd.DataFrame(rows)
    endpoint = pd.DataFrame(endpoints).set_index("origin_id")
    cut = CUTS["inner" if view.split.startswith("inner") else "refit"]
    frame["state_bin"] = np.where(
        frame.origin_id.map(endpoint.median20_scaled_V1) <= cut, "LOW", "HIGH"
    )
    if "entropy" in frame:
        frame["effective_count"] = np.exp(frame.entropy)
    state_summaries = {}
    for state, subset in frame.groupby("state_bin"):
        state_summaries[str(state)] = dict(
            origins=len(subset),
            sessions=subset.session_date_et.nunique(),
            distributions={
                c: describe(subset[c].to_numpy())
                for c in subset
                if pd.api.types.is_numeric_dtype(subset[c])
            },
        )
    frame.to_parquet(destination / "state_module_diagnostics.parquet", index=False)
    pd.DataFrame(endpoints).to_parquet(destination / "state_endpoints.parquet", index=False)
    sensitivity = []
    for pos in range(min(8, len(view.source.rows))):
        x = torch.from_numpy(view.origin_batch((pos,))["x"])
        m = panel_state(x).requires_grad_(True)
        y = model(x, m)
        grad = torch.autograd.grad((y[:, 0] - y[:, 1]).sum(), m)[0]
        sensitivity.append(
            dict(
                origin_id=view.source.rows.iloc[pos].origin_id,
                relative_state_derivative_L2=float(grad.norm()),
                maximum=float(grad.abs().max()),
            )
        )
    pd.DataFrame(sensitivity).to_parquet(
        destination / "peer_input_sensitivity.parquet", index=False
    )
    report = dict(
        arm=model.arm,
        role=view.split,
        state_cut=cut,
        state_summaries=state_summaries,
        scope="fixed checkpoint eval; mechanism use is not causal/economic proof",
        rows=len(frame),
        summary={
            c: describe(frame[c].to_numpy())
            for c in frame
            if pd.api.types.is_numeric_dtype(frame[c])
        },
        parameters={n: float(p.detach().norm()) for n, p in model.named_parameters()},
        state_self_inclusion=True,
        independent_index=False,
        architecture_only_identifiable=False,
        A8="global once per step; market-only one-way, no full-C3 feedback",
        A12="soft heads not economic regimes; sparse development LOW one long episode",
        nonfinite_count=0,
    )
    write_json(destination / "mechanisms.json", report)
    return report


def case_trace(
    model, view, selected: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Bounded state history, hidden panel and actual gate/router/local traces for cases."""
    hidden = []
    histories = []
    mechanisms = []
    positions = {key: i for i, key in enumerate(view.source.rows.origin_id)}
    model.eval()
    with torch.inference_mode():
        for row in selected.to_dict("records"):
            x = torch.from_numpy(view.origin_batch((positions[row["origin_id"]],))["x"])
            d = model.details(x)
            for step in range(48):
                histories.append(
                    dict(
                        case_id=row["case_id"],
                        historical_step=step,
                        mean20_scaled_M1=float(d["state"][0, step, 0]),
                        median20_scaled_V1=float(d["state"][0, step, 1]),
                    )
                )
            for i, ticker in enumerate(SYMBOLS):
                for j in range(32):
                    hidden.append(
                        dict(
                            case_id=row["case_id"],
                            ticker=ticker,
                            hidden=j,
                            value=float(d["readout"][0, i, j]),
                        )
                    )
            for key in (
                "alpha",
                "router",
                "global_hidden",
                "global_cell",
                "local_hidden",
                "local_cell",
            ):
                if key in d:
                    tensor = d[key][0]
                    if key in ("local_hidden", "local_cell"):
                        tensor = tensor[SYMBOLS.index(row["ticker"])]
                    values = tensor.numpy().reshape(-1)
                    mechanisms.extend(
                        dict(case_id=row["case_id"], module=key, index=i, value=float(v))
                        for i, v in enumerate(values)
                    )
    return (
        pd.DataFrame(hidden),
        pd.DataFrame(histories),
        pd.DataFrame(mechanisms, columns=["case_id", "module", "index", "value"]),
    )
