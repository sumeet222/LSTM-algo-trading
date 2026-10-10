"""Small historical SIP entitlement/timing probes; never a bulk download."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pandas as pd

from .aggregation import aggregate_session_hours
from .alpaca import DataAccessError, HistoricalClient, credentials, request_params
from .calendar import stock_qa
from .config import atomic_new, digest, now, public_config, write_json
from .validation import normalize, require_valid

PROBES = [
    ("historical_2020", "AAPL", "2020-07-01", "2020-07-10"),
    ("historical_2025", "AAPL", "2025-06-23", "2025-06-30"),
    ("fall_dst", "AAPL", "2020-10-30", "2020-11-02"),
    ("spring_dst", "AAPL", "2021-03-12", "2021-03-15"),
    ("early_close", "AAPL", "2020-11-27", "2020-11-27"),
    ("aapl_split_window", "AAPL", "2020-08-28", "2020-09-01"),
    ("wmt_split_window", "WMT", "2024-02-23", "2024-02-27"),
]


def load_pilot_samples(cfg: dict, report_path: Path) -> pd.DataFrame:
    """Load byte-verified pilot samples, refusing mixed config or unknown paths."""
    report = json.loads(report_path.read_text())
    if report.get("config_fingerprint") != cfg["_fingerprint"]:
        raise ValueError("Pilot config fingerprint differs")
    frames = []
    for probe in report["probes"]:
        relative = Path(probe["sample_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Pilot samples must be project-relative")
        path = cfg["_root"] / relative
        if digest(path) != probe["sample_sha256"]:
            raise ValueError("Pilot sample checksum changed")
        frames.append(normalize(pd.read_parquet(path), stocks=True))
    if not frames:
        raise FileNotFoundError("Pilot has no downloaded samples")
    result = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])
    require_valid(result, stocks=True)
    return result


def pilot_requests(cfg: dict) -> list[dict]:
    result = []
    for name, symbol, start, end in PROBES:
        lower = pd.Timestamp(start, tz=cfg["timezone"]).tz_convert("UTC")
        upper = (pd.Timestamp(end, tz=cfg["timezone"]) + pd.DateOffset(days=1)).tz_convert(
            "UTC"
        ) - pd.Timedelta(nanoseconds=1)
        result.append(
            {
                "name": name,
                "start_date": start,
                "end_date": end,
                "params": request_params(cfg, [symbol], lower.isoformat(), upper.isoformat()),
            }
        )
    return result


def run_pilot(cfg: dict, output: Path, client: HistoricalClient | None = None) -> dict:
    """Save redacted evidence, including an honest missing-credentials/entitlement status."""
    report = {
        "created_at": now(),
        "config_fingerprint": cfg["_fingerprint"],
        "config": public_config(cfg),
        "sip_access_pass": False,
        "timing_gate_pass": False,
        "status": "not_started",
        "probes": [],
        "requests": pilot_requests(cfg),
        "events": [],
        "sample_storage_bytes": 0,
        "adjustment_implications": "Split adjusts historical price and volume retrospectively. "
        "No dividend total-return adjustment. Levels are not point-in-time "
        "vintages. Corporate-action reference/event audit still needed.",
    }
    if output.exists():
        raise FileExistsError("Pilot output exists; choose a new run directory")
    output.mkdir(parents=True)
    try:
        if client is None:
            key, secret = credentials()
            client = HistoricalClient(cfg, key, secret)
        for probe in pilot_requests(cfg):
            frame = client.bars(probe["params"])
            qa = stock_qa(
                frame, probe["params"]["symbols"].split(","), probe["start_date"], probe["end_date"]
            )
            aggregation = None
            if cfg["timeframe"] == "30Min":
                _, aggregation = aggregate_session_hours(
                    frame,
                    probe["params"]["symbols"].split(","),
                    probe["start_date"],
                    probe["end_date"],
                )
            sample_path = (
                cfg["_root"]
                / "data/interim/alpaca_pilot"
                / output.name
                / (probe["name"] + ".parquet")
            )
            buffer = io.BytesIO()
            frame.to_parquet(buffer, index=False, compression="zstd")
            atomic_new(sample_path, buffer.getvalue())
            report["sample_storage_bytes"] += sample_path.stat().st_size
            report["probes"].append(
                {
                    "name": probe["name"],
                    "qa": qa,
                    "aggregation": aggregation,
                    "sample_path": str(sample_path.relative_to(cfg["_root"])),
                    "sample_sha256": digest(sample_path),
                }
            )
        report["sip_access_pass"] = all(
            any(s["rows"] > 0 for s in item["qa"]["symbols"].values()) for item in report["probes"]
        )
        report["timing_gate_pass"] = report["sip_access_pass"] and all(
            (
                item["aggregation"]["timing_gate_pass"]
                if item["aggregation"] is not None
                else item["qa"]["native_session_anchored_gate_pass"]
            )
            for item in report["probes"]
        )
        report["status"] = "passed" if report["timing_gate_pass"] else "blocked_timing_or_coverage"
    except (DataAccessError, ValueError) as error:
        report["status"] = "blocked_access_or_schema"
        # Only application-generated safe errors are retained; no HTTP body or headers.
        report["diagnostic"] = str(error)
    finally:
        if client is not None:
            report["events"] = client.events
    write_json(output / "sip_pilot.json", report)
    lines = [
        "# SIP feasibility pilot",
        "",
        f"Status: **{report['status']}**.",
        "",
        f"SIP access passed: {report['sip_access_pass']}. "
        f"Source/aggregation timing gate passed: {report['timing_gate_pass']}.",
        "",
        report.get("diagnostic", "All selected probe requests consumed to final page."),
        "",
        "| Probe | Symbol | Rows | Missing desired starts | Partial overlaps |",
        "|---|---|---:|---:|---:|",
    ]
    for item in report["probes"]:
        for symbol, qa in item["qa"]["symbols"].items():
            lines.append(
                f"| {item['name']} | {symbol} | {qa['rows']} | "
                f"{qa['missing_session_anchored_starts']} | "
                f"{qa['partial_session_overlap_bars']} |"
            )
    if cfg["timeframe"] == "30Min":
        lines += [
            "",
            "## Approved 30Min aggregation evidence",
            "",
            "| Probe | Hourly windows including stubs | Missing constituents | Stubs |",
            "|---|---:|---:|---:|",
        ]
        for item in report["probes"]:
            qa = item["aggregation"]
            lines.append(
                f"| {item['name']} | {qa['rows']} | {qa['missing_source_bars']} | "
                f"{qa['expected_stub_windows']} |"
            )
    lines += [
        "",
        f"Storage used for small pilot samples: {report['sample_storage_bytes']} bytes.",
        "",
        report["adjustment_implications"],
        "",
        "If native hours fail, recommended next controlled pilot: approved 30Min source "
        "bars combined into 09:30-anchored 60-minute windows, retaining the final 30-minute "
        "stub. Roughly twice the source rows; see bulk dry-run estimate. Do not shift native "
        "hours or proceed with bulk, IEX, a subscription, or 1-minute history.",
        "",
        "This implementation deliberately refuses native-hour bulk when closing stubs or "
        "opening overlaps cannot be established from provider aggregates. A 30Min change "
        "requires researcher approval, implementation and a fresh pilot.",
        "",
    ]
    atomic_new(output / "sip_pilot.md", "\n".join(lines).encode())
    return report
