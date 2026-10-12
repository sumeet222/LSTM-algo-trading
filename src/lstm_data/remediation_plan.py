"""Calendar-derived, bounded source-remediation plan; no data or scientific activation."""

from __future__ import annotations

import pandas as pd

from .alpaca import request_params
from .clocks import execution_plan
from .config import fingerprint
from .labels import UNIVERSE
from .m2 import scheduled_window
from .stock_source import StockCalendar

PACKAGE = "TA-DATA-REMED-FT0-001"
OVERLAY_VERSION = "ALPACA_ONLY_EXTENDED_CANDIDATE_V1"


def dependency_calendar() -> dict:
    """Derive the earliest source context of the earliest lawful July input window."""
    cal = StockCalendar("2019-01-02", "2020-07-01")
    windows = {origin: scheduled_window(cal, "2020-07-01", origin) for origin in (1, 2)}
    first = windows[1][0]
    index = cal._positions[first.session, first.slot]
    previous = cal.days[: cal.days.index(first.session)]
    requirements = {
        "M4_endpoint_d126": previous[-126],
        "M4_endpoint_d21": previous[-21],
        "M3_endpoint_d6": previous[-6],
        "M3_endpoint_d1": previous[-1],
        "daily_RMS63_64_closes": previous[-64],
        "Q2_60_full_sessions": previous[-60],
        "Q2_5_full_sessions": previous[-5],
        "T1_20_prior_closes": previous[-20],
        "T2_21_prior_closes": previous[-21],
        "Q1_20_matching_slot_sessions": cal.matching[first.session, first.slot][0],
        "RMS60_H": cal.steps[index - 59].session,
        "RMS12_H": cal.steps[index - 11].session,
        "EMA_seed_plus360_good_updates": cal.steps[index - 360].session,
        "RSI_14_seed_changes_plus140_updates": cal.steps[index - 154].session,
        "LSTM48": first.session,
    }
    m2 = {}
    for origin in (1, 2):
        days = cal.previous_origins(first, origin)[-60:]
        assert len(days) == 60
        plans = [execution_plan(cal.clock(d), origin) for d in days]
        assert all(p.exit is not None and p.exit <= first.end for p in plans)
        requirements[f"M2_origin{origin}_60_matured_sessions"] = days[0]
        m2[str(origin)] = {
            "sessions": days,
            "oldest_plan": {
                "cutoff": str(plans[0].cutoff),
                "entry": str(plans[0].entry),
                "exit": str(plans[0].exit),
            },
            "last_exit": str(plans[-1].exit),
            "mature_by_first_step": True,
            "return_values_computed": False,
        }
    start = min(requirements.values())
    first_seed = next(i for i, s in enumerate(cal.steps) if s.session == start)
    updates = index - first_seed
    assert updates >= 360 and updates >= 154
    return {
        "package": PACKAGE,
        "calendar": "XNYS",
        "first_training_origin": "2020-07-01:1",
        "first_input": {
            "session": first.session,
            "slot": first.slot,
            "start": str(first.start),
            "end": str(first.end),
            "information_cutoff": str(first.information_cutoff),
        },
        "window_ends": {str(o): [str(s.end) for s in w] for o, w in windows.items()},
        "lower_bounds": requirements,
        "minimal_calendar_start": start,
        "feature_context_stop_exclusive": "2020-07-01",
        "source_sessions": len([d for d in cal.days if start <= d < "2020-07-01"]),
        "complete_hour_updates_at_first_input_if_no_gaps": updates,
        "extra_safety_sessions": 0,
        "safety_reason": (
            "M4 earliest boundary exceeds EMA360 and RSI154 requirements; "
            "actual gaps audited, not assumed repaired"
        ),
        "M2": m2,
        "floors_scalers": (
            "Warmup context only; fitting restricted to frozen training prefixes; none fitted here"
        ),
        "SPY": "Existing first-July warmup verified independently; no acquisition needed",
        "scientific_readiness": False,
    }


def gap_keys(qa: dict) -> dict[tuple[str, str], tuple[str, ...]]:
    """Retain every originally missing expected native key, including closing stubs."""
    found: dict[tuple[str, str], list[str]] = {}
    for row in qa["missing_windows"]:
        found.setdefault((row["symbol"], row["session"]), []).extend(row["missing_source_starts"])
    return {key: tuple(sorted(set(values))) for key, values in sorted(found.items())}


def source_request_manifest(cfg: dict, qa: dict) -> dict:
    """Freeze exact requests before transport; one shared warmup and narrow gap windows."""
    dependency = dependency_calendar()
    cal = StockCalendar(dependency["minimal_calendar_start"], "2023-07-01")
    requests = []

    def add(
        kind: str,
        symbols: list[str],
        start: pd.Timestamp,
        end: pd.Timestamp,
        *,
        timeframe: str = "30Min",
        max_pages: int = 1,
    ) -> None:
        config = dict(cfg, timeframe=timeframe)
        params = request_params(config, symbols, start.isoformat(), end.isoformat())
        requests.append(
            {
                "kind": kind,
                "provider": "ALPACA",
                "endpoint": "https://data.alpaca.markets/v2/stocks/bars",
                "params": params,
                "request_hash": fingerprint(params),
                "max_pages": max_pages,
                "maximum_attempts": 3 * max_pages,
                "available_at": None,
                "availability_basis": "UNKNOWN",
            }
        )

    start = pd.Timestamp(dependency["minimal_calendar_start"], tz="America/New_York")
    stop = pd.Timestamp("2020-07-01", tz="America/New_York")
    while start < stop:
        boundary = min(start + pd.offsets.MonthBegin(1), stop)
        add(
            "WARMUP",
            list(UNIVERSE),
            start.tz_convert("UTC"),
            boundary.tz_convert("UTC") - pd.Timedelta(nanoseconds=1),
            max_pages=3,
        )
        start = boundary
    clock = cal.clock("2020-07-01")
    assert clock.open is not None and clock.close is not None
    add("BASIS_CONTROL", list(UNIVERSE), clock.open, clock.close - pd.Timedelta(nanoseconds=1))
    clusters = gap_keys(qa)
    for (symbol, day), missing in clusters.items():
        clock = cal.clock(day)
        assert clock.open is not None and clock.close is not None
        add("GAP_RETRY", [symbol], clock.open, clock.close - pd.Timedelta(nanoseconds=1))
        # Only the first absent half hour, after exhausting native 30Min, as diagnostic.
        lower = pd.Timestamp(missing[0])
        add(
            "CONDITIONAL_MINUTE_DIAGNOSTIC",
            [symbol],
            lower,
            lower + pd.Timedelta(minutes=30) - pd.Timedelta(nanoseconds=1),
            timeframe="1Min",
        )
    envelope = sum(r["maximum_attempts"] for r in requests)
    assert envelope <= 180
    return {
        "package": PACKAGE,
        "version": 1,
        "status": "AUTHORIZED_ACQUISITION_ONLY_NOT_ACTIVATED",
        "requests": requests,
        "manifest_hash": fingerprint(requests),
        "limits": {
            "Alpaca_new_attempts": 180,
            "secondary_new_attempts": 80,
            "new_storage_bytes": 256 * 1024 * 1024,
            "same_page_lifetime_attempts": 3,
        },
        "conservative_Alpaca_attempt_envelope": envelope,
        "priority": ["WARMUP", "BASIS_CONTROL", "GAP_RETRY", "CONDITIONAL_MINUTE_DIAGNOSTIC"],
        "expected_native_RTH_warmup_bars": sum(
            int((clock.close - clock.open) / pd.Timedelta(minutes=30)) * len(UNIVERSE)
            for day, clock in cal._sessions.items()
            if dependency["minimal_calendar_start"] <= day < "2020-07-01"
            and clock.close is not None
            and clock.open is not None
        ),
        "gap_native_keys": sum(len(keys) for keys in clusters.values()),
        "basis_control": (
            "July1 same-key RTH OHLCV, no replacement; "
            "adjustment/entity/control mismatch blocks affected symbol additions"
        ),
        "secondary": (
            "NO_REPOSITORY_MASSIVE_OR_POLYGON_KEY; bounded access only; "
            "no outside credential search"
        ),
        "policy": (
            "Daily endpoints and EMA/RSI/rolling context need seven monthly warmup chunks. "
            "Empty bars remain absent; 1Min diagnostic only, never synthesized into30Min. "
            "No SPY calls."
        ),
    }
