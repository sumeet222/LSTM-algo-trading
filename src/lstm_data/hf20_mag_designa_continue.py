"""Session2B: one coverage-only chronology amendment and three Design A pairs.

Reuse F21 by reference, preserve the parent namespace, and call the original
fold implementation with explicitly earlier initial recipes. No new model arm.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from . import hf20_mag_designa as base

OUT = Path("reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27")
PARENT = base.DEFAULT_OUT
PAIRS = (("C1a", "C0"), ("M1", "C0"), ("C1a", "M1"), ("C1a", "B0-VOL"), ("M1", "B0-VOL"))
ROLES = ("inner_train", "selector", "restricted_refit", "calibration", "oos")


def choose_candidate(candidates: list[dict]) -> dict:
    """Latest qualifying July/June/May window; counts alone, never forecast loss."""
    for month in (7, 6, 5):
        found = next(c for c in candidates if c["month"] == month)
        if found["sessions"] >= 50 and found["slot_min"] >= 25:
            return found
    raise ValueError("BLOCKED: no July/June/May selector meets50 sessions and25 per slot")


def before(grid: pd.DataFrame, day: str, *, inclusive: bool) -> str:
    keep = grid.session_date_et.le(day) if inclusive else grid.session_date_et.lt(day)
    return str(grid.loc[keep, "session_date_et"].max())


def preserved_parent(out: Path) -> dict:
    """A small critical artifact/kernel check; never a source/protected traversal."""
    bindings = base.read(out / "parent_bindings.json")
    for name, expected in bindings["files"].items():
        assert base.digest(PARENT / name) == expected, f"PARENT_CHANGED:{name}"
    for name, expected in bindings["kernels"].items():
        actual = hashlib.sha256(inspect.getsource(getattr(base, name)).encode()).hexdigest()
        assert actual == expected, f"NUMERICAL_KERNEL_CHANGED:{name}"
    return bindings


def preflight(out: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[int, dict], dict]:
    """One all-four gate, metadata/past-label coverage only; no fitting/inference."""
    bindings = preserved_parent(out)
    parent_design = base.read(PARENT / "session2_design.json")
    parent_protocol = base.read(PARENT / "session2_protocol.json")
    assert parent_protocol["status"] == "PARTIAL"
    assert parent_design["baselines"]["VOL"]["penalties"] == [0.001, 0.1, 10.0]
    assert parent_design["caps"] == base.CAPS
    assert parent_protocol["preflight"]["folds"][3]["calibration_coverage_flags"]
    grid, rows = base.metadata()
    first = np.full(len(rows), "0000", dtype=object)
    valid = rows.first_step.ge(0)
    first[valid] = grid.session_date_et.to_numpy()[rows.loc[valid, "first_step"].to_numpy(int)]
    target = pd.read_parquet(
        base.S4 / "opening_reaudit_v2/S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet",
        columns=["origin_id", "ticker", "direct_return"],
    )
    np.testing.assert_array_equal(target.origin_id.iloc[::20], rows.origin_id)
    assert target.ticker.tolist() == list(base.SYMBOLS) * len(rows)
    r = target.direct_return.to_numpy().reshape(-1, 20)
    plans: dict[int, dict] = {}
    candidates, counts, tails, folds = [], [], [], []
    for year in base.YEARS:
        prior = year - 1
        september = before(grid, f"{prior}-09-30", inclusive=True)
        december = before(grid, f"{prior}-12-31", inclusive=True)
        options = []
        for month in (7, 6, 5):
            start = f"{prior}-{month:02d}-01"
            initial_stop = before(grid, start, inclusive=False)
            mask = base.role_mask(rows, first, start, september, initial_stop)
            g = rows.loc[mask]
            slot_counts = g.groupby("slot").size().reindex(base.SLOTS, fill_value=0)
            options.append(
                dict(
                    year=year,
                    month=month,
                    start=start,
                    initial_stop=initial_stop,
                    sessions=g.session_date_et.nunique(),
                    origins=len(g),
                    slot_min=int(slot_counts.min()),
                    **{s: int(slot_counts[s]) for s in base.SLOTS},
                )
            )
        candidates.extend(options)
        chosen = choose_candidate(options)
        definitions = {
            "inner_train": ("2011-04-01", chosen["initial_stop"], "0000"),
            "selector": (chosen["start"], september, chosen["initial_stop"]),
            "restricted_refit": ("2011-04-01", september, "0000"),
            "calibration": (f"{prior}-10-01", december, september),
            "oos": (f"{year}-01-01", f"{year}-12-31", december),
        }
        plans[year] = {}
        for role, (start, stop, embargo) in definitions.items():
            mask = base.role_mask(rows, first, start, stop, embargo)
            positions = np.flatnonzero(mask)
            plans[year][role] = positions
            g = rows.loc[mask]
            assert len(g) and np.isfinite(r[positions]).all()
            assert (g.entry_index - g.first_step).eq(47).all()
            assert (first[mask] > embargo).all() and g.label_maturity_utc.lt(base.limit(stop)).all()
            assert g.trading_minutes.eq(240).all()
            slot_counts = g.groupby("slot").size().reindex(base.SLOTS, fill_value=0)
            counts.append(
                dict(
                    year=year,
                    role=role,
                    start=start,
                    cutoff=stop,
                    embargo_after=embargo,
                    maturity_before=str(base.limit(stop)),
                    first_date=g.session_date_et.min(),
                    last_date=g.session_date_et.max(),
                    sessions=g.session_date_et.nunique(),
                    origins=len(g),
                    stock_rows=20 * len(g),
                    **{s: int(slot_counts[s]) for s in base.SLOTS},
                )
            )
        p = plans[year]
        for left, right in (
            ("inner_train", "selector"),
            ("selector", "calibration"),
            ("restricted_refit", "calibration"),
            ("calibration", "oos"),
        ):
            assert not np.intersect1d(p[left], p[right]).size
        assert np.isin(p["inner_train"], p["restricted_refit"]).all()
        assert np.isin(p["selector"], p["restricted_refit"]).all()
        saved = pd.read_parquet(
            base.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "weight"],
        )
        np.testing.assert_array_equal(saved.origin_id.iloc[::20], rows.iloc[p["oos"]].origin_id)
        assert saved.ticker.tolist() == list(base.SYMBOLS) * len(p["oos"])
        np.testing.assert_allclose(
            saved.weight,
            np.repeat(base.origin_weights(rows.iloc[p["oos"]].session_date_et.to_numpy()) / 20, 20),
            atol=1e-15,
        )
        # Existing June-prefix thresholds describe event coverage only. Evaluation
        # thresholds will be fitted separately on each legal September prefix.
        early = base.read(base.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/inner_target_recipe.json")
        cp = p["calibration"]
        cal = rows.iloc[cp]
        months = cal.session_date_et.str[:7].value_counts().sort_index().to_dict()
        tails.append(
            dict(
                year=year,
                sessions=cal.session_date_et.nunique(),
                origins=len(cp),
                rows=20 * len(cp),
                month_origin_counts=months,
                min_A=float(abs(r[cp]).min()),
                max_A=float(abs(r[cp]).max()),
                June_prefix95=early["abs_r95"],
                June_prefix99=early["abs_r99"],
                exceed95_rows=int((abs(r[cp]) > early["abs_r95"]).sum()),
                exceed99_rows=int((abs(r[cp]) > early["abs_r99"]).sum()),
                finite_all=True,
                warning="Limited tail precision; global pooled scalars, no slot-wise minimum",
            )
        )
        folds.append(
            dict(
                year=year,
                status="REUSE" if year == 2021 else "READY",
                selector_start=chosen["start"],
                initial_stop=chosen["initial_stop"],
                selector_sessions=chosen["sessions"],
                slot_min=chosen["slot_min"],
                cutoffs=dict(
                    initial=chosen["initial_stop"], september=september, december=december
                ),
            )
        )
    # Exact F21 chronology and files, without a new forecast population or fit.
    original_counts = pd.read_csv(PARENT / "session2_role_counts.csv")
    new_counts = pd.DataFrame(counts)
    pd.testing.assert_frame_equal(
        original_counts.loc[original_counts.year.eq(2021)].reset_index(drop=True),
        new_counts.loc[new_counts.year.eq(2021), original_counts.columns].reset_index(drop=True),
        check_dtype=False,
    )
    for role in ("calibration", "oos"):
        f = pd.read_parquet(
            PARENT / f"F21/{role}_scores.parquet",
            columns=[
                "origin_id",
                "ticker",
                "entry_end_utc",
                "exit_end_utc",
                "label_maturity_utc",
                "weight",
            ],
        )
        p = plans[2021][role]
        np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.iloc[p].origin_id)
        assert f.ticker.tolist() == list(base.SYMBOLS) * len(p)
        for name in ("entry_end_utc", "exit_end_utc", "label_maturity_utc"):
            np.testing.assert_array_equal(f[name].iloc[::20], rows.iloc[p][name])
    model = base.model_for("MAG")
    model.load_state_dict(torch.load(PARENT / "F21/restricted_final.pt", weights_only=True))
    assert (
        base.initial_hash(model) == base.read(PARENT / "F21/result.json")["frozen_parameter_sha256"]
    )
    del model
    source_receipt = pd.read_csv(base.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv")
    source_receipt = source_receipt.loc[
        source_receipt.purpose.eq("permitted adjusted hourly source")
    ]
    for record in source_receipt.to_dict("records"):
        path = Path(str(record["path"]))
        assert "2010-07" <= path.stem <= "2024-12"
        assert path.is_file() and path.stat().st_size == record["bytes"]
    pointer = base.read(base.POINTER)
    last = json.loads(Path(pointer["real_journal"]).read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 131
    assert torch.__version__.split("+")[0] == "2.10.0"
    new_counts.to_csv(out / "role_counts.csv", index=False)
    pd.DataFrame(candidates).to_csv(out / "selector_candidates.csv", index=False)
    receipt = dict(
        status="PASS_ALL_FOUR",
        folds=folds,
        calibration_coverage=tails,
        F21_reuse="EXACT_CHRONOLOGY_KEYS_PARAMETERS_FORMULAS_AND_ARTIFACTS",
        prior_pointer=pointer,
        ledger_before=131,
        maximum_new_pairs=3,
        maximum_after=134,
        permitted_hourly_partitions=len(source_receipt),
        caps=base.CAPS,
        resources=base.resources(out),
        estimated_workload=dict(
            neural_phase_fits=6,
            coefficient_fits=27,
            initial_feature_target_recipes=3,
            restricted_feature_target_recipes=3,
            maximum_total_neural_epochs=360,
            parent_F21_pair_seconds=base.read(PARENT / "F21/result.json")["seconds"],
            rough_360epoch_seconds=base.read(PARENT / "F21/result.json")["seconds"] * 360 / 68,
            artifact_reserve_bytes=60_000_000,
        ),
        parent_bindings="parent_bindings.json",
        parent_code_sha256=bindings["parent_code_sha256"],
    )
    path = out / "preflight.json"
    if not path.exists():
        base.write(path, receipt, new=True)
    else:
        assert base.read(path)["folds"] == folds
    amendment = dict(
        kind="USER_APPROVED_SESSION2B_DESIGNA_FOURFOLD_V1",
        selector_rule=(
            "Try July1, June1, May1 in that order; first window with>=50 "
            "sessions and>=25 origins in every slot. No loss/forecast "
            "selection. No earlier month."
        ),
        initial_stop="Last complete permitted session strictly before chosen nominal start",
        calibration=(
            "October-December after48-step embargo; no new numerical minimum; "
            "limited precision accepted explicitly"
        ),
        inherited_numerical_design=parent_design,
        F21_reuse_root=str(PARENT),
        new_years=[2022, 2023, 2024],
        paired_comparisons=[list(x) for x in PAIRS],
        bootstrap=(
            "Annual: original block_interval400/22042. Equal-year: original "
            "S5/S9 per-contrast RNG22042, resample whole months independently "
            "within each year,400 draws, mean four annual draw means."
        ),
        equal_year=(
            "Only all four valid folds; proper losses/means/IC average annual "
            "values; ratio=equal-year predicted mean/observed mean. No "
            "equal-row pooling."
        ),
        chosen_windows=folds,
        preflight="preflight.json",
        parent_bindings="parent_bindings.json",
        git_start="5f7bb86a35d5aaff34ff79ef8f471117de6d3e42",
    )
    path = out / "amendment.json"
    if path.exists():
        assert base.read(path) == amendment
    else:
        base.write(path, amendment, new=True)
    return grid, rows, plans, receipt


def journal(out: Path, year: int, status: str, detail: dict) -> None:
    """Append only new F22-F24 starts; bind the unchanged131-start predecessor."""
    pre = base.read(out / "preflight.json")
    assert pre["status"] == "PASS_ALL_FOUR" and year in (2022, 2023, 2024)
    path = out / "neural_starts.jsonl"
    history = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    started = [x["year"] for x in history if x["status"] == "STARTED"]
    prior = pre["prior_pointer"]
    if not history:
        assert base.read(base.POINTER) == prior
    else:
        assert base.read(base.POINTER)["real_journal"] == str(path)
    if status == "STARTED":
        assert len(started) < 3 and year == (2022, 2023, 2024)[len(started)]
        assert not history or history[-1]["status"] == "COMPLETED"
        base.resources(out)
    else:
        assert history and history[-1]["year"] == year
    count = 131 + len(started) + int(status == "STARTED")
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        year=year,
        status=status,
        global_started_pairs=count,
        effective_ceiling=200,
        detail=detail,
        previous_journal=dict(
            path=prior["real_journal"], sha256=base.digest(Path(prior["real_journal"]))
        ),
        plan=dict(path=str(out / "amendment.json"), sha256=base.digest(out / "amendment.json")),
    )
    with path.open("a") as stream:
        stream.write(json.dumps(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    base.write(
        base.POINTER,
        dict(
            prior,
            schema_version=25,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def fold_root(out: Path, year: int) -> Path:
    return (PARENT if year == 2021 else out) / f"F{year % 100}"


def bootstrap_equal_year(daily: dict[int, pd.Series]) -> dict:
    """Original S5/S9 year-stratified month bootstrap; never resample years/rows."""
    if set(daily) != set(base.YEARS):
        raise ValueError("FOUR_VALID_YEARS_REQUIRED")
    rng = np.random.default_rng(22042)
    draws = []
    for year in base.YEARS:
        value = daily[year]
        bins = value.groupby(value.index.astype(str).str[:7]).agg(["sum", "count"])
        ix = rng.integers(len(bins), size=(400, len(bins)))
        draws.append(bins["sum"].to_numpy()[ix].sum(1) / bins["count"].to_numpy()[ix].sum(1))
    lo, hi = np.quantile(np.mean(draws, axis=0), [0.025, 0.975])
    return dict(
        mean=float(np.mean([v.mean() for v in daily.values()])), low=float(lo), high=float(hi)
    )


def postfit_report(out: Path) -> None:
    """Saved-only four-fold summaries; F21 annual rows are copied unchanged."""
    preserved_parent(out)
    annual, groups, fit_rows = [], [], []
    scores: dict[int, pd.DataFrame] = {}
    original = pd.read_csv(PARENT / "session2_metrics.csv")
    parent_groups = pd.read_csv(PARENT / "session2_groups.csv")
    for year in base.YEARS:
        root = fold_root(out, year)
        if not (root / "result.json").exists():
            continue
        result = base.read(root / "result.json")
        target = base.read(root / "restricted_target.json")
        coeff = base.read(root / "coefficients.json")
        f = pd.read_parquet(root / "oos_scores.parquet")
        cal = pd.read_parquet(root / "calibration_scores.parquet")
        expected = pd.read_parquet(
            base.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "weight"],
        )
        np.testing.assert_array_equal(f[["origin_id", "ticker"]], expected[["origin_id", "ticker"]])
        np.testing.assert_allclose(f.weight, expected.weight, atol=1e-15)
        assert np.isfinite(f[[*base.ARMS, "A", "Mhat"]].to_numpy()).all()
        z, w, a = cal.Mhat.to_numpy(float), cal.weight.to_numpy(float), cal.A.to_numpy(float)
        c = float(w @ np.exp(np.log1p(a / target["scale"]) - z) / w.sum())
        a0 = target["scale"] * np.expm1(np.maximum(z, 0))
        k = max(0.0, float(w @ (a0 * a)) / float(w @ (a0 * a0)))
        np.testing.assert_allclose([c, k], [coeff["c"], coeff["k"]], atol=1e-14, rtol=1e-13)
        for arm, value in base.decode(f.Mhat.to_numpy(), target["scale"], c, k).items():
            np.testing.assert_allclose(value, f[arm], atol=1e-14, rtol=1e-13)
        scores[year] = f
        fit_rows.append(
            dict(
                year=year,
                disposition="REUSED" if year == 2021 else "NEW",
                selector_start=next(
                    x["selector_start"]
                    for x in base.read(out / "preflight.json")["folds"]
                    if x["year"] == year
                ),
                selector_epochs=result["selector_epochs"],
                selected_epoch=result["selected_epoch"],
                initial_scale=base.read(root / "selection.json")["inner_scale"],
                scale=result["scale"],
                c=coeff["c"],
                k=coeff["k"],
                ridge_penalty=coeff["baselines"]["ridge_penalty"],
                cal_rows=coeff["calibration_rows"],
                exp_top10_share=coeff["exp_top10row_share"],
                exp_top1pct_share=coeff["exp_top1pct_share"],
                exp_max=coeff["exp_max"],
                factor_status=coeff["status"],
                negative_Mhat_oos=int(f.Mhat.lt(0).sum()),
                C1a_zero_oos=int(f.C1a.eq(0).sum()),
                M1_zero_oos=int(f.M1.eq(0).sum()),
                seconds=result["seconds"],
                peak_rss=result["peak_rss_bytes"],
                reload_max_error=result["reload_max_error"],
                checkpoint=str(root / "restricted_final.pt"),
            )
        )
        for arm in base.ARMS:
            metric: dict[str, float | int] = {**base.metrics(f, arm), **base.rank_metrics(f, arm)}
            transformed = float(f.weight @ ((np.log1p(f.A / target["scale"]) - f.Mhat) ** 2))
            if year == 2021:
                old = original.loc[original.arm.eq(arm)].iloc[0]
                for name in (
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "bias",
                    "ratio",
                    "magnitude_IC",
                    "top4",
                    "bottom4",
                    "pair_concordance",
                    "tie_rate",
                    "constant_rate",
                ):
                    np.testing.assert_allclose(metric[name], old[name], atol=1e-14, rtol=1e-13)
                    metric[name] = float(old[name])
            annual.append(
                dict(
                    year=year,
                    arm=arm,
                    **metric,
                    original_Mhat_transformed_MSE=(
                        transformed if arm in ("C0", "C1a", "M1") else None
                    ),
                )
            )
            for field in ("category", "slot"):
                for label, g in f.groupby(field):
                    groups.append(
                        dict(
                            year=year,
                            arm=arm,
                            field=field,
                            group=str(label),
                            **base.metrics(g, arm),
                        )
                    )
            low = f.groupby("origin_id")[arm].rank(method="average").le(10.5)
            cuts = np.unique(
                [
                    base.quantile(f.C0.to_numpy(), q, f.weight.to_numpy())
                    for q in np.arange(0.1, 1, 0.1)
                ]
            )
            bins = np.searchsorted(cuts, f.C0, side="left") + 1
            for label in np.unique(bins):
                groups.append(
                    dict(
                        year=year,
                        arm=arm,
                        field="C0_decile",
                        group=str(label),
                        C0_min=float(f.loc[bins == label, "C0"].min()),
                        C0_max=float(f.loc[bins == label, "C0"].max()),
                        **base.metrics(f.loc[bins == label], arm),
                    )
                )
            for percentile in (95, 99):
                mask = f.A.gt(target["thresholds"][str(percentile)])
                for label, keep in (
                    (f"PREFIX{percentile}", mask),
                    (f"LE_PREFIX{percentile}", ~mask),
                ):
                    g = f.loc[keep]
                    contribution = float((g.weight * (g[arm] - g.A) ** 2).sum())
                    groups.append(
                        dict(
                            year=year,
                            arm=arm,
                            field="tail",
                            group=label,
                            **base.metrics(g, arm),
                            weight_mass=float(g.weight.sum()),
                            raw_MSE_contribution=contribution,
                            raw_MSE_loss_share=contribution / metric["raw_MSE"],
                            false_low_rank=float(np.average(low.loc[keep], weights=g.weight)),
                        )
                    )
        core = base.rank_metrics(f, "C0")
        for arm in ("C1a", "M1"):
            other = base.rank_metrics(f, arm)
            strictly_same = (
                np.ptp(f.Mhat.to_numpy()) > 0
                and f.Mhat.ge(0).all()
                and f[arm].gt(0).all()
                and coeff["k"] > 0
            )
            if strictly_same:
                for name in ("magnitude_IC", "pair_concordance", "top4", "bottom4"):
                    np.testing.assert_allclose(core[name], other[name], atol=1e-12, rtol=1e-11)
        # F21 group rows keep their original metric values; add loss-contribution
        # bookkeeping only, calculated from the same unchanged weights/keys.
        for item in groups:
            if item["year"] == 2021:
                old = parent_groups.loc[
                    parent_groups.arm.eq(item["arm"])
                    & parent_groups.field.eq(item["field"])
                    & parent_groups.group.eq(item["group"])
                ]
                for name in ("raw_MSE", "raw_MAE", "observed", "predicted", "bias", "ratio"):
                    np.testing.assert_allclose(
                        item[name], old[name].iloc[0], atol=1e-14, rtol=1e-13
                    )
    complete = set(scores) == set(base.YEARS)
    m = pd.DataFrame(annual)
    g = pd.DataFrame(groups)
    pairs = []
    for left, right in PAIRS:
        daily: dict[int, pd.Series] = {}
        for year, f in scores.items():
            parts = (
                pd.DataFrame(
                    dict(
                        day=f.session_date_et,
                        w=f.weight,
                        d=f.weight * ((f[left] - f.A) ** 2 - (f[right] - f.A) ** 2),
                    )
                )
                .groupby("day")
                .sum()
            )
            value = parts.d / parts.w
            daily[year] = value
            interval = base.block_interval(value)
            reference = float(m.loc[m.year.eq(year) & m.arm.eq(right), "raw_MSE"].iloc[0])
            pairs.append(
                dict(
                    year=str(year),
                    model=left,
                    reference=right,
                    percent_change=100 * interval["mean"] / reference,
                    includes_zero=interval["low"] <= 0 <= interval["high"],
                    **interval,
                )
            )
        if complete:
            interval = bootstrap_equal_year(daily)
            reference = float(m.loc[m.arm.eq(right), "raw_MSE"].mean())
            pairs.append(
                dict(
                    year="EQ",
                    model=left,
                    reference=right,
                    percent_change=100 * interval["mean"] / reference,
                    includes_zero=interval["low"] <= 0 <= interval["high"],
                    **interval,
                )
            )
    if complete:
        eq = []
        for arm, h in m.groupby("arm", sort=False):
            values = {
                name: float(h[name].mean())
                for name in [
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "bias",
                    "magnitude_IC",
                    "top4",
                    "bottom4",
                    "pair_concordance",
                    "tie_rate",
                    "constant_rate",
                    "original_Mhat_transformed_MSE",
                ]
            }
            values["ratio"] = values["predicted"] / values["observed"]
            eq.append(
                dict(
                    year="EQ",
                    arm=arm,
                    rows=int(h.rows.sum()),
                    sessions=int(h.sessions.sum()),
                    origins=int(h.origins.sum()),
                    **values,
                )
            )
        m = pd.concat([m, pd.DataFrame(eq)], ignore_index=True)
        eqg = []
        for (arm, field, label), h in g.groupby(["arm", "field", "group"], sort=False):
            assert h.year.nunique() == 4
            values = {
                name: float(h[name].mean())
                for name in [
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "bias",
                    "weight_mass",
                    "raw_MSE_contribution",
                    "false_low_rank",
                ]
            }
            values["ratio"] = values["predicted"] / values["observed"]
            if field == "tail":
                total = float(m.loc[m.year.eq("EQ") & m.arm.eq(str(arm)), "raw_MSE"].iloc[0])
                values["raw_MSE_loss_share"] = values["raw_MSE_contribution"] / total
            eqg.append(
                dict(
                    year="EQ",
                    arm=arm,
                    field=field,
                    group=label,
                    rows=int(h.rows.sum()),
                    sessions=int(h.sessions.sum()),
                    origins=int(h.origins.sum()),
                    **values,
                )
            )
        g = pd.concat([g, pd.DataFrame(eqg)], ignore_index=True)
    reference = g.loc[g.arm.eq("C0"), ["year", "field", "group", "raw_MSE"]].rename(
        columns={"raw_MSE": "C0_raw_MSE"}
    )
    g = g.merge(reference, on=["year", "field", "group"], validate="many_to_one")
    g["delta_MSE_vs_C0"] = g.raw_MSE - g.C0_raw_MSE
    g["MSE_percent_vs_C0"] = 100 * g.delta_MSE_vs_C0 / g.C0_raw_MSE
    m.to_csv(out / "fourfold_metrics.csv", index=False)
    g.to_csv(out / "fourfold_groups.csv", index=False)
    pair_frame = pd.DataFrame(pairs)
    pair_frame.to_csv(out / "paired_MSE.csv", index=False)
    fit = pd.DataFrame(fit_rows)
    fit.to_csv(out / "fit_summary.csv", index=False)
    write_report(out, m, g, pair_frame, fit, complete)


def write_report(
    out: Path,
    m: pd.DataFrame,
    g: pd.DataFrame,
    pairs: pd.DataFrame,
    fit: pd.DataFrame,
    complete: bool,
) -> None:
    """Concise scientific tables, with decisions filled from saved four-fold evidence."""
    pre = base.read(out / "preflight.json")
    counts = pd.read_csv(out / "role_counts.csv")
    note_path = out / "review_interpretation.json"
    notes = base.read(note_path) if note_path.exists() else {}
    receipt_path = out / "execution_receipt.json"
    verified = base.read(receipt_path) if receipt_path.exists() else {}
    status = "COMPLETE" if complete else "PARTIAL"
    sections = [
        "# S9 MAG Stage1 / Session2B — Design A four-fold completion",
        (
            f"**Status: {status}.** F21 reused by reference; only F22–F24 are new fits. "
            "All results exploratory/post-search."
        ),
        "## Executive result",
        notes.get("executive", "Scientific interpretation not yet available."),
        "## Amendment and preflight",
        (
            "F21 reuse: PASS for exact chronology, keys, parameter identity, formulas "
            "and bound artifacts. It was not retrained or retrospectively corrected."
        ),
        (
            "Uniform rule: test July1, June1, May1 in order; choose first "
            "meeting>=50 sessions and>=25 origins in every slot, after "
            "exact48-step embargo and label maturity. Initial training/scaling "
            "ends before that nominal start. No loss, IC, forecast or OOS "
            "performance enters this choice."
        ),
        base.markdown(
            pd.DataFrame(pre["folds"])
            .drop(columns=["cutoffs"])
            .rename(columns={"status": "preflight_status"})
        ),
        base.markdown(
            counts[
                [
                    "year",
                    "role",
                    "cutoff",
                    "first_date",
                    "last_date",
                    "sessions",
                    "origins",
                    "stock_rows",
                ]
            ]
        ),
        (
            "Full per-role seven-slot counts, maturity timestamps and embargo "
            "cutoffs: role_counts.csv. All original S4/S9 OOS keys and stock "
            "order match; no dropped rows."
        ),
        "Selector and independent-tail seven-slot coverage:",
        base.markdown(
            counts.loc[
                counts.role.isin(["selector", "calibration"]),
                ["year", "role", "sessions", *base.SLOTS],
            ]
        ),
        (
            "Calibration adequacy:56/50/48/40 sessions. These are global scalar"
            " fits; no invented selector50/25 minimum is applied to the "
            "calibration tail. F24's smaller/sparser tail warrants "
            "limited-precision caution, not independent certification. "
            "Event/month coverage below uses archived June-prefix95/99 "
            "thresholds only as preflight descriptors; evaluation tails use "
            "each restricted September prefix."
        ),
        base.markdown(
            pd.DataFrame(
                [
                    {
                        **{
                            k: item[k]
                            for k in [
                                "year",
                                "sessions",
                                "origins",
                                "rows",
                                "max_A",
                                "June_prefix95",
                                "June_prefix99",
                                "exceed95_rows",
                                "exceed99_rows",
                            ]
                        },
                        "Oct/Nov/Dec_origins": "/".join(
                            str(v) for v in item["month_origin_counts"].values()
                        ),
                    }
                    for item in pre["calibration_coverage"]
                ]
            )
        ),
        (
            "Strict label maturity is before local cutoff midnight +1 day -4 hours. "
            "For selector, calibration and OOS, the first of 48 scheduled completed "
            "input hours must be strictly after the preceding cutoff. Genuine "
            "targets span 240 trading minutes; later clocks cross sessions. "
            "All-four admissibility was saved before the first new neural start."
        ),
        "## Annual and equal-year proper scores",
        base.markdown(
            m[["year", "arm", "raw_MSE", "raw_MAE", "observed", "predicted", "bias", "ratio"]]
        ),
        (
            "A=abs(log(P_endpoint/P_origin)). MAE/bias/means are log-return "
            "units; MSE is squared log-return units. Annual weights equal "
            "stocks/origin, origins/session, sessions/year. EQ losses/means/IC "
            "average four annual values; EQ ratio is the ratio of EQ "
            "predicted/observed means, not a pooled-row ratio or mean annual "
            "ratio. EQ is unavailable if any fold fails."
        ),
        "## Paired raw-MSE uncertainty",
        base.markdown(pairs),
        (
            "Annual bounds use the unchanged Session2 whole-month400-draw "
            "routine,seed22042. EQ uses the executed S5/S9 year-stratified "
            "month bootstrap: independent whole-month draws within each year, "
            "then mean four annual resampled means. No IID "
            "stock/overlapping-origin/year resampling or selection-adjusted "
            "significance claim."
        ),
        (
            "Bounds are descriptive 95% percentile intervals conditional on these "
            "already fitted encoders/scalars and chosen protocol. They do not "
            "refit calibration tails or account for model-selection/search uncertainty. "
            "Stocks, overlapping origins and four annual folds are not IID replicates."
        ),
        "## Fits and calibration precision",
        base.markdown(
            fit[
                [
                    "year",
                    "disposition",
                    "selector_start",
                    "selector_epochs",
                    "selected_epoch",
                    "initial_scale",
                    "scale",
                    "c",
                    "k",
                    "ridge_penalty",
                    "cal_rows",
                ]
            ]
        ),
        base.markdown(
            fit[
                [
                    "year",
                    "exp_top10_share",
                    "exp_top1pct_share",
                    "exp_max",
                    "negative_Mhat_oos",
                    "C1a_zero_oos",
                    "M1_zero_oos",
                    "seconds",
                    "peak_rss",
                    "reload_max_error",
                ]
            ]
        ),
        (
            "New initial FT16 floors/scalers and target scales were fitted only"
            " before the chosen selector start; restricted recipes/scales only "
            "through September. The exact September encoder supplies both "
            "independent October–December and next-year OOS forecasts. Original"
            " MAG initialization, optimizer, dropout, loss, selector, seed42, "
            "fresh-refit logic and B0 formulas/penalties are unchanged. No c/k "
            "clipping, trimming or contextual fitting."
        ),
        notes.get("methods", ""),
        "## Magnitude ordering",
        "Annual C0 and equal-year all-arm ranking; every annual arm is in fourfold_metrics.csv.",
        base.markdown(
            m.loc[
                m.year.eq("EQ") | m.arm.eq("C0"),
                [
                    "year",
                    "arm",
                    "magnitude_IC",
                    "top4",
                    "bottom4",
                    "pair_concordance",
                    "tie_rate",
                    "constant_rate",
                    "original_Mhat_transformed_MSE",
                ],
            ]
        ),
        (
            "Magnitude IC is within-origin tie-aware Spearman, then "
            "origins/sessions/years; not archived all-row0.408 or signed-return"
            " IC. Strictly monotone positive maps are asserted to preserve C0 "
            "rankings; clamping/tie exceptions are disclosed. Original Mhat "
            "loss is unchanged across network decoders, not a loss of "
            "inverse-corrected outputs."
        ),
        (
            "Spearman uses average ranks; constant-score origins yield undefined IC "
            "and would be omitted, with their rate disclosed (none here). Pair "
            "concordance excludes true-outcome ties and gives half credit to score "
            "ties; chance is 0.5. Top/bottom-four retrieval uses fractional membership "
            "at tied boundaries; chance is 0.2. No jitter or alphabetical tie breaking."
        ),
        "## Clock and tail diagnostics",
        notes.get("clock_tail", ""),
        "Annual prefix-defined event counts (same cohorts for every arm):",
        base.markdown(
            g.loc[
                g.year.ne("EQ") & g.arm.eq("C0") & g.group.isin(["PREFIX95", "PREFIX99"]),
                ["year", "group", "rows", "sessions", "origins", "weight_mass", "false_low_rank"],
            ]
        ),
        base.markdown(
            g.loc[
                g.year.eq("EQ")
                & g.arm.isin(["C0", "C1a", "M1", "B0-VOL"])
                & g.field.ne("C0_decile"),
                [
                    "arm",
                    "field",
                    "group",
                    "observed",
                    "predicted",
                    "ratio",
                    "raw_MSE",
                    "raw_MAE",
                    "MSE_percent_vs_C0",
                    "weight_mass",
                    "raw_MSE_loss_share",
                    "false_low_rank",
                ],
            ]
        )
        if complete
        else "Four-year group summaries unavailable.",
        (
            "All annual categories and seven slots, prefix95/99 and complements"
            " are in fourfold_groups.csv. Conditional group errors retain "
            "original role weights normalized within the group and then equal "
            "years. Tail loss shares use EQ unconditional loss contribution "
            "divided by EQ total MSE; no equal-row pooling. False-low rate: "
            "event-mass fraction with forecast within-origin midrank<=10.5."
        ),
        notes.get("reliability", ""),
        "## Decision and limitations",
        notes.get("decision", "Interpretation pending review."),
        "## Reproduction and verification",
        (
            "`.venv/bin/python -m lstm_data.hf20_mag_designa_continue "
            f"--out {out} --report` replays saved outputs only. Original --run is "
            "single-use; no rerun or new objective is authorized."
        ),
        notes.get("sources", ""),
        (
            "F21 artifacts and original numerical kernels remain bound in "
            "parent_bindings.json; parent code snapshot preserved as "
            "parent_implementation.py.txt. F21 annual values are copied "
            "unchanged from Session2 and checked against the identical saved "
            "population. No F21 scores/checkpoints are duplicated. New per-fold"
            " files retain initial/restricted recipes, target scale/tails, "
            "selected/final checkpoints, compact epoch trace, coefficients and "
            "compressed calibration/OOS scores. New ledgers append a successor;"
            " prior131-start history stays byte-identical."
        ),
        (
            "Historical MAG is context, not the causal calibration comparator: "
            "it refit through December, whereas C0/C1a/M1 share September "
            "training. The archived equal-year transformed MSE0.232454/raw "
            "MAE0.006505 and raw mean bias remain untouched. Four years are not"
            " independent seeds and have been inspected repeatedly. Source "
            "publication/action vintage, fixed survivors and price-only entry "
            "before origin+2min issuance remain qualifications. No2025/2026 "
            "numerical reads/hashes, acquisitions, strategies, dashboards, O1, "
            "C2/C3 or overnight-jump model."
        ),
        (
            "Files: amendment.json, preflight.json, parent_bindings.json, "
            "role_counts.csv, selector_candidates.csv, fourfold_metrics.csv, "
            "fourfold_groups.csv, paired_MSE.csv, fit_summary.csv, "
            "neural_starts.jsonl; F22/F23/F24 outputs only. F21 source "
            "reference: "
        )
        + str(PARENT),
        verified.get("summary", "Final verification not yet recorded."),
        "STOP: no subsequent fitting or protected-data release is authorized.",
    ]
    (out / "S9_MAG_STAGE1_DESIGNA_FOURFOLD_COMPLETION_REPORT.md").write_text(
        "\n\n".join(sections) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    out = args.out
    if args.report:
        postfit_report(out)
        return
    if (out / "neural_starts.jsonl").exists():
        raise SystemExit("NO_RETRY: successor already has a charged lifecycle")
    if args.run:
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
    grid, rows, plans, pre = preflight(out)
    print(json.dumps(pre, indent=2), flush=True)
    if not args.run:
        return
    c, r = base.source_components(grid, rows)
    for year in (2022, 2023, 2024):
        stop = next(x["initial_stop"] for x in pre["folds"] if x["year"] == year)
        fh = base.feature_fit_hours(c.grid, rows, stop)
        recipe, _ = base.fit_expanded(c, fh, stop, approved=True)
        ip = plans[year]["inner_train"]
        w = np.repeat(base.origin_weights(rows.iloc[ip].session_date_et.to_numpy()) / 20, 20)
        scale = max(base.quantile(abs(r[ip]).ravel(), 0.5, w), 1e-8)
        base.run_fold(
            out, year, c, rows, r, plans[year], pre, initial=(recipe, scale), journal=journal
        )
        base.write(
            out / "continuation.json",
            dict(
                completed_new_years=list(range(2022, year + 1)),
                pending_years=list(range(year + 1, 2025)),
                design="amendment.json",
                retry_completed_folds=False,
            ),
        )
        postfit_report(out)
    postfit_report(out)


if __name__ == "__main__":
    main()
