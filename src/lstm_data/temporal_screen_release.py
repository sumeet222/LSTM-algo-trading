"""Read-only P026 reports and collective viewer seal; no model training entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .branch_replication_release import markdown_table
from .config import atomic_new, digest, write_json
from .hf1m_ft16_source import checked, ref
from .temporal_screen_spec import ARCHITECTURES, ARMS, PARAMETERS, ROLES, RUNS


def document(path: Path, text: str) -> None:
    atomic_new(path, (text.rstrip() + "\n").encode())


def arm_documents(result: dict, destination: Path, cohorts: pd.DataFrame) -> list[Path]:
    arm = result["arm"]
    rows = []
    for role in ROLES:
        m = json.loads((destination / role / "metrics.json").read_text())
        rows.append(
            dict(
                role=role,
                MSE=m["mse"],
                IC=m["daily_ic"],
                prediction_SD=m["prediction_sd"],
                actual_objective_z_MSE=m["optimized_z_mse"],
            )
        )
    fit = markdown_table(pd.DataFrame(rows), list(rows[0]))
    # These tables are small aggregate scientific metadata, never point-level source candles.
    result_path = destination / f"P026_{arm}_{ARCHITECTURES[arm]}_RESULT.md"
    document(
        result_path,
        (
            f"# P026 {arm} {ARCHITECTURES[arm]}\n\n"
            f"Scope: {result['scope']}. Run {result['run_id']}; seed42; "
            f"{PARAMETERS[arm]} parameters.\n\n"
            "Calibration selector (strict original-TG20 MSE): "
            f"`{json.dumps(result['selector'], sort_keys=True)}`. "
            "Fresh refit initialization equals initial calibration initialization. "
            f"No baseline refit.\n\n{fit}\n\n"
            "Actual z-MSE, original-TG20 MSE and historical online dropout-ON objectives "
            "are separate records. Matched T2/42, T2/123 and ZERO are in role metrics. "
            "Full update/parameter-gradient telemetry and immutable epoch receipts are "
            "bound in the run result; gamma/query trajectory applies to A1. "
            "Mechanism tables measure actual saved models. GRU gates are unobserved.\n\n"
            "Development reuses183 origins/109 sessions in research scope. Paired400 "
            "one/two-month sensitivities are exploratory, not independent confirmation. "
            "Module use and amplitude changes are not predictive skill. No automatic "
            "promotion or additional training.\n"
        ),
    )
    tail_path = destination / f"P026_{arm}_OBJECTIVE_SPACE_EXTREME_LOSS.md"
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
    ]
    document(
        tail_path,
        "# P026 "
        + arm
        + (
            " actual-objective extreme loss\n\nSaved refit checkpoint, dropout "
            "OFF; true equal-session/origin/stock z-MSE allocations. Ranked t"
            "ails are observation percentages; range tails are fractions of f"
            "itting-prefix maxima. Disjoint numerator/MAD shares conserve tot"
            "al objective.\n\n"
        )
        + markdown_table(selected, list(selected.columns))
        + (
            "\n\nAll four roles and complement/sign cohorts are in cohorts.parq"
            "uet. Twenty-two source cases include five largest weighted losse"
            "s each for AAPL, AMZN, TSLA, SBUX and distinct BOTH_5/MAD_ONLY_5"
            ". Each records52 genuine hourly candles, observed volume/quality"
            ",48×16 native/scaled/fallback values and all20 independent retur"
            "n operands. Private case stores remain local; source prices are "
            "not repaired or certified by these reports.\n"
        ),
    )
    return [result_path, tail_path]


def finish(plan_path: Path) -> None:
    from .config import fingerprint
    from .temporal_screen_authority import code_binding, require_gate, rows
    from .visualization.hf1m_long import LongStudy

    plan = json.loads(plan_path.read_text())
    if (
        plan.get("scope") != "RESEARCH_CANDIDATE"
        or code_binding() != plan["code"]
        or not rows()
        or rows()[-1]["global_started_pairs"] != 56
    ):
        raise ValueError("P026_COMPLETE_THREE_ARM_IDENTITY_REQUIRED")
    out = plan_path.parent / "collective_v1"
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n")
    files = {}
    comparisons = []
    verdicts = []
    bindings = {}
    for arm, run_id in zip(ARMS, RUNS):
        gate = require_gate(plan_path.parent / (arm + "_immediate_gate.json"), arm)
        if gate["proposal_sha256"] != digest(plan_path):
            raise ValueError("P026_GATE_PROPOSAL")
        folder = Path(plan["private_root"]) / (arm + "_immediate_diagnostics")
        result_path = Path(plan["private_root"]) / run_id / "run_result.json"
        result = json.loads(result_path.read_text())
        bindings[arm] = dict(
            run_id=run_id,
            calibration=result["calibration"],
            refit=result["refit"],
            input_contract=plan["input_contract"],
        )
        for reference in gate["evidence"]:
            p = checked(reference)
            if p.is_relative_to(folder):
                files[f"{arm}/{p.relative_to(folder)}"] = reference
        updates = pd.DataFrame(
            [
                json.loads(line)
                for line in checked(result["optimizer_telemetry"]).read_text().splitlines()
            ]
        )
        updates["batch_index"] = range(len(updates))
        updates.to_parquet(out / (arm + "_updates.parquet"), index=False)
        pd.DataFrame(
            [dict(phase=e["phase"], **e["training"]) for e in result["epochs"]]
        ).to_parquet(out / (arm + "_epochs.parquet"), index=False)
        files[f"{arm}/updates.parquet"] = ref(out / (arm + "_updates.parquet"))
        files[f"{arm}/epochs.parquet"] = ref(out / (arm + "_epochs.parquet"))
        for role in ROLES:
            m = json.loads((folder / role / "metrics.json").read_text())
            if role == "development":
                primary = m["baselines"][0]["metrics"]
                dm = m["mse"] - primary["mse"]
                di = m["daily_ic"] - primary["daily_ic"]
                verdict = (
                    "suggestive joint positive point estimates"
                    if dm < 0 and di > 0
                    else "negative joint point estimates"
                    if dm > 0 and di < 0
                    else "mixed or inconclusive"
                )
                verdicts.append(
                    dict(
                        arm=arm,
                        delta_MSE=dm,
                        delta_IC=di,
                        verdict=verdict,
                        uncertainty="400 month-block sensitivities; exploratory",
                    )
                )
            if arm == "A1":
                for baseline in m["baselines"]:
                    bm = baseline["metrics"]
                    comparisons.append(
                        dict(
                            arm=baseline["name"],
                            architecture="saved TM0/T2"
                            if baseline["name"] != "ZERO"
                            else "constant",
                            parameters=6433 if baseline["name"] != "ZERO" else 0,
                            role=role,
                            MSE=bm["mse"],
                            IC=bm["daily_ic"],
                            prediction_SD=bm["prediction_sd"],
                            z_MSE=bm.get("optimized_z_mse"),
                            seconds=None,
                            RSS=None,
                            selected_epoch=None,
                            raw_epoch=None,
                            stopping_epoch=None,
                        )
                    )
            comparisons.append(
                dict(
                    arm=arm,
                    architecture=ARCHITECTURES[arm],
                    parameters=PARAMETERS[arm],
                    role=role,
                    MSE=m["mse"],
                    IC=m["daily_ic"],
                    prediction_SD=m["prediction_sd"],
                    z_MSE=m["optimized_z_mse"],
                    seconds=result["seconds"],
                    RSS=result["peak_rss_bytes"],
                    selected_epoch=result["selector"]["selected"],
                    raw_epoch=result["selector"]["raw_epoch"],
                    stopping_epoch=result["selector"]["epoch"],
                )
            )
    study = LongStudy.discover(Path.cwd())
    for seed in (42, 123):
        for role in ROLES:
            path = out / f"T2_{seed}_{role}.parquet"
            study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", role).to_parquet(path, index=False)
            files[f"baselines/{seed}/{role}.parquet"] = ref(path)
    table = pd.DataFrame(comparisons)
    table.to_parquet(out / "comparison.parquet", index=False)
    files["comparison.parquet"] = ref(out / "comparison.parquet")
    collective = out / "P026_TEMPORAL_ARCHITECTURE_COLLECTIVE_COMPARISON.md"
    document(
        collective,
        "# P026 temporal architecture comparison\n\n"
        + markdown_table(pd.DataFrame(verdicts), list(verdicts[0]))
        + "\n\n"
        + markdown_table(table, list(table.columns))
        + (
            "\n\nPrimary comparison is saved seed42 T2 on identical panels; T2/"
            "123 contextual and ZERO are in each metrics file. Joint MSE/IC i"
            "mprovement is suggestive only; mixed outcomes remain mixed. Thre"
            "e dependent, development-informed architecture comparisons canno"
            "t establish formal significance or isolate parameter-count effec"
            "ts. E1/QR1 remain independent branches. No automatic promotion o"
            "r further fitting. Inspect matched month-block intervals, all sl"
            "ices and mechanism tables before interpreting point estimates.\n"
        ),
    )
    files["comparison.md"] = ref(collective)
    guide = out / "P026_DASHBOARD_USER_GUIDE.md"
    document(
        guide,
        (
            "# P026 explorer\n\nLaunch ./scripts/run_track_a_dashboard.sh and s"
            "elect Explore → HF1M Long — Temporal Architectures (P026). Choos"
            "e A1/A2/A3 and one of four roles. Comparison shows saved T2 cont"
            "rols and paired deltas; Outputs overlays T2/42, T2/123 and ZERO."
            " Actual-Objective Tails distinguishes rank and magnitude cohorts"
            ". Exact Cases shows52 source hours, entry/exit markers, observed"
            "_volume_sum and volume_quality_tier; missing-minute volume is no"
            "t verified zero. Mechanisms shows actual module statistics and i"
            "nput-history sensitivity; attention is not attribution and GRU g"
            "ates are unobserved. Inner roles use selected calibration checkp"
            "oints; refit is in sample, development exploratory. Protected202"
            "6 and invalid selectors fail before file lookup. Private artifac"
            "ts must be lawfully provisioned and hash-identical on another ma"
            "chine.\n"
        ),
    )
    files["guide.md"] = ref(guide)
    manifest = out / "view_manifest.json"
    write_json(
        manifest,
        dict(
            status="PASS_P026_COLLECTIVE",
            ledger=56,
            source_contract=plan["input_contract"],
            protected_numeric_access=False,
            files=files,
            execution_sha256=fingerprint(plan["code"]),
        ),
    )
    write_json(
        Path("configs/track_a_p026_visualization_v1.json"),
        dict(manifest=ref(manifest), model_bindings=bindings, fit_permission=False),
    )
    document(
        out / "P026_OBJECTIVE_SPACE_EXTREME_LOSS.md",
        (
            "# P026 actual-objective loss\n\nAll three arm-specific reports are"
            " bound in the manifest. They allocate the same z-MSE definition "
            "with phase-specific fitted scales. Ranked, range, numerator, MAD"
            " and disjoint cohorts remain separate. Sixty-six genuine52-hour "
            "source witnesses remain local/ignored.\n"
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    finish(p.parse_args().plan)
