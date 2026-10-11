"""Audit-only causal as-of comparisons; no final feature join is chosen."""

from __future__ import annotations

import pandas as pd

from .validation import normalize, parse_utc, require_valid


def _optional_clock(frame: pd.DataFrame, name: str) -> pd.Series:
    """Parse supplied aware clocks, preserving missing metadata as unknown."""
    result = pd.Series(pd.NaT, index=frame.index, dtype="datetime64[ns, UTC]")
    if name in frame:
        present = frame[name].notna()
        result.loc[present] = parse_utc(frame.loc[present, name])
    return result


def asof_diagnostic(
    stocks: pd.DataFrame,
    course: pd.DataFrame,
    *,
    index_delay_minutes: int,
    stock_delay_minutes: int = 60,
    max_age_minutes: int = 90,
) -> tuple[pd.DataFrame, dict]:
    """Check period-end freshness separately from historical availability.

    Optional market columns: period_end, available_at, timing_basis. The basis
    must explicitly be 'documented' (a caller assertion, not certification) or
    'synthetic' (code tests only); other/missing bases fail closed. Missing actual
    availability may display a hypothetical label-plus-delay, never a usable
    match. No period end is inferred from a source label. Optional stock
    decision_cutoff takes precedence over legacy available_at/interval cutoffs.
    Every row uses its own cutoff. All results remain audit-only and non-ready;
    source/session compatibility and research approval are separate checks.
    """
    if index_delay_minutes < 0 or stock_delay_minutes < 0 or max_age_minutes < 0:
        raise ValueError("Availability delays and stale age must be nonnegative")
    stocks = normalize(stocks, stocks=True)
    course = normalize(course)
    require_valid(
        stocks[["symbol", "timestamp", "open", "high", "low", "close", "volume"]], stocks=True
    )
    require_valid(course)
    left = stocks[["symbol", "timestamp"]].rename(columns={"timestamp": "stock_timestamp"})
    cutoff_field = next((x for x in ("decision_cutoff", "available_at") if x in stocks), None)
    left["decision_cutoff"] = (
        parse_utc(stocks[cutoff_field])
        if cutoff_field
        else left.stock_timestamp + pd.Timedelta(minutes=stock_delay_minutes)
    )
    if (left.decision_cutoff < left.stock_timestamp).any():
        raise ValueError("Availability precedes source interval start")
    left["decision_time"] = left.decision_cutoff  # Existing callers' cutoff alias.
    left = left.sort_values("decision_cutoff")
    right = course[["timestamp"]].rename(columns={"timestamp": "index_timestamp"})
    right["period_end"] = _optional_clock(course, "period_end")
    right["available_at"] = _optional_clock(course, "available_at")
    right["timing_basis"] = course.get("timing_basis", "unverified")
    right["candidate_available_at"] = right.available_at.fillna(
        right.index_timestamp + pd.Timedelta(minutes=index_delay_minutes)
    )
    right["availability_basis"] = right.timing_basis.where(
        right.available_at.notna(), "hypothetical label plus delay"
    )
    # A recently published old period cannot displace a fresher known period.
    eligible = right[
        right.timing_basis.isin(["documented", "synthetic"])
        & right.period_end.notna()
        & right.available_at.notna()
        & (right.available_at >= right.period_end)
    ].sort_values(["candidate_available_at", "period_end", "index_timestamp"])
    eligible = eligible[eligible.period_end >= eligible.period_end.cummax()]
    joined = pd.merge_asof(
        left, eligible, left_on="decision_cutoff", right_on="candidate_available_at",
        direction="backward", allow_exact_matches=True,
    )
    # Display rejected/unknown candidates only for diagnosis, never as features.
    ordered = right.sort_values(["candidate_available_at", "index_timestamp"])
    rejected = pd.merge_asof(
        left, ordered, left_on="decision_cutoff", right_on="candidate_available_at",
        direction="backward", allow_exact_matches=True,
    )
    future = pd.merge_asof(
        left, ordered, left_on="decision_cutoff", right_on="candidate_available_at",
        direction="forward", allow_exact_matches=True,
    )
    rejected = rejected.where(rejected.index_timestamp.notna(), future)
    joined = joined.where(joined.index_timestamp.notna(), rejected)
    joined["source_timestamp_label"] = joined.index_timestamp
    joined["period_end_age_minutes"] = (
        joined.decision_cutoff - joined.period_end
    ).dt.total_seconds() / 60
    joined["availability_age_minutes"] = (
        joined.decision_cutoff - joined.available_at
    ).dt.total_seconds() / 60
    joined["availability_lag_minutes"] = (
        joined.available_at - joined.period_end
    ).dt.total_seconds() / 60
    joined["stale"] = joined.period_end_age_minutes > max_age_minutes
    joined["reason"] = "ACCEPTED_DIAGNOSTIC_ONLY"
    # Earlier assignments have lower priority than later fail-closed conditions.
    for mask, reason in (
        (joined.stale, "STALE_PERIOD_END"),
        (joined.available_at > joined.decision_cutoff, "FUTURE_AVAILABILITY"),
        (joined.period_end > joined.decision_cutoff, "FUTURE_PERIOD_END"),
        (joined.available_at < joined.period_end, "AVAILABILITY_BEFORE_PERIOD_END"),
        (~joined.timing_basis.isin(["documented", "synthetic"]), "UNVERIFIED_TIMING_METADATA"),
        (joined.available_at.isna(), "UNKNOWN_AVAILABLE_AT"),
        (joined.period_end.isna(), "UNKNOWN_PERIOD_END"),
        (joined.index_timestamp.isna(), "NO_CANDIDATE"),
    ):
        joined.loc[mask, "reason"] = reason
    joined["usable_candidate"] = joined.reason == "ACCEPTED_DIAGNOSTIC_ONLY"
    joined["timing_status"] = joined.reason.map(
        lambda reason: "PASS" if reason == "ACCEPTED_DIAGNOSTIC_ONLY"
        else "BLOCKED" if reason.startswith(("UNKNOWN", "UNVERIFIED", "NO_CANDIDATE"))
        else "INVALID"
    )
    joined["research_ready"] = False
    unmatched = joined.index_timestamp.isna() | (
        joined.candidate_available_at > joined.decision_cutoff
    )
    summary = {
        "audit_only": True,
        "research_ready": False,
        "index_delay_minutes": index_delay_minutes,
        "stock_delay_minutes": stock_delay_minutes,
        "stock_availability_policy": "explicit " + cutoff_field
        if cutoff_field else "start plus configured interval (hypothetical)",
        "max_age_minutes": max_age_minutes,
        "rows": len(joined),
        "unmatched": int(unmatched.sum()),
        "stale": int(joined.stale.sum()),
        "usable_candidate": int(joined.usable_candidate.sum()),
        "blocked": int((joined.timing_status == "BLOCKED").sum()),
        "reason_counts": {str(k): int(v) for k, v in joined.reason.value_counts().items()},
        "period_end_age_minutes_quantiles": {
            str(k): float(v)
            for k, v in joined.period_end_age_minutes.dropna().quantile([0, 0.5, 0.9, 1]).items()
        } if joined.period_end_age_minutes.notna().any() else {},
        "closure_policy": "Period-end age bounded; no overnight/weekend forward fill. "
        "All source bars remain diagnostic; inspect source/session QA separately.",
    }
    return joined, summary
