"""Versioned FT0 synthetic fitting and guarded apply; no uncertified empirical fits."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from functools import cached_property
from typing import Literal

import numpy as np
import pandas as pd

from .clocks import utc
from .config import fingerprint
from .hourly_proxy import ProxyLabelSample, proxy_fitting_membership
from .labels import UNIVERSE, FitWindow, fitting_window
from .m2 import M2FloorCertificate, M2Result, canonical_m2_keys
from .stock_source import STOCK_VERSION

FT0_VERSION = "FT0:HOURLY_CLOSE_PROXY:v1"
ORDER = (
    "M1",
    "M2",
    "M3",
    "M4",
    "V1",
    "V2",
    "V3",
    "B1",
    "B2",
    "Q1",
    "Q2",
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
)
SCALED = ("M1", "M2", "M3", "M4", "V1", "V2", "V3", "B1", "Q1", "Q2", "T1", "T3", "T4")
DICTIONARY_ID = fingerprint([FT0_VERSION, ORDER, "TA-P2-FT0-Q-VOLUME-001"])
Context = Literal["ASOF", "HISTORICAL_TRAINING"]


def identity(value: object) -> str:
    return fingerprint(json.loads(json.dumps(value, default=str, sort_keys=True)))


def check_window(window: FitWindow) -> None:
    start, stop, fitted = utc(window.start), utc(window.stop), utc(window.fitted_at)
    if (
        window.phase not in {"INNER_TRAIN", "REFIT"}
        or start >= stop
        or fitted < stop
        or start < pd.Timestamp("2020-07-01", tz="America/New_York").tz_convert("UTC")
        or stop > pd.Timestamp("2024-07-01", tz="America/New_York").tz_convert("UTC")
    ):
        raise ValueError("PERMITTED_TRAINING_PREFIX_REQUIRED")
    if window.window_id.startswith("SYNTHETIC:"):
        return
    stage, separator, phase = window.window_id.partition(":")
    if stage not in {"WF1", "WF2", "PRECONFIRMATION"} or not separator or phase != window.phase:
        raise ValueError("FROZEN_FIT_FOLD_REQUIRED")
    # Narrow by explicit membership, retaining the authoritative existing constructor.
    if stage == "WF1":
        expected = fitting_window("WF1", window.phase, fitted_at=fitted)
    elif stage == "WF2":
        expected = fitting_window("WF2", window.phase, fitted_at=fitted)
    else:
        expected = fitting_window("PRECONFIRMATION", window.phase, fitted_at=fitted)
    if (start, stop) != (expected.start, expected.stop):
        raise ValueError("FROZEN_FIT_BOUNDARY_REQUIRED")


def transform_reason(
    window: FitWindow,
    cutoff: pd.Timestamp,
    context: Context,
    training_origin: pd.Timestamp | None = None,
) -> str:
    """Historical training use keeps factual fitted_at; it never claims live availability."""
    check_window(window)
    cutoff = utc(cutoff)
    if context == "ASOF":
        return "TRANSFORM_AVAILABLE" if window.fitted_at <= cutoff else "FIT_AFTER_STEP_CUTOFF"
    if context != "HISTORICAL_TRAINING":
        raise ValueError("EXPLICIT_APPLICATION_CONTEXT_REQUIRED")
    if (
        training_origin is None
        or not window.start <= utc(training_origin) < window.stop
        or cutoff > utc(training_origin)
    ):
        return "TRAINING_ORIGIN_OUTSIDE_CERTIFIED_PREFIX"
    return "HISTORICAL_TRAINING_TRANSFORM_ONLY"


@dataclass(frozen=True)
class FitObservation:
    symbol: str
    timestamp: pd.Timestamp
    kind: str
    key: tuple[str, str, int]
    value: float
    source_id: str
    source_binding: str
    action_binding: str
    basis: Literal["SYNTHETIC", "DOCUMENTED"]
    available_at: pd.Timestamp
    origin: int | None = None
    label: ProxyLabelSample | None = None
    source_version: str = STOCK_VERSION
    dictionary_id: str = DICTIONARY_ID

    def __post_init__(self) -> None:
        utc(self.timestamp)
        utc(self.available_at)
        if (
            self.symbol not in UNIVERSE
            or self.source_version != STOCK_VERSION
            or self.dictionary_id != DICTIONARY_ID
            or self.key[0] != self.symbol
            or isinstance(self.value, bool)
            or not math.isfinite(self.value)
            or not self.source_id.strip()
            or len(self.source_binding) != 64
            or len(self.action_binding) != 64
            or self.basis not in {"SYNTHETIC", "DOCUMENTED"}
        ):
            raise ValueError("FIT_OBSERVATION_PROVENANCE_REQUIRED")
        if self.kind == "M2" and (self.origin not in (1, 2) or self.key[2] != self.origin):
            raise ValueError("M2_ORIGIN_KEY_REQUIRED")


def population(
    records: tuple[FitObservation, ...], window: FitWindow, *, allow_synthetic: bool
) -> tuple[FitObservation, ...]:
    """Filter only permitted training observations; contradictory duplicates fail closed."""
    check_window(window)
    selected: dict[tuple[str, tuple[str, str, int]], FitObservation] = {}
    for row in records:
        if not window.start <= row.timestamp < window.stop:
            continue
        if row.available_at > window.fitted_at or row.available_at > row.timestamp:
            raise ValueError("FIT_OBSERVATION_NOT_AVAILABLE_AT_OWN_CUTOFF")
        if not allow_synthetic or row.basis != "SYNTHETIC":
            raise ValueError("FIT_PENDING_SOURCE_EVIDENCE")
        if (
            row.label is not None
            and proxy_fitting_membership(row.label, window, test_scenario=True) != "FIT_ELIGIBLE"
        ):
            raise ValueError("LABEL_INFLUENCED_POPULATION_PURGED")
        key = row.kind, row.key
        prior = selected.get(key)
        if prior is not None and (
            prior.value,
            prior.source_id,
            prior.source_binding,
            prior.action_binding,
            prior.origin,
        ) != (row.value, row.source_id, row.source_binding, row.action_binding, row.origin):
            raise ValueError("CONTRADICTORY_CANONICAL_FIT_KEY")
        selected[key] = row
    if not selected:
        raise ValueError("VALID_TRAINING_POPULATION_REQUIRED")
    bindings = {(r.source_binding, r.action_binding) for r in selected.values()}
    if len(bindings) != 1:
        raise ValueError("FIT_SOURCE_ACTION_BINDING_MISMATCH")
    return tuple(selected[k] for k in sorted(selected))


@dataclass(frozen=True)
class StockParameters:
    symbol: str
    hourly_floor: float
    daily_floor: float
    hourly_pseudocount: float
    daily_pseudocount: float

    def __post_init__(self) -> None:
        if self.symbol not in UNIVERSE or any(
            isinstance(x, bool) or not math.isfinite(x) or x <= 0
            for x in (
                self.hourly_floor,
                self.daily_floor,
                self.hourly_pseudocount,
                self.daily_pseudocount,
            )
        ):
            raise ValueError("POSITIVE_STOCK_FLOORS_AND_PSEUDOCOUNTS_REQUIRED")


@dataclass(frozen=True)
class FloorCertificate:
    values: tuple[StockParameters, ...]
    window: FitWindow
    keys: tuple[tuple[str, tuple[str, str, int]], ...]
    source_binding: str
    action_binding: str
    evidence_ref: str
    source_version: str = STOCK_VERSION
    dictionary_id: str = DICTIONARY_ID
    basis: str = "SYNTHETIC"
    method: str = "POSITIVE_RMS_P05_VOLUME_POSITIVE_MEDIAN_1PCT"

    def __post_init__(self) -> None:
        check_window(self.window)
        if (
            tuple(v.symbol for v in self.values) != UNIVERSE
            or self.source_version != STOCK_VERSION
            or self.dictionary_id != DICTIONARY_ID
            or self.basis != "SYNTHETIC"
            or not self.evidence_ref.strip()
            or not self.keys
            or len(set(self.keys)) != len(self.keys)
            or len(self.source_binding) != 64
            or len(self.action_binding) != 64
        ):
            raise ValueError("FLOOR_CERTIFICATE_LINEAGE_REQUIRED")

    @cached_property
    def certificate_id(self) -> str:
        return identity(asdict(self))

    def for_stock(self, symbol: str) -> StockParameters:
        if symbol not in UNIVERSE:
            raise ValueError("CANONICAL_STOCK_REQUIRED")
        return self.values[UNIVERSE.index(symbol)]


def fit_floors(
    records: tuple[FitObservation, ...],
    window: FitWindow,
    evidence_ref: str,
    *,
    allow_synthetic: bool = False,
) -> FloorCertificate:
    selected = population(records, window, allow_synthetic=allow_synthetic)
    if any(r.kind not in {"RMS12", "RMS60", "RMS63", "VOLUME_H", "VOLUME_D"} for r in selected):
        raise ValueError("FLOOR_POPULATION_KIND_REQUIRED")
    values = []
    for symbol in UNIVERSE:

        def sample(kinds: set[str]) -> np.ndarray:
            found = [
                r.value for r in selected if r.symbol == symbol and r.kind in kinds and r.value > 0
            ]
            if not found:
                raise ValueError("POSITIVE_TRAINING_POPULATION_REQUIRED")
            return np.asarray(found, dtype=float)

        values.append(
            StockParameters(
                symbol,
                float(np.percentile(sample({"RMS12", "RMS60"}), 5)),
                float(np.percentile(sample({"RMS63"}), 5)),
                0.01 * float(np.median(sample({"VOLUME_H"}))),
                0.01 * float(np.median(sample({"VOLUME_D"}))),
            )
        )
    return FloorCertificate(
        tuple(values),
        window,
        tuple((r.kind, r.key) for r in selected),
        selected[0].source_binding,
        selected[0].action_binding,
        evidence_ref,
    )


def weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    """Weighted CDF quantile; exact boundary ties take adjacent midpoint. No replication."""
    order = np.argsort(values, kind="stable")
    data, normalized = values[order], weights[order] / float(weights.sum())
    cumulative = np.cumsum(normalized)
    index = min(int(np.searchsorted(cumulative, quantile, side="left")), len(data) - 1)
    if index + 1 < len(data) and math.isclose(float(cumulative[index]), quantile, abs_tol=1e-12):
        return float((data[index] + data[index + 1]) / 2)
    return float(data[index])


@dataclass(frozen=True)
class ScalerCertificate:
    centers: tuple[float, ...]
    scales: tuple[float, ...]
    methods: tuple[str, ...]
    window: FitWindow
    keys: tuple[tuple[str, tuple[str, str, int]], ...]
    weights: tuple[float, ...]
    source_binding: str
    action_binding: str
    evidence_ref: str
    order: tuple[str, ...] = ORDER
    source_version: str = STOCK_VERSION
    dictionary_id: str = DICTIONARY_ID
    basis: str = "SYNTHETIC"

    def __post_init__(self) -> None:
        check_window(self.window)
        if (
            self.order != ORDER
            or len(self.centers) != 13
            or len(self.scales) != 13
            or len(self.methods) != 13
            or any(not math.isfinite(x) for x in self.centers)
            or any(not math.isfinite(x) or x <= 0 for x in self.scales)
            or not set(self.methods) <= {"MAD", "IQR_1.349", "AUDITED_POPULATION_SD", "CONSTANT"}
            or self.source_version != STOCK_VERSION
            or self.dictionary_id != DICTIONARY_ID
            or self.basis != "SYNTHETIC"
            or not self.evidence_ref.strip()
            or len(self.keys) != len(self.weights)
            or len(set(self.keys)) != len(self.keys)
            or not self.keys
            or len(self.source_binding) != 64
            or len(self.action_binding) != 64
        ):
            raise ValueError("SCALER_CERTIFICATE_PROVENANCE_REQUIRED")

    @cached_property
    def certificate_id(self) -> str:
        return identity(asdict(self))

    def apply(
        self,
        feature: str,
        value: float,
        cutoff: pd.Timestamp,
        *,
        source_binding: str,
        action_binding: str,
        context: Context = "ASOF",
        training_origin: pd.Timestamp | None = None,
    ) -> tuple[float | None, str, bool]:
        if (
            feature not in ORDER
            or not math.isfinite(value)
            or source_binding != self.source_binding
            or action_binding != self.action_binding
        ):
            raise ValueError("SCALER_FEATURE_SOURCE_ACTION_MISMATCH")
        reason = transform_reason(self.window, cutoff, context, training_origin)
        if reason not in {"TRANSFORM_AVAILABLE", "HISTORICAL_TRAINING_TRANSFORM_ONLY"}:
            return None, reason, False
        if feature not in SCALED:
            if not -1 <= value <= 1:
                raise ValueError("NATIVE_BOUNDED_FEATURE_REQUIRED")
            return value, reason, False
        index = SCALED.index(feature)
        constant = self.methods[index] == "CONSTANT"
        return (
            0.0 if constant else (value - self.centers[index]) / self.scales[index],
            reason,
            constant and value != self.centers[index],
        )


def fit_scaler(
    records: tuple[FitObservation, ...],
    window: FitWindow,
    evidence_ref: str,
    *,
    allow_synthetic: bool = False,
) -> ScalerCertificate:
    selected = population(records, window, allow_synthetic=allow_synthetic)
    if any(r.kind not in SCALED for r in selected):
        raise ValueError("THIRTEEN_POOLED_SCALED_CHANNELS_REQUIRED")
    centers, scales, methods, key_weights = [], [], [], {}
    for feature in SCALED:
        rows = [r for r in selected if r.kind == feature]
        if not rows:
            raise ValueError("COMPLETE_SCALER_POPULATION_REQUIRED")
        values = np.asarray([r.value for r in rows], dtype=float)
        weights = np.full(len(rows), 1 / len(rows))
        if feature == "M2":
            counts = {o: sum(r.origin == o for r in rows) for o in (1, 2)}
            if not all(counts.values()):
                raise ValueError("BOTH_M2_ORIGIN_TYPES_REQUIRED")
            weights = np.asarray(
                [0.5 / counts[1] if r.origin == 1 else 0.5 / counts[2] for r in rows], dtype=float
            )
            center = weighted_quantile(values, weights, 0.5)
            mad = weighted_quantile(np.abs(values - center), weights, 0.5)
            iqr = (
                weighted_quantile(values, weights, 0.75) - weighted_quantile(values, weights, 0.25)
            ) / 1.349
        else:
            center = float(np.median(values))
            mad = float(np.median(np.abs(values - center)))
            iqr = float(np.diff(np.percentile(values, [25, 75]))[0]) / 1.349
        sd = math.sqrt(float(np.sum(weights * (values - float(np.sum(values * weights))) ** 2)))
        if mad > 0:
            scale, method = mad, "MAD"
        elif iqr > 0:
            scale, method = iqr, "IQR_1.349"
        elif sd > 0:
            scale, method = sd, "AUDITED_POPULATION_SD"
        else:
            scale, method = 1.0, "CONSTANT"
        centers.append(center)
        scales.append(scale)
        methods.append(method)
        key_weights.update({(r.kind, r.key): float(w) for r, w in zip(rows, weights)})
    keys = tuple((r.kind, r.key) for r in selected)
    return ScalerCertificate(
        tuple(centers),
        tuple(scales),
        tuple(methods),
        window,
        keys,
        tuple(key_weights[k] for k in keys),
        selected[0].source_binding,
        selected[0].action_binding,
        evidence_ref,
    )


def fit_m2_floor(
    results: tuple[M2Result, ...],
    window: FitWindow,
    symbol: str,
    evidence_ref: str,
    *,
    allow_synthetic: bool = False,
) -> M2FloorCertificate:
    """Fit only existing approved M2 RMS outputs; this is not a second M2 calculator."""
    check_window(window)
    if not allow_synthetic or symbol not in UNIVERSE:
        raise ValueError("FIT_PENDING_SOURCE_EVIDENCE")
    selected = tuple(
        r for r in results if r.key[0] == symbol and window.start <= r.step.end < window.stop
    )
    weighted = canonical_m2_keys(selected)
    unique = {r.key: r for r in selected}
    values, weights, keys = [], [], []
    for key, weight in weighted:
        row = unique[key]
        if row.rms60 is not None and row.rms60 > 0:
            values.append(row.rms60)
            weights.append(weight)
            keys.append(key)
    if not values:
        raise ValueError("POSITIVE_M2_RMS_TRAINING_POPULATION_REQUIRED")
    epsilon = weighted_quantile(np.asarray(values), np.asarray(weights), 0.05)
    return M2FloorCertificate(epsilon, window, tuple(keys), evidence_ref, "SYNTHETIC")
