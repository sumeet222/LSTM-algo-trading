"""Postfit report-only regression: pandas 3 exposes read-only boolean views.

Synthetic score-shaped inputs only. This is supplemental to the immutable
64-fixture prefit matrix and does not authorize another neural fit.
"""
from __future__ import annotations

import boundary

boundary.install()

import unittest

import numpy as np
import pandas as pd

import evaluation


def readonly_score_fixture() -> pd.DataFrame:
    """Two sessions, three complete twenty-stock origins and partial aux support."""
    rows: list[dict[str, object]] = []
    actual = (.01, .03, .05)
    predicted = (.02, .04, .04)
    for origin, (day, slot, weight) in enumerate((
        ("2021-01-18", "12:30", 1 / 80),
        ("2021-01-18", "13:30", 1 / 80),
        ("2021-01-19", "12:30", 1 / 40),
    )):
        for stock_index, ticker in enumerate(evaluation.STOCKS):
            supported = ticker != "CSCO" and not (ticker == "COP" and origin == 1)
            row: dict[str, object] = {
                "origin_id": pd.Timestamp(f"{day} {slot}", tz="America/New_York").tz_convert("UTC").isoformat(),
                "session_date_et": day, "ticker": ticker, "category": "OVERNIGHT",
                "weight": weight, "aux_supported": supported,
            }
            for component, multiplier in (("pre", 1.), ("gap", -.5), ("post", .25)):
                row[f"R_{component}"] = multiplier * (actual[origin] + stock_index * .001) if supported else np.nan
                row[f"Rhat_{component}"] = multiplier * (predicted[origin] + stock_index * .001)
            rows.append(row)
    return pd.DataFrame.from_records(rows)


class ReportOnlyReadOnlyMaskRegression(unittest.TestCase):
    def test_per_stock_readonly_mask_correct_values_and_no_source_mutation(self) -> None:
        rows = readonly_score_fixture()
        before = rows.copy(deep=True)
        mask = rows["aux_supported"].to_numpy(dtype=bool)
        self.assertFalse(mask.flags.writeable, "fixture must exercise pandas' read-only boolean view")
        result = evaluation.signed_diagnostics(rows, stock="VZ")
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result["rows"]), {3})
        self.assertEqual(set(result["sessions"]), {2})
        for component, multiplier in (("pre", 1.), ("gap", -.5), ("post", .25)):
            metric = result.loc[result["component"].eq(component)].iloc[0]
            self.assertAlmostEqual(float(metric["observed"]), multiplier * .035, places=14)
            self.assertAlmostEqual(float(metric["predicted"]), multiplier * .035, places=14)
            self.assertAlmostEqual(float(metric["mae"]), abs(multiplier) * .01, places=14)
            self.assertAlmostEqual(float(metric["mse"]), multiplier ** 2 * .0001, places=14)
            self.assertAlmostEqual(float(metric["covariance"]), multiplier ** 2 * .000125, places=14)
            self.assertAlmostEqual(float(metric["pearson"]), 1.25 / np.sqrt(2.75 * .75), places=14)
        pd.testing.assert_frame_equal(rows, before, check_exact=True)
        np.testing.assert_array_equal(mask, before["aux_supported"].to_numpy(dtype=bool))

    def test_all_twenty_stock_calls_preserve_support_and_skip_empty_stock(self) -> None:
        rows = readonly_score_fixture()
        before = rows.copy(deep=True)
        self.assertFalse(rows["aux_supported"].to_numpy(dtype=bool).flags.writeable)
        all_stocks = evaluation.signed_diagnostics(rows)
        self.assertEqual(set(all_stocks["rows"]), {56})
        for ticker in evaluation.STOCKS:
            result = evaluation.signed_diagnostics(rows, stock=ticker)
            if ticker == "CSCO":
                self.assertTrue(result.empty)
            else:
                self.assertEqual(len(result), 3)
                self.assertEqual(set(result["rows"]), {2 if ticker == "COP" else 3})
                self.assertEqual(set(result["sessions"]), {2})
            pd.testing.assert_frame_equal(rows, before, check_exact=True)
        replay = evaluation.signed_diagnostics(rows)
        pd.testing.assert_frame_equal(replay, all_stocks, check_exact=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
