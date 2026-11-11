"""One-change policies; no outcome data or neural dependency enters this module."""

from decimal import Decimal
from math import isfinite

import numpy as np

from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v3_dynamic.policy import Case, observe

D = Decimal
ZERO = D(0)
TREATMENTS = {
    "M04": "EVENT2",
    "R01": "V20",
    "M01": "WEAK2",
    "M05": "EVENT2",
    "M03": "GAPCAP",
    "R07": "DAILY2",
}


def cases() -> tuple[Case, ...]:
    rows = []
    for s, treatment in TREATMENTS.items():
        for variant in ("CONTROL", treatment):
            h = D(1) if s == "R01" and variant == treatment else D(".85")
            rows.append(
                Case(
                    s,
                    variant,
                    h,
                    780 if s[0] == "M" else 10,
                    "max_scheduled_minutes" if s[0] == "M" else "max_sessions",
                    D(".1"),
                )
            )
        if s == "R01":
            rows.append(Case(s, "H100", D(1), 10, "max_sessions", D(".1")))
    return tuple(rows)


def stress_scale(
    nav: D, reserve: D, existing_stressed: D, existing_loss: D, proposed: tuple[tuple[D, D], ...]
) -> tuple[D, D, D]:
    """Largest feasible common t. Inputs are USD and prior daily log-return SD."""
    if any(not x.is_finite() for x in (nav, reserve, existing_stressed, existing_loss)):
        raise ValueError("NONFINITE_RESERVE")
    if min(reserve, existing_stressed, existing_loss) < 0:
        raise ValueError("NEGATIVE_EXISTING_RESERVE")
    stressed = ZERO
    loss = ZERO
    for u, v in proposed:
        if not u.is_finite() or not v.is_finite() or u < 0 or v < 0 or v > 1:
            raise ValueError("INVALID_STRESS_UNITS")
        s = v.exp()
        stressed += u * s
        loss += u * (s - 1)
    numerator = D(".2") * (nav - reserve - existing_loss) - existing_stressed
    denominator = stressed + D(".2") * loss
    t = min(D(1), max(ZERO, numerator / denominator)) if denominator > 0 else ZERO
    return t, numerator, denominator


def capped_trail(base: float | None, sigma_gap: float) -> float | None:
    if base is None or not isfinite(sigma_gap) or sigma_gap <= 0:
        return None
    return min(base, sigma_gap)


def confirm(state: dict, token: tuple, valid: bool, failed: bool) -> bool:
    """Distinct received observations only; a missing/recovered check resets streak."""
    if token == state.get("confirmation_token"):
        return state.get("confirmation_count", 0) >= 2
    state["confirmation_token"] = token
    state["confirmation_count"] = state.get("confirmation_count", 0) + 1 if valid and failed else 0
    return state["confirmation_count"] >= 2


def observe_changed(
    state: dict, f: FeatureFrame, score: np.ndarray, rank: np.ndarray, now: int
) -> tuple[str, ...]:
    """Only named event resolution is filtered; every other trigger is preserved."""
    f.require_causal()
    sid = state["sid"]
    # M01 already has the requested two-check rule in the frozen implementation.
    if sid == "M01":
        return observe(state, f, score, rank, now)
    token = (f.session, f.latest_observation_end, f.slot)
    if state.get("observed_token") == token:
        return state.get("observed_reasons", ())
    state["observed_token"] = token
    reasons = observe(state, f, score, rank, now)
    if sid in ("M04", "M05", "R07"):
        j = state["tickers"][0]
        valid = (
            f.decision == now
            and state["active_at"] is not None
            and f.latest_observation_end > state["active_at"]
            and isfinite(float(f.values["price"][j]))
            and f.values["price"][j] > 0
            and isfinite(float(f.values["raw_price"][j]))
            and f.values["raw_price"][j] > 0
        )
        daily_token = (f.session,) if sid == "R07" else token
        failed = "EVENT_RESOLVED" in reasons
        before = state.get("confirmation_count", 0)
        accepted = confirm(state, daily_token, bool(valid), failed)
        if failed and not accepted:
            state["deferred_checks"] = state.get("deferred_checks", 0) + 1
        if before and valid and not failed:
            state["recovered_checks"] = state.get("recovered_checks", 0) + 1
        if not valid:
            state["missing_checks"] = state.get("missing_checks", 0) + 1
        if not accepted:
            reasons = tuple(r for r in reasons if r != "EVENT_RESOLVED")
    state["observed_reasons"] = reasons
    return reasons
