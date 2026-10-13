"""Exact selected-five source-key inventory; no price features, labels or fills."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from .broad_screen import read_candidate
from .calendar import schedule
from .config import atomic_new, digest, write_json
from .fast_screen import ARCHIVE, PACKAGE, SECTORS, clusters, csv_new, verified_frame
from .stock_source import StockCalendar
from .store import chunk_paths
from .universe_screen import t2_absence_bound


def saved_session_audit(
    frame: pd.DataFrame, ticker: str, day: str, opening: pd.Timestamp, closing: pd.Timestamp
) -> dict:
    """Audit validated rows against one precomputed XNYS session clock."""
    if not (frame.source_timeframe == "30Min").all():
        raise ValueError("NATIVE_30MIN_REQUIRED")
    expected = tuple(pd.date_range(opening, closing, freq="30min", inclusive="left"))
    selected = frame[
        (frame.symbol == ticker) & (frame.timestamp >= opening) & (frame.timestamp < closing)
    ]
    found = set(selected.timestamp)
    if len(found) != len(selected) or found - set(expected):
        raise ValueError("DUPLICATE_OR_OFF_GRID_NATIVE_RTH_SOURCE")
    missing = [stamp for stamp in expected if stamp not in found]
    longest = run = 0
    for stamp in expected:
        run = run + 1 if stamp not in found else 0
        longest = max(longest, run)
    return {
        "symbol": ticker,
        "session_et": day,
        "expected": len(expected),
        "actual": len(found),
        "missing": len(missing),
        "missing_starts_utc": [s.isoformat() for s in missing],
        "terminal_stub_missing": expected[-1] not in found,
        "longest_gap_half_hours": longest,
        "status": "TARGETED_DATES_PASS" if not missing else "OBSERVED_GAP",
        "population": "ZERO_KEYS" if not found else "COMPLETE" if not missing else "PARTIAL",
    }


def source_references(report: Path) -> list[dict]:
    """Canonical AAPL plus its inactive warmup, and one shared selected-four store."""
    full = report / "full_acquisition.json"
    if full.exists():
        new = json.loads(full.read_text())["chunks"]
    else:
        # A blocked multipart request is never published as a completed chunk.
        new = []
        plan = json.loads((report / "full_request_plan.json").read_text())
        for row in plan["requests"]:
            p = row["params"]
            saved = read_candidate(ARCHIVE / "full_native", p)
            if saved is None:
                continue
            frame, meta = saved
            data, manifest = chunk_paths(ARCHIVE / "full_native", p)
            new.append(
                {
                    "data": str(data),
                    "manifest": str(manifest),
                    "sha256": digest(data),
                    "manifest_sha256": digest(manifest),
                    "params": p,
                    "rows": len(frame),
                    "pages": sum(r.get("status") == 200 for r in meta["receipts"]),
                }
            )
    refs = list(new)
    for manifest in sorted(Path("data/raw/alpaca/track_a").glob("*.manifest.json")):
        meta = json.loads(manifest.read_text())
        data = manifest.with_name(manifest.name.replace(".manifest.json", ".parquet"))
        refs.append(
            {
                "data": str(data),
                "manifest": str(manifest),
                "sha256": digest(data),
                "manifest_sha256": digest(manifest),
                "params": meta["params"],
                "reused": True,
            }
        )
    warm = json.loads(
        Path(
            "reports/data_audit/ta_data_remed_ft0_001_2026-10-11_195135/source_extension_manifest_v2.json"
        ).read_text()
    )
    for row in warm["chunks"]:
        if row["kind"] == "WARMUP":
            refs.append(
                {
                    "data": row["data_path"],
                    "manifest": row["manifest_path"],
                    "sha256": row["sha256"],
                    "manifest_sha256": row["manifest_sha256"],
                    "params": row["params"],
                    "reused": True,
                }
            )
    # Exact containing sample sources remain useful evidence after a bulk stop.
    selection = json.loads((report / "selected_four_pre_acquisition.json").read_text())
    known = {r["data"] for r in refs}
    for ref in selection["source_refs"]:
        if ref["params"]["timeframe"] == "30Min" and ref["data"] not in known:
            refs.append(dict(ref, sample_only=True))
            known.add(ref["data"])
    return refs


def expand_missing(cluster_rows: list[dict]) -> list[dict]:
    """One row per absent native key, preserving ET offsets and maximal run ID."""
    rows = []
    for cluster in cluster_rows:
        for stamp in pd.date_range(
            cluster["start_utc"], cluster["end_utc"], freq="30min", inclusive="left"
        ):
            end = stamp + pd.Timedelta(minutes=30)
            rows.append(
                dict(
                    cluster,
                    start_utc=stamp.isoformat(),
                    end_utc=end.isoformat(),
                    start_et=stamp.tz_convert("America/New_York").isoformat(),
                    end_et=end.tz_convert("America/New_York").isoformat(),
                    interval_minutes=30,
                    terminal_stub=cluster["terminal_missing"]
                    and end.isoformat() == cluster["end_utc"],
                    audit_status="GENUINE_ABSENT_EXPECTED_KEY_IN_COMPLETED_RESPONSE",
                )
            )
    return rows


def summarize(ticker: str, days: list[dict], gaps: list[dict], *, period: str) -> dict:
    expected = sum(d["expected"] for d in days)
    actual = sum(d["actual"] for d in days)
    lengths = Counter(g["run_size"] for g in gaps)
    largest = max(gaps, key=lambda g: g["run_size"], default=None)
    return {
        "ticker": ticker,
        "sector_provisional": SECTORS[ticker],
        "period": period,
        "expected": expected,
        "observed": actual,
        "missing": expected - actual,
        "missing_percent": 100 * (expected - actual) / expected,
        "coverage_percent": 100 * actual / expected,
        "sessions": len(days),
        "sessions_affected": sum(d["missing"] > 0 for d in days),
        "clusters": len(gaps),
        "runs_length1": lengths[1],
        "runs_length2": lengths[2],
        "runs_length3plus": sum(n for length, n in lengths.items() if length >= 3),
        "largest_run": largest["run_size"] if largest else 0,
        "largest_run_session": largest["session_et"] if largest else None,
        "terminal_missing": sum(d["terminal_stub_missing"] for d in days),
        "native98_pass": actual / expected >= 0.98,
        "native_exact_complete": expected == actual,
        "duplicates": 0,
        "malformed": 0,
        "off_grid_rth": 0,
        "scientific": "HOLD",
        "full_FT0_retention": "NOT_MEASURED",
    }


def run(report: Path) -> dict:
    selection = json.loads((report / "selected_four_pre_acquisition.json").read_text())
    order = selection["five_order"]
    plan = json.loads((report / "full_request_plan.json").read_text())
    if digest(report / "selected_four_pre_acquisition.json") != plan["selected_sha256"]:
        raise ValueError("FROZEN_SELECTION_CHANGED")
    refs = source_references(report)
    start = plan["prehistory"]
    sessions = schedule(start, "2025-06-30")
    days_all, gaprows, coverage, nonresponse = [], [], [], []
    # Bound each audit to one completed partition and one stock-session, avoiding
    # repeated validation of five-year price tables. No indicator values are read.
    frames = {r["data"]: verified_frame(r) for r in refs}
    for ticker in order:
        relevant = [
            r
            for r in refs
            if ticker in r["params"]["symbols"].split(",")
            and (r.get("reused", False) == (ticker == "AAPL"))
        ]
        for ref in relevant:
            p = ref["params"]
            if (
                p["timeframe"] != "30Min"
                or p["feed"] != "sip"
                or p["adjustment"] != "split"
                or p["asof"] != "2025-06-30"
                or p["currency"] != "USD"
            ):
                raise ValueError("EXACT_NATIVE_IDENTITY_REQUIRED")
            f = frames[ref["data"]]
            f = f[f.symbol == ticker]
            coverage.append(
                {
                    "ticker": ticker,
                    "source": ref["data"],
                    "manifest": ref["manifest"],
                    "source_sha256": ref["sha256"],
                    "manifest_sha256": ref["manifest_sha256"],
                    "start_inclusive_utc": p["start"],
                    "end_inclusive_utc": p["end"],
                    "rows": len(f),
                    "shared_file_bytes": Path(ref["data"]).stat().st_size,
                    "pages": ref.get("pages", "INHERITED_COMPLETED"),
                    "reused": ref.get("reused", False),
                    "partition_state": "PAGINATION_EXHAUSTED_SHA_VERIFIED",
                }
            )
        for day_stamp, clock in sessions.iterrows():
            if not isinstance(day_stamp, pd.Timestamp):
                raise ValueError("EXACT_EXCHANGE_SESSION_TIMESTAMP_REQUIRED")
            day = day_stamp.strftime("%Y-%m-%d")
            matches = [
                r
                for r in relevant
                if pd.Timestamp(r["params"]["start"]) <= clock.open
                and pd.Timestamp(r["params"]["end"]) >= clock.close - pd.Timedelta(nanoseconds=1)
            ]
            # Prefer complete bulk partitions over containing day pilots; a
            # pilot is used only for its actually covered session, never a year.
            bulk_matches = [r for r in matches if not r.get("sample_only", False)]
            if bulk_matches:
                matches = bulk_matches
            if len(matches) != 1:
                nonresponse.append(
                    {
                        "ticker": ticker,
                        "session_et": day,
                        "status": "NOT_MEASURED_SOURCE_PARTITION",
                        "matches": len(matches),
                    }
                )
                continue
            ref = matches[0]
            f = frames[ref["data"]]
            f = f[(f.symbol == ticker) & (f.timestamp >= clock.open) & (f.timestamp < clock.close)]
            audit = saved_session_audit(f, ticker, day, clock.open, clock.close)
            audit.update(
                period="PREHISTORY" if day < "2020-07-01" else "FIVE_YEAR",
                source=ref["data"],
                source_sha256=ref["sha256"],
                manifest=ref["manifest"],
                partition_state="VERIFIED_PARTIAL" if audit["missing"] else "VERIFIED_COMPLETE",
            )
            days_all.append(audit)
            gaprows.extend(dict(g, period=audit["period"]) for g in clusters(audit, ref))
    missing = expand_missing(gaprows)
    main_days = [d for d in days_all if d["period"] == "FIVE_YEAR"]
    main_gaps = [g for g in gaprows if g["period"] == "FIVE_YEAR"]
    main_missing = [r for r in missing if r["period"] == "FIVE_YEAR"]
    summaries, years = [], []
    for ticker in order:
        per = [d for d in main_days if d["symbol"] == ticker]
        gaps = [g for g in main_gaps if g["ticker"] == ticker]
        summary = summarize(ticker, per, gaps, period="2020-07-01_THROUGH_2025-06-30")
        unknown = [
            r for r in nonresponse if r["ticker"] == ticker and r["session_et"] >= "2020-07-01"
        ]
        summary["unmeasured_sessions"] = len(unknown)
        summary["full_interval_expected"] = sum(
            len(pd.date_range(c.open, c.close, freq="30min", inclusive="left"))
            for stamp, c in sessions.iterrows()
            if str(stamp)[:10] >= "2020-07-01"
        )
        summary["interval_state"] = (
            "FULL_SOURCE_QA_INCOMPLETE" if unknown else "FULL_INTERVAL_VERIFIED"
        )
        source_keys = set()
        for ref in [
            r
            for r in refs
            if ticker in r["params"]["symbols"].split(",")
            and r.get("reused", False) == (ticker == "AAPL")
        ]:
            f = frames[ref["data"]]
            f = f[f.symbol == ticker]
            source_keys.update(f.timestamp)
        summary["out_of_RTH_source_rows_including_prehistory"] = len(source_keys) - sum(
            d["actual"] for d in days_all if d["symbol"] == ticker
        )
        yearly_pass = True
        for year in range(2020, 2026):
            yd = [d for d in per if d["session_et"].startswith(str(year))]
            expected, actual = sum(d["expected"] for d in yd), sum(d["actual"] for d in yd)
            not_measured = sum(r["session_et"].startswith(str(year)) for r in unknown)
            fraction = actual / expected if expected else 0.0
            yearly_pass &= not not_measured and fraction >= 0.95
            years.append(
                {
                    "ticker": ticker,
                    "year": year,
                    "expected": expected,
                    "observed": actual,
                    "missing": expected - actual,
                    "coverage_percent": "NOT_MEASURED_FULL_INTERVAL"
                    if not_measured
                    else 100 * fraction,
                    "native95_pass": "NOT_MEASURED_FULL_INTERVAL"
                    if not_measured
                    else fraction >= 0.95,
                    "window": "PARTIAL_YEAR_JUL_DEC"
                    if year == 2020
                    else "PARTIAL_YEAR_JAN_JUN"
                    if year == 2025
                    else "FULL_YEAR",
                    "source_integrity_only": True,
                    "unmeasured_sessions": sum(
                        r["session_et"].startswith(str(year)) for r in unknown
                    ),
                }
            )
        summary["each_year95_pass"] = yearly_pass
        summary["measured_D1_source_percentage_pass"] = summary["native98_pass"] and yearly_pass
        if unknown:
            for key in (
                "missing_percent",
                "coverage_percent",
                "native98_pass",
                "each_year95_pass",
                "measured_D1_source_percentage_pass",
                "native_exact_complete",
            ):
                summary[key] = "NOT_MEASURED_FULL_INTERVAL"
        summaries.append(summary)
    assert len(main_missing) == sum(s["missing"] for s in summaries)
    assert len(main_gaps) == sum(s["clusters"] for s in summaries)
    columns = [
        "ticker",
        "session_et",
        "start_utc",
        "end_utc",
        "run_size",
        "terminal_missing",
        "cluster_id",
        "source",
        "manifest",
        "source_sha256",
        "period",
    ]
    csv_new(
        report / "missing_candles_all_selected.csv",
        main_missing,
        columns + ["start_et", "end_et", "interval_minutes", "terminal_stub", "audit_status"],
    )
    csv_new(report / "missing_clusters_all_selected.csv", main_gaps, columns)
    csv_new(
        report / "prehistory_missing_candles.csv",
        [r for r in missing if r["period"] == "PREHISTORY"],
        columns + ["start_et", "end_et", "interval_minutes", "terminal_stub", "audit_status"],
    )
    csv_new(
        report / "source_nonresponse.csv",
        nonresponse,
        ["ticker", "session_et", "status", "matches"],
    )
    csv_new(report / "download_coverage.csv", coverage)
    csv_new(report / "per_stock_native_quality.csv", summaries)
    csv_new(report / "per_year_native_quality.csv", years)
    csv_new(
        report / "prehistory_native_quality.csv",
        [
            dict(
                summarize(
                    t,
                    [d for d in days_all if d["symbol"] == t and d["period"] == "PREHISTORY"],
                    [g for g in gaprows if g["ticker"] == t and g["period"] == "PREHISTORY"],
                    period="PREHISTORY",
                ),
                unmeasured_sessions=sum(
                    r["ticker"] == t and r["session_et"] < "2020-07-01" for r in nonresponse
                ),
                interval_state="MEASURED_PARTITIONS_ONLY"
                if any(r["ticker"] == t and r["session_et"] < "2020-07-01" for r in nonresponse)
                else "FULL_PREHISTORY_VERIFIED",
            )
            for t in order
        ],
    )
    write_json(report / "exact_session_key_audit.json", days_all)
    closes = {
        t: tuple(
            d["session_et"]
            for d in days_all
            if d["symbol"] == t and d["session_et"] < "2023-07-01" and d["terminal_stub_missing"]
        )
        for t in order
    }
    cal = StockCalendar(start, "2023-06-30")
    losses = {t: t2_absence_bound(cal, closes[t]) for t in order}
    union = set((r["session"], r["origin"]) for rows in losses.values() for r in rows)
    bound = {
        "denominator": 1502,
        "upper_numerator": 1502 - len(union),
        "upper_fraction": (1502 - len(union)) / 1502,
        "required_numerator": 1352,
        "missing_terminal_sessions": closes,
        "conditional_T2_only": True,
        "full_FT0": "NOT_MEASURED",
        "scientific": "HOLD",
        "no_returns_or_fits": True,
    }
    write_json(report / "training_t2_only_ceiling.json", bound)
    write_json(
        report / "immutable_source_manifest.json",
        {
            "package": PACKAGE,
            "sources": refs,
            "selection_sha256": digest(report / "selected_four_pre_acquisition.json"),
            "new_sources": len([r for r in refs if not r.get("reused", False)]),
            "original_sources_read_only": True,
            "confirmation_analysis": "RAW_KEY_GRID_ONLY_AFTER_SELECTION_FREEZE",
            "scientific": "HOLD",
        },
    )
    result = {
        "status": "FAST_FIVE_STOCK_PARTIAL_SOURCE_OR_RESOURCE_BLOCKED"
        if nonresponse
        else "FAST_FIVE_STOCK_NATIVE_DATA_QA_COMPLETE",
        "five_order": order,
        "summary": summaries,
        "missing_candles": len(main_missing),
        "clusters": len(main_gaps),
        "source_nonresponse": len(nonresponse),
        "training_ceiling": bound,
        "scientific": "HOLD",
    }
    write_json(report / "gate_c_complete_checkpoint.json", result)
    lines = [
        "# Exact missing-candle inventory",
        "",
        "**PARTIAL native source-key audit; FULL_SOURCE_QA_INCOMPLETE; SCIENTIFIC_HOLD.**"
        if nonresponse
        else "**Complete native source-key audit; provisional selection, SCIENTIFIC_HOLD.**",
        "",
        "AAPL first, followed by the four frozen selections. Each normal XNYS day has 13 starts "
        "from 09:30 through 15:30 ET. Early closes use their actual terminal stub. "
        "ET timestamps below carry explicit UTC offsets. Confirmation candles were checked "
        "only as source keys after selection; no features, labels or performance were computed.",
        "",
        "|Stock|Provisional sector|Expected|Observed|Missing|Runs|Largest run|Terminal absent|"
        "98% / yearly95%|",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in summaries:
        lines.append(
            f"|{s['ticker']}|{s['sector_provisional']}|{s['expected']}|{s['observed']}|"
            f"{s['missing']}|{s['clusters']}|{s['largest_run']}|{s['terminal_missing']}|"
            f"{s['native98_pass']} / {s['each_year95_pass']}|"
        )
    lines += [
        "",
        "## Largest clumps",
        "",
        "|Stock|Session ET|Start UTC|End UTC|Half-hours|",
        "|---|---|---|---|---:|",
    ]
    for g in sorted(
        main_gaps, key=lambda g: (-g["run_size"], order.index(g["ticker"]), g["session_et"])
    )[:20]:
        lines.append(
            f"|{g['ticker']}|{g['session_et']}|{g['start_utc']}|{g['end_utc']}|{g['run_size']}|"
        )
    for t in order:
        lines += [
            "",
            f"## {t} — "
            f"{'available-partition' if nonresponse and t != 'AAPL' else 'complete'} "
            "absent-candle list",
            "",
            "|ET start|ET end|UTC start|Run size|Terminal stub|",
            "|---|---|---|---:|---|",
        ]
        chosen = [r for r in main_missing if r["ticker"] == t]
        for r in chosen:
            lines.append(
                f"|{r['start_et']}|{r['end_et']}|{r['start_utc']}|{r['run_size']}|{r['terminal_stub']}|"
            )
        if not chosen:
            lines.append(
                "No absent keys in the measured partitions; unmeasured sessions are not gap-free."
                if nonresponse and t != "AAPL"
                else "No missing expected RTH keys."
            )
    lines += [
        "",
        f"The {'PARTIAL' if nonresponse else 'complete'} CSV contains {len(main_missing)} "
        f"absent keys in {len(main_gaps)} "
        "maximal within-session runs. Source/manifest/SHA and stable cluster IDs are in "
        "[the CSV](missing_candles_all_selected.csv). [Prehistory](prehistory_native_quality.csv) "
        f"is separate; {len(nonresponse)} stock-sessions have unverified source partitions. "
        "Malformed/duplicate/off-grid keys are rejected by the source validator, "
        "with no corrections.",
        "",
        f"Training: conditional T2-only upper bound {bound['upper_numerator']}/1502 = "
        f"{bound['upper_fraction']:.2%}; required1352. This assumes all other dependencies ideal. "
        "Actual complete48×16 FT0, M2 and scientific eligibility are NOT_MEASURED; "
        "no floor/scaler fit or TG0 label was manufactured.",
        "",
        "Source percentages alone do not resolve a major run, missing terminal close, "
        "unknown publication, action vintage or historical membership. The original five stocks, "
        "frozen rules and 0/40 scientific ledger remain unchanged. "
        "No missing candle has been filled.",
    ]
    atomic_new(report / "exact_missing_candle_inventory.md", ("\n".join(lines) + "\n").encode())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.report)
    print(
        {
            "status": result["status"],
            "missing": result["missing_candles"],
            "clusters": result["clusters"],
        }
    )


if __name__ == "__main__":
    main()
