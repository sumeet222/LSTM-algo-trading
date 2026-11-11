"""Dynamic exit annotations around the frozen physical and virtual ledger."""

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from math import isfinite, log

from ..rapid_v1.portfolio import FastAccount
from ..rapid_v2_diagnostics.book import ZERO, D, Ledger, add, price_bridge
from ..stage35.final_backtest_v4.book import EPS


def cap_causes(a: "DynamicLedger") -> tuple[str, ...]:
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
        ("NAME_CAP", max(names) > a.name_cap * nav + EPS),
        ("VINTAGE_CAP", max(vintage.values(), default=ZERO) > D(".2") * nav + EPS),
        ("RESTRICTED_CASH", a.cash < a.restricted()),
    )
    return tuple(label for label, breached in checks if breached)


@dataclass
class DynamicLedger(Ledger):
    name_cap: D = D(".10")
    groups: dict[str, dict] = field(default_factory=dict)
    group_of: dict[str, str] = field(default_factory=dict)
    cooling: dict[tuple[int, int], int] = field(default_factory=dict)
    order_exits: dict[tuple[str, str], dict] = field(default_factory=dict)
    closing: dict[str, dict] = field(default_factory=dict)
    exit_tape: list[dict] = field(default_factory=list)
    by_reason: dict[str, dict] = field(default_factory=dict)
    delayed: set[str] = field(default_factory=set)
    regime: str = ""

    def capacity(self, now: int) -> tuple[Decimal, Decimal, dict[int, Decimal], str]:
        nav = self.nav()
        if nav is None:
            return (
                ZERO,
                ZERO,
                {},
                "UNRESOLVED_EXECUTION" if self.nav_incomplete else "UNPRICED_SPECIAL",
            )
        names = {}
        for j, v in enumerate(self.abs_virtual):
            point = self.prices[j]
            if v and point is not None:
                names[j] = D(str(v)) * point
        names[20] = sum((abs(v) for v in self.special_values.values()), ZERO)
        gross = sum(names.values(), ZERO)
        stale = any(
            self.quantity[j] and (self.prices[j] is None or now - self.marks_at[j] > 5)
            for j in range(20)
        )
        pending_gross = sum(
            (abs(lot.pending) * (self.prices[lot.ticker] or ZERO) for lot in self.lots.values()),
            ZERO,
        )
        liabilities = sum((-v for v, _ in self.claims.values() if v < 0), ZERO)
        free = max(
            ZERO, min(self.cash - self.restricted() - pending_gross - liabilities, nav - gross)
        )
        vintage: dict[int, Decimal] = {}
        for lot in self.lots.values():
            p = self.prices[lot.ticker]
            if p is not None:
                vintage[lot.origin] = (
                    vintage.get(lot.origin, ZERO) + (abs(lot.quantity) + abs(lot.pending)) * p
                )
        for key, value in self.special_values.items():
            if key in self.lots:
                origin = self.lots[key].origin
                vintage[origin] = vintage.get(origin, ZERO) + abs(value)
        breach = (
            nav <= 0
            or gross > nav + EPS
            or any(v > self.name_cap * nav + EPS for v in names.values())
            or any(v > D(".2") * nav + EPS for v in vintage.values())
            or self.cash < self.restricted()
        )
        status = "RISK_BREACH" if breach else "STALE_MARK" if stale else "READY"
        return nav, free, names, status

    def record(self, kind: str, at: int, **fields) -> None:
        if kind == "ORDER":
            FastAccount.record(self, kind, at, **fields)
            ticker = fields["ticker"]
            order = self.pending[ticker]
            causes = (
                cap_causes(self)
                if any(r.role == "RISK_LIQUIDATION" for r in order.requests)
                else ()
            )
            self.order_notes[order.key] = self.prices[ticker], causes
            for r in order.requests:
                if r.role == "ENTRY":
                    continue
                state = self.groups[self.group_of[r.key]]
                if r.role == "RISK_LIQUIDATION":
                    if not causes:
                        raise ValueError("MISSING_RISK_CAP_CAUSE")
                    primary = (
                        "RISK_NAME_CAP"
                        if "NAME_CAP" in causes
                        else ("RISK_VINTAGE_CAP" if "VINTAGE_CAP" in causes else "RISK_OTHER_CAP")
                    )
                else:
                    primary = state["reason"]
                    if primary is None:
                        raise ValueError("UNLATCHED_DYNAMIC_EXIT")
                self.order_exits[order.key, r.key] = {
                    "primary": primary,
                    "triggers": tuple(dict.fromkeys((*causes, *state["triggers"]))),
                    "aligned_exit_strength": state.get("exit_score", state.get("last_aligned")),
                    "decision": at,
                    "entry_strength": state["strength"],
                    "lineage": state["lineage"],
                    "trail_level": state.get("trail_level"),
                    "group": self.group_of[r.key],
                }
            return
        if kind == "FILL" and fields["external"]:
            mark, _ = self.order_notes.get(str(fields["order"]), (None, ()))
            if mark is None:
                raise ValueError("EXTERNAL_SUBMISSION_MARK_MISSING")
            q, raw, fill = (D(str(fields[k])) for k in ("external", "reference", "external_price"))
            drift, _, _ = price_bridge(q, mark, raw, fill)
            add(self.totals, v3_signed_arrival=drift, v3_absolute_arrival=abs(drift))
        super().record(kind, at, **fields)
        if kind == "OBSERVED_MARKED_CAP_BREACH":
            self.causes.update("observed:" + c for c in cap_causes(self))
        if kind == "V5_PENDING_MISSING_BAR":
            self.delayed.add(str(fields["order"]))
        if kind == "FILL":
            self.record_exit_legs(at, fields)

    def record_exit_legs(self, at: int, fields: dict) -> None:
        order = str(fields["order"])
        raw = D(str(fields["reference"]))
        for leg in fields["legs"]:
            key = str(leg["lot"])
            context = self.order_exits.get((order, key))
            if context is None:
                if fields["roles"][key] != "ENTRY":
                    raise ValueError("EXIT_WITHOUT_SUBMISSION_PROVENANCE")
                state = self.groups[self.group_of[key]]
                state.setdefault("entry_raw", {}).setdefault(self.lots[key].ticker, float(raw))
                continue
            lot = self.lots[key]
            if lot.entry_at is None or fields["effective"] <= context["decision"]:
                raise ValueError("EXIT_WITHOUT_CAUSAL_ENTRY_OR_DECISION")
            q, fill = -D(str(leg["q"])), D(str(leg["price"]))
            if not q:
                continue
            prior = self.closing.get(key)
            primary = prior if prior and prior["primary"].startswith("RISK_") else context
            self.closing[key] = {
                **primary,
                "posted": at,
                "triggers": tuple(dict.fromkeys((*primary["triggers"], *context["triggers"]))),
            }
            gap = order in self.delayed
            if gap:
                self.stats.counts["EXIT_LEG_MISSING_SOURCE_DELAY"] += 1
            self.exit_tape.append(
                {
                    "case": self.arm,
                    "strategy_id": self.arm.split("_")[0],
                    "regime": self.regime,
                    "lot": key,
                    "ticker": lot.ticker,
                    "origin": lot.origin,
                    "entry": lot.entry_at,
                    "effective": fields["effective"],
                    "posted": at,
                    "decision": context["decision"],
                    "quantity": int(q),
                    "fill": float(fill),
                    "raw": float(raw),
                    "external": not leg["internal"],
                    "cause": context["primary"],
                    "triggers": "|".join(context["triggers"]),
                    "entry_strength": context["entry_strength"],
                    "exit_strength": context["aligned_exit_strength"],
                    "source_delay": gap,
                }
            )
            if (
                context["primary"] == "TRAILING_STOP"
                and len(self.groups[context["group"]]["tickers"]) == 1
                and context["trail_level"] is not None
            ):
                st = self.groups[context["group"]]
                adjusted = float(raw) * float(st.get("current_factor", 1.0))
                if adjusted > 0 and (1 if q > 0 else -1) * log(adjusted) < context["trail_level"]:
                    self.stats.counts["TRAILING_EXIT_BEYOND_STOP_THRESHOLD"] += 1

    def aggregate_trade(self, row: dict, date: str, rth_index) -> None:
        key = row["key"]
        super().aggregate_trade(row, date, rth_index)
        detail = self.closing.pop(key, None)
        group = self.group_of.pop(key, None)
        if group is not None and not any(k in self.group_of for k in self.groups[group]["keys"]):
            self.groups.pop(group)
        entry, end = row["entry_at"], row["exit_at"]
        if entry is None or end is None:
            return
        if detail is None:
            raise ValueError("CLOSED_LOT_WITHOUT_CAUSE")
        cause = detail["primary"]
        wall, age = end - entry, rth_index(end) - rth_index(entry)
        if age < 0:
            raise ValueError("NEGATIVE_HOLD_TIME")
        d = self.by_reason.setdefault(
            cause,
            {
                "totals": {},
                "wall": Counter(),
                "scheduled": Counter(),
                "triggers": Counter(),
            },
        )
        d["wall"][wall] += 1
        d["scheduled"][age] += 1
        d["triggers"].update(detail["triggers"])
        value = detail["aligned_exit_strength"]
        add(
            d["totals"],
            cohorts=1,
            gross_price=row["gross_signed_price_pnl"],
            action_value=row["gross_action_cash"],
            net=row["cash_pnl"],
            overnight=int(entry // 1440 != end // 1440),
            multi_day=int(age >= 390),
            entry_strength=D(str(detail["entry_strength"])),
            exit_strength=D(str(value)) if value is not None and isfinite(value) else ZERO,
            exit_strength_known=int(value is not None and isfinite(value)),
        )
        if cause.startswith("RISK_"):
            add(self.totals, risk_closed=1, risk_before_240=int(age < 240))
        else:
            add(self.totals, policy_closed=1, policy_before_240=int(age < 240))

    def finish_session(self, end: int, date: str, rth_index) -> None:
        super().finish_session(end, date, rth_index)
        orders = {o.key for o in self.pending.values()}
        self.order_exits = {k: v for k, v in self.order_exits.items() if k[0] in orders}
        self.delayed.intersection_update(orders)
        self.cooling = {k: at for k, at in self.cooling.items() if at >= end}
