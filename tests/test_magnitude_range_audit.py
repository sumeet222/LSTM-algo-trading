"""Boundary and accounting oracles for magnitude-range diagnostics."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.magnitude_range_audit import range_masks, session_weights
from lstm_data.visualization.hf1m_long import dates


def test_inclusive_ties_signs_and_nesting():
    y = np.array([-100.0, -99.0, -95.0, 0.0, 95.0, 99.0, 100.0])
    a, m99 = range_masks(y, 0.99)
    b, m95 = range_masks(y, 0.95)
    assert (a, b) == (99.0, 95.0)
    assert m99.tolist() == [True, True, False, False, False, True, True]
    assert m95.sum() == 6 and not (m99 & ~m95).any()
    assert np.array_equal((y >= a) | (y <= -a), m99)
    assert np.all(m99.astype(int) + (m95 & ~m99).astype(int) + (~m95).astype(int) == 1)


def test_zero_maximum_and_invalid_values():
    _, mask = range_masks(np.zeros(3), 0.99)
    assert mask.all()  # Inclusive zero boundary, no arbitrary sign assignment.
    for y in (np.array([]), np.array([np.nan]), np.array([np.inf])):
        with pytest.raises(ValueError):
            range_masks(y, 0.99)


def test_unequal_origins_equal_day_weights():
    f = pd.DataFrame(
        [
            dict(origin_id=o, ticker=str(i), session_date_et=d)
            for d, os in [("a", ["a1"]), ("b", ["b1", "b2"])]
            for o in os
            for i in range(20)
        ]
    )
    w = session_weights(f)
    np.testing.assert_allclose(w.sum(), 1)
    np.testing.assert_allclose(pd.Series(w).groupby(f.session_date_et).sum(), 0.5)
    loss = np.arange(len(f)) ** 2
    a = np.arange(len(f)) < 5
    b = np.arange(len(f)) < 12
    assert np.isclose(sum(np.sum(w[m] * loss[m]) for m in (a, b & ~a, ~b)), w @ loss)
    with pytest.raises(ValueError):
        session_weights(f.iloc[:-1])
    with pytest.raises(ValueError):
        session_weights(pd.concat([f, f.iloc[:1]]))


def test_protected_dates_rejected_before_reader_access():
    with pytest.raises(ValueError):
        dates("2025-12-31", "2026-01-01")
