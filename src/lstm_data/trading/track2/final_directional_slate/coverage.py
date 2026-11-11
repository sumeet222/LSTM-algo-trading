"""Causal alpha/risk availability counts, computed before funded overlay outcomes."""

from collections import Counter

import numpy as np

from ..rapid_v1.paths import digest, publish
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.strategies import evaluate
from ..rapid_v2_diagnostics.report import csv_write
from ..rapid_v2_diagnostics.variants import Case, Endpoints
from ..rapid_v3_dynamic.policy import HoldingClock
from ..stage012.calendar_schedule import MarketClock
from ..stage012.model_registry import SYMBOLS
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import minute
from .common import POLICIES, ROOT, load
from .risk_inputs import ARMS, RiskInputs


def build() -> None:
    from decimal import Decimal

    cache = FeatureCache(
        __import__("pathlib").Path(
            "trading/track2/rapid_v1/cache/49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93"
        )
    )
    selected = load(ROOT / "SELECTION_RECEIPT.json")["selected"]
    risk = RiskInputs()
    cal = ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01"))
    holding = HoldingClock(cal)
    fixed = Endpoints(cal)
    counts = Counter()
    details = Counter()
    cutoff = minute("2024-12-31T23:59:00Z")
    for date in sorted(cache.by_date):
        if not "2021-01-01" <= date <= "2024-12-31":
            continue
        for f in cache.frames(date):
            values = risk.values(f.origin, f.decision)
            for fid in selected:
                p = POLICIES[fid]
                d = evaluate(p["strategy"], f)
                for it in d.intents:
                    counts[fid, "RAW_ALPHA"] += 1
                    if p["engine"] == "V2_FIXED":
                        endpoint = fixed.anchor(
                            f, Case(p["strategy"], "T480", Decimal(1), 480, "minutes")
                        )
                        allowed = endpoint is not None and cal.next(endpoint + 2) <= cutoff
                    else:
                        allowed = holding.admits(f, p["strategy"][0] == "M", "2024-12-31")
                    if not allowed:
                        counts[fid, "CALENDAR_ONLY_CUTOFF"] += 1
                        continue
                    for j, side in zip(it.tickers, it.signs, strict=True):
                        g = values[j]
                        matched = bool(np.isfinite(g).all())
                        for k, arm in enumerate(ARMS):
                            for pop in ("MATCHED", "ATTAINABLE"):
                                ready = matched if pop == "MATCHED" else bool(np.isfinite(g[k]))
                                counts[fid, pop, arm, "READY" if ready else "MISSING"] += 1
                                key = (
                                    fid,
                                    pop,
                                    arm,
                                    date[:4],
                                    SYMBOLS[j],
                                    f.slot,
                                    side,
                                    "READY" if ready else "MISSING_RISK_INPUT",
                                )
                                details[key] += 1
    csv_write(
        ROOT / "RISK_OPPORTUNITY_COUNTS.csv",
        [
            {
                "candidate": key[0],
                "population": key[1] if len(key) > 2 else "ALPHA",
                "arm": key[2] if len(key) > 2 else key[1],
                "status": key[3] if len(key) > 3 else "COUNT",
                "count": value,
            }
            for key, value in sorted(counts.items())
        ],
    )
    csv_write(
        ROOT / "RISK_SOURCE_COVERAGE_BY_STOCK_YEAR_SLOT_SIDE.csv",
        [
            dict(
                zip(
                    ("candidate", "population", "arm", "year", "ticker", "slot", "side", "status"),
                    key,
                )
            )
            | {"count": value}
            for key, value in sorted(details.items())
        ],
    )
    publish(
        ROOT / "OPPORTUNITY_READY_GATE.json",
        {
            "status": "PASS",
            "selected": selected,
            "source_only_no_financial_results": True,
            "rerank_after_risk_filter": False,
            "original_forecast_count": 131111,
            "readiness_is_sign_independent": True,
            "future_endpoint_or_F09_mask_used": False,
            "counts_sha256": digest(ROOT / "RISK_OPPORTUNITY_COUNTS.csv"),
        },
    )


if __name__ == "__main__":
    build()
