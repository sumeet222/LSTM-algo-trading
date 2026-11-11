"""Shared-source 13-account replay; five changes and a faithful M01 identity control."""

import time
from pathlib import Path

import numpy as np

from ..rapid_v1.portfolio import FastAccount
from ..rapid_v1.shared_features import FeatureCache, FeatureFrame
from ..rapid_v1.strategies import DirectionIntent
from ..rapid_v3_dynamic.book import DynamicLedger
from ..rapid_v3_dynamic.engine import DynamicBatch
from .allocation import GuardedAllocation
from .book import DiagnosticLedger
from .policy import capped_trail, cases, observe_changed


class DiagnosticBatch(DynamicBatch, GuardedAllocation):
    def __init__(self, cache: FeatureCache, first: str, last: str):
        super().__init__(cache, first, last, cases())
        self.dynamic_accounts = [DiagnosticLedger(**vars(a)) for a in self.dynamic_accounts]
        self.fast_accounts = list(self.dynamic_accounts)
        self.accounts = list(self.dynamic_accounts)

    def allocate_budget(
        self, a: DynamicLedger, frame: FeatureFrame, intents: tuple[DirectionIntent, ...], now: int
    ):
        if a.arm == "R01_V20":
            if not isinstance(a, DiagnosticLedger):
                raise TypeError("DIAGNOSTIC_LEDGER_REQUIRED")
            return self.guarded_budget(a, frame, intents, now)
        return super().allocate_budget(a, frame, intents, now)

    def allocate(
        self, a: FastAccount, frame: FeatureFrame, intents: tuple[DirectionIntent, ...], now: int
    ):
        if a.arm == "M03_GAPCAP":
            ready = []
            for it in intents:
                j = it.tickers[0]
                gap, z = frame.values["gap"][j], frame.values["gap_z"][j]
                scale = abs(gap / z) if np.isfinite(z) and z != 0 else float("nan")
                if np.isfinite(scale) and scale > 0:
                    ready.append(it)
                else:
                    a.reject("TREATMENT_UNAVAILABLE_GAP_SCALE")
            intents = tuple(ready)
        requests = super().allocate(a, frame, intents, now)
        if isinstance(a, DynamicLedger) and a.arm == "M03_GAPCAP":
            for state in a.groups.values():
                if state["origin"] == frame.origin and not state.get("cap_fixed"):
                    state["original_trail"] = state["trail_distance"]
                    state["trail_distance"] = capped_trail(
                        state["trail_distance"], state["event_scale"]
                    )
                    if state["trail_distance"] is None:
                        raise ValueError("SUBMITTED_WITHOUT_GAP_SCALE")
                    state["cap_fixed"] = True
        return requests

    def observe_groups(
        self, a: DynamicLedger, f: FeatureFrame, score: np.ndarray, rank: np.ndarray, now: int
    ) -> bool:
        if a.regime in ("CONTROL", "H100") or a.arm in ("M03_GAPCAP", "R01_V20"):
            return super().observe_groups(a, f, score, rank, now)
        found = False
        for state in a.groups.values():
            if state["active_at"] is None or not any(
                k in a.lots and a.lots[k].quantity for k in state["keys"]
            ):
                continue
            reasons = observe_changed(state, f, score, rank, now)
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

    def run(self, stop_after: int | None = None) -> dict:
        from .state import checkpoint

        started = time.monotonic()
        for day in self.market.days():
            if self.last_completed is not None and day.date <= self.last_completed:
                continue
            self.tick_day(day)
            if self.days_completed % 100 == 0:
                print(
                    "FINAL_DIAG",
                    self.days_completed,
                    day.date,
                    round(time.monotonic() - started, 2),
                    "holds",
                    len(self.account_holds),
                    flush=True,
                )
            stopping = stop_after is not None and self.days_completed >= stop_after
            if self.checkpoint_dir and (
                stopping
                or day.date == self.last
                or (
                    day.date.startswith(("2021-12", "2022-12", "2023-12"))
                    and day.date == max(d for d in self.cache.by_date if d[:4] == day.date[:4])
                )
            ):
                checkpoint(Path(self.checkpoint_dir) / (day.date + ".json.gz"), self)
            if stopping:
                break
        return {
            "sessions": self.days_completed,
            "last_session": self.last_completed,
            "elapsed_seconds": time.monotonic() - started,
        }
