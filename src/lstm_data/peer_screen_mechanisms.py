"""Actual saved P027 peer use, source operands, Jacobians and stock-axis diagnostics."""

from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import ORDER
from .neural_engine import session_batches
from .objective_screen_source import gather, native_arrays
from .peer_screen_engine import state_hash
from .peer_screen_models import PeerModel, peer_statistics
from .peer_screen_spec import FAIRNESS


def spectrum(matrix: np.ndarray) -> dict:
    singular = np.linalg.svd(matrix, compute_uv=False)
    cutoff = (
        float(singular.max() * max(matrix.shape) * np.finfo(matrix.dtype).eps)
        if len(singular)
        else 0.0
    )
    positive = singular[singular > cutoff]
    probability = positive / positive.sum() if len(positive) else np.array([])
    return dict(
        shape=list(matrix.shape),
        singular_values=singular.tolist(),
        numerical_rank=len(positive),
        rank_cutoff=cutoff,
        effective_entropy_rank=float(np.exp(-(probability * np.log(probability)).sum()))
        if len(positive)
        else 0.0,
        nonzero_spectrum_condition=float(positive.max() / positive.min())
        if len(positive)
        else None,
        full_rank=bool(len(positive) == min(matrix.shape)),
    )


def source_cases(model: PeerModel, study, view, destination: Path, *, rehearsal: bool) -> dict:
    """Every case links all peer encoders; A4 additionally exposes all19×48 M1 operands."""
    cases = pd.read_parquet(destination / "cases.parquet")
    index = {v: i for i, v in enumerate(view.source.rows.origin_id)}
    native = native_arrays(study, view)
    quality = study.table("candles_quality").set_index(["step", "ticker"])
    operands = []
    summaries = []
    hidden = []
    attention = []
    with torch.inference_mode():
        for row in cases.to_dict("records"):
            position = index[row["origin_id"]]
            source = view.source.rows.iloc[position]
            x = view.origin_batch((position,))["x"]
            d = model.details(torch.from_numpy(x))
            focal = SYMBOLS.index(row["ticker"])
            u = gather(view, native, (position,), "native")[0, :, :, ORDER.index("M1")]
            missing = gather(view, native, (position,), "fallback")[0, :, :, ORDER.index("M1")]
            for peer, ticker in enumerate(SYMBOLS):
                for channel, value in enumerate(d["hidden"][0, peer].tolist()):
                    hidden.append(
                        dict(
                            case_id=row["case_id"],
                            origin_id=row["origin_id"],
                            focal=row["ticker"],
                            peer=ticker,
                            role_in_forecast=(
                                "FOCAL_ENCODER"
                                if peer == focal
                                else "CONTEXT_ONLY_NOT_A4_HIDDEN_INPUT"
                                if model.arm == "A4"
                                else "PEER_ENCODER_EXCHANGE"
                            ),
                            hidden_channel=channel,
                            value=value,
                            entry_end_utc=source.entry_end_utc,
                        )
                    )
                if model.arm == "A4" and peer != focal:
                    for step in range(48):
                        key = int(source.first_step) + step
                        q = quality.loc[(key, ticker)]
                        clock = (
                            q["hour_end_utc"]
                            if "hour_end_utc" in q
                            else pd.Timestamp(source.entry_end_utc) - pd.Timedelta(hours=47 - step)
                        )
                        if pd.Timestamp(clock) > pd.Timestamp(source.entry_end_utc):
                            raise ValueError("P027_FUTURE_CASE_PEER")
                        operands.append(
                            dict(
                                case_id=row["case_id"],
                                origin_id=row["origin_id"],
                                focal=row["ticker"],
                                peer=ticker,
                                step=key,
                                input_position=step,
                                hour_end_utc=clock,
                                native_M1=float(u[peer, step]),
                                scaled_M1=float(x[0, peer, step, 0]),
                                fallback=bool(missing[peer, step]),
                                volume_quality_tier=q["volume_quality_tier"],
                                source_scope="DRY_RUN_SYNTHETIC" if rehearsal else "PINNED_RELEASE",
                            )
                        )
                if model.arm == "A6":
                    for key_peer, name in enumerate(SYMBOLS):
                        attention.append(
                            dict(
                                case_id=row["case_id"],
                                origin_id=row["origin_id"],
                                query=ticker,
                                key=name,
                                probability=float(d["attention"][0, peer, key_peer]),
                            )
                        )
            if model.arm == "A4":
                a = peer_statistics(torch.from_numpy(x[..., 0]))[0, focal].numpy()
                for step in range(48):
                    selected = [v for v in range(20) if v != focal]
                    z = x[0, selected, step, 0].astype(float)
                    np.testing.assert_allclose(
                        a[step], [z.mean(), z.std(ddof=0)], rtol=1e-6, atol=2e-7
                    )
                    summaries.append(
                        dict(
                            case_id=row["case_id"],
                            input_position=step,
                            peer_mean=float(a[step, 0]),
                            peer_SD=float(a[step, 1]),
                            divisor=19,
                        )
                    )
    pd.DataFrame(hidden).to_parquet(destination / "case_peer_hidden.parquet", index=False)
    if model.arm == "A4":
        if len(operands) != 22 * 19 * 48 or len(summaries) != 22 * 48:
            raise ValueError("P027_EXACT_PEER_OPERAND_COUNTS")
        pd.DataFrame(operands).to_parquet(
            destination / "case_peer_M1_operands.parquet", index=False
        )
        pd.DataFrame(summaries).to_parquet(destination / "case_peer_summaries.parquet", index=False)
    if model.arm == "A6":
        pd.DataFrame(attention).to_parquet(destination / "case_peer_attention.parquet", index=False)
    return dict(
        cases=len(cases),
        peer_hidden_cells=len(hidden),
        peer_M1_operands=len(operands),
        attention_probabilities=len(attention),
        independent_M1_oracle="PASS" if model.arm == "A4" else "not applicable",
    )


def measure(
    model: PeerModel,
    view,
    destination: Path,
    *,
    population: pd.DataFrame,
    study,
    rehearsal: bool = False,
) -> dict:
    start = time.monotonic()
    model.eval()
    before = state_hash(model)
    batches = []
    records = []
    rows_seen = 0
    shift_square = base_square = 0.0
    with torch.inference_mode():
        for positions in session_batches(len(view.source.rows), 42, 1, shuffle=False):
            x = torch.from_numpy(view.origin_batch(positions)["x"])
            d = model.details(x)
            h = d["hidden"]
            base = model.head(h).squeeze(-1)
            score = model.head(d["readout"]).squeeze(-1)
            shift_square += float((score - base).square().sum())
            base_square += float(base.square().sum())
            rows_seen += score.numel()
            batches.append(
                dict(
                    origins=len(positions),
                    hidden_abs_mean=float(h.abs().mean()),
                    hidden_sd=float(h.std(unbiased=False)),
                    hidden_max=float(h.abs().max()),
                )
            )
            origins = view.source.rows.iloc[list(positions)]
            if model.arm == "A4":
                stats = peer_statistics(x[..., 0])
                f = pd.DataFrame(
                    dict(
                        origin_id=np.repeat(origins.origin_id.to_numpy(), 20),
                        ticker=np.tile(SYMBOLS, len(origins)),
                        session_date_et=np.repeat(origins.session_date_et.to_numpy(), 20),
                        own_M1=x[:, :, -1, 0].numpy().reshape(-1),
                        peer_mean=stats[:, :, -1, 0].numpy().reshape(-1),
                        peer_SD=stats[:, :, -1, 1].numpy().reshape(-1),
                        mean48=stats[..., 0].mean(-1).numpy().reshape(-1),
                        SD48=stats[..., 1].mean(-1).numpy().reshape(-1),
                    )
                )
                records.append(f)
            if model.arm == "A6":
                a = d["attention"]
                np.testing.assert_allclose(a.sum(-1).numpy(), 1, rtol=1e-6, atol=1e-7)
                if not bool(torch.isfinite(a).all()):
                    raise ValueError("P027_FINITE_ATTENTION")
                f = pd.DataFrame(a.numpy().reshape(-1, 20), columns=["peer_" + s for s in SYMBOLS])
                f["origin_id"] = np.repeat(origins.origin_id.to_numpy(), 20)
                f["ticker"] = np.tile(SYMBOLS, len(origins))
                f["session_date_et"] = np.repeat(origins.session_date_et.to_numpy(), 20)
                entropy = -(a * torch.log(a)).sum(-1)
                f["entropy"] = entropy.numpy().reshape(-1)
                f["normalized_entropy"] = (entropy / np.log(20)).numpy().reshape(-1)
                f["effective_peers"] = entropy.exp().numpy().reshape(-1)
                f["self_mass"] = a.diagonal(dim1=-2, dim2=-1).numpy().reshape(-1)
                f["peer_mass"] = 1 - f.self_mass
                if "V1_state" in population:
                    f = f.merge(
                        population[["origin_id", "ticker", "V1_state"]],
                        on=["origin_id", "ticker"],
                        validate="one_to_one",
                    )
                records.append(f)
    pd.DataFrame(batches).to_parquet(destination / "hidden_batches.parquet", index=False)
    summary: dict[str, object] = dict(
        arm=model.arm,
        fixed_population_stock_rows=rows_seen,
        information_fairness=FAIRNESS,
        mechanism_summary_weighting=(
            "Unweighted origin/stock summaries; objective/evaluation "
            "retain frozen session/origin/stock weights"
        ),
        scope=(
            "Saved checkpoint diagnostic; full-refit summaries and first8-ori"
            "gin local derivatives; not causal explanation"
        ),
        own_trained_base_readout_shift_RMS=float(np.sqrt(shift_square / rows_seen)),
        shift_relative_to_own_base_RMS=float(np.sqrt(shift_square / base_square))
        if base_square
        else None,
        projection_norms={
            n: float(p.detach().norm())
            for n, p in model.named_parameters()
            if n in ("M1", "M2", "WQ", "WK", "WV", "WO")
        },
    )
    if records:
        full = pd.concat(records, ignore_index=True)
        full.to_parquet(
            destination
            / (
                "peer_summary_distribution.parquet"
                if model.arm == "A4"
                else "attention_rows.parquet"
            ),
            index=False,
        )
        if model.arm == "A4":
            summary["last_step_own_peer_mean_correlation"] = float(
                np.corrcoef(full.own_M1, full.peer_mean)[0, 1]
            )
        else:
            summary["attention_summary"] = {
                c: float(full[c].mean())
                for c in (
                    "entropy",
                    "normalized_entropy",
                    "effective_peers",
                    "self_mass",
                    "peer_mass",
                )
            }
            full.groupby(["ticker", "session_date_et"], as_index=False)[
                ["entropy", "self_mass", "peer_mass"]
            ].mean().to_parquet(destination / "attention_ticker_day.parquet", index=False)
            if "V1_state" in full:
                full.groupby("V1_state", as_index=False)[
                    ["entropy", "self_mass", "peer_mass"]
                ].mean().to_parquet(destination / "attention_V1_state.parquet", index=False)
    if model.arm == "A5":
        first = model.M1.detach().numpy().astype(float)
        second = model.M2.detach().numpy().astype(float)
        product = second @ first
        summary["matrix_spectra"] = {
            name: spectrum(value)
            for name, value in [
                ("M1", first),
                ("M2", second),
                ("M2M1_linear_proxy_not_nonlinear_rank", product),
            ]
        }
        mass = abs(product).sum()
        summary["linear_proxy_concentration"] = dict(
            max_row_fraction=float(abs(product).sum(1).max() / mass) if mass else 0.0,
            max_column_fraction=float(abs(product).sum(0).max() / mass) if mass else 0.0,
            diagonal_absolute_mass_fraction=float(abs(product.diagonal()).sum() / mass)
            if mass
            else 0.0,
        )
        pd.DataFrame(
            [
                dict(target=SYMBOLS[i], peer=SYMBOLS[j], linear_proxy_weight=float(product[i, j]))
                for i in range(20)
                for j in range(20)
            ]
        ).to_parquet(destination / "stock_mixing_matrix.parquet", index=False)
        pd.DataFrame(
            [
                dict(matrix="M1", stock=SYMBOLS[j], bottleneck=k, value=float(first[k, j]))
                for k in range(4)
                for j in range(20)
            ]
            + [
                dict(matrix="M2", stock=SYMBOLS[j], bottleneck=k, value=float(second[j, k]))
                for k in range(4)
                for j in range(20)
            ]
        ).to_parquet(destination / "stock_mixing_parameters.parquet", index=False)
    positions = tuple(range(min(8, len(view.source.rows))))
    x = torch.from_numpy(view.origin_batch(positions)["x"]).requires_grad_(True)
    if model.arm == "A4":
        augmented = model.augmented(x).detach().requires_grad_(True)
        _, (h, _) = model.recurrent(augmented.reshape(-1, 48, 18))
        output = model.head(h[-1]).sum()
        gradient = torch.autograd.grad(output, augmented)[0]
        summary["extra_channel_gradient_norms"] = [float(gradient[..., j].norm()) for j in (16, 17)]
        summary["nondifferentiable_zero_SD_points"] = int(
            (peer_statistics(x[..., 0])[..., 1] == 0).sum()
        )
    d = model.details(x)
    output = model.head(d["readout"]).squeeze(-1)
    edges = []
    # At zero peer dispersion the SD input derivative is undefined; keep honest status.
    can_differentiate = model.arm != "A4" or summary["nondifferentiable_zero_SD_points"] == 0
    if can_differentiate:
        for i, target in enumerate(SYMBOLS):
            g = torch.autograd.grad(output[:, i].sum(), x, retain_graph=True)[0]
            if not torch.isfinite(g).all():
                raise ValueError("P027_NONFINITE_PEER_INPUT_DERIVATIVE")
            norms = g.detach().square().sum((2, 3)).sqrt().mean(0).numpy()
            edges.extend(
                dict(target=target, peer=peer, input_gradient_norm=float(norms[j]))
                for j, peer in enumerate(SYMBOLS)
            )
    pd.DataFrame(edges, columns=["target", "peer", "input_gradient_norm"]).to_parquet(
        destination / "peer_input_sensitivity.parquet", index=False
    )
    if model.arm != "A4":
        h = model.encode(x).detach().requires_grad_(True)
        out = model.head(model.exchange(h)["readout"]).squeeze(-1)
        hidden_edges = []
        for i, target in enumerate(SYMBOLS):
            g = torch.autograd.grad(out[:, i].sum(), h, retain_graph=True)[0]
            norms = g.detach().square().sum(-1).sqrt().mean(0).numpy()
            hidden_edges.extend(
                dict(target=target, peer=peer, hidden_gradient_norm=float(norms[j]))
                for j, peer in enumerate(SYMBOLS)
            )
        pd.DataFrame(hidden_edges).to_parquet(
            destination / "peer_hidden_jacobian.parquet", index=False
        )
        summary["off_diagonal_hidden_jacobian_norm_sum"] = float(
            sum(r["hidden_gradient_norm"] for r in hidden_edges if r["target"] != r["peer"])
        )
    with torch.inference_mode():
        donor = x.detach().clone()
        donor[..., 0] += 0.1
        delta = model.shifted(x.detach(), donor) - model.shifted(x.detach(), x.detach())
        pd.DataFrame(
            dict(
                ticker=SYMBOLS,
                mean_z_change=delta.mean(0).numpy(),
                RMS_z_change=delta.square().mean(0).sqrt().numpy(),
            )
        ).to_parquet(destination / "own_fixed_peer_M1_perturbation.parquet", index=False)
        summary["peer_M1_plus_point1_RMS_z_change"] = float(delta.square().mean().sqrt())
        permutation = torch.arange(19, -1, -1)
        equivalent = copy.deepcopy(model)
        if model.arm == "A5":
            equivalent.M1.copy_(model.M1[:, permutation])
            equivalent.M2.copy_(model.M2[permutation])
        torch.testing.assert_close(
            equivalent(x.detach()[:, permutation]),
            model(x.detach())[:, permutation],
            rtol=3e-5,
            atol=2e-6,
        )
    summary["saved_coordinate_permutation_check"] = "PASS"
    summary["source_case_peers"] = source_cases(
        model, study, view, destination, rehearsal=rehearsal
    )
    if state_hash(model) != before:
        raise ValueError("P027_MECHANISM_MUTATED_MODEL")
    summary["inference_and_diagnostic_seconds"] = time.monotonic() - start
    write_json(destination / "mechanisms.json", summary)
    return summary
