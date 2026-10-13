"""Candidate-only, training-date SIP screening; no production universe or fits."""

from __future__ import annotations

import hashlib
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import ENDPOINT, DataAccessError, HistoricalClient, credentials, request_params
from .calendar import schedule
from .config import digest, fingerprint, load_config, now, write_json
from .remediation_transport import RemediationTransport, StorageLimit, publish_chunk
from .store import chunk_paths, read_verified
from .universe_screen import t2_absence_bound, verify_screen_authority
from .universe_screen_source import read_backup_chunk
from .validation import require_valid

PACKAGE = "TA-BROAD-UNIVERSE-SCREEN-001"
ARCHIVE = Path("data/raw/alpaca/track_a_broad_candidate_v1")
DATES = ("2021-04-19", "2021-10-25", "2022-01-24", "2022-01-26", "2022-03-08")
GROUPS = {
    "Technology": ("AAPL",),
    "Financials": ("JPM", "BAC", "WFC"),
    "Health Care": ("JNJ", "MRK", "ABT"),
    "Consumer Staples": ("WMT", "COST", "PG"),
    "Consumer Discretionary": ("HD", "MCD", "LOW"),
    "Industrials": ("CAT", "HON", "UPS", "DE"),
    "Energy": ("XOM", "CVX", "COP"),
    "Utilities": ("NEE", "DUK"),
    "Materials": ("LIN", "APD"),
    "Communication Services": ("VZ", "CMCSA", "DIS"),
    "Real Estate": ("PLD", "AMT"),
}
POOL = tuple(symbol for names in GROUPS.values() for symbol in names)
TECH_CONTROLS = ("CSCO", "MSFT", "INTC", "NVDA")
IDENTITY = {"feed": "sip", "adjustment": "split", "currency": "USD", "asof": "2025-06-30"}


def panel_identity(symbols: tuple[str, ...]) -> str:
    """Authorize a hypothetical five-sector identity, never a stock switch."""
    sectors = {symbol: sector for sector, names in GROUPS.items() for symbol in names}
    if (
        len(symbols) != 5
        or len(set(symbols)) != 5
        or symbols[0] != "AAPL"
        or any(symbol not in POOL for symbol in symbols)
        or len({sectors[symbol] for symbol in symbols}) != 5
    ):
        raise ValueError("AAPL_AND_FOUR_DISTINCT_NONTECH_SECTORS_REQUIRED")
    return fingerprint([PACKAGE, symbols, "DIAGNOSTIC_ONLY"])


def mask_intersection(
    masks: dict[str, dict[str, int]], symbols: tuple[str, ...]
) -> tuple[str, ...]:
    """Intersect complete16-channel masks over identical fixed origin populations."""
    panel_identity(symbols)
    if set(symbols) - set(masks) or len({frozenset(masks[s]) for s in symbols}) != 1:
        raise ValueError("COMPLETE_FIVE_NAME_FIXED_ORIGIN_POPULATION_REQUIRED")
    if any(type(v) is not int or not 0 <= v <= 65535 for s in symbols for v in masks[s].values()):
        raise ValueError("SIXTEEN_CHANNEL_INTEGER_MASK_REQUIRED")
    return tuple(sorted(k for k in masks[symbols[0]] if all(masks[s][k] == 65535 for s in symbols)))


def audit_day(frame: pd.DataFrame, symbol: str, day: str) -> dict:
    """Audit exact native starts; never count extended hours or impute prices."""
    require_valid(frame, stocks=True)
    if not (frame.source_timeframe == "30Min").all():
        raise ValueError("NATIVE_30MIN_REQUIRED")
    sessions = schedule(day, day)
    if sessions.empty:
        raise ValueError("ACTUAL_EXCHANGE_SESSION_REQUIRED")
    clock = sessions.iloc[0]
    expected = tuple(pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"))
    group = frame[frame.symbol == symbol]
    rth = group[(group.timestamp >= clock.open) & (group.timestamp < clock.close)]
    found = set(rth.timestamp)
    extra = found - set(expected)
    if extra:
        raise ValueError("OFF_GRID_NATIVE_RTH_SOURCE")
    missing = [t for t in expected if t not in found]
    longest = run = 0
    for stamp in expected:
        run = run + 1 if stamp in missing else 0
        longest = max(longest, run)
    return {
        "symbol": symbol,
        "session_et": day,
        "expected": len(expected),
        "actual": len(found),
        "missing": len(missing),
        "missing_starts_utc": [t.isoformat() for t in missing],
        "terminal_stub_missing": expected[-1] not in found,
        "longest_gap_half_hours": longest,
        "status": "TARGETED_DATES_PASS" if not missing else "OBSERVED_GAP",
        "population": "ZERO_KEYS" if not found else "COMPLETE" if not missing else "PARTIAL",
    }


def read_candidate(store: Path, params: dict) -> tuple[pd.DataFrame, dict] | None:
    """Resume exact immutable query identity, including raw daily price/volume."""
    data, manifest = chunk_paths(store, params)
    if not data.exists() and not manifest.exists():
        return None
    if not data.exists() or not manifest.exists():
        raise ValueError("BROAD_INTERRUPTED_SOURCE_PAIR")
    meta = json.loads(manifest.read_text())
    if (
        meta["params"] != params
        or meta["sha256"] != digest(data)
        or meta["source_version"] != "ALPACA_SIP_SPLIT_REMED_NATIVE_V1"
        or meta["terminal_page_verified"] is not True
    ):
        raise ValueError("BROAD_CACHE_IDENTITY_OR_HASH_MISMATCH")
    frame = pd.read_parquet(data)
    require_valid(frame, stocks=True)
    if len(frame) != meta["rows"] or set(frame.symbol) - set(params["symbols"].split(",")):
        raise ValueError("BROAD_CACHE_POPULATION_MISMATCH")
    if (
        (frame.timestamp < pd.Timestamp(params["start"]))
        | (frame.timestamp > pd.Timestamp(params["end"]))
    ).any():
        raise ValueError("BROAD_CACHE_BOUNDARY_MISMATCH")
    for column, value in (
        ("feed", params["feed"]),
        ("adjustment", params["adjustment"]),
        ("source_timeframe", params["timeframe"]),
        ("provenance_id", fingerprint(params)),
    ):
        if column not in frame or not (frame[column] == value).all():
            raise ValueError("BROAD_CACHE_MATERIAL_METADATA_MISMATCH")
    return frame, meta


def cache_sources() -> list[dict]:
    """Read original months and matching older backup pilots, never confirmation."""
    refs = []
    for store in (
        Path("data/raw/alpaca/track_a"),
        Path("data/raw/alpaca/track_a_backup_candidate_v1/sip_timing_gap_pilot"),
        Path("data/raw/alpaca/track_a_backup_candidate_v1/formation_daily"),
    ):
        for path in sorted(store.glob("*.manifest.json")):
            meta = json.loads(path.read_text())
            params = meta["params"]
            target_months = {day[:7] for day in DATES}
            if params["timeframe"] == "30Min":
                if any(params[k] != v for k, v in IDENTITY.items()):
                    continue
                if pd.Timestamp(params["start"]).strftime("%Y-%m") not in target_months:
                    continue
            elif (
                params["timeframe"] != "1Day"
                or params["asof"] != "2020-07-01"
                or params["adjustment"] != "raw"
            ):
                continue
            data, _ = chunk_paths(store, params)
            if store.name == "track_a":
                read_verified(data, path, params)
            else:
                read_backup_chunk(store, params)
            refs.append(
                {
                    "data": str(data),
                    "manifest": str(path),
                    "sha256": digest(data),
                    "manifest_sha256": digest(path),
                    "params": params,
                    "request_hash": fingerprint(params),
                }
            )
    return refs


def prepare(report: Path) -> dict:
    """Freeze pool, training-only priorities and tiny exact request plan before GETs."""
    verify_screen_authority()
    cfg = load_config(Path("configs/track_a_data.json"))
    refs = cache_sources()
    pool = {
        "package": PACKAGE,
        "symbols": POOL,
        "groups": GROUPS,
        "sector_status": "PROVISIONAL_2020_NOT_CERTIFIED",
        "controls_ineligible": TECH_CONTROLS,
        "formation": "2020-07-01",
        "production_universe_unchanged": True,
        "selection_rule": [
            "formation_evidence",
            "fewer_five_training_date_gaps",
            "source_consistency",
            "four_distinct_nontech_sectors",
            "ticker_ascending",
        ],
        "systemic_stop": (
            "More than half of the28 nontech names have a verified targeted gap; "
            "stop full acquisition"
        ),
        "confirmation": (
            "UNOPENED; resolve full-horizon D1 selection conflict before any later acquisition"
        ),
    }
    write_json(report / "candidate_predeclared_pool.json", pool)
    rows = []
    all_symbols = POOL + TECH_CONTROLS
    for day in DATES:
        start = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
        end = start + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        cached = {
            s
            for ref in refs
            if ref["params"]["timeframe"] == "30Min"
            and pd.Timestamp(ref["params"]["start"]) <= start
            and pd.Timestamp(ref["params"]["end"]) >= end
            for s in ref["params"]["symbols"].split(",")
        }
        params = request_params(
            cfg, [s for s in all_symbols if s not in cached], start.isoformat(), end.isoformat()
        )
        rows.append(
            {
                "kind": "TARGETED_30MIN",
                "params": params,
                "hash": fingerprint(params),
                "max_pages": 4,
            }
        )
    # Same material source identity; native1Hour remains a diagnostic control.
    params = request_params(
        dict(cfg, timeframe="1Hour"),
        ["AAPL", "JPM"],
        "2021-04-19T04:00:00Z",
        "2021-04-20T03:59:59.999999999Z",
    )
    rows.append(
        {
            "kind": "NATIVE_1HOUR_CONTROL",
            "params": params,
            "hash": fingerprint(params),
            "max_pages": 4,
        }
    )
    cached_daily = {
        s
        for ref in refs
        if ref["params"]["timeframe"] == "1Day"
        for s in ref["params"]["symbols"].split(",")
    }
    params = request_params(
        dict(cfg, timeframe="1Day", adjustment="raw", asof="2020-07-01"),
        [s for s in POOL if s not in cached_daily],
        "2020-04-06T04:00:00Z",
        "2020-07-01T03:59:59.999999999Z",
    )
    rows.append(
        {"kind": "FORMATION_DAILY", "params": params, "hash": fingerprint(params), "max_pages": 4}
    )
    plan = {
        "package": PACKAGE,
        "pool_sha256": digest(report / "candidate_predeclared_pool.json"),
        "requests": rows,
        "requests_sha256": fingerprint(rows),
        "cache": refs,
        "limits": {
            "attempts": 1000,
            "sends_per_minute": 100,
            "bytes": 256 * 1024**2,
            "lifetime_attempts_per_page": 3,
        },
        "pilot_worst_page_attempt_envelope": len(rows) * 4 * 3,
        "pilot_max_calendar_rows": 5 * len(all_symbols) * 48 + 60 * len(POOL) + 48 * 2,
        "pilot_estimated_uncompressed_bytes_at128_per_row": (
            5 * len(all_symbols) * 48 + 60 * len(POOL) + 96
        )
        * 128,
        "bulk_preflight": (
            "Deferred until measured targeted density, formation and systemic stop evaluated"
        ),
        "cache_reuse": (
            "Verified containing month/day with SAME material query identity; no Parquet copies"
        ),
    }
    write_json(report / "targeted_request_manifest.json", plan)
    return plan


@dataclass
class BroadTransport(RemediationTransport):
    """One package-wide paced journal; immutable request plan bounds every send."""

    ceiling: int = 1000

    def request(
        self,
        url: str,
        *,
        params: dict,
        headers: dict,
        timeout: float,
        allow_redirects: bool = False,
    ) -> requests.Response:
        base = {k: v for k, v in params.items() if k != "page_token"}
        records = self.records()
        if (
            url != ENDPOINT
            or base not in self.allowed_requests
            or allow_redirects
            or self.ceiling != 1000
        ):
            raise DataAccessError("BROAD_UNAUTHORIZED_REQUEST")
        if any(
            r.get("status") in (401, 403, 429)
            or r["kind"] == "HOLD"
            or r.get("schema") == "DIVERGENCE"
            for r in records
        ):
            raise DataAccessError("BROAD_PROVIDER_OR_SCHEMA_HOLD")
        if records and records[-1]["kind"] == "ATTEMPT":
            raise DataAccessError("BROAD_UNRESOLVED_PRIOR_ATTEMPT")
        page_id = fingerprint(params)
        if (
            self.used >= self.ceiling
            or sum(r["kind"] == "ATTEMPT" and r["page_hash"] == page_id for r in records) >= 3
        ):
            raise DataAccessError("BROAD_ATTEMPT_BUDGET_OR_PAGE_LIMIT")
        attempts = [r for r in records if r["kind"] == "ATTEMPT"]
        if attempts:
            elapsed = (pd.Timestamp(now()) - pd.Timestamp(attempts[-1]["time_utc"])).total_seconds()
            time.sleep(max(0.0, 0.6 - elapsed))
        attempt = self.used + 1
        self.append(
            {
                "kind": "ATTEMPT",
                "package": PACKAGE,
                "attempt_id": attempt,
                "page_hash": page_id,
                "request_hash": fingerprint(base),
                "params": base,
                "endpoint": ENDPOINT,
                "continued_page": "page_token" in params,
                "time_utc": now(),
            }
        )
        try:
            response = self.get(
                url, params=params, headers=headers, timeout=timeout, allow_redirects=False
            )
        except requests.RequestException:
            self.append(
                {
                    "kind": "RESULT",
                    "attempt_id": attempt,
                    "status": "TRANSPORT_ERROR",
                    "time_utc": now(),
                }
            )
            raise requests.ConnectionError("BROAD_TRANSPORT_ERROR") from None
        receipt = {
            "kind": "RESULT",
            "attempt_id": attempt,
            "status": response.status_code,
            "bytes": len(response.content),
            "response_sha256": hashlib.sha256(response.content).hexdigest(),
            "request_hash": fingerprint(base),
            "time_utc": now(),
        }
        if response.status_code == 200:
            try:
                payload = response.json()
                bars = payload.get("bars") if isinstance(payload, dict) else None
                if (
                    not isinstance(bars, dict)
                    or set(bars) - set(base["symbols"].split(","))
                    or any(not isinstance(v, list) for v in bars.values())
                ):
                    receipt["schema"] = "DIVERGENCE"
                else:
                    receipt["returned_rows"] = sum(len(v) for v in bars.values())
                    receipt["terminal_page"] = not bool(payload.get("next_page_token"))
            except ValueError:
                receipt["schema"] = "DIVERGENCE"
        self.append(receipt)
        if receipt.get("schema") == "DIVERGENCE" or response.status_code in (401, 403, 429):
            raise DataAccessError("BROAD_HTTP_OR_SCHEMA_HOLD")
        return response


def acquire(report: Path, *, env_file: Path = Path(".env"), get=requests.get) -> dict:
    """Acquire only frozen five training dates, one hourly control and formation60."""
    verify_screen_authority()
    plan = json.loads((report / "targeted_request_manifest.json").read_text())
    if (
        plan["package"] != PACKAGE
        or fingerprint(plan["requests"]) != plan["requests_sha256"]
        or digest(report / "candidate_predeclared_pool.json") != plan["pool_sha256"]
    ):
        raise ValueError("BROAD_PREQUERY_PLAN_CHANGED")
    for row in plan["requests"]:
        p = row["params"]
        start, end = pd.Timestamp(p["start"]), pd.Timestamp(p["end"])
        day = start.tz_convert("America/New_York").strftime("%Y-%m-%d")
        if (
            row["kind"] not in {"TARGETED_30MIN", "NATIVE_1HOUR_CONTROL", "FORMATION_DAILY"}
            or p["feed"] != "sip"
            or p["currency"] != "USD"
            or p["limit"] != 10000
            or p["sort"] != "asc"
            or set(p["symbols"].split(",")) - set(POOL + TECH_CONTROLS)
            or not 1 <= row["max_pages"] <= 4
            or fingerprint(p) != row["hash"]
        ):
            raise ValueError("BROAD_FIXED_SOURCE_SCOPE_REQUIRED")
        if row["kind"] == "NATIVE_1HOUR_CONTROL" and (
            p["symbols"] != "AAPL,JPM" or day != "2021-04-19"
        ):
            raise ValueError("BROAD_FIXED_NATIVE_HOURLY_CONTROL_REQUIRED")
        if row["kind"] == "FORMATION_DAILY":
            if (
                p["timeframe"] != "1Day"
                or p["adjustment"] != "raw"
                or p["asof"] != "2020-07-01"
                or start != pd.Timestamp("2020-04-06T04:00Z")
                or end != pd.Timestamp("2020-07-01T03:59:59.999999999Z")
            ):
                raise ValueError("BROAD_FORMATION_ONLY_REQUIRED")
        elif (
            day not in DATES
            or end - start != pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
            or any(p[k] != v for k, v in IDENTITY.items())
            or p["timeframe"] != ("1Hour" if row["kind"] == "NATIVE_1HOUR_CONTROL" else "30Min")
        ):
            raise ValueError("BROAD_TRAINING_DATES_ONLY_REQUIRED")
    limit = StorageLimit((ARCHIVE, report))
    journal = ARCHIVE / "transport_attempts.jsonl"
    transport = BroadTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    cfg = load_config(Path("configs/track_a_data.json"))
    loaded = False
    key = secret = ""
    chunks = []
    for row in plan["requests"]:
        params = row["params"]
        store = ARCHIVE / row["kind"].lower()
        saved = read_candidate(store, params)
        if saved is None:
            if not loaded:
                load_dotenv(env_file, override=False)
                key, secret = credentials()
                loaded = True
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(cfg["retry"], max_attempts=3, requests_per_minute=100),
                ),
                key,
                secret,
                get=transport.request,
            )
            begin = len(transport.records())
            try:
                frame = client.bars(params)
            except (DataAccessError, ValueError):
                transport.append(
                    {
                        "kind": "HOLD",
                        "reason": "CLIENT_OR_PAGINATION_HOLD",
                        "request_hash": row["hash"],
                        "time_utc": now(),
                    }
                )
                raise DataAccessError("BROAD_SOURCE_HOLD") from None
            meta = publish_chunk(
                store, frame, params, transport.records()[begin:], kind=row["kind"], limit=limit
            )
            resumed = False
        else:
            frame, meta = saved
            resumed = True
        data, manifest = chunk_paths(store, params)
        chunks.append(
            {
                "kind": row["kind"],
                "params": params,
                "rows": len(frame),
                "resumed": resumed,
                "data": str(data),
                "manifest": str(manifest),
                "sha256": meta["sha256"],
                "manifest_sha256": digest(manifest),
                "request_hash": row["hash"],
            }
        )
    return {
        "package": PACKAGE,
        "chunks": chunks,
        "attempts": transport.used,
        "journal": str(journal),
        "journal_sha256": digest(journal),
        "bytes": limit.used,
        "scientific_activation": False,
    }


def known_close_bounds(rows: list[dict]) -> dict:
    """Necessary T2 loss unions only; no fictional prices, feature fits or validity."""
    from .stock_source import StockCalendar

    calendar = StockCalendar("2019-12-18", "2023-06-30")
    failed = {}
    for symbol in POOL:
        absent = tuple(
            r["session_et"] for r in rows if r["symbol"] == symbol and r["terminal_stub_missing"]
        )
        failed[symbol] = t2_absence_bound(calendar, absent)
    loss_keys = {s: {(r["session"], r["origin"]) for r in items} for s, items in failed.items()}
    best = []
    counts = {}
    total = 0
    sectors = tuple(GROUPS)[1:]
    maximum = -1
    for sector_set in itertools.combinations(sectors, 4):
        for names in itertools.product(*(GROUPS[s] for s in sector_set)):
            symbols = ("AAPL",) + names
            losses = set().union(*(loss_keys[s] for s in symbols))
            upper = 1502 - len(losses)
            total += 1
            counts[upper] = counts.get(upper, 0) + 1
            if upper > maximum:
                maximum, best = upper, []
            if upper == maximum and len(best) < 20:
                best.append(
                    {
                        "symbols": symbols,
                        "sectors": ("Technology",) + sector_set,
                        "optimistic_T2_upper": upper,
                        "denominator": 1502,
                        "necessary_losses": len(losses),
                        "measured_retention": None,
                    }
                )
    return {
        "scope": "COUNTERFACTUAL_NECESSARY_T2_BOUND_ONLY",
        "failed_origins_by_symbol": failed,
        "panels_enumerated": total,
        "upper_bound_distribution": counts,
        "best_bound_examples": best,
        "maximum_upper": maximum,
        "required": 1352,
        "denominator": 1502,
        "measured_candidate_panels": 0,
        "all_other_closes_assumed_present_for_bound_only": True,
        "source_available_at": "UNKNOWN",
        "scientific_status": "HOLD",
    }


def analyze(report: Path) -> dict:
    """Publish exact five-date keys, formation proxies and honest partial evidence."""
    plan = json.loads((report / "targeted_request_manifest.json").read_text())
    result = json.loads((report / "acquisition_results.json").read_text())
    refs = plan["cache"] + result["chunks"]
    frames = {}
    for ref in refs:
        data = Path(ref["data"])
        if digest(data) != ref["sha256"] or digest(Path(ref["manifest"])) != ref["manifest_sha256"]:
            raise ValueError("BROAD_SOURCE_CHANGED_AFTER_PLAN")
        frames[str(data)] = pd.read_parquet(data)
    rows = []
    for day in DATES:
        start = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
        end = start + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        for symbol in POOL + TECH_CONTROLS:
            matched = [
                r
                for r in refs
                if r["params"]["timeframe"] == "30Min"
                and symbol in r["params"]["symbols"].split(",")
                and pd.Timestamp(r["params"]["start"]) <= start
                and pd.Timestamp(r["params"]["end"]) >= end
            ]
            if len(matched) != 1:
                raise ValueError("BROAD_ONE_AUTHENTIC_SOURCE_PER_SYMBOL_DATE_REQUIRED")
            ref = matched[0]
            audit = audit_day(frames[ref["data"]], symbol, day)
            audit.update(
                source=ref["data"],
                source_sha256=ref["sha256"],
                request_hash=ref["request_hash"],
                eligible_candidate=symbol in POOL,
                sector=next(
                    (s for s, names in GROUPS.items() if symbol in names), "Technology_CONTROL_ONLY"
                ),
            )
            rows.append(audit)
    original = pd.read_csv(
        "reports/data_audit/ta_exact_missing_candles_2026-10-12_103916/missing_candles.csv"
    )
    actual_missing = {
        (r["symbol"], t)
        for r in rows
        if r["symbol"] in ("AAPL", "JPM", "JNJ", "WMT", "CAT")
        for t in r["missing_starts_utc"]
    }
    ledger_missing = {
        (r.symbol, pd.Timestamp(str(r.start_utc)).isoformat()) for r in original.itertuples()
    }
    if (
        actual_missing != ledger_missing
        or len(actual_missing) != 168
        or original.cluster_id.nunique() != 15
    ):
        raise ValueError("BROAD_ORIGINAL_168_KEYS_15_CLUSTERS_DIFFER")
    write_json(report / "five_date_exact_keys.json", rows)
    pd.DataFrame(
        [dict(r, missing_starts_utc=" | ".join(r["missing_starts_utc"])) for r in rows]
    ).to_csv(report / "five_date_30min_screen.csv", index=False)
    summary = []
    for symbol in POOL + TECH_CONTROLS:
        stock = [r for r in rows if r["symbol"] == symbol]
        missing = sum(r["missing"] for r in stock)
        summary.append(
            {
                "symbol": symbol,
                "sector": stock[0]["sector"],
                "candidate": symbol in POOL,
                "expected": sum(r["expected"] for r in stock),
                "actual": sum(r["actual"] for r in stock),
                "missing": missing,
                "missing_stub_dates": [
                    r["session_et"] for r in stock if r["terminal_stub_missing"]
                ],
                "status": "TARGETED_DATES_ONLY" if not missing else "MEASURED_FAIL_TARGETED_GRID",
                "formation": "FORMATION_INCONCLUSIVE",
                "full_history": "DATA_NOT_MEASURED",
            }
        )
    write_json(report / "screen_summary.json", summary)
    bounds = known_close_bounds(rows)
    write_json(report / "panel_overlap_loss_attribution.json", bounds)
    formation = []
    dates = tuple(str(t.date()) for t in schedule("2020-04-06", "2020-06-30").index)
    if len(dates) != 60:
        raise ValueError("EXACT_PRIOR60_SESSIONS_REQUIRED")
    for symbol in POOL:
        matched = [
            r
            for r in refs
            if r["params"]["timeframe"] == "1Day" and symbol in r["params"]["symbols"].split(",")
        ]
        if len(matched) != 1:
            raise ValueError("ONE_FORMATION_SOURCE_REQUIRED")
        ref = matched[0]
        source = frames[ref["data"]]
        daily = source[source.symbol == symbol].copy()
        daily["session"] = daily.timestamp.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
        valid = (
            len(daily) == 60
            and set(daily.session) == set(dates)
            and not daily.session.duplicated().any()
        )
        mean = float((daily.close * daily.volume).mean()) if valid else None
        formation.append(
            {
                "symbol": symbol,
                "sector_provisional": next(s for s, names in GROUPS.items() if symbol in names),
                "expected_sessions": 60,
                "actual_sessions": len(daily),
                "mean_close_vendor_volume_USD": mean,
                "liquidity_proxy_status": "PROXY_ONLY"
                if mean is not None and mean >= 50_000_000
                else "FAIL"
                if mean is not None
                else "NOT_VERIFIED",
                "formation_status": "FORMATION_INCONCLUSIVE",
                "historical_membership": "NOT_VERIFIED",
                "historical_GICS": "NOT_VERIFIED",
                "historical_publication": "UNKNOWN",
                "index_weight_2020": "NOT_MEASURED",
                "action_vintage": "UNVERIFIED",
                "source": ref["data"],
                "source_sha256": ref["sha256"],
                "request_hash": ref["request_hash"],
            }
        )
    pd.DataFrame(formation).to_csv(report / "formation_eligibility.csv", index=False)
    affected = sum(s["missing"] > 0 for s in summary if s["candidate"] and s["symbol"] != "AAPL")
    systemic = affected > 14
    shortlist = sorted(
        (s for s in summary if s["candidate"] and s["symbol"] != "AAPL"),
        key=lambda s: (s["missing"], s["symbol"]),
    )
    write_json(
        report / "training_only_shortlist.json",
        {
            "rule": (
                "Identical uncertain formation status; five-date missing keys then ticker; "
                "provisional sectors"
            ),
            "targeted_priority": shortlist,
            "full_acquisition_selected": [],
            "affected_nontech": affected,
            "nontech_denominator": 28,
            "systemic_stop": systemic,
            "status": "SOURCE_BLOCKED_NO_FULL_ACQUISITION"
            if systemic
            else "REQUIRES_FORMATION_AND_BULK_PREFLIGHT",
            "confirmation_unopened": True,
            "no_measured_full_panel_rank": True,
        },
    )
    # Do not disguise a conditional bound as a measured five-stock retention rate.
    pd.DataFrame(
        [
            dict(
                r,
                symbols=",".join(r["symbols"]),
                sectors=" | ".join(r["sectors"]),
                status="DATA_NOT_MEASURED",
                approval="REQUIRES_VERSIONED_D1_AMENDMENT",
            )
            for r in bounds["best_bound_examples"]
        ]
    ).to_csv(report / "candidate_panel_comparison.csv", index=False)
    pd.DataFrame(
        [
            dict(
                symbol=s["symbol"],
                train_denominator=1502,
                measured_train_numerator=None,
                targeted_T2_necessary_failures=len(bounds["failed_origins_by_symbol"][s["symbol"]]),
                status="DATA_NOT_MEASURED",
            )
            for s in summary
            if s["candidate"]
        ]
    ).to_csv(report / "per_stock_retention.csv", index=False)
    pd.DataFrame(
        [
            dict(
                symbol=s["symbol"],
                overall_threshold=0.98,
                yearly_threshold=0.95,
                overall_coverage=None,
                annual_coverage=None,
                status="DATA_NOT_MEASURED",
                reason="TARGETED_DATES_ONLY; full horizon and confirmation not opened",
            )
            for s in summary
            if s["candidate"]
        ]
    ).to_csv(report / "full_history_source_qa.csv", index=False)
    write_json(
        report / "immutable_source_manifest.json",
        {
            "package": PACKAGE,
            "references": refs,
            "new_attempts": result["attempts"],
            "journal": result["journal"],
            "journal_sha256": result["journal_sha256"],
            "existing_source_copies": 0,
            "original_168_keys_15_clusters": "RECHECKED_IDENTICAL",
            "available_at": "UNKNOWN",
            "source_activation": False,
        },
    )
    return {
        "affected_nontech": affected,
        "denominator_nontech": 28,
        "systemic_stop": systemic,
        "best_optimistic_T2_upper": bounds["maximum_upper"],
        "panels_bound_only": bounds["panels_enumerated"],
        "new_attempts": result["attempts"],
        "candidate_panels_measured": 0,
    }
