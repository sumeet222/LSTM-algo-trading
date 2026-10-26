"""Approved bounded S3-A then S3-B fitting, complete role diagnostics and PASS gates."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from .config import now
from .hf20_horizon_authority import JOURNAL, Journal, authorize, execution_hash
from .hf20_horizon_data import ROLES, HorizonData
from .hf20_horizon_diagnostics import export, pass_gate, source_cases
from .hf20_horizon_preflight import ledger
from .hf20_ranking import (
    GRID,
    YEARS,
    RankSelector,
    daily_ic,
    origin_weights,
    rank_targets,
    ridge_solution,
    ridge_system,
    row_loss,
)
from .hf20_ranking_authority import resources
from .hf20_ranking_continue import check_configuration, isolated_neural_failure
from .hf20_ranking_data import FoldData, assemble
from .hf20_ranking_run import POINTER, initial_hash, predict, sha, write
from .neural_engine import SharedLSTM, optimizer, seed_all


def epoch(
    model: SharedLSTM,
    opt: torch.optim.AdamW,
    data: HorizonData,
    positions: np.ndarray,
    arm: str,
    number: int,
    phase: str,
    dest: Path,
    *,
    update: bool = True,
) -> dict:
    """Same S2 arithmetic/batch order; additional per-parameter gradient incidence."""
    groups = data.rows.iloc[positions].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    telemetry, gradients = [], []
    model.train()
    for start in range(0, len(days), 16):
        chosen = days[start : start + 16]
        pos = positions[np.concatenate([groups[d] for d in chosen])]
        x, r, y = data.arrays(pos)
        w = origin_weights(data.rows.iloc[pos].session_date_et.to_numpy())
        opt.zero_grad()
        raw = model(torch.from_numpy(x.reshape(-1, 48, 16))).reshape(-1, 20)
        loss = (
            row_loss(
                arm,
                raw,
                torch.from_numpy(r),
                torch.from_numpy(y.astype(np.float32)),
                data.recipe["t2_scale"],
            ).sum(1)
            * torch.from_numpy(w.astype(np.float32))
        ).sum()
        if not bool(torch.isfinite(loss)):
            raise ValueError("S3_NONFINITE_ONLINE_LOSS")
        loss.backward()
        for name, p in model.named_parameters():
            g = p.grad
            if g is None or not bool(torch.isfinite(g).all()):
                raise ValueError("S3_MISSING_OR_NONFINITE_PARAMETER_GRADIENT")
            gradients.append(
                dict(
                    phase=phase,
                    epoch=number,
                    batch=start // 16,
                    parameter=name,
                    cells=g.numel(),
                    nonzero=int(torch.count_nonzero(g)),
                    norm=float(torch.linalg.vector_norm(g)),
                )
            )
        before = [p.detach().clone() for p in model.parameters()]
        pre = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        )
        post = math.sqrt(
            sum(float(p.grad.square().sum()) for p in model.parameters() if p.grad is not None)
        )
        if update:
            opt.step()
        delta = math.sqrt(
            sum(float((p.detach() - b).square().sum()) for p, b in zip(model.parameters(), before))
        )
        if not all(bool(torch.isfinite(p).all()) for p in model.parameters()) or post > 1.00001:
            raise ValueError("S3_NONFINITE_WEIGHTS_OR_CLIP")
        telemetry.append(
            dict(
                phase=phase,
                epoch=number,
                batch=start // 16,
                preclip=pre,
                postclip=post,
                update_norm=delta,
                sessions=len(chosen),
                online_loss=float(loss.detach()),
                parameter_norm=math.sqrt(
                    sum(float(p.detach().square().sum()) for p in model.parameters())
                ),
            )
        )
    pd.DataFrame(telemetry).to_csv(dest / f"{phase}_{number:03d}_batches.csv", index=False)
    pd.DataFrame(gradients).to_csv(dest / f"{phase}_{number:03d}_gradients.csv", index=False)
    return dict(
        phase=phase,
        epoch=number,
        steps=len(telemetry) if update else 0,
        batches=len(telemetry),
        dropout_on=True,
        online_objective=float(
            np.average(
                [r["online_loss"] for r in telemetry], weights=[r["sessions"] for r in telemetry]
            )
        ),
    )


def group_path(out: Path, stage: str, year: int, h: int) -> Path:
    p = out / stage / f"F{year % 100}_H{h}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def prepare(out: Path) -> None:
    """Real prefix transforms permitted by live authority; no empirical model/optimizer fit."""
    authorize(out)
    ledger(out)
    (out / "targets").mkdir(exist_ok=True)
    base = FoldData(live_approved=True)
    checks, replays = [], []
    for stage in ("A", "B"):
        for h in (1, 2):
            data = HorizonData(base, h, stage)
            for year in YEARS:
                group = group_path(out, stage, year, h)
                for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
                    data.phase(year, phase, group)
                    for role in roles:
                        pos = data.positions(year, role)
                        for start in range(0, len(pos), 32):
                            xx, r, y = data.arrays(pos[start : start + 32])
                            original = assemble(
                                data.rows.iloc[pos[start : start + 32]], base.common, base.m2
                            )
                            np.testing.assert_array_equal(
                                xx[..., np.arange(16) != 1], original[..., np.arange(16) != 1]
                            )
                            np.testing.assert_array_equal(rank_targets(r), rank_targets(y))
                        data.rows.iloc[pos].to_csv(
                            group / f"F{year % 100}_{role}_indices.csv", index=False
                        )
                        checks.append(
                            dict(
                                stage=stage,
                                horizon=h,
                                year=year,
                                phase=phase,
                                role=role,
                                origins=len(pos),
                                non_M2_bitwise=True,
                                target_rank_identity=True,
                            )
                        )
                    # Full actual training/checkpoint/export/gate chain, with zero optimizer calls.
                    for arm in ("T2R", "NR"):
                        with tempfile.TemporaryDirectory(prefix="s3_rehearsal_", dir=out) as tmp:
                            dest = Path(tmp)
                            seed_all(42)
                            model = SharedLSTM().float()
                            initial = initial_hash(model)
                            opt = optimizer(model)
                            check_configuration(model, opt)
                            pos = data.positions(year, roles[0])
                            selected_days = (
                                data.rows.iloc[pos].session_date_et.drop_duplicates().iloc[:16]
                            )
                            subset = pos[
                                data.rows.iloc[pos].session_date_et.isin(selected_days).to_numpy()
                            ]
                            with patch.object(
                                torch.optim.AdamW,
                                "step",
                                side_effect=AssertionError("ZERO_STEP_GUARD"),
                            ) as guard:
                                receipt = epoch(
                                    model, opt, data, subset, arm, 1, phase, dest, update=False
                                )
                                if guard.call_count or initial_hash(model) != initial or opt.state:
                                    raise ValueError("S3_REHEARSAL_UPDATED_STATE")
                                torch.save(model.state_dict(), dest / "untrained.pt")
                                fresh = SharedLSTM().float()
                                fresh.load_state_dict(
                                    torch.load(dest / "untrained.pt", weights_only=True)
                                )
                                checkpos = data.positions(year, roles[1])
                                np.testing.assert_array_equal(
                                    predict(data, checkpos, model), predict(data, checkpos, fresh)
                                )
                                binding = dict(
                                    checkpoint=str(dest / "untrained.pt"),
                                    checkpoint_sha256=sha(dest / "untrained.pt"),
                                )
                                write(
                                    dest
                                    / (
                                        "calibration_binding.json"
                                        if phase == "inner"
                                        else "refit_binding.json"
                                    ),
                                    binding,
                                )
                                # Replay the inherited parent recipe lookup.
                                recipe_link = out / f"F{year % 100}_{phase}_recipe.json"
                                if recipe_link.exists():
                                    raise ValueError("S3_TEMP_RECIPE_COLLISION")
                                recipe_link.write_bytes((group / recipe_link.name).read_bytes())
                                try:
                                    export(
                                        data,
                                        year,
                                        roles[1],
                                        arm,
                                        predict(data, checkpos, fresh),
                                        dest,
                                        execution_hash(),
                                    )
                                finally:
                                    recipe_link.unlink()
                            replays.append(
                                dict(
                                    stage=stage,
                                    horizon=h,
                                    year=year,
                                    phase=phase,
                                    arm=arm,
                                    optimizer_step_calls=0,
                                    training_batches=receipt["batches"],
                                    full_role_reload_origins=len(checkpos),
                                    checkpoint_exact=True,
                                )
                            )
                gc.collect()
            del data
            gc.collect()
    pd.DataFrame(checks).to_csv(out / "FULL_POPULATION_READINESS.csv", index=False)
    pd.DataFrame(replays).to_csv(out / "ZERO_STEP_WORKFLOW_REHEARSAL.csv", index=False)
    write(
        out / "READINESS_PASS.json",
        dict(
            status="PASS",
            populations=len(checks),
            workflows=len(replays),
            optimizer_steps=0,
            empirical_model_fits=0,
            fitted_target_recipes=16,
            fitted_B_M2_recipes=16,
            reused_original_FT16_recipes=8,
            resources=resources(out),
        ),
    )


def gate_rehearsal(out: Path) -> None:
    """Full four-role saved-state gate, including witnesses; no optimizer method called."""
    authorize(out)
    base = FoldData(live_approved=True)
    receipts = []
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("ZERO_STEP_GUARD")
    ) as guard:
        for stage in ("A", "B"):
            for h in (1, 2):
                data = HorizonData(base, h, stage)
                group = group_path(out, stage, 2024, h)
                for arm in ("T2R", "NR"):
                    print(f"GATE REHEARSAL stage={stage} h={h} arm={arm}", flush=True)
                    with tempfile.TemporaryDirectory(prefix="gate_rehearsal_", dir=group) as tmp:
                        dest = Path(tmp)
                        for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
                            seed_all(42)
                            model = SharedLSTM().float()
                            opt = optimizer(model)
                            check_configuration(model, opt)
                            data.phase(2024, phase, group)
                            checkpoint = dest / f"{phase}.pt"
                            torch.save(
                                dict(model=model.state_dict(), optimizer=opt.state_dict()),
                                checkpoint,
                            )
                            fresh = SharedLSTM().float()
                            fresh.load_state_dict(
                                torch.load(checkpoint, weights_only=True)["model"]
                            )
                            write(
                                dest
                                / (
                                    "calibration_binding.json"
                                    if phase == "inner"
                                    else "refit_binding.json"
                                ),
                                dict(checkpoint=str(checkpoint), checkpoint_sha256=sha(checkpoint)),
                            )
                            for role in roles:
                                pos = data.positions(2024, role)
                                scores = predict(data, pos, model)
                                np.testing.assert_array_equal(scores, predict(data, pos, fresh))
                                export(data, 2024, role, arm, scores, dest, execution_hash())
                        source_cases(data, 2024, dest)
                        pass_gate(data, 2024, dest, untrained_rehearsal=True)
                        receipts.append(
                            dict(
                                stage=stage,
                                horizon=h,
                                year=2024,
                                arm=arm,
                                four_roles=True,
                                checkpoint_exact=True,
                                witnesses=True,
                            )
                        )
                del data
                gc.collect()
        if guard.call_count:
            raise ValueError("S3_GATE_REHEARSAL_OPTIMIZER_CALL")
    write(
        out / "FULL_STAGE_GATE_REHEARSAL.json",
        dict(status="PASS", workflows=receipts, optimizer_step_calls=0, resources=resources(out)),
    )


def fit_baselines(base: FoldData, out: Path, journal: Journal) -> None:
    for year in YEARS:
        for h in (1, 2):
            data = HorizonData(base, h, "A")
            group = group_path(out, "A", year, h)
            data.phase(year, "inner", group)
            fp, vp = data.positions(year, "inner_train"), data.positions(year, "inner_validation")
            profiles = []
            for arm in ("P", "LR"):
                dest = group / arm
                dest.mkdir()
                candidates, system = [], None
                for penalty in (None,) if arm == "P" else GRID:
                    key = f"F{year % 100}/H{h}/{arm}/inner/{penalty}"
                    journal.baseline(key, "STARTED")
                    try:
                        if arm == "P":
                            coef = np.average(
                                rank_targets(data.returns[fp]),
                                axis=0,
                                weights=origin_weights(
                                    data.rows.iloc[fp].session_date_et.to_numpy()
                                ),
                            )
                        else:
                            if system is None:
                                system = ridge_system(data.linear_stream(fp))
                            coef = ridge_solution(
                                *system, float(penalty if penalty is not None else 0)
                            )
                        np.save(dest / f"inner_{penalty}.npy", coef)
                        ic = daily_ic(
                            data.returns[vp],
                            predict(data, vp, coef),
                            data.rows.iloc[vp].session_date_et.to_numpy(),
                        )
                        if not np.isfinite(ic):
                            raise ValueError("S3_UNDEFINED_BASELINE_SELECTION")
                        candidates.append(dict(penalty=penalty, ic=ic))
                        journal.baseline(key, "COMPLETED", dict(ic=ic))
                    except np.linalg.LinAlgError as error:
                        journal.baseline(key, "FAILED", dict(isolated=True, message=str(error)))
                    except BaseException as error:
                        journal.baseline(key, "FAILED", dict(isolated=False, message=str(error)))
                        raise
                if not candidates:
                    write(
                        dest / "UNAVAILABLE.json",
                        dict(reason="All declared candidates failed; no retry"),
                    )
                    continue
                selected = max(candidates, key=lambda r: (r["ic"], r["penalty"] or 0))
                write(dest / "selection.json", dict(candidates=candidates, selected=selected))
                coef = np.load(dest / f"inner_{selected['penalty']}.npy")
                for role in ROLES[:2]:
                    export(
                        data,
                        year,
                        role,
                        arm,
                        predict(data, data.positions(year, role), coef),
                        dest,
                        journal.execution,
                    )
                profiles.append((arm, dest, selected))
            data.phase(year, "refit", group)
            rp = data.positions(year, "refit")
            for arm, dest, selected in profiles:
                key = f"F{year % 100}/H{h}/{arm}/refit/" + (
                    "None" if arm == "P" else "INNER_SELECTED"
                )
                journal.baseline(key, "STARTED")
                try:
                    if arm == "P":
                        coef = np.average(
                            rank_targets(data.returns[rp]),
                            axis=0,
                            weights=origin_weights(data.rows.iloc[rp].session_date_et.to_numpy()),
                        )
                    else:
                        coef = ridge_solution(
                            *ridge_system(data.linear_stream(rp)), float(selected["penalty"])
                        )
                    np.save(dest / "refit_coefficients.npy", coef)
                    for role in ROLES[2:]:
                        export(
                            data,
                            year,
                            role,
                            arm,
                            predict(data, data.positions(year, role), coef),
                            dest,
                            journal.execution,
                        )
                    pass_gate(data, year, dest)
                    journal.baseline(key, "COMPLETED", dict(gate=str(dest / "PASS.json")))
                except np.linalg.LinAlgError as error:
                    journal.baseline(key, "FAILED", dict(isolated=True, message=str(error)))
                except BaseException as error:
                    journal.baseline(key, "FAILED", dict(isolated=False, message=str(error)))
                    raise
            data.phase(year, "refit", group)
            for arm in ("N0", "N1", "N2"):
                dest = group / arm
                dest.mkdir()
                pos = data.positions(year, "oos")
                export(data, year, "oos", arm, predict(data, pos, arm), dest, journal.execution)
            print(f"BASELINES PASS F{year % 100} H{h} attempts={journal.baselines}", flush=True)
            del data
            gc.collect()
    write(
        out / "BASELINE_PASS.json",
        dict(status="PASS_TECHNICAL", attempts=journal.baselines, resources=resources(out)),
    )


def neural_one(
    base: FoldData, out: Path, journal: Journal, stage: str, year: int, h: int, arm: str
) -> None:
    data = HorizonData(base, h, stage)
    group = group_path(out, stage, year, h)
    data.phase(year, "inner", group)
    run = f"HF20-S3{stage}-F{year % 100}-H{h}-{arm}-S42"
    dest = group / run
    dest.mkdir()
    journal.event(run, "STARTED", dict(stage=stage, horizon=h, year=year, arm=arm))
    print(f"START {journal.started} {run}", flush=True)
    began = time.monotonic()
    p: np.ndarray | None = None
    try:
        seed_all(42)
        model = SharedLSTM().float()
        initial = initial_hash(model)
        opt = optimizer(model)
        write(dest / "calibration_configuration.json", check_configuration(model, opt))
        selector = RankSelector()
        fp, vp = data.positions(year, "inner_train"), data.positions(year, "inner_validation")
        for n in range(1, 61):
            resources(out)
            receipt = epoch(model, opt, data, fp, arm, n, "calibration", dest)
            p = predict(data, vp, model)
            ic = daily_ic(data.returns[vp], p, data.rows.iloc[vp].session_date_et.to_numpy())
            qualifies = selector.observe(n, ic)
            torch.save(model.state_dict(), dest / f"calibration_{n:03d}.pt")
            write(
                dest / f"calibration_{n:03d}.json",
                dict(**receipt, ic=ic, qualifies=qualifies, selector=vars(selector).copy()),
            )
            print(f"{run} epoch={n} IC={ic:.8f} selected={selector.selected}", flush=True)
            if selector.stop(n):
                break
        torch.save(opt.state_dict(), dest / "calibration_stop_optimizer.pt")
        selected = dest / f"calibration_{selector.selected:03d}.pt"
        model.load_state_dict(torch.load(selected, weights_only=True))
        write(
            dest / "calibration_binding.json",
            dict(
                checkpoint=str(selected),
                checkpoint_sha256=sha(selected),
                selected=selector.selected,
                raw_best_epoch=selector.raw_epoch,
                recipe=str(group / f"F{year % 100}_inner_recipe.json"),
            ),
        )
        for role in ROLES[:2]:
            pos = data.positions(year, role)
            export(data, year, role, arm, predict(data, pos, model), dest, journal.execution)
        journal.event(run, "CALIBRATED", vars(selector).copy())
        journal.event(run, "REFITTING", dict(selected_epoch=selector.selected))
        seed_all(42)
        model = SharedLSTM().float()
        if initial_hash(model) != initial:
            raise ValueError("S3_FRESH_SEED_MISMATCH")
        opt = optimizer(model)
        if opt.state:
            raise ValueError("S3_OPTIMIZER_NOT_FRESH")
        write(dest / "refit_configuration.json", check_configuration(model, opt))
        data.phase(year, "refit", group)
        rp = data.positions(year, "refit")
        for n in range(1, selector.selected + 1):
            resources(out)
            write(dest / f"refit_{n:03d}.json", epoch(model, opt, data, rp, arm, n, "refit", dest))
        checkpoint = dest / "refit_final.pt"
        torch.save(dict(model=model.state_dict(), optimizer=opt.state_dict()), checkpoint)
        replay = SharedLSTM().float()
        saved = torch.load(checkpoint, weights_only=True)
        replay.load_state_dict(saved["model"])
        expected = selector.selected * math.ceil(data.rows.iloc[rp].session_date_et.nunique() / 16)
        if any(int(s["step"]) != expected for s in saved["optimizer"]["state"].values()):
            raise ValueError("S3_SAVED_OPTIMIZER_STEP_COUNT")
        write(
            dest / "refit_binding.json",
            dict(
                checkpoint=str(checkpoint),
                checkpoint_sha256=sha(checkpoint),
                selected=selector.selected,
                optimizer_updates=expected,
                recipe=str(group / f"F{year % 100}_refit_recipe.json"),
            ),
        )
        for role in ROLES[2:]:
            pos = data.positions(year, role)
            p = predict(data, pos, model)
            np.testing.assert_array_equal(p, predict(data, pos, replay))
            export(data, year, role, arm, p, dest, journal.execution)
        pass_gate(
            data,
            year,
            dest,
            selector=vars(selector),
            seconds=time.monotonic() - began,
            initial_sha256=initial,
            checkpoint_reload_max_error=0,
            resources=resources(out),
        )
        journal.event(
            run, "COMPLETED", dict(gate=str(dest / "PASS.json"), selected_epoch=selector.selected)
        )
        print(f"COMPLETED {run} ledger={journal.started}", flush=True)
    except BaseException as error:
        isolation = isolated_neural_failure(error, data, year, p)
        write(
            dest / "FAILURE.json",
            dict(error_type=type(error).__name__, message=str(error), **isolation),
        )
        journal.event(
            run, "FAILED", dict(error_type=type(error).__name__, message=str(error), **isolation)
        )
        if not isolation["isolated"]:
            raise


def run(out: Path) -> None:
    authorize(out)
    if JOURNAL.exists() or (out / "EXECUTION_STARTED.json").exists():
        raise ValueError("S3_NO_CAMPAIGN_RETRY")
    manifest = json.loads((out / "EXECUTION_MANIFEST.json").read_text())
    if manifest["execution_sha256"] != execution_hash():
        raise ValueError("S3_SEALED_EXECUTION_MISMATCH")
    if json.loads((out / "READINESS_PASS.json").read_text())["status"] != "PASS":
        raise ValueError("S3_READINESS_REQUIRED")
    if json.loads((out / "FULL_STAGE_GATE_REHEARSAL.json").read_text())["status"] != "PASS":
        raise ValueError("S3_COMPLETE_GATE_REHEARSAL_REQUIRED")
    if json.loads(POINTER.read_text()) != json.loads(
        (out / "prior_registry_pointer.json").read_text()
    ):
        raise ValueError("S3_PRIOR_LEDGER_POINTER_CHANGED")
    write(
        out / "EXECUTION_STARTED.json",
        dict(at=now(), pid=os.getpid(), execution_sha256=execution_hash()),
    )
    journal = Journal(out)
    try:
        base = FoldData(live_approved=True)
        fit_baselines(base, out, journal)
        for stage in ("A", "B"):
            for year in YEARS:
                for h in (1, 2):
                    for arm in ("T2R", "NR"):
                        neural_one(base, out, journal, stage, year, h, arm)
                        gc.collect()
            from .hf20_horizon_report import stage_report

            stage_report(out, stage)
            write(
                out / f"S3{stage}_PASS.json",
                dict(
                    status="PASS_TECHNICAL",
                    performance_gated=False,
                    ledger=journal.started,
                    resources=resources(out),
                ),
            )
    except BaseException as error:
        write(
            out / "FATAL_STOP.json",
            dict(
                at=now(),
                error_type=type(error).__name__,
                message=str(error),
                ledger=journal.started,
                baseline_attempts=journal.baselines,
                no_retry=True,
            ),
        )
        raise
    write(
        out / "FITTING_FINISHED.json",
        dict(
            at=now(),
            ledger=journal.started,
            baseline_attempts=journal.baselines,
            resources=resources(out),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--gate-rehearsal", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if sum((args.prepare, args.run, args.gate_rehearsal)) != 1:
        raise ValueError("S3_EXACT_ONE_MODE")
    if args.prepare:
        prepare(args.out)
    elif args.gate_rehearsal:
        gate_rehearsal(args.out)
    else:
        run(args.out)


if __name__ == "__main__":
    main()
