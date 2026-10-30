"""Matched saved-score classical benchmark reporting; no fitting or inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import hf20_mag_rank_report as rr
from . import hf20_matched as run
from . import hf20_overnight_specialist as previous
from .hf20_mag_hybrid_report import equal_year, rank_summary

b, c3, clock = run.b, run.c3, run.old.clock


def report() -> None:
    """Replay the fixed four-fold magnitude/ranking/group/month-block comparisons."""
    run.preservation()
    receipt = b.read(run.OUT / "calibration_receipt.json")
    assert receipt["status"] == "COMPLETE"
    bases = receipt["bases"]
    _, rows = b.metadata()
    plans = clock.saved_plans(rows)
    metrics, groups, tails, dynamics, rankgroups, stocks = [], [], [], [], [], []
    frames, origin_tables = {}, {}
    newarms = [f"MATCH-{name}-{family}" for name in bases for family in ["G", "IO"]]
    refs = [name + "-UNCAL" for name in bases]
    refs += [name + "-CAL" for name in run.old.ARMS]
    refs += [
        "CLOCK-C3",
        "S2C-C3",
        "S5C-C3",
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
        f = pd.read_parquet(run.OUT / f"F{year % 100}/oos_scores.parquet")
        pd.testing.assert_frame_equal(f[[*c3.META, "A"]], old[[*c3.META, "A"]], check_dtype=False)
        f["C3"] = previous.frozen_c3(old, year)
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
        # Coverage cohorts replay the saved RV missingness, never rebuild raw minutes.
        rv = (
            pd.read_parquet(run.old.OUT / "daily_rv.parquet")
            .pivot(index="session_date_et", columns="ticker", values="rv")
            .reindex(columns=b.SYMBOLS)
        )
        ends = np.searchsorted(rv.index.to_numpy(), days, side="left")
        assert (ends >= 22).all()
        missing = ~np.isfinite(rv.to_numpy()[ends[:, None] - np.arange(1, 23)])
        any_missing = missing.any(1).ravel()
        masks += [
            ("RV_22day_coverage", "ANY_MISSING", any_missing),
            ("RV_22day_coverage", "COMPLETE", ~any_missing),
        ]
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
        for arm in run.old.ARMS:
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
    classical = [n for n in bases if n not in run.NEURAL]
    for family in ["G", "IO"]:
        comparisons += [
            (f"MATCH-{n}-{family}", f"MATCH-{ref}-{family}")
            for n in classical
            for ref in run.NEURAL
        ]
    comparisons += [(f"MATCH-{n}-IO", f"MATCH-{n}-G") for n in bases]
    comparisons += [(n + "-CAL", ref + "-C3") for n in run.old.ARMS for ref in run.NEURAL]
    comparisons += [(n + "-UNCAL", ref + "-UNCAL") for n in classical for ref in run.NEURAL]
    if "GARCH11-FN" in bases:
        comparisons += [
            (f"MATCH-GARCH11-FN-{family}", ref + "-C3")
            for family in ["G", "IO"]
            for ref in run.NEURAL
        ]
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
            status="COMPLETE",
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


def verify() -> None:
    """Independent coefficient arithmetic and all archived annual score parity."""
    from .hf20_matched_math import apply_common

    bindings = run.preservation()
    coef = pd.read_csv(run.OUT / "calibration_coefficients.csv", float_precision="round_trip")
    receipt = b.read(run.OUT / "calibration_receipt.json")
    checks = []
    for year in b.YEARS:
        cal = pd.read_parquet(run.OUT / f"F{year % 100}/calibration_scores.parquet")
        oos = pd.read_parquet(run.OUT / f"F{year % 100}/oos_scores.parquet")
        for name in receipt["bases"]:
            p = cal[name + "-UNCAL"].to_numpy()
            a = cal.A.to_numpy()
            w = cal.weight.to_numpy()
            global_k = float(np.sum(w * a * p) / np.sum(w * p * p))
            co = coef.loc[(coef.year == year) & (coef.model == name)].to_dict("records")
            for c in co:
                if c["family"] == "G":
                    expected = max(0, global_k)
                else:
                    take = cal.category.eq(c["group"]).to_numpy()
                    raw = float(
                        np.sum(w[take] * a[take] * p[take]) / np.sum(w[take] * p[take] ** 2)
                    )
                    mass = cal.loc[take].groupby("session_date_et").weight.sum().to_numpy()
                    n = float(mass.sum() ** 2 / (mass @ mass))
                    rho = n / (n + 25)
                    np.testing.assert_allclose(c["n_eff"], n, rtol=1e-13)
                    expected = rho * max(0, raw) + (1 - rho) * max(0, global_k)
                np.testing.assert_allclose(c["k"], expected, rtol=1e-13, atol=1e-15)
            for family in ["G", "IO"]:
                arm = f"MATCH-{name}-{family}"
                for f in [cal, oos]:
                    np.testing.assert_allclose(
                        f[arm], apply_common(f, name + "-UNCAL", co, family), rtol=1e-13, atol=1e-15
                    )
                for metric in ["IC", "pair_concordance", "top4", "bottom4"]:
                    raw = rr.origin_metrics(
                        oos.A.to_numpy().reshape(-1, 20),
                        oos[name + "-UNCAL"].to_numpy().reshape(-1, 20),
                    )[metric]
                    matched = rr.origin_metrics(
                        oos.A.to_numpy().reshape(-1, 20), oos[arm].to_numpy().reshape(-1, 20)
                    )[metric]
                    np.testing.assert_allclose(raw, matched, rtol=0, atol=1e-15)
            checks.append(dict(year=year, model=name, coefficients=True, rank_parity=True))
    old = pd.read_csv(
        run.old.OUT / "metrics.csv", float_precision="round_trip", dtype={"year": str}
    )
    new = pd.read_csv(run.OUT / "metrics.csv", float_precision="round_trip", dtype={"year": str})
    count = 0
    for rec in old.to_dict("records"):
        arm = rec["arm"].replace("-RAW", "-UNCAL")
        match = new.loc[(new.year == rec["year"]) & (new.arm == arm) & (new.scope == rec["scope"])]
        if match.empty:
            continue
        for key in [
            "raw_MSE",
            "raw_MAE",
            "IC",
            "top4",
            "pair_concordance",
            "predicted",
            "observed",
        ]:
            np.testing.assert_allclose(match.iloc[0][key], rec[key], rtol=1e-11, atol=1e-14)
        count += 1
    new.loc[new.year != "EQ"].to_csv(run.OUT / "annual_metrics.csv", index=False)
    b.write(
        run.OUT / "verification.json",
        dict(
            status="PASS",
            preserved_bindings=bindings,
            coefficient_and_rank_checks=checks,
            archived_metric_rows_replayed=count,
            expected_archived_metric_rows=len(old),
            neural_starts=0,
            ledger=186,
            no_model_or_calibration_fits=True,
            **run.resources(),
        ),
    )
    assert count == len(old)
