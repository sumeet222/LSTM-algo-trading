"""Saved-score Stage5 magnitude-ranking assessment; never decode rank scores."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch

from . import hf20_mag_rank as run
from . import hf20_overnight_specialist as prev

b, c3, clock = run.b, run.c3, run.clock


def membership(x: np.ndarray, high: bool = True) -> np.ndarray:
    """Fractional boundary ties with exactly four expected members per origin."""
    f = pd.DataFrame(x if high else -x)
    first = f.rank(axis=1, method="min", ascending=False).to_numpy()
    last = f.rank(axis=1, method="max", ascending=False).to_numpy()
    return np.clip((5 - first) / (last - first + 1), 0, 1)


def origin_metrics(a: np.ndarray, z: np.ndarray) -> dict[str, np.ndarray]:
    """Original rank conventions plus conservative constant IC and score diagnostics."""
    sign = np.sign(a[:, run.PAIR_I] - a[:, run.PAIR_J])
    pred = np.sign(z[:, run.PAIR_I] - z[:, run.PAIR_J])
    valid = sign != 0
    q = run.targets(a)
    qr = run.targets(pd.DataFrame(z).rank(axis=1).to_numpy())
    ic = run.conservative_ic(a, z)
    constant = np.ptp(z, axis=1) == 0
    return dict(
        IC=ic,
        historical_IC=np.where(constant, np.nan, ic),
        pair_concordance=(((sign * pred > 0) + 0.5 * (pred == 0)) * valid).sum(1) / valid.sum(1),
        top4=(membership(a) * membership(z)).sum(1) / 4,
        bottom4=(membership(a, False) * membership(z, False)).sum(1) / 4,
        rank_discrepancy=((qr - q) ** 2).mean(1),
        tie_rate=(pred == 0).mean(1),
        true_tie_rate=(sign == 0).mean(1),
        constant_rate=constant.astype(float),
        score_spread=z.std(1),
        common_offset=z.mean(1),
        common_offset_squared=z.mean(1) ** 2,
        centered_score_variance=z.var(1),
    )


def reduce(frame: pd.DataFrame) -> dict:
    """Equal origins within each retained session, then equal sessions."""
    numeric = frame.select_dtypes(include="number").columns
    means = frame.groupby("day")[list(numeric)].mean().mean()
    return {str(k): float(v) for k, v in means.items()}


def equal_year(f: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows = []
    for labels, g in f.groupby(keys, sort=False):
        if g.year.nunique() != 4:
            continue
        labels = labels if isinstance(labels, tuple) else (labels,)
        row = dict(zip(keys, labels))
        row["year"] = "EQ"
        for col in g.select_dtypes(include="number").columns:
            if col != "year":
                row[col] = float(
                    g[col].sum()
                    if col in ["rows", "origins", "sessions", "undefined_IC_origins"]
                    else g[col].mean()
                )
        rows.append(row)
    return pd.concat([f, pd.DataFrame(rows)], ignore_index=True)


def report() -> None:
    out = run.OUT
    records = []
    groups = []
    stocks = []
    events = []
    dynamics = []
    tables = {}
    fits = []
    grid, rows = b.metadata()
    plans = run.validate_roles(grid, rows)
    for year in b.YEARS:
        old = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        refs = {
            k: old[k].to_numpy().reshape(-1, 20)
            for k in ["C0", "M1", "B0-VOL", "B0-CLOCK", "B0-RMEAN"]
        }
        refs["C3"] = prev.frozen_c3(old, year).reshape(-1, 20)
        for name, root in [
            ("CLOCK-C3", clock.OUT / "s2b_clock"),
            ("S2C-C3", Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28")),
        ]:
            f = pd.read_parquet(root / f"F{year % 100}/oos_scores.parquet")
            pd.testing.assert_frame_equal(
                f[[*c3.META, "A"]], old[[*c3.META, "A"]], check_dtype=False
            )
            refs[name] = f[name].to_numpy().reshape(-1, 20)
        refs["CONSTANT0"] = np.zeros_like(refs["C0"])
        for arm in ["LINEAR", "S5A", "S5B"]:
            d = out / arm / f"F{year % 100}"
            if not (d / "result.json").exists():
                continue
            result = b.read(d / "result.json")
            if result["status"] != "COMPLETED":
                continue
            fits.append(
                dict(
                    arm=arm,
                    year=year,
                    **{k: v for k, v in result.items() if k not in ["arm", "year", "resources"]},
                )
            )
            f = pd.read_parquet(d / "oos_scores.parquet")
            pd.testing.assert_frame_equal(
                f[[*c3.META, "A"]], old[[*c3.META, "A"]], check_dtype=False
            )
            refs[arm] = f.score.to_numpy().reshape(-1, 20)
        a = old.A.to_numpy().reshape(-1, 20)
        meta = old.iloc[::20].reset_index(drop=True)
        days = meta.session_date_et.to_numpy()
        w = b.origin_weights(days)
        early = ~rows.iloc[plans[year]["oos"]].regular_session.to_numpy(bool)
        thresholds = b.read(run.o1.OUT / f"F{year % 100}/phases.json")["thresholds"]
        for arm, z in refs.items():
            assert z.shape == a.shape and np.isfinite(z).all()
            values = origin_metrics(a, z)
            o = pd.DataFrame(values)
            o["day"] = days
            if arm == "S5A":
                o["objective_loss"] = ((z - run.targets(a)) ** 2).mean(1)
                o["centered_rank_MSE"] = (
                    (z - z.mean(1, keepdims=True) - run.targets(a)) ** 2
                ).mean(1)
                np.testing.assert_allclose(
                    o.objective_loss,
                    o.common_offset_squared + o.centered_rank_MSE,
                    rtol=1e-6,
                    atol=1e-8,
                )
            elif arm == "S5B":
                o["objective_loss"] = run.origin_loss(
                    torch.from_numpy(z), torch.from_numpy(run.preferences(a)), "S5B"
                ).numpy()
            elif arm == "LINEAR":
                o["objective_loss"] = ((z - run.targets(a)) ** 2).mean(1)
            tables[(year, arm)] = o
            for scope, take in [
                ("FULL", np.ones(len(a), bool)),
                ("INTRADAY", meta.category.eq("INTRADAY").to_numpy()),
                ("OVERNIGHT", meta.category.eq("OVERNIGHT").to_numpy()),
            ]:
                h = o.loc[take]
                records.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        scope=scope,
                        rows=len(h) * 20,
                        origins=len(h),
                        sessions=h.day.nunique(),
                        undefined_IC_origins=int(h.historical_IC.isna().sum()),
                        **reduce(h),
                    )
                )
                if arm != "CONSTANT0" and not (np.ptp(z[take], axis=1) == 0).any():
                    f = old.loc[np.repeat(take, 20)].copy()
                    f["rank_score"] = z[take].ravel()
                    historical = b.rank_metrics(f, "rank_score")
                    for k in ["pair_concordance", "top4", "bottom4", "tie_rate", "constant_rate"]:
                        np.testing.assert_allclose(reduce(h)[k], historical[k], atol=1e-12)
                    np.testing.assert_allclose(
                        reduce(h)["IC"], historical["magnitude_IC"], atol=1e-12
                    )
            masks = [("slot", slot, meta.slot.eq(slot).to_numpy()) for slot in b.SLOTS]
            masks += [
                ("month", month, meta.session_date_et.str[:7].eq(month).to_numpy())
                for month in sorted(meta.session_date_et.str[:7].unique())
            ]
            masks += [("calendar", "EARLY", early), ("calendar", "NORMAL", ~early)]
            for field, label, take in masks:
                h = o.loc[take]
                if len(h):
                    groups.append(
                        dict(
                            year=str(year),
                            arm=arm,
                            field=field,
                            group=label,
                            origins=len(h),
                            sessions=h.day.nunique(),
                            **reduce(h),
                        )
                    )
            rankz = pd.DataFrame(z).rank(axis=1).to_numpy()
            ranka = pd.DataFrame(a).rank(axis=1).to_numpy()
            top = membership(z)
            bottom = membership(z, False)
            centered = z - z.mean(1, keepdims=True)
            stockmean = (w[:, None] * centered).sum(0)
            temporal = (w[:, None] * (centered - stockmean) ** 2).sum(0)
            dynamics.append(
                dict(
                    year=str(year),
                    arm=arm,
                    stock_static_variance=float(stockmean.var()),
                    within_stock_temporal_variance=float(temporal.mean()),
                    static_fraction=float(stockmean.var() / (stockmean.var() + temporal.mean()))
                    if stockmean.var() + temporal.mean() > 0
                    else 0,
                )
            )
            for j, ticker in enumerate(b.SYMBOLS):
                stocks.append(
                    dict(
                        year=str(year),
                        arm=arm,
                        ticker=ticker,
                        origins=len(a),
                        mean_predicted_rank=float(w @ rankz[:, j]),
                        mean_realized_rank=float(w @ ranka[:, j]),
                        rank_MAE=float(w @ abs(rankz[:, j] - ranka[:, j])),
                        top4_retrieval_contribution=float(w @ (top[:, j] * membership(a)[:, j])),
                        bottom4_retrieval_contribution=float(
                            w @ (bottom[:, j] * membership(a, False)[:, j])
                        ),
                        centered_score_mean=float(stockmean[j]),
                        centered_temporal_variance=float(temporal[j]),
                    )
                )
            for level in [95, 99]:
                event = a > thresholds[str(level)]
                for scope, take in [
                    ("FULL", np.ones(len(a), bool)),
                    ("INTRADAY", meta.category.eq("INTRADAY").to_numpy()),
                    ("OVERNIGHT", meta.category.eq("OVERNIGHT").to_numpy()),
                ]:
                    for label, mask in [("TAIL", event), ("COMPLEMENT", ~event)]:
                        mass = w[:, None] * mask * take[:, None] / 20
                        den = mass.sum()
                        events.append(
                            dict(
                                year=str(year),
                                arm=arm,
                                scope=scope,
                                level=level,
                                cohort=label,
                                stock_rows=int((mask & take[:, None]).sum()),
                                weight_mass=float(den),
                                top4_event_recall=float((mass * top).sum() / den),
                                false_low_rank=float((mass * (rankz <= 10.5)).sum() / den),
                            )
                        )
    metric = equal_year(pd.DataFrame(records), ["arm", "scope"])
    group = equal_year(pd.DataFrame(groups), ["arm", "field", "group"])
    stock = equal_year(pd.DataFrame(stocks), ["arm", "ticker"])
    event = equal_year(pd.DataFrame(events), ["arm", "scope", "level", "cohort"])
    dynamic = equal_year(pd.DataFrame(dynamics), ["arm"])
    # Rank-only outputs have no MAG amplitude interpretation; explicit N/A, never zeros.
    metric["raw_A_MSE"] = "N/A"
    metric["A_MAE"] = "N/A"
    metric["MAG_calibration"] = "N/A"
    metric.to_csv(out / "ranking_metrics.csv", index=False)
    group.to_csv(out / "groups.csv", index=False)
    stock.to_csv(out / "stock_diagnostics.csv", index=False)
    event.to_csv(out / "tail_retrieval.csv", index=False)
    dynamic.to_csv(out / "score_dynamics.csv", index=False)
    pd.DataFrame(fits).to_csv(out / "fit_summary.csv", index=False)
    paired = []
    for arm in ["S5A", "S5B", "LINEAR"]:
        for ref in ["CLOCK-C3", "S2C-C3", "B0-RMEAN", "LINEAR"]:
            if arm == ref:
                continue
            for scope in ["FULL", "INTRADAY", "OVERNIGHT"]:
                for key in ["IC", "pair_concordance", "top4"]:
                    months = {}
                    for year in b.YEARS:
                        if (year, arm) not in tables or (year, ref) not in tables:
                            continue
                        o = tables[(year, arm)]
                        v = tables[(year, ref)]
                        meta = rows.iloc[plans[year]["oos"]]
                        take = (
                            np.ones(len(o), bool)
                            if scope == "FULL"
                            else meta.category.eq(scope).to_numpy()
                        )
                        d = (
                            pd.DataFrame(
                                {
                                    "day": o.loc[take, "day"],
                                    "delta": o.loc[take, key] - v.loc[take, key],
                                }
                            )
                            .groupby("day")
                            .delta.mean()
                        )
                        months[year] = pd.DataFrame({"numerator": d, "mass": np.ones(len(d))})
                    if months:
                        for rec in prev.paired_months(months):
                            paired.append(
                                dict(
                                    arm=arm,
                                    reference=ref,
                                    scope=scope,
                                    metric=key,
                                    **rec,
                                    interval_includes_zero=rec["low"] <= 0 <= rec["high"],
                                )
                            )
    pd.DataFrame(paired).to_csv(out / "paired_ranking.csv", index=False)
    for arm in ["S5A", "S5B"]:
        annual = metric.loc[
            metric.scope.eq("FULL")
            & metric.arm.isin(
                [
                    arm,
                    "CLOCK-C3",
                    "S2C-C3",
                    "C0",
                    "C3",
                    "M1",
                    "B0-VOL",
                    "B0-CLOCK",
                    "B0-RMEAN",
                    "LINEAR",
                    "CONSTANT0",
                ]
            )
        ]
        complete = sum((y, arm) in tables for y in b.YEARS)
        text = (
            f"# {arm}: absolute-four-hour magnitude ranking\n\nExecution: {complete}/4 folds. "
            "Scores are dimensionless; magnitude MSE/MAE/calibration N/A. "
            "Scientific verdict is finalized in the combined report.\n\n"
            + b.markdown(
                annual[
                    [
                        "year",
                        "arm",
                        "IC",
                        "historical_IC",
                        "pair_concordance",
                        "top4",
                        "bottom4",
                        "rank_discrepancy",
                        "tie_rate",
                        "constant_rate",
                    ]
                ]
            )
            + "\n\nRepeatedly studied 2021–24; 400 whole-month descriptive intervals, "
            "seed22042, not selection-adjusted. Oct–Dec unused; no trading or MAG calibration.\n"
        )
        (out / arm / f"{arm}_REPORT.md").write_text(text)


if __name__ == "__main__":
    report()
