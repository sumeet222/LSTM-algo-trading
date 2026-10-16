"""Exact historical FT0 audit populations, with no model fitting or target construction."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .config import fingerprint
from .ft0_transforms import ORDER, SCALED, identity
from .pretraining_policy import CANDIDATE
from .pretraining_source import BARRIER
from .pretraining_store import read_preparation
from .pretraining_tables import BaseTables
from .pretraining_transforms import (
    CandidatePreparation,
    CandidateView,
    canonical_population,
    raw_features,
)
from .stock_source import numeric
from .visualization.controlled import Study
from .visualization.definitions import FEATURES
from .visualization.loaders import Catalog, ViewUnavailable, predictions

PARTS = ("Inner training", "Inner validation", "Refit training", "Development")
PREFIX = {p: "inner" if p.startswith("Inner") else "refit" for p in PARTS}
BOUNDED = ("B2", "T2", "T5")


def audit_guard(end: str = "2024-06-30") -> None:
    """Validate the fixed read scope before Catalog discovery or any numerical reader."""
    day = pd.Timestamp(end)
    if day.tzinfo is not None or day != pd.Timestamp("2024-06-30"):
        raise ViewUnavailable(
            "012A is fixed to preconfirmation through 2024-06-30; protected I/O denied."
        )


@dataclass
class Population:
    fold: str
    partition: str
    preparation: CandidatePreparation
    frame: pd.DataFrame
    metadata: dict

    def channel(self, feature: str, origin: int | None = None) -> pd.DataFrame:
        """M2 retains mandatory origin identity; the other fifteen collapse duplicate contexts."""
        if feature not in ORDER:
            raise ViewUnavailable("Unknown FT0 feature.")
        data = self.frame
        if origin is not None:
            data = data.loc[data.origin.eq(origin)]
        if feature != "M2" and origin is None:
            grouped = data.groupby(["symbol", "timestamp"])
            used = grouped.ever_model_input.transform("max")
            exposures = grouped.exposure.transform("sum")
            data = data.assign(ever_model_input=used, exposure=exposures)
            data = data.sort_values("origin").drop_duplicates(["symbol", "timestamp"])
        return data

    def tags(self, feature: str, representation: str, stock: str = "POOLED") -> dict:
        p = self.preparation
        return dict(
            fold=self.fold,
            partition=self.partition,
            recipe_id=p.preparation_id,
            feature=feature,
            label=FEATURES[feature],
            representation=representation,
            symbol=stock,
            units="dimensionless " + representation,
            clock="UTC completed-hour END; ET session; idealized period-end",
            population_key="symbol/UTC/recipe" + ("/origin" if feature == "M2" else ""),
            input_status="see ever_model_input_count; no new predictions",
            source_binding=p.source_binding,
        )


def population(
    catalog: Catalog, base: BaseTables, study: Study, fold: str, part: str, view: CandidateView
) -> Population:
    """Use the exact registered masks; do not intersect incompatible populations."""
    audit_guard()
    if fold not in ("WF1", "WF2") or part not in PARTS:
        raise ViewUnavailable("Unregistered fold/partition; no confirmation audit.")
    prep = view.preparation
    if prep.window.window_id != f"{fold}:" + (
        "INNER_TRAIN" if PREFIX[part] == "inner" else "REFIT"
    ):
        raise ViewUnavailable("Wrong preparation for partition.")
    prep.ensure(base)
    fit_keys, fit_positions = canonical_population(base, prep.window)
    training = part.endswith("training")
    if training:
        keys = fit_keys
    else:
        saved = predictions(catalog, fold, "TM0", part)
        keys = tuple(sorted(set(zip(saved.session, saved.origin))))
    expected_key = {
        "Inner training": "inner",
        "Inner validation": "validation",
        "Refit training": "refit",
        "Development": fold,
    }[part]
    expected = study.json("input_binding.json")["views"][fold][expected_key]
    if len(keys) != expected["origins"] or expected["preparation_id"] != prep.preparation_id:
        raise ViewUnavailable("Actual mask/count/preparation differs from sealed neural inputs.")
    exposure: Counter[tuple[int, int]] = Counter()
    consumers: dict[tuple[int, int], str] = {}
    for day, origin in keys:
        panel = base.panels[day, origin]
        if panel.cutoff >= BARRIER or panel.maturity is None or panel.maturity >= BARRIER:
            raise ViewUnavailable("Confirmation or immature panel forbidden.")
        positions = base.origin_steps[day, origin]
        if len(positions) != 48 or base.history.calendar.steps[positions[-1]].end != panel.cutoff:
            raise ViewUnavailable("Exact scheduled 48-step mask required.")
        for pos in positions:
            step = base.history.calendar.steps[pos]
            if step.end > panel.cutoff or (not training and step.end < prep.window.stop):
                raise ViewUnavailable(
                    "Future step or scaler not available at historical input step."
                )
            exposure[pos, origin] += 1
            consumers.setdefault((pos, origin), day)
    positions = sorted({pos for pos, _ in exposure})
    if training:
        positions = list(fit_positions)  # Warm-up may be used by models, never fit membership.
    rows = []
    for symbol, floors in zip(CANDIDATE, prep.floors):
        for pos in positions:
            step = base.history.calendar.steps[pos]
            if step.end >= BARRIER:
                raise ViewUnavailable("Protected feature step forbidden.")
            for origin in (1, 2):
                used = exposure[pos, origin]
                if not training and not used:
                    continue
                native, reasons = raw_features(base, symbol, pos, origin, floors)
                scaled = view.row(symbol, pos, origin)
                component = base.components[symbol, step.session, step.slot]
                row: dict[str, object] = dict(
                    symbol=symbol,
                    timestamp=step.end,
                    session=step.session,
                    slot=step.slot,
                    origin=origin,
                    exposure=used,
                    ever_model_input=used > 0,
                    consuming_session=consumers.get((pos, origin)),
                    consuming_cutoff=str(base.panels[consumers[pos, origin], origin].cutoff)
                    if used
                    else None,
                    source_lineage=component.lineage_id,
                    flags=";".join(component.flags),
                    missing_native=sum(v is None for v in native),
                    source_only=component.source_only,
                    session_type="early close"
                    if len(base.history.calendar.clock(step.session).hours) < 6
                    else "regular",
                    ET_UTC_offset=step.end.tz_convert("America/New_York").strftime("%z"),
                )
                row.update({f: native[j] for j, f in enumerate(ORDER)})
                row.update(
                    {
                        f + "_scaled": float(np.float32(scaled[j])) if scaled is not None else None
                        for j, f in enumerate(ORDER)
                    }
                )
                row.update({f + "_reason": reasons[j] for j, f in enumerate(ORDER)})
                rows.append(row)
    frame = pd.DataFrame(rows)
    if frame.duplicated(["symbol", "timestamp", "origin"]).any():
        raise ViewUnavailable("Duplicate canonical hourly input key.")
    actual_unique_input = len(exposure) * 5
    if actual_unique_input != expected["unique_feature_rows"]:
        raise ViewUnavailable("Unique original tensor-row count differs from saved binding.")
    metadata = dict(
        fold=fold,
        partition=part,
        recipe=asdict(prep),
        recipe_ref=catalog.config["recipes"][fold][PREFIX[part]],
        saved_input_summary=expected,
        origins=len(keys),
        mask_sha256=identity(keys),
        first_origin=keys[0],
        last_origin=keys[-1],
        first_feature_UTC=str(frame.timestamp.min()),
        last_feature_UTC=str(frame.timestamp.max()),
        unique_tensor_rows=actual_unique_input,
        tensor_exposures=len(keys) * 5 * 48,
        audit_rows_with_origin_context=len(frame),
        warmup_excluded_from_fit_unique_rows=(
            actual_unique_input - int(frame.ever_model_input.sum())
        )
        if training
        else 0,
        invalid_complete_rows=int(frame.M1_scaled.isna().sum()),
        synthetic_rows=0,
        source_publication="UNKNOWN / idealized clock only",
        exclusions=expected["excluded"],
        population_policy="fit positions, warm-up excluded" if training else "saved OOS input mask",
        confirmation_numeric_rows=0,
    )
    return Population(fold, part, prep, frame, metadata)


def fit_records(pop: Population, feature: str) -> pd.DataFrame:
    if not pop.partition.endswith("training"):
        raise ViewUnavailable("Fit-record verification needs an original training population.")
    if feature == "M2":
        keys = ["symbol", "session", "origin"]
        variation = pop.frame.groupby(keys)[feature].nunique(dropna=False)
        if (variation > 1).any():
            raise ViewUnavailable("M2 is not locked within session/origin.")
    else:
        keys = ["symbol", "session", "slot"]
    selected = pop.frame.drop_duplicates(keys)
    return selected.loc[selected[feature].notna()].copy()


def verify_fit_binding(pop: Population, base: BaseTables) -> dict:
    """Recreate the recorded key/value hash, without calling any fit routine."""
    keys, positions = canonical_population(base, pop.preparation.window)
    records = {}
    for feature in SCALED:
        rows = fit_records(pop, feature)
        if len(rows) != pop.preparation.population_counts["scaled"][feature]:
            raise ViewUnavailable("Scaler fit-record population count mismatch: " + feature)
        for r in rows.itertuples():
            slot = int(numeric(r.origin)) if feature == "M2" else int(numeric(r.slot))
            records[str(r.symbol), feature, str(r.session), slot] = getattr(r, feature)
    actual = fingerprint([keys, positions, sorted(records.items())])
    return dict(
        passed=actual == pop.preparation.population_binding,
        recorded=pop.preparation.population_binding,
        reproduced=actual,
    )


def preparations(catalog: Catalog, base: BaseTables) -> dict[tuple[str, str], CandidateView]:
    audit_guard()
    return {
        (fold, prefix): CandidateView(base, read_preparation(catalog.root, ref))
        for fold, refs in catalog.config["recipes"].items()
        for prefix, ref in refs.items()
    }


def resolve_example_consumers(
    catalog: Catalog, base: BaseTables, examples: pd.DataFrame
) -> pd.DataFrame:
    """Resolve an identical non-M2 context at a boundary; retain the original values."""
    result = examples.copy()
    for index, row in examples.loc[
        examples.ever_model_input & examples.consuming_session.isna()
    ].iterrows():
        feature, fold, part = str(row.feature), str(row.fold), str(row.partition)
        if feature == "M2":
            raise ViewUnavailable("M2 consuming context cannot be substituted.")
        prefix = PREFIX[part]
        prep = read_preparation(catalog.root, catalog.config["recipes"][fold][prefix])
        if prep.preparation_id != row.recipe_id:
            raise ViewUnavailable("Example recipe identity mismatch")
        if part.endswith("training"):
            keys, _ = canonical_population(base, prep.window)
        else:
            saved = predictions(catalog, fold, "TM0", part)
            keys = tuple(sorted(set(zip(saved.session, saved.origin))))
        pos = base.history.calendar._positions[str(row.session), int(numeric(row.slot))]
        found = next(
            ((day, origin) for day, origin in keys if pos in base.origin_steps[day, origin]), None
        )
        if found is None:
            raise ViewUnavailable("No actual consuming origin for example")
        day, origin = found
        values = CandidateView(base, prep).row(str(row.symbol), pos, origin)
        if values is None or float(np.float32(values[ORDER.index(feature)])) != numeric(row.scaled):
            raise ViewUnavailable("Origin-independent value changed; cannot resolve context")
        result.at[index, "origin"] = origin
        result.at[index, "consuming_session"] = day
        result.at[index, "consuming_cutoff"] = str(base.panels[day, origin].cutoff)
    return result
