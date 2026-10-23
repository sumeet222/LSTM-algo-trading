"""P023 read-only collective reports and dependence-aware task comparisons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .dm_quantile_authority import rows
from .dm_quantile_loss import ARMS, RUNS
from .objective_screen_audit import month_ci
from .objective_screen_diagnostics import canonical, daily_scores
from .objective_screen_report import markdown
from .visualization.hf1m_long import LongStudy


def collective(plan_path: Path) -> None:
    p = plan_path.parent
    plan = json.loads(plan_path.read_text())
    study = LongStudy.discover(Path.cwd())
    assert [r["run_id"] for r in rows() if r["status"] == "COMPLETED"] == list(RUNS)
    out = p / "collective_v1"
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    frames = []
    differences = []
    health = []
    tail = []
    for arm, run_id in zip(ARMS, RUNS, strict=True):
        gate = json.loads((p / f"stage_{2 + ARMS.index(arm)}_gate.json").read_text())
        assert gate["status"] == "PASS_" + arm
        root = Path(gate["diagnostics"])
        assert (root / "supplement_v1/verification.json").exists()
        f = pd.read_json(root / "metrics.json")
        f["arm"] = arm
        frames.append(f)
        t = pd.read_parquet(root / "cohorts.parquet")
        t["arm"] = arm
        tail.append(t)
        result = json.loads((p / run_id / "run_result.json").read_text())
        epochs = []
        for record in result["epochs"]:
            for kind in ["training", "validation"]:
                if kind not in record:
                    continue
                x = record[kind]
                r = {k: v for k, v in x.items() if not isinstance(v, (dict, list))}
                for name in ["preclip", "postclip"]:
                    r.update({name + "_" + k: v for k, v in x.get(name, {}).items()})
                for i, value in enumerate(x["component_means"]):
                    r[f"component_{i}"] = value
                r.update(
                    arm=arm,
                    phase=record["phase"],
                    kind=kind,
                    selected=result["selector"]["selected"],
                    raw_best=result["selector"]["raw_epoch"],
                )
                epochs.append(r)
        health.extend(epochs)
        text = [
            f"# P023 {arm} result\n\n",
            f"Run `{run_id}`. Qualified epoch {result['selector']['selected']}; "
            f"raw best {result['selector']['raw_epoch']}. "
            "Fresh same-seed refit; no optimizer carryover.\n\n",
            markdown(f.loc[f.role.eq("development")]),
            "\nActual optimization history, phases and gradients:\n\n",
            markdown(pd.DataFrame(epochs)),
        ]
        (out / f"P023_{arm}_RESULT.md").write_text("".join(text))
        for role in ["inner_train", "inner_validation", "refit", "development"]:
            g = pd.read_parquet(root / role / "population.parquet")
            d = daily_scores(g, g.y_hat.to_numpy(), True).set_index("session_date_et")
            for baseline in ["HF1M-LONG-TM0-T2-S42-DEV1", "HF1M-LONG-TM0-T2-S123-DEV1", "ZERO"]:
                prediction = (
                    np.zeros(len(g))
                    if baseline == "ZERO"
                    else canonical(
                        study.prediction(baseline, role), g
                    ).pred_original_TG20.to_numpy()
                )
                b = daily_scores(g, prediction, True).set_index("session_date_et")
                for metric in ["mse", "ic"]:
                    diff = (d[metric] - b[metric]).dropna()
                    for block in [1, 2]:
                        low, high = month_ci(diff, block)
                        differences.append(
                            dict(
                                arm=arm,
                                role=role,
                                baseline=baseline,
                                metric=metric,
                                days=len(diff),
                                difference=float(diff.mean()),
                                low=low,
                                high=high,
                                block_months=block,
                                replicates=400,
                                seed=22042,
                            )
                        )
            recipe = plan["recipes"]["inner" if role.startswith("inner") else "refit"]
            if arm == "QR1":
                z = g.z.to_numpy()
                q = g[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy()
                tau = np.array([0.05, 0.5, 0.95])
                e = z[:, None] - q
                constant = z[:, None] - np.asarray(recipe["quantiles_z"])
                delta = np.maximum(tau * e, (tau - 1) * e).mean(axis=1) - np.maximum(
                    tau * constant, (tau - 1) * constant
                ).mean(axis=1)
                diff = pd.Series(delta, index=g.session_date_et).groupby(level=0).mean()
                for block in [1, 2]:
                    low, high = month_ci(diff, block)
                    differences.append(
                        dict(
                            arm=arm,
                            role=role,
                            baseline="PREFIX_CONSTANT",
                            metric="pinball",
                            days=len(diff),
                            difference=float(diff.mean()),
                            low=low,
                            high=high,
                            block_months=block,
                            replicates=400,
                            seed=22042,
                        )
                    )
    scores = pd.concat(frames, ignore_index=True)
    scores.to_json(out / "scores.json", orient="records", indent=2)
    pd.DataFrame(health).to_csv(out / "optimization.csv", index=False)
    pd.DataFrame(differences).to_csv(out / "paired_differences.csv", index=False)
    pd.concat(tail).to_parquet(out / "cohorts.parquet", index=False)
    dev = scores.loc[scores.role.eq("development")]
    regression = dev.loc[
        dev.model.isin(
            ["DM1", "QR1", "SS1", "HF1M-LONG-TM0-T2-S42-DEV1", "HF1M-LONG-TM0-T2-S123-DEV1", "ZERO"]
        )
    ]
    comparison = [
        (
            "# P023 collective comparison\n\nAll three independent seed42 arms "
            "completed. Ledger44/200; no other fits. "
            "Development183origins/3660rows/109sessions is exploratory. Inner "
            "validation selected epochs; refit is in-sample. Do not pool "
            "roles.\n\n"
        ),
        markdown(
            regression[
                [
                    "arm",
                    "model",
                    "mse",
                    "mae",
                    "daily_ic",
                    "prediction_sd",
                    "actual_sd",
                    "excess_mse",
                    "prediction_energy",
                    "twice_y_pred",
                ]
            ]
        ),
        (
            "\nQR1 rows are median forecasts; their MSE does not measure "
            "conditional-mean optimization. Proper QR1 "
            "pinball/coverage/interval scores versus weighted prefix-only "
            "quantiles:\n\n"
        ),
        markdown(dev.loc[dev.arm.eq("QR1") & dev.model.isin(["QR1", "PREFIX_CONSTANT"])]),
        "\nDM1 sign/magnitude and cancellation versus prefix-only constants:\n\n",
        markdown(dev.loc[dev.arm.eq("DM1") & dev.model.isin(["DM1", "PREFIX_CONSTANT"])]),
        (
            "\nPaired daily differences: fixed400replicate seed22042 "
            "whole-calendar-month bootstrap, with two-month sensitivity. "
            "Nearby labels/stocks are dependent and there are few development "
            "months. No significance, trading-alpha, final-test or multi-seed "
            "claim.\n\n"
        ),
        markdown(pd.DataFrame(differences).query("role == 'development'")),
        (
            "\nEach arm has full role, stock/year, tail and numerator/MAD "
            "conditional diagnostics and confidence/coverage tables. SS1 "
            "online importance-corrected risk differs from fixed-population "
            "checkpoint risk; estimator variance/exposure is not a population "
            "reweighting. Bigger outputs, smoother losses or reduced tail "
            "share are not success criteria. No model is automatically "
            "promoted. Any seed123 replication requires a new package. E1 "
            "remains independent.\n"
        ),
    ]
    (out / "P023_COLLECTIVE_COMPARISON.md").write_text("".join(comparison))
    tails = [
        (
            "# P023 actual-objective extreme-loss attribution\n\nFixed refit "
            "checkpoints, dropoutOFF,104200rows. Historical online dropoutON "
            "objectives remain separately logged. DM1 splits "
            "signCE/magnitudeMSE; QR1 mean three pinballs; SS1 natural "
            "equal-session zMSE here versus importance-corrected sampled "
            "losses online.\n\n"
        )
    ]
    for arm in ARMS:
        f = pd.concat(tail)
        g = f.loc[
            f.arm.eq(arm)
            & f.role.eq("refit")
            & f.cohort.isin(
                [
                    "ALL",
                    "TARGET_RANK_TOP1",
                    "TARGET_RANK_TOP5",
                    "NUMERATOR_RANK_TOP5",
                    "MAD_BOTTOM5",
                    "BOTH_5",
                    "NUM_ONLY_5",
                    "MAD_ONLY_5",
                    "NEITHER_5",
                    "RANGE_ABS_0.99",
                    "RANGE_ABS_0.95",
                ]
            )
        ]
        tails.extend([f"\n## {arm}\n\n", markdown(g)])
    tails.append(
        (
            "\nRaw/asinh ranked memberships match exactly. MAD cohorts rank "
            "unique origins before20stock expansion; intersections/complements"
            " are retained in cohort Parquets. Ranges use fitting maxima "
            "(.99/.95) and frozen side-specific cutoffs for later roles, not "
            "percentile row counts. Four mechanism groups partition exactly; "
            "overlapping groups must not be summed. RMSE is non-additive. Full"
            " population component allocations/weights/source QA, all20return "
            "vectors,48+4candles and48×16features are in each immediate "
            "diagnostic tree and supplementary witness set. All data remain "
            "private.\n"
        )
    )
    (out / "P023_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md").write_text("".join(tails))
    write_json(
        p / "stage_5_gate.json",
        dict(
            status="PASS_COLLECTIVE",
            ledger=44,
            output=str(out),
            protected_numeric_access=False,
            model_starts=0,
            optimizer_steps=0,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    a = p.parse_args()
    collective(a.plan)
