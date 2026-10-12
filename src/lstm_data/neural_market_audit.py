"""Hermetic MC0/MC1 audit: two bounded scripted-selection synthetic pairs only."""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd
import torch

from .baseline_fixtures import feature_input
from .config import write_json
from .ledger import pair_budget, read_ledger
from .market_features import MarketVector
from .neural_artifacts import MODE
from .neural_audit import peak_memory, synthetic_data
from .neural_engine import seed_all
from .neural_lifecycle import code_identity, forecast_scores, run_pair
from .neural_market import MarketEvidence, MarketStamp
from .neural_models import EndpointGatedLSTM, create_model, gate_diagnostics
from .p3_domain import Permission, UniverseSpec


def fabricated_history(times: tuple[pd.Timestamp, ...]) -> MarketEvidence:
    """Fabricated state assertions, not D7 derived from any observed OHLC series."""
    vectors = []
    for t in sorted(set(times)):
        hour = t.value // 3_600_000_000_000
        day = t.tz_convert("America/New_York").date().toordinal()
        vectors.append(
            MarketVector(
                t,
                (
                    float(hour % 7),
                    float(hour % 11),
                    float(hour % 13),
                    float(day % 17),
                    float(day % 19),
                ),
                "VECTOR_VALID",
                ("SYN:MKT:" + t.isoformat(),),
            )
        )
    rows = tuple(vectors)
    return MarketEvidence(
        "SYN:MC_AUDIT_SOURCE",
        rows,
        tuple(MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids) for v in rows),
    )


def audit(out: Path, mode: str = MODE) -> dict:
    if mode != MODE or out.exists():
        raise ValueError("SCIENTIFIC_MARKET_TRAINING_FORBIDDEN_OR_OUTPUT_EXISTS")
    start = time.monotonic()
    before = pair_budget(read_ledger(Path("reports/audit/track_a_events.jsonl")))
    permission = Permission(MODE)
    universe = UniverseSpec("SYN:MC_AUDIT", ("AAPL", "JPM", "JNJ", "WMT", "CAT"))
    old_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    out.mkdir(parents=True)
    try:
        data = synthetic_data(universe)
        history = fabricated_history(tuple(v.timestamp for v in data.market_vectors))
        data = replace(data, market_vectors=history.vectors)
        forecasts, fits = {}, {}
        for architecture in ("MC0", "MC1"):
            run = run_pair(
                data,
                "WF1",
                pd.Timestamp("2023-07-01T04:00Z"),
                permission,
                out / architecture,
                architecture=architecture,
                market_history=history,
                synthetic_validation_trace=(1.0, 0.9995) + (1.0,) * 10,
            )
            row = feature_input(universe, day="2023-07-20")
            row = replace(
                row,
                stock=replace(
                    row.stock, source_binding=data.origins[0].inputs.stock.source_binding
                ),
            )
            later = fabricated_history(tuple(s.end for s in row.stock.steps))
            f = forecast_scores(run, row, permission, market_history=later)
            forecasts[architecture] = {
                "id": f.forecast_id,
                "scores": f.scores,
                "universe": f.universe.universe_id,
                "pair": run.pair.key,
                "checkpoint_sha": run.evidence["final_checkpoint"]["sha256"],
            }
            fits[architecture] = run.evidence
        matched_fields = (
            "train_view",
            "validation_view",
            "refit_view",
            "calibration_preparation",
            "refit_preparation",
            "indexed_origins",
        )
        if any(fits["MC0"][key] != fits["MC1"][key] for key in matched_fields):
            raise ValueError("MC0_MC1_SAME_INFORMATION_REQUIRED")
        seed_all(42)
        mc0 = create_model("MC0")
        mc1 = create_model("MC1")
        assert isinstance(mc1, EndpointGatedLSTM)
        mc1.core.load_state_dict(mc0.state_dict())
        mc0.eval()
        mc1.eval()
        x = torch.randn(2, 5, 48, 16)
        m = torch.randn(2, 48, 5)
        m[:, 3:5] = 0
        z = torch.cat((x, m[:, None].expand(-1, 5, -1, -1)), dim=-1).reshape(10, 48, 21)
        with torch.no_grad():
            error = float((mc0(z) - mc1(z)).abs().max())
            gates = gate_diagnostics(mc1.compose(z)[1])
        after = pair_budget(read_ledger(Path("reports/audit/track_a_events.jsonl")))
        if before != after or after["attempted_pairs"] != 0:
            raise ValueError("SCIENTIFIC_BUDGET_MUTATION")
        evidence = {
            "mode": mode,
            "status": "ENGINEERING_COMPLETE_HUMAN_REVIEW_REQUIRED",
            "scientific_status": "HOLD",
            "code": code_identity(),
            "forecasts": forecasts,
            "fits": fits,
            "identity_max_error": error,
            "identity_gate": gates,
            "matched_information": True,
            "parameters": {
                "MC0": sum(p.numel() for p in mc0.parameters()),
                "MC1": sum(p.numel() for p in mc1.parameters()),
            },
            "scientific_budget": after,
            "seconds": time.monotonic() - start,
            "peak_memory": peak_memory(),
            "selection": "SCRIPTED_ORACLE; actual finite train/validation gradients also measured",
            "historical_batches": "NOT_RUN/BLOCKED",
            "cpu_threads": 1,
            "torch": torch.__version__,
        }
        write_json(out / "synthetic_evidence.json", evidence)
        return evidence
    finally:
        torch.set_num_threads(old_threads)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=[MODE, "SCIENTIFIC_REAL"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(audit(args.out, args.mode)["status"])


if __name__ == "__main__":
    main()
