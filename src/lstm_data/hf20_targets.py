"""Lean HF20 T0–T2 analysis using executed S4 inputs and chronology."""

from __future__ import annotations

import argparse
import gc
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_mag_designa as b
from .hf1m_ft16_math import rolling
from .hf20_ranking import origin_weights, rank_targets, ranks, ridge_solution

OUT = Path("reports/experiments/hf20_t0_t2_return_targets_2026-10-29")
PENALTIES = (0.001, 0.1, 10.0)


def indicator_scores(native: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fixed rank mean; sum exact half-integer midranks before division to preserve ties."""
    mid = np.stack([ranks(native[:, :, j]) for j in range(3)], axis=-1)
    individual = 2 * (mid - 1) / (native.shape[1] - 1) - 1
    combined = 2 * (mid.sum(axis=-1) / 3 - 1) / (native.shape[1] - 1) - 1
    return individual, combined


def risk_scale(rms: np.ndarray, floors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Missing native RMS stays missing; a valid zero RMS can hit a positive floor."""
    if not np.isfinite(floors).all() or (floors <= 0).any():
        raise ValueError("STRICTLY_POSITIVE_PREFIX_FLOORS_REQUIRED")
    sigma = np.maximum(rms, floors)
    valid = np.isfinite(rms).all(1) & (rms >= 0).all(1)
    sigma[~np.isfinite(rms) | (rms < 0)] = np.nan
    return sigma, valid


def past_window(rows: pd.DataFrame, returns: np.ndarray, day: str, context: int):
    """Exact S4 scheduled regular-origin window, input-day-open maturity lock."""
    past = rows.loc[
        rows.regular_session & rows.context.eq(context) & rows.session_date_et.lt(day)
    ].tail(60)
    values = returns[past.row_index.to_numpy(int)].copy()
    lock = pd.Timestamp(day + " 09:30", tz="America/New_York")
    unavailable = past.label_maturity_utc.ge(lock).to_numpy()
    values[unavailable] = np.nan
    rms = rolling(values, 60, 57, True)[-1] if len(values) == 60 else np.full(20, np.nan)
    return past, values, rms, lock


def target_standardize(y: np.ndarray, days: np.ndarray):
    """Equal session/origin/stock moments; no validation or OOS data supplied."""
    w = origin_weights(days)[:, None, None] / y.shape[1]
    center = (w * y).sum((0, 1))
    scale = np.sqrt((w * (y - center) ** 2).sum((0, 1)))
    if not np.isfinite(scale).all() or (scale <= 0).any():
        raise ValueError("NONPOSITIVE_TRAIN_TARGET_SCALE")
    return (y - center) / scale, center, scale


def system(view: b.View, positions: np.ndarray, y: np.ndarray):
    """Shared streamed 768-column Gram, two target RHS; no design matrix cache."""
    gram, rhs = np.zeros((769, 769)), np.zeros((769, 2))
    w = origin_weights(view.rows.iloc[positions].session_date_et.to_numpy())
    for start in range(0, len(positions), 64):
        take = positions[start : start + 64]
        x = view.x(take).reshape(-1, 768).astype(float)
        a = np.column_stack([x, np.ones(len(x))])
        rw = np.repeat(w[start : start + 64] / 20, 20)
        gram += a.T @ (rw[:, None] * a)
        rhs += a.T @ (rw[:, None] * y[start : start + 64].reshape(-1, 2))
    b.memory()
    return gram, rhs


def predict(view: b.View, positions: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """Pure linear prediction from frozen S4 windows, no neural forward pass."""
    parts = []
    for start in range(0, len(positions), 64):
        x = view.x(positions[start : start + 64]).reshape(-1, 20, 768).astype(float)
        parts.append(x @ coefficients[:-1] + coefficients[-1])
    return np.concatenate(parts)


def load_roles(rows: pd.DataFrame, grid: pd.DataFrame, year: int):
    result = {}
    inner = b.read(b.S4 / f"F{year % 100}_inner_recipe.json")["fit_stop_inclusive"]
    refit = b.read(b.S4 / f"F{year % 100}_refit_recipe.json")["fit_stop_inclusive"]
    for role in ["inner_train", "inner_validation", "refit", "oos"]:
        saved = pd.read_csv(b.S4 / f"F{year % 100}_{role}_indices.csv")
        ix = saved.row_index.to_numpy(int)
        own = rows.iloc[ix]
        np.testing.assert_array_equal(own.origin_id, saved.origin_id)
        assert own.eligible.all()
        cutoff = (
            inner if role == "inner_train" else str(year) + "-12-31" if role == "oos" else refit
        )
        assert own.label_maturity_utc.lt(b.limit(cutoff)).all()
        if role in ["inner_validation", "oos"]:
            boundary = inner if role == "inner_validation" else refit
            assert (grid.session_date_et.to_numpy()[own.first_step.to_numpy(int)] > boundary).all()
        result[role] = ix
    return result


def run(*, resume_first_fold: bool = False, complete_valid: bool = False) -> None:
    """One bounded run: eight final target fits and24 inner candidate target solves."""
    config = b.read(OUT / "REPRODUCIBILITY.json")
    assert config["penalties"] == list(PENALTIES)
    for record in [*config["recipes"].values(), *config["roles"].values()]:
        assert b.digest(Path(record["path"])) == record["sha256"]
    for record in b.read(b.S9 / "S4_REUSED_RECIPES.json"):
        assert b.digest(Path(record["path"])) == record["sha256"]
    if resume_first_fold:
        assert (OUT / "STARTED.json").exists()
        assert list(OUT.glob("F*_coefficients.npz")) == [OUT / "F21_coefficients.npz"]
        b.write(
            OUT / ("COMPLETION.json" if complete_valid else "RECOVERY.json"),
            dict(
                at=pd.Timestamp.now(tz="UTC").isoformat(),
                reason=(
                    "F22 has no risk-valid inner-validation support; finish independent stages"
                    if complete_valid
                    else "No risk-complete09:30 trace after F21 fit"
                ),
                preserved_coefficients_sha256=b.digest(OUT / "F21_coefficients.npz"),
                action="reuse F21 coefficients; no repeated trial or final solves",
                lost="six F21 trial MSE values were in memory; selected penalties saved and logged",
            ),
            new=True,
        )
    else:
        b.write(OUT / "STARTED.json", dict(at=pd.Timestamp.now(tz="UTC").isoformat()), new=True)
    tick = time.monotonic()
    grid, rows = b.metadata()
    c, returns = b.source_components(grid, rows)
    print("Saved pre2025 hourly components loaded; no market-source reconstruction", flush=True)
    last = rows.entry_index.to_numpy(int)
    context = rows.context.to_numpy(int)
    rms = np.full((len(rows), 20), np.nan)
    has_input = last >= 0
    rms[has_input] = c.m2_rms[last[has_input], :, context[has_input]]
    summaries, outputs, trials, fits, traces, blocked = [], [], [], [], [], []
    for year in b.YEARS:
        roles = load_roles(rows, grid, year)
        chosen = []
        for phase, train_role, eval_role in [
            ("inner", "inner_train", "inner_validation"),
            ("refit", "refit", "oos"),
        ]:
            recipe = b.read(b.S4 / f"F{year % 100}_{phase}_recipe.json")
            assert [f["symbol"] for f in recipe["floors"]] == list(b.SYMBOLS)
            floors = np.array([f["m2_floor"] for f in recipe["floors"]])
            sigma, valid = risk_scale(rms, floors)
            train = roles[train_role][valid[roles[train_role]]]
            test = roles[eval_role][valid[roles[eval_role]]]
            for role in [train_role, eval_role]:
                ix = roles[role]
                summaries.append(
                    dict(
                        year=year,
                        role=role,
                        original_origins=len(ix),
                        risk_origins=int(valid[ix].sum()),
                        original_sessions=rows.iloc[ix].session_date_et.nunique(),
                        risk_sessions=rows.iloc[ix[valid[ix]]].session_date_et.nunique(),
                        floor_cells=int((rms[ix[valid[ix]]] < floors).sum()),
                    )
                )
            can_fit = bool(len(train) and len(test) and (phase == "inner" or chosen))
            if not can_fit:
                blocked.append(
                    dict(
                        year=year,
                        phase=phase,
                        train_origins=len(train),
                        evaluation_origins=len(test),
                        reason="NO_LEGAL_RISK_SUPPORT_OR_SELECTION",
                    )
                )
                print(year, phase, "BLOCKED", len(train), len(test), flush=True)
                if phase == "inner":
                    continue
            if resume_first_fold and year == 2021 and phase == "inner":
                with np.load(OUT / "F21_coefficients.npz") as saved:
                    chosen = [PENALTIES.index(float(p)) for p in saved["penalties"]]
                for penalty in PENALTIES:
                    for j, target in enumerate(["R", "Z"]):
                        trials.append(
                            dict(
                                year=year,
                                target=target,
                                penalty=penalty,
                                validation_MSE=np.nan,
                                selected=penalty == PENALTIES[chosen[j]],
                                status="EXECUTED_MSE_LOST_ON_TRACE_ABORT",
                            )
                        )
                continue
            view = b.View(c, rows, returns, recipe, 1.0)
            y = np.stack([returns[train], returns[train] / sigma[train]], axis=-1)
            if can_fit:
                ys, center, scale = target_standardize(
                    y, rows.iloc[train].session_date_et.to_numpy()
                )
            else:
                ys, center, scale = np.empty((0, 20, 2)), np.zeros(2), np.ones(2)
            if can_fit and not (resume_first_fold and year == 2021):
                gram, rhs = system(view, train, ys)
            else:
                gram, rhs = np.empty((0, 0)), np.empty((0, 2))
            actual = np.stack([returns[test], returns[test] / sigma[test]], axis=-1)
            w = origin_weights(rows.iloc[test].session_date_et.to_numpy())
            if phase == "inner":
                losses = []
                for penalty in PENALTIES:
                    coef = ridge_solution(gram, rhs, penalty)
                    forecast = predict(view, test, coef) * scale + center
                    loss = (w[:, None] * ((forecast - actual) ** 2).mean(1)).sum(0)
                    losses.append(loss)
                    for j, target in enumerate(["R", "Z"]):
                        trials.append(
                            dict(
                                year=year,
                                target=target,
                                penalty=penalty,
                                validation_MSE=float(loss[j]),
                                status="SAVED",
                            )
                        )
                chosen = [
                    min(range(3), key=lambda k: (losses[k][j], -PENALTIES[k])) for j in range(2)
                ]
                for trial in trials[-6:]:
                    trial["selected"] = (
                        trial["penalty"] == PENALTIES[chosen[["R", "Z"].index(trial["target"])]]
                    )
                pd.DataFrame(trials).to_csv(OUT / "RIDGE_SELECTION.csv", index=False)
            else:
                if not can_fit:
                    forecast = np.full((len(test), 20, 2), np.nan)
                else:
                    if resume_first_fold and year == 2021:
                        with np.load(OUT / "F21_coefficients.npz") as saved:
                            coef = saved["coefficients"]
                            np.testing.assert_array_equal(center, saved["center"])
                            np.testing.assert_array_equal(scale, saved["scale"])
                    else:
                        coef = np.column_stack(
                            [
                                ridge_solution(gram, rhs[:, j], PENALTIES[chosen[j]])
                                for j in range(2)
                            ]
                        )
                    forecast = predict(view, test, coef) * scale + center
                    if not (resume_first_fold and year == 2021):
                        np.savez_compressed(
                            OUT / f"F{year % 100}_coefficients.npz",
                            coefficients=coef,
                            center=center,
                            scale=scale,
                            penalties=np.array([PENALTIES[k] for k in chosen]),
                        )
                    for j, target in enumerate(["R", "Z"]):
                        fits.append(
                            dict(
                                year=year,
                                target=target,
                                penalty=PENALTIES[chosen[j]],
                                train_origins=len(train),
                                train_sessions=rows.iloc[train].session_date_et.nunique(),
                                target_center=center[j],
                                target_scale=scale[j],
                                coefficient_norm=float(np.linalg.norm(coef[:-1, j])),
                                intercept=float(coef[-1, j]),
                                fit_cutoff=recipe["fit_stop_inclusive"],
                            )
                        )
                ix = roles["oos"]
                f = (
                    rows.iloc[ix][["origin_id", "session_date_et", "slot", "category"]]
                    .loc[rows.iloc[ix].index.repeat(20)]
                    .reset_index(drop=True)
                )
                f["fold"], f["ticker"] = year, list(b.SYMBOLS) * len(ix)
                f["R"] = returns[ix].ravel()
                f["sigma"], f["native_rms"] = sigma[ix].ravel(), rms[ix].ravel()
                f["risk_valid"] = np.repeat(valid[ix], 20)
                f["floor_hit"] = (rms[ix] < floors).ravel()
                # Actual final S4 tensor channels, including native fallbacks and float32.
                native = np.concatenate(
                    [view.x(ix[k : k + 64])[:, :, -1, [0, 1, 3]] for k in range(0, len(ix), 64)]
                )
                archive = pd.read_parquet(b.S4 / f"F{year % 100}_S4_N1/oos_scores.parquet")
                np.testing.assert_array_equal(f.origin_id, archive.origin_id)
                np.testing.assert_array_equal(f.ticker, archive.ticker)
                np.testing.assert_array_equal(f.R, archive.return_4h)
                np.testing.assert_array_equal(native[:, :, 0].ravel(), archive.score)
                individual, combined = indicator_scores(native)
                for j, name in enumerate(["M1", "M2", "M4"]):
                    f["IND-" + name] = individual[:, :, j].ravel()
                f["IND-EQ3"] = combined.ravel()
                for j, name in enumerate(["RIDGE-R", "RIDGE-Z"]):
                    p = np.full((len(ix), 20), np.nan)
                    p[valid[ix]] = forecast[:, :, j]
                    f[name] = p.ravel()
                f["RIDGE-R-RISK"] = f["RIDGE-R"] / f.sigma
                f["RIDGE-Z-RAW"] = f["RIDGE-Z"] * f.sigma
                f["Z"] = f.R / f.sigma
                f["qR"] = rank_targets(returns[ix]).ravel()
                qz = np.full((len(ix), 20), np.nan)
                qz[valid[ix]] = rank_targets(returns[test] / sigma[test])
                f["qZ"] = qz.ravel()
                outputs.append(f)
                # Morning/overnight: three recent admitted observations plus excluded outcomes.
                if year == 2021:
                    for slot in ["09:30", "15:30"]:
                        i = int(next(k for k in ix if rows.iloc[k].slot == slot))
                        row = rows.iloc[i]
                        day = str(grid.session_date_et.iloc[int(row.entry_index)])
                        past, values, manual, lock = past_window(
                            rows, returns, day, int(row.context)
                        )
                        j = list(b.SYMBOLS).index("AAPL")
                        np.testing.assert_allclose(manual[j], rms[i, j], rtol=1e-12, equal_nan=True)
                        admitted = np.flatnonzero(np.isfinite(values[:, j]))[-3:]
                        excluded = np.flatnonzero(past.label_maturity_utc.ge(lock).to_numpy())
                        for k in np.r_[admitted, excluded]:
                            item = past.iloc[k]
                            ok = np.isfinite(values[k, j])
                            if ok:
                                assert item.label_maturity_utc < lock < row.issuance_utc
                            traces.append(
                                dict(
                                    forecast_origin=row.origin_id,
                                    slot=slot,
                                    input_day=day,
                                    lock=str(lock),
                                    issue=str(row.issuance_utc),
                                    history_origin=item.origin_id,
                                    endpoint=str(item.exit_end_utc),
                                    maturity=str(item.label_maturity_utc),
                                    admitted=bool(ok),
                                    native_rms=float(manual[j]) if np.isfinite(manual[j]) else None,
                                    risk_complete_origin=bool(valid[i]),
                                    valid_history_count=int(np.isfinite(values[:, j]).sum()),
                                )
                            )
            print(
                year,
                phase,
                "origins",
                len(train),
                "selected",
                [PENALTIES[k] for k in chosen],
                "elapsed",
                round(time.monotonic() - tick, 1),
                flush=True,
            )
            del view, gram, rhs, y, ys
            gc.collect()
            b.memory()
    pd.concat(outputs, ignore_index=True).to_parquet(
        OUT / "OOS_SCORES.parquet", index=False, compression="zstd"
    )
    pd.DataFrame(trials).to_csv(OUT / "RIDGE_SELECTION.csv", index=False)
    pd.DataFrame(fits).to_csv(OUT / "RIDGE_FITS.csv", index=False)
    b.write(
        OUT / "CHECKS.json",
        dict(
            status="PARTIAL_BLOCKED" if blocked else "PASS",
            blocked=blocked,
            key_identity="exact saved S4 and archived N1",
            N1_tensor_score_exact=True,
            source_revision=config["source_revision"],
            coverage=summaries,
            maturity_examples=traces,
            training_isolation="all saved roles,maturity cutoffs and48-step embargo verified",
            sigma_convention=config["sigma"],
            trial_target_fits=len(trials),
            final_target_fits=len(fits),
            neural_starts=0,
            seconds=time.monotonic() - tick,
            peak_rss_bytes=b.memory(),
        ),
        new=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["run", "resume-saved-first-fold", "finish-valid-stages", "report"]
    )
    args = parser.parse_args()
    if args.action != "report":
        run(
            resume_first_fold=args.action != "run",
            complete_valid=args.action == "finish-valid-stages",
        )
    else:
        from .hf20_targets_report import report

        report()


if __name__ == "__main__":
    main()
