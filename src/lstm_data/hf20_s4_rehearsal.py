"""Zero optimizer-call S4 checkpoint/export/gate rehearsal with archived prefix recipes."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from .hf1m_action_audit import digest
from .hf20_rank_visuals import PRIOR
from .hf20_ranking_continue import check_configuration
from .hf20_ranking_run import initial_hash, predict
from .hf20_s4_data import ROLES, S4Data
from .hf20_s4_diagnostics import export, gate, verify
from .hf20_s4_epoch import epoch
from .hf20_s4_visuals import build
from .neural_engine import SharedLSTM, optimizer, seed_all


def run(data: S4Data, out: Path) -> None:
    torch.set_num_threads(4)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    receipts = []
    with (
        patch.object(
            torch.optim.AdamW, "step", side_effect=AssertionError("NO_OPTIMIZER_CALL")
        ) as guard,
        patch(
            "lstm_data.hf20_s4_data.fit_expanded", side_effect=AssertionError("NO_NEW_RECIPE_FIT")
        ) as fit_guard,
    ):
        for year in range(2021, 2025):
            for arm in ("NR", "T2R"):
                run_id = f"HF20-S4A-F{year % 100}-H4-{arm}-S42"
                with tempfile.TemporaryDirectory(prefix="untrained_s4_gate_", dir=out) as temporary:
                    root = Path(temporary).resolve().relative_to(Path.cwd().resolve())
                    dest = root / run_id
                    dest.mkdir()
                    for role in ROLES:
                        data.rows.iloc[data.positions(year, role)].to_csv(
                            root / f"F{year % 100}_{role}_indices.csv", index=False
                        )
                    init = None
                    exported = 0
                    for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
                        recipe_path = PRIOR / f"F{year % 100}_{phase}_recipe.json"
                        recipe = json.loads(recipe_path.read_text())
                        (root / recipe_path.name).write_bytes(recipe_path.read_bytes())
                        data.apply_recipe(year, phase, recipe)
                        seed_all(42)
                        model = SharedLSTM().float()
                        opt = optimizer(model)
                        config = check_configuration(model, opt)
                        state = initial_hash(model)
                        if init is None:
                            init = state
                        if state != init or opt.state:
                            raise ValueError("S4_FRESH_MODEL_OPTIMIZER_REHEARSAL")
                        pos = data.positions(year, roles[0])
                        days = data.rows.iloc[pos].session_date_et.drop_duplicates().iloc[:16]
                        subset = pos[data.rows.iloc[pos].session_date_et.isin(days).to_numpy()]
                        phase_name = "calibration" if phase == "inner" else "refit"
                        receipt = epoch(
                            model, opt, data, subset, arm, 1, phase_name, dest, update=False
                        )
                        (dest / f"{phase_name}_001.json").write_text(
                            json.dumps(
                                dict(receipt, ic=None, qualifies=False, untrained=True), indent=2
                            )
                            + "\n"
                        )
                        if initial_hash(model) != init or opt.state or receipt["steps"]:
                            raise ValueError("S4_ZERO_STEP_MUTATED_STATE")
                        checkpoint = dest / f"{phase}.pt"
                        torch.save(
                            dict(model=model.state_dict(), optimizer=opt.state_dict()), checkpoint
                        )
                        fresh = SharedLSTM().float()
                        fresh.load_state_dict(torch.load(checkpoint, weights_only=True)["model"])
                        (
                            dest
                            / (
                                "calibration_binding.json"
                                if phase == "inner"
                                else "refit_binding.json"
                            )
                        ).write_text(
                            json.dumps(
                                dict(
                                    checkpoint=str(checkpoint),
                                    checkpoint_sha256=digest(checkpoint),
                                    untrained=True,
                                )
                            )
                        )
                        for role in roles:
                            positions = data.positions(year, role)
                            scores = predict(data, positions, model)
                            np.testing.assert_array_equal(scores, predict(data, positions, fresh))
                            export(
                                data, year, role, arm, scores, dest, "UNTRAINED_REHEARSAL_NO_FIT"
                            )
                            exported += len(positions) * 20
                        if phase == "refit":
                            m1 = root / f"F{year % 100}_S4_N1"
                            m1.mkdir()
                            p = data.positions(year, "oos")
                            export(
                                data,
                                year,
                                "oos",
                                "N1",
                                predict(data, p, "N1"),
                                m1,
                                "UNTRAINED_REHEARSAL_NO_FIT",
                            )
                    verify(data, year, dest, rehearsal=True)
                    build(root, dest, rehearsal=True)
                    gate(dest, dict(untrained=True, optimizer_step_calls=0, recipe_fit_calls=0))
                    receipts.append(
                        dict(
                            run_id=run_id,
                            four_roles=True,
                            full_population_rows=exported,
                            configuration=config,
                            fresh_seed_and_empty_optimizer=True,
                            checkpoint_reload_max_error=0,
                            optimizer_step_calls=guard.call_count,
                            recipe_fit_calls=fit_guard.call_count,
                            numerical_gate=True,
                            visual_payload_gate=True,
                            temporary_untrained_exports_discarded=True,
                        )
                    )
                print("ZERO_STEP_FULL_GATE_PASS", run_id, flush=True)
        if guard.call_count or fit_guard.call_count:
            raise ValueError("S4_PREFLIGHT_FITTING_OCCURRED")
    (out / "S4_ZERO_STEP_WORKFLOW_REHEARSAL.json").write_text(
        json.dumps(
            dict(
                status="PASS",
                workflows=receipts,
                optimizer_step_calls=0,
                new_recipe_fits=0,
                neural_starts=0,
                scope=(
                    "Full role exports/reloads and numerical/visual gates; one representative "
                    "16-session gradient batch per phase; archived recipes for structural "
                    "rehearsal only, never S4 fitted recipes"
                ),
            ),
            indent=2,
        )
        + "\n"
    )
