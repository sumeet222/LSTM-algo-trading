"""Bounded S5/S9 preparation: source audit and four zero-update family workflows."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from .hf1m_action_audit import digest
from .hf20_ranking_run import initial_hash
from .hf20_s4_data import ROLES
from .hf20_s5s9 import ARMS, META_FIELDS, RUNS, S4, Data, model_for
from .hf20_s5s9_report import export, finish_run
from .hf20_s5s9_run import POINTER, epoch, predict, resources
from .neural_engine import optimizer


def source_audit(data: Data, out: Path) -> None:
    """Verify exact S4 role identities before any recipe/model fitting is permitted."""
    counts = []
    coverage = []
    for year in range(2021, 2025):
        for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
            data.phase(year, phase, dict(gap_cap=1.0, rehearsal_only=True))
            for role in roles:
                pos = data.base.positions(year, role)
                rows = data.base.rows.iloc[pos]
                original = pd.read_csv(S4 / f"F{year % 100}_{role}_indices.csv")
                np.testing.assert_array_equal(rows.origin_id, original.origin_id)
                q = data.base.quality_fields(pos)
                q = {name: value.reshape(-1, 20) for name, value in q.items()}
                for slot in ["ALL", *sorted(rows.slot.unique())]:
                    mask = (
                        np.ones(len(rows), bool) if slot == "ALL" else rows.slot.eq(slot).to_numpy()
                    )
                    starts = rows.loc[mask, "first_step"].to_numpy(int)
                    ix = starts[:, None] + np.arange(48)
                    finite = (
                        np.isfinite(data.step[ix]).all()
                        and np.isfinite(data.origin[pos[mask]]).all()
                    )
                    if not finite:
                        raise ValueError("S5_METADATA_CAUSAL_COVERAGE")
                    counts.append(
                        dict(
                            year=year,
                            role=role,
                            slot=slot,
                            origins=int(mask.sum()),
                            sessions=rows.loc[mask, "session_date_et"].nunique(),
                            stock_rows=int(mask.sum()) * 20,
                            metadata_finite_fraction=1.0,
                        )
                    )
                    coverage.append(
                        dict(
                            year=year,
                            phase=phase,
                            role=role,
                            slot=slot,
                            missing_minute_flag_fraction=float(
                                (q["assumed_zero_minute_count"][mask] > 0).mean()
                            ),
                            proxy_flag_fraction=float(
                                (q["price_proxy_minute_count"][mask] > 0).mean()
                            ),
                            fallback_fraction=float((q["feature_fallback_cells"][mask] > 0).mean()),
                            max_terminal_age=float(
                                np.nanmax(q["max_terminal_price_age_minutes"][mask])
                            ),
                            metadata_source_flags_used=False,
                        )
                    )
    pd.DataFrame(counts).to_csv(out / "S5_S9_ROLE_COUNTS.csv", index=False)
    pd.DataFrame(coverage).to_csv(out / "S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv", index=False)
    refs = []
    for year in range(2021, 2025):
        for phase in ("inner", "refit"):
            p = S4 / f"F{year % 100}_{phase}_recipe.json"
            refs.append(dict(path=str(p), sha256=digest(p)))
    (out / "S4_REUSED_RECIPES.json").write_text(json.dumps(refs, indent=2) + "\n")


def rehearsal(data: Data, out: Path) -> list[dict]:
    """One representative source workflow per arm; two batches, four role exports each."""
    saved = data.base.plans
    plan, masks = saved[2021]
    small = {}
    for role, mask in masks.items():
        chosen = data.base.rows.loc[mask, "session_date_et"].drop_duplicates().iloc[:2]
        small[role] = mask & data.base.rows.session_date_et.isin(chosen).to_numpy()
    data.base.plans = saved.copy()
    data.base.plans[2021] = (plan, small)
    results = []
    try:
        for arm in ARMS:
            dest = out / "rehearsal" / arm
            dest.mkdir(parents=True)
            recipes = {
                p: dict(
                    year=2021,
                    phase=p,
                    rehearsal_only=True,
                    prefix_fitted=False,
                    gap_cap=4.0,
                    magnitude_scale=0.01,
                    event_cutoff=2.0,
                    tail_y95=2.0,
                    tail_y99=4.0,
                    num95=0.01,
                    mad05=0.001,
                    abs_r95=0.02,
                    abs_r99=0.04,
                )
                for p in ("inner", "refit")
            }
            for phase in recipes:
                (dest / f"{phase}_target_recipe.json").write_text(
                    json.dumps(recipes[phase], indent=2) + "\n"
                )
            hashes = []
            exports = 0
            for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
                data.phase(2021, phase, recipes[phase])
                model = model_for(arm)
                opt = optimizer(model)
                first = initial_hash(model)
                hashes.append(first)
                pos = data.base.positions(2021, roles[0])
                x, r, y = data.arrays(pos, arm)
                original, _, _ = data.base.arrays(pos)
                np.testing.assert_array_equal(x[..., :16], original)
                if arm == "META-T2R":
                    rows = data.base.rows.iloc[pos]
                    assert (
                        pd.DatetimeIndex(
                            data.base.grid.hour_end_utc.iloc[rows.entry_index.to_numpy(int)]
                        ).to_numpy(dtype="datetime64[ns]")
                        <= pd.DatetimeIndex(rows.issuance_utc).to_numpy(dtype="datetime64[ns]")
                    ).all()
                with patch.object(
                    torch.optim.AdamW,
                    "step",
                    side_effect=AssertionError("OPTIMIZER_STEP_FORBIDDEN"),
                ) as blocked:
                    receipt = epoch(
                        data,
                        pos,
                        model,
                        opt,
                        arm,
                        1,
                        "calibration" if phase == "inner" else "refit",
                        dest,
                        update=False,
                    )
                    if (
                        blocked.call_count
                        or receipt["steps"]
                        or opt.state
                        or initial_hash(model) != first
                    ):
                        raise ValueError("S5S9_REHEARSAL_UPDATED")
                from .hf20_s5s9_run import off

                saved_receipt = dict(receipt)
                if phase == "inner":
                    saved_receipt["inner_train_off"] = off(
                        data, pos, predict(data, pos, model, arm), arm
                    )
                    vp = data.base.positions(2021, "inner_validation")
                    saved_receipt["inner_validation_off"] = off(
                        data, vp, predict(data, vp, model, arm), arm
                    )
                else:
                    saved_receipt["refit_off"] = off(data, pos, predict(data, pos, model, arm), arm)
                (dest / f"{'calibration' if phase == 'inner' else 'refit'}_001.json").write_text(
                    json.dumps(saved_receipt, indent=2) + "\n"
                )
                checkpoint = dest / f"{phase}_zero_step.pt"
                torch.save(model.state_dict(), checkpoint)
                loaded = model_for(arm)
                loaded.load_state_dict(torch.load(checkpoint, weights_only=True))
                binding = "calibration_binding.json" if phase == "inner" else "refit_binding.json"
                (dest / binding).write_text(
                    json.dumps(
                        dict(
                            rehearsal_only=True,
                            selected=0,
                            checkpoint=str(checkpoint),
                            checkpoint_sha256=digest(checkpoint),
                            reload_max_error=0,
                        ),
                        indent=2,
                    )
                    + "\n"
                )
                for role in roles:
                    positions = data.base.positions(2021, role)
                    raw = predict(data, positions, model, arm)
                    np.testing.assert_array_equal(raw, predict(data, positions, loaded, arm))
                    export(data, 2021, role, arm, raw, dest, recipes[phase])
                    exports += 1
            if hashes[0] != hashes[1]:
                raise ValueError("S5S9_FRESH_REHEARSAL_RESET")
            # Exercise the real report route with fixed toy controls and no fitted parameters.
            with patch(
                "lstm_data.hf20_s5s9_report.fit_control",
                side_effect=AssertionError("NO_REAL_CONTROL_FIT"),
            ):
                finish_run(data, 2021, arm, dest, recipes, dry=True)
            result = dict(
                arm=arm,
                status="PASS_UNTRAINED_WORKFLOW",
                roles=exports,
                batches=2,
                optimizer_step_calls=0,
                starts=0,
                prefix_fits=0,
                baseline_fits=0,
                input_dim=22 if arm == "META-T2R" else 16,
                initial_sha256=hashes[0],
            )
            (dest / "REHEARSAL.json").write_text(json.dumps(result, indent=2) + "\n")
            results.append(result)
            print("zero-step family PASS", arm, flush=True)
    finally:
        data.base.plans = saved
    return results


def prepare(out: Path) -> None:
    if (out / "SOURCE_AND_REHEARSAL.json").exists():
        raise ValueError("USE_NEW_PREPARATION_NAMESPACE")
    started = time.monotonic()
    before = POINTER.read_bytes()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    data = Data()
    print("permitted S4 source loaded", flush=True)
    prior = out.parent
    cached = [
        "S5_S9_ROLE_COUNTS.csv",
        "S5_CAUSAL_COVERAGE_AND_DIAGNOSTIC_STRATA.csv",
        "S4_REUSED_RECIPES.json",
    ]
    if all((prior / name).exists() for name in cached):
        for name in cached:
            (out / name).write_bytes((prior / name).read_bytes())
        (out / "SOURCE_AUDIT_REUSED.json").write_text(
            json.dumps(
                [dict(path=str(prior / name), sha256=digest(prior / name)) for name in cached],
                indent=2,
            )
            + "\n"
        )
    else:
        source_audit(data, out)
    print("all 16 fold-role populations exactly S4", flush=True)
    results = rehearsal(data, out)
    if POINTER.read_bytes() != before:
        raise ValueError("PREPARATION_CHANGED_LEDGER")
    from .hf20_s5s9_visual import dashboard

    dashboard(out, rehearsal=True)
    receipt = dict(
        status="PASS_SOURCE_AND_FOUR_UNTRAINED_WORKFLOWS",
        results=results,
        metadata_fields=META_FIELDS,
        run_ids=RUNS,
        ledger=114,
        neural_starts=0,
        target_or_baseline_fits=0,
        protected_reads_or_hashes=0,
        seconds=time.monotonic() - started,
        resources=resources(out),
    )
    (out / "SOURCE_AND_REHEARSAL.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("S5S9_SOURCE_REHEARSAL_PASS", receipt["seconds"], flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    prepare(p.parse_args().out)
