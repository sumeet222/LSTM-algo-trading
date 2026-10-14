"""Sparse causal placeholders for engineering only; never genuine source evidence."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .calendar import schedule
from .clocks import utc
from .config import fingerprint
from .stock_source import numeric
from .validation import normalize, require_valid

POLICY = "ENGINEERING_CAUSAL_FLAT_ALL_GAPS_v1"
MODE = "ENGINEERING_CAUSAL_CANDLE_VIEW_ONLY"
FILL_COLUMNS = [
    "profile_id",
    "policy_id",
    "source_binding",
    "symbol",
    "session_et",
    "timestamp",
    "end_utc",
    "start_et",
    "end_et",
    "run_id",
    "run_length",
    "run_index",
    "calendar_run_id",
    "calendar_run_length",
    "calendar_run_index",
    "anchor_timestamp",
    "anchor_end",
    "anchor_close",
    "market_age_minutes",
    "elapsed_age_minutes",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_count",
    "vwap",
    "volume_unknown",
    "trade_count_unknown",
    "vwap_unknown",
    "is_observed",
    "is_synthetic",
    "is_opening",
    "is_terminal",
    "cross_session_anchor",
    "long_gap_synthetic",
    "unit_id",
    "split_guard",
    "reason",
    "feature_eligible",
    "genuine_t2_eligible",
    "available_at",
    "availability_basis",
    "source_timeframe",
    "engineering_only",
]


@dataclass(frozen=True)
class PriceUnitSegment:
    """Explicit compatible-price epoch assertion, not a corporate-action certification."""

    symbol: str
    start: pd.Timestamp
    stop: pd.Timestamp
    unit_id: str
    verified: bool
    evidence_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "start", utc(self.start))
        object.__setattr__(self, "stop", utc(self.stop))
        if (
            self.start >= self.stop
            or not self.symbol.strip()
            or not self.unit_id.strip()
            or type(self.verified) is not bool
            or (self.verified and not self.evidence_ref.strip())
        ):
            raise ValueError("EXPLICIT_PRICE_UNIT_SEGMENT_REQUIRED")


@dataclass(frozen=True)
class CleanupView:
    """Raw rows stay referenced in memory; only missing-row overlay is persisted."""

    symbols: tuple[str, ...]
    profile_id: str
    source_binding: str
    observed: pd.DataFrame
    fills: pd.DataFrame
    unresolved: pd.DataFrame
    expected_keys: tuple[tuple[str, str], ...]
    observed_sha256: str

    @property
    def content_id(self) -> str:
        return fingerprint(
            [
                self.profile_id,
                self.symbols,
                self.source_binding,
                POLICY,
                self.expected_keys,
                self.observed_sha256,
                self.fills.to_json(orient="records", date_format="iso"),
                self.unresolved.to_json(orient="records", date_format="iso"),
            ]
        )

    def materialize_engineering(self, *, mode: str) -> pd.DataFrame:
        """Expose flags on every accessed candle; unresolved keys stay absent, never invented."""
        if mode != MODE:
            raise ValueError("EXPLICIT_ENGINEERING_CANDLE_MODE_REQUIRED")
        if _frame_sha(self.observed) != self.observed_sha256:
            raise ValueError("GENUINE_OBSERVATIONS_MUTATED")
        raw = self.observed.copy()
        raw["is_observed"], raw["is_synthetic"] = True, False
        raw["volume_unknown"] = raw.volume.isna()
        raw["trade_count_unknown"] = raw.trade_count.isna() if "trade_count" in raw else True
        raw["engineering_only"], raw["feature_eligible"], raw["genuine_t2_eligible"] = (
            True,
            False,
            False,
        )
        raw["policy_id"], raw["profile_id"], raw["source_binding"] = (
            POLICY,
            self.profile_id,
            self.source_binding,
        )
        result = pd.concat([raw, self.fills], ignore_index=True) if len(self.fills) else raw
        order = {s: i for i, s in enumerate(self.symbols)}
        result["_order"] = result.symbol.map(order)
        result = (
            result.sort_values(["_order", "timestamp"])
            .drop(columns="_order")
            .reset_index(drop=True)
        )
        result.attrs.update(engineering_only=True, cleanup_id=self.content_id, mode=MODE)
        if result.duplicated(["symbol", "timestamp"]).any():
            raise ValueError("ENGINEERING_OVERLAY_DUPLICATE")
        return result

    def require_scientific(self, activity: str) -> None:
        """No FT0/TG0/T2, minute reference, fit, forecasting or trading conversion exists."""
        raise ValueError(f"ENGINEERING_CANDLES_FORBIDDEN_FOR_SCIENCE:{activity}")


def _runs(keys: list[dict], absent: set[pd.Timestamp], *, within_session: bool) -> dict:
    groups: list[list[dict]] = []
    previous_missing = False
    for key in keys:
        missing = key["timestamp"] in absent
        if missing:
            if (
                not previous_missing
                or not groups
                or (within_session and groups[-1][-1]["session_et"] != key["session_et"])
            ):
                groups.append([])
            groups[-1].append(key)
        previous_missing = missing
    result = {}
    for group in groups:
        run_id = fingerprint(
            [POLICY, within_session, group[0]["symbol"], group[0]["timestamp"].isoformat()]
        )
        for index, key in enumerate(group, 1):
            result[key["timestamp"]] = (run_id, len(group), index)
    return result


def _frame_sha(frame: pd.DataFrame) -> str:
    return hashlib.sha256(
        pd.util.hash_pandas_object(frame, index=False).to_numpy(dtype="uint64").tobytes()
    ).hexdigest()


def cleanup(
    frame: pd.DataFrame,
    symbols: tuple[str, ...],
    start: str,
    stop: str,
    *,
    profile_id: str,
    source_binding: str,
    segments: tuple[PriceUnitSegment, ...],
    active_intervals: dict[str, tuple[tuple[pd.Timestamp, pd.Timestamp], ...]] | None = None,
) -> CleanupView:
    """Fill any-length absent RTH run from genuinely observed closes with end < start.

    This uses the nominal completed-interval clock only. Unknown publication is
    retained; the output cannot certify contemporaneous source availability.
    Units must be verified in the SAME segment; even equal unit IDs across a
    split/reorganization boundary never justify cross-boundary anchoring.
    """
    if (
        not symbols
        or len(set(symbols)) != len(symbols)
        or not profile_id.strip()
        or not source_binding.strip()
        or any(not s.strip() for s in symbols)
    ):
        raise ValueError("ORDERED_UNIQUE_ENGINEERING_IDENTITY_REQUIRED")
    native = normalize(frame, stocks=True)
    require_valid(native, stocks=True)
    if set(native.symbol) - set(symbols) or not (native.source_timeframe == "30Min").all():
        raise ValueError("EXACT_UNIVERSE_NATIVE_30MIN_REQUIRED")
    for segment in segments:
        if segment.symbol not in symbols:
            raise ValueError("UNIT_SEGMENT_OUTSIDE_UNIVERSE")
    for symbol in symbols:
        ordered = sorted((s for s in segments if s.symbol == symbol), key=lambda s: s.start)
        if any(a.stop > b.start for a, b in zip(ordered, ordered[1:])):
            raise ValueError("OVERLAPPING_PRICE_UNIT_SEGMENTS")
    clocks = schedule(start, stop)
    if active_intervals is not None:
        if set(active_intervals) != set(symbols):
            raise ValueError("EXPLICIT_STOCK_ACTIVE_CALENDAR_REQUIRED")
        for ranges in active_intervals.values():
            intervals = sorted((utc(a), utc(b)) for a, b in ranges)
            if any(a >= b for a, b in intervals) or any(
                a[1] > b[0] for a, b in zip(intervals, intervals[1:])
            ):
                raise ValueError("VALID_NONOVERLAPPING_ACTIVE_SEGMENTS_REQUIRED")
    selected, fills, unresolved, all_keys = [], [], [], []
    for symbol in symbols:
        keys = []
        for day, clock in clocks.iterrows():
            for stamp in pd.date_range(clock.open, clock.close, freq="30min", inclusive="left"):
                end = stamp + pd.Timedelta(minutes=30)
                if active_intervals is not None:
                    if symbol not in active_intervals:
                        raise ValueError("EXPLICIT_STOCK_ACTIVE_CALENDAR_REQUIRED")
                    if not any(
                        utc(a) <= stamp and end <= utc(b) for a, b in active_intervals[symbol]
                    ):
                        continue
                keys.append(
                    dict(
                        symbol=symbol,
                        timestamp=stamp,
                        end=end,
                        session_et=str(day)[:10],
                        is_opening=stamp == clock.open,
                        is_terminal=end == clock.close,
                    )
                )
        group = native[native.symbol == symbol]
        grid_set = {k["timestamp"] for k in keys}
        # Extended-session rows are preserved upstream; cannot be substituted for RTH anchors.
        for _, clock in clocks.iterrows():
            rth = group[(group.timestamp >= clock.open) & (group.timestamp < clock.close)]
            if active_intervals is None and set(rth.timestamp) - grid_set:
                raise ValueError("OFF_GRID_RTH_SOURCE")
        rth = group[group.timestamp.isin(grid_set)].sort_values("timestamp")
        selected.append(rth)
        observed = {row.timestamp: row for row in rth.itertuples()}
        absent = grid_set - set(observed)
        daily_runs, calendar_runs = (
            _runs(keys, absent, within_session=True),
            _runs(keys, absent, within_session=False),
        )
        finalized: list[tuple[int, dict]] = []
        pending: tuple[int, dict] | None = None
        for position, key in enumerate(keys):
            stamp = key["timestamp"]
            if pending is not None:
                finalized.append(pending)
                pending = None
            if stamp in observed:
                pending = (position, key)
                all_keys.append((symbol, stamp.isoformat()))
                continue
            # Last observed interval ending at this start is explicitly NOT eligible yet.
            eligible = [(i, k) for i, k in finalized if k["end"] < stamp]
            anchor = eligible[-1] if eligible else None
            run_id, length, index = daily_runs[stamp]
            cid, clen, cindex = calendar_runs[stamp]
            base = dict(
                profile_id=profile_id,
                policy_id=POLICY,
                source_binding=source_binding,
                symbol=symbol,
                session_et=key["session_et"],
                timestamp=stamp,
                end_utc=key["end"].isoformat(),
                start_et=stamp.tz_convert("America/New_York").isoformat(),
                end_et=key["end"].tz_convert("America/New_York").isoformat(),
                run_id=run_id,
                run_length=length,
                run_index=index,
                calendar_run_id=cid,
                calendar_run_length=clen,
                calendar_run_index=cindex,
                is_opening=key["is_opening"],
                is_terminal=key["is_terminal"],
                long_gap_synthetic=length >= 3 or clen >= 3,
            )
            reason = "NO_GENUINE_STRICTLY_PRIOR_ANCHOR"
            target_segments = [
                s
                for s in segments
                if s.symbol == symbol and s.start <= stamp and key["end"] <= s.stop
            ]
            if anchor is not None:
                apos, ak = anchor
                price = numeric(observed[ak["timestamp"]].close)
                if not math.isfinite(price) or price <= 0:
                    reason = "INVALID_GENUINE_ANCHOR"
                elif len(target_segments) != 1 or not target_segments[0].verified:
                    reason = "SPLIT_UNITS_UNVERIFIED"
                elif not (
                    target_segments[0].start <= ak["timestamp"]
                    and ak["end"] <= target_segments[0].stop
                ):
                    reason = "PRICE_UNIT_SEGMENT_DISCONTINUITY"
                else:
                    segment = target_segments[0]
                    fills.append(
                        dict(
                            base,
                            anchor_timestamp=ak["timestamp"].isoformat(),
                            anchor_end=ak["end"].isoformat(),
                            anchor_close=price,
                            market_age_minutes=(position - apos - 1) * 30,
                            elapsed_age_minutes=(stamp - ak["end"]).total_seconds() / 60,
                            open=price,
                            high=price,
                            low=price,
                            close=price,
                            volume=np.nan,
                            trade_count=np.nan,
                            vwap=np.nan,
                            volume_unknown=True,
                            trade_count_unknown=True,
                            vwap_unknown=True,
                            is_observed=False,
                            is_synthetic=True,
                            cross_session_anchor=ak["session_et"] != key["session_et"],
                            unit_id=segment.unit_id,
                            split_guard="VERIFIED_SAME_SEGMENT",
                            reason="LONG_GAP_SYNTHETIC"
                            if base["long_gap_synthetic"]
                            else "CAUSAL_FLAT_SYNTHETIC",
                            feature_eligible=False,
                            genuine_t2_eligible=False,
                            available_at=None,
                            availability_basis="UNKNOWN",
                            source_timeframe="30Min",
                            engineering_only=True,
                        )
                    )
                    all_keys.append((symbol, stamp.isoformat()))
                    continue
            unresolved.append(
                dict(
                    base,
                    reason=reason,
                    anchor_timestamp=None if anchor is None else anchor[1]["timestamp"].isoformat(),
                    split_guard="UNRESOLVED",
                    is_synthetic=False,
                    engineering_only=True,
                )
            )
            all_keys.append((symbol, stamp.isoformat()))
    expected = tuple(all_keys)
    observed_frame = pd.concat(selected, ignore_index=True)
    view = CleanupView(
        symbols,
        profile_id,
        source_binding,
        observed_frame,
        pd.DataFrame(fills, columns=FILL_COLUMNS),
        pd.DataFrame(unresolved),
        expected,
        _frame_sha(observed_frame),
    )
    if len(expected) != len(view.observed) + len(view.fills) + len(view.unresolved):
        raise ValueError("ENGINEERING_SOURCE_OVERLAY_CONSERVATION_FAILURE")
    return view
