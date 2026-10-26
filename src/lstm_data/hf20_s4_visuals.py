"""One offline S4 dashboard with separate, traceable views for every saved run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
from plotly.offline import get_plotlyjs

from .hf1m_action_audit import SYMBOLS, digest
from .hf20_rank_visuals import display_ranks, records, transitions
from .hf20_s4_authority import RUNS


class Payload(TypedDict):
    symbols: list[str]
    years: dict[str, dict]
    data: dict[str, dict]
    inventory: list[dict]
    metrics: list[dict]
    cohorts: list[dict]
    epochs: list[dict]
    witnesses: list[dict]
    daily: list[dict]
    monthly: list[dict]
    intervals: list[dict]
    group_errors: list[dict]


def build(out: Path, current: Path, *, rehearsal: bool = False) -> None:
    payload = Payload(
        symbols=list(SYMBOLS),
        years={},
        data={},
        inventory=[],
        metrics=[],
        cohorts=[],
        epochs=[],
        witnesses=[],
        daily=[],
        monthly=[],
        intervals=[],
        group_errors=[],
    )
    for year in range(2021, 2025):
        payload["years"][str(year)] = dict(
            first=f"{year}-01-01", last=f"{year}-12-31", default_end=f"{year}-01-31"
        )
    for run in RUNS:
        path = out / run
        payload["inventory"].append(
            dict(
                year=2000 + int(run.split("-")[2][1:]),
                model=run.split("-")[4],
                run_id=run,
                status="SAVED_REHEARSAL"
                if rehearsal and path.exists()
                else "SAVED_PENDING_FINAL_GATE"
                if (path / "oos_scores.parquet").exists()
                else "FAILED"
                if (path / "FAILURE.json").exists()
                else "NOT_RUN",
            )
        )
    for path in sorted(out.glob("*/oos_scores.parquet")):
        f = pd.read_parquet(path)
        supplemental = out / "S4_SOURCE_COMPONENTS_FOR_VISUALS.parquet"
        if "decomposition_supported" not in f and supplemental.exists():
            from .hf20_s4_diagnostics import join_components

            f = join_components(f, pd.read_parquet(supplemental))
        year = int(f.year.iloc[0])
        arm = str(f.model.iloc[0])
        dest = path.parent
        m1path = out / f"F{year % 100}_S4_N1/oos_scores.parquet"
        if not m1path.exists():
            raise ValueError("S4_MATCHED_M1_REQUIRED_FOR_VISUAL_GATE")
        m1 = pd.read_parquet(m1path)
        np.testing.assert_array_equal(f[["origin_id", "ticker"]], m1[["origin_id", "ticker"]])
        rows = f.iloc[::20]
        days = rows.session_date_et.tolist()
        dates = list(dict.fromkeys(days))
        payload["years"][str(year)] = dict(
            first=dates[0], last=dates[-1], default_end=dates[min(9, len(dates) - 1)]
        )
        origin = pd.read_csv(dest / "oos_origins.csv")
        movement, sets = transitions(f, year, arm)

        def matrix(name: str) -> list:
            return f[name].to_numpy().reshape(-1, 20).tolist()

        score = np.asarray(matrix("score"))
        r = np.asarray(matrix("return_4h"))
        metric = json.loads((dest / "oos_metrics.json").read_text())
        payload["data"][f"{year}|{arm}"] = dict(
            run=dest.name,
            origins=rows.origin_id.tolist(),
            days=days,
            wall=pd.to_datetime(rows.entry_end_utc, utc=True)
            .dt.tz_convert("America/New_York")
            .dt.tz_localize(None)
            .astype(str)
            .tolist(),
            exits=rows.exit_end_utc.astype(str).tolist(),
            maturity=rows.label_maturity_utc.astype(str).tolist(),
            category=rows.category.tolist(),
            score=score.tolist(),
            pred=display_ranks(score).tolist(),
            truth=display_ranks(r).tolist(),
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
            checkpoint=str(f.checkpoint_sha256.iloc[0]) if "checkpoint_sha256" in f else None,
            recipe_sha256=str(f.phase_recipe_sha256.iloc[0]),
            score_units=metric["score_units"],
        )
        payload["data"][f"{year}|{arm}"]["components"] = {
            key: json.loads(f[[key]].to_json(orient="values"))
            for key in (
                "origin_to_close",
                "close_to_next_open",
                "next_open_to_exit",
                "decomposition_supported",
            )
            if key in f
        }
        daily = origin.groupby("session_date_et", as_index=False).agg(
            ic=("ic", "mean"), origins=("origin_id", "size")
        )
        daily["year"] = year
        daily["model"] = arm
        payload["daily"] += records(daily)
        daily["month"] = daily.session_date_et.str[:7]
        monthly = daily.groupby("month", as_index=False).agg(
            ic=("ic", "mean"), sessions=("session_date_et", "size"), origins=("origins", "sum")
        )
        monthly["year"] = year
        monthly["model"] = arm
        payload["monthly"] += records(monthly)
        if arm != "N0":
            bins = daily.groupby("month").ic.agg(["sum", "count"])
            draws = np.random.default_rng(22042).integers(len(bins), size=(400, len(bins)))
            sampled = bins["sum"].to_numpy()[draws].sum(1) / bins["count"].to_numpy()[draws].sum(1)
            lo, hi = np.quantile(sampled, [0.025, 0.975])
            payload["intervals"].append(dict(year=year, model=arm, low=lo, high=hi))
        for p in dest.glob("*_metrics.json"):
            if p.stem.removesuffix("_metrics") in (
                "inner_train",
                "inner_validation",
                "refit",
                "oos",
            ):
                payload["metrics"].append(json.loads(p.read_text()))
        for p in dest.glob("*_energy_and_objective_cohorts.csv"):
            payload["cohorts"] += records(pd.read_csv(p))
        for p in sorted(dest.glob("*.json")):
            if p.stem.startswith(("calibration_", "refit_")) and p.stem.split("_")[-1].isdigit():
                row = json.loads(p.read_text())
                row["run_id"] = dest.name
                batch_path = p.with_name(p.stem + "_batches.csv")
                if batch_path.exists():
                    batch = pd.read_csv(batch_path)
                    row["gradient"] = dict(
                        preclip_max=float(batch.preclip.max()),
                        postclip_max=float(batch.postclip.max()),
                        clipped_fraction=float(batch.preclip.gt(1).mean()),
                        update_mean=float(batch.update_norm.mean()),
                    )
                payload["epochs"].append(row)
        err = f.assign(rank_error=display_ranks(score).ravel() - display_ranks(r).ravel())
        for key in ("ticker", "slot", "quality"):
            g = (
                err.groupby(key, as_index=False)
                .agg(
                    mean_absolute_rank_error=("rank_error", lambda x: abs(x).mean()),
                    rows=("origin_id", "size"),
                )
                .rename(columns={key: "group"})
            )
            g["dimension"] = key
            g["year"] = year
            g["model"] = arm
            payload["group_errors"] += records(g)
    template = Path(__file__).with_name("hf20_rank_visual_template.html").read_text()
    start = template.index("<h1>")
    end = template.index('<div class="controls">')
    template = (
        template[:start]
        + (
            "<h1>S4-A: seven-origin, four-trading-hour ranking diagnostics</h1>"
            "<p>UNTRAINED ZERO-STEP REHEARSAL — no empirical result.</p>"
            if rehearsal
            else "<h1>S4-A: seven-origin, four-trading-hour ranking diagnostics</h1>"
        )
        + "<p>Genuine reference-time price-only targets; origin+2 issuance is assumed, "
        "not verified delivery or executable P&amp;L. Opening inputs use48 previous full hours. "
        "Every missing run is explicitly NOT_RUN. Trajectory/date/category filters affect "
        "origin panels; panels labeled full-year and full-role retain their stated populations.</p>"
        + template[end:]
    )
    template = template.replace(
        "['NR','T2R','PW','N1','N2','P','LR','N0','LP']", "['NR','T2R','N1','N2','P','N0']"
    ).replace("['T2R','NR','PW','P','LR','N2','N0']", "['T2R','NR','P','N2','N0']")
    template = template.replace(
        "['N1','NR','T2R','PW','P','LR','N2','N0']", "['N1','NR','T2R','P','N2','N0']"
    )
    template = template.replace(
        "Archived annual IC; PW four-year mean unavailable",
        "S4 annual IC; equal-year mean requires all four folds",
    )
    category = (
        '<label>Origin category<select id="category">'
        "<option>ALL</option><option>INTRADAY</option><option>OVERNIGHT</option>"
        "<option>OPENING</option><option>OLD_MORNING</option><option>AFTERNOON</option>"
        "</select></label>"
    )
    template = template.replace("<label>First session", category + "<label>First session")
    selector = (
        "function categoryMatch(v,i){let k=$('category').value;"
        "let slot=v.wall[i].slice(11,16);return k==='ALL'||k===v.category[i]||"
        "(k==='OPENING'&&slot==='09:30')||"
        "(k==='OLD_MORNING'&&['10:30','11:30'].includes(slot))||"
        "(k==='AFTERNOON'&&['12:30','13:30','14:30','15:30'].includes(slot));}\n"
    )
    template = template.replace("function resetDates()", selector + "function resetDates()")
    template = template.replace(
        "&&d<=$('to').value?i:-1", "&&d<=$('to').value&&categoryMatch(v,i)?i:-1"
    )
    template = template.replace(
        "$('update').onclick=update;", "$('category').onchange=update;$('update').onclick=update;"
    )
    current_year = str(2000 + int(current.name.split("-")[2][1:]))
    current_arm = current.name.split("-")[4]
    template = template.replace(
        "\nresetDates();\n",
        f"\n$('year').value='{current_year}';$('model').value='{current_arm}';"
        "const view=new URLSearchParams(location.search).get('view');"
        "if(view&&D.data[view]){let[y,a]=view.split('|');$('year').value=y;$('model').value=a;}"
        "resetDates();\n",
        1,
    )
    template = (
        template.replace("Historical S1/S2", "S4-A")
        .replace("4h same-session historical OOS", "240 trading-minute S4 OOS")
        .replace("Sparse two-origin observations", "Hourly observations")
        .replace("The role selector below", "The role selector above")
    )
    template = template.replace(
        "'FAILED / UNAVAILABLE: F21 PW has no accepted outer-OOS score export.'",
        "'NOT_RUN — no accepted S4 output for this model/fold.'",
    )
    template = template.replace(
        "'<br>Maturity '+v.maturity[i]",
        "'<br>Category '+v.category[i]+'<br>Maturity '+v.maturity[i]",
    )
    template = template.replace(
        "../HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md",
        "../S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md",
    ).replace("../HISTORICAL_MODEL_RUN_INVENTORY.csv", "../S4_EIGHT_START_DIAGNOSTIC_INDEX.csv")
    qa_start = template.index("if(new URLSearchParams(location.search).has('qa'))")
    template = (
        template[:qa_start]
        + Path(__file__).with_name("hf20_s4_visual_qa.js").read_text()
        + "\n</script></body></html>"
    )
    template = template.replace("range:[0,3]", "range:[0,8]")
    template = template.replace(
        '<div id="roleMetrics"',
        '<div class="grid"><div id="components" class="plot"></div>'
        '<div id="componentCoverage" class="plot"></div>'
        '<div id="slotHeat" class="plot"></div><div id="categoryHeat" class="plot"></div>'
        '<div id="gradient" class="plot"></div><div id="offLoss" class="plot"></div>'
        '<div id="healthMatrix" class="plot"></div><div id="roleMatrix" class="plot"></div></div>'
        '<div id="roleMetrics"',
    )
    supplement = Path(__file__).with_name("hf20_s4_visual_supplement.js").read_text()
    template = template.replace(
        " window.__rankViewStatus=", supplement + "\n window.__rankViewStatus="
    )
    template = template.replace("plots:24", "plots:32")
    data = json.dumps(payload, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    plots = out / "plots"
    plots.mkdir(exist_ok=True)
    html = template.replace("__PLOTLY__", get_plotlyjs()).replace("__DATA__", data)
    (plots / "s4_a_rankings.html").write_text(html)
    if not payload["data"] or "<script src=" in html:
        raise ValueError("S4_OFFLINE_VISUAL_PAYLOAD_GATE")
    proof = dict(
        status="PASS_RECONCILED_VISUAL_PAYLOAD",
        run=current.name,
        scope="UNTRAINED_REHEARSAL" if rehearsal else "SAVED_S4_PREDICTIONS",
        view_keys=list(payload["data"]),
        panels=32,
        source_scores_sha256=digest(current / "oos_scores.parquet"),
        shared_dashboard=str(plots / "s4_a_rankings.html"),
        shared_dashboard_is_additive=True,
        browser_visual_qa="COMPONENT_VERIFIED_IN_PREFLIGHT; FINAL_ALL_EIGHT_REVIEW_REQUIRED",
    )
    (current / "VISUAL_DIAGNOSTICS_PASS.json").write_text(json.dumps(proof, indent=2) + "\n")
