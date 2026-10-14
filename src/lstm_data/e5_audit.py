"""Bounded E5 learning/lifecycle and D8 clock evidence, exclusively fabricated."""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .calendar import schedule
from .config import write_json
from .directed_peers import (
    Antecedent,
    FormationRow,
    directed_window,
    formation_pair,
    ridge_layout_status,
    timing_destroy,
)
from .ft0_transforms import identity
from .m2 import ScheduledCalendar
from .neural_artifacts import MODE
from .neural_audit import peak_memory
from .neural_engine import SessionBatch, batch_prediction, clip, optimizer, seed_all, session_losses
from .neural_models import create_model
from .p3_domain import Permission, UniverseSpec
from .peer_inputs import M1_INDEX, peer_summaries
from .peer_neural import e5_input, trace_e5
from .regime_peer_audit import fabricated_case


def fake_formation(universe: UniverseSpec, permission: Permission):
    """Five fictional prices/volumes over the preceding60 calendar sessions."""
    sessions = schedule("2020-01-01", "2020-06-30").iloc[-60:]
    rows = []
    for day, r in sessions.iterrows():
        if not isinstance(day, pd.Timestamp):
            raise ValueError("CALENDAR_TIMESTAMP_REQUIRED")
        for i, symbol in enumerate(universe.symbols):
            rows.append(
                FormationRow(
                    symbol,
                    day.date().isoformat(),
                    100.0,
                    (i + 1) * 1e6,
                    r.close,
                    "SYN:FORMATION:" + symbol + str(day.date()),
                )
            )
    return formation_pair(universe, tuple(rows), permission)


def fake_antecedent(row, prep, calendar: ScheduledCalendar) -> Antecedent:
    step = calendar.steps[calendar.steps.index(row.stock.steps[0]) - 1]
    return Antecedent(
        row.universe,
        step,
        (1.0, 2.0, 3.0, 4.0, 5.0),
        (step.end,) * 5,
        tuple("SYN:LAG48:" + s for s in row.universe.symbols),
        row.stock.source_binding,
        row.stock.action_binding,
        prep.stock_scaler.certificate_id,
        "SYN:UNITS:UNCHANGED",
    )


def health_fixture() -> SessionBatch:
    """The original fixed arithmetic fixture; no fit, clocks or TG0 certification.

    Construction is extracted unchanged so diagnosis can inspect the exact data
    without another sixty-step fit. RNG8049 is independent of model seed42.
    """
    generator = np.random.default_rng(8049)
    values = np.zeros((16, 2, 5, 48, 23), dtype=np.float32)
    values[..., M1_INDEX] = generator.normal(size=(16, 2, 5, 48))
    for d in range(16):
        for o in range(2):
            values[d, o, :, :, 21:] = peer_summaries(values[d, o, :, :, :16])
    targets = torch.tensor(values[..., -1, 21].copy())
    return SessionBatch(
        tuple(f"SYN:PLANTED_DAY:{i}" for i in range(16)),
        torch.tensor(values, requires_grad=True),
        targets,
        torch.ones(16, 2, dtype=torch.bool),
    )


def planted_learning() -> dict:
    """Unchanged sixty-step acceptance proof, separate from D6g calibration/refit."""
    seed_all(42)
    batch = health_fixture()
    targets = batch.targets
    values = batch.inputs.detach().numpy()
    model = create_model("E5")
    model.eval()
    with torch.no_grad():
        before = float(
            session_losses(batch_prediction(model, batch), targets, batch.origins).mean()
        )
    opt = optimizer(model)
    losses, norms, gradients = [], [], []
    for _ in range(60):
        model.train()
        opt.zero_grad(set_to_none=True)
        batch.inputs.grad = None
        loss = session_losses(batch_prediction(model, batch), targets, batch.origins).mean()
        loss.backward()
        if batch.inputs.grad is None:
            raise ValueError("PEER_CHANNEL_GRADIENT_ABSENT")
        gradients.append(float(batch.inputs.grad[..., 21:].norm()))
        norms.append(clip(model))
        opt.step()
        losses.append(float(loss.detach()))
    model.eval()
    with torch.no_grad():
        after = float(session_losses(batch_prediction(model, batch), targets, batch.origins).mean())
        ablated = replace(batch, inputs=batch.inputs.detach().clone())
        ablated.inputs[..., 21:] = 0
        # Deliberate negative-information diagnostic at the model boundary only.
        # A zeroed peer vector must never pass the canonical SessionBatch validator.
        ablated_prediction = model(ablated.inputs.reshape(-1, 48, 23)).reshape(16, 2, 5)
        without = float(session_losses(ablated_prediction, targets, batch.origins).mean())
    return {
        "scope": MODE,
        "passed": after < 0.35 * before and without > 2 * after and min(gradients) > 0,
        "proof_criterion": (
            "final < .35 * initial AND peer_zero > 2 * final AND positive peer gradient"
        ),
        "fixture": "RANDOM_OTHER_STOCK_MEAN_ONLY",
        "epochs": 60,
        "batch_sessions": 16,
        "session_origins": 2,
        "initial_eval_MSE": before,
        "final_eval_MSE": after,
        "peer_zero_ablation_MSE": without,
        "first_training_MSE": losses[0],
        "last_training_MSE": losses[-1],
        "min_peer_gradient": min(gradients),
        "max_preclip_norm": max(norms),
        "empirical_selection": False,
        "fixture_identity": identity([values.tolist(), targets.tolist(), 8049]),
    }


def audit(out: Path, mode: str, *, failed_health_proof: Path | None = None) -> dict:
    """Useful partial evidence; stop all further fitting after a failed health gate.

    Reusing an immutable failed proof never grants fit permission. It only avoids
    repeating a completed failed fixture while reporting independent D8 math.
    """
    import json

    from .config import digest

    if mode != MODE or out.exists() or "audit" in out.parts:
        raise ValueError("NEW_SYNTHETIC_E5_REPORT_ONLY")
    permission = Permission(mode)
    permission.ensure()
    out.mkdir(parents=True)
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    started = time.monotonic()
    try:
        if failed_health_proof is None:
            write_json(
                out / "engineering_fixture_reservation.json",
                {
                    "scope": MODE,
                    "fixture_id": "SYN:E5:PLANTED_HEALTH:8049",
                    "real_pairs": 0,
                    "health_epochs_cap": 60,
                },
            )
            health = planted_learning()
        else:
            proof = json.loads(failed_health_proof.read_text())
            refs = (Path(proof["log"]), Path(proof["status"]))
            if any(
                p.is_absolute() or ".." in p.parts or p.parts[:2] != ("reports", "data_audit")
                for p in refs
            ):
                raise ValueError("PROJECT_RELATIVE_SYNTHETIC_PROOF_ONLY")
            if (
                proof["scope"] != MODE
                or proof["health"]["passed"] is not False
                or digest(Path(proof["log"])) != proof["log_sha"]
                or digest(Path(proof["status"])) != proof["status_sha"]
            ):
                raise ValueError("IMMUTABLE_FAILED_HEALTH_PROOF_REQUIRED")
            health = proof["health"]
        # No new fit/refit after the failure. A passing future health gate is not
        # an automatic authorization to clear the separate review-pending gate.
        data, history, prep, val, guard = fabricated_case()
        row = data.origins[-2].inputs
        x, trace = e5_input(row, prep, history, guard)
        seed_all(42)
        model = create_model("E5")
        calendar = ScheduledCalendar("2020-07-01", "2023-06-30")
        pair = fake_formation(row.universe, guard)
        directed = directed_window(
            row, prep, history, guard, calendar, pair, fake_antecedent(row, prep, calendar)
        )
        eligible = tuple(str(d.date()) for d in schedule("2023-03-01", "2023-06-30").index)
        anchor = directed.samples[0]
        fake_history = tuple(
            replace(
                anchor,
                step=s,
                z=tuple(float(i + s.slot) for i in range(5)),
                available_at=(s.end,) * 5,
                source_ids=tuple(
                    "SYN:SHAM:" + s.session + str(s.slot) + name for name in row.universe.symbols
                ),
            )
            for s in calendar.steps
            if s.session in eligible
        )
        sham = timing_destroy(directed, fake_history, eligible, calendar)
        missing = timing_destroy(directed, (), eligible, calendar)
        if not sham.matched or missing.matched:
            raise ValueError("MATCHED_SHAM_POPULATION_GUARD_FAILED")
        parameters = {name: p.numel() for name, p in model.named_parameters()}
        evidence = {
            "scope": MODE,
            "gate_A": "P4.8_SYNTHETIC_ENGINEERING_PARTIAL",
            "gate_B": "P4.9_SYNTHETIC_ENGINEERING_PARTIAL",
            "upstream_acceptance": "HUMAN_REVIEW_PENDING_SYNTHETIC_PREREQUISITE_ONLY",
            "parameters": parameters,
            "parameter_total": sum(parameters.values()),
            "parameter_formula": "4*32*(23+32+2)+33=7329",
            "input": [5, 48, 23],
            "health": health,
            "health_proof_sha": digest(failed_health_proof)
            if failed_health_proof is not None
            else None,
            "lifecycle": "NOT_RUN_FAILED_HEALTH_GATE; reusable E5 adapter implemented",
            "final_checkpoint": "NOT_CREATED; no E5 final-refit five-score forecast claimed",
            "T1_E5_UNTRAINED": trace_e5(model, x, "SYN:E5_T1:" + trace),
            "T1_directed": directed.trace(calendar),
            "formation_means": pair.means,
            "ridge": ridge_layout_status(),
            "ridge_fits": "NOT_RUN_LAYOUT_BLOCKED",
            "synthetic_direction_fits": "NOT_RUN_LAYOUT_BLOCKED",
            "sham": {
                "matched_arms": ["LL0_R", "LL1_R", "SHIFTED_LL1_R"],
                "common_origin_mask": [sham.matched],
                "common_missing_mask": [missing.matched],
                "missing_reasons": missing.exclusions,
                "timestamp_examples": sham.timestamp_pairs[-3:],
                "binding": sham.binding,
                "limitation": sham.limitation,
                "sham_scores": "NOT_RUN_LAYOUT_BLOCKED",
            },
            "real_HL": "HL_REAL_UNRESOLVED",
            "scientific": "G0_G4_HOLD",
            "real_G5_G6_G7": "NOT_RUN",
            "real_pairs": "0/40",
            "provider_attempts": 0,
            "new_engineering_calibration_refit_pairs": 0,
            "new_health_runs": 0 if failed_health_proof is not None else 1,
            "seconds": time.monotonic() - started,
            "peak_memory": peak_memory(),
        }
        write_json(out / "synthetic_evidence.json", evidence)
        return evidence
    finally:
        torch.set_num_threads(previous_threads)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=[MODE], required=True)
    parser.add_argument("--failed-health-proof", type=Path)
    args = parser.parse_args()
    result = audit(args.out, args.mode, failed_health_proof=args.failed_health_proof)
    print({k: result[k] for k in ("gate_A", "gate_B", "parameter_total", "seconds", "real_pairs")})


if __name__ == "__main__":
    main()
