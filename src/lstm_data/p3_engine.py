"""Single synthetic physical state engine shared across policies and frictions."""

from __future__ import annotations

from decimal import Decimal, localcontext

import pandas as pd

from .clocks import utc
from .p3_accounting import ARITHMETIC, ActionInstruction, PhysicalBook
from .p3_domain import Forecast, Frictions, Permission, PriceReference, UniverseSpec, synthetic_id
from .p3_events import EventLedger
from .p3_execution import ExecutionOffer, eligible_offer, simulated_fill
from .p3_financing import BorrowTracker
from .p3_policy import Policy, Sleeve, admission, net_target, rank_intent

D = Decimal


class PortfolioEngine:
    def __init__(
        self,
        universe: UniverseSpec,
        permission: Permission,
        policy: Policy,
        frictions: Frictions,
        cash: D,
        at: pd.Timestamp,
    ):
        permission.ensure()
        if policy.universe != universe or frictions.universe != universe:
            raise ValueError("ENGINE_UNIVERSE_BINDING_MISMATCH")
        self.universe, self.permission, self.policy = universe, permission, policy
        self.ledger = EventLedger(universe, permission)
        self.book = PhysicalBook(universe, permission, self.ledger, frictions, cash, at)
        self.borrow = BorrowTracker(universe, permission, frictions)
        self.sleeves: tuple[Sleeve, ...] = ()
        self.pending_target: tuple[tuple[str, D], ...] | None = None
        self.pending_since: pd.Timestamp | None = None
        self.pending_reason: str | None = None
        self._ended: tuple[Sleeve, ...] = ()
        self.rejections: list[str] = []
        self.exceptions: list[str] = []
        self._entries: set[str] = set()
        self.halted_sessions: set[str] = set()
        self.risk_status = "UNOBSERVED"
        self.overnight_unsupported = False
        self.action_coverage = True
        self._marked_at: pd.Timestamp | None = None
        self._mark_prices: dict[str, D] = {}

    def _references(self, refs: tuple[PriceReference, ...], at: pd.Timestamp) -> dict[str, D]:
        if len({r.symbol for r in refs}) != len(refs):
            raise ValueError("DUPLICATE_MARK")
        prices = {}
        for ref in refs:
            if ref.universe != self.universe:
                raise ValueError("REFERENCE_UNIVERSE_MISMATCH")
            if ref.reason_at(
                at
            ) == "REFERENCE_ELIGIBLE" and ref.share_basis == self.book.share_basis(ref.symbol):
                prices[ref.symbol] = ref.price
        return prices

    def _offers(self, offers: tuple[ExecutionOffer, ...]) -> dict[str, ExecutionOffer]:
        if len({o.reference.symbol for o in offers}) != len(offers):
            raise ValueError("DUPLICATE_EXECUTION_OFFER")
        if any(o.universe != self.universe for o in offers):
            raise ValueError("OFFER_UNIVERSE_MISMATCH")
        return {o.reference.symbol: o for o in offers}

    def _reject(self, key: str, at: pd.Timestamp, reason: str, parent: str) -> bool:
        self.ledger.record(key + ":REJECT", at, "REJECT", {"reason": reason}, parent)
        self.rejections.append(reason)
        return False

    def _execute(
        self,
        target: tuple[tuple[str, D], ...],
        at: pd.Timestamp,
        key: str,
        offers: dict[str, ExecutionOffer],
        *,
        cutoff: pd.Timestamp | None = None,
        minute: bool = False,
        entry: bool = False,
        parent: str | None = None,
    ) -> bool:
        orders = self.book.orders_for_target(target, at, key + ":TARGET", parent)
        prices = dict(self._mark_prices) if at == self._marked_at else {}
        prices.update(self._references(tuple(o.reference for o in offers.values()), at))
        self.borrow.observe(self.book, prices, at)
        with localcontext(ARITHMETIC):
            for order in orders:
                offer = offers.get(order.symbol)
                eligible = (
                    eligible_offer(offer, at, cutoff=cutoff, minute=minute, require_at_cutoff=entry)
                    and offer is not None
                    and offer.reference.share_basis == order.share_basis
                )
                if eligible and offer is not None:
                    quantity = order.quantity * offer.fraction
                    fee = self.book.frictions.fee(quantity, offer.reference.price)
                    fill = simulated_fill(order, offer, at, fee)
                    if fill is not None:
                        self.book.fill(fill)
                        self.borrow.observe(self.book, prices, at)
                left = dict((o.order_id, q) for o, q in self.book.outstanding).get(order.order_id)
                if left:
                    reason = (
                        "MISSING_REFERENCE"
                        if offer is None
                        else ("INELIGIBLE_REFERENCE" if not eligible else offer.outcome)
                    )
                    self.book.cancel(order.order_id, at, reason)
        return self.book.balances == target

    def enter(
        self,
        forecast: Forecast,
        at: pd.Timestamp,
        offers: tuple[ExecutionOffer, ...],
        marks: tuple[PriceReference, ...],
    ) -> bool:
        self.permission.ensure()
        at = utc(at)
        if forecast.universe != self.universe:
            raise ValueError("FORECAST_UNIVERSE_MISMATCH")
        if forecast.forecast_id in self._entries:
            raise ValueError("FORECAST_ALREADY_PROCESSED_USE_REPLAY_FRAME_IDEMPOTENCE")
        self.monitor(at, marks, forecast.forecast_id + ":PRE")
        intent = rank_intent(forecast)
        self.ledger.record(
            forecast.forecast_id,
            at,
            "FORECAST",
            {
                "scores": forecast.scores,
                "issuance": forecast.plan.issuance,
                "input_version": forecast.input_version,
                "model_version": forecast.model_version,
                "basis": forecast.basis,
                "policy": self.policy.name,
            },
        )
        self.ledger.record(
            intent.intent_id,
            at,
            "INTENT",
            {"long": intent.long, "short": intent.short, "constant_scores": intent.constant_scores},
            forecast.forecast_id,
        )
        self._entries.add(forecast.forecast_id)
        plan = forecast.plan
        if not plan.calendar_valid or plan.entry != at or plan.cutoff is None or plan.exit is None:
            return self._reject(intent.intent_id, at, "INVALID_P2_ENTRY_CLOCK", intent.intent_id)
        if self.pending_target is not None:
            return self._reject(intent.intent_id, at, "OUTSTANDING_EXCEPTION", intent.intent_id)
        if any(s.expires_at <= at for s in self.sleeves):
            return self._reject(intent.intent_id, at, "OVERDUE_UNRESOLVED_EXIT", intent.intent_id)
        if at.tz_convert("America/New_York").date().isoformat() in self.halted_sessions:
            return self._reject(intent.intent_id, at, "EMERGENCY_SESSION_HALT", intent.intent_id)
        if self.risk_status in {"INCOMPLETE", "INVALID"} or not self.action_coverage:
            return self._reject(intent.intent_id, at, "RISK_OR_ACTION_INCOMPLETE", intent.intent_id)
        if self.borrow.total is None or self.overnight_unsupported:
            return self._reject(intent.intent_id, at, "FINANCING_INCOMPLETE", intent.intent_id)
        lookup = self._offers(offers)
        if any(
            not eligible_offer(lookup.get(s), at, cutoff=plan.cutoff, require_at_cutoff=True)
            or (s in lookup and lookup[s].reference.share_basis != self.book.share_basis(s))
            for s in (intent.long, intent.short)
        ):
            return self._reject(intent.intent_id, at, "PAIR_REFERENCE_INELIGIBLE", intent.intent_id)
        if self.policy.veto(intent, self.sleeves):
            return self._reject(intent.intent_id, at, "POLICY_B_VIRTUAL_CONFLICT", intent.intent_id)
        valuation = self.book.valuation(marks, at)
        equity = valuation["accrual_equity"]
        if equity is None or equity <= 0:
            return self._reject(
                intent.intent_id, at, "EQUITY_INCOMPLETE_OR_INVALID", intent.intent_id
            )
        prices = self._references(marks, at)
        if any(
            self.book.quantity(s) and prices.get(s) != lookup[s].reference.price
            for s in (intent.long, intent.short)
        ):
            return self._reject(
                intent.intent_id, at, "ENTRY_MARK_REFERENCE_MISMATCH", intent.intent_id
            )
        prices.update({s: lookup[s].reference.price for s in (intent.long, intent.short)})
        sleeve = self.policy.propose(
            intent, equity, prices, at, plan.exit, plan.cutoff + pd.Timedelta(hours=4)
        )
        target = net_target(self.universe, self.sleeves + (sleeve,))
        projected = admission(self.book.frictions, equity, self.book.balances, target, prices)
        if not projected["accepted"]:
            return self._reject(intent.intent_id, at, projected["reason"], intent.intent_id)
        self.ledger.record(
            sleeve.sleeve_id,
            at,
            "SLEEVE",
            {
                "quantities": sleeve.quantities,
                "pre_entry_equity": equity,
                "expires_at": sleeve.expires_at,
                "projection": projected,
            },
            intent.intent_id,
        )
        self.sleeves += (sleeve,)
        complete = self._execute(
            target,
            at,
            sleeve.sleeve_id,
            lookup,
            cutoff=plan.cutoff,
            parent=sleeve.sleeve_id,
            entry=True,
        )
        if not complete:
            self._pending_flat(at, "PARTIAL_PAIR_ENTRY", sleeve.sleeve_id)
        return True

    def _pending_flat(self, at: pd.Timestamp, reason: str, parent: str | None = None) -> None:
        self.pending_target = tuple((s, D(0)) for s in self.universe.symbols)
        self.pending_since, self.pending_reason = at, reason
        self._ended = self.sleeves
        self.ledger.record(
            "SYN:" + reason + ":" + at.isoformat(),
            at,
            "EXCEPTION",
            {"reason": reason, "physical": self.book.balances},
            parent,
        )
        self.exceptions.append(reason)

    def expire(self, at: pd.Timestamp, offers: tuple[ExecutionOffer, ...], key: str) -> None:
        self.permission.ensure()
        synthetic_id(key)
        at = utc(at)
        due = tuple(s for s in self.sleeves if s.expires_at <= at)
        if not due or self.pending_target is not None:
            return
        remaining = tuple(s for s in self.sleeves if s not in due)
        target = net_target(self.universe, remaining)
        cutoffs = {s.exit_reference_at for s in due}
        # A delayed visit is a retry opportunity, never backdated proxy execution.
        cutoff = (
            next(iter(cutoffs))
            if len(cutoffs) == 1 and all(s.expires_at == at for s in due)
            else None
        )
        complete = self._execute(target, at, key, self._offers(offers), cutoff=cutoff)
        if complete:
            self.sleeves = remaining
            for sleeve in due:
                self.ledger.record(
                    sleeve.sleeve_id + ":END",
                    at,
                    "SLEEVE_END",
                    {"reason": "SCHEDULED_EXIT", "actual_exit": at},
                    sleeve.sleeve_id,
                )
        else:
            self.pending_target, self.pending_since = target, at
            self.pending_reason = "MISSING_SCHEDULED_EXIT"
            self._ended = due
            self.exceptions.append(self.pending_reason)
            self.ledger.record(
                key + ":EXCEPTION",
                at,
                "EXCEPTION",
                {"reason": self.pending_reason, "physical": self.book.balances},
            )
            for s, q in self.book.balances:
                if q:
                    self.book.retain_missing_exit(s, at)

    def monitor(self, at: pd.Timestamp, marks: tuple[PriceReference, ...], key: str) -> dict:
        """Scheduled observations only; missing marks never imply zero leverage."""
        from .p3_risk import physical_risk

        self.permission.ensure()
        at = utc(at)
        self._detect_overnight(at)
        valuation = self.book.valuation(marks, at)
        prices = self._references(marks, at)
        self._marked_at, self._mark_prices = at, prices
        self.borrow.observe(self.book, prices, at)
        self.ledger.record(key + ":MARK", at, "MARK", {"references": marks})
        risk = physical_risk(self.universe, valuation["accrual_equity"], self.book.balances, prices)
        self.risk_status = risk["status"]
        self.ledger.record(key + ":RISK", at, "RISK", risk, key + ":MARK")
        if risk["emergency"]:
            self.halted_sessions.add(at.tz_convert("America/New_York").date().isoformat())
            if self.pending_reason != "EMERGENCY_GROSS":
                self._pending_flat(at, "EMERGENCY_GROSS", key + ":RISK")
        return risk

    def retry(self, at: pd.Timestamp, offers: tuple[ExecutionOffer, ...], key: str) -> bool:
        """Only a supplied later RTH minute event may satisfy an exceptional order."""
        self.permission.ensure()
        at = utc(at)
        self._detect_overnight(at)
        if self.pending_target is None:
            return False
        if self.pending_since is None or at <= self.pending_since:
            raise ValueError("NEXT_CAUSAL_MINUTE_RETRY_REQUIRED")
        from .clocks import session_clock

        clock = session_clock(at.tz_convert("America/New_York").date().isoformat())
        if (
            clock.open is None
            or clock.close is None
            or not clock.open <= at < clock.close
            or at != at.floor("min")
        ):
            raise ValueError("RETRY_OUTSIDE_RTH_MINUTE")
        # While an exit is pending another sleeve may itself expire. Do not reopen it.
        if self.pending_reason == "MISSING_SCHEDULED_EXIT":
            due = tuple(s for s in self.sleeves if s.expires_at <= at)
            self._ended = due
            self.pending_target = net_target(
                self.universe, tuple(s for s in self.sleeves if s not in due)
            )
        self.ledger.record(
            key + ":RETRY",
            at,
            "RETRY",
            {
                "reason": self.pending_reason,
                "scheduled_failure_at": self.pending_since,
                "physical_before": self.book.balances,
                "real_policy": "PENDING_REAL_EXECUTION_SOURCE_OR_SHARED_EXCEPTION_AMENDMENT",
            },
        )
        complete = self._execute(
            self.pending_target, at, key, self._offers(offers), minute=True, parent=key + ":RETRY"
        )
        if not complete:
            return False
        ended_ids = {s.sleeve_id for s in self._ended}
        for sleeve in self._ended:
            self.ledger.record(
                sleeve.sleeve_id + ":END",
                at,
                "SLEEVE_END",
                {
                    "reason": self.pending_reason,
                    "actual_exit": at,
                    "realized_minutes": (at - sleeve.entered_at).total_seconds() / 60,
                },
                sleeve.sleeve_id,
            )
        self.sleeves = tuple(s for s in self.sleeves if s.sleeve_id not in ended_ids)
        self.pending_target = self.pending_since = self.pending_reason = None
        self._ended = ()
        self.book.clear_resolved_exits()
        return True

    def _detect_overnight(self, at: pd.Timestamp) -> None:
        day = at.tz_convert("America/New_York").date()
        if any(s.entered_at.tz_convert("America/New_York").date() != day for s in self.sleeves):
            self.overnight_unsupported = True

    def apply_actions(self, actions: tuple[ActionInstruction, ...], at: pd.Timestamp) -> None:
        """Preserve primitive sequence validation and transform virtual split units only."""
        from dataclasses import replace

        self.permission.ensure()
        typed = actions
        if any(a.boundary != utc(at) or a.universe != self.universe for a in typed):
            raise ValueError("ACTION_FRAME_BINDING_MISMATCH")
        if len({(a.boundary, a.sequence) for a in typed}) != len(typed):
            raise ValueError("AMBIGUOUS_SAME_TIME_ACTION_SEQUENCE")
        for action in sorted(typed, key=lambda a: (a.boundary, a.sequence, a.action_id)):
            if self.book.action(action) and action.kind == "SPLIT":
                self.sleeves = tuple(
                    replace(
                        s,
                        quantities=self.book.transform_virtual_split(
                            s.quantities, s.entered_at, action
                        ),
                    )
                    for s in self.sleeves
                )
                if self.pending_target is not None:
                    start = min((s.entered_at for s in self.sleeves), default=self.book.as_of)
                    self.pending_target = self.book.transform_virtual_split(
                        self.pending_target, start, action
                    )
                ended_ids = {s.sleeve_id for s in self._ended}
                self._ended = tuple(s for s in self.sleeves if s.sleeve_id in ended_ids)

    def valuation(self, at: pd.Timestamp, marks: tuple[PriceReference, ...], key: str) -> dict:
        self.permission.ensure()
        snapshot = self.book.valuation(marks, at)
        reasons = []
        if snapshot["accrual_equity"] is None:
            reasons.append("MISSING_MARK")
        elif snapshot["accrual_equity"] <= 0:
            reasons.append("NONPOSITIVE_EQUITY")
        if self.pending_target is not None:
            reasons.append("UNRESOLVED_EXECUTION")
        if snapshot["unknown_payment_claims"]:
            reasons.append("UNKNOWN_PAYABLE_DATE")
        if self.borrow.total is None:
            reasons.append("INCOMPLETE_BORROW")
        day = utc(at).tz_convert("America/New_York").date().isoformat()
        if any(
            s.entered_at.tz_convert("America/New_York").date().isoformat() != day
            for s in self.sleeves
        ):
            self.overnight_unsupported = True
        if self.overnight_unsupported:
            reasons.append("UNAPPROVED_OVERNIGHT_FINANCING")
        if not self.action_coverage:
            reasons.append("UNKNOWN_ACTION_COVERAGE")
        result = {
            **snapshot,
            "toy_accrual_equity": snapshot["accrual_equity"],
            "NAV": None if reasons else snapshot["accrual_equity"],
            "status": "INCOMPLETE_OR_INVALID" if reasons else "SYNTHETIC_ASSUMPTION_DEPENDENT",
            "incomplete_reasons": reasons,
            "G4_scientific": "HOLD",
            "permission": self.permission.mode,
            "P2_handoff_sha": self.permission.ensure(),
        }
        self.ledger.record(key + ":VALUATION", at, "VALUATION", result)
        return result
