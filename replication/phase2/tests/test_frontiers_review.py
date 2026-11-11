"""Independent synthetic review of schedule, role, M2 and assembly frontiers."""
from __future__ import annotations

import boundary

boundary.install()

import unittest

import numpy as np
import pandas as pd

import dataset
import features
import geometry


class IndependentGeometryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schedule = geometry.schedule()

    def endpoint(self, day: str, clock: str) -> pd.Timestamp:
        session = int(np.flatnonzero(self.schedule["date"].to_numpy() == day)[0])
        start = pd.Timestamp(f"{day} {clock}", tz="America/New_York")
        end, _ = geometry.endpoint(start.value, session, self.schedule)
        result = pd.Timestamp(end, tz="UTC").tz_convert("America/New_York")
        if not isinstance(result, pd.Timestamp):
            raise ValueError("synthetic endpoint cannot be missing")
        return result

    def test_six_spec_endpoints_and_exact_close(self) -> None:
        examples = (
            ("2024-11-25", "09:30", "2024-11-25 13:30"),
            ("2024-11-25", "11:30", "2024-11-25 15:30"),
            ("2024-11-25", "12:30", "2024-11-26 10:00"),
            ("2024-11-22", "15:30", "2024-11-25 13:00"),
            ("2024-11-29", "09:30", "2024-12-02 10:00"),
            ("2024-11-29", "12:30", "2024-12-02 13:00"),
        )
        for day, clock, expected in examples:
            with self.subTest(day=day, clock=clock):
                self.assertEqual(self.endpoint(day, clock), pd.Timestamp(expected, tz="America/New_York"))
        self.assertEqual(self.endpoint("2024-11-25", "12:00"), pd.Timestamp("2024-11-25 16:00", tz="America/New_York"))

    def test_dst_holidays_exceptional_closures_and_halfday(self) -> None:
        self.assertEqual(self.endpoint("2024-03-08", "15:30").tz_convert("UTC"), pd.Timestamp("2024-03-11 17:00Z"))
        self.assertEqual(self.endpoint("2012-10-26", "15:30"), pd.Timestamp("2012-10-31 13:00", tz="America/New_York"))
        dates = set(self.schedule["date"])
        for closed in ("2012-10-29", "2012-10-30", "2018-12-05", "2025-01-09", "2022-06-20"):
            self.assertNotIn(closed, dates)
        self.assertIn("2021-12-31", dates)  # Saturday New Year has no Friday observation.
        row = self.schedule.loc[self.schedule["date"].eq("2024-11-29")].iloc[0]
        self.assertEqual(row["close"].tz_convert("America/New_York").strftime("%H:%M"), "13:00")

    def test_grid_slots_opening_context_and_no_stubs(self) -> None:
        hours, origins = geometry.grids(self.schedule)
        for day, hour_count, origin_count in (("2024-11-25", 6, 7), ("2024-11-29", 3, 4)):
            h = hours.loc[hours["date"].eq(day)]
            o = origins.loc[origins["date"].eq(day)]
            self.assertEqual(len(h), hour_count)
            self.assertEqual(len(o), origin_count)
            np.testing.assert_array_equal(h["end"].to_numpy() - h["start"].to_numpy(), 60 * geometry.MINUTE)
            opening = o.iloc[0]
            self.assertEqual(opening["context"], 6)
            self.assertLess(hours.iloc[int(opening["entry_index"])]["end"], opening["t"])
            for _, row in o.iloc[1:].iterrows():
                self.assertEqual(hours.iloc[int(row["entry_index"])]["end"], row["t"])
                self.assertEqual(row["context"], row["slot_index"] - 1)
                self.assertEqual(row["entry_index"] - row["first_step"], 47)
        early_open = origins.loc[origins["date"].eq("2024-11-29")].iloc[0]
        np.testing.assert_allclose(early_open["clock"][[7, 8, 9]], [210 / 240, 1, 3 / 7], rtol=1e-7, atol=1e-7)

    def test_strict_role_cutoff_and_embargo_equality(self) -> None:
        cutoff = pd.Timestamp("2024-09-30 20:00", tz="America/New_York").tz_convert("UTC").value
        rows = pd.DataFrame({
            "eligible": [True, True, True, True, False],
            "date": ["2024-09-30"] * 5,
            "first_date": ["2024-07-01", "2024-07-01", "2024-06-30", "2024-07-01", "2024-07-01"],
            "maturity": [cutoff - 1, cutoff, cutoff - 1, cutoff + 1, cutoff - 1],
        })
        np.testing.assert_array_equal(dataset.role(rows, "2024-07-01", "2024-09-30", "2024-06-30"), [0])
        np.testing.assert_array_equal(dataset.role(rows, "2024-07-01", "2024-09-30"), [0, 2])

    def test_friday_and_halfday_labels_cannot_enter_nominal_stop(self) -> None:
        for day, clock in (("2024-09-27", "15:30"), ("2024-11-29", "09:30")):
            endpoint = self.endpoint(day, clock).tz_convert("UTC").value
            rows = pd.DataFrame({"eligible": [True], "date": [day], "first_date": ["2024-01-01"], "maturity": [endpoint + 2 * geometry.MINUTE]})
            self.assertEqual(len(dataset.role(rows, "2024-01-01", day)), 0)


def component_fixture(early_day: int | None = None, days: int = 70) -> dict:
    """Synthetic scheduled days with all twenty stock cells, no data reads."""
    dates = pd.date_range("2011-04-01", periods=days, freq="B").strftime("%Y-%m-%d").tolist()
    schedule = pd.DataFrame({"date": dates, "open": [pd.Timestamp(f"{day} 09:30", tz="America/New_York").tz_convert("UTC") for day in dates], "early_close": [session == early_day for session in range(days)]})
    regular = np.asarray([session for session in range(days) if session != early_day])
    records = [(session, day, slot) for session, day in enumerate(dates) for slot in range(3 if session == early_day else 6)]
    grid = pd.DataFrame(records, columns=["session", "date", "slot"])
    origin_records = [(session, context, int(schedule.iloc[session]["open"].value) + 240 * geometry.MINUTE) for session in range(days) for context in ((6, 0, 1, 2) if session == early_day else range(7))]
    origins = pd.DataFrame(origin_records, columns=["session", "context", "maturity"])
    observations = np.asarray([session + 1 + context * 100 + np.arange(20) * 1000 for session, context, _ in origin_records], dtype=np.float64)
    n = len(grid)
    arrays: dict[str, np.ndarray] = {name: np.ones((n, 20), dtype=np.float64) for name in ("O", "H", "L", "C", "G", "V")}
    arrays.update({
        "price_regime": np.zeros((n, 20), dtype=np.int8),
        "volume_regime": np.zeros((n, 20), dtype=np.int8),
        "R": observations, "p": np.searchsorted(regular, grid["session"].to_numpy(), side="left") - 1,
        "cop_window": np.ones(n, dtype=bool),
    })
    lock = int(schedule.iloc[60]["open"].value)
    origins.loc[(origins["session"] == 59) & (origins["context"] == 0), "maturity"] = lock
    origins.loc[(origins["session"] == 59) & (origins["context"] == 1), "maturity"] = lock - geometry.MINUTE
    return {"arrays": arrays, "grid": grid, "origins": origins, "schedule": schedule, "regular": regular}


class IndependentFeatureFrontiers(unittest.TestCase):
    def test_future_source_and_labels_leave_prior_features_and_phase_recipe_invariant(self) -> None:
        data = component_fixture(days=150)
        h, o, a = data["grid"], data["origins"], data["arrays"]
        step = np.arange(len(h), dtype=np.float64)[:, None]
        stock = np.arange(20, dtype=np.float64)[None, :]
        close = 100 + .01 * step + .005 * stock + .03 * np.sin(step / 13 + stock / 7)
        a["C"], a["G"] = close.copy(), close.copy()
        a["O"] = close * np.exp(-.001 - .0002 * np.cos(step / 11 + stock / 5))
        a["H"], a["L"] = close * 1.002, a["O"] * .998
        a["V"] = 1000 + step + stock * 10
        session, context = o["session"].to_numpy(), o["context"].to_numpy()
        o["date"] = data["schedule"].iloc[session]["date"].to_numpy()
        o["entry_index"] = np.where(context == 6, session * 6 - 1, session * 6 + context)
        o["first_step"] = o["entry_index"] - 47
        o["source_input_eligible"] = (o["entry_index"].to_numpy() // 6 - 1) >= 125
        o["eligible"] = o["source_input_eligible"]
        stop_session = 140
        stop = str(data["schedule"].iloc[stop_session]["date"])
        first = features.components(data)
        recipe_before, native_before, m2_before = features.fit_recipe(data, first, stop)
        transformed_before, scaled_m2_before = features.transform(native_before, m2_before, recipe_before)
        future_hours = h["session"].to_numpy() > stop_session
        future_origins = session > stop_session
        for field in ("O", "H", "L", "C", "G"):
            a[field][future_hours] *= 1.2
        a["V"][future_hours] *= 3
        a["R"][future_origins] += 50
        second = features.components(data)
        recipe_after, native_after, m2_after = features.fit_recipe(data, second, stop)
        transformed_after, scaled_m2_after = features.transform(native_after, m2_after, recipe_before)
        self.assertEqual(recipe_before, recipe_after)
        np.testing.assert_array_equal(transformed_before[~future_hours], transformed_after[~future_hours])
        np.testing.assert_array_equal(scaled_m2_before[~future_hours], scaled_m2_after[~future_hours])
        # Once the changed next-day labels mature, later historical locks may update.
        self.assertFalse(np.array_equal(first["mean2"][142], second["mean2"][142]))
        self.assertFalse(np.array_equal(scaled_m2_before[future_hours], scaled_m2_after[future_hours]))

    def test_early_close_m2_needs_sixty_prior_regular_positions(self) -> None:
        short_history = features.components(component_fixture(early_day=30))
        self.assertTrue(np.isnan(short_history["mean2"][30]).all())
        self.assertTrue(np.isnan(short_history["rms2"][30]).all())
        self.assertTrue(np.isfinite(short_history["mean2"][29]).all())
        self.assertTrue(np.isfinite(short_history["mean2"][31]).all())
        mature_history = features.components(component_fixture(early_day=65))
        self.assertTrue(np.isfinite(mature_history["mean2"][65]).all())
        self.assertTrue(np.isfinite(mature_history["rms2"][65]).all())

    def test_phase_fit_union_uses_source_not_future_label_scoreability(self) -> None:
        dates = pd.date_range("2011-03-30", periods=14, freq="B").strftime("%Y-%m-%d").to_numpy()
        grid = pd.DataFrame({"date": np.repeat(dates, 6)})
        origins = pd.DataFrame({
            "date": grid.iloc[[47, 57, 67]]["date"].to_numpy(),
            "first_step": [0, 10, 20], "entry_index": [47, 57, 67],
            "source_input_eligible": [True, True, False], "eligible": [False, False, True],
        })
        stop = str(origins.iloc[1]["date"])
        union, unique = features.fit_indices({"grid": grid, "origins": origins}, stop)
        np.testing.assert_array_equal(union, np.arange(12, 58))
        np.testing.assert_array_equal(unique, np.arange(12, 58, 6))
        origins["eligible"] = ~origins["eligible"]
        changed, _ = features.fit_indices({"grid": grid, "origins": origins}, stop)
        np.testing.assert_array_equal(union, changed)

    def test_m2_strict_daily_lock_preserves_missing_scheduled_slot(self) -> None:
        data = component_fixture()
        first = features.components(data)
        self.assertAlmostEqual(first["mean2"][60, 0, 0], 50.)  # scheduled 41..60; 60 remains masked
        self.assertAlmostEqual(first["mean2"][60, 0, 1], 150.5)  # one minute before lock is admitted
        self.assertAlmostEqual(first["rms2"][60, 0, 0], np.sqrt(np.mean(np.arange(1., 60.) ** 2)))
        # A label maturing later in this day cannot alter this day's historical lock.
        future = data["origins"]["session"].to_numpy() >= 60
        data["arrays"]["R"][future] += 1_000_000
        second = features.components(data)
        np.testing.assert_array_equal(first["mean2"][:61], second["mean2"][:61])
        np.testing.assert_array_equal(first["rms2"][:61], second["rms2"][:61])
        recipe = {"hourly_floor": [1.] * 20, "daily_floor": [1.] * 20, "m2_floor": [1.] * 20, "pseudocounts": [{} for _ in range(20)]}
        _, native_m2 = features.native(data, first, recipe)
        steps = np.flatnonzero(data["grid"]["session"].to_numpy() == 60)
        np.testing.assert_array_equal(native_m2[steps], np.repeat(native_m2[steps[:1]], 6, axis=0))

    def test_origin_stock_time_feature_axes_and_forecast_context(self) -> None:
        origins = pd.DataFrame({"first_step": [3, 5], "context": [6, 2], "clock": [np.arange(10, dtype=np.float32), np.arange(10, dtype=np.float32) + 100]})
        step = np.arange(60)[:, None, None]
        stock = np.arange(20)[None, :, None]
        common = (step * 10_000 + stock * 100 + np.arange(15)[None, None, :]).astype(np.float32)
        m2 = (step * 10_000 + stock * 100 + np.arange(7)[None, None, :] + 50).astype(np.float32)
        assemble = features.assembler({"origins": origins}, np.array([0, 1]), common, m2)
        x, clock = assemble(np.array([1, 0]))
        self.assertEqual(x.shape, (2, 20, 48, 16))
        for local, (first, context) in enumerate(((5, 2), (3, 6))):
            for stock_index in (0, 7, 19):
                for offset in (0, 17, 47):
                    self.assertEqual(x[local, stock_index, offset, 1], m2[first + offset, stock_index, context])
                    np.testing.assert_array_equal(x[local, stock_index, offset, features.COMMON], common[first + offset, stock_index])
        np.testing.assert_array_equal(clock, np.stack(origins["clock"].tolist())[[1, 0]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
