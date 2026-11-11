"""Bounded cross-fold INPUT-ONLY original inference. Never imports accountant/execution."""

import argparse
import csv
import json
from dataclasses import asdict
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from ..stage012.calendar_schedule import MarketClock
from ..stage012.historical_input_only import BASIS, Abstention, OriginalInputOnlySnapshotProducer
from ..stage012.historical_source_store import HistoricalSourceStore, file_hash
from ..stage012.model_registry import ModelRegistry
from ..stage012.original_feature_pure import cached_endpoint, cached_origins
from ..stage012.risk_reference_prepare import load_reference
from ..stage012.sign_scheduler import SessionSignScheduler, scheduled_signal
from .intents import from_signal

ROOT = Path("trading/track2/stage35")
SAMPLES = (
    (2021, "2021-01-08", "2021-11-26"),
    (2022, "2022-01-10", "2022-11-25"),
    (2023, "2023-01-09", "2023-11-24"),
    (2024, "2024-01-08", "2024-11-29"),
)


def prepare_plan(path: Path) -> None:
    if path.exists():
        raise ValueError("APPEND_ONLY_PLAN")
    clock = MarketClock("2010-07-01", "2025-01-10")
    keys = set()
    samples = []
    regular = clock.calendar.loc[
        (clock.calendar.close - clock.calendar.open) == pd.Timedelta(minutes=390)
    ]
    for year, normal, half in SAMPLES:
        for day, hour in ((normal, 10), (half, 9)):
            origin = datetime.fromisoformat(day + f"T{hour:02}:30").replace(
                tzinfo=ZoneInfo("America/New_York")
            )
            context = 0 if hour == 10 else 6
            for ticker in ("AAPL", "COP"):
                samples.append(
                    {
                        "year": year,
                        "ticker": ticker,
                        "origin_utc": origin.astimezone(ZoneInfo("UTC")).isoformat(),
                    }
                )
            for input_day in {
                str(t.astimezone(ZoneInfo("America/New_York")).date())
                for t in clock.full_hour_slots(origin)
            }:
                day_open = clock.calendar.loc[input_day:input_day].iloc[0]["open"].to_pydatetime()
                previous = [str(d.date()) for d in regular.index if str(d.date()) < input_day][-60:]
                for d in previous:
                    times = cached_origins(clock, d)
                    t = times[0 if context == 6 else 1]
                    end = cached_endpoint(clock, t)
                    if end + timedelta(minutes=2) < day_open:
                        keys.add(t if context == 6 else t - timedelta(minutes=1))
                        keys.add(end - timedelta(minutes=1))
            if hour == 9:
                keys.add(origin)
    rows = list(
        csv.DictReader(
            Path(
                "reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv"
            ).open()
        )
    )
    by_path = {r["path"]: r for r in rows}
    sources = []
    for month in pd.period_range("2010-07", "2024-11", freq="M").astype(str):
        name = (
            "data/processed/hf20_hf1m_long_v1_action_qa_v1/"
            f"ta019b_action_qa_2026-10-22_201224/hourly/{month}.parquet"
        )
        sources.append({"path": name, "sha256": by_path[name]["sha256"], "role": "hourly_replay"})
    for month in sorted(
        {t.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m") for t in keys}
    ):
        name = (
            "data/processed/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/"
            f"qa_v2/canonical_observed/{month}.parquet"
        )
        sources.append({"path": name, "sha256": by_path[name]["sha256"], "role": "m2_source"})
    payload = {
        "kind": "STAGE35_INPUT_ONLY_NO_ECONOMICS",
        "samples": samples,
        "signal_tickers": ["AAPL", "COP"],
        "risk_tickers": [],
        "minute_keys": {"m2_source": sorted(t.isoformat() for t in keys), "risk_prefix": []},
        "sources": sources,
        "selection": "calendar-declared dates,not outcome/score membership",
        "max_forecast_keys": 16,
        "receipt_minutes": 2,
        "expected_output": (
            "SignalRecord,SignalIntent,CausalFeatureAudit OR keyed abstention;"
            "no prices/orders/fills/positions/financial PnL"
        ),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")
    seal = {
        "path": str(path),
        "sha256": file_hash(path),
        "market_values_read_before_seal": False,
        "keys": len(samples),
        "partitions": len(sources),
    }
    path.with_suffix(".seal.json").write_text(json.dumps(seal, indent=2) + "\n")


def run(plan_path: Path, expected_hash: str, output: Path) -> None:
    if output.exists():
        raise ValueError("APPEND_ONLY_EXPANSION")
    store = HistoricalSourceStore(Path("."), plan_path, expected_hash)
    if len(store.plan["samples"]) > 16 or store.plan["signal_tickers"] != ["AAPL", "COP"]:
        raise ValueError("UNREVIEWED_LARGE_EXPANSION_FORBIDDEN")
    output.mkdir(parents=True)
    facts_path = Path("configs/hf1m_p019_verified_event_facts_v1.json")
    qa = json.loads(Path("configs/hf1m_action_qa_v1.json").read_text())
    if file_hash(facts_path) != qa["facts_sha256"]:
        raise ValueError("ORIGINAL_ACTION_IDENTITY")
    facts = json.loads(facts_path.read_text())["events"]
    clock = MarketClock("2010-07-01", "2025-01-10")
    print("Reading sealed own-stock source projection", flush=True)
    producer = OriginalInputOnlySnapshotProducer(
        store.hours(), store.minutes("m2_source", facts), facts, clock, store.inventory_hash
    )
    scheduler = SessionSignScheduler(clock)
    registry = ModelRegistry(Path("."), Path("trading/track2/stage012/original_bundles.json"))
    risk_path = Path(
        "trading/track2/stage012/audits/completion_v1/historical_run_v1/RISK_REFERENCE_MANIFEST.json"
    )
    receipt = json.loads(risk_path.with_name("risk_preparation_receipt.json").read_text())
    models = {}
    records = []
    lineages = []
    for key in store.plan["samples"]:
        year = key["year"]
        ticker = key["ticker"]
        origin = datetime.fromisoformat(key["origin_utc"])
        slot = origin.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M")
        if year not in models:
            models[year] = registry.load(year)
        reference = load_reference(
            risk_path,
            f"F{year % 100}",
            ticker,
            slot,
            BASIS,
            receipt["checksum"],
            receipt["inventory_hash"],
        )
        result = scheduled_signal(producer, models[year], scheduler, ticker, origin, reference)
        if isinstance(result, Abstention):
            records.append({"key": key, "abstention": asdict(result)})
            print("ABSTAIN", key, result.reason, flush=True)
            continue
        signal, audit, frozen = result
        lineages.append(asdict(audit))
        if signal.direction:
            intent = from_signal(
                signal,
                "S2C_RISK",
                Decimal(str(signal.size_multiplier)),
                reference.lineage,
                audit.input_hash,
            )
            records.append(
                {
                    "key": key,
                    "signal": json.loads(signal.to_json()),
                    "intent": asdict(intent),
                    "session_sign_hash": frozen.lineage_hash,
                }
            )
        else:
            records.append(
                {
                    "key": key,
                    "signal": json.loads(signal.to_json()),
                    "intent_abstention": "FROZEN_ZERO_OR_MISSING_SESSION_SIGN",
                }
            )
        print(
            "SIGNAL",
            year,
            ticker,
            origin.isoformat(),
            signal.calibrated_magnitude,
            signal.direction,
            flush=True,
        )

    def default(obj: object) -> str:
        return obj.isoformat() if isinstance(obj, datetime) else str(obj)

    (output / "signal_intents.json").write_text(
        json.dumps(records, indent=2, default=default) + "\n"
    )
    (output / "feature_lineage.json").write_text(
        json.dumps(lineages, indent=2, default=default) + "\n"
    )
    (output / "source_reads.json").write_text(json.dumps(store.reads, indent=2) + "\n")
    summary = {
        "plan_sha256": expected_hash,
        "keys": len(records),
        "source_eligible_signals": sum("signal" in r for r in records),
        "intents": sum("intent" in r for r in records),
        "source_abstentions": sum("abstention" in r for r in records),
        "orders": 0,
        "fills": 0,
        "positions": 0,
        "pnl": 0,
        "folds": sorted(models),
    }
    (output / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-plan", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--plan-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.prepare_plan:
        prepare_plan(args.prepare_plan)
    elif args.plan and args.plan_sha256 and args.output:
        run(args.plan, args.plan_sha256, args.output)
    else:
        parser.error("prepare-plan OR plan/plan-sha256/output required")


if __name__ == "__main__":
    main()
