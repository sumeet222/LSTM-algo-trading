"""Source-linked V1 allocation, with one pre-rounding budget hook."""

import numpy as np

from ..rapid_v1.paths import canonical
from ..rapid_v1.portfolio import FastAccount, Lot, Request
from ..rapid_v1.runner import ROUND_DOWN, ZERO, D, FastEngine
from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v1.strategies import DirectionIntent
from ..stage35.final_backtest_v4.market import minute
from .variants import Case


def commitment_budget(budget: D, headroom: D) -> D:
    if not ZERO <= budget or headroom not in (D(1), D(".85"), D(".70")):
        raise ValueError("INVALID_HEADROOM_BUDGET")
    return budget * headroom


class AllocationEngine(FastEngine):
    case_by_key: dict[str, Case]

    def allocate(
        self, a: FastAccount, frame: FeatureFrame, intents: tuple[DirectionIntent, ...], now: int
    ) -> dict[int, list[Request]]:
        requests: dict[int, list[Request]] = {}
        nav, free, names, status = a.capacity(now)
        if nav is None or status != "READY" or a.risk_hold or a.arm in self.account_holds:
            a.reject(
                status if status != "READY" else "ACCOUNT_SPECIAL_OR_FINANCIAL_HOLD", len(intents)
            )
            return requests
        ready = []
        slots = self.budgets[a.arm].remaining(frame.session)
        for intent in intents:
            a.decision_frontier.update(
                tickers=intent.tickers, signs=intent.signs, strength=intent.strength
            )
            if any(
                self.active_duplicate(a, j, s)
                for j, s in zip(intent.tickers, intent.signs, strict=True)
            ):
                a.reject("DUPLICATE_ACTIVE_SAME_SIGN")
                continue
            if any(
                a.prices[j] is None or now - a.marks_at[j] > 5 or a.volume[j] is None
                for j in intent.tickers
            ):
                a.reject("MISSING_OR_STALE_PRETRADE_REFERENCE")
                continue
            if any(self.cost_reference(a, j, now, True) is None for j in intent.tickers):
                a.reject("MISSING_CAUSAL_MICRO_COST_REFERENCE")
                continue
            if self.execution_calendar.next(intent.endpoint + 2) > minute(self.last + "T23:59:00Z"):
                a.reject("CALENDAR_TERMINAL_CUTOFF")
                continue
            # Reserve external-order slots conservatively before submission.
            # Internal-only opportunities are later refunded to the live budget.
            if len(intent.tickers) > slots:
                a.reject("ENTRY_ORDER_CAP")
                continue
            ready.append(intent)
            slots -= len(intent.tickers)
        if not ready:
            return requests
        reserve = D(".002") * nav + sum((len(i.tickers) * a.scenario.minimum for i in ready), ZERO)
        budget = min(
            D(".2") * max(ZERO, nav - reserve),
            max(ZERO, nav - a.gross()),
            max(ZERO, free - reserve),
        )
        amount_each = commitment_budget(budget, self.case_by_key[a.arm].headroom) / len(ready)
        for intent in ready:
            weights = np.asarray(intent.weights, float)
            weights /= weights.sum()
            amounts = [amount_each * D(str(w)) for w in weights]
            scale = D(1)
            for j, amount in zip(intent.tickers, amounts, strict=True):
                if amount > 0:
                    scale = min(scale, max(ZERO, D(".1") * nav - names.get(j, ZERO)) / amount)
            quantities = []
            for j, s, amount in zip(intent.tickers, intent.signs, amounts, strict=True):
                price = a.prices[j]
                volume = a.volume[j]
                if price is None or volume is None:
                    raise AssertionError("READY_SOURCE")
                q = (amount * scale / price).to_integral_value(rounding=ROUND_DOWN)
                cap = (volume * D(".01")).to_integral_value(rounding=ROUND_DOWN)
                quantities.append(min(q, cap) * s)
            a.decision_frontier.update(
                quantities=[str(q) for q in quantities],
                known_prices=[str(a.prices[j]) for j in intent.tickers],
            )
            if any(q == 0 for q in quantities):
                a.reject("ROUNDING_OR_PARTICIPATION")
                continue
            if len(quantities) == 2:
                actual = (
                    abs(quantities[1])
                    * (a.prices[intent.tickers[1]] or ZERO)
                    / (abs(quantities[0]) * (a.prices[intent.tickers[0]] or D(1)))
                )
                if abs(float(actual) / intent.weights[1] - 1) > 0.05:
                    a.reject("PAIR_HEDGE_ROUNDING_OR_PARTICIPATION")
                    continue
            if a.population == "RETAIL_CONSERVATIVE" and any(
                abs(q) * (a.prices[j] or ZERO) < 2000
                for j, q in zip(intent.tickers, quantities, strict=True)
            ):
                a.reject("RETAIL_MIN_NOTIONAL")
                continue
            pair_id = (
                canonical((a.arm, intent.origin, intent.tickers)) if len(quantities) > 1 else None
            )
            for j, s, q in zip(intent.tickers, intent.signs, quantities, strict=True):
                key = f"{a.arm}|{intent.origin}|{j}"
                if key in a.lots:
                    raise ValueError("DUPLICATE_OR_DYNAMIC_RESIZE")
                a.lots[key] = Lot(
                    key,
                    j,
                    intent.origin,
                    intent.endpoint,
                    intent.origin + 10,
                    s,
                    int(q),
                    D(1),
                    pending=q,
                )
                a.stats.lot_lineage[key] = intent.lineage
                a.stats.lot_decision[key] = now
                requests.setdefault(j, []).append(Request(key, q, "ENTRY"))
                if pair_id:
                    self.paired_lots[key] = pair_id
        a.refresh()
        return requests
