"""P022 zero-step executable preflight and exact four-start proposal; grants no permission."""

from __future__ import annotations

import argparse
import json
import resource
import time
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from lstm_data.config import digest, fingerprint, now, write_json
from lstm_data.hf1m_ft16_source import checked, ref
from lstm_data.hf1m_training_data import TrainingView
from lstm_data.magnitude_range_audit import session_weights
from lstm_data.neural_engine import optimizer
from lstm_data.neural_lifecycle import state_hash
from lstm_data.objective_screen_authority import code_binding, ensure
from lstm_data.objective_screen_loss import ARMS, RUNS, Objective, classes, fit_recipe, model_for
from lstm_data.objective_screen_run import epoch_pass, predict, save_checkpoint
from lstm_data.objective_screen_source import assert_frozen_design, ordered_targets, scoped_view
from lstm_data.visualization.hf1m_long import LongStudy


def seal(out: Path, version: int = 1) -> None:
    if version not in (1, 2):
        raise ValueError("P022_DECLARED_PROPOSAL_VERSION")
    suffix = "" if version == 1 else "_v2"
    started = time.monotonic()
    design = assert_frozen_design(out)
    audit = json.loads((out / "stage1_verification/closure.json").read_text())
    if audit["status"] != "PASS_AUDIT_VERIFIED":
        raise ValueError("P022_AUDIT_FIRST")
    checked(audit["predecessor_gate"])
    for r in audit["files"]:
        checked(r)
    if (out / f"experiment_design{suffix}.json").exists():
        raise ValueError("P022_IMMUTABLE_PROPOSAL")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    study = LongStudy.discover(Path.cwd())
    views = {
        name: scoped_view(study, name, stage=2)
        for name in ["inner_train", "inner_validation", "refit"]
    }
    recipes = {}
    for fit_version, role in [("inner", "inner_train"), ("refit", "refit")]:
        t = ordered_targets(views[role])
        y = t.TG20.to_numpy()
        w = session_weights(t)
        recipes[fit_version] = fit_recipe(y, w, views[role].source.fit["t2_scale"])
        # Training tensors use the unchanged P021 float32 labels; no threshold class drift.
        r = recipes[fit_version]
        np.testing.assert_array_equal(
            classes(y, r["q95_abs_y"]), classes(y.astype(np.float32), r["q95_abs_y"])
        )
        np.testing.assert_array_equal(
            abs(np.arcsinh(y / r["scale"])) > r["q95_abs_z"],
            abs(np.arcsinh(y.astype(np.float32) / r["scale"])) > r["q95_abs_z"],
        )
    original = json.loads((out / "stage1/inner_event_recipe.json").read_text())
    if recipes["inner"] != original:
        raise ValueError("P022_AUDIT_THRESHOLD_CHANGED")
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name
    dry = private / f"zero_step_preflight{suffix}"
    dry.mkdir(parents=True, exist_ok=False)
    checks = []
    with patch.object(torch.optim.AdamW, "step", side_effect=AssertionError("NO_OPTIMIZER_STEP")):
        for arm in ARMS:
            model = model_for(arm)
            initial = state_hash(model)
            opt = optimizer(model)
            assert not opt.state
            for role, view in views.items():
                # Whole first two sessions; bounded inference/export test, no weight update.
                selected = view.source.rows.loc[
                    view.source.rows.session_date_et.isin(view.sessions[:2])
                ].reset_index(drop=True)
                source = replace(
                    view.source,
                    rows=selected,
                    targets=view.source.targets.loc[
                        view.source.targets.origin_id.isin(selected.origin_id)
                    ],
                )
                tiny = TrainingView(source, role)
                policy = Objective(arm, recipes[source.fit_version])
                result = epoch_pass(model, tiny, 1, policy)
                assert result["optimizer_steps"] == 0 and state_hash(model) == initial
                if arm == "R1":
                    assert result["pairwise_ordering_accuracy"] is not None
                    assert result["scaled_pairwise_objective"] > 0
                checkpoint = save_checkpoint(
                    dry / (arm + "_" + role + ".pt"),
                    model,
                    {"arm": arm, "role": role, "zero_step": True},
                    arm,
                )
                frame = predict(
                    model,
                    tiny,
                    arm,
                    dict(checkpoint_sha256=checkpoint["sha256"], run_id="UNTRAINED_PREFLIGHT"),
                )
                path = dry / (arm + "_" + role + ".parquet")
                frame.to_parquet(path, index=False)
                assert len(frame) == len(selected) * 20
                if arm == "E1":
                    assert "pred_original_TG20" not in frame
                    np.testing.assert_allclose(
                        frame[["p_NEG", "p_NORMAL", "p_POS"]].sum(axis=1), 1, atol=1e-6
                    )
                else:
                    assert frame.inverse_count.eq(1).all()
                checks.append(
                    dict(
                        arm=arm,
                        role=role,
                        rows=len(frame),
                        optimizer_steps=0,
                        objective=result["optimized_objective"],
                        checkpoint=checkpoint,
                        export=ref(path),
                        state_unchanged=True,
                    )
                )
    # Snapshot the predecessor pointer so subsequent legitimate pointer advancement cannot
    # erase or invalidate its identity. Old journal/source artifacts remain immutable.
    snapshot = out / "registry_pointer_v9_snapshot.json"
    if snapshot.exists():
        assert (
            snapshot.read_bytes() == Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_bytes()
        )
    else:
        snapshot.write_bytes(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_bytes())
    protected = json.loads((out / "preserved_references.json").read_text())
    protected = [r for r in protected if r["path"] != "configs/CURRENT_EXPERIMENT_REGISTRY.json"]
    for r in protected:
        checked(r)
    types = json.loads((out / f"types_preapproval{suffix}.json").read_text())
    if types["summary"]["errorCount"] != 0:
        raise ValueError("P022_STATIC_ERRORS")
    code = code_binding()
    write_json(out / f"fitted_objective_recipes{suffix}.json", recipes)
    preflight = dict(
        status="PASS_ZERO_STEP_EXECUTABLE_PREFLIGHT",
        at=now(),
        checks=checks,
        runtime_seconds=time.monotonic() - started,
        new_starts=0,
        optimizer_steps=0,
        peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        execution_sha256=fingerprint(code),
        development_read=False,
    )
    write_json(out / f"zero_step_preflight{suffix}.json", preflight)
    proposal = dict(
        schema_version=10,
        created=now(),
        runs=list(RUNS),
        opening_started=36,
        maximum_new_starts=4,
        ceiling=200,
        protected_numeric_access=False,
        code=code,
        execution_sha256=fingerprint(code),
        design=ref(out / "frozen_design.json"),
        audit_gate=ref(out / "stage1_verification/closure.json"),
        input_contract=design["input_contract"],
        previous_pointer=ref(snapshot),
        previous_journal=design["prior_journal"],
        protected_refs=protected,
        views={k: v.summary() for k, v in views.items()},
        recipes=recipes,
        private_root=str(private),
        registry_definition="configs/track_a_candidate_experiment_registry_v10_p022.json",
        journal="reports/audit/track_a_real_pairs_v10_p022.jsonl",
        resources=design["resource_plan"],
        zero_step_preflight=ref(out / f"zero_step_preflight{suffix}.json"),
        tests=ref(out / f"focused_tests_preapproval{suffix}.txt"),
        types=ref(out / f"types_preapproval{suffix}.json"),
        fit_authority="REQUIRES_SEPARATE_EXACT_LIVE_RESPONSE; NOT_GRANTED",
        correction="R1 pair signs from canonical float64 targets; z-regression remains float32",
    )
    previous = out / "experiment_design.json"
    if version == 2:
        proposal["supersedes_unapproved_proposal"] = ref(previous)
    plan = out / f"experiment_design{suffix}.json"
    write_json(plan, proposal)
    try:
        ensure(plan, None, RUNS[0])
    except ValueError as exc:
        assert "LIVE_FOUR_RUN_APPROVAL" in str(exc)
    else:
        raise AssertionError("missing live approval accepted")
    (out / f"experiment_design{suffix}.md").write_text(
        "# P022 exact four-start approval proposal\n\n"
        "Ready for live review; no fit permission and no new start reserved.\n\n"
        "Order: H2/42 → W1/42 → E1/42 → R1/42. Exact run IDs:\n\n"
        + "\n".join("- " + name for name in RUNS)
        + "\n\n"
        f"Proposal SHA256 `{digest(plan)}`. Execution SHA256 `{fingerprint(code)}`.\n\n"
        "Global budget36→40/200; each failure consumes its start. No "
        "retries, extra seeds or combinations. "
        "Each run is D6g calibration followed by a fresh same-seed selected-epoch refit. "
        "Frozen P020 input contract/FT16/TG20, "
        "dates,20names,48steps,32hidden units and AdamW remain "
        "unchanged. "
        "H2:2×Huber(delta1) onz. W1:normalized doubled-tail zMSE. "
        "E1:three-class normalized weightedCE. "
        "R1:zMSE+0.5all-pair logistic,temperature1. Regression "
        "selects originalTG20validationMSE; E1selectsCE.\n\n"
        "[Scientific design](P022_FROZEN_EXPERIMENT_DESIGN.md), "
        "[feature/event audit](P022_FEATURE_PREDICTABILITY_TRIAGE.md), "
        "[audit verification](stage1_verification/closure.json), "
        f"[train-only recipes](fitted_objective_recipes{suffix}.json), "
        f"[zero-step exports/checkpoint preflight](zero_step_preflight{suffix}.json).\n\n"
        "CPU4; planning0.5–6hours,≤2GB peakRAM,≤1GB additional storage within10GB ceiling. "
        "Development numerics wait until all four fits complete; protected2026neveropens. "
        "Bounded private-research rights/source/publication "
        "assumptions persist; no independent certification, "
        "trading, download, Git publication or promotion. "
        "Stage7diagnostics and additive existing-dashboard "
        "integration follow only after four successful runs.\n\n"
        "Package022 Execution and Authorization Rules and Stage2 "
        "explicitly require one separate live response "
        "before the first start or optimizer step. The submitted "
        "task and earlier approvals do not satisfy it.\n"
    )
    write_json(
        out / f"stage_02_authority_gate{suffix}.json",
        dict(
            status="AWAITING_EXACT_LIVE_FOUR_RUN_APPROVAL",
            proposal=ref(plan),
            execution_sha256=fingerprint(code),
            ledger=36,
            new_starts=0,
            no_optimizer_steps=True,
            approval_not_inferred=True,
        ),
    )
    print(json.dumps({"proposal": ref(plan), "execution_sha256": fingerprint(code)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--version", type=int, choices=[1, 2], default=1)
    args = parser.parse_args()
    seal(args.out, args.version)
