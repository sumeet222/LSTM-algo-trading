"""Hermetic synthetic G5 entry point. No empirical dataset or provider arguments."""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd
import torch

from .baseline_fit import FitData
from .baseline_fixtures import feature_input, ridge_data
from .config import fingerprint, write_json
from .labels import UNIVERSE
from .ledger import guard_operation, pair_budget, read_ledger
from .neural_artifacts import MODE
from .neural_data import data_identity
from .neural_engine import SharedLSTM, seed_all, session_losses
from .neural_lifecycle import EarlyStop, forecast_scores, run_pair
from .p3_domain import Permission, UniverseSpec


def peak_memory() -> dict:
    """Portable optional peak measurement; units differ between Darwin and Linux."""
    try:
        import resource
    except ImportError:
        return {"bytes": None, "reason": "resource unavailable on this platform"}
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {"bytes": int(value if sys.platform == "darwin" else value * 1024)}


def synthetic_data(
    universe: UniverseSpec, version: str = "SYN:PLANTED_A", *, base: FitData | None = None,
) -> FitData:
    """Fabricated FT0 signal with existing synthetic TG0 labels; no indicator math."""
    if not version.startswith("SYN:"):
        raise ValueError("FABRICATED_SOURCE_VERSION_REQUIRED")
    data = ridge_data(universe) if base is None else base
    if data.universe != universe or data.basis != "SYNTHETIC":
        raise ValueError("SYNTHETIC_SAME_UNIVERSE_FIXTURE_REQUIRED")
    source = fingerprint([version, universe.universe_id])
    raw = tuple(tuple(tuple(float(i - 2) if f == 0 else 0.0 for f in range(16))
                      for _ in range(48)) for i in range(5))
    origins = tuple(replace(
        row, inputs=replace(row.inputs, stock=replace(row.inputs.stock,
                                                     raw_values=raw, source_binding=source))
    ) for row in data.origins)
    records = tuple(replace(
        record, value=float(UNIVERSE.index(record.symbol) - 2) if record.kind == "M1"
        else record.value, source_binding=source, source_id=version + ":" + record.source_id,
    ) for record in data.stock_records)
    floors = tuple(replace(record, source_binding=source,
                           source_id=version + ":" + record.source_id)
                   for record in data.floor_records)
    return replace(data, origins=origins, stock_records=records, floor_records=floors)


def audit(out: Path, mode: str = MODE) -> dict:
    if mode != MODE or out.exists():
        raise ValueError("P4_3_BLOCKED_OR_EXISTING_AUDIT")
    events = read_ledger(Path("reports/audit/track_a_events.jsonl"))
    budget_before = pair_budget(events)
    start = time.monotonic()
    out.mkdir(parents=True)
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        permission = Permission(MODE)
        universe = UniverseSpec("SYN:NEURAL_G5", UNIVERSE)
        data = synthetic_data(universe)
        seed_all(42)
        model = SharedLSTM()
        parameters = {name: list(p.shape) for name, p in model.named_parameters()}
        prediction = torch.tensor([[[2. ** .5] * 5, [6. ** .5] * 5],
                                   [[10. ** .5] * 5, [0.] * 5]])
        loss = float(session_losses(prediction, torch.zeros_like(prediction),
                                    torch.tensor([[True, True], [True, False]])).mean())
        if abs(loss - 7) > 1e-6:
            raise ValueError("INDEPENDENT_WEIGHTED_LOSS_ORACLE_FAILED")
        write_json(out / "hand_oracles.json", {
            "parameter_formula": 4 * 32 * (16 + 32 + 2) + 33,
            "actual_parameters": sum(p.numel() for p in model.parameters()),
            "named_shapes": parameters, "expected_loss": 7, "actual_loss": loss,
            "wrong_pooled_loss": 6, "model_input": [5, 48, 16], "output": [5],
        })
        curve = EarlyStop()
        timeline = []
        for value in [1., .9995] + [1.] * 10:
            curve.observe(value)
            timeline.append(dict(vars(curve)))
        write_json(out / "scripted_selection.json", timeline)
        fitted = run_pair(data, "WF1", pd.Timestamp("2023-07-01T04:00Z"), permission,
                          out / "seed42_pair")
        if fitted.evidence["refit_initial_hash"] != fitted.evidence["calibration_initial_hash"]:
            raise ValueError("RESET_SEED_FRESH_INITIALIZATION_MISMATCH")
        example = feature_input(universe, day="2023-07-20")
        # ASOF source binding must match the final fit; retain genuine fabricated clocks.
        example = replace(example, stock=replace(example.stock,
                                                source_binding=data.origins[0].inputs.stock.source_binding))
        forecast = forecast_scores(fitted, example, permission)
        changed = synthetic_data(universe, "SYN:PLANTED_B", base=data)
        changed_id = data_identity(changed)
        if changed_id == data_identity(data):
            raise ValueError("SYNTHETIC_DATASET_VERSION_SWAP_NOT_INVALIDATED")
        after = pair_budget(read_ledger(Path("reports/audit/track_a_events.jsonl")))
        if after != budget_before or after["attempted_pairs"] != 0:
            raise ValueError("SCIENTIFIC_PAIR_BUDGET_CHANGED")
        result = {
            "status": "P4_1_P4_2_SYNTHETIC_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED",
            "scientific_status": "SCIENTIFIC_ACTIVATION_HOLD", "mode": MODE,
            "pair": fitted.evidence, "forecasts": list(forecast.scores),
            "forecast_id": forecast.forecast_id, "original_data_identity": data_identity(data),
            "changed_data_identity": changed_id, "scientific_budget": after,
            "P4_3": guard_operation("training", events),
            "elapsed_seconds": time.monotonic() - start,
            "torch": torch.__version__, "device": "cpu", "cpu_threads": 1,
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "mps_available_not_used": torch.backends.mps.is_available(),
            "peak_memory": peak_memory(),
            "cross_device_bitwise_claim": False,
            "pair_cost_estimate": "Synthetic cost only; real benchmark remains P4.3 HOLD",
            "illustrative_1502_origin_row_scale": {
                "factor": 1502 / fitted.evidence["indexed_origins"],
                "pair_seconds_at_linear_scale": (
                    fitted.evidence["calibration_seconds"] + fitted.evidence["refit_seconds"]
                ) * 1502 / fitted.evidence["indexed_origins"],
                "warning": "Illustrative only: preprocessing, eligible counts, epoch selection, "
                           "device load and actual real runtime are not established",
            },
        }
        write_json(out / "synthetic_evidence.json", result)
        return result
    finally:
        torch.set_num_threads(previous_threads)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=[MODE, "SCIENTIFIC_REAL"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.out, args.mode)
    print(result["status"])


if __name__ == "__main__":
    main()
