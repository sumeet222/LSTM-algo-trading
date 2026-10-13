"""Finite 49-name source screen and selected-four native inventory, no activation."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials, request_params
from .broad_screen import DATES, GROUPS, IDENTITY, POOL, BroadTransport, audit_day, read_candidate
from .calendar import schedule
from .config import digest, fingerprint, load_config, now, write_json
from .remediation_plan import dependency_calendar
from .remediation_transport import StorageLimit, publish_chunk
from .store import chunk_paths, read_verified
from .universe_screen import verify_screen_authority

PACKAGE = "TA-FAST-UNIVERSE-SELECT4-DOWNLOAD-QA-001"
ARCHIVE = Path("data/raw/alpaca/track_a_fast49_candidate_v1")
PREVIOUS = Path("reports/data_audit/ta_broad_universe_2026-10-13_000736")
INTERRUPTED = Path("data/raw/alpaca/track_a_sp500_greedy_candidate_v1/transport_attempts.jsonl")
ADDITIONS = {
    "Financials": ("GS", "MS", "C", "BLK"),
    "Health Care": ("PFE", "UNH", "BMY"),
    "Consumer Staples": ("KO", "PEP", "CL"),
    "Consumer Discretionary": ("GM", "F", "SBUX"),
    "Industrials": ("LMT", "RTX", "GE"),
    "Energy": ("SLB", "OXY"),
    "Utilities": ("SO", "D"),
}
NEW = tuple(s for names in ADDITIONS.values() for s in names)
ALL = POOL + NEW
SECTORS = {s: sector for sector, names in (GROUPS | ADDITIONS).items() for s in names}
SECTORS.update({s: sector for sector, names in GROUPS.items() for s in names})


def csv_new(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    """Publish derived tabular facts once, without rewriting historical evidence."""
    from .config import atomic_new

    frame = pd.DataFrame(rows, columns=columns)
    atomic_new(path, frame.to_csv(index=False).encode())


def inherited_attempts() -> int:
    return (
        sum(json.loads(line)["kind"] == "ATTEMPT" for line in INTERRUPTED.read_text().splitlines())
        if INTERRUPTED.exists()
        else 0
    )


class FastTransport(BroadTransport):
    """Separate paced journal, retaining the interrupted task's binding ceiling."""

    def append(self, item: dict) -> None:
        if item["kind"] == "ATTEMPT" and self.used + inherited_attempts() >= 1000:
            raise DataAccessError("FAST_CUMULATIVE_ATTEMPT_LIMIT")
        super().append(dict(item, package=PACKAGE, inherited_attempts=inherited_attempts()))


def prepare(report: Path) -> dict:
    """Freeze exactly 49 names and a selection rule before new samples are opened."""
    verify_screen_authority()
    if len(ALL) != 49 or len(set(ALL)) != 49 or len(NEW) != 20:
        raise ValueError("EXACT49_USER_POOL_REQUIRED")
    pool = {
        "package": PACKAGE,
        "symbols": ALL,
        "additions": NEW,
        "sectors_provisional": SECTORS,
        "anchor": "AAPL",
        "formation_membership_and_sector": "UNVERIFIED_UNLESS_PRIOR_EVIDENCE",
        "policy": {
            "per_stock_quality_ascending": [
                "any_missing",
                "any_terminal_missing",
                "any_run_ge3",
                "total_missing",
                "affected_dates",
                "action_identity_risk",
                "negative_preformation_dollar_volume",
                "ticker",
            ],
            "panel_rule": (
                "Best eligible stock per sector; enumerate all four-sector combinations; "
                "minimize descending-sorted stock quality tuples lexicographically; "
                "selected order ascending stock quality"
            ),
            "eligibility": (
                "Exactly60 unique expected preformation daily sessions and mean close*volume>=50m; "
                "sector provisional permitted by current task"
            ),
            "action_identity_risk": (
                "2 for HON/RTX/GE documented restructuring or future adjustment exposure; "
                "1 for other unverified action vintages; no scientific certificate implied"
            ),
            "selection_period": "Only formation60 and five fixed training dates",
            "full_history_quality_never_changes_selection": True,
        },
        "inherited_attempts": inherited_attempts(),
        "interrupted_journal_sha256": digest(INTERRUPTED) if INTERRUPTED.exists() else None,
        "limits": {
            "cumulative_attempts": 1000,
            "page_lifetime_attempts": 3,
            "sends_per_minute": 100,
            "bytes": 256 * 1024**2,
        },
    }
    write_json(report / "pool_49.json", pool)
    cfg = load_config(Path("configs/track_a_data.json"))
    rows = []
    daily = request_params(
        dict(cfg, timeframe="1Day", adjustment="raw", asof="2020-07-01"),
        list(NEW),
        "2020-04-06T04:00:00Z",
        "2020-07-01T03:59:59.999999999Z",
    )
    rows.append({"kind": "FORMATION_DAILY", "params": daily, "max_pages": 1})
    for day in DATES:
        start = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
        end = start + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        rows.append(
            {
                "kind": "TARGETED_30MIN",
                "params": request_params(cfg, list(NEW), start.isoformat(), end.isoformat()),
                "max_pages": 1,
            }
        )
    for row in rows:
        row["request_hash"] = fingerprint(row["params"])
    plan = {
        "package": PACKAGE,
        "pool_sha256": digest(report / "pool_49.json"),
        "requests": rows,
        "requests_sha256": fingerprint(rows),
        "maximum_pages": 6,
        "worst_attempts": 18,
        "calendar_max_rows": 60 * 20 + 5 * 48 * 20,
        "uncompressed_byte_estimate_at128": (60 * 20 + 5 * 48 * 20) * 128,
        "cache": {
            "previous_manifest": str(PREVIOUS / "immutable_source_manifest.json"),
            "sha256": digest(PREVIOUS / "immutable_source_manifest.json"),
        },
    }
    write_json(report / "screen_request_plan.json", plan)
    write_json(
        report / "gate_a_prequery_checkpoint.json",
        {
            "status": "POOL_AND_RULE_FROZEN",
            "new_GETs": 0,
            "prior_amzn_attempts": inherited_attempts(),
            "scientific": "HOLD",
        },
    )
    return plan


def acquire(report: Path, plan_path: Path, *, get=requests.get) -> dict:
    """Execute only fixed source plans and publish fully paginated immutable chunks."""
    verify_screen_authority()
    pool = json.loads((report / "pool_49.json").read_text())
    if (
        tuple(pool["symbols"]) != ALL
        or tuple(pool["additions"]) != NEW
        or pool["interrupted_journal_sha256"]
        != (digest(INTERRUPTED) if INTERRUPTED.exists() else None)
    ):
        raise ValueError("FIXED_POOL_OR_INHERITED_BUDGET_CHANGED")
    plan = json.loads(plan_path.read_text())
    if (
        plan["package"] != PACKAGE
        or plan["pool_sha256"] != digest(report / "pool_49.json")
        or plan["requests_sha256"] != fingerprint(plan["requests"])
    ):
        raise ValueError("PREQUERY_PLAN_SHA_REQUIRED")
    selected = None
    if "selected_sha256" in plan:
        if digest(report / "selected_four_pre_acquisition.json") != plan["selected_sha256"]:
            raise ValueError("SELECTION_CHANGED_AFTER_FULL_HISTORY_PLAN")
        selected = json.loads((report / "selected_four_pre_acquisition.json").read_text())[
            "selected_four"
        ]
    for row in plan["requests"]:
        p = row["params"]
        symbols = p["symbols"].split(",")
        if (
            p["feed"] != "sip"
            or p["currency"] != "USD"
            or p["limit"] != 10000
            or p["sort"] != "asc"
            or row["request_hash"] != fingerprint(p)
            or not 1 <= row["max_pages"] <= 4
            or "AAPL" in symbols
        ):
            raise ValueError("FIXED_NATIVE_SOURCE_SCOPE_REQUIRED")
        if row["kind"] == "FULL_NATIVE":
            if selected is None or set(symbols) - set(selected) or not symbols:
                raise ValueError("ONLY_PRESELECTED_FOUR_MAY_BE_DOWNLOADED")
            if (
                any(p[k] != v for k, v in IDENTITY.items())
                or p["timeframe"] != "30Min"
                or pd.Timestamp(p["start"]) < pd.Timestamp("2019-12-18T05:00Z")
                or pd.Timestamp(p["end"]) >= pd.Timestamp("2025-07-01T04:00Z")
            ):
                raise ValueError("FIXED_FULL_SOURCE_INTERVAL_REQUIRED")
        elif row["kind"] == "FORMATION_DAILY":
            if (
                symbols != list(NEW)
                or p["timeframe"] != "1Day"
                or p["adjustment"] != "raw"
                or p["asof"] != "2020-07-01"
                or p["start"] != "2020-04-06T04:00:00Z"
                or p["end"] != "2020-07-01T03:59:59.999999999Z"
            ):
                raise ValueError("EXACT_FORMATION_SAMPLE_REQUIRED")
        elif row["kind"] == "TARGETED_30MIN":
            start, end = pd.Timestamp(p["start"]), pd.Timestamp(p["end"])
            if (
                symbols != list(NEW)
                or p["timeframe"] != "30Min"
                or any(p[k] != v for k, v in IDENTITY.items())
                or start.tz_convert("America/New_York").strftime("%Y-%m-%d") not in DATES
                or end - start != pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
            ):
                raise ValueError("FIXED_FIVE_TRAINING_DATES_REQUIRED")
        else:
            raise ValueError("UNKNOWN_PLAN_KIND")
    limit = StorageLimit((ARCHIVE, report))
    journal = ARCHIVE / "transport_attempts.jsonl"
    transport = FastTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    cfg = load_config(Path("configs/track_a_data.json"))
    key = secret = ""
    chunks = []
    for row in plan["requests"]:
        p = row["params"]
        store = ARCHIVE / row["kind"].lower()
        saved = read_candidate(store, p)
        if saved is None:
            if not key:
                load_dotenv(Path(".env"), override=False)
                key, secret = credentials()
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(cfg["retry"], max_attempts=3, requests_per_minute=100),
                ),
                key,
                secret,
                get=transport.request,
            )
            begin = len(transport.records())
            try:
                frame = client.bars(p)
            except (ValueError, DataAccessError):
                transport.append(
                    {
                        "kind": "HOLD",
                        "reason": "CLIENT_OR_PAGINATION_HOLD",
                        "request_hash": row["request_hash"],
                        "time_utc": now(),
                    }
                )
                raise DataAccessError("FAST_SOURCE_HOLD") from None
            meta = publish_chunk(
                store, frame, p, transport.records()[begin:], kind=row["kind"], limit=limit
            )
            resumed = False
        else:
            frame, meta = saved
            resumed = True
        data, manifest = chunk_paths(store, p)
        chunks.append(
            {
                "data": str(data),
                "manifest": str(manifest),
                "sha256": digest(data),
                "manifest_sha256": digest(manifest),
                "params": p,
                "kind": row["kind"],
                "rows": len(frame),
                "bytes": data.stat().st_size,
                "pages": sum(r.get("status") == 200 for r in meta["receipts"]),
                "terminal_page_verified": meta["terminal_page_verified"],
                "resumed_zero_GET": resumed,
            }
        )
    return {
        "package": PACKAGE,
        "chunks": chunks,
        "new_attempts": transport.used,
        "inherited_attempts": inherited_attempts(),
        "cumulative_attempts": transport.used + inherited_attempts(),
        "journal": str(journal),
        "journal_sha256": digest(journal),
        "scientific": "HOLD",
    }


def verified_frame(ref: dict) -> pd.DataFrame:
    data, manifest = Path(ref["data"]), Path(ref["manifest"])
    if digest(data) != ref["sha256"] or digest(manifest) != ref["manifest_sha256"]:
        raise ValueError("IMMUTABLE_REUSED_SOURCE_SHA_CHANGED")
    meta = json.loads(manifest.read_text())
    if data.parent.name == "track_a":
        return read_verified(data, manifest, meta["params"])
    saved = read_candidate(data.parent, meta["params"])
    if saved is None:
        raise ValueError("VERIFIED_SOURCE_PAIR_REQUIRED")
    return saved[0]


def quality(row: dict) -> tuple:
    return (
        int(row["missing"] > 0),
        int(row["terminal_missing"] > 0),
        int(row["longest_run"] >= 3),
        row["missing"],
        row["affected_dates"],
        row["action_identity_risk"],
        -row["dollar_volume"],
        row["ticker"],
    )


def select_four(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Fixed panel lexicographic comparison; later history is not an input."""
    eligible = [r for r in rows if r["ticker"] != "AAPL" and r["liquidity_pass"]]
    best = {}
    for row in sorted(eligible, key=quality):
        best.setdefault(row["sector"], row)
    if len(best) < 4:
        raise ValueError("FOUR_LIQUIDITY_QUALIFIED_DISTINCT_SECTORS_REQUIRED")
    panels = list(itertools.combinations(best.values(), 4))
    chosen = min(panels, key=lambda panel: tuple(sorted((quality(r) for r in panel), reverse=True)))
    ranked = sorted(eligible, key=quality)
    return sorted(chosen, key=quality), ranked


def clusters(day: dict, ref: dict) -> list[dict]:
    missing = [pd.Timestamp(t) for t in day["missing_starts_utc"]]
    groups: list[list[pd.Timestamp]] = []
    for stamp in missing:
        if not groups or stamp - groups[-1][-1] != pd.Timedelta(minutes=30):
            groups.append([])
        groups[-1].append(stamp)
    return [
        {
            "ticker": day["symbol"],
            "session_et": day["session_et"],
            "start_utc": group[0].isoformat(),
            "end_utc": (group[-1] + pd.Timedelta(minutes=30)).isoformat(),
            "run_size": len(group),
            "terminal_missing": day["terminal_stub_missing"] and group[-1] == missing[-1],
            "cluster_id": fingerprint(
                [PACKAGE, day["symbol"], day["session_et"], group[0].isoformat()]
            ),
            "source": ref["data"],
            "manifest": ref["manifest"],
            "source_sha256": ref["sha256"],
        }
        for group in groups
    ]


def analyze_screen(report: Path) -> dict:
    pool = json.loads((report / "pool_49.json").read_text())
    plan = json.loads((report / "screen_request_plan.json").read_text())
    if tuple(pool["symbols"]) != ALL or digest(report / "pool_49.json") != plan["pool_sha256"]:
        raise ValueError("PRECOMMITTED_POOL_OR_POLICY_CHANGED")
    prior = json.loads((PREVIOUS / "immutable_source_manifest.json").read_text())["references"]
    acquired = json.loads((report / "screen_acquisition.json").read_text())["chunks"]
    refs = prior + acquired
    frames = {ref["data"]: verified_frame(ref) for ref in refs}
    daily_sessions = set(
        pd.DatetimeIndex(schedule("2020-04-06", "2020-06-30").index).strftime("%Y-%m-%d")
    )
    days, gaprows, formation, summaries = [], [], [], []
    for ticker in ALL:
        liquidity = None
        for ref in refs:
            p = ref["params"]
            if p["timeframe"] != "1Day" or ticker not in p["symbols"].split(","):
                continue
            if p["adjustment"] != "raw" or p["asof"] != "2020-07-01":
                raise ValueError("MATCHING_FORMATION_SOURCE_REQUIRED")
            df = frames[ref["data"]]
            df = df[df.symbol == ticker]
            actual = list(df.timestamp.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d"))
            qualified = len(df) == 60 and set(actual) == daily_sessions and len(set(actual)) == 60
            dv = float((df.close * df.volume).mean()) if len(df) else 0.0
            liquidity = {
                "ticker": ticker,
                "rows": len(df),
                "expected_sessions": 60,
                "dollar_volume": dv,
                "liquidity_pass": qualified and dv >= 50_000_000,
                "source": ref["data"],
                "source_sha256": ref["sha256"],
                "historical_sector": "PROVISIONAL_USER_POOL",
                "membership": "UNVERIFIED",
                "historical_publication": "UNKNOWN",
                "scientific": "HOLD",
            }
            break
        if liquidity is None:
            raise ValueError("FORMATION_SAMPLE_UNAVAILABLE")
        formation.append(liquidity)
        measured = []
        for day in DATES:
            lo = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
            hi = lo + pd.Timedelta(days=1)
            ref = next(
                (
                    r
                    for r in refs
                    if r["params"]["timeframe"] == "30Min"
                    and ticker in r["params"]["symbols"].split(",")
                    and all(r["params"][k] == v for k, v in IDENTITY.items())
                    and pd.Timestamp(r["params"]["start"]) <= lo
                    and pd.Timestamp(r["params"]["end"]) >= hi - pd.Timedelta(nanoseconds=1)
                ),
                None,
            )
            if ref is None:
                raise ValueError("FIVE_DATE_SOURCE_NOT_MEASURED")
            frame = frames[ref["data"]]
            frame = frame[(frame.timestamp >= lo) & (frame.timestamp < hi)]
            audit = audit_day(frame, ticker, day)
            audit.update(
                source=ref["data"],
                source_sha256=ref["sha256"],
                sector=SECTORS[ticker],
                response_state="SUCCESSFUL_EMPTY" if audit["actual"] == 0 else "SUCCESSFUL_ROWS",
            )
            measured.append(audit)
            days.append(audit)
            gaprows.extend(clusters(audit, ref))
        summaries.append(
            {
                "ticker": ticker,
                "sector": SECTORS[ticker],
                "expected": 65,
                "actual": sum(d["actual"] for d in measured),
                "missing": sum(d["missing"] for d in measured),
                "terminal_missing": sum(d["terminal_stub_missing"] for d in measured),
                "longest_run": max(d["longest_gap_half_hours"] for d in measured),
                "affected_dates": sum(d["missing"] > 0 for d in measured),
                "action_identity_risk": 2 if ticker in {"HON", "RTX", "GE"} else 1,
                "dollar_volume": liquidity["dollar_volume"],
                "liquidity_pass": liquidity["liquidity_pass"],
            }
        )
    selected, ranked = select_four(summaries)
    csv_new(report / "five_date_49_screen.csv", days)
    csv_new(report / "five_date_gap_clusters.csv", gaprows)
    csv_new(report / "formation_49.csv", formation)
    csv_new(report / "sector_selection_ranking.csv", ranked)
    decision = {
        "package": PACKAGE,
        "state": "PROVISIONAL_NOT_APPROVED",
        "selected_four": [r["ticker"] for r in selected],
        "five_order": ["AAPL"] + [r["ticker"] for r in selected],
        "selected_evidence": selected,
        "pool_sha256": digest(report / "pool_49.json"),
        "screen_sha256": digest(report / "five_date_49_screen.csv"),
        "formation_sha256": digest(report / "formation_49.csv"),
        "source_refs": refs,
        "AAPL_reuse": "Canonical data/raw/alpaca/track_a immutable monthly collection",
        "confirmation_used_for_selection": False,
        "full_FT0": "NOT_MEASURED",
        "scientific": "HOLD",
    }
    write_json(report / "selected_four_pre_acquisition.json", decision)
    write_json(
        report / "gate_a_complete_checkpoint.json",
        {
            "selected_four": decision["selected_four"],
            "state": "SELECTION_FROZEN_BEFORE_FULL_GET",
            "selected_sha256": digest(report / "selected_four_pre_acquisition.json"),
        },
    )
    return decision


def prepare_full(report: Path) -> dict:
    selected_path = report / "selected_four_pre_acquisition.json"
    selected = json.loads(selected_path.read_text())["selected_four"]
    dependency = dependency_calendar()
    write_json(report / "feature_prehistory_dependency.json", dependency)
    cfg = load_config(Path("configs/track_a_data.json"))
    start = pd.Timestamp(dependency["minimal_calendar_start"], tz="America/New_York")
    stop = pd.Timestamp("2025-07-01", tz="America/New_York")
    rows = []
    while start < stop:
        boundary = min(start + pd.offsets.MonthBegin(1), stop)
        p = request_params(
            cfg,
            selected,
            start.tz_convert("UTC").isoformat(),
            (boundary.tz_convert("UTC") - pd.Timedelta(nanoseconds=1)).isoformat(),
        )
        rows.append(
            {"kind": "FULL_NATIVE", "params": p, "request_hash": fingerprint(p), "max_pages": 4}
        )
        start = boundary
    worst = sum(r["max_pages"] * 3 for r in rows)
    journal = ARCHIVE / "transport_attempts.jsonl"
    used = sum(json.loads(s)["kind"] == "ATTEMPT" for s in journal.read_text().splitlines())
    # 4 names * 48 slots/calendar day bounds all returned extended rows conservatively.
    maximum_rows = (
        (stop - pd.Timestamp(dependency["minimal_calendar_start"], tz="America/New_York")).days
        * 48
        * 4
    )
    if (
        worst + used + inherited_attempts() > 1000
        or maximum_rows * 128 + StorageLimit((ARCHIVE, report)).used > 256 * 1024**2
    ):
        raise ValueError("FULL_PREFLIGHT_RESOURCE_ENVELOPE_EXCEEDED")
    plan = {
        "package": PACKAGE,
        "pool_sha256": digest(report / "pool_49.json"),
        "selected_sha256": digest(selected_path),
        "requests": rows,
        "requests_sha256": fingerprint(rows),
        "worst_attempts": worst,
        "used_plus_inherited_before_bulk": used + inherited_attempts(),
        "maximum_calendar_rows": maximum_rows,
        "maximum_uncompressed_bytes_at128": maximum_rows * 128,
        "prehistory": dependency["minimal_calendar_start"],
        "source_only_confirmation_counts": True,
        "no_selection_revisions": True,
        "density_basis": "pilot rows and hard 48/day/calendar upper bound, monthly max4 pages",
        "reuse_policy": (
            "Original AAPL all months plus native warmup by reference; "
            "prior selected 5-date observations reused in screen, "
            "full-month requests are required for uncovered keys; no copied panel tables"
        ),
    }
    write_json(report / "full_request_plan.json", plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("prepare", "acquire", "screen", "full-plan"), required=True
    )
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    args.report.mkdir(parents=True, exist_ok=True)
    if args.phase == "prepare":
        prepare(args.report)
    elif args.phase == "screen":
        result = analyze_screen(args.report)
        print({"selected_four": result["selected_four"], "state": result["state"]})
    elif args.phase == "full-plan":
        plan = prepare_full(args.report)
        print({"partitions": len(plan["requests"]), "worst_attempts": plan["worst_attempts"]})
    else:
        if args.plan is None or args.output is None or args.output.exists():
            raise ValueError("NEW_OUTPUT_AND_FIXED_PLAN_REQUIRED")
        write_json(args.output, acquire(args.report, args.plan))


if __name__ == "__main__":
    main()
