"""Prepare and supervise the exact Package011 sequential queue; no implicit fit approval."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from .config import digest, fingerprint, write_json
from .controlled_authority import (
    JOURNAL,
    QUEUE,
    approval_scope,
    authority,
    code_binding,
    contract,
    journal_rows,
    load_plan,
    load_stock_inputs,
    run_id,
)
from .controlled_loss import fit_policy
from .pretraining_policy import verify_ref
from .real_batch_authority import atomic_replace_json
from .real_bridge_authority import HARD_SECONDS, load_review


def reference(path: Path) -> dict:
    return {"path": str(path), "sha256": digest(path)}


def prepare(out: Path) -> dict:
    root = Path.cwd()
    pre = json.loads((out / "preflight_and_original_reference.json").read_text())
    prior = json.loads(verify_ref(root, pre["prior_plan"]).read_text())
    review = load_review(root, prior["producer"])
    preparations = {
        fold: {
            key: ref
            for key, ref in review.manifest["preparations"].items()
            if key in {fold + "_INNER_TRAIN", fold + "_REFIT"}
        }
        for fold in ("WF1", "WF2")
    }
    preparations["WF2"] = prior["stock_preparations"]
    started = time.monotonic()
    views = {}
    params = {}
    panels = {}
    for fold in ("WF1", "WF2"):
        inputs = load_stock_inputs(review, {"stock_preparations": preparations}, fold)
        stock = {key: inputs.stock_view(key) for key in ("inner", "validation", "refit", fold)}
        outer = stock[fold]
        if len(outer.sessions) != 116 or len(outer.rows) != 232:
            raise ValueError("TA011_EXPECTED_OUTER_PANEL_MISMATCH")
        views[fold] = {k: v.summary() for k, v in stock.items()}
        panels[fold] = [(r.session, r.origin, r.targets) for r in outer.rows]
        params[fold] = {
            arm: {stage: fit_policy(stock[stage], arm) for stage in ("inner", "refit")}
            for arm in ("C0", "H1", "T1", "T2", "O1")
        }
        if len(stock["validation"].sessions) < 50 or any(
            sum(r.origin == o for r in stock["validation"].rows) < 25 for o in (1, 2)
        ):
            raise ValueError("TA011_INADEQUATE_FROZEN_TAIL")
    write_json(out / "target_parameter_bindings.json", params)
    write_json(
        out / "input_binding.json",
        dict(
            views=views,
            canonical_outer_panels=panels,
            stock_preparations=preparations,
            source=review.producer["manifest"],
            confirmation_numeric_rows=0,
            seconds=time.monotonic() - started,
        ),
    )
    definition = Path("configs/track_a_candidate_experiment_registry_v4.json")
    write_json(
        definition,
        dict(
            schema=4,
            ceiling=40,
            opening_started=6,
            new_pair_limit=18,
            real_journal=JOURNAL,
            previous_pointer=reference(out / "registry_pointer_v3_snapshot.json"),
            counts_failed_starts=True,
            production_migration=False,
        ),
    )
    refs = [reference(Path(f"reports/audit/track_a_real_pairs_v{i}.jsonl")) for i in (1, 2, 3)]
    refs += [
        reference(Path("configs/CURRENT_PROTOCOL.json")),
        reference(definition),
        reference(out / "input_binding.json"),
        reference(out / "target_parameter_bindings.json"),
    ]
    refs += [ref for d in preparations.values() for ref in d.values()]
    refs += [
        reference(
            Path(
                "reports/data_audit/ta006_tm0_postrun_baseline_review_2026-10-15_002321/permitted_prediction_snapshot.csv"
            )
        ),
        reference(
            Path(
                "reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/wf2_matched_predictions.csv"
            )
        ),
    ]
    dashboard = json.loads(Path("configs/track_a_visualization_v1.json").read_text())
    for fold in ("WF1", "WF2"):
        for key in ("models", "checkpoints"):
            ref = dashboard[key][fold]["TM0"]
            verify_ref(root, ref)
            refs.append(ref)
    from .visualization.metrics import summary

    controls = {}
    for fold, path in (
        (
            "WF1",
            "reports/data_audit/ta006_tm0_postrun_baseline_review_2026-10-15_002321/permitted_prediction_snapshot.csv",
        ),
        (
            "WF2",
            "reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/wf2_matched_predictions.csv",
        ),
    ):
        frame = pd.read_csv(path, float_precision="round_trip")
        if fold == "WF1":
            frame = frame.loc[frame.partition == "WF1"].copy()
        frame["score"] = frame.TM0
        frame["squared_error"] = (frame.score - frame.TG0) ** 2
        stats = summary(frame)
        controls[fold] = {k: v for k, v in stats.items() if k not in {"daily", "by_origin"}}
        if len(frame) != 1160:
            raise ValueError("TA011_ORIGINAL_CONTROL_POPULATION_CHANGED")
        zero = frame.copy()
        zero["score"] = 0.0
        zero["squared_error"] = zero.TG0**2
        controls[fold]["ZERO_MSE"] = summary(zero)["MSE"]
        truth = [(r[0], r[1], list(r[2])) for r in panels[fold]]
        actual = [
            (
                day,
                int(g.origin.iloc[0]),
                g.set_index("symbol")
                .loc[list(contract("H1", fold, 42)["universe"])]
                .TG0.to_numpy(),
            )
            for (day, origin), g in frame.groupby(["session", "origin"], sort=True)
        ]
        import numpy as np

        if len(actual) != len(truth) or any(
            a[:2] != b[:2]
            or not np.array_equal(
                np.asarray(a[2], dtype=np.float32), np.asarray(b[2], dtype=np.float32)
            )
            for a, b in zip(actual, truth)
        ):
            raise ValueError("TA011_ORIGINAL_CONTROL_TARGET_OR_MASK_CHANGED")
    pre["original_reference_metrics"] = controls
    pre["original_control_refs"] = refs[-4:]
    atomic_replace_json(out / "preflight_and_original_reference.json", pre)
    plan = dict(
        id="TA011_CONTROLLED_18_v1",
        code_sha256=code_binding(root),
        producer=prior["producer"],
        stock_preparations=preparations,
        protected_refs=refs,
        prior_pointer_snapshot=reference(out / "registry_pointer_v3_snapshot.json"),
        registry_definition=reference(definition),
        opening_started=6,
        ceiling=40,
        maximum_new_starts=18,
        maximum_wall_seconds=7200,
        report_reserve_seconds=900,
        deadline=pre["deadline"],
        package_started_at=pre["started_at"],
        confirmation_access=False,
        production_migration=False,
        assumptions=pre["assumptions"],
        formula_decision=(
            "Live researcher confirmed pooled unweighted T1 and T2 floor 1e-6; "
            "numpy linear empirical quantile convention"
        ),
        runs=[],
    )
    for arm, fold, seed in QUEUE:
        value = dict(
            run_id=run_id(arm, fold, seed),
            arm=arm,
            fold=fold,
            seed=seed,
            architecture="TM0",
            contract=contract(arm, fold, seed),
            views=views[fold],
            target_parameters=params[fold][arm],
        )
        value["input_id"] = fingerprint([views[fold], params[fold][arm], preparations[fold]])
        plan["runs"].append(value)
    write_json(out / "predeclared_experiment_matrix.json", plan)
    text = (
        "# Package011 — exact batch proposal\n\nAWAITING_APPROVAL. Proposal SHA "
        f"`{digest(out / 'predeclared_experiment_matrix.json')}`; "
        f"execution SHA `{plan['code_sha256']}`.\n\n"
        "18 sequential calibration/fresh-refit pairs; original-scale MSE D6g selection, "
        "fixed constants, no rescues. Candidate AAPL/COST/CMCSA/SBUX/CME; qualified private "
        "rights/clock attestation, retrospective actions/universe, idealized clock and "
        "hourly-close proxy. No factual certification, confirmation, trading or migration.\n\n"
    )
    text += "\n".join(
        f"{i + 1}. {r['run_id']} — input `{r['input_id']}`" for i, r in enumerate(plan["runs"])
    )
    text += (
        "\n\nBudget 6→24/40 (failed starts count). Registry v4 activates at first STARTED. "
        f"Deadline {plan['deadline']}; 15-minute reporting reserve. "
        "Largest safe sequential prefix only. One live APPROVE / REJECT / MODIFY "
        "required before any optimizer step.\n"
    )
    (out / "PROPOSAL_FOR_LIVE_APPROVAL.md").write_text(text)
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--pair")
    args = parser.parse_args()
    if args.prepare:
        prepare(args.output)
        print("TA011_AWAITING_APPROVAL; 0 new pairs")
        return 0
    plan_path = args.plan or args.output / "predeclared_experiment_matrix.json"
    plan, _ = load_plan(Path.cwd(), reference(plan_path))
    if args.dry_run:
        print(
            json.dumps(
                dict(
                    status="NO_FITTING",
                    global_started=6
                    + sum(r["status"] == "STARTED" for r in journal_rows(Path(JOURNAL))),
                )
            )
        )
        return 0
    if args.approval is None:
        raise ValueError("TA011_NO_HUMAN_APPROVAL_NO_FITTING")
    approval_scope(reference(plan_path), json.loads(args.approval.read_text()), plan)
    if args.pair:
        from .real_bridge_run import run_worker

        permit = authority(Path.cwd(), reference(plan_path), reference(args.approval), args.pair)
        run_worker(permit, (args.output / args.pair).resolve())
        return 0
    runtime = []
    for r in plan["runs"]:
        rows = journal_rows(Path(JOURNAL))
        if any(e["run_id"] == r["run_id"] for e in rows):
            raise ValueError("TA011_ALREADY_STARTED_ID_CANNOT_RELAUNCH")
        remaining = (
            pd.Timestamp(plan["deadline"]) - pd.Timestamp.now(tz="UTC")
        ).total_seconds() - 900
        projection = max([180.0] + [v["seconds"] * 2 for v in runtime])
        if remaining < projection:
            write_json(
                args.output / "prefix_stop.json",
                dict(
                    reason="INSUFFICIENT_WHOLE_PAIR_TIME",
                    next=r["run_id"],
                    remaining_seconds=remaining,
                    projected_seconds_NOT_ACTUAL=projection,
                ),
            )
            break
        started = time.monotonic()
        command = [
            sys.executable,
            "-B",
            "-m",
            "lstm_data.controlled_batch",
            "--output",
            str(args.output),
            "--approval",
            str(args.approval),
            "--plan",
            str(plan_path),
            "--pair",
            r["run_id"],
        ]
        try:
            result = subprocess.run(
                command, timeout=min(HARD_SECONDS, remaining), check=False
            ).returncode
        except subprocess.TimeoutExpired:
            result = 124
        elapsed = time.monotonic() - started
        runtime.append(dict(run_id=r["run_id"], seconds=elapsed, return_code=result))
        atomic_replace_json(args.output / "queue_actual_runtime.json", dict(pairs=runtime))
        print(json.dumps(runtime[-1]), flush=True)
        if result:
            rows = journal_rows(Path(JOURNAL))
            own = [e for e in rows if e["run_id"] == r["run_id"]]
            if own and own[-1]["status"] not in {"COMPLETED", "FAILED"}:
                permit = authority(
                    Path.cwd(), reference(plan_path), reference(args.approval), r["run_id"]
                )
                permit.append("FAILED", dict(reason="SUPERVISED_WORKER_EXIT", return_code=result))
            write_json(
                args.output / "prefix_stop.json",
                dict(reason="PAIR_FAILURE_NO_RETRY", run_id=r["run_id"], code=result),
            )
            break
    return 0


if __name__ == "__main__":
    from lstm_data.controlled_batch import main as canonical_main

    raise SystemExit(canonical_main())
