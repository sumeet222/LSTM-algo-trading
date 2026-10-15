"""One immutable stock source adapter; provider adjustment is not as-of evidence."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from numbers import Real
from pathlib import Path

import pandas as pd

from .aggregation import aggregate_session_hours
from .clocks import Basis, execution_plan, utc
from .config import fingerprint, load_config
from .corporate_actions import Action, raw_price_from_split_adjusted
from .hourly_proxy import HourlyCloseReference
from .labels import UNIVERSE
from .m2 import ScheduledCalendar, ScheduledStep
from .store import load_store

STOCK_VERSION = "ALPACA_SIP_CORE5_SPLIT_30MIN_V1"


class StockCalendar(ScheduledCalendar):
    """Memoize the existing calendar's prior valid origin stream, without changing it."""

    def __init__(self, start: str, end: str):
        super().__init__(start, end)
        self.days = tuple(self._sessions)
        self.prior: dict[tuple[str, int], tuple[str, ...]] = {}
        previous: dict[int, list[str]] = {1: [], 2: []}
        self.matching: dict[tuple[str, int], tuple[str, ...]] = {}
        slots: dict[int, list[str]] = {i: [] for i in range(1, 7)}
        for day, clock in self._sessions.items():
            for origin in (1, 2):
                self.prior[day, origin] = tuple(previous[origin])
                if execution_plan(clock, origin).calendar_valid:
                    previous[origin].append(day)
            for slot in range(1, 7):
                self.matching[day, slot] = tuple(slots[slot][-20:])
                if slot <= len(clock.hours):
                    slots[slot].append(day)

    def previous_origins(self, step: ScheduledStep, origin: int) -> tuple[str, ...]:
        self.validate_step(step)
        if origin not in (1, 2):
            raise ValueError("ORIGIN_REQUIRED")
        return self.prior[step.session, origin]


def numeric(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError("FINITE_STOCK_NUMERIC_REQUIRED")
    return float(value)


@dataclass(frozen=True)
class StockBar:
    symbol: str
    session: str
    slot: int
    start: pd.Timestamp
    end: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    source_ids: tuple[str, ...]
    source_version: str = STOCK_VERSION
    available_at: pd.Timestamp | None = None
    basis: Basis = "UNKNOWN"
    action_verified: bool = False
    action_ref: str = "VENDOR_SPLIT_PRICE_AND_INVERSE_VOLUME_ASOF_UNVERIFIED"
    share_basis: str = "VENDOR_SPLIT_ASOF_2025-06-30"
    price_basis: str = "SPLIT_CONSISTENT"
    evidence_ref: str = ""
    action_known_at: pd.Timestamp | None = None
    universe: tuple[str, ...] = UNIVERSE

    def __post_init__(self) -> None:
        if (
            len(self.universe) != 5 or len(set(self.universe)) != 5
            or self.symbol not in self.universe
            or type(self.slot) is not int or not 0 <= self.slot <= 6
        ):
            raise ValueError("CANONICAL_STOCK_SLOT_REQUIRED")
        start, end = utc(self.start), utc(self.end)
        if end - start != pd.Timedelta(minutes=30 if self.slot == 0 else 60):
            raise ValueError("EXACT_STOCK_PERIOD_REQUIRED")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        values = tuple(
            numeric(x) for x in (self.open, self.high, self.low, self.close, self.volume)
        )
        if (
            min(values[:4]) <= 0
            or self.volume < 0
            or self.low > min(self.open, self.close)
            or self.high < max(self.open, self.close)
            or self.low > self.high
        ):
            raise ValueError("INVALID_STOCK_OHLCV")
        if (
            not self.source_ids
            or len(set(self.source_ids)) != len(self.source_ids)
            or any(not x.strip() for x in self.source_ids)
            or self.source_version != STOCK_VERSION
            or not self.action_ref.strip()
            or not self.share_basis.strip()
            or self.price_basis not in {"RAW", "SPLIT_CONSISTENT"}
            or self.basis not in {"UNKNOWN", "DOCUMENTED", "SYNTHETIC", "ASSUMED"}
        ):
            raise ValueError("STOCK_SOURCE_ACTION_LINEAGE_REQUIRED")
        if self.available_at is not None:
            available = utc(self.available_at)
            if available < end:
                raise ValueError("PUBLICATION_BEFORE_COMPLETION")
            object.__setattr__(self, "available_at", available)

        if self.action_known_at is not None:
            object.__setattr__(self, "action_known_at", utc(self.action_known_at))

    @property
    def row_id(self) -> str:
        return fingerprint(
            [
                self.symbol,
                self.start.isoformat(),
                self.end.isoformat(),
                self.source_ids,
                self.action_ref,
                self.share_basis,
            ]
        )

    @property
    def zero_range(self) -> bool:
        return self.high == self.low


def source_reason(row: StockBar | None, cutoff: pd.Timestamp, *, synthetic: bool = False) -> str:
    if row is None:
        return "SOURCE_MISSING"
    if row.available_at is None or row.basis in {"UNKNOWN", "ASSUMED"}:
        return "SOURCE_PUBLICATION_UNKNOWN"
    if row.basis == "SYNTHETIC" and not synthetic:
        return "SYNTHETIC_NOT_AUTHORIZED"
    if row.basis == "DOCUMENTED" and not row.evidence_ref.strip():
        return "PUBLICATION_EVIDENCE_REQUIRED"
    if not row.action_verified:
        return "ACTION_SCOPE_UNVERIFIED"
    if row.action_known_at is not None and row.action_known_at > cutoff:
        return "ACTION_BASIS_NOT_AVAILABLE_AT_STEP"
    if row.end > cutoff or row.available_at > cutoff:
        return "NOT_AVAILABLE_AT_STEP"
    if cutoff - row.end > pd.Timedelta(minutes=90):
        return "STALE_STOCK_SOURCE"
    return "SOURCE_VALID"


@dataclass(frozen=True)
class StockDaily:
    symbol: str
    session: str
    end: pd.Timestamp
    close: float | None
    volume: float | None
    open: float | None
    high: float | None
    low: float | None
    source_ids: tuple[str, ...]
    close_available_at: pd.Timestamp | None
    volume_available_at: pd.Timestamp | None
    basis: Basis
    action_verified: bool
    share_basis: str
    source_version: str = STOCK_VERSION
    close_basis: Basis = "UNKNOWN"
    close_action_verified: bool = False
    close_action_known_at: pd.Timestamp | None = None
    volume_action_known_at: pd.Timestamp | None = None
    universe: tuple[str, ...] = UNIVERSE

    def __post_init__(self) -> None:
        utc(self.end)
        if (len(self.universe) != 5 or len(set(self.universe)) != 5
                or self.symbol not in self.universe or self.source_version != STOCK_VERSION):
            raise ValueError("DAILY_STOCK_SOURCE_REQUIRED")
        for value in (self.open, self.high, self.low, self.close):
            if value is not None and numeric(value) <= 0:
                raise ValueError("POSITIVE_DAILY_PRICE_REQUIRED")
        if self.volume is not None and numeric(self.volume) < 0:
            raise ValueError("NONNEGATIVE_DAILY_VOLUME_REQUIRED")
        for at in (self.close_available_at, self.volume_available_at):
            if at is not None and utc(at) < self.end:
                raise ValueError("DAILY_PUBLICATION_BEFORE_COMPLETION")


class StockHistory:
    """Exact shared hourly and full-session daily positions; no raw imputation."""

    def __init__(
        self, calendar: StockCalendar, bars: tuple[StockBar, ...], *, synthetic: bool = False,
        universe: tuple[str, ...] = UNIVERSE,
    ):
        self.calendar = calendar
        self.synthetic = synthetic
        if len(universe) != 5 or len(set(universe)) != 5:
            raise ValueError("FIVE_DISTINCT_STOCKS_REQUIRED")
        self.universe = universe
        self.bars: dict[tuple[str, str, int], StockBar] = {}
        ids = set()
        for bar in bars:
            if bar.universe != universe:
                raise ValueError("STOCK_UNIVERSE_BINDING_MISMATCH")
            key = bar.symbol, bar.session, bar.slot
            if key in self.bars or bar.row_id in ids:
                raise ValueError("DUPLICATE_STOCK_SOURCE_KEY")
            clock = calendar.clock(bar.session)
            interval = (
                clock.terminal_stub
                if bar.slot == 0
                else (clock.hours[bar.slot - 1] if bar.slot <= len(clock.hours) else None)
            )
            if interval is None or (bar.start, bar.end) != (interval.start, interval.end):
                raise ValueError("STOCK_SOURCE_OFF_SCHEDULE")
            self.bars[key] = bar
            ids.add(bar.row_id)
        hasher = hashlib.sha256()
        for key in sorted(self.bars):
            hasher.update(json.dumps(vars(self.bars[key]), sort_keys=True, default=str).encode())
        self.content_sha256 = hasher.hexdigest()
        # Archive bytes are integrity evidence, not a causal input/admission discriminator.
        # Changing only a future exit must not invalidate a prior fitted source contract.
        self.binding = fingerprint(
            [
                STOCK_VERSION,
                universe,
                calendar.days[0],
                calendar.days[-1],
                synthetic,
                "SIP_SPLIT_PRICE_INVERSE_VOLUME",
            ]
        )
        self.action_binding = fingerprint(
            sorted({(b.symbol, b.share_basis, b.action_ref, b.action_verified) for b in bars})
        )
        for symbol in universe:
            if len({b.share_basis for b in bars if b.symbol == symbol}) > 1:
                raise ValueError("STOCK_ROLLING_SPLIT_EPOCH_MISMATCH")
        self.daily: dict[tuple[str, str], StockDaily] = {}
        for symbol in universe:
            for day, clock in calendar._sessions.items():
                parts = [
                    self.bars.get((symbol, day, slot)) for slot in range(1, len(clock.hours) + 1)
                ]
                if clock.terminal_stub is not None:
                    parts.append(self.bars.get((symbol, day, 0)))
                present = tuple(b for b in parts if b is not None)
                if not present:
                    continue
                terminal = parts[-1]
                complete = len(present) == len(parts)
                available = tuple(b.available_at for b in present)
                complete_available = all(t is not None for t in available)
                timestamps = tuple(t for t in available if t is not None)
                bases = {b.basis for b in present}
                epochs = {b.share_basis for b in present}
                if len(epochs) != 1:
                    raise ValueError("DAILY_SHARE_EPOCH_MISMATCH")
                if clock.close is None:
                    raise ValueError("SESSION_CLOSE_REQUIRED")
                self.daily[symbol, day] = StockDaily(
                    symbol,
                    day,
                    clock.close,
                    terminal.close if terminal else None,
                    sum(b.volume for b in present) if complete else None,
                    present[0].open if complete else None,
                    max(b.high for b in present) if complete else None,
                    min(b.low for b in present) if complete else None,
                    tuple(b.row_id for b in present),
                    terminal.available_at if terminal else None,
                    max(timestamps) if complete and complete_available else None,
                    present[0].basis if len(bases) == 1 else "UNKNOWN",
                    all(b.action_verified for b in present),
                    next(iter(epochs)),
                    close_basis=terminal.basis if terminal else "UNKNOWN",
                    close_action_verified=bool(terminal and terminal.action_verified),
                    close_action_known_at=terminal.action_known_at if terminal else None,
                    volume_action_known_at=max(
                        (b.action_known_at for b in present if b.action_known_at is not None),
                        default=None,
                    ),
                    universe=universe,
                )

    def source_status(self, row: StockBar | None, cutoff: pd.Timestamp) -> str:
        """Strict default; a candidate adapter must implement its own reviewed policy."""
        return source_reason(row, cutoff, synthetic=self.synthetic)

    def hour(
        self, symbol: str, step: ScheduledStep, *, source_only: bool = False
    ) -> StockBar | None:
        self.calendar.validate_step(step)
        row = self.bars.get((symbol, step.session, step.slot))
        if (
            source_only
            or self.source_status(row, step.information_cutoff) == "SOURCE_VALID"
        ):
            return row
        return None

    def day(
        self,
        symbol: str,
        day: str,
        cutoff: pd.Timestamp,
        *,
        volume: bool = False,
        source_only: bool = False,
    ) -> StockDaily | None:
        row = self.daily.get((symbol, day))
        if row is None or row.end > cutoff:
            return None
        value = row.volume if volume else row.close
        available = row.volume_available_at if volume else row.close_available_at
        if value is None:
            return None
        if source_only:
            return row
        action_at = row.volume_action_known_at if volume else row.close_action_known_at
        if action_at is not None and action_at > cutoff:
            return None
        if (
            available is None
            or available > cutoff
            or (row.basis if volume else row.close_basis) in {"UNKNOWN", "ASSUMED"}
            or not (row.action_verified if volume else row.close_action_verified)
            or ((row.basis if volume else row.close_basis) == "SYNTHETIC" and not self.synthetic)
        ):
            return None
        return row


def load_stock_history(
    config: Path = Path("configs/track_a_data.json"),
) -> tuple[StockHistory, dict]:
    """Read canonical split-adjusted chunks once; override legacy assumed availability."""
    cfg = load_config(config)
    if (
        tuple(cfg["symbols"]) != UNIVERSE
        or cfg["adjustment"] != "split"
        or cfg["timeframe"] != "30Min"
        or cfg["asof"] != "2025-06-30"
        or cfg["start_date"] != "2020-07-01"
        or cfg["end_date"] != "2025-06-30"
        or cfg["stock_store"] != "data/raw/alpaca/track_a"
        or cfg["feed"] != "sip"
    ):
        raise ValueError("FROZEN_STOCK_SOURCE_REQUIRED")
    frame = load_store(cfg)
    hourly, qa = aggregate_session_hours(frame, list(UNIVERSE), cfg["start_date"], cfg["end_date"])
    calendar = StockCalendar(cfg["start_date"], cfg["end_date"])
    raw_ids = {(r.symbol, r.timestamp): r.provenance_id for r in frame.itertuples()}
    bars = []
    for row in hourly.itertuples():
        start, end = row.timestamp, row.available_at
        if not isinstance(start, pd.Timestamp) or not isinstance(end, pd.Timestamp):
            raise ValueError("NATIVE_STOCK_TIMESTAMP_REQUIRED")
        if not isinstance(row.symbol, str) or not isinstance(row.session, str):
            raise ValueError("NATIVE_STOCK_KEY_REQUIRED")
        clock = calendar.clock(row.session)
        slot = 0 if row.is_stub else next(i for i, h in enumerate(clock.hours, 1) if h.end == end)
        starts = pd.date_range(start, end, freq="30min", inclusive="left")
        ids = tuple(
            fingerprint([raw_ids[row.symbol, t], row.symbol, t.isoformat()]) for t in starts
        )
        bars.append(
            StockBar(
                row.symbol,
                row.session,
                slot,
                start,
                end,
                *(numeric(x) for x in (row.open, row.high, row.low, row.close, row.volume)),
                source_ids=ids,
            )
        )
    qa.update(
        {
            "source_rows": len(frame),
            "publication": "UNKNOWN",
            "action_scope": "CURRENT_VENDOR_SPLIT_ADJUSTMENT_NOT_HISTORICAL_ASOF_CERTIFICATION",
            "source_version": STOCK_VERSION,
        }
    )
    return StockHistory(calendar, tuple(bars)), qa


def convert_split_basis(bar: StockBar, action: Action, cutoff: pd.Timestamp) -> StockBar:
    """Explicit split price/share conversion; existing pure action metadata is reused."""
    if (
        action.kind != "SPLIT"
        or action.symbol != bar.symbol
        or action.share_basis != bar.share_basis
        or action.post_split_basis is None
        or utc(pd.Timestamp(action.boundary)) > cutoff
        or bar.end > pd.Timestamp(action.boundary)
        or action.source.publication_at is None
        or utc(pd.Timestamp(action.source.publication_at)) > cutoff
    ):
        raise ValueError("SPLIT_BASIS_OR_ASOF_UNVERIFIED")
    ratio = float(action.amount)
    return replace(
        bar,
        open=bar.open / ratio,
        high=bar.high / ratio,
        low=bar.low / ratio,
        close=bar.close / ratio,
        volume=bar.volume * ratio,
        share_basis=action.post_split_basis,
        price_basis="SPLIT_CONSISTENT",
        action_verified=True,
        action_ref=action.source.event_id,
        action_known_at=max(
            utc(pd.Timestamp(action.boundary)), utc(pd.Timestamp(action.source.publication_at))
        ),
        source_ids=bar.source_ids + (action.source.sha256,),
    )


def proxy_reference(
    bar: StockBar,
    raw_per_adjusted: float | None,
    conversion_evidence: str = "",
    *,
    conversion_known_at: pd.Timestamp | None = None,
) -> HourlyCloseReference | None:
    """No split-adjusted CLOSE is relabeled raw without independent conversion evidence."""
    if bar.slot == 0 or (bar.action_known_at is not None and bar.action_known_at > bar.end):
        return None
    if bar.price_basis == "RAW":
        raw = bar.close
    elif raw_per_adjusted is not None and conversion_evidence.strip():
        if bar.basis == "DOCUMENTED" and (
            conversion_known_at is None or utc(conversion_known_at) > bar.end
        ):
            return None
        raw = float(raw_price_from_split_adjusted(bar.close, raw_per_adjusted))
    else:
        return None
    return HourlyCloseReference(
        bar.symbol,
        bar.row_id,
        bar.start,
        bar.end,
        raw,
        bar.source_version,
        "SYNTHETIC" if bar.basis == "SYNTHETIC" else "ALPACA_SIP",
        bar.available_at,
        bar.basis,
        bar.evidence_ref or conversion_evidence,
    )
