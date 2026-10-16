"""Complete target relations, typed registry and display-only range operations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil, isfinite
from typing import Literal

import numpy as np
import pandas as pd

from ..pretraining_policy import CANDIDATE
from ..pretraining_store import read_preparation
from ..pretraining_tables import BaseTables, tg0
from ..stock_source import numeric
from .controlled import KEYS, Study
from .loaders import ET, ViewUnavailable, date_window


def tg0_decomposition(
    study: Study, base: BaseTables, fold: str, population: str, seed: int
) -> pd.DataFrame:
    """Verify the entire original population before deriving any display subset."""
    prefix = "inner" if population == "Inner-training prefix" else "refit"
    prep = read_preparation(study.catalog.root, study.catalog.config["recipes"][fold][prefix])
    if population in ("Full refit prefix", "Inner-training prefix"):
        original = study.training_targets(base, fold, prefix)
        population_id = study.parameter(fold, "T2", prefix)["target_population_hash"]
        tolerance = 1e-12
    elif population == "Development":
        original = study.panel(fold, seed, "C0", "Development")
        population_id = f"{fold}:Development:{prep.preparation_id}"
        tolerance = 2e-6  # Saved outcomes are float32; registered training labels are float64.
    else:
        raise ViewUnavailable("Unregistered target population.")
    rows = []
    for (day, origin), group in original.groupby(["session", "origin"], sort=True):
        date_window(str(day), str(day))
        if not isinstance(origin, (int, np.integer)) or origin not in (1, 2):
            raise ViewUnavailable("Integer registered forecast-origin type required.")
        panel = base.panels[str(day), int(origin)]
        moments = panel.median_mad
        if moments is None or panel.maturity is None:
            raise ViewUnavailable("Registered mature decomposition unavailable.")
        values = tuple(v for v in panel.returns if v is not None)
        targets = tg0(values, prep.target_epsilon)
        median, mad = moments
        for r in group.itertuples():
            j = CANDIDATE.index(str(r.symbol))
            target = targets[j]
            if abs(target - numeric(r.TG0)) > tolerance:
                raise ViewUnavailable("Registered target/decomposition mismatch.")
            rows.append(
                dict(
                    session=str(day),
                    origin=int(origin),
                    symbol=str(r.symbol),
                    TG0=target,
                    abs_target=abs(target),
                    cutoff=panel.cutoff,
                    origin_ET=str(panel.cutoff.tz_convert(ET)),
                    origin_UTC=str(panel.cutoff),
                    log_return=values[j],
                    median=median,
                    MAD=mad,
                    epsilon=prep.target_epsilon,
                    denominator=mad + prep.target_epsilon,
                    numerator=values[j] - median,
                    floor_ge_MAD=prep.target_epsilon >= mad,
                    MAD_lt_epsilon=mad < prep.target_epsilon,
                    maturity=panel.maturity,
                    population_id=population_id,
                    preparation_id=prep.preparation_id,
                    observation_id=f"{population_id}|{day}|{origin}|{r.symbol}|{panel.cutoff}",
                )
            )
    frame = pd.DataFrame(rows)
    if frame.empty or frame.duplicated(KEYS).any() or frame.observation_id.duplicated().any():
        raise ViewUnavailable("Complete unique target population required.")
    return frame


@dataclass(frozen=True)
class TargetSpec:
    key: str
    unit: str
    semantics: str
    provenance: str
    eligibility: str
    maturity: str
    horizon_full_hours: int | None
    decomposition: Callable[[Study, BaseTables, str, str, int], pd.DataFrame]


TARGETS = {
    "TG0": TargetSpec(
        "TG0",
        "dimensionless canonical relative return",
        "signed; absolute magnitude optional",
        "Registered tg0 / immutable candidate panels + saved training epsilon",
        "Exact registered purged inner/refit population or saved development mask",
        "EX-POST; all five outcomes mature at registered nominal exit event",
        4,
        tg0_decomposition,
    )
}


def target_spec(key: str) -> TargetSpec:
    if key not in TARGETS:
        raise ViewUnavailable(f"NOT_IMPLEMENTED: {key} has no registered target or horizon.")
    return TARGETS[key]


@dataclass(frozen=True)
class TargetRange:
    mode: Literal["Signed", "Absolute"] = "Absolute"
    lower: float | None = None
    upper: float | None = None
    include_lower: bool = True
    include_upper: bool = True

    def __post_init__(self) -> None:
        if self.mode not in ("Signed", "Absolute"):
            raise ViewUnavailable("Choose Signed or Absolute range units.")
        if any(v is not None and not isfinite(v) for v in (self.lower, self.upper)):
            raise ViewUnavailable("Bounds must be finite numbers or blank.")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ViewUnavailable("Lower bound must be <= upper bound.")

    @classmethod
    def parse(cls, mode: str, lower: str, upper: str, left: bool, right: bool) -> TargetRange:
        try:
            a = float(lower) if lower.strip() else None
            b = float(upper) if upper.strip() else None
        except ValueError as exc:
            raise ViewUnavailable("Bounds must be finite numbers or blank.") from exc
        if mode not in ("Signed", "Absolute"):
            raise ViewUnavailable("Choose Signed or Absolute range units.")
        return cls(mode, a, b, left, right)

    def select(self, frame: pd.DataFrame, spec: TargetSpec) -> pd.DataFrame:
        values = frame[spec.key].abs() if self.mode == "Absolute" else frame[spec.key]
        mask = np.isfinite(values)
        if self.lower is not None:
            mask &= values.ge(self.lower) if self.include_lower else values.gt(self.lower)
        if self.upper is not None:
            mask &= values.le(self.upper) if self.include_upper else values.lt(self.upper)
        return frame.loc[mask].copy()


SORTS = {
    "Absolute target": "abs_target",
    "Signed target": "TG0",
    "Date": "session",
    "Stock": "symbol",
    "Origin": "origin",
}


def ordered(
    frame: pd.DataFrame, by: str, ascending: bool, spec: TargetSpec | None = None
) -> pd.DataFrame:
    if by not in SORTS:
        raise ViewUnavailable("Unregistered sort key.")
    field = spec.key if by == "Signed target" and spec is not None else SORTS[by]
    return frame.sort_values([field, "observation_id"], ascending=[ascending, True])


def page_rows(frame: pd.DataFrame, page: int, size: int) -> tuple[pd.DataFrame, int]:
    if size not in (25, 50, 100, 200):
        raise ViewUnavailable("Choose a bounded page size.")
    pages = max(1, ceil(len(frame) / size))
    if not 1 <= page <= pages:
        raise ViewUnavailable("Page outside matching relation.")
    return frame.iloc[(page - 1) * size : page * size].copy(), pages


def retained_selection(frame: pd.DataFrame, selected: str | None) -> str | None:
    """Retain identity through sorting; clear it when population/filter removes it."""
    return selected if selected is not None and selected in set(frame.observation_id) else None


def denominator_comparison(frame: pd.DataFrame, spec: TargetSpec) -> pd.DataFrame:
    rows = []
    for name, bounds in (
        ("ordinary |TG|<2", TargetRange("Absolute", upper=2, include_upper=False)),
        ("moderate 2<=|TG|<5", TargetRange("Absolute", 2, 5, include_upper=False)),
        ("extreme |TG|>=10", TargetRange("Absolute", 10)),
    ):
        part = bounds.select(frame, spec)
        for field in ("log_return", "MAD", "epsilon", "denominator", "numerator"):
            values = part[field].abs()
            rows.append(
                dict(
                    range=name,
                    field="|" + field + "|",
                    observations=len(part),
                    p25=values.quantile(0.25),
                    median=values.median(),
                    p75=values.quantile(0.75),
                    p95=values.quantile(0.95),
                )
            )
    return pd.DataFrame(rows)
