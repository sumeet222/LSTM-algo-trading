"""One chronological price pass, shared signals, isolated V1 economic books."""

import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from ..rapid_v1.reporting import terminal_rows
from ..rapid_v1.scheduler import EntryBudget
from ..rapid_v1.shared_features import FeatureCache
from ..rapid_v1.sources import RawDay
from ..rapid_v1.strategies import IDS, evaluate
from ..stage35.final_backtest_v4.book import YEAR
from .allocation import AllocationEngine
from .book import ZERO, D, Ledger, add
from .variants import Case, Endpoints


class RiskScreen:
    """Vector version of V1's floating prefilter. Exact order gate is inherited."""

    def __init__(self, size: int):
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

    def update(self, n: int, a: Ledger) -> None:
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
            bool(np.any(a.quantity)) or any(lot.pending for lot in a.lots.values())
        )
        vintages: dict[int, np.ndarray] = {}
        next_due = int(np.iinfo(np.int64).max)
        for lot in a.lots.values():
            if lot.quantity:
                self.filled[n, lot.ticker] += float(abs(lot.quantity))
                next_due = min(next_due, lot.endpoint + 2)
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
            (nav, nav - 1e-6 - gross, 0.1 * nav - 1e-6 - name, 0.2 * nav - 1e-6 - vintage)
        )
        breach = self.held & ((nav <= 0) | np.any(margins[:, 1:] < 0, axis=1) | self.restricted)
        ambiguous = self.held & np.any(np.abs(margins) <= 1e-7, axis=1)
        return breach, ambiguous, nav, filled


class Batch(AllocationEngine):
    fast_accounts: list[Ledger]
    variant_registry: str

    def __init__(self, cache: FeatureCache, first: str, last: str, cases: tuple[Case, ...]):
        super().__init__(cache, first, last)
        initial = {a.arm: a.scenario for a in self.fast_accounts}
        self.cases = cases
        self.case_by_key = {case.key: case for case in cases}
        if len(self.case_by_key) != len(cases):
            raise ValueError("DUPLICATE_CASE")
        self.fast_accounts = [
            Ledger(c.key, c.mode, replace(initial[c.strategy], name=c.key)) for c in cases
        ]
        self.accounts = list(self.fast_accounts)
        self.scenarios = tuple(a.scenario for a in self.fast_accounts)
        self.budgets = {c.key: EntryBudget(c.mode) for c in cases}
        self.daily_rows = {c.key: [] for c in cases}
        self.endpoints = Endpoints(self.execution_calendar)
        self.borrow_rates = np.asarray([float(a.scenario.borrow) for a in self.fast_accounts])

    def rth_index(self, at: int) -> int:
        j = int(np.searchsorted(self.execution_calendar.closes, at, side="right"))
        return int(self.endpoints.cumulative[j]) + max(
            0, at - int(self.execution_calendar.opens[j])
        )

    def tick_day(self, day: RawDay) -> None:
        frames = self.cache.frames(day.date)
        if not frames:
            raise ValueError("SHARED_FEATURE_DAY_MISSING")
        self.current_refs = frames[0].values
        frame_at = {f.decision: f for f in frames}
        self.risk_cache.clear()
        self.before_day(day)
        count = len(self.fast_accounts)
        screen = RiskScreen(count)
        pending = set()
        active_special = set()
        for n, a in enumerate(self.fast_accounts):
            a.source_pointer = day.source_hash
            screen.update(n, a)
            if a.pending:
                pending.add(n)
            if n in self.special:
                active_special.add(n)
        exposure = np.zeros(count)
        exposure_fraction = np.zeros(count)
        idle_fraction = np.zeros(count)
        for i, start0 in enumerate(day.starts):
            start = int(start0)
            self.integrate_gap(start)
            before = self.integrals.copy()
            valid = day.valid[i]
            pricing = np.where(valid, day.opens[i], self.last_prices)
            ticks = np.rint(pricing * 1_000_000).astype(np.int64)
            self.integrals += ticks * 60
            self.cursor = start + 1
            self.last_prices = np.where(valid, day.closes[i], self.last_prices)
            self.known_closes = np.where(valid, day.closes[i], self.known_closes)
            self.known_marks = np.where(valid, start + 1, self.known_marks)
            self.known_volumes = np.where(valid, day.volumes[i], self.known_volumes)
            now = start + 3
            for n in sorted(pending):
                if self.settle_pending(n, day, i, now, start, before):
                    a = self.fast_accounts[n]
                    screen.update(n, a)
                    self.risk_cache.pop(n, None)
                    if not a.pending:
                        pending.discard(n)
            for n in sorted(active_special):
                state = self.special[n]
                if state.whole_settled and state.cil_reference is not None:
                    active_special.discard(n)
                    continue
                self.special_tick(n, day.ogn.get(start), start, now)
                screen.update(n, self.fast_accounts[n])
                self.risk_cache.pop(n, None)
            breach, ambiguous, nav, filled = screen.status(
                self.known_closes,
                self.integrals.astype(float),
                self.borrow_rates,
            )
            for n in np.flatnonzero(ambiguous):
                breach[n] = self.risk_status(int(n)) == "RISK_BREACH"
            exposure += filled
            np.add(
                exposure_fraction,
                np.divide(filled, nav, out=np.zeros(count), where=nav > 0),
                out=exposure_fraction,
            )
            np.add(
                idle_fraction,
                np.divide(screen.available, nav, out=np.zeros(count), where=nav > 0),
                out=idle_fraction,
            )
            frame = frame_at.get(now)
            requests = {}
            if frame is not None:
                decisions = {s: evaluate(s, frame) for s in IDS}
                for n, case in enumerate(self.cases):
                    a = self.fast_accounts[n]
                    d = decisions[case.strategy]
                    if d.scheduled:
                        add(a.totals, candidate_intents=len(d.intents), opportunities=20)
                    intents, reason = self.endpoints.retime(frame, case, d.intents)
                    if reason:
                        a.reject(reason, len(d.intents))
                    if intents:
                        requests[n] = intents
            relevant = set(np.flatnonzero(breach | (screen.next_due <= now)).tolist()) | set(
                requests
            )
            for n in sorted(relevant):
                self.decide(n, day, now, frame, requests.get(n, ()))
                a = self.fast_accounts[n]
                screen.update(n, a)
                self.risk_cache.pop(n, None)
                if a.pending:
                    pending.add(n)
        end = int(day.starts[-1]) + 1
        self.last_market_end = end
        for n, a in enumerate(self.fast_accounts):
            self.close_day(
                a,
                end,
                day.date,
                float(exposure[n]),
                float(exposure_fraction[n]),
                float(idle_fraction[n]),
                len(day.starts),
            )
        alive = {k for a in self.fast_accounts for k in a.lots}
        self.paired_lots = {k: v for k, v in self.paired_lots.items() if k in alive}
        self.days_completed += 1
        self.last_completed = day.date

    def close_day(
        self,
        a: Ledger,
        end: int,
        date: str,
        exposure: float,
        fraction: float,
        idle: float,
        minutes: int,
    ) -> None:
        now = end + 2
        for _, o in list(a.pending.items()):
            if o.expiry is not None and o.expiry <= end - 1:
                self.expire(a, o, now)
        self.sync(a, now)
        a.accrue(self.integrals, now)
        a.accrue_funding(end)
        a.reconcile()
        nav = a.nav()
        stale = any(a.quantity[j] and now - a.marks_at[j] > 5 for j in range(20))
        complete = nav is not None and nav.is_finite() and nav > 0 and not stale and not a.risk_hold
        if not complete:
            self.account_holds.setdefault(a.arm, []).append(date + ":STALE_OR_UNPRICED_CLOSE")
        physical = sum((D(int(q)) * (a.prices[j] or ZERO) for j, q in enumerate(a.quantity)), ZERO)
        special = sum(a.special_values.values(), ZERO)
        rhs = a.cash + a.claim_total() + physical + special
        if nav is not None and abs(nav - rhs) > D("1e-8"):
            raise ValueError("DAILY_NAV_NOT_RECONCILED")
        self.daily_rows[a.arm].append(
            {
                "date": date,
                "nav": nav,
                "cash": a.cash,
                "restricted": a.restricted(),
                "claims": a.claim_total(),
                "physical_value": physical,
                "special": special,
                "virtual_gross": a.gross() + sum((abs(v) for v in a.special_values.values()), ZERO),
                "commission": a.commission,
                "friction": a.friction,
                "borrow": a.borrow_paid,
                "funding": a.funding_paid,
                "status": "OBSERVED" if complete else "HOLD",
                "gross_dollar_minutes": exposure,
                "gross_NAV_minutes": fraction,
                "spendable_cash_NAV_minutes": idle,
                "RTH_minutes": minutes,
            }
        )
        a.finish_session(end, date, self.rth_index)

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
                    "V2 sessions",
                    self.days_completed,
                    "elapsed",
                    round(time.monotonic() - start, 1),
                    "held accounts",
                    len(self.account_holds),
                    flush=True,
                )
            stopping = stop_after is not None and self.days_completed >= stop_after
            if self.checkpoint_dir and (stopping or day.date in year_ends or day.date == self.last):
                checkpoint(Path(self.checkpoint_dir) / (day.date + ".json.gz"), self)
            if stopping:
                break
        return {
            "sessions": self.days_completed,
            "last_session": self.last_completed,
            "elapsed": time.monotonic() - start,
        }

    def final_cohorts(self, a: Ledger) -> None:
        if a.lots and self.last_completed is not None:
            for row in terminal_rows(self, a.arm):
                a.aggregate_trade(row, self.last_completed, self.rth_index)
