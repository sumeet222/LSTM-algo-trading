"""Read-only P023 conditional/task scores, sampler exposure and extra source witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .dm_quantile_cases import exact_cases
from .dm_quantile_diagnostics import metrics
from .hf1m_ft16_loader import load_model_input
from .hf1m_training_data import TrainingView
from .objective_screen_attribution import cohort_masks
from .objective_screen_metrics import equal_weights
from .visualization.hf1m_long import LongStudy


def supplement(plan_path: Path, arm: str, diagnostics: Path) -> None:
    plan = json.loads(plan_path.read_text())
    study = LongStudy.discover(Path.cwd())
    records = []
    out = diagnostics / "supplement_v1"
    out.mkdir(exist_ok=False)
    for role in ["inner_train", "inner_validation", "refit", "development"]:
        version = "inner" if role.startswith("inner") else "refit"
        recipe = plan["recipes"][version]
        f = pd.read_parquet(diagnostics / role / "population.parquet")
        w = equal_weights(f.session_date_et.to_numpy())
        training = pd.read_parquet(
            diagnostics / ("inner_train" if version == "inner" else "refit") / "population.parquet"
        )
        masks, _ = cohort_masks(f, training)
        for name, mask in masks.items():
            if name not in [
                "BOTH_5",
                "NUM_ONLY_5",
                "MAD_ONLY_5",
                "NEITHER_5",
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
            ]:
                continue
            if mask.any():
                mass = w[mask].sum()
                error = (f.y_hat.to_numpy() - f.TG20.to_numpy())[mask]
                record = dict(
                    role=role,
                    group=name,
                    rows=int(mask.sum()),
                    weight_mass=mass,
                    mse=float(w[mask] @ (error**2) / mass),
                    mae=float(w[mask] @ abs(error) / mass),
                )
                if arm == "QR1":
                    z = f.z.to_numpy()[mask]
                    q = f[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy()[mask]
                    e = z[:, None] - q
                    tau = np.array([0.05, 0.5, 0.95])
                    record.update(
                        pinball=float(
                            w[mask] @ np.maximum(tau * e, (tau - 1) * e).mean(axis=1) / mass
                        ),
                        coverage=(w[mask] @ (z[:, None] <= q) / mass).tolist(),
                    )
                records.append(record)
        for field in ["ticker", "year"]:
            frame = f.assign(year=f.session_date_et.str[:4])
            for name, g in frame.groupby(field):
                gw = equal_weights(g.session_date_et.to_numpy())
                error = g.y_hat.to_numpy() - g.TG20.to_numpy()
                r = dict(
                    role=role,
                    group=field + ":" + str(name),
                    rows=len(g),
                    mse=float(gw @ (error**2)),
                    mae=float(gw @ abs(error)),
                )
                if field == "year":
                    r.update(metrics(g, arm, recipe))
                if arm == "QR1":
                    z = g.z.to_numpy()
                    q = g[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy()
                    e = z[:, None] - q
                    tau = np.array([0.05, 0.5, 0.95])
                    r.update(
                        pinball=float(gw @ np.maximum(tau * e, (tau - 1) * e).mean(axis=1)),
                        coverage=(gw @ (z[:, None] <= q)).tolist(),
                    )
                records.append(r)
        if arm == "DM1":
            c = f.TG20.ge(0).to_numpy()
            prob = f.p.to_numpy()
            cal = []
            bins = np.minimum((prob * 10).astype(int), 9)
            for b in range(10):
                m = bins == b
                mass = w[m].sum()
                cal.append(
                    dict(
                        bin=b,
                        mass=float(mass),
                        rows=int(m.sum()),
                        confidence=float(w[m] @ prob[m] / mass) if mass else None,
                        frequency=float(w[m] @ c[m] / mass) if mass else None,
                    )
                )
            write_json(
                out / (role + "_sign_calibration.json"),
                dict(
                    reliability=cal,
                    true_signed_counts=f.TG20.apply(np.sign).value_counts().to_dict(),
                    predicted_positive=int((prob >= 0.5).sum()),
                ),
            )
    pd.DataFrame(records).to_json(out / "conditional_scores.json", orient="records", indent=2)
    f = pd.read_parquet(diagnostics / "refit/population.parquet")
    masks, _ = cohort_masks(f, f)
    extra = {}
    for name in ["MAD_ONLY_5", "BOTH_5"]:
        g = f.loc[masks[name]]
        if len(g):
            extra[int(str(g.total.idxmax()))] = "representative " + name
    view = TrainingView(
        load_model_input(Path(plan["input_contract"]["path"]), split="refit", fit_version="refit"),
        "refit",
    )
    witness = out / "witnesses"
    witness.mkdir()
    check = exact_cases(
        study, view, f, pd.DataFrame(), arm, plan["recipes"]["refit"], witness, extra
    )
    if arm == "SS1":
        root = Path(plan["private_root"]) / f"HF1M-LONG-TM0-{arm}-S42-DEV1"
        b = pd.DataFrame(
            [json.loads(line) for line in (root / "batches.jsonl").read_text().splitlines()]
        )
        exposure = []
        inner_view = TrainingView(
            load_model_input(
                Path(plan["input_contract"]["path"]), split="inner_train", fit_version="inner"
            ),
            "inner_train",
        )
        date_cache = {"inner": np.asarray(inner_view.sessions), "refit": np.asarray(view.sessions)}
        for (role, epoch), g in b.loc[b.optimizer_step].groupby(["role", "epoch"]):
            version = "inner" if role == "inner_train" else "refit"
            recipe = plan["recipes"][version]
            ids = np.concatenate(g.sampled_positions.to_list())
            iw = np.concatenate(g.importance.to_list())
            tail = np.isin(ids, recipe["tail_positions"])
            dates = date_cache[version]
            for year in np.unique([d[:4] for d in dates]):
                year_mask = np.array([dates[i][:4] == year for i in ids])
                exposure.append(
                    dict(
                        role=role,
                        epoch=int(str(epoch)),
                        year=year,
                        draws=int(np.sum([dates[i][:4] == year for i in ids])),
                        tail_draws=int((tail & year_mask).sum()),
                        unique_sessions_epoch=len(set(ids.tolist())),
                        duplicates_epoch=len(ids) - len(set(ids.tolist())),
                        ESS_epoch=float(iw.sum() ** 2 / (iw**2).sum()),
                        weighted_objective_epoch=float(
                            np.average(g.objective, weights=g.sampled_positions.map(len))
                        ),
                        importance_mean_epoch=float(iw.mean()),
                    )
                )
        pd.DataFrame(exposure).to_csv(out / "sampler_exposure.csv", index=False)
    write_json(
        out / "verification.json",
        dict(
            status="PASS_SUPPLEMENT",
            case_checks=check,
            additional_mechanism_cases=extra,
            protected_numeric_access=False,
            optimizer_steps=0,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--diagnostics", type=Path, required=True)
    a = p.parse_args()
    supplement(a.plan, a.arm, a.diagnostics)
