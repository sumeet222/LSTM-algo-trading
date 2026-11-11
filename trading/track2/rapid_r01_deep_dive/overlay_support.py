"""Audit same-origin availability from sealed signal rows, without sizing or trading."""

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from math import isfinite
from pathlib import Path

import pyarrow.parquet as pq

from lstm_data.trading.track2.rapid_v1.paths import digest, publish
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS

COVERAGE = Path("trading/track2/stage35/completion_v2/FULL_SIGNAL_COVERAGE_REPORT.json")
RISK = Path(
    "trading/track2/stage012/audits/completion_v1/historical_run_v1/RISK_REFERENCE_MANIFEST.json"
)
COLUMNS = [
    "ticker",
    "origin",
    "feature_ready",
    "issued_at",
    "source_latest_completed",
    "magnitude_c3",
    "input_eligible",
    "rolling_scale",
    "ewma_scale",
    "control_latest_available",
    "control_count",
    "risk_reference",
]


def minute(value: datetime | str) -> int:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is None or value.second or value.microsecond:
        raise ValueError("NAIVE_OVERLAY_TIMESTAMP")
    return int(value.timestamp()) // 60


def audit(opportunities: Path, output: Path) -> None:
    with opportunities.open(newline="") as stream:
        wanted = {(int(r["origin"]), SYMBOLS[int(r["ticker"])]): r for r in csv.DictReader(stream)}
    dates = {r["date"] for r in wanted.values()}
    coverage = json.loads(COVERAGE.read_text())
    risk = json.loads(RISK.read_text())
    counts: dict[str, Counter] = {}
    seen = set()
    bound = {}
    for partition in coverage["partitions"]:
        if partition["date"] not in dates:
            continue
        path = Path(partition["path"])
        if digest(path) != partition["sha256"]:
            raise ValueError(f"ARCHIVED_SIGNAL_DRIFT {path}")
        bound[str(path)] = partition["sha256"]
        for row in pq.read_table(path, columns=COLUMNS).to_pylist():
            key = minute(row["origin"]), row["ticker"]
            if key not in wanted:
                continue
            if key in seen or row["risk_reference"] != risk["sha256"]:
                raise ValueError("OVERLAY_REFERENCE_OR_IDENTITY")
            seen.add(key)
            prior = wanted[key]
            decision = int(prior["decision"])
            count = counts.setdefault(prior["date"][:4], Counter())
            count["R01_candidate"] += 1
            count["R01_calendar_admissible"] += prior["calendar_admissible"] == "True"
            ready = (
                minute(row["feature_ready"]) <= decision
                and minute(row["issued_at"]) <= decision
                and minute(row["source_latest_completed"]) + 2 <= decision
            )
            valid_mag = (
                ready
                and row["input_eligible"]
                and row["magnitude_c3"] is not None
                and isfinite(row["magnitude_c3"])
                and row["magnitude_c3"] >= 0
            )
            count["causal_C3_magnitude_at_R01_decision"] += bool(valid_mag)
            control = (
                ready
                and row["rolling_scale"] is not None
                and row["ewma_scale"] is not None
                and row["control_count"] >= 40
                and row["control_latest_available"] is not None
                and minute(row["control_latest_available"]) <= decision
            )
            count["archived_control_pair_lower_bound"] += bool(control)
            count["joint_magnitude_and_archived_pair_lower_bound"] += bool(valid_mag and control)
    if seen != set(wanted):
        raise ValueError("OVERLAY_ORIGIN_CENSUS")
    publish(
        output,
        {
            "status": "INPUT_ONLY_ALIGNMENT",
            "opportunity_sha256": digest(opportunities),
            "coverage_sha256": digest(COVERAGE),
            "risk_reference_sha256": digest(RISK),
            "partition_sha256": bound,
            "counts_by_year": counts,
            "caveat": "Archived control scales are masked by legacy sign and model eligibility.",
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opportunities", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    audit(args.opportunities, args.output)
