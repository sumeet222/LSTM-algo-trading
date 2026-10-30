"""Matched saved-score classical benchmark reporting; no fitting or inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import hf20_classical as run
from . import hf20_mag_rank_report as rr
from . import hf20_overnight_specialist as previous
from .hf20_mag_hybrid_report import equal_year, rank_summary

b, c3, clock = run.b, run.c3, run.clock


def report() -> None:
    """Replay the fixed four-fold magnitude/ranking/group/month-block comparisons."""
    assert b.read(run.OUT / "run_receipt.json")["status"] == "COMPLETE_WITH_B3_BLOCKED"
    _, rows = b.metadata()
    plans = clock.saved_plans(rows)
    metrics, groups, tails, dynamics, rankgroups, stocks = [], [], [], [], [], []
    frames, origin_tables = {}, {}
    newarms = [a + suffix for a in run.ARMS for suffix in ["-UNCAL", "-CAL"]]
    refs = [
        "CLOCK-C3",
        "CLOCK-RAW",
        "S2C-C3",
        "S2C-RAW",
        "S5C-C3",
        "S5C-RAW",
        "C0",
        "C3",
        "C1a",
        "M1",
        "B0-VOL",
        "B0-CLOCK",
        "B0-RMEAN",
        "B0-RMED",
    ]
    arms = newarms + refs
    for year in b.YEARS:
        old = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        f = old.copy()
        f["C3"] = previous.frozen_c3(old, year)
        for root, names in [
            (clock.OUT / "s2b_clock", ["CLOCK-RAW", "CLOCK-C3"]),
            (run.S2C, ["S2C-RAW", "S2C-C3"]),
            (run.HYBRID, ["S5C-RAW", "S5C-C3"]),
            (run.OUT, newarms),
        ]:
            scores = pd.read_parquet(root / f"F{year % 100}/oos_scores.parquet")
            pd.testing.assert_frame_equal(
                scores[[*c3.META, "A"]], old[[*c3.META, "A"]], check_dtype=False
            )
            for name in names:
                f[name] = scores[name]
        assert np.isfinite(f[arms].to_numpy()).all() and (f[arms].to_numpy() >= 0).all()
        frames[year] = f
        a = f.A.to_numpy().reshape(-1, 20)
        days = f.session_date_et.iloc[::20].to_numpy()
        ow = b.origin_weights(days)
        early = np.repeat(~rows.iloc[plans[year]["oos"]].regular_session.to_numpy(bool), 20)
        phases = b.read(c3.O1 / f"F{year % 100}/phases.json")
        scopes = [("FULL", np.ones(len(f), bool))] + [
            (v, f.category.eq(v).to_numpy()) for v in c3.GROUPS
        ]
        cuts = np.unique(
            [b.quantile(f.C0.to_numpy(), q, f.weight.to_numpy()) for q in np.arange(0.1, 1, 0.1)]
        )
        bins = np.searchsorted(cuts, f.C0, side="left") + 1
        masks = [("slot", v, f.slot.eq(v).to_numpy()) for v in b.SLOTS]
        masks += [("stock", v, f.ticker.eq(v).to_numpy()) for v in b.SYMBOLS]
        masks += [
            ("month", v, f.session_date_et.str[:7].eq(v).to_numpy())
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
        for arm in arms:
            z = f[arm].to_numpy().reshape(-1, 20)
            ranks = pd.DataFrame(z).rank(axis=1).to_numpy()
            vals = pd.DataFrame(rr.origin_metrics(a, z))
            vals["day"] = days
            origin_tables[(year, arm)] = vals
            for scope, take in scopes:
                ix = take[::20]
                rk = rank_summary(a[ix], z[ix], days[ix])
                metrics.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        scope=scope,
                        **b.metrics(f.loc[take], arm),
                        **rk,
                        zero_forecast_rate=float(
                            np.average((z[ix] == 0).ravel(), weights=f.loc[take].weight.to_numpy())
                        ),
                    )
                )
                if not (np.ptp(z[ix], axis=1) == 0).any():
                    np.testing.assert_allclose(
                        rk["IC"], b.rank_metrics(f.loc[take], arm)["magnitude_IC"], atol=1e-12
                    )
            centered = z - z.mean(1, keepdims=True)
            stockmean = (ow[:, None] * centered).sum(0)
            temporal = (ow[:, None] * (centered - stockmean) ** 2).sum(0)
            den = stockmean.var() + temporal.mean()
            dynamics.append(
                dict(
                    year=str(year),
                    arm=arm,
                    static_variance=float(stockmean.var()),
                    temporal_variance=float(temporal.mean()),
                    static_fraction=float(stockmean.var() / den) if den > 0 else 0,
                )
            )
            arank = pd.DataFrame(a).rank(axis=1).to_numpy()
            for j, ticker in enumerate(b.SYMBOLS):
                stocks.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        ticker=ticker,
                        mean_predicted_rank=float(ow @ ranks[:, j]),
                        mean_realized_rank=float(ow @ arank[:, j]),
                        rank_MAE=float(ow @ abs(ranks[:, j] - arank[:, j])),
                        temporal_variance=float(temporal[j]),
                    )
                )
            top = rr.membership(z)
            for level in [95, 99]:
                event = a > phases["thresholds"][str(level)]
                for scope, take in scopes:
                    mass = ow[:, None] * event * take[::20, None] / 20
                    if mass.sum():
                        tails.append(
                            dict(
                                year=str(year),
                                arm=arm,
                                scope=scope,
                                level=level,
                                rows=int((event & take[::20, None]).sum()),
                                top4_event_recall=float((mass * top).sum() / mass.sum()),
                                false_low_rank=float((mass * (ranks <= 10.5)).sum() / mass.sum()),
                            )
                        )
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
                if field in ["slot", "month", "calendar"]:
                    ix = take[::20]
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
        for arm in run.ARMS:
            raw = f[arm + "-UNCAL"].to_numpy().reshape(-1, 20)
            cal = f[arm + "-CAL"].to_numpy().reshape(-1, 20)
            if np.any(cal):
                np.testing.assert_array_equal(
                    pd.DataFrame(raw).rank(axis=1), pd.DataFrame(cal).rank(axis=1)
                )
    metric = equal_year(pd.DataFrame(metrics), ["scope", "arm"])
    group = equal_year(pd.DataFrame(groups), ["arm", "field", "group"])
    for ix, row in group.loc[group.year.eq("EQ")].iterrows():
        total = metric.loc[
            metric.year.eq("EQ") & metric.arm.eq(row.arm) & metric.scope.eq("FULL"), "raw_MSE"
        ].iloc[0]
        group.loc[ix, "raw_MSE_loss_share"] = row.raw_MSE_contribution / total
    for name, frame in [
        ("metrics", metric),
        ("groups", group),
        ("rank_groups", equal_year(pd.DataFrame(rankgroups), ["arm", "field", "group"])),
        ("tail_retrieval", equal_year(pd.DataFrame(tails), ["arm", "scope", "level"])),
        ("stock_diagnostics", equal_year(pd.DataFrame(stocks), ["arm", "ticker"])),
        ("score_dynamics", equal_year(pd.DataFrame(dynamics), ["arm"])),
    ]:
        frame.to_csv(run.OUT / f"{name}.csv", index=False)
    comparisons = []
    for arm in run.ARMS:
        comparisons += [
            (arm + "-CAL", ref)
            for ref in ["CLOCK-C3", "S2C-C3", "S5C-C3", "ROLL20-CAL"]
            if arm + "-CAL" != ref
        ]
        comparisons += [
            (arm + "-UNCAL", ref)
            for ref in ["CLOCK-RAW", "S2C-RAW", "S5C-RAW", "ROLL20-UNCAL"]
            if arm + "-UNCAL" != ref
        ]
        comparisons += [(arm + "-CAL", arm + "-UNCAL")]
    paired = []
    for left, right in comparisons:
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
                    ref = float(
                        metric.loc[
                            metric.year.eq(rec["year"])
                            & metric.arm.eq(right)
                            & metric.scope.eq(scope),
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
                            percent=100 * rec["delta"] / ref if ref else np.nan,
                        )
                    )
    pd.DataFrame(paired).to_csv(run.OUT / "paired_differences.csv", index=False)
    gains = []
    for row in metric.loc[metric.scope.eq("FULL")].to_dict("records"):
        prior = metric.loc[
            metric.year.eq(row["year"]) & metric.arm.eq("B0-RMEAN") & metric.scope.eq("FULL")
        ].iloc[0]
        gains.append(
            dict(
                year=row["year"],
                arm=row["arm"],
                MSE_gain_vs_static=float(prior.raw_MSE - row["raw_MSE"]),
                IC_gain_vs_static=float(row["IC"] - prior.IC),
            )
        )
    pd.DataFrame(gains).to_csv(run.OUT / "static_prior_gains.csv", index=False)
    b.write(
        run.OUT / "report_receipt.json",
        dict(
            status="COMPLETE_WITH_GARCH_BLOCKED",
            folds=4,
            rows=80260,
            origins=4013,
            sessions=793,
            paired_draws=400,
            seed=22042,
            model_fits_in_report=0,
            calibration_fits_in_report=0,
            **run.resources(),
        ),
    )
