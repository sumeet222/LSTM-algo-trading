"""Independent actual-output accounting and proper quantile/DM1 diagnostics."""

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.dm_quantile_diagnostics import allocation, metrics
from lstm_data.dm_quantile_loss import outputs


@pytest.mark.parametrize("arm", ["DM1", "QR1", "SS1"])
def test_actual_row_component_conservation_and_constants(arm: str) -> None:
    n = 800
    y = np.linspace(-3, 3, n)
    raw = torch.zeros((n, 3) if arm != "SS1" else (n,))
    f = pd.DataFrame(
        dict(TG20=y, session_date_et=np.repeat([f"2020-01-{i + 1:02}" for i in range(20)], 40))
    )
    for i in range(3 if arm != "SS1" else 1):
        f["raw_" + str(i)] = raw.numpy().reshape(n, -1)[:, i]
    for key, value in outputs(raw, arm, 1.0).items():
        if value.ndim == 2:
            for j, name in enumerate(["05", "50", "95"]):
                f[key + "_" + name] = value.numpy()[:, j]
        else:
            f[key] = value.numpy()
    f = allocation(f, arm, dict(scale=1.0))
    np.testing.assert_allclose(f.ordinary_weight.sum(), 1)
    np.testing.assert_allclose(f.total.sum(), f.raw.mean(), rtol=1e-6)
    score = metrics(f, arm, dict(scale=1.0))
    assert np.isfinite(score["mse"])
    if arm == "DM1":
        assert score["sign_CE"] == pytest.approx(np.log(2)) and score[
            "cancellation_fraction"
        ] == pytest.approx(1)
    if arm == "QR1":
        assert len(score["coverage"]) == 3 and score["interval_width"] > 0
