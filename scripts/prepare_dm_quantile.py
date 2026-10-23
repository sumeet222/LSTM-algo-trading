"""P023 stages0/1, zero optimizer updates and no journal/registry activation."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from lstm_data.config import digest, fingerprint, now, write_json
from lstm_data.dm_quantile_authority import code_binding
from lstm_data.dm_quantile_loss import (
    ARMS,
    RUNS,
    draw_batch,
    draws,
    fitting_recipe,
    model_for,
    terms,
)
from lstm_data.dm_quantile_run import epoch_pass, predict, save
from lstm_data.hf1m_ft16_loader import load_model_input
from lstm_data.hf1m_ft16_source import checked, ref
from lstm_data.hf1m_training_data import CONTRACT, TrainingView
from lstm_data.neural_lifecycle import state_hash
from lstm_data.objective_screen_recovery import rows
from lstm_data.objective_screen_run import record_epoch
from lstm_data.objective_screen_source import identity, ordered_targets
from lstm_data.p2_closure import load_deferred_work
from lstm_data.visualization.hf1m_long import LongStudy


def prepare(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    study = LongStudy.discover(Path.cwd())
    i = identity(study)
    i["ledger"] = 41
    print(json.dumps(i), flush=True)
    write_json(out / "active_dataset_identity.json", i)
    assert digest(CONTRACT) == "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
    assert rows()[-1]["global_started_pairs"] == 41 and rows()[-1]["status"] == "COMPLETED"
    load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    scientific = dict(
        arms=list(ARMS),
        runs=list(RUNS),
        source_identity=i,
        seed=42,
        DM1=(
            "BCEWithLogits(a,1[z>=0])+(softplus(b_observed)-abs(z))^2; "
            "zhat=p*mu+-(1-p)*mu-; select original TG20 MSE"
        ),
        QR1=(
            "q50=b50,q05=q50-softplus(d-),q95=q50+softplus(d+); mean "
            "pinball(.05,.5,.95); select pinball"
        ),
        SS1=(
            "base T2 zMSE; top1% train-row tail sessions; balanced50/50 within "
            "each batch with replacement; p_g/.5 correction, no self "
            "normalization"
        ),
        remainder=(
            "paired balanced group draws plus independent Bernoulli(.5) group for odd remainder"
        ),
        constants=(
            "equal-session/origin/stock weights; QR baseline weighted inverse empirical CDF left"
        ),
        protocol=(
            "AdamW lr.001 betas(.9,.999) eps1e-8 matrixwd.01 bias0; clip1; "
            "batch16 sessions; CPU4; D6g min12 max60 patience10 >=.1% qualified "
            "improvement; fresh same-seed refit"
        ),
        diagnostics=(
            "Immediate per-arm all4 roles; exact objective component attribution "
            "and ranked/range/numerator/MAD cohorts, genuine48+4 cases; task-"
            "specific constants; paired400replicate seed22042 month/2month CIs; "
            "no P&L; QR median-MSE descriptive only"
        ),
        resources=dict(
            threads=4,
            planning_hours="0.5–6",
            peak_ram_bytes=2_000_000_000,
            additional_storage_bytes=1_000_000_000,
            total_storage_ceiling_bytes=10_000_000_000,
        ),
        protected_numeric_access=False,
        fit_permission=False,
    )
    write_json(out / "scientific_design.json", scientific)
    (out / "P023_EXPERIMENT_DESIGN_FROZEN.md").write_text(
        "# P023 frozen scientific design\n\n"
        + json.dumps(scientific, indent=2)
        + "\n\nThe submitted Package023 instruction is authoritative for the "
        "full diagnostic and dashboard requirements. QR1 median is not a "
        "conditional mean. DM1 inverse of signed-z estimate is not generally "
        "E[y|X]. SS1 odd remainder group is Bernoulli(.5); importance weights"
        " are never self-normalized. Existing T2/E1/P022 results and "
        "protected2026 remain fixed. Immediate scientific diagnostics must "
        "PASS before the next start.\n"
    )
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name / "zero_step"
    private.mkdir(parents=True)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    recipes = {}
    views = {}
    checks = []
    protected = [ref(CONTRACT), study.plan["input_contract"]]
    for r in study.plan["protected_refs"]:
        checked(r)
        protected.append(r)
    with patch.object(torch.optim.AdamW, "step", side_effect=AssertionError("NO_OPTIMIZER_STEP")):
        for role in ["inner_train", "inner_validation", "refit", "development"]:
            version = "inner" if role.startswith("inner") else "refit"
            source = load_model_input(CONTRACT, split=role, fit_version=version)
            view = TrainingView(source, role)
            views[role] = view.summary()
            target = ordered_targets(view)
            if role in ["inner_train", "refit"]:
                recipes[version] = fitting_recipe(target, source.fit["t2_scale"], view.sessions)
                recipe = recipes[version]
                top5 = (
                    target.assign(abs_y=target.TG20.abs())
                    .sort_values(["abs_y", "origin_id", "ticker"], ascending=[False, True, True])
                    .head(len(target) // 20)
                )
                recipe["top5_tail_sessions_overlap"] = len(
                    set(top5.session_date_et) & set(recipe["tail_sessions"])
                )
                pd.DataFrame(
                    dict(
                        session=view.sessions,
                        tail=[d in set(recipe["tail_sessions"]) for d in view.sessions],
                    )
                ).to_csv(out / f"{version}_sampler_groups.csv", index=False)
            small = source.rows.loc[
                source.rows.session_date_et.isin(view.sessions[:2])
            ].reset_index(drop=True)
            tiny = TrainingView(
                replace(
                    source,
                    rows=small,
                    targets=source.targets.loc[source.targets.origin_id.isin(small.origin_id)],
                ),
                role,
            )
            for arm in ARMS:
                model = model_for(arm)
                before = state_hash(model)
                batch = draw_batch(tiny, (0, 0))
                torch.testing.assert_close(batch.inputs[0], batch.inputs[1])
                assert batch.ids[0] != batch.ids[1]
                raw = (
                    model(batch.inputs[batch.origins].reshape(-1, 48, 16)).reshape(-1, 20, 3)
                    if arm != "SS1"
                    else model(batch.inputs[batch.origins].reshape(-1, 48, 16)).reshape(-1, 20)
                )
                padded = torch.zeros(
                    (*batch.targets.shape, 3) if arm != "SS1" else batch.targets.shape
                )
                padded[batch.origins] = raw
                loss = terms(padded, batch.targets, batch.origins, arm, source.fit["t2_scale"])
                loss["session_loss"].mean().backward()
                assert all(
                    p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters()
                )
                assert state_hash(model) == before
                dest = private / (arm + "_" + role)
                dest.mkdir()
                checkpoint = save(
                    dest / "untrained.pt", model, dict(zero_step=True, arm=arm, role=role), arm
                )
                frame = predict(model, tiny, arm, checkpoint)
                assert len(frame) == len(small) * 20
                frame.to_parquet(dest / "untrained.parquet", index=False)
                progress = []
                for phase in ["calibration", "refit"]:
                    for epoch in [1, 2]:
                        summary = epoch_pass(model, tiny, arm, recipes[version], epoch)
                        assert summary["optimizer_steps"] == 0
                        progress.append(dict(phase=phase, training=summary))
                        record_epoch(dest, progress)
                checks.append(
                    dict(
                        arm=arm,
                        role=role,
                        rows=len(frame),
                        parameters=sum(p.numel() for p in model.parameters()),
                        gradient_finite=True,
                        duplicate_draw_inputs_equal=True,
                        progress_receipts=4,
                        checkpoint=checkpoint,
                    )
                )
            for run in ["HF1M-LONG-TM0-T2-S42-DEV1", "HF1M-LONG-TM0-T2-S123-DEV1"]:
                result = study.run_result(run)
                for r in result["artifacts"].values():
                    checked(r)
                baseline = study.prediction(run, role).set_index(["origin_id", "ticker"])
                keys = pd.MultiIndex.from_frame(target[["origin_id", "ticker"]])
                np.testing.assert_array_equal(baseline.reindex(keys).TG20, target.TG20)
                protected.append(ref(study.packet / run / "run_result.json")) if (
                    study.packet / run / "run_result.json"
                ).exists() else None
    for version, recipe in recipes.items():
        batches = draws(recipe, 1)
        assert sum(len(ids) for ids, _ in batches) == recipe["session_count"]
    write_json(out / "fitted_prefix_recipes.json", recipes)
    write_json(
        out / "zero_step_receipt.json",
        dict(status="PASS_ZERO_STEP", checks=checks, optimizer_updates=0, new_starts=0),
    )
    write_json(
        out / "stage_0_gate.json",
        dict(
            status="PASS_PREFLIGHT",
            ledger=41,
            identity=ref(out / "active_dataset_identity.json"),
            views=views,
            baseline_exact_populations=True,
        ),
    )
    (out / "stage_0_review.md").write_text(
        "# Stage0 PASS\n\nFrozen source/input and all4roles verified through "
        "the actual P020 loader. Saved T2/42 and T2/123 predictions match "
        "exact canonical target populations. P2 holds preserved, ledger41 "
        "unchanged.\n"
    )
    snapshot = out / "registry_pointer_v11_snapshot.json"
    snapshot.write_bytes(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_bytes())
    proposal = dict(
        created=now(),
        runs=list(RUNS),
        opening_started=41,
        maximum_new_starts=3,
        ceiling=200,
        design=ref(out / "scientific_design.json"),
        audit_gate=ref(out / "stage_0_gate.json"),
        input_contract=ref(CONTRACT),
        code=code_binding(),
        execution_sha256=fingerprint(code_binding()),
        recipes=recipes,
        views=views,
        protected_refs=protected,
        previous_pointer=ref(snapshot),
        previous_journal=ref(Path("reports/audit/track_a_real_pairs_v11_p022_repair.jsonl")),
        registry_definition="configs/track_a_candidate_experiment_registry_v12_p023.json",
        private_root=str(private.parent / "trained_runs"),
        protected_numeric_access=False,
        fit_permission=False,
        requires_separate_live_approval=True,
        resources=scientific["resources"],
    )
    write_json(out / "experiment_design.json", proposal)
    write_json(
        out / "proposed_registry_v12.json",
        dict(
            active=False,
            runs=list(RUNS),
            proposal=ref(out / "experiment_design.json"),
            opening=41,
            maximum_final=44,
        ),
    )
    print(
        json.dumps(
            dict(
                proposal_sha256=digest(out / "experiment_design.json"),
                execution_sha256=proposal["execution_sha256"],
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    prepare(p.parse_args().out)
