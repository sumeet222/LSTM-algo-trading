"""P024 read-only completeness checks and forecasting/optimizer diagnostics."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import digest, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_diagnostics import daily_scores
from .objective_screen_metrics import equal_weights
from .optimization_screen import RUNS, VARIANTS, ScreenLSTM
from .optimization_screen_authority import code_binding


def read_updates(path: Path) -> pd.DataFrame:
    """Preserve JSON floats exactly; pandas' fast JSON parser can round nested group values."""
    records = [json.loads(line) for line in path.read_text().splitlines()]
    if not records:
        return pd.DataFrame(
            columns=[
                "phase",
                "epoch",
                "lr",
                "weight_decay",
                "preclip_norm",
                "postclip_norm",
                "update_norm",
                "weight_norm",
                "module_preclip",
            ]
        )
    return pd.DataFrame(records)


def forecast_profile(f: pd.DataFrame) -> dict:
    """Independent weighted moments; regression is actual y on predicted y, with intercept."""
    y = f.TG20.to_numpy(dtype=np.float64)
    prediction = f.pred_original_TG20.to_numpy(dtype=np.float64)
    w = equal_weights(f.session_date_et.to_numpy())
    pmean, ymean = float(w @ prediction), float(w @ y)
    variance = float(w @ (prediction - pmean) ** 2)
    covariance = float(w @ ((prediction - pmean) * (y - ymean)))
    slope = covariance / variance if variance > 1e-30 else None
    error = prediction - y
    daily = daily_scores(f, prediction, True)
    return dict(
        rows=len(f),
        origins=f.origin_id.nunique(),
        sessions=f.session_date_et.nunique(),
        calibration_slope_y_on_prediction=slope,
        calibration_intercept=None if slope is None else ymean - slope * pmean,
        forecast_target_covariance=covariance,
        forecast_variance=variance,
        forecast_target_sd_ratio=float(np.sqrt(variance / (w @ (y - ymean) ** 2))),
        residual_quantiles=np.quantile(error, [0, 0.01, 0.05, 0.5, 0.95, 0.99, 1]).tolist(),
        top4_recall=float(daily.top4_recall.mean()),
        bottom4_recall=float(daily.bottom4_recall.mean()),
        mse_identity_lhs=float(w @ error**2 - w @ y**2),
        mse_identity_rhs=float(w @ prediction**2 - 2 * w @ (y * prediction)),
    )


def supplement(plan_path: Path, arm: str) -> None:
    plan = json.loads(plan_path.read_text())
    if plan["code"] != code_binding():
        raise ValueError("P024_FIT_CODE_CHANGED")
    i = [v.arm for v in VARIANTS].index(arm)
    v, run_id = VARIANTS[i], RUNS[i]
    gate_path = plan_path.parent / f"stage_{i + 3}_receipt.json"
    gate = json.loads(gate_path.read_text())
    if gate["status"] != "PASS_" + arm:
        raise ValueError("P024_PRIOR_SCIENTIFIC_GATE_REQUIRED")
    for r in gate["evidence"]:
        checked(r)
    result = json.loads((plan_path.parent / run_id / "run_result.json").read_text())
    out = Path(gate["diagnostics"]) / "supplement_v2"
    out.mkdir(exist_ok=False)
    records, identities = [], []
    for key in ("calibration", "refit"):
        body = torch.load(checked(result[key]), weights_only=True)
        if body["variant"] != asdict(v):
            raise ValueError("P024_CHECKPOINT_VARIANT_MISMATCH")
        model = ScreenLSTM(v)
        model.load_state_dict(body["model"])
        expected = 21057 if arm == "H64" else 14881 if arm == "L2H32" else 6433
        if sum(p.numel() for p in model.parameters()) != expected:
            raise ValueError("P024_ACTUAL_PARAMETER_COUNT")
        if model.lstm.dropout != 0 or model.dropout.p != v.head_dropout:
            raise ValueError("P024_DROPOUT_PLACEMENT")
        identities.append(
            dict(
                phase=key,
                parameters=expected,
                layers=model.lstm.num_layers,
                width=model.lstm.hidden_size,
                head_dropout=model.dropout.p,
                recurrent_interlayer_dropout=model.lstm.dropout,
            )
        )
    for key in ("calibration_stop_optimizer", "refit_final_optimizer"):
        body = torch.load(checked(result[key]), weights_only=True)
        groups = body["param_groups"]
        if len(groups) != 2 or any(g["lr"] != v.learning_rate for g in groups):
            raise ValueError("P024_ACTUAL_OPTIMIZER_LR")
        if [g["weight_decay"] for g in groups] != [v.matrix_decay, 0.0]:
            raise ValueError("P024_ACTUAL_OPTIMIZER_DECAY")
        if any(g["betas"] != (0.9, 0.999) or g["eps"] != 1e-8 for g in groups):
            raise ValueError("P024_ACTUAL_OPTIMIZER_FIXED_FIELDS")
    updates = read_updates(checked(result["optimizer_telemetry"]))
    if any(value != [v.learning_rate] * 2 for value in updates.lr):
        raise ValueError("P024_UPDATE_LR")
    if any(value != [v.matrix_decay, 0.0] for value in updates.weight_decay):
        raise ValueError("P024_UPDATE_DECAY")
    gradient = []
    for (phase, epoch), group in updates.groupby(["phase", "epoch"]):
        if not isinstance(epoch, (int, np.integer)):
            raise ValueError("P024_INTEGRAL_TELEMETRY_EPOCH")
        values = dict(
            preclip=group.preclip_norm.to_numpy(),
            postclip=group.postclip_norm.to_numpy(),
            update=group.update_norm.to_numpy(),
            weight=group.weight_norm.to_numpy(),
        )
        for name in group.iloc[0].module_preclip:
            values[name] = np.array([r[name] for r in group.module_preclip])
        for name, a in values.items():
            if not np.isfinite(a).all():
                raise ValueError("P024_NONFINITE_GRADIENT_TELEMETRY")
            gradient.append(
                dict(
                    phase=phase,
                    epoch=int(epoch),
                    quantity=name,
                    updates=len(a),
                    mean=float(a.mean()),
                    maximum=float(a.max()),
                    **{
                        f"p{int(q * 100):02d}": float(np.quantile(a, q))
                        for q in (0.01, 0.05, 0.5, 0.9, 0.95, 0.99)
                    },
                )
            )
    pd.DataFrame(gradient).to_csv(out / "gradient_quantiles.csv", index=False)
    for role in ("inner_train", "inner_validation", "refit", "development"):
        f = pd.read_parquet(Path(gate["diagnostics"]) / role / "population.parquet")
        if f.session_date_et.ge("2026-01-01").any():
            raise ValueError("P024_PROTECTED_NUMERICS_DENIED")
        profile = forecast_profile(f)
        np.testing.assert_allclose(
            profile["mse_identity_lhs"], profile["mse_identity_rhs"], rtol=1e-8, atol=1e-12
        )
        records.append(dict(role=role, arm=arm, seed=v.seed, **profile))
    pd.DataFrame(records).to_json(out / "forecast_profiles.json", orient="records", indent=2)
    write_json(out / "model_identity.json", identities)
    for r in plan["protected_refs"]:
        checked(r)
    write_json(
        plan_path.parent / (arm + "_immediate_complete.json"),
        dict(
            status="PASS_IMMEDIATE_" + arm,
            run_id=run_id,
            base_gate=ref(gate_path),
            supplemental_code=ref(Path(__file__).relative_to(Path.cwd())),
            evidence=[
                ref(out / "gradient_quantiles.csv"),
                ref(out / "forecast_profiles.json"),
                ref(out / "model_identity.json"),
            ],
            optimizer_updates=0,
            proposal_sha256=digest(plan_path),
            fit_code_unchanged=True,
            protected_numeric_access=False,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--arm", choices=[v.arm for v in VARIANTS], required=True)
    a = parser.parse_args()
    supplement(a.plan, a.arm)
