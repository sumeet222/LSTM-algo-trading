"""As-of source replay. Source/authorization admission belongs to release.run().

Future rows may reside in a projected source frame, but only the current receipt
row is presented to decisions. Orders carry fixed pre-event quantities/volume.
"""

import gzip
import json
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from decimal import ROUND_DOWN, Decimal
from pathlib import Path
from typing import TextIO

import numpy as np
import pandas as pd

from ...stage012.model_registry import SYMBOLS
from ..completion_v3.tapes import load_actions, midnight
from .book import Account, Lot, Order, Request
from .execution_calendar import ExecutionCalendar
from .market import Day, Market, minute, stamp
from .paths import canonical, publish
from .protocol import ARMS, Scenario, valid_multiplier
from .special import EX, Distribution, OGNQuote, distribution, observe, pay_cil, settle_whole

D = Decimal
ZERO = D(0)
YEAR = D(365 * 86400)


def utc(value: int) -> datetime:
    return datetime.fromtimestamp(value * 60, tz=timezone.utc)


class Store:
    def __init__(self, path: Path, resume: bool = False):
        if path.exists() and not resume:
            raise ValueError("APPEND_ONLY_RUN_OUTPUT")
        path.mkdir(parents=True, exist_ok=resume)
        self.resume = resume
        self.path = path
        self.streams: dict[tuple[str, str], TextIO] = {}

    def write(self, scenario: str, kind: str, rows: list[dict]) -> None:
        if not rows:
            return
        key = (scenario, kind)
        if key not in self.streams:
            folder = self.path / scenario
            folder.mkdir(exist_ok=True)
            self.streams[key] = gzip.open(
                folder / (kind + ".jsonl.gz"), "at" if self.resume else "wt", compresslevel=1
            )
        stream = self.streams[key]
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    def close(self) -> None:
        for stream in self.streams.values():
            stream.close()


class Driver:
    def __init__(
        self,
        scenario_list: tuple[Scenario, ...],
        first: str,
        last: str,
        output: Path,
        diagnostic: bool = False,
        admission: object = None,
    ):
        from .release import check_admission

        check_admission(admission, first, last, diagnostic)
        if admission is not None:
            from .paths import ROOT

            frozen = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL.json").read_text())
            allowed = {canonical(row) for row in frozen["scenarios"]}
            if any(canonical(asdict(s)) not in allowed for s in scenario_list):
                raise PermissionError("UNAUTHORIZED_SCENARIO")
        self.admission = admission
        self.market = Market(first, last)
        self.execution_calendar = ExecutionCalendar(self.market.clock)
        self.scenarios = scenario_list
        self.accounts = [
            Account(arm, pop, s)
            for s in scenario_list
            for pop in ("matched", "attainable")
            for arm in ARMS
        ]
        self.store = Store(output)
        self.first, self.last, self.diagnostic = first, last, diagnostic
        self.special: dict[int, Distribution] = {}
        self.special_pending: dict[int, tuple[int, int, OGNQuote, Decimal]] = {}
        self.actions = load_actions()
        self.due = []
        for action in self.actions:
            if action.action_type not in ("CASH_DIVIDEND", "SPLIT"):
                continue
            day = action.ex_date or action.effective_date
            if day:
                self.due.append(
                    (minute(midnight(day)), 0 if action.action_type == "SPLIT" else 1, "EX", action)
                )
            if action.action_type == "CASH_DIVIDEND" and action.payable_date:
                self.due.append((minute(midnight(action.payable_date)), 2, "PAY", action))
        self.due.sort(key=lambda e: (e[0], e[1], e[3].event_id))
        self.done_due = set()
        self.integrals = np.zeros(20, dtype=np.int64)
        self.last_prices = np.zeros(20, float)
        self.known_closes = np.full(20, np.nan)
        self.known_marks = np.full(20, -1, dtype=np.int64)
        self.known_volumes = np.full(20, np.nan)
        self.cursor: int | None = None
        self.days_completed = 0
        self.opportunities = 0
        self.issued_counts = {arm: 0 for arm in ARMS}
        self.last_nav = {id(a): D(100000) for a in self.accounts}
        self.daily = []
        self.daily_incomplete_count = 0
        self.risk_cache: dict[int, tuple] = {}
        self.day_groups: dict[int, list[dict]] = {}
        self.ogn_borrow_cursors: dict[int, int] = {}
        self.last_completed: str | None = None
        self.last_market_end: int | None = None

    def sync(self, a: Account, now: int) -> None:
        for j in range(20):
            if np.isfinite(self.known_closes[j]):
                a.prices[j] = D(str(self.known_closes[j]))
                a.marks_at[j] = int(self.known_marks[j])
                a.volume[j] = D(str(self.known_volumes[j]))
                a.volume_available[j] = int(self.known_marks[j]) + a.scenario.lag

    def integrate_gap(self, end: int) -> None:
        if self.cursor is None:
            self.cursor = end
            return
        if end < self.cursor:
            raise ValueError("SOURCE_TIME_REORDER")
        seconds = (end - self.cursor) * 60
        ticks = np.rint(self.last_prices * 1000000).astype(np.int64)
        self.integrals += ticks * seconds
        self.cursor = end

    def before_day(self, day: Day) -> None:
        opened = int(day.starts[0])
        for at, _, kind, action in self.due:
            key = (action.event_id, kind)
            if key in self.done_due or at > opened:
                continue
            if at < minute(self.first + "T00:00:00Z"):
                self.done_due.add(key)
                continue
            self.integrate_gap(at)
            j = SYMBOLS.index(action.symbol)
            for a in self.accounts:
                a.accrue(self.integrals, at)
                a.accrue_funding(at)
                if kind == "PAY":
                    a.pay_dividend(action.event_id, at)
                elif action.action_type == "SPLIT":
                    if action.split_ratio_new_old is None:
                        raise ValueError("SPLIT_TERMS")
                    a.split(j, action.split_ratio_new_old, at)
                else:
                    if action.amount is None or action.payable_date is None:
                        raise ValueError("ORDINARY_ACTION_UNRESOLVED")
                    a.ex_dividend(
                        action.event_id,
                        j,
                        action.amount,
                        minute(midnight(action.payable_date)),
                        at,
                        action.status.value,
                    )
            if kind == "EX" and action.action_type == "SPLIT":
                ratio = float(action.split_ratio_new_old or 1)
                self.last_prices[j] /= ratio
                self.known_closes[j] /= ratio
            self.done_due.add(key)
        self.integrate_gap(opened)
        for a in self.accounts:
            a.accrue(self.integrals, opened)
            a.accrue_funding(opened)
        if day.date == "2021-06-03":
            for n, a in enumerate(self.accounts):
                positions = tuple(
                    (lot.key, lot.quantity, max(ZERO, lot.quantity * lot.basis))
                    for lot in a.lots.values()
                    if lot.ticker == 6 and lot.quantity
                )
                if not positions:
                    continue
                self.special[n] = distribution(
                    positions, self.market.clock, a.scenario.cil_sessions
                )
                a.unpriced_special = True
                for item in self.special[n].lots:
                    a.lots[item.cohort_id].tax_basis = item.mrk_long_tax_basis
                a.record(
                    "MRK_OGN_ENTITLEMENT",
                    opened,
                    positions=positions,
                    tax_allocation=[asdict(item) for item in self.special[n].lots],
                    source="PRIMARY_FORM8937_REGULAR_WAY;CIL_REFERENCE_PAYMENT_CONDITIONAL",
                )
        for n, state in list(self.special.items()):
            if not state.cil_paid and opened >= minute(state.pay_at) and state.cil_reference:
                changed, amounts, total = pay_cil(state, state.pay_at)
                a = self.accounts[n]
                for key, value in amounts:
                    a.credit(key, value, "OGN_CIL_CONDITIONAL_PAYMENT", opened)
                a.special_cash += total
                self.special[n] = changed
                self.special_view(n, opened)

    def special_view(self, n: int, now: int) -> None:
        a = self.accounts[n]
        state = self.special[n]
        values = state.values(utc(now))
        a.unpriced_special = values is None
        if values is not None:
            a.special_values = {key: value for key, value in values}
            if state.whole_settled and state.cil_paid:
                a.special_values = {}

    def special_tick(self, n: int, bar: dict | None, start: int, now: int) -> None:
        if n not in self.special:
            return
        a = self.accounts[n]
        state = self.special[n]
        if bar:
            at = datetime.fromisoformat(str(bar["t"]).replace("Z", "+00:00"))
            available = at + timedelta(minutes=1 + a.scenario.lag)
            oq = OGNQuote(
                at,
                at + timedelta(minutes=1),
                available,
                D(str(bar["o"])),
                self.market.ogn_source_hash,
            )
            oq.validate(utc(now))
            pending = self.special_pending.get(n)
            if pending and start >= pending[0] and not state.whole_settled:
                eff, decision, reference, capacity = pending
                changed, amounts, fee = settle_whole(
                    state,
                    oq,
                    utc(decision),
                    utc(now),
                    a.scenario.spread,
                    a.scenario.impact,
                    a.scenario.fee,
                    a.scenario.minimum,
                    known_reference=reference,
                    external_capacity=capacity,
                )
                if state.physical_whole < 0:
                    cursor = getattr(self, "ogn_borrow_cursors", {}).get(n, minute(EX))
                    integral = ZERO
                    previous = None
                    for ts, row in sorted(self.market.ogn.items()):
                        if cursor <= ts < start:
                            previous = D(str(row["o"]))
                            integral += previous * 60
                    if start > cursor and previous is None:
                        raise ValueError("UNPRICED_OGN_SHORT_CARRY")
                    outstanding = state.physical_whole + sum(
                        (q for _, q in state.whole_fills), ZERO
                    )
                    charge = max(ZERO, -outstanding) * integral * a.scenario.borrow / YEAR
                    shorts = [lot for lot in state.lots if lot.whole_attribution < 0]
                    denom = sum((-lot.whole_attribution for lot in shorts), ZERO)
                    left = charge
                    for index, lot in enumerate(shorts):
                        part = (
                            charge * (-lot.whole_attribution) / denom
                            if index < len(shorts) - 1
                            else left
                        )
                        left -= part
                        a.credit(lot.cohort_id, -part, "OGN_PHYSICAL_SHORT_BORROW", now)
                        a.lots[lot.cohort_id].borrow += part
                    a.borrow_paid += charge
                    self.ogn_borrow_cursors[n] = start
                for key, value in amounts:
                    a.credit(key, value, "OGN_WHOLE_DISPOSAL", now)
                for key, value in changed.fee_allocations[len(state.fee_allocations) :]:
                    a.lots[key].fees += value
                for key, value in changed.cost_allocations[len(state.cost_allocations) :]:
                    a.lots[key].cost += value
                external_delta = sum((q for _, q in changed.whole_fills), ZERO) - sum(
                    (q for _, q in state.whole_fills), ZERO
                )
                total_cash = sum((v for _, v in amounts), ZERO)
                a.commission += fee
                a.friction += -external_delta * oq.value - total_cash - fee
                a.record(
                    "OGN_EXTERNAL_DISPOSAL",
                    now,
                    effective=start,
                    decision=decision,
                    external_delta=external_delta,
                    raw_reference=oq.value,
                    external_cash=total_cash,
                    fee=fee,
                    conditional_CIL=True,
                )
                a.special_cash += sum((v for _, v in amounts), ZERO)
                self.special[n] = state = changed
                del self.special_pending[n]
            state = observe(
                state,
                oq,
                utc(now),
                a.scenario.cil_postclose,
            )
            cq = OGNQuote(
                at + timedelta(minutes=1),
                at + timedelta(minutes=1),
                available,
                D(str(bar["c"])),
                self.market.ogn_source_hash,
            )
            state = observe(
                state,
                cq,
                utc(now),
                a.scenario.cil_postclose,
            )
            if not state.whole_settled and n not in self.special_pending:
                remaining = state.physical_whole + sum((q for _, q in state.whole_fills), ZERO)
                capacity = (D(str(bar["v"])) * D(".01")).to_integral_value(rounding=ROUND_DOWN)
                if abs(remaining) > capacity:
                    a.reject("OGN_PARTICIPATION_CAP_REQUIRES_CONTINUATION")
                else:
                    self.special_pending[n] = (now + 1, now, cq, capacity)
                    a.record(
                        "OGN_WHOLE_ORDER",
                        now,
                        effective=now + 1,
                        quantity=-remaining,
                        prior_volume=D(str(bar["v"])),
                        capacity=capacity,
                        available=now,
                    )
            self.special[n] = state
        self.special_view(n, now)
        a.risk_hold = not self.special[n].whole_settled and self.special[n].physical_whole != 0

    def audit_origin(
        self,
        a: Account,
        org: int,
        group: list[dict],
        now: int,
        statuses: dict[str, str],
        default: str = "NOT_READY_AT_VINTAGE_DECISION",
    ) -> None:
        for row in group:
            ready_at = max(org + a.scenario.lag, minute(row["issued_at"]) + a.scenario.lag - 2)
            known = now >= ready_at and bool(row["input_eligible"])
            a.record(
                "OPPORTUNITY",
                now,
                origin=org,
                ticker=row["ticker"],
                reason=statuses.get(row["ticker"], default),
                checkpoint_hash=row["checkpoint_hash"],
                recipe_hash=row.get("recipe_hash"),
                c3_hash=row.get("c3_hash"),
                magnitude=row.get("magnitude_c3") if known else None,
                direction=row.get("direction") if known else None,
                multiplier=row.get("g_" + a.arm)
                if known and valid_multiplier(row.get("g_" + a.arm))
                else None,
                feature_lineage=row.get("feature_lineage") if known else None,
                actual_quantity=None,
            )

    def decision(self, a: Account, day: Day, now: int, integral: np.ndarray) -> None:
        if a.pending:
            return
        self.sync(a, now)
        a.accrue(integral, now)
        a.accrue_funding(
            int(
                day.starts[
                    min(len(day.starts) - 1, max(0, now - int(day.starts[0]) - 1 - a.scenario.lag))
                ]
            )
            + 1
        )
        # No later decision may rely on a not-yet-observed physical fill.
        if a.pending:
            return
        nav, free, names, status = a.capacity(now)
        if status == "RISK_BREACH":
            for lot in a.lots.values():
                a.cancel_unsubmitted(lot.key, now, "OBSERVED_CAP_BREACH")
            nav, free, names, status = a.capacity(now)
        requests: dict[int, list[Request]] = {}
        for lot in a.lots.values():
            if (
                a.scenario.borrow_stress
                and lot.quantity < 0
                and a.quantity[lot.ticker] < 0
                and 10000
                <= int(canonical(("20261109", SYMBOLS[lot.ticker], day.date)), 16) % 1000000
                < 12000
            ):
                a.cancel_unsubmitted(lot.key, now, "BORROW_RECALL")
                requests.setdefault(lot.ticker, []).append(
                    Request(lot.key, -lot.quantity, "BORROW_RECALL")
                )
                continue
            if lot.pending and now > lot.deadline:
                a.cancel_unsubmitted(lot.key, now, "ENTRY_DEADLINE")
                a.reject("ENTRY_UNSUBMITTED_REMAINDER_EXPIRED")
            if lot.quantity and (now >= lot.endpoint + a.scenario.lag or status == "RISK_BREACH"):
                role = "RISK_LIQUIDATION" if status == "RISK_BREACH" else "EXIT"
                requests.setdefault(lot.ticker, []).append(Request(lot.key, -lot.quantity, role))
        # Current origin opportunities only. No scored/F09/endpoint-price field is read.
        for org, group in self.day_groups.items():
            if org in a.processed_origins or now < org + a.scenario.lag:
                continue
            if now > org + 9:
                a.processed_origins.add(org)
                a.reject("ENTRY_WINDOW_EXPIRED", len(group))
                self.audit_origin(a, org, group, now, {}, "ENTRY_WINDOW_EXPIRED")
                continue
            ready = []
            statuses: dict[str, str] = {}
            for row in group:
                statuses[row["ticker"]] = "DEPENDENCY_NOT_READY_AT_VINTAGE_DECISION"
                issued = max(org + a.scenario.lag, minute(row["issued_at"]) + a.scenario.lag - 2)
                if now < issued:
                    continue
                ready_field = row.get("feature_ready")
                if ready_field is not None and not pd.isna(ready_field):
                    if minute(ready_field) + a.scenario.lag - 2 > now:
                        raise ValueError("FUTURE_FEATURE_READY_AT_DECISION")
                control_field = row.get("control_latest_available")
                if (
                    a.arm in ("ROLLING_RISK", "EWMA_RISK")
                    and control_field is not None
                    and not pd.isna(control_field)
                ):
                    if minute(control_field) + a.scenario.lag - 2 > now:
                        raise ValueError("UNMATURED_CLASSICAL_CONTROL_AT_DECISION")
                if (
                    not bool(row["input_eligible"])
                    or not valid_multiplier(row["g_" + a.arm])
                    or int(row["direction"]) == 0
                ):
                    a.reject("SIGNAL_OR_ARM_ABSTENTION")
                    statuses[row["ticker"]] = "SIGNAL_OR_ARM_ABSTENTION"
                    continue
                if a.population == "matched" and not bool(row["matched_four_arms"]):
                    a.reject("NOT_MATCHED_INPUT_POPULATION")
                    statuses[row["ticker"]] = "NOT_MATCHED_INPUT_POPULATION"
                    continue
                multiplier = D(str(row["g_" + a.arm]))
                if not D(".5") <= multiplier <= D("1.5") or (a.arm == "EQUAL" and multiplier != 1):
                    raise ValueError("TRADING_MULTIPLIER_CONTRACT")
                j = SYMBOLS.index(row["ticker"])
                if a.prices[j] is None or now - a.marks_at[j] > 5 or a.volume[j] is None:
                    statuses[row["ticker"]] = "EXECUTION_SOURCE_MISSING_OR_STALE"
                    continue
                endpoint = minute(row["endpoint"])
                marker = utc(self.execution_calendar.next(endpoint + a.scenario.lag))
                if str(marker.date()) > self.last:
                    a.reject("CALENDAR_TERMINAL_CUTOFF")
                    statuses[row["ticker"]] = "CALENDAR_TERMINAL_CUTOFF"
                    continue
                if a.scenario.prohibit_mrk_cross and j == 6 and org < minute(EX) <= endpoint:
                    a.reject("KNOWN_MRK_ACTION_CROSS_PROHIBITED")
                    statuses[row["ticker"]] = "KNOWN_MRK_ACTION_CROSS_PROHIBITED"
                    continue
                if a.scenario.borrow_stress and int(row["direction"]) < 0:
                    draw = int(canonical(("20261109", row["ticker"], day.date)), 16) % 1000000
                    if draw < 12000:
                        a.reject("CONDITIONAL_BORROW_REJECT_STRESS")
                        statuses[row["ticker"]] = "CONDITIONAL_BORROW_REJECT_STRESS"
                        continue
                ready.append((j, row))
            if not ready:
                if now < org + a.scenario.lag + 1:
                    continue
                a.processed_origins.add(org)
                a.reject("NO_EXECUTION_READY_CROSS_SECTION")
                self.audit_origin(a, org, group, now, statuses)
                continue
            if status != "READY" or a.unpriced_special or a.risk_hold:
                a.processed_origins.add(org)
                a.reject("SPECIAL_DISPOSAL_PENDING" if a.risk_hold else status, len(ready))
                for _, row in ready:
                    statuses[row["ticker"]] = "SPECIAL_DISPOSAL_PENDING" if a.risk_hold else status
                self.audit_origin(a, org, group, now, statuses)
                continue
            a.processed_origins.add(org)
            denominator = sum((D(str(row["g_" + a.arm])) for _, row in ready), ZERO)
            reserve = D(len(ready)) * a.scenario.minimum + D(".002") * nav
            budget = min(
                D(".2") * max(ZERO, nav - reserve),
                max(ZERO, nav - a.gross()),
                max(ZERO, free - reserve),
            )
            for j, row in sorted(ready, key=lambda pair: pair[0]):
                p = a.prices[j]
                if p is None:
                    raise AssertionError("READY_PRICE")
                amount = min(
                    budget * D(str(row["g_" + a.arm])) / denominator,
                    max(ZERO, D(".1") * nav - names.get(j, ZERO)),
                )
                q = (amount / p).to_integral_value(rounding=ROUND_DOWN) * D(int(row["direction"]))
                if not q:
                    a.reject("ROUNDING_OR_CAP_CASH")
                    statuses[row["ticker"]] = "ROUNDING_OR_CAP_CASH"
                    continue
                key = f"{row['checkpoint_hash']}|{a.arm}|{org}|{row['ticker']}"
                if key in a.lots:
                    raise ValueError("DUPLICATE_OR_DYNAMIC_RESIZE")
                lot = Lot(
                    key,
                    j,
                    org,
                    minute(row["endpoint"]),
                    org + 10,
                    int(row["direction"]),
                    int(q),
                    D(str(row["g_" + a.arm])),
                    pending=q,
                )
                a.lots[key] = lot
                statuses[row["ticker"]] = "CANDIDATE_RESERVED"
                requests.setdefault(j, []).append(Request(key, q, "ENTRY"))
            self.audit_origin(a, org, group, now, statuses)
            break
        a.refresh()
        for lot in a.lots.values():
            if (
                lot.pending
                and now <= lot.deadline
                and not any(r.key == lot.key for r in requests.get(lot.ticker, []))
            ):
                requests.setdefault(lot.ticker, []).append(Request(lot.key, lot.pending, "ENTRY"))
        for j, group in sorted(requests.items()):
            if a.volume[j] is None or now - a.marks_at[j] > 5:
                a.reject("EXIT_OR_ENTRY_SOURCE_STALE")
                continue
            target = sum((r.delta for r in group), ZERO)
            volume = a.volume[j]
            if volume is None:
                raise AssertionError("READY_VOLUME")
            cap = (volume * D(".01")).to_integral_value(rounding=ROUND_DOWN)
            submitted = min(abs(target), cap) * (1 if target > 0 else -1) if target else ZERO
            expiry = min((a.lots[r.key].deadline for r in group if r.role == "ENTRY"), default=None)
            if expiry is not None and now + 1 > expiry:
                continue
            a.order_seq += 1
            key = f"{day.date}:{now}:{j}:{a.order_seq}"
            a.pending[j] = Order(
                key,
                j,
                now,
                self.execution_calendar.next(now),
                tuple(group),
                submitted,
                a.volume_available[j],
                expiry,
            )
            a.record(
                "ORDER",
                now,
                order=key,
                ticker=j,
                effective=now + 1,
                submitted=submitted,
                target=target,
                unsubmitted=target - submitted,
                prior_volume=a.volume[j],
                prior_volume_available=a.volume_available[j],
                source_hash=day.source_hash,
            )
        a.reconcile()

    def risk_status(self, n: int) -> str:
        a = self.accounts[n]
        if a.unpriced_special:
            return "UNPRICED_SPECIAL"
        if n not in self.risk_cache:
            vintages = {}
            for lot in a.lots.values():
                if not lot.quantity and not lot.pending:
                    continue
                vintages.setdefault(lot.origin, np.zeros(20, float))[lot.ticker] += float(
                    abs(lot.quantity) + abs(lot.pending)
                )
            matrix = np.stack(list(vintages.values())) if vintages else np.zeros((0, 20), float)
            self.risk_cache[n] = (
                float(a.cash + a.claim_total() + sum(a.special_values.values(), ZERO)),
                a.quantity.astype(float).copy(),
                a.abs_virtual.copy(),
                matrix,
                np.asarray(a.borrow_anchor, dtype=float),
                float(sum((abs(v) for v in a.special_values.values()), ZERO)),
            )
        cash, q, absolute, vintage, anchor, specialgross = self.risk_cache[n]
        prices = np.nan_to_num(self.known_closes, nan=0)
        owed = (
            np.dot(np.maximum(-q, 0), self.integrals.astype(float) - anchor)
            / 1e6
            * float(a.scenario.borrow)
            / float(YEAR)
        )
        nav = cash + np.dot(q, prices) - owed
        gross = np.dot(absolute, prices) + specialgross
        # A small outward threshold sends ambiguous float comparisons to the
        # exact Decimal gate. It never grants capital or changes a submitted fill.
        if (
            nav <= 0
            or gross > nav - 1e-6
            or np.any(absolute * prices > 0.1 * nav - 1e-6)
            or np.any(vintage @ prices > 0.2 * nav - 1e-6)
            or a.cash < a.restricted()
        ):
            return "RISK_BREACH"
        return "READY"

    def checkpoint(self, day: str) -> None:
        from .checkpoint import seal

        omitted = {
            "market",
            "store",
            "risk_cache",
            "day_groups",
            "admission",
            "daily",
            "execution_calendar",
            "actions",
            "due",
        }
        body = {k: v for k, v in self.__dict__.items() if k not in omitted}
        publish(self.store.path / "checkpoints" / (day + ".json"), seal(body))

    @classmethod
    def restart(cls, checkpoint_path: Path, output: Path, admission: object):
        from .checkpoint import unseal
        from .release import check_admission

        body = unseal(json.loads(checkpoint_path.read_text()))
        if not isinstance(body, dict):
            raise ValueError("REPLAY_STATE_SCHEMA")
        if not all(isinstance(k, str) for k in body):
            raise ValueError("REPLAY_STATE_KEYS")
        restored_fields = {str(k): v for k, v in body.items()}
        first, last, diagnostic = (
            restored_fields["first"],
            restored_fields["last"],
            restored_fields["diagnostic"],
        )
        if (
            not isinstance(first, str)
            or not isinstance(last, str)
            or not isinstance(diagnostic, bool)
        ):
            raise ValueError("REPLAY_STATE_SCOPE_TYPES")
        check_admission(admission, first, last, diagnostic)
        restored = cls.__new__(cls)
        restored.__dict__.update(restored_fields)
        restored.admission = admission
        completed = restored_fields.get("last_completed")
        if not isinstance(completed, str):
            raise ValueError("REPLAY_COMPLETED_DATE")
        next_day = (datetime.fromisoformat(completed) + timedelta(days=1)).date().isoformat()
        restored.market = Market(next_day, last)
        restored.execution_calendar = ExecutionCalendar(restored.market.clock)
        restored.actions = load_actions()
        restored.due = []
        for action in restored.actions:
            if action.action_type not in ("CASH_DIVIDEND", "SPLIT"):
                continue
            day = action.ex_date or action.effective_date
            if day:
                restored.due.append(
                    (minute(midnight(day)), 0 if action.action_type == "SPLIT" else 1, "EX", action)
                )
            if action.action_type == "CASH_DIVIDEND" and action.payable_date:
                restored.due.append((minute(midnight(action.payable_date)), 2, "PAY", action))
        restored.due.sort(key=lambda e: (e[0], e[1], e[3].event_id))
        restored.store = Store(output, resume=True)
        restored.risk_cache = {}
        restored.day_groups = {}
        restored.daily = []
        for account in restored.accounts:
            account.reconcile()
        return restored

    def run(self, stop_after: int | None = None) -> dict:
        started = time.monotonic()
        for day in self.market.days():
            if self.last_completed is not None and day.date <= self.last_completed:
                continue
            self.opportunities += len(day.signals)
            self.day_groups = {
                minute(org): part.to_dict("records")
                for org, part in day.signals.groupby("origin", sort=True)
            }
            self.risk_cache.clear()
            self.before_day(day)
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
                for n, a in enumerate(self.accounts):
                    now = start + 1 + a.scenario.lag
                    due = [
                        (j, o)
                        for j, o in a.pending.items()
                        if o.effective <= start and o.status != "UNRESOLVED_SOURCE_BAR"
                    ]
                    if due:
                        a.accrue(ibefore, now)
                        a.accrue_funding(start)
                        for j, o in due:
                            if valid[j]:
                                if o.expiry is not None and start > o.expiry:
                                    a.reject("UNRESOLVED_EXPIRED_SUBMITTED_ORDER")
                                    a.nav_incomplete = True
                                    continue
                                self.sync(a, now)
                                a.fill(o, D(str(day.opens[i, j])), now, start)
                                if o.status == "OBSERVED":
                                    del a.pending[j]
                            else:
                                if o.status != "UNRESOLVED_SOURCE_BAR":
                                    a.record(
                                        "UNRESOLVED_SOURCE_BAR",
                                        now,
                                        order=o.key,
                                        ticker=j,
                                        first_expected_minute=o.effective,
                                        submitted_quantity=o.submitted_quantity,
                                        no_broker_cancellation_claim=True,
                                    )
                                o.status = "UNRESOLVED_SOURCE_BAR"
                                a.nav_incomplete = True
                                a.reject("UNOBSERVABLE_SUBMITTED_FILL")
                    special_active = n in self.special and (
                        not self.special[n].whole_settled or self.special[n].cil_reference is None
                    )
                    if special_active:
                        self.special_tick(n, day.ogn.get(start), start, now)
                    if due or special_active:
                        self.risk_cache.pop(n, None)
                    state = self.risk_status(n)
                    relevant = (
                        bool(a.pending)
                        or any(
                            lot.pending or lot.quantity and now >= lot.endpoint + a.scenario.lag
                            for lot in a.lots.values()
                        )
                        or any(
                            org + a.scenario.lag <= now <= org + 9
                            and org not in a.processed_origins
                            for org in self.day_groups
                        )
                        or state == "RISK_BREACH"
                    )
                    if relevant:
                        self.decision(a, day, now, self.integrals)
                        self.risk_cache.pop(n, None)
            end = int(day.starts[-1]) + 1
            self.last_market_end = end
            for n, a in enumerate(self.accounts):
                now = end + a.scenario.lag
                if (
                    day.date == "2021-06-03"
                    and n in self.special
                    and a.scenario.cil_postclose is not None
                ):
                    state = self.special[n]
                    if state.mark is not None:
                        when = max(now, minute(pd.Timestamp("2021-06-03T20:02:00Z")))
                        self.special[n] = observe(
                            state,
                            state.mark,
                            utc(when),
                            a.scenario.cil_postclose,
                        )
                        self.special_view(n, when)
                for org, group in self.day_groups.items():
                    if org not in a.processed_origins:
                        self.audit_origin(
                            a, org, group, now, {}, "ACCOUNT_PENDING_OR_WINDOW_NOT_EXECUTABLE"
                        )
                        a.processed_origins.add(org)
                self.sync(a, now)
                a.accrue(self.integrals, now)
                a.accrue_funding(end)
                a.reconcile()
                nav = a.nav()
                status = (
                    "NAV_INCOMPLETE"
                    if nav is None
                    or a.nav_incomplete
                    or a.risk_hold
                    or any(o.status == "UNRESOLVED_SOURCE_BAR" for o in a.pending.values())
                    or any(a.quantity[j] and now - a.marks_at[j] > 5 for j in range(20))
                    else "OBSERVED"
                )
                daily = {
                    "date": day.date,
                    "arm": a.arm,
                    "population": a.population,
                    "scenario": a.scenario.name,
                    "asof_market_utc": stamp(end),
                    "known_at_utc": stamp(
                        max(
                            now,
                            end + 2
                            if day.date == "2021-06-03" and a.scenario.cil_postclose
                            else now,
                        )
                    ),
                    "nav": nav if status == "OBSERVED" else None,
                    "last_known_mark_equity": nav,
                    "proxy_standalone_cumulative": a.proxy_total(),
                    "physical_long_value": sum(
                        (
                            D(int(q)) * (a.prices[j] or ZERO)
                            for j, q in enumerate(a.quantity)
                            if q > 0
                        ),
                        ZERO,
                    ),
                    "physical_short_value": sum(
                        (
                            -D(int(q)) * (a.prices[j] or ZERO)
                            for j, q in enumerate(a.quantity)
                            if q < 0
                        ),
                        ZERO,
                    ),
                    "marked_net": sum(
                        (D(int(q)) * (a.prices[j] or ZERO) for j, q in enumerate(a.quantity)), ZERO
                    ),
                    "cash": a.cash,
                    "restricted_proceeds": a.restricted(),
                    "claims": a.claim_total(),
                    "special_value": sum(a.special_values.values(), ZERO),
                    "gross": a.gross() + sum((abs(v) for v in a.special_values.values()), ZERO),
                    "own_cash": a.cash - a.restricted(),
                    "physical": a.quantity.tolist(),
                    "status": status,
                    "commission_cumulative": a.commission,
                    "friction_cumulative": a.friction,
                    "borrow_cumulative": a.borrow_paid,
                    "funding_cumulative": a.funding_paid,
                    "dividend_cash_cumulative": a.dividend_cash,
                    "maximum_balance_residual": a.maximum_residual,
                    "rejections_cumulative": dict(a.rejected),
                    "journal_hash": a.journal_hash,
                    "outstanding_lots": len(a.lots),
                    "pending_orders": len(a.pending),
                }
                if status != "OBSERVED":
                    self.daily_incomplete_count += 1
                self.store.write(a.scenario.name, "daily", [daily])
                self.daily.append(daily)
                a.compact(now)
                self.store.write(a.scenario.name, "events", a.events)
                a.events = []
                self.store.write(a.scenario.name, "cohorts", a.closed)
                a.closed = []
            self.days_completed += 1
            self.last_completed = day.date
            self.checkpoint(day.date)
            if stop_after is not None and self.days_completed >= stop_after:
                break
            if not self.diagnostic and any(a.nav_incomplete for a in self.accounts):
                # Preserve the complete received-day books and unresolved
                # reservations; no later strategy day or headline is computed.
                break
            if self.days_completed % 10 == 0:
                print(
                    "days",
                    self.days_completed,
                    "elapsed",
                    round(time.monotonic() - started, 1),
                    flush=True,
                )
        end = self.last_market_end
        if end is None:
            raise ValueError("NO_MARKET_SESSION_IN_AUTHORIZED_SCOPE")
        for a in self.accounts:
            for lot in a.lots.values():
                point = a.prices[lot.ticker]
                known = (
                    point is not None
                    and not a.unpriced_special
                    and not a.nav_incomplete
                    and (not lot.quantity or end + a.scenario.lag - a.marks_at[lot.ticker] <= 5)
                )
                claims = sum(
                    (v for (event, key), (v, due) in a.claims.items() if key == lot.key), ZERO
                )
                self.store.write(
                    a.scenario.name,
                    "terminal_lots",
                    [
                        {
                            "arm": a.arm,
                            "population": a.population,
                            "key": lot.key,
                            "ticker": lot.ticker,
                            "origin": lot.origin,
                            "endpoint": lot.endpoint,
                            "quantity": lot.quantity,
                            "entry_at": lot.entry_at,
                            "entry_price": lot.entry_price,
                            "pending": lot.pending,
                            "cash": lot.cash,
                            "ordinary_claims": claims,
                            "special_claims": a.special_values.get(lot.key, ZERO),
                            "marked_value": lot.quantity * point if point is not None else None,
                            "total_attributable_equity": lot.cash
                            + lot.quantity * point
                            + claims
                            + a.special_values.get(lot.key, ZERO)
                            if known and point is not None
                            else None,
                            "snapshot_session": self.last_completed,
                            "partial_snapshot": self.last_completed != self.last,
                            "status": "MARKED_OPEN" if known else "UNRESOLVED",
                            "fees": lot.fees,
                            "cost": lot.cost,
                            "borrow": lot.borrow,
                            "funding": lot.funding,
                        }
                    ],
                )
        self.store.close()
        summary = {
            "sessions": self.days_completed,
            "opportunities": self.opportunities,
            "accounts": len(self.accounts),
            "elapsed_seconds": time.monotonic() - started,
            "maximum_ledger_residual": str(
                max((a.maximum_residual for a in self.accounts), default=ZERO)
            ),
            "terminal_pending_orders": sum(len(a.pending) for a in self.accounts),
            "terminal_unpriced_special": sum(a.unpriced_special for a in self.accounts),
            "unresolved": any(a.nav_incomplete for a in self.accounts)
            or self.daily_incomplete_count > 0,
            "daily_incomplete_records": self.daily_incomplete_count,
            "diagnostic": self.diagnostic,
        }
        publish(self.store.path / ("RUN_RECEIPT_" + str(self.last_completed) + ".json"), summary)
        return summary
