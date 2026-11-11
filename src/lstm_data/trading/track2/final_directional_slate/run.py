"""Bounded sequential population runs with a shared chronological market source."""

import argparse
import fcntl
import gzip
import json
import subprocess
import time
from dataclasses import fields
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_final_diag.engine import DiagnosticBatch
from ..rapid_v1.cli import peak_memory_bytes
from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.state import decode
from ..rapid_v2_diagnostics.engine import Batch
from ..rapid_v2_diagnostics.report import csv_write, summarize
from ..rapid_v2_diagnostics.state import STATE, binding
from ..rapid_v2_diagnostics.state import snapshot as fixed_snapshot
from ..rapid_v2_diagnostics.variants import Case
from ..rapid_v3_dynamic.state import FIELDS
from ..rapid_v3_dynamic.state import snapshot as dynamic_snapshot
from .common import CODE, POLICIES, ROOT, load, verify_inputs
from .engines import create
from .ledger import DynamicLedger, FixedLedger
from .risk_inputs import RiskInputs


def overlay_hashes() -> dict:
    return {str(p): digest(p) for p in sorted(CODE.glob("*.py"))}


def seal() -> None:
    if load(ROOT / "PRE_OVERLAY_TEST_GATE.json")["status"] != "PASS":
        raise ValueError("OWNED_TEST_HOLD")
    if load(ROOT / "RISK_INPUT_READINESS.json")["status"] != "PASS":
        raise ValueError("INPUT_READINESS_HOLD")
    verify_inputs()
    body = {
        "five_registry_sha256": digest(ROOT / "FIVE_ALGORITHM_REGISTRY.json"),
        "selection_sha256": digest(ROOT / "SELECTION_RECEIPT.json"),
        "risk_cache_sha256": digest(ROOT / "SIGN_INDEPENDENT_RISK_INPUTS.npz"),
        "code": overlay_hashes(),
        "test_receipt_sha256": digest(ROOT / "PRE_OVERLAY_TEST_GATE.json"),
        "opportunity_receipt_sha256": digest(ROOT / "OPPORTUNITY_READY_GATE.json"),
        "pilots": ["2024-11-18", "2024-12-02"],
        "arms": ["EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"],
        "populations": ["MATCHED", "ATTAINABLE"],
        "equal_attainable": "REUSE_EXACT_ARCHIVED_CANDIDATE",
        "no_new_policy_or_threshold": True,
        "maximum_active_overlay_books": 12,
        "output_limit": 200_000_000,
    }
    body["identity"] = canonical(body)
    publish(ROOT / "OVERLAY_RUN_REGISTRY.json", body)


def ready() -> dict:
    spec = load(ROOT / "OVERLAY_RUN_REGISTRY.json")
    if (
        spec["five_registry_sha256"] != digest(ROOT / "FIVE_ALGORITHM_REGISTRY.json")
        or spec["test_receipt_sha256"] != digest(ROOT / "PRE_OVERLAY_TEST_GATE.json")
        or spec["opportunity_receipt_sha256"] != digest(ROOT / "OPPORTUNITY_READY_GATE.json")
        or spec["code"] != overlay_hashes()
        or spec["risk_cache_sha256"] != digest(ROOT / "SIGN_INDEPENDENT_RISK_INPUTS.npz")
        or spec["selection_sha256"] != digest(ROOT / "SELECTION_RECEIPT.json")
    ):
        raise ValueError("OVERLAY_CODE_SOURCE_OR_SELECTION_DRIFT")
    verify_inputs()
    return spec


def setup(pop: str, first="2021-01-01", last="2024-12-31", unit=False):
    spec = ready()
    cache = FeatureCache(
        Path(
            load(ROOT / "FIVE_ALGORITHM_REGISTRY.json").get(
                "rapid_cache",
                "trading/track2/rapid_v1/cache/49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93",
            )
        )
    )
    risk = RiskInputs()
    if unit:

        class UnitInputs(RiskInputs):
            def multiplier(self, origin, decision, ticker, arm, population):
                from decimal import Decimal

                return Decimal(1)

        risk = UnitInputs()
    fixed, dynamic, mapping = create(cache, risk, pop, first, last, equal_only=unit)
    for e in (fixed, dynamic):
        e.variant_registry = spec["identity"]
    return fixed, dynamic, mapping


def envelope(fixed, dynamic) -> dict:
    return {"fixed": fixed_snapshot(fixed), "dynamic": dynamic_snapshot(dynamic)}


def checkpoint(path: Path, fixed, dynamic) -> None:
    body = envelope(fixed, dynamic)
    blob = gzip.compress(
        json.dumps({"body": body, "sha256": canonical(body)}, sort_keys=True).encode(),
        compresslevel=3,
        mtime=0,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(blob)


def restore(path: Path, fixed, dynamic) -> None:
    outer = json.loads(gzip.decompress(path.read_bytes()))
    body = outer["body"]
    if canonical(body) != outer["sha256"]:
        raise ValueError("CHECKPOINT_HASH")
    for e, name, kind, fs in (
        (fixed, "fixed", FixedLedger, STATE),
        (dynamic, "dynamic", DynamicLedger, FIELDS),
    ):
        b = body[name]
        if b["binding"] != binding(e):
            raise ValueError("CHECKPOINT_REGISTRY_OR_CENSUS")
        values = decode(b["state"])
        accounts = decode(b["accounts"])
        if not isinstance(values, dict) or set(values) != set(fs) or not isinstance(accounts, list):
            raise ValueError("CHECKPOINT_SCHEMA")
        for k in fs:
            setattr(e, k, values[k])
        restored = []
        for a in accounts:
            if not isinstance(a, dict) or set(a) != {f.name for f in fields(kind)}:
                raise ValueError("CHECKPOINT_LEDGER_FIELDS")
            item = object.__new__(kind)
            for k, v in a.items():
                object.__setattr__(item, k, v)
            item.reconcile()
            restored.append(item)
        if [a.arm for a in restored] != list(e.case_by_key):
            raise ValueError("CHECKPOINT_ACCOUNT_ORDER")
        if name == "dynamic":
            e.dynamic_accounts = restored
        e.fast_accounts = list(restored)
        e.accounts = list(restored)
        e.market.first = (date.fromisoformat(e.last_completed) + timedelta(days=1)).isoformat()
        e.risk_cache.clear()
        if any(
            len(r) != e.days_completed or r[-1]["date"] != e.last_completed
            for r in e.daily_rows.values()
        ):
            raise ValueError("CHECKPOINT_DAILY_FRONTIER")


def pilot() -> None:
    start = time.monotonic()
    fixed, dynamic, mapping = setup("MATCHED", "2024-11-18", unit=True)
    canonical_dynamic = DiagnosticBatch(dynamic.cache, "2024-11-18", "2024-12-31")
    canonical_fixed = Batch(
        fixed.cache,
        "2024-11-18",
        "2024-12-31",
        (Case("M04", "T480", __import__("decimal").Decimal(1), 480, "minutes"),),
    )
    fixed.market.last = "2024-12-02"
    for day in fixed.market.days():
        fixed.tick_day(day)
        dynamic.tick_day(day)
        canonical_fixed.tick_day(day)
        canonical_dynamic.tick_day(day)
    previous = {"F1": "R01_CONTROL", "F2": "R01_V20", "F4": "R07_DAILY2", "F5": "M05_EVENT2"}
    for e in (fixed, dynamic):
        for a in e.fast_accounts:
            fid, _, _ = mapping[a.arm]
            reference = (
                canonical_fixed.daily_rows["M04_T480"]
                if fid == "F3"
                else canonical_dynamic.daily_rows[previous[fid]]
            )
            for x, y in zip(e.daily_rows[a.arm], reference, strict=True):
                for name in (
                    "nav",
                    "cash",
                    "claims",
                    "restricted",
                    "physical_value",
                    "special",
                    "virtual_gross",
                    "commission",
                    "friction",
                    "borrow",
                    "funding",
                    "gross_dollar_minutes",
                    "gross_NAV_minutes",
                ):
                    if not np.isclose(float(x[name]), float(y[name]), rtol=1e-12, atol=1e-7):
                        raise ValueError("UNIT_G1_CANONICAL_PARITY " + fid + " " + name)
    # Actual varied-risk books and their same-code restart are independently checked.
    del fixed, dynamic, canonical_fixed, canonical_dynamic
    one, two, _ = setup("MATCHED", "2024-11-18")
    one.market.last = "2024-12-02"
    replay_days = list(one.market.days())
    for day in replay_days[:2]:
        one.tick_day(day)
        two.tick_day(day)
    path = ROOT / "pilot_checkpoint.json.gz"
    checkpoint(path, one, two)
    for day in replay_days[2:]:
        one.tick_day(day)
        two.tick_day(day)
    if any(e.account_holds for e in (one, two)) or any(
        a.nav() is None or a.unpriced_special for e in (one, two) for a in e.fast_accounts
    ):
        raise ValueError("PILOT_ECONOMIC_SOURCE_HOLD")
    source_reads = list(one.market.reads)
    expected = canonical(envelope(one, two))
    del one, two
    resumed_fixed, resumed_dynamic, _ = setup("MATCHED", "2024-11-18")
    restore(path, resumed_fixed, resumed_dynamic)
    for day in replay_days[2:]:
        resumed_fixed.tick_day(day)
        resumed_dynamic.tick_day(day)
    if expected != canonical(envelope(resumed_fixed, resumed_dynamic)):
        raise ValueError("EXACT_RESTART_DIVERGENCE")
    elapsed = time.monotonic() - start
    publish(
        ROOT / "OVERLAY_PILOT_GATE.json",
        {
            "status": "PASS",
            "source_sessions": len(replay_days),
            "g1_candidates_checked": len(mapping),
            "restart": "EXACT_FULL_STATE_EQUAL",
            "known_open_inventory_at_slice_end": "RETAINED_NOT_FORCED_CLOSED",
            "elapsed_seconds": elapsed,
            "projection_two_full_passes_seconds": elapsed / 4 / len(replay_days) * 2010,
            "source_reads": source_reads,
        },
    )


def emit(directory: Path, fixed, dynamic, mapping: dict) -> dict:
    directory.mkdir(exist_ok=False)
    results = []
    daily = []
    trades = []
    physical = []
    reasons = []
    attribution = []
    exits = []
    for e in (fixed, dynamic):
        for a in e.fast_accounts:
            r = summarize(e, a)
            fid, pop, arm = mapping[a.arm]
            if r["status"] == "HOLD":
                raise ValueError("MATERIAL_FUNDED_HOLD " + a.arm + " " + r["hold_reasons"])
            r.update(candidate=fid, label=POLICIES[fid]["label"], population=pop, arm=arm)
            if isinstance(a, DynamicLedger):
                r.update(
                    risk_closed_cohorts=int(a.totals.get("risk_closed", 0)),
                    name_breach_decisions=a.causes["observed:NAME_CAP"],
                    vintage_breach_decisions=a.causes["observed:VINTAGE_CAP"],
                )
                for cause, item in a.by_reason.items():
                    reasons.append(
                        {
                            "candidate": fid,
                            "population": pop,
                            "arm": arm,
                            "cause": cause,
                            **item["totals"],
                        }
                    )
            nav = 100000.0
            for year in ("2021", "2022", "2023", "2024"):
                end = next(x["nav"] for x in reversed(e.daily_rows[a.arm]) if x["date"][:4] == year)
                r["return_" + year] = float(end) / nav - 1
                nav = float(end)
            results.append(r)
            daily.extend(
                {"candidate": fid, "population": pop, "arm": arm, **x} for x in e.daily_rows[a.arm]
            )
            for row in a.completed_records:
                trades.append(
                    {
                        "candidate": fid,
                        "population": pop,
                        "arm": arm,
                        **{
                            k: float(v) if hasattr(v, "as_tuple") else v
                            for k, v in row.items()
                            if k != "physical_or_internal_order_links"
                        },
                    }
                )
            physical.extend(
                {
                    "candidate": fid,
                    "population": pop,
                    "arm": arm,
                    **{k: float(v) if hasattr(v, "as_tuple") else v for k, v in row.items()},
                }
                for row in a.physical_records
            )
            exits.extend(
                {"candidate": fid, "population": pop, "arm": arm, **x} for x in a.exit_tape
            )
            attribution.extend(
                {
                    "candidate": fid,
                    "population": pop,
                    "arm": arm,
                    "axis": k.split("|", 1)[0],
                    "label": k.split("|", 1)[1],
                    **v,
                }
                for k, v in a.breakdown.items()
            )
            attribution.extend(
                {
                    "candidate": fid,
                    "population": pop,
                    "arm": arm,
                    "axis": "rejection",
                    "label": k,
                    "count": v,
                }
                for k, v in a.rejected.items()
            )
    csv_write(directory / "RESULTS.csv", results)
    csv_write(directory / "EXIT_REASONS.csv", reasons)
    csv_write(directory / "ATTRIBUTION.csv", attribution)
    for name, rows in (
        ("DAILY_NAV", daily),
        ("COHORTS", trades),
        ("PHYSICAL_FILLS", physical),
        ("DYNAMIC_EXIT_PORTIONS", exits),
    ):
        frame = pd.DataFrame(
            [{k: float(v) if hasattr(v, "as_tuple") else v for k, v in x.items()} for x in rows]
        )
        frame.to_parquet(directory / (name + ".parquet"), index=False, compression="zstd")
    receipt = {
        "status": "COMPLETE",
        "accounts": len(results),
        "cohort_rows": len(trades),
        "maximum_ledger_residual": str(
            max(a.maximum_residual for e in (fixed, dynamic) for a in e.fast_accounts)
        ),
        "files": {p.name: digest(p) for p in sorted(directory.iterdir())},
    }
    publish(directory / "OUTPUT_MANIFEST.json", receipt)
    return receipt


def run(population: str, run_id: str, resume: Path | None) -> None:
    spec = ready()
    if load(ROOT / "OVERLAY_PILOT_GATE.json")["status"] != "PASS":
        raise ValueError("PILOT_HOLD")
    directory = ROOT / "runs" / run_id
    if resume is None:
        directory.mkdir(parents=True, exist_ok=False)
    elif not resume.is_relative_to(directory):
        raise ValueError("RESUME_LINEAGE")
    with (directory / "process.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        fixed, dynamic, mapping = setup(population)
        if resume is not None:
            restore(resume, fixed, dynamic)
        for day in fixed.market.days():
            if fixed.last_completed and day.date <= fixed.last_completed:
                continue
            fixed.tick_day(day)
            dynamic.tick_day(day)
            if fixed.days_completed % 100 == 0:
                print(
                    population,
                    fixed.days_completed,
                    day.date,
                    round(time.monotonic() - start, 1),
                    flush=True,
                )
            if day.date.endswith(("12-31", "12-30", "12-29")) and day.date == max(
                d for d in fixed.cache.by_date if d[:4] == day.date[:4]
            ):
                checkpoint(directory / "states" / (day.date + ".json.gz"), fixed, dynamic)
                size = sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
                if size > 200_000_000:
                    raise ValueError("OUTPUT_BUDGET_HOLD")
        output = emit(directory / "results", fixed, dynamic, mapping)
        publish(
            directory / "RUN_RECEIPT.json",
            {
                "status": "COMPLETE",
                "population": population,
                "registry": spec["identity"],
                "sessions": fixed.days_completed,
                "last_session": fixed.last_completed,
                "elapsed_seconds": time.monotonic() - start,
                "peak_RSS_bytes": peak_memory_bytes(),
                "source_reads": fixed.market.reads,
                "output": output,
                "resume_from": str(resume) if resume else None,
            },
        )


def checks() -> None:
    target = ROOT / "pre_overlay_validation"
    target.mkdir(exist_ok=False)
    commands = [
        [
            ".venv/bin/python",
            "-m",
            "pytest",
            "-q",
            "tests/track2_final_directional_slate",
            "tests/track2_rapid_v1",
            "tests/track2_rapid_v2",
            "tests/track2_rapid_v3",
            "tests/track2_rapid_final_diag",
        ],
        [
            ".venv/bin/ruff",
            "check",
            "--select",
            "E,F,I",
            str(CODE),
            "tests/track2_final_directional_slate",
        ],
        [
            ".venv/bin/pyright",
            "--pythonpath",
            ".venv/bin/python",
            str(CODE),
            "tests/track2_final_directional_slate",
        ],
    ]
    records = []
    for n, cmd in enumerate(commands):
        started = time.monotonic()
        p = subprocess.run(cmd, text=True, capture_output=True)
        (target / f"{n}.stdout").write_text(p.stdout)
        (target / f"{n}.stderr").write_text(p.stderr)
        records.append(
            {"argv": cmd, "returncode": p.returncode, "elapsed_seconds": time.monotonic() - started}
        )
    publish(
        ROOT / "PRE_OVERLAY_TEST_GATE.json",
        {
            "status": "PASS" if all(r["returncode"] == 0 for r in records) else "HOLD",
            "commands": records,
            "code": overlay_hashes(),
            "receipt_files": {p.name: digest(p) for p in target.iterdir()},
        },
    )
    if any(r["returncode"] for r in records):
        raise ValueError("OWNED_TEST_HOLD")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["checks", "seal", "pilot", "run"])
    p.add_argument("--population", choices=["MATCHED", "ATTAINABLE"], default="MATCHED")
    p.add_argument("--run-id", default="sizing-matched-20261110-r1")
    p.add_argument("--resume", type=Path)
    a = p.parse_args()
    if a.command == "checks":
        checks()
    elif a.command == "seal":
        seal()
    elif a.command == "pilot":
        pilot()
    else:
        run(a.population, a.run_id, a.resume)


if __name__ == "__main__":
    main()
