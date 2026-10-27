"""Saved-score verification, same-task controls and compact S5/S9 reports."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import digest
from .hf20_ranking_continue_report import markdown
from .hf20_s4_closeout import block_interval, paired
from .hf20_s4_data import ROLES
from .hf20_s5s9 import RUNS, S4, Data
from .hf20_s5s9_metrics import control_raw, fit_control, make_frame, metrics


def loss_deltas(f: pd.DataFrame, g: pd.DataFrame, arm: str) -> dict[str, np.ndarray]:
    """Same-key row contributions; never compare losses across task units."""
    np.testing.assert_array_equal(f[["origin_id", "ticker"]], g[["origin_id", "ticker"]])
    out = {"proper_loss": (f.actual_loss - g.actual_loss).to_numpy()}
    if arm == "MAG":
        a = f.prediction_A - f.return_4h.abs()
        b = g.prediction_A - f.return_4h.abs()
        out.update(
            magnitude_MAE=(abs(a) - abs(b)).to_numpy(), magnitude_MSE=(a * a - b * b).to_numpy()
        )
    elif arm == "EVENT":
        event = f.event_class.ne(1).to_numpy().astype(float)
        a = np.clip(f.p_ANY.to_numpy(), 1e-12, 1 - 1e-12)
        b = np.clip(g.p_ANY.to_numpy(), 1e-12, 1 - 1e-12)
        out.update(
            ANY_Brier=(a - event) ** 2 - (b - event) ** 2,
            ANY_log_loss=-event * np.log(a)
            - (1 - event) * np.log1p(-a)
            + event * np.log(b)
            + (1 - event) * np.log1p(-b),
        )
    elif arm == "QUANTILE":
        for level, tau in [("05", 0.05), ("50", 0.5), ("95", 0.95)]:
            a = f.Z - f["quantiles_z_" + level]
            b = f.Z - g["quantiles_z_" + level]
            out["pinball_" + level] = (
                np.maximum(tau * a, (tau - 1) * a) - np.maximum(tau * b, (tau - 1) * b)
            ).to_numpy()
    return out


def verify_frame(f: pd.DataFrame, arm: str, recipe: dict) -> None:
    """Independent NumPy loss oracle, full panels and strict pre-2025 source boundary."""
    if (
        f.session_date_et.ge("2025-01-01").any()
        or f.duplicated(["origin_id", "ticker"]).any()
        or f.groupby("origin_id").size().ne(20).any()
    ):
        raise ValueError("S5S9_EXPORT_KEYS_OR_SCOPE")
    y, z = f.TG20.to_numpy(), f.Z.to_numpy()
    if arm == "META-T2R":
        expected = (f.raw_0.to_numpy() - z) ** 2
    elif arm == "MAG":
        expected = (f.raw_0 - np.log1p(abs(f.return_4h) / recipe["magnitude_scale"])) ** 2
    elif arm == "EVENT":
        raw = f[[f"raw_{k}" for k in range(3)]].to_numpy(dtype=float)
        m = raw.max(1)
        cls = np.where(y < -recipe["event_cutoff"], 0, np.where(y > recipe["event_cutoff"], 2, 1))
        expected = m + np.log(np.exp(raw - m[:, None]).sum(1)) - raw[np.arange(len(raw)), cls]
        np.testing.assert_allclose(f.p_NEG + f.p_NORMAL + f.p_POS, 1, atol=1e-12, rtol=1e-11)
    else:
        raw = f[[f"raw_{k}" for k in range(3)]].to_numpy(dtype=float)
        q = np.column_stack(
            [
                raw[:, 0] - np.logaddexp(0, raw[:, 1]),
                raw[:, 0],
                raw[:, 0] + np.logaddexp(0, raw[:, 2]),
            ]
        )
        error = z[:, None] - q
        tau = np.array([0.05, 0.5, 0.95])
        expected = np.maximum(tau * error, (tau - 1) * error).mean(1)
    np.testing.assert_allclose(f.actual_loss, expected, atol=1e-12, rtol=1e-11)
    np.testing.assert_allclose(
        f.TG20, f.numerator / (f.mad + recipe["epsilon"]), atol=1e-12, rtol=1e-11
    )


def strata(f: pd.DataFrame, arm: str) -> pd.DataFrame:
    frames = []
    for field in ("slot", "category", "ticker", "quality", "fallback", "age_band", "month"):
        for key, g in f.groupby(field):
            # Normalize within each session after filtering, retaining equal stocks/origins.
            g = g.copy()
            g["weight"] = 1 / (
                g.session_date_et.nunique()
                * g.groupby("session_date_et").origin_id.transform("nunique")
                * g.groupby("origin_id").ticker.transform("size")
            )
            frames.append(dict(field=field, group=str(key), **metrics(g, arm)))
    return pd.DataFrame(frames)


def cohorts(f: pd.DataFrame, arm: str, recipe: dict) -> pd.DataFrame:
    y = abs(f.TG20.to_numpy())
    target = abs(f.return_4h.to_numpy()) if arm == "MAG" else y
    threshold = recipe["abs_r95"] if arm == "MAG" else recipe["tail_y95"]
    threshold99 = recipe["abs_r99"] if arm == "MAG" else recipe["tail_y99"]
    num = abs(f.numerator.to_numpy()) > recipe["num95"]
    mad = f.mad.to_numpy() < recipe["mad05"]
    masks = dict(
        ALL=np.ones(len(f), bool),
        TRAIN_TASK95=target > threshold,
        TRAIN_TASK99=target > threshold99,
        POS=f.TG20.gt(0).to_numpy(),
        NEG=f.TG20.lt(0).to_numpy(),
        NUM_ONLY=num & ~mad,
        MAD_ONLY=mad & ~num,
        BOTH=num & mad,
        NEITHER=~num & ~mad,
        FLOOR=f.mad.le(recipe["epsilon"]).to_numpy(),
    )
    for name, value in (("TARGET", target), ("ERROR", f.actual_loss.to_numpy())):
        for pct in (1, 5):
            order = np.argsort(-value, kind="stable")
            mask = np.zeros(len(f), bool)
            mask[order[: len(f) * pct // 100]] = True
            masks[f"{name}_TOP{pct}"] = mask
            masks[f"{name}_TOP{pct}_COMPLEMENT"] = ~mask
    mass = f.weight.to_numpy()
    loss = f.actual_loss.to_numpy()
    total = float(mass @ loss)
    result = []
    for name, mask in masks.items():
        result.append(
            dict(
                cohort=name,
                rows=int(mask.sum()),
                origins=f.loc[mask, "origin_id"].nunique(),
                sessions=f.loc[mask, "session_date_et"].nunique(),
                weight_mass=float(mass[mask].sum()),
                actual_loss_contribution=float(mass[mask] @ loss[mask]),
                actual_loss_share=float(mass[mask] @ loss[mask] / total),
            )
        )
    return pd.DataFrame(result)


def export(
    data: Data, year: int, role: str, arm: str, raw: np.ndarray, dest: Path, recipe: dict
) -> None:
    pos = data.base.positions(year, role)
    rows = data.base.rows.iloc[pos]
    _, r, y = data.base.arrays(pos)
    f = make_frame(rows, data.base.symbols, r, y, raw, arm, data.task_recipe, role)
    for name, value in data.base.quality_fields(pos).items():
        f[name] = value
    f["quality"] = np.where(
        (f.assumed_zero_minute_count + f.price_proxy_minute_count) > 0,
        "SOURCE_FLAGGED",
        "NO_LISTED_SOURCE_FLAG",
    )
    f["fallback"] = np.where(f.feature_fallback_cells > 0, "ANY", "NONE")
    f["month"] = f.session_date_et.str[:7]
    f["age_band"] = pd.cut(
        f.max_terminal_price_age_minutes,
        [-np.inf, 0, 1, 2, 5, np.inf],
        labels=["ZERO", "LE1", "LE2", "LE5", "GT5"],
    ).astype(str)
    f["sigma_proxy"] = data.volatility(pos).ravel()
    f["run_id"], f["year"] = dest.name, year
    from .hf20_s5s9_run import code_hash

    f["execution_sha256"] = code_hash()
    f["S4_contract_sha256"] = digest(S4 / "S4_FROZEN_EXPERIMENT_CARD.json")
    binding = dest / ("calibration_binding.json" if role in ROLES[:2] else "refit_binding.json")
    f["checkpoint_sha256"] = json.loads(binding.read_text())["checkpoint_sha256"]
    f["task_recipe_sha256"] = digest(
        dest / ("inner_target_recipe.json" if role in ROLES[:2] else "refit_target_recipe.json")
    )
    f["S4_recipe_sha256"] = digest(
        S4 / f"F{year % 100}_{'inner' if role in ROLES[:2] else 'refit'}_recipe.json"
    )
    f["last_input_end_utc"] = np.repeat(
        data.base.grid.hour_end_utc.iloc[rows.entry_index.to_numpy(int)].to_numpy(), 20
    )
    if (
        not pd.to_datetime(f.last_input_end_utc, utc=True)
        .le(pd.to_datetime(f.entry_end_utc, utc=True))
        .all()
    ):
        raise ValueError("S5_FUTURE_INPUT")
    verify_frame(f, arm, data.task_recipe)
    f.to_parquet(dest / f"{role}_scores.parquet", index=False)
    (dest / f"{role}_metrics.json").write_text(
        json.dumps(metrics(f, arm), indent=2, allow_nan=True) + "\n"
    )
    strata(f, arm).to_csv(dest / f"{role}_strata.csv", index=False)
    cohorts(f, arm, dict(data.task_recipe, **recipe)).to_csv(
        dest / f"{role}_cohorts.csv", index=False
    )


def baseline_event(out: Path, key: str, status: str, *, prefix: bool = False) -> None:
    from .hf20_s5s9_run import ensure

    ensure(out)
    path = out / ("PREFIX_ATTEMPTS.jsonl" if prefix else "BASELINE_ATTEMPTS.jsonl")
    old = [json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    if status == "STARTED":
        if len([x for x in old if x["status"] == "STARTED"]) >= (32 if prefix else 64) or any(
            x["key"] == key for x in old
        ):
            raise ValueError("S9_BASELINE_BUDGET_NO_RETRY")
    elif not old or old[-1]["key"] != key or old[-1]["status"] != "STARTED":
        raise ValueError("S9_BASELINE_NOT_PENDING")
    with path.open("a") as f:
        f.write(json.dumps(dict(key=key, status=status)) + "\n")


def finish_run(
    data: Data, year: int, arm: str, dest: Path, recipes: dict, *, dry: bool = False
) -> None:
    comparisons = []
    all_metrics = []
    for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
        data.phase(year, phase, recipes[phase])
        fit_pos = data.base.positions(year, roles[0])
        fit_rows = data.base.rows.iloc[fit_pos]
        if arm == "META-T2R":
            from .hf20_s4_diagnostics import export as old_export
            from .hf20_s4_diagnostics import verify as old_verify
            from .hf20_s5s9_run import code_hash

            # Preserve S4's complete objective-specific diagnostic contract in a nested folder.
            legacy = dest / "ranking"
            legacy.mkdir(exist_ok=True)
            binding = "calibration_binding.json" if phase == "inner" else "refit_binding.json"
            (legacy / binding).write_bytes((dest / binding).read_bytes())
            (dest / f"F{year % 100}_{phase}_recipe.json").write_bytes(
                (S4 / f"F{year % 100}_{phase}_recipe.json").read_bytes()
            )
            for role in roles:
                data.base.rows.iloc[data.base.positions(year, role)].to_csv(
                    dest / f"F{year % 100}_{role}_indices.csv", index=False
                )
                f = pd.read_parquet(dest / f"{role}_scores.parquet")
                old_export(
                    data.base,
                    year,
                    role,
                    "T2R",
                    f.raw_0.to_numpy().reshape(-1, 20),
                    legacy,
                    code_hash(),
                )
                for ref, name in [
                    ("T2R", f"HF20-S4A-F{year % 100}-H4-T2R-S42"),
                    ("N1", f"F{year % 100}_S4_N1"),
                    ("P", f"F{year % 100}_S4_P"),
                ]:
                    g = pd.read_parquet(S4 / name / f"{role}_scores.parquet")
                    comparisons.extend(dict(role=role, **v) for v in paired(f, g, ref))
            if phase == "refit":
                old_verify(data.base, year, legacy, rehearsal=dry)
        else:
            r = data.base.returns[fit_pos]
            from .hf20_s5s9 import target_y

            y = target_y(r, data.base.recipe["epsilon"])
            sigma = data.volatility(fit_pos)
            kinds = ("GLOBAL", "STOCK", "VOL")
            for kind in kinds:
                fitted = not (arm == "MAG" and kind == "VOL")
                key = f"{dest.name}/{phase}/{kind}"
                if dry:
                    value = (
                        0.0
                        if arm == "MAG"
                        else [0.025, 0.95, 0.025]
                        if arm == "EVENT"
                        else [-1.0, 0.0, 1.0]
                    )
                    control = dict(
                        value=([value] * 4 if arm == "EVENT" and kind == "VOL" else value),
                        rehearsal_only=True,
                    )
                    if arm == "EVENT" and kind == "VOL":
                        control["cuts"] = [-10.0, -5.0, 0.0]
                elif fitted:
                    from .hf20_s5s9_run import resources

                    resources(dest.parent, 20_000_000)
                    baseline_event(dest.parent, key, "STARTED")
                    control = fit_control(
                        r,
                        y,
                        sigma,
                        fit_rows.session_date_et.to_numpy(),
                        arm,
                        data.task_recipe,
                        kind,
                    )
                    baseline_event(dest.parent, key, "COMPLETED")
                else:
                    control = {}
                (dest / f"{phase}_{kind}_control.json").write_text(
                    json.dumps(control, indent=2) + "\n"
                )
                for role in roles:
                    f = pd.read_parquet(dest / f"{role}_scores.parquet")
                    pos = data.base.positions(year, role)
                    raw = control_raw(control, data.volatility(pos), arm, kind, data.task_recipe)
                    g = make_frame(
                        data.base.rows.iloc[pos],
                        data.base.symbols,
                        data.base.returns[pos],
                        f.TG20.to_numpy().reshape(-1, 20),
                        raw,
                        arm,
                        data.task_recipe,
                        role,
                    )
                    verify_frame(g, arm, data.task_recipe)
                    m = metrics(g, arm)
                    m["year"] = year
                    all_metrics.append(dict(role=role, model=kind, **m))
                    # Fixed observations and equal-session weighted losses for paired intervals.
                    for metric, delta in loss_deltas(f, g, arm).items():
                        d = (
                            pd.DataFrame(dict(day=f.session_date_et, delta=delta))
                            .groupby("day")
                            .delta.mean()
                        )
                        comparisons.append(
                            dict(
                                role=role,
                                reference=kind,
                                group="ALL",
                                metric=metric,
                                **block_interval(d),
                            )
                        )
                    # Store each target once in the canonical neural-role bundle.
                    # Controls retain exact keys, forecasts/loss and both content bindings.
                    g["canonical_target_sha256"] = digest(dest / f"{role}_scores.parquet")
                    g["control_recipe_sha256"] = digest(dest / f"{phase}_{kind}_control.json")
                    keep = [
                        c
                        for c in g
                        if isinstance(c, str)
                        and (
                            c
                            in (
                                "origin_id",
                                "ticker",
                                "actual_loss",
                                "canonical_target_sha256",
                                "control_recipe_sha256",
                            )
                            or c.startswith(("raw_", "prediction_", "p_", "quantiles_"))
                        )
                    ]
                    g[keep].to_parquet(dest / f"{role}_{kind}_control_scores.parquet", index=False)
        for role in roles:
            f = pd.read_parquet(dest / f"{role}_scores.parquet")
            verify_frame(f, arm, data.task_recipe)
            value = metrics(f, arm)
            value["year"] = year
            if arm == "META-T2R":
                value.update(json.loads((dest / "ranking" / f"{role}_metrics.json").read_text()))
                value.pop("role", None)
                value.pop("model", None)
            all_metrics.append(dict(role=role, model="NEURAL", **value))
    pd.DataFrame(comparisons).to_csv(dest / "matched_baseline_differences.csv", index=False)
    pd.DataFrame(all_metrics).to_csv(dest / "model_and_control_metrics.csv", index=False)
    report = (
        f"# {dest.name}\n\n"
        + (
            "UNTRAINED_REHEARSAL. No fitted controls or scientific results.\n\n"
            if dry
            else "TECHNICAL_PASS. All four roles verified; OOS remains exploratory.\n\n"
        )
        + markdown(pd.DataFrame(all_metrics))
        + "\n\n"
        + markdown(pd.DataFrame(comparisons))
        + "\n\nAll diagnostic files:\n\n"
    )
    report += "\n".join(
        f"- [{p.relative_to(dest)}]({p.relative_to(dest)})"
        for p in sorted(dest.rglob("*"))
        if p.is_file()
    )
    (dest / "RUN_DIAGNOSTICS.md").write_text(report + "\n")


def closeout(out: Path) -> None:
    roster = []
    m = []
    d = []
    trace = []
    paired_daily = []
    for run in RUNS:
        dest = out / run
        passed = (dest / "PASS.json").exists()
        roster.append(
            dict(
                run_id=run,
                status="PASS"
                if passed
                else "FAILED"
                if (dest / "FAILURE.json").exists()
                else "NOT_RUN",
                report=str(dest / "RUN_DIAGNOSTICS.md"),
            )
        )
        if not passed:
            continue
        gate = json.loads((dest / "PASS.json").read_text())
        for name, sha in gate["files"].items():
            if digest(Path(name)) != sha:
                raise ValueError("S5S9_CLOSED_RUN_CHANGED")
        m.append(pd.read_csv(dest / "model_and_control_metrics.csv").assign(run_id=run))
        d.append(pd.read_csv(dest / "matched_baseline_differences.csv").assign(run_id=run))
        f = pd.read_parquet(dest / "oos_scores.parquet")
        arm = str(f.arm.iloc[0])
        year = int(f.year.iloc[0])
        if arm == "META-T2R":
            references = [
                ("S4_T2R", S4 / f"HF20-S4A-F{year % 100}-H4-T2R-S42/oos_scores.parquet"),
                ("N1", S4 / f"F{year % 100}_S4_N1/oos_scores.parquet"),
                ("P", S4 / f"F{year % 100}_S4_P/oos_scores.parquet"),
            ]
        else:
            references = [
                (k, dest / f"oos_{k}_control_scores.parquet") for k in ("GLOBAL", "STOCK", "VOL")
            ]
        for reference, path in references:
            g = pd.read_parquet(path)
            np.testing.assert_array_equal(f[["origin_id", "ticker"]], g[["origin_id", "ticker"]])
            if arm == "META-T2R":
                from .hf20_ranking import origin_ic

                r = f.return_4h.to_numpy().reshape(-1, 20)
                delta = origin_ic(r, f.score.to_numpy().reshape(-1, 20)) - origin_ic(
                    r, g.score.to_numpy().reshape(-1, 20)
                )
                per = (
                    pd.DataFrame(
                        dict(session_date_et=f.session_date_et.to_numpy()[::20], difference=delta)
                    )
                    .groupby("session_date_et")
                    .difference.mean()
                )
            else:
                for metric, delta in loss_deltas(f, g, arm).items():
                    per = (
                        pd.DataFrame(dict(session_date_et=f.session_date_et, difference=delta))
                        .groupby("session_date_et")
                        .difference.mean()
                    )
                    paired_daily.append(
                        pd.DataFrame(
                            dict(
                                session_date_et=per.index,
                                difference=per.to_numpy(),
                                year=year,
                                arm=arm,
                                reference=reference,
                                metric=metric,
                            )
                        )
                    )
                continue
            paired_daily.append(
                pd.DataFrame(
                    dict(
                        session_date_et=per.index,
                        difference=per.to_numpy(),
                        year=year,
                        arm=arm,
                        reference=reference,
                        metric="daily_rank_ic",
                    )
                )
            )
        for p in sorted(dest.glob("*.json")):
            if p.stem.startswith(("calibration_", "refit_")) and p.stem[-3:].isdigit():
                trace.append(dict(run_id=run, **json.loads(p.read_text())))
    pd.DataFrame(roster).to_csv(out / "RUN_INVENTORY.csv", index=False)
    if m:
        pd.concat(m, ignore_index=True).to_csv(out / "S5_S9_MODEL_METRICS.csv", index=False)
    if d:
        pd.concat(d, ignore_index=True).to_csv(
            out / "S5_S9_MATCHED_BASELINE_DIFFERENCES.csv", index=False
        )
    pd.json_normalize(trace).to_csv(out / "S5_S9_TRAINING_TRACE.csv", index=False)
    effects = []
    if paired_daily:
        daily = pd.concat(paired_daily, ignore_index=True)
        daily.to_csv(out / "S5_S9_OOS_PAIRED_SESSION_DIFFERENCES.csv", index=False)
        for (arm, reference, metric), frame in daily.groupby(["arm", "reference", "metric"]):
            rng = np.random.default_rng(22042)
            draws = []
            annual = []
            for year, g in frame.groupby("year"):
                value = g.set_index("session_date_et").difference
                effects.append(
                    dict(
                        arm=arm,
                        reference=reference,
                        metric=metric,
                        year=year,
                        **block_interval(value),
                    )
                )
                bins = g.groupby(g.session_date_et.str[:7]).difference.agg(["sum", "count"])
                ix = rng.integers(len(bins), size=(400, len(bins)))
                draws.append(
                    bins["sum"].to_numpy()[ix].sum(1) / bins["count"].to_numpy()[ix].sum(1)
                )
                annual.append(float(g.difference.mean()))
            if len(annual) == 4:
                lo, hi = np.quantile(np.mean(draws, axis=0), [0.025, 0.975])
                effects.append(
                    dict(
                        arm=arm,
                        reference=reference,
                        metric=metric,
                        year="EQUAL_YEAR",
                        mean=float(np.mean(annual)),
                        low=float(lo),
                        high=float(hi),
                        sessions=len(frame),
                        months=frame.session_date_et.str[:7].nunique(),
                    )
                )
        pd.DataFrame(effects).to_csv(out / "S5_S9_PAIRED_OOS_UNCERTAINTY.csv", index=False)
    complete = all((out / run / "PASS.json").exists() for run in RUNS)
    body = "# S5 + S9 research review\n\n" + (
        "All 16 authorized lifecycles passed numerical gates; "
        "final browser review remains required.\n\n"
        if complete
        else "NOT_ALL_SIXTEEN_COMPLETED. Missing runs are explicitly listed.\n\n"
    )
    body += (
        "S5 differences are RankIC (higher is better). S9 differences are same-target "
        "proper loss (lower is better). Units differ between tasks. Whole-month intervals "
        "are descriptive after repeated research inspection. AP, calibration, magnitude "
        "accuracy and quantile coverage must be interpreted separately.\n\n"
    )
    if m:
        allm = pd.concat(m, ignore_index=True)
        oos = allm[allm.role.eq("oos")]
        for arm, g in oos.groupby("arm"):
            body += f"## {arm}\n\n" + markdown(g) + "\n\n"
            if len(g.run_id.unique()) == 4:
                means = g.groupby("model").mean(numeric_only=True).reset_index()
                body += "Equal-year descriptive means:\n\n" + markdown(means) + "\n\n"
    body += "Paired primary uncertainty:\n\n" + markdown(pd.DataFrame(effects)) + "\n\n"
    body += (
        "Technical PASS does not establish scientific support. No seed, threshold, "
        "architecture, signed-ranking fusion, portfolio or protected confirmation "
        "follows automatically.\n\n[Complete run index](S5_S9_DIAGNOSTIC_INDEX.md) · "
        "[Dashboard](S5_S9_VISUAL_DIAGNOSTICS.html).\n"
    )
    (out / "S5_S9_FINAL_RESEARCH_DECISION.md").write_text(body)
    links = [
        "# S5 + S9 complete diagnostic index\n",
        markdown(pd.DataFrame(roster)),
        "\n## Every run and diagnostic artifact\n",
    ]
    for row in roster:
        run = row["run_id"]
        links.append(f"### {run}: {row['status']}\n")
        if row["status"] == "PASS":
            links.append(
                f"[Model view](S5_S9_VISUAL_DIAGNOSTICS.html?view={run}) · "
                f"[PNG after final renderer](plots/{run}.png)\n"
            )
        links.extend(
            f"- [{p.relative_to(out)}]({p.relative_to(out)})"
            for p in sorted((out / run).rglob("*"))
            if p.is_file()
        )
    (out / "S5_S9_DIAGNOSTIC_INDEX.md").write_text("\n".join(links) + "\n")
    from .hf20_s4_clock import month_guard
    from .hf20_s5s9_run import JOURNAL, ensure, resources

    ensure(out)
    history = [json.loads(s) for s in JOURNAL.read_text().splitlines()]
    source = pd.read_csv(S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv")
    for ref in source.itertuples():
        path = Path(str(ref.path))
        month_guard(path.stem)
        if digest(path) != ref.sha256:
            raise ValueError("S5S9_SOURCE_CHANGED")
    attempts = (
        [json.loads(s) for s in (out / "BASELINE_ATTEMPTS.jsonl").read_text().splitlines()]
        if (out / "BASELINE_ATTEMPTS.jsonl").exists()
        else []
    )
    started = sum(x["status"] == "STARTED" for x in history)
    completed = sum(x["status"] == "COMPLETED" for x in history)
    fitted_controls = sum(x["status"] == "STARTED" for x in attempts)
    prefix = (
        [json.loads(s) for s in (out / "PREFIX_ATTEMPTS.jsonl").read_text().splitlines()]
        if (out / "PREFIX_ATTEMPTS.jsonl").exists()
        else []
    )
    prefix_started = sum(x["status"] == "STARTED" for x in prefix)
    recipes = len(list(out.glob("HF20-*/*_target_recipe.json")))
    if started > 16 or fitted_controls > 64 or recipes > 32 or prefix_started > 32:
        raise ValueError("S5S9_FINAL_BUDGET")
    if complete and (
        started != 16
        or completed != 16
        or fitted_controls != 64
        or recipes != 32
        or prefix_started != 32
    ):
        raise ValueError("S5S9_INCOMPLETE_ACCOUNTING")
    receipt = dict(
        status="NUMERICAL_PASS_BROWSER_PENDING" if complete else "PARTIAL_NOT_ALL_COMPLETED",
        neural_starts=started,
        neural_completed=completed,
        ledger=114 + started,
        control_attempts=fitted_controls,
        prefix_recipes=recipes,
        prefix_attempts=prefix_started,
        source_files_rehashed=len(source),
        protected_reads_or_hashes=0,
        resources=resources(out),
        scientific_status="EXPLORATORY_REVIEW_REQUIRED",
    )
    (out / "S5_S9_NUMERICAL_VERIFICATION.json").write_text(json.dumps(receipt, indent=2) + "\n")
    from .hf20_s5s9_visual import dashboard

    dashboard(out)
