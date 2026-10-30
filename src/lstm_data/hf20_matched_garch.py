"""One supported Gaussian GARCH(1,1) estimate per legal stock-slot-fold."""

from __future__ import annotations

import time
import traceback
import warnings

import numpy as np
import pandas as pd
from arch import arch_model

from . import hf20_matched as task
from .hf20_classical_math import folded_normal
from .hf20_matched_math import mature_prefix, next_variance

b, c3, old, OUT = task.b, task.c3, task.old, task.OUT


def admitted(rows: pd.DataFrame) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    """Independent chronological greedy overlap audit, shared complete20 support."""
    streams, reference = old.stream_masks(rows)
    result = {}
    audit = []
    for slot, indices in streams.items():
        last = None
        keep = []
        for i in indices:
            row = rows.iloc[i]
            ok = last is None or row.entry_end_utc >= last
            audit.append(
                dict(
                    row_index=int(i),
                    origin_id=row.origin_id,
                    slot=slot,
                    start=str(row.entry_end_utc),
                    end=str(row.exit_end_utc),
                    maturity=str(row.label_maturity_utc),
                    category=row.category,
                    retained=ok,
                    previous_retained_end=str(last),
                    stocks=20,
                )
            )
            if ok:
                keep.append(i)
                last = row.exit_end_utc
        result[slot] = np.asarray(keep, dtype=np.int64)
        np.testing.assert_array_equal(result[slot], reference[slot])
    return result, pd.DataFrame(audit)


def run() -> None:
    """No retries: retain failed units and block all-fold scoring if any gate fails."""
    task.preservation()
    b.write(OUT / "garch_started.json", dict(at=pd.Timestamp.now(tz="UTC").isoformat()), new=True)
    tick = time.monotonic()
    grid, rows = b.metadata()
    plans = old.rank.validate_roles(grid, rows)
    signed = old.signed_targets(rows)
    streams, audit = admitted(rows)
    audit.to_csv(OUT / "garch_overlap_audit.csv", index=False)
    diagnostics = []
    traces = []
    all_ok = True
    support = pd.read_csv(OUT / "garch_support_prefit.csv")
    for year, roles in plans.items():
        dest = OUT / f"GARCH/F{year % 100}"
        dest.mkdir(parents=True)
        scores = {
            role: pd.read_parquet(c3.root(year) / f"{role}_scores.parquet", columns=[*c3.META, "A"])
            for role in ["calibration", "oos"]
        }
        forecasts = {role: np.full((len(roles[role]), 20), np.nan) for role in scores}
        for slot, stream in streams.items():
            fit = np.intersect1d(stream, roles["restricted_refit"])
            future = stream[stream > fit[-1]]
            maturity = rows.iloc[future].label_maturity_utc.dt.as_unit("ns").array.asi8
            query = sorted(
                [
                    (int(ix), role, j)
                    for role in scores
                    for j, ix in enumerate(roles[role])
                    if rows.iloc[ix].slot == slot
                ]
            )
            for stock, ticker in enumerate(b.SYMBOLS):
                unit = dest / (ticker + "_" + slot.replace(":", ""))
                unit.mkdir()
                b.write(unit / "started.json", dict(year=year, ticker=ticker, slot=slot), new=True)
                task.journal("GARCH_UNIT_STARTED", year=year, ticker=ticker, slot=slot)
                unit_tick = time.monotonic()
                d = dict(year=year, ticker=ticker, slot=slot, n=len(fit), status="FAILED")
                try:
                    x = 100 * signed[fit, stock]
                    assert len(x) == int(
                        support.loc[
                            (support.year == year)
                            & (support.slot == slot)
                            & (support.ticker == ticker),
                            "n",
                        ].iloc[0]
                    )
                    model = arch_model(
                        x, mean="Constant", vol="GARCH", p=1, o=0, q=1, dist="normal", rescale=False
                    )
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        result = model.fit(
                            update_freq=0,
                            disp="off",
                            tol=1e-9,
                            options={"maxiter": 1000, "ftol": 1e-9},
                        )
                    mu, omega, alpha, beta = (
                        float(result.params[k]) for k in ["mu", "omega", "alpha[1]", "beta[1]"]
                    )
                    h = np.asarray(result.conditional_volatility) ** 2
                    persistence = alpha + beta
                    valid = bool(
                        result.convergence_flag == 0
                        and np.isfinite([mu, omega, alpha, beta]).all()
                        and omega > 0
                        and alpha >= 0
                        and beta >= 0
                        and persistence < 1
                        and np.isfinite(omega / (1 - persistence))
                        and np.isfinite(h).all()
                        and (h > 0).all()
                    )
                    d.update(
                        mu_percent=mu,
                        omega_percent_squared=omega,
                        alpha=alpha,
                        beta=beta,
                        persistence=persistence,
                        near_unit=persistence >= 0.99,
                        convergence_flag=int(result.convergence_flag),
                        optimizer_message=str(result.optimization_result.message),
                        iterations=int(result.optimization_result.nit),
                        variance_min=float(h.min()),
                        variance_max=float(h.max()),
                        unconditional_variance=omega / (1 - persistence)
                        if persistence < 1
                        else None,
                        warnings=[str(w.message) for w in caught],
                        loglikelihood=float(result.loglikelihood),
                        status="PASS" if valid else "BLOCKED_FIT_GATE",
                    )
                    b.write(unit / "parameters.json", d, new=True)
                    np.savez_compressed(unit / "fit_state.npz", indices=fit, x=x, h=h)
                    if not valid:
                        all_ok = False
                    else:
                        state = next_variance(float(h[-1]), float(x[-1]), mu, omega, alpha, beta)
                        # Preserve the estimator's prefix starting-residual backcast/bounds.
                        # ConstantMean.forecast recomputes its backcast at the fitted mean.
                        vol = model.volatility
                        initial_residuals = x - x.mean()
                        forecast = vol.forecast(
                            np.array([omega, alpha, beta]),
                            x - mu,
                            vol.backcast(initial_residuals),
                            vol.variance_bounds(initial_residuals),
                            start=len(x) - 1,
                            horizon=1,
                        )
                        assert forecast.forecasts is not None
                        arch_next = float(forecast.forecasts[-1, 0])
                        np.testing.assert_allclose(state, arch_next, rtol=1e-10, atol=1e-12)
                        cursor = 0
                        last = int(fit[-1])
                        updates = []
                        for index, role, j in query:
                            row = rows.iloc[index]
                            end = mature_prefix(maturity, int(row.issuance_utc.value))
                            for update in future[cursor:end]:
                                before = state
                                state = next_variance(
                                    state,
                                    float(100 * signed[update, stock]),
                                    mu,
                                    omega,
                                    alpha,
                                    beta,
                                )
                                updates.append(
                                    dict(
                                        row_index=int(update),
                                        h_before=before,
                                        x=float(100 * signed[update, stock]),
                                        h_after=state,
                                    )
                                )
                                last = int(update)
                            cursor = end
                            assert rows.iloc[last].label_maturity_utc < row.issuance_utc
                            # Endpoint maturity implies no unfinished interval enters state.
                            assert rows.iloc[last].exit_end_utc <= row.entry_end_utc
                            pred = float(
                                folded_normal(np.array([mu / 100]), np.array([state / 10000]))[0]
                            )
                            forecasts[role][j, stock] = pred
                            traces.append(
                                dict(
                                    year=year,
                                    ticker=ticker,
                                    slot=slot,
                                    role=role,
                                    origin_id=row.origin_id,
                                    category=row.category,
                                    early_close=not bool(row.regular_session),
                                    issue=str(row.issuance_utc),
                                    latest_update_origin=rows.iloc[last].origin_id,
                                    latest_maturity=str(rows.iloc[last].label_maturity_utc),
                                    latest_endpoint=str(rows.iloc[last].exit_end_utc),
                                    updates_after_fit=cursor,
                                    variance_percent_squared=state,
                                    mu_log=mu / 100,
                                    sigma_log=float(np.sqrt(state) / 100),
                                    prediction=pred,
                                )
                            )
                        pd.DataFrame(updates).to_csv(unit / "state_updates.csv", index=False)
                except Exception:
                    all_ok = False
                    (unit / "failure.txt").write_text(traceback.format_exc())
                    d["status"] = "FAILED_EXCEPTION"
                d["seconds"] = time.monotonic() - unit_tick
                diagnostics.append(d)
                b.write(unit / "completion.json", d, new=True)
                task.journal(
                    "GARCH_UNIT_FINISHED",
                    year=year,
                    ticker=ticker,
                    slot=slot,
                    result=d["status"],
                    seconds=d["seconds"],
                )
            task.resources()
        for role, f in scores.items():
            f["GARCH11-FN-UNCAL"] = forecasts[role].ravel()
            f.to_parquet(dest / f"{role}_scores.parquet", index=False, compression="zstd")
        print(
            "GARCH",
            year,
            "completed units",
            len(diagnostics),
            "passing",
            sum(d["status"] == "PASS" for d in diagnostics),
            flush=True,
        )
    pd.DataFrame(diagnostics).to_csv(OUT / "garch_fit_diagnostics.csv", index=False)
    pd.DataFrame(traces).to_csv(OUT / "garch_filter_trace.csv", index=False)
    receipt = dict(
        status="COMPLETE" if all_ok else "PARTIAL_BLOCKED",
        fits=len(diagnostics),
        passing=sum(d["status"] == "PASS" for d in diagnostics),
        failures=sum(d["status"] != "PASS" for d in diagnostics),
        retry=0,
        excluded_history_origins=int((~audit.retained).sum()),
        evaluation_keys_dropped=0,
        seconds=time.monotonic() - tick,
        **task.resources(),
    )
    b.write(OUT / "garch_status.json", receipt, new=True)
    task.journal("GARCH_FINISHED", result=receipt)
