"""Seal, validate and run the fixed Rapid V2 diagnostic matrix offline."""

import argparse
import fcntl
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from ..rapid_v1.cli import peak_memory_bytes, unique
from ..rapid_v1.paths import ROOT as V1_ROOT
from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.verification import preserve_check, source_kernel_parity
from .engine import Batch
from .report import baseline_check, emit, summarize
from .state import restore, snapshot
from .variants import FIRST, LAST, case_axis

ROOT = Path("trading/track2/rapid_v2_diagnostics")
CODE = Path("src/lstm_data/trading/track2/rapid_v2_diagnostics")
TESTS = Path("tests/track2_rapid_v2")
V1_RESULTS = V1_ROOT / "runs/rapid-v1-defaults-20261110-r1/results"
V1_BENCH = V1_ROOT / "runs/benchmark_20261110T220133119214Z"
LIMIT = 200_000_000


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def code_hashes() -> dict[str, str]:
    return {str(p): digest(p) for root in (CODE, TESTS) for p in sorted(root.glob("*.py"))}


def v1_integrity() -> dict:
    before = load(ROOT / "V1_BOUNDARY_BEFORE.json")
    for path, rec in before["files"].items():
        p = Path(path)
        if p.stat().st_mtime_ns != rec["mtime_ns"] or digest(p) != rec["sha256"]:
            raise ValueError("V1_PROTECTED_INPUT_DRIFT:" + path)
    return before


def freeze(reason: str | None) -> None:
    old = v1_integrity()
    file = ROOT / "EXPERIMENT_REGISTRY.json"
    code = code_hashes()
    if file.exists():
        if not reason:
            raise FileExistsError(file)
        initial = load(file)
        body = {
            **initial,
            "code_and_test_hashes": code,
            "amendment_reason": reason,
            "initial_registry_sha256": digest(file),
        }
        body.pop("registry_identity")
        file = ROOT / "amendments" / (unique() + ".json")
    else:
        body = {
            "version": "RAPID_V2_FIXED_MATRIX_1",
            "authorized_period": [FIRST, LAST],
            "matrix": [asdict(x) for x in case_axis()],
            "code_and_test_hashes": code,
            "V1_boundary_sha256": digest(ROOT / "V1_BOUNDARY_BEFORE.json"),
            "V1_executed_registry_identity": old["V1_executed_registry"],
            "V1_result_manifest_sha256": old["V1_result_manifest_sha256"],
            "V1_cache": old["V1_feature_cache"],
            "V1_content_sha256": old["V1_content_sha256"],
            "parent_integrity_sha256": digest(ROOT / "PARENT_RESEARCH_BEFORE.json"),
            "explicit_scope": {
                "allocation": "Multiply eligible V1 vintage budget before rounding or name caps.",
                "liquidation": "V1 hard limits and causal forced reduction remain in every case.",
                "session_horizon": "Same ET nominal slot on Nth subsequent XNYS session, "
                "abstain if slot absent. No post-2024 observations.",
                "prices": "V1 raw-share next valid executable open, V1 received submission mark, "
                "lag and concession models. Independent arrival and paid-cost attribution.",
                "cost_alternative": "Arithmetic zero incremental price concession on fixed fills. "
                "Commission, carry and funding remain. No funded cost sweep.",
                "reporting": "All 108 cases, H100 matched against immutable V1 exports. "
                "USD residual <=1e-7, return metrics <=1e-12.",
                "exposure_year": "Causal gross dollar RTH minute sum divided by 252 x 390. "
                "Pending shares excluded from exposure, included in hard limits.",
                "hold": "Required unresolved market/action or invalid NAV is a scoped HOLD. "
                "Unresolved pending orders and exposure remain explicit.",
                "clock": "V1 causal receipt, entry expiry, order priorities and participation.",
                "output_limit_bytes": LIMIT,
                "runtime_projection_limit_seconds": 1800,
                "baseline_costs": "V1 mode-specific, no funded cost alternatives.",
                "named_abstention": "FUTURE_SESSION_SLOT_UNAVAILABLE plus all V1 typed reasons.",
            },
            "dependencies": {
                p: importlib.metadata.version(p)
                for p in (
                    "numpy",
                    "pandas",
                    "pyarrow",
                    "exchange_calendars",
                )
            },
            "qualification": "Exploratory reused 2021-24. Retrospective source/actions, fixed "
            "survivors, assumed latency/borrow and OHLCV transaction proxy.",
        }
    body["registry_identity"] = canonical(body)
    publish(file, body)
    publish(file.with_suffix(".seal.json"), {"path": str(file), "sha256": digest(file)})
    print(file, body["registry_identity"], flush=True)


def registry() -> dict:
    initial = ROOT / "EXPERIMENT_REGISTRY.json"
    current = [initial, *sorted((ROOT / "amendments").glob("*.json"))]
    current = [p for p in current if not p.name.endswith(".seal.json")]
    file = current[-1]
    seal = load(file.with_suffix(".seal.json"))
    value = load(file)
    identity = value.pop("registry_identity")
    if (
        digest(file) != seal["sha256"]
        or canonical(value) != identity
        or code_hashes() != value["code_and_test_hashes"]
        or digest(ROOT / "V1_BOUNDARY_BEFORE.json") != value["V1_boundary_sha256"]
        or canonical([asdict(c) for c in case_axis()]) != canonical(value["matrix"])
    ):
        raise ValueError("RAPID_V2_REGISTRY_DRIFT")
    if file != initial:
        first = load(initial)
        if digest(initial) != value["initial_registry_sha256"] or any(
            canonical(value[k]) != canonical(first[k])
            for k in (
                "matrix",
                "explicit_scope",
                "V1_boundary_sha256",
                "authorized_period",
            )
        ):
            raise ValueError("AMENDMENT_POLICY_DRIFT")
    return {**value, "registry_identity": identity, "path": str(file)}


def process(args: list[str], root: Path, name: str) -> dict:
    started = time.monotonic()
    result = subprocess.run(args, capture_output=True, text=True)
    stdout, stderr = root / (name + ".stdout"), root / (name + ".stderr")
    stdout.write_text(result.stdout)
    stderr.write_text(result.stderr)
    return {
        "argv": args,
        "returncode": result.returncode,
        "seconds": time.monotonic() - started,
        "stdout_sha256": digest(stdout),
        "stderr_sha256": digest(stderr),
    }


def validate(reg: dict) -> None:
    root = ROOT / "validation" / unique()
    root.mkdir(parents=True)
    v5 = "tests/track2_stage35_v5/test_next_valid_execution.py::"
    tests = [
        ".venv/bin/python",
        "-m",
        "pytest",
        "-q",
        str(TESTS),
        "tests/track2_rapid_v1",
        v5 + "test_wait_next_valid_and_nominal_lifetime",
        v5 + "test_open_exit_remains_without_expiry_and_partial_fees_accumulate",
        v5 + "test_later_open_cannot_rewrite_submission_or_predecision_state",
        v5 + "test_actual_pre_spinoff_share_cases_exact_without_tolerance_waiver",
    ]
    cmds = {
        "pytest": tests,
        "ruff": [".venv/bin/ruff", "check", "--select", "E,F,I", str(CODE), str(TESTS)],
        "types": [
            ".venv/bin/pyright",
            "--pythonpath",
            ".venv/bin/python",
            "--outputjson",
            str(CODE),
            str(TESTS),
        ],
    }
    receipts = {name: process(args, root, name) for name, args in cmds.items()}
    passed = all(v["returncode"] == 0 for v in receipts.values())
    publish(
        root / "VALIDATION.json",
        {
            "status": "PASS" if passed else "HOLD",
            "registry": reg["registry_identity"],
            "checks": receipts,
        },
    )
    print(root, "PASS" if passed else "HOLD", flush=True)
    if not passed:
        raise ValueError("VALIDATION_HOLD")


def require_validation(reg: dict) -> Path:
    for p in reversed(sorted((ROOT / "validation").glob("*/VALIDATION.json"))):
        m = load(p)
        if m["registry"] == reg["registry_identity"] and m["status"] == "PASS":
            for name, check in m["checks"].items():
                if check["returncode"] != 0 or any(
                    digest(p.parent / f"{name}.{s}") != check[s + "_sha256"]
                    for s in ("stdout", "stderr")
                ):
                    raise ValueError("VALIDATION_RECEIPT_DRIFT")
            return p
    raise PermissionError("RAPID_V2_TEST_GATE_REQUIRED")


def batch(reg: dict, first: str, last: str, baseline_only: bool = False) -> Batch:
    cache = FeatureCache(Path(reg["V1_cache"]))
    cases = tuple(x for x in case_axis() if not baseline_only or x.variant == "H100")
    engine = Batch(cache, first, last, cases)
    engine.variant_registry = reg["registry_identity"]
    return engine


def pilot(reg: dict) -> None:
    tests = require_validation(reg)
    out = ROOT / "pilots" / unique()
    out.mkdir(parents=True)
    v1_bench = load(V1_BENCH / "BENCHMARK_GATE.json")
    expected = V1_BENCH / "month/results"
    found = next(r for r in v1_bench["measurements"] if r["label"] == "month")
    if digest(expected / "manifest.json") != found["result_manifest_sha256"]:
        raise ValueError("V1_PILOT_MANIFEST_DRIFT")
    manifest = load(expected / "manifest.json")
    if any(digest(expected / f) != h for f, h in manifest["files"].items()):
        raise ValueError("V1_PILOT_PAYLOAD_DRIFT")
    full = batch(reg, "2021-01-04", "2021-01-29")
    started = time.monotonic()
    actual = full.run()
    elapsed = time.monotonic() - started
    pilot_rows = [summarize(full, a) for a in full.fast_accounts]
    checked = baseline_check(full, pilot_rows, expected)
    projection = elapsed * 1005 / actual["sessions"]
    publish(
        out / "MONTH_REPLAY.json",
        {
            "actual": actual,
            "baseline": checked,
            "peak_RSS_bytes": peak_memory_bytes(),
            "all_case_count": len(full.cases),
            "full_projection_seconds": projection,
            "status_counts": {
                s: sum(r["status"] == s for r in pilot_rows)
                for s in ("COMPLETE", "NO_TRADES", "HOLD")
            },
        },
    )
    if any(r["status"] == "HOLD" for r in pilot_rows):
        publish(
            out / "PILOT_HOLD.json", {"holds": [r for r in pilot_rows if r["status"] == "HOLD"]}
        )
        raise ValueError("MATERIAL_VARIANT_PILOT_HOLD")
    if projection > 1800:
        raise ValueError("PROJECTED_RUNTIME_EXCEEDS_PREREGISTERED_BUDGET")
    source_kernel_parity(out / "AVGO_PARITY.json")
    short = batch(reg, "2021-01-04", "2021-01-08")
    short.run()
    uninterrupted = canonical(snapshot(short))
    stopped = batch(reg, "2021-01-04", "2021-01-08")
    stopped.checkpoint_dir = out / "state"
    stopped.run(stop_after=2)
    resumed = batch(reg, "2021-01-04", "2021-01-08")
    restore(out / "state/2021-01-05.json.gz", resumed)
    resumed.run()
    if canonical(snapshot(resumed)) != uninterrupted:
        raise ValueError("RAPID_V2_RESTART_PARITY")
    publish(
        out / "PILOT_GATE.json",
        {
            "status": "PASS",
            "registry": reg["registry_identity"],
            "tests": digest(tests),
            "restart_state_sha256": uninterrupted,
            "outputs": {
                f: digest(out / f)
                for f in (
                    "AVGO_PARITY.json",
                    "MONTH_REPLAY.json",
                )
            },
        },
    )
    print(out, "PASS", f"month {elapsed:.2f}s, full estimate {projection:.1f}s", flush=True)


def require_pilot(reg: dict) -> Path:
    require_validation(reg)
    for p in reversed(sorted((ROOT / "pilots").glob("*/PILOT_GATE.json"))):
        value = load(p)
        if value["registry"] == reg["registry_identity"] and value["status"] == "PASS":
            if any(digest(p.parent / name) != sha for name, sha in value["outputs"].items()):
                raise ValueError("PILOT_RECEIPT_DRIFT")
            return p
    raise PermissionError("RAPID_V2_SOURCE_PILOT_GATE_REQUIRED")


def size(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def screen(reg: dict, run_id: str, resume: bool) -> None:
    if not re.fullmatch("[A-Za-z0-9_-]+", run_id):
        raise ValueError("INVALID_RUN_ID")
    gate = require_pilot(reg)
    v1_integrity()
    ROOT.mkdir(exist_ok=True)
    with (ROOT / "engine.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        out = ROOT / "runs" / run_id
        if not resume:
            out.mkdir(parents=True, exist_ok=False)
            publish(
                out / "START.json",
                {
                    "registry": reg["registry_identity"],
                    "pid": os.getpid(),
                    "argv": sys.argv,
                    "pilot_sha256": digest(gate),
                },
            )
        elif load(out / "START.json")["registry"] != reg["registry_identity"]:
            raise ValueError("RESUME_REGISTRY_MISMATCH")
        if (out / "RUN_COMPLETION.json").exists():
            raise FileExistsError("SEALED_RUN")
        engine = batch(reg, FIRST, LAST)
        engine.checkpoint_dir = out / "states"
        if resume:
            latest = max(engine.checkpoint_dir.glob("*.json.gz"))
            restore(latest, engine)
            publish(
                out / ("RESUME_" + unique() + ".json"),
                {"state": str(latest), "sha256": digest(latest), "pid": os.getpid()},
            )
        started = time.monotonic()
        cpu = time.process_time()
        try:
            run = engine.run()
            if run["sessions"] != 1005 or run["last_session"] != LAST:
                raise ValueError("INCOMPLETE_EVALUATION_SESSIONS")
            results = out / ("results_" + unique())
            results.mkdir()
            summary = emit(engine, results, V1_RESULTS)
            v1_integrity()
            protected = out / "PARENT_RESEARCH_AFTER.json"
            if not protected.exists():
                preserve_check(protected)
            used = size(out)
            if used > LIMIT:
                raise ValueError("OUTPUT_BUDGET_EXCEEDED")
            manifest = {
                "result_files": {p.name: digest(p) for p in sorted(results.iterdir())},
                "code_and_test_hashes": code_hashes(),
            }
            publish(results / "MANIFEST.json", manifest)
            publish(
                out / "RUN_COMPLETION.json",
                {
                    "status": "PARTIAL" if summary["status_counts"].get("HOLD") else "COMPLETE",
                    "registry": reg["registry_identity"],
                    "results": str(results),
                    "result_manifest_sha256": digest(results / "MANIFEST.json"),
                    "source_partitions_this_process": engine.market.reads,
                    "source_period": [FIRST, LAST],
                    "runtime_seconds": time.monotonic() - started,
                    "CPU_seconds": time.process_time() - cpu,
                    "peak_RSS_bytes": peak_memory_bytes(),
                    "bytes_before_completion": used,
                    "integrity_receipt_sha256": digest(protected),
                    "V1_boundary_rechecked": True,
                    **run,
                    **summary,
                },
            )
            print(out, summary["status_counts"], flush=True)
        except (ValueError, AssertionError) as error:
            publish(
                out / ("HOLD_" + unique() + ".json"),
                {
                    "error": str(error),
                    "committed_sessions": engine.days_completed,
                    "frontier": engine.last_completed,
                },
            )
            raise


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["freeze", "validate", "pilot", "screen", "resume"])
    p.add_argument("--run-id")
    p.add_argument("--amendment-reason")
    args = p.parse_args()
    if args.command == "freeze":
        freeze(args.amendment_reason)
        return
    r = registry()
    if args.command == "validate":
        validate(r)
    elif args.command == "pilot":
        pilot(r)
    else:
        if not args.run_id:
            p.error("--run-id is required")
        screen(r, args.run_id, args.command == "resume")


if __name__ == "__main__":
    main()
