"""P023 immediate read-only verification, proper scores and actual-objective attribution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import fingerprint, write_json
from .dm_quantile_authority import code_binding, rows
from .dm_quantile_loss import ARMS, RUNS, terms
from .hf1m_ft16_loader import load_model_input
from .hf1m_ft16_source import checked, ref
from .hf1m_training_data import TrainingView
from .objective_screen_attribution import cohort_masks, cohort_table
from .objective_screen_diagnostics import canonical, daily_scores, exact_cases
from .objective_screen_metrics import equal_weights, regression
from .objective_screen_run import Selector
from .objective_screen_source import ordered_targets
from .visualization.hf1m_long import LongStudy


def metrics(f: pd.DataFrame, arm: str, recipe: dict) -> dict:
    y = f.TG20.to_numpy(dtype=float)
    z = np.arcsinh(y / recipe["scale"])
    w = equal_weights(f.session_date_et.to_numpy())
    result = regression(y, f.y_hat.to_numpy(dtype=float), f.session_date_et.to_numpy())
    result["z_correlation"] = (
        float(np.corrcoef(z, f.z_hat)[0, 1]) if np.std(f.z_hat.to_numpy()) > 1e-15 else float("nan")
    )
    result["near_zero_z_fraction"] = float(w @ (abs(f.z_hat.to_numpy()) < 0.05))
    if arm == "DM1":
        c = z >= 0
        p = f.p.to_numpy(dtype=float)
        magnitude = np.where(c, f.mu_positive, f.mu_negative)
        ce = -c.astype(float) * np.log(np.maximum(p, 1e-15))
        ce -= (~c) * np.log(np.maximum(1 - p, 1e-15))
        result.update(
            sign_CE=float(w @ ce),
            sign_Brier=float(w @ ((p - c) ** 2)),
            binary_sign_hit=float(w @ ((p >= 0.5) == c)),
            exact_zero_rows=int((y == 0).sum()),
            magnitude_mse=float(w @ ((magnitude - abs(z)) ** 2)),
            magnitude_mae=float(w @ abs(magnitude - abs(z))),
            cancellation_fraction=float(
                w @ ((abs(p - 0.5) < 0.05) & (abs(f.mu_positive - f.mu_negative) < 0.1))
            ),
            probability_mean=float(w @ p),
        )
        for name, mask in [("positive", c), ("negative", ~c)]:
            result["magnitude_MSE_" + name] = float(
                w[mask] @ ((magnitude[mask] - abs(z[mask])) ** 2) / w[mask].sum()
            )
    if arm == "QR1":
        q = f[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
        error = z[:, None] - q
        tau = np.array([0.05, 0.5, 0.95])
        pin = np.maximum(tau * error, (tau - 1) * error)
        assert (q[:, 0] <= q[:, 1]).all() and (q[:, 1] <= q[:, 2]).all()
        interval = (
            q[:, 2] - q[:, 0] + 20 * np.maximum(q[:, 0] - z, 0) + 20 * np.maximum(z - q[:, 2], 0)
        )
        result.update(
            pinball=float(w @ pin.mean(axis=1)),
            pinball_by_quantile=(w @ pin).tolist(),
            coverage=(w @ (z[:, None] <= q)).tolist(),
            interval_coverage=float(w @ ((z >= q[:, 0]) & (z <= q[:, 2]))),
            interval_width=float(w @ (q[:, 2] - q[:, 0])),
            interval_score=float(w @ interval),
            point_forecast="conditional median; MSE descriptive, not conditional-mean optimization",
        )
    return result


def allocation(f: pd.DataFrame, arm: str, recipe: dict) -> pd.DataFrame:
    f = f.copy()
    days, di = np.unique(f.session_date_et.to_numpy().reshape(-1, 20)[:, 0], return_inverse=True)
    slots = pd.Series(di).groupby(di).cumcount().to_numpy().copy()
    y = torch.zeros((len(days), 2, 20))
    mask = torch.zeros((len(days), 2), dtype=torch.bool)
    y[di, slots] = torch.tensor(f.TG20.to_numpy().reshape(-1, 20).copy(), dtype=torch.float32)
    mask[di, slots] = True
    raw = torch.zeros((*y.shape, 3) if arm != "SS1" else y.shape)
    values = f[["raw_0", "raw_1", "raw_2"]].to_numpy() if arm != "SS1" else f.raw_0.to_numpy()
    raw[di, slots] = torch.tensor(
        values.reshape(-1, 20, 3) if arm != "SS1" else values.reshape(-1, 20), dtype=torch.float32
    )
    t = terms(raw, y, mask, arm, recipe["scale"])
    f["raw"] = t["loss"][di, slots].detach().numpy().reshape(-1)
    f["ordinary_weight"] = equal_weights(f.session_date_et.to_numpy())
    f["normalized_weight"] = f.ordinary_weight
    f["coefficient"] = 1.0
    f["pointwise"] = f.raw * f.ordinary_weight
    f["pairwise"] = 0.0
    f["total"] = f.pointwise
    f["equivalent_row_loss"] = f.raw
    f["z"] = np.arcsinh(f.TG20 / recipe["scale"])
    comp = t["components"][di, slots].detach().numpy().reshape(len(f), -1)
    for k in range(comp.shape[1]):
        f[f"component_{k}"] = comp[:, k] * f.ordinary_weight / (3 if arm == "QR1" else 1)
    np.testing.assert_allclose(
        f[[c for c in f if str(c).startswith("component_")]].sum(axis=1),
        f.total,
        rtol=3e-7,
        atol=1e-10,
    )
    # Independent NumPy formulas, including exact same float32 supervision.
    z = np.arcsinh(f.TG20.to_numpy(dtype=np.float32) / np.float32(recipe["scale"])).astype(float)
    a = values.astype(float)
    if arm == "DM1":
        c = z >= 0
        mu = np.where(c, np.logaddexp(0, a[:, 1]), np.logaddexp(0, a[:, 2]))
        expected = np.logaddexp(0, a[:, 0]) - c * a[:, 0] + (mu - abs(z)) ** 2
    elif arm == "QR1":
        q = np.stack(
            [a[:, 0] - np.logaddexp(0, a[:, 1]), a[:, 0], a[:, 0] + np.logaddexp(0, a[:, 2])],
            axis=1,
        )
        e = z[:, None] - q
        tau = np.array([0.05, 0.5, 0.95])
        expected = np.maximum(tau * e, (tau - 1) * e).mean(axis=1)
    else:
        expected = (z - a) ** 2
    np.testing.assert_allclose(f.raw, expected, rtol=3e-5, atol=2e-6)
    return f


def run(plan_path: Path, arm: str, out: Path) -> None:
    plan = json.loads(plan_path.read_text())
    assert plan["code"] == code_binding()
    run_id = RUNS[ARMS.index(arm)]
    history = [r for r in rows() if r["run_id"] == run_id]
    assert history[-1]["status"] == "COMPLETED"
    result_path = checked(history[-1]["detail"]["result"])
    r = json.loads(result_path.read_text())
    selector = Selector()
    for row in r["epochs"]:
        if row["phase"] == "calibration":
            v = row["validation"]
            value = v["optimized_objective"] if arm == "QR1" else v["original_mse"]
            assert selector.observe(value) == row["qualifies"]
        receipt = (
            result_path.parent
            / "epoch_receipts"
            / f"{row['phase']}_{row['training']['epoch']:03d}.json"
        )
        assert fingerprint(json.loads(receipt.read_text())) == fingerprint(row)
    assert selector.selected == r["selector"]["selected"]
    for key in ["calibration", "refit"]:
        checked(r[key])
        torch.load(checked(r[key]), weights_only=True)
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    study = LongStudy.discover(Path.cwd())
    all_metrics = []
    tables = []
    training = {}
    private = Path(plan["private_root"]) / run_id
    for role in ["inner_train", "inner_validation", "refit", "development"]:
        version = "inner" if role.startswith("inner") else "refit"
        recipe = plan["recipes"][version]
        view = TrainingView(
            load_model_input(Path(plan["input_contract"]["path"]), split=role, fit_version=version),
            role,
        )
        target = ordered_targets(view)
        f = canonical(pd.read_parquet(private / (role + ".parquet")), target)
        if role in ["inner_train", "refit"]:
            training[version] = target
        f["raw_net_output"] = f.z_hat
        f["pred_original_TG20"] = f.y_hat
        np.testing.assert_allclose(
            f.y_hat, recipe["scale"] * np.sinh(f.z_hat), rtol=5e-7, atol=1e-7
        )
        quality = study.targets(role)
        extra = [c for c in quality if c not in f]
        f = f.merge(
            quality[["origin_id", "ticker"] + extra],
            on=["origin_id", "ticker"],
            validate="one_to_one",
        )
        f["run_id"] = run_id
        f = allocation(f, arm, recipe)
        dest = out / role
        dest.mkdir()
        f.to_parquet(dest / "population.parquet", index=False)
        m = metrics(f, arm, recipe)
        all_metrics.append(dict(model=arm, role=role, **m))
        write_json(dest / "metrics.json", m)
        d = daily_scores(f, f.y_hat.to_numpy(), True)
        d.to_parquet(dest / "daily.parquet", index=False)
        masks, thresholds = cohort_masks(f, training[version])
        table = cohort_table(f, masks, thresholds)
        table["role"] = role
        tables.append(table)
        write_json(dest / "thresholds.json", thresholds)
        if role == "refit":
            exact_cases(study, view, f, pd.DataFrame(), arm, recipe, dest)
        for baseline in [
            "HF1M-LONG-TM0-T2-S42-DEV1",
            "HF1M-LONG-TM0-T2-S123-DEV1",
            "ZERO",
            "PREFIX_CONSTANT",
        ]:
            g = f.copy()
            if baseline == "ZERO":
                g["y_hat"] = 0.0
            elif baseline == "PREFIX_CONSTANT":
                if arm == "DM1":
                    g["p"] = recipe["sign_prior"]
                    g["mu_positive"] = recipe["magnitude_positive"]
                    g["mu_negative"] = recipe["magnitude_negative"]
                    g["z_hat"] = g.p * g.mu_positive - (1 - g.p) * g.mu_negative
                elif arm == "QR1":
                    for j, name in enumerate(["05", "50", "95"]):
                        g["quantiles_z_" + name] = recipe["quantiles_z"][j]
                    g["z_hat"] = recipe["quantiles_z"][1]
                else:
                    g["z_hat"] = 0.0
                g["y_hat"] = recipe["scale"] * np.sinh(g.z_hat)
            else:
                b = canonical(study.prediction(baseline, role), target)
                g["y_hat"] = b.pred_original_TG20.to_numpy()
            bm = (
                metrics(g, arm, recipe)
                if baseline == "PREFIX_CONSTANT"
                else regression(g.TG20.to_numpy(), g.y_hat.to_numpy(), g.session_date_et.to_numpy())
            )
            all_metrics.append(dict(model=baseline, role=role, **bm))
    pd.DataFrame(all_metrics).to_json(out / "metrics.json", orient="records", indent=2)
    pd.concat(tables).to_parquet(out / "cohorts.parquet", index=False)
    for item in plan["protected_refs"]:
        checked(item)
    # Only now can the following authorized arm start.
    write_json(
        plan_path.parent / f"stage_{2 + ARMS.index(arm)}_gate.json",
        dict(
            status="PASS_" + arm,
            run=ref(result_path),
            diagnostics=str(out),
            selector_replayed=True,
            all_roles=4,
            objective_numpy_oracle="PASS",
            source_preserved=True,
            protected_numeric_access=False,
        ),
    )
    (plan_path.parent / f"stage_{2 + ARMS.index(arm)}_review.md").write_text(
        f"# {arm} PASS\n\nFit and immediate four-role mathematical diagnostics passed. "
        f"No promotion; development exploratory. See {out}/metrics.json and cohorts.parquet.\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--arm", choices=ARMS, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    run(a.plan, a.arm, a.out)
