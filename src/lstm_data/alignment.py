"""Audit-only causal as-of comparisons; no final feature join is chosen."""

from __future__ import annotations

import pandas as pd

from .validation import normalize, parse_utc, require_valid


def asof_diagnostic(
    stocks: pd.DataFrame,
    course: pd.DataFrame,
    *,
    index_delay_minutes: int,
    stock_delay_minutes: int = 60,
    max_age_minutes: int = 90,
) -> tuple[pd.DataFrame, dict]:
    """Compare candidate availability times with strictly backward, age-bounded matches.

    Delays are hypotheses, not timestamp-semantic approval. A native stock hour may
    cross a market closure; callers must inspect stock QA before interpreting it.
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
    left["decision_time"] = (
        parse_utc(stocks.available_at)
        if "available_at" in stocks
        else left.stock_timestamp + pd.Timedelta(minutes=stock_delay_minutes)
    )
    if (left.decision_time < left.stock_timestamp).any():
        raise ValueError("Availability precedes source interval start")
    right = course[["timestamp"]].rename(columns={"timestamp": "index_timestamp"})
    right["candidate_available_at"] = right.index_timestamp + pd.Timedelta(
        minutes=index_delay_minutes
    )
    joined = pd.merge_asof(
        left.sort_values("decision_time"),
        right.sort_values("candidate_available_at"),
        left_on="decision_time",
        right_on="candidate_available_at",
        direction="backward",
        allow_exact_matches=True,
    )
    joined["age_minutes"] = (
        joined.decision_time - joined.candidate_available_at
    ).dt.total_seconds() / 60
    joined["stale"] = joined.age_minutes > max_age_minutes
    joined["usable_candidate"] = joined.index_timestamp.notna() & ~joined.stale
    valid = joined.candidate_available_at.notna()
    if (joined.loc[valid, "candidate_available_at"] > joined.loc[valid, "decision_time"]).any():
        raise AssertionError("Future availability row in backward diagnostic")
    summary = {
        "audit_only": True,
        "index_delay_minutes": index_delay_minutes,
        "stock_delay_minutes": stock_delay_minutes,
        "stock_availability_policy": "explicit available_at"
        if "available_at" in stocks
        else "start plus configured interval",
        "max_age_minutes": max_age_minutes,
        "rows": len(joined),
        "unmatched": int(joined.index_timestamp.isna().sum()),
        "stale": int(joined.stale.sum()),
        "usable_candidate": int(joined.usable_candidate.sum()),
        "age_minutes_quantiles": {
            str(k): float(v)
            for k, v in joined.age_minutes.dropna().quantile([0, 0.5, 0.9, 1]).items()
        }
        if joined.age_minutes.notna().any()
        else {},
        "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. "
        "All source bars remain diagnostic; inspect RTH QA before interpretation.",
    }
    return joined, summary
