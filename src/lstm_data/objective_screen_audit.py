"""Frozen P022 feature/event triage, using saved inner-role observations only."""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

from .config import digest, now, write_json
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import ORDER, checked, ref
from .hf1m_training_data import TrainingView
from .magnitude_range_audit import session_weights
from .objective_screen_loss import classes, fit_recipe
from .objective_screen_source import (
    assert_frozen_design,
    gather,
    native_arrays,
    ordered_targets,
    scoped_view,
)
from .visualization.hf1m_long import LongStudy


def correlation(x: np.ndarray, y: np.ndarray) -> float:
    good = np.isfinite(x) & np.isfinite(y)
    if good.sum() < 3:
        return float("nan")
    a = pd.Series(x[good]).rank().to_numpy()
    b = pd.Series(y[good]).rank().to_numpy()
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def origin_ic(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Average-tied ranks; require all20 finite values, constant score undefined."""
    a = pd.DataFrame(x.reshape(-1, 20)).rank(axis=1).to_numpy()
    b = pd.DataFrame(y.reshape(-1, 20)).rank(axis=1).to_numpy()
    a = a - np.mean(a, axis=1, keepdims=True)
    b = b - np.mean(b, axis=1, keepdims=True)
    den = np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))
    return np.divide((a * b).sum(axis=1), den, out=np.full(len(a), np.nan), where=den > 0)


def month_ci(daily: pd.Series, block_months: int = 1) -> tuple[float, float]:
    """Whole-month resampling retains all dependent stocks/origins within each day."""
    d = daily.dropna()
    if not len(d):
        return float("nan"), float("nan")
    month = np.array([int(str(v)[:4]) * 12 + int(str(v)[5:7]) for v in d.index])
    block = (month - month.min()) // block_months
    g = pd.DataFrame({"v": d.to_numpy(), "b": block}).groupby("b").v.agg(["sum", "count"])
    rng = np.random.default_rng(22042)
    ids = rng.integers(0, len(g), size=(400, len(g)))
    means = g["sum"].to_numpy()[ids].sum(axis=1) / g["count"].to_numpy()[ids].sum(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(lo), float(hi)


def average_precision(label: np.ndarray, score: np.ndarray, weight: np.ndarray) -> float:
    """Tie-grouped noninterpolated AP; no arbitrary ordering within score ties."""
    if weight[label].sum() <= 0:
        return float("nan")
    order = np.argsort(-score, kind="stable")
    s, truth, w = score[order], label[order], weight[order]
    end = np.r_[s[:-1] != s[1:], True]
    tp = np.cumsum(w * truth)[end]
    total = np.cumsum(w)[end]
    recall = tp / tp[-1]
    return float(np.sum(np.diff(np.r_[0.0, recall]) * tp / total))


def summaries(
    study: LongStudy, view: TrainingView, q: float
) -> tuple[dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    arrays = native_arrays(study, view)
    values: dict[str, list[np.ndarray]] = {}
    precursor = []
    missing = []
    target = ordered_targets(view)
    labels = classes(target.TG20.to_numpy(), q).reshape(-1, 20)
    weights = session_weights(target).reshape(-1, 20)
    for start in range(0, len(view.source.rows), 32):
        pos = tuple(range(start, min(start + 32, len(view.source.rows))))
        native = gather(view, arrays, pos, "native")
        fallback = gather(view, arrays, pos, "fallback")
        scaled = view.origin_batch(pos)["x"].astype(float)
        for kind, x in [("native", native), ("scaled", scaled)]:
            valid = np.isfinite(x)
            count = valid.sum(axis=2)
            mean = np.divide(
                np.where(valid, x, 0).sum(axis=2),
                count,
                out=np.full(count.shape, np.nan),
                where=count > 0,
            )
            for summary, a in [
                ("latest", x[:, :, 47]),
                ("valid_mean48", mean),
                ("last_minus_first", x[:, :, 47] - x[:, :, 0]),
            ]:
                values.setdefault(kind + "_" + summary, []).append(a.reshape(-1, 16))
        missing.append(
            pd.DataFrame(
                dict(
                    feature=ORDER,
                    native_missing=(~np.isfinite(native)).sum(axis=(0, 1, 2)),
                    fallback_cells=fallback.sum(axis=(0, 1, 2)),
                    cells=native.shape[0] * 20 * 48,
                )
            )
        )
        for channel in ["M1", "V1", "Q2", "B1"]:
            j = ORDER.index(channel)
            for cls in range(3):
                mass = weights[list(pos)] * (labels[list(pos)] == cls)
                total = mass.sum()
                for step in range(48):
                    precursor.append(
                        dict(
                            feature=channel,
                            event=["NEG", "NORMAL", "POS"][cls],
                            step=step - 47,
                            mass=float(total),
                            weighted_sum=float((scaled[:, :, step, j] * mass).sum()),
                            fallback_sum=float((fallback[:, :, step, j] * mass).sum()),
                        )
                    )
    p = pd.DataFrame(precursor).groupby(["feature", "event", "step"], as_index=False).sum()
    p["scaled_mean"] = p.weighted_sum / p.mass
    p["fallback_fraction"] = p.fallback_sum / p.mass
    m = pd.concat(missing).groupby("feature", as_index=False).sum()
    m["native_missing_fraction"] = m.native_missing / m.cells
    m["fallback_fraction"] = m.fallback_cells / m.cells
    return {key: np.concatenate(v) for key, v in values.items()}, p, m


def threshold_bins(x: np.ndarray, bounds: list[float]) -> np.ndarray:
    """0 below min,1..5 quintiles,6 above max,7 missing. Ties stay in lower bin."""
    b = np.searchsorted(np.asarray(bounds[1:-1]), x, side="left") + 1
    b[x < bounds[0]] = 0
    b[x > bounds[-1]] = 6
    b[~np.isfinite(x)] = 7
    return b


def replay_targets(study: LongStudy, view: TrainingView) -> list[dict]:
    rows = view.source.rows
    target = ordered_targets(view)
    # Predeclared first/middle/last plus largest |y| origin; not selecting model performance.
    extreme = target.iloc[int(np.argmax(abs(target.TG20)))].origin_id
    selected = rows.loc[
        rows.origin_id.isin(
            [
                rows.iloc[0].origin_id,
                rows.iloc[len(rows) // 2].origin_id,
                rows.iloc[-1].origin_id,
                extreme,
            ]
        )
    ]
    steps = sorted(set(selected.entry_index) | set(selected.exit_index))
    candles = pd.read_parquet(
        checked(study.contract["files"]["candles_quality"]), filters=[("step", "in", steps)]
    )
    result = []
    for row in selected.itertuples(index=False):
        entry = candles.loc[candles.step.eq(row.entry_index)].set_index("ticker").reindex(SYMBOLS)
        exit_ = candles.loc[candles.step.eq(row.exit_index)].set_index("ticker").reindex(SYMBOLS)
        assert entry.genuine_close.all() and exit_.genuine_close.all()
        assert entry.session_date_et.eq(row.session_date_et).all()
        assert exit_.session_date_et.eq(row.session_date_et).all()
        assert ((exit_.hour_end_utc - entry.hour_end_utc).dt.total_seconds() == 14400).all()
        r = np.log(exit_.close.to_numpy() / entry.close.to_numpy())
        median = np.median(r)
        n = r - median
        mad = np.median(abs(n))
        y = n / (mad + view.source.fit["epsilon"])
        saved = target.loc[target.origin_id.eq(row.origin_id)].set_index("ticker").reindex(SYMBOLS)
        for expected, actual in [(r, saved.return_4h), (n, saved.numerator), (y, saved.TG20)]:
            np.testing.assert_allclose(expected, actual, rtol=1e-11, atol=1e-12)
        result.append(
            dict(
                origin_id=row.origin_id,
                max_error=float(np.max(abs(y - saved.TG20))),
                median=float(median),
                mad=float(mad),
                epsilon=view.source.fit["epsilon"],
            )
        )
    return result


def cohort_cutoffs(t: pd.DataFrame) -> dict:
    result = {}
    for fraction in (0.01, 0.05):
        k = int(len(t) * fraction)
        for name, column in [("y", "TG20"), ("n", "numerator")]:
            result[f"{name}_top{int(fraction * 100)}"] = float(
                np.sort(abs(t[column].to_numpy()))[-k]
            )
        origins = t.drop_duplicates("origin_id")
        result[f"mad_bottom{int(fraction * 100)}"] = float(
            np.sort(origins.cross_section_mad)[int(len(origins) * fraction) - 1]
        )
    for side, select in [
        ("global", np.ones(len(t), bool)),
        ("positive", t.TG20.gt(0)),
        ("negative", t.TG20.lt(0)),
    ]:
        for fraction in (0.99, 0.95):
            result[f"{side}_range{int(fraction * 100)}"] = float(
                abs(t.loc[select, "TG20"]).max() * fraction
            )
    return result


def cohorts(t: pd.DataFrame, cut: dict, split: str) -> list[dict]:
    w = session_weights(t)
    masks = {}
    for pct in (1, 5):
        yn = abs(t.TG20).ge(cut[f"y_top{pct}"]).to_numpy()
        n = abs(t.numerator).ge(cut[f"n_top{pct}"]).to_numpy()
        mad = t.cross_section_mad.le(cut[f"mad_bottom{pct}"]).to_numpy()
        masks.update(
            {
                f"y_top{pct}": yn,
                f"n_top{pct}": n,
                f"mad_bottom{pct}": mad,
                f"both{pct}": n & mad,
                f"num_only{pct}": n & ~mad,
                f"mad_only{pct}": mad & ~n,
                f"neither{pct}": ~(n | mad),
                f"union{pct}": n | mad,
                f"outside_y{pct}": ~yn,
            }
        )
        assert np.all((n & mad).astype(int) + (n & ~mad) + (mad & ~n) + ~(n | mad) == 1)
    for key, value in cut.items():
        if "range" in key:
            m = abs(t.TG20).ge(value).to_numpy()
            if key.startswith("positive"):
                m = m & t.TG20.gt(0).to_numpy()
            if key.startswith("negative"):
                m = m & t.TG20.lt(0).to_numpy()
            masks[key] = m
    return [
        dict(
            role=split,
            cohort=key,
            rows=int(mask.sum()),
            row_fraction=float(mask.mean()),
            origins=t.loc[mask, "origin_id"].nunique(),
            sessions=t.loc[mask, "session_date_et"].nunique(),
            weight_mass=float(w[mask].sum()),
            negative_rows=int((mask & t.TG20.lt(0)).sum()),
            positive_rows=int((mask & t.TG20.gt(0)).sum()),
        )
        for key, mask in masks.items()
    ]


def run(out: Path) -> None:
    started = time.monotonic()
    design = assert_frozen_design(out)
    dest = out / "stage1"
    if dest.exists():
        raise ValueError("P022_AUDIT_OUTPUT_EXISTS")
    dest.mkdir()
    study = LongStudy.discover(Path.cwd())
    train = scoped_view(study, "inner_train", stage=1)
    train_t = ordered_targets(train)
    recipe = fit_recipe(
        train_t.TG20.to_numpy(), session_weights(train_t), train.source.fit["t2_scale"]
    )
    cuts = cohort_cutoffs(train_t)
    write_json(dest / "inner_event_recipe.json", recipe)
    write_json(dest / "training_cohort_thresholds.json", cuts)
    associations = []
    bins = []
    stability = []
    events = []
    qa = []
    responses = []
    oracles = []
    allprec = []
    allmissing = []
    boundaries = {}
    regime_bounds = {}
    for split in ["inner_train", "inner_validation"]:
        print("AUDIT", split, flush=True)
        view = train if split == "inner_train" else scoped_view(study, split, stage=1)
        t = ordered_targets(view)
        w = session_weights(t)
        y = t.TG20.to_numpy()
        n = abs(t.numerator.to_numpy())
        event = classes(y, recipe["q95_abs_y"])
        feature, p, m = summaries(study, view, recipe["q95_abs_y"])
        p["role"] = split
        m["role"] = split
        allprec.append(p)
        allmissing.append(m)
        oracles += [dict(role=split, **r) for r in replay_targets(study, view)]
        qa += cohorts(t, cuts, split)
        t["event"] = event
        t["weight"] = w
        t["year"] = t.session_date_et.str[:4]
        for scope, groups in [
            ("all", [("all", t)]),
            ("year", t.groupby("year")),
            ("stock", t.groupby("ticker")),
        ]:
            for group, g in groups:
                for cls in range(3):
                    events.append(
                        dict(
                            role=split,
                            scope=scope,
                            group=group,
                            event=["NEG", "NORMAL", "POS"][cls],
                            rows=int(g.event.eq(cls).sum()),
                            fraction=float(g.event.eq(cls).mean()),
                            weight_fraction=float(
                                g.loc[g.event.eq(cls), "weight"].sum() / g.weight.sum()
                            ),
                        )
                    )
        dates = view.source.rows.session_date_et.to_numpy()
        for representation, array in feature.items():
            for j, channel in enumerate(ORDER):
                key = representation + "_" + channel
                x = array[:, j]
                if split == "inner_train":
                    finite = x[np.isfinite(x)]
                    boundaries[key] = np.quantile(finite, [0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()
                b = threshold_bins(x, boundaries[key])
                assert len(b) == len(t) and np.isin(b, range(8)).all()
                for bin_id in range(8):
                    mask = b == bin_id
                    ww = w[mask]
                    total = ww.sum()
                    bins.append(
                        dict(
                            role=split,
                            feature=channel,
                            representation=representation,
                            bin=bin_id,
                            rows=int(mask.sum()),
                            weight_mass=float(total),
                            target_mean=float(np.average(y[mask], weights=ww)) if total else np.nan,
                            target_median=float(np.median(y[mask])) if mask.any() else np.nan,
                            NEG=float(ww[event[mask] == 0].sum() / total) if total else np.nan,
                            NORMAL=float(ww[event[mask] == 1].sum() / total) if total else np.nan,
                            POS=float(ww[event[mask] == 2].sum() / total) if total else np.nan,
                        )
                    )
                ic = origin_ic(x, y)
                daily = pd.Series(ic, index=dates).groupby(level=0).mean()
                lo, hi = month_ci(daily)
                lo2, hi2 = month_ci(daily, 2)
                associations.append(
                    dict(
                        role=split,
                        feature=channel,
                        representation=representation,
                        rows=len(x),
                        finite=int(np.isfinite(x).sum()),
                        pooled_spearman=correlation(x, y),
                        daily_ic=float(daily.mean()),
                        defined_days=int(daily.notna().sum()),
                        months=len(set(t.session_date_et.str[:7])),
                        ci_low=lo,
                        ci_high=hi,
                        two_month_low=lo2,
                        two_month_high=hi2,
                        abs_n_spearman=correlation(x, n),
                        NEG_rank_biserial=correlation(x, (event == 0).astype(float)),
                        POS_rank_biserial=correlation(x, (event == 2).astype(float)),
                    )
                )
                for stock in SYMBOLS:
                    mask = t.ticker.eq(stock).to_numpy()
                    stability.append(
                        dict(
                            role=split,
                            feature=channel,
                            representation=representation,
                            scope="stock",
                            group=stock,
                            rows=int(mask.sum()),
                            spearman=correlation(x[mask], y[mask]),
                        )
                    )
                if split == "inner_train":
                    for start, stop in design["stage1"]["subperiods"]:
                        mask = t.session_date_et.between(start, stop).to_numpy()
                        stability.append(
                            dict(
                                role=split,
                                feature=channel,
                                representation=representation,
                                scope="era",
                                group=start + "/" + stop,
                                rows=int(mask.sum()),
                                spearman=correlation(x[mask], y[mask]),
                            )
                        )
        for channel in ["V1", "Q2"]:
            x = feature["native_latest"][:, ORDER.index(channel)]
            if split == "inner_train":
                regime_bounds[channel] = np.quantile(x[np.isfinite(x)], [1 / 3, 2 / 3]).tolist()
        for seed in [42, 123]:
            pred = study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", split).set_index(
                ["origin_id", "ticker"]
            )
            pred = pred.reindex(pd.MultiIndex.from_frame(t[["origin_id", "ticker"]]))
            np.testing.assert_array_equal(pred.actual_TG20, y)
            score = pred.pred_original_TG20.to_numpy()
            daily = pd.Series(origin_ic(score, y), index=dates).groupby(level=0).mean()
            for channel in ["ALL", "V1", "Q2"]:
                x = (
                    feature["native_latest"][:, ORDER.index(channel)]
                    if channel != "ALL"
                    else np.zeros(len(t))
                )
                regime = np.searchsorted(regime_bounds.get(channel, []), x)
                regime[~np.isfinite(x)] = 3
                for level in sorted(set(regime)):
                    mask = regime == level
                    ww = w[mask]
                    ww = ww / ww.sum()
                    ys = y[mask]
                    ps = score[mask]
                    ev = event[mask]
                    responses.append(
                        dict(
                            role=split,
                            seed=seed,
                            regime_channel=channel,
                            regime=int(level),
                            rows=int(mask.sum()),
                            prediction_mean=float(ww @ ps),
                            prediction_sd=float(np.sqrt(ww @ (ps - ww @ ps) ** 2)),
                            actual_sd=float(np.sqrt(ww @ (ys - ww @ ys) ** 2)),
                            mse=float(ww @ (ps - ys) ** 2),
                            residual_mean=float(ww @ (ps - ys)),
                            signed_spearman=correlation(ps, ys),
                            full20_daily_ic=float(daily.mean()) if channel == "ALL" else np.nan,
                            POS_AP=average_precision(ev == 2, ps, ww),
                            NEG_AP=average_precision(ev == 0, -ps, ww),
                            ANY_AP=average_precision(ev != 1, abs(ps), ww),
                        )
                    )
        # Small summary matrices, never dense windows; private and exactly role keyed.
        np.savez_compressed(
            dest / (split + "_feature_summaries.npz"),
            allow_pickle=False,
            native_latest=feature["native_latest"],
            scaled_latest=feature["scaled_latest"],
            native_valid_mean48=feature["native_valid_mean48"],
            scaled_valid_mean48=feature["scaled_valid_mean48"],
            native_last_minus_first=feature["native_last_minus_first"],
            scaled_last_minus_first=feature["scaled_last_minus_first"],
        )
        print("AUDIT_DONE", split, flush=True)
    tables = {
        "associations": pd.DataFrame(associations),
        "quintiles": pd.DataFrame(bins),
        "stability": pd.DataFrame(stability),
        "event_rates": pd.DataFrame(events),
        "cohorts": pd.DataFrame(qa),
        "baseline_response": pd.DataFrame(responses),
        "precursors": pd.concat(allprec),
        "missing_fallback": pd.concat(allmissing),
    }
    for name, frame in tables.items():
        frame.to_csv(dest / (name + ".csv"), index=False)
    write_json(
        dest / "frozen_quintile_and_regime_boundaries.json",
        dict(quintiles=boundaries, regimes=regime_bounds),
    )
    write_json(dest / "independent_target_replay.json", oracles)
    plot_tables = [
        (
            "quintiles",
            tables["quintiles"].query(
                "representation=='scaled_latest' and feature in ['M1','V1','Q2','B1']"
            ),
            dict(x="bin", y="target_mean", color="role", facet_col="feature"),
        ),
        (
            "precursors",
            tables["precursors"],
            dict(x="step", y="scaled_mean", color="event", facet_col="feature", facet_row="role"),
        ),
        (
            "stability_ci",
            tables["associations"].query("representation=='scaled_latest'"),
            dict(x="feature", y="daily_ic", color="role"),
        ),
        (
            "baseline_response",
            tables["baseline_response"].query("regime_channel=='ALL'"),
            dict(x="seed", y="prediction_sd", color="role"),
        ),
    ]
    for name, frame, options in plot_tables:
        fig = px.line(
            frame,
            x=options["x"],
            y=options["y"],
            color=options["color"],
            facet_col=options.get("facet_col"),
            facet_row=options.get("facet_row"),
            markers=True,
            title="P022 exploratory " + name,
        )
        fig.write_html(dest / (name + ".html"), include_plotlyjs=True)
    a = tables["associations"].query("representation=='scaled_latest'")
    brief = a[["role", "feature", "daily_ic", "ci_low", "ci_high"]].to_string(
        index=False, float_format=lambda x: f"{x:.5f}"
    )
    (out / "P022_FEATURE_PREDICTABILITY_TRIAGE.md").write_text(
        "# P022 bounded feature/event predictability triage\n\n"
        "Exploratory inner-training and checkpoint-selection "
        "validation only. No development row read, "
        "inference, classifier fit, optimizer step or change to "
        "frozen design. Correlated rows are not independent.\n\n"
        f"Inner q95|TG20|={recipe['q95_abs_y']:.12g}; NEG/NORMAL/POS counts={recipe['counts']}; "
        f"equal-session prevalences={recipe['prevalence']}. "
        "Strict inequalities define the two tails; equality is NORMAL.\n\n"
        "All16 published dimensionless channels retain their native "
        "economics and train-scaled units. "
        "See the bound P020 feature dictionary. Latest, valid48mean "
        "and endpoint difference use only completed input hours. "
        "Native missingness and scaled fallbacks are distinguished; "
        "no price/volume repair or clipping.\n\n"
        "Daily cross-sectional Spearman for the latest scaled "
        "channel; intervals resample entire calendar months "
        "(400 replicates,seed22042). Two-month sensitivity and "
        "all96representation/summary/channel comparisons "
        "are in associations.csv. These are descriptive intervals "
        "with no multiple-testing or alpha claim.\n\n"
        "```text\n" + brief + "\n```\n\n"
        "The [quintile plots](stage1/quintiles.html) use frozen "
        "inner-training cutoffs and explicit out-of-range/missing "
        "bins. "
        "[Precursors](stage1/precursors.html) show M1(open-close "
        "momentum),V1(log12h volatility),Q2(5/60daily-volume ratio) "
        "and B1(log high/low range), aligned48steps strictly before "
        "issuance. NORMAL controls are unmatched; "
        "calendar/stock mix and shared overlapping windows confound "
        "retrospective class differences.\n\n"
        "[Stability](stage1/stability.csv) retains all20stocks and three predeclared eras. "
        "[Saved model response](stage1/baseline_response.csv) "
        "separates T2/42 and123, train and validation, "
        "V1/Q2training-tercile regimes and signed/absolute event "
        "rankings. Small scores can still rank stocks. "
        "Regime subsets report pooled rank association; full20daily "
        "IC is reported only for the complete panel.\n\n"
        "[Cohorts](stage1/cohorts.csv) distinguish ranked tails from "
        "magnitude-range maxima, numerator from unique-origin MAD, "
        "and disjoint both/only/neither sets. Validation applies "
        "training numeric cutoffs. Exact threshold ties are "
        "retained and counts disclosed. These are retrospective "
        "label QA, never forecast-time eligibility.\n\n"
        "[Independent20-stock target "
        "replay](stage1/independent_target_replay.json) checks "
        "genuine same-session endpoints, "
        "returns,median,MAD,epsilon and TG20 on first/middle/last "
        "and largest-target origins in each role. "
        "[Missing/fallback](stage1/missing_fallback.csv) counts "
        "repeated-window cells explicitly.\n\n"
        "This bounded univariate audit neither proves nor disproves "
        "learnability, causality or economic usefulness. "
        "The four fixed objective experiments remain unchanged "
        "regardless of weak or unstable associations. "
        "Inner validation has already selected historical baseline "
        "checkpoints. One future seed per new arm "
        "cannot establish repeatability. No trading result or promotion follows.\n"
    )
    for r in json.loads((out / "preserved_references.json").read_text()):
        checked(r)
    write_json(
        out / "stage_01_feature_audit_gate.json",
        dict(
            status="PASS_AUDIT_COMPLETE",
            at=now(),
            design_sha256=digest(out / "frozen_design.json"),
            source_preserved=True,
            roles=["inner_train", "inner_validation"],
            no_development_rows=True,
            optimizer_steps=0,
            inference_steps=0,
            ledger=36,
            runtime_seconds=time.monotonic() - started,
            peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            files=[ref(p) for p in dest.iterdir() if p.is_file()],
            report=ref(out / "P022_FEATURE_PREDICTABILITY_TRIAGE.md"),
        ),
    )
    print("PASS_AUDIT_COMPLETE", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)
