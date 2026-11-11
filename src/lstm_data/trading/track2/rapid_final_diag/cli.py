"""Seal, validate, pilot and run only the authorized final diagnostic matrix."""

import argparse
import fcntl
import json
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from ..rapid_v1.cli import peak_memory_bytes
from ..rapid_v1.paths import digest, publish
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.strategies import IDS
from ..rapid_v1.verification import source_kernel_parity
from ..rapid_v3_dynamic.engine import DynamicBatch
from .engine import DiagnosticBatch
from .policy import cases
from .provenance import ROOT, V3, load, registry, seal
from .results import CONTROLS, publish_results
from .state import restore, snapshot


def freeze() -> None:
    seal(
        {
            "schema": "HF20_FINAL_TARGETED_DIAGNOSTICS_1",
            "period": ["2021-01-01", "2024-12-31"],
            "all18_retained": IDS,
            "protocol_hash": digest(ROOT / "SOURCE_AND_CONTROL_BINDINGS.md"),
            "cases": [asdict(c) for c in cases()],
            "authority": "Owner final targeted diagnostics prompt 2026-11-10; research only",
            "cache": load(V3 / "PARENT_BOUNDARY.json")["cache"],
            "controls": CONTROLS,
            "pilot_dates": ["2024-11-18", "2024-12-02"],
            "rules": {
                "M04": "EVENT_RESOLVED two distinct eligible failures; reset missing/recovery",
                "R01": "H100 entry-only common maximal t from prescribed one-v20 inequality",
                "M01": "V3 already requires two micro weakening checks: faithful identity variant",
                "M05": "EVENT_RESOLVED: two distinct range failures; reset missing/recovery",
                "M03": "At entry log trail min(2*v20, abs(gap/gap_z)); missing scale abstains",
                "R07": "EVENT_RESOLVED two distinct full-session daily10:30 failures",
            },
            "invariants": [
                "Other exits and original priority preempt confirmation",
                "No change to entry formulas, schedules, costs or hard caps",
                "No redistribution; whole-share rounding after common stress scaling",
                "M01 no third confirmation invented",
                "No new funded M06 or other IDs",
            ],
            "primary": ["net_PnL_USD", "net_per_1M_RTH_gross_dollar_years_USD"],
            "R01_additional_primary": "vintage-caused risk closures / original candidate intents",
            "tail_diagnostic": "worst cohort, worst five, negative cohort sum; unoptimized",
            "offline_sample": "100 hash-smallest exit portions/treatment, after publication",
            "offline_horizons": [60, 240, "NEXT_FULL_SESSION"],
            "offline_forward_limit": 5,
            "output_hard_limit": 150_000_000,
            "target": 100_000_000,
            "status": "SEALED_BEFORE_NEW_FUNDED_OUTCOMES",
        }
    )


def make(first: str, last: str) -> DiagnosticBatch:
    r = registry()
    e = DiagnosticBatch(FeatureCache(Path(r["cache"])), first, last)
    e.variant_registry = r["identity"]
    return e


def validation() -> None:
    registry()
    target = ROOT / "validation"
    target.mkdir(exist_ok=False)
    commands = [
        [
            ".venv/bin/python",
            "-m",
            "pytest",
            "-q",
            "tests/track2_rapid_final_diag",
            "tests/track2_rapid_v3",
            "tests/track2_rapid_v2",
            "tests/track2_rapid_v1",
        ],
        [
            ".venv/bin/ruff",
            "check",
            "--select",
            "E,F,I",
            "src/lstm_data/trading/track2/rapid_final_diag",
            "tests/track2_rapid_final_diag",
        ],
        [
            ".venv/bin/pyright",
            "--pythonpath",
            ".venv/bin/python",
            "src/lstm_data/trading/track2/rapid_final_diag",
            "tests/track2_rapid_final_diag",
        ],
    ]
    results = []
    for n, command in enumerate(commands):
        started = time.monotonic()
        p = subprocess.run(command, text=True, capture_output=True)
        (target / f"{n}.stdout").write_text(p.stdout)
        (target / f"{n}.stderr").write_text(p.stderr)
        results.append(
            {"argv": command, "returncode": p.returncode, "seconds": time.monotonic() - started}
        )
    publish(
        target / "RECEIPT.json",
        {
            "status": "PASS" if all(r["returncode"] == 0 for r in results) else "HOLD",
            "commands": results,
        },
    )
    if any(r["returncode"] for r in results):
        raise ValueError("VALIDATION_HOLD")


def pilot() -> None:
    r = registry()
    if load(ROOT / "validation/RECEIPT.json")["status"] != "PASS":
        raise ValueError("TEST_GATE")
    start = time.monotonic()
    first, last = r["pilot_dates"]
    e = make(first, "2024-12-31")
    e.market.last = last
    e.run()
    # Exact unchanged economic kernel on the same bounded source; no archived-state shortcut.
    original = DynamicBatch(e.cache, first, "2024-12-31", cases())
    original.market.last = last
    original.variant_registry = r["identity"]
    original.run()
    for key in CONTROLS:
        if snapshot(e)["state"] is None:
            raise AssertionError("SNAPSHOT_UNAVAILABLE")
        if e.daily_rows[key] != original.daily_rows[key]:
            raise ValueError("PILOT_CANONICAL_CONTROL_DRIFT " + key)
    # Restart at a committed source-backed day, including accumulated partial state.
    from .state import checkpoint

    small = make(first, "2024-12-31")
    small.market.last = last
    small.run(stop_after=2)
    path = ROOT / "pilot_restart.json.gz"
    checkpoint(path, small)
    resumed = make(first, "2024-12-31")
    resumed.market.last = last
    restore(path, resumed)
    resumed.run()
    if snapshot(e) != snapshot(resumed):
        raise ValueError("PILOT_EXACT_RESTART_DRIFT")
    if e.account_holds or any(a.nav() is None or a.unpriced_special for a in e.dynamic_accounts):
        raise ValueError("PILOT_ECONOMIC_OR_SOURCE_HOLD")
    source_kernel_parity(ROOT / "AVGO_KERNEL_PARITY.json")
    out = ROOT / "pilot"
    receipt = publish_results(e, out, False)
    elapsed = time.monotonic() - start
    publish(
        ROOT / "PILOT_GATE.json",
        {
            "status": "PASS",
            "dates": [first, last],
            "sessions": e.days_completed,
            "exact_controls": len(CONTROLS),
            "restart": "EXACT_FULL_STATE_EQUAL",
            "elapsed_seconds": elapsed,
            "projected_full_seconds": elapsed / (e.days_completed * 4) * 1005,
            "source_backed": receipt,
        },
    )


def run(run_id: str, resume: Path | None) -> None:
    r = registry()
    if (
        load(ROOT / "PILOT_GATE.json")["status"] != "PASS"
        or load(ROOT / "validation/RECEIPT.json")["status"] != "PASS"
    ):
        raise ValueError("READINESS_HOLD")
    run_dir = ROOT / "runs" / run_id
    if resume is None:
        run_dir.mkdir(exist_ok=False, parents=True)
    elif not run_dir.exists() or not resume.is_relative_to(run_dir):
        raise ValueError("RESUME_LINEAGE_REQUIRED")
    with (run_dir / "process.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        started = time.monotonic()
        e = make("2021-01-01", "2024-12-31")
        e.checkpoint_dir = run_dir / "states"
        if resume is not None:
            restore(resume, e)
        stats = e.run()
        output = publish_results(e, run_dir / "funded", True)
        publish(
            run_dir / "RUN_RECEIPT.json",
            {
                "status": "COMPLETE",
                "registry": r["identity"],
                "elapsed_seconds": time.monotonic() - started,
                "engine": stats,
                "peak_RSS_bytes": peak_memory_bytes(),
                "output": output,
                "resume_from": str(resume) if resume else None,
            },
        )
        print(json.dumps({"run": str(run_dir), "status": "COMPLETE", "seconds": stats}), flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["freeze", "validate", "pilot", "run"])
    p.add_argument("--run-id", default="final-diag-20261110-r1")
    p.add_argument("--resume", type=Path)
    a = p.parse_args()
    if a.command == "freeze":
        freeze()
    elif a.command == "validate":
        validation()
    elif a.command == "pilot":
        pilot()
    else:
        run(a.run_id, a.resume)


if __name__ == "__main__":
    main()
