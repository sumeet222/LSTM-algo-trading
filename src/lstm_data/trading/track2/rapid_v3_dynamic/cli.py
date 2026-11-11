"""Freeze, validate, pilot and replay the fixed 54-case dynamic suite."""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from ..rapid_v1.cli import peak_memory_bytes, unique
from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.strategies import IDS
from ..rapid_v1.verification import preserve_check, source_kernel_parity
from ..rapid_v2_diagnostics.report import baseline_check
from ..rapid_v2_diagnostics.variants import FIRST, LAST
from .engine import DynamicBatch
from .policy import ADAPTERS, REGIMES, Case, D, case_axis
from .report import assess, emit, result_rows
from .state import restore, snapshot

ROOT = Path("trading/track2/rapid_v3_dynamic")
CODE = Path("src/lstm_data/trading/track2/rapid_v3_dynamic")
TESTS = Path("tests/track2_rapid_v3")
V1_BENCH = Path("trading/track2/rapid_v1/runs/benchmark_20261110T220133119214Z")
LIMIT = 200_000_000


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def code_hashes() -> dict:
    return {str(p): digest(p) for folder in (CODE, TESTS) for p in sorted(folder.glob("*.py"))}


def verify_parents() -> dict:
    b = load(ROOT / "PARENT_BOUNDARY.json")
    for path, (sha, mtime) in b["files"].items():
        p = Path(path)
        if digest(p) != sha or p.stat().st_mtime_ns != mtime:
            raise ValueError("V3_PROTECTED_PARENT_DRIFT:" + path)
    return b


def freeze(reason: str | None) -> None:
    b = verify_parents()
    initial = ROOT / "V3_EXPERIMENT_REGISTRY.json"
    if initial.exists():
        if not reason:
            raise FileExistsError(initial)
        body = load(initial)
        del body["registry_identity"]
        body["engineering_amendment"] = reason
        body["initial_registry_sha256"] = digest(initial)
        target = ROOT / "amendments" / (unique() + ".json")
    else:
        target = initial
        v1 = Path(b["V1_results"])
        old = load(v1 / "EXPERIMENT_REGISTRY.json")
        body = {
            "schema": "HF20_RAPID_V3_FIXED_DYNAMIC_1",
            "period": [FIRST, LAST],
            "strategy_ids": IDS,
            "adapters": ADAPTERS,
            "case_axis": [asdict(c) for c in case_axis()],
            "V1_direction_and_cost_registry": old,
            "parent_boundary_sha256": digest(ROOT / "PARENT_BOUNDARY.json"),
            "parent_initial_protected_sha256": digest(ROOT / "PARENT_PROTECTED_BEFORE.json"),
            "cache": b["cache"],
            "initial_cash_USD": 100000,
            "protocol_sha256": digest(ROOT / "V3_DYNAMIC_EXIT_PROTOCOL.md"),
            "mode_budgets": {
                "MICRO_PRO": "6 physical new orders/session",
                "RETAIL_CONSERVATIVE": "5 physical new orders/scan week",
            },
            "hard_limits": {
                "virtual_gross": 1,
                "absolute_physical_net": 1,
                "vintage": 0.20,
                "name_by_regime": {k: str(v[1]) for k, v in REGIMES.items()},
            },
            "tail_diagnostic": {
                "from": "sealed actual exit legs only",
                "horizons": [60, 240, "NEXT_FULL_SESSION"],
                "net_funding": False,
                "output_excluded_from_engine": True,
            },
            "admission": {
                "max_entry_delay_minutes": 10,
                "receipt_minutes": 2,
                "max_micro_scheduled_minutes": 780,
                "max_retail_sessions": 10,
                "end_cutoff": "Reject latest-entry maximum beyond 2024 by calendar.",
            },
            "bench_projection_ceiling_seconds": 1500,
            "hard_run_size_bytes": LIMIT,
        }
    body["code_and_test_hashes"] = code_hashes()
    body["registry_identity"] = canonical(body)
    publish(target, body)
    publish(target.with_suffix(".seal.json"), {"sha256": digest(target), "path": str(target)})
    print(target, body["registry_identity"], flush=True)


def registry() -> dict:
    base = ROOT / "V3_EXPERIMENT_REGISTRY.json"
    files = sorted(
        p for p in (ROOT / "amendments").glob("*.json") if not p.name.endswith(".seal.json")
    )
    current = files[-1] if files else base
    body = load(current)
    identity = body.pop("registry_identity")
    if digest(current) != load(current.with_suffix(".seal.json"))["sha256"] or (
        canonical(body) != identity
        or body["code_and_test_hashes"] != code_hashes()
        or body["protocol_sha256"] != digest(ROOT / "V3_DYNAMIC_EXIT_PROTOCOL.md")
        or body["parent_boundary_sha256"] != digest(ROOT / "PARENT_BOUNDARY.json")
    ):
        raise ValueError("V3_REGISTRY_DRIFT")
    if files:
        old = load(base)
        if body["initial_registry_sha256"] != digest(base) or any(
            body[k] != v
            for k, v in old.items()
            if k not in ("registry_identity", "code_and_test_hashes")
        ):
            raise ValueError("V3_AMENDMENT_POLICY_DRIFT")
    return {**body, "registry_identity": identity, "registry_path": str(current)}


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
        "tests/track2_rapid_v2",
        "tests/track2_rapid_v1",
        v5 + "test_wait_next_valid_and_nominal_lifetime",
        v5 + "test_open_exit_remains_without_expiry_and_partial_fees_accumulate",
        v5 + "test_later_open_cannot_rewrite_submission_or_predecision_state",
        v5 + "test_actual_pre_spinoff_share_cases_exact_without_tolerance_waiver",
        "tests/track2_stage35_v4/test_special_and_book.py",
        "tests/track2_stage35_completion_v3/test_event_and_book_integration.py"
        "::test_friday_monday_physical_net_short_borrow",
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


def build(reg: dict, first: str, last: str, legacy: bool = False) -> DynamicBatch:
    axis = (
        tuple(Case(s, "H100", D(1), 240, "minutes", D(".1")) for s in IDS)
        if legacy
        else case_axis()
    )
    e = DynamicBatch(FeatureCache(Path(reg["cache"])), first, last, axis, legacy)
    e.variant_registry = reg["registry_identity"]
    return e


def pilot(reg: dict) -> None:
    tests = require_validation(reg)
    out = ROOT / "pilots" / unique()
    out.mkdir(parents=True)
    expected = V1_BENCH / "month/results"
    old = load(expected / "manifest.json")
    seal = next(
        r for r in load(V1_BENCH / "BENCHMARK_GATE.json")["measurements"] if r["label"] == "month"
    )
    if digest(expected / "manifest.json") != seal["result_manifest_sha256"] or any(
        digest(expected / name) != sha for name, sha in old["files"].items()
    ):
        raise ValueError("V1_LEGACY_PILOT_PAYLOAD_DRIFT")
    legacy = build(reg, "2021-01-04", "2021-01-29", True)
    legacy.run()
    parity = baseline_check(legacy, result_rows(legacy), expected)
    source_kernel_parity(out / "AVGO_TWO_ACCOUNT_KERNEL.json")
    full = build(reg, "2021-01-04", "2021-01-29")
    runtime = full.run()
    # Save the pre-report state so final-lot bookkeeping cannot affect restart parity.
    short = build(reg, "2021-01-04", "2021-01-29")
    short.checkpoint_dir = out / "states"
    short.run(stop_after=4)
    checkpoint = out / "states/2021-01-07.json.gz"
    resumed = build(reg, "2021-01-04", "2021-01-29")
    restore(checkpoint, resumed)
    resumed.run()
    state_hash = canonical(snapshot(full))
    if canonical(snapshot(resumed)) != state_hash:
        raise ValueError("V3_RESTART_PARITY")
    rows = result_rows(full)
    projected = runtime["elapsed"] * 1005 / runtime["sessions"]
    actions = []
    for first, last in (
        ("2021-05-24", "2021-06-21"),
        ("2022-08-15", "2022-09-12"),
        ("2024-05-06", "2024-06-03"),
        ("2024-11-18", "2024-12-16"),
    ):
        fixture = build(reg, first, last)
        wall = fixture.run()
        r = result_rows(fixture)
        census = Counter(x["status"] for x in r)
        counts = Counter()
        for a in fixture.dynamic_accounts:
            counts.update(
                {
                    k: n
                    for k, n in a.stats.counts.items()
                    if any(s in k for s in ("OGN", "SPLIT", "DIVIDEND"))
                }
            )
        actions.append(
            {
                "first": first,
                "last": last,
                "census": dict(census),
                "actions": dict(counts),
                "seconds": wall["elapsed"],
                "source": fixture.market.reads,
                "holds": [
                    [x["strategy_id"], x["regime"], x["hold_reasons"]]
                    for x in r
                    if x["status"] == "HOLD"
                ],
                "maximum_residual": str(max(a.maximum_residual for a in fixture.dynamic_accounts)),
            }
        )
    observed = Counter(r["status"] for r in rows)
    result = {
        "status": "PASS"
        if not observed["HOLD"] and projected < 1500 and not any(x["holds"] for x in actions)
        else "HOLD",
        "registry": reg["registry_identity"],
        "tests_sha256": digest(tests),
        "legacy": parity,
        "benchmark": runtime,
        "projected_full_seconds": projected,
        "peak_RSS_bytes": peak_memory_bytes(),
        "dynamic_census": dict(observed),
        "holds": [
            [r["strategy_id"], r["regime"], r["hold_reasons"]]
            for r in rows
            if r["status"] == "HOLD"
        ],
        "restart_hash": state_hash,
        "AVGO_sha256": digest(out / "AVGO_TWO_ACCOUNT_KERNEL.json"),
        "action_windows": actions,
    }
    publish(out / "PILOT_GATE.json", result)
    print(out, result["status"], round(projected, 1), "projected seconds", flush=True)
    if result["status"] != "PASS":
        raise ValueError("V3_SOURCE_OR_RUNTIME_GATE_HOLD")


def require_pilot(reg: dict) -> Path:
    require_validation(reg)
    for p in reversed(sorted((ROOT / "pilots").glob("*/PILOT_GATE.json"))):
        gate = load(p)
        if gate["registry"] == reg["registry_identity"] and gate["status"] == "PASS":
            if digest(p.parent / "AVGO_TWO_ACCOUNT_KERNEL.json") != gate["AVGO_sha256"]:
                raise ValueError("V3_PILOT_SOURCE_RECEIPT_DRIFT")
            return p
    raise PermissionError("V3_SEALED_PILOT_REQUIRED")


def run_size(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def screen(reg: dict, run_id: str, resume: bool) -> None:
    if not re.fullmatch("[A-Za-z0-9_-]+", run_id):
        raise ValueError("INVALID_RUN_ID")
    gate = require_pilot(reg)
    parents = verify_parents()
    with (ROOT / "engine.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        out = ROOT / "runs" / run_id
        if not resume:
            out.mkdir(exist_ok=False, parents=True)
            publish(
                out / "START.json",
                {
                    "pid": os.getpid(),
                    "argv": sys.argv,
                    "registry": reg["registry_identity"],
                    "pilot_sha256": digest(gate),
                },
            )
        elif load(out / "START.json")["registry"] != reg["registry_identity"]:
            raise ValueError("V3_RESUME_REGISTRY")
        if (out / "V3_RUN_STATUS.json").exists():
            raise FileExistsError("IMMUTABLE_COMPLETED_RUN")
        e = build(reg, FIRST, LAST)
        e.checkpoint_dir = out / "states"
        if resume:
            p = max(e.checkpoint_dir.glob("*.json.gz"))
            restore(p, e)
            publish(out / ("RESUME_" + unique() + ".json"), {"state": str(p), "sha256": digest(p)})
        started = time.monotonic()
        try:
            runtime = e.run()
            if runtime["sessions"] != 1005 or runtime["last_session"] != LAST:
                raise ValueError("V3_INCOMPLETE_EVALUATION")
            funded = out / ("funded_" + unique())
            result = emit(e, funded, parents)
            after = out / ("PARENT_PROTECTED_AFTER_" + unique() + ".json")
            preserve_check(after)
            verify_parents()
            size = run_size(out)
            if size > LIMIT:
                raise ValueError("V3_STORAGE_LIMIT")
            publish(
                out / "V3_RUN_STATUS.json",
                {
                    "status": "PARTIAL" if result["status_counts"].get("HOLD") else "COMPLETE",
                    "cases": 54,
                    "status_counts": result["status_counts"],
                    "registry": reg["registry_identity"],
                    "source_months": e.market.reads,
                    "period": [FIRST, LAST],
                    "funded_directory": str(funded),
                    "funded_manifest_sha256": digest(funded / "FUNDED_OUTPUT_MANIFEST.json"),
                    "wall_seconds": time.monotonic() - started,
                    "peak_RSS_bytes": peak_memory_bytes(),
                    "new_bytes": size,
                    "protection_sha256": digest(after),
                    "ledger_residual_USD": result["maximum_ledger_residual_USD"],
                    **runtime,
                },
            )
            print(out, result["status_counts"], flush=True)
        except (ValueError, AssertionError) as error:
            publish(
                out / ("HOLD_" + unique() + ".json"),
                {
                    "error": str(error),
                    "committed_days": e.days_completed,
                    "frontier": e.last_completed,
                },
            )
            raise


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["freeze", "validate", "pilot", "screen", "resume", "assess"])
    p.add_argument("--amendment-reason")
    p.add_argument("--run-id")
    a = p.parse_args()
    if a.command == "freeze":
        freeze(a.amendment_reason)
        return
    r = registry()
    if a.command == "validate":
        validate(r)
    elif a.command == "pilot":
        pilot(r)
    else:
        if not a.run_id or not re.fullmatch("[A-Za-z0-9_-]+", a.run_id):
            p.error("Valid --run-id required")
        if a.command == "assess":
            root = ROOT / "runs" / a.run_id
            status = load(root / "V3_RUN_STATUS.json")
            funded = Path(status["funded_directory"])
            if digest(funded / "FUNDED_OUTPUT_MANIFEST.json") != status["funded_manifest_sha256"]:
                raise ValueError("FUNDED_REPORT_DRIFT")
            assess(funded, root / "offline_diagnostic", root / "V3_SCREENING_ASSESSMENT.md")
        else:
            screen(r, a.run_id, a.command == "resume")


if __name__ == "__main__":
    main()
