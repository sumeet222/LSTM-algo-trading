"""Train-prefix-only preprocessing for the approved conditional candidate study.

These objects intentionally cannot satisfy legacy SYNTHETIC or DOCUMENTED model
interfaces. Their actual construction time is retained, separately from historical
fitting-information bounds and retrospective research application.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import numpy as np

from .config import fingerprint
from .ft0_transforms import (
    ORDER,
    SCALED,
    check_window,
    identity,
    robust_parameters,
    weighted_quantile,
)
from .labels import FitWindow
from .pretraining_policy import CANDIDATE
from .pretraining_tables import BaseTables, tg0
from .stock_features import apply_component_floors


def check_candidate_window(window: FitWindow) -> None:
    """Real candidate preparation admits only the six frozen nonsynthetic prefixes."""
    check_window(window)
    allowed = {stage + ":" + phase for stage in ("WF1", "WF2", "PRECONFIRMATION")
               for phase in ("INNER_TRAIN", "REFIT")}
    if window.window_id not in allowed:
        raise ValueError("FROZEN_NONSYNTHETIC_CANDIDATE_PREFIX_REQUIRED")


@dataclass(frozen=True)
class CandidateFloors:
    symbol: str
    hourly_floor: float
    daily_floor: float
    hourly_pseudocount: float
    daily_pseudocount: float
    m2_floor: float

    def __post_init__(self) -> None:
        if self.symbol not in CANDIDATE or any(
            not math.isfinite(x) or x <= 0 for x in
            (self.hourly_floor, self.daily_floor, self.hourly_pseudocount,
             self.daily_pseudocount, self.m2_floor)
        ):
            raise ValueError("POSITIVE_CANDIDATE_FLOORS_REQUIRED")


@dataclass(frozen=True)
class CandidateScaler:
    centers: tuple[float, ...]
    scales: tuple[float, ...]
    methods: tuple[str, ...]

    def __post_init__(self) -> None:
        if (len(self.centers) != 13 or len(self.scales) != 13 or len(self.methods) != 13
                or not all(math.isfinite(x) for x in self.centers)
                or not all(math.isfinite(x) and x > 0 for x in self.scales)
                or not set(self.methods) <= {"MAD", "IQR_1.349", "AUDITED_POPULATION_SD",
                                             "CONSTANT"}):
            raise ValueError("FINITE_THIRTEEN_CHANNEL_CANDIDATE_SCALER_REQUIRED")

    def apply(self, values: tuple[float, ...]) -> tuple[float, ...]:
        if len(values) != 16 or not all(math.isfinite(x) for x in values):
            raise ValueError("COMPLETE_FINITE_FT0_ROW_REQUIRED")
        output = list(values)
        for i, feature in enumerate(SCALED):
            output[ORDER.index(feature)] = (
                0.0 if self.methods[i] == "CONSTANT"
                else (values[ORDER.index(feature)] - self.centers[i]) / self.scales[i]
            )
        for feature in ("B2", "T2", "T5"):
            if not -1 <= values[ORDER.index(feature)] <= 1:
                raise ValueError("NATIVE_BOUNDED_FT0_REQUIRED")
        return tuple(output)


@dataclass(frozen=True)
class CandidatePreparation:
    window: FitWindow
    floors: tuple[CandidateFloors, ...]
    scaler: CandidateScaler
    target_epsilon: float
    authority_binding: str
    source_binding: str
    action_binding: str
    population_binding: str
    population_counts: dict
    constructed_at: str
    designation: str = "ASSUMPTION_CONDITIONAL_CANDIDATE_NOT_FOR_TRAINING"

    @property
    def preparation_id(self) -> str:
        # Construction wall time is audit metadata; numeric identity is reproducible.
        contents = asdict(self)
        contents.pop("constructed_at")
        return identity(contents)

    def ensure(self, base: BaseTables) -> None:
        base.history.authority.ensure("FIT_TRANSFORM_ONLY")
        if (self.authority_binding != base.history.authority.binding
                or self.source_binding != base.history.binding
                or self.action_binding != base.history.action_binding
                or tuple(p.symbol for p in self.floors) != CANDIDATE
                or self.designation != "ASSUMPTION_CONDITIONAL_CANDIDATE_NOT_FOR_TRAINING"):
            raise ValueError("CANDIDATE_PREPROCESS_SOURCE_POLICY_MISMATCH")
        check_candidate_window(self.window)


def raw_features(base: BaseTables, symbol: str, position: int, origin: int,
                 floors: CandidateFloors) -> tuple[tuple[float | None, ...], tuple[str, ...]]:
    step = base.history.calendar.steps[position]
    component = base.components[symbol, step.session, step.slot]
    values = apply_component_floors(component.values, floors)
    stat = base.m2[symbol, step.session, origin]
    valid_m2 = (stat.reason == "M2_HISTORY_VALID" and stat.mean20 is not None
                and stat.rms60 is not None and stat.maturity is not None
                and stat.maturity <= step.end)
    values["M2"] = (stat.mean20 / max(stat.rms60, floors.m2_floor)
                    if valid_m2 and stat.mean20 is not None and stat.rms60 is not None else None)
    reasons = tuple("VALID" if values[f] is not None and (
        valid_m2 if f == "M2" else component.coverage[f]) else "INVALID_" + f for f in ORDER)
    return tuple(values[f] if reasons[i] == "VALID" else None for i, f in enumerate(ORDER)), reasons


def canonical_population(base: BaseTables, window: FitWindow) -> tuple[
    tuple[tuple[str, int], ...], tuple[int, ...]
]:
    """Canonical unique feature positions; training membership/purge is explicit."""
    check_candidate_window(window)
    origins = []
    positions = set()
    for key, panel in sorted(base.panels.items()):
        if not window.start <= panel.cutoff < window.stop:
            continue
        input_valid, _ = base.potential(*key)
        if (not input_valid or not panel.label_valid or panel.maturity is None
                or panel.maturity >= window.stop or panel.maturity > window.fitted_at):
            continue
        origins.append(key)
        for pos in base.origin_steps[key]:
            step = base.history.calendar.steps[pos]
            if window.start <= step.end < window.stop:
                positions.add(pos)
    if not origins or not positions:
        raise ValueError("VALID_PURGED_TRAINING_POPULATION_REQUIRED")
    return tuple(origins), tuple(sorted(positions))


def positive_sample(values: tuple[float | None, ...]) -> np.ndarray:
    found = np.asarray([x for x in values if x is not None and math.isfinite(x) and x > 0])
    if not len(found):
        raise ValueError("POSITIVE_TRAINING_POPULATION_REQUIRED")
    return found


def derive_floors(base: BaseTables, positions: tuple[int, ...],
                  window: FitWindow) -> tuple[CandidateFloors, ...]:
    calendar = base.history.calendar
    days = tuple(sorted({calendar.steps[pos].session for pos in positions}))
    output = []
    for symbol in CANDIDATE:
        rows = [base.components[symbol, calendar.steps[p].session, calendar.steps[p].slot]
                for p in positions]
        # Daily measurements count once per session, never six times per hour.
        daily = [base.components[symbol, day, 1].values for day in days]
        volumes = tuple(row.volume for (name, _), row in sorted(base.history.daily.items())
                        if name == symbol and window.start <= row.end < window.stop)
        h = positive_sample(tuple(r.values[k] for r in rows for k in ("RMS12", "RMS60")))
        d = positive_sample(tuple(r["RMS63"] for r in daily))
        hv = positive_sample(tuple(r.values["VOLUME_H"] for r in rows))
        dv = positive_sample(volumes)
        moments = [base.m2[symbol, day, o] for day in days for o in (1, 2)]
        good = [r for r in moments if r.rms60 is not None and r.rms60 > 0
                and r.reason == "M2_HISTORY_VALID"]
        counts = {o: sum(r.origin == o for r in good) for o in (1, 2)}
        if not all(counts.values()):
            raise ValueError("BOTH_M2_TRAINING_ORIGINS_REQUIRED")
        m2 = weighted_quantile(np.asarray([r.rms60 for r in good], dtype=float),
                               np.asarray([0.5 / counts[r.origin] for r in good]), 0.05)
        output.append(CandidateFloors(symbol, float(np.percentile(h, 5)),
                                      float(np.percentile(d, 5)), 0.01 * float(np.median(hv)),
                                      0.01 * float(np.median(dv)), m2))
    return tuple(output)


def fit_preparation(base: BaseTables, window: FitWindow) -> CandidatePreparation:
    """Fit only FT0 floor/pseudocount/scaler + TG0 floor, never estimator weights."""
    base.history.authority.ensure("FIT_TRANSFORM_ONLY")
    origins, positions = canonical_population(base, window)
    floors = derive_floors(base, positions, window)
    records: dict[tuple[str, str, str, int], float] = {}
    for p in floors:
        for pos in positions:
            step = base.history.calendar.steps[pos]
            for origin in (1, 2):
                values, _ = raw_features(base, p.symbol, pos, origin, p)
                for name in SCALED:
                    value = values[ORDER.index(name)]
                    if value is not None:
                        key = p.symbol, name, step.session, origin if name == "M2" else step.slot
                        previous = records.get(key)
                        if previous is not None and previous != value:
                            raise ValueError("CONFLICTING_CANONICAL_FEATURE_KEY")
                        records[key] = value
    centers, scales, methods, counts = [], [], [], {}
    for feature in SCALED:
        items = [(key, value) for key, value in sorted(records.items()) if key[1] == feature]
        weights = None
        if feature == "M2":
            n = {o: sum(key[3] == o for key, _ in items) for o in (1, 2)}
            if not all(n.values()):
                raise ValueError("BOTH_POOLED_M2_ORIGINS_REQUIRED")
            weights = np.asarray([0.5 / n[key[3]] for key, _ in items])
        center, scale, method = robust_parameters(np.asarray([v for _, v in items]), weights)
        centers.append(center)
        scales.append(scale)
        methods.append(method)
        counts[feature] = len(items)
    mads = []
    for key in origins:
        moments = base.panels[key].median_mad
        if moments is not None:
            mads.append(moments[1])
    if not mads:
        raise ValueError("TRAINING_TARGET_FLOOR_POPULATION_REQUIRED")
    epsilon = max(1e-4, 0.1 * float(np.median(mads)))
    return CandidatePreparation(
        window, floors, CandidateScaler(tuple(centers), tuple(scales), tuple(methods)), epsilon,
        base.history.authority.binding, base.history.binding, base.history.action_binding,
        fingerprint([origins, positions, sorted(records.items())]),
        {"origins": len(origins), "feature_positions": len(positions), "scaled": counts,
         "m2_origin_weights": [0.5, 0.5], "daily_floors": "UNIQUE_SESSION",
         "target_mad_origins": len(mads)}, datetime.now(timezone.utc).isoformat(),
    )


class CandidateView:
    """Shared canonical components + on-demand windows; never a neural Permission."""

    def __init__(self, base: BaseTables, preparation: CandidatePreparation):
        preparation.ensure(base)
        self.base = base
        self.preparation = preparation
        self._rows: dict[tuple[str, int, int], tuple[float, ...] | None] = {}

    def row(self, symbol: str, pos: int, origin: int) -> tuple[float, ...] | None:
        key = symbol, pos, origin
        if key not in self._rows:
            floors = self.preparation.floors[CANDIDATE.index(symbol)]
            values, _ = raw_features(self.base, symbol, pos, origin, floors)
            self._rows[key] = (self.preparation.scaler.apply(tuple(x for x in values
                                                                     if x is not None))
                               if all(x is not None for x in values) else None)
        return self._rows[key]

    def input_status(self, day: str, origin: int) -> tuple[bool, tuple[str, ...]]:
        valid, reasons = self.base.potential(day, origin)
        if not valid:
            return valid, reasons
        positions = self.base.origin_steps[day, origin]
        bad = {"TRANSFORM_OR_FEATURE_INVALID" for s in CANDIDATE for pos in positions
               if self.row(s, pos, origin) is None}
        return not bad, tuple(sorted(bad))

    def window(self, day: str, origin: int) -> tuple[np.ndarray, np.ndarray]:
        """Explicit candidate review access; training/replay entry points still reject."""
        self.preparation.ensure(self.base)
        valid, _ = self.input_status(day, origin)
        panel = self.base.panels[day, origin]
        if not valid or not panel.label_valid or panel.maturity is None:
            raise ValueError("COMPLETE_INPUT_AND_MATURE_LABEL_REQUIRED")
        values = [[self.row(s, pos, origin) for pos in self.base.origin_steps[day, origin]]
                  for s in CANDIDATE]
        x = np.asarray(values, dtype=float)
        y = np.asarray(tg0(tuple(v for v in panel.returns if v is not None),
                          self.preparation.target_epsilon))
        if x.shape != (5, 48, 16) or y.shape != (5,) or not np.isfinite(x).all():
            raise ValueError("EXACT_CANDIDATE_WINDOW_REQUIRED")
        return x, y
