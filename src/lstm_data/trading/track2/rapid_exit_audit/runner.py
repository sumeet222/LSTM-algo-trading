"""Seal-verified all-account descriptive audit. No simulation or order API."""

import argparse
import gzip
import json
import os
import time
from collections import Counter
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_v1.cli import peak_memory_bytes
from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.registry import FORMULAS
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.strategies import IDS, SLOTS, mode
from ..rapid_v2_diagnostics.report import csv_write
from ..rapid_v3_dynamic.policy import ADAPTERS, EVENT, PRIORITY, RANKED, THRESHOLD
from .io import as_rows, column, csv_at, decimal_scalar, json_at, near, table
from .offline import LIMIT, clock, make_sample

ROOT = Path("trading/track2/rapid_exit_audit_v1")
D = Decimal


def check_inputs() -> dict:
    s = json_at(ROOT / "INPUT_SEAL.json")
    for name, spec in s["input_files"].items():
        p = Path(name)
        if digest(p) != spec["sha256"] or p.stat().st_mtime_ns != spec["mtime_ns"]:
            raise ValueError("EXIT_AUDIT_INPUT_DRIFT " + name)
    return s


def load_tape(s: dict) -> tuple[pd.DataFrame, dict]:
    funded = Path(s["funded"])
    m = json_at(funded / "FUNDED_OUTPUT_MANIFEST.json")
    if any(digest(funded / k) != sha for k, sha in m["files"].items()):
        raise ValueError("EXIT_AUDIT_FUNDED_DRIFT")
    tape = pd.read_parquet(funded / "SEALED_ACTUAL_EXIT_LEGS.parquet")
    if len(tape) != m["exit_legs"] or not set(column(tape, "strategy_id")) == set(IDS):
        raise ValueError("EXIT_EVENT_AXIS")
    if tape.duplicated().any():
        raise ValueError("DUPLICATE_EXIT_LEG")
    if (
        (column(tape, "effective") <= column(tape, "decision")).any()
        or (column(tape, "posted") < column(tape, "effective") + 3).any()
        or (column(tape, "quantity") == 0).any()
        or (column(tape, "effective") < column(tape, "entry")).any()
    ):
        raise ValueError("EXECUTED_EVENT_CLOCK_OR_QUANTITY")
    tape["leg_id"] = np.arange(len(tape), dtype=np.int64)
    return tape, m


def contracts() -> list[dict]:
    return [
        {
            "strategy_id": s,
            "mode": mode(s),
            "direction_rule": FORMULAS[s],
            "entry_slots": ",".join(str(x) for x in SLOTS[s]),
            "entry_cadence": "legal strategy slots, 6 new physical tickets/session"
            if s.startswith("M")
            else "first full ISO-week session, 5 physical tickets/week",
            "inputs_maturity": "received bar prefix; daily lookbacks end before current session",
            "exit_monitor": ADAPTERS[s],
            "monitor_cadence": (
                "legal micro slots; M07 same-clock score; M09 extra next-day open/first hour"
            )
            if s.startswith("M")
            else "10:30 each full XNYS session, decision after receipt",
            "exit_score": "saved aligned standardized score at submission; missing retained",
            "state_labels": "negative=reversed, [0,1)=weak, >=1=strong; these are descriptive bins",
            "reversal_trigger": f"aligned score<=-{max(1.0, THRESHOLD.get(s, 1.0))}; "
            + ("2 valid micro checks" if s.startswith("M") else "1 valid daily check")
            + ("; opposite top-four rank gate" if s in RANKED else ""),
            "weakening_trigger": f"aligned<=.5 entry and <{THRESHOLD.get(s, 1.0)}; "
            + ("leave top four; " if s in RANKED else "")
            + "minimum age 60m micro/one session retail",
            "event_resolution": ADAPTERS[s] if s in EVENT or s in ("M02", "M08", "R05") else "none",
            "trailing_stop": "2x entry v20 log units, favorable received-checkpoint peak; "
            "R05 hedged spread and R06 frozen factor hedge; causal support required",
            "cooldown": (
                "one entry opportunity after normal signal/event exit; none after risk/trail/max"
            ),
            "maximum": "780 scheduled minutes"
            if s.startswith("M")
            else "10 following sessions, same offset/clamp close",
            "regimes": ".85/10%,1/10%,1/15% entry fraction/name cap",
            "hard_caps": "20% vintage,100% virtual gross/net, own cash and restricted shorts",
            "timing": "2m receipt, entry expiry origin+10m, orders before bar, posted bar+3m",
            "exit_precedence": "mandatory account risk, then " + ",".join(PRIORITY),
            "source": "rapid_v1/strategies.py; rapid_v3_dynamic/policy.py; decisions.py; book.py",
        }
        for s in IDS
    ]


def reconcile(tape: pd.DataFrame, s: dict) -> list[dict]:
    f = Path(s["funded"])
    summary = csv_at(f / "V3_ALL54_SUMMARY.csv")
    daily = pd.read_parquet(f / "DAILY_NAV.parquet")
    envelope = json.loads(
        gzip.decompress((Path(s["run"]) / "states/2024-12-31.json.gz").read_bytes())
    )
    body = envelope["body"]
    if canonical(body) != envelope["sha256"]:
        raise ValueError("ORIGINAL_CHECKPOINT_CHECKSUM")
    state = dict(body["state"]["mapping"])
    if state["last_completed"] != "2024-12-31" or state["days_completed"] != 1005:
        raise ValueError("ORIGINAL_CHECKPOINT_FRONTIER")
    accounts = {dict(x["mapping"])["arm"]: x for x in body["accounts"]["items"]}
    c = clock()
    counts = {}
    for key, group in tape.groupby(["case", "lot"]):
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError("EXIT_GROUP_SCHEMA")
        case, lot = key
        g = table(group).sort_values(["effective", "posted"])
        rows = as_rows(g)
        risk = any(x.cause.startswith("RISK_") for x in rows)
        final = rows[-1].cause
        age = c.index(int(rows[-1].effective)) - c.index(int(rows[0].entry))
        counter = counts.setdefault(case, Counter())
        counter.update(
            {
                "cohorts": 1,
                "risk_closed_cohorts": int(risk),
                "risk_final_exits": int(final.startswith("RISK_")),
                "scheduled_final_exits": int(not final.startswith("RISK_")),
                "risk_before_240": int(risk and age < 240),
                "policy_before_240": int(not risk and age < 240),
            }
        )
    out = []
    for r in summary:
        case = r["strategy_id"] + "_" + r["regime"]
        saved = dict(accounts[case]["mapping"])
        initial = decimal_scalar(saved["initial"])
        cash = decimal_scalar(saved["cash"])
        claims = sum((decimal_scalar(v["items"][0]) for _, v in saved["claims"]["mapping"]), D(0))
        if (
            any(saved["quantity"]["array"])
            or saved["pending"]["mapping"]
            or saved["special_values"]["mapping"]
        ):
            raise ValueError("UNRESOLVED_TERMINAL_STATE")
        nav = cash + claims
        near(nav, D(r["final_NAV_USD"]), "BASE_NAV")
        cost = sum(
            D(r[k])
            for k in (
                "commission_USD",
                "assumed_spread_USD",
                "assumed_impact_USD",
                "borrow_USD",
                "funding_USD",
            )
        )
        net = D(r["gross_signed_price_PnL_USD"]) + D(r["gross_action_value_USD"]) - cost
        near(net, nav - initial, "BASE_MONEY")
        near(cash + claims, nav, "BASE_COMPONENTS")
        near(
            D(r["gross_winners_USD"]) + D(r["gross_losers_USD"]),
            D(r["gross_signed_price_PnL_USD"]),
            "BASE_GROSS_TAILS",
        )
        for k, value in counts[case].items():
            if int(r[k]) != value:
                raise ValueError("BASE_COUNT_" + case + "_" + k)
        near(D(r["cohorts_with_risk_fill"]), D(r["risk_closed_cohorts"]), "ANY_RISK")
        if int(r["early_exits"]) != 0:
            raise ValueError("UNEXPECTED_LEGACY_EARLY")
        d = table(
            daily[
                (column(daily, "strategy_id") == r["strategy_id"])
                & (column(daily, "regime") == r["regime"])
            ]
        )
        if len(d) != 1005 or not column(d, "status").eq("OBSERVED").all():
            raise ValueError("BASE_DAILY_FRONTIER")
        residual = column(d, "nav").to_numpy(float) - d[
            ["cash", "claims", "physical_value", "special"]
        ].to_numpy(float).sum(axis=1)
        if np.max(abs(residual)) > 1e-7:
            raise ValueError("BASE_DAILY_RESIDUAL")
        out.append(
            {
                "case": case,
                "status": "PASS",
                "net_USD": net,
                "terminal_NAV": nav,
                "terminal_claims": claims,
                "cash_bridge_residual": net - (nav - initial),
                "daily_max_residual": float(np.max(abs(residual))),
                "daily_rows": len(d),
                "exit_legs": int((column(tape, "case") == case).sum()),
                **counts[case],
            }
        )
    if len(out) != 54 or len({r["case"] for r in out}) != 54:
        raise ValueError("BASE_CASE_AXIS")
    return out


def stats(g: pd.DataFrame) -> dict:
    valid = column(g, "valid").to_numpy(bool)
    raw = column(g, "price_raw_to_raw").to_numpy(float)[valid]
    actual = column(g, "price_actual_exit_anchor").to_numpy(float)[valid]
    bps = column(g, "raw_bps").to_numpy(float)[valid]
    notional = column(g, "ref_notional").to_numpy(float)[valid]
    conditional = column(g, "conditional_standalone_net").to_numpy(float)[valid]
    finite = np.isfinite(conditional)
    n = len(raw)
    row = {
        "exits": len(g),
        "valid": n,
        "favorable": int(np.sum(raw > 0)),
        "unfavorable": int(np.sum(raw < 0)),
        "zero": int(np.sum(raw == 0)),
        "favorable_fraction": float(np.mean(raw > 0)) if n else None,
        "signed_raw_USD": float(raw.sum()) if n else None,
        "signed_actual_exit_anchor_USD": float(actual.sum()) if n else None,
        "missed_upside_USD": float(np.maximum(raw, 0).sum()) if n else None,
        "avoided_loss_USD": float(np.maximum(-raw, 0).sum()) if n else None,
        "mean_USD": float(raw.mean()) if n else None,
        "equal_leg_mean_bps": float(bps.mean()) if n else None,
        "notional_weighted_bps": float(raw.sum() / notional.sum() * 10000) if n else None,
        "absolute_share_weighted_bps": float(
            np.average(bps, weights=abs(column(g, "quantity").to_numpy(float)[valid]))
        )
        if n
        else None,
        "conditional_supported": int(finite.sum()),
        "conditional_standalone_USD": float(conditional[finite].sum()) if finite.any() else None,
        "median_reference_delay_minutes": float(np.median(column(g, "lag").to_numpy(float)[valid]))
        if n
        else None,
        "maximum_reference_delay_minutes": float(column(g, "lag")[valid].max()) if n else None,
    }
    for k in (
        "CENSORED_EVALUATION_CUTOFF",
        "CENSORED_NO_VALID_MARK",
        "CENSORED_FORWARD_LIMIT",
        "CENSORED_UNSUPPORTED_DISTRIBUTION",
    ):
        row[k] = int(column(g, "censor").eq(k).sum())
    for field in (
        "action_cash",
        "action_claims",
        "original_exit_concession_recovery",
        "assumed_later_exit_concession",
        "standalone_fee_difference",
        "frozen_mark_short_carry",
    ):
        values = column(g, field).to_numpy(float)[valid]
        row[field + "_USD"] = float(np.nansum(values)) if n else None
    if n:
        for p in (5, 25, 50, 75, 95):
            row[f"p{p}_USD"] = float(np.quantile(raw, p / 100))
            row[f"p{p}_bps"] = float(np.quantile(bps, p / 100))
        good = table(g.loc[valid])
        day_table = table(good.groupby("exit_day").agg(daily=("raw_bps", "mean")))
        day = column(day_table, "daily")
        row["exit_days"] = len(day)
        row["mean_equal_exit_day_bps"] = float(day.mean())
        row["positive_exit_day_fraction"] = float((day > 0).mean())
        row["p05_equal_exit_day_bps"] = float(np.quantile(day.to_numpy(float), 0.05))
        row["p95_equal_exit_day_bps"] = float(np.quantile(day.to_numpy(float), 0.95))
        row["top_5_positive_raw_USD"] = float(np.sort(raw[raw > 0])[-5:].sum())
        row["raw_less_top_5_positive_USD"] = float(raw.sum() - np.sort(raw[raw > 0])[-5:].sum())
        stock_table = table(good.groupby("symbol").agg(amount=("price_raw_to_raw", "sum")))
        by_stock = column(stock_table, "amount").sort_values(ascending=False)
        row["top_2_stock_raw_USD"] = float(by_stock.head(2).sum())
        row["raw_less_top_2_stock_USD"] = float(raw.sum() - by_stock.head(2).sum())
    if row["valid"] + sum(row[k] for k in row if k.startswith("CENSORED")) != len(g):
        raise ValueError("CENSOR_SUM")
    return row


def aggregate(frame: pd.DataFrame) -> list[dict]:
    result = []
    for axis in (
        "all",
        "cause",
        "side",
        "exit_year",
        "symbol",
        "exit_state",
        "exit_score_quantile",
        "prior_raw_leg_state",
        "triggers",
        "entry_state",
        "holding",
        "session_type",
        "cross_session",
        "external_state",
        "cause_side",
        "cause_state",
        "year_cause",
        "action_scope",
        "feasibility",
        "feasible_external",
    ):
        for key, g in frame.groupby(
            ["strategy_id", "regime", "horizon", axis], dropna=False, sort=True
        ):
            if not isinstance(key, tuple) or len(key) != 4:
                raise ValueError("STRATUM_GROUP_SCHEMA")
            if not all(isinstance(x, str) for x in key):
                raise ValueError("NON_STRING_STRATUM")
            sid, regime, horizon, label = (str(x) for x in key)
            result.append(
                {
                    "strategy_id": sid,
                    "mode": mode(sid),
                    "regime": regime,
                    "horizon": horizon,
                    "axis": axis,
                    "label": str(label),
                    **stats(table(g)),
                }
            )
    return result


def legacy_check(frame: pd.DataFrame, legacy: dict, s: dict) -> list[dict]:
    previous = csv_at(Path(s["run"]) / "offline_diagnostic/V3_POST_EXIT_EXTENSION.csv")
    wanted = (column(frame, "horizon").to_numpy() == "T240") & legacy["valid"]
    rows = []
    for label in ("reversed", "weak", "strong", "unknown"):
        b = wanted & (column(frame, "exit_state").to_numpy() == label)
        old = [
            r
            for r in previous
            if r["horizon"] == "T240"
            and r["axis"] == "exit_strength"
            and r["label"] == label
            and int(r["valid"]) > 0
        ]
        old_n = sum(int(r["valid"]) for r in old)
        old_mean = sum(float(r["mean_bps"]) * int(r["valid"]) for r in old) / old_n
        value = float(np.mean(legacy["bps"][b]))
        if int(b.sum()) != old_n or abs(value - old_mean) > 1e-10:
            raise ValueError("LEGACY_POOLED_REPRODUCTION")
        rows.append(
            {
                "state": label,
                "valid": old_n,
                "saved_mean_bps": old_mean,
                "independent_mean_bps": value,
                "new_search_limit": LIMIT,
                "note": "Legacy same-session search and action censoring reproduced.",
            }
        )
    return rows


def run(out: Path) -> None:
    started = time.monotonic()
    s = check_inputs()
    pilot = json_at(ROOT / "SOURCE_PILOT_RELEASE.json")
    if (
        pilot["status"] != "PASS"
        or pilot["offline_code_sha256"]
        != digest(Path("src/lstm_data/trading/track2/rapid_exit_audit/offline.py"))
        or (ROOT / "validation/pytest.exit").read_text().strip() != "0"
    ):
        raise PermissionError("SOURCE_OR_TEST_GATE")
    tape, m = load_tape(s)
    out.mkdir(exist_ok=False, parents=True)
    publish(
        out / "START.json",
        {
            "pid": os.getpid(),
            "input_seal_sha256": digest(ROOT / "INPUT_SEAL.json"),
            "code_sha256": {
                str(p): digest(p)
                for p in Path("src/lstm_data/trading/track2/rapid_exit_audit").glob("*.py")
            },
        },
    )
    pre = json_at(ROOT / "PRE_EXTRACTION_ACCOUNT_CHECK.json")
    if pre["status"] != "PASS" or pre["cases"] != 54:
        raise ValueError("ACCOUNT_GATE_REQUIRED")
    csv_write(out / "ACCOUNT_RECONCILIATION.csv", pre["rows"])
    csv_write(out / "ALL18_EXECUTED_EXIT_CONTRACTS.csv", contracts())
    print("54 accounts verified; loading shared marks", flush=True)
    cache = FeatureCache(Path(s["cache"]))
    frame, legacy, resource = make_sample(tape, cache)
    print("Shared source lookup complete", len(frame), flush=True)
    records = aggregate(frame)
    csv_write(out / "ALL18_POST_EXIT_EXTENSIONS.csv", records)
    csv_write(
        out / "ALL18_EXIT_REFERENCE_COVERAGE.csv",
        [
            {
                k: r[k]
                for k in r
                if k
                in ("strategy_id", "mode", "regime", "horizon", "axis", "label", "exits", "valid")
                or k.startswith("CENSORED")
            }
            for r in records
            if r["axis"] in ("all", "cause", "exit_year", "cause_side", "year_cause")
        ],
    )
    csv_write(out / "LEGACY_POOLED_STATE_REPRODUCTION.csv", legacy_check(frame, legacy, s))
    # Only a small deterministic source receipt is retained, independent of payoff.
    ids = np.argsort(
        [
            canonical((int(i), str(c), int(t)))
            for i, c, t in zip(
                frame.index, column(frame, "case"), column(frame, "effective"), strict=True
            )
        ]
    )[:100]
    frame.iloc[ids].to_csv(out / "HASHED_REFERENCE_AUDIT_SAMPLE.csv", index=False)
    print("Aggregated offline diagnostics", len(records), flush=True)
    # Actual-cohort raw reconstruction is downstream descriptive support only.
    from .review import analyze

    analyze(out, frame, s)
    check_inputs()
    output_bytes = sum(p.stat().st_size for p in out.iterdir() if p.is_file())
    if output_bytes > 100_000_000:
        raise ValueError("ANALYSIS_OUTPUT_BUDGET")
    publish(
        out / "RUN_RECEIPT.json",
        {
            "status": "PASS",
            "seconds": time.monotonic() - started,
            "peak_RSS_bytes": peak_memory_bytes(),
            "actual_exit_legs": len(tape),
            "reference_targets": len(frame),
            "unique_reference_requests": resource["unique_reference_requests"],
            "source_reads": resource["source_reads"],
            "baseline_replays": 0,
            "online_modules_changed": False,
            "bytes_before_receipt": sum(p.stat().st_size for p in out.iterdir() if p.is_file()),
            "output_hashes": {p.name: digest(p) for p in out.iterdir() if p.is_file()},
        },
    )
    print(out, len(tape), len(frame), round(time.monotonic() - started, 2), flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    run(a.output)


if __name__ == "__main__":
    main()
