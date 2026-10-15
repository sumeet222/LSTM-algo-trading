"""Canonical conditional-study components, price-only proxy outcomes and mature M2.

No model inputs are issued as forecasts here. Future outcomes are held in a
separate table and never decide contemporaneous feature/entry availability.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .clocks import execution_plan
from .config import fingerprint
from .m2 import return_moments, scheduled_window
from .pretraining_policy import CANDIDATE, PreparationAuthority
from .pretraining_source import BARRIER, ConditionalHistory
from .stock_features import Components, FeatureCalculator, covered
from .stock_source import StockCalendar, StockDaily


@dataclass(frozen=True)
class ProxyPanel:
    session: str
    origin: int
    cutoff: pd.Timestamp
    issuance: pd.Timestamp
    entry_event: pd.Timestamp
    exit_event: pd.Timestamp
    entry_prices: tuple[float | None, ...]
    exit_prices: tuple[float | None, ...]
    entry_valid: tuple[bool, ...]
    outcome_valid: tuple[bool, ...]
    returns: tuple[float | None, ...]
    reference_ids: tuple[tuple[str | None, str | None], ...]
    maturity: pd.Timestamp | None

    @property
    def label_valid(self) -> bool:
        return all(self.outcome_valid)

    @property
    def median_mad(self) -> tuple[float, float] | None:
        if not self.label_valid:
            return None
        return target_moments(tuple(x for x in self.returns if x is not None))


def target_moments(values: tuple[float, ...]) -> tuple[float, float]:
    """Five genuine price-only returns; unscaled median absolute deviation."""
    if len(values) != 5 or not all(math.isfinite(x) for x in values):
        raise ValueError("FIVE_FINITE_PROXY_RETURNS_REQUIRED")
    data = np.asarray(values, dtype=float)
    center = float(np.median(data))
    return center, float(np.median(np.abs(data - center)))


def tg0(values: tuple[float, ...], epsilon: float) -> tuple[float, ...]:
    if not math.isfinite(epsilon) or epsilon < 1e-4:
        raise ValueError("TRAINING_TARGET_FLOOR_REQUIRED")
    center, mad = target_moments(values)
    return tuple((x - center) / (mad + epsilon) for x in values)


def proxy_panel(history: ConditionalHistory, day: str, origin: int) -> ProxyPanel:
    plan = execution_plan(history.calendar.clock(day), origin)
    if not plan.calendar_valid or any(x is None for x in
                                      (plan.cutoff, plan.issuance, plan.entry, plan.exit)):
        raise ValueError("ORDINARY_ELIGIBLE_PROXY_PLAN_REQUIRED")
    cutoff, issuance, entry, exit_event = plan.cutoff, plan.issuance, plan.entry, plan.exit
    if (not isinstance(cutoff, pd.Timestamp) or not isinstance(issuance, pd.Timestamp)
            or not isinstance(entry, pd.Timestamp) or not isinstance(exit_event, pd.Timestamp)):
        raise ValueError("FINITE_PROXY_EVENT_CLOCKS_REQUIRED")
    if cutoff >= BARRIER or exit_event >= BARRIER:
        raise ValueError("CONFIRMATION_TARGET_ACCESS_FORBIDDEN")
    ep, xp, ev, xv, returns, ids = [], [], [], [], [], []
    for symbol in CANDIDATE:
        a = history.bars.get((symbol, day, origin))
        b = history.bars.get((symbol, day, origin + 4))
        entry_ok = bool(a and a.end == cutoff
                        and history.source_status(a, cutoff) == "SOURCE_VALID")
        exit_ok = bool(b and b.end == cutoff + pd.Timedelta(hours=4)
                       and history.source_status(b, b.end) == "SOURCE_VALID")
        valid = entry_ok and exit_ok
        ep.append(a.close if a else None)
        xp.append(b.close if b else None)
        ev.append(entry_ok)
        xv.append(valid)
        returns.append(math.log(b.close / a.close) if valid and a and b else None)
        ids.append((a.row_id if a else None, b.row_id if b else None))
    # On this approved IDEAL clock each exit close precedes the event by 180s.
    # Maturity still waits for the actual scheduled event, not its older proxy.
    return ProxyPanel(day, origin, cutoff, issuance, entry, exit_event,
                      tuple(ep), tuple(xp), tuple(ev), tuple(xv), tuple(returns), tuple(ids),
                      exit_event if all(xv) else None)


@dataclass(frozen=True)
class M2Moments:
    symbol: str
    session: str
    origin: int
    mean20: float | None
    rms60: float | None
    valid20: int
    valid60: int
    max_missing_run: int
    maturity: pd.Timestamp | None
    reference_binding: str
    reason: str


def m2_moments(history: ConditionalHistory, panels: dict[tuple[str, int], ProxyPanel],
               symbol: str, day: str, origin: int) -> M2Moments:
    calendar = history.calendar
    step = calendar.steps[calendar._positions[day, 1]]
    previous = calendar.previous_origins(step, origin)[-60:]
    index = CANDIDATE.index(symbol)
    values: list[float | None] = []
    references = []
    maturities = []
    longest = run = 0
    for earlier in previous:
        panel = panels.get((earlier, origin))
        # Stock-specific outcome maturity, independent of five-name TG0 validity.
        valid = bool(panel and panel.outcome_valid[index] and panel.exit_event <= step.end)
        values.append(panel.returns[index] if valid and panel else None)
        references.append(panel.reference_ids[index] if valid and panel else None)
        if valid and panel:
            maturities.append(panel.exit_event)
        run = run + 1 if values[-1] is None else 0
        longest = max(longest, run)
    valid20, valid60 = sum(x is not None for x in values[-20:]), sum(x is not None for x in values)
    reason = "M2_HISTORY_VALID"
    mean = rms = None
    if len(previous) != 60:
        reason = "M2_SCHEDULED_HISTORY_INSUFFICIENT"
    elif not covered(tuple(values), 60, 57) or valid20 < 19:
        reason = "M2_MATURE_RETURN_COVERAGE_FAILED"
    else:
        mean, rms = return_moments(tuple(x for x in values[-20:] if x is not None),
                                   tuple(x for x in values if x is not None))
    return M2Moments(symbol, day, origin, mean, rms, valid20, valid60, longest,
                     max(maturities, default=None), fingerprint([previous, references]), reason)


@dataclass
class CanonicalHistory:
    """Persisted metadata/volumes for lazy review; no fabricated hourly raw bars."""

    calendar: StockCalendar
    daily: dict[tuple[str, str], StockDaily]
    authority: PreparationAuthority
    binding: str
    action_binding: str


@dataclass
class BaseTables:
    history: ConditionalHistory | CanonicalHistory
    components: dict[tuple[str, str, int], Components]
    panels: dict[tuple[str, int], ProxyPanel]
    m2: dict[tuple[str, str, int], M2Moments]
    origin_steps: dict[tuple[str, int], tuple[int, ...]]

    def potential(self, day: str, origin: int) -> tuple[bool, tuple[str, ...]]:
        """Input history only; no future target, exit mask or model permission."""
        positions = self.origin_steps.get((day, origin))
        if positions is None:
            return False, ("SCHEDULED_WINDOW_INSUFFICIENT",)
        reasons = set()
        for symbol in CANDIDATE:
            for pos in positions:
                step = self.history.calendar.steps[pos]
                row = self.components[symbol, step.session, step.slot]
                for feature, valid in row.coverage.items():
                    if feature != "M2" and not valid:
                        reasons.add("FT0_HISTORY_" + feature)
                stat = self.m2[symbol, step.session, origin]
                if stat.reason != "M2_HISTORY_VALID":
                    reasons.add(stat.reason)
                if stat.maturity is not None and stat.maturity > step.end:
                    reasons.add("M2_NOT_MATURE_AT_STEP")
        return not reasons, tuple(sorted(reasons))


def build_tables(history: ConditionalHistory) -> BaseTables:
    history.authority.ensure("FEATURE_TARGET_PREPARATION")
    calendar = history.calendar
    calculator = FeatureCalculator(history)
    components = {(symbol, step.session, step.slot): calculator.components(symbol, step)
                  for symbol in CANDIDATE for step in calendar.steps}
    panels = {}
    windows = {}
    for day in calendar.days:
        for origin in (1, 2):
            if not execution_plan(calendar.clock(day), origin).calendar_valid:
                continue
            panels[day, origin] = proxy_panel(history, day, origin)
            if day >= "2020-07-01":
                steps = scheduled_window(calendar, day, origin)
                windows[day, origin] = tuple(calendar._positions[s.session, s.slot] for s in steps)
    moments = {(symbol, day, origin): m2_moments(history, panels, symbol, day, origin)
               for symbol in CANDIDATE for day in calendar.days for origin in (1, 2)}
    return BaseTables(history, components, panels, moments, windows)
