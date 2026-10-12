"""Exactly1000 independent seeded paths; one causal calendar and shared P3 replay."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from .baseline_authority import replay_permission, verify
from .baseline_inputs import Prediction, forecast_adapter
from .clocks import ExecutionPlan, utc
from .config import digest, fingerprint, write_json
from .p3_domain import Forecast, Frictions, Permission, UniverseSpec, synthetic_id
from .p3_events import json_value
from .p3_replay import ReplayFrame, replay

MASTER = 20261010
NAMESPACE = 0x503352
PATHS = 1000


@dataclass(frozen=True)
class RandomOpportunity:
    universe: UniverseSpec
    opportunity_id: str
    input_id: str
    plan: ExecutionPlan
    available_at: pd.Timestamp | None
    input_eligible: bool
    basis: str

    def __post_init__(self) -> None:
        synthetic_id(self.opportunity_id)
        synthetic_id(self.input_id)
        if self.basis != "SYNTHETIC":
            raise ValueError("RANDOM_HISTORICAL_SOURCE_ACTIVATION_HOLD")
        if self.available_at is not None:
            object.__setattr__(self, "available_at", utc(self.available_at))
        if self.plan.issuance is not None:
            Forecast(self.universe, "SYN:OP_CLOCK_CHECK", self.plan, (0.0,) * 5)

    @property
    def eligible(self) -> bool:
        return (
            self.input_eligible
            and self.plan.calendar_valid
            and self.plan.cutoff is not None
            and self.available_at is not None
            and self.available_at <= self.plan.cutoff
        )


@dataclass(frozen=True)
class RandomDraw:
    universe: UniverseSpec
    path_id: int
    opportunity_id: str
    permutation: tuple[str, ...]
    stream_id: str
    algorithm: str
    numpy_version: str

    def __post_init__(self) -> None:
        if (
            type(self.path_id) is not int
            or not 0 <= self.path_id < PATHS
            or set(self.permutation) != set(self.universe.symbols)
            or len(self.permutation) != 5
            or self.algorithm != "NUMPY_PCG64DXSM_SEEDSEQUENCE"
            or self.numpy_version != np.__version__
            or len(self.stream_id) != 64
        ):
            raise ValueError("FIVE_UNIQUE_RANDOM_NAMES_AND_PATH_REQUIRED")


def draws(
    universe: UniverseSpec,
    opportunities: tuple[RandomOpportunity, ...],
    path_id: int,
    permission: Permission,
    *,
    allow_synthetic: bool = False,
) -> tuple[RandomDraw, ...]:
    verify(permission)
    if (
        not allow_synthetic
        or type(path_id) is not int
        or not 0 <= path_id < PATHS
        or any(o.universe != universe for o in opportunities)
    ):
        raise ValueError("SYNTHETIC_BOUND_RANDOM_PATH_REQUIRED")
    keys = [o.opportunity_id for o in opportunities]
    origin_keys = [(o.plan.session, o.plan.origin, o.plan.cutoff) for o in opportunities]
    if len(set(keys)) != len(keys) or len(set(origin_keys)) != len(origin_keys):
        raise ValueError("UNIQUE_CAUSAL_OPPORTUNITY_KEYS_REQUIRED")
    cutoffs = [o.plan.cutoff for o in opportunities if o.plan.cutoff is not None]
    if cutoffs != sorted(cutoffs):
        raise ValueError("CHRONOLOGICAL_OPPORTUNITY_CALENDAR_REQUIRED")
    seed = np.random.SeedSequence(MASTER, spawn_key=(NAMESPACE, path_id))
    generator = np.random.Generator(np.random.PCG64DXSM(seed))
    stream = fingerprint(
        [MASTER, NAMESPACE, path_id, seed.generate_state(4).tolist(), universe.universe_id]
    )
    return tuple(
        RandomDraw(
            universe,
            path_id,
            o.opportunity_id,
            tuple(universe.symbols[int(i)] for i in generator.permutation(5)),
            stream,
            "NUMPY_PCG64DXSM_SEEDSEQUENCE",
            np.__version__,
        )
        for o in opportunities
        if o.eligible
    )


def random_predictions(
    opportunities: tuple[RandomOpportunity, ...],
    path_draws: tuple[RandomDraw, ...],
    permission: Permission,
) -> tuple[Prediction, ...]:
    verify(permission)
    lookup = {o.opportunity_id: o for o in opportunities}
    output = []
    for d in path_draws:
        o = lookup[d.opportunity_id]
        if d.universe != o.universe or not o.eligible:
            raise ValueError("DRAW_CANNOT_ACTIVATE_INELIGIBLE_INPUT")
        rank = {s: float(5 - i) for i, s in enumerate(d.permutation)}
        output.append(
            Prediction(
                o.universe,
                f"SYN:RANDOM:{d.path_id}:" + o.opportunity_id,
                o.input_id,
                o.plan,
                tuple(rank[s] for s in o.universe.symbols),
                "UNIFORM_RANDOM",
                "SYN:STREAM:" + d.stream_id,
                "SYNTHETIC",
            )
        )
    return tuple(output)


def path_script(
    universe: UniverseSpec,
    opportunities: tuple[RandomOpportunity, ...],
    template: tuple[ReplayFrame, ...],
    path_id: int,
    permission: Permission,
):
    d = draws(universe, opportunities, path_id, permission, allow_synthetic=True)
    predictions = random_predictions(opportunities, d, permission)
    forecasts = {
        p.plan.entry: forecast_adapter(p, permission, allow_synthetic=True) for p in predictions
    }
    if any(f.universe != universe for f in template):
        raise ValueError("RANDOM_TEMPLATE_UNIVERSE_MISMATCH")
    if any(p.plan.entry not in {f.at for f in template} for p in predictions):
        raise ValueError("RANDOM_TEMPLATE_MISSING_CAUSAL_OPPORTUNITY")
    # Template forecast scores never affect draws or opportunities.
    return tuple(replace(frame, forecast=forecasts.get(frame.at)) for frame in template), d


def replay_scenario(
    permission: Permission,
    universe: UniverseSpec,
    script: tuple[ReplayFrame, ...],
    policy: str,
    bps: int,
    borrow: Decimal,
    cash: Decimal,
    at: pd.Timestamp,
):
    guarded = replay_permission(permission)
    engine = replay(
        guarded, universe, script, policy, Frictions(universe, Decimal(bps), borrow), cash, at
    )
    verify(permission)
    return engine


def random_matrix(
    permission: Permission,
    universe: UniverseSpec,
    opportunities: tuple[RandomOpportunity, ...],
    template: tuple[ReplayFrame, ...],
    cash: Decimal,
    at: pd.Timestamp,
    out: Path,
    *,
    allow_synthetic: bool = False,
    stop_after_paths: int = PATHS,
) -> dict:
    verify(permission)
    if not allow_synthetic or not 1 <= stop_after_paths <= PATHS:
        raise ValueError("EXPLICIT_SYNTHETIC_RANDOM_MATRIX_REQUIRED")
    binding = fingerprint(
        [
            universe.universe_id,
            json_value(opportunities),
            json_value(template),
            np.__version__,
            {
                path.as_posix(): digest(path)
                for path in sorted(Path("src/lstm_data").glob("p3_*.py"))
            },
            {
                name: digest(Path("src/lstm_data") / name)
                for name in (
                    "baseline_random.py",
                    "baseline_authority.py",
                    "baseline_inputs.py",
                    "calendar.py",
                    "clocks.py",
                    "labels.py",
                    "corporate_actions.py",
                )
            },
            str(cash),
            str(at),
            MASTER,
            NAMESPACE,
        ]
    )
    out.mkdir(parents=True, exist_ok=True)
    existing = sorted(out.glob("random_chunk_*.json"))
    completed = []
    for file in existing:
        payload = json.loads(file.read_text())
        if payload["binding"] != binding or payload["rows_sha"] != fingerprint(payload["rows"]):
            raise ValueError("RANDOM_CHECKPOINT_BINDING_OR_HASH_CHANGED")
        completed.extend(payload["rows"])
    if [r["path_id"] for r in completed] != list(range(len(completed))):
        raise ValueError("RANDOM_CHECKPOINT_PREFIX_REQUIRED")
    if len(completed) > PATHS or any(len(r["scenarios"]) != 24 for r in completed):
        raise ValueError("RANDOM_CHECKPOINT_SCENARIO_COVERAGE_REQUIRED")
    buffer = []
    cases = [
        (p, c, b)
        for p in ("A", "B")
        for c in (0, 2, 5, 10)
        for b in (Decimal(0), Decimal(".005"), Decimal(".03"))
    ]
    for path_id in range(len(completed), stop_after_paths):
        script, path_draws = path_script(universe, opportunities, template, path_id, permission)
        summaries = []
        for policy, bps, borrow in cases:
            e = replay_scenario(permission, universe, script, policy, bps, borrow, cash, at)
            event_counts = {
                kind: sum(ev.kind == kind for ev in e.ledger.events)
                for kind in ("SLEEVE", "FILL", "EXCEPTION", "RETRY")
            }
            summaries.append(
                {
                    "hash": e.ledger.trace_id,
                    "accepted": event_counts["SLEEVE"],
                    "rejected": len(e.rejections),
                    "veto": e.rejections.count("POLICY_B_VIRTUAL_CONFLICT"),
                    "cap": e.rejections.count("POST_COST_100_CAP"),
                    "fills": event_counts["FILL"],
                    "exceptions": len(e.exceptions),
                    "outstanding": e.pending_target is not None,
                    "execution_fee": str(e.book.execution_fees),
                    "borrow_fee": None if e.borrow.total is None else str(e.borrow.total),
                }
            )
        buffer.append(
            {
                "path_id": path_id,
                "draw_hash": fingerprint([d.permutation for d in path_draws]),
                "stream_id": path_draws[0].stream_id if path_draws else None,
                "scenarios": summaries,
            }
        )
        if len(buffer) == 25 or path_id + 1 == stop_after_paths:
            chunk = out / f"random_chunk_{len(completed):04d}.json"
            if chunk.exists():
                raise ValueError("RANDOM_OUTPUT_EXISTS")
            write_json(
                chunk,
                {
                    "scope": "SYNTHETIC_ONLY",
                    "binding": binding,
                    "rows": buffer,
                    "rows_sha": fingerprint(buffer),
                },
            )
            completed.extend(buffer)
            buffer = []
    summary = {
        "scope": "SYNTHETIC_ONLY",
        "binding": binding,
        "master_seed": MASTER,
        "namespace": NAMESPACE,
        "algorithm": "NUMPY_PCG64DXSM_SEEDSEQUENCE",
        "numpy_version": np.__version__,
        "universe_id": universe.universe_id,
        "completed_paths": len(completed),
        "completed_scenarios": len(completed) * 24,
        "required_paths": PATHS,
        "status": "COMPLETE" if len(completed) == PATHS else "CHECKPOINT_PARTIAL",
        "path_reproducibility_hash": fingerprint(completed),
        "scientific_status": "HOLD",
        "research_ready": False,
        "context": "DESCRIPTIVE_RANDOMIZED_REFERENCE_NOT_FORMAL_SELECTION_ADJUSTED_NULL",
    }
    summary_path = out / (
        "random_summary.json"
        if len(completed) == PATHS
        else f"random_summary_{len(completed):04d}.json"
    )
    if summary_path.exists():
        if json.loads(summary_path.read_text()) != summary:
            raise ValueError("RANDOM_SUMMARY_ALREADY_EXISTS_WITH_DIFFERENT_EVIDENCE")
    else:
        write_json(summary_path, summary)
    return summary
