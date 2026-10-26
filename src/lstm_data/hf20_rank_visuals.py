"""Offline, saved-score S1/S2 ranking views; no model fitting or source-price reads."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

from .hf1m_action_audit import SYMBOLS, digest
from .hf20_ranking import daily_ic, ranks

PRIOR = Path("reports/experiments/hf20_s1_s2_continuation_2026-10-25_204117")
ARMS = ("N0", "N1", "N2", "P", "LR", "LP", "T2R", "NR", "PW")


def display_ranks(values: np.ndarray) -> np.ndarray:
    """Preserve average ties; larger score is better, display rank 1 is best."""
    return values.shape[1] + 1 - ranks(values)


def transitions(frame: pd.DataFrame, year: int, arm: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """No transition across folds; ties at the four-name boundary remain ambiguous."""
    score = frame.score.to_numpy().reshape(-1, 20)
    dr = display_ranks(score)
    ids = frame.origin_id.to_numpy()[::20]
    days = frame.session_date_et.to_numpy()[::20]
    times = pd.DatetimeIndex(pd.to_datetime(ids, utc=True))
    changes, sets = [], []
    for k in range(1, len(ids)):
        same = days[k] == days[k - 1]
        relation = (
            "WITHIN_SESSION_ADJACENT"
            if same and times[k] - times[k - 1] == pd.Timedelta(hours=1)
            else "WITHIN_SESSION_MISSING_SLOT"
            if same
            else "ACROSS_SESSION"
        )
        for j, ticker in enumerate(SYMBOLS):
            changes.append(
                dict(
                    year=year,
                    model=arm,
                    origin_id=ids[k],
                    previous_origin=ids[k - 1],
                    ticker=ticker,
                    relation=relation,
                    signed_change=dr[k, j] - dr[k - 1, j],
                    absolute_change=abs(dr[k, j] - dr[k - 1, j]),
                )
            )
        for side, mask in (("TOP4", dr <= 4), ("BOTTOM4", dr >= 17)):
            a, b = set(np.flatnonzero(mask[k - 1])), set(np.flatnonzero(mask[k]))
            valid = len(a) == len(b) == 4
            sets.append(
                dict(
                    year=year,
                    model=arm,
                    origin_id=ids[k],
                    previous_origin=ids[k - 1],
                    relation=relation,
                    side=side,
                    unambiguous_four_names=valid,
                    jaccard=len(a & b) / len(a | b) if valid else np.nan,
                    entering=len(b - a) if valid else np.nan,
                    leaving=len(a - b) if valid else np.nan,
                )
            )
    return pd.DataFrame(changes), pd.DataFrame(sets)


def source_dir(year: int, arm: str) -> Path:
    return PRIOR / (
        f"HF20-S1S2-F{year % 100}-{arm}-S42"
        if arm in ("NR", "T2R", "PW")
        else f"F{year % 100}_S1_{arm}"
    )


def records(frame: pd.DataFrame) -> list[dict]:
    """JSON-safe records retain missing values as null, never fabricated zeros."""
    return json.loads(frame.to_json(orient="records", double_precision=15))


def historical(out: Path) -> None:
    from .hf20_rank_visual_html import page

    plots = out / "plots"
    plots.mkdir(exist_ok=True)
    roster, refs, checks, changes, set_changes, sessions, monthly, intervals = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    payload: dict = dict(
        symbols=SYMBOLS,
        years={},
        data={},
        inventory=[],
        metrics=[],
        cohorts=[],
        epochs=[],
        witnesses=[],
    )
    scored = []
    for year in range(2021, 2025):
        m1_path = source_dir(year, "N1") / "oos_scores.parquet"
        m1 = pd.read_parquet(m1_path)
        base_keys = m1[
            [
                "origin_id",
                "ticker",
                "session_date_et",
                "return_4h",
                "TG20",
                "epsilon",
                "scale",
                "entry_end_utc",
                "exit_end_utc",
                "label_maturity_utc",
            ]
        ]
        dates = m1.session_date_et.drop_duplicates().tolist()
        payload["years"][str(year)] = dict(
            first=dates[0],
            last=dates[-1],
            default_end=dates[min(9, len(dates) - 1)],
            selection="first ten saved OOS sessions, outcome-independent",
        )
        for arm in ARMS:
            dest = source_dir(year, arm)
            path = dest / "oos_scores.parquet"
            neural = arm in ("T2R", "NR", "PW")
            status = (
                "FAILED"
                if neural and (dest / "FAILURE.json").exists()
                else "DEFERRED"
                if arm == "LP"
                else "PASS"
                if path.exists()
                else "UNAVAILABLE"
            )
            row = dict(
                year=year,
                model=arm,
                run_id=dest.name,
                status=status,
                phase="refit",
                evaluation_role="oos",
                horizon="4h same-session",
                saved_scores=str(path) if path.exists() else None,
                reason="F21 PW failed start65; no accepted OOS"
                if status == "FAILED"
                else "LP original failed attempt8; no accepted OOS and no retry"
                if arm == "LP"
                else "",
            )
            roster.append(row)
            if status != "PASS":
                continue
            f = pd.read_parquet(path)
            if (
                f.session_date_et.ge("2025-01-01").any()
                or f.year.ne(year).any()
                or f.role.ne("oos").any()
            ):
                raise ValueError("HISTORICAL_OOS_SCOPE_BEFORE_PLOTTING")
            if (
                f.duplicated(["origin_id", "ticker"]).any()
                or not f.groupby("origin_id").size().eq(20).all()
            ):
                raise ValueError("HISTORICAL_PANEL_KEYS")
            np.testing.assert_array_equal(
                f.ticker.to_numpy().reshape(-1, 20), np.tile(SYMBOLS, (len(f) // 20, 1))
            )
            pd.testing.assert_frame_equal(f[base_keys.columns], base_keys, check_exact=True)
            r, s = f.return_4h.to_numpy().reshape(-1, 20), f.score.to_numpy().reshape(-1, 20)
            actual, prediction = display_ranks(r), display_ranks(s)
            np.testing.assert_array_equal(actual.ravel(), 21 - f.actual_rank.to_numpy())
            np.testing.assert_array_equal(prediction.ravel(), 21 - f.prediction_rank.to_numpy())
            days = f.session_date_et.to_numpy()[::20]
            metric = json.loads((dest / "oos_metrics.json").read_text())
            ic = daily_ic(r, s, days) if arm != "N0" else np.nan
            if arm != "N0":
                np.testing.assert_allclose(ic, metric["daily_ic"], rtol=1e-12, atol=1e-12)
            elif metric["daily_ic"] is not None:
                raise ValueError("CONSTANT_IC_NOT_UNDEFINED")
            checks.append(
                dict(
                    year=year,
                    model=arm,
                    rows=len(f),
                    origins=len(f) // 20,
                    sessions=len(set(days)),
                    same_keys_and_targets=True,
                    rank_display_inversion=True,
                    ic_reconciled=True,
                    score_sha256=digest(path),
                )
            )
            origin = pd.read_csv(dest / "oos_origins.csv")
            np.testing.assert_array_equal(origin.origin_id, f.origin_id.to_numpy()[::20])
            origin["year"], origin["model"] = year, arm
            day = origin.groupby("session_date_et", as_index=False).agg(
                ic=("ic", "mean"),
                origins=("origin_id", "size"),
                concordance=("concordance", "mean"),
                top4=("top4", "mean"),
                bottom4=("bottom4", "mean"),
            )
            day["year"], day["model"] = year, arm
            sessions.append(day)
            day["month"] = day.session_date_et.str[:7]
            mo = day.groupby("month", as_index=False).agg(
                ic=("ic", "mean"), sessions=("session_date_et", "size"), origins=("origins", "sum")
            )
            mo["year"], mo["model"] = year, arm
            monthly.append(mo)
            if arm != "N0":
                bins = day.groupby("month").ic.agg(["sum", "count"])
                draw = np.random.default_rng(22042).integers(len(bins), size=(400, len(bins)))
                sample = bins["sum"].to_numpy()[draw].sum(1) / bins["count"].to_numpy()[draw].sum(1)
                lo, hi = np.quantile(sample, [0.025, 0.975])
                intervals.append(
                    dict(
                        year=year,
                        model=arm,
                        ic=ic,
                        low=lo,
                        high=hi,
                        replicates=400,
                        unit="whole calendar month; descriptive only",
                    )
                )
            movement, sets = transitions(f, year, arm)
            changes.append(movement)
            set_changes.append(sets)
            times = pd.DatetimeIndex(
                pd.to_datetime(f.entry_end_utc.to_numpy()[::20], utc=True)
            ).tz_convert("America/New_York")
            wall = times.tz_localize(None).astype(str).tolist()

            def matrix(name: str) -> list:
                return f[name].to_numpy().reshape(-1, 20).tolist()

            payload["data"][f"{year}|{arm}"] = dict(
                run=dest.name,
                origins=f.origin_id.to_numpy()[::20].tolist(),
                days=days.tolist(),
                wall=wall,
                exits=f.exit_end_utc.iloc[::20].astype(str).tolist(),
                maturity=f.label_maturity_utc.iloc[::20].astype(str).tolist(),
                score=s.tolist(),
                pred=prediction.tolist(),
                truth=actual.tolist(),
                m1=m1.score.to_numpy().reshape(-1, 20).tolist(),
                m1rank=display_ranks(m1.score.to_numpy().reshape(-1, 20)).tolist(),
                quality=matrix("quality"),
                fallback=matrix("feature_fallback_cells"),
                y=matrix("TG20"),
                q=matrix("q"),
                z=matrix("Z"),
                inverse=matrix("inverse_TG20") if arm == "T2R" else None,
                origins_metrics=records(origin),
                movement=records(movement),
                set_changes=records(sets),
                checkpoint=str(f.checkpoint_sha256.iloc[0]) if neural else None,
                recipe_sha256=str(f.phase_recipe_sha256.iloc[0]),
                score_units=metric["score_units"],
            )
            small = f[
                [
                    "origin_id",
                    "ticker",
                    "session_date_et",
                    "year",
                    "model",
                    "score",
                    "actual_rank",
                    "prediction_rank",
                    "return_4h",
                    "TG20",
                    "quality",
                    "feature_fallback_cells",
                ]
            ].copy()
            small["display_realized_rank"], small["display_prediction_rank"] = (
                actual.ravel(),
                prediction.ravel(),
            )
            small["M1"], small["M1_display_rank"] = (
                m1.score.to_numpy(),
                display_ranks(m1.score.to_numpy().reshape(-1, 20)).ravel(),
            )
            scored.append(small)
            for qpath in sorted(dest.glob("*")):
                if qpath.is_file():
                    refs.append(
                        dict(
                            path=str(qpath),
                            sha256=digest(qpath),
                            bytes=qpath.stat().st_size,
                            kind="archived model artifact; unchanged",
                        )
                    )
    payload["inventory"] = roster
    source_names = {
        "metrics": "all_role_metrics.csv",
        "cohorts": "cohort_objective_and_error_decomposition_v2.csv",
        "epochs": "complete_epoch_trace.csv",
        "witnesses": "source_case_checkpoint_replay.csv",
    }
    for key, name in source_names.items():
        payload[key] = records(pd.read_csv(PRIOR / name))
        refs.append(
            dict(
                path=str(PRIOR / name),
                sha256=digest(PRIOR / name),
                bytes=(PRIOR / name).stat().st_size,
                kind="canonical archived diagnostic table",
            )
        )
    payload["daily"] = records(pd.concat(sessions, ignore_index=True))
    payload["monthly"] = records(pd.concat(monthly, ignore_index=True))
    payload["intervals"] = records(pd.DataFrame(intervals))
    all_scores = pd.concat(scored, ignore_index=True)
    all_scores["slot"] = (
        pd.to_datetime(all_scores.origin_id, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.strftime("%H:%M")
    )
    all_scores["display_rank_error"] = (
        all_scores.display_prediction_rank - all_scores.display_realized_rank
    )
    group_errors = []
    for key in ("ticker", "slot", "quality"):
        table = (
            all_scores.groupby(["year", "model", key], as_index=False)
            .agg(
                signed_rank_error=("display_rank_error", "mean"),
                mean_absolute_rank_error=("display_rank_error", lambda a: abs(a).mean()),
                rows=("origin_id", "size"),
            )
            .rename(columns={key: "group"})
        )
        table["dimension"] = key
        group_errors.append(table)
    errors = pd.concat(group_errors, ignore_index=True)
    errors.to_csv(out / "historical_group_rank_errors.csv", index=False)
    payload["group_errors"] = records(errors)
    pd.DataFrame(roster).to_csv(out / "HISTORICAL_MODEL_RUN_INVENTORY.csv", index=False)
    pd.DataFrame(checks).to_csv(out / "HISTORICAL_SCORE_RECONCILIATION.csv", index=False)
    pd.DataFrame(refs).drop_duplicates("path").to_csv(
        out / "HISTORICAL_SOURCE_REFERENCES.csv", index=False
    )
    pd.concat(scored, ignore_index=True).to_parquet(
        out / "historical_plot_scores.parquet", index=False
    )
    pd.concat(changes, ignore_index=True).to_csv(out / "historical_rank_movements.csv", index=False)
    pd.concat(set_changes, ignore_index=True).to_csv(
        out / "historical_selection_set_changes.csv", index=False
    )
    pd.concat(sessions, ignore_index=True).to_csv(out / "historical_daily_IC.csv", index=False)
    pd.concat(monthly, ignore_index=True).to_csv(out / "historical_monthly_IC.csv", index=False)
    pd.DataFrame(intervals).to_csv(out / "historical_month_block_intervals.csv", index=False)
    (out / "HISTORICAL_WINDOW_SELECTION.json").write_text(
        json.dumps(payload["years"], indent=2) + "\n"
    )
    (plots / "historical_s1_s2_rankings.html").write_text(page(payload, get_plotlyjs()))
    for year in range(2021, 2025):
        v = payload["data"][f"{year}|NR"]
        chosen = [
            i for i, d in enumerate(v["days"]) if d <= payload["years"][str(year)]["default_end"]
        ]
        j = SYMBOLS.index("AAPL")
        fig = go.Figure()
        for label, values, dash in (
            ("Realized later-known 4h rank", v["truth"], "solid"),
            ("NR predicted rank", v["pred"], "dash"),
            ("M1 momentum rank", v["m1rank"], "dot"),
            ("T2R predicted rank", payload["data"][f"{year}|T2R"]["pred"], "dashdot"),
        ):
            x, y = [], []
            for k in chosen:
                if x and (v["days"][k] != v["days"][k - 1]):
                    x.append(None)
                    y.append(None)
                x.append(v["wall"][k])
                y.append(values[k][j])
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name=label,
                    line=dict(dash=dash),
                    connectgaps=False,
                )
            )
        fig.add_hrect(y0=1, y1=4, fillcolor="green", opacity=0.08, line_width=0)
        fig.add_hrect(y0=17, y1=20, fillcolor="red", opacity=0.08, line_width=0)
        fig.update_layout(
            title=f"S1/S2 {year}: AAPL, first ten saved OOS sessions (not outcome-selected)",
            height=850,
            width=1500,
            xaxis_title="Forecast origin ET; separated sessions, no interpolation across closures",
            yaxis=dict(title="Display midrank: 1 best, 20 worst", range=[20.5, 0.5]),
            legend=dict(orientation="h", y=-0.15),
        )
        fig.write_html(
            plots / f"historical_{year}_static.html", include_plotlyjs=True, full_html=True
        )
    print(
        json.dumps(
            dict(
                status="HISTORICAL_NUMERIC_PASS_GRAPHIC_QA_PENDING",
                models=len(checks),
                rows=sum(r["rows"] for r in checks),
                new_fits=0,
            )
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    historical(args.out)


if __name__ == "__main__":
    main()
