"""Saved-score Stage3 report; no training, inference or coefficient estimation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_minute_inputs as source
from . import hf20_overnight_specialist as previous
from . import hf20_s3c_priceonly as run
from . import hf20_stage2_bcd as clock


def equal_year(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Arithmetic annual losses/means; ratios are ratios of equal-year means."""
    result = []
    for labels, g in frame.groupby(keys, sort=False):
        if len(g) != 4:
            continue
        labels = labels if isinstance(labels, tuple) else (labels,)
        row: dict[str, str | float] = {key: str(value) for key, value in zip(keys, labels)}
        for name in g.select_dtypes(include="number").columns:
            if name not in ["year", "ratio"]:
                row[name] = float(
                    g[name].sum() if name in ["rows", "origins", "sessions"] else g[name].mean()
                )
        row.update(year="EQ", ratio=float(row["predicted"]) / float(row["observed"]))
        result.append(row)
    return pd.concat([frame, pd.DataFrame(result)], ignore_index=True)


def report() -> None:
    out = run.OUT
    years = [y for y in b.YEARS if (run.DEST / f"F{y % 100}/result.json").exists()]
    frames = {}
    fits = []
    coefficients = []
    records, groups = [], []
    arms = [
        run.CAL,
        run.RAW,
        "CLOCK-C3",
        "CLOCK-RAW",
        "S3B-C3",
        "S3B-RAW",
        "C3",
        "M1",
        "C1a",
        "C0",
        "B0-VOL",
        "B0-CLOCK",
        "B0-RMEAN",
        "B0-RMED",
    ]
    grid, rows, roles = source.metadata()
    flags = np.load(out / "minute_price_observed.npy", mmap_mode="r")
    mapping = np.load(out / "minute_hour_mapping.npy")
    for year in years:
        dest = run.DEST / f"F{year % 100}"
        original = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        new = pd.read_parquet(dest / "oos_scores.parquet")
        known = pd.read_parquet(clock.OUT / f"s2b_clock/F{year % 100}/oos_scores.parquet")
        pd.testing.assert_frame_equal(
            original[[*c3.META, "A"]], new[[*c3.META, "A"]], check_dtype=False
        )
        pd.testing.assert_frame_equal(
            original[[*c3.META, "A"]], known[[*c3.META, "A"]], check_dtype=False
        )
        summary = pd.read_parquet(source.OUT / f"S3B/F{year % 100}/oos_scores.parquet")
        pd.testing.assert_frame_equal(
            original[[*c3.META, "A"]], summary[[*c3.META, "A"]], check_dtype=False
        )
        f = original.copy()
        for arm in ["S3B-RAW", "S3B-C3"]:
            f[arm] = summary[arm]
        f["C3"] = previous.frozen_c3(f, year)
        for arm in [run.RAW, run.CAL]:
            f[arm] = new[arm]
        for arm in ["CLOCK-RAW", "CLOCK-C3"]:
            f[arm] = known[arm]
        assert np.isfinite(f[arms].to_numpy()).all() and (f[arms].to_numpy() >= 0).all()
        fits.append(b.read(dest / "result.json"))
        coef = pd.read_csv(dest / "calibration_coefficients.csv", float_precision="round_trip")
        coef.insert(0, "year", year)
        coefficients.append(coef)
        phases = b.read(dest / "phases.json")
        scale = phases["phases"]["restricted"]["scale"]
        z = new.Mhat.to_numpy(float)
        np.testing.assert_allclose(f[run.RAW], previous.raw_decode(z, scale), rtol=0, atol=0)
        factors = dict(zip(coef.group, coef.c_star))
        np.testing.assert_allclose(
            f[run.CAL],
            c3.decode(z, scale, f.category.map(factors).to_numpy()),
            atol=1e-15,
            rtol=1e-13,
        )
        pos = roles[f"F{year % 100}_oos"]
        observed = flags[mapping[rows.iloc[pos].entry_index.to_numpy(int)]]
        latest = observed.all(-1).ravel()
        f["source_latest_complete"] = latest
        f["source_latest_complete_fraction"] = observed.mean(-1).ravel()
        frames[year] = f
        early = f.exit_end_utc.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
        # The actual origin session duration, not the outcome day, defines early close.
        early_mask = np.repeat(~rows.iloc[pos].regular_session.to_numpy(bool), 20)
        assert early.notna().all()
        for scope, take in [
            ("FULL", np.ones(len(f), bool)),
            ("INTRADAY", f.category.eq("INTRADAY").to_numpy()),
            ("OVERNIGHT", f.category.eq("OVERNIGHT").to_numpy()),
        ]:
            h = f.loc[take]
            for arm in arms:
                result: dict[str, str | int | float] = dict(
                    year=str(year),
                    scope=scope,
                    arm=arm,
                    **b.metrics(h, arm),
                    **b.rank_metrics(h, arm),
                )
                if arm in [run.RAW, run.CAL]:
                    w = h.weight.to_numpy(float, copy=True)
                    w /= w.sum()
                    result["unchanged_encoder_M_MSE"] = float(
                        w
                        @ (np.log1p(h.A.to_numpy() / scale) - new.loc[take, "Mhat"].to_numpy()) ** 2
                    )
                    result["raw_decode_clamp_rate"] = float(
                        np.average(new.loc[take, "Mhat"].lt(0), weights=w)
                    )
                records.append(result)
        cuts = np.unique(
            [b.quantile(f.C0.to_numpy(), q, f.weight.to_numpy()) for q in np.arange(0.1, 1, 0.1)]
        )
        bins = np.searchsorted(cuts, f.C0, side="left") + 1
        masks = [("slot", v, f.slot.eq(v).to_numpy()) for v in b.SLOTS]
        masks += [("stock", str(v), f.ticker.eq(v).to_numpy()) for v in b.SYMBOLS]
        masks += [
            ("month", str(v), f.session_date_et.str[:7].eq(v).to_numpy())
            for v in sorted(f.session_date_et.str[:7].unique())
        ]
        masks += [("calendar", "EARLY", early_mask), ("calendar", "NORMAL", ~early_mask)]
        masks += [
            ("source_latest", label, latest == value)
            for label, value in [("COMPLETE", True), ("INCOMPLETE", False)]
        ]
        masks += [("C0_decile", str(v), bins == v) for v in np.unique(bins)]
        for level in [95, 99]:
            event = f.A.gt(phases["thresholds"][str(level)]).to_numpy()
            for scope, take in [
                ("ALL", np.ones(len(f), bool)),
                ("INTRADAY", f.category.eq("INTRADAY").to_numpy()),
                ("OVERNIGHT", f.category.eq("OVERNIGHT").to_numpy()),
            ]:
                masks += [
                    (f"tail_{scope}", f"PREFIX{level}", event & take),
                    (f"tail_{scope}", f"LE_PREFIX{level}", ~event & take),
                ]
        for arm in [
            run.CAL,
            run.RAW,
            "CLOCK-C3",
            "CLOCK-RAW",
            "C3",
            "M1",
            "C0",
            "B0-VOL",
            "B0-CLOCK",
        ]:
            total = b.metrics(f, arm)["raw_MSE"]
            ranked = f.groupby("origin_id")[arm]
            low = ranked.rank(method="average").le(10.5)
            first = ranked.rank(method="min", ascending=False)
            last = ranked.rank(method="max", ascending=False)
            top = np.clip((5 - first) / (last - first + 1), 0, 1)
            for field, label, take in masks:
                h = f.loc[take]
                if h.empty:
                    continue
                contribution = float((h.weight * (h[arm] - h.A) ** 2).sum())
                row = dict(
                    year=str(year),
                    arm=arm,
                    field=field,
                    group=label,
                    **b.metrics(h, arm),
                    weight_mass=float(h.weight.sum()),
                    raw_MSE_contribution=contribution,
                    raw_MSE_loss_share=contribution / total,
                    false_low_rank=float(np.average(low.loc[take], weights=h.weight)),
                    top4_group_capture=float(np.average(top.loc[take], weights=h.weight)),
                    source_complete_fraction=float(
                        np.average(h.source_latest_complete_fraction, weights=h.weight)
                    ),
                )
                if field in ["slot", "calendar"]:
                    row.update(b.rank_metrics(h, arm))
                groups.append(row)
    metric = pd.DataFrame(records)
    group = pd.DataFrame(groups)
    if len(years) == 4:
        metric = equal_year(metric, ["scope", "arm"])
        group = equal_year(group, ["arm", "field", "group"])
        full = metric.loc[metric.scope.eq("FULL")].set_index(["year", "arm"]).raw_MSE
        for ix, row in group.loc[group.year.eq("EQ")].iterrows():
            group.loc[ix, "raw_MSE_loss_share"] = (
                row.raw_MSE_contribution / full.loc[("EQ", row.arm)]
            )
    metric.to_csv(run.DEST / "metrics.csv", index=False)
    group.to_csv(run.DEST / "groups.csv", index=False)
    pd.DataFrame(fits).to_csv(run.DEST / "fit_summary.csv", index=False)
    if coefficients:
        pd.concat(coefficients, ignore_index=True).to_csv(
            run.DEST / "calibration_coefficients.csv", index=False
        )
    paired = []
    for left, right in [
        (run.CAL, "CLOCK-C3"),
        (run.CAL, "S3B-C3"),
        (run.RAW, "S3B-RAW"),
        (run.CAL, "C3"),
        (run.CAL, "M1"),
        (run.CAL, "C0"),
        (run.CAL, "B0-VOL"),
        (run.CAL, "B0-CLOCK"),
        (run.RAW, "CLOCK-RAW"),
        (run.RAW, "C0"),
    ]:
        for scope in ["FULL", "INTRADAY", "OVERNIGHT"]:
            months = {}
            for year, f in frames.items():
                h = f if scope == "FULL" else f.loc[f.category.eq(scope)]
                months[year] = (
                    pd.DataFrame(
                        dict(
                            day=h.session_date_et,
                            numerator=h.weight * ((h[left] - h.A) ** 2 - (h[right] - h.A) ** 2),
                            mass=h.weight,
                        )
                    )
                    .groupby("day")
                    .sum()
                )
            for value in previous.paired_months(months):
                ref = metric.loc[
                    metric.year.eq(value["year"]) & metric.scope.eq(scope) & metric.arm.eq(right),
                    "raw_MSE",
                ].to_numpy(float)[0]
                paired.append(
                    dict(
                        left=left,
                        right=right,
                        scope=scope,
                        **value,
                        percent=100 * value["delta"] / ref,
                        interval_includes_zero=value["low"] <= 0 <= value["high"],
                    )
                )
    pd.DataFrame(paired).to_csv(run.DEST / "paired_MSE.csv", index=False)
    status = "COMPLETE" if len(years) == 4 else "PARTIAL"
    pair_frame = pd.DataFrame(paired)
    section = [
        "# S3-C newest-hour price-only H8",
        f"**{status}: {len(years)}/4 folds; exploratory/post-search.**",
        (
            "Same complete20 original4h target/keys/weights. Unchanged48x16 plus newest60x5 "
            "price-only H8,6931parameters,H32,seed42,original transformed-M "
            "selector/refit and own independentOct-Dec C3kappa25. Raw is a diagnostic,"
            "never an OOS-selected replacement."
        ),
        "## Annual/equal-year primary metrics",
        b.markdown(
            metric.loc[
                metric.scope.eq("FULL"),
                [
                    "year",
                    "arm",
                    "raw_MSE",
                    "raw_MAE",
                    "predicted",
                    "observed",
                    "ratio",
                    "magnitude_IC",
                ],
            ]
        ),
        "## Paired whole-month descriptive uncertainty",
        b.markdown(pair_frame.loc[pair_frame["scope"].eq("FULL"), :]),
        "## Boundaries",
        (
            "400 whole-calendar-month draws/seed22042,year-stratified equal-year. Conditional "
            "on trained/selected/calibrated models and repeatedly inspected years;not "
            "selection-adjusted confirmation. Group scores renormalize original row weights "
            "within the conditional population,not an independent replication. Tail thresholds "
            "are original lawful September-prefix95/99;cohorts retrospective. C0 score deciles "
            "are descriptive shared memberships,not future calibration boundaries. See "
            "groups.csv for clocks,IO,early closes,stock/month,tails and source missingness. "
            "Magnitudes are not signed alpha,volatility-integral,option-IV or P&L."
        ),
        (
            "Source publication byorigin+2min and revised-vintage action/quarantine rules "
            "are disclosed historical proxies. Masks/extra parameters and B's full48-hour "
            "information versus C's intended newest-hour reach prevent architecture-only "
            "attribution. No minute volume/share-regime normalizer is used in the new model."
        ),
        (
            "The former S3-C volume-based experiment remains BLOCKED and unchanged. This "
            "price-only amendment is separate. No optional latest-hour fitted "
            "control,third LSTM,S3-D/E,Stage5,protected release or trading work."
        ),
    ]
    (run.DEST / "S3C_PRICE_ONLY_RESULTS.md").write_text("\n\n".join(section) + "\n")


if __name__ == "__main__":
    report()
