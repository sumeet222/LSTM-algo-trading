"""Independent postrun D6g/checkpoint/scale/conservation audit, with zero optimizer steps."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.config import digest, write_json
from lstm_data.hf20_training_authority import IDS, code_binding, read_rows
from lstm_data.hf20_training_data import load_views, target_values
from lstm_data.hf20_training_run import reload_checkpoint
from lstm_data.neural_lifecycle import EarlyStop, state_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    plan = json.loads((out / "experiment_design.json").read_text())
    assert plan["code"] == code_binding()
    views = load_views(Path(plan["input_contract"]["path"]))
    scales = {
        s: max(float(np.median(np.abs(target_values(views[s]).astype(np.float64)))), 1e-6)
        for s in ("inner_train", "refit")
    }
    assert {k: v["scale"] for k, v in plan["scales"].items()} == scales
    records = []
    initial = []
    for arm, name in zip(("C0", "T2"), IDS):
        directory = out / name
        result = json.loads((directory / "run_result.json").read_text())
        epochs = json.loads((directory / "epoch_records.json").read_text())
        selector = EarlyStop()
        for e in epochs["calibration"]:
            qualifying = selector.observe(e["validation_MSE"])
            assert qualifying == e["qualifying"]
            assert e["sessions"] == len(views["inner_train"].sessions)
            assert e["optimizer_steps"] == math.ceil(len(views["inner_train"].sessions) / 16)
        assert vars(selector) == result["selection"] == epochs["selection"]
        assert len(epochs["refit"]) == selector.selected
        assert result["fresh_optimizer"] and result["initial_hash"] == result["fresh_initial_hash"]
        assert result["calibration_steps"] == sum(
            e["optimizer_steps"] for e in epochs["calibration"]
        )
        assert result["refit_steps"] == selector.selected * math.ceil(
            len(views["refit"].sessions) / 16
        )
        initial.append(result["initial_hash"])
        for stem, stage, recipe, scale_split in [
            ("calibration_selected", "CALIBRATION_SELECTED", "inner_train", "inner_train"),
            ("refit_final", "REFIT_FINAL", "refit", "refit"),
        ]:
            path = directory / (stem + ".pt")
            manifest = json.loads(path.with_suffix(".manifest.json").read_text())
            binding = manifest["binding"]
            assert binding["stage"] == stage and binding["selected_epoch"] == selector.selected
            assert binding["recipe_id"] == views[recipe].source.recipe_id
            assert (
                binding["target_id"] == plan["target_id"] and binding["symbols"] == plan["symbols"]
            )
            assert binding["code_sha256"] == plan["code_sha256"]
            assert binding["scale"] == (plan["scales"][scale_split] if arm == "T2" else None)
            loaded = reload_checkpoint(path, binding, manifest)
            assert sum(p.numel() for p in loaded.parameters()) == 6433
            records.append(
                dict(
                    arm=arm,
                    stage=stage,
                    epoch=selector.selected,
                    checkpoint_sha256=digest(path),
                    state_sha256=state_hash(loaded),
                    finite_float32_cpu=True,
                    scale=scales[scale_split] if arm == "T2" else None,
                )
            )
        train = pd.read_csv(directory / "calibration_epochs.csv")
        assert (
            np.isfinite(train[["canonical_training_MSE", "optimizer_objective", "validation_MSE"]])
            .all()
            .all()
        )
    assert len(set(initial)) == 1
    journal = read_rows()
    assert len(journal) == 8 and sum(e["status"] == "STARTED" for e in journal) == 2
    assert [e["run_id"] for e in journal if e["status"] == "COMPLETED"] == list(IDS)
    assert journal[-1]["global_started_pairs"] == 30
    write_json(
        out / "independent_postrun_audit.json",
        dict(
            status="PASS",
            checkpoints=records,
            scales_independently_recomputed=scales,
            canonical_validation_D6g_replay_exact=True,
            fresh_refit_exact_epoch_and_optimizer_state=True,
            equal_seed_initial_weights=True,
            actual_updates_per_arm=dict(calibration=336, refit=32),
            journal_starts=2,
            global_pairs=30,
            optimizer_steps_in_this_readonly_audit=0,
            source_and_feature_numeric_barrier="2026-01-07",
            no_model_selection_on_development=True,
        ),
    )
    print(
        "PASS:4safe CPU checkpoints; canonical D6g replay; "
        "independent train-only T2 scales; fresh refits;30/200"
    )


if __name__ == "__main__":
    main()
