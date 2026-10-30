"""Frozen Stage5 absolute-magnitude rank objectives; no magnitude decoder/calibrator."""

from __future__ import annotations

import argparse
import gc
import json
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
from . import hf20_stage2_bcd as clock
from .hf20_s4_clock import sessions

OUT = Path("reports/experiments/hf20_s9_mag_stage5_session1_rank_AB_2026-10-29")
PAIR_I, PAIR_J = np.triu_indices(20, 1)


def targets(a: np.ndarray) -> np.ndarray:
    """Ascending midranks of raw absolute outcome, never stock-normalized/signed."""
    if a.ndim != 2 or a.shape[1] != 20 or not np.isfinite(a).all() or (a < 0).any():
        raise ValueError("FINITE_NONNEGATIVE_COMPLETE20_REQUIRED")
    return 2 * (pd.DataFrame(a).rank(axis=1, method="average").to_numpy() - 1) / 19 - 1


def preferences(a: np.ndarray) -> np.ndarray:
    """Float64 outcome equality defines exact true ties before float32 optimization."""
    targets(a)
    y = np.sign(a[:, PAIR_I] - a[:, PAIR_J])
    if (np.count_nonzero(y, axis=1) == 0).any():
        raise ValueError("ORIGIN_WITH_NO_UNEQUAL_PAIR")
    return y.astype(np.float32)


def origin_loss(z: torch.Tensor, label: torch.Tensor, arm: str) -> torch.Tensor:
    """Full20 rank-MSE or once-only valid-pair logistic mean, per origin."""
    if z.ndim != 2 or z.shape[1] != 20 or not bool(torch.isfinite(z).all()):
        raise ValueError("FINITE_COMPLETE20_SCORE_REQUIRED")
    if arm == "S5A":
        if label.shape != z.shape:
            raise ValueError("RANK_LABEL_SHAPE")
        return (z - label).square().mean(1)
    if arm != "S5B" or label.shape != (len(z), 190):
        raise ValueError("PAIR_LABEL_SHAPE_OR_ARM")
    valid = label != 0
    count = valid.sum(1)
    if bool((count == 0).any()):
        raise ValueError("NO_VALID_PAIR")
    return (torch.nn.functional.softplus(-label * (z[:, PAIR_I] - z[:, PAIR_J])) * valid).sum(
        1
    ) / count


def loss(z: torch.Tensor, label: torch.Tensor, days: np.ndarray, arm: str) -> torch.Tensor:
    """Equal origins within each session, then equal sessions; batch means unbiased."""
    w = torch.as_tensor(b.origin_weights(days), dtype=z.dtype)
    return (w * origin_loss(z, label, arm)).sum()


def conservative_ic(a: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Average-rank Spearman with explicit zero contribution for undefined origins."""
    x, y = pd.DataFrame(a).rank(axis=1).to_numpy(), pd.DataFrame(z).rank(axis=1).to_numpy()
    x = x - x.mean(1, keepdims=True)
    y = y - y.mean(1, keepdims=True)
    den = np.sqrt((x * x).sum(1) * (y * y).sum(1))
    return np.divide((x * y).sum(1), den, out=np.zeros(len(x)), where=den > 0)


def resources() -> dict:
    """Aggregate filesystem size only, no protected-content/hash discovery."""
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    r = dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())
    if project + 30_000_000 > b.CAPS["project_bytes"] or task + 30_000_000 > b.CAPS["task_bytes"]:
        raise ValueError("RESOURCE_CEILING", r)
    return r


def validate_roles(grid: pd.DataFrame, rows: pd.DataFrame) -> dict:
    """Reconcile saved five-role geometry without changing any eligibility rule."""
    plans = clock.saved_plans(rows)
    counts = pd.read_csv(c3.CONT / "role_counts.csv")
    first = np.full(len(rows), "0000", object)
    good = rows.first_step.ge(0)
    first[good] = grid.session_date_et.to_numpy()[rows.loc[good, "first_step"].to_numpy(int)]
    for year in b.YEARS:
        for item in counts.loc[counts.year.eq(year)].to_dict("records"):
            role = str(item["role"])
            pos = plans[year][role]
            expected = np.flatnonzero(
                b.role_mask(
                    rows, first, str(item["start"]), str(item["cutoff"]), str(item["embargo_after"])
                )
            )
            np.testing.assert_array_equal(pos, expected)
            assert (rows.iloc[pos].entry_index - rows.iloc[pos].first_step).eq(47).all()
            assert rows.iloc[pos].label_maturity_utc.lt(b.limit(str(item["cutoff"]))).all()
            if role == "selector":
                f = rows.iloc[pos]
                assert (
                    f.session_date_et.nunique() >= 50
                    and f.groupby("slot").size().reindex(b.SLOTS, fill_value=0).min() >= 25
                )
        for left, right in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(plans[year][left], plans[year][right]).size
        pos = plans[year]["oos"]
        assert len(pos) * 20 == {2021: 19100, 2022: 23600, 2023: 17740, 2024: 19820}[year]
        for root in [
            c3.root(year),
            clock.OUT / f"s2b_clock/F{year % 100}",
            Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28") / f"F{year % 100}",
        ]:
            k = pd.read_parquet(root / "oos_scores.parquet", columns=[*c3.META])
            np.testing.assert_array_equal(k.origin_id, np.repeat(rows.iloc[pos].origin_id, 20))
            assert k.ticker.tolist() == list(b.SYMBOLS) * len(pos)
            np.testing.assert_allclose(
                k.weight,
                np.repeat(b.origin_weights(rows.iloc[pos].session_date_et.to_numpy()) / 20, 20),
                rtol=1e-13,
                atol=1e-15,
            )
            assert not k.duplicated(["origin_id", "ticker"]).any()
    return plans


def phase_view(c: b.Components, rows: pd.DataFrame, r: np.ndarray, year: int, phase: str) -> b.View:
    """Reuse exact saved input-only FT16 recipe; rank scores have no target scale."""
    recipe = b.read(o1.OUT / f"F{year % 100}/{phase}_recipe.json")
    return b.View(c, rows, r, recipe, 1.0)


def prepare() -> None:
    """All-fold mathematical/data/feature gate before any neural or ridge fit."""
    if (OUT / "preflight.json").exists():
        raise ValueError("SINGLE_USE_PREFLIGHT")
    grid, rows = b.metadata()
    plans = validate_roles(grid, rows)
    clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
    c, r = b.source_components(grid, rows)
    records = []
    recipes = []
    for year in b.YEARS:
        for role, pos in plans[year].items():
            a = abs(r[pos])
            y = preferences(a)
            records.append(
                dict(
                    year=year,
                    role=role,
                    origins=len(pos),
                    rows=len(pos) * 20,
                    sessions=int(rows.iloc[pos].session_date_et.nunique()),
                    true_tied_pairs=int((y == 0).sum()),
                    all_tied_origins=0,
                    min_valid_pairs=int((y != 0).sum(1).min()),
                )
            )
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            old = b.read(o1.OUT / f"F{year % 100}/phases.json")
            cutoff = old["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(grid, rows, cutoff), cutoff, approved=True
            )
            ref = o1.OUT / f"F{year % 100}/{phase}_recipe.json"
            assert recipe == b.read(ref)
            v = phase_view(c, rows, r, year, phase)
            for pos in [
                plans[year][role],
                plans[year]["selector" if phase == "initial" else "oos"],
            ]:
                for start in range(0, len(pos), 64):
                    x = v.x(pos[start : start + 64])
                    assert x.shape[1:] == (20, 48, 16) and np.isfinite(x).all()
            recipes.append(
                dict(
                    year=year,
                    phase=phase,
                    cutoff=cutoff,
                    recipe=str(ref),
                    sha256=b.digest(ref),
                    parity=True,
                )
            )
            del v
            gc.collect()
        for arm in ["S5A", "S5B", "LINEAR"]:
            d = OUT / arm / f"F{year % 100}"
            d.mkdir(exist_ok=False)
            b.write(
                d / "phases.json",
                dict(
                    year=year,
                    input_recipes=[x for x in recipes if x["year"] == year],
                    target_scale=None,
                    calibration="UNUSED",
                    threshold_reference=str(o1.OUT / f"F{year % 100}/phases.json"),
                ),
                new=True,
            )
    pd.DataFrame(records).to_csv(OUT / "role_counts.csv", index=False)
    pd.DataFrame(recipes).to_csv(OUT / "phase_recipes.csv", index=False)
    pd.DataFrame(clocks, columns=[f"clock{i}" for i in range(10)]).drop_duplicates().to_csv(
        OUT / "clock_dictionary.csv", index=False
    )
    b.write(
        OUT / "preflight.json",
        dict(
            status="DATA_PASS_ALL_FOUR",
            roles=records,
            recipes=recipes,
            resources=resources(),
            no_minute_source=True,
            calibration_unused=True,
            OOS_rows=80260,
            OOS_origins=4013,
            OOS_sessions=793,
        ),
        new=True,
    )


def label_values(a: np.ndarray, arm: str) -> np.ndarray:
    return targets(a).astype(np.float32) if arm == "S5A" else preferences(a)


def epoch(
    view: b.View,
    pos: np.ndarray,
    model: clock.ClockMAG,
    opt: torch.optim.AdamW,
    number: int,
    clocks: np.ndarray,
    arm: str,
) -> dict:
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    model.train()
    norms = []
    for start in range(0, len(days), 16):
        ix = pos[np.concatenate([groups[d] for d in days[start : start + 16]])]
        opt.zero_grad()
        z = model(
            torch.from_numpy(view.x(ix).reshape(-1, 48, 16)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
        ).reshape(-1, 20)
        lab = torch.from_numpy(label_values(abs(view.r[ix]), arm))
        error = loss(z, lab, view.rows.iloc[ix].session_date_et.to_numpy(), arm)
        if not bool(torch.isfinite(error)):
            raise ValueError("NONFINITE_LOSS")
        error.backward()
        norms.append(
            float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True))
        )
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(x > 1 for x in norms)
    )


def journal(arm: str, year: int, status: str, detail: dict) -> None:
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
        assert starts < 8 and [arm, year] == protocol["order"][starts]
        assert not history or history[-1]["status"] == "COMPLETED"
        assert b.read(OUT / "readiness.json")["status"] == "READY"
        resources()
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        arm=arm,
        year=year,
        status=status,
        global_started_pairs=174 + starts + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
        previous_journal=dict(
            path=protocol["previous_pointer"]["real_journal"],
            sha256=protocol["preservation_bindings"][protocol["previous_pointer"]["real_journal"]],
        ),
        plan=dict(path=str(OUT / "protocol.json"), sha256=b.digest(OUT / "protocol.json")),
    )
    with path.open("a") as s:
        s.write(json.dumps(row) + "\n")
        s.flush()
        os.fsync(s.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=34,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def run_fold(
    arm: str, year: int, c: b.Components, rows: pd.DataFrame, r: np.ndarray, clocks: np.ndarray
) -> None:
    dest = OUT / arm / f"F{year % 100}"
    plans = clock.saved_plans(rows)[year]
    trace = []
    tick = time.monotonic()
    model = clock.model_for_clock()
    initial = b.initial_hash(model)
    opt = b.optimizer(model)
    view = phase_view(c, rows, r, year, "initial")
    selector = b.Selector()
    best = {}
    journal(arm, year, "STARTED", dict(parameters=6443, seed=42))
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            t = time.monotonic()
            stats = epoch(view, plans["inner_train"], model, opt, n, clocks, arm)
            ix = plans["selector"]
            z = clock.predict_clock(view, ix, model, clocks)
            val = float(
                loss(
                    torch.from_numpy(z),
                    torch.from_numpy(label_values(abs(r[ix]), arm)),
                    rows.iloc[ix].session_date_et.to_numpy(),
                    arm,
                )
            )
            ic = float(
                b.origin_weights(rows.iloc[ix].session_date_et.to_numpy())
                @ conservative_ic(abs(r[ix]), z)
            )
            if selector.observe(val):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_surrogate=val,
                    validation_IC_diagnostic=ic,
                    selected=selector.selected,
                    seconds=time.monotonic() - t,
                    **stats,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print(arm, year, "selector", n, val, "best", selector.selected, flush=True)
        model.load_state_dict(best)
        torch.save(model.state_dict(), dest / "selected_initial.pt")
        b.write(dest / "selection.json", vars(selector), new=True)
        journal(arm, year, "SELECTED", dict(epoch=selector.selected))
        del view, model, opt, best
        gc.collect()
        view = phase_view(c, rows, r, year, "restricted")
        model = clock.model_for_clock()
        opt = b.optimizer(model)
        assert b.initial_hash(model) == initial and not opt.state
        journal(arm, year, "REFITTING", dict(epochs=selector.selected))
        for n in range(1, selector.selected + 1):
            t = time.monotonic()
            stats = epoch(view, plans["restricted_refit"], model, opt, n, clocks, arm)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - t, **stats))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print(arm, year, "refit", n, "of", selector.selected, flush=True)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        frozen = b.initial_hash(model)
        z = clock.predict_clock(view, plans["oos"], model, clocks)
        reload = clock.model_for_clock()
        reload.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, clock.predict_clock(view, plans["oos"], reload, clocks))
        assert b.initial_hash(model) == frozen
        f = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(f.A, abs(r[plans["oos"]]).ravel())
        f["score"] = z.ravel()
        f.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
        result = dict(
            year=year,
            arm=arm,
            status="COMPLETED",
            parameters=6443,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_hash=initial,
            frozen_parameter_hash=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            raw_A_MSE=None,
            A_MAE=None,
            calibration=None,
            seconds=time.monotonic() - tick,
            resources=resources(),
        )
        b.write(dest / "result.json", result, new=True)
        journal(arm, year, "COMPLETED", result)
        del view, model, opt, reload
        gc.collect()
    except BaseException as exc:
        journal(arm, year, "FAILED", dict(error=repr(exc), retry=False))
        raise


def linear_x(view: b.View, ix: np.ndarray, clocks: np.ndarray) -> np.ndarray:
    """Exactly same information: intercept, time-major FT16 flatten,10 clocks."""
    return np.column_stack(
        [np.ones(len(ix) * 20), view.x(ix).reshape(-1, 768), np.repeat(clocks[ix], 20, axis=0)]
    ).astype(float)


def moments(view: b.View, ix: np.ndarray, clocks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Streaming weighted sufficient statistics avoid a full 48-hour panel copy."""
    gram = np.zeros((779, 779))
    rhs = np.zeros(779)
    weights = np.repeat(b.origin_weights(view.rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
    for k in range(0, len(ix), 32):
        take = ix[k : k + 32]
        x = linear_x(view, take, clocks)
        w = weights[k * 20 : (k + len(take)) * 20]
        q = targets(abs(view.r[take])).ravel()
        gram += x.T @ (w[:, None] * x)
        rhs += x.T @ (w * q)
        b.memory()
    return gram, rhs


def solve(gram: np.ndarray, rhs: np.ndarray, alpha: float) -> np.ndarray:
    reg = np.eye(len(rhs)) * alpha
    reg[0, 0] = 0
    result = np.linalg.solve(gram + reg, rhs)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_RIDGE")
    return result


def linear_predict(
    view: b.View, ix: np.ndarray, clocks: np.ndarray, beta: np.ndarray
) -> np.ndarray:
    return np.concatenate(
        [linear_x(view, ix[k : k + 32], clocks) @ beta for k in range(0, len(ix), 32)]
    ).reshape(-1, 20)


def run_linear(c: b.Components, rows: pd.DataFrame, r: np.ndarray, clocks: np.ndarray) -> None:
    marker = OUT / "LINEAR/started.json"
    b.write(marker, dict(status="STARTED", neural_starts=0), new=True)
    for year in b.YEARS:
        d = OUT / "LINEAR" / f"F{year % 100}"
        plans = clock.saved_plans(rows)[year]
        view = phase_view(c, rows, r, year, "initial")
        gram, rhs = moments(view, plans["inner_train"], clocks)
        candidates = []
        for alpha in [0.01, 1.0, 100.0]:
            beta = solve(gram, rhs, alpha)
            ix = plans["selector"]
            z = linear_predict(view, ix, clocks, beta)
            error = float(
                b.origin_weights(rows.iloc[ix].session_date_et.to_numpy())
                @ ((z - targets(abs(r[ix]))) ** 2).mean(1)
            )
            candidates.append(dict(alpha=alpha, selector_rank_MSE=error))
        chosen = min(candidates, key=lambda x: (x["selector_rank_MSE"], -x["alpha"]))["alpha"]
        del view
        gc.collect()
        view = phase_view(c, rows, r, year, "restricted")
        gram, rhs = moments(view, plans["restricted_refit"], clocks)
        beta = solve(gram, rhs, chosen)
        np.save(d / "coefficients.npy", beta)
        b.write(
            d / "selection.json",
            dict(
                candidates=candidates,
                chosen_alpha=chosen,
                penalty="weighted MSE plus alpha nonintercept squared norm",
            ),
            new=True,
        )
        ix = plans["oos"]
        z = linear_predict(view, ix, clocks, beta)
        f = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
        f["score"] = z.ravel()
        f.to_parquet(d / "oos_scores.parquet", compression="zstd", index=False)
        b.write(
            d / "result.json",
            dict(status="COMPLETED", alpha=chosen, parameters=779, resources=resources()),
            new=True,
        )
        print("LINEAR", year, "complete alpha", chosen, flush=True)
        del view
        gc.collect()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.prepare:
        prepare()
    elif args.run:
        if (OUT / "neural_starts.jsonl").exists() or (OUT / "LINEAR/started.json").exists():
            raise ValueError("SINGLE_USE_NO_RETRY")
        ready = b.read(OUT / "readiness.json")
        assert ready["status"] == "READY"
        for f, h in ready["hashes"].items():
            assert b.digest(Path(f)) == h, f
        grid, rows = b.metadata()
        validate_roles(grid, rows)
        c, r = b.source_components(grid, rows)
        clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
        run_linear(c, rows, r, clocks)
        for arm in ["S5A", "S5B"]:
            for year in b.YEARS:
                run_fold(arm, year, c, rows, r, clocks)
    elif args.report:
        from .hf20_mag_rank_report import report

        report()


if __name__ == "__main__":
    main()
