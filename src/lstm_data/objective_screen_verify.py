"""Read-only stage verification for completed P022 runs; never trains a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import checked, ref
from .objective_screen_loss import RUNS, model_for
from .objective_screen_recovery import code_binding, rows
from .objective_screen_run import Selector


def verify(plan_path: Path, run_id: str) -> dict:
    plan = json.loads(plan_path.read_text())
    if plan["code"] != code_binding():
        raise ValueError("P022_EXECUTION_CHANGED")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    assert [r["status"] for r in own] == ["STARTED", "CALIBRATED", "REFITTING", "COMPLETED"]
    assert own[-1]["global_started_pairs"] == 38 + RUNS.index(run_id)
    result_path = checked(own[-1]["detail"]["result"])
    result = json.loads(result_path.read_text())
    arm = result["arm"]
    epochs = json.loads(checked(result["epochs"]).read_text())
    calibration = [r for r in epochs if r["phase"] == "calibration"]
    refit = [r for r in epochs if r["phase"] == "refit"]
    assert len(calibration) == result["calibration_epochs"]
    assert len(refit) == result["refit_epochs"] == result["selector"]["selected"]
    selector = Selector()
    for row in calibration:
        validation = row["validation"]
        metric = validation["optimized_objective"] if arm == "E1" else validation["original_mse"]
        assert selector.observe(metric) == row["qualifies"]
        assert selector.selected == row["selector"]["selected"]
    assert selector.status == result["selector"]["status"]
    for row in epochs:
        epoch = row["training"]["epoch"]
        receipt = result_path.parent / "epoch_receipts" / f"{row['phase']}_{epoch:03d}.json"
        assert json.loads(receipt.read_text()) == row
        assert row["training"]["nonfinite_count"] == 0
        assert row["training"]["optimizer_steps"] == (158 if row["phase"] == "calibration" else 187)
    for stage, version in [("calibration", "inner"), ("refit", "refit")]:
        saved = torch.load(checked(result[stage]), map_location="cpu", weights_only=True)
        assert saved["binding"]["recipe"] == plan["recipes"][version]
        assert saved["binding"]["input_contract"] == plan["input_contract"]
        model = model_for(arm)
        model.load_state_dict(saved["state_dict"])
        assert all(bool(torch.isfinite(v).all()) for v in model.state_dict().values())
    for name in ["inner_train", "inner_validation", "refit"]:
        f = pd.read_parquet(checked(result["artifacts"][name + "_predictions.parquet"]))
        assert len(f) == {"inner_train": 88560, "inner_validation": 15320, "refit": 104200}[name]
        assert not f.duplicated(["origin_id", "ticker"]).any()
        assert f.ticker.tolist() == list(SYMBOLS) * (len(f) // 20)
        assert f.partition.eq(name).all() and f.session_date_et.lt("2026-01-01").all()
        version = "inner" if name.startswith("inner") else "refit"
        if arm == "E1":
            assert "pred_original_TG20" not in f
            np.testing.assert_allclose(f[["p_NEG", "p_NORMAL", "p_POS"]].sum(axis=1), 1, atol=2e-7)
        else:
            assert f.inverse_count.eq(1).all()
            np.testing.assert_allclose(
                plan["recipes"][version]["scale"] * np.sinh(f.raw_net_output),
                f.pred_original_TG20,
                rtol=3e-7,
                atol=1e-8,
            )
    batches = pd.DataFrame(
        [
            json.loads(line)
            for line in checked(result["artifacts"]["optimizer_batches.jsonl"])
            .read_text()
            .splitlines()
        ]
    )
    steps = 158 * len(calibration) + 187 * len(refit)
    assert int(batches.optimizer_step.sum()) == steps
    assert len(batches) == steps + 29 * len(calibration)
    for item in plan["protected_refs"]:
        checked(item)
    return dict(
        status="PASS_STAGE_VERIFIED",
        run_id=run_id,
        result=ref(result_path),
        calibration_epochs=len(calibration),
        refit_epochs=len(refit),
        optimizer_steps=steps,
        telemetry_records=len(batches),
        ledger=own[-1]["global_started_pairs"],
        protected_numeric_access=False,
        development_access=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-id", choices=RUNS, required=True)
    args = parser.parse_args()
    receipt = verify(args.plan, args.run_id)
    write_json(args.plan.parent / (args.run_id + "_stage_verification.json"), receipt)
    print(json.dumps(receipt))
