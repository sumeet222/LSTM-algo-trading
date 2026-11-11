"""Distinct fixed-T480 and native dynamic engines; shared source observations."""

import numpy as np

from ..rapid_final_diag.policy import observe_changed
from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v2_diagnostics.book import Ledger
from ..rapid_v2_diagnostics.engine import Batch
from ..rapid_v2_diagnostics.variants import Case as FixedCase
from ..rapid_v3_dynamic.book import DynamicLedger as OriginalLedger
from ..rapid_v3_dynamic.engine import DynamicBatch
from ..rapid_v3_dynamic.policy import Case
from .allocation import allocate
from .common import POLICIES, ROOT, load
from .ledger import DynamicLedger, FixedLedger
from .risk_inputs import ARMS, RiskInputs


def axis(selected: list[str], population: str, equal_only: bool = False):
    fixed = []
    dynamic = []
    mapping = {}
    for fid in selected:
        p = POLICIES[fid]
        for arm in ARMS:
            if equal_only and arm != "EQUAL":
                continue
            if population == "ATTAINABLE" and arm == "EQUAL":
                continue
            variant = fid + "_" + population + "_" + arm
            args = (
                p["strategy"],
                variant,
                __import__("decimal").Decimal(p["headroom"]),
                p["horizon"],
                p["unit"],
            )
            if p["engine"] == "V2_FIXED":
                c = FixedCase(*args)
                fixed.append(c)
            else:
                c = Case(*args, __import__("decimal").Decimal(".1"))
                dynamic.append(c)
            mapping[c.key] = (fid, population, arm)
    return tuple(fixed), tuple(dynamic), mapping


class FixedEngine(Batch):
    def __init__(self, cache, first, last, cases, risk: RiskInputs, mapping: dict):
        super().__init__(cache, first, last, cases)
        self.fast_accounts = [FixedLedger(**vars(a)) for a in self.fast_accounts]
        self.accounts = list(self.fast_accounts)
        self.risk = risk
        self.mapping = mapping

    def allocate(self, a, frame, intents, now):
        if not isinstance(a, Ledger):
            raise TypeError("OVERLAY_LEDGER_REQUIRED")
        fid, pop, arm = self.mapping[a.arm]
        return allocate(self, a, frame, intents, now, self.risk, arm, pop, fid == "F2")


class DynamicEngine(DynamicBatch):
    def __init__(self, cache, first, last, cases, risk: RiskInputs, mapping: dict):
        super().__init__(cache, first, last, cases)
        self.dynamic_accounts = [DynamicLedger(**vars(a)) for a in self.dynamic_accounts]
        self.fast_accounts = list(self.dynamic_accounts)
        self.accounts = list(self.dynamic_accounts)
        self.risk = risk
        self.mapping = mapping

    def allocate_budget(self, a, frame, intents, now):
        if not isinstance(a, Ledger):
            raise TypeError("OVERLAY_LEDGER_REQUIRED")
        fid, pop, arm = self.mapping[a.arm]
        return allocate(self, a, frame, intents, now, self.risk, arm, pop, fid == "F2")

    def observe_groups(
        self, a: OriginalLedger, f: FeatureFrame, score: np.ndarray, rank: np.ndarray, now: int
    ) -> bool:
        fid, *_ = self.mapping[a.arm]
        if fid not in ("F4", "F5"):
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


def create(
    cache, risk: RiskInputs, population: str, first: str, last: str, equal_only: bool = False
):
    selected = load(ROOT / "SELECTION_RECEIPT.json")["selected"]
    fixed, dynamic, mapping = axis(selected, population, equal_only)
    return (
        FixedEngine(cache, first, last, fixed, risk, mapping),
        DynamicEngine(cache, first, last, dynamic, risk, mapping),
        mapping,
    )
