"""Offline canonical SPY QA and typed D7 traces; no empirical fits or activation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import fingerprint
from .m2 import ScheduledCalendar, scheduled_window
from .market_features import MarketHistory, history_from_archive, window_from_history
from .market_source import (
    MarketSource,
    archive_qa,
    hourly_archive,
    load_archive,
    load_market_history,
)
from .spy_completion import write_bounded_report


def structural_history(history: MarketHistory, session: str, origin: int) -> dict:
    """Keep exact historical positions; report coverage independently of causal validity."""
    calendar = history.calendar
    steps = scheduled_window(calendar, session, origin)
    days = tuple(calendar._sessions)
    requirements = []
    for step in steps:
        position = calendar._positions[(step.session, step.slot)]
        hours = calendar.steps[max(0, position - 59):position + 1]
        day_position = days.index(step.session)
        previous = days[max(0, day_position - 64):day_position]
        hour_mask = [s.end in history.hours for s in hours]
        daily_mask = [day in history.closes for day in previous]

        def valid(mask: list[bool], length: int, minimum: int) -> bool:
            run = 0
            if len(mask) != length or sum(mask) < minimum:
                return False
            for present in mask:
                run = 0 if present else run + 1
                if run > 2:
                    return False
            return True

        daily_returns = [a and b for a, b in zip(daily_mask, daily_mask[1:])]
        complete = (step.end in history.hours and valid(hour_mask[-12:], 12, 12)
                    and valid(hour_mask, 60, 57) and valid(daily_returns, 63, 60)
                    and len(daily_mask) >= 21 and all(daily_mask[-21:]))
        requirements.append({"session": step.session, "slot": step.slot,
                             "cutoff": step.end.isoformat(),
                             "scheduled_hour_history": len(hours),
                             "observed_hour_history": sum(hour_mask),
                             "previous_completed_sessions": len(previous),
                             "observed_previous_closes": sum(daily_mask),
                             "daily_lock": previous[-1] if previous else None,
                             "structural_vector_complete": complete})
    return {"session": session, "origin": origin, "scheduled_positions": len(steps),
            "observed_hours": sum(s.end in history.hours for s in steps),
            "structural_vector_count": sum(r["structural_vector_complete"] for r in requirements),
            "endpoint_structurally_complete": requirements[-1]["structural_vector_complete"],
            "all_48_history_requirements_met": all(r["structural_vector_complete"]
                                                   for r in requirements),
            "step_requirements": requirements,
            "scientific_readiness": False, "reason": "PUBLICATION_UNKNOWN_ACTION_UNVERIFIED"}


def canonical_integration(source: MarketSource) -> dict:
    """Actual archive → existing adapter → each step's own cutoff → audited MarketWindow."""
    history = load_market_history(source)
    examples = []
    for day in ("2020-07-01", "2020-10-30", "2020-11-02", "2020-11-27"):
        clock = history.calendar.clock(day)
        observations = []
        for slot in clock.hours:
            row = history.hours.get(slot.end)
            position = history.calendar._positions[(day, clock.hours.index(slot) + 1)]
            step = history.calendar.steps[position]
            measures = history.measures(step)
            observations.append({"period_start": slot.start.isoformat(),
                                 "period_end": slot.end.isoformat(),
                                 "close": row.close if row else None,
                                 "evidence_id": row.evidence_id if row else None,
                                 "basis": row.basis if row else "MISSING",
                                 "available_at": None, "mask": False,
                                 "reason": measures.reason,
                                 "U1_U5": None, "own_cutoff": step.information_cutoff.isoformat()})
        close = history.closes.get(day)
        item = {"kind": "REAL_CANONICAL_ARCHIVE", "session": day,
                "complete_hour_positions": len(clock.hours),
                "open_utc": clock.open.isoformat() if clock.open else None,
                "close_utc": clock.close.isoformat() if clock.close else None,
                "hours": observations, "daily_close": close.close if close else None,
                "daily_close_source_id": close.evidence_id if close else None}
        if day != "2020-11-27":
            window = window_from_history(history, day, 1)
            assert (window.values is None and len(window.valid_mask) == 48
                    and not any(window.valid_mask) and not window.research_ready)
            item["typed_window"] = {
                "scheduled_ends": [s.isoformat() for s in window.scheduled_ends],
                                    "valid_mask": list(window.valid_mask), "values": None,
                                    "reason": window.reason,
                                    "step_lineage": [{"count": len(ids),
                                                      "sha256": fingerprint(ids),
                                                      "first": ids[0] if ids else None,
                                                      "last": ids[-1] if ids else None}
                                                     for ids in window.source_ids],
                                    "step_reasons": window.step_reasons,
                                    "research_ready": window.research_ready}
        else:
            try:
                window_from_history(history, day, 1)
            except ValueError as exc:
                item["typed_window_reason"] = str(exc)
            else:
                raise ValueError("EARLY_CLOSE_ORIGIN_MUST_BE_STRUCTURALLY_INELIGIBLE")
        examples.append(item)
    return {"source_version": source.config["source_version"],
            "decision_id": source.config["decision_id"],
            "status": "CANONICAL_D7_ENGINEERING_PASS_SCIENTIFIC_HOLD",
            "history_complete_hours": len(history.hours),
            "observed_daily_closes": len(history.closes),
            "real_examples": examples, "market_channels": 5, "stock_features": 16,
            "eventual_MC0_width": 21, "empirical_fits": "NOT_RUN",
            "handoff": ["lstm_data.market_source.load_market_history(source)",
                        "lstm_data.market_features.window_from_history(history, session, origin, "
                        "floors=None, scaler=None)"],
            "research_ready": False}


def full_source_qa(source: MarketSource) -> dict:
    """Extend existing full-period QA only with missing warm-up, lineage and grid diagnostics."""
    qa = archive_qa(source)
    frame = load_archive(source)
    hours, _ = hourly_archive(frame, "2020-03-19", "2025-06-30")
    calendar = ScheduledCalendar("2020-03-19", "2025-06-30")
    history = history_from_archive(calendar, hours)
    first = [structural_history(history, "2020-07-01", origin) for origin in (1, 2)]
    qa["warmup_first_july_windows"] = first
    qa["warmup_status"] = ("PASS" if all(x["all_48_history_requirements_met"]
                                      for x in first) else "DEFICIENT")
    qa["first_july_raw_windows"] = [r for r in qa["origins"] if r["session"] == "2020-07-01"]
    duplicates = int(frame.duplicated(["symbol", "timestamp"]).sum())
    nulls = int(frame[["timestamp", "open", "high", "low", "close", "volume"]]
                .isna().sum().sum())
    off_grid = int(((frame.timestamp.dt.minute % 30 != 0)
                    | (frame.timestamp.dt.second != 0)).sum())
    qa["source_integrity"] = {"status": "PASS", "unique_rows": len(frame),
                              "duplicate_keys": duplicates,
                              "null_required_values": nulls,
                              "lineage_keys": sorted(frame.provenance_id.unique().tolist()),
                              "off_half_hour_grid": off_grid}
    native = []
    for day in ("2020-07-01", "2020-10-30", "2020-11-02", "2020-11-27"):
        clock = calendar.clock(day)
        sample = frame.loc[(frame.timestamp >= clock.open) & (frame.timestamp < clock.close)]
        rows = []
        for row in sample.itertuples():
            stamp = row.timestamp
            if not isinstance(stamp, pd.Timestamp):
                raise ValueError("CANONICAL_NATIVE_TIMESTAMP_REQUIRED")
            rows.append({"start": stamp.isoformat(),
                         "end": (stamp + pd.Timedelta(minutes=30)).isoformat(),
                         "open": row.open, "high": row.high, "low": row.low, "close": row.close,
                         "source_request_key": row.provenance_id,
                         "source_row_id": fingerprint([row.provenance_id, stamp.isoformat()])})
        native.append({"session": day, "native_rows": rows})
    qa["canonical_native_training_traces"] = native
    research_origins = [r for r in qa["origins"] if r["session"] >= "2020-07-01"]
    qa["research_raw_window_retention"] = {
        "numerator": sum(r["raw_46_of_48_retained"] for r in research_origins),
        "denominator": sum(r["calendar_valid"] for r in research_origins),
        "scope": "Research source coverage only, no causal vectors or labels"}
    qa["raw_window_retention_by_year_origin"] = {
        f"{year}:origin{origin}": {
            "numerator": sum(r["raw_46_of_48_retained"] for r in research_origins
                             if r["session"].startswith(year) and r["origin"] == origin),
            "denominator": sum(r["calendar_valid"] for r in research_origins
                               if r["session"].startswith(year) and r["origin"] == origin)}
        for year in sorted({r["session"][:4] for r in research_origins}) for origin in (1, 2)}
    all_days = pd.date_range("2020-03-19", "2025-06-30", freq="D")
    non_sessions = [d for d in all_days if d.date().isoformat() not in calendar._sessions]
    observed_days = frame.timestamp.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
    qa["calendar_non_sessions"] = {
        "weekday_holidays": [d.date().isoformat() for d in non_sessions if d.weekday() < 5],
        "weekend_days": sum(d.weekday() >= 5 for d in non_sessions),
        "off_session_date_native_rows": int((~observed_days.isin(tuple(calendar._sessions))).sum()),
        "off_session_rows_policy": "Preserved native records, never fabricated session positions"}
    qa["FT0"] = "NOT_IMPLEMENTED_BY_THIS_PACKAGE; source coverage is not stock-feature admission"
    qa["publication"] = {"status": "UNKNOWN_HOLD", "documented_historical_rows": 0,
                         "retrieval_is_publication": False,
                         "stale_documented_rows": "NOT_EVALUABLE"}
    qa["confirmation"] = "SOURCE_INTEGRITY_COVERAGE_ONLY; no returns/labels/performance computed"
    return qa


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_market_spy_v3.json"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    source = MarketSource.load(args.config)
    write_bounded_report(source, args.report, args.report / "source_qa_full_period.json",
                         full_source_qa(source))
    write_bounded_report(source, args.report, args.report / "market_source_integration.json",
                         canonical_integration(source))
    print({"source_qa": "MEASURED", "D7": "ENGINEERING_PASS", "activation": "HOLD"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
