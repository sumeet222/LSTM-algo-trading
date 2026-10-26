"""Resume only unstarted S3 IDs at an authorized storage-amendment boundary."""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path

import torch

from . import hf20_horizon_authority as authority
from . import hf20_horizon_run as runner
from .config import now
from .hf20_horizon_preflight import proposed_runs
from .hf20_horizon_report import stage_report
from .hf20_horizon_resources import resources
from .hf20_ranking_data import FoldData
from .hf20_ranking_run import sha, write

MANIFEST = "RESOURCE_AMENDMENT_EXECUTION_v1.json"
NEW_CODE = (
    "src/lstm_data/hf20_horizon_resources.py",
    "src/lstm_data/hf20_horizon_resource_continue.py",
)


def remaining_runs(history: list[dict]) -> list[str]:
    authority.validate(history)
    if history and history[-1]["status"] != "COMPLETED":
        raise ValueError("S3_RESOURCE_CONTINUATION_REQUIRES_DURABLE_COMPLETION")
    started = [r["run_id"] for r in history if r["status"] == "STARTED"]
    if started != proposed_runs()[: len(started)]:
        raise ValueError("S3_RESOURCE_CONTINUATION_CANNOT_RETRY_OR_REORDER")
    return proposed_runs()[len(started) :]


def check_amendment(out: Path) -> dict:
    manifest = json.loads((out / MANIFEST).read_text())
    original = json.loads((out / "EXECUTION_MANIFEST.json").read_text())
    if (
        authority.execution_hash() != original["execution_sha256"]
        or manifest["base_execution_sha256"] != original["execution_sha256"]
        or manifest["scientific_changes"] is not False
        or manifest["additional_starts"] != 0
    ):
        raise ValueError("S3_RESOURCE_ONLY_BINDING_REQUIRED")
    for ref in manifest["bindings"]:
        if sha(Path(ref["path"])) != ref["sha256"]:
            raise ValueError("S3_RESOURCE_AMENDMENT_BINDING_CHANGED")
    prefix = Path(manifest["journal_boundary_snapshot"]).read_bytes()
    if authority.JOURNAL.read_bytes()[: len(prefix)] != prefix:
        raise ValueError("S3_PRE_AMENDMENT_JOURNAL_PREFIX_CHANGED")
    return manifest


class ResourceJournal(authority.Journal):
    """Original transition/gate/accounting implementation, plus a resource receipt."""

    def __init__(self, out: Path):
        super().__init__(out)
        self.amendment = check_amendment(out)
        history = authority.validate(
            [json.loads(s) for s in authority.JOURNAL.read_text().splitlines()]
        )
        self.started = 74 + sum(r["status"] == "STARTED" for r in history)
        self.baselines = 72

    def event(self, run: str, status: str, detail: dict) -> None:
        check_amendment(self.out)
        if status == "STARTED":
            resources(self.out)
        super().event(
            run,
            status,
            dict(
                **detail,
                resource_amendment=dict(
                    path=str(self.out / MANIFEST), sha256=sha(self.out / MANIFEST)
                ),
            ),
        )


def resume(out: Path) -> None:
    authority.authorize(out)
    amendment = check_amendment(out)
    history = authority.validate(
        [json.loads(s) for s in authority.JOURNAL.read_text().splitlines()]
    )
    remaining = remaining_runs(history)
    if remaining != amendment["remaining_runs"]:
        raise ValueError("S3_RESOURCE_CONTINUATION_NOT_EXACT_UNSTARTED_SUFFIX")
    if (out / "RESOURCE_CONTINUATION_STARTED.json").exists():
        raise ValueError("S3_NO_RESOURCE_CONTINUATION_RETRY")
    lock = authority.JOURNAL.with_suffix(".lock")
    owner = json.loads(lock.read_text())
    if (
        owner["owner"] != "S3_RESOURCE_AMENDMENT_SAFE_BOUNDARY"
        or owner["ledger"] != history[-1]["global_started_pairs"]
    ):
        raise ValueError("S3_RESOURCE_BOUNDARY_OWNER_OR_LEDGER")
    # Change only resource-check call sites in this new controller process.
    # All fit/math/export/selector/stage-gate functions remain the sealed originals.
    authority.resources = resources
    runner.resources = resources
    current = resources(out)
    write(
        out / "RESOURCE_CONTINUATION_STARTED.json",
        dict(
            at=now(),
            pid=os.getpid(),
            ledger=history[-1]["global_started_pairs"],
            remaining_runs=remaining,
            resources=current,
            active_training_interrupted=False,
            completed_models_restarted=0,
        ),
    )
    lock.unlink()
    journal = ResourceJournal(out)
    try:
        base = FoldData(live_approved=True)
        for stage in ("A", "B"):
            for run in [r for r in remaining if f"S3{stage}" in r]:
                parts = run.split("-")
                year, h, arm = 2000 + int(parts[2][1:]), int(parts[3][1:]), parts[4]
                resources(out)
                runner.neural_one(base, out, journal, stage, year, h, arm)
                gc.collect()
            if not (out / f"S3{stage}_PASS.json").exists():
                stage_report(out, stage)
                write(
                    out / f"S3{stage}_PASS.json",
                    dict(
                        status="PASS_TECHNICAL",
                        performance_gated=False,
                        ledger=journal.started,
                        resources=resources(out),
                        resource_amendment=str(out / MANIFEST),
                    ),
                )
    except BaseException as error:
        write(
            out / "RESOURCE_CONTINUATION_FATAL_STOP.json",
            dict(
                at=now(),
                error_type=type(error).__name__,
                message=str(error),
                ledger=journal.started,
                no_retry=True,
                approved_caps=current["caps"],
            ),
        )
        raise
    write(
        out / "FITTING_FINISHED.json",
        dict(
            at=now(),
            ledger=journal.started,
            baseline_attempts=72,
            resources=resources(out),
            resource_amendment=str(out / MANIFEST),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    resume(args.out)


if __name__ == "__main__":
    main()
