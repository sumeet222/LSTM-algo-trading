"""Gate D independent synthetic audits; no market or historical result inputs."""

from __future__ import annotations

import boundary

boundary.install()

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

import evaluation as ev


IDENTITY = ev.ModelIdentity("1" * 64, "2" * 64)


def fixture_rows(origins: list[tuple[str, str, bool]]) -> pd.DataFrame:
    """Schedule-shaped synthetic rows with complete twenty-stock origins."""
    records: list[dict[str, object]] = []
    for day, slot, early in origins:
        stamp = pd.Timestamp(f"{day} {slot}", tz="America/New_York")
        close = pd.Timestamp(f"{day} {'13:00' if early else '16:00'}", tz="America/New_York")
        remaining = (close - stamp).total_seconds() / 60
        if remaining >= 240:
            endpoint = stamp + pd.Timedelta(minutes=240)
            category = "INTRADAY"
        else:
            next_day = (pd.Timestamp(day) + pd.offsets.BDay()).strftime("%Y-%m-%d")
            endpoint = pd.Timestamp(f"{next_day} 09:30", tz="America/New_York") + pd.Timedelta(minutes=240 - remaining)
            category = "OVERNIGHT"
        for index, ticker in enumerate(ev.STOCKS):
            records.append({
                "origin_id": stamp.tz_convert("UTC").isoformat(),
                "session_date_et": day, "slot": slot, "category": category,
                "entry_end_utc": stamp.tz_convert("UTC"),
                "exit_end_utc": endpoint.tz_convert("UTC"),
                "label_maturity_utc": endpoint.tz_convert("UTC") + pd.Timedelta(minutes=2),
                "ticker": ticker, "early_close": early, "A": (index + 1) / 1000,
            })
    rows = pd.DataFrame.from_records(records)
    rows["weight"] = ev.hierarchy_weights(rows)
    return rows


def calibration_fixture() -> pd.DataFrame:
    rows = fixture_rows([
        ("2020-10-19", "09:30", False), ("2020-10-19", "12:30", False),
        ("2020-10-19", "13:30", False), ("2020-10-19", "14:30", False),
        ("2020-10-20", "09:30", False), ("2020-10-20", "10:30", False),
        ("2020-10-20", "11:30", False), ("2020-10-20", "12:30", False),
    ])
    rows["Mhat"] = np.float32(0)
    return rows


def fit_fixture(rows: pd.DataFrame | None = None) -> ev.C3Calibration:
    return ev.fit_c3(
        calibration_fixture() if rows is None else rows, .02, IDENTITY,
        role_cutoff_utc="2020-12-31T20:00:00-05:00", finalized_at_utc="2021-01-01T00:00:00-05:00",
    )


def scored_fixture(year: int = 2021) -> pd.DataFrame:
    rows = fixture_rows([
        (f"{year}-01-18", "09:30", False), (f"{year}-01-18", "12:30", False),
        (f"{year}-01-19", "09:30", True),
    ])
    rows["Mhat"] = np.float32(.1)
    rows["S2C-RAW"] = rows["A"] * .7
    rows["S2C-C3"] = rows["A"] * 1.2
    return ev.canonical_rows(rows, require_scores=True)


class GateDCalibrationTests(unittest.TestCase):
    def test_unclamped_q_and_decoder_order(self) -> None:
        self.assertAlmostEqual(ev.decode_raw([np.log(2)], .02)[0], .02, places=14)
        negative = calibration_fixture()
        negative["A"] = .06
        negative["Mhat"] = np.float32(-np.log(2))
        calibration = fit_fixture(negative)
        expected_q = float(np.exp(np.log1p(.06 / .02) - float(np.float32(-np.log(2)))))
        self.assertAlmostEqual(calibration.global_moment, expected_q, places=12)
        self.assertGreater(calibration.global_moment, 7.9)
        self.assertEqual(ev.decode_raw([-np.log(2)], .02)[0], 0)
        groups = tuple(replace(group, factor=1.5) for group in calibration.categories)
        explicit = replace(calibration, categories=groups)
        result = ev.decode_c3([np.log(2), -10], ["INTRADAY", "OVERNIGHT"], explicit, IDENTITY)
        np.testing.assert_allclose(result, [.04, 0], rtol=0, atol=1e-14)
        self.assertNotAlmostEqual(result[0], ev.decode_raw([np.log(2)], .02)[0] * 1.5)

    def test_effective_sessions_kappa_and_contribution_diagnostics(self) -> None:
        rows = calibration_fixture()
        rows["A"] = np.where(rows["category"].eq("INTRADAY"), .02, .06)
        calibration = fit_fixture(rows)
        self.assertAlmostEqual(calibration.global_moment, 3, places=14)
        for category in calibration.categories:
            self.assertAlmostEqual(category.effective_sessions, 1.6, places=14)
            self.assertAlmostEqual(category.rho, 1.6 / 26.6, places=14)
            moment = 2 if category.category == "INTRADAY" else 4
            self.assertAlmostEqual(category.factor, 3 + 1.6 / 26.6 * (moment - 3), places=14)
            self.assertEqual(category.sessions, 2)
        self.assertEqual(calibration.kappa, 25)
        q = np.log1p(rows["A"].to_numpy() / .02)
        q = np.exp(q)
        contributions = np.sort(q * rows["weight"].to_numpy())[::-1]
        self.assertAlmostEqual(calibration.contributions.top10_share, contributions[:10].sum() / contributions.sum(), places=14)
        self.assertAlmostEqual(calibration.contributions.top1pct_share, contributions[0] / contributions.sum(), places=14)

    def test_future_oos_labels_cannot_change_frozen_coefficients(self) -> None:
        calibration = fit_fixture()
        original = calibration
        first = fixture_rows([("2021-01-18", "09:30", False), ("2021-01-18", "12:30", False)])
        second = first.copy()
        second["A"] = first["A"] * 10_000
        values = np.linspace(-1, 1, len(first), dtype=np.float32)
        scores1 = ev.build_score_frame(first, values, calibration, IDENTITY)
        scores2 = ev.build_score_frame(second, values, calibration, IDENTITY)
        np.testing.assert_array_equal(scores1[list(ev.MODELS)], scores2[list(ev.MODELS)])
        self.assertEqual(calibration, original)
        with self.assertRaisesRegex(ValueError, "same frozen"):
            ev.decode_c3([.2], ["INTRADAY"], calibration, ev.ModelIdentity("3" * 64, "2" * 64))
        with self.assertRaisesRegex(ValueError, "same frozen"):
            ev.decode_c3([.2], ["INTRADAY"], calibration, ev.ModelIdentity("1" * 64, "4" * 64))

    def test_maturity_finalization_and_arithmetic_fail_closed(self) -> None:
        rows = calibration_fixture()
        last = str(rows["label_maturity_utc"].max())
        with self.assertRaisesRegex(ValueError, "strictly mature"):
            ev.fit_c3(rows, .02, IDENTITY, role_cutoff_utc=last, finalized_at_utc="2021-01-01T05:00:00Z")
        with self.assertRaisesRegex(ValueError, "before its last"):
            ev.fit_c3(rows, .02, IDENTITY, role_cutoff_utc="2020-12-31T20:00:00-05:00", finalized_at_utc="2020-10-01T05:00:00Z")
        rows["Mhat"] = np.float32(-1000)
        with self.assertRaises(FloatingPointError):
            fit_fixture(rows)
        rows["Mhat"] = np.float32(1000)
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            fit_fixture(rows)
        with self.assertRaises(FloatingPointError):
            ev.decode_raw([1000], .02)


class GateDEvaluationTests(unittest.TestCase):
    def test_weighted_left_and_session_hierarchy(self) -> None:
        self.assertEqual(ev.weighted_left_quantile([1, 3], [1, 1], .5), 1)
        rows = fixture_rows([
            ("2021-01-18", "09:30", False), ("2021-01-19", "09:30", False),
            ("2021-01-19", "10:30", False),
        ])
        rows["A"] = 0
        rows["P"] = np.repeat(np.sqrt([2, 4, 8]), 20)
        result = ev.scalar_metrics(rows, "P")
        self.assertAlmostEqual(float(result["mse"]), 4, places=13)
        self.assertNotAlmostEqual(float(result["mse"]), 14 / 3)
        self.assertTrue(np.isinf(result["ratio"]))
        rows["P"] = 0
        self.assertTrue(np.isnan(ev.scalar_metrics(rows, "P")["ratio"]))

    def test_equal_year_ratio_uses_mean_numerator_and_denominator(self) -> None:
        annual: list[dict[str, float | int]] = []
        for index, actual in enumerate((1., 2., 4., 8.)):
            row: dict[str, float | int] = {
                "observed": actual, "predicted": 2., "bias": 2 - actual, "mae": abs(2 - actual),
                "mse": (2 - actual) ** 2, "ratio": 2 / actual, "rows": 20 * (index + 1),
                "origins": index + 1, "sessions": index + 1,
                "original_mass": 1., "loss_contribution": (2 - actual) ** 2,
            }
            annual.append(row)
        result = ev.equal_year_scalar(annual, [float(row["mse"]) for row in annual])
        self.assertAlmostEqual(float(result["ratio"]), 2 / 3.75, places=14)
        self.assertNotAlmostEqual(float(result["ratio"]), np.mean([2, 1, .5, .25]))
        self.assertEqual(result["rows"], 200)
        self.assertAlmostEqual(float(result["loss_share"]), 1)

    def test_conditional_mass_differs_from_rebuilt_rank_session_means(self) -> None:
        rows = calibration_fixture()
        rows["S2C-RAW"] = rows["A"]
        rows["S2C-C3"] = rows["A"]
        first_day_overnight = rows["session_date_et"].eq("2020-10-19") & rows["category"].eq("OVERNIGHT")
        second_day_overnight = rows["session_date_et"].eq("2020-10-20") & rows["category"].eq("OVERNIGHT")
        rows.loc[first_day_overnight, "S2C-C3"] = rows.loc[first_day_overnight, "A"] + 1
        rows.loc[second_day_overnight, "S2C-C3"] = np.tile(np.arange(20, 0, -1) / 1000, 1)
        scalar = ev.scalar_metrics(rows.loc[rows["category"].eq("OVERNIGHT")], "S2C-C3")
        reverse_error = np.mean((np.arange(20, 0, -1) / 1000 - np.arange(1, 21) / 1000) ** 2)
        self.assertAlmostEqual(float(scalar["mse"]), .75 + .25 * reverse_error, places=13)
        tail = ev.fit_tail_thresholds(rows)
        tables = ev.evaluate_scores(rows, {2020: tail}, expected_years=(2020,))
        rank = tables.ranks.query("year == '2020' and model == 'S2C-C3' and dimension == 'category' and group == 'OVERNIGHT'").iloc[0]
        self.assertAlmostEqual(float(rank["spearman_ic"]), 0, places=14)
        self.assertNotAlmostEqual(float(rank["spearman_ic"]), .5)
        scalar_table = tables.scalars.query("year == '2020' and model == 'S2C-C3' and dimension == 'category'")
        all_mse = tables.scalars.query("year == '2020' and model == 'S2C-C3' and dimension == 'all'").iloc[0]["mse"]
        self.assertAlmostEqual(float(scalar_table["loss_contribution"].to_numpy(dtype=np.float64).sum()), float(all_mse), places=14)
        self.assertAlmostEqual(float(scalar_table["loss_share"].to_numpy(dtype=np.float64).sum()), 1, places=14)

    def test_ties_retrieval_and_undefined_ranks(self) -> None:
        truth = np.arange(20, dtype=np.float64)
        perfect = ev.origin_rank_metrics(truth, truth)
        for metric in ("spearman_ic", "pair_concordance", "top4_retrieval", "bottom4_retrieval"):
            self.assertAlmostEqual(perfect[metric], 1, places=14)
        constant = ev.origin_rank_metrics(truth, np.ones(20))
        self.assertTrue(np.isnan(constant["spearman_ic"]))
        self.assertEqual(constant["pair_concordance"], .5)
        self.assertEqual(constant["tie_rate"], 1)
        self.assertEqual(constant["constant_rate"], 1)
        self.assertAlmostEqual(constant["top4_retrieval"], .2)
        np.testing.assert_allclose(ev.fractional_top4(np.ones(20)), .2, atol=1e-15)
        tied_boundary = np.r_[np.ones(2) * 3, np.ones(4) * 2, np.zeros(14)]
        membership = ev.fractional_top4(tied_boundary)
        np.testing.assert_array_equal(membership[:6], [1, 1, .5, .5, .5, .5])
        self.assertEqual(membership.sum(), 4)
        self.assertTrue(np.isnan(ev.origin_rank_metrics(np.ones(20), truth)["pair_concordance"]))

    def test_tail_strictness_top4_and_false_low_threshold(self) -> None:
        rows = fixture_rows([("2021-01-18", "09:30", False)])
        rows["P"] = np.arange(1, 21, dtype=np.float64)
        # Values equal to threshold belong to the complement.
        rows["A"] = 1.
        rows.loc[[0, 9, 10, 19], "A"] = 2.
        event = ev.tail_event_metrics(rows, "P", 1.)
        self.assertEqual(event["event_rows"], 4)
        self.assertAlmostEqual(float(event["prevalence"]), .2)
        self.assertAlmostEqual(float(event["top4_recall"]), .25)
        self.assertAlmostEqual(float(event["top4_precision"]), .25)
        self.assertAlmostEqual(float(event["false_low_rank"]), .5)
        rows["P"] = 0.
        tied = ev.tail_event_metrics(rows, "P", 1.)
        self.assertAlmostEqual(float(tied["top4_recall"]), .2)
        self.assertAlmostEqual(float(tied["top4_precision"]), .2)
        self.assertEqual(tied["false_low_rank"], 1.)

    def test_signed_partial_mask_and_zero_variance(self) -> None:
        rows = fixture_rows([("2021-01-18", "12:30", False), ("2021-01-19", "12:30", False)])
        rows["aux_supported"] = False
        rows.loc[[0, 1, 20], "aux_supported"] = True
        for component in ev.SIGNED_COMPONENTS:
            rows[f"R_{component}"] = np.nan
            rows[f"Rhat_{component}"] = 0.
            rows.loc[[0, 1, 20], f"R_{component}"] = [1., 2., 3.]
            rows.loc[[0, 1, 20], f"Rhat_{component}"] = [2., 4., 6.]
        diagnostic = ev.signed_diagnostics(rows)
        self.assertEqual(set(diagnostic["rows"]), {3})
        self.assertEqual(set(diagnostic["sessions"]), {2})
        np.testing.assert_allclose(diagnostic["pearson"], 1, atol=1e-14)
        np.testing.assert_allclose(diagnostic["mse"], 14 / 3, atol=1e-14)
        for component in ev.SIGNED_COMPONENTS:
            rows[f"Rhat_{component}"] = 0.
        self.assertTrue(ev.signed_diagnostics(rows)["pearson"].isna().all())

    def test_full_evaluation_scope_completeness_and_no_invented_comparators(self) -> None:
        years = (2021, 2022, 2023, 2024)
        scores = pd.concat([scored_fixture(year) for year in years], ignore_index=True)
        thresholds = {year: ev.fit_tail_thresholds(scored_fixture(year)) for year in years}
        tables = ev.evaluate_scores(scores, thresholds)
        self.assertEqual(set(tables.scalars["dimension"]), {"all", "category", "slot", "stock", "calendar", "tail"})
        self.assertEqual(set(tables.scalars["year"]), {"2021", "2022", "2023", "2024", "EQ"})
        self.assertEqual(set(tables.scalars.query("dimension == 'stock'")["group"]), set(ev.STOCKS))
        self.assertEqual(set(tables.scalars.query("dimension == 'calendar'")["group"]), {"EARLY_CLOSE", "REGULAR"})
        self.assertTrue(tables.signed.empty)
        self.assertEqual(len(tables.pending), 2)
        self.assertFalse(any("decile" in str(value) for value in tables.scalars["dimension"]))

    def test_full_key_shuffled_join_checks_labels_and_twenty_names(self) -> None:
        rows = scored_fixture()
        lhs, rhs = ev.align_scores_by_full_key(rows, rows.sample(frac=1, random_state=41))
        pd.testing.assert_frame_equal(lhs, rhs)
        wrong = rows.copy()
        wrong.loc[0, "A"] += .001
        with self.assertRaisesRegex(ValueError, "mismatch: A"):
            ev.align_scores_by_full_key(rows, wrong)
        with self.assertRaisesRegex(ValueError, "twenty-stock|twenty stock"):
            ev.canonical_rows(rows.iloc[1:])
        duplicated = pd.concat([rows, rows.iloc[:1]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            ev.canonical_rows(duplicated)

    def test_new_score_storage_and_report_only_replay(self) -> None:
        calibration = fit_fixture()
        base = fixture_rows([("2021-01-18", "09:30", False), ("2021-01-18", "12:30", False)])
        scores = ev.build_score_frame(base, np.linspace(-2, 1, len(base), dtype=np.float32), calibration, IDENTITY)
        thresholds = ev.fit_tail_thresholds(calibration_fixture())
        with tempfile.TemporaryDirectory(prefix="s2c-evaluation-test-") as directory:
            root = Path(directory)
            manifest = ev.write_score_bundle(root / "new_scores", scores, {2021: calibration}, {2021: thresholds}, run_id="synthetic-gate-d")
            restored, calibrations, tail_thresholds = ev.read_score_bundle(manifest)
            pd.testing.assert_frame_equal(restored, scores)
            self.assertEqual(calibrations[2021], calibration)
            self.assertEqual(tail_thresholds[2021], thresholds)
            replay = ev.report_only_replay(manifest, root / "new_replay")
            fresh = ev.evaluate_scores(scores, {2021: thresholds}, expected_years=(2021,))
            pd.testing.assert_frame_equal(replay.scalars, fresh.scalars)
            pd.testing.assert_frame_equal(replay.ranks, fresh.ranks)
            receipt = json.loads((root / "new_replay" / "replay_receipt.json").read_text())
            self.assertEqual(receipt["fit_calls"], 0)
            self.assertTrue((replay.clamping["new_ties_vs_mhat"] > 0).any())
            with self.assertRaisesRegex(ValueError, "new destination"):
                ev.write_score_bundle(root / "new_scores", scores, {2021: calibration}, {2021: thresholds}, run_id="second")
            score_path = manifest.parent / "scores.parquet"
            with score_path.open("ab") as handle:
                handle.write(b"changed")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                ev.read_score_bundle(manifest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
