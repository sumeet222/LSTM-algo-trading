"""Genuine candidate archive adapter with a strict preconfirmation numeric barrier."""
from __future__ import annotations

import json

import pandas as pd
import pyarrow.parquet as pq

from .aggregation import aggregate_session_hours
from .config import digest, fingerprint
from .pretraining_policy import CANDIDATE, PreparationAuthority, local_path, verify_ref
from .stock_source import StockBar, StockCalendar, StockDaily, StockHistory, numeric

BARRIER = pd.Timestamp("2024-07-01", tz="America/New_York").tz_convert("UTC")
FIRST = "2019-12-18"
LAST = "2024-06-30"
COLUMNS = ["symbol", "timestamp", "open", "high", "low", "close", "volume",
           "trade_count", "source_timeframe", "feed", "adjustment", "provenance_id"]


class ConditionalHistory(StockHistory):
    """Idealized study access; UNKNOWN observed clocks/actions are never overwritten.

    This is not a StockHistory scientific certificate. Legacy source_reason,
    real model permissions and raw-price proxy_reference still reject these bars.
    """

    def __init__(self, calendar: StockCalendar, bars: tuple[StockBar, ...],
                 authority: PreparationAuthority):
        authority.ensure("SOURCE_PREPARATION")
        self.authority = authority
        super().__init__(calendar, bars, universe=CANDIDATE)
        self.binding = fingerprint([self.binding, authority.binding, "IDEAL_CLOCK_CANDIDATE_ONLY"])
        self.action_binding = fingerprint([self.action_binding, authority.binding,
                                           "RETROSPECTIVE_UNVERIFIED_ACTION_VINTAGE"])

    def source_status(self, row: StockBar | None, cutoff: pd.Timestamp) -> str:
        if row is None:
            return "SOURCE_MISSING"
        if (
            row.universe != CANDIDATE or row.basis != "ASSUMED"
            or row.evidence_ref != self.authority.binding or row.action_verified
            or row.available_at is not None or row.action_known_at is not None
            or row.price_basis != "SPLIT_CONSISTENT"
            or row.action_ref != "RETROSPECTIVE_VENDOR_ADJUSTMENT_UNVERIFIED_VINTAGE"
        ):
            return "CONDITIONAL_SOURCE_POLICY_MISMATCH"
        if row.end >= BARRIER or row.end > cutoff:
            return "NOT_AVAILABLE_ON_IDEAL_STEP_CLOCK"
        if cutoff - row.end > pd.Timedelta(minutes=90):
            return "STALE_STOCK_SOURCE"
        return "SOURCE_VALID"

    def day(self, symbol: str, day: str, cutoff: pd.Timestamp, *, volume: bool = False,
            source_only: bool = False) -> StockDaily | None:
        # Daily source evidence remains UNKNOWN. Only the approved idealized clock
        # permits completed *prior* sessions, never a current partial daily close.
        row = self.daily.get((symbol, day))
        if row is None or row.end > cutoff or row.end >= BARRIER:
            return None
        value = row.volume if volume else row.close
        if value is None or row.basis != "ASSUMED" or row.action_verified:
            return None
        return row


def read_native(authority: PreparationAuthority) -> tuple[pd.DataFrame, dict]:
    """Verify bytes/requests before filtered Arrow reads; never materialize confirmation OHLCV."""
    authority.ensure("SOURCE_PREPARATION")
    manifest_path = verify_ref(authority.root, authority.policy["source_manifest"])
    manifest = json.loads(manifest_path.read_text())
    if tuple(manifest["ordered_universe"]) != CANDIDATE:
        raise ValueError("CANDIDATE_ORDER_CHANGED")
    selected: dict[str, dict] = {}
    for symbol in CANDIDATE:
        for ref in manifest["source_by_stock"][symbol]:
            selected[ref["data"]] = ref
    frames, audit = [], []
    lower = pd.Timestamp(FIRST, tz="America/New_York").tz_convert("UTC")
    for name, ref in sorted(selected.items()):
        data = local_path(authority.root, name)
        meta_path = local_path(authority.root, ref["manifest"])
        if digest(data) != ref["sha256"] or digest(meta_path) != ref["manifest_sha256"]:
            raise ValueError("IMMUTABLE_NATIVE_ARCHIVE_CHANGED")
        meta = json.loads(meta_path.read_text())
        params = meta["params"]
        if (params != ref["params"] or meta.get("sha256") != ref["sha256"]
                or any(params.get(k) != v for k, v in
                       {"feed": "sip", "adjustment": "split", "asof": "2025-06-30",
                        "timeframe": "30Min", "currency": "USD"}.items())):
            raise ValueError("NATIVE_REQUEST_PRICE_UNIT_OR_SOURCE_CHANGED")
        if data.parent.name != "track_a" and (
            meta.get("source_version") != "ALPACA_SIP_SPLIT_REMED_NATIVE_V1"
            or meta.get("terminal_page_verified") is not True
        ):
            raise ValueError("GENUINE_COMPLETED_NATIVE_SOURCE_REQUIRED")
        if pd.Timestamp(params["start"]) >= BARRIER:
            audit.append({"data": name, "numeric_rows_read": 0, "barrier": "HASH_SCHEMA_ONLY"})
            continue
        # Arrow applies the date/symbol predicate before conversion to a pandas
        # financial frame, including files straddling the protected boundary.
        table = pq.read_table(data, columns=COLUMNS,
                              filters=[("timestamp", ">=", lower.to_pydatetime()),
                                       ("timestamp", "<", BARRIER.to_pydatetime()),
                                       ("symbol", "in", list(CANDIDATE))])
        frame = table.to_pandas()
        if not frame.empty:
            if (frame.timestamp >= BARRIER).any():
                raise ValueError("CONFIRMATION_NUMERIC_ACCESS_FORBIDDEN")
            if not (frame.source_timeframe.eq("30Min") & frame.feed.eq("sip")
                    & frame.adjustment.eq("split")).all():
                raise ValueError("NATIVE_ROW_UNIT_MISMATCH")
            frame["archive_sha256"] = ref["sha256"]
            frames.append(frame)
        audit.append({"data": name, "sha256": ref["sha256"],
                      "manifest_sha256": ref["manifest_sha256"],
                      "numeric_rows_read": len(frame), "barrier": "PRECONFIRMATION_ONLY"})
    if not frames:
        raise ValueError("GENUINE_PRECONFIRMATION_NATIVE_ROWS_REQUIRED")
    native = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])
    if native.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("DUPLICATE_NATIVE_KEY_NO_OVERLAY_ALLOWED")
    return native, {"archive_pairs": len(selected), "references": audit,
                    "numeric_rows_read": len(native), "confirmation_numeric_rows": 0}


def load_history(authority: PreparationAuthority) -> tuple[ConditionalHistory, dict]:
    native, audit = read_native(authority)
    hourly, qa = aggregate_session_hours(native, list(CANDIDATE), FIRST, LAST)
    if qa["missing_source_bars"]:
        raise ValueError("INCOMPLETE_NATIVE_CANDIDATE_NO_FILL_ALLOWED")
    calendar = StockCalendar(FIRST, LAST)
    raw_ids = {}
    for r in native.itertuples():
        if not isinstance(r.timestamp, pd.Timestamp) or not isinstance(r.symbol, str):
            raise ValueError("NATIVE_SOURCE_KEY_TYPE_REQUIRED")
        raw_ids[r.symbol, r.timestamp] = fingerprint(
            [r.archive_sha256, r.provenance_id, r.symbol, r.timestamp.isoformat()]
        )
    bars = []
    for row in hourly.itertuples():
        start, end = row.timestamp, row.available_at
        if (not isinstance(start, pd.Timestamp) or not isinstance(end, pd.Timestamp)
                or not isinstance(row.symbol, str) or not isinstance(row.session, str)):
            raise ValueError("EXACT_NATIVE_HOURLY_KEY_REQUIRED")
        clock = calendar.clock(row.session)
        slot = 0 if row.is_stub else next(i for i, h in enumerate(clock.hours, 1) if h.end == end)
        ids = tuple(raw_ids[row.symbol, t] for t in
                    pd.date_range(start, end, freq="30min", inclusive="left"))
        bars.append(StockBar(
            row.symbol, row.session, slot, start, end,
            *(numeric(x) for x in (row.open, row.high, row.low, row.close, row.volume)),
            source_ids=ids, basis="ASSUMED", available_at=None, action_verified=False,
            action_ref="RETROSPECTIVE_VENDOR_ADJUSTMENT_UNVERIFIED_VINTAGE",
            evidence_ref=authority.binding, universe=CANDIDATE,
        ))
    audit.update({k: qa[k] for k in ("expected_source_bars", "missing_source_bars",
                                    "complete_windows", "expected_stub_windows")})
    audit.update({"observed_publication": "UNKNOWN", "idealized_clock": "APPROVAL_BOUND",
                  "inserted_candles": 0, "strict_observed_certification": False})
    return ConditionalHistory(calendar, tuple(bars), authority), audit
