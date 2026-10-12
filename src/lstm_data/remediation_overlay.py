"""Explicit candidate-only resolution of true additions; original source rows always win."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from .aggregation import aggregate_session_hours
from .config import fingerprint
from .ft0_audit import mechanical_m2, retention_audit
from .ft0_transforms import ORDER
from .labels import UNIVERSE
from .remediation_plan import OVERLAY_VERSION
from .stock_features import FeatureCalculator
from .stock_source import StockBar, StockCalendar, StockHistory, numeric
from .validation import normalize, require_valid


@dataclass(frozen=True)
class NativeAddition:
    frame: pd.DataFrame
    provider: str
    kind: str
    request_hash: str
    chunk_sha256: str
    adjustment: str = "split"
    currency: str = "USD"
    volume_unit: str = "SPLIT_ADJUSTED_SHARES"
    entity_asof: str = "2025-06-30"
    available_at: None = None
    availability_basis: str = "UNKNOWN"
    secondary_contract_verified: bool = False

    def __post_init__(self) -> None:
        if self.available_at is not None or self.availability_basis != "UNKNOWN":
            raise ValueError("RETROSPECTIVE_PUBLICATION_MUST_REMAIN_UNKNOWN")


def native_timestamp(value: object) -> pd.Timestamp:
    """Normalized timestamps must retain the exact timezone-aware native type."""
    if not isinstance(value, pd.Timestamp) or value.tzinfo is None:
        raise ValueError("NATIVE_TIMESTAMP_TYPE_REQUIRED")
    return value


def same_observation(left: pd.Series, right: pd.Series) -> bool:
    """Binary precision tolerance only, not a fitted economic vendor-tolerance threshold."""
    return all(
        math.isclose(
            float(left[c]), float(right[c]), rel_tol=1e-9, abs_tol=1e-6 if c == "volume" else 1e-9
        )
        for c in ("open", "high", "low", "close", "volume")
    )


def compatible_contract(item: NativeAddition) -> bool:
    """Secondary rows never establish an Alpaca adjustment/share contract implicitly."""
    return (
        item.provider == "ALPACA"
        and item.adjustment == "split"
        and item.currency == "USD"
        and item.volume_unit == "SPLIT_ADJUSTED_SHARES"
        and item.entity_asof == "2025-06-30"
        and len(item.chunk_sha256) == 64
    )


def resolve_native(
    original: pd.DataFrame,
    additions: tuple[NativeAddition, ...],
    calendar: StockCalendar,
    *,
    view: str,
) -> tuple[pd.DataFrame, dict]:
    """Original native observations win. Conflicting/unsupported additions never enter features."""
    if view not in {"HISTORY_ONLY", "GAP_ONLY", "ALPACA_ONLY_EXTENDED"}:
        raise ValueError("EXPLICIT_CANDIDATE_VIEW_REQUIRED")
    original = normalize(original, stocks=True)
    require_valid(original, stocks=True)
    indexed = {
        (str(row.symbol), native_timestamp(row.timestamp)): i
        for i, row in enumerate(original.itertuples())
    }
    controls = {s: {"matched": 0, "conflicts": 0} for s in UNIVERSE}
    for item in additions:
        if item.kind != "BASIS_CONTROL" or not compatible_contract(item):
            continue
        for _, row in item.frame.iterrows():
            symbol, timestamp = str(row["symbol"]), row["timestamp"]
            key = symbol, timestamp
            if symbol in controls and key in indexed:
                name = (
                    "matched" if same_observation(original.iloc[indexed[key]], row) else "conflicts"
                )
                controls[symbol][name] += 1
    allowed = {s: c["matched"] > 0 and c["conflicts"] == 0 for s, c in controls.items()}
    selected, selection, rejected, collisions = [], [], [], []
    chosen_keys = set(indexed)
    seen_additional: dict[tuple[str, pd.Timestamp], pd.Series] = {}
    for item in additions:
        if not compatible_contract(item):
            rejected.append(
                {
                    "request_hash": item.request_hash,
                    "reason": "SECONDARY_CANDIDATE_OR_BASIS_CONTRACT_HOLD",
                    "provider": item.provider,
                }
            )
            continue
        if item.kind not in {"WARMUP", "GAP_RETRY", "BASIS_CONTROL"}:
            continue
        frame = normalize(item.frame, stocks=True)
        require_valid(frame, stocks=True)
        if "source_timeframe" not in frame or not (frame.source_timeframe == "30Min").all():
            raise ValueError("NATIVE_30MIN_ADDITIONS_REQUIRED")
        if not (frame.feed == "sip").all() or not (frame.adjustment == "split").all():
            raise ValueError("SIP_SPLIT_ADDITION_REQUIRED")
        conflict = any(
            not same_observation(original.iloc[indexed[str(r["symbol"]), r["timestamp"]]], r)
            for _, r in frame.iterrows()
            if (str(r["symbol"]), r["timestamp"]) in indexed
        )
        if conflict and item.kind == "GAP_RETRY":
            rejected.append(
                {
                    "request_hash": item.request_hash,
                    "reason": "GAP_NEIGHBOR_OHLCV_CONFLICT",
                    "provider": item.provider,
                }
            )
        for _, row in frame.iterrows():
            symbol, timestamp = str(row["symbol"]), pd.Timestamp(row["timestamp"])
            key = symbol, timestamp
            if symbol not in UNIVERSE:
                raise ValueError("ADDITIONAL_TRAINING_NAME_FORBIDDEN")
            if key in indexed:
                collisions.append(
                    {
                        "symbol": symbol,
                        "timestamp": timestamp.isoformat(),
                        "result": "IDENTICAL"
                        if same_observation(original.iloc[indexed[key]], row)
                        else "CONFLICT_ORIGINAL_PRESERVED",
                        "request_hash": item.request_hash,
                    }
                )
                continue
            if not allowed[symbol] or (conflict and item.kind == "GAP_RETRY"):
                continue
            if (item.kind == "WARMUP" and view == "GAP_ONLY") or (
                item.kind == "GAP_RETRY" and view == "HISTORY_ONLY"
            ):
                continue
            if item.kind == "BASIS_CONTROL":
                continue
            day = timestamp.tz_convert("America/New_York").date().isoformat()
            clock = calendar._sessions.get(day)
            if (
                clock is None
                or clock.open is None
                or clock.close is None
                or not clock.open <= timestamp < clock.close
            ):
                continue  # Preserve native extended/non-session rows in archive, not FT0.
            if timestamp not in pd.date_range(
                clock.open, clock.close, freq="30min", inclusive="left"
            ):
                raise ValueError("ADDITION_TIMESTAMP_OFF_NATIVE_GRID")
            prior = seen_additional.get(key)
            if prior is not None:
                if not same_observation(prior, row):
                    raise ValueError("CONFLICTING_ADDITIONAL_NATIVE_KEY")
                continue
            if key in chosen_keys:
                continue
            source_id = fingerprint(
                [item.provider, item.chunk_sha256, item.request_hash, symbol, timestamp.isoformat()]
            )
            copy = row.copy()
            copy["native_source_id"] = source_id
            selected.append(copy)
            seen_additional[key] = row
            chosen_keys.add(key)
            selection.append(
                {
                    "symbol": symbol,
                    "timestamp": timestamp.isoformat(),
                    "provider": item.provider,
                    "kind": item.kind,
                    "source_id": source_id,
                    "request_hash": item.request_hash,
                    "chunk_sha256": item.chunk_sha256,
                    "available_at": None,
                    "availability_basis": "UNKNOWN",
                }
            )
    base = original.copy()
    base["native_source_id"] = [
        fingerprint([r.provenance_id, r.symbol, native_timestamp(r.timestamp).isoformat()])
        for r in base.itertuples()
    ]
    merged = pd.concat([base, pd.DataFrame(selected)], ignore_index=True) if selected else base
    merged = merged.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    require_valid(merged, stocks=True)
    return merged, {
        "version": OVERLAY_VERSION,
        "view": view,
        "original_rows": len(original),
        "added_RTH_rows": len(selected),
        "selected_rows": selection,
        "basis_controls": controls,
        "symbols_control_compatible": allowed,
        "overlap_checks": collisions,
        "rejected_partitions": rejected,
        "status": "CANDIDATE_NOT_ACTIVATED",
        "scientific_readiness": False,
        "secondary": "SECONDARY_UNAVAILABLE_OR_REQUIRES_SEPARATE_TYPED_ADAPTER_REVIEW",
    }


def history_from_view(
    frame: pd.DataFrame, start: str, *, view: str, end: str = "2025-06-30"
) -> tuple[StockHistory, dict]:
    """Thin additive adapter: reuse aggregation/calendar/StockHistory and all feature math."""
    hours, qa = aggregate_session_hours(frame, list(UNIVERSE), start, end)
    cal = StockCalendar(start, end)
    ids = {(r.symbol, r.timestamp): r.native_source_id for r in frame.itertuples()}
    bars = []
    for row in hours.itertuples():
        if not isinstance(row.timestamp, pd.Timestamp) or not isinstance(
            row.available_at, pd.Timestamp
        ):
            raise ValueError("NATIVE_VIEW_TIMESTAMP_REQUIRED")
        clock = cal.clock(str(row.session))
        slot = (
            0
            if row.is_stub
            else next(i for i, h in enumerate(clock.hours, 1) if h.end == row.available_at)
        )
        sources = tuple(
            str(ids[row.symbol, t])
            for t in pd.date_range(row.timestamp, row.available_at, freq="30min", inclusive="left")
        )
        bars.append(
            StockBar(
                str(row.symbol),
                str(row.session),
                slot,
                row.timestamp,
                row.available_at,
                *(numeric(x) for x in (row.open, row.high, row.low, row.close, row.volume)),
                source_ids=sources,
            )
        )
    history = StockHistory(cal, tuple(bars))
    # Selection identity, not scientific/source approval. Original interface remains intact.
    history.binding = fingerprint([history.binding, OVERLAY_VERSION, view])
    qa["source_rows"] = len(frame)
    return history, qa


def fixed_retention(history: StockHistory, qa: dict) -> dict:
    """Same frozen original origins, excluding warmup-only origins from audit denominators."""
    calculator = FeatureCalculator(history)
    result = retention_audit(history, qa, calculator)
    rows = [r for r in result["origins"] if "2020-07-01" <= r["session"] < "2024-07-01"]
    masks = {key: comp.coverage for key, comp in calculator._components.items()}
    m2_mask: dict[tuple[str, str, int], bool] = {}
    counts = {name: 0 for name in ORDER}
    from .m2 import scheduled_window

    for row in rows:
        failed = set()
        if not row["scheduled_history"]:
            row["failed_channels"] = list(ORDER)
            continue
        for step in scheduled_window(history.calendar, row["session"], row["origin"]):
            for symbol in UNIVERSE:
                coverage = masks[symbol, step.end, True]
                key = symbol, step.session, row["origin"]
                if key not in m2_mask:
                    m2_mask[key] = mechanical_m2(history, symbol, step.session, row["origin"])
                failed.update(
                    name for name in ORDER if not (m2_mask[key] if name == "M2" else coverage[name])
                )
        row["failed_channels"] = [name for name in ORDER if name in failed]
        for name in failed:
            counts[name] += 1
    result["origins"] = rows
    result["first_mechanical_complete_origin"] = next(
        (r for r in rows if r["mechanical_ft0"]), None
    )
    result["feature_loss_counts"] = counts
    result["fixed_origin_universe"] = (
        "July2020-June2024, exact original calendar; warmup not counted"
    )
    assert result["populations"]["train"]["denominator"] == 1502
    assert result["populations"]["development"]["denominator"] == 496
    return result
