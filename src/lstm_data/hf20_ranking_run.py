"""Lean S1/S2 preflight and explicitly approved sequential historical fitting campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .hf1m_ft16_source import checked
from .hf20_ranking import (
    ARMS,
    GRID,
    RUNS,
    YEARS,
    RankSelector,
    daily_ic,
    linear_pair,
    origin_weights,
    rank_targets,
    ridge,
    ridge_solution,
    ridge_system,
    row_loss,
)
from .hf20_ranking_data import FoldData, fold_masks, metadata
from .neural_engine import SharedLSTM, optimizer, seed_all

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
CODE = (
    "src/lstm_data/hf20_ranking.py",
    "src/lstm_data/hf20_ranking_data.py",
    "src/lstm_data/hf20_ranking_run.py",
    "src/lstm_data/hf20_ranking_diagnostics.py",
    "src/lstm_data/hf20_ranking_authority.py",
)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write(path: Path, value: dict | list) -> None:
    """Immutable receipt, including per-epoch reports; never reuse a failed namespace."""
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)


def code_hash() -> str:
    return hashlib.sha256(
        json.dumps({p: sha(Path(p)) for p in CODE}, sort_keys=True).encode()
    ).hexdigest()


def initial_hash(model: SharedLSTM) -> str:
    h = hashlib.sha256()
    for name, value in model.state_dict().items():
        h.update(name.encode())
        h.update(value.detach().numpy().tobytes())
    return h.hexdigest()


def authorize(out: Path, path: Path | None) -> dict:
    """Reject absent/stale authority before historical feature decoding or any fit."""
    if path is None:
        raise ValueError("LIVE_APPROVAL_REQUIRED_BEFORE_FIT_IO")
    card = out / "proposal.json"
    approval = json.loads(path.read_text())
    plan = json.loads(card.read_text())
    if (
        approval.get("approved") is not True
        or approval.get("proposal_sha256") != sha(card)
        or approval.get("execution_sha256") != code_hash()
        or plan["execution_sha256"] != code_hash()
        or approval.get("baseline_fits") != 64
        or approval.get("neural_runs") not in (list(RUNS), [])
    ):
        raise ValueError("EXACT_S1_S2_AUTHORITY_MISMATCH")
    for r in plan["preserve_refs"]:
        if sha(Path(r["path"])) != r["sha256"]:
            raise ValueError("BOUND_SOURCE_CHANGED")
    approval["_approval_path"] = str(path)
    approval["_approval_sha256"] = sha(path)
    return approval


class Journal:
    """Separate finite baseline jobs; linked neural journal counts every attempted lifecycle."""

    def __init__(self, out: Path, approval: dict):
        self.out, self.approval = out, approval
        self.baseline_jobs = 0
        self.started = 62
        self.neural = Path("reports/audit/track_a_real_pairs_v19_hf20_ranking.jsonl")
        self.original = json.loads(POINTER.read_text())
        self.pending_baseline: str | None = None
        old = [json.loads(x) for x in Path(self.original["real_journal"]).read_text().splitlines()]
        if old[-1]["global_started_pairs"] != 62 or old[-1]["status"] != "COMPLETED":
            raise ValueError("PRIOR_NEURAL_LIFECYCLE_NOT_TERMINAL62")
        if self.original["real_journal"] != "reports/audit/track_a_real_pairs_v18_p028.jsonl":
            raise ValueError("EXPECTED_LEDGER62_BEFORE_CAMPAIGN")

    def baseline(self, key: str) -> None:
        from .hf20_ranking_authority import resources

        resources(self.out)
        if self.pending_baseline is not None:
            raise ValueError("PREVIOUS_BASELINE_NOT_VERIFIED")
        if self.baseline_jobs >= 64:
            raise ValueError("BASELINE_FIT_CAP")
        self.baseline_jobs += 1
        self.pending_baseline = key
        with (self.out / "baseline_fit_jobs.jsonl").open("a") as f:
            f.write(
                json.dumps(dict(job=self.baseline_jobs, key=key, status="STARTED", neural_charge=0))
                + "\n"
            )

    def baseline_done(self, status: str) -> None:
        if self.pending_baseline is None:
            raise ValueError("NO_BASELINE_JOB")
        with (self.out / "baseline_fit_jobs.jsonl").open("a") as f:
            f.write(
                json.dumps(dict(job=self.baseline_jobs, key=self.pending_baseline, status=status))
                + "\n"
            )
        self.pending_baseline = None

    def event(self, run: str, status: str, detail: dict) -> None:
        from .hf20_ranking_authority import append_neural

        self.started = append_neural(self.out, self.approval, self.original, run, status, detail)


def preflight(out: Path) -> None:
    if (out / "folds.json").exists():
        raise ValueError("PREFLIGHT_ALREADY_RECORDED")
    d, f, g = metadata(2021)
    # Only immutable raw-return operands, never future-fitted features as a fold input.
    raw = pd.read_parquet(
        checked(d["files"]["targets"]),
        filters=[("fit_version", "=", "inner"), ("session_date_et", "<=", "2024-12-31")],
    )
    plans = []
    for year in YEARS:
        plan, masks = fold_masks(year, f, g)
        plans.append(plan)
        for role, mask in masks.items():
            rows = f.loc[mask].sort_values("origin_id")
            target = raw.loc[raw.origin_id.isin(rows.origin_id)].copy()
            target["j"] = target.ticker.map({s: i for i, s in enumerate(d["symbols"])})
            target = target.sort_values(["origin_id", "j"])
            assert (
                len(target) == 20 * len(rows)
                and not target.duplicated(["origin_id", "ticker"]).any()
            )
            rr = target.return_4h.to_numpy(float).reshape(-1, 20)
            yy = target.TG20.to_numpy(float).reshape(-1, 20)
            np.testing.assert_array_equal(rank_targets(rr), rank_targets(yy))
            np.testing.assert_array_equal(rank_targets(rr), rank_targets(np.arcsinh(yy)))
            if not np.isfinite(rr).all():
                raise ValueError("MISSING_REAL_RETURN")
            rows[
                [
                    "origin_id",
                    "session_date_et",
                    "entry_index",
                    "first_step",
                    "entry_end_utc",
                    "exit_end_utc",
                    "label_maturity_utc",
                ]
            ].to_csv(out / f"F{year % 100}_{role}_indices.csv", index=False)
    write(out / "folds.json", plans)
    write(
        out / "preflight_numerics.json",
        dict(
            status="PASS_METADATA_AND_RANK_IDENTITY",
            actual_prefix_recipes_fitted=False,
            real_model_fits=0,
            real_optimizer_steps=0,
            protected_numeric_access=False,
            oos_predictions_generated=False,
            warning=(
                "Historical P020 targets used only to verify monotone rank identity; "
                "new fold losses require prefix epsilon/scale."
            ),
        ),
    )


def predict(
    data: FoldData, positions: np.ndarray, model: SharedLSTM | np.ndarray | str
) -> np.ndarray:
    values = []
    if isinstance(model, SharedLSTM):
        model.eval()
    with torch.no_grad():
        for start in range(0, len(positions), 16):
            x, _, _ = data.arrays(positions[start : start + 16])
            if isinstance(model, SharedLSTM):
                p = model(torch.from_numpy(x.reshape(-1, 48, 16))).numpy().reshape(-1, 20)
            elif isinstance(model, str):
                if model == "N0":
                    p = np.zeros((len(x), 20))
                elif model in ("N1", "N2"):
                    p = x[:, :, -1, 0] * (1 if model == "N1" else -1)
                else:
                    raise ValueError("NO_FIT_CONTROL")
            elif model.shape == (20,):
                p = np.broadcast_to(model, (len(x), 20))
            elif model.shape == (769,):
                p = x.reshape(-1, 20, 768) @ model[:-1] + model[-1]
            else:
                p = x.reshape(-1, 20, 768) @ model
            values.append(p)
    return np.concatenate(values)


def export(data: FoldData, year: int, role: str, arm: str, score: np.ndarray, dest: Path) -> dict:
    from .hf20_ranking_diagnostics import export_diagnostics

    return export_diagnostics(data, year, role, arm, score, dest)


def s1(data: FoldData, out: Path, journal: Journal) -> None:
    summaries = []
    for year in YEARS:
        fitpos = data.positions(year, "inner_train")
        valpos = data.positions(year, "inner_validation")
        refitpos = data.positions(year, "refit")
        testpos = data.positions(year, "oos")
        data.phase(year, "inner", out)
        profiles = {}
        for arm in ("P", "LR", "LP"):
            dest = out / f"F{year % 100}_S1_{arm}"
            dest.mkdir(exist_ok=False)
            grid = GRID if arm != "P" else (None,)
            candidates = []
            system = None
            for penalty in grid:
                journal.baseline(f"F{year % 100}/{arm}/inner/{penalty}")
                if arm == "P":
                    coef = np.average(
                        rank_targets(data.returns[fitpos]),
                        axis=0,
                        weights=origin_weights(data.rows.iloc[fitpos].session_date_et.to_numpy()),
                    )
                elif arm == "LR":
                    if system is None:
                        system = ridge_system(data.linear_stream(fitpos))
                    coef = ridge_solution(*system, float(penalty if penalty is not None else 0))
                else:
                    coef, convergence = linear_pair(
                        data.linear_stream(fitpos), float(penalty if penalty is not None else 0)
                    )
                    write(dest / f"inner_{penalty}_solver.json", convergence)
                p = predict(data, valpos, coef)
                ic = daily_ic(
                    data.returns[valpos], p, data.rows.iloc[valpos].session_date_et.to_numpy()
                )
                if not np.isfinite(ic):
                    raise ValueError("UNDEFINED_LINEAR_SELECTION_IC")
                candidates.append(dict(penalty=penalty, ic=ic))
                np.save(dest / f"inner_{penalty}.npy", coef)
                journal.baseline_done("COMPLETED")
            # Exact IC tie chooses larger penalty. No OOS score influences this choice.
            selected = max(candidates, key=lambda r: (r["ic"], r["penalty"] or 0))
            write(dest / "selection.json", dict(candidates=candidates, selected=selected))
            old = np.load(dest / f"inner_{selected['penalty']}.npy")
            for role, pos in [("inner_train", fitpos), ("inner_validation", valpos)]:
                export(data, year, role, arm, predict(data, pos, old), dest)
            profiles[arm] = (selected, dest)
        data.phase(year, "refit", out)
        for arm, (selected, dest) in profiles.items():
            journal.baseline(f"F{year % 100}/{arm}/refit")
            if arm == "P":
                coef = np.average(
                    rank_targets(data.returns[refitpos]),
                    axis=0,
                    weights=origin_weights(data.rows.iloc[refitpos].session_date_et.to_numpy()),
                )
            elif arm == "LR":
                coef = ridge(data.linear_stream(refitpos), float(selected["penalty"]))
            else:
                coef, convergence = linear_pair(
                    data.linear_stream(refitpos), float(selected["penalty"])
                )
                write(dest / "refit_solver.json", convergence)
            np.save(dest / "refit_coefficients.npy", coef)
            for role, pos in [("refit", refitpos), ("oos", testpos)]:
                summaries.append(export(data, year, role, arm, predict(data, pos, coef), dest))
            journal.baseline_done("COMPLETED")
        for arm in ("N0", "N1", "N2"):
            dest = out / f"F{year % 100}_S1_{arm}"
            dest.mkdir(exist_ok=False)
            summaries.append(export(data, year, "oos", arm, predict(data, testpos, arm), dest))
    pd.DataFrame(summaries).to_csv(out / "s1_summary.csv", index=False)
    from .hf20_ranking_diagnostics import verify_exports

    reconciliation = verify_exports(out, sorted(out.glob("F*_S1_*/*_scores.parquet")))
    if journal.baseline_jobs != 64:
        raise ValueError("S1_EXACT_FIT_ACCOUNTING")
    write(
        out / "S1_PASS.json",
        dict(
            status="PASS_TECHNICAL_NOT_PERFORMANCE",
            baseline_fits=journal.baseline_jobs,
            reconciliation=reconciliation,
        ),
    )


def epoch(
    model: SharedLSTM,
    opt: torch.optim.AdamW,
    data: FoldData,
    positions: np.ndarray,
    arm: str,
    number: int,
    phase: str,
    dest: Path,
) -> dict:
    from .hf20_ranking_authority import resources

    resources(dest.parent)
    groups = data.rows.iloc[positions].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    rng = np.random.default_rng(42 + number)
    rng.shuffle(days)
    telemetry = []
    model.train()
    for start in range(0, len(days), 16):
        chosen = days[start : start + 16]
        local = np.concatenate([groups[d] for d in chosen])
        pos = positions[local]
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
        loss.backward()
        before = [p.detach().clone() for p in model.parameters()]
        norm = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        )
        post = float(
            math.sqrt(
                sum(float(p.grad.square().sum()) for p in model.parameters() if p.grad is not None)
            )
        )
        opt.step()
        delta = float(
            math.sqrt(
                sum(
                    float((p.detach() - b).square().sum())
                    for p, b in zip(model.parameters(), before)
                )
            )
        )
        if not all(bool(torch.isfinite(p).all()) for p in model.parameters()):
            raise ValueError("NONFINITE_WEIGHTS")
        telemetry.append(
            dict(
                phase=phase,
                epoch=number,
                batch=start // 16,
                preclip=norm,
                postclip=post,
                update_norm=delta,
                parameter_norm=float(
                    math.sqrt(sum(float(p.detach().square().sum()) for p in model.parameters()))
                ),
                sessions=len(chosen),
                online_loss=float(loss.detach()),
            )
        )
    pd.DataFrame(telemetry).to_csv(dest / f"{phase}_{number:03d}_batches.csv", index=False)
    return dict(
        phase=phase,
        epoch=number,
        steps=len(telemetry),
        online_objective=float(
            np.average(
                [r["online_loss"] for r in telemetry], weights=[r["sessions"] for r in telemetry]
            )
        ),
    )


def s2(data: FoldData, out: Path, journal: Journal) -> None:
    if not (out / "S1_PASS.json").is_file():
        raise ValueError("S1_GATE_REQUIRED")
    for year in YEARS:
        for arm in ARMS:
            run = f"HF20-S1S2-F{year % 100}-{arm}-S42"
            dest = out / run
            dest.mkdir(exist_ok=False)
            journal.event(run, "STARTED", {})
            try:
                started = time.monotonic()
                seed_all(42)
                model = SharedLSTM().float()
                initial = initial_hash(model)
                if sum(p.numel() for p in model.parameters()) != 6433:
                    raise ValueError("EXACT_TM0_PARAMETER_COUNT")
                opt = optimizer(model)
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
                    export(data, year, role, arm, predict(data, pos, model), dest)
                journal.event(run, "CALIBRATED", vars(selector).copy())
                journal.event(run, "REFITTING", dict(selected_epoch=selector.selected))
                seed_all(42)
                model = SharedLSTM().float()
                if initial_hash(model) != initial:
                    raise ValueError("REFIT_NOT_FRESH_SEED42")
                opt = optimizer(model)
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
                    export(data, year, role, arm, predict(data, pos, model), dest)
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
            except BaseException as error:
                journal.event(
                    run, "FAILED", dict(error_type=type(error).__name__, message=str(error))
                )
                raise


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--run", action="store_true")
    p.add_argument("--approval", type=Path)
    args = p.parse_args()
    if args.prepare == args.run:
        raise ValueError("EXACTLY_ONE_MODE")
    if args.prepare:
        preflight(args.out)
        return
    approval = authorize(args.out, args.approval)
    os.environ.update(
        {
            k: "4"
            for k in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
            )
        }
    )
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if (args.out / "baseline_fit_jobs.jsonl").exists():
        raise ValueError("NO_AUTOMATIC_RETRY")
    from .hf20_ranking_authority import resources

    resources(args.out)
    journal = Journal(args.out, approval)
    write(
        args.out / "execution_authority_ref.json",
        dict(path=str(args.approval), sha256=sha(args.approval)),
    )
    data = FoldData(live_approved=True)
    try:
        s1(data, args.out, journal)
    except BaseException:
        if journal.pending_baseline is not None:
            journal.baseline_done("FAILED")
        raise
    if approval["neural_runs"]:
        s2(data, args.out, journal)
    from .hf20_ranking_diagnostics import closeout

    closeout(args.out)


if __name__ == "__main__":
    main()
