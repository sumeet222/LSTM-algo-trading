"""Independent annual-reduction fixtures; no market data or model execution."""

import numpy as np
import pandas as pd

from lstm_data.hf20_minute_report import equal_year


def test_equal_year_ignores_unequal_row_counts_and_ratio_is_of_means():
    rows = []
    for year, count, predicted, observed, error in [
        ("2021", 20, 1.0, 2.0, 1.0),
        ("2022", 2000, 3.0, 3.0, 3.0),
        ("2023", 40, 2.0, 4.0, 2.0),
        ("2024", 100, 2.0, 7.0, 4.0),
    ]:
        rows.append(
            dict(
                year=year,
                arm="TOY",
                rows=count,
                origins=count // 20,
                sessions=1,
                predicted=predicted,
                observed=observed,
                raw_MSE=error,
                ratio=predicted / observed,
            )
        )
    frame = equal_year(pd.DataFrame(rows), ["arm"])
    eq = frame.loc[frame.year.eq("EQ")].iloc[0]
    np.testing.assert_allclose([eq.raw_MSE, eq.ratio], [2.5, 0.5])
    assert eq["rows"] == 2160
    assert not np.isclose(eq.ratio, np.mean([0.5, 1, 0.5, 2 / 7]))
    assert not equal_year(pd.DataFrame(rows[:3]), ["arm"]).year.eq("EQ").any()
