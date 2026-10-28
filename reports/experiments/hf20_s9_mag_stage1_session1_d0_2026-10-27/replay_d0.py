"""S9-MAG Session 1: explicit saved-artifact reads and descriptive arithmetic only.

Run from repository root. No model imports, fits, inference, acquisition or source
reconstruction. Writes only two aggregate CSVs and the report in this directory.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

S9 = Path("reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation")
S4 = Path("reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation")
OUT = Path(__file__).resolve().parent
YEARS = (2021, 2022, 2023, 2024)
KEY = ["origin_id", "ticker"]
READS: list[str] = []


def js(path: Path) -> dict:
    """Read one explicitly named historical recipe/binding; never discover stores."""
    READS.append(str(path))
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    """Only call on explicitly named pre-2025 score/recipe files."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv(path: Path) -> pd.DataFrame:
    READS.append(str(path))
    return pd.read_csv(path)


def scores(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    READS.append(str(path))
    return pd.read_parquet(path, columns=columns)


def close(a: np.ndarray | pd.Series | float, b: np.ndarray | pd.Series | float) -> None:
    np.testing.assert_allclose(
        np.asarray(a, dtype=float), np.asarray(b, dtype=float), atol=1e-12, rtol=1e-11
    )


def weighted_quantile(v: np.ndarray, w: np.ndarray, q: float) -> float:
    """Diagnostic weighted empirical quantile; identical to archived quantile rule."""
    ix = np.argsort(v, kind="stable")
    k = min(int(np.searchsorted(np.cumsum(w[ix]) / w.sum(), q)), len(v) - 1)
    return float(v[ix[k]])


def summary(g: pd.DataFrame) -> dict:
    """Condition original role weights on group, normalize per year, equal years."""
    w = g.weight.to_numpy(float) / g.groupby("year").weight.transform("sum").to_numpy()
    w /= g.year.nunique()
    a, p, m, z = (g[k].to_numpy(float) for k in ("A", "prediction_A", "M", "raw_0"))
    e, residual = p - a, m - z

    def avg(x: np.ndarray) -> float:
        return float(w @ x)

    return dict(
        rows=len(g),
        origins=g.origin_id.nunique(),
        sessions=g.session_date_et.nunique(),
        years=g.year.nunique(),
        observed=avg(a),
        predicted=avg(p),
        bias=avg(e),
        absolute_bias=abs(avg(e)),
        ratio=avg(p) / avg(a),
        raw_MAE=avg(abs(e)),
        raw_MSE=avg(e * e),
        transformed_MSE=avg(residual * residual),
        M_residual=avg(residual),
        M_residual_sd=float(np.sqrt(avg((residual - avg(residual)) ** 2))),
        M_residual_p95=weighted_quantile(residual, w, 0.95),
        M_residual_p99=weighted_quantile(residual, w, 0.99),
        forecast_min=float(p.min()),
        forecast_max=float(p.max()),
        negative_Mhat=avg(z < 0),
        zero_forecast=avg(p == 0),
    )


def rank_association(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    """Historical annual all-row midranks, then weighted Pearson of those ranks."""
    x, y = (pd.Series(v).rank(method="average").to_numpy(float) for v in (a, b))
    x, y = x - w @ x, y - w @ y
    return float((w @ (x * y)) / np.sqrt((w @ (x * x)) * (w @ (y * y))))


def ranking(f: pd.DataFrame, model: str) -> dict:
    """20-stock within-origin magnitude ordering; fractional boundary-tie retrieval."""
    a = f.A.to_numpy().reshape(-1, 20)
    p = f.prediction_A.to_numpy().reshape(-1, 20)
    ra, rp = (pd.DataFrame(v).rank(axis=1, method="average").to_numpy() for v in (a, p))
    x, y = ra - ra.mean(1)[:, None], rp - rp.mean(1)[:, None]
    den = np.sqrt((x * x).sum(1) * (y * y).sum(1))
    ic = np.divide((x * y).sum(1), den, out=np.full(len(x), np.nan), where=den > 0)
    i, j = np.triu_indices(20, 1)
    ad, pdiff = np.sign(a[:, i] - a[:, j]), np.sign(p[:, i] - p[:, j])
    valid = ad != 0
    concordance = ((ad * pdiff > 0) + 0.5 * (pdiff == 0)) * valid
    pair = concordance.sum(1) / valid.sum(1)

    def membership(v: np.ndarray, high: bool) -> np.ndarray:
        d = pd.DataFrame(v if high else -v)
        first = d.rank(axis=1, method="min", ascending=False).to_numpy()
        last = d.rank(axis=1, method="max", ascending=False).to_numpy()
        return np.clip((5 - first) / (last - first + 1), 0, 1)

    top, bottom = [(membership(a, high) * membership(p, high)).sum(1) / 4 for high in (True, False)]
    o = pd.DataFrame(
        dict(
            day=f.session_date_et.iloc[::20].to_numpy(),
            ic=ic,
            pair=pair,
            top4=top,
            bottom4=bottom,
            ties=(pdiff == 0).mean(1),
            constant=np.ptp(p, axis=1) == 0,
            undefined=~np.isfinite(ic),
        )
    )
    values = {str(k): float(v) for k, v in o.groupby("day").mean().mean().to_dict().items()}
    w = f.weight.to_numpy(float, copy=True)
    w /= w.sum()
    return dict(
        year=int(f.year.iloc[0]),
        model=model,
        historical_allrow_rank=rank_association(f.A.to_numpy(), f.prediction_A.to_numpy(), w),
        **values,
    )


def table(frame: pd.DataFrame, columns: list[str] | None = None, digits: int = 6) -> str:
    """Dependency-free Markdown; keep units/weight definitions in surrounding text."""
    frame = frame if columns is None else frame[columns]
    lines = [
        "| " + " | ".join(map(str, frame.columns)) + " |",
        "| " + " | ".join("---" for _ in frame.columns) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        cells = [f"{v:.{digits}f}" if isinstance(v, (float, np.floating)) else str(v) for v in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    """Verify exact permitted keys/recipes and summarize saved forecasts, never fit."""
    card = js(S4 / "S4_FROZEN_EXPERIMENT_CARD.json")
    symbols = card["symbols"]
    reused = json.loads((S9 / "S4_REUSED_RECIPES.json").read_text())
    READS.append(str(S9 / "S4_REUSED_RECIPES.json"))
    frames, controls, coverage, chronology, rankrows = [], [], [], [], []
    control_frames: dict[str, list[pd.DataFrame]] = {k: [] for k in ("MAG", "STOCK", "VOL")}
    recipes: dict[int, dict] = {}
    metrics_archive = csv(S9 / "S5_S9_MODEL_METRICS.csv")
    for year in YEARS:
        run = S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42"
        cfg = js(run / "configuration.json")
        assert [cfg[k] for k in ("arm", "seed", "input_dim", "hidden", "layers", "dropout")] == [
            "MAG",
            42,
            16,
            32,
            1,
            0.1,
        ]
        inner, refit = (js(run / f"{phase}_target_recipe.json") for phase in ("inner", "refit"))
        cb, rb = (js(run / f"{phase}_binding.json") for phase in ("calibration", "refit"))
        recipes[year] = refit
        for phase in ("inner", "refit"):
            path = S4 / f"F{year % 100}_{phase}_recipe.json"
            recipe = js(path)
            expected = next(x["sha256"] for x in reused if x["path"] == str(path))
            assert sha(path) == expected
            assert recipe["target_minutes"] == 240 and recipe["s4_contexts"] == 7
        f = scores(run / "oos_scores.parquet")
        assert (
            f.year.eq(year).all()
            and f.session_date_et.between(f"{year}-01-01", f"{year}-12-31").all()
        )
        assert not f.duplicated(KEY).any() and f.groupby("origin_id").size().eq(20).all()
        assert f.ticker.tolist() == symbols * f.origin_id.nunique()
        idx = csv(S4 / f"F{year % 100}_oos_indices.csv")
        origins = f.iloc[::20]
        for column in [
            "origin_id",
            "session_date_et",
            "slot",
            "category",
            "entry_end_utc",
            "exit_end_utc",
            "label_maturity_utc",
        ]:
            if column.endswith("utc"):
                np.testing.assert_array_equal(
                    pd.to_datetime(origins[column], utc=True), pd.to_datetime(idx[column], utc=True)
                )
            else:
                np.testing.assert_array_equal(origins[column], idx[column])
        assert idx.trading_minutes.eq(240).all()
        assert (
            (
                pd.to_datetime(idx.issuance_utc, utc=True)
                - pd.to_datetime(idx.entry_end_utc, utc=True)
            )
            .eq(pd.Timedelta(minutes=2))
            .all()
        )
        assert (
            (
                pd.to_datetime(f.label_maturity_utc, utc=True)
                - pd.to_datetime(f.exit_end_utc, utc=True)
            )
            .eq(pd.Timedelta(minutes=2))
            .all()
        )
        assert (
            pd.to_datetime(f.last_input_end_utc, utc=True)
            .le(pd.to_datetime(f.entry_end_utc, utc=True))
            .all()
        )
        expected_w = 1 / (
            f.session_date_et.nunique()
            * f.groupby("session_date_et").origin_id.transform("nunique")
            * 20
        )
        close(f.weight, expected_w)
        assert np.isfinite(
            f[
                [
                    "weight",
                    "raw_0",
                    "prediction_m",
                    "prediction_A",
                    "return_4h",
                    "actual_loss",
                    "sigma_proxy",
                ]
            ].to_numpy(float)
        ).all()
        close(f.raw_0, f.prediction_m)
        f["A"] = f.return_4h.abs()
        f["M"] = np.log1p(f.A / refit["magnitude_scale"])
        decoded = refit["magnitude_scale"] * np.expm1(np.maximum(f.raw_0.to_numpy(float), 0))
        close(decoded, f.prediction_A)
        close((f.M - f.raw_0) ** 2, f.actual_loss)
        for column, expected in [
            ("task_recipe_sha256", sha(run / "refit_target_recipe.json")),
            ("S4_recipe_sha256", sha(S4 / f"F{year % 100}_refit_recipe.json")),
            ("checkpoint_sha256", rb["checkpoint_sha256"]),
            ("execution_sha256", cfg["execution_sha256"]),
        ]:
            assert f[column].eq(expected).all()
        # Saved EVENT cuts are historical prefix cuts on the same saved V2 proxy.
        cutpath = S9 / f"HF20-S9-F{year % 100}-H4-EVENT-S42/refit_VOL_control.json"
        cuts = js(cutpath)["cuts"]
        f["vol_state"] = np.digitize(np.log(f.sigma_proxy), cuts).astype(str)
        f["quarter"] = pd.to_datetime(f.session_date_et).dt.to_period("Q").astype(str)
        f["prefix95"] = f.A > refit["abs_r95"]
        # Actual 20-name bottom half, with boundary ties included by midrank <=10.5.
        f["low_forecast"] = f.groupby("origin_id").prediction_A.rank(method="average").le(10.5)
        coverage.append(
            dict(
                year=year,
                rows=len(f),
                origins=f.origin_id.nunique(),
                sessions=f.session_date_et.nunique(),
                inner_scale=inner["magnitude_scale"],
                refit_scale=refit["magnitude_scale"],
                abs_r95=refit["abs_r95"],
                abs_r99=refit["abs_r99"],
                decode_max_error=float(np.max(abs(decoded - f.prediction_A))),
                negative_outputs=int(f.raw_0.lt(0).sum()),
                min_Mhat=float(f.raw_0.min()),
                max_Mhat=float(f.raw_0.max()),
            )
        )
        for model in ("MAG", "STOCK", "VOL"):
            g = f.copy()
            if model != "MAG":
                path = run / f"oos_{model}_control_scores.parquet"
                c = scores(path)
                assert not c.duplicated(KEY).any()
                np.testing.assert_array_equal(c[KEY], f[KEY])
                assert c.canonical_target_sha256.eq(sha(run / "oos_scores.parquet")).all()
                cpath = run / f"refit_{model}_control.json"
                recipe = js(cpath)
                assert c.control_recipe_sha256.eq(sha(cpath)).all()
                if model == "STOCK":
                    close(
                        c.raw_0.to_numpy().reshape(-1, 20),
                        np.broadcast_to(recipe["value"], (len(f) // 20, 20)),
                    )
                else:
                    assert recipe == {}
                    close(c.prediction_A, 2 * np.sqrt(2 / np.pi) * f.sigma_proxy)
                for k in ("raw_0", "prediction_m", "prediction_A", "actual_loss"):
                    g[k] = c[k].to_numpy()
                close(
                    g.prediction_A,
                    refit["magnitude_scale"] * np.expm1(np.maximum(g.raw_0.to_numpy(float), 0)),
                )
                close(g.actual_loss, (g.M - g.raw_0) ** 2)
            st = summary(g)
            archive = metrics_archive.loc[
                metrics_archive.arm.eq("MAG")
                & metrics_archive.role.eq("oos")
                & metrics_archive.year.eq(year)
                & metrics_archive.model.eq("NEURAL" if model == "MAG" else model)
            ]
            assert len(archive) == 1
            close(st["transformed_MSE"], archive.optimized_loss.iloc[0])
            close(st["raw_MAE"], archive.magnitude_MAE.iloc[0])
            close(st["raw_MSE"], archive.magnitude_RMSE.iloc[0] ** 2)
            rr = ranking(g, model)
            close(rr["historical_allrow_rank"], archive.magnitude_rank_association.iloc[0])
            controls.append(dict(year=year, model=model, **st))
            rankrows.append(rr)
            control_frames[model].append(
                g[
                    [
                        "year",
                        "weight",
                        "origin_id",
                        "session_date_et",
                        "A",
                        "M",
                        "prediction_A",
                        "raw_0",
                    ]
                ].copy()
            )
        # Inventory earlier prefixes only: no new performance analysis on these rows.
        for role in ("inner_train", "inner_validation", "refit"):
            p = run / f"{role}_scores.parquet"
            h = scores(
                p,
                [
                    "origin_id",
                    "ticker",
                    "session_date_et",
                    "entry_end_utc",
                    "label_maturity_utc",
                    "checkpoint_sha256",
                    "task_recipe_sha256",
                    "raw_0",
                    "return_4h",
                    "sigma_proxy",
                    "weight",
                ],
            )
            assert h.session_date_et.lt(f"{year}-01-01").all() and not h.duplicated(KEY).any()
            assert np.isfinite(
                h[["raw_0", "return_4h", "sigma_proxy", "weight"]].to_numpy(float)
            ).all()
            phase = "inner" if role.startswith("inner") else "refit"
            b = cb if phase == "inner" else rb
            assert h.checkpoint_sha256.eq(b["checkpoint_sha256"]).all()
            assert h.task_recipe_sha256.eq(sha(run / f"{phase}_target_recipe.json")).all()
            hi = csv(S4 / f"F{year % 100}_{role}_indices.csv")
            np.testing.assert_array_equal(h.origin_id.iloc[::20], hi.origin_id)
            assert (
                pd.to_datetime(h.label_maturity_utc, utc=True)
                .lt(pd.Timestamp(f"{year}-01-01", tz="UTC"))
                .all()
            )
            chronology.append(
                dict(
                    year=year,
                    role=role,
                    rows=len(h),
                    origins=h.origin_id.nunique(),
                    sessions=h.session_date_et.nunique(),
                    start=h.session_date_et.min(),
                    stop=h.session_date_et.max(),
                    last_maturity=str(h.label_maturity_utc.max()),
                    selected_epoch=b["selected"],
                    scale=(inner if phase == "inner" else refit)["magnitude_scale"],
                )
            )
        frames.append(f)

    f = pd.concat(frames, ignore_index=True)
    assert len(f) == 80260 and f.origin_id.nunique() == 4013 and f.session_date_et.nunique() == 793
    assert not f.duplicated(["year", "session_date_et", "origin_id", "ticker"]).any()
    records: list[dict[str, str | int | float]] = [
        dict(field="model", group=x["model"], **x) for x in controls
    ]
    for model in ("MAG", "STOCK", "VOL"):
        records.append(
            dict(
                field="model",
                group=model,
                year="EQ",
                model=model,
                **summary(pd.concat(control_frames[model], ignore_index=True)),
            )
        )

    def add(field: str, group: str, g: pd.DataFrame, year: str | int) -> None:
        records.append(dict(field=field, group=group, year=year, model="MAG", **summary(g)))

    for field in (
        "ticker",
        "slot",
        "category",
        "quality",
        "fallback",
        "age_band",
        "vol_state",
        "month",
        "quarter",
    ):
        for (year, group), g in f.groupby(["year", field], observed=True):
            add(field, str(group), g, str(year))
        if field not in ("month", "quarter"):
            for group, g in f.groupby(field, observed=True):
                add(field, str(group), g, "EQ")
    # Pooled cutpoints use equal-year role weights, only historical forecast values.
    # Annual bins use each year's own forecast distribution. Never future boundaries.
    for label, g0 in [("EQ", f), *[(str(y), x) for y, x in f.groupby("year")]]:
        g = g0.copy()
        w = (
            g.weight.to_numpy(float)
            / g.groupby("year").weight.transform("sum").to_numpy()
            / g.year.nunique()
        )
        cuts = np.unique(
            [weighted_quantile(g.prediction_A.to_numpy(), w, q) for q in np.arange(0.1, 1, 0.1)]
        )
        g["bin"] = np.searchsorted(cuts, g.prediction_A, side="left") + 1
        for group, h in g.groupby("bin"):
            add("forecast_bin", str(group), h, label)
    tailrows = []
    cohort_frames: dict[str, list[pd.DataFrame]] = {}
    for year, g0 in f.groupby("year"):
        g = g0.copy()
        masks = {
            "PREFIX95": g.prefix95.to_numpy(),
            "ORDINARY_LE_PREFIX95": ~g.prefix95.to_numpy(),
            "PREFIX99": g.A.gt(recipes[int(year)]["abs_r99"]).to_numpy(),
        }
        for field, vals in [
            ("REALIZED", g.A.to_numpy()),
            ("ABS_RAW_ERROR", abs(g.prediction_A - g.A).to_numpy()),
            ("TRANSFORMED_LOSS_ARCHIVE", g.actual_loss.to_numpy()),
        ]:
            for pct in (1, 5):
                mask = np.zeros(len(g), bool)
                mask[np.argsort(-vals, kind="stable")[: len(g) * pct // 100]] = True
                masks[f"{field}_TOP{pct}"] = mask
        for name, mask in masks.items():
            h = g.loc[mask]
            cohort_frames.setdefault(name, []).append(h)
            add("cohort", name, h, str(year))
            w = g.weight.to_numpy(float)
            mass = float(w[mask].sum())
            contribution = float(w[mask] @ g.actual_loss.to_numpy()[mask])
            false_count = int(h.low_forecast.sum())
            tailrows.append(
                dict(
                    year=year,
                    cohort=name,
                    mass=mass,
                    loss_contribution=contribution,
                    loss_share=contribution / float(w @ g.actual_loss),
                    low_count=false_count,
                    event_count=len(h),
                    low_fraction=false_count / len(h),
                    weighted_low_fraction=float(np.average(h.low_forecast, weights=h.weight)),
                )
            )
    ts = pd.DataFrame(tailrows)
    for name in ts.cohort.unique():
        r = dict(
            field="cohort",
            group=name,
            year="EQ",
            model="MAG",
            **summary(pd.concat(cohort_frames[name], ignore_index=True)),
        )
        r.update(ts.loc[ts.cohort.eq(name)].drop(columns=["year", "cohort"]).mean().to_dict())
        for k in ("low_count", "event_count"):
            r[k] = int(ts.loc[ts.cohort.eq(name), k].sum())
        records.append(r)
    summary_frame = pd.DataFrame(records)
    for row in tailrows:
        mask = (
            summary_frame.field.eq("cohort")
            & summary_frame.group.eq(row["cohort"])
            & summary_frame.year.astype(str).eq(str(row["year"]))
        )
        for k, value in row.items():
            if k not in ("year", "cohort"):
                summary_frame.loc[mask, k] = value
    rr = pd.DataFrame(rankrows)
    for model in ("MAG", "STOCK", "VOL"):
        row = rr.loc[rr.model.eq(model)].drop(columns=["year", "model"]).mean().to_dict()
        rankrows.append(dict(year="EQ", model=model, **row))
    ranks_frame = pd.DataFrame(rankrows)
    summary_frame.to_csv(OUT / "D0_AGGREGATED_DIAGNOSTICS.csv", index=False)
    ranks_frame.to_csv(OUT / "D0_MAGNITUDE_RANKING.csv", index=False)
    write_report(
        f,
        summary_frame,
        ranks_frame,
        pd.DataFrame(coverage),
        pd.DataFrame(chronology),
    )
    print(
        json.dumps(
            dict(
                status="D0_COMPUTED",
                rows=len(f),
                origins=4013,
                sessions=793,
                aggregate_rows=len(summary_frame),
                rank_rows=len(ranks_frame),
                sources=len(set(READS)),
                output=str(OUT.relative_to(Path.cwd())),
            )
        )
    )


def write_report(
    f: pd.DataFrame,
    d: pd.DataFrame,
    r: pd.DataFrame,
    coverage: pd.DataFrame,
    chronology: pd.DataFrame,
) -> None:
    """Render compact descriptive tables; narrative interpretation added below."""

    def subset(field: str, year: str = "EQ") -> pd.DataFrame:
        return d.loc[d.field.eq(field) & d.year.astype(str).eq(year)].copy()

    cols = [
        "group",
        "rows",
        "sessions",
        "observed",
        "predicted",
        "bias",
        "ratio",
        "transformed_MSE",
        "raw_MAE",
        "raw_MSE",
    ]
    models = d.loc[d.field.eq("model")].copy()
    annual = models.pivot(index="year", columns="model", values="transformed_MSE").reset_index()
    annual["MAG-STOCK"] = annual.MAG - annual.STOCK
    annual["MAG-VOL"] = annual.MAG - annual.VOL
    bias = models.loc[models.model.eq("MAG")]
    bins = subset("forecast_bin")
    stock = subset("ticker").sort_values("bias")
    signs = (
        d.loc[d.field.eq("ticker") & d.year.astype(str).ne("EQ")]
        .pivot(index="group", columns="year", values="bias")
        .reset_index()
    )
    clock = (
        d.loc[d.field.eq("slot") & d.year.astype(str).ne("EQ")]
        .pivot(index="group", columns="year", values="bias")
        .reset_index()
    )
    worst = f.assign(error=f.prediction_A - f.A).sort_values("error").head(5)
    tails = subset("cohort")
    tailcols = [
        "group",
        "rows",
        "sessions",
        "observed",
        "predicted",
        "raw_MAE",
        "raw_MSE",
        "mass",
        "loss_share",
        "weighted_low_fraction",
    ]
    doc = [
        "# S9 MAG Stage 1 / Session 1 — D0 read-only report",
        (
            "Prepared 27 October 2026. **Status: PARTIAL (all feasible saved-score D0 "
            "computations complete; missing menu and independent calibration history remain"
            " explicit limitations).** No fitting or inference was performed. F21–F24 "
            "forecasts are historically out of fit within fold, but all new analysis is "
            "post-search exploratory. Sections below separate archive reproduction from "
            "descriptive and retrospective cohorts."
        ),
        "## 1. Executive result",
        (
            "1. **Historical results reproduced:** 80,260 rows, 4,013 origins, 793 sessions; "
            "correct tensor order, refit scales and hierarchical weights. Equal-year MAG "
            "transformed MSE 0.232454 and raw MAE 0.006505 match saved controls/reports.\n"
            "2. **Broad underprediction:** mean Ahat 0.008361 vs A 0.010313, ratio 0.811 "
            "(18.9% shortfall). Bias is negative in 4/4 years, 48/48 months, 80/80 "
            "stock-years, 28/28 clock-years and all forecast deciles.\n"
            "3. **Uneven severity:** overnight-crossing ratio 0.765 vs intraday 0.907; "
            "15:30 ratio 0.694. This is not just one extreme forecast bin or one bad year.\n"
            "4. **Tails dominate mean shortfall:** prefix-95 exceedances have 5.87% "
            "weight mass and 24.08% of transformed loss; predicted/realized mean is "
            "0.294. Their unconditional signed-error contribution accounts for 92.2% "
            "of net mean underprediction. Ordinary-period mean ratio is 0.981.\n"
            "5. **Ordering survives level failure:** within-origin magnitude Spearman "
            "0.326608 (STOCK 0.300056, VOL 0.296950); historical all-row association "
            "0.408184 is a different statistic. A large move can rank high yet be far "
            "too small in predicted level.\n"
            "6. **F21 chronology is the constraint:** pre-2021 inner-validation pairs "
            "exist, but selected the epoch and use a different encoder/scale from the "
            "full refit. No selector-independent pre-F21 forecast bank was located in "
            "these saved S9 exports. A rigorous four-fold C1 result is not ready from "
            "existing artifacts alone.\n\n"
            "**Recommended next discussion:** if F21 must be included, will the "
            "researcher choose strategy A with a truly reserved calibration tail and "
            "matched restricted-history uncalibrated comparator, accepting separately "
            "authorized encoder work? An artifact-only strategy C pilot would instead "
            "require explicit acceptance of selector reuse and refit-transfer limits. "
            "No choice or improvement is frozen here."
        ),
        "## 2. Source and metric reproduction",
        (
            f"S9 root `S9 = {S9}`; S4 root `S4 = {S4}`. "
            "These aliases below are repository-relative. The four runs are "
            "`HF20-S9-F21-H4-MAG-S42`, `HF20-S9-F22-H4-MAG-S42`, "
            "`HF20-S9-F23-H4-MAG-S42`, `HF20-S9-F24-H4-MAG-S42` under S9."
        ),
        (
            "Each run supplies `oos_scores.parquet`, `oos_STOCK_control_scores.parquet`, "
            "`oos_VOL_control_scores.parquet`, `configuration.json`, "
            "`inner_target_recipe.json`, `refit_target_recipe.json`, "
            "`calibration_binding.json`, `refit_binding.json`, and "
            "`refit_STOCK_control.json`/`refit_VOL_control.json`. Actual member/endpoint "
            "records: "
            "`S4/F{21,22,23,24}_{inner_train,inner_validation,refit,oos}_indices.csv`. "
            "Feature recipes: `S4/Fxx_{inner,refit}_recipe.json`, bound in "
            "`S9/S4_REUSED_RECIPES.json`. Saved controls bind the exact canonical neural "
            "score file. Checkpoints were not opened or run; their saved binding IDs were "
            "checked against score metadata."
        ),
        (
            "Tensor order preserved exactly: `VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO"
            " JNJ AMZN XOM WFC AVGO TSLA MA CSCO`. Every admitted origin has exactly these "
            "20 stocks in this order. Zero duplicate, missing or mismatched keys. Four-fold"
            " total **80,260 rows / 4,013 origins / 793 sessions**. No dropping or "
            "imputation."
        ),
        table(
            coverage.assign(
                inner_scale=coverage.inner_scale.map(lambda v: f"{v:.17g}"),
                refit_scale=coverage.refit_scale.map(lambda v: f"{v:.17g}"),
            )
        ),
        (
            "Executed `A=abs(return_4h)`; original `M=log1p(A/refit_scale)` reconstructed "
            "in float64 from saved labels. `prediction_m == raw_0`; saved `prediction_A` "
            "equals freshly recomputed `refit_scale*expm1(max(raw_0,0))`. Loss "
            "reconstruction uses **unclamped** `raw_0`. Nonfinite numeric fields: zero. "
            "Negative outputs/clamped-to-zero forecasts: zero in every fold. No inner-scale"
            " substitution or double inverse. Cached forecasts remain the evaluated "
            "forecasts; only arithmetic identities were recomputed."
        ),
        (
            "All S4 origin IDs, dates, slots, endpoint and maturity timestamps agree in "
            "order; saved `trading_minutes=240`. Issuance is origin+2 minutes and maturity "
            "endpoint+2 minutes. Last input end is at/before origin. These checks do not "
            "independently reconstruct the exchange calendar or certify historical "
            "publication. The closing stub is not treated as an input hour. Original "
            "price-only target begins before approximate issuance and is not verified "
            "executable return."
        ),
        (
            "Weights: `w=1/(D*n_day*20)` within year; equal four-year mean. All saved row "
            "weights match. For descriptive subsets, condition original role weights on "
            "group membership **within each year**, then give represented years equal "
            "weight. No naive equal-row pooling. This differs from the legacy `strata()` "
            "helper's rebalancing of members after filtering; archive full-population "
            "metrics are unaffected. Cohort masses/loss shares retain unconditional role "
            "weights, averaged over years."
        ),
        (
            "Annual/equal-year transformed-target MSE (dimensionless squared log1p units; "
            "original out-of-fit saved population):"
        ),
        table(annual),
        (
            "Raw errors use absolute log-return units (MAE/means) or their squares (MSE). "
            "0.01 magnitude is approximately 1% for small moves. Annual/equal-year original"
            " forecasts:"
        ),
        table(models, ["year", "model", "observed", "predicted", "raw_MAE", "raw_MSE"]),
        (
            "**MATCH:** every annual MAG/STOCK/VOL transformed MSE, MAE, squared saved RMSE"
            " and historical all-row rank statistic agrees with "
            "`S9/S5_S9_MODEL_METRICS.csv` at atol=1e-12, rtol=1e-11. Equal-year archive "
            "targets 0.232454/0.269383/0.268266 MSE, 0.006505/0.006903/0.006992 MAE, "
            "0.00836/0.01031 forecast/realized means and 0.408 association match their "
            "printed precision. No material metric discrepancy required hand-trace "
            "correction. `STOCK` is a prefix mean of M, not raw A; `VOL` is parameter-free "
            "`2*sqrt(2/pi)*sigma_proxy`, with saved empty coefficient JSON, not a fitted "
            "raw-mean benchmark. A handoff accounting qualification conflates "
            "parameter-free MAG VOL outputs with the 64 charged fits: the actual "
            "`BASELINE_ATTEMPTS.jsonl` has 16 MAG, 24 EVENT and 24 QUANTILE starts, "
            "with zero MAG/VOL starts. Thus 64 historical fitted controls plus eight "
            "additional phase-specific parameter-free MAG VOL outputs is the correct "
            "distinction. No ledger entry was changed."
        ),
        (
            "**Minor handoff rounding MISMATCH:** the v2 prose annual table prints F23 "
            "MAG MSE 0.208858; the executed CSV and saved scores give "
            "0.20885746933969868, which rounds to 0.208857 at six decimals. The "
            "executed-source annex preserves the precise number. This is a prose "
            "rounding inconsistency, not a key/scale/loss failure; no historical "
            "file was corrected. Archive mean/rank targets above agree at their "
            "reported precision. No adjusted values were used to force a match."
        ),
        "## 3. Where raw-magnitude bias lives",
        (
            "Overall/year profile; positive `M_residual=M-Mhat` means transformed "
            "underprediction; raw `bias=Ahat-A` uses the opposite sign convention:"
        ),
        table(
            bias,
            [
                "year",
                "observed",
                "predicted",
                "bias",
                "absolute_bias",
                "ratio",
                "raw_MAE",
                "raw_MSE",
                "M_residual",
                "M_residual_sd",
                "M_residual_p95",
                "M_residual_p99",
            ],
        ),
        "### Forecast strength",
        (
            "Ten bins from weighted empirical forecast-score deciles, separately within "
            "each OOS year and also pooled using equal-year role mass. Identical forecast "
            "values stay together; unique cutpoints only. Bins are **descriptive historical"
            " score boundaries**, never proposed calibration boundaries. Table shows pooled"
            " bins; all annual bins are in the aggregate CSV. Each group's means follow the"
            " subset weighting above, so pooled bins are not unweighted averages over rows."
            " No bins have a zero-score point mass."
        ),
        table(
            bins,
            [
                "group",
                "forecast_min",
                "forecast_max",
                "rows",
                "sessions",
                "predicted",
                "observed",
                "bias",
                "ratio",
                "raw_MAE",
                "raw_MSE",
                "M_residual_sd",
                "M_residual_p99",
            ],
        ),
        "### Stock and clock heterogeneity",
        (
            "All 20 stocks, ordered from most negative to least negative equal-year mean "
            "bias; counts prevent a best/worst-only view from hiding coverage:"
        ),
        table(stock, cols),
        (
            "Stock raw mean bias by OOS year (stability check, overlapping groups are not "
            "independent replications):"
        ),
        table(signs),
        (
            "Seven saved origin slots, plus the saved target's INTRADAY/OVERNIGHT category."
            " Later origins retain their actual next-session endpoints; these are not newly"
            " constructed overnight labels."
        ),
        table(subset("slot"), cols),
        table(clock),
        table(subset("category"), cols),
        "### Calendar, volatility and source context",
        (
            "All 48 calendar months and 16 quarters are tabulated in "
            "`D0_AGGREGATED_DIAGNOSTICS.csv`, with counts/means/ratios/proper MSE/raw "
            "MAE/MSE; no favorable period was chosen. Quarter compact view:"
        ),
        table(
            d.loc[d.field.eq("quarter")],
            [
                "group",
                "rows",
                "sessions",
                "observed",
                "predicted",
                "bias",
                "ratio",
                "transformed_MSE",
                "raw_MAE",
            ],
        ),
        (
            "Volatility states 0–3 reuse each fold's **already fitted** EVENT refit `VOL` "
            "control's 25/50/75% cuts on log(sigma_proxy); this same construction is "
            "documented in the saved S9 summarizer. These are historical training-prefix "
            "cuts, not OOS/future-volatility regimes. `sigma_proxy` is "
            "decoded/imputed/floored FT16 V2 hourly open-to-close RMS60. Native "
            "unsmoothed/unimputed volatility and newly computed realized volatility were "
            "not reconstructed."
        ),
        table(subset("vol_state"), cols),
        (
            "Quality/fallback/terminal-age are already saved, directly keyed retrospective "
            "source diagnostics; not asserted observable model inputs. `SOURCE_FLAGGED` "
            "means assumed-zero or price-proxy minutes; fallback ANY means at least one "
            "feature-fallback cell. Age bins ZERO/LE1/LE2/LE5 use archived cut semantics. "
            "No source QA rebuild:"
        ),
        table(subset("quality"), cols),
        table(subset("fallback"), cols),
        table(subset("age_band"), cols),
        (
            "**Stability versus heterogeneity:** all stock-year and clock-year bias "
            "signs are negative, as are all 48 months and 16 quarters. This supports "
            "a persistent global raw-mean discrepancy. Its absolute scale is larger "
            "for TSLA/AMD (equal-year biases −0.005008/−0.004204) than JNJ/PEP "
            "(−0.000516/−0.000529), partly reflecting different move sizes. "
            "The 15:30 shortfall recurs in each year; all seven slots retain negative "
            "annual signs. Source-flagged and unflagged groups both underpredict, as "
            "do fallback ANY/NONE and all four prefix-volatility states. Thus the "
            "bias is not confined to recorded repairs. Age LE5 has only 184 pooled "
            "sessions and lacks one year's group; its EQ uses represented years "
            "only. It cannot establish stable age-specific effects. Clock/source/"
            "stock/year groups overlap heavily; no independent-replication claim.\n\n"
            "Forecast-decile ratios (~0.766–0.847 pooled; ~0.732–0.882 across "
            "annual deciles) suggest a broadly multiplicative level discrepancy "
            "with larger absolute errors and residual dispersion at high scores. "
            "They do not identify one universal factor: clock ratios differ, tail "
            "and ordinary cohorts differ sharply, and conditional means do not "
            "identify a deployable calibration map. No analytic calibrator slope "
            "was estimated."
        ),
        "## 4. Tails, magnitude ordering and Jensen gap",
        "### Tails and false-low forecasts",
        (
            "Saved refit `abs_r95` and `abs_r99` are prefix-weighted empirical raw-A "
            "thresholds (first sorted value reaching cumulative mass; no interpolation). "
            "Their labels mature before the outer year; exact prefix index maturity was "
            "checked. **No stored 90th threshold exists in the inspected target recipes: "
            "UNAVAILABLE; no 90th threshold was estimated.** The saved 99th threshold is an"
            " additional available check. No OOS outcomes determine a deployable threshold."
        ),
        (
            "Retrospective REALIZED_TOP1/TOP5 and ABS_RAW_ERROR_TOP1/TOP5 use the largest "
            "floor(N*pct/100) rows **within each year**, stable saved-row order for exact "
            "ties. The archive's ERROR_TOP cohorts instead sort transformed squared loss; "
            "these are shown under TRANSFORMED_LOSS_ARCHIVE and must not be confused with "
            "raw-error cohorts. Cohort averages condition original role weights within "
            "year; masses and transformed-loss shares are unconditional equal-year "
            "averages."
        ),
        table(tails, tailcols),
        (
            "`weighted_low_fraction` is the role-weighted fraction of the indicated cohort "
            "whose MAG score is in its origin's bottom half (20-name average rank <=10.5). "
            "For PREFIX95 this is the false-low rate; chance under unrelated scores is "
            "about 50%, not an event probability. Annual exact numerators/denominators, low"
            " rates, counts and loss contributions appear below; ordinary complement is "
            "retained."
        ),
        table(
            d.loc[d.field.eq("cohort") & d.group.eq("PREFIX95") & d.year.astype(str).ne("EQ")],
            [
                "year",
                "rows",
                "sessions",
                "low_count",
                "event_count",
                "low_fraction",
                "weighted_low_fraction",
                "mass",
                "loss_share",
            ],
        ),
        (
            "Five largest raw underpredictions only (retrospective examples, unweighted row"
            " values; error=Ahat-A):"
        ),
        table(worst, ["year", "session_date_et", "slot", "ticker", "A", "prediction_A", "error"]),
        "### Magnitude ranking",
        (
            "The historical ~0.408 is **equal-year mean of annual all-row magnitude rank "
            "association**: unweighted pandas midranks across all stock-origin rows of that"
            " year, followed by a weighted Pearson correlation of ranks using hierarchical "
            "row weights. It mixes stock identity, time and cross-section. It is not a "
            "signed-return IC or within-origin IC. Reproduced directly from the "
            "implementation `hf20_s5s9_metrics.weighted_rank_association`."
        ),
        (
            "New diagnostic `ic`: within each 20-stock origin Spearman via average ties, "
            "then origin mean within session, session mean within year, equal years. "
            "Constant scores yield undefined IC and are not converted to zero; `undefined` "
            "reports their fraction. Top/bottom-four retrieval uses fractional membership "
            "across boundary ties (expected overlap under independent random tie-breaks); "
            "chance 0.20. Pair concordance excludes realized tied pairs, assigns predicted "
            "ties 0.5, chance 0.50. `ties` is fraction of predicted tied pairs; `constant` "
            "is fraction of constant-score origins. All fractions use origin→session→year "
            "means."
        ),
        table(r),
        (
            "**Tail interpretation (SUPPORTED descriptively):** prefix95 realized "
            "mean 0.044639 vs predicted 0.013127; ordinary complement 0.008210 vs "
            "0.008058. Large moves are usually not assigned bottom-half scores: "
            "917/5,126 such rows are bottom-half (annual weighted false-low mean "
            "16.4%, ranging 14.6–21.2%). That does not constitute reliable jump "
            "prediction: many high-ranked events remain severely underpredicted. "
            "The whole forecast range is 0.001912–0.041622, while largest misses "
            "include realized magnitudes near 0.20. Retrospective top1% realized "
            "mean 0.074408 vs forecast 0.014790 further shows compressed amplitude.\n\n"
            "Within-origin MAG IC and pair concordance exceed both controls in each "
            "year; top4 retrieval averages 42.7% vs 38.0% STOCK and 40.5% VOL. "
            "Bottom4 retrieval (30.1%) slightly trails STOCK (30.6%). This is "
            "movement-size discrimination, not signed equity ranking. Supported "
            "facts are partial ordering and tail-level shortfall; failure to know "
            "unanticipated jumps, limited input information, or shrinkage may all "
            "contribute. Their causal shares remain unknown."
        ),
        "### Jensen gap and competing explanations",
        (
            "For unconstrained saved Mhat and e=M−Mhat, "
            "`A=s*(exp(M)−1)=s*(exp(Mhat)*exp(e)−1)` exactly. If a model were the ideal "
            "E[M|X], Jensen implies `s*(exp(E[M|X])−1) <= E[A|X]`. That directional result "
            "concerns an ideal conditional mean; it does not identify the source of the "
            "entire observed bias. In this population no decode clamp is active."
        ),
        (
            "The annual residual table and forecast-bin residual dispersions/p99 show "
            "whether M is centered and how its upper tail varies. Positive raw misses "
            "coexist with transformed residuals of either sign; convex inversion can make "
            "raw means low even when mean M residual is near zero or negative. We did "
            "**not** calculate/deploy a smearing factor, multiply forecasts by residual "
            "moments, save adjusted scores, or score a hypothetical correction. `exp(e)` is"
            " especially sensitive to rare positive residuals, so OOS residual averages "
            "could not serve as honest calibration history."
        ),
        (
            "**SUPPORTED:** raw mean bias is negative every year even though mean "
            "M residual changes sign (+0.0217, −0.0177, +0.0037, −0.0255; "
            "equal-year −0.00447). Pooled residual SD is 0.4821 and 99th percentile "
            "1.1995; dispersion rises from 0.316 in the lowest forecast bin to "
            "0.638 in the highest. Thus correcting a single M-space signed bias "
            "cannot by itself explain the raw mean gap.\n\n"
            "**SUGGESTIVE:** transformed/raw functional mismatch and conditional "
            "heteroskedasticity are consistent with these facts. Systematic "
            "clock differences and annual changes also suggest imperfect "
            "conditioning or distribution shift. **UNRESOLVED:** how much each "
            "of misspecification, original-scale bias, irreducible event noise, "
            "source/clock composition and year shifts causes the gap. Jensen's "
            "inequality proves no allocation of historical blame. No OOS oracle "
            "factor or corrected forecast performance is reported."
        ),
        "## 5. Chronological calibration and B0 readiness",
        (
            "Saved earlier-prefix inventory (counts/date metadata only for "
            "interpretation/recipe verification, no new predictive performance claims on "
            "prefixes):"
        ),
        table(chronology),
        (
            "`inner_train_scores` are in sample for the selected calibration "
            "encoder. `inner_validation_scores` are out of optimizer training but "
            "were evaluated every epoch to select that same checkpoint: they are "
            "**not selector-independent calibration data**. `refit_scores` are in "
            "sample for the fresh full-prefix encoder. `oos_scores` are held out "
            "within the fold. The runner reloads selected calibration weights for "
            "inner exports, then resets seed/model/optimizer for a fresh full-prefix "
            "refit. Inner/refit scales and feature recipes differ. Saved bindings "
            "identify `calibration_{027,020,041,027}.pt` versus `refit_final.pt`; "
            "no checkpoint forward pass or new paired population was generated.\n\n"
            "| Later evaluation | Earlier saved out-of-fit history | Readiness |\n"
            "| --- | --- | --- |\n"
            "| F21 | 2020 inner validation: 674 origins, 120 sessions; selected epoch 27 | "
            "C only, exploratory selector reuse/model mismatch. Strict independent "
            "bank UNAVAILABLE / NEW FIT REQUIRED. |\n"
            "| F22 | F21 outer scores (2021), 955 origins/188 sessions | "
            "Earlier chronological bank exists; different encoder/refit scale; "
            "transfer protocol and shift check required. |\n"
            "| F23 | F21–F22 outer scores, 2,135 origins/398 sessions | "
            "Same caveat; never use F23 outcomes for F23 calibration. |\n"
            "| F24 | F21–F23 outer scores, 3,022 origins/585 sessions | "
            "Same caveat; never use F24 outcomes for F24 calibration. |\n\n"
            "Those outer labels mature before the next evaluation year. Earlier "
            "OOS pairs can be a sparse annual prequential bank, but they do not "
            "supply pre-F21 history or predictions of the newly refitted encoder "
            "on genuinely unseen earlier observations. Residuals must use each "
            "generating model's own target scale. A raw decode/re-encode under "
            "another scale does not establish conditional-mean equivalence or "
            "repair encoder distribution shift. All years remain post-search.\n\n"
            "| Design | Saved-artifact feasibility | Main scientific trade-off |\n"
            "| --- | --- | --- |\n"
            "| A: reserved chronological calibration tail | Not already independent "
            "of selection/training in current exports; NEW FIT/FORECAST WORK REQUIRED | "
            "Most defensible uniform four-fold design: separate earlier epoch "
            "selection from calibration, purge/mature labels, freeze encoder before "
            "tail, compare calibrated and uncalibrated versions of that identical "
            "restricted-history encoder. Reusing today's selector-exposed tail "
            "would not implement this design. |\n"
            "| B: honest earlier-prefix prequential bank | Limited bank available "
            "for F22–F24, absent pre-F21 | Uses more encoder history at evaluation; "
            "requires a declared bank window/weight rule and refit-distribution "
            "shift check. Full four-fold bank requires new earlier encoder fits. |\n"
            "| C: archived inner-validation pairs | Present for every fold; no "
            "new encoder inference needed for these pairs | Lowest-cost exploratory "
            "pilot only: labels also chose epoch, limited recent sessions, "
            "different inner/refit scalers and weights. Direct transfer to full "
            "refit cannot be presented as validated calibration. |\n\n"
            "**Recommendation for discussion:** A is the smallest scientifically "
            "clean all-four-fold C1a experiment if a uniform F21 result is required. "
            "Begin with one global scalar residual-smearing hypothesis, no stock "
            "or clock segmentation, and its matched restricted-history raw "
            "comparator. Freeze calendar tail, separate selector period, "
            "maturity/embargo, residual units, weights, clamp convention and "
            "primary raw-mean MSE/calibration metrics before fitting. Also retain "
            "original transformed MSE and raw MAE. If the researcher requires a "
            "non-neural-only next session, finish B0 and decide whether C is an "
            "explicitly limited exploratory pilot; an honest A-based four-fold "
            "C1 claim must wait for separately authorized encoder work.\n\n"
            "| Later B0/C1 prerequisite | Saved availability | New calculation/work later |\n"
            "| --- | --- | --- |\n"
            "| Prefix raw-mean/median B0 | `return_4h`, weights and exact refit keys "
            "already saved in each `refit_scores.parquet`; raw A is abs(R) | "
            "New prefix-only baseline fitting, separately authorized; no source "
            "rebuild needed. Existing STOCK optimizes M, not raw A. |\n"
            "| Stock×clock B0 | ticker, slot/category and raw A on same prefix keys | "
            "New prefix-only grouped controls and a predeclared sparse-cell policy. |\n"
            "| Conditional-volatility B0 | `sigma_proxy` is decoded phase FT16 V2; "
            "stock/clock keys and phase scalers saved | A limited matched-information "
            "control needs no minute rebuild. Additional V1/range/history channels "
            "are not in score exports; require separately permitted materialization. |\n"
            "| Original M | No dedicated M column; exact phase scale + raw A exist | "
            "Formula-only transform, not a fit; do not confuse saved Z/TG20 with M. |\n"
            "| C1 residual pairs | inner validation and earlier outer-year pairs above | "
            "Chronology/model-transfer decision before any smearing estimate. "
            "In-sample refit pairs cannot substitute for honest residual history. |\n\n"
            "Reuse `hf20_s5s9_metrics.decode/metrics`, ranking/weight primitives, "
            "`hf20_s5s9_report.verify_frame` mathematics, saved S4 role indices/"
            "phase recipes and saved bindings. Do not invoke `Data()` or the "
            "completed campaign runner just to analyze saved scores: those paths "
            "reconstruct sources or initiate fitting. B0 grouped controls and a "
            "separately approved artifact-only C1 pilot could share one later "
            "non-neural session after the design decision. Minimum new code is "
            "a bounded key/phase reader and permitted prefix-fit/calibration "
            "routine with exact weights and matched evaluation; no new framework, "
            "source dataset or dashboard is needed. No future runtime promise."
        ),
        "## 6. Decision table — diagnosed patterns are not fitted improvements",
        (
            "The research-menu file is missing, so C1a/b/c/C2 names below are "
            "discussion labels from the live instruction, not recovered frozen "
            "menu definitions.\n\n"
            "| D0 finding | Possible later implication | Evidence quality | Researcher decision |\n"
            "| --- | --- | --- | --- |\n"
            "| Broad raw mean gap with near-centered M | Discuss scalar C1a first; "
            "no fitted benefit established | SUPPORTED pattern, SUGGESTIVE mechanism | "
            "Choose A/B/C chronology and estimand; decide F21 scope. |\n"
            "| Decile dispersion/ratios vary | Reason to consider score/state-conditional "
            "C1b/C1c hypotheses only after scalar control | Exploratory heterogeneity | "
            "Recover exact menu definitions and predeclare limited comparison; "
            "OOS bins cannot become calibration boundaries. |\n"
            "| Overnight/15:30 gap recurs | Clock-conditioned hypothesis may deserve "
            "later review; first fit stock×clock B0 on past prefixes | SUPPORTED "
            "descriptive pattern, causation UNRESOLVED | Whether a conditional map "
            "or later C2/objective change is justified after C1a/B0. |\n"
            "| Tail amplitudes missed despite ranking | C2/later objective question "
            "may remain after level calibration | SUPPORTED shortfall; irreducible "
            "noise vs misspecification UNRESOLVED | Choose raw mean/median/tail "
            "estimand; no automatic new neural objective. |\n"
            "| STOCK/VOL are limited functional controls | B0 raw mean/median and "
            "conditional-volatility controls are needed | Exact executed formulas | "
            "Declare information set, prefix weights and comparison metric. |\n"
            "| F21 independent pairs absent | A or new pre-F21 bank requires new "
            "authorized encoder work; C remains qualified exploratory | Exact saved "
            "roles and epoch-selection implementation | Do not invent historical "
            "forecasts or calibrate on F21 outcomes. |"
        ),
        "## 7. Reproduction, integrity and files changed",
        (
            "From the repository root, with the existing declared environment and legally "
            "available ignored saved artifacts:\n\n```bash\n.venv/bin/python -B "
            "reports/experiments/hf20_s9_mag_stage1_session1_d0_2026-10-27/replay_d0.py\n```"
        ),
        (
            "The helper imports only pathlib/hashlib/json/NumPy/pandas. It never imports a "
            "model runner or source loader; no training, fitting, optimization, neural "
            "forward pass, score adjustment, data download, minute/FT16 rebuild, trade "
            "signal or backtest is present. It reads explicit F21–F24 paths and earlier "
            "prefixes; no recursive source loaders or discovery globs. Source hashes are "
            "limited to correctness-critical permitted recipes/canonical saved scores and "
            "control bindings; no protected content/hash was read. No 2025 numerical "
            "analysis. No canonical artifact, configuration, dashboard, ledger or old "
            "report was modified."
        ),
        (
            "Scope reference availability: "
            "`HF20_S9_MAG_Stage1_Calibration_and_Prediction_Objectives_Research_Menu_v0.1_2026-10-27.md`"
            " **not found** in repository filename inventory; no supplied copy beyond the "
            "detailed live prompt. The prompt governs D0 and A/B/C definitions; exact "
            "C1a/b/c/C2 menu wording must be checked before freezing later work. The S9 v2 "
            "and complete-experiment v3 handoffs under `docs/track_a/Consolidation/` were "
            "read, with executed-source annexes; existing sources override handoff prose. "
            "No external search/install was needed or performed."
        ),
        (
            "Source readers actually used (deduplicated explicit paths; checkpoints and raw"
            " sources are deliberately absent):"
        ),
        (
            "83 distinct executed-artifact reads, compressed here by the four "
            "explicit run/fold IDs above (not a recursive loader):\n\n"
            "- S9 root: `S4_REUSED_RECIPES.json`, `S5_S9_MODEL_METRICS.csv`.\n"
            "- Each MAG run: `configuration.json`, `inner_target_recipe.json`, "
            "`refit_target_recipe.json`, `calibration_binding.json`, "
            "`refit_binding.json`; the four `inner_train/inner_validation/refit/oos` "
            "`_scores.parquet` files; `oos_STOCK_control_scores.parquet`, "
            "`oos_VOL_control_scores.parquet`, `refit_STOCK_control.json`, "
            "`refit_VOL_control.json`.\n"
            "- S4: `S4_FROZEN_EXPERIMENT_CARD.json`, eight "
            "`Fxx_{inner,refit}_recipe.json`, sixteen "
            "`Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`.\n"
            "- Each `S9/HF20-S9-Fxx-H4-EVENT-S42/refit_VOL_control.json`: cutoffs "
            "only. No EVENT prediction population was analyzed.\n\n"
            "Read-only interpretation also inspected the two named Consolidation "
            "handoffs, newest S5/S9 session reports, final research decision, and "
            "executed target/decoder/metric/selection/export code. Existing HTML "
            "is referenced by `S9/S5_S9_VISUAL_DIAGNOSTICS.html` without loading "
            "or changing it. No bulk source, checkpoint tensors, 2025 or protected "
            "2026 stores were accessed."
        ),
        (
            "Verification: the replay's strict key/order/endpoint/scale/decode/"
            "weight/binding/metric assertions passed on all four folds, with 379 "
            "aggregate records and 15 ranking records. `ruff check` passed. The "
            "full-project basic Pylance-stub parity check completed over 498 "
            "Python files with **0 errors / 0 warnings**:\n\n"
            "```bash\n.venv/bin/python scripts/check_python_types.py "
            "--pylance-dist /Users/pradeepgupta/.vscode/extensions/"
            "ms-python.vscode-pylance-2026.4.1/dist\n```\n\n"
            "The absolute path above is the actual local editor-check tooling "
            "location, not a runtime dependency; on another machine select that "
            "machine's installed Pylance `dist`. Select repository `.venv/bin/python`, "
            "restart Pylance and refresh Problems; the final editor view remains "
            "human-confirmed. No pytest suite was invoked because existing tests "
            "include fitting paths outside this zero-fit session; the replay's "
            "mathematical assertions are the targeted smoke/verification. PyArrow "
            "emitted nonfatal sandbox CPU-cache/neon sysctl warnings; all reads "
            "and calculations completed. No installation or sandbox escalation "
            "was needed. Initial helper float32-inverse/read-only-array bugs and "
            "six type diagnostics were corrected; they were not historical "
            "score mismatches. Final checked arithmetic uses FP64 decode.\n\n"
            "Starting/ending branch `feat/track-a-data-intake`, commit "
            "`5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`; fetch succeeded, upstream "
            "0 ahead / 0 behind. Four pre-existing untracked documentation files "
            "(shown as three entries by initial short status) remain untouched. "
            "No tracked changes, staging, commits, push, pull or merge. This package "
            "and the mandatory session report are new, uncommitted files for review.\n\n"
            "New output files (read-only **with respect to research sources**, "
            "ordinary writable report files):\n\n"
            "| File in this namespace | Bytes | Purpose |\n"
            "| --- | --- | --- |\n"
            "| S9_MAG_STAGE1_SESSION1_D0_READONLY_REPORT.md | {REPORT_BYTES} | "
            "Self-contained scientific review |\n"
            f"| replay_d0.py | {(OUT / 'replay_d0.py').stat().st_size} | "
            "One namespaced descriptive replay helper |\n"
            f"| D0_AGGREGATED_DIAGNOSTICS.csv | "
            f"{(OUT / 'D0_AGGREGATED_DIAGNOSTICS.csv').stat().st_size} | "
            "379 aggregate rows; all groups/annual bins/cohorts |\n"
            f"| D0_MAGNITUDE_RANKING.csv | "
            f"{(OUT / 'D0_MAGNITUDE_RANKING.csv').stat().st_size} | "
            "15 annual/equal-year predictor summaries |\n\n"
            "Mandatory handoff: `reports/codex_sessions/"
            "2026-10-27_184041_hf20_s9_mag_d0_readonly.md`. No new figures, "
            "prediction Parquets, adjusted forecasts, model artifacts, framework "
            "layers or dashboard files. Review the package and handoff before any "
            "separate commit; no automatic Git publication was authorized."
        ),
        (
            "Completion: [x] no fitting/inference/trading; [x] 2026 content/hashes closed "
            "and no 2025 analysis; [x] saved three-predictor metrics reproduced; [x] "
            "feasible D0 dimensions, tails and magnitude ranking complete; [x] no "
            "fitted-improvement claim; [x] chronology inventoried with F21 limitation; [x] "
            "compact additive package. Missing 90th threshold, independent pre-F21 forecast"
            " bank and research menu are explicit. **STOP: no C1/B0 fit, C2 or later "
            "objective launched.**"
        ),
    ]
    rendered = "\n\n".join(doc) + "\n"
    size = 0
    content = rendered
    for _ in range(5):
        content = rendered.replace("{REPORT_BYTES}", str(size))
        measured = len(content.encode())
        if measured == size:
            break
        size = measured
    (OUT / "S9_MAG_STAGE1_SESSION1_D0_READONLY_REPORT.md").write_text(content)


if __name__ == "__main__":
    main()
