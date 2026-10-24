"""P027 append-only reports and progressive gated viewer; no training entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .branch_replication_release import markdown_table
from .config import atomic_new, digest, fingerprint, write_json
from .hf1m_ft16_source import checked, ref
from .peer_screen_metrics import paired
from .peer_screen_spec import ARCHITECTURES, ARMS, FAIRNESS, P026, PARAMETERS, ROLES, RUNS
from .real_batch_authority import atomic_replace_json


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
    result_path = destination / f"P027_{arm}_{ARCHITECTURES[arm]}_RESULT.md"
    text = (
        f"# P027 {arm} {ARCHITECTURES[arm]}\n\nScope: {result['scope']}. "
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
        "\n\nFull gradients/clipping/epoch updates, saved model/optimizer/R"
        "NG hashes and four-role reload receipts are bound in run_result."
        "json. Actual-objective z-MSE is distinct from raw TG20 MSE and h"
        "istorical online dropout-ON losses. Mechanisms use saved weights"
        "; off-diagonal sensitivity and attention are not causal explanat"
        "ions. Ten-session same-slot peer replacement is a matched distri"
        "bution shift, not a trained null or p-value. Source/rights/clock"
        " assumptions remain conditional; repeated109-session development"
        " is exploratory. No automatic promotion, fourth full-peer contro"
        "l, seed123 fit or additional model is authorized.\n"
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
    tail = destination / f"P027_{arm}_OBJECTIVE_SPACE_EXTREME_LOSS.md"
    document(
        tail,
        f"# P027 {arm} true optimized-objective tails\n\n{FAIRNESS}\n\n"
        "Saved checkpoint/dropout OFF; phase-correct z-squared error and "
        "session→origin→20-stock weights. Ranked top1%/5% are row groups; "
        "99%/95%-of-fitting-maximum groups are magnitude ranges and may be empty or one row. "
        "The numerator/MAD disjoint partition conserves all rows and objective.\n\n"
        + markdown_table(selected, list(selected.columns))
        + (
            "\n\nAll four roles, signs, complements and exact thresholds are in"
            " cohorts.parquet/thresholds.json.22 distinct genuine source case"
            "s carry48 inputs+four future outcome hours, observed volume/qual"
            "ity,16 native/scaled features/masks and all20 target operands. c"
            "ase_peer_hidden links all peer encoders. A4 also records19×48 M1"
            " operands and independently checked summaries per case; A6 recor"
            "ds true20×20 case attention. All point-level stores remain ignor"
            "ed/private. Protected2026 is not read.\n"
        ),
    )
    return [result_path, tail]


def publish_partial(plan_path: Path) -> dict:
    from .peer_screen_authority import code_binding, require_gate, rows

    plan = json.loads(plan_path.read_text())
    if plan["scope"] != "RESEARCH_CANDIDATE" or plan["code"] != code_binding():
        raise ValueError("P027_RESEARCH_VIEW_IDENTITY")
    completed = [r["run_id"] for r in rows() if r["status"] == "COMPLETED"]
    count = len(completed)
    if not count or completed != list(RUNS[:count]):
        raise ValueError("P027_GATED_VIEW_ORDER")
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
            raise ValueError("P027_VIEW_GATE_PROPOSAL")
        gates.append(ref(gate_path))
        folder = Path(plan["private_root"]) / (arm + "_immediate_diagnostics")
        payload = json.loads((folder / "ui_payload/manifest.json").read_text())
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
        out / "P027_CROSS_STOCK_COLLECTIVE_COMPARISON.md",
        "# P027 completed subset\n\n"
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
    guide = out / "P027_DASHBOARD_USER_GUIDE.md"
    document(
        guide,
        (
            "# P027 cross-stock explorer\n\nExplore → HF1M Long — Cross-Stock S"
            "haring (P027). Select a completed A4/A5/A6 and one of four roles"
            "; inner roles use calibration recipes/checkpoints, refit is in s"
            "ample, development exploratory. Comparison/Outputs show raw TG20"
            " MSE separately from actual optimized z-MSE, T2/42 primary, T2/1"
            "23 and ZERO context (ZERO IC undefined). Actual-Objective Tails "
            "separates ranked and magnitude ranges/disjoint numerator-MAD gro"
            "ups. Exact Cases shows52 genuine source hours with input/issuanc"
            "e/exit markers, volume flags,16 features and peer operands/encod"
            "ers/attention. Mechanisms shows summary statistics, canonical st"
            "ock-axis mixing or true same-origin attention, never causal clai"
            "ms. Peer Information Control reports matched ten-session same-sl"
            "ot source-input-only donor shifts, own history fixed; not a trai"
            "ned null. History / Features covers all20 tickers/16 channels. T"
            "raining / Gradients reads immutable telemetry. Protected2026/mal"
            "formed routes fail before lookup; no fitting or downloads.\n\n"
        )
        + FAIRNESS,
    )
    files["guide.md"] = ref(guide)
    files["comparison.md"] = ref(out / "P027_CROSS_STOCK_COLLECTIVE_COMPARISON.md")
    manifest = out / "view_manifest.json"
    write_json(
        manifest,
        dict(
            status="PASS_P027_COLLECTIVE" if count == 3 else "PASS_P027_PARTIAL_VIEW",
            scope="RESEARCH_CANDIDATE",
            ledger=56 + count,
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
    immutable = Path(f"configs/track_a_p027_visualization_stage{count}.json")
    write_json(immutable, config)
    pointer = Path("configs/track_a_p027_visualization_v1.json")
    if pointer.exists():
        atomic_new(out / "previous_view_pointer.json", pointer.read_bytes())
    atomic_replace_json(pointer, config)
    return ref(manifest)


def finish(plan_path: Path) -> None:
    from .peer_screen_authority import code_binding, require_gate, rows

    plan = json.loads(plan_path.read_text())
    if (
        plan["scope"] != "RESEARCH_CANDIDATE"
        or plan["code"] != code_binding()
        or rows()[-1]["global_started_pairs"] != 59
    ):
        raise ValueError("P027_EXACT_THREE_COMPLETED_ARMS_REQUIRED")
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
    for a, b in [("A5", "A4"), ("A6", "A4"), ("A6", "A5")]:
        matched, daily = paired(populations[a], populations[b])
        matched["interpretation"] = (
            a
            + " minus "
            + b
            + "; dependent reused-development comparison, not equal-information A4 control"
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
    historical.to_parquet(out / "historical_P026_reference.parquet", index=False)
    document(
        out / "P027_CROSS_STOCK_COLLECTIVE_COMPARISON.md",
        "# P027 cross-stock comparison\n\n"
        + FAIRNESS
        + "\n\n"
        + markdown_table(pd.DataFrame(verdicts), list(verdicts[0]))
        + "\n\n"
        + markdown_table(comparison, list(comparison.columns))
        + (
            "\n\nPaired400 month/two-month sensitivities seed22042, signed effe"
            "cts, origin/daily IC and block occupancy remain in matched_T2_S4"
            "2.json and pairwise contrast JSONs. One seed, differing capacity"
            "/information, three comparisons and repeatedly used109 developme"
            "nt sessions preclude formal significance or causal mechanism att"
            "ribution. P026 references are separately labeled historical; no "
            "P026 parent promotion, E1/QR1 fusion, automatic model promotion "
            "or new training."
        ),
    )
    write_json(
        out / "mechanism_and_peer_controls.json",
        dict(information_fairness=FAIRNESS, models=mechanisms),
    )
    document(
        out / "P027_PEER_INFORMATION_AND_MECHANISM_FALSIFICATION.md",
        "# P027 peer mechanisms and falsification\n\n"
        + FAIRNESS
        + (
            "\n\nAll actual projection/mixing norms and spectra, local cross-hi"
            "dden and peer-input derivatives, own-base readout shifts, source"
            " operands, true same-origin attention/self mass and saved coordi"
            "nate-permutation checks are bound in per-arm mechanisms.json and"
            " private Parquets. mechanism_and_peer_controls.json preserves th"
            "e four-role original-vs-ten-session-shift matched metrics and co"
            "unts, not only favorable slices. Zero/near-zero peer response is"
            " a negative finding, not a rescue trigger. Shifts alter input di"
            "stributions and are not a trained permutation null; common-marke"
            "t information can cancel in TG20 rankings. Attention is not caus"
            "al explanation. A5 depends on ticker coordinates; A6 is equivari"
            "ant absent learned identities. A5/A6 versus A4 do not isolate ar"
            "chitecture. A fourth full-peer ordinary LSTM, replication, marke"
            "t-state or regime work requires a separate proposal and authoriz"
            "ation."
        ),
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
        out / "P027_OBJECTIVE_SPACE_EXTREME_LOSS.md",
        "# P027 true transformed-objective tails\n\n"
        + FAIRNESS
        + "\n\n"
        + markdown_table(selected, list(selected.columns))
        + (
            "\n\nDropout-OFF z-MSE, exact session/origin/20-stock weights. Rank"
            "ed observation tails and fractions-of-fitting-maximum magnitude "
            "ranges are distinct. Disjoint partitions conserve all rows/objec"
            "tive.66 exact source cases and peer operands/encoders remain loc"
            "al/ignored; no invented data or protected2026 access."
        ),
    )
    document(
        out / "P027_FINAL_HUMAN_REVIEW.md",
        (
            "# P027 completed three-arm review\n\nLedger59/200: exactly three s"
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
            status="PASS_P027_COMPLETE_COLLECTIVE",
            ledger=59,
            proposal=ref(plan_path),
            execution_sha256=fingerprint(plan["code"]),
            gates=[ref(plan_path.parent / (a + "_immediate_gate.json")) for a in ARMS],
            historical_P026_reference=ref(historical_path),
            files=[ref(f) for f in sorted(out.iterdir()) if f.is_file()],
            protected_numeric_access=False,
        ),
    )
