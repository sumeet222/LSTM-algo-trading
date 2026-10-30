"""Public-API constraint fixtures; synthetic fits only, never research histories."""

import numpy as np
from arch import arch_model
from arch.univariate import GARCH, ConstantMean, Normal

from lstm_data.hf20_strict999_model import Strict999GARCH, constraint_audit, make_model


def fixture_series():
    rng = np.random.default_rng(22042)
    z = rng.standard_normal(1500)
    x = np.zeros(len(z))
    h = 1.0
    for i in range(len(z)):
        x[i] = np.sqrt(h) * z[i]
        h = 0.01 + 0.12 * x[i] ** 2 + 0.89 * h
    return x


def test_constraint_matrix_and_tolerance():
    default = GARCH(p=1, o=0, q=1)
    strict = Strict999GARCH(p=1, o=0, q=1)
    a, b = strict.constraints()
    da, db = default.constraints()
    np.testing.assert_array_equal(a, da)
    np.testing.assert_array_equal(b[:-1], db[:-1])
    assert (a @ [0.1, 0.1, 0.899] - b).min() >= 0
    assert (a @ [0.1, 0.1, 0.9] - b).min() < 0
    assert constraint_audit(0.1, 0.1, 0.899)["constraint_pass"]
    assert constraint_audit(0.1, 0.1, 0.899)["cap_contact"]
    assert constraint_audit(0.1, 0.1, 0.899 + 5e-11)["roundoff_overshoot"]
    assert not constraint_audit(0.1, 0.1, 0.899 + 2e-10)["constraint_pass"]
    assert not constraint_audit(0, 0.1, 0.8)["constraint_pass"]


def test_inherited_likelihood_variance_initialization_and_starts():
    x = fixture_series()
    default = arch_model(x, mean="Constant", vol="GARCH", p=1, q=1, dist="normal", rescale=False)
    strict = make_model(x)
    for method in [
        "compute_variance",
        "backcast",
        "variance_bounds",
        "bounds",
        "starting_values",
        "forecast",
    ]:
        assert getattr(Strict999GARCH, method) is getattr(GARCH, method)
    for method in ["fit", "resids", "fix"]:
        assert getattr(type(strict), method) is getattr(type(default), method)
    residuals = x - x.mean()
    np.testing.assert_array_equal(
        strict.volatility.starting_values(residuals), default.volatility.starting_values(residuals)
    )
    np.testing.assert_array_equal(
        strict.volatility.starting_values(residuals), strict.volatility.starting_values(residuals)
    )
    pars = np.array([0.02, 0.01, 0.12, 0.87])
    s, d = strict.fix(pars), default.fix(pars)
    assert s.loglikelihood == d.loglikelihood
    np.testing.assert_array_equal(s.conditional_volatility, d.conditional_volatility)


def test_supported_optimizer_applies_cap_on_synthetic_boundary():
    class PermissiveGARCH(Strict999GARCH):
        def constraints(self):
            return GARCH.constraints(self)

    x = fixture_series()
    default = arch_model(
        x, mean="Constant", vol="GARCH", p=1, q=1, dist="normal", rescale=False
    ).fit(update_freq=0, disp="off", tol=1e-9, options={"maxiter": 1000, "ftol": 1e-9})
    permissive = ConstantMean(
        x, volatility=PermissiveGARCH(p=1, o=0, q=1), distribution=Normal(), rescale=False
    ).fit(update_freq=0, disp="off", tol=1e-9, options={"maxiter": 1000, "ftol": 1e-9})
    strict = make_model(x).fit(
        update_freq=0, disp="off", tol=1e-9, options={"maxiter": 1000, "ftol": 1e-9}
    )
    np.testing.assert_array_equal(default.params, permissive.params)
    assert default.loglikelihood == permissive.loglikelihood
    assert strict.convergence_flag == default.convergence_flag == 0
    p = strict.params
    audit = constraint_audit(float(p["omega"]), float(p["alpha[1]"]), float(p["beta[1]"]))
    assert audit["constraint_pass"]
    assert audit["cap_contact"]
    assert default.params["alpha[1]"] + default.params["beta[1]"] > 0.999
    np.testing.assert_array_equal(strict.params.to_numpy(), strict.optimization_result.x)
    assert not np.array_equal(strict.params, default.params)
