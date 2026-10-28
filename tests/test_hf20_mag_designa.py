"""Small independent fixtures for the new Design A boundaries and scalar maps."""

import math

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_mag_designa import (
    decode,
    factors,
    feature_fit_hours,
    limit,
    ridge_fit,
    role_mask,
)


def test_strict_maturity_and_first_step_embargo() -> None:
    cutoff = limit("2020-09-30")
    rows = pd.DataFrame(
        dict(
            session_date_et=["2020-07-15"] * 4,
            eligible=[True, True, True, False],
            label_maturity_utc=[
                cutoff - pd.Timedelta(seconds=1),
                cutoff,
                cutoff - pd.Timedelta(seconds=1),
                cutoff,
            ],
        )
    )
    first = np.array(["2020-07-01", "2020-07-01", "2020-06-30", "2020-07-01"])
    actual = role_mask(rows, first, "2020-07-01", "2020-09-30", "2020-06-30")
    assert actual.tolist() == [True, False, False, False]
    assert cutoff == pd.Timestamp("2020-10-01T00:00:00Z")


def test_feature_fitting_union_is_input_only_and_prefix_clipped() -> None:
    grid = pd.DataFrame(dict(session_date_et=["2020-09-29", "2020-09-30", "2020-10-01"]))
    rows = pd.DataFrame(
        dict(
            session_date_et=["2020-09-30", "2020-10-01"],
            source_input_eligible=[True, True],
            first_step=[0, 1],
            entry_index=[1, 2],
            label_eligible=[False, True],
        )
    )
    assert feature_fit_hours(grid, rows, "2020-09-30").tolist() == [True, True, False]
    rows["label_eligible"] = ~rows.label_eligible
    assert feature_fit_hours(grid, rows, "2020-09-30").tolist() == [True, True, False]


def test_independent_scalar_formulas_and_unconstrained_residual() -> None:
    raw = np.array([math.log(2), math.log(2)])
    fitted = factors(np.array([1.0, 3.0]), raw, 1.0, np.array([0.25, 0.75]))
    assert fitted["c"] == pytest.approx(1.75)
    assert fitted["k"] == pytest.approx(2.5)
    values = decode(raw, 1.0, fitted["c"], fitted["k"])
    np.testing.assert_allclose(values["C0"], 1.0)
    np.testing.assert_allclose(values["C1a"], 2.5)
    np.testing.assert_allclose(values["M1"], 2.5)
    z = np.array([-0.1, 0.2])
    a = np.array([0.2, 0.4])
    fitted = factors(a, z, 1.0, np.array([0.5, 0.5]))
    expected = 0.5 * ((1 + 0.2) / math.exp(-0.1) + (1 + 0.4) / math.exp(0.2))
    assert fitted["c"] == pytest.approx(expected)
    assert decode(z, 1.0, fitted["c"], 1.0)["C0"][0] == 0
    with pytest.raises(ValueError, match="DENOMINATOR"):
        factors(a, np.zeros(2), 1.0, np.array([0.5, 0.5]))


def test_ridge_has_unpenalized_intercept() -> None:
    x = np.column_stack([np.ones(4), [-2.0, -1.0, 1.0, 2.0]])
    beta = ridge_fit(x, np.full(4, 7.0), np.full(4, 0.25), 10.0)
    np.testing.assert_allclose(beta, [7.0, 0.0], atol=1e-12)
