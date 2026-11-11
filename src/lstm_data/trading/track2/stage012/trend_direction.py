"""Session-locked five-session sign. Missing prior 15:30 abstains (stale limit zero)."""
from datetime import datetime
import math
from zoneinfo import ZoneInfo
from .contracts import Observation, TrendSignal


def trend(prior_sessions: tuple[str, ...], references: dict[str, tuple[float, Observation]],
          first_decision: datetime, basis: str) -> TrendSignal:
    """Ascending completed session dates: compare prior[-1] against prior[-6]."""
    if tuple(sorted(set(prior_sessions))) != prior_sessions or len(prior_sessions) < 6:
        return TrendSignal(0, 0, (), 'MISSING_SIX_PRIOR_SESSIONS')
    if prior_sessions[-1] >= str(first_decision.astimezone(ZoneInfo('America/New_York')).date()):
        return TrendSignal(0, 0, (), 'SESSIONS_NOT_COMPLETED')
    keys = (prior_sessions[-6], prior_sessions[-1])
    if any(k not in references for k in keys):
        return TrendSignal(0, 0, (), 'MISSING_1530_REFERENCE_NO_STALE_FALLBACK')
    old, new = (references[k] for k in keys)
    for key, (price, obs) in zip(keys, (old, new)):
        if not math.isfinite(price) or price <= 0 or obs.available_at > first_decision or obs.price_basis != basis:
            return TrendSignal(0, 0, (), 'UNAVAILABLE_OR_UNIT_MISMATCH')
        local = obs.event_time.astimezone(ZoneInfo('America/New_York'))
        if local.strftime('%H:%M') != '15:30' or str(local.date()) != key:
            return TrendSignal(0, 0, (), 'NOT_GENUINE_1530_REFERENCE')
    alpha = math.log(new[0] / old[0])
    return TrendSignal(alpha, (alpha > 0) - (alpha < 0), (old[1], new[1]), 'OK')
