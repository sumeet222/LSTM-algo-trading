"""Independent synthetic review of newly written FT16 mathematics; no source data."""
from __future__ import annotations

import math
import statistics
import unittest

import numpy as np
import pandas as pd

from dataset import rolling
import features as f


def direct_rolling(x: np.ndarray, n: int, minimum: int, regimes: np.ndarray | None = None) -> np.ndarray:
    """Small explicit-window oracle with Python finite-value sums."""
    result = np.full(x.shape, np.nan, dtype=np.float64)
    if x.ndim == 1:
        for end in range(n - 1, len(x)):
            window = x[end - n + 1:end + 1]
            valid = np.isfinite(window)
            triple = any(not valid[k:k + 3].any() for k in range(n - 2))
            regime_ok = regimes is None or regimes[end - n + 1] == regimes[end]
            if valid.sum() >= minimum and not triple and regime_ok:
                result[end] = statistics.fmean(window[valid])
    else:
        for column in range(x.shape[1]):
            r = None if regimes is None else regimes[:, column]
            result[:, column] = direct_rolling(x[:, column], n, minimum, r)
    return result


def native_fixture() -> tuple[dict, dict, dict]:
    n = 3

    def stock(value: float) -> np.ndarray:
        return np.full((n, 20), value, dtype=np.float64)

    data = {
        "arrays": {
            "p": np.arange(n), "C": stock(105), "H": stock(110), "L": stock(90),
            "V": stock(20), "volume_regime": np.zeros((n, 20), dtype=np.int64),
            "cop_window": np.ones(n, dtype=np.bool_),
        },
        "grid": pd.DataFrame({"session": np.arange(n), "date": ["2020-01-02", "2020-01-03", "2020-01-06"]}),
    }
    components = {
        "oc": stock(.02), "rms12": stock(.4), "rms60": stock(.5),
        "mom5": stock(.4), "mom105": stock(.8), "rms63": stock(.7),
        "qmean": stock(10), "u5": stock(100), "u60": stock(200),
        "sma": stock(100), "sign20": stock(-.3),
        "ind": np.tile(np.array([.001, .002, .2]), (n, 20, 1)),
        "mean2": np.tile(np.arange(1, 8) * .1, (n, 20, 1)),
        "rms2": np.full((n, 20, 7), .8),
        "daily_vreg": np.zeros((n, 20), dtype=np.int64),
    }
    recipe = {
        "hourly_floor": [.1] * 20, "daily_floor": [.2] * 20, "m2_floor": [.3] * 20,
        "pseudocounts": [{"0": [2., 3.], "1": [4., 6.]} for _ in range(20)],
    }
    return data, components, recipe


class FeatureMathReview(unittest.TestCase):
    def test_rolling_full_positions_minimum_triple_and_regime_against_oracle(self) -> None:
        rng = np.random.default_rng(150)
        values = rng.normal(size=(100, 3))
        values[10:12, 0] = np.nan
        values[21:24, 1] = np.nan
        values[[8, 17, 25, 32, 45, 80], 2] = np.nan
        values[65, 0] = math.inf
        regimes = np.zeros_like(values, dtype=np.int64)
        regimes[40:, 0] = 1
        regimes[70:, 1] = 1
        for n, minimum in [(1, 1), (2, 1), (3, 1), (12, 10), (20, 19), (60, 57)]:
            with self.subTest(n=n, minimum=minimum):
                expected = direct_rolling(values, n, minimum, regimes)
                actual = rolling(values, n, minimum, regimes)
                np.testing.assert_array_equal(np.isnan(actual), np.isnan(expected))
                np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=1e-12, equal_nan=True)
                self.assertTrue(np.isnan(actual[:n - 1]).all())
        # A triple ending at the window's first two positions is not wholly inside it.
        x = np.array([math.nan, math.nan, math.nan, 1., 2., 3.])
        self.assertTrue(math.isnan(float(rolling(x, 4, 2)[3])))
        self.assertEqual(float(rolling(x, 4, 2)[4]), 1.5)

    def test_rolling_large_remote_prefix_cannot_erase_small_later_windows(self) -> None:
        x = np.array([1e16, 1., 1., 1.])
        np.testing.assert_allclose(rolling(x, 2, 2)[2:], [1., 1.], atol=0, rtol=0)
        y = np.array([1e16, 1e-12, 1e-12, 1e-12])
        np.testing.assert_allclose(rolling(y, 2, 2)[2:], [1e-12, 1e-12], atol=0, rtol=0)

    def test_quantile_interpolation_left_rule_and_robust_fallback_chain(self) -> None:
        self.assertEqual(f.quantile(np.array([1., 3.]), .5), 2)
        self.assertEqual(f.quantile(np.array([1., 3.]), .5, np.array([1., 1.])), 1)
        self.assertEqual(f.quantile(np.repeat([1., 3.], 20), .5, np.full(40, 1 / 40)), 1)
        self.assertEqual(f.quantile(np.array([8., 2., 3.]), .25, np.array([1., 2., 1.])), 2)
        center, scale, method = f.robust(np.array([1., 2., 3.]))
        self.assertEqual((center, scale, method), (2, 1, "MAD"))
        center, scale, method = f.robust(np.array([0., 0., 0., 2.]))
        self.assertEqual(center, 0)
        self.assertAlmostEqual(scale, .5 / 1.349, delta=1e-12)
        self.assertEqual(method, "IQR")
        center, scale, method = f.robust(np.array([0., 0., 0., 0., 0., 2.]))
        self.assertEqual(center, 0)
        self.assertAlmostEqual(scale, math.sqrt(5) / 3, delta=1e-12)
        self.assertEqual(method, "SD")
        self.assertEqual(f.robust(np.array([7., 7., 7.])), (7, 1, "CONSTANT"))

    def test_all_sixteen_native_formulas_and_contexts(self) -> None:
        data, components, recipe = native_fixture()
        common, m2 = f.native(data, components, recipe)
        expected = np.array([
            .02 / .5, math.nan, .4 / (math.sqrt(5) * .7), .8 / (math.sqrt(105) * .7),
            math.log(.4), math.log(.5), math.log(.4) - math.log(.5), math.log(110 / 90),
            .5, math.log(22 / 12), math.log(103 / 203), math.log(105 / 100), -.3, .001, .002, .2,
        ])
        np.testing.assert_allclose(common, np.tile(expected[f.COMMON], (3, 20, 1)), atol=1e-12, rtol=1e-12)
        np.testing.assert_allclose(m2, np.tile(np.arange(1, 8) * .1 / .8, (3, 20, 1)), atol=1e-12, rtol=1e-12)

    def test_native_floor_missing_extrema_b2_tolerance_and_cop_block(self) -> None:
        data, components, recipe = native_fixture()
        components["rms12"][:] = .01
        components["rms60"][:] = .02
        components["rms63"][:] = .03
        components["rms2"][:] = .04
        data["arrays"]["H"][0, 0] = 105
        data["arrays"]["L"][0, 0] = 105
        data["arrays"]["H"][0, 1] = math.nan
        data["arrays"]["C"][0, 2] = 110 + 1e-8
        data["arrays"]["C"][0, 3] = 110 + 1e-10
        data["arrays"]["cop_window"][2] = False
        common, m2 = f.native(data, components, recipe)
        b2_index = int(np.flatnonzero(f.COMMON == 8)[0])
        self.assertEqual(common[0, 0, b2_index], 0)
        self.assertTrue(math.isnan(common[0, 1, b2_index]))
        self.assertTrue(math.isnan(common[0, 2, b2_index]))
        self.assertGreater(common[0, 3, b2_index], 1)  # Preserve tolerated value; do not clip.
        self.assertAlmostEqual(common[0, 4, 0], .02 / .1, delta=1e-12)
        self.assertAlmostEqual(common[0, 4, 1], .4 / (math.sqrt(5) * .2), delta=1e-12)
        self.assertAlmostEqual(m2[0, 4, 0], .1 / .3, delta=1e-12)
        self.assertTrue(np.isnan(common[2, 1]).all())
        self.assertTrue(np.isnan(m2[2, 1]).all())
        self.assertTrue(np.isfinite(common[2, 2]).all())

    def test_q2_rejects_current_and_previous_daily_volume_regime_mismatch(self) -> None:
        data, components, recipe = native_fixture()
        data["arrays"]["volume_regime"][1, 0] = 1
        common, _ = f.native(data, components, recipe)
        q2_index = int(np.flatnonzero(f.COMMON == 10)[0])
        self.assertTrue(math.isnan(float(common[1, 0, q2_index])))
        self.assertTrue(math.isfinite(float(common[1, 1, q2_index])))
        components["daily_vreg"][1, 0] = 1
        corrected, _ = f.native(data, components, recipe)
        self.assertAlmostEqual(float(corrected[1, 0, q2_index]), math.log(106 / 206), delta=1e-12)

    def test_feature_fallback_identity_channels_and_float32(self) -> None:
        common = np.tile(np.arange(15, dtype=np.float64), (2, 20, 1))
        m2 = np.ones((2, 20, 7))
        center = np.arange(15, dtype=np.float64)
        scale = np.full(15, 2.)
        for channel in (8, 12, 15):
            j = int(np.flatnonzero(f.COMMON == channel)[0])
            center[j], scale[j] = 0, 1
        common[0, 0, :] = np.nan
        common[1, 1, :] = math.inf
        m2[0, 0, :] = np.nan
        recipe = {"centers": center.tolist(), "scales": scale.tolist(), "m2_center": .5, "m2_scale": .25}
        transformed, transformed2 = f.transform(common, m2, recipe)
        self.assertEqual(transformed.dtype, np.float32)
        self.assertEqual(transformed2.dtype, np.float32)
        np.testing.assert_array_equal(transformed[0, 0], np.zeros(15, dtype=np.float32))
        np.testing.assert_array_equal(transformed[1, 1], np.zeros(15, dtype=np.float32))
        np.testing.assert_array_equal(transformed2[0, 0], np.zeros(7, dtype=np.float32))
        np.testing.assert_array_equal(transformed2[1, 0], np.full(7, 2., dtype=np.float32))

    def test_indicator_warmup_exact_boundaries_and_constant_direction_limits(self) -> None:
        values = np.stack([np.arange(1, 502, dtype=np.float64), np.full(501, 100.), np.arange(601, 100, -1, dtype=np.float64)], axis=1)
        actual = f.indicators(values, np.zeros(values.shape, dtype=np.int64))
        self.assertTrue(np.isnan(actual[:360, :, :2]).all())
        self.assertTrue(np.isfinite(actual[360:, :, :2]).all())
        self.assertTrue(np.isnan(actual[:154, :, 2]).all())
        np.testing.assert_array_equal(actual[154:, :, 2], np.tile([1., 0., -1.], (347, 1)))
        for column in range(3):
            ema = {period: float(values[0, column]) for period in (6, 18, 24, 72)}
            for index in range(1, len(values)):
                for period in ema:
                    alpha = 2 / (period + 1)
                    ema[period] = alpha * float(values[index, column]) + (1 - alpha) * ema[period]
                if index >= 360:
                    expected = [(ema[6] - ema[18]) / values[index, column], (ema[24] - ema[72]) / values[index, column]]
                    np.testing.assert_allclose(actual[index, column, :2], expected, atol=1e-12, rtol=1e-12)

    def test_indicator_missing_and_basis_resets_without_bridging_rsi(self) -> None:
        base = np.arange(1, 901, dtype=np.float64)
        values = np.repeat(base[:, None], 4, axis=1)
        values[400, 0] = np.nan
        values[400:403, 1] = np.nan
        values[10, 2] = np.nan
        regimes = np.zeros(values.shape, dtype=np.int64)
        regimes[400:, 3] = 1
        actual = f.indicators(values, regimes)
        self.assertTrue(np.isnan(actual[400, 0]).all())
        self.assertTrue(np.isfinite(actual[401, 0]).all())
        self.assertTrue(np.isnan(actual[403:763, 1, :2]).all())
        self.assertTrue(np.isfinite(actual[763, 1, :2]).all())
        self.assertTrue(np.isnan(actual[403:557, 1, 2]).all())
        self.assertEqual(actual[557, 1, 2], 1)
        self.assertTrue(np.isnan(actual[:165, 2, 2]).all())
        self.assertEqual(actual[165, 2, 2], 1)
        self.assertTrue(np.isnan(actual[400:760, 3, :2]).all())
        self.assertTrue(np.isfinite(actual[760, 3, :2]).all())
        self.assertTrue(np.isnan(actual[400:554, 3, 2]).all())
        self.assertEqual(actual[554, 3, 2], 1)
        # An isolated missing close must not create an RSI gain spanning the gap.
        varied = np.full((500, 1), 100., dtype=np.float64)
        varied[400] = np.nan
        varied[401:] = 1000.
        state = f.indicators(varied, np.zeros(varied.shape, dtype=np.int64))
        self.assertEqual(state[401, 0, 2], 0)

    def test_assembler_same_origin_context_every_historical_step(self) -> None:
        common = np.empty((60, 20, 15), dtype=np.float32)
        m2 = np.empty((60, 20, 7), dtype=np.float32)
        for step in range(60):
            for stock in range(20):
                common[step, stock] = 1000 * step + 20 * stock + np.arange(15)
                m2[step, stock] = 1000 * step + 20 * stock + np.arange(7)
        clock = [np.arange(10, dtype=np.float32), np.arange(10, dtype=np.float32) + 50]
        data = {"origins": pd.DataFrame({"first_step": [0, 6], "context": [1, 5], "clock": clock})}
        getter = f.assembler(data, np.array([0, 1]), common, m2)
        x, clocks = getter(np.array([1, 0]))
        self.assertEqual(x.shape, (2, 20, 48, 16))
        np.testing.assert_array_equal(clocks, np.array(clock)[[1, 0]])
        for row, start, context in [(0, 6, 5), (1, 0, 1)]:
            for stock in range(20):
                np.testing.assert_array_equal(x[row, stock, :, 1], m2[start:start + 48, stock, context])
                np.testing.assert_array_equal(x[row, stock][:, f.COMMON], common[start:start + 48, stock])


if __name__ == "__main__":
    unittest.main(verbosity=2)
