"""S3 bounded append-only attempts; no reservation and no retry or implicit gate waiver."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from .config import fingerprint, now
from .hf20_horizon_data import DESIGN_SHA, PREPARATION
from .hf20_horizon_preflight import proposed_runs
from .hf20_ranking_authority import resources
from .hf20_ranking_run import CODE, POINTER, sha, write
from .real_batch_authority import atomic_replace_json

JOURNAL = Path("reports/audit/track_a_real_pairs_v21_hf20_s3.jsonl")
DEFINITION = Path("configs/track_a_candidate_experiment_registry_v21_hf20_s3.json")
S3_CODE = (
    "src/lstm_data/hf20_horizon_data.py",
    "src/lstm_data/hf20_horizon_math.py",
    "src/lstm_data/hf20_horizon_preflight.py",
    "src/lstm_data/hf20_horizon_authority.py",
    "src/lstm_data/hf20_horizon_diagnostics.py",
    "src/lstm_data/hf20_horizon_run.py",
    "src/lstm_data/hf20_horizon_report.py",
    "src/lstm_data/hf20_ranking_continue.py",
    "src/lstm_data/hf20_ranking_continue_report.py",
)


def execution_hash() -> str:
    return fingerprint({p: sha(Path(p)) for p in (*CODE, *S3_CODE)})


def authorize(out: Path) -> dict:
    a = json.loads((out / "LIVE_AUTHORITY.json").read_text())
    card = PREPARATION / "S3_FROZEN_EXPERIMENT_CARD.json"
    if (
        sha(card) != DESIGN_SHA
        or a["approved_design_sha256"] != DESIGN_SHA
        or a["kind"] != "ACTUAL_DIRECT_USER_RESPONSE"
        or a["baseline_cap"] != 72
        or a["neural_cap"] != 32
        or a["ledger_before"] != 74
    ):
        raise ValueError("S3_LIVE_AUTHORITY_OR_DESIGN_MISMATCH")
    design = json.loads(card.read_text())
    for ref in (*design["code"], *design["evidence"]):
        if sha(Path(ref["path"])) != ref["sha256"]:
            raise ValueError("S3_FROZEN_BINDING_CHANGED:" + ref["path"])
    return a


def validate(history: list[dict]) -> list[dict]:
    states: dict[str, str] = {}
    count = 0
    transitions = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "COMPLETED": set(),
        "FAILED": set(),
    }
    for i, row in enumerate(history):
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("S3_JOURNAL_CHAIN")
        run, status = row["run_id"], row["status"]
        if status == "STARTED":
            if count >= 32 or run != proposed_runs()[count] or run in states:
                raise ValueError("S3_NO_RETRY_REORDER_OR_EXTRA")
            if (
                i
                and history[i - 1]["status"] != "COMPLETED"
                and not (
                    history[i - 1]["status"] == "FAILED"
                    and history[i - 1]["detail"].get("isolated") is True
                )
            ):
                raise ValueError("S3_PREVIOUS_GATE_INCOMPLETE")
            count += 1
        elif run not in states or status not in transitions[states[run]]:
            raise ValueError("S3_TRANSITION")
        if row["global_started_pairs"] != 74 + count or row["effective_ceiling"] != 200:
            raise ValueError("S3_LEDGER_ACCOUNTING")
        states[run] = status
    return history


class Journal:
    def __init__(self, out: Path):
        self.out = out
        self.original = json.loads((out / "prior_registry_pointer.json").read_text())
        self.started, self.baselines = 74, 0
        self.execution = execution_hash()
        self.pending: str | None = None

    def baseline(self, key: str, status: str, detail: dict | None = None) -> None:
        if status == "STARTED":
            resources(self.out)
            if self.pending is not None or self.baselines >= 72:
                raise ValueError("S3_BASELINE_CAP_OR_UNFINISHED")
            path = self.out / "baseline_attempts.jsonl"
            old = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
            allowed = pd.read_csv(PREPARATION / "S3_PROPOSED_BASELINE_TASKS.csv").key.tolist()
            full_key = "S3A/" + key
            if full_key not in allowed:
                raise ValueError("S3_BASELINE_OUTSIDE_FROZEN_PLAN")
            starts = [r["key"] for r in old if r["status"] == "STARTED"]
            if starts and allowed.index(full_key) <= allowed.index("S3A/" + starts[-1]):
                raise ValueError("S3_BASELINE_ORDER")
            if any(r["key"] == key for r in old):
                raise ValueError("S3_BASELINE_NO_RETRY")
            self.baselines += 1
            self.pending = key
        elif key != self.pending:
            raise ValueError("S3_BASELINE_NOT_PENDING")
        with (self.out / "baseline_attempts.jsonl").open("a") as f:
            f.write(
                json.dumps(
                    dict(
                        at=now(),
                        key=key,
                        status=status,
                        attempt=self.baselines,
                        neural_charge=0,
                        detail=detail or {},
                    ),
                    allow_nan=False,
                )
                + "\n"
            )
            f.flush()
            os.fsync(f.fileno())
        if status != "STARTED":
            self.pending = None

    def event(self, run: str, status: str, detail: dict) -> None:
        if self.execution != execution_hash():
            raise ValueError("S3_EXECUTION_CHANGED_DURING_CAMPAIGN")
        with JOURNAL.with_suffix(".lock").open("x"):
            pass
        try:
            history = (
                validate([json.loads(x) for x in JOURNAL.read_text().splitlines()])
                if JOURNAL.exists()
                else []
            )
            if status == "STARTED":
                resources(self.out)
                manifest = json.loads((self.out / "EXECUTION_MANIFEST.json").read_text())
                for ref in manifest["prepared_bindings"]:
                    if sha(Path(ref["path"])) != ref["sha256"]:
                        raise ValueError("S3_PREPARED_TARGET_INPUT_OR_GATE_CHANGED")
                if (
                    not (self.out / "READINESS_PASS.json").is_file()
                    or not (self.out / "BASELINE_PASS.json").is_file()
                ):
                    raise ValueError("S3_READINESS_AND_BASELINE_GATES_REQUIRED")
                if "S3B" in run and not (self.out / "S3A_PASS.json").is_file():
                    raise ValueError("S3_A_MUST_FINISH_BEFORE_B")
                if history and history[-1]["status"] == "COMPLETED":
                    gate = json.loads(Path(history[-1]["detail"]["gate"]).read_text())
                    if gate["status"] != "PASS_TECHNICAL":
                        raise ValueError("S3_PREVIOUS_SCIENTIFIC_GATE")
                    for p, expected in gate["files"].items():
                        if sha(Path(p)) != expected:
                            raise ValueError("S3_PREVIOUS_VERIFIED_OUTPUT_CHANGED")
            self.started = (
                74 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
            )
            row = dict(
                sequence=len(history) + 1,
                previous=fingerprint(history),
                at=now(),
                run_id=run,
                status=status,
                detail=detail,
                global_started_pairs=self.started,
                effective_ceiling=200,
                plan=dict(
                    path=str(self.out / "EXECUTION_MANIFEST.json"),
                    sha256=sha(self.out / "EXECUTION_MANIFEST.json"),
                ),
                authority=dict(
                    path=str(self.out / "LIVE_AUTHORITY.json"),
                    sha256=sha(self.out / "LIVE_AUTHORITY.json"),
                ),
                previous_journal=dict(
                    path=self.original["real_journal"],
                    sha256=sha(Path(self.original["real_journal"])),
                ),
            )
            validate(history + [row])
            with JOURNAL.open("a") as f:
                f.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            if not DEFINITION.exists():
                write(
                    DEFINITION,
                    dict(
                        schema_version=21,
                        package="HF20_S3",
                        runs=proposed_runs(),
                        plan=row["plan"],
                        previous_journal=row["previous_journal"],
                    ),
                )
            atomic_replace_json(
                POINTER,
                dict(
                    schema_version=21,
                    definition=dict(path=str(DEFINITION), sha256=sha(DEFINITION)),
                    plan=row["plan"],
                    real_journal=str(JOURNAL),
                    previous_journal=row["previous_journal"],
                    counts_started_including_failed=True,
                    effective_ceiling=200,
                    fit_permission=False,
                    live_approval_required=True,
                    budget_amendment=self.original["budget_amendment"],
                ),
            )
        finally:
            JOURNAL.with_suffix(".lock").unlink()
