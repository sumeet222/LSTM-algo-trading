"""Track A SPY archive adapter. Source selection never authorizes research use."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import requests
from dotenv import load_dotenv

from .aggregation import aggregate_session_hours
from .alpaca import ENDPOINT, DataAccessError, HistoricalClient, credentials, request_params
from .calendar import stock_qa
from .config import digest, fingerprint, now, write_json
from .ledger import parse_json
from .store import chunk_paths, read_verified, save_chunk
from .validation import require_valid

if TYPE_CHECKING:
    from .market_features import MarketHistory

DECISION_ID = "TA-D2-MARKET-SPY-001"
SOURCE_VERSION = "ALPACA_SIP_SPY_RAW_30MIN_V1"
DEFAULT_CONFIG = Path("configs/track_a_market_spy_v2.json")
PILOT_DATES = ("2020-03-19", "2020-03-20", "2020-07-01", "2020-11-27", "2021-01-04")


@dataclass(frozen=True)
class MarketSource:
    """Validated nonactivating selector; no USA500 or IEX fallback."""

    root: Path
    config: dict[str, object]

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG) -> MarketSource:
        path = path.resolve()
        cfg = parse_json(path.read_bytes())
        required = {
            "schema_version": 1, "decision_id": DECISION_ID, "source_version": SOURCE_VERSION,
            "source_kind": "ETF_PROXY", "provider": "ALPACA", "feed": "sip",
            "symbols": ["SPY"], "adjustment": "raw", "timeframe": "30Min",
            "calendar": "XNYS", "timezone": "America/New_York", "research_status": "BLOCKED",
            "available_at_basis": "UNKNOWN", "start_date": "2020-03-19",
            "end_date": "2025-06-30", "asof": "2025-06-30", "currency": "USD",
            "page_limit": 10000, "partition_months": 6,
        }
        if any(cfg.get(k) != v for k, v in required.items()):
            raise ValueError("SPY_SOURCE_VERSION_OR_POLICY_MISMATCH_NO_FALLBACK")
        location = cfg.get("stock_store")
        if location != "data/raw/alpaca/track_a_spy_v1":
            raise ValueError("SPY_CANONICAL_NAMESPACE_REQUIRED")
        version = cfg.get("acquisition_policy_version", 1)
        policy = (2, 24, 60, 2) if version == 1 else (12, 96, 240, 3)
        if version not in (1, 2) or any(cfg.get(k) != v for k, v in zip(
            ("max_pages_per_request", "max_partitions", "max_transport_attempts"), policy[:3]
        )):
            raise ValueError("SPY_VERSIONED_ACQUISITION_POLICY_REQUIRED")
        if version == 2 and (cfg.get("max_additional_bytes") != 256 * 1024**2
                             or cfg.get("authorization_package") != "TA-MKT-SPY-002"):
            raise ValueError("SPY_CONTINUATION_AUTHORIZATION_REQUIRED")
        retry = cfg.get("retry")
        if not isinstance(retry, dict) or retry != {
            "max_attempts": policy[3], "base_seconds": 1, "max_seconds": 10,
            "jitter_seconds": 0.5, "requests_per_minute": 180, "timeout_seconds": 30,
        }:
            raise ValueError("SPY_BOUNDED_RETRY_POLICY_REQUIRED")
        return cls(path.parent.parent, cfg)

    @property
    def store(self) -> Path:
        return self.root / "data/raw/alpaca/track_a_spy_v1"

    @property
    def identity(self) -> str:
        return fingerprint(self.config)

    def interval(self, start: str, end_exclusive: str) -> dict:
        lower = pd.Timestamp(start, tz="America/New_York").tz_convert("UTC")
        upper = pd.Timestamp(end_exclusive, tz="America/New_York").tz_convert("UTC")
        return request_params(
            self.config, ["SPY"], lower.isoformat(),
            (upper - pd.Timedelta(nanoseconds=1)).isoformat(),
        )

    def partitions(self) -> list[dict]:
        boundaries = ["2020-03-19", "2020-07-01"] + [
            f"{year}-{month:02d}-01"
            for year in range(2021, 2026) for month in (1, 7)
        ]
        return [self.interval(a, b) for a, b in zip(boundaries, boundaries[1:])]


@dataclass
class AttemptBudget:
    """Persist each transport attempt before GET; failed attempts also count on resume."""

    journal: Path
    stage: str
    ceiling: int = 60

    @property
    def used(self) -> int:
        raw = self.journal.read_bytes() if self.journal.exists() else b""
        if raw and not raw.endswith(b"\n"):
            raise ValueError("SPY_ATTEMPT_JOURNAL_TRUNCATED_REVIEW_REQUIRED")
        rows = raw.splitlines()
        count = 0
        for row in rows:
            item = parse_json(row)
            if item.get("record_kind") != "result":
                count += 1
        return count

    def append(self, item: dict[str, object]) -> None:
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        with self.journal.open("ab") as stream:
            stream.write(json.dumps(item, sort_keys=True).encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())

    def get(self, url: str, **kwargs) -> requests.Response:
        if self.ceiling not in (60, 240) or url != ENDPOINT or self.used >= self.ceiling:
            raise DataAccessError("SPY_TRANSPORT_BUDGET_EXHAUSTED_OR_UNEXPECTED_ENDPOINT")
        attempt = self.used + 1
        params = kwargs.get("params", {})
        request_key = fingerprint(params)
        self.append({"record_kind": "attempt", "attempt_id": attempt,
                     "time_utc": now(), "stage": self.stage, "request_key": request_key})
        try:
            response = requests.get(url, **kwargs)
        except requests.RequestException:
            self.append({"record_kind": "result", "attempt_id": attempt,
                         "time_utc": now(), "status": "transport_error"})
            raise
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        bars = payload.get("bars", {}) if isinstance(payload, dict) else {}
        rows = sum(len(v) for v in bars.values() if isinstance(v, list)) \
            if isinstance(bars, dict) else 0
        self.append({"record_kind": "result", "attempt_id": attempt, "time_utc": now(),
                     "status": response.status_code, "response_bytes": len(response.content),
                     "response_sha256": hashlib.sha256(response.content).hexdigest(),
                     "returned_rows": rows, "request_key": request_key,
                     "continued_request": "page_token" in params,
                     "has_continuation": bool(payload.get("next_page_token"))
                         if isinstance(payload, dict) else False,
                     "retry_after": response.headers.get("Retry-After")})
        return response


def hourly_archive(frame: pd.DataFrame, start: str, end: str) -> tuple[pd.DataFrame, dict]:
    """Reuse aggregation while replacing its assumed availability with honest unknowns."""
    if frame.empty:
        raise FileNotFoundError("MISSING_SPY_SOURCE_NO_FALLBACK")
    for column, expected in (
        ("symbol", "SPY"), ("feed", "sip"), ("adjustment", "raw"),
        ("source_timeframe", "30Min"),
    ):
        if column not in frame or not (frame[column] == expected).all():
            raise ValueError("SPY_SOURCE_POLICY_MISMATCH_NO_FALLBACK")
    result, qa = aggregate_session_hours(frame, ["SPY"], start, end)
    result["period_start"] = result.timestamp
    result["period_end"] = result.available_at
    result["provider_bar_timestamp"] = result.timestamp
    result["available_at"] = pd.Series(pd.NaT, index=result.index, dtype="datetime64[ns, UTC]")
    result["available_at_basis"] = "UNKNOWN"
    result["source_version"] = SOURCE_VERSION
    # Constituent request IDs are retained, rather than claiming a generated panel is raw.
    if "provenance_id" in frame:
        ids = frame.set_index("timestamp").provenance_id

        def constituent_identity(start: object, stop: object) -> str:
            if not isinstance(start, pd.Timestamp) or not isinstance(stop, pd.Timestamp):
                raise ValueError("SPY_INTERVAL_TIMESTAMP_REQUIRED")
            expected = pd.date_range(start, stop, freq="30min", inclusive="left")
            return fingerprint(ids.loc[expected].tolist())

        result["evidence_id"] = [
            constituent_identity(row.period_start, row.period_end)
            for row in result.itertuples()
        ]
    else:
        result["evidence_id"] = "UNPERSISTED_SOURCE"
    qa["availability"] = "UNKNOWN; archive retrieval is not historical publication proof"
    return result, qa


def load_archive(source: MarketSource) -> pd.DataFrame:
    """Require every planned immutable chunk, including warm-up; no partial-source success."""
    frames = []
    for params in source.partitions():
        data, manifest = chunk_paths(source.store, params)
        if not data.exists() or not manifest.exists():
            raise FileNotFoundError("MISSING_SPY_PARTITION_NO_FALLBACK")
        frames.append(read_verified(data, manifest, params))
    result = pd.concat(frames, ignore_index=True)
    require_valid(result, stocks=True)
    return result


def load_market_history(source: MarketSource) -> MarketHistory:
    """Canonical SHA-verified archive → anchored intervals → existing D7 history.

    Publication remains UNKNOWN, actions unverified, and closing stubs supply
    genuine daily closes without becoming complete hourly feature positions.
    Missing canonical partitions raise; there is no pilot or USA500 fallback.
    """
    from .m2 import ScheduledCalendar
    from .market_features import history_from_archive

    frame = load_archive(source)
    hours, _ = hourly_archive(frame, "2020-03-19", "2025-06-30")
    return history_from_archive(ScheduledCalendar("2020-03-19", "2025-06-30"), hours)


def archive_qa(source: MarketSource) -> dict:
    """Source-only full-period denominators; missingness never becomes synthetic prices.

    A successful request-completeness proof is separate from calendar coverage.
    Raw window retention below is structural only, never causal feature eligibility.
    """
    from .clocks import execution_plan
    from .m2 import ScheduledCalendar, scheduled_window
    from .market_features import history_from_archive

    frame = load_archive(source)
    hours, qa = hourly_archive(frame, "2020-03-19", "2025-06-30")
    calendar = ScheduledCalendar("2020-03-19", "2025-06-30")
    history = history_from_archive(calendar, hours)
    windows: dict[str, list[dict]] = {}
    for window in qa["windows"]:
        windows.setdefault(window["session"], []).append(window)
    daily = []
    origins = []
    for day, clock in calendar._sessions.items():
        current = windows[day]
        expected = sum(1 if w["stub"] else 2 for w in current)
        missing = sum(len(w["missing_source_starts"]) for w in current)
        if clock.open is None or clock.close is None:
            raise ValueError("VALID_XNYS_CLOCK_REQUIRED")
        local = clock.open.tz_convert("America/New_York")
        offset = local.utcoffset()
        if offset is None:
            raise ValueError("XNYS_TIMEZONE_OFFSET_REQUIRED")
        daily.append({"session": day, "expected_native_rth": expected,
                      "observed_native_rth": expected - missing,
                      "missing_native_rth": missing, "empty_rth": missing == expected,
                      "expected_complete_hours": len(clock.hours),
                      "observed_complete_hours": sum(w["complete"] and not w["stub"]
                                                     for w in current),
                      "daily_close_observed": day in history.closes,
                      "early_close": len(clock.hours) < 6,
                      "utc_offset_hours": offset.total_seconds() / 3600,
                      "open_utc": clock.open.isoformat(), "close_utc": clock.close.isoformat()})
        for origin in (1, 2):
            plan = execution_plan(clock, origin)
            retained, present, endpoint = False, 0, False
            reason = "STRUCTURALLY_INELIGIBLE_ORIGIN"
            if plan.calendar_valid:
                try:
                    steps = scheduled_window(calendar, day, origin)
                    present = sum(s.end in history.hours for s in steps)
                    endpoint = steps[-1].end in history.hours
                    retained = endpoint and present >= 46
                    reason = "PUBLICATION_UNKNOWN" if retained else "SOURCE_WINDOW_INCOMPLETE"
                except ValueError:
                    reason = "SCHEDULED_HISTORY_INSUFFICIENT"
            origins.append({"session": day, "origin": origin,
                            "calendar_valid": plan.calendar_valid, "observed_hours": present,
                            "endpoint_observed": endpoint, "raw_46_of_48_retained": retained,
                            "causal_feature_eligible": False, "reason": reason})

    def summary(rows: list[dict]) -> dict:
        expected = sum(r["expected_native_rth"] for r in rows)
        observed = sum(r["observed_native_rth"] for r in rows)
        return {"sessions": len(rows), "expected_native_rth": expected,
                "observed_native_rth": observed, "missing_native_rth": expected - observed,
                "observed_fraction": observed / expected if expected else None,
                "empty_sessions": sum(r["empty_rth"] for r in rows),
                "daily_close_count": sum(r["daily_close_observed"] for r in rows),
                "complete_hours": sum(r["observed_complete_hours"] for r in rows),
                "expected_complete_hours": sum(r["expected_complete_hours"] for r in rows)}

    return {"source_version": SOURCE_VERSION, "status": "ARCHIVE_SOURCE_QA_ONLY",
            "rows": len(frame), "totals": summary(daily), "sessions": daily,
            "months": {month: summary([r for r in daily if r["session"].startswith(month)])
                       for month in sorted({r["session"][:7] for r in daily})},
            "years": {year: summary([r for r in daily if r["session"].startswith(year)])
                      for year in sorted({r["session"][:4] for r in daily})},
            "quarters": {quarter: summary([r for r in daily if
                         f'{r["session"][:4]}-Q{(int(r["session"][5:7]) - 1) // 3 + 1}' == quarter])
                         for quarter in sorted({
                             f'{r["session"][:4]}-Q{(int(r["session"][5:7]) - 1) // 3 + 1}'
                             for r in daily})},
            "session_types": {kind: summary([r for r in daily if r["early_close"] == early])
                              for kind, early in (("ordinary", False), ("early", True))},
            "dst": {str(offset): summary([r for r in daily if r["utc_offset_hours"] == offset])
                    for offset in (-5, -4)},
            "missing_windows": [w for w in qa["windows"] if not w["complete"]],
            "closing_stubs_observed": int(hours.is_stub.sum()), "origins": origins,
            "raw_window_retention": {"numerator": sum(r["raw_46_of_48_retained"] for r in origins),
                                     "denominator": sum(r["calendar_valid"] for r in origins)},
            "thresholds": {"diagnostic_native_grid": "Zero missing RTH slots for grid PASS",
                           "raw_window": "Endpoint present and >=46/48; not feature eligibility",
                           "feature_valid": "Publication/action checks and valid certificates"},
            "complete_grid_pass": qa["timing_gate_pass"],
            "publication_verified_rows": 0, "causal_feature_eligible_windows": 0,
            "corporate_action_scope": "UNVERIFIED; separate evidence required",
            "stock_missing_bars_inherited_separately": 168,
            "empirical_floor_scaler_fit": "NOT_RUN", "research_status": "BLOCKED"}


def acquire_partition(
    source: MarketSource, client: HistoricalClient, params: dict,
    *, completion_check: Callable[[], dict] | None = None,
) -> dict:
    """Reuse the stock checkpoint writer; six-month ranges need no second storage framework."""
    data, manifest = chunk_paths(source.store, params)
    if data.exists() and manifest.exists():
        read_verified(data, manifest, params)
        return parse_json(manifest.read_bytes())
    if data.exists() or manifest.exists():
        raise ValueError("INTERRUPTED_SPY_PARTITION_REVIEW_REQUIRED_NO_OVERWRITE")
    event_start = len(client.events)
    frame = client.bars(params)  # All pages must finish before save_chunk is called.
    completion = completion_check() if completion_check else None
    if completion is not None:
        start = pd.Timestamp(params["start"]).tz_convert("America/New_York").date().isoformat()
        end = pd.Timestamp(params["end"]).tz_convert("America/New_York").date().isoformat()
        _, qa = hourly_archive(frame, start, end)
        completion.update({"expected_native_rth": qa["expected_source_bars"],
                           "missing_native_rth": qa["missing_source_bars"],
                           "missing_windows": [w for w in qa["windows"] if not w["complete"]],
                           "native_grid_complete": qa["timing_gate_pass"],
                           "publication": "UNKNOWN"})
    return save_chunk(source.store, frame, params, client.events[event_start:], source.config,
                      coverage_audit=completion)


def pilot(source: MarketSource, client: HistoricalClient) -> dict:
    """Five date-sized probes. Save compact evidence, not a duplicated pilot raw store."""
    days = []
    for day in PILOT_DATES:
        next_day = (pd.Timestamp(day) + pd.Timedelta(days=1)).date().isoformat()
        params = source.interval(day, next_day)
        event_start = len(client.events)
        frame = client.bars(params)
        hours, aggregate = hourly_archive(frame, day, day)
        qa = stock_qa(frame, ["SPY"], day, day)
        days.append({
            "session": day, "params": params, "rows": len(frame),
            "frame_identity": fingerprint(frame.to_json(date_format="iso")),
            "events": client.events[event_start:], "grid": qa["daily"],
            "complete_hours": int((~hours.is_stub).sum()), "stub_count": int(hours.is_stub.sum()),
            "pass": qa["native_session_anchored_gate_pass"] and aggregate["timing_gate_pass"],
            "hourly_samples": hours.iloc[[0, 1, -1]].to_json(orient="records", date_format="iso"),
        })
    return {
        "schema_version": 1, "config_id": source.identity, "source_version": SOURCE_VERSION,
        "decision_id": DECISION_ID, "retrieved_at": now(), "days": days,
        "pilot_pass": all(d["pass"] for d in days),
        "access": "HISTORICAL_SIP_GET_SUCCEEDED; no paid-tier or redistribution attestation",
        "period_timestamp_basis": "LEFT_BOUNDARY; Alpaca FAQ plus exact 30Min grid",
        "publication_asof_verified": False, "scientific_status": "BLOCKED",
    }


def main(argv: list[str] | None = None) -> int:
    """Standalone market-source entry point; old stock/course CLI remains archival/unchanged."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "pilot", "acquire", "qa"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    source = MarketSource.load(args.config)
    if args.command == "acquire" and source.config.get("acquisition_policy_version") == 2:
        from .spy_completion import complete

        return complete(source, args.report, args.env_file)
    if args.command == "plan":
        print(json.dumps({"source": "ALPACA:SIP:SPY", "config_id": source.identity,
                          "partitions": source.partitions(), "research_status": "BLOCKED"},
                         indent=2))
        return 0
    if args.command == "qa":
        write_json(args.report / "source_qa_full_period.json", archive_qa(source))
        return 0
    if args.env_file:
        load_dotenv(args.env_file, override=False)
    key, secret = credentials()
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", args.command,
                           240 if source.config.get("acquisition_policy_version") == 2 else 60)
    client = HistoricalClient(source.config, key, secret, get=budget.get)
    source.store.mkdir(parents=True, exist_ok=True)
    lock = source.store / ".acquire.lock"
    with lock.open("x"):
        pass
    try:
        if args.command == "pilot":
            result = pilot(source, client)
            write_json(args.report / "pilot.json", result)
            return 0 if result["pilot_pass"] else 2
        pilot_path = args.report / "pilot.json"
        evidence = parse_json(pilot_path.read_bytes())
        if (evidence.get("pilot_pass") is not True
                or evidence.get("config_id") != source.identity
                or [d["session"] for d in evidence.get("days", [])] != list(PILOT_DATES)):
            raise ValueError("MATCHING_SPY_PILOT_REQUIRED")
        partitions = source.partitions()
        if len(partitions) > 24 or budget.used + len(partitions) * 4 > 60:
            # A complete resume consumes no new transport calls.
            missing = sum(not chunk_paths(source.store, p)[1].exists() for p in partitions)
            if len(partitions) > 24 or budget.used + missing * 4 > 60:
                raise ValueError("SPY_PLANNED_BUDGET_REQUIRES_REVIEW")
        manifests = [acquire_partition(source, client, p) for p in partitions]
        index = {"source_version": SOURCE_VERSION, "config_id": source.identity,
                 "pilot_sha256": digest(pilot_path), "partitions": [
                     {"path": str(chunk_paths(source.store, m["params"])[0]
                                  .relative_to(source.root)),
                      "sha256": m["sha256"], "rows": m["rows"], "size_bytes": m["size_bytes"]}
                     for m in manifests], "transport_attempts": budget.used,
                 "status": "ACQUIRED_ARCHIVE", "research_status": "BLOCKED"}
        destination = args.report / "archive_index.json"
        if not destination.exists():
            write_json(destination, index)
        print(json.dumps({"status": index["status"], "transport_attempts": budget.used}))
        return 0
    except (DataAccessError, ValueError, FileNotFoundError) as exc:
        write_json(args.report / f"source_failure_{budget.used}.json", {
            "status": "SOURCE_BLOCKED", "command": args.command,
            "reason": str(exc), "config_id": source.identity,
            "transport_attempts": budget.used, "events": client.events,
            "partial_response_saved": False, "scientific_status": "BLOCKED",
        })
        return 2
    finally:
        lock.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
