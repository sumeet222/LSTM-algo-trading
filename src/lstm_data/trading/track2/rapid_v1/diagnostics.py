"""Mature-only unfunded price diagnostics, isolated from order decisions."""

import heapq
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np

from ..stage35.final_backtest_v4.market import minute
from ..stage35.final_backtest_v5.special import EX
from .sources import RawDay
from .strategies import IDS, DirectionIntent

ET = ZoneInfo("America/New_York")


@dataclass
class PendingOutcome:
    intent: DirectionIntent
    entry_effective: int
    exit_effective: int
    entry_at: int | None = None
    entry_prices: tuple[float, ...] = ()
    entry_factors: tuple[float, ...] = ()


@dataclass
class QualityBook:
    queue: list[tuple[int, int, PendingOutcome]] = field(default_factory=list)
    sequence: int = 0
    completed: dict[str, list[dict]] = field(default_factory=lambda: {s: [] for s in IDS})
    reasons: dict[str, Counter] = field(default_factory=lambda: {s: Counter() for s in IDS})

    @property
    def pending(self) -> list[PendingOutcome]:
        return [p for _, _, p in self.queue]

    def add(self, intent: DirectionIntent, entry: int, exit_at: int) -> None:
        self.sequence += 1
        heapq.heappush(self.queue, (entry, self.sequence, PendingOutcome(intent, entry, exit_at)))

    def tick(self, day: RawDay, i: int, factor: np.ndarray) -> None:
        start = int(day.starts[i])
        while self.queue and self.queue[0][0] <= start:
            _, sequence, p = heapq.heappop(self.queue)
            intent = p.intent
            valid = all(day.valid[i, j] for j in intent.tickers)
            if p.entry_at is None:
                if start > intent.origin + 10:
                    self.reasons[intent.strategy_id]["ENTRY_EXPIRED_NO_QUALIFIED_BAR"] += 1
                    continue
                if valid:
                    p.entry_at = start
                    p.entry_prices = tuple(float(day.opens[i, j]) for j in intent.tickers)
                    p.entry_factors = tuple(float(factor[j]) for j in intent.tickers)
                when = p.exit_effective if p.entry_at is not None else start + 1
                heapq.heappush(self.queue, (max(start + 1, when), sequence, p))
                continue
            if not valid:
                heapq.heappush(self.queue, (start + 1, sequence, p))
                continue
            # A price-only return across a noncash distribution is not an
            # economic total return. Censor this diagnostic only, never the intent.
            if 6 in intent.tickers and p.entry_at < minute(EX) <= start:
                self.reasons[intent.strategy_id]["PRICE_ONLY_SPECIAL_ACTION_CENSORED"] += 1
                continue
            weights = np.asarray(intent.weights, dtype=float)
            weights /= weights.sum()
            logret = 0.0
            simple = 0.0
            for k, j in enumerate(intent.tickers):
                ratio = (
                    float(day.opens[i, j])
                    * float(factor[j])
                    / (p.entry_prices[k] * p.entry_factors[k])
                )
                logret += weights[k] * intent.signs[k] * float(np.log(ratio))
                simple += weights[k] * intent.signs[k] * (ratio - 1)
            self.completed[intent.strategy_id].append(
                {
                    "session": intent.session,
                    "origin": intent.origin,
                    "slot": datetime.fromtimestamp(intent.origin * 60, ET).strftime("%H:%M"),
                    "entry_at": p.entry_at,
                    "exit_at": start,
                    "tickers": intent.tickers,
                    "signs": intent.signs,
                    "signed_log_return": logret,
                    "gross_equal_notional_USD": simple * 10000,
                    "source": intent.lineage,
                    "outcome_source": day.source_hash,
                }
            )


def quality_summary(records: list[dict], reasons: Counter) -> dict:
    values = np.asarray([r["signed_log_return"] for r in records], float)
    pnl = np.asarray([r["gross_equal_notional_USD"] for r in records], float)
    wins = pnl[pnl > 0]
    loss = pnl[pnl < 0]
    n = len(values)
    top = max(1, int(np.ceil(n * 0.01))) if n else 0
    days = {}
    for r in records:
        days.setdefault(r["session"], []).append(r["signed_log_return"])
    grouped = {}
    for dimension in ("year", "sign", "overnight", "slot", "ticker"):
        groups = {}
        for r in records:
            if dimension == "year":
                key = r["session"][:4]
            elif dimension == "sign":
                key = "PAIR" if len(r["signs"]) > 1 else str(r["signs"][0])
            elif dimension == "overnight":
                key = str(r["entry_at"] // 1440 != r["exit_at"] // 1440)
            elif dimension == "slot":
                key = r["slot"]
            else:
                key = ",".join(str(x) for x in r["tickers"])
            groups.setdefault(key, []).append(r["signed_log_return"])
        grouped[dimension] = {
            k: {
                "count": len(a),
                "mean_signed_log_return": float(np.mean(a)),
                "hit_rate": float(np.mean(np.asarray(a) > 0)),
            }
            for k, a in groups.items()
        }
    return {
        "mature_outcomes": n,
        "censor_reasons": dict(reasons),
        "mean_signed_log_return": float(values.mean()) if n else None,
        "median_signed_log_return": float(np.median(values)) if n else None,
        "sign_hit_rate": float(np.mean(values > 0)) if n else None,
        "gross_positive_USD_at_10000_notional": float(wins.sum()),
        "gross_negative_USD_at_10000_notional": float(loss.sum()),
        "average_gross_winner_USD": float(wins.mean()) if len(wins) else None,
        "average_gross_loser_USD": float(loss.mean()) if len(loss) else None,
        "top_1percent_absolute_pnl_concentration": float(
            np.sort(np.abs(pnl))[-top:].sum() / np.abs(pnl).sum()
        )
        if n and np.abs(pnl).sum()
        else None,
        "mean_gross_roundtrip_breakeven_bps": float(values.mean() * 10000) if n else None,
        "descriptive_day_cluster_mean": float(np.mean([np.mean(v) for v in days.values()]))
        if days
        else None,
        "opposite_sign_null_mean_log_return": float(-values.mean()) if n else None,
        "null_on_identical_outcome_opportunities": True,
        "groups": grouped,
        "examples": records[:5],
        "funded_portfolio_estimate": False,
        "definition": (
            "Unfunded split-neutral observed-bar price path; no depth guarantee or total return. "
            "Hypothetical $10000 notional, no costs. Special distributions censor scoring only."
        ),
    }
