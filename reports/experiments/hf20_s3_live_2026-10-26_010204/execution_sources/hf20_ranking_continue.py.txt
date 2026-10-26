"""Prospectively authorized HF20 continuation: reuse F21, defer LP, isolate failures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import time
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch

from .config import fingerprint, now
from .hf20_ranking import (
    ARMS,
    GRID,
    RUNS,
    YEARS,
    RankSelector,
    daily_ic,
    origin_weights,
    rank_targets,
    ridge,
    ridge_solution,
    ridge_system,
)
from .hf20_ranking_authority import resources
from .hf20_ranking_data import FoldData, fold_masks
from .hf20_ranking_diagnostics import export_diagnostics, verify_exports
from .hf20_ranking_run import CODE, POINTER, code_hash, epoch, initial_hash, predict, sha, write
from .neural_engine import SharedLSTM, optimizer, seed_all
from .real_batch_authority import atomic_replace_json

MANIFEST = "CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json"
NEW_CODE = (
    "src/lstm_data/hf20_ranking_continue.py",
    "src/lstm_data/hf20_ranking_continue_report.py",
)
NEURAL_JOURNAL = Path("reports/audit/track_a_real_pairs_v19_hf20_ranking_continuation.jsonl")
DEFINITION = Path(
    "configs/track_a_candidate_experiment_registry_v19_hf20_ranking_continuation.json"
)


def continuation_hash() -> str:
    return hashlib.sha256(
        json.dumps({p: sha(Path(p)) for p in (*CODE, *NEW_CODE)}, sort_keys=True).encode()
    ).hexdigest()


def baseline_plan() -> list[str]:
    keys = []
    for year in YEARS:
        if year != 2021:
            keys += [f"F{year % 100}/P/inner/None"]
            keys += [f"F{year % 100}/LR/inner/{penalty}" for penalty in GRID]
        keys += [f"F{year % 100}/P/refit", f"F{year % 100}/LR/refit"]
    return keys


def validate_events(history: list[dict]) -> list[dict]:
    states: dict[str, str] = {}
    count = 0
    transitions = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "COMPLETED": set(),
        "FAILED": set(),
    }
    for i, row in enumerate(history):
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("CONTINUATION_JOURNAL_CHAIN")
        run, status = row["run_id"], row["status"]
        if status == "STARTED":
            if count >= 12 or run != RUNS[count] or run in states:
                raise ValueError("NO_RETRY_EXTRA_OR_REORDER")
            if (
                i
                and history[i - 1]["status"] != "COMPLETED"
                and not (
                    history[i - 1]["status"] == "FAILED"
                    and history[i - 1]["detail"].get("isolated") is True
                )
            ):
                raise ValueError("PREVIOUS_SHARED_FATAL_OR_INCOMPLETE")
            count += 1
        elif run not in states or status not in transitions[states[run]]:
            raise ValueError("CONTINUATION_TRANSITION")
        if row["global_started_pairs"] != 62 + count or row["effective_ceiling"] != 200:
            raise ValueError("CONTINUATION_NEURAL_BUDGET")
        states[run] = status
    return history


class ContinuationJournal:
    """Original eight attempts are references; new baseline attempts and charged starts append."""

    def __init__(self, out: Path, manifest: dict):
        self.out, self.manifest = out, manifest
        self.baseline_keys: list[str] = []
        self.original = json.loads((out / "prior_registry_pointer.json").read_text())
        self.started = 62

    def baseline(self, key: str, status: str, detail: dict | None = None) -> None:
        if key not in baseline_plan() or "/LP/" in key:
            raise ValueError("UNAUTHORIZED_BASELINE_OR_LP")
        if status == "STARTED":
            resources(self.out)
            if key in self.baseline_keys or len(self.baseline_keys) >= 29:
                raise ValueError("NO_BASELINE_RETRY_OR_EXTRA")
            if self.baseline_keys and baseline_plan().index(key) <= baseline_plan().index(
                self.baseline_keys[-1]
            ):
                raise ValueError("BASELINE_ORDER")
            self.baseline_keys.append(key)
        elif key not in self.baseline_keys:
            raise ValueError("BASELINE_NOT_STARTED")
        row = dict(
            at=now(),
            key=key,
            status=status,
            attempt=8 + len(self.baseline_keys),
            neural_charge=0,
            detail=detail or {},
        )
        with (self.out / "baseline_continuation_events.jsonl").open("a") as f:
            f.write(json.dumps(row, allow_nan=False) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def event(self, run: str, status: str, detail: dict) -> None:
        if continuation_hash() != self.manifest["execution_sha256"]:
            raise ValueError("CONTINUATION_EXECUTION_CHANGED")
        lock = NEURAL_JOURNAL.with_suffix(".lock")
        with lock.open("x"):
            pass
        try:
            raw = NEURAL_JOURNAL.read_bytes() if NEURAL_JOURNAL.exists() else b""
            if raw and not raw.endswith(b"\n"):
                raise ValueError("TRUNCATED_CONTINUATION_JOURNAL")
            history = validate_events([json.loads(r) for r in raw.splitlines()])
            if status == "STARTED":
                resources(self.out)
                if not (self.out / "STAGE_B_HANDOFF.json").exists():
                    raise ValueError("COMMON_READINESS_HANDOFF_REQUIRED")
                if history and history[-1]["status"] == "COMPLETED":
                    gate = json.loads((self.out / history[-1]["run_id"] / "PASS.json").read_text())
                    if gate["status"] != "PASS_TECHNICAL":
                        raise ValueError("PRIOR_OUTPUT_GATE")
                    for path, expected in gate["files"].items():
                        if sha(Path(path)) != expected:
                            raise ValueError("PRIOR_VERIFIED_OUTPUT_CHANGED")
                elif history and history[-1]["detail"].get("isolated") is not True:
                    raise ValueError("PRIOR_FAILURE_NOT_INDEPENDENTLY_ISOLATED")
            self.started = (
                62 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
            )
            row = dict(
                sequence=len(history) + 1,
                previous=fingerprint(history),
                at=now(),
                run_id=run,
                status=status,
                global_started_pairs=self.started,
                effective_ceiling=200,
                plan=dict(path=str(self.out / MANIFEST), sha256=sha(self.out / MANIFEST)),
                authority=dict(
                    path=str(self.out / "submitted_continuation_authority.txt"),
                    sha256=sha(self.out / "submitted_continuation_authority.txt"),
                ),
                previous_journal=dict(
                    path=self.original["real_journal"],
                    sha256=sha(Path(self.original["real_journal"])),
                ),
                detail=detail,
            )
            validate_events(history + [row])
            with NEURAL_JOURNAL.open("ab") as f:
                f.write((json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode())
                f.flush()
                os.fsync(f.fileno())
            if not DEFINITION.exists():
                write(
                    DEFINITION,
                    dict(
                        schema_version=19,
                        package="HF20_S1_S2_CONTINUATION",
                        runs=list(RUNS),
                        plan=row["plan"],
                        previous_journal=row["previous_journal"],
                    ),
                )
            atomic_replace_json(
                POINTER,
                dict(
                    schema_version=19,
                    definition=dict(path=str(DEFINITION), sha256=sha(DEFINITION)),
                    plan=row["plan"],
                    real_journal=str(NEURAL_JOURNAL),
                    previous_journal=row["previous_journal"],
                    counts_started_including_failed=True,
                    effective_ceiling=200,
                    fit_permission=False,
                    live_approval_required=True,
                    budget_amendment=self.original["budget_amendment"],
                ),
            )
        finally:
            lock.unlink()


def export(data: FoldData, year: int, role: str, arm: str, score: np.ndarray, dest: Path) -> dict:
    """Reuse immutable helper units; bind the actual new executor in a companion receipt."""
    result = export_diagnostics(data, year, role, arm, score, dest)
    case_ref = None
    if role == "oos" and arm in ARMS and (dest.parent / "shared_source_case_keys.csv").exists():
        keys = pd.read_csv(dest.parent / "shared_source_case_keys.csv")
        keys = keys.loc[keys.year.eq(year)]
        positions = np.array(
            [int(np.flatnonzero(data.rows.origin_id.eq(k))[0]) for k in keys.origin_id]
        )
        x, r, y = data.arrays(positions)
        j = np.array([data.symbols.index(t) for t in keys.ticker])
        chosen = x[np.arange(len(keys)), j]
        path = dest.parent / f"F{year % 100}_refit_source_case_inputs.npz"
        if path.exists():
            with np.load(path) as saved:
                np.testing.assert_array_equal(saved["inputs"], chosen)
                np.testing.assert_array_equal(saved["returns20"], r)
        else:
            np.savez_compressed(
                path, inputs=chosen, returns20=r, TG20_20=y, case_id=keys.case_id.to_numpy()
            )
        case_ref = dict(path=str(path), sha256=sha(path), shared_across_neural_families=True)
    write(
        dest / f"{role}_continuation_provenance.json",
        dict(
            execution_sha256=continuation_hash(),
            helper_execution_sha256=code_hash(),
            manifest_sha256=sha(dest.parent / MANIFEST),
            shared_case_inputs=case_ref,
        ),
    )
    return result


def fit_baseline(
    journal: ContinuationJournal, key: str, function: Callable[[], np.ndarray], path: Path
) -> np.ndarray | None:
    journal.baseline(key, "STARTED")
    print(f"BASELINE START {key}", flush=True)
    began = time.monotonic()
    try:
        value = function()
        if not np.isfinite(value).all():
            raise ValueError("NONFINITE_BASELINE_SHARED_MATH")
        np.save(path, value)
        journal.baseline(
            key,
            "COMPLETED",
            dict(coefficients=str(path), sha256=sha(path), seconds=time.monotonic() - began),
        )
        print(f"BASELINE COMPLETED {key}", flush=True)
        return value
    except np.linalg.LinAlgError as error:
        journal.baseline(
            key, "FAILED", dict(isolated=True, error_type=type(error).__name__, message=str(error))
        )
        return None
    except BaseException as error:
        journal.baseline(
            key, "FAILED", dict(isolated=False, error_type=type(error).__name__, message=str(error))
        )
        raise


def run_baselines(data: FoldData, out: Path, journal: ContinuationJournal) -> None:
    old = Path(journal.manifest["old_namespace"])
    available = []
    for year in YEARS:
        data.phase(year, "inner", out)
        fitpos = data.positions(year, "inner_train")
        valpos = data.positions(year, "inner_validation")
        profiles = {}
        for arm in ("P", "LR"):
            dest = out / f"F{year % 100}_S1_{arm}"
            dest.mkdir()
            if year == 2021:
                selection = json.loads((old / dest.name / "selection.json").read_text())
                write(dest / "selection.json", selection)
                write(
                    dest / "reused_inner_outputs.json",
                    dict(
                        source=str(old / dest.name),
                        source_selection_sha256=sha(old / dest.name / "selection.json"),
                        coefficient_fit_repeated=False,
                        predictions_reused=True,
                    ),
                )
                profiles[arm] = (selection["selected"], dest)
                continue
            candidates = []
            system = None
            for penalty in GRID if arm == "LR" else (None,):
                key = f"F{year % 100}/{arm}/inner/{penalty}"

                def calculate() -> np.ndarray:
                    nonlocal system
                    if arm == "P":
                        return np.average(
                            rank_targets(data.returns[fitpos]),
                            axis=0,
                            weights=origin_weights(
                                data.rows.iloc[fitpos].session_date_et.to_numpy()
                            ),
                        )
                    if system is None:
                        system = ridge_system(data.linear_stream(fitpos))
                    return ridge_solution(*system, float(penalty if penalty is not None else 0))

                coef = fit_baseline(journal, key, calculate, dest / f"inner_{penalty}.npy")
                if coef is None:
                    continue
                score = predict(data, valpos, coef)
                ic = daily_ic(
                    data.returns[valpos], score, data.rows.iloc[valpos].session_date_et.to_numpy()
                )
                if np.isfinite(ic):
                    candidates.append(dict(penalty=penalty, ic=ic))
            if not candidates:
                write(
                    dest / "UNAVAILABLE.json",
                    dict(reason="No finite inner selection candidate", LP_related=False),
                )
                continue
            selected = max(candidates, key=lambda r: (r["ic"], r["penalty"] or 0))
            write(dest / "selection.json", dict(candidates=candidates, selected=selected))
            coef = np.load(dest / f"inner_{selected['penalty']}.npy")
            for role, pos in [("inner_train", fitpos), ("inner_validation", valpos)]:
                export(data, year, role, arm, predict(data, pos, coef), dest)
            profiles[arm] = (selected, dest)
        data.phase(year, "refit", out)
        pos = data.positions(year, "refit")
        for arm, (selected, dest) in profiles.items():

            def calculate_refit() -> np.ndarray:
                if arm == "P":
                    return np.average(
                        rank_targets(data.returns[pos]),
                        axis=0,
                        weights=origin_weights(data.rows.iloc[pos].session_date_et.to_numpy()),
                    )
                return ridge(data.linear_stream(pos), float(selected["penalty"]))

            coef = fit_baseline(
                journal,
                f"F{year % 100}/{arm}/refit",
                calculate_refit,
                dest / "refit_coefficients.npy",
            )
            if coef is None:
                continue
            for role in ("refit", "oos"):
                positions = data.positions(year, role)
                export(data, year, role, arm, predict(data, positions, coef), dest)
            available.append(dict(year=year, model=arm, status="COMPLETED"))
        for arm in ("N0", "N1", "N2"):
            dest = out / f"F{year % 100}_S1_{arm}"
            dest.mkdir()
            positions = data.positions(year, "oos")
            export(data, year, "oos", arm, predict(data, positions, arm), dest)
    verified = verify_exports(out, sorted(out.glob("F*_S1_*/*_scores.parquet")))
    old_verified = verify_exports(out, sorted(old.glob("F21_S1_*/*_scores.parquet")))
    write(
        out / "STAGE_B_HANDOFF.json",
        dict(
            status="PASS_COMMON_SCIENTIFIC_CHECKS",
            LP="DEFERRED_AFTER_PRIOR_FAILURE",
            S1_performance_gate=False,
            baseline_available=available,
            independent_outputs=verified + old_verified,
            new_attempts=len(journal.baseline_keys),
            old_attempts_preserved=8,
        ),
    )


def isolated_neural_failure(
    error: BaseException, data: FoldData, year: int, score: np.ndarray | None
) -> dict:
    """Only provable candidate score-constancy is isolated; unknown common bugs stop."""
    message = str(error)
    if (
        not isinstance(error, ValueError)
        or message not in ("UNDEFINED_SELECTOR_OR_EPOCH", "OOS_DEFINED_IC_BELOW99PCT")
        or score is None
    ):
        return dict(
            isolated=False,
            reason="Shared/unknown numerical, source, checkpoint or resource failure",
        )
    role = "inner_validation" if message == "UNDEFINED_SELECTOR_OR_EPOCH" else "oos"
    returns = data.returns[data.positions(year, role)]
    healthy = (
        returns.shape == score.shape
        and np.isfinite(returns).all()
        and np.isfinite(score).all()
        and (np.ptp(returns, axis=1) > 0).all()
    )
    constant = int((np.ptp(score, axis=1) == 0).sum()) if score.ndim == 2 else 0
    return dict(
        isolated=bool(healthy and constant > 0),
        reason="Finite candidate score ties with varying verified source outcomes",
        constant_origins=constant,
        role=role,
    )


def neural_one(
    data: FoldData, out: Path, journal: ContinuationJournal, year: int, arm: str
) -> None:
    run = f"HF20-S1S2-F{year % 100}-{arm}-S42"
    dest = out / run
    dest.mkdir(exist_ok=False)
    journal.event(run, "STARTED", {})
    print(f"NEURAL START {run}", flush=True)
    p: np.ndarray | None = None
    try:
        started = time.monotonic()
        seed_all(42)
        model = SharedLSTM().float()
        initial = initial_hash(model)
        if sum(p.numel() for p in model.parameters()) != 6433:
            raise ValueError("EXACT_TM0_PARAMETER_COUNT")
        opt = optimizer(model)
        write(dest / "calibration_configuration.json", check_configuration(model, opt))
        data.phase(year, "inner", out)
        selector = RankSelector()
        fitpos = data.positions(year, "inner_train")
        valpos = data.positions(year, "inner_validation")
        for number in range(1, 61):
            receipt = epoch(model, opt, data, fitpos, arm, number, "calibration", dest)
            p = predict(data, valpos, model)
            ic = daily_ic(
                data.returns[valpos], p, data.rows.iloc[valpos].session_date_et.to_numpy()
            )
            qualifies = selector.observe(number, ic)
            print(f"{run} epoch={number} IC={ic:.8f} selected={selector.selected}", flush=True)
            torch.save(model.state_dict(), dest / f"calibration_{number:03d}.pt")
            write(
                dest / f"calibration_{number:03d}.json",
                dict(**receipt, ic=ic, qualifies=qualifies, selector=vars(selector).copy()),
            )
            if selector.stop(number):
                break
        torch.save(opt.state_dict(), dest / "calibration_stop_optimizer.pt")
        model.load_state_dict(
            torch.load(dest / f"calibration_{selector.selected:03d}.pt", weights_only=True)
        )
        write(
            dest / "calibration_binding.json",
            dict(
                checkpoint=str(dest / f"calibration_{selector.selected:03d}.pt"),
                checkpoint_sha256=sha(dest / f"calibration_{selector.selected:03d}.pt"),
                selected=selector.selected,
                raw_best_epoch=selector.raw_epoch,
                recipe=str(out / f"F{year % 100}_inner_recipe.json"),
            ),
        )
        for role, pos in [("inner_train", fitpos), ("inner_validation", valpos)]:
            p = predict(data, pos, model)
            export(data, year, role, arm, p, dest)
        journal.event(run, "CALIBRATED", vars(selector).copy())
        journal.event(run, "REFITTING", dict(selected_epoch=selector.selected))
        seed_all(42)
        model = SharedLSTM().float()
        if initial_hash(model) != initial:
            raise ValueError("REFIT_NOT_FRESH_SEED42")
        opt = optimizer(model)
        write(dest / "refit_configuration.json", check_configuration(model, opt))
        if opt.state:
            raise ValueError("REFIT_OPTIMIZER_NOT_FRESH")
        data.phase(year, "refit", out)
        pos = data.positions(year, "refit")
        for number in range(1, selector.selected + 1):
            write(
                dest / f"refit_{number:03d}.json",
                epoch(model, opt, data, pos, arm, number, "refit", dest),
            )
        torch.save(
            dict(model=model.state_dict(), optimizer=opt.state_dict()),
            dest / "refit_final.pt",
        )
        saved = torch.load(dest / "refit_final.pt", weights_only=True)
        model.load_state_dict(saved["model"])
        expected = selector.selected * math.ceil(
            len(data.rows.iloc[pos].session_date_et.unique()) / 16
        )
        if any(int(state["step"]) != expected for state in opt.state.values()):
            raise ValueError("REFIT_OPTIMIZER_STEPS_DISAGREE")
        write(
            dest / "refit_binding.json",
            dict(
                checkpoint=str(dest / "refit_final.pt"),
                checkpoint_sha256=sha(dest / "refit_final.pt"),
                recipe=str(out / f"F{year % 100}_refit_recipe.json"),
            ),
        )
        for role in ("refit", "oos"):
            pos = data.positions(year, role)
            p = predict(data, pos, model)
            export(data, year, role, arm, p, dest)
        from .hf20_ranking_diagnostics import verify_exports

        reconciliation = verify_exports(out, sorted(dest.glob("*_scores.parquet")))
        write(
            dest / "PASS.json",
            dict(
                run_id=run,
                selector=vars(selector),
                seconds=time.monotonic() - started,
                status="PASS_TECHNICAL",
                initial_sha256=initial,
                reconciliation=reconciliation,
                files={str(p): sha(p) for p in dest.iterdir() if p.is_file()},
            ),
        )
        journal.event(run, "COMPLETED", dict(selected_epoch=selector.selected))
        print(f"NEURAL COMPLETED {run} selected={selector.selected}", flush=True)
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


def check_configuration(model: SharedLSTM, opt: torch.optim.AdamW) -> dict:
    expected = dict(hidden=32, layers=1, dropout=0.1, parameters=6433)
    actual = dict(
        hidden=model.lstm.hidden_size,
        layers=model.lstm.num_layers,
        dropout=model.dropout.p,
        parameters=sum(p.numel() for p in model.parameters()),
    )
    if actual != expected:
        raise ValueError("FROZEN_ARCHITECTURE_CHANGED")
    groups = []
    for group in opt.param_groups:
        if group["lr"] != 0.001 or group["betas"] != (0.9, 0.999) or group["eps"] != 1e-8:
            raise ValueError("FROZEN_ADAMW_CHANGED")
        decay = group["weight_decay"]
        for parameter in group["params"]:
            if decay != (0.01 if parameter.ndim > 1 else 0):
                raise ValueError("MATRIX_BIAS_DECAY_CHANGED")
        groups.append(
            dict(
                lr=group["lr"],
                betas=list(group["betas"]),
                eps=group["eps"],
                weight_decay=decay,
                parameters=sum(p.numel() for p in group["params"]),
            )
        )
    return dict(
        model=actual,
        groups=groups,
        dtype="float32",
        device="cpu",
        session_batch=16,
        gradient_cap=1,
        seed=42,
    )


def readiness(out: Path) -> None:
    """No fits: immutable recipe replay, fold membership, saved coefficient and selection checks."""
    source = json.loads((out / "SOURCE_AND_AUTHORITY_PREFLIGHT.json").read_text())
    old = Path(source["old_namespace"])
    for p in old.glob("F*_indices.csv"):
        shutil.copyfile(p, out / p.name)
    for name in ("folds.json", "shared_source_case_keys.csv", "F21_inner_recipe.json"):
        shutil.copyfile(old / name, out / name)
    shutil.copyfile(POINTER, out / "prior_registry_pointer.json")
    data = FoldData(live_approved=True)
    plans = json.loads((old / "folds.json").read_text())
    for plan in plans:
        actual, _ = fold_masks(plan["year"], data.rows, data.grid)
        if actual != plan:
            raise ValueError("CHANGED_FOLD_CUTOFF_OR_POPULATION")
        for role in ("inner_train", "inner_validation", "refit", "oos"):
            pos = data.positions(plan["year"], role)
            expected = pd.read_csv(out / f"F{plan['year'] % 100}_{role}_indices.csv")
            if set(data.rows.iloc[pos].origin_id) != set(expected.origin_id):
                raise ValueError("CHANGED_ROLE_KEYS")
            r = data.returns[pos]
            if not np.isfinite(r).all() or (np.ptp(r, axis=1) == 0).any():
                raise ValueError("INVALID_SHARED_LABEL_POPULATION")
    data.phase(2021, "inner", out)
    witnesses = pd.read_csv(out / "shared_source_case_keys.csv")
    witness_values = witnesses.witness_return_4h.to_numpy(dtype=float)
    for witness_index, row in enumerate(witnesses.itertuples()):
        pos = int(np.flatnonzero(data.rows.origin_id.eq(row.origin_id))[0])
        j = data.symbols.index(row.ticker)
        np.testing.assert_allclose(
            data.returns[pos, j], witness_values[witness_index], rtol=1e-14, atol=1e-16
        )
    if (
        data.recipe["epsilon"] != 0.00031079729533760086
        or data.recipe["t2_scale"] != 0.9072704147262087
    ):
        raise ValueError("REUSED_RECIPE_CHANGED")
    pos = data.positions(2021, "inner_validation")
    replayed = []
    for arm in ("P", "LR"):
        dest = old / f"F21_S1_{arm}"
        selection = json.loads((dest / "selection.json").read_text())
        independent = []
        for candidate in selection["candidates"]:
            coef = np.load(dest / f"inner_{candidate['penalty']}.npy")
            score = predict(data, pos, coef)
            ic = daily_ic(data.returns[pos], score, data.rows.iloc[pos].session_date_et.to_numpy())
            np.testing.assert_allclose(ic, candidate["ic"], rtol=1e-13, atol=1e-14)
            independent.append(dict(penalty=candidate["penalty"], ic=ic))
        selected = max(independent, key=lambda r: (r["ic"], r["penalty"] or 0))
        if selected != selection["selected"]:
            raise ValueError("REUSED_SELECTION_CHANGED")
        replayed.append(dict(model=arm, candidates=independent, selected=selected, refitted=False))
    verified = verify_exports(out, sorted(old.glob("F21_S1_*/*_scores.parquet")))
    write(
        out / "READINESS_REPLAY.json",
        dict(
            status="PASS",
            actual_supervised_fits=0,
            actual_optimizer_steps=0,
            prefix_recipes_fitted=0,
            recipe_sha256=sha(out / "F21_inner_recipe.json"),
            replayed=replayed,
            old_outputs=verified,
            protected_numeric_reads=0,
        ),
    )


def seal(out: Path) -> None:
    source = json.loads((out / "SOURCE_AND_AUTHORITY_PREFLIGHT.json").read_text())
    old = Path(source["old_namespace"])
    prior = json.loads((old / "proposal.json").read_text())
    refs = {r["path"]: r["sha256"] for r in prior["preserve_refs"]}
    for p in old.rglob("*"):
        if p.is_file():
            refs[str(p)] = sha(p)
    for name in (*NEW_CODE, "tests/test_hf20_ranking_continue.py"):
        refs[name] = sha(Path(name))
    for name in (
        "submitted_continuation_authority.txt",
        "READINESS_REPLAY.json",
        "SOURCE_AND_AUTHORITY_PREFLIGHT.json",
        "tests.txt",
        "static_check.json",
        "ruff.txt",
        "prior_registry_pointer.json",
        "LP_FAILURE_READONLY_DIAGNOSIS.md",
    ):
        refs[str(out / name)] = sha(out / name)
    summary = json.loads((out / "static_check.json").read_text())["summary"]
    if summary["errorCount"] or summary["warningCount"]:
        raise ValueError("STATIC_GATE")
    if "passed" not in (out / "tests.txt").read_text():
        raise ValueError("TEST_GATE")
    instruction = (out / "submitted_continuation_authority.txt").read_text()
    if "This user message authorizes the revised continuation" not in instruction:
        raise ValueError("DIRECT_AUTHORITY_REQUIRED")
    jobs = [json.loads(x) for x in (old / "baseline_fit_jobs.jsonl").read_text().splitlines()]
    write(
        out / MANIFEST,
        dict(
            schema="HF20_S1_S2_CONTINUATION_v1",
            authority=dict(
                kind="DIRECT_PROSPECTIVE_USER_REQUEST",
                path=str(out / "submitted_continuation_authority.txt"),
                sha256=sha(out / "submitted_continuation_authority.txt"),
                signature_claimed=False,
            ),
            old_namespace=str(old),
            old_proposal_sha256=sha(old / "proposal.json"),
            execution_sha256=continuation_hash(),
            inherited_helper_bundle_sha256=code_hash(),
            science={
                k: prior[k]
                for k in (
                    "folds",
                    "sources",
                    "baseline_penalties",
                    "baseline_selection",
                    "baseline_inputs",
                    "linear_objective",
                    "model",
                    "objectives",
                    "selector",
                    "metrics",
                )
            },
            old_baseline_events=jobs,
            old_attempts=8,
            reused_successful_inner_fits=7,
            new_baseline_tasks=baseline_plan(),
            new_baseline_cap=29,
            cumulative_baseline_cap=37,
            LP="DEFERRED_AFTER_PRIOR_FAILURE_NO_LP_RETRY",
            neural_runs=list(RUNS),
            neural_before=62,
            neural_maximum=74,
            effective_ceiling=200,
            prefix_recipes_reused=1,
            prefix_recipes_new_max=7,
            prior_count_3994_verified=True,
            preserve_refs=[dict(path=p, sha256=h) for p, h in sorted(refs.items())],
            failure_policy=(
                "Continue independent arms after proven isolation; "
                "unknown/shared/fatal failures stop; no retries or performance gate"
            ),
            resources=prior["resources"],
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--readiness", action="store_true")
    parser.add_argument("--seal", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if sum((args.readiness, args.seal, args.run)) != 1:
        raise ValueError("EXACT_ONE_CONTINUATION_MODE")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.readiness:
        readiness(args.out)
        return
    if args.seal:
        seal(args.out)
        return
    out = args.out
    manifest = json.loads((out / MANIFEST).read_text())
    if (
        manifest["authority"]["kind"] != "DIRECT_PROSPECTIVE_USER_REQUEST"
        or manifest["execution_sha256"] != continuation_hash()
    ):
        raise ValueError("ACTIVE_CONTINUATION_AUTHORITY_MISMATCH")
    for ref in manifest["preserve_refs"]:
        if sha(Path(ref["path"])) != ref["sha256"]:
            raise ValueError("BOUND_CONTINUATION_SOURCE_CHANGED:" + ref["path"])
    if (out / "EXECUTION_STARTED.json").exists() or NEURAL_JOURNAL.exists():
        raise ValueError("NO_CAMPAIGN_RETRY")
    previous = json.loads(POINTER.read_text())
    events = [json.loads(x) for x in Path(previous["real_journal"]).read_text().splitlines()]
    if events[-1]["global_started_pairs"] != 62 or events[-1]["status"] != "COMPLETED":
        raise ValueError("CONTINUATION_LEDGER_NOT62")
    resources(out)
    write(
        out / "EXECUTION_STARTED.json",
        dict(
            at=now(),
            manifest_sha256=sha(out / MANIFEST),
            execution_sha256=continuation_hash(),
            pid=os.getpid(),
            neural_before=62,
        ),
    )
    data = FoldData(live_approved=True)
    journal = ContinuationJournal(out, manifest)
    try:
        run_baselines(data, out, journal)
        for year in YEARS:
            for arm in ARMS:
                neural_one(data, out, journal, year, arm)
    except BaseException as error:
        write(
            out / "FATAL_STOP.json",
            dict(
                at=now(),
                error_type=type(error).__name__,
                message=str(error),
                neural_started=journal.started - 62,
                global_started_pairs=journal.started,
                no_retry=True,
            ),
        )
        raise
    write(
        out / "FITTING_FINISHED.json",
        dict(
            at=now(),
            neural_started=journal.started - 62,
            global_started_pairs=journal.started,
            baseline_attempts=len(journal.baseline_keys),
            resources=resources(out),
        ),
    )
    from .hf20_ranking_continue_report import collective

    collective(out)


if __name__ == "__main__":
    main()
