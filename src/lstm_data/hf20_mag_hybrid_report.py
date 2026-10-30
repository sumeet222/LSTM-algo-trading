"""Saved-score hybrid magnitude/rank assessment; no model or baseline fitting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch

from . import hf20_mag_hybrid as run
from . import hf20_mag_rank_report as rr
from . import hf20_overnight_specialist as previous

b, c3, clock = run.b, run.c3, run.clock


def equal_year(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Only four completed annual estimates yield an equal-year row."""
    result = []
    for labels, g in frame.groupby(keys, sort=False):
        if g.year.nunique() != 4:
            continue
        labels = labels if isinstance(labels, tuple) else (labels,)
        row: dict[str, str | float] = {key: str(value) for key, value in zip(keys, labels)}
        row["year"] = "EQ"
        for name in g.select_dtypes(include="number").columns:
            if name not in ["year", "ratio"]:
                row[name] = float(
                    g[name].sum()
                    if name in ["rows", "origins", "sessions", "undefined_IC_origins"]
                    else g[name].mean()
                )
        if "predicted" in row:
            row["ratio"] = float(row["predicted"]) / float(row["observed"])
        result.append(row)
    return pd.concat([frame, pd.DataFrame(result)], ignore_index=True)


def rank_summary(a: np.ndarray, z: np.ndarray, days: np.ndarray) -> dict:
    """Equal origins/session rank reduction; conservative and historical IC shown."""
    o = pd.DataFrame(rr.origin_metrics(a, z))
    o["day"] = days
    return dict(rr.reduce(o), undefined_IC_origins=int(o.historical_IC.isna().sum()))


def report() -> None:
    out = run.OUT
    years = [y for y in b.YEARS if (out / f"F{y % 100}/result.json").exists()]
    assert all(b.read(out / f"F{y % 100}/result.json")["status"] == "COMPLETED" for y in years)
    _, rows = b.metadata()
    plans = clock.saved_plans(rows)
    metrics = []
    ranking = []
    groups = []
    rankgroups = []
    tails = []
    stocks = []
    dynamics = []
    fits = []
    coefs = []
    paths = []
    frames = {}
    origin_tables = {}
    magarms = [
        run.CAL,
        run.RAW,
        "CLOCK-C3",
        "CLOCK-RAW",
        "S2C-C3",
        "C0",
        "C1a",
        "C3",
        "M1",
        "B0-VOL",
        "B0-CLOCK",
        "B0-RMEAN",
        "B0-RMED",
    ]
    for year in years:
        dest = out / f"F{year % 100}"
        original = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        new = pd.read_parquet(dest / "oos_scores.parquet")
        f = original.copy()
        pd.testing.assert_frame_equal(
            new[[*c3.META, "A"]], original[[*c3.META, "A"]], check_dtype=False
        )
        f["C3"] = previous.frozen_c3(original, year)
        for root, names in [
            (clock.OUT / "s2b_clock", ["CLOCK-RAW", "CLOCK-C3"]),
            (Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28"), ["S2C-C3"]),
        ]:
            ref = pd.read_parquet(root / f"F{year % 100}/oos_scores.parquet")
            pd.testing.assert_frame_equal(
                ref[[*c3.META, "A"]], original[[*c3.META, "A"]], check_dtype=False
            )
            for name in names:
                f[name] = ref[name]
        for name in [run.RAW, run.CAL, "Mhat"]:
            f[name] = new[name]
        for arm in ["S5A", "S5B", "LINEAR"]:
            ref = pd.read_parquet(run.rank.OUT / arm / f"F{year % 100}/oos_scores.parquet")
            pd.testing.assert_frame_equal(
                ref[[*c3.META, "A"]], original[[*c3.META, "A"]], check_dtype=False
            )
            f[arm] = ref.score
        assert np.isfinite(f[magarms].to_numpy()).all() and (f[magarms].to_numpy() >= 0).all()
        frames[year] = f
        meta = f.iloc[::20].reset_index(drop=True)
        a = f.A.to_numpy().reshape(-1, 20)
        days = meta.session_date_et.to_numpy()
        phases = b.read(dest / "phases.json")
        scale = phases["phases"]["restricted"]["scale"]
        coef = pd.read_csv(dest / "calibration_coefficients.csv", float_precision="round_trip")
        coef.insert(0, "year", year)
        coefs.append(coef)
        fits.append(b.read(dest / "result.json"))
        allarms = magarms + ["Mhat", "S5A", "S5B", "LINEAR"]
        ranks = {
            name: pd.DataFrame(f[name].to_numpy().reshape(-1, 20)).rank(axis=1).to_numpy()
            for name in allarms
        }
        for name in [run.RAW, run.CAL]:
            assert np.array_equal(new[name + "_rank"].to_numpy().reshape(-1, 20), ranks[name])
            paths.append(
                dict(
                    year=year,
                    arm=name,
                    changed_origins=int(np.any(ranks[name] != ranks["Mhat"], axis=1).sum()),
                    changed_stock_rows=int(np.count_nonzero(ranks[name] != ranks["Mhat"])),
                    zero_predictions=int((f[name] == 0).sum()),
                )
            )
        early = np.repeat(~rows.iloc[plans[year]["oos"]].regular_session.to_numpy(bool), 20)
        scopes = [
            ("FULL", np.ones(len(f), bool)),
            ("INTRADAY", f.category.eq("INTRADAY").to_numpy()),
            ("OVERNIGHT", f.category.eq("OVERNIGHT").to_numpy()),
        ]
        for arm in allarms:
            z = f[arm].to_numpy().reshape(-1, 20)
            vals = pd.DataFrame(rr.origin_metrics(a, z))
            vals["day"] = days
            origin_tables[(year, arm)] = vals
            for scope, take in scopes:
                ix = take[::20]
                h = f.loc[take]
                rk = rank_summary(a[ix], z[ix], days[ix])
                ranking.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        scope=scope,
                        rows=len(h),
                        origins=len(h) // 20,
                        sessions=h.session_date_et.nunique(),
                        **rk,
                    )
                )
                if arm in magarms:
                    entry: dict = dict(
                        year=str(year), arm=arm, scope=scope, **b.metrics(h, arm), **rk
                    )
                    if arm in [run.RAW, run.CAL]:
                        w = h.weight.to_numpy() / h.weight.sum()
                        entry["encoder_M_MSE"] = float(
                            w @ (np.log1p(h.A.to_numpy() / scale) - h.Mhat.to_numpy()) ** 2
                        )
                        parts = run.reduced(
                            torch.from_numpy(f.Mhat.to_numpy().reshape(-1, 20)[ix]),
                            a[ix],
                            days[ix],
                            phases["phases"]["restricted"],
                        )
                        entry["hybrid_diagnostic"] = float(parts[2])
                        entry["pair_diagnostic"] = float(parts[1])
                    metrics.append(entry)
                if not (np.ptp(z[ix], axis=1) == 0).any():
                    old = b.rank_metrics(h, arm)
                    np.testing.assert_allclose(rk["IC"], old["magnitude_IC"], atol=1e-12)
                    np.testing.assert_allclose(rk["top4"], old["top4"], atol=1e-12)
            w = b.origin_weights(days)
            centered = z - z.mean(1, keepdims=True)
            stockmean = (w[:, None] * centered).sum(0)
            temporal = (w[:, None] * (centered - stockmean) ** 2).sum(0)
            den = stockmean.var() + temporal.mean()
            dynamics.append(
                dict(
                    year=str(year),
                    arm=arm,
                    stock_static_variance=float(stockmean.var()),
                    within_stock_temporal_variance=float(temporal.mean()),
                    static_fraction=float(stockmean.var() / den) if den > 0 else 0,
                )
            )
            arank = pd.DataFrame(a).rank(axis=1).to_numpy()
            top = rr.membership(z)
            for j, ticker in enumerate(b.SYMBOLS):
                stocks.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        ticker=ticker,
                        mean_predicted_rank=float(w @ ranks[arm][:, j]),
                        mean_realized_rank=float(w @ arank[:, j]),
                        rank_MAE=float(w @ abs(ranks[arm][:, j] - arank[:, j])),
                        centered_score_mean=float(stockmean[j]),
                        centered_temporal_variance=float(temporal[j]),
                    )
                )
            for level in [95, 99]:
                event = a > phases["thresholds"][str(level)]
                for scope, take in scopes:
                    for label, mask in [("TAIL", event), ("COMPLEMENT", ~event)]:
                        mass = w[:, None] * mask * take[::20, None] / 20
                        den = mass.sum()
                        tails.append(
                            dict(
                                year=str(year),
                                arm=arm,
                                scope=scope,
                                level=level,
                                cohort=label,
                                stock_rows=int((mask & take[::20, None]).sum()),
                                weight_mass=float(den),
                                top4_event_recall=float((mass * top).sum() / den),
                                false_low_rank=float((mass * (ranks[arm] <= 10.5)).sum() / den),
                            )
                        )
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
        masks += [("calendar", "EARLY", early), ("calendar", "NORMAL", ~early)]
        masks += [("C0_decile", str(v), bins == v) for v in np.unique(bins)]
        for level in [95, 99]:
            event = f.A.gt(phases["thresholds"][str(level)]).to_numpy()
            for scope, take in scopes:
                masks += [
                    (f"tail_{scope}", f"PREFIX{level}", event & take),
                    (f"tail_{scope}", f"LE_PREFIX{level}", ~event & take),
                ]
        for arm in magarms:
            total = b.metrics(f, arm)["raw_MSE"]
            for field, label, take in masks:
                h = f.loc[take]
                if h.empty:
                    continue
                contribution = float((h.weight * (h[arm] - h.A) ** 2).sum())
                groups.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        field=field,
                        group=label,
                        **b.metrics(h, arm),
                        weight_mass=float(h.weight.sum()),
                        raw_MSE_contribution=contribution,
                        raw_MSE_loss_share=contribution / total,
                    )
                )
        for arm in allarms:
            z = f[arm].to_numpy().reshape(-1, 20)
            for field, label, take in masks:
                if field not in ["slot", "month", "calendar"]:
                    continue
                ix = take[::20]
                if ix.any():
                    rankgroups.append(
                        dict(
                            year=str(year),
                            arm=arm,
                            field=field,
                            group=label,
                            origins=int(ix.sum()),
                            sessions=len(set(days[ix])),
                            **rank_summary(a[ix], z[ix], days[ix]),
                        )
                    )
    metric = equal_year(pd.DataFrame(metrics), ["scope", "arm"])
    ranking_f = equal_year(pd.DataFrame(ranking), ["scope", "arm"])
    group = equal_year(pd.DataFrame(groups), ["arm", "field", "group"])
    for ix, row in group.loc[group.year.eq("EQ")].iterrows():
        total = metric.loc[
            metric.year.eq("EQ") & metric.arm.eq(row.arm) & metric.scope.eq("FULL"), "raw_MSE"
        ].iloc[0]
        group.loc[ix, "raw_MSE_loss_share"] = row.raw_MSE_contribution / total
    for name, frame in [
        ("metrics", metric),
        ("ranking_metrics", ranking_f),
        ("groups", group),
        ("rank_groups", equal_year(pd.DataFrame(rankgroups), ["arm", "field", "group"])),
        ("stock_diagnostics", equal_year(pd.DataFrame(stocks), ["arm", "ticker"])),
        ("tail_retrieval", equal_year(pd.DataFrame(tails), ["arm", "scope", "level", "cohort"])),
        ("score_dynamics", equal_year(pd.DataFrame(dynamics), ["arm"])),
        ("fit_summary", pd.DataFrame(fits)),
        ("rank_path_checks", pd.DataFrame(paths)),
        ("calibration_coefficients", pd.concat(coefs, ignore_index=True)),
    ]:
        frame.to_csv(out / f"{name}.csv", index=False)
    paired = []
    for left, right in [(run.CAL, "CLOCK-C3"), (run.CAL, "S2C-C3"), (run.RAW, "CLOCK-RAW")]:
        for scope in ["FULL", "INTRADAY", "OVERNIGHT"]:
            for key in ["raw_MSE", "IC", "pair_concordance", "top4"]:
                months = {}
                for year, f in frames.items():
                    take = (
                        np.ones(len(f), bool)
                        if scope == "FULL"
                        else f.category.eq(scope).to_numpy()
                    )
                    if key == "raw_MSE":
                        h = f.loc[take]
                        d = (
                            pd.DataFrame(
                                dict(
                                    day=h.session_date_et,
                                    numerator=h.weight
                                    * ((h[left] - h.A) ** 2 - (h[right] - h.A) ** 2),
                                    mass=h.weight,
                                )
                            )
                            .groupby("day")
                            .sum()
                        )
                    else:
                        a = origin_tables[(year, left)].loc[take[::20]]
                        v = origin_tables[(year, right)].loc[take[::20]]
                        delta = (
                            pd.DataFrame(dict(day=a.day, delta=a[key] - v[key]))
                            .groupby("day")
                            .delta.mean()
                        )
                        d = pd.DataFrame(dict(numerator=delta, mass=np.ones(len(delta))))
                    months[year] = d
                for rec in previous.paired_months(months):
                    source = metric if key == "raw_MSE" else ranking_f
                    ref = float(
                        source.loc[
                            source.year.eq(rec["year"])
                            & source.arm.eq(right)
                            & source.scope.eq(scope),
                            key,
                        ].iloc[0]
                    )
                    paired.append(
                        dict(
                            left=left,
                            right=right,
                            scope=scope,
                            metric=key,
                            **rec,
                            percent=100 * rec["delta"] / ref,
                            interval_includes_zero=rec["low"] <= 0 <= rec["high"],
                        )
                    )
    pd.DataFrame(paired).to_csv(out / "paired_comparisons.csv", index=False)
    b.write(
        out / "report_receipt.json",
        dict(
            completed_folds=years,
            full_equalyear=len(years) == 4,
            sources="saved predictions only",
            new_fits=0,
            calibration_fits=0,
            bootstrap_draws=400,
            seed=22042,
        ),
    )


if __name__ == "__main__":
    report()
