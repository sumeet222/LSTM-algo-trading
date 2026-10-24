"""P028 append-only reports and progressive gated viewer; no training entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .branch_replication_release import markdown_table
from .config import atomic_new, digest, fingerprint, write_json
from .hf1m_ft16_source import checked, ref
from .real_batch_authority import atomic_replace_json
from .state_screen_metrics import paired
from .state_screen_spec import ARCHITECTURES, ARMS, FAIRNESS, P026, PARAMETERS, ROLES, RUNS


def document(path: Path, text: str) -> None:
    atomic_new(path, (text.strip() + "\n").encode())


def arm_documents(result: dict, destination: Path, cohorts: pd.DataFrame) -> list[Path]:
    arm = result["arm"]
    records = []
    for role in ROLES:
        m = json.loads((destination / role / "metrics.json").read_text())
        control = json.loads((destination / role / "peer_information_control.json").read_text())
        records.append(
            dict(
                role=role,
                original_TG20_MSE=m["mse"],
                MAE=m["mae"],
                daily_IC=m["daily_ic"],
                origin_IC=m["origin_ic_mean"],
                actual_z_MSE=m["optimized_z_mse"],
                prediction_SD=m["prediction_sd"],
                matched_peer_shift_origins=control["matched_origins"],
            )
        )
    result_path = destination / f"P028_{arm}_{ARCHITECTURES[arm]}_RESULT.md"
    text = (
        f"# P028 {arm} {ARCHITECTURES[arm]}\n\nScope: {result['scope']}. "
        f"Run {result['run_id']}; seed42; {PARAMETERS[arm]} parameters.\n\n{FAIRNESS}\n\n"
    )
    text += (
        f"Selector: `{json.dumps(result['selector'], sort_keys=True)}`. "
        "Fresh refit initialization equals original calibration initialization; no baseline refit. "
        "Strict original-TG20 D6g, frozen AdamW/session weighting, phase-correct "
        "train-only epsilon/scale and once-only inverse.\n\n"
    )
    text += markdown_table(pd.DataFrame(records), list(records[0]))
    text += (
        "\n\nComplete calibration/refit telemetry, optimizer moments/RNG, exact four-role "
        "reload and target reconstruction are bound in run_result.json. Fixed-checkpoint "
        "z-loss differs from online dropout-ON training loss. Only the two approved "
        "panel-state channels shift in the matched ten-session sensitivity; own16 stay "
        "fixed. This changes the input distribution, not a trained null or causal test. "
        "Source publication/rights/action-vintage qualifications and protected2026 lock remain.\n"
    )
    document(result_path, text)
    selected = cohorts.loc[
        cohorts.role.eq("refit")
        & cohorts.cohort.isin(
            [
                "ALL",
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "NUM_ONLY_5",
                "MAD_ONLY_5",
                "BOTH_5",
                "NEITHER_5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
            ]
        )
    ].copy()
    selected["conditional_objective"] = selected.weighted_objective / selected.objective_weight_mass
    tail = destination / f"P028_{arm}_OBJECTIVE_SPACE_EXTREME_LOSS.md"
    document(
        tail,
        f"# P028 {arm} true optimized-objective tails\n\n{FAIRNESS}\n\n"
        "Saved checkpoint/dropout OFF; phase-correct z-squared error and "
        "session→origin→20-stock weights. Ranked top1%/5% are row groups; "
        "99%/95%-of-fitting-maximum groups are magnitude ranges and may be empty or one row. "
        "The numerator/MAD disjoint partition conserves all rows and objective.\n\n"
        + markdown_table(selected, list(selected.columns))
        + "\n\nTrue float32 asinh z-loss and equal-session/origin/20-stock allocation. "
        "Rank tails differ from fractions-of-training-maximum ranges; disjoint numerator/MAD "
        "groups conserve all rows/loss. Exactly22 role-balanced deterministic source witnesses "
        "include52 candles, all20 target returns, native/scaled16 features and actual state/"
        "gate/router/global-local traces. No historic dropout mask reconstruction is claimed.",
    )
    return [result_path, tail]


def publish_partial(plan_path: Path) -> dict:
    from .state_screen_authority import code_binding, require_gate, rows

    plan = json.loads(plan_path.read_text())
    if plan["scope"] != "RESEARCH_CANDIDATE" or plan["code"] != code_binding():
        raise ValueError("P028_RESEARCH_VIEW_IDENTITY")
    completed = [r["run_id"] for r in rows() if r["status"] == "COMPLETED"]
    count = len(completed)
    if not count or completed != list(RUNS[:count]):
        raise ValueError("P028_GATED_VIEW_ORDER")
    out = plan_path.parent / f"viewer_stage_{count}"
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n")
    files = {}
    bindings = {}
    comparison = []
    gates = []
    for arm, run in zip(ARMS[:count], RUNS[:count]):
        gate_path = plan_path.parent / (arm + "_immediate_gate.json")
        gate = require_gate(gate_path, arm)
        if gate["proposal_sha256"] != digest(plan_path):
            raise ValueError("P028_VIEW_GATE_PROPOSAL")
        gates.append(ref(gate_path))
        folder = Path(plan["private_root"]) / (arm + "_immediate_diagnostics")
        payload = json.loads((folder / "ui_payload/manifest.json").read_text())
        if "context.json" in payload["files"]:
            files["context.json"] = payload["files"]["context.json"]
        for key, reference in payload["files"].items():
            if key.startswith(arm + "/"):
                checked(reference)
                files[key] = reference
        result = json.loads((Path(plan["private_root"]) / run / "run_result.json").read_text())
        bindings[arm] = dict(
            run_id=run,
            parameters=PARAMETERS[arm],
            calibration=result["calibration"],
            refit=result["refit"],
            input_contract=plan["input_contract"],
        )
        for role in ROLES:
            m = json.loads((folder / role / "metrics.json").read_text())
            comparison.append(
                dict(
                    arm=arm,
                    role=role,
                    parameters=PARAMETERS[arm],
                    original_TG20_MSE=m["mse"],
                    daily_IC=m["daily_ic"],
                    origin_IC=m["origin_ic_mean"],
                    actual_z_MSE=m["optimized_z_mse"],
                    prediction_SD=m["prediction_sd"],
                    selected=result["selector"]["selected"],
                    raw_best=result["selector"]["raw_epoch"],
                    stopped=result["selector"]["epoch"],
                    fit_seconds=result["seconds"],
                    fit_peak_RSS=result["peak_rss_bytes"],
                )
            )
            if arm == ARMS[0]:
                for b in m["baselines"]:
                    bm = b["metrics"]
                    comparison.append(
                        dict(
                            arm=b["name"],
                            role=role,
                            parameters=0 if b["name"] == "ZERO" else 6433,
                            original_TG20_MSE=bm["mse"],
                            daily_IC=bm["daily_ic"],
                            actual_z_MSE=bm.get("optimized_z_mse"),
                            prediction_SD=bm["prediction_sd"],
                        )
                    )
    table = pd.DataFrame(comparison)
    table.to_parquet(out / "comparison.parquet", index=False)
    files["comparison.parquet"] = ref(out / "comparison.parquet")
    document(
        out / "P028_MARKET_STATE_COLLECTIVE_COMPARISON.md",
        "# P028 completed subset\n\n"
        + FAIRNESS
        + "\n\n"
        + markdown_table(table, list(table.columns))
        + (
            "\n\nOnly models whose complete scientific and component gate passe"
            "d are shown. Refit in sample; development exploratory; absent ar"
            "ms are not inferred. No promotion or causal architecture attribu"
            "tion."
        ),
    )
    guide = out / "P028_DASHBOARD_USER_GUIDE.md"
    document(
        guide,
        "# P028 market-state explorer\n\nExplore → HF1M Long — Market-State Recurrence (P028). "
        "Choose completed A7/A8/A12 and one of four roles. Inner roles use calibration; refit "
        "is in sample; development repeatedly inspected/exploratory. Comparison shows original "
        "TG20 MSE and daily/origin IC, signed T2/42 deltas and400 seed22042 month/two-month "
        "intervals. Outputs distinguish actual optimized z-MSE, forecast SD and ZERO undefined IC. "
        "Actual-Objective Tails shows ranked1/5%, magnitude95/99%-of-fitting-max and disjoint "
        "numerator/MAD groups. Exact Cases has22 deterministic refit/development source witnesses, "
        "52 candles with true observed volume/flags, 16 native/scaled "
        "features plus2 state histories, "
        "all20 future-return operands and eval-mode model traces. Mechanisms reads full-refit "
        "gates/global-local norms/router-head divergence and fixed-weight derivatives; "
        "State Information Control shifts only2 histories ten earlier "
        "eligible sessions, own16 fixed. "
        "History / Features covers20stocks/16channels. Training / Gradients reads immutable "
        "batch/epoch telemetry and selected/raw epochs. Protected2026 and malformed routes "
        "fail before lookup. Private read-only view; no training/downloads/trading.\n\n" + FAIRNESS,
    )
    files["guide.md"] = ref(guide)
    files["comparison.md"] = ref(out / "P028_MARKET_STATE_COLLECTIVE_COMPARISON.md")
    manifest = out / "view_manifest.json"
    write_json(
        manifest,
        dict(
            status="PASS_P028_COLLECTIVE" if count == 3 else "PASS_P028_PARTIAL_VIEW",
            scope="RESEARCH_CANDIDATE",
            ledger=59 + count,
            available_arms=list(ARMS[:count]),
            source_contract=plan["input_contract"],
            protected_numeric_access=False,
            files=files,
            gates=gates,
            execution_sha256=fingerprint(plan["code"]),
        ),
    )
    config = dict(
        manifest=ref(manifest),
        available_arms=list(ARMS[:count]),
        model_bindings=bindings,
        fit_permission=False,
    )
    immutable = Path(f"configs/track_a_p028_visualization_stage{count}.json")
    write_json(immutable, config)
    pointer = Path("configs/track_a_p028_visualization_v1.json")
    if pointer.exists():
        atomic_new(out / "previous_view_pointer.json", pointer.read_bytes())
    atomic_replace_json(pointer, config)
    return ref(manifest)


def finish(plan_path: Path) -> None:
    from .state_screen_authority import code_binding, require_gate, rows

    plan = json.loads(plan_path.read_text())
    if (
        plan["scope"] != "RESEARCH_CANDIDATE"
        or plan["code"] != code_binding()
        or rows()[-1]["global_started_pairs"] != 62
    ):
        raise ValueError("P028_EXACT_THREE_COMPLETED_ARMS_REQUIRED")
    out = plan_path.parent / "collective_v1"
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n")
    comparison = pd.read_parquet(plan_path.parent / "viewer_stage_3/comparison.parquet")
    verdicts = []
    mechanisms = []
    tails = []
    populations = {}
    intervals = []
    for arm in ARMS:
        require_gate(plan_path.parent / (arm + "_immediate_gate.json"), arm)
        folder = Path(plan["private_root"]) / (arm + "_immediate_diagnostics")
        m = json.loads((folder / "development/metrics.json").read_text())
        b = m["baselines"][0]["metrics"]
        dm = m["mse"] - b["mse"]
        di = m["daily_ic"] - b["daily_ic"]
        verdicts.append(
            dict(
                arm=arm,
                delta_MSE=dm,
                delta_daily_IC=di,
                verdict="joint positive point estimates"
                if dm < 0 and di > 0
                else "joint negative point estimates"
                if dm > 0 and di < 0
                else "mixed/inconclusive",
            )
        )
        populations[arm] = pd.read_parquet(folder / "development/population.parquet")
        for item in json.loads((folder / "development/matched_T2_S42.json").read_text())[
            "intervals"
        ]:
            intervals.append(dict(comparison=arm + "_minus_T2_42", **item))
        mechanisms.append(
            dict(
                arm=arm,
                summary=json.loads((folder / "refit/mechanisms.json").read_text()),
                four_role_peer_controls={
                    role: json.loads((folder / role / "peer_information_control.json").read_text())
                    for role in ROLES
                },
            )
        )
        f = pd.read_parquet(folder / "cohorts.parquet")
        f["arm"] = arm
        tails.append(f)
    for a, b in [("A8", "A7"), ("A12", "A7"), ("A12", "A8")]:
        matched, daily = paired(populations[a], populations[b])
        matched["interpretation"] = (
            a + " minus " + b + "; dependent reused-development comparison, shared state source, "
            "differing processing/capacity"
        )
        write_json(out / (a + "_minus_" + b + ".json"), matched)
        daily.to_parquet(out / (a + "_minus_" + b + "_daily.parquet"), index=False)
        intervals.extend(
            dict(comparison=a + "_minus_" + b, **item) for item in matched["intervals"]
        )
    comparison.to_parquet(out / "comparison.parquet", index=False)
    pd.DataFrame(intervals).to_json(out / "paired_intervals.json", orient="records", indent=2)
    historical_path = P026 / "collective_v1/comparison.parquet"
    historical = pd.read_parquet(historical_path)
    historical.to_parquet(out / "historical_P027_reference.parquet", index=False)
    document(
        out / "P028_MARKET_STATE_COLLECTIVE_COMPARISON.md",
        "# P028 cross-stock comparison\n\n"
        + FAIRNESS
        + "\n\n"
        + markdown_table(pd.DataFrame(verdicts), list(verdicts[0]))
        + "\n\n"
        + markdown_table(comparison, list(comparison.columns))
        + (
            "\n\nPaired400 month/two-month sensitivities seed22042, signed effe"
            "cts, origin/daily IC and block occupancy remain in matched_T2_S4"
            "2.json and pairwise contrast JSONs. One seed, differing capacity"
            "/processing, three comparisons and repeatedly used109 developme"
            "nt sessions preclude formal significance or causal mechanism att"
            "ribution. P027 references are separately labeled historical; no "
            "P027 parent promotion, E1/QR1 fusion, automatic model promotion "
            "or new training."
        ),
    )
    write_json(
        out / "mechanism_and_peer_controls.json",
        dict(information_fairness=FAIRNESS, models=mechanisms),
    )
    document(
        out / "P028_MARKET_STATE_MECHANISM_FALSIFICATION.md",
        "# P028 state mechanism and bounded falsification\n\n"
        + FAIRNESS
        + "\n\nPer-arm mechanisms.json preserves actual gate/hidden-cell/router/head summaries and "
        "parameter norms. Full four-role ten-session source-only shifts, exact matched forecasts, "
        "representation changes and signed metrics are in mechanism_and_peer_controls.json. "
        "A7 uses endpoint MC1 with direct historical state; MC2 NOT_RUN. "
        "A8 updates one market-only "
        "global8 cell then local32 cells; no learned pooling or local feedback/fullC3. A12 uses "
        "two soft scalar readouts, not two recurrent encoders or identified economic regimes. "
        "Initial identity, null/gradient connectivity and relative-score "
        "routes were proved without "
        "optimizer steps. Nonzero sensitivity/gradients alone do not prove alpha. Development LOW "
        "has35sessions but only1 qualifying episode; source/support drift is descriptive. "
        "No fourth rich-input control, post-hoc promotion or further starts.",
    )
    f = pd.concat(tails)
    f.to_parquet(out / "all_objective_cohorts.parquet", index=False)
    selected = f.loc[
        f.role.eq("refit")
        & f.cohort.isin(
            [
                "ALL",
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "BOTH_5",
                "MAD_ONLY_5",
                "NUM_ONLY_5",
                "NEITHER_5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
            ]
        )
    ]
    document(
        out / "P028_OBJECTIVE_SPACE_EXTREME_LOSS.md",
        "# P028 true transformed-objective tails\n\n"
        + FAIRNESS
        + "\n\n"
        + markdown_table(selected, list(selected.columns))
        + (
            "\n\nDropout-OFF z-MSE, exact session/origin/20-stock weights. Rank"
            "ed observation tails and fractions-of-fitting-maximum magnitude "
            "ranges are distinct. Disjoint partitions conserve all rows/objec"
            "tive.66 exact role-balanced source cases and state traces remain loc"
            "al/ignored; no invented data or protected2026 access."
        ),
    )
    document(
        out / "P028_FINAL_HUMAN_REVIEW.md",
        (
            "# P028 completed three-arm review\n\nLedger62/200: exactly three s"
            "tarts, all full scientific/component gates pass. Correct executi"
            "on does not imply alpha.\n\n"
        )
        + FAIRNESS
        + "\n\n"
        + markdown_table(pd.DataFrame(verdicts), list(verdicts[0]))
        + (
            "\n\nRead the collective comparison, true-objective tail report, pe"
            "er mechanism falsification and dashboard guide. All source/right"
            "s/clock/protected holds persist. No further fitting/trading/Git "
            "publication is authorized."
        ),
    )
    write_json(
        out / "collective_receipt.json",
        dict(
            status="PASS_P028_COMPLETE_COLLECTIVE",
            ledger=62,
            proposal=ref(plan_path),
            execution_sha256=fingerprint(plan["code"]),
            gates=[ref(plan_path.parent / (a + "_immediate_gate.json")) for a in ARMS],
            historical_P027_reference=ref(historical_path),
            files=[ref(f) for f in sorted(out.iterdir()) if f.is_file()],
            protected_numeric_access=False,
        ),
    )
