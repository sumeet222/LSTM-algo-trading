"""The eighteen menu mechanisms. Functions receive no outcomes or model forecasts."""

from dataclasses import dataclass

import numpy as np

from .shared_features import PAIRS, FeatureFrame, divide

IDS = tuple(f"M{k:02d}" for k in range(1, 10)) + tuple(f"R{k:02d}" for k in range(1, 10))
SLOTS = {
    "M01": (1, 2, 3, 4, 5, 6),
    "M02": (1, 2, 3, 4, 5, 6),
    "M03": (0, 1),
    "M04": (1, 2, 3),
    "M05": (1, 2, 3, 4),
    "M06": (1, 2, 3, 4, 5, 6),
    "M07": (0, 1, 2, 3, 4, 5, 6),
    "M08": (1, 2, 3, 4, 5, 6),
    "M09": (5, 6),
    **{f"R{k:02d}": (5,) if k == 8 else (1,) for k in range(1, 10)},
}


@dataclass(frozen=True)
class DirectionIntent:
    strategy_id: str
    session: str
    origin: int
    decision: int
    endpoint: int
    tickers: tuple[int, ...]
    signs: tuple[int, ...]
    weights: tuple[float, ...]
    strength: float
    lineage: str


@dataclass(frozen=True)
class SignalDecision:
    intents: tuple[DirectionIntent, ...]
    reasons: tuple[str, ...]
    scheduled: bool


def mode(strategy_id: str) -> str:
    return "MICRO_PRO" if strategy_id.startswith("M") else "RETAIL_CONSERVATIVE"


def evaluate(strategy_id: str, f: FeatureFrame) -> SignalDecision:
    if strategy_id not in IDS:
        raise ValueError("UNREGISTERED_STRATEGY")
    f.require_causal()
    if f.slot not in SLOTS[strategy_id] or (strategy_id.startswith("R") and not f.weekly_scan):
        return SignalDecision((), tuple("NOT_SCHEDULED" for _ in range(20)), False)
    v = f.values
    reason = np.full(20, "BELOW_THRESHOLD", dtype=object)
    eligible = np.isfinite(v["raw_price"]) & (v["raw_price"] > 0)
    reason[~eligible] = "MISSING_RECEIVED_REFERENCE"
    sign = np.zeros(20, dtype=int)
    strength = np.full(20, np.nan)
    ranked = False
    rank_value = np.full(20, np.nan)
    if strategy_id in ("M01", "M02", "M08"):
        strength = np.abs(v["r60_z"])
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_SAME_SLOT_SCALE_OR_RETURN"
        selected = good & (strength >= 1)
        if strategy_id == "M08":
            reason[selected & ~np.isfinite(v["volume_z"])] = "MISSING_SAME_SLOT_VOLUME"
            selected &= np.isfinite(v["volume_z"]) & (v["volume_z"] >= 1.5)
        sign[selected] = np.sign(v["r60"][selected]).astype(int) * (
            1 if strategy_id == "M01" else -1
        )
    elif strategy_id == "M03":
        strength = np.abs(v["gap_z"])
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_GAP_OR_PAST_SCALE"
        pick = good & (strength >= 1)
        sign[pick] = -np.sign(v["gap"][pick]).astype(int)
    elif strategy_id == "M04":
        strength = np.minimum(np.abs(v["gap_z"]), np.abs(v["first_hour_z"]))
        good = eligible & np.isfinite(strength) & np.isfinite(v["cumulative_volume_ratio"])
        reason[eligible & ~good] = "MISSING_GAP_FIRST_HOUR_OR_VOLUME"
        pick = (
            good
            & (np.abs(v["gap_z"]) >= 1)
            & (v["cumulative_volume_ratio"] > 1)
            & (v["gap"] * v["first_hour"] > 0)
        )
        sign[pick] = np.sign(v["gap"][pick]).astype(int)
    elif strategy_id in ("M05", "R03", "R07"):
        high, low = (v["or_high"], v["or_low"]) if strategy_id == "M05" else (v["h20"], v["l20"])
        good = (
            eligible & np.isfinite(high) & np.isfinite(low) & np.isfinite(v["v20"]) & (v["v20"] > 0)
        )
        reason[eligible & ~good] = "MISSING_COMPLETED_RANGE_OR_SCALE"
        up = good & (v["price"] > high * 1.0005)
        down = good & (v["price"] < low * 0.9995)
        sign[up] = 1
        sign[down] = -1
        strength = np.where(
            up,
            divide(np.log(divide(v["price"], high)), v["v20"]),
            divide(np.log(divide(low, v["price"])), v["v20"]),
        )
        if strategy_id == "R07":
            reason[(sign != 0) & (v["compression"] != 1)] = "NO_PAST_VOLATILITY_CONTRACTION"
            sign[v["compression"] != 1] = 0
    elif strategy_id == "M06":
        strength = np.abs(v["residual_z"])
        rank_value = v["residual"]
        good = eligible & np.isfinite(strength) & (v["peer_count"] >= 12)
        reason[eligible & ~good] = "MISSING_RESIDUAL_SCALE_OR_PEERS"
        pick = good & (strength >= 1)
        sign[pick] = np.sign(rank_value[pick]).astype(int)
        ranked = True
    elif strategy_id == "M07":
        strength = np.abs(v["same_clock_z"])
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "INSUFFICIENT_PRIOR_SAME_CLOCK_SUPPORT"
        pick = good & (strength >= 1)
        sign[pick] = np.sign(v["same_clock_z"][pick]).astype(int)
    elif strategy_id == "M09":
        strength = np.abs(v["intraday_z"])
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_RECEIVED_INTRADAY_OR_PAST_SCALE"
        pick = good & (strength >= 1)
        sign[pick] = -np.sign(v["intraday"][pick]).astype(int)
    elif strategy_id in ("R01", "R04", "R06", "R09"):
        key = {"R01": "j6minus1", "R04": "j5", "R06": "residual5", "R09": "volume_rank"}[
            strategy_id
        ]
        rank_value = v[key]
        ranked = True
        if strategy_id == "R01":
            strength = np.abs(divide(rank_value, v["v60"] * np.sqrt(104)))
        elif strategy_id == "R04":
            strength = np.abs(divide(rank_value, v["v60"] * np.sqrt(5)))
        else:
            strength = np.abs(rank_value)
        good = eligible & np.isfinite(rank_value) & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_COMPLETED_DAILY_REFERENCE"
        threshold = 1 if strategy_id in ("R06", "R09") else 0
        pick = good & (strength >= threshold)
        sign[pick] = np.sign(rank_value[pick]).astype(int) * (
            -1 if strategy_id in ("R04", "R06") else 1
        )
    elif strategy_id == "R02":
        strength = np.abs(v["trend"])
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_PAST_20_60_TREND"
        pick = good & (strength >= 0.5)
        sign[pick] = np.sign(v["trend"][pick]).astype(int)
    elif strategy_id == "R08":
        a = divide(v["on10"], v["on_scale"])
        b = divide(v["intra10"], v["intra_scale"])
        strength = np.minimum(np.abs(a), np.abs(b))
        good = eligible & np.isfinite(strength)
        reason[eligible & ~good] = "MISSING_PRIOR_OVERNIGHT_INTRADAY_COMPONENTS"
        sign[good & (a >= 1) & (b <= -1)] = 1
        sign[good & (a <= -1) & (b >= 1)] = -1
    elif strategy_id == "R05":
        intents = []
        reason[:] = "NOT_PRECOMMITTED_PAIR_MEMBER"
        for n, (i, j) in enumerate(PAIRS):
            reason[[i, j]] = "PAIR_STABILITY_OR_SOURCE_ABSTENTION"
            beta, mu, sd, r2 = f.pair_parameters[n]
            if not (eligible[i] and eligible[j] and np.isfinite([beta, mu, sd, r2]).all()):
                continue
            z = (np.log(v["price"][i]) - beta * np.log(v["price"][j]) - mu) / sd
            reason[[i, j]] = "BELOW_PAIR_Z_THRESHOLD"
            if abs(z) < 2:
                continue
            s = -1 if z > 0 else 1
            intents.append(
                DirectionIntent(
                    strategy_id,
                    f.session,
                    f.origin,
                    f.decision,
                    f.endpoint,
                    (i, j),
                    (s, -s),
                    (1.0, float(beta)),
                    float(abs(z)),
                    f.lineage,
                )
            )
            reason[[i, j]] = "CANDIDATE_PAIR"
        return SignalDecision(
            tuple(sorted(intents, key=lambda x: (-x.strength, x.tickers))), tuple(reason), True
        )
    if ranked:
        source_count = int(np.sum(eligible & np.isfinite(rank_value) & np.isfinite(strength)))
        if source_count < 12:
            sign[:] = 0
            reason[eligible] = "INSUFFICIENT_CURRENT_PEERS"
        else:
            # Select tails by the menu's signed raw score (standardized R06/R09),
            # not by any later outcome. Strength only prioritizes live orders.
            positive = [i for i in range(20) if sign[i] and rank_value[i] > 0]
            negative = [i for i in range(20) if sign[i] and rank_value[i] < 0]
            keep = set(
                sorted(positive, key=lambda i: (-rank_value[i], i))[:2]
                + sorted(negative, key=lambda i: (rank_value[i], i))[:2]
            )
            for i in range(20):
                if sign[i] and i not in keep:
                    sign[i] = 0
                    reason[i] = "OUTSIDE_CROSS_SECTIONAL_TAIL"
    intents = []
    for i in range(20):
        if sign[i]:
            reason[i] = "CANDIDATE"
            intents.append(
                DirectionIntent(
                    strategy_id,
                    f.session,
                    f.origin,
                    f.decision,
                    f.endpoint,
                    (i,),
                    (int(sign[i]),),
                    (1.0,),
                    float(strength[i]),
                    f.lineage,
                )
            )
    return SignalDecision(
        tuple(sorted(intents, key=lambda x: (-x.strength, x.tickers))), tuple(reason), True
    )
