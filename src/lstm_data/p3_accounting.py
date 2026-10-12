"""Generic physical fills and a reversible shim to unchanged P1.CA primitives.

Only this adapter knows the legacy validator's five symbol keys. The injected
ordered universe maps by ordinal; no ticker-specific arithmetic or source claim.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext

import pandas as pd

from . import corporate_actions as ca
from .clocks import utc
from .labels import UNIVERSE as LEGACY_KEYS
from .p3_domain import (
    SHARE_BASIS,
    Fill,
    Frictions,
    Order,
    Permission,
    PriceReference,
    UniverseSpec,
    synthetic_id,
)
from .p3_events import EventLedger, json_value

ARITHMETIC = Context(prec=40, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class ActionInstruction:
    universe: UniverseSpec
    action_id: str
    symbol: str
    kind: str
    boundary: pd.Timestamp
    known_at: pd.Timestamp
    amount: Decimal
    share_basis: str
    sequence: int = 0
    post_split_basis: str | None = None
    payable_date: date | None = None
    fractional_policy: str | None = None
    basis: str = "SYNTHETIC"

    def __post_init__(self) -> None:
        self.universe.check_symbol(self.symbol)
        synthetic_id(self.action_id)
        synthetic_id(self.share_basis)
        if self.post_split_basis:
            synthetic_id(self.post_split_basis)
        object.__setattr__(self, "boundary", utc(self.boundary))
        object.__setattr__(self, "known_at", utc(self.known_at))
        object.__setattr__(self, "amount", ca.number(self.amount))
        if self.basis != "SYNTHETIC" or self.known_at > self.boundary:
            raise ValueError("SYNTHETIC_KNOWN_ACTION_REQUIRED")
        # Reuse the original type/rate/boundary/fractional/settlement validation.
        action_primitive(self)


def action_primitive(action: ActionInstruction) -> ca.Action:
    alias = LEGACY_KEYS[action.universe.symbols.index(action.symbol)]
    from .config import fingerprint

    source = ca.SourceEvidence(
        action.action_id,
        fingerprint(
            [action.action_id, action.universe.universe_id, action.kind, str(action.amount)]
        ),
        action.known_at.to_pydatetime(),
        action.known_at.to_pydatetime(),
    )
    return ca.Action(
        source,
        alias,
        action.kind,
        action.boundary.to_pydatetime(),
        action.sequence,
        action.amount,
        action.share_basis,
        action.post_split_basis,
        action.payable_date,
        action.fractional_policy,
    )


class PhysicalBook:
    def __init__(
        self,
        universe: UniverseSpec,
        permission: Permission,
        ledger: EventLedger,
        frictions: Frictions,
        cash: Decimal,
        at: pd.Timestamp,
    ):
        permission.ensure()
        if ledger.universe != universe or frictions.universe != universe:
            raise ValueError("BOOK_UNIVERSE_BINDING_MISMATCH")
        self.universe, self.permission, self.ledger, self.frictions = (
            universe,
            permission,
            ledger,
            frictions,
        )
        self._alias = dict(zip(universe.symbols, LEGACY_KEYS))
        self._inverse: dict[str, str] = dict(zip(LEGACY_KEYS, universe.symbols))
        self._epochs = {symbol: SHARE_BASIS for symbol in universe.symbols}
        at = utc(at)
        self._account = ca.Account(
            ca.number(cash),
            tuple(
                ca.Position(
                    alias, "SYN:POSITION:" + symbol, Decimal(0), at.to_pydatetime(), SHARE_BASIS
                )
                for symbol, alias in self._alias.items()
            ),
            at.to_pydatetime(),
        )
        self._orders: dict[str, Order] = {}
        self._remaining: dict[str, Decimal] = {}
        self._fills: dict[str, Fill] = {}
        self._debits: dict[str, tuple] = {}
        self._action_boundaries: set[pd.Timestamp] = set()
        self._fill_boundaries: set[pd.Timestamp] = set()
        self.execution_fees = Decimal(0)
        self.ledger.record(
            "SYN:ACCOUNT",
            at,
            "ACCOUNT",
            {
                "cash": self.cash,
                "symbols": universe.symbols,
                "basis": "SYNTHETIC",
                "arithmetic": "DECIMAL40_HALF_EVEN_EXACT_FRACTIONAL_ASSUMPTION",
            },
        )

    @property
    def cash(self) -> Decimal:
        return self._account.cash

    @property
    def as_of(self) -> pd.Timestamp:
        return pd.Timestamp(self._account.as_of)

    def quantity(self, symbol: str) -> Decimal:
        self.universe.check_symbol(symbol)
        return next(p.quantity for p in self._account.positions if p.symbol == self._alias[symbol])

    def share_basis(self, symbol: str) -> str:
        self.universe.check_symbol(symbol)
        return self._epochs[symbol]

    @property
    def balances(self) -> tuple[tuple[str, Decimal], ...]:
        return tuple((symbol, self.quantity(symbol)) for symbol in self.universe.symbols)

    @property
    def outstanding(self) -> tuple[tuple[Order, Decimal], ...]:
        return tuple((self._orders[key], left) for key, left in self._remaining.items() if left)

    def orders_for_target(
        self,
        targets: tuple[tuple[str, Decimal], ...],
        at: pd.Timestamp,
        target_id: str,
        parent_id: str | None = None,
    ) -> tuple[Order, ...]:
        self.permission.ensure()
        if tuple(s for s, _ in targets) != self.universe.symbols:
            raise ValueError("EXACT_ORDERED_UNIVERSE_TARGET_REQUIRED")
        synthetic_id(target_id)
        normalized = tuple((s, ca.number(q)) for s, q in targets)
        self.ledger.record(
            target_id,
            at,
            "TARGET",
            {"desired_physical": normalized, "physical_before": self.balances},
            parent_id,
        )
        orders = []
        for symbol, target in normalized:
            with localcontext(ARITHMETIC):
                delta = target - self.quantity(symbol)
            if not delta:
                continue
            order = Order(
                self.universe,
                target_id + ":ORDER:" + symbol,
                target_id,
                at,
                symbol,
                delta,
                self.share_basis(symbol),
            )
            self.register_order(order)
            orders.append(order)
        return tuple(orders)

    def register_order(self, order: Order) -> None:
        self.permission.ensure()
        if order.universe != self.universe or order.share_basis != self.share_basis(order.symbol):
            raise ValueError("ORDER_UNIVERSE_OR_SHARE_EPOCH_MISMATCH")
        previous = self._orders.get(order.order_id)
        if previous is not None and previous != order:
            raise ValueError("DIVERGENT_DUPLICATE_ORDER")
        self.ledger.record(
            order.order_id,
            order.at,
            "ORDER",
            {"symbol": order.symbol, "quantity": order.quantity, "share_basis": order.share_basis},
            order.parent_id,
        )
        if previous is None:
            self._orders[order.order_id] = order
            self._remaining[order.order_id] = order.quantity

    def cancel(self, order_id: str, at: pd.Timestamp, reason: str) -> None:
        self.permission.ensure()
        if order_id not in self._orders:
            raise ValueError("UNKNOWN_ORDER")
        self.ledger.record(
            order_id + ":CANCEL:" + utc(at).isoformat(),
            at,
            "EXCEPTION",
            {"reason": reason, "unfilled_quantity": self._remaining[order_id]},
            order_id,
        )
        self._remaining[order_id] = Decimal(0)

    def fill(self, fill: Fill) -> None:
        self.permission.ensure()
        previous = self._fills.get(fill.fill_id)
        if previous is not None:
            if previous != fill:
                raise ValueError("DIVERGENT_DUPLICATE_FILL")
            return
        left = self._remaining.get(fill.order.order_id)
        if fill.at in self._action_boundaries:
            raise ValueError("UNAPPROVED_SAME_TIME_ACTION_FILL_ORDERING")
        if (
            fill.universe != self.universe
            or self._orders.get(fill.order.order_id) != fill.order
            or left is None
            or fill.quantity * left <= 0
            or abs(fill.quantity) > abs(left)
            or fill.at < self.as_of
            or fill.reference.share_basis != self.share_basis(fill.order.symbol)
        ):
            raise ValueError("FILL_REMAINDER_TIME_OR_UNIVERSE_MISMATCH")
        with localcontext(ARITHMETIC):
            expected_fee = self.frictions.fee(fill.quantity, fill.reference.price)
            if fill.fee != expected_fee:
                raise ValueError("FILL_FRICTION_EPOCH_OR_FEE_MISMATCH")
            alias = self._alias[fill.order.symbol]
            positions = []
            before_quantity = self.quantity(fill.order.symbol)
            after_quantity = before_quantity + fill.quantity
            for position in self._account.positions:
                if position.symbol != alias:
                    positions.append(position)
                else:
                    since = (
                        position.held_since
                        if before_quantity * after_quantity > 0
                        else fill.at.to_pydatetime()
                    )
                    positions.append(
                        replace(
                            position,
                            quantity=after_quantity,
                            held_since=since,
                            share_basis=fill.order.share_basis,
                        )
                    )
            movement = -fill.quantity * fill.reference.price - fill.fee
            account = replace(
                self._account,
                cash=self.cash + movement,
                positions=tuple(positions),
                as_of=fill.at.to_pydatetime(),
            )
        self.ledger.record(
            fill.fill_id,
            fill.at,
            "FILL",
            {
                "symbol": fill.order.symbol,
                "quantity": fill.quantity,
                "price": fill.reference.price,
                "fee": fill.fee,
                "source_id": fill.reference.source_id,
                "observation_at": fill.reference.observation_at,
                "available_at": fill.reference.available_at,
                "scheduled_order_at": fill.order.at,
                "actual_fill_at": fill.at,
                "proxy_age_seconds": (fill.at - fill.reference.observation_at).total_seconds(),
                "kind": fill.reference.kind,
                "share_basis": fill.reference.share_basis,
                "source_version": fill.reference.source_version,
                "basis": "SYNTHETIC",
            },
            fill.order.order_id,
        )
        self.ledger.record(
            fill.fill_id + ":CASH",
            fill.at,
            "CASH",
            {"movement": movement, "cash_before": self.cash, "cash_after": account.cash},
            fill.fill_id,
        )
        self.ledger.record(
            fill.fill_id + ":POSITION",
            fill.at,
            "POSITION",
            {"symbol": fill.order.symbol, "before": before_quantity, "after": after_quantity},
            fill.fill_id,
        )
        self.ledger.record(
            fill.fill_id + ":FEE", fill.at, "FEE", {"amount": fill.fee}, fill.fill_id
        )
        self._account = account
        self._fills[fill.fill_id] = fill
        self._fill_boundaries.add(fill.at)
        with localcontext(ARITHMETIC):
            self._remaining[fill.order.order_id] = left - fill.quantity
            self.execution_fees += fill.fee

    def valuation(self, references: tuple[PriceReference, ...], at: pd.Timestamp) -> dict:
        self.permission.ensure()
        at = utc(at)
        if len({r.symbol for r in references}) != len(references):
            raise ValueError("DUPLICATE_MARK")
        marks, reasons = [], {}
        for row in references:
            if row.universe != self.universe:
                raise ValueError("MARK_UNIVERSE_MISMATCH")
            reason = row.reason_at(at)
            if row.share_basis != self.share_basis(row.symbol):
                reason = "MARK_SHARE_EPOCH_MISMATCH"
            reasons[row.symbol] = reason
            if reason == "REFERENCE_ELIGIBLE":
                assert row.available_at is not None
                marks.append(
                    ca.RawMark(
                        self._alias[row.symbol],
                        row.price,
                        row.observation_at.to_pydatetime(),
                        row.available_at.to_pydatetime(),
                        row.share_basis,
                        row.source_id,
                    )
                )
        with localcontext(ARITHMETIC):
            result = ca.snapshot(self._account, tuple(marks), at.to_pydatetime())
        result["missing_marks"] = [self._inverse[s] for s in result["missing_marks"]]
        result["unresolved_exits"] = [self._inverse[s] for s in result["unresolved_exits"]]
        for mark in result["marks"]:
            mark["symbol"] = self._inverse[mark["symbol"]]
        result["mark_reasons"] = reasons
        result["physical_balances"] = self.balances
        result["universe_id"] = self.universe.universe_id
        return result

    def action(self, instruction: ActionInstruction) -> bool:
        self.permission.ensure()
        if instruction.universe != self.universe:
            raise ValueError("ACTION_UNIVERSE_MISMATCH")
        if instruction.boundary in self._fill_boundaries:
            raise ValueError("UNAPPROVED_SAME_TIME_ACTION_FILL_ORDERING")
        primitive = action_primitive(instruction)
        with localcontext(ARITHMETIC):
            after = ca.apply_actions(self._account, (primitive,))
        if after == self._account:
            return False
        self.ledger.record(
            instruction.action_id,
            instruction.boundary,
            "ACTION",
            {
                "symbol": instruction.symbol,
                "kind": instruction.kind,
                "amount": instruction.amount,
                "known_at": instruction.known_at,
                "boundary": instruction.boundary,
                "before": self.balances,
                "after": tuple((self._inverse[x.symbol], x.quantity) for x in after.positions),
                "basis": "SYNTHETIC",
                "fractional_policy": instruction.fractional_policy,
            },
        )
        for position in after.positions:
            symbol = self._inverse[position.symbol]
            if position.quantity != self.quantity(symbol):
                self.ledger.record(
                    instruction.action_id + ":POSITION:" + symbol,
                    instruction.boundary,
                    "POSITION",
                    {
                        "symbol": symbol,
                        "before": self.quantity(symbol),
                        "after": position.quantity,
                        "share_basis": position.share_basis,
                    },
                    instruction.action_id,
                )
        self._account = after
        self._action_boundaries.add(instruction.boundary)
        if instruction.kind == "SPLIT" and instruction.post_split_basis:
            self._epochs[instruction.symbol] = instruction.post_split_basis
        return True

    def transform_virtual_split(
        self,
        quantities: tuple[tuple[str, Decimal], ...],
        entered_at: pd.Timestamp,
        instruction: ActionInstruction,
    ) -> tuple[tuple[str, Decimal], ...]:
        """Same tested split primitive; no virtual dividend or duplicate physical claims."""
        if instruction.kind != "SPLIT" or instruction.universe != self.universe:
            raise ValueError("MATCHED_VIRTUAL_SPLIT_REQUIRED")
        positions = tuple(
            ca.Position(
                self._alias[s],
                "SYN:VIRTUAL:" + s,
                q,
                entered_at.to_pydatetime(),
                instruction.share_basis,
            )
            for s, q in quantities
        )
        account = ca.Account(Decimal(0), positions, entered_at.to_pydatetime())
        with localcontext(ARITHMETIC):
            changed = ca.apply_action(account, action_primitive(instruction))
        return tuple(
            (self._inverse[position.symbol], position.quantity) for position in changed.positions
        )

    def retain_missing_exit(self, symbol: str, at: pd.Timestamp) -> None:
        self.permission.ensure()
        self.universe.check_symbol(symbol)
        self._account = ca.retain_missing_exit(
            self._account, self._alias[symbol], utc(at).to_pydatetime()
        )

    def settle(self, claim_id: str, at: pd.Timestamp) -> None:
        self.permission.ensure()
        before = self.cash
        with localcontext(ARITHMETIC):
            account = ca.settle_dividend(self._account, claim_id, utc(at).to_pydatetime())
        if account == self._account:
            return
        self.ledger.record(
            claim_id + ":SETTLE",
            at,
            "SETTLEMENT",
            {"claim_id": claim_id, "cash_before": before, "cash_after": account.cash},
        )
        with localcontext(ARITHMETIC):
            movement = account.cash - before
        self.ledger.record(
            claim_id + ":SETTLE:CASH",
            at,
            "CASH",
            {"movement": movement, "cash_before": before, "cash_after": account.cash},
            claim_id + ":SETTLE",
        )
        self._account = account

    @property
    def claims(self) -> tuple[dict, ...]:
        with localcontext(ARITHMETIC):
            return tuple(
                {
                    "claim_id": c.claim_id,
                    "symbol": self._inverse[c.symbol],
                    "amount": c.signed_amount,
                    "payable_date": c.payable_date,
                    "settled": c.settled,
                }
                for c in self._account.claims
            )

    def debit(self, amount: Decimal, at: pd.Timestamp, event_id: str, details: dict) -> None:
        self.permission.ensure()
        amount = ca.number(amount)
        from .config import fingerprint

        signature = (amount, utc(at), fingerprint(json_value(details)))
        if event_id in self._debits:
            if self._debits[event_id] != signature:
                raise ValueError("DIVERGENT_DUPLICATE_DEBIT")
            return
        if amount < 0 or utc(at) < self.as_of:
            raise ValueError("NONNEGATIVE_CAUSAL_DEBIT_REQUIRED")
        with localcontext(ARITHMETIC):
            cash_before = self.cash
            movement = -amount
            cash_after = cash_before + movement
        self.ledger.record(
            event_id,
            at,
            "BORROW",
            {
                **details,
                "amount": amount,
                "cash_before": self.cash,
                "cash_after": cash_after,
            },
        )
        self._account = replace(self._account, cash=cash_after, as_of=utc(at).to_pydatetime())
        self.ledger.record(
            event_id + ":CASH",
            at,
            "CASH",
            {"movement": movement, "cash_before": cash_before, "cash_after": cash_after},
            event_id,
        )
        self._debits[event_id] = signature

    def clear_resolved_exits(self) -> None:
        self.permission.ensure()
        unresolved = tuple(
            s for s in self._account.unresolved_exits if self.quantity(self._inverse[s]) != 0
        )
        self._account = replace(self._account, unresolved_exits=unresolved)
