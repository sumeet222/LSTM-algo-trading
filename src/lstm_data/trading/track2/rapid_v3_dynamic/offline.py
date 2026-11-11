"""Post-publication diagnostics. This module is never imported by the funded engine."""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ..rapid_v1.cli import peak_memory_bytes
from ..rapid_v1.paths import digest, publish
from ..rapid_v1.sources import RawMarket
from ..stage012.calendar_schedule import MarketClock
from ..stage012.model_registry import SYMBOLS
from ..stage35.completion_v3.tapes import load_actions, midnight
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import minute
from ..stage35.final_backtest_v5.special import EX
from .policy import HoldingClock


def extension(quantity, actual, later):
    return quantity * (later - actual)


def targets(clock: HoldingClock, effective: np.ndarray) -> dict[str, np.ndarray]:
    cal = clock.cal
    session = np.searchsorted(cal.closes, effective, side="right")
    offset = effective - cal.opens[session]
    full = np.flatnonzero(cal.closes - cal.opens == 390)
    following = full[np.searchsorted(full, session, side="right")]
    result = {"NEXT_FULL_SESSION": cal.opens[following] + offset}
    for h in (60, 240):
        t = clock.cumulative[session] + offset + h
        j = np.searchsorted(clock.cumulative, t, side="left") - 1
        result[f"T{h}"] = cal.opens[j] + t - clock.cumulative[j]
    return result


def action_frontiers() -> dict[int, np.ndarray]:
    events: dict[int, list[int]] = {j: [] for j in range(20)}
    for a in load_actions():
        if a.symbol in SYMBOLS and a.action_type in ("CASH_DIVIDEND", "SPLIT", "SPINOFF"):
            date = a.ex_date or a.effective_date
            if date:
                events[SYMBOLS.index(a.symbol)].append(minute(midnight(date)))
    events[SYMBOLS.index("MRK")].append(minute(EX))
    return {k: np.asarray(sorted(set(v)), dtype=np.int64) for k, v in events.items()}


def load_sealed(run: Path) -> tuple[pd.DataFrame, dict]:
    receipt = json.loads((run / "V3_RUN_STATUS.json").read_text())
    base = Path(receipt["funded_directory"])
    path = base / "FUNDED_OUTPUT_MANIFEST.json"
    if digest(path) != receipt["funded_manifest_sha256"]:
        raise ValueError("POST_EXIT_REQUIRES_SEALED_FUNDED_OUTPUTS")
    manifest = json.loads(path.read_text())
    if any(digest(base / k) != h for k, h in manifest["files"].items()):
        raise ValueError("SEALED_FUNDED_OUTPUT_DRIFT")
    tape = pd.read_parquet(base / "SEALED_ACTUAL_EXIT_LEGS.parquet")
    if len(tape) != manifest["exit_legs"] or (tape["effective"] <= tape["decision"]).any():
        raise ValueError("EXIT_TAPE_CENSUS_OR_TIMING")
    return tape, receipt


def analyze(run: Path) -> None:
    start = time.monotonic()
    tape, receipt = load_sealed(run)
    out = run / "offline_diagnostic"
    out.mkdir(exist_ok=False)
    market = RawMarket("2021-01-01", "2024-12-31")
    clock = HoldingClock(ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01")))
    last = int(clock.cal.closes[clock.session(minute("2024-12-31T14:30:00Z"))])
    plan = targets(clock, tape["effective"].to_numpy(np.int64))
    names = tuple(plan)
    orig = tape["effective"].to_numpy(np.int64)
    end = np.concatenate([plan[k] for k in names])
    sample = pd.concat([tape.assign(horizon=k) for k in names], ignore_index=True)
    opening = clock.cal.opens
    target_day = np.searchsorted(clock.cal.closes, end, side="right")
    end = np.maximum(end, opening[target_day])
    stock = sample["ticker"].to_numpy(np.int64)
    orig = np.tile(orig, len(names))
    valid = (end < last) & (end > orig)
    why = np.full(len(sample), "EVALUATION_CUTOFF", dtype="<U30")
    why[valid] = "MISSING_TARGET_SESSION_BAR"
    later = np.full(len(sample), np.nan)
    actions = action_frontiers()
    order = np.argsort(target_day, kind="stable")
    sorted_day = target_day[order]
    for day in market.days():
        j = clock.session(int(day.starts[0]))
        left, right = np.searchsorted(sorted_day, [j, j + 1], side="left")
        block = order[left:right]
        if not len(block):
            continue
        for k in range(20):
            b = block[(stock[block] == k) & valid[block]]
            if not len(b):
                continue
            starts = day.starts[day.valid[:, k]]
            lookup = np.searchsorted(starts, end[b])
            inside = lookup < len(starts)
            found = b[inside]
            ref = starts[lookup[inside]]
            events = actions[k]
            crossing = np.searchsorted(events, ref, side="right") > np.searchsorted(
                events, orig[found], side="right"
            )
            why[found[crossing]] = "CORPORATE_ACTION_CROSSING"
            used = found[~crossing]
            later[used] = day.opens[np.searchsorted(day.starts, ref[~crossing]), k]
            why[used] = "VALID"
    q = sample["quantity"].to_numpy(float)
    fill = sample["fill"].to_numpy(float)
    result = extension(q, fill, later)
    if not np.array_equal(extension(-q, fill, later), -result, equal_nan=True):
        raise ValueError("SIGNED_EXTENSION_SYMMETRY")
    sample = sample.assign(
        dollars=result,
        bps=result / (abs(q) * fill) * 10000,
        valid=np.isfinite(result).astype(int),
        positive=(result > 0).astype(int),
        missed=np.maximum(result, 0),
        avoided=np.maximum(-result, 0),
        cutoff=(why == "EVALUATION_CUTOFF").astype(int),
        action=(why == "CORPORATE_ACTION_CROSSING").astype(int),
        missing=(why == "MISSING_TARGET_SESSION_BAR").astype(int),
        feasible=np.where(sample["cause"].str.startswith("RISK_"), "INFEASIBLE_RISK", "UNFUNDED"),
        side=np.where(q > 0, "long", "short"),
        year=sample["effective"]
        .to_numpy(np.int64)
        .astype("datetime64[m]")
        .astype("datetime64[Y]")
        .astype(int)
        + 1970,
    )
    hold = clock.index  # Clock-based durations, never wall-clock substitution.
    held = np.fromiter(
        (
            hold(int(x)) - hold(int(y))
            for x, y in zip(sample["effective"], sample["entry"], strict=True)
        ),
        dtype=np.int64,
    )
    exit_strength = sample["exit_strength"].to_numpy(float)
    sample = sample.assign(
        all="all",
        extension_overnight=np.where(
            target_day == np.searchsorted(clock.cal.closes, orig, side="right"),
            "same_session",
            "later_session",
        ),
        holding=np.select(
            [held < 60, held < 240, held < 390], ["lt60", "60to239", "240to389"], default="390plus"
        ),
        overnight=np.where(
            sample["effective"] // 1440 == sample["entry"] // 1440, "same_day", "overnight"
        ),
        entry_strength=np.select(
            [sample["entry_strength"] < 1, sample["entry_strength"] < 2],
            ["lt1", "1to2"],
            default="2plus",
        ),
        exit_strength=np.select(
            [~np.isfinite(exit_strength), exit_strength < 0, exit_strength < 1],
            ["unknown", "reversed", "weak"],
            default="strong",
        ),
    )
    rows = []
    keys = ["strategy_id", "regime", "cause", "horizon", "feasible"]
    for axis in (
        "all",
        "year",
        "side",
        "entry_strength",
        "exit_strength",
        "holding",
        "overnight",
        "extension_overnight",
    ):
        table = (
            sample.groupby([*keys, axis], dropna=False)
            .agg(
                total=("valid", "size"),
                valid=("valid", "sum"),
                positive=("positive", "sum"),
                mean_USD=("dollars", "mean"),
                median_USD=("dollars", "median"),
                mean_bps=("bps", "mean"),
                median_bps=("bps", "median"),
                missed_upside_USD=("missed", "sum"),
                losses_avoided_USD=("avoided", "sum"),
                cutoff=("cutoff", "sum"),
                action=("action", "sum"),
                missing=("missing", "sum"),
            )
            .reset_index()
            .rename(columns={axis: "label"})
        )
        table["axis"] = axis
        table["positive_fraction"] = table["positive"].div(table["valid"].where(table["valid"] > 0))
        table.loc[table["valid"] == 0, ["missed_upside_USD", "losses_avoided_USD"]] = np.nan
        if (
            table["valid"] + table["cutoff"] + table["action"] + table["missing"] != table["total"]
        ).any():
            raise ValueError("POST_EXIT_CENSOR_CENSUS")
        rows.append(table)
    pd.concat(rows, ignore_index=True).to_csv(out / "V3_POST_EXIT_EXTENSION.csv", index=False)
    final_manifest = Path(receipt["funded_directory"]) / "FUNDED_OUTPUT_MANIFEST.json"
    if digest(final_manifest) != receipt["funded_manifest_sha256"]:
        raise ValueError("FUNDED_OUTPUT_CHANGED_DURING_OFFLINE_DIAGNOSTIC")
    publish(
        out / "POST_EXIT_RECEIPT.json",
        {
            "status": "PASS",
            "funded_manifest_sha256": receipt["funded_manifest_sha256"],
            "exit_legs": len(tape),
            "targets": len(sample),
            "census": {
                str(k): int(v) for k, v in zip(*np.unique(why, return_counts=True), strict=True)
            },
            "sampling": "All filled exit legs including partials. No outcome selection.",
            "scope": "Isolated signed price marks. No new orders, carry or feasible portfolio.",
            "source_months": market.reads,
            "elapsed_seconds": time.monotonic() - start,
            "peak_RSS_bytes": peak_memory_bytes(),
            "output_sha256": digest(out / "V3_POST_EXIT_EXTENSION.csv"),
        },
    )
    print(out, len(sample), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    analyze(parser.parse_args().run)
