"""One fixed Stage3 minute-summary family; separate C source/normalizer gate."""

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
from torch import nn

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_minute_inputs as source
from . import hf20_overnight_specialist as previous
from . import hf20_stage2_bcd as clock
from .hf1m_ft16_fit import robust
from .hf20_s4_clock import sessions
from .neural_engine import seed_all

OUT = source.OUT
DEST = OUT / "S3B"
RAW, CAL = "S3B-RAW", "S3B-C3"


class MinuteSummaryMAG(clock.ClockMAG):
    """Original clock readout with exactly seven extra hourly scalar inputs."""

    def __init__(self) -> None:
        nn.Module.__init__(self)
        self.input_dim = 23
        self.lstm = nn.LSTM(23, 32, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.10)
        self.head = nn.Linear(42, 1)


def model_for_summary() -> MinuteSummaryMAG:
    seed_all(42)
    model = MinuteSummaryMAG().float()
    assert sum(p.numel() for p in model.parameters()) == 7339
    return model


def normalized_features(primitives: np.ndarray, floors: np.ndarray, scaler: dict) -> np.ndarray:
    """A missing native MIN01 receives prefix median, hence normalized zero."""
    if floors.shape != (20,) or not np.isfinite(floors).all() or (floors <= 0).any():
        raise ValueError("POSITIVE_PHASE_HOURLY_FLOORS_REQUIRED")
    x = primitives.copy()
    valid = x[:, :, 5].astype(bool)
    x[:, :, 0] = np.log1p(x[:, :, 0] / floors[None, :] ** 2)
    x[:, :, 0] = np.where(valid, (x[:, :, 0] - scaler["center"]) / scaler["scale"], 0)
    x[:, :, 1:4] = np.where(valid[:, :, None], x[:, :, 1:4], 0)
    x[:, :, 4] = np.where(x[:, :, 6].astype(bool), x[:, :, 4], 0.25)
    assert np.isfinite(x).all() and (x[:, :, 6] <= x[:, :, 5]).all()
    return x.astype(np.float32)


class SummaryView(b.View):
    """All original FT16 entries retained; add same-hour frozen derived scalars."""

    def __init__(
        self,
        c: b.Components,
        rows: pd.DataFrame,
        returns: np.ndarray,
        phase: dict,
        primitives: np.ndarray,
    ):
        recipe = b.read(Path(phase["recipe_reference"]))
        super().__init__(c, rows, returns, recipe, phase["scale"])
        floors = np.asarray([x["hourly_floor"] for x in recipe["floors"]])
        self.extra = normalized_features(primitives, floors, phase["MIN01_scaler"])

    def x(self, pos: np.ndarray) -> np.ndarray:
        original = super().x(pos)
        ix = self.rows.iloc[pos].first_step.to_numpy(int)[:, None] + np.arange(48)
        extra = self.extra[ix].transpose(0, 2, 1, 3)
        result = np.concatenate([original, extra], axis=-1)
        assert result.shape[1:] == (20, 48, 23)
        return result


def resources() -> dict:
    """Filesystem block accounting only; no source values/holdout hashes."""
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    result = dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())
    if project + 50_000_000 > 15_000_000_000 or task + 50_000_000 > 2_500_000_000:
        raise ValueError("RESOURCE_CEILING", result)
    return result


def prepare(
    c: b.Components, rows: pd.DataFrame, returns: np.ndarray, primitives: np.ndarray
) -> dict[int, dict]:
    """All eight lawful prefix normalizers and unchanged source/target recipes."""
    plans = clock.saved_plans(rows)
    allphases = {}
    for year in b.YEARS:
        dest = DEST / f"F{year % 100}"
        dest.mkdir(exist_ok=False)
        old = b.read(source.O1 / f"F{year % 100}/phases.json")
        phases = {}
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            cutoff = old["phases"][phase]["cutoff"]
            fit = b.feature_fit_hours(c.grid, rows, cutoff)
            recipe, _ = b.fit_expanded(c, fit, cutoff, approved=True)
            ref = source.O1 / f"F{year % 100}/{phase}_recipe.json"
            assert recipe == b.read(ref)
            ix = plans[year][role]
            w = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(returns[ix]).ravel(), 0.5, w), 1e-8)
            assert scale == old["phases"][phase]["scale"]
            floors = np.asarray([v["hourly_floor"] for v in recipe["floors"]])
            native = np.log1p(primitives[:, :, 0] / floors[None, :] ** 2)
            valid = fit[:, None] & primitives[:, :, 5].astype(bool)
            if not valid.any():
                raise ValueError("NO_LEGAL_MIN01_POPULATION", year, phase)
            scaler = robust(native[valid])
            x = normalized_features(primitives, floors, scaler)
            assert np.isfinite(x).all()
            phases[phase] = dict(
                cutoff=cutoff,
                scale=scale,
                recipe_reference=str(ref),
                original_recipe_sha256=b.digest(ref),
                MIN01_scaler=scaler,
                fit_unique_hour_keys=int(fit.sum()),
                valid_MIN01_stock_hours=int(valid.sum()),
                MIN01_native_min=float(native[valid].min()),
                MIN01_native_max=float(native[valid].max()),
                MIN06_equals_MIN07=bool(np.array_equal(x[:, :, 5], x[:, :, 6])),
                constant_new_channels=[i + 1 for i in range(7) if np.ptp(x[fit, :, i]) == 0],
            )
        result = dict(year=year, phases=phases, thresholds=old["thresholds"])
        source.write(dest / "phases.json", result)
        allphases[year] = result
    source.write(
        DEST / "phase_readiness.json", dict(status="ALL_FOUR_PHASES_READY", folds=allphases)
    )
    return allphases


def validate_roles(grid: pd.DataFrame, rows: pd.DataFrame) -> None:
    plans = clock.saved_plans(rows)
    counts = pd.read_csv(c3.CONT / "role_counts.csv")
    first = np.full(len(rows), "0000", object)
    good = rows.first_step.ge(0)
    first[good] = grid.session_date_et.to_numpy()[rows.loc[good, "first_step"].to_numpy(int)]
    total = 0
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
            if role == "selector":
                g = rows.iloc[pos]
                assert (
                    g.session_date_et.nunique() >= 50
                    and g.groupby("slot").size().reindex(b.SLOTS, fill_value=0).min() >= 25
                )
        pos = plans[year]["oos"]
        for ref in [c3.root(year), clock.OUT / f"s2b_clock/F{year % 100}"]:
            keys = pd.read_parquet(
                ref / "oos_scores.parquet", columns=["origin_id", "ticker", "weight"]
            )
            assert keys.ticker.tolist() == list(b.SYMBOLS) * len(pos)
            np.testing.assert_array_equal(keys.origin_id, np.repeat(rows.iloc[pos].origin_id, 20))
            np.testing.assert_allclose(
                keys.weight,
                np.repeat(b.origin_weights(rows.iloc[pos].session_date_et.to_numpy()) / 20, 20),
                atol=1e-15,
                rtol=1e-13,
            )
            assert not keys.duplicated(["origin_id", "ticker"]).any()
        total += len(pos)
    assert total == 4013


def complete_normalizers() -> None:
    """Complete legal input-only prefix coverage before the first neural start.

    The first source union covered every supervised role but omitted80 input-only
    fitting hours. Preserve those preliminary records and append corrected ones;
    no model, calibration or OOS score was computed using the preliminary records.
    """
    grid, rows, _ = source.metadata()
    packed = np.load(OUT / "minute_summary_primitives_v2.npz")
    primitives = packed["features"]
    covered = np.zeros(len(grid), bool)
    covered[packed["required_hours"]] = True
    folds = {}
    for year in b.YEARS:
        dest = DEST / f"F{year % 100}"
        original = b.read(dest / "phases.json")
        corrected = json.loads(json.dumps(original))
        for phase, old in original["phases"].items():
            fit = b.feature_fit_hours(grid, rows, old["cutoff"])
            assert not (fit & ~covered).any()
            recipe = b.read(Path(old["recipe_reference"]))
            assert b.digest(Path(old["recipe_reference"])) == old["original_recipe_sha256"]
            floors = np.asarray([v["hourly_floor"] for v in recipe["floors"]])
            native = np.log1p(primitives[:, :, 0] / floors[None, :] ** 2)
            valid = fit[:, None] & primitives[:, :, 5].astype(bool)
            scaler = robust(native[valid])
            x = normalized_features(primitives, floors, scaler)
            corrected["phases"][phase].update(
                MIN01_scaler=scaler,
                valid_MIN01_stock_hours=int(valid.sum()),
                MIN01_native_min=float(native[valid].min()),
                MIN01_native_max=float(native[valid].max()),
                constant_new_channels=[i + 1 for i in range(7) if np.ptp(x[fit, :, i]) == 0],
            )
        corrected["materialization"] = (
            "complete original input-only prefix union; source_normalizer_supplement.json"
        )
        source.write(dest / "phases_v2.json", corrected)
        folds[year] = corrected
    source.write(
        DEST / "phase_readiness_v2.json",
        dict(
            status="ALL_FOUR_PHASES_READY_COMPLETE_INPUT_PREFIX",
            folds=folds,
            preliminary_phases_not_used_for_models=True,
        ),
    )


def predict(
    view: SummaryView, pos: np.ndarray, model: MinuteSummaryMAG, clocks: np.ndarray
) -> np.ndarray:
    model.eval()
    parts = []
    with torch.inference_mode():
        for start in range(0, len(pos), 32):
            ix = pos[start : start + 32]
            x = torch.from_numpy(view.x(ix).reshape(-1, 48, 23))
            known = torch.from_numpy(np.repeat(clocks[ix], 20, axis=0))
            parts.append(model(x, known).numpy().reshape(-1, 20))
    result = np.concatenate(parts)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_FORECAST")
    return result


def train_epoch(
    view: SummaryView,
    pos: np.ndarray,
    model: MinuteSummaryMAG,
    opt: torch.optim.AdamW,
    epoch: int,
    clocks: np.ndarray,
) -> dict:
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + epoch).shuffle(days)
    model.train()
    norms = []
    for start in range(0, len(days), 16):
        ix = pos[np.concatenate([groups[d] for d in days[start : start + 16]])]
        opt.zero_grad()
        z = model(
            torch.from_numpy(view.x(ix).reshape(-1, 48, 23)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
        ).reshape(-1, 20)
        loss = previous.weighted_loss(
            z,
            torch.from_numpy(view.r[ix].astype(np.float32)),
            view.scale,
            b.origin_weights(view.rows.iloc[ix].session_date_et.to_numpy()),
        )
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_LOSS")
        loss.backward()
        norms.append(
            float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True))
        )
        b.memory()
        opt.step()
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(x > 1 for x in norms)
    )


def journal(year: int, status: str, detail: dict) -> None:
    protocol = b.read(OUT / "frozen_protocol.json")
    path = OUT / "neural_starts.jsonl"
    history = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    starts = [v for v in history if v["status"] == "STARTED"]
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["previous_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert b.read(DEST / "readiness.json")["status"] == "READY_ALL_FOUR"
        assert len(starts) < 4 and year == b.YEARS[len(starts)]
        assert not history or history[-1]["status"] == "COMPLETED"
        resources()
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        experiment="S3-B",
        year=year,
        status=status,
        global_started_pairs=166 + len(starts) + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
        previous_journal=dict(
            path=protocol["previous_pointer"]["real_journal"],
            sha256=protocol["preservation_bindings"][protocol["previous_pointer"]["real_journal"]],
        ),
        plan=dict(
            path=str(OUT / "frozen_protocol.json"), sha256=b.digest(OUT / "frozen_protocol.json")
        ),
    )
    with path.open("a") as stream:
        stream.write(json.dumps(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=32,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def run_fold(
    year: int,
    c: b.Components,
    rows: pd.DataFrame,
    returns: np.ndarray,
    primitives: np.ndarray,
    phases: dict,
    clocks: np.ndarray,
) -> None:
    dest = DEST / f"F{year % 100}"
    plans = clock.saved_plans(rows)[year]
    trace = []
    tick = time.monotonic()
    model = model_for_summary()
    initial_hash = b.initial_hash(model)
    opt = b.optimizer(model)
    assert not opt.state
    inner = SummaryView(c, rows, returns, phases["phases"]["initial"], primitives)
    selector = b.Selector()
    best = {}
    journal(year, "STARTED", dict(run_id=f"HF20-S3B-F{year % 100}-S42", parameters=7339))
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            started = time.monotonic()
            stats = train_epoch(inner, plans["inner_train"], model, opt, n, clocks)
            z = predict(inner, plans["selector"], model, clocks)
            target = torch.log1p(
                torch.from_numpy(returns[plans["selector"]].astype(np.float32)).abs() / inner.scale
            ).numpy()
            val = float(
                b.origin_weights(rows.iloc[plans["selector"]].session_date_et.to_numpy())
                @ ((z - target) ** 2).mean(1)
            )
            if selector.observe(val):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_M_MSE=val,
                    selected=selector.selected,
                    seconds=time.monotonic() - started,
                    **stats,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S3B", year, "selector", n, val, "best", selector.selected, flush=True)
        model.load_state_dict(best)
        torch.save(model.state_dict(), dest / "selected_initial.pt")
        source.write(
            dest / "selection.json",
            dict(vars(selector), selected_initial_hash=b.initial_hash(model)),
        )
        journal(year, "SELECTED", dict(epoch=selector.selected))
        del inner, model, opt, best
        gc.collect()
        refit = SummaryView(c, rows, returns, phases["phases"]["restricted"], primitives)
        model = model_for_summary()
        assert b.initial_hash(model) == initial_hash
        opt = b.optimizer(model)
        assert not opt.state
        journal(year, "REFITTING", dict(epochs=selector.selected))
        for n in range(1, selector.selected + 1):
            started = time.monotonic()
            stats = train_epoch(refit, plans["restricted_refit"], model, opt, n, clocks)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - started, **stats))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S3B", year, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        zcal = predict(refit, plans["calibration"], model, clocks)
        cal = pd.read_parquet(c3.root(year) / "calibration_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(cal.A, abs(returns[plans["calibration"]]).ravel())
        cal["Mhat"] = zcal.ravel()
        coeffs = c3.fit_categories(cal, refit.scale)
        pd.DataFrame(coeffs).to_csv(dest / "calibration_coefficients.csv", index=False, mode="x")
        cal.to_parquet(dest / "calibration_scores.parquet", compression="zstd", index=False)
        factors = {v["group"]: v["c_star"] for v in coeffs}
        z = predict(refit, plans["oos"], model, clocks)
        reload = model_for_summary()
        reload.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, predict(refit, plans["oos"], reload, clocks))
        assert frozen == b.initial_hash(model)
        frame = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(frame.A, abs(returns[plans["oos"]]).ravel())
        frame["Mhat"] = z.ravel()
        frame[RAW] = previous.raw_decode(z, refit.scale).ravel()
        frame[CAL] = c3.decode(z.ravel(), refit.scale, frame.category.map(factors).to_numpy())
        frame.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
        result = dict(
            year=year,
            status="COMPLETED",
            parameters=7339,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_hash=initial_hash,
            frozen_parameter_hash=frozen,
            reload_max_error=0,
            initial_scale=phases["phases"]["initial"]["scale"],
            scale=refit.scale,
            optimizer_fresh=True,
            seconds=time.monotonic() - tick,
            resources=resources(),
        )
        source.write(dest / "result.json", result)
        journal(year, "COMPLETED", result)
        del refit, model, opt, reload
        gc.collect()
    except BaseException as exc:
        journal(year, "FAILED", dict(error=repr(exc), retry=False))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--normalizers", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.normalizers:
        complete_normalizers()
        return
    assert (
        b.read(OUT / "source_certification.json")["status"]
        == "SOURCE_CERTIFIED_HISTORICAL_TIMING_PROXY"
    )
    grid, rows = b.metadata()
    validate_roles(grid, rows)
    if args.run and (OUT / "neural_starts.jsonl").exists():
        raise SystemExit("NO_RETRY_STARTED_NAMESPACE")
    packed = np.load(OUT / "minute_summary_primitives_v2.npz")
    primitives = packed["features"]
    c, returns = b.source_components(grid, rows)
    if args.prepare:
        prepare(c, rows, returns, primitives)
        return
    if args.run:
        assert b.read(DEST / "readiness.json")["status"] == "READY_ALL_FOUR"
        clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
        for year in b.YEARS:
            phases = b.read(DEST / f"F{year % 100}/phases_v2.json")
            run_fold(year, c, rows, returns, primitives, phases, clocks)


if __name__ == "__main__":
    main()
