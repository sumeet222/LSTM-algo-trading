"""Explicitly approved P021 continuation: preserve failed start33; never recalibrate it."""

from __future__ import annotations

import argparse
import json
import math
import os
import resource
import time
from pathlib import Path

import pandas as pd
import torch

from .config import atomic_new, digest, fingerprint, now, write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_authority import IDS, POINTER
from .hf1m_training_authority import code_binding as base_code
from .hf1m_training_authority import read_rows as failed_prefix
from .hf1m_training_data import load_views
from .hf1m_training_run import epoch_pass, predictions, run
from .hf20_training_run import checkpoint, reload_checkpoint
from .neural_engine import SharedLSTM, optimizer, seed_all
from .neural_lifecycle import state_hash
from .real_batch_authority import atomic_replace_json

JOURNAL = Path("reports/audit/track_a_real_pairs_v9.jsonl")


def code_binding() -> dict:
    return {**base_code(), "hf1m_training_recovery.py": digest(Path(__file__))}


def read_rows(path: Path = JOURNAL) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P021_RECOVERY_TRUNCATED_JOURNAL")
    rows = [json.loads(s) for s in raw.splitlines()]
    states: dict[str, str] = {}
    starts = 0
    transitions = {
        "RESUMED_EXISTING_START": {"REFITTING", "FAILED_AFTER_RESUME"},
        "STARTED": {"CALIBRATED", "FAILED_AFTER_START"},
        "CALIBRATED": {"REFITTING", "FAILED_AFTER_START"},
        "REFITTING": {"COMPLETED", "FAILED_AFTER_START", "FAILED_AFTER_RESUME"},
        "COMPLETED": set(),
        "FAILED_AFTER_START": set(),
        "FAILED_AFTER_RESUME": set(),
    }
    for i, r in enumerate(rows):
        name, status = r["run_id"], r["status"]
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(rows[:i]) or name not in IDS:
            raise ValueError("P021_RECOVERY_CHAIN")
        if i == 0:
            if name != IDS[0] or status != "RESUMED_EXISTING_START":
                raise ValueError("P021_EXISTING_START33_ONLY_FIRST")
        elif status == "STARTED":
            if (
                starts >= 3
                or name != IDS[starts + 1]
                or name in states
                or rows[i - 1]["status"] != "COMPLETED"
            ):
                raise ValueError("P021_RECOVERY_NO_RETRY_REORDER_EXTRA_START")
            starts += 1
        elif name not in states or status not in transitions[states[name]]:
            raise ValueError("P021_RECOVERY_INVALID_TRANSITION")
        if r["global_started_pairs"] != 33 + starts or r["effective_ceiling"] != 200:
            raise ValueError("P021_RECOVERY_BUDGET")
        states[name] = status
    return rows


def ensure(plan_path: Path, approval: Path | None, run_id: str, *, terminal: bool = False) -> dict:
    p = json.loads(plan_path.read_text())
    if approval is None:
        raise ValueError("P021_REPAIR_CONTINUATION_LIVE_APPROVAL_REQUIRED")
    a = json.loads(approval.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("proposal_sha256") != digest(plan_path)
        or a.get("code_sha256") != fingerprint(code_binding())
        or a.get("approved_runs") != list(IDS)
        or a.get("resume_existing_start33_without_recalibration") is not True
        or p["code"] != code_binding()
        or p["runs"] != list(IDS)
        or run_id not in IDS
        or p["opening_started"] != 33
        or p["maximum_new_starts"] != 3
        or p["ceiling"] != 200
        or p["heldout_access"] is not False
    ):
        raise ValueError("P021_EXACT_REPAIR_CONTINUATION_SCOPE_REQUIRED")
    if not terminal and pd.Timestamp.now(tz="UTC") >= pd.Timestamp(p["fit_deadline"]):
        raise ValueError("P021_RECOVERY_AUTHORITY_EXPIRED")
    for r in p["protected_refs"] + [
        p["input_contract"],
        p["previous_journal"],
        p["original_plan"],
        p["registry_definition"],
        p["selected_calibration_checkpoint"],
    ]:
        checked(r)
    prior = failed_prefix(Path(p["previous_journal"]["path"]))
    if prior[-1]["status"] != "FAILED_AFTER_START" or prior[-1]["global_started_pairs"] != 33:
        raise ValueError("P021_RECOVERY_EXPECT_PRESERVED_FAILED33")
    original = json.loads(checked(p["original_plan"]).read_text())
    for key in (
        "input_contract",
        "fit_recipes",
        "views",
        "source_revision",
        "symbols",
        "feature_id",
        "target_id",
        "frozen_training",
        "private_root",
        "cpu_threads",
    ):
        if p[key] != original[key]:
            raise ValueError("P021_RECOVERY_SCIENTIFIC_CHANGE:" + key)
    ptr = json.loads(POINTER.read_text())
    if digest(POINTER) != p["previous_pointer"]["sha256"] and (
        ptr.get("schema") != 9
        or ptr.get("plan") != ref(plan_path)
        or ptr.get("real_journal") != str(JOURNAL)
    ):
        raise ValueError("P021_RECOVERY_OTHER_ACTIVE_LEDGER")
    read_rows()
    return p


def append(plan_path: Path, approval: Path, run_id: str, status: str, detail: dict) -> None:
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        p = ensure(
            plan_path,
            approval,
            run_id,
            terminal=status in ("COMPLETED", "FAILED_AFTER_START", "FAILED_AFTER_RESUME"),
        )
        rows = read_rows()
        starts = sum(r["status"] == "STARTED" for r in rows)
        if status == "STARTED" and run_id == IDS[2]:
            pair = json.loads((plan_path.parent / "PASS_SEED42_PAIR.json").read_text())
            if pair["status"] != "PASS_SEED42_PAIR" or pair["runs"] != list(IDS[:2]):
                raise ValueError("P021_RECOVERY_SEED42_PAIR_GATE_REQUIRED")
        event = dict(
            sequence=len(rows) + 1,
            previous=fingerprint(rows),
            at=now(),
            run_id=run_id,
            status=status,
            detail=detail,
            authority=ref(approval),
            plan=ref(plan_path),
            previous_journal=p["previous_journal"],
            global_started_pairs=33 + starts + int(status == "STARTED"),
            effective_ceiling=200,
            existing_start33_retained=True,
        )
        pending = JOURNAL.with_suffix(".pending")
        atomic_new(
            pending,
            (JOURNAL.read_bytes() if JOURNAL.exists() else b"")
            + json.dumps(event, sort_keys=True, allow_nan=False).encode()
            + b"\n",
        )
        read_rows(pending)
        if not rows:
            atomic_replace_json(
                POINTER,
                dict(
                    schema=9,
                    definition=p["registry_definition"],
                    plan=ref(plan_path),
                    real_journal=str(JOURNAL),
                    previous_journal=p["previous_journal"],
                    previous_pointer=p["previous_pointer"],
                    budget_amendment=p["budget_amendment"],
                    counts_started_including_failed=True,
                    fit_permission=False,
                ),
            )
        os.replace(pending, JOURNAL)
    finally:
        lock.unlink()


def continue_first(plan_path: Path, approval: Path) -> None:
    """Never rerun calibration. Fresh refit is the one originally selected epoch."""
    started = time.monotonic()
    name = IDS[0]
    p = ensure(plan_path, approval, name)
    out = Path(p["private_root"]) / name / "continuation_v1"
    public = plan_path.parent / name
    if out.exists() or public.exists():
        raise ValueError("P021_RECOVERY_IMMUTABLE_OUTPUT_NO_RETRY")
    views = load_views(Path(p["input_contract"]["path"]))
    if {k: v.summary() for k, v in views.items()} != p["views"]:
        raise ValueError("P021_RECOVERY_INPUT_CHANGED")
    original = Path(p["original_plan"]["path"]).parent
    progress = pd.read_csv(original / name / "epochs_progress.csv")
    if (
        len(progress) != 12
        or int(progress.selected_epoch.iloc[-1]) != 1
        or progress.stop_reason.iloc[-1] != "PATIENCE_STOP"
    ):
        raise ValueError("P021_RECOVERY_EXACT12_SELECTED1_REQUIRED")
    torch.set_num_threads(p["cpu_threads"])
    torch.set_num_interop_threads(1)
    selected = checked(p["selected_calibration_checkpoint"])
    cal = json.loads(selected.with_suffix(".manifest.json").read_text())
    model = reload_checkpoint(selected, cal["binding"], cal)
    second = reload_checkpoint(selected, cal["binding"], cal)
    out.mkdir(parents=True)
    public.mkdir(parents=True)
    append(
        plan_path,
        approval,
        name,
        "RESUMED_EXISTING_START",
        dict(
            original_failed_start=33, calibration_replayed=False, selected_checkpoint=ref(selected)
        ),
    )
    try:
        checks = []
        artifacts = {"calibration_selected.pt": ref(selected)}
        for split in ("inner_train", "inner_validation"):
            f = predictions(
                model,
                views[split],
                LossPolicy("C0"),
                dict(run_id=name, seed=42, arm="C0", checkpoint_sha256=cal["checkpoint"]["sha256"]),
            )
            other = predictions(
                second,
                views[split],
                LossPolicy("C0"),
                dict(run_id=name, seed=42, arm="C0", checkpoint_sha256=cal["checkpoint"]["sha256"]),
            )
            if not f.equals(other):
                raise ValueError("P021_RECOVERY_CALIBRATION_RELOAD_MISMATCH")
            path = out / (split + "_predictions.parquet")
            f.to_parquet(path, index=False)
            artifacts[path.name] = ref(path)
            checks.append(dict(partition=split, rows=len(f), reload_max_error=0.0))
        seed_all(42)
        final = SharedLSTM()
        initial = state_hash(final)
        opt = optimizer(final)
        pre = json.loads((original / "dry_precheck.json").read_text())
        if initial != pre["initial_hashes"]["42"] or opt.state:
            raise ValueError("P021_RECOVERY_FRESH_SEED42_REQUIRED")
        append(
            plan_path,
            approval,
            name,
            "REFITTING",
            dict(initial_hash=initial, optimizer_state_empty=True, exact_epochs=1),
        )
        ensure(plan_path, approval, name)
        record, batches = epoch_pass(final, views["refit"], 1, 42, LossPolicy("C0"), opt)
        common = {
            **cal["binding"],
            "stage": "REFIT_FINAL",
            "fit_version": "refit",
            "scale": views["refit"].source.fit["t2_scale"],
            "code_sha256": p["code_sha256"],
            "plan": ref(plan_path),
            "calibration_code_sha256": cal["binding"]["code_sha256"],
            "continuation_of_charged_start": 33,
        }
        fit = checkpoint(out / "refit_final.pt", final, common)
        loaded = reload_checkpoint(out / "refit_final.pt", common, fit)
        artifacts["refit_final.pt"] = ref(out / "refit_final.pt")
        for split in ("refit", "development"):
            identity = dict(
                run_id=name, seed=42, arm="C0", checkpoint_sha256=fit["checkpoint"]["sha256"]
            )
            a = predictions(final, views[split], LossPolicy("C0"), identity)
            b = predictions(loaded, views[split], LossPolicy("C0"), identity)
            if not a.equals(b):
                raise ValueError("P021_RECOVERY_REFIT_RELOAD_MISMATCH")
            path = out / (split + "_predictions.parquet")
            a.to_parquet(path, index=False)
            artifacts[path.name] = ref(path)
            checks.append(dict(partition=split, rows=len(a), reload_max_error=0.0))
        table = pd.concat(
            [progress, pd.DataFrame([dict(phase="refit", **record)])], ignore_index=True
        )
        table["checkpoint_selected"] = table.phase.eq("calibration") & table.epoch.eq(1)
        table.to_csv(public / "epochs.csv", index=False)
        batchpath = out / "gradient_batches.parquet"
        pd.DataFrame([dict(phase="refit", **b) for b in batches]).to_parquet(batchpath, index=False)
        artifacts[batchpath.name] = ref(batchpath)
        write_json(
            public / "run_result.json",
            dict(
                status="COMPLETED",
                run_id=name,
                seed=42,
                arm="C0",
                selector=dict(
                    epoch=12,
                    selected=1,
                    best=float(progress.qualifying_best.iloc[-1]),
                    raw_min=float(progress.raw_best.iloc[-1]),
                    raw_epoch=int(progress.raw_best_epoch.iloc[-1]),
                    status="PATIENCE_STOP",
                ),
                calibration_epochs=12,
                refit_epochs=1,
                calibration_steps=1896,
                refit_steps=math.ceil(2980 / 16),
                initial_hash=initial,
                refit_initial_hash=initial,
                fresh_optimizer_state_empty=True,
                calibration=cal,
                refit=fit,
                reload_checks=checks,
                artifacts=artifacts,
                epochs=ref(public / "epochs.csv"),
                device="cpu",
                threads=p["cpu_threads"],
                elapsed_seconds=time.monotonic() - started,
                peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                recovery=(
                    "Original failed export event preserved; no calibration rerun or "
                    "additional start. Completed selected fresh refit only."
                ),
                telemetry_limitation=(
                    "All12 calibration epoch summaries retained; original "
                    "in-memory per-batch calibration norms lost on failure. "
                    "No replay to regenerate them."
                ),
            ),
        )
        append(plan_path, approval, name, "COMPLETED", dict(result=ref(public / "run_result.json")))
    except BaseException as error:
        write_json(
            public / "failure.json", dict(status="FAILED_AFTER_RESUME", error=str(error), at=now())
        )
        append(
            plan_path,
            approval,
            name,
            "FAILED_AFTER_RESUME",
            dict(failure=ref(public / "failure.json")),
        )
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--run-id", choices=IDS, required=True)
    a = parser.parse_args()
    if a.run_id == IDS[0]:
        continue_first(a.plan, a.approval)
    else:
        run(a.plan, a.approval, a.run_id, check=ensure, journal=append)


if __name__ == "__main__":
    main()
