"""Offline FT0 adequacy and source-only bridge; no empirical fits or confirmation outcomes."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from .clocks import execution_plan
from .config import write_json
from .ft0_tensor import join_market, stock_window
from .ft0_transforms import ORDER
from .hourly_proxy import proxy_causal_eligibility
from .labels import UNIVERSE, ForecastEvidence, fitting_window
from .m2 import scheduled_window
from .market_features import MarketHistory
from .market_source import MarketSource, load_market_history
from .spy_qa import structural_history
from .stock_features import FeatureCalculator, covered
from .stock_source import StockHistory, load_stock_history, proxy_reference


def peak_memory_bytes() -> int | None:
    """Optional native process peak; unavailable on platforms without resource."""
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def mechanical_m2(history: StockHistory, symbol: str, session: str, origin: int) -> bool:
    """Reference presence and scheduled maturity only; never computes real four-hour returns."""
    days = history.calendar.prior[session, origin][-60:]
    present = tuple(
        1.0
        if ((symbol, day, origin) in history.bars and (symbol, day, origin + 4) in history.bars)
        else None
        for day in days
    )
    return covered(present, 60, 57) and covered(present[-20:], 20, 19)


def group_summary(rows: list[dict], *, minimum: float) -> dict:
    denominator = len(rows)
    numerator = sum(r["mechanical_ft0"] for r in rows)
    sessions = {r["session"] for r in rows if r["mechanical_ft0"]}
    return {
        "numerator": numerator,
        "denominator": denominator,
        "fraction": numerator / denominator if denominator else None,
        "eligible_sessions": len(sessions),
        "minimum_retention": minimum,
        "mechanical_threshold": ("PASS" if numerator / denominator >= minimum else "FAIL")
        if denominator
        else "INCONCLUSIVE",
        "causal_eligible": 0,
        "scientific_threshold": "HOLD_SOURCE_ASOF_ACTION_AND_CERTIFICATES",
    }


def retention_audit(
    history: StockHistory, qa: dict, calculator: FeatureCalculator | None = None
) -> dict:
    """Enumerate exact complete-case input histories and direct gap cluster overlap."""
    calculator = calculator or FeatureCalculator(history)
    calendar = history.calendar
    masks: dict[tuple[str, pd.Timestamp], tuple[bool, ...]] = {}
    for symbol in UNIVERSE:
        for step in calendar.steps:
            if step.session >= "2024-07-01":
                break
            comp = calculator.components(symbol, step, source_only=True)
            masks[symbol, step.end] = tuple(comp.coverage[name] for name in ORDER)
    origins, clusters, feature_failures = [], Counter(), Counter()
    direct_lost_keys = set()
    missing_native = [w for w in qa["windows"] if not w["complete"]]
    for day, clock in calendar._sessions.items():
        if day >= "2024-07-01":
            break
        for origin in (1, 2):
            plan = execution_plan(clock, origin)
            if not plan.calendar_valid:
                continue
            item = {
                "session": day,
                "origin": origin,
                "scheduled_history": False,
                "direct_48_source_complete": False,
                "mechanical_ft0": False,
                "source_time_eligible": False,
                "input_eligible": False,
                "certificate_status": "FIT_PENDING_SOURCE_EVIDENCE",
                "label_status": "HOLD_RAW_CONVERSION_ACTION_AND_PUBLICATION",
                "execution": "NOT_EVALUATED",
            }
            try:
                steps = scheduled_window(calendar, day, origin)
            except ValueError:
                item["first_bad"] = {"reason": "SCHEDULED_HISTORY_INSUFFICIENT"}
                origins.append(item)
                continue
            item["scheduled_history"] = True
            gaps = {
                (symbol, step.session)
                for symbol in UNIVERSE
                for step in steps
                if (symbol, step.session, step.slot) not in history.bars
            }
            item["direct_48_source_complete"] = not gaps
            if gaps:
                direct_lost_keys.add((day, origin))
                for cluster in gaps:
                    clusters[cluster] += 1
            failures = []
            for symbol in UNIVERSE:
                for step in steps:
                    available = list(masks[symbol, step.end])
                    available[1] = mechanical_m2(history, symbol, step.session, origin)
                    for channel, present in zip(ORDER, available):
                        if not present:
                            failures.append((symbol, step.session, step.slot, channel))
            for channel in {f[3] for f in failures}:
                feature_failures[channel] += 1
            item["mechanical_ft0"] = not failures
            item["first_bad"] = (
                {
                    "symbol": failures[0][0],
                    "historical_session": failures[0][1],
                    "slot": failures[0][2],
                    "channel": failures[0][3],
                    "reason": "WARMUP_OR_MISSING_REQUIRED_HISTORY",
                }
                if failures
                else None
            )
            item["missing_clusters"] = [list(g) for g in sorted(gaps)]
            origins.append(item)

    def subset(start: str, stop: str, origin: int | None = None) -> list[dict]:
        return [
            r
            for r in origins
            if start <= r["session"] < stop and (origin is None or r["origin"] == origin)
        ]

    periods = {
        "train": ("2020-07-01", "2023-07-01", 0.90),
        "development": ("2023-07-01", "2024-07-01", 0.90),
        "WF1": ("2023-07-01", "2024-01-01", 0.85),
        "WF2": ("2024-01-01", "2024-07-01", 0.85),
    }
    groups = {
        name: group_summary(subset(start, stop), minimum=minimum)
        for name, (start, stop, minimum) in periods.items()
    }
    by_origin = {
        f"{name}:origin{origin}": group_summary(subset(start, stop, origin), minimum=0.85)
        for name, (start, stop, _) in periods.items()
        for origin in (1, 2)
    }
    inner = {}
    for stage in ("WF1", "WF2", "PRECONFIRMATION"):
        if stage == "WF1":
            window = fitting_window("WF1", "INNER_VALIDATION", fitted_at="2024-07-01T04:00Z")
        elif stage == "WF2":
            window = fitting_window("WF2", "INNER_VALIDATION", fitted_at="2024-07-01T04:00Z")
        else:
            window = fitting_window(
                "PRECONFIRMATION", "INNER_VALIDATION", fitted_at="2024-07-01T04:00Z"
            )
        rows = [
            r
            for r in origins
            if window.start
            <= pd.Timestamp(r["session"], tz="America/New_York").tz_convert("UTC")
            < window.stop
        ]
        count = len({r["session"] for r in rows if r["mechanical_ft0"]})
        counts = {o: sum(r["mechanical_ft0"] for r in rows if r["origin"] == o) for o in (1, 2)}
        inner[stage] = {
            "calendar_tail_sessions": 63,
            "mechanically_eligible_sessions": count,
            "origin_counts": counts,
            "minimum_sessions": 50,
            "minimum_each_origin": 25,
            "mechanical_guard": count >= 50 and min(counts.values()) >= 25,
            "mature_label_sample": "INCONCLUSIVE_SOURCE_CLOCK_ACTION_HOLD",
        }
    first = next((r for r in origins if r["mechanical_ft0"]), None)
    gap_detail = []
    for (symbol, day), affected in sorted(clusters.items()):
        key = symbol, day
        exclusive = sum(r.get("missing_clusters") == [list(key)] for r in origins)
        gap_detail.append(
            {
                "symbol": symbol,
                "source_session": day,
                "direct_48_candidate_loss_contribution": affected,
                "exclusive_direct_loss": exclusive,
            }
        )
    return {
        "status": "MEASURED_MECHANICAL_RETENTION_CAUSAL_HOLD",
        "populations": groups,
        "by_origin": by_origin,
        "origins": origins,
        "inner_63_session_tails": inner,
        "fold_100_distinct_session_guard": {
            fold: {
                "minimum": 100,
                "observed": groups[fold]["eligible_sessions"],
                "mechanical_pass": groups[fold]["eligible_sessions"] >= 100,
                "scientific_status": "HOLD",
            }
            for fold in ("WF1", "WF2")
        },
        "missing_native_half_hours_full_source": qa["missing_source_bars"],
        "missing_hour_or_stub_windows_full_source": len(missing_native),
        "direct_48_gap_lost_origins": len(direct_lost_keys),
        "gap_overlap_clusters": gap_detail,
        "overlap_counting": "Cluster contributions overlap; "
        "exclusive counts are separately measured",
        "feature_loss_counts": dict(feature_failures),
        "first_mechanical_complete_origin": first,
        "volatility_regimes": {
            "status": "UNVERIFIED_SPY_PUBLICATION",
            "85_percent_guard": "INCONCLUSIVE",
            "10_percentage_point_gap_guard": "INCONCLUSIVE",
        },
        "market_intersection": {
            "structural_market": "Measured in canonical SPY QA",
            "causal_matched_origins": 0,
            "status": "HOLD",
        },
        "confirmation": "RAW_GAPS_ONLY; no FT0 feature/target/performance computation",
        "fitting": "NO_REAL_EMPIRICAL_FITS",
        "research_ready": False,
    }


def market_alignment(retention: dict, market: MarketHistory) -> dict:
    """Measure the identical origin intersection using the existing D7 coverage audit."""
    measured = []
    for row in retention["origins"]:
        result = structural_history(market, row["session"], row["origin"])
        valid = (
            result["endpoint_structurally_complete"]
            and result["structural_vector_count"] >= 46
        )
        measured.append((row, valid))
    groups = {}
    for name, start, stop in (
        ("train", "2020-07-01", "2023-07-01"),
        ("development", "2023-07-01", "2024-07-01"),
        ("WF1", "2023-07-01", "2024-01-01"),
        ("WF2", "2024-01-01", "2024-07-01"),
    ):
        subset = [(r, good) for r, good in measured if start <= r["session"] < stop]
        groups[name] = {
            "denominator": len(subset),
            "market_structural": sum(good for _, good in subset),
            "stock_only_mechanical": sum(r["mechanical_ft0"] for r, _ in subset),
            "matched_mechanical": sum(r["mechanical_ft0"] and good for r, good in subset),
            "causal_stock_only": 0,
            "causal_matched": 0,
        }
    return {
        "by_population": groups,
        "market_rule": "EXISTING_D7_ENDPOINT_AND_46_OF_48_STRUCTURAL_VECTORS",
        "causal_matched_origins": 0,
        "status": "MECHANICAL_INTERSECTION_MEASURED_CAUSAL_HOLD",
    }


def timing_bridge(history: StockHistory, retention: dict) -> dict:
    """Pinned real negative references and source-only waterfall; no fabricated raw prices/fills."""
    traces = []
    for day, origin in (("2020-07-01", 1), ("2021-03-15", 2), ("2020-11-27", 1)):
        clock = history.calendar.clock(day)
        plan = execution_plan(clock, origin)
        if not plan.calendar_valid:
            traces.append(
                {"session": day, "origin": origin, "reason": plan.reason, "calendar_valid": False}
            )
            continue
        entries, details = [], []
        for symbol in UNIVERSE:
            bar = history.bars.get((symbol, day, origin))
            reference = proxy_reference(bar, None) if bar else None
            if reference is not None:
                entries.append(reference)
            details.append(
                {
                    "symbol": symbol,
                    "source_id": bar.row_id if bar else None,
                    "split_adjusted_close": bar.close if bar else None,
                    "raw_reference": "RAW_CONVERSION_FACTOR_UNVERIFIED" if bar else "MISSING",
                    "source_publication": "UNKNOWN",
                    "action_scope": "UNVERIFIED",
                }
            )
        forecast = ForecastEvidence(
            False,
            plan.cutoff or clock.hours[0].end,
            UNIVERSE,
            "UNKNOWN",
            "REAL_CANONICAL_SOURCE_NEGATIVE",
        )
        causal = proxy_causal_eligibility(plan, forecast, tuple(entries))
        traces.append(
            {
                "session": day,
                "origin": origin,
                "calendar_valid": True,
                "cutoff": str(plan.cutoff),
                "issuance": str(plan.issuance),
                "issuance_kind": plan.issuance_kind,
                "nominal_entry": str(plan.entry),
                "nominal_exit": str(plan.exit),
                "event_horizon_minutes": 240,
                "entry_proxy_end": str(plan.cutoff),
                "exit_proxy_end": str(plan.cutoff + pd.Timedelta(hours=4))
                if plan.cutoff is not None
                else None,
                "forecast_issuable": causal.forecast_issuable,
                "entry_eligible": causal.entry_eligible,
                "references": details,
                "raw_label": "NO_ELIGIBLE_REAL_CASE",
                "fills": "NOT_EVALUATED",
            }
        )
    rows = retention["origins"]
    return {
        "P2_1": "IMPLEMENTATION_ALREADY_APPROVED",
        "P2_2": "IMPLEMENTATION_ALREADY_APPROVED",
        "G2": "SOURCE_TIME_ACTION_CONVERSION_HOLD",
        "real_traces": traces,
        "waterfall": {
            "structurally_valid_origins": len(rows),
            "sufficient_48_history": sum(r["scheduled_history"] for r in rows),
            "mechanical_source_48_complete": sum(r["direct_48_source_complete"] for r in rows),
            "issuance_source_time_eligible": 0,
            "all_five_entry_reference_eligible": 0,
            "independently_matured_TG0_labels": 0,
            "future_exit_diagnostics": "NO_CERTIFIED_RAW_REFERENCES",
            "physical_positions_or_fills": "NOT_EVALUATED",
        },
        "minute_api": "PRESERVED_SEPARATE_VERSION",
        "TG0_math": "EXISTING_MEDIAN_UNSCALED_MAD",
        "TG0_epsilon": "EXISTING_MAX_1E-4_0.1_TRAINING_MEDIAN_MAD",
        "C01": "NO_EXIT_ARGUMENT_IN_FORECAST_OR_ENTRY_BRIDGE",
        "research_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_data.json"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    history, qa = load_stock_history(args.config)
    calculator = FeatureCalculator(history)
    retention = retention_audit(history, qa, calculator)
    market = load_market_history(MarketSource.load())
    retention["market_intersection"] = market_alignment(retention, market)
    write_json(args.report / "retention_and_attrition.json", retention)
    write_json(args.report / "g2_timing_label_bridge.json", timing_bridge(history, retention))
    # Source-only math before confirmation; certificates remain absent, and all real masks false.
    stock = stock_window(calculator, "2021-03-15", 1, source_only=True)
    joined = join_market(stock, market, origin=1)
    write_json(
        args.report / "ft0_tensor_trace.json",
        {
            "status": "REAL_SOURCE_ONLY_NO_ELIGIBLE_REAL_CASE",
            "stock_shape": stock.shape,
            "market_shape": [48, 5],
            "symbols": stock.symbols,
            "channels": stock.channels,
            "scheduled_ends": [s.end.isoformat() for s in stock.steps],
            "stock_valid_cells": sum(v for symbol in stock.mask for row in symbol for v in row),
            "stock_input_eligible": stock.input_eligible,
            "matched_eligible": joined.matched_market_eligible,
            "market_reason": joined.market.reason if joined.market else "MISSING",
            "source_binding": history.binding,
            "action_binding": history.action_binding,
            "sample_AAPL_final_raw": stock.raw_values[0][-1],
            "sample_AAPL_final_scaled": stock.values[0][-1],
            "sample_AAPL_final_reasons": stock.reasons[0][-1],
            "source_only": True,
            "actual_transform_fit": "NOT_RUN",
            "research_ready": False,
        },
    )
    # Compact QA, preserving every missing native slot locator without a second data store.
    write_json(
        args.report / "ft0_source_qa.json",
        {
            "source_rows": qa["source_rows"],
            "hour_or_stub_rows": len(history.bars),
            "missing_source_bars": qa["missing_source_bars"],
            "missing_windows": [w for w in qa["windows"] if not w["complete"]],
            "daily_close_observed": sum(d.close is not None for d in history.daily.values()),
            "full_session_volume_observed": sum(
                d.volume is not None for d in history.daily.values()
            ),
            "publication": qa["publication"],
            "action_scope": qa["action_scope"],
            "source_version": qa["source_version"],
            "source_binding": history.binding,
            "history_content_sha256": history.content_sha256,
            "action_binding": history.action_binding,
            "peak_process_memory_bytes": peak_memory_bytes(),
            "feature_cache_unique_steps": len(calculator._components),
            "canonical_cache_disk_bytes": 0,
            "no_per_window_datasets": True,
            "confirmation_policy": "Source integrity only",
        },
    )
    print(
        {
            "status": "SOURCE_QA_ATTRITION_MEASURED",
            "first_mechanical_origin": retention["first_mechanical_complete_origin"],
            "real_scientific_admission": 0,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
