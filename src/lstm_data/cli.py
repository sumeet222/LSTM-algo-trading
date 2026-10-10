"""Reproducible data-only commands; every command offers a network-free dry run."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv

from .aggregation import aggregate_session_hours
from .alignment import asof_diagnostic
from .alpaca import DataAccessError, HistoricalClient, credentials
from .calendar import fully_inside_rth, schedule, stock_qa
from .config import atomic_new, load_config, now, write_json
from .course import audit_course, save_course_audit
from .pilot import load_pilot_samples, pilot_requests, run_pilot
from .store import acquire, check_approval, load_store, plan


def runtime(cfg: dict) -> dict:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cfg["_root"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"
    return {
        "created_at": now(),
        "git_sha": sha,
        "python": platform.python_version(),
        "packages": {
            name: version(name)
            for name in (
                "lstm-market-data",
                "numpy",
                "pandas",
                "pyarrow",
                "exchange-calendars",
                "requests",
                "python-dotenv",
            )
        },
        "config_fingerprint": cfg["_fingerprint"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_data.json"))
    parser.add_argument("--env-file", type=Path, help="Explicit local ignored .env; never printed")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("source-audit", "Inspect original USA500 CSV without modifying bytes"),
        ("sip-pilot", "Small SIP entitlement/DST/early-close/split probes"),
        ("download", "Gated, resumable monthly canonical stock acquisition"),
        ("stock-qa", "Validate verified stock store against historical XNYS sessions"),
        ("alignment", "Audit-only backward as-of availability scenarios"),
    ):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--dry-run", action="store_true", help="No network or writes")
        command.add_argument("--output", type=Path, help="New report directory; never overwritten")
        if name == "download":
            command.add_argument("--approval", type=Path, help="Explicit reviewed approval JSON")
        if name == "alignment":
            command.add_argument(
                "--pilot-report",
                type=Path,
                help="Use checksum-verified small pilot samples instead of store",
            )
            command.add_argument(
                "--max-age-minutes",
                type=int,
                default=90,
                help="Audit sensitivity only; not an approved model rule",
            )
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    if args.dry_run:
        dry = plan(cfg)
        dry["command"] = args.command
        if args.command == "sip-pilot":
            dry["requests"] = pilot_requests(cfg)
            dry["minimum_initial_calls"] = len(dry["requests"])
            dry["pilot_rows_upper_estimate"] = 24 * sum(
                len(schedule(p["start_date"], p["end_date"])) for p in dry["requests"]
            )
            dry["paths_touched_on_execution"] = [cfg["report_dir"], "data/interim/alpaca_pilot"]
        elif args.command != "download":
            dry["requests"] = []
            dry["minimum_initial_calls"] = 0
            dry["paths_touched_on_execution"] = [cfg["report_dir"]]
            dry["inputs_read_on_execution"] = (
                [cfg["course_source"]]
                if args.command == ("source-audit")
                else [cfg["stock_store"], cfg["course_source"]]
            )
        print(json.dumps(dry, indent=2))
        return 0
    stamp = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d_%H%M%S_%f")
    output = args.output or cfg["_report_dir"] / f"{stamp}_{args.command}"
    if output.exists():
        raise FileExistsError("Report directory exists; choose a new output path")
    if args.env_file:
        if not args.env_file.is_file():
            raise FileNotFoundError("Requested local .env file missing")
        load_dotenv(args.env_file, override=False)
    client = None
    if args.command == "sip-pilot":
        report = run_pilot(cfg, output)
        write_json(output / "runtime.json", runtime(cfg))
        print(f"Pilot: {report['status']}; report: {output / 'sip_pilot.md'}")
        return 0 if report["timing_gate_pass"] else 2
    output.mkdir(parents=True)
    write_json(output / "runtime.json", runtime(cfg))
    try:
        if args.command == "source-audit":
            _, audit = audit_course(
                cfg["_course_source"], cfg["course_provider"], cfg["start_date"], cfg["end_date"]
            )
            save_course_audit(output, audit)
        elif args.command == "download":
            if not args.approval:
                raise ValueError(
                    "Bulk blocked: --approval plus successful SIP/timing pilot required"
                )
            check_approval(cfg, args.approval)
            key, secret = credentials()
            client = HistoricalClient(cfg, key, secret)
            results = acquire(cfg, client, args.approval)
            write_json(output / "download.json", results)
        elif args.command == "stock-qa":
            frame = load_store(cfg)
            qa = stock_qa(frame, cfg["symbols"], cfg["start_date"], cfg["end_date"])
            # Keep small tracked evidence: daily records with issues plus selected
            # calendar examples, rather than thousands of repeated healthy grids.
            selected_days = {
                cfg["start_date"],
                cfg["end_date"],
                "2020-10-30",
                "2020-11-02",
                "2020-11-27",
                "2021-03-12",
                "2021-03-15",
            }
            qa["daily_sessions_audited"] = len(qa["daily"])
            qa["daily"] = [
                day
                for day in qa["daily"]
                if day["missing_expected_starts_utc"]
                or day["extra_overlapping_starts_utc"]
                or day["partial_overlap_count"]
                or day["session"] in selected_days
                or day["early_close"]
            ]
            qa["daily_output_policy"] = (
                "Issues, early closes and representative calendar days; "
                "all sessions audited and summarized"
            )
            write_json(output / "stock_qa.json", qa)
            atomic_new(
                output / "stock_qa.md",
                (
                    "# Stock QA\n\nInspect stock_qa.json for "
                    "per-symbol coverage and per-session grids. Missing desired starts are "
                    "not automatically missing provider data.\n"
                ).encode(),
            )
        elif args.command == "alignment":
            stocks = (
                load_pilot_samples(cfg, args.pilot_report) if args.pilot_report else load_store(cfg)
            )
            course, _ = audit_course(
                cfg["_course_source"], cfg["course_provider"], cfg["start_date"], cfg["end_date"]
            )
            results = []
            panels = [
                ("all_native_source_bars", stocks),
                (
                    "native_source_bars_inside_rth",
                    fully_inside_rth(stocks, cfg["start_date"], cfg["end_date"]),
                ),
            ]
            if cfg["timeframe"] == "30Min":
                if args.pilot_report:
                    pilot_metadata = json.loads(args.pilot_report.read_text())
                    hourly_parts = []
                    for probe in pilot_metadata["requests"]:
                        params = probe["params"]
                        panel = stocks[
                            (stocks.timestamp >= pd.Timestamp(params["start"]))
                            & (stocks.timestamp <= pd.Timestamp(params["end"]))
                            & stocks.symbol.isin(params["symbols"].split(","))
                        ]
                        part, _ = aggregate_session_hours(
                            panel,
                            params["symbols"].split(","),
                            probe["start_date"],
                            probe["end_date"],
                        )
                        hourly_parts.append(part)
                    hours = pd.concat(hourly_parts, ignore_index=True).sort_values(
                        ["symbol", "timestamp"]
                    )
                else:
                    hours, _ = aggregate_session_hours(
                        stocks, cfg["symbols"], cfg["start_date"], cfg["end_date"]
                    )
                panels.append(("session_anchored_hourly_with_stubs", hours))
            for label, panel in panels:
                for delay in (0, 60):
                    _, summary = asof_diagnostic(
                        panel,
                        course,
                        index_delay_minutes=delay,
                        stock_delay_minutes=30 if cfg["timeframe"] == "30Min" else 60,
                        max_age_minutes=args.max_age_minutes,
                    )
                    summary["sample_policy"] = label
                    summary["researcher_assumption"] = cfg["course_availability_assumption"]
                    results.append(summary)
            write_json(output / "alignment.json", results)
            atomic_new(
                output / "alignment.md",
                (
                    "# Alignment diagnostic\n\n"
                    + json.dumps(results, indent=2)
                    + "\n\nProvisional course close assumption approved; "
                    "final feature join unset.\n"
                ).encode(),
            )
    except (DataAccessError, ValueError, FileNotFoundError) as error:
        write_json(
            output / "failure.json",
            {
                "status": "blocked",
                "diagnostic": str(error),
                "events": client.events if client else [],
            },
        )
        print(str(error), file=sys.stderr)
        return 2
    print(f"Reports: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from None
