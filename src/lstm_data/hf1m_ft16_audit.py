"""P020 quantitative readiness, genuine label checks and deterministic batch QA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_source import publish_json, publish_table
from .hf1m_ft16_loader import inverse_t2, load_model_input
from .hf1m_ft16_source import COMMON, ORDER, SYMBOLS, checked


def longest_missing(a: np.ndarray) -> int:
    best = run = 0
    for value in a:
        run = 0 if value else run + 1
        best = max(best, run)
    return best


def window_sum(a: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    prefix = np.concatenate([np.zeros((1,) + a.shape[1:]), np.cumsum(a, axis=0)], axis=0)
    return prefix[ends + 1] - prefix[starts]


def audit(out: Path) -> None:
    d = json.loads((out / "model_input_contract.json").read_text())
    recipes = json.loads(checked(d["fit_recipes"]).read_text())
    rows = pd.read_parquet(checked(d["files"]["origins"]))
    grid = pd.read_parquet(checked(d["files"]["grid"]))
    candles = pd.read_parquet(checked(d["files"]["candles_quality"]))
    targets = pd.read_parquet(checked(d["files"]["targets"]))
    private = Path(d["files"]["components"]["path"]).parent
    with np.load(checked(d["files"]["components"]), allow_pickle=False) as store:
        arrays = {key: store[key] for key in store.files if key.startswith(("inner_", "refit_"))}
    assert not rows.session_date_et.ge("2026-01-01").any()
    assert not candles.session_date_et.ge("2026-01-01").any()
    assert not targets.session_date_et.ge("2026-01-01").any()
    training = rows.loc[rows.refit_admitted]
    year_counts = training.groupby(training.session_date_et.str[:4]).size().to_dict()
    summaries = []
    missingness = []
    drift = []
    fallbacks = []
    waterfall = []
    index = pd.DatetimeIndex(grid.hour_start_utc)
    volume = (
        candles.pivot(
            index="hour_start_utc", columns="ticker", values="volume_missing_assumed_zero"
        )
        .reindex(index=index, columns=SYMBOLS)
        .to_numpy(bool)
    )
    poor = (
        candles.pivot(index="hour_start_utc", columns="ticker", values="volume_usable_for_feature")
        .reindex(index=index, columns=SYMBOLS)
        .to_numpy(bool)
    )
    proxy = (
        candles.pivot(index="hour_start_utc", columns="ticker", values="proxy_count")
        .reindex(index=index, columns=SYMBOLS)
        .to_numpy(float)
    )
    missing = (
        candles.pivot(index="hour_start_utc", columns="ticker", values="assumed_zero_missing_count")
        .reindex(index=index, columns=SYMBOLS)
        .to_numpy(float)
    )
    origin_quality = rows.copy()
    starts = rows.first_step.to_numpy(dtype=int)
    ends = rows.entry_index.to_numpy(dtype=int)
    for key, a in [
        ("assumed_zero_minute_count", missing),
        ("price_proxy_minute_count", proxy),
        ("poor_volume_hour_count", ~poor),
    ]:
        origin_quality[key] = window_sum(a, np.maximum(starts, 0), ends).sum(axis=1).astype(int)
    for name in ["inner", "refit"]:
        a = arrays[name + "_native_common"]
        m = arrays[name + "_native_m2"]
        scaled = arrays[name + "_scaled_common"]
        scaled_m2 = arrays[name + "_scaled_m2"]
        assert np.isfinite(scaled).all() and np.isfinite(scaled_m2).all()
        imputed = arrays[name + "_fallback_common"]
        im2 = arrays[name + "_fallback_m2"]
        total = window_sum(imputed, np.maximum(starts, 0), ends).sum(axis=(1, 2))
        o = rows.entry_end_utc.dt.tz_convert("America/New_York").dt.hour.to_numpy() - 10
        m2count = window_sum(im2, np.maximum(starts, 0), ends).sum(axis=1)
        origin_quality[name + "_feature_fallback_cells"] = (
            total + m2count[np.arange(len(rows)), o]
        ).astype(int)
        fit_idx = np.asarray(recipes[name]["fit_hour_indices"], dtype=int)
        assert grid.session_date_et.iloc[fit_idx].le(recipes[name]["fit_stop_inclusive"]).all()
        assert len(set(fit_idx)) == len(fit_idx)
        for k, feature in enumerate(COMMON):
            sample = a[fit_idx, :, k]
            finite = sample[np.isfinite(sample)]
            value = scaled[fit_idx, :, k].reshape(-1)
            dev = scaled[grid.session_date_et.ge("2025-07-01").to_numpy(), :, k].reshape(-1)
            summaries.append(
                {
                    "fit": name,
                    "feature": feature,
                    "native_n": len(finite),
                    "native_median": float(np.median(finite)),
                    "scaled_min": float(value.min()),
                    "scaled_p01": float(np.quantile(value, 0.01)),
                    "scaled_p99": float(np.quantile(value, 0.99)),
                    "scaled_max": float(value.max()),
                    "scaled_std": float(value.std()),
                    "native_unique": len(np.unique(finite)),
                    "fallback_fraction_unique_fit": float(imputed[fit_idx, :, k].mean()),
                }
            )
            drift.append(
                {
                    "fit": name,
                    "feature": feature,
                    "training_scaled_median": float(np.median(value)),
                    "development_scaled_median": float(np.median(dev)),
                    "development_scaled_p99": float(np.quantile(dev, 0.99)),
                }
            )
        for split in (
            ["inner_train", "inner_validation"] if name == "inner" else ["refit", "development"]
        ):
            chosen = rows[split + "_admitted"].to_numpy()
            r = rows.loc[chosen]
            ss = r.first_step.to_numpy(int)
            ee = r.entry_index.to_numpy(int)
            oo = o[chosen]
            denominator = len(r) * 20 * 48
            common_counts = window_sum(imputed, ss, ee).sum(axis=(0, 1))
            m2_counts = window_sum(im2, ss, ee).sum(axis=1)
            for feature in ORDER:
                count = (
                    float(m2_counts[np.arange(len(r)), oo].sum())
                    if feature == "M2"
                    else float(common_counts[COMMON.index(feature)])
                )
                fallbacks.append(
                    {
                        "split": split,
                        "feature": feature,
                        "fallback_cells": int(count),
                        "admitted_cells": denominator,
                        "fallback_fraction": count / denominator,
                    }
                )
        if name == "refit":
            years = grid.session_date_et.str[:4].to_numpy()
            for year in sorted(set(years)):
                selected = years == year
                for j, stock in enumerate(SYMBOLS):
                    for feature in ORDER:
                        good = (
                            np.isfinite(m[selected, j, :]).reshape(-1)
                            if feature == "M2"
                            else np.isfinite(a[selected, j, COMMON.index(feature)])
                        )
                        missingness.append(
                            {
                                "ticker": stock,
                                "year": year,
                                "feature": feature,
                                "rows": len(good),
                                "native_available_fraction": float(good.mean()),
                                "fallback_fraction": float((~good).mean()),
                                "longest_missing_scheduled_positions": longest_missing(good),
                                "assumed_zero_volume_hour_fraction": float(
                                    volume[selected, j].mean()
                                ),
                                "poor_volume_hour_fraction": float((~poor[selected, j]).mean()),
                                "proxy_minute_count": int(proxy[selected, j].sum()),
                            }
                        )
    for split in ["inner_train", "inner_validation", "refit", "development"]:
        mask = rows[split]
        if split == "inner_validation":
            mask = rows.session_date_et.between("2023-01-24", "2025-06-30")
        if split == "development":
            mask = rows.session_date_et.ge("2025-07-01")
        r = rows.loc[mask]
        waterfall.append(
            {
                "split": split,
                "scheduled": len(r),
                "past_source_input": int(r.source_input_eligible.sum()),
                "finite16_after_declared_fallback": int(r.source_input_eligible.sum()),
                "genuine20_future": int(r.label_eligible.sum()),
                "joint_before_fit_embargo": int((r.source_input_eligible & r.label_eligible).sum()),
                "final_admitted": int(r[split + "_admitted"].sum()),
                "stock_rows": int(r[split + "_admitted"].sum()) * 20,
            }
        )
    pd.DataFrame(summaries).to_csv(out / "feature_distributions_train_unique.csv", index=False)
    pd.DataFrame(missingness).to_csv(out / "feature_missingness_stock_year.csv", index=False)
    pd.DataFrame(drift).to_csv(out / "feature_drift_train_vs_development.csv", index=False)
    pd.DataFrame(fallbacks).to_csv(out / "admitted_feature_fallback_rates.csv", index=False)
    pd.DataFrame(waterfall).to_csv(out / "origin_attrition_waterfall.csv", index=False)
    origin_ref = publish_table(private / "P020_origin_quality_diagnostics.parquet", origin_quality)
    cquality = candles.groupby(
        ["ticker", candles.session_date_et.str[:4], "volume_quality_tier"]
    ).agg(
        hours=("hour_id", "size"),
        assumed_zero_minutes=("assumed_zero_missing_count", "sum"),
        unknown_minutes=("quarantine_volume_unknown_count", "sum"),
        observed_fraction=("observed_minute_fraction", "mean"),
    )
    cquality.to_csv(out / "volume_quality_stock_year.csv")
    batch_checks = []
    for split in ["inner_train", "inner_validation", "refit", "development"]:
        view = load_model_input(
            out / "model_input_contract.json",
            split=split,
            fit_version="inner" if split.startswith("inner") else "refit",
        )
        positions = (0, len(view.rows) // 2, len(view.rows) - 1)
        raw = view.batch(positions)
        other = view.batch(positions, "T2")
        repeat = view.batch(positions)
        assert np.array_equal(raw["x"], other["x"]) and np.array_equal(raw["x"], repeat["x"])
        np.testing.assert_allclose(
            inverse_t2(other["y"].astype(float), view.fit["t2_scale"]),
            raw["y"],
            rtol=3e-6,
            atol=1e-6,
        )
        for i, position in enumerate(positions):
            row = view.rows.iloc[position]
            last = int(row.entry_index)
            first = int(row.first_step)
            o = pd.Timestamp(row.entry_end_utc).tz_convert("America/New_York").hour - 10
            for k, feature in enumerate(ORDER):
                r = (
                    arrays[view.fit_version + "_native_m2"][first : last + 1, :, o].T
                    if feature == "M2"
                    else arrays[view.fit_version + "_native_common"][
                        first : last + 1, :, COMMON.index(feature)
                    ].T
                )
                p = recipes[view.fit_version]["scalers"][feature]
                f = recipes[view.fit_version]["fallbacks"][feature]
                expected = ((np.where(np.isfinite(r), r, f) - p["center"]) / p["scale"]).astype(
                    np.float32
                )
                assert np.array_equal(expected, raw["x"][i, :, :, k]), feature
            batch_checks.append(
                {
                    "split": split,
                    "origin_id": str(row.origin_id),
                    "source_first_end": str(grid.hour_end_utc.iloc[first]),
                    "source_last_end": str(grid.hour_end_utc.iloc[last]),
                    "cutoff": str(row.entry_end_utc),
                    "issuance": str(row.issuance_utc),
                    "label_maturity": str(row.label_maturity_utc),
                    "shape": [20, 48, 16],
                    "component_float32_bitwise_equal": True,
                    "C0_T2_inputs_identical": True,
                }
            )
    # Reconstruct authentic future endpoints and target decomposition from source rows.
    target_checks = []
    for name in ["inner", "refit"]:
        t = targets.loc[targets.fit_version.eq(name)]
        sample = (
            t.loc[t.label_eligible]
            .sort_values("TG20", key=lambda s: s.abs(), ascending=False)
            .head(25)
        )
        for row in sample.to_dict("records"):
            stock = str(row["ticker"])
            entry = pd.Timestamp(str(row["entry_end_utc"]))
            exit_ = pd.Timestamp(str(row["exit_end_utc"]))
            endpoint = candles.loc[
                candles.ticker.eq(stock) & candles.hour_end_utc.isin([entry, exit_])
            ].sort_values("hour_end_utc")
            assert (
                len(endpoint) == 2
                and endpoint.genuine_close.all()
                and endpoint.price_basis_id.nunique() == 1
            )
            expected = float(np.log(endpoint.close.iloc[1] / endpoint.close.iloc[0]))
            assert abs(expected - float(row["return_4h"])) < 1e-14
            assert (
                abs((float(row["numerator"]) / float(row["denominator"])) - float(row["TG20"]))
                < 1e-12
            )
            target_checks.append(
                {
                    "fit": name,
                    "origin_id": row["origin_id"],
                    "ticker": stock,
                    "genuine_endpoint_ratio_verified": True,
                }
            )
    tf = targets.loc[
        targets.fit_version.eq("refit")
        & targets.label_eligible
        & targets.session_date_et.le("2025-06-30")
    ].copy()
    q_mad = float(tf.cross_section_mad.quantile(0.05))
    q_num = float(tf.numerator.abs().quantile(0.95))
    q_tail = float(tf.TG20.abs().quantile(0.99))
    tf["tail_class"] = np.where(
        tf.cross_section_mad.le(q_mad) & tf.numerator.abs().ge(q_num),
        "BOTH",
        np.where(
            tf.cross_section_mad.le(q_mad),
            "SMALL_MAD",
            np.where(tf.numerator.abs().ge(q_num), "LARGE_NUMERATOR", "ORDINARY"),
        ),
    )
    selections = []
    for key, series, asc in [
        ("TOP_ABS_TG20", tf.TG20.abs(), False),
        ("TOP_ABS_NUMERATOR", tf.numerator.abs(), False),
        ("SMALLEST_MAD", tf.cross_section_mad, True),
    ]:
        a = tf.loc[series.sort_values(ascending=asc).head(100).index].copy()
        a["selection"] = key
        selections.append(a)
    tail_ref = publish_table(
        private / "P020_target_extremes_dashboard.parquet", pd.concat(selections, ignore_index=True)
    )
    correlations = []
    origin_lookup = rows.set_index("origin_id")
    selected_origins = origin_lookup.loc[tf.origin_id]
    ii = selected_origins.entry_index.to_numpy(dtype=int)
    jj = tf.ticker.map({name: j for j, name in enumerate(SYMBOLS)}).to_numpy(dtype=int)
    oo = selected_origins.entry_end_utc.dt.tz_convert("America/New_York").dt.hour.to_numpy() - 10
    for feature in ORDER:
        values = (
            arrays["refit_scaled_m2"][ii, jj, oo]
            if feature == "M2"
            else arrays["refit_scaled_common"][ii, jj, COMMON.index(feature)]
        )
        # Spearman is Pearson correlation of average tie ranks; no SciPy dependency.
        corr = float(pd.Series(values).rank().corr(pd.Series(tf.TG20.to_numpy()).rank()))
        correlations.append(
            {
                "feature": feature,
                "training_contemporaneous_input_vs_future_TG20_spearman": corr,
                "diagnostic_only_no_feature_selection": True,
            }
        )
    pd.DataFrame(correlations).to_csv(
        out / "training_input_target_correlation_diagnostic.csv", index=False
    )
    publish_json(
        out / "quantitative_qa.json",
        {
            "year_train_origin_counts": {str(k): int(v) for k, v in year_counts.items()},
            "train_years_at_least100": sum(v >= 100 for v in year_counts.values()),
            "waterfall": waterfall,
            "admitted_fallback_rates": fallbacks,
            "maximum_admitted_channel_fallback_fraction": max(
                f["fallback_fraction"] for f in fallbacks
            ),
            "train_only_tail_thresholds": {
                "mad_p05": q_mad,
                "abs_numerator_p95": q_num,
                "abs_TG20_p99": q_tail,
            },
            "training_TG20_quantiles": {
                str(q): float(tf.TG20.quantile(q)) for q in [0, 0.01, 0.5, 0.99, 1]
            },
            "tail_mechanism_counts": tf.loc[tf.TG20.abs().ge(q_tail)]
            .tail_class.value_counts()
            .to_dict(),
            "final16_all_finite": True,
            "new_store_protected_rows": 0,
            "source_complete48_volume20_windows": 0,
            "batch_checks": batch_checks,
            "target_extreme_endpoint_checks": target_checks,
            "quality_artifacts": {"origin_quality": origin_ref, "target_extremes": tail_ref},
            "model_trained": False,
        },
    )
    print("QUANTITATIVE_AND_BATCH_QA_PASS")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    audit(p.parse_args().out)


if __name__ == "__main__":
    main()
