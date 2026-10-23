"""Pure magnitude-range membership and equal-session diagnostic weights."""

from __future__ import annotations

import numpy as np
import pandas as pd


def range_masks(values: np.ndarray, fraction: float) -> tuple[float, np.ndarray]:
    """Inclusive cutoff anchored at zero and global absolute maximum; never a rank."""
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Finite nonempty one-dimensional targets required")
    if not 0 <= fraction <= 1:
        raise ValueError("Fraction outside unit interval")
    cutoff = float(fraction * np.max(np.abs(values)))
    return cutoff, np.abs(values) >= cutoff


def session_weights(frame: pd.DataFrame) -> np.ndarray:
    """Equal session, admitted origin and stock weights for complete cohorts."""
    if frame.duplicated(["origin_id", "ticker"]).any():
        raise ValueError("Duplicate observation")
    counts = frame.groupby("origin_id").ticker.transform("size")
    if not counts.eq(20).all():
        raise ValueError("Incomplete20-stock origin")
    origins = frame.groupby("session_date_et").origin_id.transform("nunique")
    return 1.0 / (frame.session_date_et.nunique() * origins.to_numpy() * 20)
