"""V5 exact accountant without its journal; isolated mode-specific pricing hook.

The inherited atomic transaction, crossing, inventory and conservation machinery
is unchanged. Only _fill_candidate's price/fee prelude is extracted to permit
micro fractional-cent commission and incremental-print friction. Its original
source hash and exact extraction delta are recorded in the audit receipt.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import ROUND_DOWN, Decimal

from ..stage35.accounting import inventory
from ..stage35.final_backtest_v4.book import Lot, Order, Request, integer_cross
from ..stage35.final_backtest_v5.book import Account as FrozenAccount
from .costs import CostReference

D = Decimal
ZERO = D(0)


@dataclass
class CompactStats:
    counts: Counter = field(default_factory=Counter)
    physical_rows: list[dict] = field(default_factory=list)
    trade_rows: list[dict] = field(default_factory=list)
    anomalies: list[dict] = field(default_factory=list)
    anomaly_kinds: Counter = field(default_factory=Counter)
    lot_regular_cost: dict[str, Decimal] = field(default_factory=dict)
    lot_entry_notional: dict[str, Decimal] = field(default_factory=dict)
    lot_lineage: dict[str, str] = field(default_factory=dict)
    lot_decision: dict[str, int] = field(default_factory=dict)
    lot_order_links: dict[str, list[str]] = field(default_factory=dict)
    spread: Decimal = ZERO
    impact: Decimal = ZERO


@dataclass
class FastAccount(FrozenAccount):
    stats: CompactStats = field(default_factory=CompactStats)
    cost_references: dict[str, CostReference] = field(default_factory=dict)
    source_pointer: str = ""
    decision_frontier: dict = field(default_factory=dict)

    def reject(self, reason: str, count: int = 1) -> None:
        super().reject(reason, count)
        if len(self.stats.anomalies) < 100 and self.stats.anomaly_kinds["REJECT:" + reason] < 3:
            self.stats.anomaly_kinds["REJECT:" + reason] += 1
            self.stats.anomalies.append(
                {
                    "kind": "REJECT",
                    "reason": reason,
                    "count": count,
                    "source": self.source_pointer,
                    **self.decision_frontier,
                }
            )

    def record(self, kind: str, at: int, **fields) -> None:
        self.stats.counts[kind] += 1
        if kind == "FILL":
            q = D(str(fields["external"]))
            ref = D(str(fields["reference"]))
            fee = D(str(fields["fee"]))
            price = D(str(fields["external_price"]))
            h = D(str(fields.get("cost_h", ".0005")))
            j = D(str(fields.get("cost_j", ".0005")))
            friction = abs(q) * abs(price - ref)
            spread = friction * h / (h + j) if h + j else ZERO
            self.stats.spread += spread
            self.stats.impact += friction - spread
            for leg in fields["legs"]:
                key = str(leg["lot"])
                if fields.get("roles", {}).get(key) == "ENTRY":
                    self.stats.lot_entry_notional[key] = (
                        self.stats.lot_entry_notional.get(key, ZERO) + abs(D(str(leg["q"]))) * ref
                    )
                self.stats.lot_order_links.setdefault(key, []).append(str(fields["order"]))
                if not leg["internal"]:
                    value = D(str(leg["fee"])) + abs(D(str(leg["q"]))) * abs(
                        D(str(leg["price"])) - ref
                    )
                    key = str(leg["lot"])
                    self.stats.lot_regular_cost[key] = (
                        self.stats.lot_regular_cost.get(key, ZERO) + value
                    )
            if q:
                self.stats.physical_rows.append(
                    {
                        "strategy_id": self.arm,
                        "order_id": fields["order"],
                        "ticker": fields["ticker"],
                        "decision": fields["decision"],
                        "effective": fields["effective"],
                        "posted": at,
                        "shares": q,
                        "raw_open": ref,
                        "external_price": price,
                        "commission": fee,
                        "print_slippage": spread,
                        "impact": friction - spread,
                        "h": h,
                        "j": j,
                        "cumulative_fee": fields["order_cumulative_fee"],
                        "status": fields["order_status"],
                        "source": self.source_pointer,
                        "volatility_ratio": self.cost_references[
                            str(fields["order"])
                        ].volatility_ratio,
                        "ADV20_raw_shares": self.cost_references[
                            str(fields["order"])
                        ].adv20_raw_shares,
                    }
                )
                self.stats.counts["EXTERNAL_PHYSICAL_FILLS"] += 1
            else:
                self.stats.counts["INTERNAL_ONLY_SETTLEMENTS"] += 1
        if kind == "OGN_EXTERNAL_DISPOSAL":
            q = D(str(fields["external_delta"]))
            fee = D(str(fields["fee"]))
            raw = D(str(fields["raw_reference"]))
            cash = D(str(fields["external_cash"]))
            friction = -q * raw - cash - fee
            self.stats.spread += friction / 2
            self.stats.impact += friction / 2
            if q:
                self.stats.physical_rows.append(
                    {
                        "strategy_id": self.arm,
                        "order_id": "OGN:" + str(fields["decision"]),
                        "ticker": 20,
                        "decision": fields["decision"],
                        "effective": fields["effective"],
                        "posted": at,
                        "shares": q,
                        "raw_open": raw,
                        "external_price": -(cash + fee) / q,
                        "commission": fee,
                        "print_slippage": friction / 2,
                        "impact": friction / 2,
                        "status": "SPECIAL_OBSERVED",
                        "source": "SEALED_OGN_SIP;CONDITIONAL_DISTRIBUTION_POLICY",
                    }
                )
                self.stats.counts["EXTERNAL_PHYSICAL_FILLS"] += 1
        if (
            any(token in kind for token in ("MISSING", "EXPIRE", "BREACH", "OGN", "SPLIT"))
            and len(self.stats.anomalies) < 100
            and self.stats.anomaly_kinds[kind] < 3
        ):
            self.stats.anomaly_kinds[kind] += 1
            self.stats.anomalies.append(
                {"kind": kind, "at": at, "source": self.source_pointer, **fields}
            )

    def compact(self, at: int) -> None:
        if self.unpriced_special:
            return  # An unpriced distribution still owns its originating cohort.
        before = {
            key: (lot.nontrade, lot.cost, self.stats.lot_regular_cost.get(key, ZERO))
            for key, lot in self.lots.items()
        }
        super().compact(at)
        for row in self.closed:
            nontrade, total_cost, regular = before[row["key"]]
            row["regular_trading_cost"] = regular
            row["gross_signed_price_pnl"] = row["cash_pnl"] - nontrade + regular
            row["gross_action_cash"] = (
                nontrade + row["borrow"] + row["funding"] + total_cost - regular
            )
            row["entry_notional_raw_USD"] = self.stats.lot_entry_notional.pop(row["key"], ZERO)
            row["source"] = self.source_pointer
            row["intent_lineage"] = self.stats.lot_lineage.pop(row["key"], "")
            row["decision"] = self.stats.lot_decision.pop(row["key"], None)
            row["physical_or_internal_order_links"] = self.stats.lot_order_links.pop(row["key"], [])
            self.stats.trade_rows.append(row)
            self.stats.lot_regular_cost.pop(row["key"], None)
        self.closed.clear()

    def _fill_candidate(
        self, order: Order, raw_open: Decimal, now: int, effective: int, fraction: Decimal = D(1)
    ) -> None:
        if not raw_open.is_finite() or raw_open <= 0:
            raise ValueError("INVALID_EXECUTION_PRICE")
        if order.prior_volume_available > order.decision or now < effective + 1 + self.scenario.lag:
            raise ValueError("FILL_BEFORE_SOURCE_RECEIPT_OR_FUTURE_VOLUME")
        if not order.decision < effective or not ZERO <= fraction <= 1:
            raise ValueError("FILL_ORDER_CLOCK_OR_PARTIAL")
        if order.expiry is not None and effective > order.expiry:
            raise ValueError("LATE_ENTRY_EXECUTION")
        q = (abs(order.submitted_quantity) * fraction).to_integral_value(rounding=ROUND_DOWN) * (
            1 if order.submitted_quantity > 0 else -1
        )
        if not order.submitted_quantity:
            q = ZERO
        reference = self.cost_references.get(order.key)
        if reference is None:
            raise ValueError("MISSING_FROZEN_COST_REFERENCE")
        external, fee, paid, h, jrate = reference.quote(
            raw_open, q, order.cumulative_quantity, order.paid_fee, order.decision
        )
        legs = integer_cross(order.requests, raw_open, external, q, fee)
        roles = {r.key: r.role for r in order.requests}
        for leg in legs:
            lot = self.lots[leg.cohort_id]
            if roles[lot.key] == "ENTRY":
                if leg.quantity * lot.pending <= 0 or abs(leg.quantity) > abs(lot.pending):
                    raise ValueError("ENTRY_OVERFILL")
            elif leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity):
                raise ValueError("EXIT_OVERFILL")
            if roles[lot.key] == "EXIT" and effective < lot.endpoint:
                raise ValueError("FIXED_ENDPOINT_VIOLATION")
        for leg in legs:
            lot = self.lots[leg.cohort_id]
            if roles[lot.key] == "ENTRY":
                if leg.quantity * lot.pending <= 0 or abs(leg.quantity) > abs(lot.pending):
                    raise ValueError("ENTRY_OVERFILL")
                lot.pending -= leg.quantity
                if lot.entry_at is None:
                    lot.entry_at = effective
                    lot.entry_price = leg.price
                else:
                    old_price = lot.entry_price
                    if old_price is None:
                        raise AssertionError("MISSING_ENTRY_BASIS")
                    lot.entry_price = (
                        abs(lot.quantity) * old_price + abs(leg.quantity) * leg.price
                    ) / (abs(lot.quantity) + abs(leg.quantity))
            else:
                if leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity):
                    raise ValueError("EXIT_OVERFILL")
                if roles[lot.key] == "EXIT" and effective < lot.endpoint:
                    raise ValueError("FIXED_ENDPOINT_VIOLATION")
                lot.exit_at = effective
                lot.exit_price = leg.price
            qty, basis, real = inventory(lot.quantity, lot.basis, leg.quantity, leg.price)
            lot.quantity = qty
            lot.basis = basis
            lot.realized += real - leg.fee
            lot.cash -= leg.quantity * leg.price + leg.fee
            lot.fees += leg.fee
            if not leg.internal:
                lot.cost += abs(leg.quantity) * abs(leg.price - raw_open) + leg.fee
        j = order.ticker
        qty, basis, real = inventory(D(int(self.quantity[j])), self.physical_basis[j], q, external)
        if qty != qty.to_integral_value():
            raise AssertionError("PHYSICAL_FRACTIONAL_ORDINARY_STOCK")
        self.quantity[j] = int(qty)
        self.physical_basis[j] = basis
        self.physical_realized[j] += real - fee
        self.cash -= q * external + fee
        self.commission += fee
        self.friction += abs(q) * abs(external - raw_open)
        order.paid_fee = paid
        order.cumulative_quantity += abs(q)
        filled = {r.key: ZERO for r in order.requests}
        for leg in legs:
            filled[leg.cohort_id] += leg.quantity
        order.requests = tuple(
            Request(r.key, r.delta - filled[r.key], r.role)
            for r in order.requests
            if r.delta - filled[r.key]
        )
        order.submitted_quantity -= q
        order.status = "PARTIALLY_FILLED" if order.submitted_quantity else "OBSERVED"
        self.refresh()
        self.reconcile()
        self.record(
            "FILL",
            now,
            order=order.key,
            ticker=j,
            decision=order.decision,
            decision_at_utc=(
                datetime.fromtimestamp(order.decision * 60, timezone.utc)
                + timedelta(microseconds=1)
            ).isoformat(),
            submitted_at_utc=(
                datetime.fromtimestamp(order.decision * 60, timezone.utc)
                + timedelta(microseconds=1)
            ).isoformat(),
            effective_fill_at_utc=datetime.fromtimestamp(effective * 60, timezone.utc).isoformat(),
            observed_bar_complete_at_utc=datetime.fromtimestamp(
                (effective + 1) * 60, timezone.utc
            ).isoformat(),
            bar_available_at_utc=datetime.fromtimestamp(
                (effective + 1 + self.scenario.lag) * 60, timezone.utc
            ).isoformat(),
            effective=effective,
            reference=raw_open,
            roles=roles,
            cost_h=h,
            cost_j=jrate,
            external=q,
            external_price=external,
            fee=fee,
            order_status=order.status,
            order_cumulative_quantity=order.cumulative_quantity,
            order_cumulative_fee=order.paid_fee,
            legs=[
                {
                    "lot": item.cohort_id,
                    "q": item.quantity,
                    "price": item.price,
                    "fee": item.fee,
                    "internal": item.internal,
                }
                for item in legs
            ],
        )


__all__ = ["FastAccount", "CompactStats", "Lot", "Order", "Request"]
