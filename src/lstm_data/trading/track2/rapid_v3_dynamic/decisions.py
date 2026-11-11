"""Scoped V1 decision adapter with a configurable name cap and dynamic exit hooks."""

from decimal import ROUND_DOWN

import numpy as np

from ..rapid_v1.paths import canonical
from ..rapid_v1.portfolio import Lot, Order, Request
from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v1.sources import RawDay
from ..rapid_v1.strategies import DirectionIntent
from ..rapid_v2_diagnostics.allocation import commitment_budget
from ..rapid_v2_diagnostics.engine import Batch
from ..stage35.final_backtest_v4.book import integer_cross
from ..stage35.final_backtest_v4.market import minute
from .book import ZERO, D, DynamicLedger


class DecisionEngine(Batch):
    dynamic_accounts: list[DynamicLedger]
    legacy: bool = False

    def allocate_budget(
        self, a: DynamicLedger, frame: FeatureFrame, intents: tuple[DirectionIntent, ...], now: int
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
                    scale = min(scale, max(ZERO, a.name_cap * nav - names.get(j, ZERO)) / amount)
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

    def decide(
        self,
        n: int,
        day: RawDay,
        now: int,
        frame: FeatureFrame | None,
        intents: tuple[DirectionIntent, ...],
    ) -> None:
        a = self.dynamic_accounts[n]
        a.decision_frontier = {
            "decision": now,
            "origin": frame.origin if frame is not None else None,
            "feature_lineage": frame.lineage if frame is not None else None,
        }
        if a.pending:
            if intents:
                a.reject("PENDING_UNOBSERVED_ORDER", len(intents))
            return
        self.sync(a, now)
        a.accrue(self.integrals, now)
        a.accrue_funding(now - 2)
        _, _, _, status = a.capacity(now)
        if status == "RISK_BREACH":
            a.record("OBSERVED_MARKED_CAP_BREACH", now, source=day.source_hash)
        self.latch_maximum(a, now)
        requests: dict[int, list[Request]] = {}
        if not self.legacy:
            self.release_unsent_for_exits(a, status, now)
            if status == "RISK_BREACH":
                # Releasing an unsent reservation can cure a marked breach.
                # Keep the breach receipt and reject new risk at this decision.
                if intents:
                    a.reject("RISK_BREACH", len(intents))
                    intents = ()
                _, _, _, status = a.capacity(now)
        for lot in a.lots.values():
            if lot.pending and now > lot.deadline:
                a.cancel_unsubmitted(lot.key, now, "ENTRY_LIFETIME")
        if not self.legacy and status == "RISK_BREACH":
            _, _, _, status = a.capacity(now)
        for lot in a.lots.values():
            if lot.quantity and (self.policy_due(a, lot.key) or status == "RISK_BREACH"):
                requests.setdefault(lot.ticker, []).append(
                    Request(
                        lot.key,
                        -lot.quantity,
                        "RISK_LIQUIDATION" if status == "RISK_BREACH" else "EXIT",
                    )
                )
        if frame is not None and intents:
            new = self.allocate(a, frame, intents, now)
            for j, items in new.items():
                requests.setdefault(j, []).extend(items)
        for lot in a.lots.values():
            if (
                lot.pending
                and now <= lot.deadline
                and not any(r.key == lot.key for r in requests.get(lot.ticker, []))
            ):
                requests.setdefault(lot.ticker, []).append(Request(lot.key, lot.pending, "ENTRY"))
        # Pair exits use joint full-quantity capacity. They wait rather than
        # creating an accidental one-legged hedge when either capacity is absent.
        paired = {
            self.paired_lots[r.key]
            for items in requests.values()
            for r in items
            if r.key in self.paired_lots
        }
        for pair in paired:
            members = [
                (j, r)
                for j, items in requests.items()
                for r in items
                if self.paired_lots.get(r.key) == pair
            ]
            if len(members) != 2 or any(
                a.volume[j] is None or abs(r.delta) > (a.volume[j] or ZERO) * D(".01")
                for j, r in members
            ):
                for j, r in members:
                    requests[j].remove(r)
                a.reject("PAIR_JOINT_CAPACITY_WAIT")
        self.guard_atomic_pair_orders(a, requests, now)
        for j, items in sorted(requests.items()):
            if not items:
                continue
            if a.volume[j] is None or now - a.marks_at[j] > 5:
                a.reject("ENTRY_OR_EXIT_SOURCE_STALE")
                continue
            target = sum((r.delta for r in items), ZERO)
            cap = ((a.volume[j] or ZERO) * D(".01")).to_integral_value(rounding=ROUND_DOWN)
            submitted = min(abs(target), cap) * (1 if target > 0 else -1) if target else ZERO
            has_entry = any(r.role == "ENTRY" for r in items)
            roles = {r.key: r.role for r in items}
            preview = integer_cross(tuple(items), D(1), D(1), submitted, ZERO)
            external_entry = any(
                not leg.internal and roles[leg.cohort_id] == "ENTRY" for leg in preview
            )
            if target and not submitted:
                a.reject("NO_PRIOR_VOLUME_CAPACITY")
                continue
            expiry = min((a.lots[r.key].deadline for r in items if r.role == "ENTRY"), default=None)
            effective = self.execution_calendar.next(now)
            if expiry is not None and effective > expiry:
                continue
            if (
                external_entry
                and submitted
                and a.population == "RETAIL_CONSERVATIVE"
                and abs(submitted) * (a.prices[j] or ZERO) < 2000
            ):
                for r in items:
                    if r.role == "ENTRY":
                        a.cancel_unsubmitted(r.key, now, "RETAIL_MIN_NOTIONAL")
                items = [r for r in items if r.role != "ENTRY"]
                a.reject("RETAIL_MIN_NOTIONAL")
                if not items:
                    continue
                target = sum((r.delta for r in items), ZERO)
                submitted = min(abs(target), cap) * (1 if target > 0 else -1) if target else ZERO
                has_entry = False
                external_entry = False
                expiry = None
            if external_entry and submitted:
                if self.budgets[a.arm].remaining(day.date) <= 0:
                    for r in items:
                        if r.role == "ENTRY":
                            a.cancel_unsubmitted(r.key, now, "ENTRY_ORDER_CAP")
                    a.reject("ENTRY_ORDER_CAP")
                    continue
                self.budgets[a.arm].reserve(day.date, 1)
            a.order_seq += 1
            key = f"{day.date}:{now}:{j}:{a.order_seq}"
            a.pending[j] = Order(
                key, j, now, effective, tuple(items), submitted, a.volume_available[j], expiry
            )
            reference = self.cost_reference(a, j, now, has_entry)
            if reference is None:
                raise AssertionError("ORDER_WITHOUT_COST_REFERENCE")
            a.cost_references[key] = reference
            a.record(
                "ORDER",
                now,
                order=key,
                ticker=j,
                submitted=submitted,
                unsubmitted=target - submitted,
                entry=has_entry,
                source=day.source_hash,
            )
        a.refresh()
        a.reconcile()

    def policy_due(self, a: DynamicLedger, lot: str) -> bool:
        key = a.group_of.get(lot)
        return key is not None and a.groups[key]["reason"] is not None

    def release_unsent_for_exits(self, a: DynamicLedger, status: str, now: int) -> None:
        for lot in a.lots.values():
            if lot.pending and (status == "RISK_BREACH" or self.policy_due(a, lot.key)):
                a.cancel_unsubmitted(lot.key, now, "V3_EXIT_RELEASE_UNSENT_ONLY")

    def latch_maximum(self, a: DynamicLedger, now: int) -> None:
        for state in a.groups.values():
            max_at = state["max_decision"]
            if max_at is not None and max_at <= now:
                state["triggers"] = tuple(dict.fromkeys((*state["triggers"], "MAX_HOLD")))
                if state["reason"] is None:
                    state["reason"] = "MAX_HOLD"
                    state["exit_score"] = state.get("last_aligned")

    def guard_atomic_pair_orders(self, a: DynamicLedger, requests: dict, now: int) -> None:
        if not a.arm.startswith("R05_"):
            return
        from ..rapid_v1.shared_features import PAIRS

        for pair in PAIRS:
            first, second = pair
            q = [requests.get(j, []) for j in pair]
            if not any(q):
                continue
            if not all(q) or any(
                a.volume[j] is None
                or now - a.marks_at[j] > 5
                or abs(sum((r.delta for r in batch), ZERO))
                > ((a.volume[j] or ZERO) * D(".01")).to_integral_value(rounding=ROUND_DOWN)
                for j, batch in zip(pair, q, strict=True)
            ):
                requests.pop(first, None)
                requests.pop(second, None)
                a.reject("V3_PAIRED_JOINT_RECEIVED_CAPACITY_WAIT")
