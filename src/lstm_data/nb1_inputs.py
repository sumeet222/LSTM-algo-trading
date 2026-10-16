"""Single-factor, training-key-bound B1 compression for Package012B."""

from __future__ import annotations

import json
from dataclasses import asdict, replace

import numpy as np
import torch

from .config import fingerprint
from .ft0_transforms import ORDER, SCALED, identity, robust_parameters
from .pretraining_policy import CANDIDATE
from .pretraining_transforms import CandidateView, canonical_population, raw_features
from .real_batch_data import BatchInputs
from .real_bridge_data import RealInputView, tensor_hash

B1 = ORDER.index("B1")
VERSION = "TA012B_B1_ASINH_POSITIVE_MEDIAN_POOLED_MAD_v1"


def parameters(values: np.ndarray) -> dict:
    """Fit only the supplied unique training population; never insert a scale floor."""
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("FINITE_NONNEGATIVE_B1_TRAINING_REQUIRED")
    positive = values[values > 0]
    if not len(positive):
        raise ValueError("B1_POSITIVE_POPULATION_HOLD")
    s = float(np.median(positive))
    q = np.arcsinh(values / s)
    c, a, method = robust_parameters(q)
    # The unrelated synthetic near-zero-SD edge is not repaired here.
    if not np.isfinite(q).all() or method != "MAD" or a <= 0:
        raise ValueError("B1_AMBIGUOUS_FALLBACK_HOLD")
    return dict(
        s=s,
        c=c,
        a=a,
        method=method,
        weights="UNWEIGHTED_UNIQUE_HOURLY_KEYS",
        fallback="MAD / IQR_1.349 / AUDITED_POPULATION_SD / CONSTANT; unchanged",
        added_floor=None,
        version=VERSION,
    )


def transform(values: np.ndarray, recipe: dict) -> np.ndarray:
    """Preserve full precision until the original float32 input conversion."""
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("INVALID_NATIVE_B1")
    q = np.arcsinh(values / recipe["s"])
    result = np.asarray((q - recipe["c"]) / recipe["a"], dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_TRANSFORMED_B1")
    return result


def fit_recipe(view: CandidateView, code: str) -> dict:
    """Reproduce original B1 fitting keys, independent of duplicated window exposures."""
    prep, base = view.preparation, view.base
    prep.ensure(base)
    origins, positions = canonical_population(base, prep.window)
    records = {}
    for symbol, floors in zip(CANDIDATE, prep.floors):
        for pos in positions:
            step = base.history.calendar.steps[pos]
            value = raw_features(base, symbol, pos, 1, floors)[0][B1]
            if value is not None:
                records[symbol, "B1", step.session, step.slot] = value
    values = np.asarray(list(records.values()), dtype=np.float64)
    j = SCALED.index("B1")
    c, a, method = robust_parameters(values)
    if (c, a, method) != (prep.scaler.centers[j], prep.scaler.scales[j], prep.scaler.methods[j]):
        raise ValueError("ORIGINAL_B1_FIT_POPULATION_NOT_REPRODUCED")
    if len(values) != prep.population_counts["scaled"]["B1"]:
        raise ValueError("ORIGINAL_B1_KEY_COUNT_CHANGED")
    result = dict(
        **parameters(values),
        count=len(values),
        positive_count=int((values > 0).sum()),
        keys_sha256=fingerprint(sorted(records)),
        values_sha256=fingerprint(sorted(records.items())),
        original_population_binding=prep.population_binding,
        training_origins_sha256=identity(origins),
        fit_positions_sha256=identity(positions),
        original_preparation_id=prep.preparation_id,
        window=json.loads(json.dumps(asdict(prep.window), default=str)),
        symbol_order=list(CANDIDATE),
        source_binding=prep.source_binding,
        action_binding=prep.action_binding,
        code_sha256=code,
        original_center=c,
        original_scale=a,
        original_method=method,
    )
    result["recipe_id"] = identity(result)
    return result


def compressed_view(inputs: BatchInputs, key: str, recipe: dict) -> tuple[RealInputView, dict]:
    """Replace one column of a transient unique-row table, retaining every indexed origin."""
    original = inputs.stock_view(key)
    prefix = inputs.fold + ("_INNER_TRAIN" if key in {"inner", "validation"} else "_REFIT")
    candidate = inputs.candidates[prefix]
    if recipe["original_preparation_id"] != original.preparation_id:
        raise ValueError("STALE_NB1_RECIPE")
    native = np.full(len(original.values), np.nan, dtype=np.float64)
    for row in original.rows:
        for symbol, indices in zip(CANDIDATE, row.indices):
            floors = candidate.preparation.floors[CANDIDATE.index(symbol)]
            for pos, index in zip(inputs.base.origin_steps[row.session, row.origin], indices):
                if np.isnan(native[index]):
                    value = raw_features(inputs.base, symbol, pos, row.origin, floors)[0][B1]
                    if value is None:
                        raise ValueError("NO_NEW_B1_ELIGIBILITY_LOSSES")
                    native[index] = value
    values = original.values.clone()
    values[:, B1] = torch.from_numpy(transform(native, recipe))
    prep_id = identity([original.preparation_id, recipe["recipe_id"]])
    metadata = identity(
        [
            original.review_binding,
            prep_id,
            original.window,
            original.rows,
            original.sessions,
            original.excluded,
        ]
    )
    result = replace(
        original,
        preparation_id=prep_id,
        values=values,
        content_hash=tensor_hash(values),
        metadata_hash=metadata,
    )
    result.verify()
    untouched = [j for j in range(16) if j != B1]
    if not torch.equal(values[:, untouched], original.values[:, untouched]):
        raise ValueError("NON_B1_INPUT_DRIFT")
    unique = np.unique(native)
    q = np.arcsinh(unique / recipe["s"])
    scaled = transform(unique, recipe)
    if (np.diff(q) < 0).any() or (np.diff(scaled) < 0).any():
        raise ValueError("B1_ORDER_REVERSAL")
    return result, dict(
        non_B1_float32_exact=True,
        targets_and_indices_exact=result.rows == original.rows,
        masks_exact=result.excluded == original.excluded,
        original=original.summary(),
        transformed=result.summary(),
        native_unique=len(unique),
        q_float64_ties=int((np.diff(q) == 0).sum()),
        final_float32_ties=int((np.diff(scaled) == 0).sum()),
        native_min=float(native.min()),
        q_min=float(q.min()),
        original_abs_max=float(original.values[:, B1].abs().max()),
        transformed_abs_max=float(values[:, B1].abs().max()),
    )
