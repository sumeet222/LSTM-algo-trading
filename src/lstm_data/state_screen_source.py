"""P028 immutable source/approval chain, cached state identity and support recheck."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import exchange_calendars as xcals
import numpy as np
import pandas as pd

from .config import now, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_run import storage_bytes
from .objective_screen_source import scoped_view
from .p2_closure import load_deferred_work
from .panel_state_audit import CHANNELS, support
from .peer_screen_authority import JOURNAL, rows
from .state_screen_models import panel_state
from .state_screen_spec import AUDIT, CUTS, P026, SCIENCE
from .visualization.hf1m_long import LongStudy


def verify_support() -> dict:
    audit = json.loads(AUDIT.read_text())
    cache = audit["cache"]
    for reference in cache:
        checked(reference)
    calendar = (
        xcals.get_calendar("XNYS")
        .sessions_in_range("2011-01-01", "2025-12-31")
        .strftime("%Y-%m-%d")
        .tolist()
    )
    results = []
    for role in ("inner_train", "inner_validation", "refit", "development"):
        reference = next(r for r in cache if r["path"].endswith(role + "_daily_support.parquet"))
        daily = pd.read_parquet(checked(reference))
        phase = "inner" if role.startswith("inner") else "refit"
        fitting = "inner_train" if phase == "inner" else "refit"
        train = pd.read_parquet(
            checked(
                next(r for r in cache if r["path"].endswith(fitting + "_daily_support.parquet"))
            )
        )
        cut = float(np.median(train[CHANNELS[1]]))
        if cut != CUTS[phase]:
            raise ValueError("P028_FROZEN_SUPPORT_CUT")
        actual = support(daily, cut, calendar, role)
        expected = next(r for r in audit["proposed_regime_support"] if r["role"] == role)
        if actual != expected:
            raise ValueError("P028_SUPPORT_CACHE_REGRESSION")
        if role != "development":
            for state in actual["states"].values():
                # Counts only, not postfit usage or assumed economic regimes.
                sessions = state["sessions"]
                episodes = state["runs_at_least_five"]
                if sessions < (20 if role == "inner_validation" else 50) or episodes < (
                    2 if role == "inner_validation" else 5
                ):
                    raise ValueError("P028_A12_INACTIVE_CONDITIONAL")
        results.append(actual)
    return dict(
        status="PASS_P028_A12_SUPPORT",
        roles=results,
        development="descriptive LOW sparse-episode WARN accepted",
    )


def audit(out: Path) -> dict:
    scope = json.loads((out / "authorization_scope.json").read_text())
    checked(scope["work_order"])
    for reference in scope["approved_references"]:
        checked(reference)
    prior = json.loads((P026 / "experiment_design.json").read_text())
    if rows()[-1]["global_started_pairs"] != 59 or rows()[-1]["status"] != "COMPLETED":
        raise ValueError("P028_LEDGER59")
    load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    allowed = {
        "apps/track_a_dashboard.py",
        "configs/track_a_visualization_v1.json",
        "docs/track_a/Visualization_Quickstart.md",
        "docs/track_a/Visualization_User_Guide.md",
        "configs/CURRENT_EXPERIMENT_REGISTRY.json",
    }
    preservation = []
    with (P026 / "final_execution_artifact_inventory.csv").open() as stream:
        for row in csv.DictReader(stream):
            if row["path"] not in allowed:
                reference = dict(path=row["path"], bytes=int(row["bytes"]), sha256=row["sha256"])
                checked(reference)
                preservation.append(reference)
    for reference in (
        list(prior["source_hashes"].values()) + prior["protected_refs"] + prior["baseline_refs"]
    ):
        checked(reference)
    for path in allowed:
        p = Path(path)
        if p.exists():
            dest = out / "prior_reader_snapshots" / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                dest.write_bytes(p.read_bytes())
    data = json.loads(AUDIT.read_text())
    study = LongStudy.discover(Path.cwd())
    views = {}
    probes = []
    import torch

    for role in ("inner_train", "inner_validation", "refit", "development"):
        view = scoped_view(study, role, stage=7)
        views[role] = view.summary()
        if views[role] != prior["views"][role]:
            raise ValueError("P028_ROLE_POPULATION_REGRESSION")
        phase = "inner" if role.startswith("inner") else "refit"
        cached = pd.read_parquet(
            checked(
                next(
                    r
                    for r in data["cache"]
                    if r["path"].endswith(phase + "_unique_step_state.parquet")
                )
            )
        ).set_index("step")
        for start in range(0, len(view.source.rows), 32):
            pos = tuple(range(start, min(start + 32, len(view.source.rows))))
            x = torch.from_numpy(view.origin_batch(pos)["x"])
            actual = panel_state(x).numpy()
            steps = view.source.rows.iloc[list(pos)].first_step.to_numpy(dtype=int)[
                :, None
            ] + np.arange(48)
            expected = (
                cached.loc[steps.reshape(-1), list(CHANNELS)]
                .to_numpy(dtype=np.float32)
                .reshape(len(pos), 48, 2)
            )
            np.testing.assert_array_equal(actual, expected)
        probes.append(dict(role=role, origins=len(view.source.rows), states_exact=True))
        del view, cached
    result = dict(
        status="PASS_P028_STAGE0_AUTHORITY_IDENTITY",
        at=now(),
        ledger=59,
        new_starts=0,
        optimizer_updates=0,
        input_contract=study.plan["input_contract"],
        views=views,
        recipes={
            v: dict(scale=study.recipe(v)["t2_scale"], epsilon=study.recipe(v)["epsilon"])
            for v in ("inner", "refit")
        },
        source_hashes=prior["source_hashes"],
        baseline_refs=prior["baseline_refs"],
        protected_refs=prior["protected_refs"],
        preservation_refs=preservation,
        previous_journal=ref(JOURNAL),
        previous_pointer=ref(out / "registry_pointer_v17_snapshot.json"),
        storage_before=storage_bytes([Path(".")]) - 6_000_000,
        source_cache_probes=probes,
        support=verify_support(),
        authorization_scope=ref(out / "authorization_scope.json"),
        protected_hash_only=True,
    )
    write_json(out / "scientific_definitions.json", SCIENCE)
    result["scientific_definitions"] = ref(out / "scientific_definitions.json")
    write_json(out / "P028_STAGE_0_SOURCE_AND_AUTHORITY_RECEIPT_v2.json", result)
    return result
