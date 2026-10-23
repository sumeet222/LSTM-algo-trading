"""P024 repair real-source zero-step check; no authority activation or optimizer updates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from .config import write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .neural_engine import batch_prediction, clip
from .neural_lifecycle import state_hash
from .objective_screen_source import scoped_view
from .optimization_screen import make_model, make_optimizer
from .optimization_screen_recovery_authority import VARIANTS, require_complete_gate
from .optimization_screen_run import Telemetry, save_reload
from .optimization_screen_supplement import read_updates
from .visualization.hf1m_long import LongStudy


def preflight(out: Path) -> None:
    require_complete_gate(out / "LRLOW_complete_verified.json", "LRLOW")
    original = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3")
    p = json.loads((original / "experiment_design.json").read_text())
    before = json.loads((original / "stage_1_preflight_final.json").read_text())
    for r in p["protected_refs"]:
        checked(r)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    view = scoped_view(LongStudy.discover(Path.cwd()), "inner_train", stage=2)
    if view.summary() != p["views"]["inner_train"]:
        raise ValueError("P024_INPUT_PARITY")
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name / "zero_step"
    private.mkdir(parents=True, exist_ok=False)
    checks = []
    with patch.object(torch.optim.AdamW, "step", side_effect=AssertionError("ZERO_STEPS_ONLY")):
        for v in VARIANTS:
            model = make_model(v)
            initial = state_hash(model)
            previous = next(r for r in before["checks"] if r["arm"] == v.arm)
            if initial != previous["initial_hash"]:
                raise ValueError("P024_INITIALIZATION_CHANGED")
            opt = make_optimizer(model, v)
            observer = Telemetry(
                model, opt, private / (v.arm + "_observer.jsonl"), "ZERO_UPDATE", 1
            )
            batch = view.batch(tuple(range(16)))
            policy = LossPolicy("T2", scale=view.source.fit["t2_scale"])
            raw = batch_prediction(model, batch)
            loss = policy.objective(raw, batch.targets, batch.origins, stock_count=20)
            loss.mean().backward()
            pre = clip(model)
            observer.pre(opt, (), {})
            observer.post(opt, (), {})
            observer.close()
            np.testing.assert_allclose(observer.records[0]["preclip_norm"], pre, rtol=2e-6)
            if observer.records[0]["update_norm"] != 0 or opt.state:
                raise ValueError("P024_NO_UPDATES_REQUIRED")
            frame = read_updates(private / (v.arm + "_observer.jsonl"))
            if frame.iloc[0].lr != [v.learning_rate] * 2:
                raise ValueError("P024_EXACT_LR_ROUNDTRIP")
            checkpoint, loaded = save_reload(
                private / (v.arm + ".pt"), model, v, dict(zero_step=True)
            )
            if state_hash(loaded) != initial or state_hash(make_model(v)) != initial:
                raise ValueError("P024_FRESH_RELOAD_IDENTITY")
            checks.append(
                dict(
                    arm=v.arm,
                    checkpoint=checkpoint,
                    initial_hash=initial,
                    finite_backward=True,
                    exact_lr_json_roundtrip=True,
                    optimizer_updates=0,
                )
            )
    write_json(
        out / "zero_step_preflight.json",
        dict(
            status="PASS_ZERO_STEP_REPAIR",
            checks=checks,
            optimizer_updates=0,
            new_starts=0,
            ledger=46,
            completed_lrlow=ref(out / "LRLOW_complete_verified.json"),
            protected_numeric_access=False,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    preflight(parser.parse_args().out)
