"""Bounded T0/T2 successor: full raw ridge, one causal risk proxy, conditional Z ridge."""

from __future__ import annotations

import argparse
import gc
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_mag_designa as b
from . import hf20_targets as old
from .hf20_ranking import origin_weights, ridge_solution

OUT = Path("reports/experiments/hf20_t0_t2_repair_2026-10-29_v2")


def window_bounds(
    days: np.ndarray,
    maturity: np.ndarray,
    current: np.ndarray,
    issue: np.ndarray,
    lower: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Prior session dates and matured <= issue; equality at maturity is lawful."""
    hi = np.minimum(
        np.searchsorted(days, current, side="left"), np.searchsorted(maturity, issue, side="right")
    )
    lo = np.minimum(np.searchsorted(days, lower, side="left"), hi)
    return lo, hi


def risk_history(rows: pd.DataFrame, returns: np.ndarray) -> dict[str, np.ndarray]:
    """Stock-level valid-observation histories, never a complete-panel history filter."""
    assert rows.origin_id.is_unique and rows.entry_end_utc.is_monotonic_increasing
    assert rows.label_maturity_utc.is_monotonic_increasing
    days = rows.session_date_et.to_numpy()
    regular = rows.regular_session.to_numpy(bool)
    regdays = np.unique(days[regular])
    q = np.searchsorted(regdays, days, side="left")
    lower = regdays[np.clip(q - 252, 0, len(regdays) - 1)]
    maturity = (
        pd.DatetimeIndex(rows.label_maturity_utc).to_numpy(dtype="datetime64[ns]").view("int64")
    )
    issue = pd.DatetimeIndex(rows.issuance_utc).to_numpy(dtype="datetime64[ns]").view("int64")
    context = rows.context.to_numpy(int)
    n, stocks = returns.shape
    result: dict[str, np.ndarray] = {
        key: np.full((n, stocks), np.nan)
        for key in ["rms", "age_same", "age_all", "age_all_hours", "same_span", "missing_same_252"]
    }
    result.update({key: np.zeros((n, stocks), dtype=np.int16) for key in ["n_same", "n_all"]})
    result["composition"] = np.zeros((n, stocks, 7), dtype=np.int16)
    for j in range(stocks):
        pool_mean = np.zeros(n)
        for c in [-1, *range(7)]:
            mask = regular & np.isfinite(returns[:, j])
            if c >= 0:
                mask &= context == c
            ix = np.flatnonzero(mask)
            lo, hi = window_bounds(days[ix], maturity[ix], days, issue, lower)
            count = np.minimum(hi - lo, 200 if c == -1 else 60)
            start = hi - count
            prefix = np.r_[0.0, np.cumsum(returns[ix, j] ** 2)]
            mean = (prefix[hi] - prefix[start]) / np.maximum(count, 1)
            age = np.full(n, np.nan)
            supported = count > 0
            last = ix[hi[supported] - 1]
            age[supported] = q[supported] - np.searchsorted(regdays, days[last])
            if c == -1:
                pool_mean = mean
                result["n_all"][:, j] = count
                result["age_all"][:, j] = age
                result["age_all_hours"][supported, j] = (issue[supported] - maturity[last]) / 3.6e12
                for k in range(7):
                    cp = np.r_[0, np.cumsum(context[ix] == k)]
                    result["composition"][:, j, k] = cp[hi] - cp[start]
            else:
                take = context == c
                result["n_same"][take, j] = count[take]
                result["age_same"][take, j] = age[take]
                both = supported & take
                first = ix[start[both]]
                result["same_span"][both, j] = q[both] - np.searchsorted(regdays, days[first])
                variance = (count * mean + 20 * pool_mean) / (count + 20)
                result["rms"][take, j] = np.sqrt(np.maximum(variance[take], 0))
                scheduled = np.flatnonzero(regular & (context == c))
                sl, sh = window_bounds(days[scheduled], maturity[scheduled], days, issue, lower)
                result["missing_same_252"][take, j] = (sh - sl - (hi - lo))[take]
    result["rms"][result["n_all"] < 30] = np.nan
    return result


def histories(rows: pd.DataFrame, returns: np.ndarray, i: int, j: int):
    """Small independent direct-selection witness; not used to calculate the bulk proxy."""
    row = rows.iloc[i]
    previous = np.unique(
        rows.loc[
            rows.regular_session & rows.session_date_et.lt(row.session_date_et), "session_date_et"
        ].to_numpy()
    )[-252:]
    mask = (
        rows.regular_session
        & rows.session_date_et.isin(previous)
        & rows.entry_end_utc.lt(row.entry_end_utc)
        & rows.label_maturity_utc.le(row.issuance_utc)
    ).to_numpy()
    valid = mask & np.isfinite(returns[:, j])
    same = np.flatnonzero(valid & rows.context.eq(row.context).to_numpy())[-60:]
    pool = np.flatnonzero(valid)[-200:]
    return same, pool


def positions(role: np.ndarray, scale: np.ndarray | None = None) -> np.ndarray:
    """Raw fit population is unconditional; only Z fits require a complete scale."""
    return role if scale is None else role[np.isfinite(scale[role]).all(1)]


def coverage(
    rows: pd.DataFrame,
    risk: dict[str, np.ndarray],
    roles: dict,
    year: int,
    phase: str,
    floors: np.ndarray,
) -> list[dict]:
    records = []
    sigma, valid = old.risk_scale(risk["rms"], floors)
    for role in ["inner_train", "inner_validation"] if phase == "inner" else ["refit", "oos"]:
        base = roles[role]
        groups = [("ALL", "ALL", base, np.arange(20))]
        groups += [("STOCK", s, base, np.array([j])) for j, s in enumerate(b.SYMBOLS)]
        for col in ["slot", "category"]:
            groups += [
                (col, str(v), base[rows.iloc[base][col].eq(v)], np.arange(20))
                for v in rows.iloc[base][col].unique()
            ]
        for level, name, ix, js in groups:
            sl = np.ix_(ix, js)
            cells = np.isfinite(sigma[sl])
            ok = cells.all(1)
            record: dict[str, str | int | float | None] = dict(
                year=year,
                phase=phase,
                role=role,
                level=level,
                group=name,
                original_origins=len(ix),
                scale_complete=int(ok.sum()),
                fraction=float(ok.mean()),
                sessions=rows.iloc[ix[ok]].session_date_et.nunique(),
                floor_min=float(floors[js].min()),
                floor_max=float(floors[js].max()),
                floor_hit=float(
                    ((risk["rms"][sl] < floors[js]) & cells).sum() / max(cells.sum(), 1)
                ),
                fallback=float(((risk["n_same"][sl] == 0) & cells).sum() / max(cells.sum(), 1)),
            )
            for key in [
                "n_same",
                "n_all",
                "age_same",
                "age_all",
                "age_all_hours",
                "same_span",
                "missing_same_252",
            ]:
                values = risk[key][sl].ravel()
                values = values[np.isfinite(values)]
                for suffix, p in [("min", 0), ("p50", 0.5), ("p95", 0.95), ("max", 1)]:
                    record[key + "_" + suffix] = (
                        float(np.quantile(values, p)) if len(values) else None
                    )
            record["same_older_than5_sessions"] = float((risk["age_same"][sl] > 5).mean())
            for c in range(7):
                record[f"pool_context{c}_mass"] = float(
                    risk["composition"][ix][:, js, c].sum() / max(risk["n_all"][sl].sum(), 1)
                )
            records.append(record)
    assert valid.shape == (len(rows),)
    return records


def fit_target(
    c,
    rows: pd.DataFrame,
    returns: np.ndarray,
    grid: pd.DataFrame,
    target: str,
    log: list[dict],
    risk: dict[str, np.ndarray] | None = None,
):
    """Exactly three inner solves and one fresh final solve per supported fold."""
    outputs = []
    for year in b.YEARS:
        roles = old.load_roles(rows, grid, year)
        selected = None
        for phase, train_role, eval_role in [
            ("inner", "inner_train", "inner_validation"),
            ("refit", "refit", "oos"),
        ]:
            tick = time.monotonic()
            recipe = b.read(b.S4 / f"F{year % 100}_{phase}_recipe.json")
            scale = None
            if risk is not None:
                floors = np.array([f["m2_floor"] for f in recipe["floors"]])
                scale = old.risk_scale(risk["rms"], floors)[0]
            train, test = positions(roles[train_role], scale), positions(roles[eval_role], scale)
            assert len(train) and len(test)
            if target == "R":
                np.testing.assert_array_equal(train, roles[train_role])
                np.testing.assert_array_equal(test, roles[eval_role])
            y = returns[train] if scale is None else returns[train] / scale[train]
            actual = returns[test] if scale is None else returns[test] / scale[test]
            ys, mean, sd = old.target_standardize(
                y[:, :, None], rows.iloc[train].session_date_et.to_numpy()
            )
            view = b.View(c, rows, returns, recipe, 1.0)
            # Reuse the first-session two-RHS accumulator; only first RHS is solved here.
            gram, rhs2 = old.system(view, train, np.repeat(ys, 2, axis=2))
            rhs = rhs2[:, 0]
            trials = []
            penalties = old.PENALTIES if phase == "inner" else (selected,)
            for penalty in penalties:
                assert penalty is not None
                coef = ridge_solution(gram, rhs, penalty)
                forecast = old.predict(view, test, coef[:, None])[:, :, 0] * sd[0] + mean[0]
                loss = float(
                    origin_weights(rows.iloc[test].session_date_et.to_numpy())
                    @ ((forecast - actual) ** 2).mean(1)
                )
                record = dict(
                    year=year,
                    target=target,
                    phase=phase,
                    penalty=penalty,
                    MSE=loss,
                    train_origins=len(train),
                    evaluation_origins=len(test),
                    fit_stop=recipe["fit_stop_inclusive"],
                    center=float(mean[0]),
                    scale=float(sd[0]),
                    seconds=time.monotonic() - tick,
                )
                log.append(record)
                pd.DataFrame(log).to_csv(OUT / "FITS.csv", index=False)
                trials.append((loss, penalty))
                if phase == "refit":
                    np.savez_compressed(
                        OUT / f"F{year % 100}_{target}.npz",
                        coefficient=coef,
                        mean=mean,
                        scale=sd,
                        penalty=penalty,
                    )
                    with np.load(OUT / f"F{year % 100}_{target}.npz") as saved:
                        replay = (
                            view.x(test[:2]).reshape(-1, 20, 768) @ saved["coefficient"][:-1]
                            + saved["coefficient"][-1]
                        ) * saved["scale"][0] + saved["mean"][0]
                    np.testing.assert_allclose(replay, forecast[:2], rtol=1e-6, atol=1e-10)
                    ix = roles["oos"]
                    frame = rows.iloc[ix][["origin_id", "session_date_et", "slot", "category"]]
                    frame = frame.loc[frame.index.repeat(20)].reset_index(drop=True)
                    frame["fold"], frame["ticker"] = year, list(b.SYMBOLS) * len(ix)
                    p = np.full((len(ix), 20), np.nan)
                    p[np.isin(ix, test)] = forecast
                    frame["RIDGE-" + target] = p.ravel()
                    if target == "R":
                        frame["R"] = returns[ix].ravel()
                    else:
                        assert scale is not None
                        frame["sigma"] = scale[ix].ravel()
                    outputs.append(frame)
                    pd.concat(outputs).to_parquet(OUT / f"{target}_SCORES.parquet", index=False)
            if phase == "inner":
                selected = min(trials, key=lambda item: (item[0], -item[1]))[1]
            print(
                target,
                year,
                phase,
                "selected",
                selected,
                "origins",
                len(train),
                "seconds",
                round(time.monotonic() - tick, 2),
                flush=True,
            )
            del view, gram, rhs, rhs2, ys
            gc.collect()
            b.memory()
    return pd.concat(outputs, ignore_index=True)


def run() -> None:
    plan = b.read(OUT / "PLAN.json")
    for path, sha in plan["preserve"].items():
        assert b.digest(Path(path)) == sha
    cfg = b.read(old.OUT / "REPRODUCIBILITY.json")
    for p, sha in cfg["essential_bindings"].items():
        assert b.digest(Path(p)) == sha
    for item in [*cfg["roles"].values(), *cfg["recipes"].values()]:
        assert b.digest(Path(item["path"])) == item["sha256"]
    b.write(OUT / "STARTED.json", dict(at=pd.Timestamp.now(tz="UTC").isoformat()), new=True)
    tick = time.monotonic()
    grid, rows = b.metadata()
    c, returns = b.source_components(grid, rows)
    log = []
    raw = fit_target(c, rows, returns, grid, "R", log)
    archived = pd.read_parquet(old.OUT / "OOS_SCORES.parquet")
    for key in ["origin_id", "ticker", "R"]:
        np.testing.assert_array_equal(raw[key], archived[key])
    check: dict[str, object] = dict(
        raw_status="COMPLETED",
        raw_rows=len(raw),
        neural_starts=0,
        source_history_origins=len(rows),
        partial_stock_history_origins=int(
            (np.isfinite(returns).any(1) & ~np.isfinite(returns).all(1)).sum()
        ),
    )
    try:
        risk = risk_history(rows, returns)
        records = []
        for year in b.YEARS:
            roles = old.load_roles(rows, grid, year)
            for phase in ["inner", "refit"]:
                recipe = b.read(b.S4 / f"F{year % 100}_{phase}_recipe.json")
                floors = np.array([x["m2_floor"] for x in recipe["floors"]])
                records += coverage(rows, risk, roles, year, phase, floors)
        cv = pd.DataFrame(records)
        cv.to_csv(OUT / "COVERAGE.csv", index=False)
        allrows = cv.loc[cv.level.eq("ALL")]
        gate = bool(
            (allrows.loc[allrows.role.eq("oos"), "fraction"] >= 0.9).all()
            and (allrows.loc[allrows.role.eq("inner_validation"), "sessions"] >= 50).all()
            and (
                cv.loc[cv.role.eq("inner_validation") & cv.level.eq("slot"), "scale_complete"] >= 25
            ).all()
            and (
                cv.loc[cv.role.eq("oos") & cv.level.isin(["category", "slot"]), "scale_complete"]
                > 0
            ).all()
        )
        check["risk_gate"] = gate
        check["coverage_gate_time"] = pd.Timestamp.now(tz="UTC").isoformat()
        check["witnesses"] = witnesses(rows, returns, risk)
        b.write(OUT / "CHECKS.json", check)
        print(
            "Risk coverage gate",
            gate,
            allrows.loc[allrows.role.eq("oos"), ["year", "fraction"]].to_dict("records"),
            flush=True,
        )
        # Save scale-only records even if Z cannot be fitted. Never gate raw predictions.
        scales = []
        for year in b.YEARS:
            ix = old.load_roles(rows, grid, year)["oos"]
            recipe = b.read(b.S4 / f"F{year % 100}_refit_recipe.json")
            floors = np.array([x["m2_floor"] for x in recipe["floors"]])
            frame = raw.loc[raw.fold.eq(year), ["origin_id", "ticker", "fold"]].copy()
            frame["sigma"] = old.risk_scale(risk["rms"], floors)[0][ix].ravel()
            scales.append(frame)
        pd.concat(scales).to_parquet(OUT / "RISK_SCORES.parquet", index=False)
        if gate:
            fit_target(c, rows, returns, grid, "Z", log, risk)
        check["normalized_status"] = "COMPLETED" if gate else "BLOCKED_COVERAGE"
    except Exception:
        (OUT / "risk_failure.txt").write_text(traceback.format_exc())
        check["normalized_status"] = "BLOCKED_RISK_OR_Z_ERROR"
    check.update(
        seconds=time.monotonic() - tick,
        peak_rss_bytes=b.memory(),
        final_fits=sum(x["phase"] == "refit" for x in log),
        validation_solves=sum(x["phase"] == "inner" for x in log),
    )
    b.write(OUT / "CHECKS.json", check)


def witnesses(rows: pd.DataFrame, returns: np.ndarray, risk: dict[str, np.ndarray]) -> list[dict]:
    cases = []
    for slot in ["09:30", "15:30"]:
        i = int(
            rows.loc[
                rows.eligible & rows.session_date_et.ge("2021-01-13") & rows.slot.eq(slot)
            ].index[0]
        )
        cases.append((i, list(b.SYMBOLS).index("AVGO"), slot))
    for label, mask in [
        ("pooled_fallback", (risk["n_same"] == 0) & (risk["n_all"] >= 30)),
        ("missing_risk", risk["n_all"] < 30),
    ]:
        found = np.argwhere(mask)
        if len(found):
            i, j = map(int, found[0])
            cases.append((i, j, label))
    result = []
    for i, j, label in cases:
        same, pool = histories(rows, returns, i, j)
        assert len(same) == risk["n_same"][i, j] and len(pool) == risk["n_all"][i, j]
        if len(pool) >= 30:
            direct = np.sqrt(
                (np.sum(returns[same, j] ** 2) + 20 * np.mean(returns[pool, j] ** 2))
                / (len(same) + 20)
            )
            np.testing.assert_allclose(direct, risk["rms"][i, j], rtol=1e-11, atol=1e-13)
        obs = []
        for k in np.unique(np.r_[same[-3:], pool[-3:]]):
            h = rows.iloc[k]
            assert h.label_maturity_utc <= rows.iloc[i].issuance_utc
            obs.append(
                dict(
                    origin=h.origin_id,
                    endpoint=str(h.exit_end_utc),
                    maturity=str(h.label_maturity_utc),
                    R=float(returns[k, j]),
                )
            )
        assert rows.iloc[i].label_maturity_utc > rows.iloc[i].issuance_utc
        immature = np.flatnonzero(
            (
                rows.entry_end_utc.lt(rows.iloc[i].entry_end_utc)
                & rows.label_maturity_utc.gt(rows.iloc[i].issuance_utc)
            ).to_numpy()
            & np.isfinite(returns[:, j])
        )
        excluded = None
        if len(immature):
            k = int(immature[-1])
            assert k not in pool and k not in same
            excluded = dict(
                origin=rows.iloc[k].origin_id,
                maturity=str(rows.iloc[k].label_maturity_utc),
                admitted=False,
            )
        result.append(
            dict(
                case=label,
                origin=rows.iloc[i].origin_id,
                ticker=b.SYMBOLS[j],
                issue=str(rows.iloc[i].issuance_utc),
                n_same=len(same),
                n_all=len(pool),
                current_target_excluded=True,
                immature_prior_excluded=excluded,
                observations=obs,
            )
        )
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["run", "report"])
    if p.parse_args().action == "run":
        run()
    else:
        from .hf20_targets_repair_report import report

        report()


if __name__ == "__main__":
    main()
