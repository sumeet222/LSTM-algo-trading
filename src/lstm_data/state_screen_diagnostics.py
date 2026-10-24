"""P028 independent saved-checkpoint scientific gate, required before each next start."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .branch_replication_diagnostics import verify_magnitude_order
from .config import digest, fingerprint, write_json
from .hf1m_ft16_source import checked, ref
from .neural_lifecycle import EarlyStop
from .objective_screen_attribution import cohort_masks, cohort_table
from .objective_screen_diagnostics import canonical, daily_scores
from .objective_screen_run import storage_bytes
from .objective_screen_source import ordered_targets
from .optimization_screen_diagnostics import original_identity
from .state_screen_cases import collect as collect_cases
from .state_screen_control import evaluate as peer_information_control
from .state_screen_engine import peak_rss_bytes, predict
from .state_screen_mechanisms import measure
from .state_screen_metrics import allocation, heterogeneity, metrics, paired
from .state_screen_models import exact_optimizer, model_for, optimizer
from .state_screen_spec import ROLES
from .visualization.hf1m_long import LongStudy


def diagnose(
    plan: dict,
    result_path: Path,
    destination: Path,
    *,
    rehearsal: bool = False,
    study_override=None,
) -> dict:
    from .state_screen_authority import code_binding
    from .state_screen_run import get_view

    if study_override is not None and not rehearsal:
        raise ValueError("P028_MOCK_IS_NOT_SCIENTIFIC_AUTHORITY")
    r = json.loads(result_path.read_text())
    if (
        (r["scope"] == "REHEARSAL_ONLY") != rehearsal
        or r["execution_sha256"] != fingerprint(code_binding())
        or r["initial_hash"] != r["refit_initial_hash"]
    ):
        raise ValueError("P028_RESULT_SCOPE_BINDING_INITIALIZATION")
    selector = EarlyStop()
    for epoch in r["epochs"]:
        receipt = (
            result_path.parent
            / "epoch_receipts"
            / f"{epoch['phase']}_{epoch['training']['epoch']:03d}.json"
        )
        if json.loads(receipt.read_text()) != epoch:
            raise ValueError("P028_IMMUTABLE_PROGRESS")
        if epoch["phase"] == "calibration":
            if (
                selector.observe(epoch["validation"]["original_mse"]) != epoch["qualifies"]
                or asdict(selector) != epoch["selector"]
            ):
                raise ValueError("P028_EXACT_T2_SELECTOR_REPLAY")
    if (
        asdict(selector) != r["selector"]
        or json.loads((result_path.parent / "epochs_progress.json").read_text()) != r["epochs"]
    ):
        raise ValueError("P028_COMPLETE_SELECTOR")
    updates = [
        json.loads(line) for line in checked(r["optimizer_telemetry"]).read_text().splitlines()
    ]
    if sum(u["optimizer_step"] for u in updates) != (
        0 if rehearsal else sum(e["training"]["optimizer_steps"] for e in r["epochs"])
    ):
        raise ValueError("P028_UPDATES")
    for u in updates:
        if (
            (not rehearsal and u["lr"] != [0.001, 0.001])
            or (not rehearsal and u["weight_decay"] != [0.01, 0.0])
            or not np.isfinite(
                [u["weight_norm"], u["update_norm"]]
                if rehearsal
                else [u["preclip_norm"], u["postclip_norm"], u["weight_norm"], u["update_norm"]]
            ).all()
            or (not rehearsal and u["postclip_norm"] > 1.00001)
        ):
            raise ValueError("P028_ACTUAL_TELEMETRY_HYPERPARAMETERS")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / ".gitignore").write_text("*\n!.gitignore\n")
    study = (
        study_override
        if rehearsal and study_override is not None
        else LongStudy.discover(Path.cwd())
    )
    training = {}
    tables = []
    checks = []
    peer_checks = []
    evidence = [ref(result_path)]
    case_summary = None
    case_populations = {}
    arm = r["arm"]
    for role in ROLES:
        version = "inner" if role.startswith("inner") else "refit"
        view = get_view(study, role, rehearsal)
        recipe = plan["recipes"][arm][version]
        saved = r["populations"][role]
        f = canonical(pd.read_parquet(checked(saved["population"])), ordered_targets(view))
        model = model_for(arm)
        checkpoint = r["calibration" if version == "inner" else "refit"]
        model.load_state_dict(
            torch.load(checked(checkpoint), weights_only=True, map_location="cpu")["state_dict"]
        )
        exact_optimizer(model, optimizer(model))
        reload = predict(model, view, arm, recipe, saved["binding"])
        pd.testing.assert_frame_equal(f, reload, check_exact=True)
        original_identity(study, view, f)
        f = allocation(f, recipe["scale"])
        np.testing.assert_allclose(
            f.pred_original_TG20,
            recipe["scale"] * np.sinh(f.raw_net_output.to_numpy(dtype=float)),
            rtol=7e-7,
            atol=1e-7,
        )
        np.testing.assert_allclose(f.total.sum(), saved["fixed_objective"], rtol=5e-7, atol=1e-8)
        if role in ("inner_train", "refit"):
            training[version] = f.copy()
        transform_ties = verify_magnitude_order(f.TG20.to_numpy(), f.z.to_numpy())
        masks, thresholds = cohort_masks(f, training[version])
        table = cohort_table(f, masks, thresholds)
        table["role"] = role
        tables.append(table)
        dest = destination / role
        dest.mkdir()
        f["year"] = f.session_date_et.str[:4]
        f["era"] = np.select(
            [f.year.le("2015"), f.year.le("2020")], ["2011–15", "2016–20"], default="2021–25"
        )
        f["month"] = f.session_date_et.str[:7]
        if not rehearsal:
            quality = study.targets(role)
            extras = [c for c in quality if c not in f]
            f = f.merge(
                quality[["origin_id", "ticker"] + extras],
                on=["origin_id", "ticker"],
                validate="one_to_one",
            )
            from .state_screen_models import panel_state
            from .state_screen_spec import CUTS

            values = []
            for start in range(0, len(view.source.rows), 32):
                pos = tuple(range(start, min(start + 32, len(view.source.rows))))
                values.extend(
                    panel_state(torch.from_numpy(view.origin_batch(pos)["x"])).numpy()[:, -1, 1]
                )
            v = np.repeat(values, 20)
            f["panel_state2"] = v
            f["V1_state"] = np.where(v <= CUTS[version], "LOW", "HIGH")
            write_json(
                dest / "V1_state_definition.json",
                dict(
                    channel="median20_scaled_fallback_V1",
                    input_step=47,
                    fit_version=version,
                    cut=CUTS[version],
                    method="first-origin fitting-session median; LOW<=cut/HIGH>cut; descriptive",
                ),
            )
            sectors = json.loads(Path("configs/hf_twelvedata_hourly_audit_v3.json").read_text())[
                "publisher_sector_etfs"
            ]
            f["sector_context"] = f.ticker.map(sectors).fillna("UNKNOWN")
            quality_columns = [
                c
                for c in (
                    "assumed_zero_minute_count",
                    "price_proxy_minute_count",
                    "poor_volume_hour_count",
                )
                if c in f
            ]
            f["quality"] = np.where(f[quality_columns].sum(axis=1) > 0, "FLAGGED", "NO_LISTED_FLAG")
            counter = f[version + "_feature_fallback_cells"]
            f["fallback_state"] = np.where(
                counter.isna(),
                "UNKNOWN_METADATA",
                np.where(counter.gt(0), "ANY_PANEL_PREFIX_FALLBACK", "NO_PANEL_PREFIX_FALLBACK"),
            )
        else:
            f["fallback_state"] = "DRY_RUN_CONTROLLED_NOT_VENDOR"
        result = metrics(f, training[version])
        result["scope"] = r["scope"]
        baselines = []
        for seed in (42, 123):
            b = study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", role).copy()
            if "TG20" not in b:
                b["TG20"] = b.actual_TG20
            b = canonical(b, ordered_targets(view))
            b.to_parquet(dest / f"T2_S{seed}.parquet", index=False)
            from .state_screen_metrics import regression

            bm = regression(
                b.TG20.to_numpy(), b.pred_original_TG20.to_numpy(), b.session_date_et.to_numpy()
            )
            bm["optimized_z_mse"] = float(allocation(b, recipe["scale"]).total.sum())
            baselines.append(dict(name=f"T2/{seed}", metrics=bm))
            if seed == 42:
                matched, days = paired(f, b)
                write_json(dest / "matched_T2_S42.json", matched)
                days.to_parquet(dest / "paired_daily.parquet", index=False)
        baselines.append(
            dict(
                name="ZERO",
                metrics=regression(
                    f.TG20.to_numpy(), np.zeros(len(f)), f.session_date_et.to_numpy()
                ),
            )
        )
        result["baselines"] = baselines
        write_json(dest / "metrics.json", result)
        write_json(dest / "thresholds.json", thresholds)
        heterogeneity(f).to_parquet(dest / "heterogeneity.parquet", index=False)
        daily_scores(f, f.pred_original_TG20.to_numpy(), True).to_parquet(
            dest / "daily.parquet", index=False
        )
        f.to_parquet(dest / "population.parquet", index=False)
        peer_checks.append(
            peer_information_control(
                model, study, view, f, training[version], recipe, dest, rehearsal=rehearsal
            )
        )
        if role in ("refit", "development"):
            from .state_screen_models import panel_state

            state_values = []
            for begin in range(0, len(view.source.rows), 32):
                pos = tuple(range(begin, min(begin + 32, len(view.source.rows))))
                state_values.extend(
                    panel_state(torch.from_numpy(view.origin_batch(pos)["x"])).numpy()[:, -1, 1]
                )
            f["panel_state2"] = np.repeat(state_values, 20)
            clocks = view.source.rows.set_index("origin_id").entry_end_utc
            f["entry_end_utc"] = f.origin_id.map(clocks)
            case_populations[role] = f.copy()
        measure(model, view, dest, population=f, study=study, rehearsal=rehearsal)
        checks.append(
            dict(
                role=role,
                rows=len(f),
                sessions=len(view.sessions),
                objective=float(f.total.sum()),
                reload_exact=True,
                targets_reconstructed=True,
                transform_collapsed_ties=transform_ties,
            )
        )
        evidence.extend(ref(p) for p in sorted(dest.iterdir()) if p.is_file())
        del view, model, f, reload
    case_view = get_view(study, "refit", rehearsal)
    case_model = model_for(arm)
    case_model.load_state_dict(torch.load(checked(r["refit"]), weights_only=True)["state_dict"])
    case_summary = collect_cases(
        study,
        case_populations,
        lambda role: get_view(study, role, rehearsal),
        case_model,
        plan["recipes"][arm]["refit"],
        destination / "refit",
    )
    evidence.extend(ref(p) for p in sorted((destination / "refit").rglob("*")) if p.is_file())
    del case_view, case_model, case_populations
    if case_summary is None or case_summary["cases"] != 22 or case_summary["candles"] != 1144:
        raise ValueError("P028_22_EXACT_CASES_REQUIRED")
    pd.concat(tables).to_parquet(destination / "cohorts.parquet", index=False)
    evidence.append(ref(destination / "cohorts.parquet"))
    # The real controller binds a completed read-only component probe, not a text claim.
    from .visualization.state_screen_ui import verify_payload

    ui_receipt = verify_payload(destination, r, plan=plan, rehearsal=rehearsal)
    evidence.extend(ref(p) for p in sorted(ui_receipt.parent.iterdir()) if p.is_file())
    from .state_screen_release import arm_documents

    evidence.extend(ref(p) for p in arm_documents(r, destination, pd.concat(tables)))
    for reference in (
        plan["baseline_refs"]
        + plan["protected_refs"]
        + plan["preservation_refs"]
        + list(plan["source_hashes"].values())
    ):
        checked(reference)
    storage = storage_bytes([Path(".")])
    if (
        storage > 10_000_000_000
        or storage - plan["storage_before"] > 1_000_000_000
        or peak_rss_bytes() > 2_000_000_000
    ):
        raise ValueError("P028_RESOURCES")
    inventory = []
    for root in (result_path.parent, destination):
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.name != ".gitignore":
                inventory.append(
                    dict(
                        **ref(path),
                        purpose="immutable run/scientific evidence",
                        git_intent="PRIVATE_LOCAL_IGNORED",
                    )
                )
    inventory_path = destination / "artifact_inventory.csv"
    pd.DataFrame(inventory).to_csv(inventory_path, index=False)
    evidence.append(ref(inventory_path))
    tests = json.loads(checked(plan["validation"]).read_text())
    if tests["status"] != ("PASS_P028_REHEARSAL_INPUTS" if rehearsal else "PASS_P028_VALIDATION"):
        raise ValueError("P028_TESTS_REQUIRED")
    gate = dict(
        status="PASS_P028_" + arm,
        scope=r["scope"],
        all_roles=4,
        proposal_sha256=r["proposal_sha256"],
        execution_sha256=r["execution_sha256"],
        scientific_sha256=plan["scientific_definitions"]["sha256"],
        objective_reconciled=True,
        reload_reconciled=True,
        mechanisms_verified=True,
        resources_verified=True,
        source_verified=True,
        uncertainty_verified=True,
        tests_verified=True,
        peer_control_verified=len(peer_checks) == 4
        and all(
            c["status"]
            in ("PASS_P028_MATCHED_PEER_INFORMATION_CONTROL", "EMPTY_P028_CAUSAL_DONOR_SUBSET")
            for c in peer_checks
        ),
        case_peer_evidence_verified=len(
            pd.read_parquet(destination / "refit/case_peer_hidden.parquet")
        )
        == 22 * 20 * 32,
        ui_verified=True,
        order_and_clock_verified=True,
        roles=checks,
        cases=case_summary,
        storage=storage,
        peak_rss_bytes=peak_rss_bytes(),
        evidence=evidence,
        evidence_fingerprint=fingerprint(evidence),
        result_sha256=digest(result_path),
    )
    from .state_screen_authority import required_artifacts

    gate["diagnostics_root"] = str(destination)
    gate["deliverables"] = {name: ref(destination / name) for name in required_artifacts(arm)}
    write_json(destination / "gate.json", gate)
    return gate
