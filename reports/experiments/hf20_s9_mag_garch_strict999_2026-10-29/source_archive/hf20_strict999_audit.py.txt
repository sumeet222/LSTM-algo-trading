"""Read-only fit coefficient, constraint, input and predecessor sensitivity audit."""

import numpy as np
import pandas as pd

from . import hf20_strict999 as task
from .hf20_strict999_model import Strict999GARCH, constraint_audit


def audit() -> None:
    """Verify optimizer vectors and saved starts without invoking any fit."""
    b, out = task.b, task.OUT
    old = pd.read_csv(task.parent.OUT / "garch_fit_diagnostics.csv", float_precision="round_trip")
    new = pd.read_csv(out / "garch_fit_diagnostics.csv", float_precision="round_trip")
    assert len(new) == len(old) == 560
    checks = []
    bounds = []
    for d in new.to_dict("records"):
        unit = (
            out
            / f"GARCH/F{int(d['year']) % 100}"
            / (str(d["ticker"]) + "_" + str(d["slot"]).replace(":", ""))
        )
        if not (unit / "parameters.json").exists():
            checks.append(
                dict(year=d["year"], ticker=d["ticker"], slot=d["slot"], status=d["status"])
            )
            continue
        p = b.read(unit / "parameters.json")
        opt = b.read(unit / "optimizer.json")
        initial = b.read(unit / "initialization.json")
        v = np.array([p[k] for k in ["mu_percent", "omega_percent_squared", "alpha", "beta"]])
        np.testing.assert_array_equal(v, opt["x"])
        residual = constraint_audit(*v[1:])
        for key in ["constraint_pass", "cap_contact", "roundoff_overshoot", "cap_slack"]:
            assert p[key] == residual[key]
        with np.load(unit / "fit_state.npz") as saved:
            x, h, ix = saved["x"], saved["h"], saved["indices"]
        prior = task.parent.OUT / f"GARCH/F{int(d['year']) % 100}" / unit.name / "fit_state.npz"
        assert b.digest(prior) == initial["input_sha256"]
        with np.load(prior) as saved:
            np.testing.assert_array_equal(x, saved["x"])
            np.testing.assert_array_equal(ix, saved["indices"])
        normal_loglik = float(-0.5 * np.sum(np.log(2 * np.pi) + np.log(h) + (x - v[0]) ** 2 / h))
        np.testing.assert_allclose(normal_loglik, p["loglikelihood"], rtol=1e-12, atol=1e-9)
        np.testing.assert_allclose(-normal_loglik, opt["fun"], rtol=1e-12, atol=1e-9)
        vol = Strict999GARCH(p=1, o=0, q=1)
        centered = x - x.mean()
        np.testing.assert_array_equal(vol.starting_values(centered), initial["volatility_start"])
        assert vol.backcast(centered) == initial["backcast"]
        vb = vol.variance_bounds(centered)
        np.testing.assert_array_equal(vb, initial["variance_bounds"])
        pb = np.array(initial["parameter_bounds"])
        slack = np.minimum(v[1:] - pb[:, 0], pb[:, 1] - v[1:])
        assert (slack >= -1e-10).all()
        bounds.append(
            dict(
                year=d["year"],
                ticker=d["ticker"],
                slot=d["slot"],
                parameter_bound_min_slack=float(slack.min()),
                variance_bound_lower_min=float(vb[:, 0].min()),
                variance_bound_upper_max=float(vb[:, 1].max()),
                initial_h=float(h[0]),
                last_h=float(h[-1]),
                filter_min=float(h.min()),
                filter_max=float(h.max()),
                conditional_values_below_lower=int((h < vb[:, 0] - 1e-12).sum()),
                conditional_values_above_soft_upper=int((h > vb[:, 1] + 1e-12).sum()),
            )
        )
        checks.append(
            dict(
                year=d["year"],
                ticker=d["ticker"],
                slot=d["slot"],
                status=d["status"],
                **residual,
                optimizer_vector_exact=True,
                input_exact=True,
                package_start_exact=True,
                independent_gaussian_loglikelihood=normal_loglik,
            )
        )
    delta = new.merge(
        old, on=["year", "ticker", "slot"], suffixes=("_new", "_old"), validate="one_to_one"
    )
    for key in [
        "mu_percent",
        "omega_percent_squared",
        "alpha",
        "beta",
        "persistence",
        "loglikelihood",
    ]:
        delta["delta_" + key] = delta[key + "_new"] - delta[key + "_old"]
    delta["large_alpha_beta_change"] = (delta.delta_alpha.abs() > 0.01) | (
        delta.delta_beta.abs() > 0.01
    )
    delta["old_far_from_cap"] = delta.persistence_old < 0.99
    delta.to_csv(out / "garch_persistence_delta.csv", index=False)
    pd.DataFrame(checks).to_csv(out / "garch_constraint_units.csv", index=False)
    pd.DataFrame(bounds).to_csv(out / "garch_variance_bounds.csv", index=False)
    b.write(
        out / "garch_constraints_verification.json",
        dict(
            status="PASS_AUDIT",
            units=560,
            feasible=int(new.constraint_pass.sum()),
            cap_contacts=int(new.cap_contact.sum()),
            roundoff_overshoots=int(new.roundoff_overshoot.sum()),
            minimum_slack=float(new.cap_slack.min()),
            maximum_persistence=float(new.persistence.max()),
            old_near_unit=int((old.persistence >= 0.99).sum()),
            old_failed=int(old.status.ne("PASS").sum()),
            large_changes=int(delta.large_alpha_beta_change.sum()),
            large_changes_old_far_from_cap=int(
                (delta.large_alpha_beta_change & delta.old_far_from_cap).sum()
            ),
            no_postfit_adjustment=True,
            **task.resources(),
        ),
    )


if __name__ == "__main__":
    audit()
