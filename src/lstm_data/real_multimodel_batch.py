"""Prepare, inspect or dispatch the exact approval-gated MC0/MC1/E5 queue."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from .config import digest, write_json
from .ft0_transforms import identity
from .neural_engine import SharedLSTM, batch_prediction, seed_all
from .neural_models import EndpointGatedLSTM
from .peer_inputs import peer_summaries
from .real_batch_authority import (
    JOURNAL_V2,
    QUEUE,
    SHAPES,
    approval_scope,
    batch_code,
    journal_rows_v2,
    load_pair_authority,
    load_plan,
    pair_contract,
)
from .real_batch_data import load_batch_inputs
from .real_bridge_authority import load_review
from .real_bridge_run import peak_rss_bytes, run_worker

BRIDGE = Path("reports/data_audit/ta_real_input_bridge_005_2026-10-14_215455")
PILOT = Path("reports/data_audit/ta005_first_pair_2026-10-14_234019")
REVIEW = Path("reports/data_audit/ta006_tm0_postrun_baseline_review_2026-10-15_002321")


def ref(path: Path) -> dict:
    return {"path": str(path), "sha256": digest(path)}


def prepare(out: Path) -> dict:
    """All independent data/shape checks; zero training or registry activation."""
    started = time.monotonic()
    preflight = json.loads((out / "preflight.json").read_text())
    torch.set_num_threads(1)
    review = load_review(Path.cwd(), ref(BRIDGE / "verified_producer.json"))
    binding = json.loads((BRIDGE / "final_v2/dataset_input_binding.json").read_text())
    inputs = load_batch_inputs(review, binding)
    views = {key: inputs.view(key, 21) for key in ("inner", "validation", "refit", "WF1")}
    peers = {key: inputs.view(key, 23) for key in views}
    counts = {
        "inner": (1376, 688),
        "validation": (110, 55),
        "refit": (1502, 751),
        "WF1": (232, 116),
    }
    for key, view in views.items():
        if (
            (len(view.rows), len(view.sessions)) != counts[key]
            or view.stock.version != binding["views"][key]["view_id"]
            or peers[key].stock is not view.stock
        ):
            raise ValueError("EXACT_FROZEN_MATCHED_TM0_POPULATION_REQUIRED")
    examples = []
    train = views["inner"]
    for pos in (0, len(train.sessions) // 2, len(train.sessions) - 1):
        batch = train.batch((pos,))
        peer_batch = peers["inner"].batch((pos,))
        if not torch.equal(batch.inputs, peer_batch.inputs[..., :21]):
            raise ValueError("E5_MUST_KEEP_EXACT_MC0_PREFIX")
        row = train.rows[2 * pos]
        x = batch.inputs[0, 0]
        z = x[:, -1, 0].numpy()
        expected = np.asarray(
            [
                [
                    np.mean(np.delete(z.astype(float), i)),
                    np.std(np.delete(z.astype(float), i), ddof=0),
                ]
                for i in range(5)
            ],
            dtype=np.float32,
        )
        if not np.array_equal(peer_batch.inputs[0, 0, :, -1, 21:].numpy(), expected):
            raise ValueError("INDEPENDENT_FOUR_PEER_DIVISOR4_ORACLE_FAILED")
        changed = x[:, :, :16].numpy().copy()
        changed[1, -1, 0] += 1
        altered = peer_summaries(changed)
        before = peer_summaries(x[:, :, :16].numpy())
        if not np.isclose(altered[0, -1, 0] - before[0, -1, 0], 0.25, atol=2e-6):
            raise ValueError("OTHER_PEER_PERTURBATION_REQUIRED")
        examples.append(
            {
                "session": row.session,
                "origin": row.origin,
                "cutoff": str(inputs.base.panels[row.session, row.origin].cutoff),
                "clock_basis": "IDEALIZED_PERIOD_END_NOT_OBSERVED_PUBLICATION",
                "stock_endpoint": x[:, -1, :16].tolist(),
                "shared_market_endpoint": x[0, -1, 16:21].tolist(),
                "four_peer_endpoints": expected.tolist(),
                "peer_perturbation_mean_change": float(altered[0, -1, 0] - before[0, -1, 0]),
            }
        )
    forward = {}
    sample = train.batch((0,))
    seed_all(42)
    mc0 = SharedLSTM(21).eval()
    seed_all(42)
    mc1 = EndpointGatedLSTM().eval()
    with torch.inference_mode():
        if not torch.equal(batch_prediction(mc0, sample), batch_prediction(mc1, sample)):
            raise ValueError("MC1_IDENTITY_INITIALIZATION_FAILED")
    for architecture in QUEUE:
        seed_all(42)
        model = (
            EndpointGatedLSTM() if architecture == "MC1" else SharedLSTM(SHAPES[architecture][0])
        )
        if sum(p.numel() for p in model.parameters()) != SHAPES[architecture][1]:
            raise ValueError("EXACT_FROZEN_PARAMETER_INVENTORY_REQUIRED")
        model.eval()
        batch = peers["inner"].batch((0,)) if architecture == "E5" else sample
        t = time.monotonic()
        with torch.inference_mode():
            prediction = batch_prediction(model, batch)
        if not bool(torch.isfinite(prediction).all()):
            raise ValueError("FINITE_PREFIT_FORWARD_REQUIRED")
        forward[architecture] = {
            "seconds": time.monotonic() - t,
            "parameters": SHAPES[architecture][1],
            "optimizer_steps": 0,
            "eval_mode": not model.training,
        }
    input_binding = {
        "dataset": ref(BRIDGE / "final_v2/dataset_input_binding.json"),
        "market": binding["SPY_store_reference_only_not_TM0_input"],
        "stock_market_views": {k: v.summary() for k, v in views.items()},
        "peer_views": {k: v.summary() for k, v in peers.items()},
        "same_targets_and_masks_for_all_models": True,
        "source_basis": "RESEARCHER_ATTESTED_IDEALIZED_RETROSPECTIVE_CANDIDATE_ONLY",
    }
    write_json(out / "batch_input_binding.json", input_binding)
    write_json(
        out / "preflight_and_input_oracles.json",
        {
            "status": "PASS_NO_FITTING",
            "examples": examples,
            "prefit_forward": forward,
            "MC1_identity_equal_MC0": True,
            "E5_four_peer_divisor4_and_prefix": True,
            "finite_matched_views": {k: v.summary() for k, v in views.items()},
            "preparation_application_only_no_new_scalers": True,
            "prior_TM0_fit_seconds": 52.63942466682056,
            "expected_pair_seconds_NOT_ACTUAL": 900,
            "free_disk_bytes": shutil.disk_usage(Path.cwd()).free,
            "peak_whole_process_RSS_bytes": peak_rss_bytes(),
            "seconds": time.monotonic() - started,
            "new_neural_pairs": 0,
            "confirmation_outcome_rows": 0,
            "upstream_E5_history": (
                "Original v1 FAIL and v2 60-epoch underfit WARN preserved; "
                "v3 engineering PASS is not real efficacy."
            ),
        },
    )
    pointer = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
    snapshot = out / "registry_pointer_v1_snapshot.json"
    snapshot.write_bytes(pointer.read_bytes())
    definition = Path("configs/track_a_candidate_experiment_registry_v2.json")
    write_json(
        definition,
        {
            "schema": 2,
            "scope": "EXACT_TA007_MC0_MC1_E5_BATCH_ONLY",
            "legacy_pointer": ref(snapshot),
            "legacy_real_journal": ref(Path("reports/audit/track_a_real_pairs_v1.jsonl")),
            "new_real_journal": JOURNAL_V2,
            "ceiling": 40,
            "new_pair_limit": 3,
            "counts_failed_starts": True,
            "production_migration": False,
        },
    )
    runs = []
    for architecture in QUEUE:
        use = peers if architecture == "E5" else views
        descriptor = {
            "architecture": architecture,
            "contract": pair_contract(architecture),
            "views": {k: v.summary() for k, v in use.items()},
        }
        descriptor["input_id"] = identity(
            [input_binding["dataset"], input_binding["market"], descriptor]
        )
        descriptor["run_id"] = "TA007:" + architecture + ":" + identity(descriptor)
        runs.append(descriptor)
    plan = {
        "id": "TA007-THREE-PAIR-BATCH-v1",
        "runs": runs,
        "code_sha256": batch_code(Path.cwd()),
        "producer": ref(BRIDGE / "verified_producer.json"),
        "dataset": input_binding["dataset"],
        "market": input_binding["market"],
        "input_binding": ref(out / "batch_input_binding.json"),
        "registry_definition": ref(definition),
        "prior_real_journal": ref(Path("reports/audit/track_a_real_pairs_v1.jsonl")),
        "prior_pointer_snapshot": ref(snapshot),
        "original_protocol": ref(Path("configs/CURRENT_PROTOCOL.json")),
        "tm0_result": ref(PILOT / "first_tm0_seed42_WF1/seed42_tm0_first_pair_result.json"),
        "baseline_snapshot": ref(REVIEW / "permitted_prediction_snapshot.csv"),
        "package_started_at": preflight["package_started_at"],
        "deadline": preflight["deadline"],
        "maximum_wall_seconds": 7200,
        "report_reserve_seconds": 900,
        "expected_pair_seconds_NOT_ACTUAL": 900,
        "starting_pair_budget": "1/40",
        "maximum_ending_pair_budget": "4/40",
        "production_migration": False,
        "confirmation_access": False,
        "no_performance_contingent_branching": True,
        "policy_scope_requested": (
            "Extend qualified researcher-attested local stock/SPY rights/clock/privacy reliance "
            "to exactly these three candidate pairs; accept existing MC0/MC1/E5 engineering "
            "with preserved warnings. No external fact certification or course substitution."
        ),
    }
    write_json(out / "batch_plan.json", plan)
    return {
        "status": "BATCH_AWAITING_APPROVAL",
        "plan": ref(out / "batch_plan.json"),
        "dataset": plan["dataset"],
        "code_sha256": plan["code_sha256"],
        "new_neural_pairs": 0,
    }


def status(plan: dict) -> dict:
    rows = journal_rows_v2(Path(JOURNAL_V2))
    return {
        "global_started_pairs": 1 + sum(r["status"] == "STARTED" for r in rows),
        "runs": {
            r["architecture"]: next(
                (e["status"] for e in reversed(rows) if e["run_id"] == r["run_id"]),
                "PENDING_NOT_STARTED",
            )
            for r in plan["runs"]
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--pair", choices=QUEUE, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare(args.output)))
        return 0
    plan_path = args.plan or args.output / "batch_plan.json"
    plan_ref = ref(plan_path)
    plan, _ = load_plan(Path.cwd(), plan_ref)
    if args.status or args.dry_run:
        print(
            json.dumps(
                {
                    "status": "ZERO_FIT_VALIDATED",
                    **status(plan),
                    "plan": plan_ref,
                    "approval_supplied": args.approval is not None,
                }
            )
        )
        return 0
    if args.approval is None:
        raise ValueError("ACTUAL_BATCH_APPROVAL_REQUIRED_BEFORE_ANY_FIT")
    approval_ref = ref(args.approval)
    approval = json.loads(args.approval.read_text())
    approved = approval_scope(plan_ref, approval)
    if args.pair:
        authority = load_pair_authority(Path.cwd(), plan_ref, approval_ref, args.pair)
        run_worker(authority, (args.output / args.pair).resolve())
        return 0
    batch_started = time.monotonic()
    if any(s != "PENDING_NOT_STARTED" for s in status(plan)["runs"].values()):
        raise ValueError("BATCH_ALREADY_STARTED_NO_REPLAY_OR_RETRY")
    for architecture in approved:
        remaining = (
            datetime.fromisoformat(plan["deadline"]) - datetime.now(timezone.utc)
        ).total_seconds()
        if remaining < plan["expected_pair_seconds_NOT_ACTUAL"] + plan["report_reserve_seconds"]:
            write_json(
                args.output / "continuation_manifest.json",
                {
                    "status": "PENDING_AUTHORIZED_NOT_STARTED",
                    "next": architecture,
                    "reason": "INSUFFICIENT_COMPLETE_PAIR_AND_REPORT_RESERVE",
                    "current": status(plan),
                },
            )
            break
        authority = load_pair_authority(Path.cwd(), plan_ref, approval_ref, architecture)
        command = [
            sys.executable,
            "-B",
            "-m",
            "lstm_data.real_multimodel_batch",
            "--plan",
            str(plan_path),
            "--approval",
            str(args.approval),
            "--output",
            str(args.output),
            "--pair",
            architecture,
        ]
        t = time.monotonic()
        try:
            result = subprocess.run(command, timeout=remaining - 900, check=False).returncode
        except subprocess.TimeoutExpired:
            result = 124
        pair_out = args.output / architecture
        if result != 0:
            rows = journal_rows_v2(Path(JOURNAL_V2))
            own = [r for r in rows if r["run_id"] == authority.run_id]
            if own and own[-1]["status"] not in {"FAILED", "COMPLETED"}:
                authority.append("FAILED", {"reason": "SUPERVISED_WORKER_EXIT", "code": result})
        if pair_out.exists():
            write_json(
                pair_out / "supervisor_actual_runtime.json",
                {
                    "total_pair_wall_seconds": time.monotonic() - t,
                    "return_code": result,
                    "hard_timeout_seconds": remaining - 900,
                },
            )
        if result != 0:
            break
    current = status(plan)
    completed = sum(s == "COMPLETED" for s in current["runs"].values())
    write_json(
        args.output / "batch_execution_summary.json",
        {
            "status": "TA007_THREE_PAIRS_COMPLETED"
            if completed == 3
            else "TA007_PARTIAL_APPROVED_BATCH",
            "approved": approved,
            "actual_batch_execution_seconds": time.monotonic() - batch_started,
            "current": current,
            "permission_consumed_for_started_pairs": True,
        },
    )
    print(json.dumps(current))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
