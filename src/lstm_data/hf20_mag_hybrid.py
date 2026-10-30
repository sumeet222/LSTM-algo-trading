"""One frozen CLOCK magnitude/ranking hybrid; reuse historical kernels unchanged."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_mag_o1 as o1
from . import hf20_mag_rank as rank
from . import hf20_stage2_bcd as clock
from .hf20_s4_clock import sessions

OUT = Path("reports/experiments/hf20_s9_mag_stage5_session2_hybrid_C_2026-10-29")
RAW, CAL = "S5C-RAW", "S5C-C3"
LAMBDA = 0.25


def preferences(a: np.ndarray) -> np.ndarray:
    """Exact original A ties; this approved arm retains all-tied origins."""
    rank.targets(a)  # finite nonnegative complete-panel assertion only
    return np.sign(a[:, rank.PAIR_I] - a[:, rank.PAIR_J]).astype(np.float32)


def phase_constants(a: np.ndarray, days: np.ndarray, scale: float) -> dict:
    """Two-pass float64 global variance from one legal training role only."""
    preferences(a)
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("INVALID_PHASE_SCALE")
    w = b.origin_weights(days)
    m = np.log1p(a.astype(np.float64) / scale)
    mu = float(w @ m.mean(1))
    variance = float(w @ ((m - mu) ** 2).mean(1))
    tau = math.sqrt(variance)
    if not all(math.isfinite(x) for x in [mu, variance, tau]) or min(variance, tau) <= 0:
        raise ValueError("NONPOSITIVE_PHASE_VARIANCE")
    return dict(scale=scale, mu=mu, variance=variance, tau=tau, lambda_fixed=LAMBDA)


def components(
    z: torch.Tensor, target: torch.Tensor, y: torch.Tensor, variance: float, tau: float
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Per-origin unscaled MSE, pair mean and normalized hybrid; no detached score."""
    if z.shape != target.shape or z.ndim != 2 or z.shape[1] != 20 or y.shape != (len(z), 190):
        raise ValueError("COMPLETE_PANEL_SHAPE")
    if not all(math.isfinite(x) and x > 0 for x in [variance, tau]):
        raise ValueError("INVALID_FROZEN_NORMALIZER")
    if not all(bool(torch.isfinite(x).all()) for x in [z, target, y]):
        raise ValueError("NONFINITE_HYBRID_INPUT")
    valid = y != 0
    margins = (z[:, rank.PAIR_I] - z[:, rank.PAIR_J]) / tau
    pair = (torch.nn.functional.softplus(-y * margins) * valid).sum(1) / valid.sum(1).clamp_min(1)
    mag = (z - target).square().mean(1)
    return mag, pair, mag / variance + LAMBDA * pair / math.log(2)


def reduced(
    z: torch.Tensor, a: np.ndarray, days: np.ndarray, constants: dict
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Original float32 M construction; exact float64 A sign, fixed phase moments."""
    target = torch.log1p(torch.as_tensor(a, dtype=z.dtype) / constants["scale"])
    y = torch.as_tensor(preferences(a), dtype=z.dtype)
    parts = components(z, target, y, constants["variance"], constants["tau"])
    w = torch.as_tensor(b.origin_weights(days), dtype=z.dtype)
    return (w * parts[0]).sum(), (w * parts[1]).sum(), (w * parts[2]).sum()


def resources() -> dict:
    # Aggregate directory bytes without exposing protected path names/metadata.
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    result = dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())
    if project + 30_000_000 > b.CAPS["project_bytes"] or task + 30_000_000 > b.CAPS["task_bytes"]:
        raise ValueError("RESOURCE_CEILING", result)
    return result


def bindings() -> None:
    """Check only explicitly authorized files; never scan protected sources."""
    protocol = b.read(OUT / "protocol.json")
    for name, sha in protocol["preservation_bindings"].items():
        if name != str(b.POINTER):
            assert b.digest(Path(name)) == sha, name


def prepare() -> None:
    """All-four causal scale/input/key and calibration-geometry gates, no model fit."""
    if (OUT / "preflight.json").exists():
        raise ValueError("SINGLE_USE_PREFLIGHT")
    bindings()
    assert b.read(b.POINTER) == b.read(OUT / "protocol.json")["previous_pointer"]
    grid, rows = b.metadata()
    plans = rank.validate_roles(grid, rows)
    clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
    c, r = b.source_components(grid, rows)
    counts, scales = [], []
    for year in b.YEARS:
        dest = OUT / f"F{year % 100}"
        dest.mkdir(exist_ok=False)
        old = b.read(o1.OUT / f"F{year % 100}/phases.json")
        phases = {}
        for role, pos in plans[year].items():
            y = preferences(abs(r[pos]))
            counts.append(
                dict(
                    year=year,
                    role=role,
                    rows=len(pos) * 20,
                    origins=len(pos),
                    sessions=int(rows.iloc[pos].session_date_et.nunique()),
                    true_tied_pairs=int((y == 0).sum()),
                    all_tied_origins=int((y == 0).all(1).sum()),
                    min_valid_pairs=int((y != 0).sum(1).min()),
                )
            )
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            cutoff = old["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(grid, rows, cutoff), cutoff, approved=True
            )
            ref = o1.OUT / f"F{year % 100}/{phase}_recipe.json"
            assert recipe == b.read(ref)
            pos = plans[year][role]
            days = rows.iloc[pos].session_date_et.to_numpy()
            w = np.repeat(b.origin_weights(days) / 20, 20)
            scale = max(b.quantile(abs(r[pos]).ravel(), 0.5, w), 1e-8)
            assert scale == old["phases"][phase]["scale"]
            constants = phase_constants(abs(r[pos]), days, scale)
            constants.update(
                cutoff=cutoff,
                role=role,
                first_date=str(min(days)),
                last_date=str(max(days)),
                rows=len(pos) * 20,
                sessions=len(set(days)),
                recipe_reference=str(ref),
                recipe_sha256=b.digest(ref),
            )
            phases[phase] = constants
            scales.append(dict(year=year, phase=phase, **constants, risk_check="PASS"))
            view = b.View(c, rows, r, recipe, scale)
            for name in [role, "selector"] if phase == "initial" else [role, "calibration", "oos"]:
                ix = plans[year][name]
                for k in range(0, len(ix), 64):
                    x = view.x(ix[k : k + 64])
                    assert x.shape[1:] == (20, 48, 16) and np.isfinite(x).all()
            del view
            gc.collect()
        for name in ["calibration", "oos"]:
            # Keys/labels/source agreement only; no forecast scoring or choice here.
            f = pd.read_parquet(c3.root(year) / f"{name}_scores.parquet", columns=[*c3.META, "A"])
            np.testing.assert_array_equal(f.A, abs(r[plans[year][name]]).ravel())
            if name == "calibration":
                for group in c3.GROUPS:
                    assert c3.effective_sessions(f.loc[f.category.eq(group)]) > 0
        b.write(
            dest / "phases.json",
            dict(year=year, phases=phases, thresholds=old["thresholds"]),
            new=True,
        )
    pd.DataFrame(counts).to_csv(OUT / "role_counts.csv", index=False)
    pd.DataFrame(scales).to_csv(OUT / "phase_scales.csv", index=False)
    pd.DataFrame(clocks, columns=[f"clock{i}" for i in range(10)]).drop_duplicates().to_csv(
        OUT / "clock_dictionary.csv", index=False
    )
    b.write(
        OUT / "preflight.json",
        dict(
            status="PASS_ALL_FOUR",
            OOS_rows=80260,
            OOS_origins=4013,
            OOS_sessions=793,
            roles=counts,
            scales=scales,
            resources=resources(),
            no_minute_source=True,
            no_future_normalizers=True,
            calibration_geometry_pass=True,
        ),
        new=True,
    )


def epoch(
    view: b.View,
    pos: np.ndarray,
    model: clock.ClockMAG,
    opt: torch.optim.AdamW,
    number: int,
    clocks: np.ndarray,
    constants: dict,
) -> dict:
    """Session-unbiased batches; reported training components are online batch means."""
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    norms, totals = [], np.zeros(3)
    model.train()
    for k in range(0, len(days), 16):
        batchdays = days[k : k + 16]
        ix = pos[np.concatenate([groups[d] for d in batchdays])]
        opt.zero_grad()
        z = model(
            torch.from_numpy(view.x(ix).reshape(-1, 48, 16)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
        ).reshape(-1, 20)
        parts = reduced(
            z, abs(view.r[ix]), view.rows.iloc[ix].session_date_et.to_numpy(), constants
        )
        if not bool(torch.isfinite(parts[2])):
            raise ValueError("NONFINITE_HYBRID_LOSS")
        totals += np.array([float(v.detach()) for v in parts]) * len(batchdays) / len(days)
        parts[2].backward()
        norms.append(
            float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True))
        )
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        train_M_MSE=totals[0],
        train_pair_loss=totals[1],
        train_hybrid=totals[2],
        steps=len(norms),
        gradient_norm_max=max(norms),
        clipped_batches=sum(x > 1 for x in norms),
    )


def journal(year: int, status: str, detail: dict) -> None:
    protocol = b.read(OUT / "protocol.json")
    path = OUT / "neural_starts.jsonl"
    history = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    starts = sum(x["status"] == "STARTED" for x in history)
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["previous_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert starts < 4 and year == protocol["order"][starts]
        assert not history or history[-1]["status"] == "COMPLETED"
        ready = b.read(OUT / "readiness.json")
        assert ready["status"] == "READY"
        for name, sha in ready["hashes"].items():
            assert b.digest(Path(name)) == sha, name
        bindings()
        resources()
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        year=year,
        status=status,
        global_started_pairs=182 + starts + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
        previous_journal=dict(
            path=protocol["previous_pointer"]["real_journal"],
            sha256=protocol["preservation_bindings"][protocol["previous_pointer"]["real_journal"]],
        ),
        plan=dict(path=str(OUT / "protocol.json"), sha256=b.digest(OUT / "protocol.json")),
    )
    with path.open("a") as h:
        h.write(json.dumps(row) + "\n")
        h.flush()
        os.fsync(h.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=35,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def run_fold(
    year: int, c: b.Components, rows: pd.DataFrame, r: np.ndarray, clocks: np.ndarray
) -> None:
    dest = OUT / f"F{year % 100}"
    plans = clock.saved_plans(rows)[year]
    phases = b.read(dest / "phases.json")["phases"]
    initial, restricted = phases["initial"], phases["restricted"]
    view = b.View(c, rows, r, b.read(Path(initial["recipe_reference"])), initial["scale"])
    model = clock.model_for_clock()
    init = b.initial_hash(model)
    opt = b.optimizer(model)
    selector = b.Selector()
    best = {}
    trace = []
    started = time.monotonic()
    journal(year, "STARTED", dict(seed=42, parameters=6443, run_id=f"HF20-S5C-F{year % 100}-S42"))
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            tick = time.monotonic()
            stats = epoch(view, plans["inner_train"], model, opt, n, clocks, initial)
            ix = plans["selector"]
            z = clock.predict_clock(view, ix, model, clocks)
            parts = reduced(
                torch.from_numpy(z), abs(r[ix]), rows.iloc[ix].session_date_et.to_numpy(), initial
            )
            mag, pair, hybrid = [float(v) for v in parts]
            if selector.observe(hybrid):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_M_MSE=mag,
                    validation_pair_loss=pair,
                    validation_hybrid=hybrid,
                    selected=selector.selected,
                    seconds=time.monotonic() - tick,
                    **stats,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print(year, "selector", n, hybrid, "best", selector.selected, flush=True)
        model.load_state_dict(best)
        torch.save(model.state_dict(), dest / "selected_initial.pt")
        b.write(
            dest / "selection.json",
            dict(vars(selector), selected_parameter_hash=b.initial_hash(model)),
            new=True,
        )
        journal(year, "SELECTED", dict(epoch=selector.selected, raw_epoch=selector.raw_epoch))
        del view, model, opt, best
        gc.collect()
        view = b.View(c, rows, r, b.read(Path(restricted["recipe_reference"])), restricted["scale"])
        model = clock.model_for_clock()
        opt = b.optimizer(model)
        assert b.initial_hash(model) == init and not opt.state
        journal(year, "REFITTING", dict(epochs=selector.selected))
        for n in range(1, selector.selected + 1):
            tick = time.monotonic()
            stats = epoch(view, plans["restricted_refit"], model, opt, n, clocks, restricted)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - tick, **stats))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print(year, "refit", n, "of", selector.selected, flush=True)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        frozen = b.initial_hash(model)
        zcal = clock.predict_clock(view, plans["calibration"], model, clocks)
        cal = pd.read_parquet(c3.root(year) / "calibration_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(cal.A, abs(r[plans["calibration"]]).ravel())
        cal["Mhat"] = zcal.ravel()
        # Persist raw calibration predictions before fitting, so failures remain traceable.
        cal.to_parquet(dest / "calibration_scores.parquet", compression="zstd", index=False)
        coeff = c3.fit_categories(cal, view.scale)
        pd.DataFrame(coeff).to_csv(dest / "calibration_coefficients.csv", mode="x", index=False)
        factors = {x["group"]: x["c_star"] for x in coeff}
        z = clock.predict_clock(view, plans["oos"], model, clocks)
        reload = clock.model_for_clock()
        reload.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, clock.predict_clock(view, plans["oos"], reload, clocks))
        np.testing.assert_array_equal(
            zcal, clock.predict_clock(view, plans["calibration"], reload, clocks)
        )
        assert b.initial_hash(model) == frozen
        f = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(f.A, abs(r[plans["oos"]]).ravel())
        f["Mhat"] = z.ravel()
        f[RAW] = clock.previous.raw_decode(z, view.scale).ravel()
        f[CAL] = c3.decode(z.ravel(), view.scale, f.category.map(factors).to_numpy())
        for name in ["Mhat", RAW, CAL]:
            f[name + "_rank"] = f.groupby("origin_id")[name].rank(method="average")
        f.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
        result = dict(
            year=year,
            status="COMPLETED",
            parameters=6443,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_hash=init,
            frozen_parameter_hash=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            scale=view.scale,
            calibration_valid=True,
            seconds=time.monotonic() - started,
            resources=resources(),
        )
        b.write(dest / "result.json", result, new=True)
        journal(year, "COMPLETED", result)
        del view, model, opt, reload
        gc.collect()
    except BaseException as exc:
        journal(year, "FAILED", dict(error=repr(exc), retry=False))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for flag in ["prepare", "run", "report"]:
        mode.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.prepare:
        prepare()
    elif args.run:
        if (OUT / "neural_starts.jsonl").exists():
            raise ValueError("SINGLE_USE_NO_RELAUNCH")
        assert b.read(OUT / "readiness.json")["status"] == "READY"
        bindings()
        resources()
        grid, rows = b.metadata()
        rank.validate_roles(grid, rows)
        clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
        c, r = b.source_components(grid, rows)
        for year in b.YEARS:
            run_fold(year, c, rows, r, clocks)
    else:
        from .hf20_mag_hybrid_report import report

        report()


if __name__ == "__main__":
    main()
