"""Numerical and temporal fixtures, independent of any research fit."""

import math

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_classical_math import deoverlap, folded_normal
from lstm_data.hf20_matched_math import apply_common, fit_common, mature_prefix, next_variance


def test_folded_normal_limits_and_quadrature():
    np.testing.assert_allclose(
        folded_normal(np.array([0.0]), np.array([4.0])), [2 * math.sqrt(2 / math.pi)]
    )
    np.testing.assert_allclose(
        folded_normal(np.array([-2.0, 2.0]), np.array([0.0, 1e-30])), [2.0, 2.0]
    )
    x = np.linspace(-10, 10, 200001)
    density = np.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    for mu in [-1.2, 0.0, 1.2]:
        numerical = np.trapezoid(abs(mu + 0.7 * x) * density, x)
        analytic = folded_normal(np.array([mu]), np.array([0.49]))[0]
        assert analytic > 0
        assert abs(analytic - numerical) < 1e-9
    np.testing.assert_allclose(
        folded_normal(np.array([-1.2, 1.2]), np.array([0.49, 0.49])), np.repeat(analytic, 2)
    )


def test_recursion_scale_and_maturity_index():
    h = next_variance(2.0, 3.0, 1.0, 0.2, 0.1, 0.7)
    assert h == pytest.approx(2.0)
    np.testing.assert_allclose(
        folded_normal(np.array([1.0]), np.array([h])) / 100,
        folded_normal(np.array([0.01]), np.array([h / 10000])),
    )
    assert mature_prefix(np.array([10, 20, 30]), 20) == 1
    assert mature_prefix(np.array([10, 20, 30]), 21) == 2
    np.testing.assert_array_equal(
        deoverlap(np.array([0, 3, 4, 8]), np.array([4, 7, 8, 12])), [True, False, True, True]
    )
    # Mature overnight interval can update; unfinished future target cannot.
    assert mature_prefix(np.array([5, 30, 45]), 31) == 2
    prices = np.array([100.0, 102.0])
    signed = np.log(prices[1] / prices[0])
    assert signed > 0 and abs(signed) == signed


def test_common_coefficients_weights_and_no_label_application():
    f = pd.DataFrame(
        dict(
            A=[1.0, 3.0, 2.0, 6.0],
            b=[1.0, 1.0, 2.0, 2.0],
            weight=[0.125, 0.125, 0.375, 0.375],
            category=["INTRADAY", "OVERNIGHT"] * 2,
            session_date_et=["a", "a", "b", "b"],
        )
    )
    c = fit_common(f, "b")
    w = f.weight.to_numpy()
    a = f.A.to_numpy()
    p = f.b.to_numpy()
    k = (w * a * p).sum() / (w * p * p).sum()
    assert c[0]["k"] == pytest.approx(k)
    for v in c[1:]:
        assert v["n_eff"] == pytest.approx(1 / (0.25**2 + 0.75**2))
        assert v["k"] == pytest.approx(v["rho"] * v["k_raw"] + (1 - v["rho"]) * k)
    g = f.drop(columns="A")
    np.testing.assert_allclose(apply_common(g, "b", c, "G"), k * p)
    expanded = pd.concat([f] * 20, ignore_index=True)
    expanded["weight"] /= 20
    cc = fit_common(expanded, "b")
    np.testing.assert_allclose([v["k"] for v in c], [v["k"] for v in cc])
    np.testing.assert_allclose([v["n_eff"] for v in c], [v["n_eff"] for v in cc])
    with pytest.raises(ValueError):
        fit_common(f.assign(b=0), "b")
    with pytest.raises(ValueError):
        fit_common(f.loc[f.category.eq("INTRADAY")], "b")


def test_supported_arch_frozen_one_step():
    from arch import arch_model

    x = np.array([0.2, -0.3, 0.6, -1.1, 0.9, 0.4, -0.7, 1.2])
    pars = np.array([0.1, 0.05, 0.15, 0.75])
    fixed = arch_model(x, mean="Constant", vol="GARCH", p=1, q=1, dist="normal", rescale=False).fix(
        pars
    )
    h = float(np.asarray(fixed.conditional_volatility)[-1] ** 2)
    own = next_variance(h, float(x[-1]), *pars)
    vol = fixed.model.volatility
    prefix_residuals = x - x.mean()
    forecast = vol.forecast(
        pars[1:],
        x - pars[0],
        vol.backcast(prefix_residuals),
        vol.variance_bounds(prefix_residuals),
        start=len(x) - 1,
        horizon=1,
    )
    assert forecast.forecasts is not None
    expected = float(forecast.forecasts[-1, 0])
    assert own == pytest.approx(expected, rel=1e-12)
