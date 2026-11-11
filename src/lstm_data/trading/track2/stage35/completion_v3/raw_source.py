"""Sealed projected raw-minute source; never supplies model-adjusted cash prices."""

import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd

from ..common import RAW
from ..completion_v2.tapes import RawObservation
from .acquire import ROOT, write_once
from .event_ledger import after_bar
from .inventory import digest


def audit_raw(root: Path = ROOT) -> tuple[RawObservation, ...]:
    path = root / "BOUNDED_ECONOMIC_SOURCE_PLAN_V3.json"
    plan = json.loads(path.read_text())
    seal = json.loads(path.with_suffix(".seal.json").read_text())
    if digest(path) != seal["sha256"]:
        raise ValueError("SOURCE_PLAN_SEAL_CHANGED")
    allowed = {(key["symbol"], pd.Timestamp(key["at"])) for key in plan["keys"]}
    observations = []
    reads = []
    missing = []
    for source in plan["sources"]:
        part = Path(source["path"])
        if (
            part.is_absolute()
            or ".." in part.parts
            or part.stem > "2024-12"
            or "canonical_observed" not in part.parts
            or digest(part) != source["sha256"]
        ):
            raise ValueError("RAW_SOURCE_SCOPE_OR_IDENTITY")
        keys = {(symbol, at) for symbol, at in allowed if at.strftime("%Y-%m") == part.stem}
        frame = pd.read_parquet(
            part,
            columns=plan["columns"],
            filters=[
                ("ticker", "in", sorted({symbol for symbol, _ in keys})),
                ("timestamp", "in", [at for _, at in keys]),
                ("is_rth", "==", True),
            ],
        )
        seen = set()
        for row in frame.to_dict("records"):
            at = datetime.fromisoformat(row["timestamp"].isoformat())
            key = (row["ticker"], pd.Timestamp(at))
            if key not in keys:
                continue
            if key in seen:
                raise ValueError("DUPLICATE_RAW_MINUTE")
            seen.add(key)
            complete, available = after_bar(at)
            obs = RawObservation(
                row["ticker"],
                at,
                complete,
                available,
                Decimal(str(row["open"])),
                Decimal(str(row["high"])),
                Decimal(str(row["low"])),
                Decimal(str(row["close"])),
                Decimal(str(row["volume"])),
                RAW,
                source["sha256"],
                "ORIGINAL_OBSERVED",
            )
            obs.validate()
            observations.append(obs)
        missing.extend(
            {"symbol": symbol, "at": at.isoformat(), "status": "SOURCE_MINUTE_ABSENT"}
            for symbol, at in sorted(keys - seen)
        )
        reads.append(
            {
                **source,
                "projected_rows": len(seen),
                "columns": plan["columns"],
                "source_kind": "ACTUAL_HISTORICAL_RAW_NOT_SYNTHETIC",
            }
        )
    observations.sort(key=lambda obs: (obs.available, obs.ticker))
    write_once(
        root / "audits/RAW_SOURCE_FIXTURES_V3.json",
        {
            "plan_sha256": seal["sha256"],
            "reads": reads,
            "observations": [asdict(o) for o in observations],
            "missing": missing,
            "projected_rows": len(observations),
            "economic_trades": 0,
            "financial_wealth_computed": False,
            "basis": "RAW_SHARE via original pre-adjust_prices canonical lineage;not PIT certified",
        },
    )
    # Certify identities/schema family for all OOS partitions without scanning their values.
    old = json.loads(
        Path("trading/track2/stage35/completion_v2/audits/cache/source_receipts.json").read_text()
    )
    partitions = [
        item
        for item in old
        if item["family"] == "minute" and "2021-01" <= Path(item["path"]).stem <= "2024-12"
    ]
    for item in partitions:
        part = Path(item["path"])
        if digest(part) != item["sha256"] or part.stat().st_mtime_ns != item["mtime_ns"]:
            raise ValueError("PRIOR_RAW_PARTITION_CHANGED")
    write_once(
        root / "RAW_SHARE_SOURCE_COVERAGE_V3.json",
        {
            "oos_minute_partitions": len(partitions),
            "partitions": partitions,
            "certification_scope": (
                "source lineage and immutable bytes;11 projected value checks only"
            ),
            "raw_basis": "ORIGINAL_OBSERVED_PRE_ADJUST_PRICES",
            "model_hourly_basis": "SPLIT_ADJUSTED_FORBIDDEN_FOR_LEDGER",
            "source_quarantine_sha256": digest(Path(plan["quarantine"])),
            "prior_quarantine_policy": "unchanged;retrospective QA not live-available knowledge",
            "full_every_bar_validation": "ON_INGESTION_REQUIRED;not a new panel scan",
            "PIT_corporate_action_certification": False,
            "bounded_rows": len(observations),
            "missing_fixture_rows": missing,
        },
    )
    return tuple(observations)


if __name__ == "__main__":
    audit_raw()
