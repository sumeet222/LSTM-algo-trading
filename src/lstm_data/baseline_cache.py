"""Bounded memoization of the unchanged immutable P2 scaler application."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from .ft0_transforms import Context, ScalerCertificate

_CERTIFICATES: dict[str, ScalerCertificate] = {}


@lru_cache(maxsize=32768)
def _apply(
    certificate_id: str,
    feature: str,
    value: float,
    cutoff: pd.Timestamp,
    source: str,
    action: str,
    context: Context,
    origin: pd.Timestamp | None,
):
    return _CERTIFICATES[certificate_id].apply(
        feature,
        value,
        cutoff,
        source_binding=source,
        action_binding=action,
        context=context,
        training_origin=origin,
    )


def canonical_apply(
    scaler: ScalerCertificate,
    feature: str,
    value: float,
    cutoff: pd.Timestamp,
    *,
    source_binding: str,
    action_binding: str,
    context: Context,
    training_origin: pd.Timestamp | None = None,
):
    ident = scaler.certificate_id
    if ident not in _CERTIFICATES:
        if len(_CERTIFICATES) >= 32:
            _apply.cache_clear()
            _CERTIFICATES.clear()
        _CERTIFICATES[ident] = scaler
    # P2 ASOF ignores training_origin; HISTORICAL_TRAINING retains it in the key.
    origin = training_origin if context == "HISTORICAL_TRAINING" else None
    return _apply(ident, feature, value, cutoff, source_binding, action_binding, context, origin)
