"""S3 truthful horizon units, independent role gates and original-Y tail identities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf20_horizon_data import PREPARATION, HorizonData, sha_array
from .hf20_ranking import origin_weights, rank_targets
from .hf20_ranking_continue_report import cohort_tables
from .hf20_ranking_diagnostics import export_diagnostics
from .hf20_ranking_run import sha, write


def export(
    data: HorizonData, year: int, role: str, arm: str, score: np.ndarray, dest: Path, execution: str
) -> dict:
    """Reuse accepted mathematics; replace legacy 4h labels/provenance before publication."""
    summary = export_diagnostics(data, year, role, arm, score, dest)
    path = dest / f"{role}_scores.parquet"
    # The inherited helper's temporary return_4h field is renamed to explicit h units.
    cohorts, strata, pairs, examples = cohort_tables(path)
    for frame, name in (
        (cohorts, "tail_energy"),
        (strata, "tail_strata"),
        (pairs, "tail_pairs"),
        (examples, "extreme_examples"),
    ):
        frame["stage"], frame["horizon"] = data.stage, data.horizon
        frame.rename(columns={"return_4h": "return_h"}).to_parquet(
            dest / f"{role}_{name}.parquet", index=False
        )
    f = pd.read_parquet(path).rename(columns={"return_4h": "return_h"})
    f["inherited_helper_execution_sha256"] = f.execution_sha256
    f["execution_sha256"] = execution
    f["stage"], f["horizon"] = data.stage, data.horizon
    positions = data.positions(year, role)
    rows = data.rows.iloc[positions]
    entry, exit_ = rows.entry_index.to_numpy(int), rows.exit_index.to_numpy(int)
    slot = (
        pd.to_datetime(rows.entry_end_utc, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.hour.to_numpy()
        - 10
    )
    f["entry_source_close"] = data.components.source["close"][entry].reshape(-1)
    f["exit_source_close"] = data.components.source["close"][exit_].reshape(-1)
    f["conservative_admission_maturity_utc"] = np.repeat(
        data.base.rows.iloc[positions].label_maturity_utc.to_numpy(), 20
    )
    f["M2_scaled_latest"] = data.m2[entry, :, slot].reshape(-1)
    if data.stage == "B":
        floor = np.array(data.recipe["S3_M2"]["floors"])
        mean, rms = data.mean, data.rms
    else:
        floor = np.array([r["m2_floor"] for r in data.recipe["floors"]])
        mean, rms = data.components.m2_mean, data.components.m2_rms
    f["M2_native_latest"] = (mean[entry, :, slot] / np.maximum(rms[entry, :, slot], floor)).reshape(
        -1
    )
    f["M2_native_latest_valid"] = np.isfinite(f.M2_native_latest)
    f["denominator"] = f.mad + f.epsilon
    f["Z_actual_float32"] = np.arcsinh(
        f.TG20.to_numpy(np.float32) / np.float32(data.recipe["t2_scale"])
    )
    f.to_parquet(path, index=False)
    summary.update(
        stage=data.stage,
        horizon=data.horizon,
        target_units=f"TG20_h{data.horizon}",
        execution_sha256=execution,
    )
    (dest / f"{role}_metrics.json").write_text(json.dumps(summary, indent=2, allow_nan=False))
    verify_role(data, year, role, dest)
    return summary


def verify_role(data: HorizonData, year: int, role: str, dest: Path) -> dict:
    """Independent saved-key, raw target, weights, IC, true objective and partitions."""
    f = pd.read_parquet(dest / f"{role}_scores.parquet")
    positions = data.positions(year, role)
    rows = data.rows.iloc[positions]
    if f.duplicated(["origin_id", "ticker"]).any() or len(f) != 20 * len(rows):
        raise ValueError("S3_OUTPUT_DUPLICATE_OR_INCOMPLETE")
    np.testing.assert_array_equal(f.origin_id.to_numpy(), np.repeat(rows.origin_id.to_numpy(), 20))
    np.testing.assert_array_equal(f.ticker.to_numpy(), np.tile(data.symbols, len(rows)))
    if f.session_date_et.ge("2025-01-01").any():
        raise ValueError("S3_OUTPUT_PROTECTED_DATE")
    r = f.return_h.to_numpy().reshape(-1, 20)
    np.testing.assert_array_equal(r, data.returns[positions])
    entry = rows.entry_index.to_numpy(int)
    exit_ = rows.exit_index.to_numpy(int)
    oracle_return = np.log(
        data.components.source["close"][exit_] / data.components.source["close"][entry]
    )
    np.testing.assert_allclose(r, oracle_return, rtol=1e-14, atol=1e-16)
    med = np.median(r, axis=1)
    mad = np.median(abs(r - med[:, None]), axis=1)
    y = (r - med[:, None]) / (mad[:, None] + data.recipe["epsilon"])
    np.testing.assert_array_equal(f.TG20.to_numpy().reshape(-1, 20), y)
    w = origin_weights(rows.session_date_et.to_numpy())
    np.testing.assert_allclose(f.weight, np.repeat(w / 20, 20), rtol=1e-14, atol=1e-15)
    p = f.score.to_numpy().reshape(-1, 20)
    if not np.isfinite(p).all():
        raise ValueError("S3_NONFINITE_SCORES")
    independent = []
    for actual, pred in zip(r, p):
        a, b = pd.Series(actual).rank().to_numpy(), pd.Series(pred).rank().to_numpy()
        independent.append(float(np.corrcoef(a, b)[0, 1]) if b.std() > 0 else np.nan)
    ic = (
        pd.DataFrame(dict(day=rows.session_date_et.to_numpy(), ic=independent))
        .groupby("day")
        .ic.mean()
        .mean()
    )
    report = json.loads((dest / f"{role}_metrics.json").read_text())
    if report["daily_ic"] is None:
        if np.isfinite(ic):
            raise ValueError("S3_UNDEFINED_IC_CHANGED")
    else:
        np.testing.assert_allclose(ic, report["daily_ic"], rtol=1e-12, atol=1e-12)
    model = str(f.model.iloc[0])
    if report["actual_objective"] is not None:
        if model == "T2R":
            target = np.arcsinh(y.astype(np.float32) / np.float32(data.recipe["t2_scale"]))
            loss = (p.astype(np.float32) - target) ** 2
        else:
            loss = (p - rank_targets(r)) ** 2
        expected = float(w @ loss.mean(1))
        np.testing.assert_allclose(expected, report["actual_objective"], rtol=3e-7, atol=1e-8)
        cohorts = pd.read_csv(dest / f"{role}_cohorts.csv").set_index("cohort")
        for labels in (
            ("NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER"),
            ("TARGET_RANK_TOP1", "TARGET_RANK_TOP1_COMPLEMENT"),
            ("TARGET_RANK_TOP5", "TARGET_RANK_TOP5_COMPLEMENT"),
            ("ACTUAL_OBJECTIVE_TOP1", "ACTUAL_OBJECTIVE_TOP1_COMPLEMENT"),
            ("ACTUAL_OBJECTIVE_TOP5", "ACTUAL_OBJECTIVE_TOP5_COMPLEMENT"),
        ):
            np.testing.assert_allclose(
                cohorts.loc[list(labels), "actual_objective_contribution"].sum(),
                expected,
                rtol=3e-7,
                atol=1e-8,
            )
    return dict(
        role=role, rows=len(f), status="PASS", output_sha256=sha(dest / f"{role}_scores.parquet")
    )


def pass_gate(data: HorizonData, year: int, dest: Path, **extra: object) -> None:
    checks = []
    for phase, roles in (
        ("inner", ("inner_train", "inner_validation")),
        ("refit", ("refit", "oos")),
    ):
        data.phase(year, phase, dest.parent)
        checks.extend(verify_role(data, year, role, dest) for role in roles)
    if dest.name.startswith("HF20"):
        source_cases(data, year, dest)
    write(
        dest / "PASS.json",
        dict(
            status="PASS_TECHNICAL",
            reconciliation=checks,
            **extra,
            files={str(p): sha(p) for p in dest.iterdir() if p.is_file()},
        ),
    )


def source_cases(data: HorizonData, year: int, dest: Path) -> None:
    """Join the 22 predeclared source events, with full-checkpoint reload already checked."""
    keys = pd.read_csv(PREPARATION / "S3_PREDECLARED_SOURCE_WITNESSES.csv")
    keys = keys.loc[keys.year.eq(year) & keys.horizon.eq(data.horizon)].copy()
    stored = pd.read_parquet(dest / "oos_scores.parquet")
    trace = keys.merge(
        stored,
        on=["origin_id", "ticker", "year", "horizon"],
        validate="one_to_one",
        suffixes=("_declared", ""),
    )
    if len(trace) != len(keys):
        raise ValueError("S3_PREDECLARED_SOURCE_CASE_MISSING")
    np.testing.assert_allclose(trace.return_h, trace.return_4h_or_h, rtol=1e-14, atol=1e-16)
    pos = np.array([int(np.flatnonzero(data.rows.origin_id.eq(k))[0]) for k in keys.origin_id])
    x, r, y = data.arrays(pos)
    j = np.array([data.symbols.index(str(t)) for t in keys.ticker])
    chosen = x[np.arange(len(pos)), j]
    shared = dest.parent / "shared_source_case_inputs.npz"
    if shared.exists():
        with np.load(shared) as old:
            np.testing.assert_array_equal(old["inputs"], chosen)
            np.testing.assert_array_equal(old["returns20"], r)
            np.testing.assert_array_equal(old["Y20"], y)
    else:
        np.savez_compressed(
            shared, inputs=chosen, returns20=r, Y20=y, case_id=keys.case_id.to_numpy(int)
        )
    trace["shared_inputs_sha256"] = sha(shared)
    trace["input_array_sha256"] = sha_array(chosen)
    trace["checkpoint_full_population_reload_error"] = 0
    trace.to_csv(dest / "source_cases.csv", index=False)
