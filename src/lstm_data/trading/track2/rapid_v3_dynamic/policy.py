"""Predeclared score adapters and calendar geometry for variable holds."""

from dataclasses import dataclass
from decimal import Decimal
from math import isfinite, log, sqrt

import numpy as np

from ..rapid_v1.shared_features import PAIRS, FeatureFrame, divide
from ..rapid_v1.strategies import IDS, SLOTS, DirectionIntent
from ..rapid_v2_diagnostics.variants import Case as FixedCase
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import minute

D = Decimal
REGIMES = {
    "CONSERVATIVE": (D(".85"), D(".10")),
    "STANDARD": (D(1), D(".10")),
    "HIGH_RISK": (D(1), D(".15")),
}
ADAPTERS = {
    "M01": "own standardized r60",
    "M02": "negative standardized r60, temporary shock normalization",
    "M03": "distance to frozen prior close in initial gap units",
    "M04": "progress relative to frozen entry-day open, no continued volume gate",
    "M05": "entry opening range boundary re-entry or break failure",
    "M06": "leave-one-out residual z and top-four hysteresis, minimum 12 peers",
    "M07": "past matured same-clock z at the entry slot, trail at other legal slots",
    "M08": "negative r60 z normalization without ongoing high-volume condition",
    "M09": "distance to entry-day opening reference, first received next-day open",
    "R01": "completed-session relative momentum and top-four hysteresis",
    "R02": "completed 20/60 MA separation",
    "R03": "frozen completed-channel breakout level",
    "R04": "negative completed five-day ranking and top-four hysteresis",
    "R05": "frozen past fitted beta, mean and spread sd, converged at abs(z)<=.5",
    "R06": "completed residual z, frozen past-only hedge for trailing path",
    "R07": "frozen channel breakout boundary, no continued compression gate",
    "R08": "completed overnight/intraday divergence",
    "R09": "completed volume anomaly rank with top-four hysteresis",
}
EVENT = {"M03", "M04", "M05", "M09", "R03", "R07"}
RANKED = {"M06", "R01", "R04", "R06", "R09"}
THRESHOLD = {"R02": 0.5, "R05": 2.0}
PRIORITY = ("SIGNAL_REVERSAL", "EVENT_RESOLVED", "SIGNAL_WEAKENING", "TRAILING_STOP", "MAX_HOLD")


@dataclass(frozen=True)
class Case(FixedCase):
    name_cap: Decimal


def case_axis() -> tuple[Case, ...]:
    return tuple(
        Case(
            s,
            regime,
            headroom,
            780 if s.startswith("M") else 10,
            "max_scheduled_minutes" if s.startswith("M") else "max_sessions",
            cap,
        )
        for s in IDS
        for regime, (headroom, cap) in REGIMES.items()
    )


class HoldingClock:
    def __init__(self, cal: ExecutionCalendar):
        self.cal = cal
        self.cumulative = np.r_[0, np.cumsum(cal.closes - cal.opens)]

    def session(self, at: int) -> int:
        return int(np.searchsorted(self.cal.closes, at, side="right"))

    def index(self, at: int) -> int:
        j = self.session(at)
        return int(self.cumulative[j]) + max(0, at - int(self.cal.opens[j]))

    def advance(self, at: int, minutes: int) -> int:
        ix = self.index(at) + minutes
        j = int(np.searchsorted(self.cumulative, ix, side="left")) - 1
        return int(self.cal.opens[j]) + ix - int(self.cumulative[j])

    def sessions(self, at: int, n: int) -> int:
        j = self.session(at)
        target = j + n
        return min(
            int(self.cal.closes[target]), int(self.cal.opens[target]) + at - int(self.cal.opens[j])
        )

    def maximum(self, at: int, micro: bool) -> int:
        return self.advance(at, 780) if micro else self.sessions(at, 10)

    def admits(self, f: FeatureFrame, micro: bool, last: str) -> bool:
        end = int(self.cal.closes[self.session(f.origin)])
        latest = min(end - 1, f.origin + 10)
        return self.cal.next(self.maximum(latest, micro) + 2) <= minute(last + "T23:59:00Z")


def monitored(s: str, f: FeatureFrame, full: bool) -> bool:
    if s.startswith("R"):
        return full and f.slot == 1
    return f.slot in SLOTS[s] or (s == "M09" and f.slot in (0, 1))


def scores(s: str, f: FeatureFrame) -> tuple[np.ndarray, np.ndarray]:
    f.require_causal()
    v = f.values
    keys = {
        "M01": ("r60_z", 1),
        "M02": ("r60_z", -1),
        "M08": ("r60_z", -1),
        "M06": ("residual_z", 1),
        "M07": ("same_clock_z", 1),
        "R02": ("trend", 1),
        "R06": ("residual5", -1),
        "R09": ("volume_rank", 1),
    }
    if s in keys:
        key, sign = keys[s]
        score = v[key] * sign
    elif s in ("R01", "R04"):
        score = (
            divide(v["j6minus1"], v["v60"] * sqrt(104))
            if s == "R01"
            else (-divide(v["j5"], v["v60"] * sqrt(5)))
        )
    elif s == "R08":
        a, b = divide(v["on10"], v["on_scale"]), divide(v["intra10"], v["intra_scale"])
        score = np.sign(a) * np.maximum(0, np.minimum(abs(a), -np.sign(a) * b))
    else:
        score = np.full(20, np.nan)
    rank = {"M06": "residual", "R01": "j6minus1", "R04": "j5"}.get(s)
    ordered = (v[rank] * (-1 if s == "R04" else 1)) if rank else score.copy()
    valid = np.isfinite(v["raw_price"]) & (v["raw_price"] > 0)
    if s == "M06":
        valid &= v["peer_count"] >= 12
    valid &= np.isfinite(score)
    if s in RANKED and np.sum(valid) < 12:
        valid[:] = False
    return np.where(valid, score, np.nan), np.where(valid, ordered, np.nan)


def initial(s: str, intent: DirectionIntent, f: FeatureFrame, beta: np.ndarray) -> dict:
    f.require_causal()
    v, tickers = f.values, intent.tickers
    j, side = tickers[0], intent.signs[0]
    scale = float(v["v20"][j])
    base = None
    event_scale = scale
    pair = None
    peers: tuple[int, ...] = ()
    fitted = None
    if s == "M03":
        base = float(v["previous_close"][j])
        event_scale = abs(float(v["gap"][j] / v["gap_z"][j]))
    elif s in ("M04", "M09"):
        base = float(v["price"][j] * np.exp(-v["intraday"][j]))
        event_scale = abs(float(v["first_hour" if s == "M04" else "intraday"][j])) / intent.strength
    elif s in ("M05", "R03", "R07"):
        stem = "or_" if s == "M05" else ""
        field = stem + ("high" if side > 0 else "low") if stem else ("h20" if side > 0 else "l20")
        base = float(v[field][j])
    elif s == "R05":
        pair = tuple(float(x) for x in f.pair_parameters[PAIRS.index(tickers)][:3])
        scale = sqrt(scale**2 + (pair[0] * float(v["v20"][tickers[1]])) ** 2)
    elif s == "R06":
        fitted = float(beta[j])
        peers = tuple(k for k in range(20) if k != j and np.isfinite(v["price"][k]))
        if not isfinite(fitted) or len(peers) < 11:
            scale = float("nan")
        else:
            scale = sqrt(scale**2 + (fitted * float(np.nanmedian(v["v20"]))) ** 2)
    return {
        "sid": s,
        "origin": intent.origin,
        "session": f.session,
        "tickers": tickers,
        "signs": intent.signs,
        "strength": intent.strength,
        "lineage": intent.lineage,
        "entry_slot": f.slot,
        "base": base,
        "event_scale": event_scale,
        "pair": pair,
        "trail_distance": 2 * scale if isfinite(scale) and scale > 0 else None,
        "fitted_beta": fitted,
        "peers": peers,
        "peak": None,
        "reversal": 0,
        "weak": 0,
        "active_at": None,
        "max_decision": None,
        "minimum_age": None,
        "reason": None,
        "triggers": (),
        "exit_score": None,
        "decision": None,
    }


def observe(
    state: dict,
    f: FeatureFrame,
    score: np.ndarray,
    ranked: np.ndarray,
    now: int,
) -> tuple[str, ...]:
    """Read only a received frame. Missing scores break the persistence streak."""
    f.require_causal()
    if (
        f.decision != now
        or state["active_at"] is None
        or (f.latest_observation_end <= state["active_at"])
    ):
        return ()
    s, j, side = state["sid"], state["tickers"][0], state["signs"][0]
    p = f.values["price"]
    val = float(score[j])
    trail = side * log(float(p[j])) if p[j] > 0 and isfinite(p[j]) else None
    resolved = False
    if s == "M09" and f.session != state["session"] and "overnight_segments" not in state:
        previous = float(f.values["previous_close"][j])
        intra = float(f.values["intraday"][j])
        if trail is not None and previous > 0 and isfinite(intra):
            opened = float(p[j]) * np.exp(-intra)
            state["overnight_segments"] = (
                log(previous / state["base"]),
                log(opened / previous),
                intra,
                f.session,
            )
    if s in EVENT:
        base, scale = state["base"], state["event_scale"]
        val = (
            log(float(p[j]) / base) / scale
            if trail is not None and base > 0 and scale > 0
            else (float("nan"))
        )
        if s in ("M03", "M09"):
            val = -val
            resolved = isfinite(val) and side * val <= 0.25 * state["strength"]
        else:
            boundary = 0.0 if s in ("M04", "M05") else -0.0005 / scale
            resolved = isfinite(val) and side * val <= boundary
    elif s == "R05":
        k = state["tickers"][1]
        beta, mu, sd = state["pair"]
        if trail is not None and p[k] > 0 and isfinite(p[k]):
            spread = log(float(p[j])) - beta * log(float(p[k]))
            trail = side * spread
            val = -(spread - mu) / sd
            resolved = abs(val) <= 0.5
        else:
            val, trail = float("nan"), None
    elif s == "R06":
        peers = p[list(state["peers"])]
        b = state["fitted_beta"]
        if trail is None or not len(peers) or not np.all(np.isfinite(peers) & (peers > 0)):
            trail = None
        elif b is not None and isfinite(b):
            trail -= side * b * float(np.log(peers).mean())
        else:
            trail = None
    elif s == "M07" and f.slot != state["entry_slot"]:
        val = float("nan")  # Trail still observes legal received prices.
    aligned = side * val
    reverse, weak = False, False
    if isfinite(aligned):
        threshold = THRESHOLD.get(s, 1.0)
        reverse = aligned <= -max(1.0, threshold)
        weak = aligned <= 0.5 * state["strength"] and aligned < threshold
        if s in RANKED and isfinite(ranked[j]):
            rank = float(ranked[j]) * side
            reverse &= int(np.sum(ranked * side < rank)) < 4
            weak &= int(np.sum(ranked * side > rank)) >= 4
        state["last_aligned"] = aligned
    if s != "M07" or f.slot == state["entry_slot"]:
        state["reversal"] = state["reversal"] + 1 if reverse else 0
        state["weak"] = state["weak"] + 1 if weak else 0
    confirmations = 2 if s.startswith("M") else 1
    triggers = set()
    if state["reversal"] >= confirmations:
        triggers.add("SIGNAL_REVERSAL")
    if resolved:
        triggers.add("EVENT_RESOLVED")
    if now >= state["minimum_age"] and state["weak"] >= confirmations:
        triggers.add("EVENT_RESOLVED" if s in ("M02", "M08") else "SIGNAL_WEAKENING")
    distance = state["trail_distance"]
    if trail is not None and distance is not None:
        state["peak"] = trail if state["peak"] is None else max(trail, state["peak"])
        if state["peak"] - trail >= distance:
            state["trail_level"] = state["peak"] - distance
            state["current_factor"] = float(f.values["factor"][j])
            triggers.add("TRAILING_STOP")
    return tuple(r for r in PRIORITY if r in triggers)
