"""Compact truthful-unit S1/S2 diagnostics over already computed, exactly keyed scores."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .hf20_ranking import (
    YEARS,
    daily_ic,
    origin_ic,
    origin_weights,
    pair_terms,
    rank_targets,
    ranks,
    row_loss,
)
from .hf20_ranking_data import FoldData


def export_diagnostics(
    data: FoldData, year: int, role: str, arm: str, score: np.ndarray, dest: Path
) -> dict:
    positions = data.positions(year, role)
    rows = data.rows.iloc[positions]
    r = data.returns[positions]
    if score.shape != r.shape or not np.isfinite(score).all():
        raise ValueError("INVALID_SCORE_POPULATION")
    ic = origin_ic(r, score)
    defined = float(np.isfinite(ic).mean())
    if role == "oos" and arm != "N0" and defined < 0.99:
        raise ValueError("OOS_DEFINED_IC_BELOW99PCT")
    day = rows.session_date_et.to_numpy()
    ow = origin_weights(day)
    med = np.median(r, axis=1)
    mad = np.median(abs(r - med[:, None]), axis=1)
    numerator = r - med[:, None]
    y = numerator / (mad[:, None] + data.recipe["epsilon"])
    q = rank_targets(r)
    pr = rank_targets(score)
    i, j = np.triu_indices(20, 1)
    direction = np.sign(r[:, i] - r[:, j])
    pred = np.sign(score[:, i] - score[:, j])
    valid = direction != 0
    paircount = valid.sum(1)
    concord = np.divide(
        ((direction == pred) * valid + 0.5 * (pred == 0) * valid).sum(1),
        paircount,
        out=np.full(len(r), np.nan),
        where=paircount > 0,
    )

    def member(v: np.ndarray, top: bool) -> np.ndarray:
        a = v if top else -v
        cut = np.sort(a, axis=1)[:, -4]
        above = a > cut[:, None]
        tie = a == cut[:, None]
        return above + tie * ((4 - above.sum(1)) / tie.sum(1))[:, None]

    top = (member(r, True) * member(score, True)).sum(1) / 4
    bottom = (member(r, False) * member(score, False)).sum(1) / 4
    dtype = torch.float32 if arm in ("T2R", "NR", "PW") else torch.float64
    actual = None
    if arm in ("NR", "LR", "P"):
        actual = (score.astype(np.float32 if arm == "NR" else float) - q) ** 2 / 20
    elif arm in ("PW", "LP"):
        actual = pair_terms(torch.tensor(score, dtype=dtype), torch.tensor(r, dtype=torch.float64))[
            1
        ].numpy()
    elif arm == "T2R":
        actual = row_loss(
            arm,
            torch.tensor(score, dtype=dtype),
            torch.tensor(r),
            torch.tensor(y, dtype=torch.float32),
            data.recipe["t2_scale"],
        ).numpy()

    def scalar(v: np.ndarray) -> float:
        return float(np.nansum(ow * v))

    summary = dict(
        year=year,
        role=role,
        model=arm,
        origins=len(rows),
        sessions=len(set(day)),
        rows=len(rows) * 20,
        daily_ic=daily_ic(r, score, day) if np.isfinite(ic).any() else None,
        defined_origin_fraction=defined,
        defined_ic_sessions=int(
            pd.DataFrame(dict(day=day, ic=ic)).groupby("day").ic.mean().notna().sum()
        ),
        origin_ic=float(np.nanmean(ic)) if np.isfinite(ic).any() else None,
        pair_concordance=scalar(concord),
        normalized_rank_mse=scalar(((q - pr) ** 2).mean(1)),
        top4=scalar(top),
        bottom4=scalar(bottom),
        score_sd=scalar(score.std(1)),
        pair_tie_rate=scalar((pred == 0).mean(1)),
        actual_objective=scalar(actual.sum(1)) if actual is not None else None,
        score_units="asinh TG20" if arm == "T2R" else "ordinal score; no return calibration",
        phase="inner" if role.startswith("inner") else "refit",
    )
    if arm == "T2R":
        inverse = data.recipe["t2_scale"] * np.sinh(score.astype(float))
        summary["original_TG20_mse"] = scalar(((inverse - y) ** 2).mean(1))
        summary["inverse_count"] = 1
        common = scalar((inverse.mean(1) - y.mean(1)) ** 2)
        centered = scalar(
            ((inverse - inverse.mean(1)[:, None] - y + y.mean(1)[:, None]) ** 2).mean(1)
        )
        np.testing.assert_allclose(
            common + centered, summary["original_TG20_mse"], rtol=1e-13, atol=1e-13
        )
        summary["original_common_mse"], summary["original_centered_mse"] = common, centered
    base = dict(
        origin_id=np.repeat(rows.origin_id.to_numpy(), 20),
        ticker=np.tile(data.symbols, len(rows)),
        session_date_et=np.repeat(day, 20),
        role=role,
        model=arm,
        year=year,
        return_4h=r.reshape(-1),
        numerator=numerator.reshape(-1),
        median=np.repeat(med, 20),
        mad=np.repeat(mad, 20),
        epsilon=data.recipe["epsilon"],
        scale=data.recipe["t2_scale"],
        TG20=y.reshape(-1),
        score=score.reshape(-1),
        q=q.reshape(-1),
        weight=np.repeat(ow / 20, 20),
        actual_row_allocation=actual.reshape(-1)
        if actual is not None
        else np.full(len(rows) * 20, np.nan),
    )
    f = pd.DataFrame(base)
    from .config import digest
    from .hf1m_training_data import CONTRACT
    from .hf20_ranking_run import code_hash

    f["input_contract_sha256"] = digest(CONTRACT)
    f["execution_sha256"] = code_hash()
    f["phase_recipe_sha256"] = digest(dest.parent / f"F{year % 100}_{summary['phase']}_recipe.json")
    f["source_revision"] = data.contract["revision"]
    f["entry_end_utc"] = np.repeat(rows.entry_end_utc.to_numpy(), 20)
    f["exit_end_utc"] = np.repeat(rows.exit_end_utc.to_numpy(), 20)
    f["label_maturity_utc"] = np.repeat(rows.label_maturity_utc.to_numpy(), 20)
    f["Z"] = np.arcsinh(f.TG20 / data.recipe["t2_scale"])
    for name, values in data.quality_fields(positions).items():
        f[name] = values
    f["quality"] = np.where(
        f.assumed_zero_minute_count.gt(0) | f.price_proxy_minute_count.gt(0),
        "SOURCE_FLAGGED",
        "NO_LISTED_SOURCE_FLAG",
    )
    f["fallback"] = np.where(f.feature_fallback_cells.gt(0), "ANY", "NONE")
    f["actual_rank"] = ranks(r).reshape(-1)
    f["prediction_rank"] = ranks(score).reshape(-1)
    f["relative_side_hit"] = (
        np.sign(score - np.median(score, axis=1)[:, None]) == np.sign(numerator)
    ).reshape(-1)
    sector = json.loads(Path("configs/hf_twelvedata_hourly_audit_v3.json").read_text())[
        "publisher_sector_etfs"
    ]
    f["static_publisher_sector_proxy"] = f.ticker.map(sector).fillna("UNVERIFIED")
    if arm == "T2R":
        f["inverse_TG20"] = inverse.reshape(-1)
        f["original_squared_error"] = ((inverse - y) ** 2).reshape(-1)
        f["inverse_count"] = 1
    if arm in ("T2R", "NR", "PW"):
        binding_file = dest / (
            "calibration_binding.json" if role.startswith("inner") else "refit_binding.json"
        )
        binding = json.loads(binding_file.read_text())
        if digest(Path(binding["checkpoint"])) != binding["checkpoint_sha256"]:
            raise ValueError("CHECKPOINT_BINDING_CHANGED")
        f["checkpoint_sha256"] = binding["checkpoint_sha256"]
    elif arm in ("P", "LR", "LP"):
        selected = json.loads((dest / "selection.json").read_text())["selected"]
        coefficient = dest / (
            f"inner_{selected['penalty']}.npy"
            if role.startswith("inner")
            else "refit_coefficients.npy"
        )
        f["coefficient_sha256"] = digest(coefficient)
    if actual is not None:
        np.testing.assert_allclose(
            np.repeat(ow, 20) @ f.actual_row_allocation,
            float(summary["actual_objective"] or 0),
            rtol=3e-7,
            atol=1e-8,
        )
    f.to_parquet(dest / f"{role}_scores.parquet", index=False)
    cases_file = dest.parent / "shared_source_case_keys.csv"
    if role == "oos" and arm in ("T2R", "NR", "PW") and cases_file.is_file():
        keys = pd.read_csv(cases_file)
        keys = keys.loc[keys.year.eq(year)]
        trace = keys.merge(
            f, on=["origin_id", "ticker", "year", "session_date_et"], validate="one_to_one"
        )
        if len(trace) != len(keys):
            raise ValueError("SOURCE_WITNESS_JOIN_MISSING")
        np.testing.assert_allclose(trace.return_4h, trace.witness_return_4h, rtol=1e-14, atol=1e-16)
        trace.to_csv(dest / "source_cases.csv", index=False)
    origin = pd.DataFrame(
        dict(
            origin_id=rows.origin_id.to_numpy(),
            session_date_et=day,
            ic=ic,
            concordance=concord,
            rank_mse=((q - pr) ** 2).mean(1),
            top4=top,
            bottom4=bottom,
            score_sd=score.std(1),
            min_score_gap=np.diff(np.sort(score, axis=1), axis=1).min(1),
            pair_tie_rate=(pred == 0).mean(1),
        )
    )
    origin["slot"] = (
        pd.to_datetime(rows.entry_end_utc, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.strftime("%H:%M")
        .to_numpy()
    )
    origin["month"] = origin.session_date_et.str[:7]
    origin.to_csv(dest / f"{role}_origins.csv", index=False)
    # Cross-sectional stock/quality contributions, never stockwise time-series IC.
    rr, pp = ranks(r), ranks(score)
    rr -= rr.mean(1)[:, None]
    pp -= pp.mean(1)[:, None]
    denom = np.sqrt((rr * rr).sum(1) * (pp * pp).sum(1))
    contribution = np.divide(
        20 * rr * pp, denom[:, None], out=np.full_like(rr, np.nan), where=denom[:, None] > 0
    ).reshape(-1)
    strata = []
    for group in ("ticker", "static_publisher_sector_proxy", "quality", "fallback"):
        for label, indices in f.groupby(group).indices.items():
            strata.append(
                dict(
                    group=group,
                    label=str(label),
                    rows=len(indices),
                    ic_contribution=float(
                        np.nansum(f.weight.to_numpy()[indices] * contribution[indices])
                    ),
                    weight_mass=float(f.weight.to_numpy()[indices].sum()),
                )
            )
    pd.DataFrame(strata).to_csv(dest / f"{role}_stock_quality.csv", index=False)
    for group in ("month", "slot"):
        origin.groupby([group, "session_date_et"]).mean(numeric_only=True).groupby(group).mean(
            numeric_only=True
        ).to_csv(dest / f"{role}_{group}.csv")
    trainrole = "inner_train" if role.startswith("inner") else "refit"
    train = data.returns[data.positions(year, trainrole)]
    tm = np.median(train, axis=1)
    td = np.median(abs(train - tm[:, None]), axis=1)
    tn = train - tm[:, None]
    ty = tn / (td[:, None] + data.recipe["epsilon"])
    thresholds = dict(
        abs_y95=float(np.quantile(abs(ty), 0.95)),
        abs_y99=float(np.quantile(abs(ty), 0.99)),
        num95=float(np.quantile(abs(tn), 0.95)),
        mad05=float(np.quantile(td, 0.05)),
        source="applicable calibration-fit or full-prefix-refit historical observations only",
    )
    masks = dict(
        ALL=np.ones(len(f), bool),
        POS=f.TG20.gt(0).to_numpy(),
        NEG=f.TG20.lt(0).to_numpy(),
        TRAIN_EVENT95=abs(f.TG20.to_numpy()) > thresholds["abs_y95"],
        TRAIN_EVENT99=abs(f.TG20.to_numpy()) > thresholds["abs_y99"],
        FLOOR=f.mad.le(f.epsilon).to_numpy(),
    )
    n = abs(f.numerator.to_numpy()) > thresholds["num95"]
    m = f.mad.to_numpy() < thresholds["mad05"]
    for label, value in [
        ("NUM_ONLY", n & ~m),
        ("MAD_ONLY", m & ~n),
        ("BOTH", n & m),
        ("NEITHER", ~(n | m)),
    ]:
        masks[label] = value
    for pct in (1, 5):
        order = np.lexsort(
            (np.tile(np.arange(20), len(rows)), f.origin_id.to_numpy(), -abs(f.TG20.to_numpy()))
        )
        chosen = np.zeros(len(f), bool)
        chosen[order[: len(f) * pct // 100]] = True
        masks[f"TARGET_RANK_TOP{pct}"] = chosen
        masks[f"TARGET_RANK_TOP{pct}_COMPLEMENT"] = ~chosen
        if actual is not None:
            order = np.argsort(-actual.reshape(-1), kind="stable")
            chosen = np.zeros(len(f), bool)
            chosen[order[: len(f) * pct // 100]] = True
            masks[f"ACTUAL_OBJECTIVE_TOP{pct}"] = chosen
            masks[f"ACTUAL_OBJECTIVE_TOP{pct}_COMPLEMENT"] = ~chosen
    cohort = []
    w = f.weight.to_numpy()
    for label, mask in masks.items():
        row = dict(
            cohort=label,
            rows=int(mask.sum()),
            origins=f.loc[mask, "origin_id"].nunique(),
            sessions=f.loc[mask, "session_date_et"].nunique(),
            weight_mass=float(w[mask].sum()),
            normalized_rank_error=float(w[mask] @ ((q - pr).reshape(-1)[mask] ** 2)),
            relative_side_hit_mass=float(w[mask] @ f.relative_side_hit.to_numpy()[mask]),
        )
        if actual is not None:
            row["actual_objective_contribution"] = float(
                np.repeat(ow, 20)[mask] @ actual.reshape(-1)[mask]
            )
        if arm == "T2R":
            row["original_y_error_contribution"] = float(
                w[mask] @ ((inverse - y).reshape(-1)[mask] ** 2)
            )
        cohort.append(row)
    # Preserve positive/negative versions of each original-target event cohort.
    for name in ("TRAIN_EVENT95", "TRAIN_EVENT99", "TARGET_RANK_TOP1", "TARGET_RANK_TOP5"):
        for side, sign in (("POS", 1), ("NEG", -1)):
            mask = masks[name] & (f.TG20.to_numpy() * sign > 0)
            cohort.append(
                dict(
                    cohort=name + "_" + side,
                    rows=int(mask.sum()),
                    origins=f.loc[mask, "origin_id"].nunique(),
                    sessions=f.loc[mask, "session_date_et"].nunique(),
                    weight_mass=float(w[mask].sum()),
                    normalized_rank_error=float(w[mask] @ ((q - pr).reshape(-1)[mask] ** 2)),
                    actual_objective_contribution=float(
                        np.repeat(ow, 20)[mask] @ actual.reshape(-1)[mask]
                    )
                    if actual is not None
                    else None,
                )
            )
    if arm in ("PW", "LP"):
        pair_raw, _ = pair_terms(torch.tensor(score, dtype=dtype), torch.tensor(r))
        event = abs(y) > thresholds["abs_y95"]
        pair_rows = []
        for label, mask in (
            ("BOTH_EXTREME", event[:, i] & event[:, j]),
            ("ONE_EXTREME", event[:, i] ^ event[:, j]),
            ("NEITHER_EXTREME", ~(event[:, i] | event[:, j])),
        ):
            allocation = (pair_raw.numpy() * mask).sum(1) / paircount
            pair_rows.append(dict(pair_type=label, weighted_loss=scalar(allocation)))
        np.testing.assert_allclose(
            sum(float(p["weighted_loss"]) for p in pair_rows),
            float(summary["actual_objective"] or 0),
            rtol=3e-7,
            atol=1e-8,
        )
        # Diagnostic gap cut is fitted on the prior fitting prefix, not outer labels.
        gaps = abs(train[:, i] - train[:, j])
        cut = float(np.quantile(gaps, 0.05))
        pair_rows.append(
            dict(
                pair_type="SMALL_GAP_TRAIN_P05",
                weighted_loss=scalar(
                    (pair_raw.numpy() * (abs(r[:, i] - r[:, j]) <= cut)).sum(1) / paircount
                ),
                training_gap_cut=cut,
            )
        )
        pd.DataFrame(pair_rows).to_csv(dest / f"{role}_pair_types.csv", index=False)
    if actual is not None:
        disjoint = [
            r["actual_objective_contribution"]
            for r in cohort
            if r["cohort"] in ("NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER")
        ]
        np.testing.assert_allclose(
            sum(disjoint), float(summary["actual_objective"] or 0), rtol=3e-7, atol=1e-8
        )
    pd.DataFrame(cohort).to_csv(dest / f"{role}_cohorts.csv", index=False)
    (dest / f"{role}_thresholds.json").write_text(json.dumps(thresholds, indent=2))
    (dest / f"{role}_metrics.json").write_text(json.dumps(summary, indent=2, allow_nan=False))
    return summary


def verify_exports(out: Path, paths: list[Path]) -> list[dict]:
    """Independent stored-key/weight/IC/objective gate, called before the next fit."""
    reconciled = []
    for p in paths:
        a = pd.read_parquet(p)
        if a.duplicated(["origin_id", "ticker"]).any():
            raise ValueError("DUPLICATE_OUTPUT_KEYS")
        year = int(a.year.iloc[0])
        role = str(a.role.iloc[0])
        indices = pd.read_csv(out / f"F{year % 100}_{role}_indices.csv")
        if set(a.origin_id) != set(indices.origin_id) or len(a) != 20 * len(indices):
            raise ValueError("FROZEN_ROLE_KEY_MISMATCH")
        expected = 1 / (
            a.session_date_et.nunique()
            * a.session_date_et.map(a.session_date_et.value_counts()).to_numpy()
        )
        np.testing.assert_allclose(a.weight, expected, rtol=1e-14, atol=1e-15)
        actual = a.return_4h.to_numpy().reshape(-1, 20)
        score = a.score.to_numpy().reshape(-1, 20)
        # Independent per-origin corrcoef oracle rather than calling origin_ic again.
        independent = []
        for y, s in zip(actual, score):
            yr = pd.Series(y).rank().to_numpy()
            sr = pd.Series(s).rank().to_numpy()
            independent.append(
                float(np.corrcoef(yr, sr)[0, 1]) if yr.std() > 0 and sr.std() > 0 else np.nan
            )
        ic = float(
            pd.DataFrame(dict(day=a.session_date_et.to_numpy()[::20], ic=independent))
            .groupby("day")
            .ic.mean()
            .mean()
        )
        reported = json.loads((p.parent / f"{role}_metrics.json").read_text())
        if reported["daily_ic"] is None:
            if np.isfinite(ic):
                raise ValueError("UNDEFINED_IC_CHANGED")
        else:
            np.testing.assert_allclose(ic, reported["daily_ic"], rtol=1e-12, atol=1e-12)
        if reported["actual_objective"] is not None:
            ow = a.weight.to_numpy().reshape(-1, 20).sum(1)
            model = str(a.model.iloc[0])
            if model in ("PW", "LP"):
                i, j = np.triu_indices(20, 1)
                direction = np.sign(actual[:, i] - actual[:, j])
                valid = direction != 0
                terms = np.logaddexp(0, -direction * (score[:, i] - score[:, j])) * valid
                oracle = float(ow @ (terms.sum(1) / valid.sum(1)))
            elif model == "T2R":
                y = a.TG20.to_numpy().reshape(-1, 20).astype(np.float32)
                oracle = float(ow @ ((score - np.arcsinh(y / float(a.scale.iloc[0]))) ** 2).mean(1))
            else:
                oracle = float(ow @ ((score - rank_targets(actual)) ** 2).mean(1))
            if not np.isfinite(oracle):
                raise ValueError("NONFINITE_OBJECTIVE_ORACLE")
            np.testing.assert_allclose(oracle, reported["actual_objective"], rtol=3e-7, atol=1e-8)
            np.testing.assert_allclose(
                (20 * a.weight * a.actual_row_allocation).sum(),
                reported["actual_objective"],
                rtol=3e-7,
                atol=1e-8,
            )
            cohorts = pd.read_csv(p.parent / f"{role}_cohorts.csv").set_index("cohort")
            for names in (
                ("NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER"),
                ("TARGET_RANK_TOP1", "TARGET_RANK_TOP1_COMPLEMENT"),
                ("TARGET_RANK_TOP5", "TARGET_RANK_TOP5_COMPLEMENT"),
            ):
                np.testing.assert_allclose(
                    cohorts.loc[list(names), "actual_objective_contribution"].sum(),
                    oracle,
                    rtol=3e-7,
                    atol=1e-8,
                )
        reconciled.append(
            dict(file=str(p), rows=len(a), keys="PASS", weights="PASS", independent_ic="PASS")
        )
    return reconciled


def closeout(out: Path) -> None:
    from .config import digest
    from .hf20_ranking_run import code_hash

    proposal = json.loads((out / "proposal.json").read_text())
    if proposal["execution_sha256"] != code_hash():
        raise ValueError("CLOSEOUT_CODE_CHANGED")
    for ref in proposal["preserve_refs"]:
        if (
            ref["path"] != "configs/CURRENT_EXPERIMENT_REGISTRY.json"
            and digest(Path(ref["path"])) != ref["sha256"]
        ):
            raise ValueError("PREVIOUS_SOURCE_OR_CHECKPOINT_CHANGED")
    reconciled = verify_exports(out, sorted(out.glob("*/*_scores.parquet")))
    pd.DataFrame(reconciled).to_csv(out / "independent_output_reconciliation.csv", index=False)
    rows = []
    for p in sorted(out.glob("*/oos_metrics.json")):
        rows.append(json.loads(p.read_text()))
    f = pd.DataFrame(rows)
    expected_models = {"N0", "N1", "N2", "P", "LR", "LP"}
    if any(out.glob("HF20-S1S2-*/PASS.json")):
        expected_models |= {"T2R", "NR", "PW"}
    if set(zip(f.year, f.model)) != {(y, m) for y in YEARS for m in expected_models} or len(
        f
    ) != 4 * len(expected_models):
        raise ValueError("INCOMPLETE_FOUR_FOLD_MODEL_MATRIX")
    f.to_csv(out / "four_fold_models.csv", index=False)
    numeric = list(f.select_dtypes(include="number").columns)
    f.groupby("model")[numeric].mean().to_csv(out / "equal_year_summary.csv")
    paired = []
    for year in YEARS:
        paths = [p for p in out.glob("*/oos_scores.parquet") if f"F{year % 100}" in p.parent.name]
        models = {}
        for p in paths:
            a = pd.read_parquet(p).sort_values(["origin_id", "ticker"]).reset_index(drop=True)
            models[str(a.model.iloc[0])] = a
        for control in ("LR", "LP", "T2R"):
            if control not in models:
                continue
            b = models[control]
            for model, a in models.items():
                pd.testing.assert_frame_equal(
                    a[["origin_id", "ticker", "return_4h"]],
                    b[["origin_id", "ticker", "return_4h"]],
                    check_exact=True,
                )
                ar = a.score.to_numpy().reshape(-1, 20)
                br = b.score.to_numpy().reshape(-1, 20)
                y = a.return_4h.to_numpy().reshape(-1, 20)
                days = a.session_date_et.to_numpy()[::20]
                aa = pd.DataFrame(dict(day=days, delta=origin_ic(y, ar) - origin_ic(y, br)))
                daily = aa.groupby("day").delta.mean().dropna()
                monthly = daily.groupby(lambda d: d[:7]).agg(["sum", "count"])
                if len(monthly):
                    rng = np.random.default_rng(22042)
                    draw = rng.integers(len(monthly), size=(400, len(monthly)))
                    resample = monthly["sum"].to_numpy()[draw].sum(1) / monthly["count"].to_numpy()[
                        draw
                    ].sum(1)
                    interval = np.quantile(resample, [0.025, 0.975]).tolist()
                else:
                    interval = [None, None]
                paired.append(
                    dict(
                        year=year,
                        model=model,
                        control=control,
                        daily_ic_delta=float(aa.groupby("day").delta.mean().mean())
                        if aa.delta.notna().any()
                        else None,
                        month_block_sensitivity_interval=interval,
                        not_a_significance_test=True,
                        matched_defined_origins=int(aa.delta.notna().sum()),
                        population=(
                            "identical score/outcome keys; paired IC uses intersection of defi"
                            "ned origins"
                        ),
                    )
                )
    (out / "paired_calendar_sensitivity.json").write_text(
        json.dumps(paired, indent=2, allow_nan=False)
    )
    # One portable offline visual rather than a new dashboard route/framework.
    import plotly.graph_objects as go

    plot = go.Figure()
    for model, g in f.groupby("model"):
        if model != "N0":
            plot.add_trace(
                go.Scatter(x=g.year, y=g.daily_ic, mode="lines+markers", name=str(model))
            )
    plot.update_layout(
        title="Retrospective annual OOS daily Rank IC — no trading claim",
        xaxis_title="Outer year",
        yaxis_title="Daily Rank IC",
    )
    plot.write_html(out / "annual_rank_ic.html", include_plotlyjs=True)
    reports = out / "completed_reports_v1"
    reports.mkdir(exist_ok=False)

    def markdown(frame: pd.DataFrame) -> str:
        columns = list(frame.columns)
        lines = [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join(["---"] * len(columns)) + " |",
        ]
        for row in frame.to_dict("records"):
            lines.append("| " + " | ".join(str(row[c]) for c in columns) + " |")
        return "\n".join(lines) + "\n"

    for title, models in [
        ("S1_FOUR_FOLD_RANKING_BASELINES", ["N0", "N1", "N2", "P", "LR", "LP"]),
        ("S2_FOUR_FOLD_LSTM_RANKING_COMPARISON", ["T2R", "NR", "PW"]),
    ]:
        shown = f.loc[
            f.model.isin(models),
            [
                "year",
                "model",
                "daily_ic",
                "pair_concordance",
                "normalized_rank_mse",
                "defined_origin_fraction",
            ],
        ]
        (reports / (title + ".md")).write_text(
            "# "
            + title
            + (
                "\n\nRetrospective chronological OOS; no trading/confirmation claim."
                " Constant-score IC remains undefined.\n\n"
            )
            + markdown(shown)
        )
    (reports / "RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md").write_text(
        "# Ranking extremes and true-objective diagnostics\n\n"
        "Each model/fold has four-role cohorts with counts, origins, sessions and weight mass; "
        "target tails and complements; training-frozen events; NUM/MAD partitions. "
        "NR/LR have rank losses; PW/LP half-allocate pairs and report pair types and gaps. "
        "Only T2R has an asinh inverse and original-TG20 MSE. Stock/quality, month/slot "
        "and genuine source case tables accompany these. Independent reconciliation passed. "
        "Concentration is descriptive, not causal alpha.\n"
    )
    traces = []
    for path in out.glob("HF20-S1S2-*/PASS.json"):
        result = json.loads(path.read_text())
        traces.append(
            dict(run_id=result["run_id"], **result["selector"], seconds=result["seconds"])
        )
    (reports / "TRAINING_AND_SELECTION_TRACE.md").write_text(
        "# Training and selection trace\n\nStrict absolute 0.001 IC qualification; raw maxima "
        "separate; min12/max60/patience10 and fresh seed42 refit. Online dropout-ON batch "
        "telemetry, immutable epoch receipts/checkpoints and final step checks are retained.\n\n"
        + markdown(pd.DataFrame(traces))
    )
    for arm in ("T2R", "NR", "PW"):
        paths = list(out.glob(f"HF20-S1S2-*-{arm}-S42/source_cases.csv"))
        if paths:
            cases = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
            if len(cases) != 22 or cases.case_id.duplicated().any():
                raise ValueError("22_SOURCE_CASES_NOT_RECONCILED")
    journal = Path("reports/audit/track_a_real_pairs_v19_hf20_ranking.jsonl")
    count = 62
    if traces:
        from .hf20_ranking_authority import validate

        events = validate([json.loads(x) for x in journal.read_text().splitlines()])
        count = events[-1]["global_started_pairs"]
        if len(traces) != 12 or count != 74:
            raise ValueError("FINAL_NEURAL_COUNT")
    else:
        (reports / "S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md").write_text(
            "# S2 NOT_RUN\n\nS1-only scope: no neural results or neural starts. Ledger62/200.\n"
        )
    jobs = [json.loads(x) for x in (out / "baseline_fit_jobs.jsonl").read_text().splitlines()]
    if (
        sum(r["status"] == "STARTED" for r in jobs) != 64
        or sum(r["status"] == "COMPLETED" for r in jobs) != 64
    ):
        raise ValueError("FINAL_BASELINE_FIT_ACCOUNTING")
    (reports / "README.md").write_text(
        "# Completed S1/S2 reports\n\nSee S1_FOUR_FOLD_RANKING_BASELINES.md, "
        "S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md, RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md "
        "and TRAINING_AND_SELECTION_TRACE.md. Parent tables give annual/equal-year metrics. "
        "Source publication/action vintage, local rights and survivor selection remain qualified. "
        "2026 was not numerically accessed. No next experiment is authorized.\n"
    )
    (reports / "WORK_SESSION_REPORT.md").write_text(
        "# Campaign execution receipt\n\nSource/code/key/weight/IC checks completed. "
        f"64 baseline fits; {len(traces)} neural lifecycles; final ledger {count}/200. "
        "Detailed researcher/session handoff follows from these machine artifacts.\n"
    )
    (out / "FINAL_RESEARCH_DECISION.md").write_text(
        "# S1/S2 research decision\n\n"
        "All completed annual metrics and paired calendar sensitivities are in "
        "four_fold_models.csv, equal_year_summary.csv and paired_calendar_sensitivity.json. "
        "Four retrospective years are not pristine confirmation or independent stock/pair trials. "
        "No model promotion or next experiment is automatic. Review objective/cohort units "
        "and per-year stability before any hypothesis selection.\n"
    )
