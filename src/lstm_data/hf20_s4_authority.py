"""S4 live authority, resource checks and strict sequential append-only journal."""

from __future__ import annotations

import json
import os
import resource
import sys
from pathlib import Path

from .config import fingerprint, now
from .hf1m_action_audit import digest
from .hf20_ranking_run import CODE, POINTER
from .real_batch_authority import atomic_replace_json

JOURNAL = Path("reports/audit/track_a_real_pairs_v22_hf20_s4a.jsonl")
DEFINITION = Path("configs/track_a_candidate_experiment_registry_v22_hf20_s4a.json")
RUNS = tuple(f"HF20-S4A-F{y % 100}-H4-{a}-S42" for y in range(2021, 2025) for a in ("NR", "T2R"))


def execution_hash() -> str:
    files = set(CODE) | {str(p) for p in Path("src/lstm_data").glob("hf20_s4*.py")}
    files.update(
        "src/lstm_data/" + n
        for n in [
            "hf1m_ft16_math.py",
            "hf1m_ft16_fit.py",
            "hf1m_ft16_oracles.py",
            "hf1m_action_source.py",
            "hf20_horizon_run.py",
            "hf20_ranking_continue.py",
            "hf20_ranking_continue_report.py",
            "neural_engine.py",
            "hf20_rank_visual_html.py",
            "hf20_rank_visual_template.html",
            "hf20_s4_visual_qa.js",
            "hf20_s4_visual_supplement.js",
        ]
    )
    files.add("scripts/render_hf20_s4.py")
    return fingerprint({p: digest(Path(p)) for p in sorted(files)})


def authorize(out: Path) -> dict:
    path = out / "LIVE_AUTHORITY.json"
    if not path.exists():
        raise ValueError("S4_MANDATORY_LIVE_AUTHORITY_MISSING_BEFORE_FIT")
    a = json.loads(path.read_text())
    p = json.loads((out / "S4_FROZEN_EXPERIMENT_CARD.json").read_text())
    if (
        a.get("kind") != "ACTUAL_DIRECT_USER_RESPONSE"
        or a.get("approved") is not True
        or a.get("proposal_sha256") != digest(out / "S4_FROZEN_EXPERIMENT_CARD.json")
        or a.get("execution_sha256") != execution_hash()
        or p["execution_sha256"] != execution_hash()
        or tuple(a.get("run_ids", [])) != RUNS
        or a.get("neural_starts") != 8
        or a.get("baseline_attempts") != 8
        or a.get("ledger_before") != 106
    ):
        raise ValueError("S4_EXACT_LIVE_AUTHORITY_BINDING")
    for r in p["evidence"]:
        if digest(Path(r["path"])) != r["sha256"]:
            raise ValueError("S4_FROZEN_EVIDENCE_CHANGED:" + r["path"])
    if a.get("resource_caps") != p["resource_caps"]:
        raise ValueError("S4_RESOURCE_AUTHORITY_REQUIRED")
    return a


def resources(out: Path, *, approved: bool = False, reserve_bytes: int = 0) -> dict:
    """Metadata-only disk scan; protected files are never opened or hashed."""
    cap = dict(task_bytes=1_000_000_000, project_bytes=10_000_000_000, ram_bytes=2_000_000_000)
    if approved:
        cap = authorize(out)["resource_caps"]
    task = sum(p.stat().st_size for p in out.rglob("*") if p.is_file() and not p.is_symlink())
    total = 0
    for directory, _, files in os.walk(Path.cwd(), followlinks=False):
        for name in files:
            p = Path(directory) / name
            if not p.is_symlink():
                total += p.stat().st_size
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    result = dict(
        task_bytes=task,
        project_bytes=total,
        peak_rss_bytes=rss,
        reserve_bytes=reserve_bytes,
        caps=cap,
    )
    if (
        task + reserve_bytes > cap["task_bytes"]
        or total + reserve_bytes > cap["project_bytes"]
        or rss > cap["ram_bytes"]
    ):
        raise ValueError("S4_RESOURCE_LIMIT", result)
    return result


def validate(history: list[dict]) -> list[dict]:
    count = 0
    states = {}
    edges = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "COMPLETED": set(),
        "FAILED": set(),
    }
    for i, r in enumerate(history):
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(history[:i]):
            raise ValueError("S4_JOURNAL_CHAIN")
        run, status = r["run_id"], r["status"]
        if status == "STARTED":
            if (
                count >= 8
                or run != RUNS[count]
                or run in states
                or (i and history[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("S4_PREVIOUS_PASS_REQUIRED_NO_RETRY_REORDER_EXTRA")
            count += 1
        elif run not in states or status not in edges[states[run]]:
            raise ValueError("S4_ILLEGAL_TRANSITION")
        if r["global_started_pairs"] != 106 + count or r["effective_ceiling"] != 200:
            raise ValueError("S4_START_ACCOUNTING")
        states[run] = status
    return history


def event(out: Path, run: str, status: str, detail: dict) -> int:
    authorize(out)
    old = json.loads((out / "prior_registry_pointer.json").read_text())
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        history = (
            validate([json.loads(line) for line in JOURNAL.read_text().splitlines()])
            if JOURNAL.exists()
            else []
        )
        current_pointer = json.loads(POINTER.read_text())
        if history and current_pointer.get("real_journal") != str(JOURNAL):
            raise ValueError("S4_ACTIVE_LEDGER_POINTER_CHANGED")
        if status == "STARTED":
            resources(out, approved=True, reserve_bytes=80_000_000)
            if history:
                prior = out / history[-1]["run_id"] / "PASS.json"
                gate = json.loads(prior.read_text())
                if gate["status"] != "PASS_TECHNICAL_AND_DIAGNOSTICS":
                    raise ValueError("S4_PREVIOUS_SCIENTIFIC_GRAPHIC_GATE")
                for path, sha in gate["files"].items():
                    if digest(Path(path)) != sha:
                        raise ValueError("S4_PREVIOUS_GATE_CHANGED")
            elif json.loads(POINTER.read_text()) != old:
                raise ValueError("S4_PRIOR_LEDGER_CHANGED")
        count = 106 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
        row = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            at=now(),
            run_id=run,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
            detail=detail,
            previous_journal=dict(
                path=old["real_journal"], sha256=digest(Path(old["real_journal"]))
            ),
            plan=dict(
                path=str(out / "S4_FROZEN_EXPERIMENT_CARD.json"),
                sha256=digest(out / "S4_FROZEN_EXPERIMENT_CARD.json"),
            ),
            authority=dict(
                path=str(out / "LIVE_AUTHORITY.json"), sha256=digest(out / "LIVE_AUTHORITY.json")
            ),
        )
        validate(history + [row])
        with JOURNAL.open("a") as f:
            f.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        if not DEFINITION.exists():
            with DEFINITION.open("x") as f:
                json.dump(
                    dict(
                        schema_version=22,
                        package="S4A",
                        runs=RUNS,
                        previous_journal=row["previous_journal"],
                        plan=row["plan"],
                    ),
                    f,
                    indent=2,
                )
        atomic_replace_json(
            POINTER,
            dict(
                schema_version=22,
                definition=dict(path=str(DEFINITION), sha256=digest(DEFINITION)),
                plan=row["plan"],
                real_journal=str(JOURNAL),
                previous_journal=row["previous_journal"],
                counts_started_including_failed=True,
                effective_ceiling=200,
                fit_permission=False,
                live_approval_required=True,
                budget_amendment=old["budget_amendment"],
            ),
        )
        return count
    finally:
        lock.unlink()
