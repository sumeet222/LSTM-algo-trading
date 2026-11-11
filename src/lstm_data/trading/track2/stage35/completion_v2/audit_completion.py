"""Read-only final coverage, prior witness and protected-byte verification."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ...stage012.historical_source_store import file_hash
from ...stage012.model_registry import SYMBOLS
from .cache import ROOT, publish


def audit(signals: Path, report: Path, output: Path) -> None:
    summary = json.loads(report.read_text())
    totals = {k: 0 for k in summary["totals"]}
    frames = []
    for item in summary["partitions"]:
        path = Path(item["path"])
        if file_hash(path) != item["sha256"]:
            raise ValueError("PARTITION_IDENTITY")
        data = pd.read_parquet(path)
        frames.append(data)
        for key in totals:
            totals[key] += item[key]
        if len(data) != item["rows"] or set(data.ticker) != set(SYMBOLS):
            raise ValueError("SILENT_UNIVERSE_LOSS")
        if (
            not (data.issued_at >= data.feature_ready).all()
            or not (data.earliest_entry_marker > data.issued_at).all()
        ):
            raise ValueError("SIGNAL_CLOCK")
        for _, stock in data.groupby("ticker"):
            good = stock.loc[stock.input_eligible]
            if not good.empty:
                first = good.issued_at.min()
                frozen = stock.loc[stock.issued_at >= first]
                if not (frozen.sign_frozen_at == first).all() or frozen.direction.nunique() != 1:
                    raise ValueError("SESSION_FREEZE")
            for name in ("EQUAL", "S2C_RISK", "ROLLING_RISK", "EWMA_RISK"):
                values = stock["g_" + name].dropna()
                if not values.between(0.5, 1.5).all():
                    raise ValueError("SIZE_CLIP")
        ready = data.loc[data.g_ROLLING_RISK.notna()]
        if (
            not ready.empty
            and not (
                pd.to_datetime(ready.control_latest_available, utc=True) < ready.issued_at
            ).all()
        ):
            raise ValueError("CONTROL_FRONTIER")
        forbidden = {
            "future_return",
            "future_price",
            "P_e",
            "F09",
            "cash",
            "nav",
            "pnl",
            "execution_price",
            "fill_price",
        }
        if forbidden & set(data.columns):
            raise ValueError("FINANCIAL_OR_LABEL_OUTPUT")
    if totals != summary["totals"]:
        raise ValueError("COUNT_RECONCILIATION")
    all_rows = pd.concat(frames, ignore_index=True)
    old = json.loads(
        Path("trading/track2/stage35/audits/H4_signals_v1/signal_intents.json").read_text()
    )
    parity = []
    for record in old:
        origin = pd.Timestamp(record["key"]["origin_utc"])
        ticker = record["key"]["ticker"]
        shared = all_rows.loc[(all_rows.origin == origin) & (all_rows.ticker == ticker)]
        if len(shared) != 1 or not shared.iloc[0].input_eligible:
            raise ValueError("H4_WITNESS_KEY_LOST")
        actual = float(shared.iloc[0].magnitude_c3)
        expected = float(record["signal"]["calibrated_magnitude"])
        np.testing.assert_allclose(actual, expected, atol=1e-7, rtol=1e-5)
        parity.append(
            {"ticker": ticker, "origin": str(origin), "abs_difference": abs(actual - expected)}
        )
    protected = json.loads((ROOT / "audits/H0_inventory.json").read_text())["protected"]
    changed = []
    for item in protected:
        path = Path(item["path"])
        if file_hash(path) != item["sha256"] or path.stat().st_mtime_ns != item["mtime_ns"]:
            changed.append(str(path))
    source_receipts = json.loads((ROOT / "audits/cache/source_receipts.json").read_text())
    source_changed = []
    for item in source_receipts:
        path = Path(item["path"])
        if file_hash(path) != item["sha256"] or path.stat().st_mtime_ns != item["mtime_ns"]:
            source_changed.append(str(path))
    if changed or source_changed:
        raise ValueError("IMMUTABILITY_VIOLATION:" + str(changed + source_changed))
    by = []
    for group_key, group in all_rows.groupby(["fold", "ticker"]):
        if not isinstance(group_key, tuple) or len(group_key) != 2:
            raise ValueError("GROUP_SCHEMA")
        fold, ticker = group_key
        by.append(
            {
                "fold": fold,
                "ticker": ticker,
                "opportunities": len(group),
                "forecasts": int(group.input_eligible.sum()),
                "input_missing": int((~group.input_eligible).sum()),
                "s2c": int(group.g_S2C_RISK.notna().sum()),
                "rolling": int(group.g_ROLLING_RISK.notna().sum()),
            }
        )
    publish(
        output,
        {
            "status": "PASS",
            "final_report": str(report),
            "report_sha256": file_hash(report),
            "protected_objects": len(protected),
            "protected_changed": changed,
            "source_partitions": len(source_receipts),
            "source_changed": source_changed,
            "totals": totals,
            "fold_ticker_coverage": by,
            "H4_shared_keys": parity,
            "archived_original_parity": "HISTORICAL_PREDICTION_PARITY_NOT_COMPARABLE",
            "historical_financial_outputs": False,
            "unique_opportunities": len(all_rows),
            "resume_identities": file_hash(signals / "RUN_BINDING.json"),
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signals", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.signals, args.report, args.output)
