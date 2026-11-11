"""Claim/share consistency kernel; no trade prices, cost basis, NAV or P&L.

Synthetic endowed quantities may exercise actual historical action facts in this
isolated witness. This is not the funded V2 trading book and cannot place orders.
The same entitlement/settlement deltas are consumable by a released book adapter.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal

from ...stage012.contracts import utc
from .actions import Action, Truth

D = Decimal
ZERO = D(0)


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


@dataclass(frozen=True)
class ShareLot:
    lot_id: str
    symbol: str
    shares: Decimal
    pending_unsubmitted: Decimal = ZERO


@dataclass(frozen=True)
class Claim:
    event_id: str
    lot_id: str
    symbol: str
    signed_amount: Decimal
    due_at: datetime | None
    truth: str
    asset: str = "USD"
    source_hash: str = ""
    assumption_rule_id: str = ""


@dataclass(frozen=True)
class Receipt:
    event_id: str
    effective_at: datetime
    available_at: datetime
    posted_at: datetime
    kind: str
    payload_hash: str
    before: str
    after: str
    truth: str
    source_hash: str
    assumption_rule_id: str


@dataclass(frozen=True)
class ClaimShareBook:
    """No funded capital or trade simulation. All initial shares are test endowments."""

    lots: tuple[ShareLot, ...]
    claims: tuple[Claim, ...] = ()
    settled: tuple[Claim, ...] = ()
    cash_distribution_only: Decimal = ZERO
    carry_expense_only: Decimal = ZERO
    unresolved: tuple[str, ...] = ()
    journal: tuple[Receipt, ...] = ()
    carry_frontiers: tuple[tuple[str, datetime], ...] = ()
    carry_allocations: tuple[tuple[str, Decimal], ...] = ()

    def state_hash(self) -> str:
        return sha({k: v for k, v in asdict(self).items() if k != "journal"})

    def physical_shares(self, symbol: str) -> Decimal:
        return sum((lot.shares for lot in self.lots if lot.symbol == symbol), ZERO)

    def reconcile(self) -> None:
        if len({lot.lot_id for lot in self.lots}) != len(self.lots):
            raise ValueError("DUPLICATE_TEST_LOT")
        if self.cash_distribution_only != sum(
            (c.signed_amount for c in self.settled if c.asset == "USD"), ZERO
        ):
            raise AssertionError("CLAIM_CASH_CONSERVATION")
        if len({(c.event_id, c.lot_id) for c in self.claims + self.settled}) != len(
            self.claims + self.settled
        ):
            raise AssertionError("DUPLICATE_ENTITLEMENT")
        if self.carry_expense_only != sum((v for _, v in self.carry_allocations), ZERO):
            raise AssertionError("PHYSICAL_CARRY_ATTRIBUTION")
        if not all(lot.shares.is_finite() for lot in self.lots):
            raise ValueError("FINITE_SHARES_REQUIRED")

    def commit(
        self,
        new: "ClaimShareBook",
        event_id: str,
        kind: str,
        effective: datetime,
        available: datetime,
        posted: datetime,
        payload: object,
        truth: str,
        source_hash: str,
        rule: str = "",
    ) -> "ClaimShareBook":
        if not utc(effective) <= utc(available) <= utc(posted):
            raise ValueError("EVENT_RECEIPT_INVERSION")
        value_hash = sha(payload)
        prior = next((r for r in self.journal if r.event_id == event_id), None)
        if prior is not None:
            if prior.payload_hash != value_hash:
                raise ValueError("CORRECTED_EVENT_REQUIRES_REPLAY_NOT_SILENT_REWRITE")
            return self
        if self.journal and posted < self.journal[-1].posted_at:
            raise ValueError("CHRONOLOGICAL_REPLAY_REQUIRED")
        new.reconcile()
        receipt = Receipt(
            event_id,
            effective,
            available,
            posted,
            kind,
            value_hash,
            self.state_hash(),
            new.state_hash(),
            truth,
            source_hash,
            rule,
        )
        return replace(new, journal=self.journal + (receipt,))

    def apply(
        self,
        event: Action,
        effective: datetime,
        available: datetime,
        posted: datetime,
        *,
        modeled_retrospective: bool,
        due_at: datetime | None = None,
    ) -> "ClaimShareBook":
        event.validate()
        if not modeled_retrospective:
            raise PermissionError("PIT_ACTION_RECEIPT_NOT_CERTIFIED")
        if event.economic_basis != "RAW_COMMON_SHARE":
            raise ValueError("RAW_SHARE_ACTION_REQUIRED")
        rule = event.assumption_rule_id + ";RETROSPECTIVE_DATE_ONLY_EVENT_AVAILABILITY"
        source = sha(event.record())
        key = event.event_id + ":EFFECTIVE"
        prior = next((j for j in self.journal if j.event_id == key), None)
        if prior is not None:
            if prior.source_hash != source:
                raise ValueError("CORRECTED_EVENT_REQUIRES_REPLAY_NOT_SILENT_REWRITE")
            return self
        if event.status in (Truth.CONFLICTED_HOLD, Truth.UNKNOWN):
            new = replace(self, unresolved=self.unresolved + (event.event_id,))
        elif event.action_type == "CASH_DIVIDEND":
            if event.amount is None:
                raise ValueError("DIVIDEND_AMOUNT_UNRESOLVED")
            if event.special:
                raise ValueError("SPECIAL_CANNOT_USE_ORDINARY_RULE")
            claims = tuple(
                Claim(
                    event.event_id,
                    lot.lot_id,
                    event.symbol,
                    lot.shares * event.amount,
                    due_at,
                    event.status.value,
                    source_hash=source,
                    assumption_rule_id=rule,
                )
                for lot in self.lots
                if lot.symbol == event.symbol and lot.shares
            )
            new = replace(
                self,
                claims=self.claims + claims,
                unresolved=self.unresolved
                + ((event.event_id + ":PAY_UNKNOWN",) if due_at is None else ()),
            )
        elif event.action_type == "SPLIT":
            ratio = event.split_ratio_new_old
            if ratio is None or not ratio.is_finite() or ratio <= 0:
                raise ValueError("SPLIT_RATIO_UNRESOLVED")
            lots = tuple(
                replace(
                    lot,
                    shares=lot.shares * ratio,
                    pending_unsubmitted=(lot.pending_unsubmitted * ratio).to_integral_value(
                        rounding="ROUND_DOWN"
                    ),
                )
                if lot.symbol == event.symbol
                else lot
                for lot in self.lots
            )
            total = sum((lot.shares for lot in lots if lot.symbol == event.symbol), ZERO)
            new = replace(
                self,
                lots=lots,
                unresolved=self.unresolved
                + (
                    (event.event_id + ":FRACTIONAL_CIL_UNPRICED",)
                    if total != total.to_integral_value(rounding="ROUND_DOWN")
                    else ()
                ),
            )
        elif event.action_type == "SPINOFF":
            if event.sub_type != "OGN_PER_MRK_0.1":
                raise ValueError("SPECIAL_TERMS_NOT_IMPLEMENTED_HOLD")
            claims = tuple(
                Claim(
                    event.event_id,
                    lot.lot_id,
                    event.symbol,
                    lot.shares / D(10),
                    None,
                    event.status.value,
                    "OGN_UNPRICED",
                    source,
                    rule,
                )
                for lot in self.lots
                if lot.symbol == event.symbol and lot.shares
            )
            new = replace(
                self,
                claims=self.claims + claims,
                unresolved=self.unresolved + (event.event_id + ":OGN_VALUE_CIL_UNKNOWN",),
            )
        elif event.effect_on_books.startswith("NO_"):
            new = self
        else:
            new = replace(self, unresolved=self.unresolved + (event.event_id + ":SPECIAL_HOLD",))
        return self.commit(
            new,
            key,
            event.action_type,
            effective,
            available,
            posted,
            event.record(),
            event.status.value,
            source,
            rule,
        )

    def pay(
        self, action_id: str, effective: datetime, available: datetime, posted: datetime
    ) -> "ClaimShareBook":
        key = action_id + ":PAY"
        if any(r.event_id == key for r in self.journal):
            return self
        claims = tuple(c for c in self.claims if c.event_id == action_id and c.asset == "USD")
        if not claims or any(c.due_at is None or c.due_at > effective for c in claims):
            raise ValueError("PAY_NOT_DUE_OR_UNDATED")
        new = replace(
            self,
            claims=tuple(c for c in self.claims if c not in claims),
            settled=self.settled + claims,
            cash_distribution_only=self.cash_distribution_only
            + sum((c.signed_amount for c in claims), ZERO),
        )
        return self.commit(
            new,
            key,
            "CASH_SETTLEMENT",
            effective,
            available,
            posted,
            claims,
            ";".join(sorted({c.truth for c in claims})),
            sha([c.source_hash for c in claims]),
            ";".join(sorted({c.assumption_rule_id for c in claims})),
        )

    def carry(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        known_raw_mark: Decimal | None,
        mark_available: datetime,
        posted: datetime,
        rate: Decimal | None,
        source_hash: str,
    ) -> "ClaimShareBook":
        event_key = f"CARRY:{symbol}:{start}:{end}"
        payload = (symbol, start, end, known_raw_mark, rate)
        prior = next((j for j in self.journal if j.event_id == event_key), None)
        if prior is not None:
            if prior.payload_hash != sha(payload) or prior.source_hash != source_hash:
                raise ValueError("CORRECTED_CARRY_REPLAY_REQUIRED")
            return self
        frontier = dict(self.carry_frontiers).get(symbol)
        if frontier is not None and start != frontier:
            raise ValueError("CARRY_OVERLAP_OR_MISSING_SEGMENT")
        if end < start or utc(mark_available) > utc(start):
            raise ValueError("CARRY_ASOF_MARK_FRONTIER")
        q = self.physical_shares(symbol)
        valid = (
            rate is not None
            and rate.is_finite()
            and rate >= 0
            and known_raw_mark is not None
            and known_raw_mark.is_finite()
            and known_raw_mark > 0
        )
        if not valid:
            new = replace(self, unresolved=self.unresolved + (f"CARRY_PENDING:{symbol}:{end}",))
        else:
            if rate is None or known_raw_mark is None:
                raise AssertionError("CARRY_VALIDATION")
            seconds = D(str((end - start).total_seconds()))
            amount = max(ZERO, -q) * known_raw_mark * rate * seconds / D(365 * 86400)
            shorts = sorted(
                (lot for lot in self.lots if lot.symbol == symbol and lot.shares < 0),
                key=lambda lot: lot.lot_id,
            )
            gross = sum((-lot.shares for lot in shorts), ZERO)
            allocated = []
            left = amount
            for n, lot in enumerate(shorts):
                share = left if n == len(shorts) - 1 else amount * (-lot.shares) / gross
                allocated.append((event_key + ":" + lot.lot_id, share))
                left -= share
            frontiers = dict(self.carry_frontiers)
            frontiers[symbol] = end
            new = replace(
                self,
                carry_expense_only=self.carry_expense_only + amount,
                carry_allocations=self.carry_allocations + tuple(allocated),
                carry_frontiers=tuple(sorted(frontiers.items())),
            )
        return self.commit(
            new,
            f"CARRY:{symbol}:{start}:{end}",
            "PHYSICAL_NET_SHORT_CARRY",
            end,
            end,
            posted,
            payload,
            "CONDITIONAL_ACADEMIC_SHORT",
            source_hash,
            f"ACT365_SCENARIO_RATE:{rate}",
        )


def verify_journal(book: ClaimShareBook) -> None:
    book.reconcile()
    for before, after in zip(book.journal, book.journal[1:]):
        if before.after != after.before:
            raise AssertionError("ADJACENT_JOURNAL_CHAIN")
    if book.journal and book.journal[-1].after != book.state_hash():
        raise AssertionError("TERMINAL_STATE_HASH")


def after_bar(start: datetime, delay_minutes: int = 2) -> tuple[datetime, datetime]:
    if delay_minutes not in (1, 2, 5):
        raise ValueError("UNREVIEWED_RECEIPT_SCENARIO")
    complete = start + timedelta(minutes=1)
    return complete, complete + timedelta(minutes=delay_minutes)
