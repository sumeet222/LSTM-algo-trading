"""Read-only consolidated diagnostics for the LP-deferred HF20 continuation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf20_ranking import YEARS, origin_ic
from .hf20_ranking_diagnostics import verify_exports
from .hf20_ranking_run import sha, write


def score_paths(out: Path) -> list[Path]:
    manifest = json.loads((out / "CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json").read_text())
    old = Path(manifest["old_namespace"])
    paths = sorted(old.glob("F21_S1_*/*_scores.parquet"))
    paths += [
        p
        for p in sorted(out.glob("*/*_scores.parquet"))
        if not p.parent.name.startswith("HF20-S1S2-") or (p.parent / "PASS.json").exists()
    ]
    return paths


def markdown(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for row in frame.to_dict("records"):
        lines.append(
            "| "
            + " | ".join(
                f"{row[c]:.7g}" if isinstance(row[c], float) else str(row[c]) for c in cols
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def cohort_tables(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """True units, subset error-energy identities, ranking attribution and pair conservation."""
    f = pd.read_parquet(path)
    role = str(f.role.iloc[0])
    model = str(f.model.iloc[0])
    year = int(f.year.iloc[0])
    th = json.loads((path.parent / f"{role}_thresholds.json").read_text())
    n = len(f) // 20
    r = f.return_4h.to_numpy().reshape(n, 20)
    score = f.score.to_numpy().reshape(n, 20)
    aw = f.actual_row_allocation.to_numpy()
    w = f.weight.to_numpy()
    obj = 20 * w * aw
    ids = f.origin_id.to_numpy()
    ticker_order = np.tile(np.arange(20), n)
    order = np.lexsort((ticker_order, ids, -abs(f.TG20.to_numpy())))
    num = abs(f.numerator.to_numpy()) > th["num95"]
    small = f.mad.to_numpy() < th["mad05"]
    masks = {
        "ALL": np.ones(len(f), bool),
        "TRAIN_EVENT95": abs(f.TG20.to_numpy()) > th["abs_y95"],
        "TRAIN_EVENT99": abs(f.TG20.to_numpy()) > th["abs_y99"],
        "NUM_ONLY": num & ~small,
        "MAD_ONLY": small & ~num,
        "BOTH": num & small,
        "NEITHER": ~(num | small),
        "FLOOR": f.mad.le(f.epsilon).to_numpy(),
    }
    for pct in (1, 5):
        chosen = np.zeros(len(f), bool)
        chosen[order[: len(f) * pct // 100]] = True
        masks[f"TARGET_RANK_TOP{pct}"] = chosen
        masks[f"TARGET_RANK_TOP{pct}_COMPLEMENT"] = ~chosen
    for label in ("TRAIN_EVENT95", "TRAIN_EVENT99", "TARGET_RANK_TOP1", "TARGET_RANK_TOP5"):
        for sign in (-1, 1):
            masks[label + ("_POS" if sign == 1 else "_NEG")] = masks[label] & (
                f.TG20.to_numpy() * sign > 0
            )
    ar = f.actual_rank.to_numpy().reshape(n, 20)
    pr = f.prediction_rank.to_numpy().reshape(n, 20)
    ar = ar - ar.mean(1)[:, None]
    pr = pr - pr.mean(1)[:, None]
    den = np.sqrt((ar * ar).sum(1) * (pr * pr).sum(1))
    valid = den > 0
    days = f.session_date_et.to_numpy()[::20]
    counts = pd.Series(days[valid]).value_counts()
    day_count = len(counts)
    effective = np.array([1 / (day_count * counts[d]) if ok else 0 for d, ok in zip(days, valid)])
    ic_alloc = (
        effective[:, None]
        * np.divide(ar * pr, den[:, None], out=np.zeros_like(ar), where=den[:, None] > 0)
    ).reshape(-1)
    cohorts = []
    strata = []
    pair_rows = []
    inverse = f.inverse_TG20.to_numpy() if model == "T2R" else None
    if inverse is not None:
        y = f.TG20.to_numpy()
        e = inverse - y
        common = np.repeat(e.reshape(n, 20).mean(1), 20)
        center = e - common
    for label, mask in masks.items():
        row = dict(
            year=year,
            model=model,
            role=role,
            cohort=label,
            rows=int(mask.sum()),
            origins=f.loc[mask, "origin_id"].nunique(),
            sessions=f.loc[mask, "session_date_et"].nunique(),
            weight_mass=float(w[mask].sum()),
            actual_objective_contribution=float(obj[mask].sum()) if np.isfinite(aw).all() else None,
            rank_ic_contribution=float(ic_alloc[mask].sum()),
            relative_side_hit_mass=float(w[mask] @ f.relative_side_hit.to_numpy()[mask]),
        )
        if inverse is not None:
            energies: dict[str, float] = dict(
                original_MSE_contribution=float(w[mask] @ (e[mask] ** 2)),
                target_energy=float(w[mask] @ (y[mask] ** 2)),
                forecast_energy=float(w[mask] @ (inverse[mask] ** 2)),
                alignment=float(w[mask] @ (2 * y[mask] * inverse[mask])),
                common_error=float(w[mask] @ (common[mask] ** 2)),
                centered_error=float(w[mask] @ (center[mask] ** 2)),
                subset_cross_term=float(w[mask] @ (2 * common[mask] * center[mask])),
            )
            row.update(energies)
            np.testing.assert_allclose(
                energies["original_MSE_contribution"],
                energies["target_energy"] + energies["forecast_energy"] - energies["alignment"],
                rtol=1e-11,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                energies["original_MSE_contribution"],
                energies["common_error"]
                + energies["centered_error"]
                + energies["subset_cross_term"],
                rtol=1e-11,
                atol=1e-12,
            )
        cohorts.append(row)
        for group in ("ticker", "static_publisher_sector_proxy", "month", "quality", "fallback"):
            group_values = f.session_date_et.str[:7] if group == "month" else f[group]
            for value, indices in pd.Series(np.flatnonzero(mask), index=group_values[mask]).groupby(
                level=0
            ):
                ix = indices.to_numpy(int)
                strata.append(
                    dict(
                        year=year,
                        model=model,
                        role=role,
                        cohort=label,
                        dimension=group,
                        value=str(value),
                        rows=len(ix),
                        origins=f.iloc[ix].origin_id.nunique(),
                        sessions=f.iloc[ix].session_date_et.nunique(),
                        weight_mass=float(w[ix].sum()),
                        objective_contribution=float(obj[ix].sum())
                        if np.isfinite(aw).all()
                        else None,
                        IC_contribution=float(ic_alloc[ix].sum()),
                        original_MSE_contribution=float(w[ix] @ (e[ix] ** 2))
                        if inverse is not None
                        else None,
                    )
                )
    i, j = np.triu_indices(20, 1)
    direction = np.sign(r[:, i] - r[:, j])
    untied = direction != 0
    count = untied.sum(1)
    terms = np.logaddexp(0, -direction * (score[:, i] - score[:, j])) * untied
    if model == "PW":
        allocation = np.zeros_like(score)
        for k, (a, b) in enumerate(zip(i, j)):
            half = terms[:, k] / (2 * count)
            allocation[:, a] += half
            allocation[:, b] += half
        np.testing.assert_allclose(
            allocation, f.actual_row_allocation.to_numpy().reshape(n, 20), rtol=3e-7, atol=1e-8
        )
    event = masks["TRAIN_EVENT95"].reshape(n, 20)
    pred = np.sign(score[:, i] - score[:, j])
    credit = ((pred == direction) + 0.5 * (pred == 0)) * untied
    ow = w.reshape(n, 20).sum(1)
    for name, mask in [
        ("BOTH_EXTREME", event[:, i] & event[:, j]),
        ("ONE_EXTREME", event[:, i] ^ event[:, j]),
        ("NEITHER_EXTREME", ~(event[:, i] | event[:, j])),
    ]:
        mass = float(ow @ ((mask * untied).sum(1) / count))
        pair_rows.append(
            dict(
                year=year,
                model=model,
                role=role,
                pair_type=name,
                weighted_pair_mass=mass,
                concordance_contribution=float(ow @ ((credit * mask).sum(1) / count)),
                PW_loss_contribution=float(ow @ ((terms * mask).sum(1) / count))
                if model == "PW"
                else None,
                weighted_absolute_score_gap=float(
                    ow @ ((abs(score[:, i] - score[:, j]) * mask * untied).sum(1) / count)
                ),
            )
        )
    # All fitted families keep identical target-defined cohorts; no per-model error-based selection.
    f["example_cohort"] = "TARGET_RANK_TOP1"
    examples = f.iloc[order[: len(f) // 100]].copy()
    return pd.DataFrame(cohorts), pd.DataFrame(strata), pd.DataFrame(pair_rows), examples


def collective(out: Path) -> None:
    paths = score_paths(out)
    write(
        out / "COLLECTIVE_INDEPENDENT_VERIFICATION.json",
        dict(status="PASS", files=verify_exports(out, paths)),
    )
    metrics = [
        json.loads(
            (
                p.parent
                / (str(pd.read_parquet(p, columns=["role"]).role.iloc[0]) + "_metrics.json")
            ).read_text()
        )
        for p in paths
    ]
    f = pd.DataFrame(metrics)
    f.to_csv(out / "all_role_metrics.csv", index=False)
    oos = f.loc[f.role.eq("oos")].copy()
    oos.to_csv(out / "four_fold_OOS_metrics.csv", index=False)
    summary = []
    for model, g in oos.groupby("model"):
        complete = set(g.year) == set(YEARS) and len(g) == 4
        row = dict(
            model=model,
            available_years=len(g),
            complete_four_years=complete,
            daily_ic=float(g.daily_ic.mean()) if complete and g.daily_ic.notna().all() else None,
        )
        for key in (
            "pair_concordance",
            "normalized_rank_mse",
            "top4",
            "bottom4",
            "defined_origin_fraction",
        ):
            row[key] = float(g[key].mean()) if complete else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out / "equal_year_summary.csv", index=False)
    cc = []
    ss = []
    pp = []
    ee = []
    for path in paths:
        c, s, p, e = cohort_tables(path)
        cc.append(c)
        ss.append(s)
        pp.append(p)
        ee.append(e)
    for name, frames in [
        ("cohort_objective_and_error_decomposition", cc),
        ("cohort_stock_month_sector_quality", ss),
        ("cohort_pair_concordance_and_PW", pp),
        ("original_target_extreme_examples", ee),
    ]:
        pd.concat(frames, ignore_index=True).to_csv(out / (name + ".csv"), index=False)
    paired = []
    for year in YEARS:
        models = {
            str(a.model.iloc[0]): a.sort_values(["origin_id", "ticker"]).reset_index(drop=True)
            for path in paths
            if path.name == "oos_scores.parquet"
            for a in [pd.read_parquet(path)]
            if int(a.year.iloc[0]) == year
        }
        for control in ("P", "LR", "T2R"):
            if control not in models:
                continue
            b = models[control]
            for model, a in models.items():
                pd.testing.assert_frame_equal(
                    a[["origin_id", "ticker", "return_4h"]],
                    b[["origin_id", "ticker", "return_4h"]],
                    check_exact=True,
                )
                y = a.return_4h.to_numpy().reshape(-1, 20)
                ar = a.score.to_numpy().reshape(-1, 20)
                br = b.score.to_numpy().reshape(-1, 20)
                days = a.session_date_et.to_numpy()[::20]
                delta = origin_ic(y, ar) - origin_ic(y, br)
                daily = (
                    pd.DataFrame(dict(day=days, delta=delta)).groupby("day").delta.mean().dropna()
                )
                month = daily.groupby(lambda d: d[:7]).agg(["sum", "count"])
                interval = None
                if len(month):
                    draw = np.random.default_rng(22042).integers(len(month), size=(400, len(month)))
                    boot = month["sum"].to_numpy()[draw].sum(1) / month["count"].to_numpy()[
                        draw
                    ].sum(1)
                    interval = np.quantile(boot, [0.025, 0.975]).tolist()
                paired.append(
                    dict(
                        year=year,
                        model=model,
                        control=control,
                        daily_IC_delta=float(daily.mean()) if len(daily) else None,
                        matched_defined_origins=int(np.isfinite(delta).sum()),
                        month_block_sensitivity_interval=interval,
                        significance_test=False,
                    )
                )
    write(out / "paired_month_block_sensitivity.json", paired)
    traces = []
    for path in out.glob("HF20-S1S2-*/PASS.json"):
        a = json.loads(path.read_text())
        traces.append(dict(run_id=a["run_id"], seconds=a["seconds"], **a["selector"]))
    pd.DataFrame(traces).to_csv(out / "neural_selection_and_runtime.csv", index=False)
    gradient = []
    epochs = []
    for dest in out.glob("HF20-S1S2-*"):
        for path in dest.glob("*_batches.csv"):
            a = pd.read_csv(path)
            a["run_id"] = dest.name
            if not np.isfinite(
                a[
                    ["preclip", "postclip", "update_norm", "parameter_norm", "online_loss"]
                ].to_numpy()
            ).all():
                raise ValueError("NONFINITE_TRAINING_TELEMETRY")
            if a.postclip.gt(1.000003).any():
                raise ValueError("GRADIENT_CAP_VIOLATION")
            gradient.append(a)
        for path in sorted(dest.glob("calibration_???.json")) + sorted(dest.glob("refit_???.json")):
            a = json.loads(path.read_text())
            a.pop("selector", None)
            a["run_id"] = dest.name
            epochs.append(a)
    if gradient:
        g = pd.concat(gradient, ignore_index=True)
        g.groupby(["run_id", "phase"])[
            ["preclip", "postclip", "update_norm", "parameter_norm", "online_loss"]
        ].agg(["count", "min", "median", "max"]).to_csv(out / "gradient_clip_update_summary.csv")
    pd.DataFrame(epochs).to_csv(out / "complete_epoch_trace.csv", index=False)
    import plotly.graph_objects as go

    fig = go.Figure()
    for model, g in oos.groupby("model"):
        if model != "N0":
            fig.add_trace(go.Scatter(x=g.year, y=g.daily_ic, name=str(model), mode="lines+markers"))
    fig.update_layout(
        title="Retrospective annual OOS daily Rank IC; LP deferred; no trading claim",
        xaxis_title="Year",
        yaxis_title="Daily Rank IC",
    )
    fig.write_html(out / "annual_rank_IC.html", include_plotlyjs=True)
    for title, models in [
        ("S1_FOUR_FOLD_RANKING_BASELINES", ["N0", "N1", "N2", "P", "LR"]),
        ("S2_FOUR_FOLD_LSTM_RANKING_COMPARISON", ["T2R", "NR", "PW"]),
    ]:
        (out / (title + ".md")).write_text(
            "# "
            + title
            + "\n\nRetrospective OOS. LP DEFERRED_AFTER_PRIOR_FAILURE; constants undefined.\n\n"
            + markdown(
                oos.loc[
                    oos.model.isin(models),
                    [
                        "year",
                        "model",
                        "daily_ic",
                        "pair_concordance",
                        "normalized_rank_mse",
                        "defined_origin_fraction",
                    ],
                ]
            )
        )
    write(
        out / "COLLECTIVE_TABLES_RECEIPT.json",
        dict(
            status="PASS_READONLY_TABLES",
            score_files=len(paths),
            oos_models=len(oos),
            LP="DEFERRED_AFTER_PRIOR_FAILURE",
            source_files=[dict(path=str(p), sha256=sha(p)) for p in paths],
        ),
    )
