"""New-task, bounded SIP-only backup transport; immutable candidate archive only."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import ENDPOINT, DataAccessError, HistoricalClient, credentials, request_params
from .config import digest, fingerprint, load_config, now
from .remediation_plan import dependency_calendar
from .remediation_transport import RemediationTransport, StorageLimit, publish_chunk
from .store import chunk_paths
from .universe_screen import BACKUPS, PACKAGE, verify_screen_authority
from .validation import normalize, require_valid

ARCHIVE = Path("data/raw/alpaca/track_a_backup_candidate_v1")


def read_backup_chunk(store: Path, params: dict) -> tuple[pd.DataFrame, dict] | None:
    """Verify true raw controls/daily bars as well as split native bars, without GETs.

    The original remediation reader deliberately requires split adjustment. This
    isolated reader preserves that contract and verifies the actual new request.
    """
    if (
        params["feed"] != "sip"
        or set(params["symbols"].split(",")) - set(BACKUPS)
        or pd.Timestamp(params["end"]) >= pd.Timestamp("2024-07-01T04:00Z")
    ):
        raise ValueError("SCREEN_READ_SCOPE_REQUIRED")
    data, manifest = chunk_paths(store, params)
    if not data.exists() and not manifest.exists():
        return None
    if not data.exists() or not manifest.exists():
        raise ValueError("SCREEN_INTERRUPTED_CHUNK_PAIR")
    meta = json.loads(manifest.read_text())
    if (
        meta["params"] != params
        or meta["sha256"] != digest(data)
        or meta["source_version"] != "ALPACA_SIP_SPLIT_REMED_NATIVE_V1"
        or not meta["terminal_page_verified"]
        or pd.Timestamp(params["end"]) >= pd.Timestamp("2024-07-01T04:00Z")
    ):
        raise ValueError("SCREEN_CHUNK_SOURCE_OR_BOUNDARY_MISMATCH")
    frame = normalize(pd.read_parquet(data), stocks=True)
    require_valid(frame, stocks=True)
    if len(frame) != meta["rows"] or set(frame.symbol) - set(params["symbols"].split(",")):
        raise ValueError("SCREEN_CHUNK_ROWS_OR_SYMBOLS_MISMATCH")
    if (
        (frame.timestamp < pd.Timestamp(params["start"]))
        | (frame.timestamp > pd.Timestamp(params["end"]))
    ).any():
        raise ValueError("SCREEN_CHUNK_BOUNDS_MISMATCH")
    for column, expected in (
        ("feed", "sip"),
        ("adjustment", params["adjustment"]),
        ("source_timeframe", params["timeframe"]),
        ("provenance_id", fingerprint(params)),
    ):
        if column not in frame or not (frame[column] == expected).all():
            raise ValueError("SCREEN_CHUNK_METADATA_MISMATCH")
    return frame, meta


@dataclass
class ScreenTransport(RemediationTransport):
    """Reuse durable journal primitives, isolated 1000-attempt authorization boundary."""

    ceiling: int = 1000
    exception_ref: Path | None = None

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
        page_id = fingerprint(params)
        records = self.records()
        if (
            url != ENDPOINT
            or base not in self.allowed_requests
            or allow_redirects
            or self.ceiling != 1000
        ):
            raise DataAccessError("SCREEN_UNAUTHORIZED_REQUEST")
        if any(
            r.get("status") in (401, 403, 429)
            or r.get("schema") == "DIVERGENCE"
            or r["kind"] == "HOLD"
            for r in records
        ):
            raise DataAccessError("SCREEN_PROVIDER_HOLD_NO_FURTHER_SEND")
        if self.used >= self.ceiling:
            raise DataAccessError("SCREEN_ATTEMPT_CEILING")
        page_limit = 3
        if self.exception_ref is not None:
            exception = json.loads(self.exception_ref.read_text())
            prefix = b"".join(self.journal.read_bytes().splitlines(keepends=True)[:6])
            if (
                exception["package"] != PACKAGE
                or exception["approved"] is not True
                or exception["additional_attempts"] != 1
                or hashlib.sha256(prefix).hexdigest() != exception["journal_prefix_sha256"]
                or len(records[:6]) != 6
                or any(
                    r.get("status") != "TRANSPORT_ERROR"
                    for r in records[:6]
                    if r["kind"] == "RESULT"
                )
            ):
                raise DataAccessError("SCREEN_EXCEPTION_AUTHORITY_CHANGED")
            if page_id == exception["page_hash"]:
                page_limit = 4
        if sum(r["kind"] == "ATTEMPT" and r["page_hash"] == page_id for r in records) >= page_limit:
            raise DataAccessError("SCREEN_PAGE_LIFETIME_CEILING")
        attempt = self.used + 1
        self.append(
            {
                "kind": "ATTEMPT",
                "package": PACKAGE,
                "attempt_id": attempt,
                "page_hash": page_id,
                "request_hash": fingerprint(base),
                "params": base,
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
            raise requests.ConnectionError("SCREEN_TRANSPORT_ERROR") from None
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
                if isinstance(payload, dict) and isinstance(payload.get("bars"), dict):
                    if set(payload["bars"]) - set(base["symbols"].split(",")) or any(
                        not isinstance(v, list) for v in payload["bars"].values()
                    ):
                        receipt["schema"] = "DIVERGENCE"
                    receipt["returned_rows"] = sum(
                        len(v) for v in payload["bars"].values() if isinstance(v, list)
                    )
                    receipt["terminal_page"] = not bool(payload.get("next_page_token"))
                else:
                    receipt["schema"] = "DIVERGENCE"
            except ValueError:
                receipt["schema"] = "DIVERGENCE"
        self.append(receipt)
        if receipt.get("schema") == "DIVERGENCE":
            raise DataAccessError("SCREEN_SOURCE_SCHEMA_HOLD")
        if response.status_code in (401, 403, 429):
            raise DataAccessError(f"SCREEN_HTTP_{response.status_code}_HOLD")
        return response


def pilot_plan() -> dict:
    cfg = load_config(Path("configs/track_a_data.json"))
    requests_list = []

    def add(kind, symbols, start, stop, timeframe="30Min", adjustment="split", asof="2025-06-30"):
        params = request_params(
            dict(cfg, timeframe=timeframe, adjustment=adjustment, asof=asof),
            list(symbols),
            start,
            stop,
        )
        requests_list.append(
            {"kind": kind, "params": params, "hash": fingerprint(params), "max_pages": 4}
        )

    add(
        "FORMATION_DAILY",
        BACKUPS,
        "2020-04-06T04:00:00Z",
        "2020-07-01T03:59:59.999999999Z",
        "1Day",
        "raw",
        "2020-07-01",
    )
    for day in (
        "2021-04-19",
        "2021-10-25",
        "2022-03-08",
        "2022-01-24",
        "2020-11-27",
        "2021-03-15",
        "2019-12-18",
    ):
        lo = pd.Timestamp(day, tz="America/New_York")
        hi = lo + pd.Timedelta(days=1)
        add(
            "SIP_TIMING_GAP_PILOT",
            BACKUPS,
            lo.tz_convert("UTC").isoformat(),
            (hi.tz_convert("UTC") - pd.Timedelta(nanoseconds=1)).isoformat(),
        )
    # A raw/split same-key control on the earliest necessary history boundary.
    add(
        "RAW_SPLIT_CONTROL",
        BACKUPS,
        "2019-12-18T05:00:00Z",
        "2019-12-19T04:59:59.999999999Z",
        adjustment="raw",
    )
    return {
        "package": PACKAGE,
        "phase": "B_PILOT",
        "archive": str(ARCHIVE),
        "requests": requests_list,
        "requests_sha256": fingerprint(requests_list),
        "limits": {"new_attempts": 1000, "lifetime_attempts_per_page": 3, "bytes": 256 * 1024**2},
        "pilot_attempt_envelope": len(requests_list) * 4 * 3,
        "dependency_calendar": dependency_calendar(),
        "no_confirmation": True,
        "scientific_activation": False,
        "prior_source_journals_unchanged": True,
    }


def acquire_requests(
    report: Path, plan: dict, *, env_file: Path = Path(".env"), get=requests.get
) -> dict:
    verify_screen_authority()
    if plan["package"] != PACKAGE or fingerprint(plan["requests"]) != plan["requests_sha256"]:
        raise ValueError("SCREEN_PLAN_BINDING_CHANGED")
    for row in plan["requests"]:
        params = row["params"]
        if (
            set(params["symbols"].split(",")) - set(BACKUPS)
            or params["feed"] != "sip"
            or params["timeframe"] not in {"30Min", "1Day"}
            or params["adjustment"] not in {"raw", "split"}
            or params["currency"] != "USD"
            or params["asof"] not in {"2020-07-01", "2025-06-30"}
            or pd.Timestamp(params["start"]) < pd.Timestamp("2019-12-18T05:00Z")
            or pd.Timestamp(params["end"]) >= pd.Timestamp("2024-07-01T04:00Z")
            or params["limit"] != 10000
            or not 1 <= row["max_pages"] <= 8
        ):
            raise ValueError("PREDECLARED_BACKUP_SOURCE_SCOPE_REQUIRED")
    limits = StorageLimit((ARCHIVE, report))
    journal = ARCHIVE / "transport_attempts.jsonl"
    transport = ScreenTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limits.reserve,
        exception_ref=(report / "formation_transport_exception_v1.json")
        if (report / "formation_transport_exception_v1.json").exists()
        else None,
    )
    # Only load credentials if at least one complete chunk is missing.
    cfg = load_config(Path("configs/track_a_data.json"))
    loaded = False
    key = secret = ""
    output = []
    for row in plan["requests"]:
        params = row["params"]
        store = ARCHIVE / row["kind"].lower()
        saved = read_backup_chunk(store, params)
        if saved is None:
            if not loaded:
                load_dotenv(env_file, override=False)
                key, secret = credentials()
                loaded = True
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(
                        cfg["retry"],
                        max_attempts=1 if row["kind"] == "FORMATION_DAILY" else 3,
                        max_seconds=10,
                    ),
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
                        "reason": "CLIENT_VALIDATION_OR_TRANSPORT_HOLD",
                        "request_hash": row["hash"],
                        "time_utc": now(),
                    }
                )
                raise DataAccessError("SCREEN_SOURCE_OR_PAGINATION_HOLD") from None
            meta = publish_chunk(
                store, frame, params, transport.records()[begin:], kind=row["kind"], limit=limits
            )
            resumed = False
        else:
            frame, meta = saved
            resumed = True
        output.append(
            {
                "hash": row["hash"],
                "kind": row["kind"],
                "params": params,
                "manifest": meta,
                "resumed": resumed,
                "rows": len(frame),
            }
        )
    return {
        "package": PACKAGE,
        "attempts": transport.used,
        "journal_sha256": digest(journal) if journal.exists() else None,
        "journal": str(journal),
        "archive": str(ARCHIVE),
        "bytes": limits.used,
        "chunks": output,
        "scientific_activation": False,
    }
