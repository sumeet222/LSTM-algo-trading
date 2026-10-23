"""P025 complete immediate scientific gate, shared by rehearsal and authorized fits."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .branch_replication_comparison import baseline_path, comparison, heterogeneity
from .branch_replication_engine import model_for, predict
from .branch_replication_metrics import event_metrics, qr_metrics
from .branch_replication_spec import ROLES
from .branch_replication_states import causal_states, plots, state_analysis, state_cutoffs
from .config import digest, fingerprint, write_json
from .dm_quantile_cases import exact_cases
from .dm_quantile_diagnostics import allocation
from .hf1m_ft16_source import checked, ref
from .neural_engine import optimizer
from .objective_screen_attribution import allocations, cohort_masks, cohort_table
from .objective_screen_diagnostics import canonical
from .objective_screen_run import Selector
from .objective_screen_source import ordered_targets, scoped_view
from .optimization_screen_diagnostics import original_identity
from .visualization.hf1m_long import LongStudy


def exact_optimizer(model, opt) -> dict:
    """Assert every parameter and all floating settings exactly, before any fitting."""
    names = {id(p): n for n, p in model.named_parameters()}
    seen = []
    groups = []
    for group in opt.param_groups:
        if group["lr"] != 0.001 or group["betas"] != (0.9, 0.999) or group["eps"] != 1e-8:
            raise ValueError("P025_EXACT_OPTIMIZER_FLOATS")
        members = [names[id(p)] for p in group["params"]]
        if any(group["weight_decay"] != (0.01 if p.ndim >= 2 else 0.0) for p in group["params"]):
            raise ValueError("P025_MATRIX_BIAS_DECAY")
        seen.extend(members)
        groups.append(
            dict(
                names=members,
                lr=group["lr"],
                betas=list(group["betas"]),
                eps=group["eps"],
                weight_decay=group["weight_decay"],
            )
        )
    if sorted(seen) != sorted(names.values()) or len(seen) != len(set(seen)):
        raise ValueError("P025_EXHAUSTIVE_UNIQUE_OPTIMIZER")
    return dict(parameters=sum(p.numel() for p in model.parameters()), groups=groups)


def verify_magnitude_order(y: np.ndarray, z: np.ndarray) -> int:
    """Verify monotonicity exactly, permitting representational ties under asinh.

    Distinct adjacent float64 |y| can map to exactly equal float64 |z|. That
    cannot change a strict magnitude ordering; the original y ranks are retained.
    cohort_masks separately checks exact canonical top1/5 membership equality.
    """
    order = np.argsort(abs(y), kind="stable")
    delta = np.diff(abs(z[order]))
    if (delta < 0).any():
        raise ValueError("P025_ASINH_MAGNITUDE_ORDER_REVERSAL")
    return int(((np.diff(abs(y[order])) > 0) & (delta == 0)).sum())


def diagnose(plan: dict, result_path: Path, destination: Path, *, rehearsal: bool = False) -> dict:
    import torch

    r = json.loads(result_path.read_text())
    if (r["scope"] == "REHEARSAL_ONLY") != rehearsal:
        raise ValueError("P025_SCOPE_MISMATCH")
    arm = r["arm"]
    from .branch_replication_authority import code_binding

    if (
        r["execution_sha256"] != fingerprint(code_binding())
        or r["initial_hash"] != r["refit_initial_hash"]
    ):
        raise ValueError("P025_EXECUTION_OR_FRESH_REFIT_IDENTITY")
    selector = Selector()
    for epoch in r["epochs"]:
        receipt = (
            result_path.parent
            / "epoch_receipts"
            / f"{epoch['phase']}_{epoch['training']['epoch']:03d}.json"
        )
        if json.loads(receipt.read_text()) != epoch:
            raise ValueError("P025_IMMUTABLE_PROGRESS_RECEIPT")
        if epoch["phase"] == "calibration":
            qualifies = selector.observe(epoch["validation"]["optimized_objective"])
            if qualifies != epoch["qualifies"] or asdict(selector) != epoch["selector"]:
                raise ValueError("P025_SELECTOR_REPLAY")
    if (
        asdict(selector) != r["selector"]
        or json.loads((result_path.parent / "epochs_progress.json").read_text()) != r["epochs"]
    ):
        raise ValueError("P025_COMPLETE_SELECTOR_PROGRESS")
    updates = [
        json.loads(line) for line in checked(r["optimizer_telemetry"]).read_text().splitlines()
    ]
    expected_steps = 0 if rehearsal else sum(e["training"]["optimizer_steps"] for e in r["epochs"])
    if sum(u["optimizer_step"] for u in updates) != expected_steps:
        raise ValueError("P025_UPDATE_COUNT")
    for u in updates:
        if u["lr"] != [0.001, 0.001] or u["weight_decay"] != [0.01, 0.0]:
            raise ValueError("P025_NESTED_FLOAT_HYPERPARAMETERS")
        if (
            not np.isfinite(
                [u["preclip_norm"], u["postclip_norm"], u["weight_norm"], u["update_norm"]]
            ).all()
            or u["postclip_norm"] > 1.00001
        ):
            raise ValueError("P025_GRADIENT_OR_WEIGHT_INTEGRITY")
        if not u["model_state_sha256"] or not u["optimizer_state_sha256"]:
            raise ValueError("P025_COMPLETE_STATE_HASHES")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / ".gitignore").write_text("*\n!.gitignore\n")
    study = LongStudy.discover(Path.cwd())
    tables, checks, evidence = [], [], [ref(result_path)]
    training, cutoffs, baseline_cutoffs = {}, {}, {}
    cases = None
    for role in ROLES:
        version = "inner" if role.startswith("inner") else "refit"
        recipe = plan["recipes"][arm][version]
        view = scoped_view(study, role, stage=7)
        saved = r["populations"][role]
        f = canonical(pd.read_parquet(checked(saved["population"])), ordered_targets(view))
        model = model_for(arm)
        checkpoint = torch.load(
            checked(r["calibration" if version == "inner" else "refit"]),
            weights_only=True,
            map_location="cpu",
        )
        model.load_state_dict(checkpoint["state_dict"])
        exact_optimizer(model, optimizer(model))
        reload = predict(model, view, arm, recipe, saved["binding"])
        pd.testing.assert_frame_equal(f, reload, check_exact=True)
        original_identity(study, view, f)
        if arm == "E1":
            f, pairs = allocations(f, arm, recipe)
            raw = f[["logit_NEG", "logit_NORMAL", "logit_POS"]].to_numpy(dtype=float)
            logsum = np.logaddexp.reduce(raw, axis=1)
            # Supervision in the actual objective is float32, including threshold ties.
            from .objective_screen_loss import classes

            label = classes(f.TG20.to_numpy(dtype=np.float32), recipe["q95_abs_y"])
            np.testing.assert_allclose(
                f.raw, logsum - raw[np.arange(len(f)), label], rtol=3e-5, atol=2e-6
            )
        else:
            f = allocation(f, arm, recipe)
            pairs = pd.DataFrame()
            q = f[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
            qy = f[["quantiles_y_05", "quantiles_y_50", "quantiles_y_95"]].to_numpy(dtype=float)
            np.testing.assert_allclose(qy, recipe["scale"] * np.sinh(q), rtol=7e-7, atol=1e-7)
            if not (np.diff(q, axis=1) >= 0).all() or not (np.diff(qy, axis=1) >= 0).all():
                raise ValueError("P025_QUANTILE_ORDER")
        np.testing.assert_allclose(f.total.sum(), saved["fixed_objective"], rtol=5e-7, atol=1e-8)
        if role in ("inner_train", "refit"):
            training[version] = f
        quality = study.targets(role)
        extra = [c for c in quality if c not in f]
        f = f.merge(
            quality[["origin_id", "ticker"] + extra],
            on=["origin_id", "ticker"],
            validate="one_to_one",
        )
        masks, threshold = cohort_masks(f, training[version])
        # asinh is monotone in |y|, so the stable ranked order must be identical.
        transform_ties = verify_magnitude_order(f.TG20.to_numpy(), f.z.to_numpy())
        table = cohort_table(f, masks, threshold)
        table["role"] = role
        tables.append(table)
        dest = destination / role
        dest.mkdir()
        baseline_reference = next(
            (r for r in plan["baseline_refs"] if r["path"] == str(baseline_path(arm, role))), None
        )
        if baseline_reference is None:
            raise ValueError("P025_BOUND_MATCHED_BASELINE_REQUIRED")
        checked(baseline_reference)
        paired, day_differences = comparison(f, arm, role, recipe)
        paired["scope"] = r["scope"]
        write_json(dest / "matched_seed42_comparison.json", paired)
        day_differences.to_parquet(dest / "matched_daily_differences.parquet", index=False)
        heterogeneity(f).to_parquet(dest / "stock_year_era_quality.parquet", index=False)
        f.to_parquet(dest / "population.parquet", index=False)
        write_json(dest / "thresholds.json", threshold)
        if arm == "E1":
            metrics, curve = event_metrics(f, recipe)
            correction, corrected_curve = event_metrics(f, recipe, inverse=True)
            metrics["analytical_inverse_weight"] = correction
            curve.to_parquet(dest / "PR_raw.parquet", index=False)
            corrected_curve.to_parquet(dest / "PR_inverse_weight.parquet", index=False)
        else:
            metrics = qr_metrics(f, recipe)
            states = causal_states(study, view)
            if role in ("inner_train", "refit"):
                cutoffs[version] = state_cutoffs(f, states)
            state_table, enriched, response = state_analysis(f, states, cutoffs[version], recipe)
            state_table.to_parquet(dest / "state_metrics.parquet", index=False)
            enriched.to_parquet(dest / "state_population.parquet", index=False)
            write_json(dest / "state_response.json", response)
            write_json(dest / "training_state_cutoffs.json", cutoffs[version])
            if role == "development":
                plots(state_table, dest)
            baseline = canonical(
                pd.read_parquet(checked(baseline_reference)), ordered_targets(view)
            )
            if role in ("inner_train", "refit"):
                baseline_cutoffs[version] = state_cutoffs(baseline, states)
            baseline_table, _, baseline_response = state_analysis(
                baseline, states, baseline_cutoffs[version], recipe
            )
            baseline_table.to_parquet(dest / "seed42_state_metrics.parquet", index=False)
            write_json(dest / "seed42_state_response.json", baseline_response)
            write_json(dest / "seed42_training_state_cutoffs.json", baseline_cutoffs[version])
        metrics["fixed_checkpoint_actual_objective"] = float(f.total.sum())
        metrics["scope"] = r["scope"]
        write_json(dest / "metrics.json", metrics)
        if role == "refit":
            extras = {}
            for name in ("BOTH_5", "MAD_ONLY_5"):
                if name in masks and masks[name].any():
                    index = (
                        f.loc[masks[name]]
                        .sort_values(["total", "origin_id"], ascending=[False, True])
                        .index[0]
                    )
                    extras[int(index)] = name
            cases = exact_cases(study, view, f, pairs, arm, recipe, dest, extras)
        checks.append(
            dict(
                role=role,
                rows=len(f),
                sessions=f.session_date_et.nunique(),
                objective=float(f.total.sum()),
                reload_exact=True,
                targets_reconstructed=True,
                asinh_float64_collapsed_adjacent_ties=transform_ties,
            )
        )
        evidence.extend(ref(p) for p in sorted(dest.iterdir()) if p.is_file())
    if cases is None or cases["cases"] < 20 or cases["candles"] != 52 * cases["cases"]:
        raise ValueError("P025_COMPLETE_EXACT_CASES")
    pd.concat(tables).to_parquet(destination / "cohorts.parquet", index=False)
    evidence.append(ref(destination / "cohorts.parquet"))
    gate = dict(
        status=f"PASS_{arm}_S123",
        scope=r["scope"],
        all_roles=4,
        proposal_sha256=r["proposal_sha256"],
        execution_sha256=r["execution_sha256"],
        scientific_sha256=plan["scientific_definitions"]["sha256"],
        objective_reconciled=True,
        reload_reconciled=True,
        roles=checks,
        cases=cases,
        evidence=evidence,
        evidence_fingerprint=fingerprint(evidence),
        result_sha256=digest(result_path),
    )
    write_json(destination / "gate.json", gate)
    return gate
