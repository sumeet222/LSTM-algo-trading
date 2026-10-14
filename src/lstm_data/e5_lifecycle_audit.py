"""Actual fabricated E5 two-pass integration after a SHA-bound v2 health PASS."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from dataclasses import replace
from pathlib import Path
from typing import Callable

import pandas as pd
import torch

from .baseline_fit import prepare
from .baseline_ridge import fitting_origins, windows
from .config import digest, fingerprint, write_json
from .e5_fixture_v2 import FIXTURE, fixture, forecast_input, later_history
from .neural_artifacts import load_checkpoint
from .neural_audit import peak_memory
from .neural_data import data_identity
from .neural_lifecycle import forecast_scores, run_pair, state_hash
from .neural_market import market_preparation_identity
from .neural_models import create_model
from .peer_neural import e5_input


def run(out: Path) -> dict:
    """One genuine D6g pair; only immutable final refit can forecast, never trade."""
    health_path = out / "extension_1024" / "health_v2_result.json"
    health = json.loads(health_path.read_text())
    config = out / "extension_1024" / "fixture_v2_config.json"
    if health["status"] != "PASS" or not all(health["checks"].values()):
        raise ValueError("CREDIBLE_E5_HEALTH_PASS_REQUIRED")
    if digest(config) != health["config_sha"]:
        raise ValueError("HEALTH_CONFIGURATION_SHA_CHANGED")
    write_json(
        out / "lifecycle_reservation.json",
        {
            "health_sha": digest(health_path),
            "config_sha": digest(config),
            "source_code": digest(Path(__file__).with_name("e5_fixture_v2.py")),
            "audit_code": digest(Path(__file__)),
            "actual_monitor": "ACTUAL_INNER_MSE",
            "seed": 42,
            "architecture": "E5",
            "max_epochs": [60, 60],
            "scientific_pairs": 0,
            "forecast_minutes": 30,
            "replacement_scope": "fresh source-bound preparation/view, no stale weights migration",
        },
    )
    start = time.monotonic()
    data, history, guard = fixture()
    fitted_at = pd.Timestamp("2023-07-01T04:00Z")
    pair = run_pair(
        data,
        "WF1",
        fitted_at,
        guard,
        out / "seed42_pair",
        architecture="E5",
        market_history=history,
    )
    if pair.evidence["selection_monitor"] != "ACTUAL_INNER_MSE":
        raise ValueError("MOCK_MONITOR_FORBIDDEN")
    if pair.evidence["calibration_initial_hash"] != pair.evidence["refit_initial_hash"]:
        raise ValueError("FRESH_SEED_RESET_REQUIRED")
    selected = create_model("E5")
    epoch, _ = load_checkpoint(
        pair.checkpoint.with_name("calibration_selected.pt"),
        selected,
        pair.pair,
        "CALIBRATION_SELECTED",
    )
    assert epoch == pair.evidence["selector"]["selected"]
    assert state_hash(selected) == pair.evidence["calibration_selected_hash"]
    row = forecast_input(data)
    later = later_history(row, history)
    forecast = forecast_scores(pair, row, guard, market_history=later)
    repeat = forecast_scores(pair, row, guard, market_history=later)
    assert forecast == repeat and len(forecast.scores) == 5
    negatives = {}

    def deny(name: str, call: Callable[[], object]) -> None:
        try:
            call()
        except ValueError as error:
            negatives[name] = str(error)
        else:
            raise ValueError("EXPECTED_CHECKPOINT_OR_SOURCE_DENIAL:" + name)

    deny(
        "calibration_as_final",
        lambda: load_checkpoint(
            pair.checkpoint.with_name("calibration_selected.pt"),
            create_model("E5"),
            pair.pair,
            "REFIT_FINAL",
        ),
    )
    deny(
        "wrong_family",
        lambda: load_checkpoint(
            pair.checkpoint,
            create_model("MC0"),
            pair.pair,
            "REFIT_FINAL",
            fit_binding=pair.evidence["refit_preparation"],
        ),
    )
    for field in (
        "universe",
        "source_features_data",
        "preprocess",
        "code",
        "model_optimizer_selection",
    ):
        stale = replace(pair.pair, **{field: "SYN:STALE"})
        deny(
            "stale_" + field,
            lambda stale=stale: load_checkpoint(
                pair.checkpoint,
                create_model("E5"),
                stale,
                "REFIT_FINAL",
                fit_binding=pair.evidence["refit_preparation"],
            ),
        )
    # A bounded disposable checkpoint copy, never mutate the authoritative file.
    with tempfile.TemporaryDirectory(prefix="e5_v2_tamper_") as folder:
        bad = Path(folder) / pair.checkpoint.name
        bad.write_bytes(pair.checkpoint.read_bytes() + b"CORRUPTED")
        bad.with_suffix(".manifest.json").write_bytes(
            pair.checkpoint.with_suffix(".manifest.json").read_bytes()
        )
        deny(
            "tampered",
            lambda: load_checkpoint(
                bad,
                create_model("E5"),
                pair.pair,
                "REFIT_FINAL",
                fit_binding=pair.evidence["refit_preparation"],
            ),
        )

    # Rebind immutable raw tuples rather than copying/downloading raw history.
    version = FIXTURE + ":SOURCE_REPLACEMENT"
    source = fingerprint([version, "FABRICATED_FEATURE_SOURCE"])
    replacement = replace(
        data,
        origins=tuple(
            replace(
                origin,
                inputs=replace(
                    origin.inputs,
                    input_id=version + ":" + origin.inputs.input_id,
                    stock=replace(origin.inputs.stock, source_binding=source),
                ),
            )
            for origin in data.origins
        ),
        stock_records=tuple(
            replace(r, source_binding=source, source_id=version + ":" + r.source_id)
            for r in data.stock_records
        ),
        floor_records=tuple(
            replace(r, source_binding=source, source_id=version + ":" + r.source_id)
            for r in data.floor_records
        ),
    )
    assert all(
        a.inputs.stock.raw_values is b.inputs.stock.raw_values
        for a, b in zip(data.origins, replacement.origins)
    )
    changed_row = replace(
        row, input_id=version + ":" + row.input_id, stock=replace(row.stock, source_binding=source)
    )
    deny(
        "old_prep_new_source_forecast",
        lambda: forecast_scores(pair, changed_row, guard, market_history=later),
    )
    _, _, full = windows("WF1", fitted_at)
    accepted, _ = fitting_origins(replacement.origins, replacement.universe, full)
    rebuilt = prepare(
        replacement, full, accepted, market=True, permission=guard, allow_synthetic=True
    )
    assert market_preparation_identity(rebuilt) != pair.evidence["refit_preparation"]
    rebuilt = rebuilt.with_market_history(
        history.extend(later).vectors, guard, allow_synthetic=True
    )
    replacement_values, replacement_input = e5_input(
        changed_row, rebuilt, history.extend(later), guard
    )
    assert tuple(replacement_values.shape) == (5, 48, 23)
    changed_pair = replace(
        pair.pair,
        source_features_data=data_identity(replacement),
        preprocess=market_preparation_identity(rebuilt),
    )
    deny(
        "old_checkpoint_new_source",
        lambda: load_checkpoint(
            pair.checkpoint,
            create_model("E5"),
            changed_pair,
            "REFIT_FINAL",
            fit_binding=market_preparation_identity(rebuilt),
        ),
    )
    # Numerical content alone changes the data identity even without a version change.
    first = data.origins[0]
    raw = first.inputs.stock.raw_values
    cell = raw[0][0][0]
    if cell is None:
        raise ValueError("COMPLETE_SOURCE_CONTENT_REQUIRED")
    changed_cell = ((cell + 0.1,) + raw[0][0][1:],) + raw[0][1:]
    mutated = replace(
        first,
        inputs=replace(
            first.inputs, stock=replace(first.inputs.stock, raw_values=(changed_cell,) + raw[1:])
        ),
    )
    content_changed = replace(data, origins=(mutated,) + data.origins[1:])
    assert data_identity(content_changed) != data_identity(data)
    result = {
        "status": "E5_ACTUAL_D6G_INTEGRATION_PASS",
        "pair": pair.evidence,
        "selected_audit_reload_epoch": epoch,
        "selected_reload_state_exact": True,
        "forecast": {
            "id": forecast.forecast_id,
            "symbols": forecast.universe.symbols,
            "universe": forecast.universe.universe_id,
            "scores": forecast.scores,
            "input": row.input_id,
            "cutoff": row.plan.cutoff.isoformat() if row.plan.cutoff is not None else None,
            "repeat_exact": True,
            "label_or_exit_input": False,
            "trading_replay": False,
        },
        "negative_cases": negatives,
        "replacement": {
            "source_version": version,
            "raw_tuples_shared": True,
            "new_source_identity": data_identity(replacement),
            "new_preparation": market_preparation_identity(rebuilt),
            "new_input_identity": replacement_input,
            "input_shape": [5, 48, 23],
            "numerical_content_change_invalidates": True,
            "fresh_replacement_model": "NOT_FITTED; new source requires fresh pair",
            "new_prep_and_input_built": True,
        },
        "seconds": time.monotonic() - start,
        "peak_memory": peak_memory(),
        "device": "cpu",
        "cpu_threads": 1,
        "mps_used": False,
        "real_pairs": "0/40",
    }
    write_json(out / "lifecycle_evidence.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    print(run(args.out)["status"])


if __name__ == "__main__":
    main()
