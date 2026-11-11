"""Reproducible compact screen; no force switch, optimization or neural runner."""

import argparse
import datetime
import fcntl
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

from .paths import ROOT, code_identity, digest, publish
from .registry import freeze_registry, verify_registry
from .reporting import footprint, write_results
from .runner import FastEngine
from .shared_features import FeatureCache, build_cache
from .state import restore_state
from .strategies import IDS
from .verification import preserve_check, source_kernel_parity

PILOTS = (
    ("2021-01-04", "2021-01-08"),
    ("2021-06-02", "2021-06-11"),
    ("2022-08-24", "2022-08-26"),
    ("2024-05-09", "2024-05-17"),
    ("2024-11-27", "2024-12-02"),
)
V5_TESTS = [
    "test_wait_next_valid_and_nominal_lifetime",
    "test_open_exit_remains_without_expiry_and_partial_fees_accumulate",
    "test_later_open_cannot_rewrite_submission_or_predecision_state",
    "test_actual_calendar_later_observation_is_strictly_future_and_rth",
    "test_lossless_checkpoint_compression_is_atomic_deterministic_and_immutable",
    "test_actual_pre_spinoff_share_cases_exact_without_tolerance_waiver",
]


def unique() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def peak_memory_bytes() -> int:
    n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if sys.platform == "darwin" else n * 1024)


def checked_command(arguments: list[str], out: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run(arguments, text=True, capture_output=True)
    out.with_suffix(".stdout.txt").write_text(result.stdout)
    out.with_suffix(".stderr.txt").write_text(result.stderr)
    receipt = {
        "argv": arguments,
        "returncode": result.returncode,
        "seconds": time.monotonic() - started,
        "stdout_sha256": digest(out.with_suffix(".stdout.txt")),
        "stderr_sha256": digest(out.with_suffix(".stderr.txt")),
    }
    publish(out.with_suffix(".json"), receipt)
    return receipt


def validate() -> Path:
    registry = verify_registry()
    out = ROOT / "test_receipts" / unique()
    out.mkdir()
    pytest = [
        ".venv/bin/python",
        "-m",
        "pytest",
        "tests/track2_rapid_v1",
        *["tests/track2_stage35_v5/test_next_valid_execution.py::" + n for n in V5_TESTS],
        "-q",
    ]
    tests = checked_command(pytest, out / "pytest")
    ruff = checked_command(
        [
            ".venv/bin/ruff",
            "check",
            "src/lstm_data/trading/track2/rapid_v1",
            "tests/track2_rapid_v1",
            "--select",
            "E,F,I",
        ],
        out / "ruff",
    )
    types = checked_command(
        [
            ".venv/bin/pyright",
            "src/lstm_data/trading/track2/rapid_v1",
            "tests/track2_rapid_v1",
            "--pythonpath",
            ".venv/bin/python",
            "--outputjson",
        ],
        out / "types",
    )
    status = "PASS" if all(x["returncode"] == 0 for x in (tests, ruff, types)) else "HOLD"
    publish(
        out / "VALIDATION_RECEIPTS.json",
        {
            "status": status,
            "registry": registry["identity"],
            "code": code_identity(),
            "test_sources": {str(p): digest(p) for p in Path("tests/track2_rapid_v1").glob("*.py")},
            "commands": [tests, ruff, types],
        },
    )
    print(status, out, flush=True)
    if status != "PASS":
        raise RuntimeError("VALIDATION_FAILED")
    return out


def validation_gate() -> dict:
    registry = verify_registry()
    candidates = []
    for p in (ROOT / "test_receipts").glob("*/VALIDATION_RECEIPTS.json"):
        r = json.loads(p.read_text())
        if (
            r["registry"] == registry["identity"]
            and r["status"] == "PASS"
            and r["code"] == code_identity()
        ):
            if any(digest(Path(k)) != v for k, v in r["test_sources"].items()):
                continue
            for name, command in zip(("pytest", "ruff", "types"), r["commands"], strict=True):
                if command["returncode"] != 0 or any(
                    digest(p.parent / f"{name}.{stream}.txt") != command[f"{stream}_sha256"]
                    for stream in ("stdout", "stderr")
                ):
                    raise ValueError("FAILED_OR_DRIFTED_TEST_GATE")
            candidates.append((p, r))
    if not candidates:
        raise PermissionError("CURRENT_TEST_RUFF_TYPE_GATE_REQUIRED")
    p, r = candidates[-1]
    return {"path": str(p), "sha256": digest(p), "registry": registry["identity"]}


def run_window(
    cache: FeatureCache, first: str, last: str, run_root: Path, resume: Path | None = None
) -> tuple[dict, FastEngine]:
    started = time.monotonic()
    cpu = time.process_time()
    engine = FastEngine(cache, first, last)
    engine.checkpoint_dir = run_root / "states"
    if resume is not None:
        restore_state(resume, engine)
    result = engine.run()
    info = {
        "first": first,
        "last": last,
        "PID": os.getpid(),
        "wall_seconds": time.monotonic() - started,
        "CPU_seconds": time.process_time() - cpu,
        "process_peak_memory_bytes": peak_memory_bytes(),
        "registry": engine.registry["identity"],
        "cache_identity": cache.manifest["identity"],
        "financial_result": result,
        "new_source_network_requests": 0,
    }
    destination = run_root / "results"
    if destination.exists():
        destination = run_root / ("results_postprocess_recovery_" + unique())
    outputs = write_results(engine, destination, info)
    receipt = {
        **info,
        **outputs,
        "results": str(destination),
        "result_manifest_sha256": digest(destination / "manifest.json"),
    }
    if footprint(run_root) > 500 * 2**20:
        raise RuntimeError("RUN_TOTAL_HARD_SIZE_LIMIT")
    publish(run_root / ("WINDOW_OUTPUTS_" + unique() + ".json"), receipt)
    return receipt, engine


def pilots(cache: FeatureCache) -> Path:
    gate = validation_gate()
    out = ROOT / "runs" / ("pilots_" + unique())
    out.mkdir(parents=True)
    rows = []
    for first, last in PILOTS:
        root = out / first
        root.mkdir()
        receipt, _ = run_window(cache, first, last, root)
        rows.append(receipt)
        print(
            "pilot", first, receipt["status_counts"], round(receipt["wall_seconds"], 2), flush=True
        )
    parity = source_kernel_parity(out / "V5_SOURCE_KERNEL_PARITY.json")
    passed = all(set(row["status_counts"]) <= {"COMPLETE", "NO_TRADES"} for row in rows)
    body = {
        "status": "PASS" if passed else "HOLD",
        "registry": verify_registry()["identity"],
        "cache": cache.manifest["identity"],
        "test_gate": gate,
        "windows": rows,
        "kernel_parity_sha256": digest(out / "V5_SOURCE_KERNEL_PARITY.json"),
        "parity_status": parity["status"],
    }
    publish(out / "PILOT_GATE.json", body)
    if not passed:
        raise RuntimeError("PILOT_FINANCIAL_HOLD")
    return out


def benchmark(cache: FeatureCache) -> Path:
    gate = validation_gate()
    out = ROOT / "runs" / ("benchmark_" + unique())
    out.mkdir(parents=True)
    rows = []
    for label, first, last in [
        ("day", "2021-01-04", "2021-01-04"),
        ("week", "2021-01-04", "2021-01-08"),
        ("month", "2021-01-04", "2021-01-29"),
    ]:
        root = out / label
        root.mkdir()
        r, _ = run_window(cache, first, last, root)
        rows.append({"label": label, **r})
        print("benchmark", label, round(r["wall_seconds"], 3), r["output_bytes"], flush=True)
    month = rows[-1]
    projection = month["wall_seconds"] * 1005 / month["financial_result"]["days"]
    passed = projection < 3600 and all(
        set(r["status_counts"]) <= {"COMPLETE", "NO_TRADES"} for r in rows
    )
    publish(
        out / "BENCHMARK_GATE.json",
        {
            "status": "PASS" if passed else "HOLD_REDESIGN_REQUIRED",
            "registry": verify_registry()["identity"],
            "cache": cache.manifest["identity"],
            "test_gate": gate,
            "measurements": rows,
            "four_year_projection_seconds": projection,
            "financial_runtime_hard_projection_seconds": 3600,
            "not_actual_full_runtime": True,
        },
    )
    if not passed:
        raise RuntimeError("BENCHMARK_REDESIGN_REQUIRED")
    return out


def full_gate(cache: FeatureCache) -> dict:
    test = validation_gate()
    identity = verify_registry()["identity"]
    found = {}
    for name in ("PILOT_GATE.json", "BENCHMARK_GATE.json"):
        for p in sorted((ROOT / "runs").glob("*/" + name)):
            r = json.loads(p.read_text())
            if (
                r["registry"] == identity
                and r["cache"] == cache.manifest["identity"]
                and r["status"] == "PASS"
            ):
                rows = r.get("windows", r.get("measurements", []))
                if any(
                    digest(Path(row["results"]) / "manifest.json") != row["result_manifest_sha256"]
                    for row in rows
                ):
                    raise ValueError("PILOT_OUTPUT_DRIFT")
                if name == "PILOT_GATE.json":
                    if tuple((row["first"], row["last"]) for row in rows) != PILOTS:
                        raise ValueError("PILOT_SCOPE_DRIFT")
                    parity = p.parent / "V5_SOURCE_KERNEL_PARITY.json"
                    if (
                        digest(parity) != r["kernel_parity_sha256"]
                        or json.loads(parity.read_text())["status"] != "PASS"
                    ):
                        raise ValueError("SOURCE_KERNEL_PARITY_DRIFT")
                elif len(rows) != 3 or r["four_year_projection_seconds"] >= 3600:
                    raise ValueError("BENCHMARK_GATE")
                for row in rows:
                    base = Path(row["results"])
                    manifest = json.loads((base / "manifest.json").read_text())
                    if any(digest(base / f) != h for f, h in manifest["files"].items()):
                        raise ValueError("PILOT_MANIFEST_FILE_DRIFT")
                    for s in IDS:
                        summary = json.loads(
                            (Path(row["results"]) / s / "summary.json").read_text()
                        )
                        if (
                            summary["status"] not in ("COMPLETE", "NO_TRADES")
                            or float(summary["balance_residual_USD"]) > 1e-8
                        ):
                            raise ValueError("PILOT_ACCOUNT_GATE")
                found[name] = {"path": str(p), "sha256": digest(p)}
    if len(found) != 2:
        raise PermissionError("ALL_FIVE_PILOTS_AND_BENCHMARK_REQUIRED")
    return {
        "tests": test,
        **found,
        "registry": identity,
        "scope": (
            "Owner-authorized 18 direction-only defaults; no neural, sensitivity, or Stage 6 run."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "list",
            "freeze",
            "prepare",
            "validate",
            "pilot",
            "benchmark",
            "screen",
            "resume",
            "verify",
            "report",
        ],
    )
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--run", type=Path)
    parser.add_argument("--reason", default="initial implementation before outcomes")
    args = parser.parse_args()
    if args.command == "list":
        print("\n".join(IDS))
        return
    if args.command == "freeze":
        print(freeze_registry(args.reason)["identity"])
        return
    if args.command == "validate":
        print(validate())
        return
    if args.command == "prepare":
        print(build_cache())
        return
    if args.command in ("verify", "report"):
        if args.run is None:
            parser.error("--run required")
        manifest = json.loads((args.run / "manifest.json").read_text())
        if tuple(manifest["strategy_IDs"]) != IDS:
            raise ValueError("EIGHTEEN_OUTPUT_IDS")
        bad = [p for p, h in manifest["files"].items() if digest(args.run / p) != h]
        if bad:
            raise ValueError("OUTPUT_DRIFT:" + str(bad[:3]))
        print("VERIFIED", manifest["status_counts"], footprint(args.run))
        return
    if args.cache is None:
        parser.error("--cache required")
    cache = FeatureCache(args.cache)
    # A single process lock prevents accidental duplicate financial screens.
    lock_path = ROOT / "engine.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == "pilot":
            print(pilots(cache))
            return
        if args.command == "benchmark":
            print(benchmark(cache))
            return
        gate = full_gate(cache)
        if args.command == "screen":
            if not args.run_id:
                parser.error("--run-id required")
            if not args.run_id.replace("-", "").replace("_", "").isalnum():
                parser.error("--run-id must be alphanumeric with optional hyphen or underscore")
            root = ROOT / "runs" / args.run_id
            root.mkdir(parents=True, exist_ok=False)
            publish(root / "ADMISSION.json", gate)
            publish(
                root / "RUNNING.json",
                {
                    "PID": os.getpid(),
                    "registry": gate["registry"],
                    "cache": cache.manifest["identity"],
                    "argv": sys.argv,
                    "first": "2021-01-01",
                    "last": "2024-12-31",
                },
            )
            preserve_check(root / "FROZEN_PRE_SCREEN.json")
            result, _ = run_window(cache, "2021-01-01", "2024-12-31", root)
        else:
            if args.run is None:
                parser.error("--run required")
            root = args.run
            if list(root.glob("RUN_COMPLETION_*.json")):
                raise FileExistsError("COMPLETE_RUN_DO_NOT_RERUN;use verify/report")
            states = sorted((root / "states").glob("*.json.gz"))
            if not states:
                raise ValueError(
                    "NO_VALID_RESUME_FRONTIER;use new unique run only after inspection"
                )
            publish(
                root / ("RESUME_" + unique() + ".json"),
                {"state": str(states[-1]), "state_sha256": digest(states[-1]), "gate": gate},
            )
            result, _ = run_window(cache, "2021-01-01", "2024-12-31", root, states[-1])
        post = root / ("FROZEN_POST_SCREEN_" + unique() + ".json")
        preserve_check(post)
        result["frozen_post_sha256"] = digest(post)
        result["total_run_bytes_before_completion"] = footprint(root)
        publish(root / ("RUN_COMPLETION_" + unique() + ".json"), result)
        print("SCREEN_FINISHED", result["status_counts"], result["results"], flush=True)


if __name__ == "__main__":
    main()
