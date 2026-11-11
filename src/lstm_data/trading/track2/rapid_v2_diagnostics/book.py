"""Aggregate V1 fills and virtual lots without replay journals."""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from ..rapid_v1.portfolio import FastAccount
from ..stage35.final_backtest_v4.book import EPS

D = Decimal
ZERO = D(0)
ET = ZoneInfo("America/New_York")


def price_bridge(q: D, mark: D, raw: D, fill: D) -> tuple[D, D, D]:
    """Positive signed values are adverse to the direction of the physical order."""
    drift, concession = q * (raw - mark), q * (fill - raw)
    total = q * (fill - mark)
    if concession < -EPS or abs(drift + concession - total) > EPS:
        raise ValueError("INVALID_EXECUTION_BRIDGE")
    return drift, concession, total


def cap_causes(a: FastAccount) -> tuple[str, ...]:
    nav = a.nav()
    if nav is None:
        return ("UNAVAILABLE_NAV",)
    names = [D(str(v)) * (a.prices[j] or ZERO) for j, v in enumerate(a.abs_virtual)] + [
        sum((abs(v) for v in a.special_values.values()), ZERO)
    ]
    vintage: dict[int, D] = {}
    for lot in a.lots.values():
        value = (abs(lot.quantity) + abs(lot.pending)) * (a.prices[lot.ticker] or ZERO)
        vintage[lot.origin] = vintage.get(lot.origin, ZERO) + value
        vintage[lot.origin] += abs(a.special_values.get(lot.key, ZERO))
    checks = (
        ("NONPOSITIVE_NAV", nav <= 0),
        ("GROSS_CAP", sum(names, ZERO) > nav + EPS),
        ("NAME_CAP", max(names) > D(".1") * nav + EPS),
        ("VINTAGE_CAP", max(vintage.values(), default=ZERO) > D(".2") * nav + EPS),
        ("RESTRICTED_CASH", a.cash < a.restricted()),
    )
    return tuple(label for label, breached in checks if breached)


def add(group: dict[str, D], **values: D | int) -> None:
    for key, value in values.items():
        group[key] = group.get(key, ZERO) + value


@dataclass
class Ledger(FastAccount):
    totals: dict[str, D] = field(default_factory=dict)
    breakdown: dict[str, dict[str, D]] = field(default_factory=dict)
    causes: Counter = field(default_factory=Counter)
    order_notes: dict[str, tuple[D | None, tuple[str, ...]]] = field(default_factory=dict)
    exit_notes: dict[str, tuple[str, tuple[str, ...]]] = field(default_factory=dict)
    any_forced: set[str] = field(default_factory=set)
    durations: Counter = field(default_factory=Counter)
    scheduled_durations: Counter = field(default_factory=Counter)
    partial_orders: dict[str, tuple[D, D, bool]] = field(default_factory=dict)
    ledger_examples: list[dict] = field(default_factory=list)

    def record(self, kind: str, at: int, **fields) -> None:
        super().record(kind, at, **fields)
        if kind == "ORDER":
            j = int(fields["ticker"])
            order = self.pending[j]
            forced = any(r.role == "RISK_LIQUIDATION" for r in order.requests)
            causes = cap_causes(self) if forced else ()
            if forced and not causes:
                raise ValueError("MISSING_EXACT_FORCED_EXIT_CAUSE")
            self.order_notes[order.key] = self.prices[j], causes
        elif kind == "SPLIT":
            for order in self.pending.values():
                if order.ticker == fields["ticker"] and order.key in self.order_notes:
                    mark, causes = self.order_notes[order.key]
                    self.order_notes[order.key] = (
                        mark / fields["ratio"] if mark is not None else None,
                        causes,
                    )
        elif kind == "FILL":
            self.audit_fill(at, fields)
        elif kind in ("DIVIDEND_EX", "DIVIDEND_PAY", "MRK_OGN_ENTITLEMENT", "SPLIT"):
            # SPLIT is recorded by the frozen event counter above.
            if len(self.ledger_examples) < 8:
                self.ledger_examples.append({"kind": kind, "at": at, **fields})

    def audit_fill(self, at: int, fields: dict) -> None:
        key = str(fields["order"])
        mark, causes = self.order_notes.get(key, (None, ()))
        q, raw, fill = (D(str(fields[k])) for k in ("external", "reference", "external_price"))
        roles = fields["roles"]
        forced_abs = ZERO
        for leg in fields["legs"]:
            lot = leg["lot"]
            role = roles[lot]
            if role in ("EXIT", "RISK_LIQUIDATION"):
                self.exit_notes[lot] = role, causes if role == "RISK_LIQUIDATION" else ()
            if role == "RISK_LIQUIDATION":
                self.any_forced.add(lot)
                if not leg["internal"]:
                    forced_abs += abs(D(str(leg["q"])))
        if not q:
            if fields["fee"] or forced_abs:
                raise ValueError("EXTERNAL_COST_ON_INTERNAL_ONLY")
            return
        prior_shares, prior_notional, prior_forced = self.partial_orders.pop(
            key, (ZERO, ZERO, False)
        )
        notional = abs(q) * fill
        if forced_abs > abs(q):
            raise ValueError("FORCED_EXTERNAL_ALLOCATION")
        row = self.stats.physical_rows[-1]
        if fields["effective"] <= fields["decision"] or at < fields["effective"] + 3:
            raise ValueError("FILLED_OUTSIDE_CAUSAL_FRONTIER")
        add(
            self.totals,
            external_fills=1,
            turnover=notional,
            raw_turnover=abs(q) * raw,
            forced_attributed_notional=forced_abs * fill,
            forced_external_fill_notional=notional if forced_abs else ZERO,
        )
        if self.arm.endswith("_H100"):
            if mark is None:
                raise ValueError("BASELINE_SUBMISSION_MARK_UNAVAILABLE")
            drift, concession, _ = price_bridge(q, mark, raw, fill)
            if abs(concession - row["print_slippage"] - row["impact"]) > EPS:
                raise ValueError("PRICE_CONCESSION_COMPONENT_MISMATCH")
            stamp = datetime.fromtimestamp(int(fields["effective"]) * 60, ET)
            ticker, window = fields["ticker"], f"{stamp.hour:02}:{(stamp.minute // 30) * 30:02}"
            group = self.breakdown.setdefault(f"friction|{ticker}|{window}", {})
            values = {
                "orders": 1,
                "notional": notional,
                "signed_arrival_drift": drift,
                "absolute_arrival_drift": abs(drift),
                "positive_drift": max(drift, ZERO),
                "negative_drift": min(drift, ZERO),
                "adverse": int(drift > 0),
                "favorable": int(drift < 0),
                "flat": int(drift == 0),
                "spread": row["print_slippage"],
                "impact": row["impact"],
                "commission": row["commission"],
            }
            add(group, **values)
            add(
                self.totals,
                arrival_covered_fills=1,
                **{
                    name: value
                    for name, value in values.items()
                    if name not in ("orders", "notional", "spread", "impact", "commission")
                },
            )
        forced = prior_forced or bool(forced_abs)
        if fields["order_status"] == "PARTIALLY_FILLED":
            self.partial_orders[key] = prior_shares + abs(q), prior_notional + notional, forced
        else:
            add(self.totals, physical_orders=1, forced_external_orders=int(forced))
            self.order_notes.pop(key, None)

    def aggregate_trade(self, row: dict, date: str, rth_index) -> None:
        key = row["key"]
        role, causes = self.exit_notes.pop(key, ("OPEN", ()))
        forced_any = key in self.any_forced
        self.any_forced.discard(key)
        if row["entry_at"] is None:
            return
        entry, exit_at = row["entry_at"], row["exit_at"]
        early = exit_at is not None and exit_at < row["endpoint"]
        if early and not forced_any:
            raise ValueError("EARLY_EXIT_WITHOUT_RISK_ORDER")
        stamp = datetime.fromtimestamp(int(row["origin"]) * 60, ET)
        gross = row["gross_signed_price_pnl"]
        amounts = {
            "cohorts": 1,
            "completed": int(exit_at is not None),
            "early": int(early),
            "scheduled": int(role == "EXIT"),
            "risk_final": int(role == "RISK_LIQUIDATION"),
            "any_forced": int(forced_any),
            "gross_price": gross,
            "gross_winners": max(gross, ZERO),
            "gross_losers": min(gross, ZERO),
            "actions": row["gross_action_cash"],
            "net": row["cash_pnl"],
            "cohort_cost": row["cost"],
            "cohort_borrow": row["borrow"],
        }
        add(self.totals, **amounts)
        if exit_at is not None:
            self.durations[int(exit_at) - int(entry)] += 1
            self.scheduled_durations[rth_index(int(exit_at)) - rth_index(int(entry))] += 1
        for c in causes:
            self.causes[("early:" if early else "scheduled_or_late:") + c] += 1
        for group in (
            f"entry_year|{stamp.year}",
            f"attribution_year|{date[:4]}",
            f"side|{row['direction']}",
            f"ticker|{row['ticker']}",
            f"slot|{stamp:%H:%M}",
            f"overnight|{bool(exit_at is not None and entry // 1440 != exit_at // 1440)}",
        ):
            add(self.breakdown.setdefault(group, {}), **amounts)

    def finish_session(self, end: int, date: str, rth_index) -> None:
        self.compact(end)
        for row in self.stats.trade_rows:
            self.aggregate_trade(row, date, rth_index)
        self.stats.trade_rows.clear()
        for row in self.stats.physical_rows:
            if row["ticker"] == 20:  # Frozen special distribution execution convention.
                add(
                    self.totals,
                    physical_orders=1,
                    external_fills=1,
                    turnover=abs(row["shares"]) * row["external_price"],
                    raw_turnover=abs(row["shares"]) * row["raw_open"],
                )
        self.stats.physical_rows.clear()
        pending = {o.key for o in self.pending.values()}
        for key, (_, _, forced) in list(self.partial_orders.items()):
            if key not in pending:
                add(self.totals, physical_orders=1, forced_external_orders=int(forced))
                del self.partial_orders[key]
        self.order_notes = {k: v for k, v in self.order_notes.items() if k in pending}
        self.cost_references = {k: v for k, v in self.cost_references.items() if k in pending}
