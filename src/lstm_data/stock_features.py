"""All frozen FT0 stock channels; exact per-step clocks and existing M2 composition."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import fmean

import pandas as pd

from .config import fingerprint
from .ft0_transforms import (
    DICTIONARY_ID,
    FT0_VERSION,
    ORDER,
    Context,
    FloorCertificate,
    transform_reason,
)
from .labels import UNIVERSE
from .m2 import M2FloorCertificate, M2Result, ReturnIndex, ScheduledStep, evaluate_m2
from .market_features import rms
from .stock_source import StockHistory, source_reason


def covered(
    values: tuple[float | None, ...], count: int, minimum: int, maximum_gap: int = 2
) -> bool:
    if len(values) != count or sum(v is not None for v in values) < minimum:
        return False
    run = 0
    for value in values:
        run = run + 1 if value is None else 0
        if run > maximum_gap:
            return False
    return True


def mean(values: tuple[float | None, ...]) -> float | None:
    good = tuple(v for v in values if v is not None)
    return fmean(good) if good else None


@dataclass
class IndicatorState:
    """Streaming EMA/Wilder state; missing prices freeze state, recovery has no fake RSI delta."""

    emas: dict[int, float] = field(default_factory=dict)
    ema_updates: int = 0
    previous_close: float | None = None
    initial_changes: list[float] = field(default_factory=list)
    average_gain: float | None = None
    average_loss: float | None = None
    wilder_updates: int = 0

    def update(self, close: float | None) -> None:
        if close is None:
            self.previous_close = None
            if self.average_gain is None:
                self.initial_changes.clear()
            return
        if not math.isfinite(close) or close <= 0:
            raise ValueError("POSITIVE_INDICATOR_PRICE_REQUIRED")
        if not self.emas:
            self.emas = {period: close for period in (6, 18, 24, 72)}
        else:
            for period, value in self.emas.items():
                alpha = 2 / (period + 1)
                self.emas[period] = alpha * close + (1 - alpha) * value
            self.ema_updates += 1
        if self.previous_close is not None:
            change = close - self.previous_close
            if self.average_gain is None:
                self.initial_changes.append(change)
                if len(self.initial_changes) == 14:
                    self.average_gain = fmean(max(x, 0) for x in self.initial_changes)
                    self.average_loss = fmean(max(-x, 0) for x in self.initial_changes)
            else:
                if self.average_loss is None:
                    raise ValueError("WILDER_PAIRED_STATE_REQUIRED")
                self.average_gain = (13 * self.average_gain + max(change, 0)) / 14
                self.average_loss = (13 * self.average_loss + max(-change, 0)) / 14
                self.wilder_updates += 1
        self.previous_close = close

    def normalized_rsi(self) -> float | None:
        gain, loss = self.average_gain, self.average_loss
        if gain is None or loss is None or self.wilder_updates < 140:
            return None
        if gain == 0 and loss == 0:
            return 0.0
        if loss == 0:
            return 1.0
        if gain == 0:
            return -1.0
        return (100 - 100 / (1 + gain / loss) - 50) / 50


@dataclass(frozen=True)
class Components:
    symbol: str
    step: ScheduledStep
    values: dict[str, float | None]
    coverage: dict[str, bool]
    source_binding: str
    action_binding: str
    source_ids: tuple[str, ...]
    source_only: bool
    flags: tuple[str, ...]
    lineage_id: str


@dataclass(frozen=True)
class FeatureCell:
    feature: str
    value: float | None
    valid: bool
    reason: str
    key: tuple[str, str, int]
    timestamp: pd.Timestamp
    source_ids: tuple[str, ...]
    lineage_id: str
    source_binding: str
    action_binding: str
    basis: str
    floor_id: str | None = None
    m2: M2Result | None = None
    feature_version: str = FT0_VERSION
    dictionary_id: str = DICTIONARY_ID
    research_ready: bool = False


class FeatureCalculator:
    """One source/component cache; no per-window source copies or alternate M2 math."""

    def __init__(self, history: StockHistory, returns: ReturnIndex | None = None):
        self.history = history
        self.returns = returns or ReturnIndex(())
        self._components: dict[tuple[str, pd.Timestamp, bool], Components] = {}
        self._built: set[tuple[str, bool]] = set()
        self._m2: dict[tuple[str, pd.Timestamp, int, str | None], M2Result] = {}

    def components(
        self, symbol: str, step: ScheduledStep, *, source_only: bool = False
    ) -> Components:
        self.history.calendar.validate_step(step)
        if symbol not in UNIVERSE:
            raise ValueError("CANONICAL_STOCK_REQUIRED")
        if step.end >= pd.Timestamp("2024-07-01", tz="America/New_York").tz_convert("UTC"):
            raise ValueError("CONFIRMATION_FEATURE_COMPUTATION_NOT_AUTHORIZED")
        if (symbol, source_only) not in self._built:
            self._build(symbol, source_only)
        return self._components[symbol, step.end, source_only]

    def _build(self, symbol: str, source_only: bool) -> None:
        history, calendar = self.history, self.history.calendar
        returns: list[float | None] = []
        closes: list[float | None] = []
        state = IndicatorState()
        day_cache: dict[str, tuple[list[float | None], list[float | None]]] = {}
        day_lineage: dict[str, str] = {}
        state_lineage = fingerprint([symbol, history.binding, "EMA_WILDER_SEED"])
        for step in calendar.steps:
            if step.end >= pd.Timestamp("2024-07-01", tz="America/New_York").tz_convert("UTC"):
                break
            row = history.hour(symbol, step, source_only=source_only)
            current_return = math.log(row.close / row.open) if row else None
            returns.append(current_return)
            closes.append(row.close if row else None)
            state.update(row.close if row else None)
            state_lineage = fingerprint(
                [
                    state_lineage,
                    step.end.isoformat(),
                    [
                        row.row_id,
                        row.open,
                        row.high,
                        row.low,
                        row.close,
                        row.volume,
                        str(row.available_at),
                        str(row.action_known_at),
                    ]
                    if row
                    else None,
                ]
            )
            h12 = rms(tuple(returns[-12:]), 12, 12)
            h60 = rms(tuple(returns[-60:]), 60, 57)
            day_index = calendar.days.index(step.session)
            previous = calendar.days[max(0, day_index - 126) : day_index]
            if step.session not in day_cache:
                daily_close, daily_volume = [], []
                dependencies = []
                for day in previous:
                    price = history.day(symbol, day, step.end, source_only=source_only)
                    volume = history.day(
                        symbol, day, step.end, volume=True, source_only=source_only
                    )
                    daily_close.append(price.close if price else None)
                    daily_volume.append(volume.volume if volume else None)
                    dependencies.append(
                        [
                            day,
                            price.source_ids if price else (),
                            volume.source_ids if volume else (),
                        ]
                    )
                day_cache[step.session] = daily_close, daily_volume
                day_lineage[step.session] = fingerprint(dependencies)
            # Daily inputs can arrive late within a day; never freeze a later assertion backward.
            prices, volumes = day_cache[step.session]
            if not source_only and any(
                r is not None
                and (
                    (r.close_available_at is not None and r.close_available_at > step.end)
                    or (r.volume_available_at is not None and r.volume_available_at > step.end)
                )
                for r in (history.daily.get((symbol, day)) for day in previous)
            ):
                day_cache.pop(step.session, None)
            recent_prices = tuple(prices[-64:])
            daily_returns = tuple(
                None if a is None or b is None else math.log(b / a)
                for a, b in zip(recent_prices, recent_prices[1:])
            )
            d63 = rms(daily_returns, 63, 60)

            def ratio(first: int, last: int) -> float | None:
                if (
                    len(prices) < max(first, last)
                    or prices[-first] is None
                    or prices[-last] is None
                ):
                    return None
                numerator, denominator = prices[-first], prices[-last]
                if numerator is None or denominator is None:
                    return None
                return math.log(numerator / denominator)

            matching = calendar.matching[step.session, step.slot]
            slot_volumes = []
            slot_source_ids = []
            for day in matching:
                prior_step = calendar.steps[calendar._positions[day, step.slot]]
                earlier = history.hour(symbol, prior_step, source_only=source_only)
                slot_volumes.append(earlier.volume if earlier else None)
                slot_source_ids.append(earlier.row_id if earlier else None)
            q1 = mean(tuple(slot_volumes)) if covered(tuple(slot_volumes), 20, 19) else None
            v5, v60 = tuple(volumes[-5:]), tuple(volumes[-60:])
            q2short = mean(v5) if covered(v5, 5, 5) else None
            q2long = mean(v60) if covered(v60, 60, 57) else None
            p20 = tuple(prices[-20:])
            sma20 = mean(p20) if covered(p20, 20, 19) else None
            p21 = tuple(prices[-21:])
            changes = tuple(
                None if a is None or b is None else float((b > a) - (b < a))
                for a, b in zip(p21, p21[1:])
            )
            sign20 = mean(changes) if covered(changes, 20, 19) else None
            recent72 = covered(tuple(closes[-72:]), 72, 69)
            ema_ready = row is not None and recent72 and state.ema_updates >= 360
            t3 = (state.emas[6] - state.emas[18]) / row.close if ema_ready and row else None
            t4 = (state.emas[24] - state.emas[72]) / row.close if ema_ready and row else None
            t5 = state.normalized_rsi() if row and recent72 else None
            values = {
                "OC": current_return,
                "RMS12": h12,
                "RMS60": h60,
                "RMS63": d63,
                "MOM5": ratio(1, 6),
                "MOM105": ratio(21, 126),
                "B1": math.log(row.high / row.low) if row else None,
                "B2": (
                    0.0
                    if row.zero_range
                    else (2 * row.close - row.high - row.low) / (row.high - row.low)
                )
                if row
                else None,
                "VOLUME_H": row.volume if row else None,
                "VOLUME_D": volumes[-1] if volumes else None,
                "Q1_MEAN": q1,
                "Q2_5": q2short,
                "Q2_60": q2long,
                "T1": math.log(row.close / sma20) if row and sma20 else None,
                "T2": sign20,
                "T3": t3,
                "T4": t4,
                "T5": t5,
            }
            coverage = {
                "M1": current_return is not None and h60 is not None,
                "M2": False,
                "M3": values["MOM5"] is not None and d63 is not None,
                "M4": values["MOM105"] is not None and d63 is not None,
                "V1": h12 is not None,
                "V2": h60 is not None,
                "V3": h12 is not None and h60 is not None,
                "B1": row is not None,
                "B2": row is not None,
                "Q1": row is not None and q1 is not None,
                "Q2": q2short is not None and q2long is not None,
                "T1": values["T1"] is not None,
                "T2": sign20 is not None,
                "T3": t3 is not None,
                "T4": t4 is not None,
                "T5": t5 is not None,
            }
            ids = (row.row_id,) if row else ()
            binding = fingerprint(
                [
                    history.binding,
                    symbol,
                    step.end.isoformat(),
                    source_only,
                    values,
                    coverage,
                    state_lineage,
                    day_lineage[step.session],
                    slot_source_ids,
                ]
            )
            self._components[symbol, step.end, source_only] = Components(
                symbol,
                step,
                values,
                coverage,
                history.binding,
                history.action_binding,
                ids,
                source_only,
                ("ZERO_RANGE",) if row and row.zero_range else (),
                binding,
            )
        self._built.add((symbol, source_only))

    def evaluate(
        self,
        symbol: str,
        step: ScheduledStep,
        origin: int,
        floors: FloorCertificate | None = None,
        m2_floor: M2FloorCertificate | None = None,
        *,
        source_only: bool = False,
        context: Context = "ASOF",
        training_origin: pd.Timestamp | None = None,
    ) -> tuple[FeatureCell, ...]:
        if origin not in (1, 2):
            raise ValueError("ORIGIN_REQUIRED")
        components = self.components(symbol, step, source_only=source_only)
        if floors is not None and (
            floors.source_binding != self.history.binding
            or floors.action_binding != self.history.action_binding
        ):
            raise ValueError("FT0_SOURCE_CERTIFICATE_BINDING_MISMATCH")
        p = floors.for_stock(symbol) if floors else None
        floor_reason = (
            transform_reason(floors.window, step.information_cutoff, context, training_origin)
            if floors
            else "FLOOR_CERTIFICATE_REQUIRED"
        )
        floor_ready = p is not None and floor_reason in {
            "TRANSFORM_AVAILABLE",
            "HISTORICAL_TRAINING_TRANSFORM_ONLY",
        }
        if floors is not None and not self.history.synthetic:
            floor_ready = False
            floor_reason = "SYNTHETIC_CERTIFICATE_NOT_REAL_SOURCE"
        v = components.values
        row = self.history.bars.get((symbol, step.session, step.slot))
        clock_reason = source_reason(row, step.information_cutoff, synthetic=self.history.synthetic)
        raw: dict[str, float | None] = {name: v.get(name) for name in ORDER}
        m2 = None
        if not source_only and clock_reason == "SOURCE_VALID":
            key = symbol, step.end, origin, m2_floor.floor_id if m2_floor else None
            if key not in self._m2:
                self._m2[key] = evaluate_m2(
                    self.history.calendar,
                    self.returns,
                    symbol,
                    step,
                    origin,
                    m2_floor,
                    test_scenario=self.history.synthetic,
                )
            m2 = self._m2[key]
            raw["M2"] = m2.value
        if floor_ready and p is not None:
            h12, h60, daily = v["RMS12"], v["RMS60"], v["RMS63"]
            if v["OC"] is not None and h60 is not None:
                raw["M1"] = v["OC"] / max(h60, p.hourly_floor)
            raw["V1"] = math.log(max(h12, p.hourly_floor)) if h12 is not None else None
            raw["V2"] = math.log(max(h60, p.hourly_floor)) if h60 is not None else None
            if raw["V1"] is not None and raw["V2"] is not None:
                raw["V3"] = raw["V1"] - raw["V2"]
            if daily is not None:
                raw["M3"] = (
                    v["MOM5"] / (math.sqrt(5) * max(daily, p.daily_floor))
                    if v["MOM5"] is not None
                    else None
                )
                raw["M4"] = (
                    v["MOM105"] / (math.sqrt(105) * max(daily, p.daily_floor))
                    if v["MOM105"] is not None
                    else None
                )
            if v["Q1_MEAN"] is not None and v["VOLUME_H"] is not None:
                raw["Q1"] = math.log(
                    (v["VOLUME_H"] + p.hourly_pseudocount) / (v["Q1_MEAN"] + p.hourly_pseudocount)
                )
            if v["Q2_5"] is not None and v["Q2_60"] is not None:
                raw["Q2"] = math.log(
                    (v["Q2_5"] + p.daily_pseudocount) / (v["Q2_60"] + p.daily_pseudocount)
                )
        output = []
        floor_channels = {"M1", "M3", "M4", "V1", "V2", "V3", "Q1", "Q2"}
        for name in ORDER:
            value = raw[name]
            if name == "M2" and m2 is not None:
                reason = "FEATURE_VALID" if m2.reason == "M2_VALID" else m2.reason
            elif name in floor_channels and not floor_ready:
                reason = floor_reason
            else:
                reason = "FEATURE_VALID" if value is not None else "FEATURE_HISTORY_INCOMPLETE"
            if clock_reason != "SOURCE_VALID":
                reason = clock_reason
            if source_only:
                reason = "SOURCE_ONLY_DIAGNOSTIC:" + reason
            if value is not None and not math.isfinite(value):
                raise ValueError("NONFINITE_FT0_FEATURE")
            slot = origin if name == "M2" else step.slot
            canonical_key = symbol, step.session, slot
            lineage = fingerprint(
                [
                    self.history.binding,
                    self.history.action_binding,
                    DICTIONARY_ID,
                    name,
                    canonical_key,
                    m2.reference_ids if name == "M2" and m2 else None,
                    components.lineage_id if name != "M2" else None,
                ]
            )
            output.append(
                FeatureCell(
                    name,
                    value,
                    reason == "FEATURE_VALID",
                    reason,
                    canonical_key,
                    step.end,
                    components.source_ids,
                    lineage,
                    self.history.binding,
                    self.history.action_binding,
                    "SOURCE_ONLY"
                    if source_only
                    else ("SYNTHETIC" if self.history.synthetic else "DOCUMENTED_ASSERTION"),
                    floors.certificate_id if floors else None,
                    m2 if name == "M2" else None,
                )
            )
        return tuple(output)
