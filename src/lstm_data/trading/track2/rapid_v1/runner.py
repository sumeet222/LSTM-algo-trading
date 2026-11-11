"""One received-minute pass, eighteen isolated compact funded accounts."""

import copy
import time
from collections import Counter
from dataclasses import replace
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import numpy as np

from ..stage35.completion_v3.tapes import load_actions, midnight
from ..stage35.final_backtest_v4.book import integer_cross
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import Day, minute
from ..stage35.final_backtest_v4.protocol import Scenario
from ..stage35.final_backtest_v5.driver import Driver as V5Driver
from ..stage35.final_backtest_v5.special import cross_exact
from .costs import CostReference
from .diagnostics import QualityBook
from .paths import canonical
from .portfolio import FastAccount, Lot, Order, Request
from .registry import verify_registry
from .scheduler import EntryBudget
from .shared_features import FeatureCache, FeatureFrame
from .sources import RawDay, RawMarket
from .strategies import IDS, DirectionIntent, evaluate, mode

D = Decimal
ZERO = D(0)


class FastEngine(V5Driver):
    def __init__(self, cache: FeatureCache, first: str, last: str):
        self.registry = verify_registry()
        self.cache = cache
        self.market = RawMarket(first, last)
        self.execution_calendar = ExecutionCalendar(self.market.clock)
        self.fast_accounts = [
            FastAccount(
                s,
                mode(s),
                Scenario(
                    name=s,
                    fee=D(".002") if s.startswith("M") else D(".005"),
                    minimum=ZERO if s.startswith("M") else D(1),
                ),
            )
            for s in IDS
        ]
        self.accounts = list(self.fast_accounts)
        self.first, self.last, self.diagnostic = first, last, False
        self.scenarios = tuple(a.scenario for a in self.fast_accounts)
        self.special = {}
        self.special_pending = {}
        self.ogn_borrow_cursors = {}
        self.actions = load_actions()
        self.due = []
        for a in self.actions:
            if a.action_type not in ("CASH_DIVIDEND", "SPLIT"):
                continue
            day = a.ex_date or a.effective_date
            if day:
                self.due.append(
                    (minute(midnight(day)), 0 if a.action_type == "SPLIT" else 1, "EX", a)
                )
            if a.action_type == "CASH_DIVIDEND" and a.payable_date:
                self.due.append((minute(midnight(a.payable_date)), 2, "PAY", a))
        self.due.sort(key=lambda x: (x[0], x[1], x[3].event_id))
        self.done_due = set()
        self.integrals = np.zeros(20, dtype=object)
        self.last_prices = np.zeros(20, float)
        self.known_closes = np.full(20, np.nan)
        self.known_marks = np.full(20, -1, dtype=np.int64)
        self.known_volumes = np.full(20, np.nan)
        self.cursor = None
        self.risk_cache = {}
        self.policy_counts = {}
        self.day_groups = {}
        self.budgets = {s: EntryBudget(mode(s)) for s in IDS}
        self.paired_lots: dict[str, str] = {}
        self.quality = QualityBook()
        self.daily_rows: dict[str, list[dict]] = {s: [] for s in IDS}
        self.signal_rows: dict[str, list[dict]] = {s: [] for s in IDS}
        self.account_holds: dict[str, list[str]] = {}
        self.current_refs: dict[str, np.ndarray] = {}
        self.days_completed = 0
        self.last_completed = None
        self.last_market_end = None
        self.checkpoint_dir: Path | None = None
        self.phase_seconds: dict[str, float] = {"financial_days": 0.0}

    def before_day(self, day: Day) -> None:
        before = set(self.done_due)
        super().before_day(day)
        for _, _, kind, action in self.due:
            key = (action.event_id, kind)
            if (
                key in before
                or key not in self.done_due
                or kind != "EX"
                or action.action_type != "SPLIT"
            ):
                continue
            from ..stage012.model_registry import SYMBOLS

            j = SYMBOLS.index(action.symbol)
            ratio = float(action.split_ratio_new_old or 1)
            for account in self.fast_accounts:
                for order in account.pending.values():
                    if order.ticker == j and order.key in account.cost_references:
                        reference = account.cost_references[order.key]
                        account.cost_references[order.key] = replace(
                            reference, adv20_raw_shares=reference.adv20_raw_shares * ratio
                        )

    def cost_reference(self, a: FastAccount, j: int, now: int, entry: bool) -> CostReference | None:
        if a.population == "RETAIL_CONSERVATIVE":
            return CostReference(a.population, available_at=now)
        v = self.current_refs
        ratio = float(v["v20"][j] / v["v60"][j]) if v["v60"][j] > 0 else np.nan
        adv = float(v["adv20"][j])
        if not (np.isfinite(ratio) and np.isfinite(adv) and adv > 0):
            if entry:
                return None
            a.stats.counts["EXIT_COST_FALLBACK_MAX_ATTEMPTS"] += 1
            ratio, adv = 2.0, 1.0  # Declared maximum-friction exit fallback, never a zero cost.
        return CostReference(a.population, ratio, adv, now)

    def special_tick(self, n: int, bar: dict | None, start: int, now: int) -> None:
        a = self.fast_accounts[n]
        before = self.special.get(n)
        old_count = a.stats.counts["OGN_EXTERNAL_DISPOSAL"]
        super().special_tick(n, bar, start, now)
        if (
            before is None
            or a.population != "MICRO_PRO"
            or a.stats.counts["OGN_EXTERNAL_DISPOSAL"] == old_count
        ):
            return
        after = self.special[n]
        # Preserve V5 special reference/tick convention; correct only its
        # rounded-to-cent micro commission to exact .002 per physical share.
        old_fees = after.fee_allocations[len(before.fee_allocations) :]
        new_fills = after.whole_fills[len(before.whole_fills) :]
        external = sum((q for _, q in new_fills), ZERO)
        if not external:
            return
        reference = after.mark
        if bar is None or reference is None:
            raise ValueError("SPECIAL_FILL_REFERENCE")
        raw = D(str(bar["o"]))
        price = (raw * (1 + D(".001") * (1 if external > 0 else -1))).quantize(
            D(".01"), rounding="ROUND_UP" if external > 0 else ROUND_DOWN
        )
        remaining = {
            lot.cohort_id: lot.whole_attribution
            + sum((q for k, q in before.whole_fills if k == lot.cohort_id), ZERO)
            for lot in before.lots
        }
        desired = D(".002") * abs(external)
        legs = cross_exact(
            tuple((k, -q) for k, q in sorted(remaining.items()) if q), raw, price, external, desired
        )
        old_by = {}
        for k, v in old_fees:
            old_by[k] = old_by.get(k, ZERO) + v
        new_by = {}
        for leg in legs:
            new_by[leg.cohort_id] = new_by.get(leg.cohort_id, ZERO) + leg.fee
        for k in sorted(set(old_by) | set(new_by)):
            delta = new_by.get(k, ZERO) - old_by.get(k, ZERO)
            a.credit(k, -delta, "OGN_MICRO_COMMISSION_PRECISION", now)
            a.lots[k].fees += delta
            a.lots[k].cost += delta
        delta = desired - sum((v for _, v in old_fees), ZERO)
        a.commission += delta
        a.special_cash -= delta
        a.stats.physical_rows[-1]["commission"] = desired
        costs = []
        old_costs = after.cost_allocations[len(before.cost_allocations) :]
        for (k, value), leg, (_, old_fee) in zip(old_costs, legs, old_fees, strict=True):
            costs.append((k, value + leg.fee - old_fee))
        self.special[n] = replace(
            after,
            fee_allocations=before.fee_allocations
            + tuple((lot_item.cohort_id, lot_item.fee) for lot_item in legs),
            cost_allocations=before.cost_allocations + tuple(costs),
        )
        a.reconcile()

    def active_duplicate(self, a: FastAccount, j: int, sign: int) -> bool:
        return any(
            lot_item.ticker == j and (lot_item.quantity * sign > 0 or lot_item.pending * sign > 0)
            for lot_item in a.lots.values()
        )

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
        amount_each = budget / len(ready)
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

    def decide(
        self,
        n: int,
        day: RawDay,
        now: int,
        frame: FeatureFrame | None,
        intents: tuple[DirectionIntent, ...],
    ) -> None:
        a = self.fast_accounts[n]
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
        requests: dict[int, list[Request]] = {}
        for lot in a.lots.values():
            if lot.pending and now > lot.deadline:
                a.cancel_unsubmitted(lot.key, now, "ENTRY_LIFETIME")
            if lot.quantity and (now >= lot.endpoint + 2 or status == "RISK_BREACH"):
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

    def settle_pending(
        self, n: int, day: RawDay, i: int, now: int, start: int, integral: np.ndarray
    ) -> bool:
        a = self.fast_accounts[n]
        due = [(j, o) for j, o in a.pending.items() if o.effective <= start]
        if not due:
            return False
        a.accrue(integral, now)
        a.accrue_funding(start)
        groups: dict[str, list[int]] = {}
        for j, o in due:
            pair = next(
                (self.paired_lots[r.key] for r in o.requests if r.key in self.paired_lots), None
            )
            if pair:
                groups.setdefault(pair, []).append(j)
        handled = set()
        for pair, js in groups.items():
            orders = [a.pending[j] for j in js]
            if len(js) != 2:
                raise ValueError("ATOMIC_PAIR_ORDER_SET")
            if any(o.expiry is not None and start > o.expiry for o in orders):
                for o in orders:
                    self.expire(a, o, now)
            elif all(day.valid[i, j] for j in js):
                candidate = copy.deepcopy(a)
                for j in js:
                    self.attempt(candidate, day, i, candidate.pending[j], now, start)
                a.__dict__.update(candidate.__dict__)
            else:
                a.stats.counts["PAIR_PENDING_JOINT_VALID_BAR"] += 1
            handled.update(js)
        for j, o in due:
            if j not in handled:
                self.attempt(a, day, i, o, now, start)
        return True

    def run(self, stop_after: int | None = None) -> dict:
        started = time.monotonic()
        final_session = max(d for d in self.cache.by_date if self.first <= d <= self.last)
        year_ends = {
            max(d for d in self.cache.by_date if d.startswith(year))
            for year in sorted({d[:4] for d in self.cache.by_date})
        }
        for day in self.market.days():
            if self.last_completed is not None and day.date <= self.last_completed:
                continue
            t = time.monotonic()
            frames = self.cache.frames(day.date)
            if not frames:
                raise ValueError("SHARED_FEATURE_DAY_MISSING")
            self.current_refs = frames[0].values
            frame_at = {f.decision: f for f in frames}
            self.risk_cache.clear()
            self.before_day(day)
            factor = frames[0].values["factor"]
            for a in self.fast_accounts:
                a.source_pointer = day.source_hash
            for i, start0 in enumerate(day.starts):
                start = int(start0)
                self.integrate_gap(start)
                ibefore = self.integrals.copy()
                valid = day.valid[i]
                pricing = np.where(valid, day.opens[i], self.last_prices)
                ticks = np.rint(pricing * 1000000).astype(np.int64)
                self.integrals += ticks * 60
                self.cursor = start + 1
                self.last_prices = np.where(valid, day.closes[i], self.last_prices)
                self.known_closes = np.where(valid, day.closes[i], self.known_closes)
                self.known_marks = np.where(valid, start + 1, self.known_marks)
                self.known_volumes = np.where(valid, day.volumes[i], self.known_volumes)
                now = start + 3
                self.quality.tick(day, i, factor)
                frame = frame_at.get(now)
                for n, a in enumerate(self.fast_accounts):
                    due = self.settle_pending(n, day, i, now, start, ibefore)
                    special_active = n in self.special and (
                        not self.special[n].whole_settled or self.special[n].cil_reference is None
                    )
                    if special_active:
                        self.special_tick(n, day.ogn.get(start), start, now)
                    if due or special_active:
                        self.risk_cache.pop(n, None)
                    intents = ()
                    if frame is not None:
                        decision = evaluate(a.arm, frame)
                        intents = decision.intents
                        reasons = Counter(decision.reasons)
                        self.signal_rows[a.arm].append(
                            {
                                "date": day.date,
                                "slot": frame.slot,
                                "scheduled": decision.scheduled,
                                "calendar_names": 20,
                                "potential": 20 if decision.scheduled else 0,
                                "candidate_intents": len(intents),
                                "long_legs": sum(s > 0 for x in intents for s in x.signs),
                                "short_legs": sum(s < 0 for x in intents for s in x.signs),
                                **dict(reasons),
                            }
                        )
                        for intent in intents:
                            exit_at = self.execution_calendar.next(intent.endpoint + 2)
                            if exit_at <= minute(self.last + "T23:59:00Z"):
                                self.quality.add(intent, self.execution_calendar.next(now), exit_at)
                            else:
                                self.quality.reasons[a.arm]["CALENDAR_TERMINAL_CUTOFF"] += 1
                    held = bool(np.any(a.quantity)) or any(
                        lot_item.pending for lot_item in a.lots.values()
                    )
                    state = self.risk_status(n) if held else "READY"
                    relevant = (
                        bool(intents)
                        or state == "RISK_BREACH"
                        or any(
                            lot_item.pending or lot_item.quantity and now >= lot_item.endpoint + 2
                            for lot_item in a.lots.values()
                        )
                    )
                    if relevant:
                        self.decide(n, day, now, frame, intents)
                        self.risk_cache.pop(n, None)
            end = int(day.starts[-1]) + 1
            self.last_market_end = end
            for n, a in enumerate(self.fast_accounts):
                now = end + 2
                for j, o in list(a.pending.items()):
                    if o.expiry is not None and o.expiry <= end - 1:
                        self.expire(a, o, now)
                self.sync(a, now)
                a.accrue(self.integrals, now)
                a.accrue_funding(end)
                a.reconcile()
                nav = a.nav()
                stale = any(a.quantity[j] and now - a.marks_at[j] > 5 for j in range(20))
                status = (
                    "OBSERVED"
                    if nav is not None and nav > 0 and not stale and not a.risk_hold
                    else "HOLD"
                )
                if status != "OBSERVED":
                    self.account_holds.setdefault(a.arm, []).append(
                        day.date + ":UNPRICED_STALE_OR_NONPOSITIVE_NAV"
                    )
                self.daily_rows[a.arm].append(
                    {
                        "date": day.date,
                        "nav": nav,
                        "cash": a.cash,
                        "restricted": a.restricted(),
                        "claims": a.claim_total(),
                        "special": sum(a.special_values.values(), ZERO),
                        "physical_value": sum(
                            (D(int(q)) * (a.prices[j] or ZERO) for j, q in enumerate(a.quantity)),
                            ZERO,
                        ),
                        "virtual_gross": a.gross()
                        + sum((abs(v) for v in a.special_values.values()), ZERO),
                        "physical_gross": sum(
                            (
                                D(abs(int(q))) * (a.prices[j] or ZERO)
                                for j, q in enumerate(a.quantity)
                            ),
                            ZERO,
                        ),
                        "commission": a.commission,
                        "friction": a.friction,
                        "borrow": a.borrow_paid,
                        "funding": a.funding_paid,
                        "dividend_cash": a.dividend_cash,
                        "special_cash": a.special_cash,
                        "status": status,
                        "pending": len(a.pending),
                        "stock_positions": int(np.count_nonzero(a.quantity)),
                        "balance_residual": a.maximum_residual,
                    }
                )
                a.compact(now)
            self.days_completed += 1
            self.last_completed = day.date
            self.phase_seconds["financial_days"] += time.monotonic() - t
            if self.days_completed % 50 == 0:
                print(
                    "rapid days",
                    self.days_completed,
                    "elapsed",
                    round(time.monotonic() - started, 2),
                    flush=True,
                )
            stopping = stop_after is not None and self.days_completed >= stop_after
            if self.checkpoint_dir is not None and (
                day.date in year_ends or day.date == final_session or stopping
            ):
                from .state import write_state

                write_state(self.checkpoint_dir / (day.date + ".json.gz"), self)
            if stopping:
                break
        return {
            "days": self.days_completed,
            "elapsed_seconds": time.monotonic() - started,
            "holds": self.account_holds,
            "maximum_balance_residual": str(
                max((a.maximum_residual for a in self.fast_accounts), default=ZERO)
            ),
        }
