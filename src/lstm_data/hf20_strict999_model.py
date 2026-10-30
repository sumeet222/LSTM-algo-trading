"""Public arch volatility extension: only the GARCH(1,1) persistence constraint."""

import numpy as np
from arch.univariate import GARCH, ConstantMean, Normal

CAP = 0.999
FEASIBILITY_TOLERANCE = 1e-10
CONTACT_TOLERANCE = 1e-8


class Strict999GARCH(GARCH):
    """Keep package likelihood/recursion/bounds/starts; change one linear bound."""

    def constraints(self):
        if (self.p, self.o, self.q, self.power) != (1, 0, 1, 2.0):
            raise ValueError("Only the authorized Gaussian GARCH(1,1) is supported")
        a, bound = super().constraints()
        np.testing.assert_array_equal(a[-1], [0.0, -1.0, -1.0])
        assert bound[-1] == -1.0
        bound[-1] = -CAP
        return a, bound


def make_model(x: np.ndarray) -> ConstantMean:
    """Public component API; normal errors and default initialization unchanged."""
    return ConstantMean(
        x, volatility=Strict999GARCH(p=1, o=0, q=1), distribution=Normal(), rescale=False
    )


def constraint_audit(omega: float, alpha: float, beta: float) -> dict:
    """Audit unrounded coefficients without adjusting the estimated vector."""
    a, bound = Strict999GARCH(p=1, o=0, q=1).constraints()
    residual = a @ np.array([omega, alpha, beta]) - bound
    slack = float(CAP - (alpha + beta))
    return dict(
        cap=CAP,
        cap_slack=slack,
        constraint_residuals=residual.tolist(),
        constraint_pass=bool(
            np.isfinite(residual).all()
            and omega > 0
            and alpha >= 0
            and beta >= 0
            and slack >= -FEASIBILITY_TOLERANCE
        ),
        cap_contact=bool(abs(slack) <= CONTACT_TOLERANCE),
        roundoff_overshoot=bool(-FEASIBILITY_TOLERANCE <= slack < 0),
    )
