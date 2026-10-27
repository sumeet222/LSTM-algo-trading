"""One sealed S5/S9 campaign: sixteen ordered lifecycles, no implicit retry."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import fingerprint, now
from .hf1m_action_audit import digest
from .hf20_ranking import RankSelector, daily_ic, origin_weights
from .hf20_ranking_run import initial_hash, write
from .hf20_s4_authority import execution_hash as old_execution
from .hf20_s4_data import ROLES
from .hf20_s5s9 import ARMS, RUNS, Data, fit_task, model_for, row_objective
from .neural_engine import SharedLSTM, optimizer
from .objective_screen_run import Selector
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v23_hf20_s5_s9.jsonl")
DEFINITION = Path("configs/track_a_candidate_experiment_registry_v23_hf20_s5_s9.json")
CAPS = dict(task_bytes=2_500_000_000, project_bytes=15_000_000_000, ram_bytes=2_000_000_000)


def code_hash() -> str:
    return fingerprint(
        dict(
            s4=old_execution(),
            new={
                str(p): digest(p)
                for p in sorted(Path("src/lstm_data").glob("hf20_s5s9*"))
                if p.is_file()
            },
        )
    )


def ensure(out: Path) -> dict:
    """No inherited S4 approval can authorize a new target, recipe or start."""
    a = json.loads((out / "LIVE_AUTHORITY.json").read_text())
    card = json.loads((out / "design.json").read_text())
    if (
        a.get("kind") != "ACTUAL_DIRECT_USER_RESPONSE"
        or a.get("approved") is not True
        or a.get("proposal_sha256") != digest(out / "design.json")
        or a.get("execution_sha256") != code_hash()
        or card["execution_sha256"] != code_hash()
        or tuple(a.get("run_ids", [])) != RUNS
        or a.get("neural_starts") != 16
        or a.get("baseline_attempts") != 64
        or a.get("prefix_recipes") != 32
        or a.get("resource_caps") != CAPS
    ):
        raise ValueError("S5S9_EXACT_LIVE_AUTHORITY_REQUIRED")
    for ref in card["evidence"]:
        if digest(Path(ref["path"])) != ref["sha256"]:
            raise ValueError("S5S9_EVIDENCE_CHANGED")
    current = json.loads(POINTER.read_text())
    if JOURNAL.exists():
        if current.get("real_journal") != str(JOURNAL):
            raise ValueError("S5S9_ACTIVE_POINTER_CHANGED")
    elif current != json.loads((out / "prior_registry_pointer.json").read_text()):
        raise ValueError("S5S9_PRIOR_POINTER_CHANGED_BEFORE_FIT")
    return card


def resources(out: Path, reserve: int = 0) -> dict:
    """Metadata-only traversal: never open or hash protected source contents."""
    task = sum(p.stat().st_size for p in out.rglob("*") if p.is_file() and not p.is_symlink())
    total = 0
    for folder, _, files in os.walk(Path.cwd(), followlinks=False):
        for name in files:
            p = Path(folder) / name
            if not p.is_symlink():
                total += p.stat().st_size
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    result = dict(
        task_bytes=task, project_bytes=total, peak_rss_bytes=rss, reserve_bytes=reserve, caps=CAPS
    )
    if (
        task + reserve > CAPS["task_bytes"]
        or total + reserve > CAPS["project_bytes"]
        or rss > CAPS["ram_bytes"]
    ):
        raise ValueError("S5S9_RESOURCE_LIMIT", result)
    return result


def memory_check() -> None:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )
    if rss > CAPS["ram_bytes"]:
        raise ValueError("S5S9_RAM_BEFORE_UPDATE")


def event(out: Path, run: str, status: str, detail: dict) -> int:
    ensure(out)
    old = json.loads((out / "prior_registry_pointer.json").read_text())
    if JOURNAL.exists():
        h = [json.loads(line) for line in JOURNAL.read_text().splitlines()]
    else:
        h = []
    for k, row in enumerate(h):
        if row["sequence"] != k + 1 or row["previous"] != fingerprint(h[:k]):
            raise ValueError("S5S9_JOURNAL_CHAIN")
    starts = [v["run_id"] for v in h if v["status"] == "STARTED"]
    if status == "STARTED":
        if len(starts) >= 16 or run != RUNS[len(starts)] or (h and h[-1]["status"] != "COMPLETED"):
            raise ValueError("S5S9_SEQUENTIAL_GATE_NO_RETRY")
        if h:
            gate = json.loads((out / h[-1]["run_id"] / "PASS.json").read_text())
            if gate.get("status") != "PASS":
                raise ValueError("S5S9_PREVIOUS_PASS_REQUIRED")
            for name, sha in gate["files"].items():
                if digest(Path(name)) != sha:
                    raise ValueError("S5S9_PREVIOUS_GATE_CHANGED")
        elif json.loads(POINTER.read_text()) != old:
            raise ValueError("S5S9_PRIOR_POINTER_CHANGED")
        resources(out, 100_000_000)
    else:
        previous = h[-1] if h else {}
        edges = {
            "STARTED": {"CALIBRATED", "FAILED"},
            "CALIBRATED": {"REFITTING", "FAILED"},
            "REFITTING": {"COMPLETED", "FAILED"},
        }
        state = previous.get("status")
        if (
            previous.get("run_id") != run
            or not isinstance(state, str)
            or status not in edges.get(state, set())
        ):
            raise ValueError("S5S9_ILLEGAL_TRANSITION")
    count = 114 + len(starts) + int(status == "STARTED")
    row = dict(
        sequence=len(h) + 1,
        previous=fingerprint(h),
        at=now(),
        run_id=run,
        status=status,
        global_started_pairs=count,
        effective_ceiling=200,
        detail=detail,
        previous_journal=dict(path=old["real_journal"], sha256=digest(Path(old["real_journal"]))),
        plan=dict(path=str(out / "design.json"), sha256=digest(out / "design.json")),
    )
    with JOURNAL.open("a") as f:
        f.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    if not DEFINITION.exists():
        write(
            DEFINITION,
            dict(
                schema_version=23,
                package="HF20_S5_S9",
                runs=RUNS,
                plan=row["plan"],
                previous_journal=row["previous_journal"],
            ),
        )
    current = dict(
        old,
        definition=dict(path=str(DEFINITION), sha256=digest(DEFINITION)),
        schema_version=23,
        real_journal=str(JOURNAL),
        previous_journal=row["previous_journal"],
        plan=row["plan"],
        fit_permission=False,
    )
    atomic_replace_json(POINTER, current)
    return count


def predict(data: Data, positions: np.ndarray, model: SharedLSTM, arm: str) -> np.ndarray:
    model.eval()
    chunks = []
    with torch.inference_mode():
        for k in range(0, len(positions), 32):
            x, _, _ = data.arrays(positions[k : k + 32], arm)
            raw = model(torch.from_numpy(x.reshape(-1, 48, x.shape[-1]))).numpy()
            chunks.append(
                raw.reshape(-1, 20, 3) if arm in ("EVENT", "QUANTILE") else raw.reshape(-1, 20)
            )
    result = np.concatenate(chunks)
    if not np.isfinite(result).all():
        raise ValueError("S5S9_NONFINITE_FORECAST")
    return result


def off(data: Data, pos: np.ndarray, raw: np.ndarray, arm: str) -> dict:
    r = data.base.returns[pos]
    from .hf20_s5s9 import target_y

    y = target_y(r, data.base.recipe["epsilon"])
    loss = row_objective(
        torch.from_numpy(raw),
        torch.from_numpy(r.astype(np.float32)),
        torch.from_numpy(y.astype(np.float32)),
        arm,
        data.task_recipe,
    ).numpy()
    days = data.base.rows.iloc[pos].session_date_et.to_numpy()
    result = dict(actual_objective=float(origin_weights(days) @ loss.mean(1)), dropout_on=False)
    if arm == "META-T2R":
        result["daily_ic"] = daily_ic(r, raw, days)
    return result


def epoch(
    data: Data,
    pos: np.ndarray,
    model: SharedLSTM,
    opt: torch.optim.AdamW,
    arm: str,
    number: int,
    phase: str,
    dest: Path,
    *,
    update: bool = True,
) -> dict:
    if update:
        ensure(dest.parent)
    groups = data.base.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    traces = []
    gradients = []
    model.train()
    for k in range(0, len(days), 16):
        chosen = days[k : k + 16]
        selected = pos[np.concatenate([groups[d] for d in chosen])]
        x, r, y = data.arrays(selected, arm)
        opt.zero_grad()
        raw = model(torch.from_numpy(x.reshape(-1, 48, x.shape[-1])))
        raw = raw.reshape(-1, 20, 3) if arm in ("EVENT", "QUANTILE") else raw.reshape(-1, 20)
        loss = (
            row_objective(
                raw,
                torch.from_numpy(r.astype(np.float32)),
                torch.from_numpy(y.astype(np.float32)),
                arm,
                data.task_recipe,
            ).mean(1)
            * torch.from_numpy(
                origin_weights(data.base.rows.iloc[selected].session_date_et.to_numpy()).astype(
                    np.float32
                )
            )
        ).sum()
        if not bool(torch.isfinite(loss)):
            raise ValueError("S5S9_NONFINITE_LOSS")
        loss.backward()
        for name, param in model.named_parameters():
            if param.grad is None or not bool(torch.isfinite(param.grad).all()):
                raise ValueError("S5S9_NONFINITE_GRADIENT")
            gradients.append(
                dict(
                    phase=phase,
                    epoch=number,
                    batch=k // 16,
                    parameter=name,
                    cells=param.numel(),
                    nonzero=int(torch.count_nonzero(param.grad)),
                    norm=float(param.grad.norm()),
                )
            )
        before = [v.detach().clone() for v in model.parameters()]
        pre = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        )
        post = math.sqrt(
            sum(float(v.grad.square().sum()) for v in model.parameters() if v.grad is not None)
        )
        if update:
            memory_check()
            opt.step()
        delta = math.sqrt(
            sum(float((v.detach() - b).square().sum()) for v, b in zip(model.parameters(), before))
        )
        if post > 1.00001 or not all(bool(torch.isfinite(v).all()) for v in model.parameters()):
            raise ValueError("S5S9_CLIP_OR_WEIGHTS")
        traces.append(
            dict(
                phase=phase,
                epoch=number,
                batch=k // 16,
                sessions=len(chosen),
                online_loss=float(loss.detach()),
                preclip=pre,
                postclip=post,
                update_norm=delta,
            )
        )
    pd.DataFrame(traces).to_csv(dest / f"{phase}_{number:03d}_batches.csv", index=False)
    pd.DataFrame(gradients).to_csv(dest / f"{phase}_{number:03d}_gradients.csv", index=False)
    return dict(
        phase=phase,
        epoch=number,
        steps=len(traces) if update else 0,
        batches=len(traces),
        dropout_on=True,
        online_objective=float(
            np.average([t["online_loss"] for t in traces], weights=[t["sessions"] for t in traces])
        ),
    )


def neural(data: Data, out: Path, year: int, arm: str) -> None:
    from .hf20_s5s9_report import baseline_event, export, finish_run

    ensure(out)
    resources(out, 200_000_000)
    run = f"HF20-{'S5' if arm == 'META-T2R' else 'S9'}-F{year % 100}-H4-{arm}-S42"
    dest = out / run
    dest.mkdir()
    started = time.monotonic()
    charged = False
    prefix_pending: str | None = None
    try:
        recipes = {}
        for phase in ("inner", "refit"):
            resources(out, 100_000_000)
            prefix_key = f"{run}/{phase}"
            baseline_event(out, prefix_key, "STARTED", prefix=True)
            prefix_pending = prefix_key
            recipes[phase] = fit_task(data, year, phase, arm, out)
            write(dest / f"{phase}_target_recipe.json", recipes[phase])
            baseline_event(out, prefix_pending, "COMPLETED", prefix=True)
            prefix_pending = None
        data.phase(year, "inner", recipes["inner"])
        print("START", event(out, run, "STARTED", dict(year=year, arm=arm)), run, flush=True)
        charged = True
        model = model_for(arm)
        initial = initial_hash(model)
        opt = optimizer(model)
        write(
            dest / "configuration.json",
            dict(
                arm=arm,
                seed=42,
                input_dim=model.input_dim,
                hidden=32,
                layers=1,
                dropout=0.1,
                head_outputs=model.head.out_features,
                optimizer="AdamW",
                learning_rate=0.001,
                betas=[0.9, 0.999],
                epsilon=1e-8,
                weight_decay_matrices=0.01,
                weight_decay_bias=0,
                gradient_cap=1.0,
                session_batch=16,
                min_epochs=12,
                max_epochs=60,
                patience=10,
                selection="absolute RankIC > best+.001"
                if arm == "META-T2R"
                else "proper loss <= .999*best",
                initial_sha256=initial,
                execution_sha256=code_hash(),
            ),
        )
        selector = RankSelector() if arm == "META-T2R" else Selector()
        fp, vp = (
            data.base.positions(year, "inner_train"),
            data.base.positions(year, "inner_validation"),
        )
        n = 0
        for n in range(1, 61):
            ensure(out)
            resources(out, 20_000_000)
            trace = epoch(data, fp, model, opt, arm, n, "calibration", dest)
            train = off(data, fp, predict(data, fp, model, arm), arm)
            val = off(data, vp, predict(data, vp, model, arm), arm)
            if isinstance(selector, RankSelector):
                qualifies = selector.observe(n, val["daily_ic"])
            else:
                qualifies = selector.observe(val["actual_objective"])
            torch.save(model.state_dict(), dest / f"calibration_{n:03d}.pt")
            write(
                dest / f"calibration_{n:03d}.json",
                dict(
                    **trace,
                    inner_train_off=train,
                    inner_validation_off=val,
                    qualifies=qualifies,
                    selector=vars(selector).copy(),
                ),
            )
            print(run, n, "selected", selector.selected, flush=True)
            if (
                selector.stop(n)
                if isinstance(selector, RankSelector)
                else selector.status != "CALIBRATING"
            ):
                break
        calibration_updates = n * math.ceil(data.base.rows.iloc[fp].session_date_et.nunique() / 16)
        if any(int(s["step"]) != calibration_updates for s in opt.state.values()):
            raise ValueError("S5S9_CALIBRATION_UPDATE_COUNT")
        torch.save(opt.state_dict(), dest / "calibration_stop_optimizer.pt")
        selected = selector.selected
        checkpoint = dest / f"calibration_{selected:03d}.pt"
        model.load_state_dict(torch.load(checkpoint, weights_only=True))
        write(
            dest / "calibration_binding.json",
            dict(
                selected=selected,
                checkpoint=str(checkpoint),
                checkpoint_sha256=digest(checkpoint),
                selector=vars(selector),
                optimizer_updates=calibration_updates,
            ),
        )
        for role in ROLES[:2]:
            export(
                data,
                year,
                role,
                arm,
                predict(data, data.base.positions(year, role), model, arm),
                dest,
                recipes["inner"],
            )
        event(out, run, "CALIBRATED", dict(selected=selected))
        event(out, run, "REFITTING", dict(selected=selected))
        resources(out, 200_000_000)
        data.phase(year, "refit", recipes["refit"])
        model = model_for(arm)
        opt = optimizer(model)
        if initial_hash(model) != initial or opt.state:
            raise ValueError("S5S9_REFIT_NOT_FRESH")
        rp = data.base.positions(year, "refit")
        for n in range(1, selected + 1):
            trace = epoch(data, rp, model, opt, arm, n, "refit", dest)
            write(
                dest / f"refit_{n:03d}.json",
                dict(**trace, refit_off=off(data, rp, predict(data, rp, model, arm), arm)),
            )
        checkpoint = dest / "refit_final.pt"
        torch.save(dict(model=model.state_dict(), optimizer=opt.state_dict()), checkpoint)
        replay = model_for(arm)
        saved = torch.load(checkpoint, weights_only=True)
        replay.load_state_dict(saved["model"])
        expected = selected * math.ceil(data.base.rows.iloc[rp].session_date_et.nunique() / 16)
        if any(int(v["step"]) != expected for v in saved["optimizer"]["state"].values()):
            raise ValueError("S5S9_UPDATE_COUNT")
        write(
            dest / "refit_binding.json",
            dict(
                selected=selected,
                optimizer_updates=expected,
                checkpoint=str(checkpoint),
                checkpoint_sha256=digest(checkpoint),
                reload_max_error=0,
            ),
        )
        for role in ROLES[2:]:
            pos = data.base.positions(year, role)
            raw = predict(data, pos, model, arm)
            np.testing.assert_array_equal(raw, predict(data, pos, replay, arm))
            export(data, year, role, arm, raw, dest, recipes["refit"])
        finish_run(data, year, arm, dest, recipes)
        gate = dict(
            status="PASS",
            seconds=time.monotonic() - started,
            resources=resources(out),
            files={str(p): digest(p) for p in sorted(dest.rglob("*")) if p.is_file()},
        )
        write(dest / "PASS.json", gate)
        event(out, run, "COMPLETED", dict(gate=str(dest / "PASS.json"), selected=selected))
    except BaseException as error:
        if prefix_pending is not None:
            baseline_event(out, prefix_pending, "FAILED", prefix=True)
        write(
            dest / ("FAILURE.json" if charged else "PRESTART_FAILURE.json"),
            dict(
                error_type=type(error).__name__,
                message=str(error),
                retry_authorized=False,
                neural_start_charged=charged,
            ),
        )
        if charged:
            event(out, run, "FAILED", dict(error_type=type(error).__name__, message=str(error)))
        raise


def run(out: Path) -> None:
    from .hf20_s5s9_report import closeout

    ensure(out)
    if JOURNAL.exists() or (out / "EXECUTION_STARTED.json").exists():
        raise ValueError("S5S9_NO_RESTART_OR_RETRY")
    if json.loads((out / "PREFLIGHT.json").read_text())["status"] != "PASS":
        raise ValueError("S5S9_PREFLIGHT_REQUIRED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    write(out / "EXECUTION_STARTED.json", dict(run_ids=RUNS, execution_sha256=code_hash()))
    data = Data()
    for arm in ARMS:
        for year in range(2021, 2025):
            neural(data, out, year, arm)
    del data
    gc.collect()
    closeout(out)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    run(p.parse_args().out)
