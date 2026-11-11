"""Full source-side schema/coverage audit; no portfolio, fills, NAV or P&L."""

import json
import time

import numpy as np

from ...stage012.model_registry import SYMBOLS
from .market import Market
from .paths import ROOT, V2, V3, digest, publish


def scan() -> None:
    started = time.monotonic()
    market = Market()
    totals = {
        "sessions": 0,
        "rows": 0,
        "valid": 0,
        "missing_or_invalid": 0,
        "opportunities": 0,
        "forecasts": 0,
        "equal": 0,
        "s2c": 0,
        "rolling": 0,
        "ewma": 0,
        "matched": 0,
    }
    per_ticker = {t: {"valid": 0, "missing_or_invalid": 0} for t in SYMBOLS}
    first_bad = []
    calendar = []
    previous_fold = None
    for day in market.days():
        totals["sessions"] += 1
        totals["rows"] += day.valid.size
        totals["valid"] += int(day.valid.sum())
        totals["missing_or_invalid"] += int((~day.valid).sum())
        totals["opportunities"] += len(day.signals)
        totals["forecasts"] += int(day.signals.magnitude_c3.notna().sum())
        for arm, key in [
            ("EQUAL", "equal"),
            ("S2C_RISK", "s2c"),
            ("ROLLING_RISK", "rolling"),
            ("EWMA_RISK", "ewma"),
        ]:
            totals[key] += int(np.asarray(day.signals["g_" + arm].notna(), dtype=bool).sum())
        totals["matched"] += int(np.asarray(day.signals["matched_four_arms"], dtype=bool).sum())
        for j, t in enumerate(SYMBOLS):
            per_ticker[t]["valid"] += int(day.valid[:, j].sum())
            per_ticker[t]["missing_or_invalid"] += int((~day.valid[:, j]).sum())
        for i, j in np.argwhere(~day.valid)[: max(0, 10 - len(first_bad))]:
            first_bad.append(
                {
                    "date": day.date,
                    "ticker": SYMBOLS[j],
                    "minute": int(day.starts[i]),
                    "status": "INVALID_OR_MISSING_EXECUTION_OBSERVATION_NO_PRICE_INVENTED",
                }
            )
        year = day.date[:4]
        if year != previous_fold:
            calendar.append(
                {
                    "first_session": day.date,
                    "fold": "F" + year[2:],
                    "opportunities": len(day.signals),
                }
            )
            previous_fold = year
        if totals["sessions"] % 100 == 0:
            print("source_sessions", totals["sessions"], flush=True)
    expected = json.loads((V2 / "FULL_SIGNAL_COVERAGE_REPORT.json").read_text())["totals"]
    for key in ("forecasts", "equal", "s2c", "rolling", "ewma", "matched"):
        if totals[key] != expected[key]:
            raise ValueError("FROZEN_SIGNAL_COUNTS_CHANGED:" + key)
    if totals["opportunities"] != expected["rows"]:
        raise ValueError("OPPORTUNITY_AXIS_CHANGED")
    publish(
        ROOT / "RAW_SOURCE_AND_SIGNAL_PREFLIGHT_V4.json",
        {
            "totals": totals,
            "per_ticker": per_ticker,
            "first_invalid_witnesses": first_bad,
            "fold_boundaries": calendar,
            "sources": market.reads,
            "elapsed_seconds": time.monotonic() - started,
            "source_basis": "canonical observed before adjust_prices;retrospective raw-share study",
            "invalid_policy": (
                "new entry no modeled fill;existing exposure retained and fut"
                "ure attempt;never future-universe filter"
            ),
            "post2024_price_reads": 0,
            "financial_outputs": False,
            "canonical_actions_sha256": digest(V3 / "ACTION_PROVENANCE_V3.jsonl"),
        },
    )


if __name__ == "__main__":
    scan()
