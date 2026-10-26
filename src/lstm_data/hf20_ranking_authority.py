"""Small linked-journal and resource barriers for exactly twelve prospective starts."""

from __future__ import annotations

import json
import os
import resource
import sys
from functools import lru_cache
from pathlib import Path

from .config import fingerprint, now
from .hf20_ranking import RUNS
from .real_batch_authority import atomic_replace_json


@lru_cache(maxsize=4)
def fixed_project_bytes(root: Path, out: Path) -> int:
    """Existing files are immutable; only this task and two tiny journal files may grow."""
    project_bytes = 0
    for directory, children, files in os.walk(root, followlinks=False):
        children[:] = [name for name in children if Path(directory) / name != out]
        for name in files:
            p = Path(directory) / name
            if not p.is_symlink():
                project_bytes += p.stat().st_size
    return project_bytes


def resources(out: Path) -> dict:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != "darwin":
        rss *= 1024
    additions = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    # Reserve 16 MB for append-only journal/definition growth outside the task namespace.
    project_bytes = (
        fixed_project_bytes(Path.cwd().resolve(), out.resolve()) + additions + 16_000_000
    )
    if rss > 2_000_000_000 or additions > 1_000_000_000 or project_bytes > 10_000_000_000:
        raise ValueError("S1S2_RESOURCE_CAP")
    return dict(peak_rss_bytes=rss, task_bytes=additions, project_logical_bytes=project_bytes)


def validate(history: list[dict]) -> list[dict]:
    started = 0
    states = {}
    allowed = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "COMPLETED": set(),
        "FAILED": set(),
    }
    for i, row in enumerate(history):
        run, status = row["run_id"], row["status"]
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("S1S2_JOURNAL_CHAIN")
        if status == "STARTED":
            if (
                started >= 12
                or run != RUNS[started]
                or run in states
                or (i and history[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("S1S2_NO_RETRY_REORDER_EXTRA")
            started += 1
        elif run not in states or status not in allowed[states[run]]:
            raise ValueError("S1S2_INVALID_TRANSITION")
        if row["global_started_pairs"] != 62 + started or row["effective_ceiling"] != 200:
            raise ValueError("S1S2_BUDGET")
        states[run] = status
    return history


def append_neural(
    out: Path, approval: dict, previous: dict, run: str, status: str, detail: dict
) -> int:
    from .hf20_ranking_run import POINTER, code_hash, sha, write

    if run not in approval["neural_runs"]:
        raise ValueError("NEURAL_START_NOT_AUTHORIZED")
    if code_hash() != approval["execution_sha256"]:
        raise ValueError("EXECUTION_CHANGED")
    approval_path = Path(approval["_approval_path"])
    if sha(approval_path) != approval["_approval_sha256"]:
        raise ValueError("LIVE_APPROVAL_FILE_CHANGED")
    journal = Path("reports/audit/track_a_real_pairs_v19_hf20_ranking.jsonl")
    definition = Path("configs/track_a_candidate_experiment_registry_v19_hf20_ranking.json")
    lock = journal.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        raw = journal.read_bytes() if journal.exists() else b""
        if raw and not raw.endswith(b"\n"):
            raise ValueError("TRUNCATED_S1S2_JOURNAL")
        history = validate([json.loads(r) for r in raw.splitlines()])
        if status == "STARTED":
            resources(out)
            if history:
                gate = out / history[-1]["run_id"] / "PASS.json"
                g = json.loads(gate.read_text())
                if g["status"] != "PASS_TECHNICAL":
                    raise ValueError("PREVIOUS_SCIENTIFIC_GATE")
                for path, expected in g["files"].items():
                    if sha(Path(path)) != expected:
                        raise ValueError("PRIOR_GATE_ARTIFACT_CHANGED")
        count = 62 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
        record = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            at=now(),
            run_id=run,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
            plan=dict(path=str(out / "proposal.json"), sha256=sha(out / "proposal.json")),
            authority=dict(path=str(approval_path), sha256=sha(approval_path)),
            previous_journal=dict(
                path=previous["real_journal"], sha256=sha(Path(previous["real_journal"]))
            ),
            detail=detail,
        )
        validate(history + [record])
        with journal.open("ab") as stream:
            stream.write((json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        if not definition.exists():
            write(
                definition,
                dict(
                    schema_version=19,
                    package="HF20_S1_S2",
                    runs=list(RUNS),
                    plan=record["plan"],
                    previous_journal=record["previous_journal"],
                ),
            )
        atomic_replace_json(
            POINTER,
            dict(
                schema_version=19,
                definition=dict(path=str(definition), sha256=sha(definition)),
                plan=record["plan"],
                real_journal=str(journal),
                previous_journal=record["previous_journal"],
                counts_started_including_failed=True,
                effective_ceiling=200,
                fit_permission=False,
                live_approval_required=True,
                budget_amendment=previous["budget_amendment"],
            ),
        )
        return count
    finally:
        lock.unlink()
