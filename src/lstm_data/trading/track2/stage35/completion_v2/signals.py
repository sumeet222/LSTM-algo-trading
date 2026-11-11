"""Resumable all-universe ORIGINAL-model input-only inference and mature controls.

No accountant,order executor,financial return or F09/evaluation reader is imported.
Derived movement tape is read only through the strict endpoint-receipt frontier.
"""

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from lstm_data.hf20_mag_c3_io import decode
from lstm_data.hf20_s4_witnesses import assemble
from lstm_data.hf20_stage2_bcd import clock_values

from ...stage012.calendar_schedule import MarketClock
from ...stage012.historical_input_only import Abstention, OriginalInputOnlySnapshotProducer
from ...stage012.historical_source_store import file_hash
from ...stage012.model_registry import SYMBOLS, ModelRegistry
from .cache import REV, Sources, geometry, ns, publish


def verify_cache(cache: Path, plan_hash: str) -> dict:
    manifest = json.loads((cache / "CACHE_READY.json").read_text())
    if manifest["version"] != REV or manifest["plan_sha256"] != plan_hash:
        raise ValueError("CACHE_VERSION_OR_PLAN")
    for row in manifest["identities"]:
        if file_hash(cache / row["path"]) != row["sha256"]:
            raise ValueError("CACHE_IDENTITY:" + row["path"])
    return manifest


class Inputs:
    def __init__(self, cache: Path, year: int):
        self.grid = pd.read_parquet(cache / "grid.parquet")
        self.end_ns = ns(self.grid.hour_end_utc)
        self.common = np.load(cache / f"{year}_common.npy", mmap_mode="r")
        self.m2 = np.load(cache / f"{year}_m2.npy", mmap_mode="r")
        self.valid = np.load(cache / "input_valid.npy", mmap_mode="r")
        self.close = np.load(cache / "genuine_close.npy", mmap_mode="r")
        self.opens = pd.read_parquet(cache / "opening_refs.parquet")
        self.missing = np.load(cache / f"{year}_missing_common.npy", mmap_mode="r")
        self.missing_m2 = np.load(cache / f"{year}_missing_m2.npy", mmap_mode="r")

    def rows(self, rows: pd.DataFrame) -> pd.DataFrame:
        r = rows.copy()
        r["entry_index"] = np.searchsorted(self.end_ns, ns(r.entry_end_utc), side="right") - 1
        r["first_step"] = r.entry_index - 47
        return r

    def x(self, rows: pd.DataFrame) -> np.ndarray:
        return assemble(self.rows(rows), self.common, self.m2)

    def eligible(self, row: pd.Series) -> np.ndarray:
        idx = int(
            np.searchsorted(
                self.end_ns, pd.Timestamp(str(row["entry_end_utc"])).value, side="right"
            )
            - 1
        )
        result = self.valid[idx].copy()
        if row["slot"] == "09:30":
            current = (
                self.opens.loc[self.opens.timestamp == row["entry_end_utc"]]
                .set_index("ticker")
                .open.reindex(SYMBOLS)
                .to_numpy(float)
            )
            result &= np.isfinite(current) & (current > 0)
        return result

    def trend(self, clock: MarketClock, day: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
        previous = [
            str(pd.Timestamp(str(d)).date())
            for d in clock.calendar.loc[:day].index
            if str(pd.Timestamp(str(d)).date()) < day
        ][-6:]
        alpha = np.full(20, np.nan)
        direction = np.zeros(20, int)
        if len(previous) < 6:
            return alpha, direction, previous
        values = []
        for date in (previous[-6], previous[-1]):
            at = pd.Timestamp(date + " 15:30", tz="America/New_York")
            ix = np.flatnonzero(self.end_ns == at.value)
            values.append(self.close[ix[0]] if len(ix) else np.full(20, np.nan))
        good = np.isfinite(values[0]) & np.isfinite(values[1]) & (values[0] > 0) & (values[1] > 0)
        alpha[good] = np.log(values[1][good] / values[0][good])
        direction[good] = np.sign(alpha[good]).astype(int)
        return alpha, direction, previous


def parity(plan: Path, plan_hash: str, cache: Path, output: Path) -> None:
    if output.exists():
        raise ValueError("APPEND_ONLY_PARITY")
    verify_cache(cache, plan_hash)
    source = Sources(plan, plan_hash)
    hours, raw, facts = source.read()
    from lstm_data.hf1m_action_source import adjust_prices

    adjusted = adjust_prices(raw.loc[raw.ticker.isin(["AAPL", "COP"])], facts)
    prices = {
        (str(ticker), at.to_pydatetime(), field): float(value)
        for ticker, at, op, cl in adjusted[["ticker", "timestamp", "open", "close"]].itertuples(
            index=False, name=None
        )
        for field, value in [("open", op), ("close", cl)]
    }
    clock = MarketClock("2010-07-01", "2025-01-10")
    geo = geometry(clock)
    producer = OriginalInputOnlySnapshotProducer(
        hours.loc[hours.ticker.isin(["AAPL", "COP"])].copy(), prices, facts, clock, source.hash
    )
    registry = ModelRegistry(Path("."), Path("trading/track2/stage012/original_bundles.json"))
    models = {}
    inputs = {}
    rows = []
    started = time.monotonic()
    for year, day, slot, ticker in source.plan["parity_sample"]:
        if year not in models:
            models[year] = registry.load(year)
            inputs[year] = Inputs(cache, year)
        origin = datetime.fromisoformat(
            pd.Timestamp(day + " " + slot, tz="America/New_York").isoformat()
        )
        model = models[year]
        original = producer.produce(model.bundle, ticker, origin)
        one = geo.loc[(geo.session_date_et == day) & (geo.slot == slot)]
        cached = inputs[year].x(one)[0, SYMBOLS.index(ticker)]
        eligible = bool(inputs[year].eligible(one.iloc[0])[SYMBOLS.index(ticker)])
        if isinstance(original, Abstention):
            if eligible:
                raise AssertionError("ELIGIBILITY_PARITY")
            rows.append(
                {
                    "year": year,
                    "day": day,
                    "slot": slot,
                    "ticker": ticker,
                    "status": "MATCHED_ABSTENTION",
                    "reason": original.reason,
                }
            )
            continue
        snapshot, audit = original
        if not eligible:
            raise AssertionError("ELIGIBILITY_PARITY")
        expected = np.asarray(snapshot.values, np.float32)
        np.testing.assert_allclose(cached, expected, atol=1e-6, rtol=1e-5)
        clocks, _ = clock_values(one, clock.calendar)
        np.testing.assert_array_equal(clocks[0], np.asarray(snapshot.clock, np.float32))
        with torch.inference_mode():
            z = model.model(torch.from_numpy(cached.copy())[None], torch.from_numpy(clocks))[
                0
            ].item()
        prediction = float(decode(np.array([z]), model.scale, model.factors[snapshot.category])[0])
        reference = model.predict(snapshot)
        np.testing.assert_allclose(prediction, reference, atol=1e-7, rtol=1e-5)
        rows.append(
            {
                "year": year,
                "day": day,
                "slot": slot,
                "ticker": ticker,
                "status": "PASS",
                "max_input_abs": float(np.max(abs(cached - expected))),
                "forecast_abs_difference": abs(prediction - reference),
                "original_snapshot_hash": audit.input_hash,
            }
        )
        print("PARITY", year, day, slot, ticker, rows[-1]["max_input_abs"], flush=True)
    publish(
        output,
        {
            "status": "PASS",
            "rows": rows,
            "elapsed_seconds": time.monotonic() - started,
            "scope": "cache vs original INPUT_ONLY producer,not archived model forecast parity",
            "plan_sha256": plan_hash,
        },
    )


def controls(
    moves: np.ndarray, geo: pd.DataFrame, row: pd.Series, decision_ns: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, str]:
    selected = geo.index[
        (geo.slot == row["slot"]) & (ns(geo.exit_end_utc) + 120 * 10**9 < decision_ns)
    ].to_numpy(int)[-60:]
    count = np.zeros(20, int)
    median = np.full(20, np.nan)
    rms = median.copy()
    if not len(selected):
        return median, rms, count, 0, ""
    sample = np.abs(moves[selected])
    count = np.isfinite(sample).sum(axis=0)
    # Preserve inherited strict known-missing policy,do not silently pool/impute.
    valid = (count == len(sample)) & (count >= 40)
    if valid.any():
        median[valid] = np.median(sample[:, valid], axis=0)
        v = sample[0, valid] ** 2
        for item in sample[1:, valid]:
            v = 0.94 * v + 0.06 * item**2
        rms[valid] = np.sqrt(v)
    latest = pd.Timestamp(geo.iloc[selected[-1]]["exit_end_utc"]) + pd.Timedelta(minutes=2)
    return median, rms, count, len(selected), latest.isoformat()


def full_run(
    plan: Path,
    plan_hash: str,
    cache: Path,
    parity_receipt: Path,
    output: Path,
    report_root: Path | None = None,
) -> None:
    manifest = verify_cache(cache, plan_hash)
    par = json.loads(parity_receipt.read_text())
    if par["status"] != "PASS" or par["plan_sha256"] != plan_hash:
        raise ValueError("PARITY_GATE")
    root = report_root or Path("trading/track2/stage35/completion_v2")
    if (root / "FULL_SIGNAL_COVERAGE_REPORT.json").exists():
        raise ValueError("COMPLETE_REPORT_EXISTS_VERIFY_INVENTORY_NOT_REWRITE")
    output.mkdir(parents=True, exist_ok=True)
    root = report_root or Path("trading/track2/stage35/completion_v2")
    policy_hash = file_hash(plan.parent / "protocol_stage35_completion_v2.json")
    code_files = [Path(__file__), Path(__file__).with_name("cache.py")]
    binding = {
        "plan": plan_hash,
        "cache_manifest": file_hash(cache / "CACHE_READY.json"),
        "policy": policy_hash,
        "code": {str(f): file_hash(f) for f in code_files},
    }
    publish(output / "RUN_BINDING.json", binding)
    clock = MarketClock("2010-07-01", "2025-01-10")
    geo = pd.read_parquet(cache / "movement_geometry.parquet")
    moves = np.load(cache / "matured_source_moves.npy", mmap_mode="r")
    risk_path = Path(
        "trading/track2/stage012/audits/completion_v1/historical_run_v1/RISK_REFERENCE_MANIFEST.json"
    )
    risk = json.loads(risk_path.read_text())
    actual = hashlib.sha256(
        json.dumps(risk["payload"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if actual != "5c453193572a2e428c561249c842c90a3d36041736183195f3e1dc6a350b6681":
        raise ValueError("PREFIX_RISK_IDENTITY")
    references = {(r["fold"], r["ticker"], r["slot"]): r for r in risk["payload"]["records"]}
    registry = ModelRegistry(Path("."), Path("trading/track2/stage012/original_bundles.json"))
    started = time.monotonic()
    summaries = []
    torch.set_num_threads(4)
    for year in range(2021, 2025):
        model = registry.load(year)
        inp = Inputs(cache, year)
        fold = f"F{year % 100}"
        folder = output / fold
        folder.mkdir(exist_ok=True)
        yearly = geo.loc[geo.session_date_et.str.startswith(str(year))]
        for day, dayrows in yearly.groupby("session_date_et", sort=True):
            target = folder / (str(day) + ".parquet")
            receipt = target.with_suffix(".json")
            if receipt.exists():
                saved = json.loads(receipt.read_text())
                if not target.exists() or file_hash(target) != saved["sha256"]:
                    raise ValueError("RESUME_PARTITION_IDENTITY")
                summaries.append(saved)
                continue
            if target.exists():
                raise ValueError("UNSEALED_PARTITION_REQUIRES_REVIEW")
            x = inp.x(dayrows)
            clocks, _ = clock_values(dayrows, clock.calendar)
            with torch.inference_mode():
                z = (
                    model.model(
                        torch.from_numpy(x.reshape(-1, 48, 16)),
                        torch.from_numpy(np.repeat(clocks, 20, axis=0)),
                    )
                    .numpy()
                    .reshape(-1, 20)
                )
            factors = np.asarray([model.factors[c] for c in dayrows.category])[:, None]
            magnitude = decode(z, model.scale, factors)
            raw = model.scale * np.expm1(np.maximum(z, 0))
            alpha, direction, refs = inp.trend(clock, str(day))
            records = []
            frozen_at: list[datetime | None] = [None] * 20
            for n, (_, row) in enumerate(dayrows.iterrows()):
                t = pd.Timestamp(row["entry_end_utc"])
                decision = t + pd.Timedelta(minutes=2)
                marker = clock.next_observation(datetime.fromisoformat(decision.isoformat()))
                valid = inp.eligible(row)
                med, rms, counts, window, latest = controls(moves, geo, row, decision.value)
                for j, ticker in enumerate(SYMBOLS):
                    ref = references[(fold, ticker, row["slot"])]
                    b = float(ref["b"])
                    floor = float(ref["m_floor"])
                    if valid[j] and frozen_at[j] is None:
                        frozen_at[j] = datetime.fromisoformat(str(decision))
                    sign_ok = bool(direction[j]) and frozen_at[j] is not None
                    s2c_ok = bool(valid[j] and sign_ok and ref["status"] == "READY")
                    control_ok = bool(
                        valid[j] and np.isfinite(med[j]) and np.isfinite(rms[j]) and sign_ok
                    )

                    def g(value):
                        return min(1.5, max(0.5, b / max(float(value), floor)))

                    record = {
                        "fold": fold,
                        "cohort_key": f"{model.bundle.identities[0]}|{t.isoformat()}|{ticker}|ARM",
                        "date": day,
                        "ticker": ticker,
                        "origin": t,
                        "endpoint": row["exit_end_utc"],
                        "feature_ready": decision,
                        "source_latest_completed": t + pd.Timedelta(minutes=1)
                        if row["slot"] == "09:30"
                        else pd.Timestamp(
                            inp.grid.iloc[
                                int(np.searchsorted(inp.end_ns, t.value, side="right") - 1)
                            ]["hour_end_utc"]
                        ),
                        "receipt_policy": "ASSUMED_2_WALL_MINUTES_NOT_MEASURED",
                        "feature_lineage": (
                            "cache_manifest+recipe+48 scheduled slots ending<=origin;"
                            "M2 prior regular contexts endpoint+2 strictly before input-day open"
                        ),
                        "issued_at": decision,
                        "earliest_entry_marker": marker,
                        "entry_expiry": t + pd.Timedelta(minutes=10),
                        "model_z": float(z[n, j]) if valid[j] else None,
                        "magnitude_raw": float(raw[n, j]) if valid[j] else None,
                        "magnitude_c3": float(magnitude[n, j]) if valid[j] else None,
                        "input_eligible": bool(valid[j]),
                        "direction": int(direction[j]) if frozen_at[j] is not None else 0,
                        "trend_alpha": float(alpha[j]) if sign_ok else None,
                        "g_EQUAL": 1.0 if valid[j] and sign_ok else None,
                        "g_S2C_RISK": g(magnitude[n, j]) if s2c_ok else None,
                        "g_ROLLING_RISK": g(med[j]) if control_ok else None,
                        "g_EWMA_RISK": g(rms[j]) if control_ok else None,
                        "matched_four_arms": bool(s2c_ok and control_ok),
                        "control_count": int(counts[j]),
                        "control_window": window,
                        "control_latest_available": latest,
                        "rolling_scale": float(med[j]) if control_ok else None,
                        "ewma_scale": float(rms[j]) if control_ok else None,
                        "control_reason": "READY"
                        if control_ok
                        else "NO_SIGN"
                        if not sign_ok
                        else "INSUFFICIENT_OR_MISSING_MATURE_WINDOW",
                        "status": "ISSUED" if valid[j] else "UNAVAILABLE_PAST_INPUT",
                        "sign_reference_dates": "|".join(refs),
                        "sign_cache_hash": hashlib.sha256(
                            f"{ticker}|{day}|{refs}|{alpha[j]}|{manifest['source_hash']}".encode()
                        ).hexdigest(),
                        "sign_frozen_at": frozen_at[j],
                        "checkpoint_hash": model.bundle.identities[0],
                        "recipe_hash": model.bundle.identities[1],
                        "c3_hash": model.bundle.identities[2],
                        "risk_reference": risk["sha256"],
                        "basis": "SPLIT_CONSISTENT_20260331",
                        "calendar": "XNYS",
                        "source_hash": manifest["source_hash"],
                        "input_hash": hashlib.sha256(
                            x[n, j].tobytes() + clocks[n].tobytes()
                        ).hexdigest(),
                        "qualification": (
                            "retrospective_source_survivors_assumed_receipt;no_execution_or_PnL"
                        ),
                    }
                    records.append(record)
            frame = pd.DataFrame(records)
            temp = target.with_suffix(".parquet.tmp")
            frame.to_parquet(temp, index=False)
            temp.replace(target)
            saved = {
                "fold": fold,
                "date": str(day),
                "path": str(target),
                "sha256": file_hash(target),
                "rows": len(frame),
                "forecasts": int(frame.input_eligible.sum()),
                "equal": int(frame.g_EQUAL.notna().sum()),
                "s2c": int(frame.g_S2C_RISK.notna().sum()),
                "rolling": int(frame.g_ROLLING_RISK.notna().sum()),
                "ewma": int(frame.g_EWMA_RISK.notna().sum()),
                "matched": int(frame.matched_four_arms.sum()),
            }
            publish(receipt, saved)
            summaries.append(saved)
            if len(summaries) % 25 == 0:
                print(
                    "PROGRESS",
                    len(summaries),
                    "sessions",
                    sum(s["rows"] for s in summaries),
                    "opportunities",
                    flush=True,
                )
        del inp, model
    total = {
        key: sum(r[key] for r in summaries)
        for key in ("rows", "forecasts", "equal", "s2c", "rolling", "ewma", "matched")
    }
    publish(
        root / "FULL_SIGNAL_COVERAGE_REPORT.json",
        {
            "status": "COMPLETE_INPUT_ONLY",
            "totals": total,
            "sessions": len(summaries),
            "symbols": list(SYMBOLS),
            "folds": [2021, 2022, 2023, 2024],
            "elapsed_this_run_seconds": time.monotonic() - started,
            "partitions": summaries,
            "orders": 0,
            "fills": 0,
            "positions": 0,
            "financial_PnL": False,
        },
    )
    publish(
        root / "CLASSICAL_MATURED_CONTROLS_MANIFEST.json",
        {
            "status": "COMPLETE_SOURCE_ONLY",
            "policy": (
                "last60 scheduled matured slot movements,min40,strict known missingness;"
                "oldStage35 recurrence .94"
            ),
            "reference_sha256": risk["sha256"],
            "source_hash": manifest["source_hash"],
            "counts": total,
            "storage": "control columns in daily signal-only partitions",
            "frontier": "endpoint+2minutes STRICTLY beforedecision",
            "own_universe_vs_matched": "separate columns;EQUAL/S2C not gated oncontrols",
            "future_targets_in_signal_output": False,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["parity", "run"])
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--hash", required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--parity", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report-root", type=Path)
    args = parser.parse_args()
    if args.action == "parity":
        parity(args.plan, args.hash, args.cache, args.parity)
    elif args.output:
        full_run(args.plan, args.hash, args.cache, args.parity, args.output, args.report_root)
    else:
        parser.error("run requiresoutput")


if __name__ == "__main__":
    main()
