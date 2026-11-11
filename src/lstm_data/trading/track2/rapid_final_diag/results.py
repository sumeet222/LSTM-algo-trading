"""Fail-closed exact-control checks and compact, auditable funded tables."""

import csv
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_exit_audit.io import column, table
from ..rapid_v1.paths import digest, publish
from ..rapid_v2_diagnostics.report import csv_write
from ..rapid_v3_dynamic.report import result_rows
from .engine import DiagnosticBatch
from .policy import D
from .provenance import FUNDED

CONTROLS = {s + "_CONTROL": s + "_CONSERVATIVE" for s in ("M04", "R01", "M01", "M05", "M03", "R07")}
CONTROLS["R01_H100"] = "R01_STANDARD"


def floats(rows: list[dict]) -> list[dict]:
    return [{k: float(v) if isinstance(v, D) else v for k, v in row.items()} for row in rows]


def parity(engine: DiagnosticBatch, current: list[dict]) -> dict:
    """Every daily economic/exposure column and terminal count; no partial-period waiver."""
    old = pd.read_parquet(FUNDED / "DAILY_NAV.parquet")
    with (FUNDED / "V3_ALL54_SUMMARY.csv").open() as f:
        summaries = {r["strategy_id"] + "_" + r["regime"]: r for r in csv.DictReader(f)}
    fields = (
        "nav",
        "cash",
        "restricted",
        "claims",
        "physical_value",
        "special",
        "virtual_gross",
        "commission",
        "friction",
        "borrow",
        "funding",
        "gross_dollar_minutes",
        "gross_NAV_minutes",
        "spendable_cash_NAV_minutes",
        "RTH_minutes",
    )
    maxima = {}
    for key, prior in CONTROLS.items():
        sid, regime = prior.split("_", 1)
        p = table(old.loc[(column(old, "strategy_id") == sid) & (column(old, "regime") == regime)])
        records = engine.daily_rows[key]
        if list(column(p, "date")) != [r["date"] for r in records]:
            raise ValueError("CONTROL_DAILY_CENSUS " + key)
        for name in fields:
            a = column(p, name).to_numpy(float)
            b = np.asarray([float(r[name]) for r in records])
            tolerance = 1e-7 if name != "gross_dollar_minutes" else 1e-5
            if not np.allclose(a, b, atol=tolerance, rtol=1e-12, equal_nan=False):
                first = int(np.flatnonzero(~np.isclose(a, b, atol=tolerance, rtol=1e-12))[0])
                raise ValueError(f"CONTROL_DAILY_DRIFT {key} {name} {records[first]['date']}")
            maxima[key + ":" + name] = float(np.max(abs(a - b)))
        r = next(r for r in current if r["strategy_id"] + "_" + r["variant"] == key)
        for name, expected in summaries[prior].items():
            if name in ("variant", "regime", "hold_reasons", "gross_basis") or name not in r:
                continue
            value = r[name]
            if expected == "" and value is None:
                continue
            if isinstance(value, (int, float, D)) and not isinstance(value, bool):
                if not np.isclose(float(value), float(expected), atol=1e-7, rtol=1e-12):
                    raise ValueError(f"CONTROL_SUMMARY_DRIFT {key} {name} {value} {expected}")
            elif str(value) != expected:
                raise ValueError(f"CONTROL_SUMMARY_TEXT_DRIFT {key} {name}")
    # The requested M01 rule is already implemented in V3: assert its identity.
    for x, y in zip(engine.daily_rows["M01_CONTROL"], engine.daily_rows["M01_WEAK2"], strict=True):
        if any(x[k] != y[k] for k in fields):
            raise ValueError("M01_EXISTING_TWO_CHECK_IDENTITY")
    return {
        "status": "PASS",
        "controls": len(CONTROLS),
        "daily_rows": 1005 * len(CONTROLS),
        "absolute_tolerance_USD": 1e-7,
        "relative_rendering_tolerance": 1e-12,
        "max_abs_difference_by_field": maxima,
        "M01": "IDENTICAL_EXISTING_TWO_CHECK_RULE",
    }


def publish_results(engine: DiagnosticBatch, directory: Path, require_archive: bool) -> dict:
    rows = result_rows(engine)
    if require_archive:
        check = parity(engine, rows)
    else:
        check = {"status": "DIAGNOSTIC_PILOT_ONLY"}
    directory.mkdir(exist_ok=False, parents=True)
    publish(directory / "CONTROL_PARITY.json", check)
    reasons, annual, daily, trades, physical, legs, reserves, risks = ([] for _ in range(8))
    for a, row in zip(engine.dynamic_accounts, rows, strict=True):
        if not hasattr(a, "completed_records"):
            raise TypeError("DIAGNOSTIC_EXPORT_ACCOUNT")
        # The actual ledger class is narrowed explicitly below for static checks.
        from .book import DiagnosticLedger

        if not isinstance(a, DiagnosticLedger):
            raise TypeError("DIAGNOSTIC_EXPORT_ACCOUNT")
        key = {"case": a.arm, "strategy_id": row["strategy_id"]}
        row.update(a.monitor_totals)
        row["arithmetic_residual_USD"] = (
            row["initial_cash_USD"]
            + row["gross_signed_price_PnL_USD"]
            + row["gross_action_value_USD"]
            - row["total_cost_USD"]
            - a.nav()
        )
        for cause, item in sorted(a.by_reason.items()):
            reasons.append(
                {**key, "cause": cause, **item["totals"], "triggers": str(item["triggers"])}
            )
        annual.extend(
            {**key, "axis": k.split("|", 1)[0], "label": k.split("|", 1)[1], **v}
            for k, v in sorted(a.breakdown.items())
        )
        annual.extend(
            {**key, "axis": "rejection", "label": k, "count": v}
            for k, v in sorted(a.rejected.items())
        )
        daily.extend({**key, **r} for r in engine.daily_rows[a.arm])
        trades.extend(a.completed_records)
        physical.extend(a.physical_records)
        legs.extend(a.exit_tape)
        reserves.extend(a.entry_reserves)
        risks.extend({**key, **r} for r in a.risk_samples)
    csv_write(directory / "FUNDED_TARGETED_RESULTS.csv", rows)
    csv_write(directory / "EXIT_REASONS.csv", reasons)
    csv_write(directory / "ANNUAL_AND_CAUSAL_DIAGNOSTICS.csv", annual)
    csv_write(directory / "R01_ENTRY_RESERVES.csv", reserves)
    csv_write(directory / "RISK_BREACH_SAMPLES.csv", risks)
    for name, records in (
        ("DAILY_NAV", daily),
        ("COMPLETED_COHORTS", trades),
        ("PHYSICAL_FILLS", physical),
        ("ACTUAL_EXIT_PORTIONS", legs),
    ):
        # Link arrays are redundant with the shared physical fills and exit tape.
        if name == "COMPLETED_COHORTS":
            records = [
                {k: v for k, v in r.items() if k != "physical_or_internal_order_links"}
                for r in records
            ]
        pd.DataFrame(floats(records)).to_parquet(
            directory / (name + ".parquet"), index=False, compression="zstd"
        )
    size = sum(p.stat().st_size for p in directory.iterdir())
    if size > 100_000_000:
        raise ValueError("STORAGE_BUDGET_EXCEEDED")
    receipt = {
        "status_counts": {
            s: sum(r["status"] == s for r in rows) for s in {r["status"] for r in rows}
        },
        "accounts": len(rows),
        "days": engine.days_completed,
        "cohort_rows": len(trades),
        "exit_portions": len(legs),
        "physical_fill_rows": len(physical),
        "bytes": size,
        "source_reads": engine.market.reads,
        "files": {p.name: digest(p) for p in sorted(directory.iterdir())},
    }
    publish(directory / "FUNDED_MANIFEST.json", receipt)
    return receipt
