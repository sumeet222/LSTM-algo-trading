"""Single-use, non-neural classical four-hour magnitude benchmark study."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_mag_rank as rank
from . import hf20_stage2_bcd as clock
from .hf20_classical_math import (
    deoverlap,
    ewma,
    folded_normal,
    har_features,
    multiplier,
    ridge_fit,
    ridge_predict,
)

OUT = Path("reports/experiments/hf20_s9_mag_classical_volatility_benchmarks_2026-10-29")
TARGET = b.S4 / "opening_reaudit_v2/S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet"
HYBRID = Path("reports/experiments/hf20_s9_mag_stage5_session2_hybrid_C_2026-10-29")
S2C = Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28")
ARMS = ("ROLL20", "ROLL60", "EXPANDING", "EWMA-R2-FN", "EWMA-A", "HAR-RV-A")


def resources() -> dict:
    """Aggregate sizes only; never enumerate protected data or manifests."""
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    result = dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())
    if project + 30_000_000 > b.CAPS["project_bytes"] or task + 30_000_000 > b.CAPS["task_bytes"]:
        raise ValueError("RESOURCE_CEILING", result)
    return result


def history(rows: pd.DataFrame) -> np.ndarray:
    """The original complete-panel source/input/label support, never expanded."""
    return np.flatnonzero(rows.eligible & rows.session_date_et.between("2011-04-01", "2024-12-31"))


def signed_targets(rows: pd.DataFrame) -> np.ndarray:
    """Minimal saved genuine endpoints; no components/minute outcomes opened."""
    f = pd.read_parquet(
        TARGET,
        columns=["origin_id", "ticker", "direct_return", "entry_source_price", "exit_source_price"],
    )
    np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.origin_id)
    assert f.ticker.tolist() == list(b.SYMBOLS) * len(rows)
    r = f.direct_return.to_numpy().reshape(-1, 20)
    ix = history(rows)
    start = f.entry_source_price.to_numpy().reshape(-1, 20)[ix]
    end = f.exit_source_price.to_numpy().reshape(-1, 20)[ix]
    assert (
        np.isfinite(start).all()
        and np.isfinite(end).all()
        and (start > 0).all()
        and (end > 0).all()
    )
    np.testing.assert_allclose(r[ix], np.log(end / start), atol=1e-12, rtol=1e-11)
    return r


def stream_masks(rows: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Chronological same-slot streams and researcher-approved causal R2 thinning."""
    h = history(rows)
    streams, thin = {}, {}
    for slot in b.SLOTS:
        ix = h[rows.iloc[h].slot.eq(slot).to_numpy()]
        g = rows.iloc[ix]
        assert (
            g.entry_end_utc.is_monotonic_increasing and g.label_maturity_utc.is_monotonic_increasing
        )
        assert not g.session_date_et.duplicated().any()
        keep = deoverlap(
            g.entry_end_utc.dt.as_unit("ns").array.asi8, g.exit_end_utc.dt.as_unit("ns").array.asi8
        )
        streams[slot], thin[slot] = ix, ix[keep]
        kept = rows.iloc[ix[keep]]
        assert (
            kept.exit_end_utc.dt.as_unit("ns").array.asi8[:-1]
            <= kept.entry_end_utc.dt.as_unit("ns").array.asi8[1:]
        ).all()
    return streams, thin


def freeze() -> None:
    """Declare all formulas and source boundaries before fitting or outcome scoring."""
    if OUT.exists():
        raise ValueError("SINGLE_USE_NAMESPACE")
    OUT.mkdir()
    pointer = b.read(b.POINTER)
    entries = [json.loads(x) for x in Path(pointer["real_journal"]).read_text().splitlines()]
    assert entries[-1]["status"] == "COMPLETED" and entries[-1]["global_started_pairs"] == 186
    old = b.read(HYBRID / "protocol.json")
    bindings = dict(old["preservation_bindings"])
    paths = [
        b.POINTER,
        Path(pointer["real_journal"]),
        TARGET,
        b.S4 / "opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet",
        b.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv",
        b.S4 / "opening_reaudit_v2/S4_SOURCE_POLICY.json",
        c3.O1 / "role_indices.npz",
        c3.CONT / "role_counts.csv",
        HYBRID / "protocol.json",
        HYBRID / "S5C_HYBRID_FINAL_REPORT.md",
    ]
    for year in b.YEARS:
        for root in [
            c3.root(year),
            clock.OUT / f"s2b_clock/F{year % 100}",
            S2C / f"F{year % 100}",
            HYBRID / f"F{year % 100}",
        ]:
            paths.append(root / "oos_scores.parquet")
        paths += [
            c3.root(year) / "calibration_scores.parquet",
            c3.O1 / f"F{year % 100}/phases.json",
        ]
    paths += [
        Path(__file__).relative_to(Path.cwd()) if Path(__file__).is_absolute() else Path(__file__),
        Path("src/lstm_data/hf20_classical_math.py"),
        Path("src/lstm_data/hf20_classical_rv.py"),
        Path("tests/test_hf20_classical.py"),
    ]
    for p in paths:
        bindings[str(p)] = b.digest(p)
    # Inherited binding contains the prior pointer version, replaced above by live state.
    for name, sha in bindings.items():
        assert b.digest(Path(name)) == sha, ("CHANGED_PREDECESSOR", name)
    b.write(
        OUT / "protocol.json",
        dict(
            kind="HF20_CLASSICAL_MAGNITUDE_BENCHMARKS",
            date="2026-10-29",
            git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            starting_git_status=subprocess.check_output(
                ["git", "status", "--short", "--branch"], text=True
            ),
            preservation_bindings=bindings,
            neural_starts=0,
            ledger_before=186,
            ceiling=300,
            target=(
                "A=abs(log(genuine 240-trading-minute endpoint/origin)); original complete20 keys"
            ),
            symbols=list(b.SYMBOLS),
            roles=str(c3.O1 / "role_indices.npz"),
            expected_oos_rows=[19100, 23600, 17740, 19820],
            history=(
                "Original rows.eligible, dates2011-04-01..2024-12-31; same stock/slot; "
                "no expanded source population"
            ),
            asof=(
                "Only label_maturity_utc strictly less than issuance_utc; state paramet"
                "ers locked at restricted fit; no future state initialization"
            ),
            B1=(
                "ROLL20/ROLL60 exact arithmetic mean last20/60 matured valid same-slot "
                "A; EXPANDING all such A. Require60 for every calibration/OOS/selector "
                "origin; no fallback needed or allowed in this implementation"
            ),
            B2=dict(
                decay=0.94,
                mu=(
                    "hierarchical conditional weighted signed mean on restricted role and r"
                    "etained R2 history"
                ),
                seed_variance="same weighted centered second moment; strictly positive",
                seed_A="weighted mean A on unthinned restricted stock-slot role",
                burnin=(
                    "start from prefix seeds, filter each corresponding restricted-fit obse"
                    "rvation once chronologically; then only non-fit observations later tha"
                    "n final retained fit maturity"
                ),
                r2_deoverlap=(
                    "User amendment: chronological greedy keep start>=last kept genuine end"
                    "point; decisions use earlier intervals only. Thinned fit and updates f"
                    "or R2 only, never scoring keys or other histories"
                ),
                conversion="exact folded-normal expectation with abs(mu) zero-sigma limit",
                ewma_A="same .94 recursion on A, unthinned",
            ),
            B3=dict(
                status="BLOCKED",
                reason=(
                    "Neither arch/statsmodels nor scipy installed; no dependency installati"
                    "on authorized; zero GARCH fits, no substitute"
                ),
            ),
            B4=dict(
                source_grant=(
                    "User explicit follow-up authorizes same pinned source full-session clo"
                    "ses including closing half-hour, pre2025 only"
                ),
                revision="776328445b7ac6e7815ef3a483e9c8ded1eb6d56",
                columns=(
                    "ticker,timestamp,OHLC,is_rth,is_genuine,is_imputed,source_revision; sa"
                    "ved hourly factor/basis/quarantine/count/terminal close metadata; NO m"
                    "inute volume"
                ),
                RV=(
                    "Full390-minute regular sessions only; adjacent observed closes within "
                    "same day/basis; >=370 of389 pairs, RV=389*sum(r²)/count; invalid daily"
                    " RV remainsNaN"
                ),
                features=(
                    "log last1 / mean last5 / mean last22 regular-day RV plus corresponding"
                    " missing fractions (six fields); only dates strictly before origin day"
                ),
                fallback=(
                    "stock median valid native RV from unique prior22 input days of restric"
                    "ted fit; floor=max(median*1e-8,1e-16); replace missing RV by median be"
                    "fore lag means; no RV validation-selected thresholds"
                ),
                regression=(
                    "140 independent stock-slot weighted ridge fits/fold; original row weig"
                    "hts conditional on stock-slot; training weighted center/popSD, constan"
                    "t scale1; rawA/global legal restricted s; intercept unpenalized, mean "
                    "squared error+.01 slopeL2; solve normal equations; max(0) decode"
                ),
                source_failure="Block B4 only, never substitute hourly squares or drop target keys",
            ),
            calibration=(
                "One nonnegative global raw-A least-squares multiplier per arm/fold fro"
                "m reserved out-of-fit Oct-Dec; no C3 applied to classical forecasts"
            ),
            selection=(
                "No hyperparameter or candidate selection; no initial fit needed; exact"
                " September restricted parameters; all arms independently reported CAL "
                "primary/UNCAL diagnostic"
            ),
            evaluation=(
                "Original stock-origin-session-year hierarchy; rawA MSE primary, MAE,bi"
                "as,ratio; conservative constantIC0, true ties excluded/pred tieshalf, "
                "fractionaltopbottom4; sharedC0deciles, original prefix95/99 tails, slo"
                "ts/calendar/stocks/months; paired400 whole-month draws seed22042"
            ),
            comparisons=(
                "Frozen CLOCK-C3,S2C-C3,S5C-C3,C0,C3,C1a,M1,B0VOL/B0CLOCK/B0RMEAN plus "
                "savedRAW; no gap or rank-only magnitude metrics"
            ),
            uncertainty=(
                "exploratory/post-search, not selection-adjusted; no economic-value inference"
            ),
            timing_qualification=(
                "The original target's nominal origin is before approximate origin+2-mi"
                "nute publication."
            ),
            no_2025_2026_market_access=True,
            no_network=True,
            caps=b.CAPS,
            resources=resources(),
        ),
        new=True,
    )


def prepare() -> None:
    """All-fold source/geometry/history gates; no model or calibration fit."""
    freeze()
    grid, rows = b.metadata()
    plans = rank.validate_roles(grid, rows)
    streams, thin = stream_masks(rows)
    counts, overlaps, histories = [], [], []
    for slot, ix in streams.items():
        for n in ix[~np.isin(ix, thin[slot])]:
            preceding = thin[slot][thin[slot] < n][-1]
            overlaps.append(
                dict(
                    slot=slot,
                    excluded_origin=rows.iloc[n].origin_id,
                    retained_origin=rows.iloc[preceding].origin_id,
                    retained_exit=str(rows.iloc[preceding].exit_end_utc),
                    excluded_start=str(rows.iloc[n].entry_end_utc),
                )
            )
    assert len(overlaps) == 59
    for year, roles in plans.items():
        for role, ix in roles.items():
            f = rows.iloc[ix]
            counts.append(
                dict(
                    year=year,
                    role=role,
                    origins=len(f),
                    rows=20 * len(f),
                    sessions=f.session_date_et.nunique(),
                    first=str(f.session_date_et.min()),
                    last=str(f.session_date_et.max()),
                )
            )
        for role in ["selector", "calibration", "oos"]:
            for slot, ix in streams.items():
                queries = rows.iloc[roles[role]].loc[lambda f: f.slot.eq(slot)]
                n = np.searchsorted(
                    rows.iloc[ix].label_maturity_utc.dt.as_unit("ns").array.asi8,
                    queries.issuance_utc.dt.as_unit("ns").array.asi8,
                    side="left",
                )
                assert n.min() >= 60
                histories.append(
                    dict(
                        year=year,
                        role=role,
                        slot=slot,
                        minimum_matured_history=int(n.min()),
                        fallbacks=0,
                    )
                )
    pd.DataFrame(counts).to_csv(OUT / "role_counts.csv", index=False)
    pd.DataFrame(overlaps).to_csv(OUT / "r2_deoverlap_audit.csv", index=False)
    pd.DataFrame(histories).to_csv(OUT / "history_coverage.csv", index=False)
    r = signed_targets(rows)
    for year, roles in plans.items():
        for role, name in [
            ("oos", "oos_scores.parquet"),
            ("calibration", "calibration_scores.parquet"),
        ]:
            f = pd.read_parquet(c3.root(year) / name, columns=[*c3.META, "A"])
            np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.iloc[roles[role]].origin_id)
            np.testing.assert_array_equal(f.A.to_numpy().reshape(-1, 20), abs(r[roles[role]]))
    from .hf20_classical_rv import build_rv

    build_rv(
        OUT,
        str(rows.iloc[np.concatenate([p["oos"] for p in plans.values()])].session_date_et.max()),
    )
    # Source only: native RV support and 22-day history; no median/coefficients fitted here.
    rv = (
        pd.read_parquet(OUT / "daily_rv.parquet")
        .pivot(index="session_date_et", columns="ticker", values="rv")
        .reindex(columns=b.SYMBOLS)
    )
    for year, roles in plans.items():
        for role, ix in roles.items():
            assert (
                np.searchsorted(rv.index.to_numpy(), rows.iloc[ix].session_date_et.to_numpy()) >= 22
            ).all()
        prefix = rv.loc[rv.index < rows.iloc[roles["restricted_refit"]].session_date_et.max()]
        assert prefix.notna().sum().min() > 0
    b.write(
        OUT / "readiness.json",
        dict(
            status="READY",
            B1="PASS",
            B2="PASS_WITH_APPROVED_DEOVERLAP",
            B3="BLOCKED_DEPENDENCY",
            B4="SOURCE_PASS",
            roles=20,
            original_adjacent_overlaps=59,
            excluded_R2_history_origins=59,
            remaining_R2_overlaps=0,
            primary_rows_dropped=0,
            endpoint_identity=True,
            saved_target_key_parity=True,
            original_48step_roles=True,
            dependencies={
                x: importlib.util.find_spec(x) is not None for x in ["scipy", "arch", "statsmodels"]
            },
            ledger=186,
            resources=resources(),
        ),
        new=True,
    )


def dynamic_forecasts(
    rows: pd.DataFrame, r: np.ndarray, fit: np.ndarray, queries: np.ndarray
) -> tuple[dict[str, np.ndarray], list[dict], list[dict]]:
    """Predict before each strict maturity update frontier; parameters never refitted."""
    streams, thinned = stream_masks(rows)
    outputs = {name: np.full((len(queries), 20), np.nan) for name in ARMS[:-1]}
    params, audits = [], []
    fitw = pd.Series(b.origin_weights(rows.iloc[fit].session_date_et.to_numpy()), index=fit)
    for slot, stream in streams.items():
        qloc = np.flatnonzero(rows.iloc[queries].slot.eq(slot).to_numpy())
        qix = queries[qloc]
        mature = rows.iloc[stream].label_maturity_utc.dt.as_unit("ns").array.asi8
        origins = rows.iloc[stream].entry_end_utc.dt.as_unit("ns").array.asi8
        fit_all = stream[np.isin(stream, fit)]
        fit_r2 = thinned[slot][np.isin(thinned[slot], fit)]
        w = fitw.loc[fit_r2].to_numpy(copy=True)
        w /= w.sum()
        mu = w @ r[fit_r2]
        variance = w @ ((r[fit_r2] - mu) ** 2)
        wa = fitw.loc[fit_all].to_numpy(copy=True)
        wa /= wa.sum()
        mean_a = wa @ abs(r[fit_all])
        assert np.isfinite(variance).all() and (variance > 0).all()
        state_v, state_a = variance.copy(), mean_a.copy()
        for n in fit_r2:
            state_v = ewma(state_v, (r[n] - mu) ** 2)
        for n in fit_all:
            state_a = ewma(state_a, abs(r[n]))
        curs_a = int(np.searchsorted(stream, fit_all[-1], side="right"))
        rstream = thinned[slot]
        curs_r = int(np.searchsorted(rstream, fit_r2[-1], side="right"))
        for j, ticker in enumerate(b.SYMBOLS):
            params.append(
                dict(
                    ticker=ticker,
                    slot=slot,
                    fit_n=len(fit_all),
                    r2_fit_n=len(fit_r2),
                    mu=float(mu[j]),
                    variance_seed=float(variance[j]),
                    A_seed=float(mean_a[j]),
                    variance_after_fit=float(state_v[j]),
                    A_after_fit=float(state_a[j]),
                )
            )
        ar = abs(r[stream])
        cumulative = np.vstack([np.zeros(20), np.cumsum(ar, axis=0)])
        for loc, n in zip(qloc, qix):
            issue = rows.iloc[n].issuance_utc.value
            end = int(np.searchsorted(mature, issue, side="left"))
            assert (
                end >= 60
                and mature[end - 1] < issue
                and origins[end - 1] < rows.iloc[n].entry_end_utc.value
            )
            for k in [20, 60]:
                outputs[f"ROLL{k}"][loc] = (cumulative[end] - cumulative[end - k]) / k
            outputs["EXPANDING"][loc] = cumulative[end] / end
            while (
                curs_a < len(stream) and rows.iloc[stream[curs_a]].label_maturity_utc.value < issue
            ):
                state_a = ewma(state_a, abs(r[stream[curs_a]]))
                curs_a += 1
            while (
                curs_r < len(rstream)
                and rows.iloc[rstream[curs_r]].label_maturity_utc.value < issue
            ):
                state_v = ewma(state_v, (r[rstream[curs_r]] - mu) ** 2)
                curs_r += 1
            assert rows.iloc[stream[curs_a - 1]].label_maturity_utc.value < issue
            assert rows.iloc[rstream[curs_r - 1]].label_maturity_utc.value < issue
            outputs["EWMA-A"][loc] = state_a
            outputs["EWMA-R2-FN"][loc] = folded_normal(mu, state_v)
            audits.append(
                dict(
                    origin_id=rows.iloc[n].origin_id,
                    slot=slot,
                    issue=str(rows.iloc[n].issuance_utc),
                    history_n=end,
                    latest_used_origin=rows.iloc[stream[end - 1]].origin_id,
                    latest_maturity=str(rows.iloc[stream[end - 1]].label_maturity_utc),
                    R2_history_n=curs_r,
                    R2_latest_origin=rows.iloc[rstream[curs_r - 1]].origin_id,
                    R2_latest_maturity=str(rows.iloc[rstream[curs_r - 1]].label_maturity_utc),
                )
            )
    assert all(np.isfinite(x).all() and (x >= 0).all() for x in outputs.values())
    return outputs, params, audits


def har_forecasts(
    rows: pd.DataFrame, r: np.ndarray, fit: np.ndarray, queries: np.ndarray
) -> tuple[np.ndarray, list[dict], dict]:
    """One fixed September HAR fit, same keys and six prior-session RV predictors."""
    table = (
        pd.read_parquet(OUT / "daily_rv.parquet")
        .pivot(index="session_date_et", columns="ticker", values="rv")
        .reindex(columns=b.SYMBOLS)
    )
    dates, rv = table.index.to_numpy(), table.to_numpy()
    fd = rows.iloc[fit].session_date_et.to_numpy()
    ends = np.searchsorted(dates, fd)
    unique = np.unique((ends[:, None] - np.arange(1, 23)).ravel())
    assert unique.min() >= 0
    med = np.nanmedian(rv[unique], axis=0)
    assert np.isfinite(med).all() and (med > 0).all()
    floors = np.maximum(med * 1e-8, 1e-16)
    x, _ = har_features(rv, dates, fd, med, floors)
    q, missing = har_features(rv, dates, rows.iloc[queries].session_date_et.to_numpy(), med, floors)
    w = b.origin_weights(fd)
    scale = max(b.quantile(abs(r[fit]).ravel(), 0.5, np.repeat(w / 20, 20)), 1e-8)
    pred = np.full((len(queries), 20), np.nan)
    params = []
    for slot in b.SLOTS:
        select = rows.iloc[fit].slot.eq(slot).to_numpy()
        score = rows.iloc[queries].slot.eq(slot).to_numpy()
        for j, ticker in enumerate(b.SYMBOLS):
            model = ridge_fit(x[select, j], abs(r[fit[select], j]) / scale, w[select])
            pred[score, j] = ridge_predict(q[score, j], model, scale)
            params.append(dict(slot=slot, ticker=ticker, n=int(select.sum()), **model))
    assert np.isfinite(pred).all() and (pred >= 0).all()
    return (
        pred,
        params,
        dict(
            scale=float(scale),
            median_RV=med.tolist(),
            floor_RV=floors.tolist(),
            input_prefix_first=str(dates[unique.min()]),
            input_prefix_last=str(dates[unique.max()]),
            query_missing_fraction_by_stock=missing.mean(0).tolist(),
            query_cells_with_fallback=int((missing > 0).sum()),
            latest_day_strictly_before_origin=True,
        ),
    )


def run(*, resume_unstarted: bool = False) -> None:
    """One guarded run, six fixed non-neural arms; no neural journal mutations."""
    if (OUT / "execution.jsonl").exists() and not resume_unstarted:
        raise ValueError("SINGLE_USE_EXECUTION_NO_RETRY")
    assert b.read(OUT / "readiness.json")["status"] == "READY"
    protocol = b.read(OUT / "protocol.json")
    recovery = b.read(OUT / "logging_recovery_final.json") if resume_unstarted else {}
    for name, sha in protocol["preservation_bindings"].items():
        if resume_unstarted and name == "src/lstm_data/hf20_classical.py":
            sha = recovery["fixed_runner_sha256"]
        assert b.digest(Path(name)) == sha, name
    _, rows = b.metadata()
    plans = clock.saved_plans(rows)
    r = signed_targets(rows)
    calibration, summary = [], []
    started = time.monotonic()

    def event(status: str, year: int, detail: dict) -> None:
        with (OUT / "execution.jsonl").open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        **detail,
                        "status": status,
                        "year": year,
                        "at": pd.Timestamp.now(tz="UTC").isoformat(),
                    }
                )
                + "\n"
            )

    if resume_unstarted:
        assert b.digest(OUT / "execution.jsonl") == recovery["failed_journal_sha256"]
        saved = b.read(OUT / "logging_failure_preservation.json")
        for name, sha in saved["F21_bindings"].items():
            assert b.digest(Path(name)) == sha, name
        assert not any((OUT / f"F{year % 100}").exists() for year in [2022, 2023, 2024])
        calibration.extend(
            pd.read_csv(OUT / "F21/calibration.csv", float_precision="round_trip").to_dict(
                "records"
            )
        )
        recovered = dict(
            year=2021,
            status="COMPLETED_LOG_RECOVERED",
            HAR_fits=140,
            EWMA_R2_stock_slot_parameters=140,
            EWMA_A_seeds=140,
            global_calibrations=6,
            GARCH_fits=0,
            neural_fits=0,
            telemetry=(
                "Resource check passed before logger failure; exact F21 peak/runtime not persisted"
            ),
        )
        summary.append(recovered)
        event("COMPLETED_LOG_RECOVERED", 2021, recovered)
    for year, roles in plans.items():
        if resume_unstarted and year == 2021:
            continue
        dest = OUT / f"F{year % 100}"
        dest.mkdir()
        event("STARTED", year, dict(neural_starts=0))
        tick = time.monotonic()
        try:
            fit = roles["restricted_refit"]
            queries = np.concatenate([roles["calibration"], roles["oos"]])
            pred, params, audit = dynamic_forecasts(rows, r, fit, queries)
            pred["HAR-RV-A"], har, recipe = har_forecasts(rows, r, fit, queries)
            b.write(
                dest / "fit_parameters.json",
                dict(dynamic=params, HAR=har, HAR_recipe=recipe),
                new=True,
            )
            pd.DataFrame(audit).to_csv(dest / "maturity_audit.csv", index=False)
            nc = len(roles["calibration"])
            cf = pd.read_parquet(
                c3.root(year) / "calibration_scores.parquet", columns=[*c3.META, "A"]
            )
            of = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
            for arm in ARMS:
                coef = multiplier(cf.A.to_numpy(), pred[arm][:nc].ravel(), cf.weight.to_numpy())
                calibration.append(
                    dict(
                        year=year,
                        arm=arm,
                        rows=len(cf),
                        sessions=cf.session_date_et.nunique(),
                        **coef,
                    )
                )
                for f, values in [(cf, pred[arm][:nc]), (of, pred[arm][nc:])]:
                    f[arm + "-UNCAL"] = values.ravel()
                    f[arm + "-CAL"] = coef["k"] * values.ravel()
                    assert np.isfinite(f[arm + "-CAL"]).all()
            # Calibration factors are frozen before any OOS score calculation.
            pd.DataFrame([x for x in calibration if x["year"] == year]).to_csv(
                dest / "calibration.csv", index=False
            )
            cf.to_parquet(dest / "calibration_scores.parquet", compression="zstd", index=False)
            of.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
            result = dict(
                year=year,
                status="COMPLETED",
                HAR_fits=140,
                EWMA_R2_stock_slot_parameters=140,
                EWMA_A_seeds=140,
                global_calibrations=len(ARMS),
                GARCH_fits=0,
                neural_fits=0,
                seconds=time.monotonic() - tick,
                **resources(),
            )
            summary.append(result)
            event("COMPLETED", year, result)
            print("COMPLETED", year, result["seconds"], flush=True)
        except Exception as exc:
            event("FAILED", year, dict(error=repr(exc)))
            raise
    pd.DataFrame(summary).to_csv(OUT / "fit_summary.csv", index=False)
    pd.DataFrame(calibration).to_csv(OUT / "calibration.csv", index=False)
    b.write(
        OUT / "run_receipt.json",
        dict(
            status="COMPLETE_WITH_B3_BLOCKED",
            seconds=time.monotonic() - started,
            runtime_scope="unstarted F22-F24 only" if resume_unstarted else "all four folds",
            logging_recovery_no_refit=resume_unstarted,
            ledger_unchanged=186,
            **resources(),
        ),
        new=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--run", action="store_true")
    actions.add_argument("--resume-unstarted", action="store_true")
    actions.add_argument("--report", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.run:
        run()
    elif args.resume_unstarted:
        run(resume_unstarted=True)
    else:
        from .hf20_classical_report import report

        report()
