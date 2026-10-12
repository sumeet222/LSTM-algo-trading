"""Bounded authorized acquisition and offline candidate audit; no activation or real fits."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials
from .config import digest, load_config, write_json
from .ft0_audit import market_alignment
from .market_source import MarketSource, load_market_history
from .remediation_overlay import NativeAddition, fixed_retention, history_from_view, resolve_native
from .remediation_plan import PACKAGE, dependency_calendar, gap_keys, source_request_manifest
from .remediation_transport import RemediationTransport, StorageLimit, publish_chunk, read_chunk
from .stock_source import StockCalendar
from .store import load_store

ARCHIVE = Path("data/raw/alpaca/track_a_remediation_v1")
ORIGINAL_REPORT = Path("reports/data_audit/ta_p2_close_ft0_2026-10-11")


def read_plan(report: Path) -> dict:
    """Fail closed if the frozen request list, resource policy or original QA identity drifted."""
    value = json.loads((report / "request_manifest.json").read_text())
    expected = source_request_manifest(
        load_config(Path("configs/track_a_data.json")),
        json.loads((ORIGINAL_REPORT / "ft0_source_qa.json").read_text()),
    )
    if value != expected or value["package"] != PACKAGE:
        raise ValueError("REMEDIATION_REQUEST_MANIFEST_CHANGED")
    baseline = json.loads((report / "original_replay/retention_and_attrition.json").read_text())
    if baseline != json.loads((ORIGINAL_REPORT / "retention_and_attrition.json").read_text()):
        raise ValueError("ORIGINAL_RETENTION_NOT_REPRODUCED")
    return value


def acquire(report: Path, env_file: Path) -> dict:
    """Execute only predeclared history/controls/gaps, optionally tight native1Min diagnosis."""
    plan = read_plan(report)
    amendment_path = report / "pagination_observation_amendment_v1.json"
    page_overrides = {}
    if amendment_path.exists():
        amendment = json.loads(amendment_path.read_text())
        expected = {r["request_hash"] for r in plan["requests"] if r["kind"] == "WARMUP"}
        page_overrides = amendment["warmup_max_pages"]
        if (
            set(page_overrides) != expected
            or any(n != 10 for n in page_overrides.values())
            or amendment["Alpaca_ceiling"] != 180
            or amendment["original_manifest_sha256"] != digest(report / "request_manifest.json")
        ):
            raise ValueError("REMEDIATION_OPERATIONAL_AMENDMENT_CHANGED")
    load_dotenv(env_file, override=False)
    key, secret = credentials()
    limits = StorageLimit((ARCHIVE, report))
    journal = ARCHIVE / "source_transport_journal.jsonl"
    transport = RemediationTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limits.reserve,
    )
    results = []
    cluster_keys = gap_keys(json.loads((ORIGINAL_REPORT / "ft0_source_qa.json").read_text()))
    unresolved: set[tuple[str, str]] = set()
    interrupted = None
    for request in plan["requests"]:
        params = request["params"]
        symbol = params["symbols"]
        day = pd.Timestamp(params["start"]).tz_convert("America/New_York").date().isoformat()
        kind = request["kind"]
        if kind == "CONDITIONAL_MINUTE_DIAGNOSTIC" and (symbol, day) not in unresolved:
            results.append(
                {
                    "request_hash": request["request_hash"],
                    "kind": kind,
                    "status": "INACTIVE_NATIVE_GAP_RECOVERED",
                }
            )
            continue
        store = ARCHIVE / ("minute_diagnostics" if params["timeframe"] == "1Min" else "native30")
        saved = read_chunk(store, params)
        if saved is None:
            config = load_config(Path("configs/track_a_data.json"))
            config["timeframe"] = params["timeframe"]
            config["max_pages_per_request"] = page_overrides.get(
                request["request_hash"], request["max_pages"]
            )
            config["retry"] = dict(config["retry"], max_attempts=3, max_seconds=10)
            client = HistoricalClient(config, key, secret, get=transport.request)
            begin = len(transport.records())
            try:
                frame = client.bars(params)
                receipts = transport.records()[begin:]
                value = publish_chunk(store, frame, params, receipts, kind=kind, limit=limits)
            except (DataAccessError, ValueError) as error:
                # Safe codes only: never response body, token, headers, or exception credentials.
                interrupted = {
                    "request_hash": request["request_hash"],
                    "kind": kind,
                    "status": "ACQUISITION_HOLD",
                    "error_class": type(error).__name__,
                    "reason": str(error)
                    if isinstance(error, DataAccessError)
                    else "SOURCE_SCHEMA_OR_PROVENANCE_VALIDATION_HOLD",
                }
                break
        else:
            frame, value = saved
        results.append(
            {
                "request_hash": request["request_hash"],
                "kind": kind,
                "rows": len(frame),
                "sha256": value["sha256"],
                "resumed": saved is not None,
                "status": "SHA_VERIFIED_TERMINAL",
            }
        )
        if kind == "GAP_RETRY":
            observed = {pd.Timestamp(t).isoformat() for t in frame.timestamp}
            if set(cluster_keys[symbol, day]) - observed:
                unresolved.add((symbol, day))
    runs = report / "acquisition_runs"
    run = len(list(runs.glob("*.json"))) + 1 if runs.exists() else 1
    summary = {
        "package": PACKAGE,
        "status": "COMPLETE" if interrupted is None else "PARTIAL_HOLD",
        "attempts": transport.used,
        "remaining": 180 - transport.used,
        "journal": journal.as_posix(),
        "journal_sha256": digest(journal) if journal.exists() else None,
        "results": results,
        "interrupted": interrupted,
        "storage_bytes": limits.used,
        "secondary": {
            "Massive_key_present": bool(os.getenv("MASSIVE_API_KEY")),
            "Polygon_key_present": bool(os.getenv("POLYGON_API_KEY")),
            "status": (
                "SECONDARY_KEY_PRESENT_ACCESS_NOT_YET_VERIFIED"
                if os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY")
                else "SECONDARY_UNAVAILABLE_NO_REPOSITORY_PROVISIONED_VENDOR"
            ),
            "attempts": 0,
            "remaining": 80,
        },
        "no_SPY_calls": True,
        "real_fits": 0,
        "scientific_activation": False,
    }
    write_json(runs / f"run_{run:03d}.json", summary)
    return summary


def additions_from_archive(plan: dict) -> tuple[NativeAddition, ...]:
    found = []
    for request in plan["requests"]:
        if request["params"]["timeframe"] != "30Min":
            continue
        saved = read_chunk(ARCHIVE / "native30", request["params"])
        if saved is not None:
            frame, value = saved
            found.append(
                NativeAddition(
                    frame, "ALPACA", request["kind"], request["request_hash"], value["sha256"]
                )
            )
    return tuple(found)


def recovery_comparison(baseline: dict, views: dict[str, dict]) -> dict:
    """Disjoint recovery mechanisms on original fixed origin keys, not summed feature failures."""
    original = {
        (r["session"], r["origin"]): r for r in baseline["origins"] if r["session"] < "2023-07-01"
    }
    chosen = {
        name: {(r["session"], r["origin"]): r["mechanical_ft0"] for r in report["origins"]}
        for name, report in views.items()
    }
    counts: dict[str, int] = {}
    changes = []
    for key, before in original.items():
        history = chosen["HISTORY_ONLY"][key]
        gap = chosen["GAP_ONLY"][key]
        both = chosen["ALPACA_ONLY_EXTENDED"][key]
        if before["mechanical_ft0"]:
            mechanism = "RETAINED" if both else "REGRESSION"
        elif history and gap:
            mechanism = "RECOVERED_BY_EITHER_INDEPENDENTLY"
        elif history:
            mechanism = "HISTORY_ONLY_SUFFICIENT"
        elif gap:
            mechanism = "GAP_ONLY_SUFFICIENT"
        elif both:
            mechanism = "BOTH_REQUIRED_INTERACTION"
        else:
            mechanism = "STILL_REJECTED"
        category = (
            "BASELINE_RETAINED919"
            if before["mechanical_ft0"]
            else ("STARTUP264" if key[0] < "2021-01-12" else "LATER319")
        )
        counts[f"{category}:{mechanism}"] = counts.get(f"{category}:{mechanism}", 0) + 1
        if not before["mechanical_ft0"] or not both:
            changes.append(
                {
                    "session": key[0],
                    "origin": key[1],
                    "baseline": before["mechanical_ft0"],
                    "history_only": history,
                    "gap_only": gap,
                    "both": both,
                    "mechanism": mechanism,
                }
            )
    return {
        "disjoint_counts": counts,
        "original_train_rejections": 583,
        "origin_changes": changes,
        "regressions": sum(n for k, n in counts.items() if k.endswith(":REGRESSION")),
        "no_fabricated_values": True,
    }


def audit(report: Path) -> dict:
    """Read the original archive once; recompute three candidate views with identical math."""
    plan = read_plan(report)
    original = load_store(load_config(Path("configs/track_a_data.json")))
    additions = additions_from_archive(plan)
    dependency = dependency_calendar()
    market = load_market_history(MarketSource.load())
    outcomes = {}
    summaries = {}
    for view in ("HISTORY_ONLY", "GAP_ONLY", "ALPACA_ONLY_EXTENDED"):
        start = "2020-07-01" if view == "GAP_ONLY" else dependency["minimal_calendar_start"]
        calendar = StockCalendar(start, "2025-06-30")
        frame, selection = resolve_native(original, additions, calendar, view=view)
        write_json(report / view.lower() / "selection_manifest.json", selection)
        history, qa = history_from_view(frame, start, view=view)
        result = fixed_retention(history, qa)
        result["market_intersection"] = market_alignment(result, market)
        write_json(report / view.lower() / "retention.json", result)
        outcomes[view] = result
        summaries[view] = {
            "populations": result["populations"],
            "by_origin": result["by_origin"],
            "first_mechanical": result["first_mechanical_complete_origin"],
            "feature_loss_counts": result["feature_loss_counts"],
            "inner_63_session_tails": result["inner_63_session_tails"],
            "fold_100_distinct_session_guard": result["fold_100_distinct_session_guard"],
            "market_intersection": result["market_intersection"],
            "volatility_regimes": result["volatility_regimes"],
            "added_RTH_rows": selection["added_RTH_rows"],
            "native_missing_in_full_view": qa["missing_source_bars"],
            "own_publication": "UNKNOWN",
            "causal_admission": 0,
            "model_fits": 0,
            "status": "CANDIDATE_NOT_ACTIVATED",
        }
        print({"view": view, "train": result["populations"]["train"]}, flush=True)
    baseline = json.loads((report / "original_replay/retention_and_attrition.json").read_text())
    comparison = {
        "original": baseline["populations"],
        "views": summaries,
        "recovery": recovery_comparison(baseline, outcomes),
        "secondary_candidate_view": "INACTIVE_SECONDARY_UNAVAILABLE",
        "scientific_activation": False,
        "confirmation": "NO_FEATURE_TARGET_OR_PERFORMANCE",
    }
    write_json(report / "retention_before_after.json", comparison)
    return comparison


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("acquire", "audit"))
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if args.command == "acquire":
        if args.authorization != PACKAGE:
            parser.error("acquisition requires explicit reviewed package authorization")
        result = acquire(args.report, args.env_file)
        print(
            {
                "status": result["status"],
                "new_attempts": result["attempts"],
                "remaining": result["remaining"],
                "interrupted": result["interrupted"],
            }
        )
        return 0 if result["interrupted"] is None else 2
    audit(args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
