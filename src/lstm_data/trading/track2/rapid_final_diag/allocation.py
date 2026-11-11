"""Versioned R01-only allocation adapter; unchanged V3 gates plus common stress scale.

The original function is copied additively to expose the before-rounding hook.
Controls continue to call the frozen implementation directly.
"""

from decimal import ROUND_DOWN

import numpy as np

from ..rapid_v1.paths import canonical
from ..rapid_v1.portfolio import Lot, Request
from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v1.strategies import DirectionIntent
from ..rapid_v2_diagnostics.allocation import commitment_budget
from ..rapid_v3_dynamic.decisions import DecisionEngine
from ..stage35.final_backtest_v4.market import minute
from .book import DiagnosticLedger
from .policy import ZERO, D, stress_scale


class GuardedAllocation(DecisionEngine):
    def guarded_budget(
        self,
        a: DiagnosticLedger,
        frame: FeatureFrame,
        intents: tuple[DirectionIntent, ...],
        now: int,
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
            if any(
                not np.isfinite(frame.values["v20"][j])
                or frame.values["v20"][j] < 0
                or frame.values["v20"][j] > 1
                for j in intent.tickers
            ):
                a.reject("MISSING_NEW_LEG_V20")
                continue
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
        proposed = []
        for it in ready:
            if len(it.tickers) != 1:
                raise ValueError("R01_SINGLE_LEG_ONLY")
            j = it.tickers[0]
            u = min(amount_each, max(ZERO, a.name_cap * nav - names.get(j, ZERO)))
            proposed.append((u, D(str(frame.values["v20"][j]))))
        A, L = ZERO, ZERO
        for lot in a.lots.values():
            if lot.origin != frame.origin or not (lot.quantity or lot.pending):
                continue
            v = frame.values["v20"][lot.ticker]
            if not np.isfinite(v) or v < 0 or v > 1:
                a.reject("MISSING_EXISTING_VINTAGE_V20", len(ready))
                return requests
            x = (abs(lot.quantity) + abs(lot.pending)) * (a.prices[lot.ticker] or ZERO)
            s = D(str(v)).exp()
            A += x * s
            L += x * (s - 1)
        common, numerator, denominator = stress_scale(nav, reserve, A, L, tuple(proposed))
        for intent in ready:
            weights = np.asarray(intent.weights, float)
            weights /= weights.sum()
            amounts = [amount_each * D(str(w)) for w in weights]
            scale = D(1)
            for j, amount in zip(intent.tickers, amounts, strict=True):
                if amount > 0:
                    scale = min(scale, max(ZERO, a.name_cap * nav - names.get(j, ZERO)) / amount)
            original_scale = scale
            scale *= common
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
            a.entry_reserves.append(
                {
                    "case": a.arm,
                    "origin": frame.origin,
                    "decision": now,
                    "ticker": intent.tickers[0],
                    "side": intent.signs[0],
                    "N": nav,
                    "R": reserve,
                    "A": A,
                    "L": L,
                    "t": common,
                    "numerator": numerator,
                    "denominator": denominator,
                    "v20": D(str(frame.values["v20"][intent.tickers[0]])),
                    "old_commitment": sum(amounts, ZERO) * original_scale,
                    "new_commitment": sum(amounts, ZERO) * scale,
                    "rounded_shares": quantities[0],
                    "free": free,
                    "name_marked": names.get(intent.tickers[0], ZERO),
                    "virtual_gross": a.gross(),
                    "restricted": a.restricted(),
                    "feature_lineage": frame.lineage,
                }
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
