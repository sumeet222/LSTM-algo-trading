"""Symbol-injected native candle QA and training-only candidate ordering."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from .calendar import schedule
from .fast_inventory import expand_missing, saved_session_audit
from .fast_screen import clusters, verified_frame


def liquidity60(frame: pd.DataFrame, ticker: str) -> dict:
    """Require exactly the 60 actual preformation daily keys; no volume fitting."""
    expected = tuple(
        pd.DatetimeIndex(schedule("2020-04-06", "2020-06-30").index).strftime("%Y-%m-%d")
    )
    selected = frame[frame.symbol == ticker].sort_values("timestamp")
    days = tuple(selected.timestamp.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d"))
    if len(expected) != 60 or days != expected or not (selected.source_timeframe == "1Day").all():
        raise ValueError("EXACT_GENUINE_FORMATION60_KEYS_REQUIRED")
    mean = float((selected.close * selected.volume).mean())
    return {
        "daily_sessions": len(days),
        "first_session": days[0],
        "last_session": days[-1],
        "mean_daily_dollar_volume": mean,
        "liquidity_pass": mean >= 50_000_000,
        "basis": "RETROSPECTIVE_VENDOR_RAW_CLOSE_TIMES_SHARE_VOLUME",
        "historical_publication": "UNVERIFIED",
    }


def quality_summary(ticker: str, days: list[dict], gaps: list[dict]) -> dict:
    """Summarize measured sessions, preserving missingness and exact denominators."""
    expected, observed = sum(d["expected"] for d in days), sum(d["actual"] for d in days)
    if not expected:
        raise ValueError("MEASURED_SESSION_POPULATION_REQUIRED")
    counts = Counter(g["run_size"] for g in gaps)
    return {
        "ticker": ticker,
        "expected": expected,
        "observed": observed,
        "missing": expected - observed,
        "coverage_percent": 100 * observed / expected,
        "sessions": len(days),
        "affected_sessions": sum(bool(d["missing"]) for d in days),
        "clusters": len(gaps),
        "runs1": counts[1],
        "runs2": counts[2],
        "runs3plus": sum(n for length, n in counts.items() if length >= 3),
        "longest_run": max(counts, default=0),
        "terminal_missing": sum(d["terminal_stub_missing"] for d in days),
        "native98_pass": observed / expected >= 0.98,
        "duplicates": 0,
        "malformed": 0,
        "off_grid_rth": 0,
    }


def audit_native(refs: list[dict], ticker: str, start: str, end: str) -> dict:
    """Check complete response intervals against one XNYS grid without price transforms.

    Unknown source intervals remain unmeasured, never manufactured absent keys.
    Validated extended-session records are counted separately from RTH gaps.
    """
    frames = {}
    for ref in refs:
        p = ref["params"]
        if (
            ticker not in p["symbols"].split(",")
            or p["timeframe"] != "30Min"
            or p["feed"] != "sip"
            or p["currency"] != "USD"
            or p["adjustment"] != "split"
            or p["asof"] != "2025-06-30"
        ):
            raise ValueError("EXACT_NATIVE_CANDIDATE_SOURCE_IDENTITY_REQUIRED")
        frame = verified_frame(ref)
        frames[ref["data"]] = frame[frame.symbol == ticker]
    days, gaps, unknown = [], [], []
    source_keys = set()
    for frame in frames.values():
        source_keys.update(frame.timestamp)
    for day_stamp, clock in schedule(start, end).iterrows():
        if not isinstance(day_stamp, pd.Timestamp):
            raise ValueError("EXACT_EXCHANGE_SESSION_REQUIRED")
        day = day_stamp.strftime("%Y-%m-%d")
        matches = [
            r
            for r in refs
            if pd.Timestamp(r["params"]["start"]) <= clock.open
            and pd.Timestamp(r["params"]["end"]) >= clock.close - pd.Timedelta(nanoseconds=1)
        ]
        if len(matches) > 1:
            raise ValueError("OVERLAPPING_RESPONSE_INTERVALS_REQUIRED_RECONCILIATION")
        if not matches:
            unknown.append({"ticker": ticker, "session_et": day, "status": "NOT_MEASURED"})
            continue
        ref = matches[0]
        frame = frames[ref["data"]]
        selected = frame[(frame.timestamp >= clock.open) & (frame.timestamp < clock.close)]
        row = saved_session_audit(selected, ticker, day, clock.open, clock.close)
        row.update(
            source=ref["data"],
            manifest=ref["manifest"],
            source_sha256=ref["sha256"],
            manifest_sha256=ref["manifest_sha256"],
            period="PREHISTORY" if day < "2020-07-01" else "FIVE_YEAR",
        )
        days.append(row)
        gaps.extend(dict(g, period=row["period"]) for g in clusters(row, ref))
    missing = expand_missing(gaps)
    summary: dict = quality_summary(ticker, days, gaps) if days else {"ticker": ticker}
    summary.update(
        unmeasured_sessions=len(unknown),
        full_interval_verified=not unknown,
        out_of_audited_RTH_keys=len(source_keys) - sum(d["actual"] for d in days),
        scientific="HOLD",
        full_FT0_retention="NOT_MEASURED",
    )
    if len(missing) != sum(d["missing"] for d in days) or len(missing) != sum(
        g["run_size"] for g in gaps
    ):
        raise ValueError("EXACT_ABSENCE_CLUSTER_RECONCILIATION_REQUIRED")
    return dict(summary=summary, days=days, clusters=gaps, missing=missing, unknown=unknown)


def rank_candidates(rows: list[dict], *, fixed_sectors: tuple[str, ...]) -> list[dict]:
    """Rank exclusively from the frozen five training dates and formation evidence."""
    for row in rows:
        if row["sector"] in fixed_sectors:
            raise ValueError("DISTINCT_FIFTH_SECTOR_REQUIRED")
        if any("confirmation" in key.lower() or "development" in key.lower() for key in row):
            raise ValueError("TRAINING_ONLY_SELECTION_REQUIRED")
    qualified = [
        r
        for r in rows
        if r["historical_eligibility_qualified"]
        and r["liquidity_pass"]
        and r["source_complete"]
        and r["terminal_missing"] == 0
        and r["longest_run"] <= 2
    ]
    return sorted(
        qualified,
        key=lambda r: (
            r["missing"] != 0,
            r["terminal_missing"] != 0,
            r["longest_run"] > 2,
            r["missing"],
            r["priority"],
        ),
    )
