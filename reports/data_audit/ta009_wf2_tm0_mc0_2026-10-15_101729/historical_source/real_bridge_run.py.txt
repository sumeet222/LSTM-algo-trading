"""One approval-gated real TM0 pair. Legacy synthetic executors remain unchanged."""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .baseline_ridge import windows
from .config import atomic_new, digest, fingerprint, now, write_json
from .ft0_transforms import identity
from .labels import FitWindow
from .ledger import pair_budget, read_ledger
from .neural_engine import (
    SharedLSTM,
    batch_prediction,
    clip,
    norm_summary,
    optimizer,
    seed_all,
    session_batches,
    session_losses,
)
from .neural_health import g6_summary
from .neural_lifecycle import EarlyStop
from .neural_models import EndpointGatedLSTM, gate_diagnostics
from .pretraining_policy import verify_ref
from .real_batch_authority import BatchPairAuthority
from .real_batch_data import ConditionedView
from .real_bridge_authority import (
    ACTIVE_SECONDS,
    CONTRACT,
    HARD_SECONDS,
    TrainingAuthority,
    load_review,
    load_training_authority,
    require_training,
)
from .real_bridge_data import RealInputView, build_view, load_inputs

FitAuthority = TrainingAuthority | BatchPairAuthority
FitModel = SharedLSTM | EndpointGatedLSTM
FitView = RealInputView | ConditionedView


def execution_contract(authority: FitAuthority | None) -> dict:
    return authority.contract if type(authority) is BatchPairAuthority else CONTRACT


def execution_model(authority: FitAuthority) -> FitModel:
    contract = execution_contract(authority)
    return (
        EndpointGatedLSTM()
        if contract["architecture"] == "MC1"
        else SharedLSTM(contract["channels"])
    )


JOURNAL = "reports/audit/track_a_real_pairs_v1.jsonl"
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED"},
    "CALIBRATED": {"REFITTING", "FAILED"},
    "REFITTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


def journal_rows(path: Path) -> list[dict]:
    """All started pairs count permanently; this first-pair writer admits only one."""
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("TRUNCATED_REAL_PAIR_JOURNAL")
    rows = [json.loads(r) for r in raw.splitlines()]
    for i, row in enumerate(rows):
        if (
            row.get("sequence") != i + 1
            or row.get("status") not in TRANSITIONS
            or row.get("previous") != fingerprint(rows[:i])
            or row.get("contract") != CONTRACT
        ):
            raise ValueError("REAL_PAIR_JOURNAL_CHAIN_OR_CONTRACT_CHANGED")
        if i == 0:
            if row["status"] != "STARTED":
                raise ValueError("REAL_PAIR_START_REQUIRED")
        elif (
            row["pair_key"] != rows[0]["pair_key"]
            or row["status"] not in TRANSITIONS[rows[i - 1]["status"]]
        ):
            raise ValueError("SINGLE_PAIR_MONOTONIC_TRANSITION_REQUIRED")
    return rows


def pair_key(authority: FitAuthority) -> str:
    return fingerprint(
        [authority.binding_ref, authority.binding["input_id"], execution_contract(authority)]
    )


def append_pair(authority: FitAuthority, status: str, detail: dict) -> None:
    """New v1 real journal links immutable P0 history; it never rewrites P0 events."""
    if type(authority) is BatchPairAuthority:
        authority.append(status, detail)
        return
    if status != "FAILED":
        require_training(
            authority,
            "START_PAIR" if status == "STARTED" else "CHECKPOINT",
            authority.binding["input_id"],
        )
    root = authority.review.root
    proposal = json.loads(verify_ref(root, authority.binding["proposal"]).read_text())
    legacy = verify_ref(root, proposal["legacy_ledger"])
    if pair_budget(read_ledger(legacy))["attempted_pairs"] != 0:
        raise ValueError("FIRST_PAIR_LEGACY_BUDGET_MUST_BE_ZERO")
    path = root / JOURNAL
    lock = path.with_suffix(".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("x"):
        pass
    try:
        rows = journal_rows(path)
        key = pair_key(authority)
        if (status == "STARTED" and rows) or (
            status != "STARTED"
            and (
                not rows
                or rows[0]["pair_key"] != key
                or status not in TRANSITIONS[rows[-1]["status"]]
            )
        ):
            raise ValueError("NO_DUPLICATE_OR_SECOND_GENUINE_PAIR")
        event = {
            "sequence": len(rows) + 1,
            "previous": fingerprint(rows),
            "at": now(),
            "pair_key": key,
            "status": status,
            "contract": CONTRACT,
            "authority": authority.binding_ref,
            "legacy": proposal["legacy_ledger"],
            "detail": detail,
        }
        if status == "STARTED":
            definition = proposal["registry_definition"]
            verify_ref(root, definition)
            pointer = root / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
            value = {
                "schema": 1,
                "definition": definition,
                "authority": authority.binding_ref,
                "legacy": proposal["legacy_ledger"],
                "real_journal": JOURNAL,
                "counts_started_including_failed": True,
            }
            if pointer.exists():
                if json.loads(pointer.read_text()) != value:
                    raise ValueError("UNREVIEWED_EXPERIMENT_REGISTRY_POINTER")
            else:
                write_json(pointer, value)
        old = path.read_bytes() if path.exists() else b""
        temporary = path.with_suffix(".pending")
        with temporary.open("xb") as stream:
            stream.write(old + json.dumps(event, sort_keys=True, allow_nan=False).encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        journal_rows(temporary)
        os.replace(temporary, path)
    finally:
        lock.unlink()


def save_real_checkpoint(
    path: Path,
    model: FitModel,
    binding: str,
    preparation: str,
    stage: str,
    epoch: int,
    authority: FitAuthority | None = None,
) -> dict:
    if (
        stage not in {"CALIBRATION_SELECTED", "REFIT_FINAL", "SYNTHETIC_SMOKE"}
        or type(epoch) is not int
        or not 1 <= epoch <= 60
        or model.input_dim != execution_contract(authority)["channels"]
        or sum(p.numel() for p in model.parameters()) != execution_contract(authority)["parameters"]
        or any(
            p.dtype != torch.float32 or p.device.type != "cpu" or not bool(torch.isfinite(p).all())
            for p in model.parameters()
        )
    ):
        raise ValueError("EXACT_CHECKPOINT_STAGE_EPOCH_REQUIRED")
    checkpoint_authority(authority, binding, preparation, stage)
    body = {
        "schema": 1,
        "pair_key": binding,
        "preparation_id": preparation,
        "stage": stage,
        "epoch": epoch,
        "contract": execution_contract(authority),
        "model": model.state_dict(),
        "torch_rng": torch.get_rng_state(),
        "resumable": False,
    }
    buffer = io.BytesIO()
    torch.save(body, buffer)
    atomic_new(path, buffer.getvalue())
    manifest = {
        "schema": 1,
        "sha256": digest(path),
        "bytes": path.stat().st_size,
        "pair_key": binding,
        "preparation_id": preparation,
        "stage": stage,
        "epoch": epoch,
        "resumable": False,
    }
    write_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def load_real_checkpoint(
    path: Path,
    model: FitModel,
    binding: str,
    preparation: str,
    stage: str,
    authority: FitAuthority | None = None,
) -> None:
    checkpoint_authority(authority, binding, preparation, stage)
    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
    if (
        manifest.get("sha256") != digest(path)
        or manifest.get("pair_key") != binding
        or manifest.get("preparation_id") != preparation
        or manifest.get("stage") != stage
    ):
        raise ValueError("REAL_CHECKPOINT_BINDING_CHANGED")
    obj = torch.load(path, map_location="cpu", weights_only=True)
    if (
        obj.get("contract") != execution_contract(authority)
        or obj.get("pair_key") != binding
        or obj.get("preparation_id") != preparation
        or obj.get("stage") != stage
        or obj.get("epoch") != manifest["epoch"]
        or not 1 <= obj["epoch"] <= 60
    ):
        raise ValueError("REAL_CHECKPOINT_SCHEMA_CHANGED")
    expected = model.state_dict()
    state = obj["model"]
    if set(state) != set(expected) or any(
        not isinstance(state[k], torch.Tensor)
        or state[k].shape != v.shape
        or state[k].dtype != v.dtype
        or not bool(torch.isfinite(state[k]).all())
        for k, v in expected.items()
    ):
        raise ValueError("EXACT_FINITE_TM0_STATE_REQUIRED")
    model.load_state_dict(state, strict=True)
    model.eval()


def checkpoint_authority(
    authority: FitAuthority | None, binding: str, preparation: str, stage: str
) -> None:
    if stage == "SYNTHETIC_SMOKE":
        if not binding.startswith("SYN:") or not preparation.startswith("SYN:"):
            raise ValueError("EXPLICIT_SYNTHETIC_SMOKE_IDENTITY_REQUIRED")
        return
    if authority is None:
        raise ValueError("REAL_CHECKPOINT_REQUIRES_ACTUAL_TRAINING_AUTHORITY")
    require_training(authority, "CHECKPOINT", authority.binding["input_id"])
    if type(authority) is BatchPairAuthority:
        key = "inner" if stage == "CALIBRATION_SELECTED" else "refit"
        if (
            binding != pair_key(authority)
            or preparation != authority.descriptor["views"][key]["preparation_id"]
        ):
            raise ValueError("APPROVED_ARCHITECTURE_AND_PREPARATION_REQUIRED")
        return
    prefix = "WF1_INNER_TRAIN" if stage == "CALIBRATION_SELECTED" else "WF1_REFIT"
    if (
        binding != pair_key(authority)
        or preparation != authority.review.manifest["preparations"][prefix]["preparation_id"]
    ):
        raise ValueError("APPROVED_PAIR_AND_PREPARATION_REQUIRED")


def rank_ic(prediction: tuple[float, ...], target: tuple[float, ...]) -> tuple[float | None, str]:
    """Frozen midranks, project-zero constant forecasts and omitted constant targets."""
    if len(prediction) != 5 or len(target) != 5 or not np.isfinite((*prediction, *target)).all():
        raise ValueError("FIVE_FINITE_RANK_SCORES_REQUIRED")
    if np.ptp(target) == 0:
        return None, "TARGET_CONSTANT_OMITTED_FROM_IC_NOT_MSE"
    if np.ptp(prediction) == 0:
        return 0.0, "PREDICTION_CONSTANT_PROJECT_ZERO_MATHEMATICALLY_UNDEFINED"
    x = pd.Series(prediction).rank(method="average").to_numpy()
    y = pd.Series(target).rank(method="average").to_numpy()
    return float(np.corrcoef(x, y)[0, 1]), "DEFINED"


def daily_ic(
    rows: tuple[tuple[str, float | None, bool], ...], *, defined_only: bool
) -> float | None:
    days = sorted(
        {day for day, value, defined in rows if value is not None and (defined or not defined_only)}
    )
    means = [
        float(
            np.mean(
                [
                    v
                    for d, v, defined in rows
                    if d == day and v is not None and (defined or not defined_only)
                ]
            )
        )
        for day in days
    ]
    return float(np.mean(means)) if means else None


def peak_rss_bytes() -> int | None:
    """Peak whole-process RSS, not a claimed isolated model-memory measurement."""
    try:
        import resource
    except ImportError:
        return None
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value * (1 if sys.platform == "darwin" else 1024))


def epoch_pass(
    authority: FitAuthority,
    input_id: str,
    model: FitModel,
    view: FitView,
    epoch: int,
    opt: torch.optim.AdamW | None,
    deadline: float,
) -> dict:
    """Existing pure TM0 math, sampler, optimizer and session objective; real metadata."""
    require_training(
        authority, "CALIBRATION" if opt is not None else "DEVELOPMENT_EVALUATION", input_id
    )
    model.train(opt is not None)
    losses, norms, seen, scores = [], [], [], []
    rank_rows, gate_rows, gate_states = [], [], []
    started = time.monotonic()
    for positions in session_batches(len(view.sessions), 42, epoch, shuffle=opt is not None):
        if time.monotonic() >= deadline:
            raise TimeoutError("APPROVED_ACTIVE_FITTING_LIMIT_REACHED")
        batch = view.batch(positions)
        if isinstance(model, EndpointGatedLSTM) and opt is None:
            endpoints = batch.inputs[batch.origins][:, 0, -1, 16:21]
            with torch.no_grad():
                gate_rows.append(model.gate(endpoints).detach())
                gate_states.extend(endpoints[:, -1].tolist())
        with torch.set_grad_enabled(opt is not None):
            prediction = batch_prediction(model, batch)
            by_day = session_losses(prediction, batch.targets, batch.origins)
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                by_day.mean().backward()
                norms.append(clip(model))
                opt.step()
        losses.extend(float(x) for x in by_day.detach())
        scores.extend(float(x) for x in prediction.detach()[batch.origins].reshape(-1))
        seen.extend(batch.ids)
        if opt is None:
            for j, day in enumerate(batch.ids):
                for origin in (1, 2):
                    if bool(batch.origins[j, origin - 1]):
                        truth = next(
                            r.targets for r in view.rows if r.session == day and r.origin == origin
                        )
                        value, status = rank_ic(tuple(prediction[j, origin - 1].tolist()), truth)
                        mse = float(
                            (prediction[j, origin - 1] - batch.targets[j, origin - 1])
                            .square()
                            .mean()
                        )
                        rank_rows.append(
                            {
                                "session": day,
                                "origin": origin,
                                "IC": value,
                                "status": status,
                                "MSE": mse,
                                "scores": prediction[j, origin - 1].tolist(),
                                "targets": batch.targets[j, origin - 1].tolist(),
                            }
                        )
    if len(seen) != len(view.sessions) or set(seen) != set(view.sessions):
        raise ValueError("COMPLETE_SESSION_EPOCH_CONSERVATION_REQUIRED")
    total = sum(losses)
    ic_rows = tuple((r["session"], r["IC"], r["status"] == "DEFINED") for r in rank_rows)
    return {
        "epoch": epoch,
        "origin_records": rank_rows,
        "gate": gate_diagnostics(torch.cat(gate_rows)) if gate_rows else None,
        "gate_by_standardized_U5_sign": {
            str(sign): gate_diagnostics(
                torch.cat(gate_rows)[torch.tensor([int(v >= 0) == sign for v in gate_states])]
            )
            for sign in (0, 1)
            if any(int(v >= 0) == sign for v in gate_states)
        }
        if gate_rows
        else {},
        "mse": total / len(losses),
        "sessions": len(seen),
        "steps": len(norms),
        "seconds": time.monotonic() - started,
        "permutation_hash": fingerprint(seen),
        "score_std": float(np.std(scores)),
        "daily_rank_IC": daily_ic(ic_rows, defined_only=False),
        "defined_only_daily_IC": daily_ic(ic_rows, defined_only=True),
        "constant_predictions": sum(
            r["status"].startswith("PREDICTION_CONSTANT") for r in rank_rows
        ),
        "constant_target_IC_omissions": sum(r["IC"] is None for r in rank_rows),
        "per_origin": {
            str(o): {
                "count": sum(r["origin"] == o for r in rank_rows),
                "MSE": float(np.mean([r["MSE"] for r in rank_rows if r["origin"] == o])),
                "IC": float(
                    np.mean(
                        [r["IC"] for r in rank_rows if r["origin"] == o and r["IC"] is not None]
                    )
                )
                if any(r["origin"] == o and r["IC"] is not None for r in rank_rows)
                else None,
            }
            for o in (1, 2)
            if any(r["origin"] == o for r in rank_rows)
        },
        "gradients": norm_summary(tuple(norms)) if norms else None,
        "top_session_loss_share": {
            str(p): sum(sorted(losses, reverse=True)[: max(1, math.ceil(len(losses) * p))]) / total
            if total
            else 0.0
            for p in (0.01, 0.05, 0.1)
        },
    }


def run_worker(authority: FitAuthority, out: Path) -> None:
    """Private supervised worker; all authorization is checked before fitting starts."""
    started = time.monotonic()
    input_id = authority.binding["input_id"]
    require_training(authority, "START_PAIR", input_id)
    if out.exists():
        raise ValueError("IMMUTABLE_EXPERIMENT_OUTPUT_ALREADY_EXISTS")
    t = time.monotonic()
    candidates = {}
    if type(authority) is BatchPairAuthority:
        authority.inputs()
    else:
        _, candidates = load_inputs(authority.review, ("WF1_INNER_TRAIN", "WF1_REFIT"))
    timings = {"raw_derived_loading": time.monotonic() - t}
    t = time.monotonic()
    inner, tail, full = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    views: dict[str, FitView] = {
        "inner": authority.view("inner")
        if type(authority) is BatchPairAuthority
        else build_view(authority.review, candidates["WF1_INNER_TRAIN"], inner),
        "validation": authority.view("validation")
        if type(authority) is BatchPairAuthority
        else build_view(authority.review, candidates["WF1_INNER_TRAIN"], tail, asof=True),
    }
    timings["inner_preprocessing_application"] = time.monotonic() - t
    if type(authority) is BatchPairAuthority:
        dataset = {
            "first_pair_views": {k: v["view_id"] for k, v in authority.descriptor["views"].items()}
        }
    else:
        proposal = json.loads(
            verify_ref(authority.review.root, authority.binding["proposal"]).read_text()
        )
        dataset = json.loads(
            verify_ref(authority.review.root, proposal["dataset_input_binding"]).read_text()
        )
    if any(v.version != dataset["first_pair_views"][k] for k, v in views.items()):
        raise ValueError("APPROVED_VIEW_POPULATION_CHANGED")
    valid = views["validation"]
    if len(valid.sessions) < 50 or any(sum(r.origin == o for r in valid.rows) < 25 for o in (1, 2)):
        raise ValueError("BLOCKED_INADEQUATE_INNER_VALIDATION")
    # No statistics are re-fitted: the reviewed inner/refit recipes are immutable.
    torch.set_num_threads(1)
    seed_all(42)
    model = execution_model(authority)
    contract = execution_contract(authority)
    if sum(p.numel() for p in model.parameters()) != contract["parameters"]:
        raise ValueError("FROZEN_6433_PARAMETER_TM0_REQUIRED")
    initial = identity({k: v.tolist() for k, v in model.state_dict().items()})
    opt = optimizer(model)
    selector, trace, best = EarlyStop(), [], None
    out.mkdir(parents=True)
    append_pair(authority, "STARTED", {"output": str(out.relative_to(authority.review.root))})
    fit_started = time.monotonic()
    remaining = ACTIVE_SECONDS
    if type(authority) is BatchPairAuthority:
        remaining = min(
            remaining,
            max(
                0.0,
                (
                    pd.Timestamp(authority.plan["deadline"]) - pd.Timestamp.now(tz="UTC")
                ).total_seconds()
                - 900,
            ),
        )
    deadline = fit_started + remaining
    evaluation_deadline = (
        deadline if type(authority) is BatchPairAuthority else started + HARD_SECONDS
    )
    try:
        while selector.status == "CALIBRATING":
            e = selector.epoch + 1
            training = epoch_pass(authority, input_id, model, views["inner"], e, opt, deadline)
            validation = epoch_pass(authority, input_id, model, valid, e, None, deadline)
            qualifies = selector.observe(validation["mse"])
            if qualifies:
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            entry = {
                "training": training,
                "validation": validation,
                "selection": dict(vars(selector)),
            }
            trace.append(entry)
            write_json(out / f"calibration_epoch_{e:02d}.json", entry)
            if e == 1:
                projected = 60 * (training["seconds"] + validation["seconds"]) + (
                    60 * training["seconds"] * math.ceil(751 / 16) / math.ceil(688 / 16)
                )
                write_json(
                    out / "first_epoch_machine_benchmark.json",
                    {
                        "actual_training_seconds": training["seconds"],
                        "actual_validation_seconds": validation["seconds"],
                        "projected_maximum_pair_seconds_NOT_ACTUAL": projected,
                        "calibration_sessions": 688,
                        "refit_sessions": 751,
                        "batch_sessions": 16,
                    },
                )
                if projected > deadline - time.monotonic():
                    raise TimeoutError("FIRST_EPOCH_PROJECTED_PAIR_EXCEEDS_APPROVED_BUDGET")
        timings["calibration_training"] = sum(r["training"]["seconds"] for r in trace)
        timings["calibration_validation"] = sum(r["validation"]["seconds"] for r in trace)
        if best is None:
            raise ValueError("NO_QUALIFYING_CHECKPOINT")
        t = time.monotonic()
        model.load_state_dict(best)
        key = pair_key(authority)
        selected = save_real_checkpoint(
            out / "calibration_selected.pt",
            model,
            key,
            views["inner"].preparation_id,
            "CALIBRATION_SELECTED",
            selector.selected,
            authority,
        )
        timings["selection_and_calibration_checkpoint"] = time.monotonic() - t
        append_pair(authority, "CALIBRATED", {"selected_epoch": selector.selected})
        t = time.monotonic()
        views["refit"] = (
            authority.view("refit")
            if type(authority) is BatchPairAuthority
            else build_view(authority.review, candidates["WF1_REFIT"], full)
        )
        timings["full_prefix_preprocessing_application"] = time.monotonic() - t
        if views["refit"].version != dataset["first_pair_views"]["refit"]:
            raise ValueError("APPROVED_FULL_PREFIX_CHANGED")
        seed_all(42)
        final = execution_model(authority)
        fresh_opt = optimizer(final)
        fresh = identity({k: v.tolist() for k, v in final.state_dict().items()})
        if final is model or fresh_opt is opt or fresh_opt.state or fresh != initial:
            raise ValueError("FRESH_SEEDED_MODEL_AND_OPTIMIZER_REQUIRED")
        append_pair(authority, "REFITTING", {"epochs": selector.selected})
        refit_trace = []
        for e in range(1, selector.selected + 1):
            item = epoch_pass(authority, input_id, final, views["refit"], e, fresh_opt, deadline)
            refit_trace.append(item)
            write_json(out / f"refit_epoch_{e:02d}.json", item)
        timings["refit_training"] = sum(r["seconds"] for r in refit_trace)
        t = time.monotonic()
        train_metrics = epoch_pass(
            authority, input_id, final, views["refit"], 1, None, evaluation_deadline
        )
        timings["refit_train_prediction_audit"] = time.monotonic() - t
        t = time.monotonic()
        checkpoint = out / "refit_final.pt"
        saved = save_real_checkpoint(
            checkpoint,
            final,
            key,
            views["refit"].preparation_id,
            "REFIT_FINAL",
            selector.selected,
            authority,
        )
        reloaded = execution_model(authority)
        load_real_checkpoint(
            checkpoint, reloaded, key, views["refit"].preparation_id, "REFIT_FINAL", authority
        )
        final.eval()
        sample = views["refit"].batch((0,))
        if not torch.equal(batch_prediction(final, sample), batch_prediction(reloaded, sample)):
            raise ValueError("EXACT_SAME_DEVICE_CHECKPOINT_RELOAD_REQUIRED")
        timings["final_checkpoint_and_verification"] = time.monotonic() - t
        t = time.monotonic()
        w = FitWindow(
            "BRIDGE_REVIEW:WF1",
            pd.Timestamp("2023-07-01T04:00Z"),
            pd.Timestamp("2024-01-01T05:00Z"),
            pd.Timestamp("2024-01-01T05:00Z"),
            "INNER_VALIDATION",
        )
        development = (
            authority.view("WF1")
            if type(authority) is BatchPairAuthority
            else build_view(authority.review, candidates["WF1_REFIT"], w, asof=True)
        )
        metrics = epoch_pass(authority, input_id, final, development, 1, None, evaluation_deadline)
        timings["development_prediction_and_audit"] = time.monotonic() - t
        timings["total_end_to_end_worker"] = time.monotonic() - started
        write_json(
            out / "training_actual_runtime.json",
            {
                "seconds": timings,
                "minutes": {k: v / 60 for k, v in timings.items()},
                "neural_fitting_seconds": timings["calibration_training"]
                + timings["refit_training"],
                "device": "cpu",
                "threads": 1,
                "python": platform.python_version(),
                "torch": torch.__version__,
                "numpy": np.__version__,
                "platform": platform.platform(),
                "machine": platform.machine(),
                "logical_CPUs": os.cpu_count(),
                "peak_whole_process_RSS_bytes": peak_rss_bytes(),
                "preprocessing": "REUSED_BOUND_PREFIX_RECIPES_NO_RECALCULATION",
                "calibration_epochs": selector.epoch,
                "refit_epochs": selector.selected,
                "calibration_steps": sum(r["training"]["steps"] for r in trace),
                "refit_steps": sum(r["steps"] for r in refit_trace),
            },
        )
        result_name = (
            f"seed42_{contract['architecture'].lower()}_pair_result.json"
            if type(authority) is BatchPairAuthority
            else "seed42_tm0_first_pair_result.json"
        )
        write_json(
            out / result_name,
            {
                "status": "COMPLETED_DESCRIPTIVE_CONDITIONAL_PILOT",
                "pair_key": key,
                "input_id": input_id,
                "contract": contract,
                "selector": vars(selector),
                "initial_hashes": [initial, fresh],
                "fresh_optimizer_state_empty": True,
                "selected_checkpoint": selected,
                "final_checkpoint": saved,
                "development": metrics,
                "refit_train_evaluation": train_metrics,
                "development_population": development.summary(),
                "G6": g6_summary(
                    tuple(r["training"] for r in trace),
                    tuple(refit_trace),
                    metrics["score_std"],
                    selector.status,
                )["status"],
                "comparative_economic_statistical_claims": "HOLD",
                "confirmation_numeric_rows": 0,
            },
        )
        append_pair(
            authority,
            "COMPLETED",
            {"result": str((out / result_name).relative_to(authority.review.root))},
        )
    except BaseException as exc:
        append_pair(authority, "FAILED", {"error_type": type(exc).__name__, "reason": str(exc)})
        write_json(
            out / "failure.json",
            {
                "status": "FAILED_COUNTED_PAIR",
                "reason": str(exc),
                "seconds_since_first_fit": time.monotonic() - fit_started,
            },
        )
        raise


def main() -> int:
    supervisor_started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer", type=Path, required=True)
    parser.add_argument("--approval-binding", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = Path.cwd()
    review = load_review(root, {"path": str(args.producer), "sha256": digest(args.producer)})
    authority = load_training_authority(
        review, {"path": str(args.approval_binding), "sha256": digest(args.approval_binding)}
    )
    require_training(authority, "START_PAIR", authority.binding["input_id"])
    if args.worker:
        run_worker(authority, args.report.resolve())
        return 0
    command = [sys.executable, "-B", "-m", "lstm_data.real_bridge_run", *sys.argv[1:], "--worker"]
    try:
        result = subprocess.run(command, timeout=HARD_SECONDS, check=False).returncode
    except subprocess.TimeoutExpired:
        result = 124
    if result != 0:
        rows = journal_rows(root / JOURNAL)
        if rows and rows[-1]["status"] not in {"FAILED", "COMPLETED"}:
            append_pair(authority, "FAILED", {"reason": "SUPERVISED_WORKER_EXIT", "code": result})
    if args.report.exists():
        write_json(
            args.report / "supervisor_actual_runtime.json",
            {
                "total_package_wall_seconds": time.monotonic() - supervisor_started,
                "return_code": result,
                "hard_worker_wall_limit_seconds": HARD_SECONDS,
                "neural_times": "See worker training_actual_runtime.json; not test-suite time",
            },
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
