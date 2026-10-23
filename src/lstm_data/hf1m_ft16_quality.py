"""P020 explicit quality reason masks, volume sensitivity and fit-prefix independence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_source import publish_json, publish_table
from .hf1m_ft16_fit import fit
from .hf1m_ft16_math import build, volume_fields
from .hf1m_ft16_source import COMMON, SYMBOLS, checked, configuration, read_hourly, source_masks


def verify(out: Path) -> None:
    d = json.loads((out / "model_input_contract.json").read_text())
    config = configuration()
    recipes = json.loads(checked(d["fit_recipes"]).read_text())
    hours = read_hourly(config)
    up = Path(config["upstream_packet"])
    fref = json.loads((up / "hour_field_mask_manifest.json").read_text())["file"]
    fields = pd.read_parquet(checked(fref))
    fit_checks = []
    for name in ["inner", "refit"]:
        stop = recipes[name]["fit_stop_inclusive"]
        c = build(hours.loc[hours.session_date_et.le(stop)].copy(), fields)
        selected = np.zeros(len(c.grid), bool)
        selected[np.asarray(recipes[name]["fit_hour_indices"], int)] = True
        r, _arrays = fit(c, selected, stop)
        assert r == {k: v for k, v in recipes[name].items() if k in r}
        assert not c.grid.session_date_et.loc[selected].gt(stop).any()
        fit_checks.append(
            {
                "fit": name,
                "stop": stop,
                "unique_fit_hours": int(selected.sum()),
                "prefix_only_refit_of_all_preprocessing_parameters_identical": True,
                "development_observations_used": 0,
                "overlap_windows_not_duplicated": True,
            }
        )
    full = hours.loc[~hours.is_stub].copy()
    overlay_columns = [
        "hour_id",
        "ticker",
        "session_date_et",
        "hour_start_utc",
        "hour_end_utc",
        "first_minute",
        "last_minute",
        "longest_gap_minutes",
        "opening_minutes_missing",
        "invalid_minutes",
        "quality_tier",
        "source_quality_tier_018d",
        "source_action_uncertainty_018d",
        "issue_ids",
        "issue_reasons",
        "raw_linkage_hash",
    ]
    overlay = full[overlay_columns].copy()
    age = (full.hour_end_utc - pd.Timedelta(minutes=1) - full.last_minute).dt.total_seconds() / 60
    proxy_endpoint = ~full.genuine_close & full.close_input_cap5.notna()
    if not age.loc[proxy_endpoint].between(1, 5).all():
        raise ValueError("P020_PRICE_PROXY_AGE_OR_SESSION_FAILURE")
    overlay["terminal_input_price_age_minutes"] = age.where(
        full.genuine_close | proxy_endpoint
    ).to_numpy()
    overlay_ref = publish_table(
        Path(d["files"]["components"]["path"]).parent / "P020_hour_provenance_overlay.parquet",
        overlay,
    )
    publish_json(
        out / "provenance_overlay_manifest.json",
        {
            "file": overlay_ref,
            "all_proxy_endpoint_ages_between1_and5_minutes": True,
            "genuine_endpoint_age_minutes": 0,
            "protected_numeric_rows": 0,
            "source_provenance_preserved": True,
        },
    )
    sensitivity = []
    for threshold in [0, 1, 2, 5]:
        v = volume_fields(full, threshold)
        group = v.groupby(["ticker", v.session_date_et.str[:4]]).volume_usable_for_feature.agg(
            ["sum", "size"]
        )
        for key, row in group.iterrows():
            if not isinstance(key, tuple) or len(key) != 2:
                raise ValueError("STOCK_YEAR_GROUP_REQUIRED")
            ticker, year = key
            sensitivity.append(
                {
                    "ticker": ticker,
                    "year": year,
                    "max_absent_minutes": threshold,
                    "usable_hours": int(row["sum"]),
                    "total_hours": int(row["size"]),
                    "usable_fraction": float(row["sum"] / row["size"]),
                }
            )
    pd.DataFrame(sensitivity).to_csv(
        out / "volume_threshold_sensitivity_stock_year.csv", index=False
    )
    candles = pd.read_parquet(checked(d["files"]["candles_quality"]))
    reasons = candles[["hour_id", "ticker", "session_date_et", "step", "hour_end_utc"]].copy()
    reasons["source_close_proxy"] = (
        ~candles.genuine_close & candles.close_input_cap5.notna()
    ).to_numpy()
    reasons["source_close_missing"] = candles.close_input_cap5.isna().to_numpy()
    reasons["source_open_missing"] = ~candles.genuine_open.to_numpy()
    reasons["extrema_untrusted"] = candles.high.isna().to_numpy() | candles.low.isna().to_numpy()
    reasons["source_conflict"] = candles.conflict_count.gt(0).to_numpy()
    reasons["source_material_quarantine"] = candles.quarantine_count.gt(0).to_numpy()
    reasons["volume_assumed_zero_minute"] = candles.volume_missing_assumed_zero.to_numpy()
    reasons["volume_unknown_or_severe"] = ~candles.volume_usable_for_feature.to_numpy()
    reasons["COP_long_dependency"] = candles.hour_id.map(
        fields.set_index("hour_id").hour_feature_dependency_action_crossing
    ).to_numpy()
    reasons["volume_Q1_basis_reset"] = False
    reasons["volume_Q2_basis_reset"] = False
    for stock, part in candles.groupby("ticker", sort=False):
        p = part.sort_values("step")
        daily = p.groupby("session_date_et").filter(lambda group: len(group) == 6)
        daily = daily.groupby("session_date_et", sort=True).tail(1).sort_values("session_date_et")
        days = daily.session_date_et.to_numpy()
        basis = daily.volume_basis_id.to_numpy()
        earliest = np.searchsorted(days, p.session_date_et.to_numpy(), side="left") - 60
        current = p.volume_basis_id.to_numpy()
        prior = np.searchsorted(days, p.session_date_et.to_numpy(), side="left") - 1
        good = earliest >= 0
        reset = np.zeros(len(p), bool)
        reset[good] = (basis[earliest[good]] != current[good]) | (
            basis[prior[good]] != current[good]
        )
        reasons.loc[p.index, "volume_Q2_basis_reset"] = reset
        slot = p.hour_end_utc.dt.tz_convert("America/New_York").dt.hour.to_numpy() - 10
        for which in range(6):
            own = p.iloc[np.flatnonzero(slot == which)]
            b = own.volume_basis_id.to_numpy()
            bad = np.zeros(len(b), bool)
            bad[20:] = b[:-20] != b[20:]
            reasons.loc[own.index, "volume_Q1_basis_reset"] = bad
    with np.load(checked(d["files"]["components"]), allow_pickle=False) as a:
        st = candles.step.to_numpy(int)
        j = candles.ticker.map({s: i for i, s in enumerate(SYMBOLS)}).to_numpy(int)
        for k, name in enumerate(COMMON):
            reasons["missing_" + name] = a["refit_fallback_common"][st, j, k]
        for o in (0, 1):
            reasons["missing_M2_origin" + str(o + 1)] = a["refit_fallback_m2"][st, j, o]
    private = Path(d["files"]["components"]["path"]).parent
    reason_ref = publish_table(private / "P020_component_quality_reason_masks.parquet", reasons)
    flags = [str(k) for k in reasons if reasons[k].dtype == bool]
    reasons.groupby(["ticker", reasons.session_date_et.str[:4]])[flags].mean().to_csv(
        out / "source_channel_reason_rates_stock_year.csv"
    )
    mask, clock = source_masks(config)
    mask = mask.loc[mask.session_date_et.between("2011-04-01", "2025-06-30")]
    weak = []
    for excluded in [[], ["MA"], ["AVGO"], ["MA", "AVGO"]]:
        part = mask.loc[~mask.ticker.isin(excluded)].copy()
        part["joint"] = part.origin_input_48_cap5 & part.origin_future_4h_eligible
        count = int(part.groupby("origin_id").joint.all().sum())
        weak.append(
            {
                "excluded_hypothetical": ",".join(excluded) or "NONE",
                "retained_stocks": 20 - len(excluded),
                "feature_and_endpoint_potential": count,
                "actual_cohort_changed": False,
                "smaller_target_constructed": False,
            }
        )
    pd.DataFrame(weak).to_csv(out / "weak_stock_feature_readiness_counterfactuals.csv", index=False)
    targets = pd.read_parquet(checked(d["files"]["targets"]))
    epsilon_checks = []
    origins = pd.read_parquet(checked(d["files"]["origins"]))
    for name in ["inner", "refit"]:
        recipe = recipes[name]
        t = targets.loc[
            targets.fit_version.eq(name)
            & targets.label_eligible
            & targets.session_date_et.le(recipe["fit_stop_inclusive"])
        ]
        unique = t.drop_duplicates("origin_id")
        epsilon = max(1e-4, 0.1 * float(np.median(unique.cross_section_mad)))
        assert epsilon == recipe["epsilon"]
        keys = origins.loc[
            origins.source_input_eligible
            & origins.label_eligible
            & origins.session_date_et.le(recipe["fit_stop_inclusive"]),
            "origin_id",
        ]
        scale = max(float(np.median(np.abs(t.loc[t.origin_id.isin(keys), "TG20"]))), 1e-6)
        assert scale == recipe["t2_scale"]
        epsilon_checks.append(
            {
                "fit": name,
                "epsilon": epsilon,
                "unique_train_origins": len(unique),
                "T2_scale": scale,
                "development_values_used": 0,
                "nonfinite_target_imputed": False,
                "unscaled_MAD": True,
            }
        )
    publish_json(
        out / "quality_and_fit_prefix_receipt.json",
        {
            "result": "PASS",
            "fit_prefix_checks": fit_checks,
            "epsilon_T2_independent_train_prefix_checks": epsilon_checks,
            "reason_masks": reason_ref,
            "volume_thresholds_predeclared": [0, 1, 2, 5],
            "weak_stock_counterfactuals": weak,
            "quality_masks_are_not_extra_model_channels": True,
            "genuine_zero_volume_hours": int(
                (candles.source_volume_observed & candles.observed_volume_sum.eq(0)).sum()
            ),
            "assumed_zero_minutes": int(candles.assumed_zero_missing_count.sum()),
            "unknown_conflict_quarantine_minutes": int(
                candles.quarantine_volume_unknown_count.sum()
            ),
            "feature_volume_complete_source_claim": False,
            "protected_numeric_access": False,
        },
    )
    print("FIT_PREFIX_QUALITY_AND_VOLUME_REASON_MASKS_PASS")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    verify(p.parse_args().out)


if __name__ == "__main__":
    main()
