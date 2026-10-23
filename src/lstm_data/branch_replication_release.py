"""P025 read-only scientific reporting after each approved, gated fit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .branch_replication_authority import code_binding, require_gate, rows
from .branch_replication_spec import ARMS, CONTRACT, ROLES, RUNS
from .config import atomic_new, digest, now, write_json
from .hf1m_ft16_source import checked, ref


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def value(v) -> str:
        if isinstance(v, (float, np.floating)):
            return f"{v:.6g}" if np.isfinite(v) else "undefined"
        return str(v).replace("|", "/").replace("\n", " ")

    return (
        "| "
        + " | ".join(columns)
        + " |\n|"
        + "|".join("---" for _ in columns)
        + "|\n"
        + "\n".join(
            "| " + " | ".join(value(row[c]) for c in columns) + " |" for _, row in frame.iterrows()
        )
        + "\n"
    )


def document(path: Path, text: str) -> None:
    atomic_new(path, (text.rstrip() + "\n").encode())


def initialize(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    ignore = out / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n!.gitignore\n!*.md\n")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def diagnosis(plan: dict, arm: str) -> Path:
    return Path(plan["private_root"]) / (arm + "_immediate_diagnostics")


def checked_arm(plan_path: Path, arm: str) -> tuple[dict, dict, dict]:
    plan = load_json(plan_path)
    if plan["code"] != code_binding() or plan["input_contract"]["sha256"] != CONTRACT:
        raise ValueError("P025_READ_ONLY_REPORT_BINDING")
    gate = require_gate(plan_path.parent / (arm + "_immediate_gate.json"), arm)
    if gate["proposal_sha256"] != digest(plan_path):
        raise ValueError("P025_REPORT_PROPOSAL")
    history = [r for r in rows() if r["run_id"] == RUNS[ARMS.index(arm)]]
    if not history or history[-1]["status"] != "COMPLETED":
        raise ValueError("P025_REAL_COMPLETION_REQUIRED")
    result = load_json(checked(history[-1]["detail"]["result"]))
    return plan, result, gate


def optimizer_summary(result: dict) -> list[dict]:
    updates = pd.DataFrame(
        [
            json.loads(line)
            for line in checked(result["optimizer_telemetry"]).read_text().splitlines()
        ]
    )
    answer = []
    for phase, role in (("calibration", "inner_train"), ("refit", "refit")):
        f = updates.loc[updates.role.eq(role)]
        row = dict(
            arm=result["arm"],
            phase=phase,
            updates=len(f),
            epochs=f.epoch.nunique(),
            clipped_fraction=float(f.preclip_norm.gt(1).mean()),
            nonfinite=0,
        )
        for column in ("preclip_norm", "postclip_norm", "update_norm", "weight_norm"):
            a = f[column].to_numpy(dtype=float)
            if not np.isfinite(a).all():
                raise ValueError("P025_NONFINITE_SAVED_TELEMETRY")
            for suffix, value in zip(
                ("p50", "p90", "p99", "max", "mean"),
                [*np.quantile(a, [0.5, 0.9, 0.99]), a.max(), a.mean()],
            ):
                row[column + "_" + suffix] = float(value)
        answer.append(row)
    return answer


def arm_report(plan_path: Path, arm: str, out: Path) -> None:
    plan, result, gate = checked_arm(plan_path, arm)
    initialize(out)
    diag = diagnosis(plan, arm)
    scores = []
    for role in ROLES:
        m = load_json(diag / role / "metrics.json")
        if arm == "E1":
            scores.append(
                dict(
                    role=role,
                    objective=m["fixed_checkpoint_actual_objective"],
                    ANY_AP=m["ANY_AP"],
                    NEG_AP=m["NEG_AP"],
                    POS_AP=m["POS_AP"],
                    signed_IC=m["ordinal_daily_IC"],
                    CE=m["unweighted_CE"],
                    Brier=sum(m["Brier_by_class"]),
                    ANY_ECE=m["ANY_ECE10"],
                )
            )
        else:
            scores.append(
                dict(
                    role=role,
                    objective=m["fixed_checkpoint_actual_objective"],
                    pinball=m["pinball"],
                    unconditional=m["unconditional"]["pinball"],
                    skill=m["pinball_skill"],
                    coverage90=m["interval_coverage"],
                    width_z=m["interval_width"],
                    interval_score=m["interval_score"],
                    descriptive_median_MSE=m["mse"],
                    descriptive_median_IC=m["daily_ic"],
                )
            )
    frame = pd.DataFrame(scores)
    frame.to_csv(out / (arm + "_role_scores.csv"), index=False)
    optimization = pd.DataFrame(optimizer_summary(result))
    optimization.to_csv(out / (arm + "_optimization.csv"), index=False)
    epochs = pd.DataFrame(
        [
            dict(
                phase=e["phase"],
                epoch=e["training"]["epoch"],
                train=e["training"]["optimized_objective"],
                validation=e.get("validation", {}).get("optimized_objective", np.nan),
                qualifies=e.get("qualifies", False),
            )
            for e in result["epochs"]
        ]
    )
    epochs.to_csv(out / (arm + "_epochs.csv"), index=False)
    fig = go.Figure()
    for phase in ("calibration", "refit"):
        e = epochs.loc[epochs.phase.eq(phase)]
        fig.add_trace(go.Scatter(x=e.epoch, y=e.train, name=phase + " online/dropout training"))
        if phase == "calibration":
            fig.add_trace(
                go.Scatter(x=e.epoch, y=e.validation, name="inner validation/dropout OFF")
            )
    fig.update_layout(
        title=arm + " actual objective; online training differs from fixed-checkpoint loss",
        xaxis_title="Epoch",
        yaxis_title="Session-normalized CE" if arm == "E1" else "Mean-three pinball (z)",
    )
    fig.write_html(out / (arm + "_training.html"), include_plotlyjs="directory")
    cohorts = pd.read_parquet(diag / "cohorts.parquet")
    cohorts.to_csv(out / (arm + "_objective_cohorts.csv"), index=False)
    cases = pd.read_parquet(diag / "refit/cases.parquet")
    cases.to_csv(out / (arm + "_exact_cases.csv"), index=False)
    document(
        out / (arm + "_EXACT_CASES.md"),
        f"# P025 {arm}/123 exact source cases\n\n"
        + (
            "Highest actual weighted objective losses, not ex-ante signals. Each case "
            "preserves48 scheduled input hours and4 future outcome hours,20 genuine "
            "horizon return operands,16 native/scaled features and source/volume flags."
            " Future outcomes are labels only. Private Parquets remain local.\n\n"
        )
        + markdown_table(
            cases,
            [
                c
                for c in (
                    "case_id",
                    "ticker",
                    "session_date_et",
                    "selection",
                    "TG20",
                    "return_4h",
                    "cross_section_median",
                    "cross_section_mad",
                    "numerator",
                    "epsilon",
                    "total",
                )
                if c in cases
            ],
        ),
    )
    dev = load_json(diag / "development/metrics.json")
    matched = load_json(diag / "development/matched_seed42_comparison.json")
    selector = result["selector"]
    if arm == "E1":
        old = matched["seed42_raw"]
        finding = f"""Development ANY AP is {dev[("ANY_AP")]:.9f} versus seed42 {
            old[("ANY_AP")]:.9f} and
constant-prior AP {dev["constant_fit_prior"]["ANY_AP"]:.9f}. Signed probability IC is
{dev["ordinal_daily_IC"]:.6f}; ANY-event ranking is separate from signed alpha. Raw
natural-frequency CE is {dev["unweighted_CE"]:.6f}; analytical correction CE is
{dev["analytical_inverse_weight"]["unweighted_CE"]:.6f}."""
        uncertainty = matched["raw_ANY_AP_difference_123_minus_42_month_blocks"]
    else:
        old = matched["seed42"]
        finding = f"""Development proper pinball is {dev[("pinball")]:.9f} versus seed42 {
            old[("pinball")]:.9f} and
frozen unconditional {dev["unconditional"]["pinball"]:.9f}; point skill {
            100 * dev["pinball_skill"]:.3f}%. 90% interval coverage is {
            dev["interval_coverage"]:.6f}.
Median TG20 MSE/IC are descriptive and do not test conditional-mean skill."""
        uncertainty = matched["pinball_difference_123_minus_42_month_blocks"]
    optimization_text = markdown_table(
        optimization,
        [
            ("phase"),
            ("epochs"),
            ("updates"),
            ("preclip_norm_p50"),
            ("preclip_norm_p90"),
            ("preclip_norm_p99"),
            ("preclip_norm_max"),
            ("postclip_norm_max"),
            ("clipped_fraction"),
        ],
    )
    text = f"""# P025 {arm} seed123 replication result

{finding}

Successful numerical execution is separate from useful task improvement and replication.
Development is exploratory:183 origins,3,660 stock rows,109 reused sessions. No 2026 outcomes,
trading or production conclusion.

## Frozen fit and verification

Run `{result["run_id"]}`; seed123;6,499 parameters; calibration epochs{selector["epoch"]},
qualifying selected{selector["selected"]}, raw best{selector["raw_epoch"]}; fresh refit
epochs{selector["selected"]}. Original loss/recipe/D6g and inputs unchanged. Gate
`{gate["status"]}` verifies all4 populations, exact checkpoint reloads, genuine20-stock target
reconstruction, tensor/NumPy actual objective and{gate["cases"]["cases"]} exact source cases.
Input SHA256 `{CONTRACT}`; proposal `{digest(plan_path)}`; executor
`{result["execution_sha256"]}`.

## All permitted roles

{markdown_table(frame, list(frame.columns))}

## Matched development sensitivity

One/two-month blocks,400 resamples,seed22042. Recompute nonlinear AP from full-day panels. Few
calendar blocks and repeated development use limit interpretation; these are sensitivity
intervals, not formal significance or held-out confirmation.

{json.dumps(uncertainty, indent=2)}

## Optimization and source cases

{optimization_text}

Actual full update/state hashes, immutable epochs, saved optimizer states, dropout-OFF
checkpoint objectives and source-bound per-role cohort tables remain in the private
run/diagnostic directories. See `{arm}_training.html`, `{arm}_objective_cohorts.csv` and [{arm}
exact cases]({arm}_EXACT_CASES.md). Fixed-checkpoint loss is not historical
online/dropout-active loss. Bounds and protected-source assumptions remain unchanged.
"""
    document(out / f"P025_{arm}_S123_RESULT.md", text)
    document(
        out / f"P025_{arm}_REPLICATION_RESULT.md",
        f"# P025 {arm} replication result\n\n"
        f"Canonical report: [P025_{arm}_S123_RESULT.md](P025_{arm}_S123_RESULT.md).",
    )
    write_json(
        out / (arm + "_stage_scientific_review.json"),
        dict(
            status="PASS_" + arm + "_S123_REPORT_COMPLETE",
            at=now(),
            gate=ref(plan_path.parent / (arm + "_immediate_gate.json")),
            report=ref(out / f"P025_{arm}_S123_RESULT.md"),
            result_run_id=result["run_id"],
            no_additional_fit=True,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    arm_report(a.plan, a.arm, a.out)


if __name__ == "__main__":
    main()
