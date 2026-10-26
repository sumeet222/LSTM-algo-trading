"""Exactly eight prospectively authorized S4 neural lifecycles, with strict PASS gates."""

from __future__ import annotations

import argparse
import gc
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .hf1m_action_audit import digest
from .hf20_ranking import RankSelector, daily_ic, origin_weights, rank_targets, row_loss
from .hf20_ranking_continue import check_configuration
from .hf20_ranking_run import initial_hash, predict, write
from .hf20_s4_authority import JOURNAL, RUNS, authorize, event, execution_hash, resources
from .hf20_s4_closeout import closeout, per_run
from .hf20_s4_data import ROLES, S4Data
from .hf20_s4_diagnostics import export, gate, verify
from .hf20_s4_epoch import epoch
from .hf20_s4_preflight import expanded_m2, load_source
from .hf20_s4_visuals import build
from .neural_engine import SharedLSTM, optimizer, seed_all


def source_data(out: Path) -> S4Data:
    authorize(out)
    card = json.loads((out / "S4_FROZEN_EXPERIMENT_CARD.json").read_text())
    audit = Path(card["source_audit"])
    c, hours, prices, _, _ = load_source(audit)
    del hours, prices
    clock = pd.read_parquet(audit / "S4_ORIGIN_SOURCE_ELIGIBILITY.parquet")
    target = pd.read_parquet(audit / "S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet")
    np.testing.assert_array_equal(target.origin_id.to_numpy()[::20], clock.origin_id)
    np.testing.assert_array_equal(target.ticker.to_numpy(), np.tile(card["symbols"], len(clock)))
    returns = target.direct_return.to_numpy().reshape(-1, 20)
    mean, rms, _ = expanded_m2(c, clock, returns)
    c.m2_mean, c.m2_rms = mean, rms
    data = S4Data(c, clock, returns)
    data.target_components = target
    return data


def off_metrics(data: S4Data, pos: np.ndarray, scores: np.ndarray, arm: str) -> dict:
    r = data.returns[pos]
    med = np.median(r, axis=1)
    mad = np.median(abs(r - med[:, None]), axis=1)
    y = (r - med[:, None]) / (mad[:, None] + data.recipe["epsilon"])
    allocation = row_loss(
        arm,
        torch.from_numpy(scores),
        torch.from_numpy(r),
        torch.from_numpy(y.astype(np.float32)),
        data.recipe["t2_scale"],
    ).numpy()
    weights = origin_weights(data.rows.iloc[pos].session_date_et.to_numpy())
    return dict(
        actual_objective=float(weights @ allocation.sum(1)),
        daily_ic=daily_ic(r, scores, data.rows.iloc[pos].session_date_et.to_numpy()),
        dropout_on=False,
        origins=len(pos),
    )


def baseline_event(out: Path, key: str, status: str) -> None:
    authorize(out)
    path = out / "S4_BASELINE_ATTEMPTS.jsonl"
    old = [json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []
    starts = [r["key"] for r in old if r["status"] == "STARTED"]
    expected = [
        f"F{year % 100}/P/{phase}" for year in range(2021, 2025) for phase in ("inner", "refit")
    ]
    if status == "STARTED":
        resources(out, approved=True, reserve_bytes=80_000_000)
        if (
            len(starts) >= 8
            or key != expected[len(starts)]
            or (old and old[-1]["status"] != "COMPLETED")
        ):
            raise ValueError("S4_BASELINE_ORDER_NO_RETRY_OR_EXTRA")
    elif not old or old[-1]["status"] != "STARTED" or old[-1]["key"] != key:
        raise ValueError("S4_BASELINE_NOT_PENDING")
    with path.open("a") as f:
        f.write(json.dumps(dict(key=key, status=status, neural_charge=0)) + "\n")
        f.flush()


def baselines(data: S4Data, out: Path) -> None:
    for year in range(2021, 2025):
        for role in ROLES:
            data.rows.iloc[data.positions(year, role)].to_csv(
                out / f"F{year % 100}_{role}_indices.csv", index=False
            )
        for phase, roles in (("inner", ROLES[:2]), ("refit", ROLES[2:])):
            resources(out, approved=True, reserve_bytes=80_000_000)
            data.phase(year, phase, out)
            key = f"F{year % 100}/P/{phase}"
            baseline_event(out, key, "STARTED")
            try:
                pos = data.positions(year, roles[0])
                profile = np.average(
                    rank_targets(data.returns[pos]),
                    axis=0,
                    weights=origin_weights(data.rows.iloc[pos].session_date_et.to_numpy()),
                )
                p = out / f"F{year % 100}_S4_P"
                p.mkdir(exist_ok=True)
                if phase == "inner":
                    write(
                        p / "selection.json",
                        dict(selected=dict(penalty=None), no_hyperparameter_search=True),
                    )
                np.save(
                    p / ("inner_None.npy" if phase == "inner" else "refit_coefficients.npy"),
                    profile,
                )
                for arm, model in (("P", profile), ("N0", "N0"), ("N1", "N1"), ("N2", "N2")):
                    dest = out / f"F{year % 100}_S4_{arm}"
                    dest.mkdir(exist_ok=True)
                    for role in roles:
                        pos = data.positions(year, role)
                        export(
                            data, year, role, arm, predict(data, pos, model), dest, execution_hash()
                        )
                baseline_event(out, key, "COMPLETED")
            except BaseException:
                baseline_event(out, key, "FAILED")
                raise
        verify(data, year, out / f"F{year % 100}_S4_P")
    write(
        out / "S4_BASELINE_PASS.json",
        dict(
            status="PASS",
            attempts=8,
            controls=["N0", "N1", "N2", "P"],
            LR="NOT_INCLUDED_OPTIONAL",
            neural_starts=0,
        ),
    )


def neural_one(data: S4Data, out: Path, year: int, arm: str) -> None:
    authorize(out)
    resources(out, approved=True, reserve_bytes=80_000_000)
    data.phase(year, "inner", out)
    run = f"HF20-S4A-F{year % 100}-H4-{arm}-S42"
    dest = out / run
    dest.mkdir()
    count = event(out, run, "STARTED", dict(year=year, arm=arm))
    print("START", count, run, flush=True)
    started = time.monotonic()
    try:
        seed_all(42)
        model = SharedLSTM().float()
        initial = initial_hash(model)
        opt = optimizer(model)
        write(dest / "calibration_configuration.json", check_configuration(model, opt))
        fp, vp = data.positions(year, "inner_train"), data.positions(year, "inner_validation")
        selector = RankSelector()
        for n in range(1, 61):
            resources(out, approved=True, reserve_bytes=10_000_000)
            receipt = epoch(model, opt, data, fp, arm, n, "calibration", dest)
            val = predict(data, vp, model)
            train = predict(data, fp, model)
            ic = daily_ic(data.returns[vp], val, data.rows.iloc[vp].session_date_et.to_numpy())
            qualifies = selector.observe(n, ic)
            torch.save(model.state_dict(), dest / f"calibration_{n:03d}.pt")
            write(
                dest / f"calibration_{n:03d}.json",
                dict(
                    **receipt,
                    ic=ic,
                    qualifies=qualifies,
                    selector=vars(selector).copy(),
                    inner_train_off=off_metrics(data, fp, train, arm),
                    inner_validation_off=off_metrics(data, vp, val, arm),
                ),
            )
            print(run, "epoch", n, "IC", ic, "selected", selector.selected, flush=True)
            if selector.stop(n):
                break
        torch.save(opt.state_dict(), dest / "calibration_stop_optimizer.pt")
        checkpoint = dest / f"calibration_{selector.selected:03d}.pt"
        model.load_state_dict(torch.load(checkpoint, weights_only=True))
        write(
            dest / "calibration_binding.json",
            dict(
                checkpoint=str(checkpoint),
                checkpoint_sha256=digest(checkpoint),
                selected=selector.selected,
                raw_best_epoch=selector.raw_epoch,
            ),
        )
        for role in ROLES[:2]:
            pos = data.positions(year, role)
            export(data, year, role, arm, predict(data, pos, model), dest, execution_hash())
        event(out, run, "CALIBRATED", vars(selector).copy())
        event(out, run, "REFITTING", dict(selected_epoch=selector.selected))
        seed_all(42)
        model = SharedLSTM().float()
        opt = optimizer(model)
        if initial_hash(model) != initial or opt.state:
            raise ValueError("S4_REFIT_NOT_FRESH")
        write(dest / "refit_configuration.json", check_configuration(model, opt))
        data.phase(year, "refit", out)
        rp = data.positions(year, "refit")
        for n in range(1, selector.selected + 1):
            resources(out, approved=True, reserve_bytes=10_000_000)
            receipt = epoch(model, opt, data, rp, arm, n, "refit", dest)
            write(
                dest / f"refit_{n:03d}.json",
                dict(**receipt, refit_off=off_metrics(data, rp, predict(data, rp, model), arm)),
            )
        checkpoint = dest / "refit_final.pt"
        torch.save(dict(model=model.state_dict(), optimizer=opt.state_dict()), checkpoint)
        saved = torch.load(checkpoint, weights_only=True)
        replay = SharedLSTM().float()
        replay.load_state_dict(saved["model"])
        expected = selector.selected * math.ceil(data.rows.iloc[rp].session_date_et.nunique() / 16)
        if any(int(s["step"]) != expected for s in saved["optimizer"]["state"].values()):
            raise ValueError("S4_OPTIMIZER_UPDATE_COUNT")
        write(
            dest / "refit_binding.json",
            dict(
                checkpoint=str(checkpoint),
                checkpoint_sha256=digest(checkpoint),
                optimizer_updates=expected,
                selected=selector.selected,
            ),
        )
        for role in ROLES[2:]:
            pos = data.positions(year, role)
            scores = predict(data, pos, model)
            np.testing.assert_array_equal(scores, predict(data, pos, replay))
            export(data, year, role, arm, scores, dest, execution_hash())
        verify(data, year, dest)
        build(out, dest)
        per_run(out, dest)
        gate(
            dest,
            dict(
                selector=vars(selector),
                seconds=time.monotonic() - started,
                initial_sha256=initial,
                checkpoint_reload_max_error=0,
                resources=resources(out, approved=True),
            ),
        )
        event(
            out,
            run,
            "COMPLETED",
            dict(gate=str(dest / "PASS.json"), selected_epoch=selector.selected),
        )
        print("COMPLETED", run, flush=True)
    except BaseException as error:
        write(
            dest / "FAILURE.json",
            dict(error_type=type(error).__name__, message=str(error), retry_authorized=False),
        )
        event(out, run, "FAILED", dict(error_type=type(error).__name__, message=str(error)))
        raise


def run(out: Path) -> None:
    authorize(out)
    if JOURNAL.exists() or (out / "S4_EXECUTION_STARTED.json").exists():
        raise ValueError("S4_NO_IMPLICIT_RETRY")
    if json.loads((out / "S4_READINESS_PASS.json").read_text())["status"] != "PASS":
        raise ValueError("S4_READINESS_REQUIRED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    write(out / "S4_EXECUTION_STARTED.json", dict(execution_sha256=execution_hash(), run_ids=RUNS))
    data = source_data(out)
    baselines(data, out)
    for year in range(2021, 2025):
        for arm in ("NR", "T2R"):
            neural_one(data, out, year, arm)
            gc.collect()
    closeout(out)
    write(
        out / "S4_EIGHT_MODELS_COMPLETED.json",
        dict(
            status="EIGHT_STAGE_GATES_PASS_COLLECTIVE_REVIEW_PENDING", neural_starts=8, ledger=114
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    run(p.parse_args().out)
