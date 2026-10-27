"""One offline, task-specific saved-output dashboard; no server, fits or raw-source I/O."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from plotly.offline import get_plotlyjs

from .hf20_s4_data import ROLES
from .hf20_s5s9 import RUNS, S4


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records", date_format="iso", double_precision=9))


def calibration(f: pd.DataFrame, arm: str) -> dict:
    """Full-role descriptive bins; no curve or bin boundary is fitted into a model."""
    if arm == "EVENT":
        score = f.p_ANY.to_numpy()
        actual = f.event_class.ne(1).to_numpy(float)
        group = np.minimum((score * 10).astype(int), 9)
    elif arm == "MAG":
        score = f.prediction_A.to_numpy()
        actual = f.return_4h.abs().to_numpy()
        group = (
            pd.Series(score).rank(method="average", pct=True).mul(10).clip(upper=9).to_numpy(int)
        )
    else:
        return {}
    w = f.weight.to_numpy()
    bins = []
    for k in range(10):
        mask = group == k
        if mask.any():
            bins.append(
                dict(
                    predicted=float(np.average(score[mask], weights=w[mask])),
                    observed=float(np.average(actual[mask], weights=w[mask])),
                    mass=float(w[mask].sum()),
                )
            )
    result: dict[str, object] = dict(bins=bins)
    if arm == "EVENT":
        order = np.argsort(-score, kind="stable")
        s = score[order]
        a = actual[order]
        ww = w[order]
        ends = np.r_[np.flatnonzero(s[:-1] != s[1:]), len(s) - 1]
        tp = np.cumsum(a * ww)[ends]
        mass = np.cumsum(ww)[ends]
        ix = np.unique(np.linspace(0, len(ends) - 1, min(512, len(ends))).astype(int))
        result["pr"] = dict(
            precision=(tp[ix] / mass[ix]).tolist(),
            recall=(tp[ix] / tp[-1]).tolist() if tp[-1] else [],
        )
    return result


def dashboard(out: Path, *, rehearsal: bool = False) -> Path:
    payload = {}
    roster = []
    folders = sorted((out / "rehearsal").glob("*")) if rehearsal else [out / r for r in RUNS]
    for dest in folders:
        passed = (dest / "PASS.json").exists()
        roster.append(
            dict(
                run=dest.name,
                status="UNTRAINED_REHEARSAL"
                if rehearsal
                else "PASS"
                if passed
                else "FAILED"
                if (dest / "FAILURE.json").exists()
                else "NOT_RUN",
            )
        )
        if not rehearsal and not passed:
            continue
        for role in ROLES:
            path = dest / f"{role}_scores.parquet"
            if not path.exists():
                continue
            f = pd.read_parquet(path)
            arm = str(f.arm.iloc[0])
            year = int(f.year.iloc[0])
            if arm == "META-T2R":
                for ref, folder in [
                    ("S4", f"HF20-S4A-F{year % 100}-H4-T2R-S42"),
                    ("M1", f"F{year % 100}_S4_N1"),
                ]:
                    old = pd.read_parquet(
                        S4 / folder / f"{role}_scores.parquet",
                        columns=["origin_id", "ticker", "prediction_rank"],
                    )
                    old["prediction_rank"] = 21 - old.prediction_rank
                    f = f.merge(
                        old.rename(columns={"prediction_rank": ref + "_rank"}),
                        on=["origin_id", "ticker"],
                        validate="one_to_one",
                        how="left",
                    )
            else:
                for ref in ("STOCK", "VOL"):
                    control = pd.read_parquet(dest / f"{role}_{ref}_control_scores.parquet")
                    names = [
                        n
                        for n in control
                        if isinstance(n, str) and n.startswith(("prediction_", "p_", "quantiles_"))
                    ]
                    f = f.merge(
                        control[["origin_id", "ticker", *names]].rename(
                            columns={n: ref + "_" + n for n in names}
                        ),
                        on=["origin_id", "ticker"],
                        validate="one_to_one",
                        how="left",
                    )
            days = f.groupby("session_date_et").actual_loss.mean()
            sampled = (
                f
                if role == "oos"
                else f[f.session_date_et.isin(sorted(f.session_date_et.unique())[:10])]
            )
            cols = [
                c
                for c in [
                    "origin_id",
                    "session_date_et",
                    "ticker",
                    "slot",
                    "category",
                    "exit_end_utc",
                    "return_4h",
                    "TG20",
                    "actual_loss",
                    "prediction_m",
                    "prediction_A",
                    "p_ANY",
                    "event_class",
                    "quantiles_y_05",
                    "quantiles_y_50",
                    "quantiles_y_95",
                    "actual_rank",
                    "prediction_rank",
                    "S4_rank",
                    "M1_rank",
                    "quality",
                    "fallback",
                    "max_terminal_price_age_minutes",
                ]
                if c in f
            ]
            cols.extend(c for c in f if isinstance(c, str) and c.startswith(("STOCK_", "VOL_")))
            metric = json.loads((dest / f"{role}_metrics.json").read_text())
            selection = json.loads((dest / "calibration_binding.json").read_text())
            coverage = (
                f.assign(
                    fallback_fraction=f.feature_fallback_cells.gt(0).astype(float),
                    missing_fraction=f.assumed_zero_minute_count.gt(0).astype(float),
                )
                .groupby(["ticker", "slot"], as_index=False)
                .agg(
                    fallback_fraction=("fallback_fraction", "mean"),
                    missing_fraction=("missing_fraction", "mean"),
                    age_mean=("max_terminal_price_age_minutes", "mean"),
                )
            )
            movement = []
            stability = []
            if arm == "META-T2R":
                from .hf20_rank_visuals import transitions

                changes, sets = transitions(f, year, arm)
                movement = records(
                    pd.concat(
                        [
                            changes.groupby(["relation", field], as_index=False)
                            .size()
                            .rename(columns={field: "value"})
                            .assign(kind=field)
                            for field in ("absolute_change", "signed_change")
                        ],
                        ignore_index=True,
                    )
                )
                stability = records(
                    sets.groupby(["relation", "side"], as_index=False)[
                        ["jaccard", "entering", "leaving"]
                    ].mean()
                )
            slot_metrics = pd.read_csv(dest / f"{role}_strata.csv")
            training = []
            for trace in sorted(dest.glob("calibration_[0-9][0-9][0-9].json")):
                t = json.loads(trace.read_text())
                batches = pd.read_csv(trace.with_name(trace.stem + "_batches.csv"))
                training.append(
                    dict(
                        epoch=t["epoch"],
                        online=t["online_objective"],
                        train_off=t.get("inner_train_off", {}).get("actual_objective"),
                        validation_off=t.get("inner_validation_off", {}).get("actual_objective"),
                        preclip=float(batches.preclip.max()),
                        postclip=float(batches.postclip.max()),
                    )
                )
            payload[dest.name + "|" + role] = dict(
                arm=arm,
                year=year,
                role=role,
                rows=records(sampled[cols]),
                metrics=metric,
                selection=dict(
                    selected=selection["selected"],
                    raw_best=selection.get("selector", {}).get("raw_epoch"),
                ),
                coverage=records(coverage),
                movement=movement,
                stability=stability,
                symbols=list(dict.fromkeys(f.ticker)),
                slot_metrics=records(slot_metrics[slot_metrics.field.eq("slot")]),
                training=training,
                full_rows=len(f),
                full_origins=f.origin_id.nunique(),
                full_sessions=f.session_date_et.nunique(),
                calibration=calibration(f, arm),
                daily=dict(day=days.index.tolist(), loss=days.tolist()),
                cohorts=records(pd.read_csv(dest / f"{role}_cohorts.csv"))
                if (dest / f"{role}_cohorts.csv").exists()
                else [],
            )
    encoded = json.dumps(
        dict(views=payload, roster=roster, rehearsal=rehearsal), allow_nan=True
    ).replace("</", "<\\/")
    page = Path(__file__).with_name("hf20_s5s9_template.html").read_text()
    page = page.replace("@@PLOTLY_JS@@", get_plotlyjs()).replace("@@PAYLOAD@@", encoded)
    path = out / (
        "REHEARSAL_VISUAL_DIAGNOSTICS.html" if rehearsal else "S5_S9_VISUAL_DIAGNOSTICS.html"
    )
    path.write_text(page)
    return path


def render(out: Path, *, rehearsal: bool = False) -> None:
    path = dashboard(out, rehearsal=rehearsal)
    browser = (
        shutil.which("chromium")
        or shutil.which("google-chrome")
        or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
    if not Path(browser).is_file():
        raise ValueError("EXISTING_BROWSER_REQUIRED_NO_INSTALL")
    views = (
        sorted((out / "rehearsal").glob("*"))
        if rehearsal
        else [out / r for r in RUNS if (out / r / "PASS.json").exists()]
    )
    plots = out / ("plots_final" if rehearsal else "plots")
    plots.mkdir(exist_ok=True)
    receipts = []
    with tempfile.TemporaryDirectory(prefix="s5s9_local_browser_") as profile:
        flags = [
            browser,
            "--headless",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-extensions",
            "--no-first-run",
            "--hide-scrollbars",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--window-size=1600,1100",
            "--user-data-dir=" + profile,
        ]
        for dest in views:
            png = plots / (dest.name + ".png")
            result = subprocess.run(
                flags
                + [
                    "--virtual-time-budget=4000",
                    "--screenshot=" + str(png.resolve()),
                    path.resolve().as_uri() + "?view=" + dest.name,
                ],
                capture_output=True,
                timeout=90,
            )
            if result.returncode or not png.exists() or png.stat().st_size < 10000:
                raise ValueError("S5S9_EMPTY_IMAGE")
            receipts.append(dict(run=dest.name, png=str(png), bytes=png.stat().st_size))
        result = subprocess.run(
            flags
            + ["--virtual-time-budget=30000", "--dump-dom", path.resolve().as_uri() + "?qa=1"],
            capture_output=True,
            timeout=180,
        )
        match = re.search(r'<pre id="qa-result">(.*?)</pre>', result.stdout.decode(), re.S)
        if result.returncode or match is None:
            raise ValueError("S5S9_BROWSER_QA_INCOMPLETE")
        qa = json.loads(html.unescape(match.group(1)))
        if qa["status"] != "PASS":
            raise ValueError("S5S9_BROWSER_QA_FAIL", qa)
    name = "REHEARSAL_BROWSER_QA.json" if rehearsal else "BROWSER_QA.json"
    (out / name).write_text(
        json.dumps(
            dict(status="PASS", rehearsal=rehearsal, views=receipts, interactive=qa), indent=2
        )
        + "\n"
    )
    if not rehearsal:
        numerical = json.loads((out / "S5_S9_NUMERICAL_VERIFICATION.json").read_text())
        numerical.update(
            status="PASS_COMPLETE"
            if numerical["neural_completed"] == 16
            else "PARTIAL_WITH_VERIFIED_AVAILABLE_VIEWS",
            browser_status="PASS",
            browser_views=len(views),
            browser_role_cases=len(qa["cases"]),
        )
        (out / "S5_S9_VERIFICATION.json").write_text(json.dumps(numerical, indent=2) + "\n")
    print("S5S9_BROWSER_PASS", len(views), len(qa["cases"]), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--rehearsal", action="store_true")
    p.add_argument("--render", action="store_true")
    a = p.parse_args()
    render(a.out, rehearsal=a.rehearsal) if a.render else dashboard(a.out, rehearsal=a.rehearsal)
