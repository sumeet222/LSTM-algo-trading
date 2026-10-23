"""P025 metadata-first source/baseline preflight; never fits or reads protected outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from .branch_replication_spec import CONTRACT, P022, P023, P024, ROLES, RUNS, SCIENCE
from .config import fingerprint, now, write_json
from .dm_quantile_loss import fitting_recipe
from .hf1m_ft16_source import checked, ref
from .objective_screen_attribution import allocations
from .objective_screen_diagnostics import canonical
from .objective_screen_loss import fit_recipe, model_for
from .objective_screen_metrics import classification, equal_weights
from .objective_screen_source import identity, ordered_targets, scoped_view
from .optimization_screen_audit import verify_refs
from .optimization_screen_recovery_authority import JOURNAL, POINTER, rows
from .p2_closure import load_deferred_work
from .visualization.hf1m_long import LongStudy
from .visualization.objective_screen import Screen


def baseline_result(arm: str) -> Path:
    root = P022 if arm == "E1" else P023
    return root / f"HF1M-LONG-TM0-{arm}-S42-DEV1/run_result.json"


def audit(out: Path) -> None:
    """Seal definitions before baseline numerical checks and preserve all predecessor bytes."""
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n!submitted_instruction.txt\n")
    write_json(out / "scientific_definitions.json", SCIENCE)
    study = LongStudy.discover(Path.cwd())
    contract = study.plan["input_contract"]
    if contract["sha256"] != CONTRACT:
        raise ValueError("P025_INPUT_CONTRACT_MISMATCH")
    checked(contract)
    prior = rows()
    if prior[-1]["status"] != "COMPLETED" or prior[-1]["global_started_pairs"] != 51:
        raise ValueError("P025_LEDGER51_REQUIRED")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        raise ValueError("P025_CURRENT_JOURNAL_REQUIRED")
    for journal in Path("reports/audit").glob("track_a_real_pairs_v*.jsonl"):
        if any(json.loads(line).get("run_id") in RUNS for line in journal.read_text().splitlines()):
            raise ValueError("P025_RUN_ID_COLLISION")
    p2 = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    p024_plan = json.loads((P024 / "experiment_design.json").read_text())
    stage0 = json.loads(checked(p024_plan["stage0"]).read_text())
    metadata = identity(study)
    metadata.update(
        ledger=51,
        baseline_results=[ref(baseline_result(a)) for a in ("E1", "QR1")],
        source_stage0=p024_plan["stage0"],
        p024_closeout=ref(P024 / "final_closeout_receipt.json"),
        pointer=ref(POINTER),
        journal=ref(JOURNAL),
    )
    print(json.dumps(metadata, indent=2), flush=True)
    write_json(out / "source_identity.json", metadata)
    (out / "registry_pointer_v14_snapshot.json").write_bytes(POINTER.read_bytes())
    for reference in list(stage0["source_hashes"].values()) + p024_plan["protected_refs"]:
        checked(reference)
    if (
        json.loads((P024 / "final_closeout_receipt.json").read_text())["status"]
        != "PASS_P024_COMPLETE"
    ):
        raise ValueError("P025_P024_FINAL_RELEASE_REQUIRED")
    e1_plan = json.loads((P022 / "experiment_design.json").read_text())
    qr_plan = json.loads((P023 / "experiment_design.json").read_text())
    recipes = dict(E1=e1_plan["recipes"], QR1=qr_plan["recipes"])
    views = {r: scoped_view(study, r, stage=7) for r in ROLES}
    refs: dict[str, dict] = {}
    baseline_checks = []
    screen = Screen.discover(Path.cwd())
    qr_config = json.loads(Path("configs/track_a_p023_visualization_v1.json").read_text())
    qr_manifest = json.loads(checked(qr_config["manifest"]).read_text())
    if qr_manifest["ledger"] != 44:
        raise ValueError("P025_QR1_BASELINE_RELEASE_REQUIRED")
    quantile = Screen(Path.cwd(), qr_manifest["files"], qr_config["manifest"]["sha256"], qr_config)
    for arm in ("E1", "QR1"):
        result_path = baseline_result(arm)
        result = json.loads(result_path.read_text())
        verify_refs(result, refs)
        expected_status = (
            "COMPLETED" if arm == "E1" else "COMPLETED_FIT_PENDING_IMMEDIATE_DIAGNOSTICS"
        )
        if result["status"] != expected_status:
            raise ValueError("P025_BASELINE_MODEL_IDENTITY")
        if arm == "QR1":
            gate_path = P023 / "stage_3_gate.json"
            gate = json.loads(gate_path.read_text())
            if gate["status"] != "PASS_QR1" or checked(gate["run"]) != result_path:
                raise ValueError("P025_QR1_IMMEDIATE_COMPLETION_GATE_REQUIRED")
            refs[str(gate_path)] = ref(gate_path)
        for key in ("calibration", "refit"):
            body = torch.load(checked(result[key]), weights_only=True)
            model = model_for("E1")  # Both frozen three-head architectures share these dimensions.
            model.load_state_dict(body["state_dict"])
            if sum(p.numel() for p in model.parameters()) != 6499:
                raise ValueError("P025_ACTUAL_BASELINE_PARAMETER_COUNT")
        for role in ROLES:
            view = views[role]
            target = ordered_targets(view)
            recipe = recipes[arm][view.source.fit_version]
            if recipe["scale"] != view.source.fit["t2_scale"]:
                raise ValueError("P025_BASELINE_RECIPE_SCALE")
            f = canonical(
                screen.population("E1", role)
                if arm == "E1"
                else quantile.table(f"QR1/{role}/population.parquet"),
                target,
            )
            if role in ("inner_train", "refit"):
                recomputed = (
                    fit_recipe(
                        target.TG20.to_numpy(),
                        equal_weights(target.session_date_et.to_numpy()),
                        recipe["scale"],
                    )
                    if arm == "E1"
                    else fitting_recipe(target, recipe["scale"], view.sessions)
                )
                if any(
                    k not in recipe or fingerprint(value) != fingerprint(recipe[k])
                    for k, value in recomputed.items()
                ):
                    raise ValueError("P025_PREFIX_RECIPE_REPRODUCTION")
            if arm == "E1":
                p = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy()
                metrics = classification(f.TG20.to_numpy(), p, f.session_date_et.to_numpy(), recipe)
                allocations(f, "E1", recipe)
                value = metrics["ANY_AP"]
            else:
                from .dm_quantile_diagnostics import metrics as qr_metrics

                metrics = qr_metrics(f, "QR1", recipe)
                value = metrics["pinball"]
            baseline_checks.append(
                dict(
                    arm=arm,
                    role=role,
                    rows=len(f),
                    sessions=len(view.sessions),
                    main_metric=value,
                    checkpoint=result["calibration" if role.startswith("inner") else "refit"],
                )
            )
            for name, reference in (screen.files if arm == "E1" else quantile.files).items():
                if name.startswith(("E1/" if arm == "E1" else "QR1/")):
                    checked(reference)
                    refs[reference["path"]] = reference
    np.testing.assert_allclose(
        next(
            c["main_metric"]
            for c in baseline_checks
            if c["arm"] == "E1" and c["role"] == "development"
        ),
        0.131678,
        atol=1e-6,
        rtol=0,
    )
    np.testing.assert_allclose(
        next(
            c["main_metric"]
            for c in baseline_checks
            if c["arm"] == "QR1" and c["role"] == "development"
        ),
        0.226082,
        atol=1e-6,
        rtol=0,
    )
    write_json(
        out / "stage_0_receipt.json",
        dict(
            status="PASS_P025_IDENTITY_BASELINES",
            at=now(),
            ledger=51,
            new_starts=0,
            optimizer_updates=0,
            protected_numeric_access=False,
            input_contract=contract,
            source_identity=ref(out / "source_identity.json"),
            scientific_definitions=ref(out / "scientific_definitions.json"),
            previous_pointer=ref(out / "registry_pointer_v14_snapshot.json"),
            previous_journal=ref(JOURNAL),
            views={r: v.summary() for r, v in views.items()},
            recipes=recipes,
            baseline_checks=baseline_checks,
            baseline_refs=list(refs.values()),
            source_hashes=stage0["source_hashes"],
            protected_refs=p024_plan["protected_refs"],
            p2_entries=len(p2),
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    audit(parser.parse_args().out)
