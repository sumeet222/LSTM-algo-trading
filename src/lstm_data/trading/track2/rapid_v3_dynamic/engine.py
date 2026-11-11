"""A shared chronological replay with independent dynamic cohort state."""

import time
from dataclasses import replace
from math import log

import numpy as np

from ..rapid_v1.portfolio import FastAccount, Request
from ..rapid_v1.shared_features import FeatureCache, FeatureFrame
from ..rapid_v1.sources import RawDay
from ..rapid_v1.strategies import IDS, DirectionIntent, evaluate
from ..stage012.calendar_schedule import MarketClock
from ..stage35.final_backtest_v4.book import YEAR
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from .book import ZERO, DynamicLedger, add
from .decisions import DecisionEngine
from .policy import Case, HoldingClock, initial, monitored, observe, scores


class DynamicRiskScreen:
    """Vector version of V1's floating prefilter. Exact order gate is inherited."""

    def __init__(self, size: int):
        self.name_limit = np.full(size, 0.10)
        self.q = np.zeros((size, 20))
        self.absolute = np.zeros_like(self.q)
        self.filled = np.zeros_like(self.q)
        self.anchor = np.zeros_like(self.q)
        self.vintage = np.zeros((size, 8, 20))
        self.cash = np.zeros(size)
        self.available = np.zeros(size)
        self.special = np.zeros(size)
        self.restricted = np.zeros(size, bool)
        self.held = np.zeros(size, bool)
        self.next_due = np.full(size, np.iinfo(np.int64).max)

    def update(self, n: int, a: DynamicLedger, legacy: bool) -> None:
        self.name_limit[n] = float(a.name_cap)
        self.q[n] = a.quantity
        self.absolute[n] = a.abs_virtual
        self.anchor[n] = a.borrow_anchor
        self.filled[n] = 0
        restricted = a.restricted()
        self.available[n] = float(a.cash - restricted)
        self.restricted[n] = a.cash < restricted
        self.cash[n] = float(a.cash + a.claim_total() + sum(a.special_values.values(), ZERO))
        self.special[n] = float(sum((abs(v) for v in a.special_values.values()), ZERO))
        self.held[n] = not a.unpriced_special and (
            bool(np.any(a.quantity if legacy else a.abs_virtual))
            or any(lot.pending for lot in a.lots.values())
        )
        vintages: dict[int, np.ndarray] = {}
        next_due = int(np.iinfo(np.int64).max)
        for lot in a.lots.values():
            if lot.quantity:
                self.filled[n, lot.ticker] += float(abs(lot.quantity))
                state = a.groups[a.group_of[lot.key]]
                if state["reason"] is not None:
                    next_due = 0
                elif state["max_decision"] is not None:
                    next_due = min(next_due, state["max_decision"])
            if lot.pending:
                next_due = 0
            if lot.quantity or lot.pending:
                v = vintages.setdefault(lot.origin, np.zeros(20))
                v[lot.ticker] += float(abs(lot.quantity) + abs(lot.pending))
        self.next_due[n] = next_due
        if len(vintages) > self.vintage.shape[1]:
            extra = max(self.vintage.shape[1], len(vintages) - self.vintage.shape[1])
            self.vintage = np.pad(self.vintage, ((0, 0), (0, extra), (0, 0)))
        self.vintage[n] = 0
        for j, v in enumerate(vintages.values()):
            self.vintage[n, j] = v

    def status(
        self,
        price: np.ndarray,
        integral: np.ndarray,
        rates: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        price = np.nan_to_num(price, nan=0)
        owed = np.einsum("ij,ij->i", np.maximum(-self.q, 0), integral - self.anchor)
        owed = owed / 1e6 * rates / float(YEAR)
        nav = self.cash + np.einsum("ij,j->i", self.q, price) - owed
        gross = np.einsum("ij,j->i", self.absolute, price) + self.special
        filled = np.einsum("ij,j->i", self.filled, price) + self.special
        name = np.max(self.absolute * price, axis=1)
        vintage = np.max(np.einsum("ijk,k->ij", self.vintage, price), axis=1)
        # Use the same outward tolerance as V1. Near the floating boundary
        # check the V1 prefilter before enabling any new prospective decision.
        margins = np.column_stack(
            (
                nav,
                nav - 1e-6 - gross,
                self.name_limit * nav - 1e-6 - name,
                0.2 * nav - 1e-6 - vintage,
            )
        )
        breach = self.held & ((nav <= 0) | np.any(margins[:, 1:] < 0, axis=1) | self.restricted)
        ambiguous = self.held & np.any(np.abs(margins) <= 1e-7, axis=1)
        return breach, ambiguous, nav, filled


class DynamicBatch(DecisionEngine):
    def __init__(
        self,
        cache: FeatureCache,
        first: str,
        last: str,
        cases: tuple[Case, ...],
        legacy: bool = False,
    ):
        super().__init__(cache, first, last, cases)
        self.dynamic_accounts = [
            DynamicLedger(c.key, c.mode, a.scenario, name_cap=c.name_cap, regime=c.variant)
            for c, a in zip(cases, self.fast_accounts, strict=True)
        ]
        self.fast_accounts = list(self.dynamic_accounts)
        self.accounts = list(self.dynamic_accounts)
        self.dynamic_cases = {c.key: c for c in cases}
        # Calendar metadata only. RawMarket still stops at 2024-12-31.
        self.execution_calendar = ExecutionCalendar(MarketClock("2020-01-01", "2025-02-01"))
        self.holding = HoldingClock(self.execution_calendar)
        self.legacy = legacy
        self.factor_history: list[np.ndarray] = []
        self.beta = np.full(20, np.nan)
        self.entry_slots: dict[str, np.ndarray] = {}
        for sid in IDS:
            from ..rapid_v1.strategies import SLOTS

            self.entry_slots[sid] = np.asarray(
                [
                    cache.data["decisions"][i]
                    for i, date in enumerate(cache.data["dates"])
                    if first <= str(date) <= last
                    and int(cache.data["slots"][i]) in SLOTS[sid]
                    and (sid.startswith("M") or bool(cache.data["weekly"][i]))
                ],
                dtype=np.int64,
            )

    def rth_index(self, at: int) -> int:
        return self.holding.index(at)

    def fit_beta(self, previous_close: np.ndarray) -> None:
        self.factor_history.append(previous_close.copy())
        self.factor_history = self.factor_history[-61:]
        self.beta[:] = np.nan
        if len(self.factor_history) < 51:
            return
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.diff(np.log(np.asarray(self.factor_history)), axis=0)
        for j in range(20):
            others = np.delete(r, j, axis=1)
            valid = np.isfinite(others)
            count = valid.sum(axis=1)
            peer = np.where(valid, others, 0).sum(axis=1) / np.maximum(1, count)
            ok = (count >= 11) & np.isfinite(r[:, j])
            if ok.sum() >= 50 and np.var(peer[ok], ddof=1) > 1e-12:
                self.beta[j] = np.cov(peer[ok], r[ok, j], ddof=1)[0, 1] / np.var(peer[ok], ddof=1)

    def allocate(
        self, a: FastAccount, frame: FeatureFrame, intents: tuple[DirectionIntent, ...], now: int
    ) -> dict[int, list[Request]]:
        if not isinstance(a, DynamicLedger):
            raise TypeError("V3_DYNAMIC_ACCOUNT_REQUIRED")
        case = self.dynamic_cases[a.arm]
        ready = []
        for it in intents:
            if not self.legacy and any(
                a.cooling.get((j, s), -1) >= now for j, s in zip(it.tickers, it.signs, strict=True)
            ):
                a.reject("V3_SIGNAL_COOLDOWN")
            else:
                ready.append(it if self.legacy else replace(it, endpoint=it.origin))
        req = self.allocate_budget(a, frame, tuple(ready), now)
        submitted = {r.key for rs in req.values() for r in rs}
        for it in ready:
            keys = tuple(f"{a.arm}|{it.origin}|{j}" for j in it.tickers)
            if not any(k in submitted for k in keys):
                continue
            if not all(k in submitted for k in keys):
                raise ValueError("INCOMPLETE_PAIRED_ALLOCATION")
            g = initial(case.strategy, it, frame, self.beta)
            g["keys"] = keys
            g["frozen_endpoint"] = it.endpoint
            a.groups[keys[0]] = g
            a.group_of.update({k: keys[0] for k in keys})
            if g["trail_distance"] is None:
                a.stats.counts["V3_TRAIL_PREENTRY_SCALE_UNAVAILABLE"] += 1
        return req

    def after_settlement(self, a: DynamicLedger) -> None:
        for state in a.groups.values():
            lots = [a.lots[k] for k in state["keys"] if k in a.lots]
            if not lots:
                continue
            case = self.dynamic_cases[a.arm]
            if (
                state["active_at"] is None
                and len(lots) == len(state["keys"])
                and all(x.quantity and x.entry_at is not None for x in lots)
            ):
                active = max(int(x.entry_at or 0) for x in lots)
                micro = case.strategy.startswith("M")
                state["active_at"] = active
                state["max_decision"] = (
                    state["frozen_endpoint"] if self.legacy else self.holding.maximum(active, micro)
                ) + 2
                state["minimum_age"] = (
                    self.holding.advance(active, 60) if micro else self.holding.sessions(active, 1)
                ) + 2
                if not self.legacy:
                    self.initialize_peak(state)
            if self.legacy or state.get("cooling_booked") or any(x.quantity for x in lots):
                continue
            details = [a.closing[x.key] for x in lots if x.key in a.closing]
            if not details or any(d["primary"].startswith("RISK_") for d in details):
                continue
            last = max(details, key=lambda d: d["posted"])
            if last["primary"] not in ("SIGNAL_REVERSAL", "SIGNAL_WEAKENING", "EVENT_RESOLVED"):
                continue
            at = last["posted"]
            slots = self.entry_slots[case.strategy]
            i = int(np.searchsorted(slots, at, side="right"))
            until = int(slots[i]) if i < len(slots) else at
            for j, s in zip(state["tickers"], state["signs"], strict=True):
                a.cooling[j, s] = max(until, a.cooling.get((j, s), -1))
            state["cooling_booked"] = True

    def initialize_peak(self, state: dict) -> None:
        raw = state.get("entry_raw", {})
        j = state["tickers"][0]
        if j not in raw or state["trail_distance"] is None:
            return
        factors = self.current_refs["factor"]
        base = log(raw[j] * float(factors[j]))
        if state["sid"] == "R05":
            k = state["tickers"][1]
            if k not in raw:
                return
            base -= state["pair"][0] * log(raw[k] * float(factors[k]))
        if state["sid"] == "R06":
            peers = list(state["peers"])
            p = self.known_closes[peers] * factors[peers]
            if not len(peers) or not np.all(np.isfinite(p) & (p > 0)):
                return
            base -= state["fitted_beta"] * float(np.log(p).mean())
        state["peak"] = state["signs"][0] * base

    def observe_groups(
        self, a: DynamicLedger, f: FeatureFrame, score: np.ndarray, rank: np.ndarray, now: int
    ) -> bool:
        found = False
        for state in a.groups.values():
            if state["active_at"] is None or not any(
                k in a.lots and a.lots[k].quantity for k in state["keys"]
            ):
                continue
            reasons = observe(state, f, score, rank, now)
            if state["max_decision"] is not None and now >= state["max_decision"]:
                reasons = (*reasons, "MAX_HOLD")
            if reasons:
                state["triggers"] = tuple(dict.fromkeys((*state["triggers"], *reasons)))
                if state["reason"] is None:
                    state["reason"] = reasons[0]
                    state["exit_score"] = state.get("last_aligned")
                    state["decision"] = now
                found = True
        return found

    def tick_day(self, day: RawDay) -> None:
        frames = self.cache.frames(day.date)
        if not frames:
            raise ValueError("SHARED_FEATURE_DAY_MISSING")
        self.current_refs = frames[0].values
        self.fit_beta(frames[0].values["previous_close"])
        frame_at = {f.decision: f for f in frames}
        self.risk_cache.clear()
        self.before_day(day)
        count = len(self.dynamic_accounts)
        screen = DynamicRiskScreen(count)
        pending = set()
        special = set()
        for n, a in enumerate(self.dynamic_accounts):
            a.source_pointer = day.source_hash
            screen.update(n, a, self.legacy)
            if a.pending:
                pending.add(n)
            if n in self.special:
                special.add(n)
        exposure, exposure_fraction, idle_fraction = (np.zeros(count) for _ in range(3))
        for i, start0 in enumerate(day.starts):
            start = int(start0)
            self.integrate_gap(start)
            before = self.integrals.copy()
            valid = day.valid[i]
            pricing = np.where(valid, day.opens[i], self.last_prices)
            self.integrals += np.rint(pricing * 1_000_000).astype(np.int64) * 60
            self.cursor = start + 1
            self.last_prices = np.where(valid, day.closes[i], self.last_prices)
            self.known_closes = np.where(valid, day.closes[i], self.known_closes)
            self.known_marks = np.where(valid, start + 1, self.known_marks)
            self.known_volumes = np.where(valid, day.volumes[i], self.known_volumes)
            now = start + 3
            for n in sorted(pending):
                if self.settle_pending(n, day, i, now, start, before):
                    a = self.dynamic_accounts[n]
                    self.after_settlement(a)
                    screen.update(n, a, self.legacy)
                    self.risk_cache.pop(n, None)
                    if not a.pending:
                        pending.discard(n)
            for n in sorted(special):
                state = self.special[n]
                if state.whole_settled and state.cil_reference is not None:
                    special.discard(n)
                else:
                    self.special_tick(n, day.ogn.get(start), start, now)
                    screen.update(n, self.dynamic_accounts[n], self.legacy)
                    self.risk_cache.pop(n, None)
            breach, ambiguous, nav, filled = screen.status(
                self.known_closes, self.integrals.astype(float), self.borrow_rates
            )
            for k in np.flatnonzero(ambiguous):
                n = int(k)
                breach[n] = self.risk_status(n) == "RISK_BREACH" if self.legacy else True
            exposure += filled
            exposure_fraction += np.divide(filled, nav, out=np.zeros(count), where=nav > 0)
            idle_fraction += np.divide(screen.available, nav, out=np.zeros(count), where=nav > 0)
            frame = frame_at.get(now)
            intents = {}
            relevant = set(np.flatnonzero(breach | (screen.next_due <= now)).tolist())
            if frame is not None:
                entries = {s: evaluate(s, frame) for s in IDS}
                updates = {
                    s: scores(s, frame)
                    for s in IDS
                    if not self.legacy and monitored(s, frame, len(day.starts) == 390)
                }
                allows = (
                    {
                        prefix: self.holding.admits(frame, prefix == "M", self.last)
                        for prefix in ("M", "R")
                    }
                    if not self.legacy
                    else {}
                )
                for n, a in enumerate(self.dynamic_accounts):
                    sid = self.dynamic_cases[a.arm].strategy
                    if sid in updates and self.observe_groups(a, frame, *updates[sid], now):
                        relevant.add(n)
                    d = entries[sid]
                    if d.scheduled:
                        add(a.totals, candidate_intents=len(d.intents), opportunities=20)
                    if d.intents and (self.legacy or allows[sid[0]]):
                        intents[n] = d.intents
                        relevant.add(n)
                    elif d.intents:
                        a.reject("V3_MAXIMUM_HOLD_CALENDAR_CUTOFF", len(d.intents))
            for n in sorted(relevant):
                self.decide(n, day, now, frame, intents.get(n, ()))
                a = self.dynamic_accounts[n]
                screen.update(n, a, self.legacy)
                self.risk_cache.pop(n, None)
                if a.pending:
                    pending.add(n)
        end = int(day.starts[-1]) + 1
        self.last_market_end = end
        for n, a in enumerate(self.dynamic_accounts):
            self.close_day(
                a,
                end,
                day.date,
                float(exposure[n]),
                float(exposure_fraction[n]),
                float(idle_fraction[n]),
                len(day.starts),
            )
        alive = {k for a in self.dynamic_accounts for k in a.lots}
        self.paired_lots = {k: v for k, v in self.paired_lots.items() if k in alive}
        self.days_completed += 1
        self.last_completed = day.date

    def run(self, stop_after: int | None = None) -> dict:
        from .state import checkpoint

        start = time.monotonic()
        year_ends = {
            max(d for d in self.cache.by_date if d.startswith(year))
            for year in ("2021", "2022", "2023", "2024")
        }
        for day in self.market.days():
            if self.last_completed is not None and day.date <= self.last_completed:
                continue
            self.tick_day(day)
            if self.days_completed % 50 == 0:
                print(
                    "V3 sessions",
                    self.days_completed,
                    "elapsed",
                    round(time.monotonic() - start, 1),
                    "held accounts",
                    len(self.account_holds),
                    flush=True,
                )
            stopping = stop_after is not None and self.days_completed >= stop_after
            if self.checkpoint_dir and (stopping or day.date in year_ends or day.date == self.last):
                checkpoint(self.checkpoint_dir / (day.date + ".json.gz"), self)
            if stopping:
                break
        return {
            "sessions": self.days_completed,
            "last_session": self.last_completed,
            "elapsed": time.monotonic() - start,
        }
