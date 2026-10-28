"""One authorized O1 family: raw expected magnitude, fixed Design A history.

No predecessor fitting, calibration, extra information, or protected years.
Run once; --report replays only saved forecasts and frozen comparators.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn import functional as F

from . import hf20_mag_designa as b
from . import hf20_mag_designa_continue as previous
from .hf20_s5s9_metrics import auc, average_precision

OUT = Path("reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28")
REF = previous.OUT
ARMS = ("O1", *b.ARMS)


def positive(z: torch.Tensor, scale: float) -> torch.Tensor:
    """Stable, parameter-free nonnegative link in original log-return units."""
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("POSITIVE_FINITE_PREFIX_SCALE_REQUIRED")
    return scale * F.softplus(z)


def stock_loss(z: torch.Tensor, returns: torch.Tensor, scale: float) -> torch.Tensor:
    """Declared scaled raw MSE, without a signed target or transformed inverse."""
    return ((positive(z, scale) - returns.abs()) / scale).square()


def weighted_loss(
    z: torch.Tensor, returns: torch.Tensor, scale: float, days: np.ndarray
) -> torch.Tensor:
    """Equal stocks/origin, origins/session and sessions, including short batches."""
    assert z.shape == returns.shape and z.ndim == 2 and z.shape[1] == 20
    w = torch.from_numpy(b.origin_weights(days)).to(dtype=z.dtype, device=z.device)
    return (stock_loss(z, returns, scale).mean(1) * w).sum()


def decoded(z: np.ndarray, scale: float) -> np.ndarray:
    value = positive(torch.from_numpy(z), scale).numpy()
    if not np.isfinite(value).all() or (value < 0).any():
        raise ValueError("INVALID_O1_FORECAST")
    return value


def reference_root(year: int) -> Path:
    return previous.fold_root(REF, year)


def initial_recipe_path(year: int) -> Path:
    return (
        b.S4 / "F21_inner_recipe.json"
        if year == 2021
        else reference_root(year) / "initial_recipe.json"
    )


def preflight(out: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[int, dict], dict]:
    """Reuse frozen source eligibility and exact executed role derivation, not dates alone."""
    prior_receipt = b.read(REF / "execution_receipt.json")
    assert prior_receipt["status"] == "COMPLETE" and prior_receipt["ledger_after"] == 134
    for name, expected in prior_receipt["code_sha256"].items():
        assert b.digest(Path(name)) == expected, f"PREDECESSOR_CODE_CHANGED:{name}"
    previous.preserved_parent(REF)
    pointer = b.read(b.POINTER)
    history = Path(pointer["real_journal"])
    assert history == REF / "neural_starts.jsonl"
    last = json.loads(history.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 134
    assert pointer["effective_ceiling"] == 200 and 134 + 4 <= 200
    assert b.digest(Path(pointer["plan"]["path"])) == pointer["plan"]["sha256"]
    assert (
        b.digest(Path(pointer["previous_journal"]["path"])) == pointer["previous_journal"]["sha256"]
    )
    grid, rows = b.metadata()
    first = np.full(len(rows), "0000", dtype=object)
    valid = rows.first_step.ge(0)
    first[valid] = grid.session_date_et.to_numpy()[rows.loc[valid, "first_step"].to_numpy(int)]
    target = pd.read_parquet(
        b.S4 / "opening_reaudit_v2/S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet",
        columns=["origin_id", "ticker", "direct_return"],
    )
    np.testing.assert_array_equal(target.origin_id.iloc[::20], rows.origin_id)
    assert target.ticker.tolist() == list(b.SYMBOLS) * len(rows)
    r = target.direct_return.to_numpy().reshape(-1, 20)
    counts = pd.read_csv(REF / "role_counts.csv")
    old_metrics = pd.read_csv(REF / "fourfold_metrics.csv", dtype={"year": str})
    plans: dict[int, dict] = {}
    folds = []
    bindings = {str(history): b.digest(history)}
    for year in b.YEARS:
        plans[year] = {}
        for record in counts.loc[counts.year.eq(year)].to_dict("records"):
            role = str(record["role"])
            mask = b.role_mask(
                rows,
                first,
                str(record["start"]),
                str(record["cutoff"]),
                str(record["embargo_after"]),
            )
            ix = np.flatnonzero(mask)
            g = rows.iloc[ix]
            assert len(ix) == record["origins"] and len(ix) * 20 == record["stock_rows"]
            assert g.session_date_et.nunique() == record["sessions"]
            assert g.session_date_et.min() == record["first_date"]
            assert g.session_date_et.max() == record["last_date"]
            assert g.entry_index.sub(g.first_step).eq(47).all()
            assert g.trading_minutes.eq(240).all() and np.isfinite(r[ix]).all()
            assert g.label_maturity_utc.lt(b.limit(str(record["cutoff"]))).all()
            assert (first[ix] > str(record["embargo_after"])).all()
            slots = g.groupby("slot").size().reindex(b.SLOTS, fill_value=0)
            assert slots.tolist() == [record[s] for s in b.SLOTS]
            if role == "selector":
                assert record["sessions"] >= 50 and slots.min() >= 25
            plans[year][role] = ix
        p = plans[year]
        for left, right in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("selector", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(p[left], p[right]).size
        assert np.isin(p["selector"], p["restricted_refit"]).all()
        source = reference_root(year)
        for role in ("calibration", "oos"):
            saved = pd.read_parquet(
                source / f"{role}_scores.parquet", columns=["origin_id", "ticker", "weight"]
            )
            np.testing.assert_array_equal(saved.origin_id.iloc[::20], rows.iloc[p[role]].origin_id)
            assert saved.ticker.tolist() == list(b.SYMBOLS) * len(p[role])
            np.testing.assert_allclose(
                saved.weight,
                np.repeat(b.origin_weights(rows.iloc[p[role]].session_date_et.to_numpy()) / 20, 20),
                atol=1e-15,
                rtol=1e-13,
            )
        scores = pd.read_parquet(source / "oos_scores.parquet")
        original = pd.read_parquet(
            b.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "weight", "return_4h"],
        )
        np.testing.assert_array_equal(
            scores[["origin_id", "ticker"]], original[["origin_id", "ticker"]]
        )
        np.testing.assert_array_equal(scores.A, abs(original.return_4h))
        assert not scores.duplicated(["origin_id", "ticker"]).any()
        np.testing.assert_allclose(scores.weight, original.weight, atol=1e-15, rtol=1e-13)
        for arm in b.ARMS:
            value = {**b.metrics(scores, arm), **b.rank_metrics(scores, arm)}
            archived = old_metrics.loc[
                old_metrics.year.eq(str(year)) & old_metrics.arm.eq(arm)
            ].iloc[0]
            for metric in value:
                np.testing.assert_allclose(value[metric], archived[metric], atol=1e-14, rtol=1e-13)
        scales = {}
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            ix = p[role]
            w = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(r[ix]).ravel(), 0.5, w), 1e-8)
            recipe = b.read(
                initial_recipe_path(year)
                if phase == "initial"
                else source / "restricted_recipe.json"
            )
            expected = (
                b.read(source / "selection.json")["inner_scale"]
                if phase == "initial"
                else b.read(source / "restricted_target.json")["scale"]
            )
            assert scale == expected
            cutoff = str(counts.loc[counts.year.eq(year) & counts.role.eq(role), "cutoff"].iloc[0])
            assert recipe["fit_stop_inclusive"] == cutoff
            np.testing.assert_array_equal(
                recipe["fit_hour_indices"], np.flatnonzero(b.feature_fit_hours(grid, rows, cutoff))
            )
            scales[phase] = dict(scale=scale, cutoff=cutoff)
        thresholds = b.read(source / "restricted_target.json")["thresholds"]
        folds.append(
            dict(
                year=year,
                status="READY",
                phases=scales,
                thresholds=thresholds,
                comparator_root=str(source),
            )
        )
        bindings[str(source / "oos_scores.parquet")] = b.digest(source / "oos_scores.parquet")
    source_files = pd.read_csv(b.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv")
    source_files = source_files.loc[source_files.purpose.eq("permitted adjusted hourly source")]
    assert len(source_files) == 174
    for item in source_files.to_dict("records"):
        path = Path(str(item["path"]))
        assert "2010-07" <= path.stem <= "2024-12" and not path.is_absolute()
        assert path.is_file() and path.stat().st_size == item["bytes"]
    traces = pd.concat([pd.read_csv(reference_root(y) / "training.csv") for y in b.YEARS])
    resources = b.resources(out)
    protocol = dict(
        kind="HF20_STAGE1_SESSION3_O1_SEED42_V1",
        folds=folds,
        information="original own-stock48x16 FT16; H32,one layer,final dropout0.1;6433 parameters",
        objective="mean_session mean_origin mean20 ((s*torch.softplus(z)-abs(R))/s)^2",
        decoder="s*torch.softplus(z); no calibration, inverse transform, output cap or target trim",
        optimizer="AdamW lr.001,beta(.9,.999),eps1e-8,matrix decay.01,bias0,clip1,batch16sessions",
        selector=(
            "O1 scaled raw MSE; first finite nonnegative; <=.999*qualified "
            "best; min12,patience10,max60"
        ),
        seed=42,
        threads=[4, 1],
        dtype="CPU float32",
        fresh_refit=True,
        calibration_tail=(
            "reserved and excluded from all O1 fitting and selection; no inference needed"
        ),
        weights="equal stocks/origin,origins/session,sessions/year,then equal four years",
        primary_comparators=list(b.ARMS),
        bootstrap=dict(draws=400, seed=22042, kind="existing whole months within year"),
        event_definition="A>restricted September weighted prefix95/99; strict exceedance",
        event_prior="UNAVAILABLE: archived EVENT uses |TG20|, not these raw-A labels",
        authority=(
            "Session3 explicit raw-MSE/softplus protocol overrides older "
            "rank-primary/full-December prose"
        ),
        ledger_before=134,
        maximum_new_pairs=4,
        maximum_neural_phase_fits=8,
        maximum_after=138,
        caps=b.CAPS,
        resources=resources,
        source_partitions=174,
        source_end="2024-12-31",
        workload=dict(
            maximum_epochs=480,
            reference_epoch_seconds_p95=float(traces.seconds.quantile(0.95)),
            rough_max_seconds=float(traces.seconds.quantile(0.95)) * 480,
            artifact_reserve_bytes=30_000_000,
        ),
        prior_pointer=pointer,
        preservation_bindings=bindings,
        source_code={name: b.digest(Path(name)) for name in prior_receipt["code_sha256"]},
        git_start="5f7bb86a35d5aaff34ff79ef8f471117de6d3e42",
    )
    out.mkdir(exist_ok=True)
    path = out / "protocol.json"
    if path.exists():
        old = b.read(path)
        assert old["folds"] == folds and old["preservation_bindings"] == bindings
    else:
        b.write(path, protocol, new=True)
    counts.to_csv(out / "role_counts.csv", index=False)
    np.savez_compressed(
        out / "role_indices.npz",
        **{f"F{y % 100}_{role}": ix for y, p in plans.items() for role, ix in p.items()},
    )
    return grid, rows, plans, protocol


def journal(out: Path, year: int, status: str, detail: dict) -> None:
    """One append-only successor for four pairs; no retry or predecessor rewrite."""
    protocol = b.read(out / "protocol.json")
    path = out / "neural_starts.jsonl"
    history = [json.loads(v) for v in path.read_text().splitlines()] if path.exists() else []
    started = [v["year"] for v in history if v["status"] == "STARTED"]
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["prior_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert len(started) < 4 and year == b.YEARS[len(started)]
        assert not history or history[-1]["status"] == "COMPLETED"
        b.resources(out)
    else:
        assert history and history[-1]["year"] == year
    count = 134 + len(started) + int(status == "STARTED")
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        year=year,
        status=status,
        global_started_pairs=count,
        effective_ceiling=200,
        detail=detail,
        previous_journal=dict(
            path=protocol["prior_pointer"]["real_journal"],
            sha256=b.digest(Path(protocol["prior_pointer"]["real_journal"])),
        ),
        plan=dict(path=str(out / "protocol.json"), sha256=b.digest(out / "protocol.json")),
    )
    with path.open("a") as stream:
        stream.write(json.dumps(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=26,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def train_epoch(
    view: b.View, pos: np.ndarray, model: b.SharedLSTM, opt: torch.optim.AdamW, number: int
) -> dict:
    """Historical session shuffle/batching/optimizer, with exactly the O1 loss."""
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    model.train()
    norms = []
    for k in range(0, len(days), 16):
        selected = pos[np.concatenate([groups[d] for d in days[k : k + 16]])]
        x = view.x(selected)
        opt.zero_grad()
        z = model(torch.from_numpy(x.reshape(-1, 48, 16))).reshape(-1, 20)
        r = torch.from_numpy(view.r[selected].astype(np.float32))
        loss = weighted_loss(z, r, view.scale, view.rows.iloc[selected].session_date_et.to_numpy())
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_O1_LOSS")
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        norms.append(float(norm))
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(v > 1 for v in norms)
    )


def check_recipe(recipe: dict, original: dict, *, s4_metadata: bool) -> list[str]:
    """Exact FT16 parity; original F21 also carries five unrelated S4 target fields."""
    assert all(k in original and recipe[k] == original[k] for k in recipe), "FT16_FIELD_MISMATCH"
    extra = set(original) - set(recipe)
    permitted = (
        {"epsilon", "t2_scale", "s4_contexts", "task", "target_minutes"} if s4_metadata else set()
    )
    assert extra == permitted, "UNEXPECTED_RECIPE_SCHEMA"
    return sorted(extra)


def prepare_recipes(out: Path, c: b.Components, rows: pd.DataFrame, protocol: dict) -> None:
    """Recompute the eight legal prefix recipes and require exact predecessor parity."""
    parity = []
    for fold in protocol["folds"]:
        year = fold["year"]
        dest = out / f"F{year % 100}"
        dest.mkdir(exist_ok=True)
        for phase in ("initial", "restricted"):
            cutoff = fold["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(c.grid, rows, cutoff), cutoff, approved=True
            )
            original = b.read(
                initial_recipe_path(year)
                if phase == "initial"
                else reference_root(year) / "restricted_recipe.json"
            )
            extra = check_recipe(recipe, original, s4_metadata=year == 2021 and phase == "initial")
            parity.append(
                dict(
                    year=year,
                    phase=phase,
                    all_FT16_fields_exact=True,
                    source_only_S4_target_metadata=extra,
                )
            )
            path = dest / f"{phase}_recipe.json"
            if path.exists():
                assert b.read(path) == recipe
            else:
                b.write(path, recipe, new=True)
        if (dest / "phases.json").exists():
            assert b.read(dest / "phases.json") == fold
        else:
            b.write(dest / "phases.json", fold, new=True)
    b.write(out / "phase_parity.json", dict(status="PASS_ALL_EIGHT", checks=parity), new=True)


def run_fold(
    out: Path, year: int, c: b.Components, rows: pd.DataFrame, r: np.ndarray, pos: dict, fold: dict
) -> None:
    dest = out / f"F{year % 100}"
    started = time.monotonic()
    initial_scale = fold["phases"]["initial"]["scale"]
    inner = b.View(c, rows, r, b.read(dest / "initial_recipe.json"), initial_scale)
    model = b.model_for("MAG")
    assert sum(p.numel() for p in model.parameters()) == 6433
    initial = b.initial_hash(model)
    assert (
        initial
        == b.read(b.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/configuration.json")["initial_sha256"]
    )
    opt = b.optimizer(model)
    assert not opt.state
    selector = b.Selector()
    traces = []
    journal(
        out, year, "STARTED", dict(run_id=f"HF20-O1-F{year % 100}-DESIGNA-S42", phase="selection")
    )
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            tick = time.monotonic()
            train = train_epoch(inner, pos["inner_train"], model, opt, n)
            z = b.predict(inner, pos["selector"], model)
            validation = stock_loss(
                torch.from_numpy(z),
                torch.from_numpy(r[pos["selector"]].astype(np.float32)),
                initial_scale,
            ).numpy()
            val = float(
                b.origin_weights(rows.iloc[pos["selector"]].session_date_et.to_numpy())
                @ validation.mean(1)
            )
            if selector.observe(val):
                torch.save(model.state_dict(), dest / "selected_initial.pt")
            traces.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_scaled_raw_MSE=val,
                    selected=selector.selected,
                    seconds=time.monotonic() - tick,
                    **train,
                )
            )
            pd.DataFrame(traces).to_csv(dest / "training.csv", index=False)
            print(
                year,
                "selector",
                n,
                "scaled_raw_MSE",
                val,
                "selected",
                selector.selected,
                flush=True,
            )
        b.write(
            dest / "selection.json", dict(vars(selector), initial_scale=initial_scale), new=True
        )
        journal(
            out,
            year,
            "SELECTED",
            dict(selected_epoch=selector.selected, raw_epoch=selector.raw_epoch),
        )
        scale = fold["phases"]["restricted"]["scale"]
        refit = b.View(c, rows, r, b.read(dest / "restricted_recipe.json"), scale)
        model = b.model_for("MAG")
        assert b.initial_hash(model) == initial
        opt = b.optimizer(model)
        assert not opt.state
        journal(
            out,
            year,
            "REFITTING",
            dict(epochs=selector.selected, cutoff=fold["phases"]["restricted"]["cutoff"]),
        )
        for n in range(1, selector.selected + 1):
            tick = time.monotonic()
            train = train_epoch(refit, pos["restricted_refit"], model, opt, n)
            traces.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - tick, **train))
            pd.DataFrame(traces).to_csv(dest / "training.csv", index=False)
            print(year, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        z = b.predict(refit, pos["oos"], model)
        prediction = decoded(z, scale)
        reloaded = b.model_for("MAG")
        reloaded.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, b.predict(refit, pos["oos"], reloaded))
        assert b.initial_hash(model) == frozen
        admitted = rows.iloc[pos["oos"]]
        frame = (
            admitted[
                [
                    "origin_id",
                    "session_date_et",
                    "slot",
                    "category",
                    "entry_end_utc",
                    "exit_end_utc",
                    "label_maturity_utc",
                ]
            ]
            .loc[admitted.index.repeat(20)]
            .reset_index(drop=True)
        )
        frame["ticker"] = np.tile(b.SYMBOLS, len(admitted))
        frame["A"], frame["z"], frame["O1"] = (
            abs(r[pos["oos"]]).ravel(),
            z.ravel(),
            prediction.ravel(),
        )
        frame["weight"] = np.repeat(b.origin_weights(admitted.session_date_et.to_numpy()) / 20, 20)
        reference = pd.read_parquet(
            reference_root(year) / "oos_scores.parquet",
            columns=["origin_id", "ticker", "A", "weight"],
        )
        pd.testing.assert_frame_equal(frame[reference.columns], reference, check_dtype=False)
        frame.to_parquet(dest / "oos_scores.parquet", index=False, compression="zstd")
        result = dict(
            year=year,
            status="COMPLETED",
            run_id=f"HF20-O1-F{year % 100}-DESIGNA-S42",
            selector_epochs=selector.epoch,
            selected_epoch=selector.selected,
            raw_minimum_epoch=selector.raw_epoch,
            initial_scale=initial_scale,
            scale=scale,
            parameters=6433,
            initial_sha256=initial,
            frozen_parameter_sha256=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            prediction_zero_rows=int((prediction == 0).sum()),
            prediction_min=float(prediction.min()),
            prediction_max=float(prediction.max()),
            seconds=time.monotonic() - started,
            peak_rss_bytes=b.memory(),
        )
        b.write(dest / "result.json", result, new=True)
        journal(out, year, "COMPLETED", result)
        del inner, refit, model, opt, reloaded
        gc.collect()
    except (Exception, KeyboardInterrupt) as error:
        journal(out, year, "FAILED", dict(error=repr(error)))
        b.write(dest / "failure.json", dict(error=repr(error), seconds=time.monotonic() - started))
        raise


def top_membership(score: np.ndarray) -> np.ndarray:
    """Exactly the predecessor's fractional top-four membership at tied boundaries."""
    frame = pd.DataFrame(score.reshape(-1, 20))
    first = frame.rank(axis=1, method="min", ascending=False).to_numpy()
    last = frame.rank(axis=1, method="max", ascending=False).to_numpy()
    return np.clip((5 - first) / (last - first + 1), 0, 1).ravel()


def paired_daily(frame: pd.DataFrame, reference: str) -> pd.Series:
    value = pd.DataFrame(
        dict(
            day=frame.session_date_et,
            w=frame.weight,
            d=frame.weight * ((frame.O1 - frame.A) ** 2 - (frame[reference] - frame.A) ** 2),
        )
    )
    summed = value.groupby("day").sum()
    return summed.d / summed.w


def report(out: Path) -> None:
    """Pure saved-score reductions; no model inference, fitting or calibration."""
    protocol = b.read(out / "protocol.json")
    for name, expected in protocol["preservation_bindings"].items():
        assert b.digest(Path(name)) == expected, f"PREDECESSOR_CHANGED:{name}"
    annual = []
    groups = []
    fits = []
    frames: dict[int, pd.DataFrame] = {}
    historical = []
    for fold in protocol["folds"]:
        year = fold["year"]
        dest = out / f"F{year % 100}"
        if not (dest / "result.json").exists():
            continue
        result = b.read(dest / "result.json")
        selected = b.read(dest / "selection.json")
        assert result["status"] == "COMPLETED"
        raw = pd.read_parquet(dest / "oos_scores.parquet")
        frame = pd.read_parquet(reference_root(year) / "oos_scores.parquet")
        pd.testing.assert_frame_equal(
            raw[frame.columns.intersection(raw.columns)],
            frame[frame.columns.intersection(raw.columns)],
            check_dtype=False,
        )
        np.testing.assert_array_equal(raw.O1, decoded(raw.z.to_numpy(), result["scale"]))
        frame["O1"] = raw.O1
        logit = torch.from_numpy(raw.z.to_numpy().astype(float))
        dldz = (
            2
            * ((positive(logit, result["scale"]).numpy() - frame.A.to_numpy()) / result["scale"])
            * torch.sigmoid(logit).numpy()
        )
        frame["O1_abs_dLdz"] = abs(dldz)
        gradient_mass = float(frame.weight.to_numpy(float) @ frame.O1_abs_dLdz.to_numpy(float))
        assert np.isfinite(frame[[*ARMS, "A"]].to_numpy()).all()
        assert not frame.duplicated(["origin_id", "ticker"]).any()
        assert frame.groupby("origin_id").size().eq(20).all()
        frames[year] = frame
        fits.append(
            dict(
                year=year,
                selected_epoch=result["selected_epoch"],
                selector_epochs=result["selector_epochs"],
                raw_minimum_epoch=result["raw_minimum_epoch"],
                qualified_scaled_MSE=selected["best"],
                raw_minimum_scaled_MSE=selected["raw_best"],
                initial_scale=result["initial_scale"],
                restricted_scale=result["scale"],
                seconds=result["seconds"],
                peak_rss=result["peak_rss_bytes"],
                reload_error=result["reload_max_error"],
                minimum_prediction=result["prediction_min"],
                maximum_prediction=result["prediction_max"],
                zero_rows=result["prediction_zero_rows"],
            )
        )
        cuts = np.unique(
            [
                b.quantile(frame.O1.to_numpy(), q, frame.weight.to_numpy())
                for q in np.arange(0.1, 1, 0.1)
            ]
        )
        bins = np.searchsorted(cuts, frame.O1, side="left") + 1
        all_masks = [
            (field, str(label), frame[field].eq(label))
            for field in ("category", "slot")
            for label in frame[field].unique()
        ]
        for p in (95, 99):
            event = frame.A.gt(fold["thresholds"][str(p)])
            all_masks.extend([("tail", f"PREFIX{p}", event), ("tail", f"LE_PREFIX{p}", ~event)])
        all_masks.extend(
            ("O1_decile", str(n), pd.Series(bins == n, index=frame.index)) for n in np.unique(bins)
        )
        for arm in ARMS:
            stat = b.metrics(frame, arm)
            annual.append(dict(year=str(year), arm=arm, **stat, **b.rank_metrics(frame, arm)))
            low = frame.groupby("origin_id")[arm].rank(method="average").le(10.5)
            membership = top_membership(frame[arm].to_numpy())
            for field, label, mask in all_masks:
                g = frame.loc[mask]
                value = b.metrics(g, arm)
                contribution = float((g.weight * (g[arm] - g.A) ** 2).sum())
                value.update(
                    year=str(year),
                    arm=arm,
                    field=field,
                    group=label,
                    weight_mass=float(g.weight.sum()),
                    raw_MSE_contribution=contribution,
                    raw_MSE_loss_share=contribution / stat["raw_MSE"],
                )
                if arm == "O1":
                    value["O1_abs_dLdz_share"] = (
                        float(g.weight.to_numpy(float) @ g.O1_abs_dLdz.to_numpy(float))
                        / gradient_mass
                    )
                if field == "O1_decile":
                    value.update(O1_min=float(g.O1.min()), O1_max=float(g.O1.max()))
                if field == "tail":
                    value["false_low_rank"] = float(np.average(low.loc[mask], weights=g.weight))
                    if not label.startswith("LE_"):
                        event = mask.to_numpy(float)
                        w = frame.weight.to_numpy(float)
                        value.update(
                            event_AP=average_precision(event, frame[arm].to_numpy(), w),
                            event_AUC=auc(event, frame[arm].to_numpy(), w),
                            event_prevalence=float(w @ event),
                            top4_event_recall=float(w @ (event * membership) / (w @ event)),
                            top4_event_precision=float(w @ (event * membership) / (w @ membership)),
                        )
                groups.append(value)
        original = pd.read_parquet(
            b.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "return_4h", "prediction_A", "weight"],
        )
        np.testing.assert_array_equal(
            original[["origin_id", "ticker"]], frame[["origin_id", "ticker"]]
        )
        historic = frame.copy()
        historic["HIST_MAG"] = original.prediction_A
        historical.append(
            dict(
                year=str(year), arm="HIST_MAG_DIFFERENT_HISTORY", **b.metrics(historic, "HIST_MAG")
            )
        )
    complete = set(frames) == set(b.YEARS)
    if not annual:
        (out / "S9_MAG_STAGE1_SESSION3_O1_REPORT.md").write_text(
            (
                "# O1 Session3\n\nPREPARED: no empirical model fit complete. See "
                "protocol.json and role_counts.csv.\n"
            )
        )
        return
    m = pd.DataFrame(annual)
    g = pd.DataFrame(groups)
    pairs = []
    for arm in b.ARMS:
        daily: dict[int, pd.Series] = {}
        for year, frame in frames.items():
            daily[year] = paired_daily(frame, arm)
            interval = b.block_interval(daily[year])
            reference = float(m.loc[m.year.eq(str(year)) & m.arm.eq(arm), "raw_MSE"].iloc[0])
            pairs.append(
                dict(
                    year=str(year),
                    reference=arm,
                    percent_change=100 * interval["mean"] / reference,
                    includes_zero=interval["low"] <= 0 <= interval["high"],
                    **interval,
                )
            )
        if complete:
            interval = previous.bootstrap_equal_year(daily)
            reference = float(m.loc[m.arm.eq(arm), "raw_MSE"].mean())
            pairs.append(
                dict(
                    year="EQ",
                    reference=arm,
                    percent_change=100 * interval["mean"] / reference,
                    includes_zero=interval["low"] <= 0 <= interval["high"],
                    **interval,
                )
            )
    if complete:
        eq = []
        metric_names = [
            "observed",
            "predicted",
            "bias",
            "raw_MSE",
            "raw_MAE",
            "magnitude_IC",
            "pair_concordance",
            "top4",
            "bottom4",
            "tie_rate",
            "constant_rate",
        ]
        for arm, h in m.groupby("arm", sort=False):
            value = {name: float(h[name].mean()) for name in metric_names}
            value["ratio"] = value["predicted"] / value["observed"]
            eq.append(
                dict(
                    year="EQ",
                    arm=arm,
                    rows=int(h.rows.sum()),
                    sessions=int(h.sessions.sum()),
                    origins=int(h.origins.sum()),
                    **value,
                )
            )
        m = pd.concat([m, pd.DataFrame(eq)], ignore_index=True)
        eqg = []
        for (arm, field, label), h in g.groupby(["arm", "field", "group"], sort=False):
            assert len(h) == 4
            value = {
                name: float(h[name].mean())
                for name in [
                    "observed",
                    "predicted",
                    "bias",
                    "raw_MSE",
                    "raw_MAE",
                    "weight_mass",
                    "raw_MSE_contribution",
                    "false_low_rank",
                    "event_AP",
                    "event_AUC",
                    "event_prevalence",
                    "top4_event_recall",
                    "top4_event_precision",
                    "O1_abs_dLdz_share",
                ]
            }
            value["ratio"] = value["predicted"] / value["observed"]
            total = float(m.loc[m.year.eq("EQ") & m.arm.eq(str(arm)), "raw_MSE"].iloc[0])
            value["raw_MSE_loss_share"] = value["raw_MSE_contribution"] / total
            eqg.append(
                dict(
                    year="EQ",
                    arm=arm,
                    field=field,
                    group=label,
                    rows=int(h.rows.sum()),
                    sessions=int(h.sessions.sum()),
                    origins=int(h.origins.sum()),
                    **value,
                )
            )
        g = pd.concat([g, pd.DataFrame(eqg)], ignore_index=True)
        h = pd.DataFrame(historical)
        value = {
            name: float(h[name].mean())
            for name in ["observed", "predicted", "bias", "raw_MSE", "raw_MAE"]
        }
        value["ratio"] = value["predicted"] / value["observed"]
        historical.append(
            dict(
                year="EQ",
                arm="HIST_MAG_DIFFERENT_HISTORY",
                rows=int(h.rows.sum()),
                sessions=int(h.sessions.sum()),
                origins=int(h.origins.sum()),
                **value,
            )
        )
    for reference in ("C0", "C1a", "M1"):
        match = g.loc[g.arm.eq(reference), ["year", "field", "group", "raw_MSE"]].rename(
            columns={"raw_MSE": f"MSE_{reference}"}
        )
        g = g.merge(match, on=["year", "field", "group"], validate="many_to_one")
        g[f"delta_MSE_vs_{reference}"] = g.raw_MSE - g[f"MSE_{reference}"]
        g[f"percent_MSE_vs_{reference}"] = (
            100 * g[f"delta_MSE_vs_{reference}"] / g[f"MSE_{reference}"]
        )
    p = pd.DataFrame(pairs)
    m.to_csv(out / "metrics.csv", index=False)
    g.to_csv(out / "groups.csv", index=False)
    p.to_csv(out / "paired_MSE.csv", index=False)
    write_report(out, m, g, p, pd.DataFrame(fits), pd.DataFrame(historical), complete)


def write_report(
    out: Path,
    m: pd.DataFrame,
    g: pd.DataFrame,
    p: pd.DataFrame,
    fits: pd.DataFrame,
    historical: pd.DataFrame,
    complete: bool,
) -> None:
    protocol = b.read(out / "protocol.json")
    counts = pd.read_csv(out / "role_counts.csv")
    notes = b.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    verified = b.read(out / "verification.json")
    sections = [
        "# S9 MAG Stage1 / Session3 — O1 direct expected absolute magnitude",
        (
            f"**Status: {'COMPLETE' if complete else 'PARTIAL'}.** {len(fits)}/4 folds; "
            "exploratory/post-search."
        ),
        (
            f"Ledger {protocol['ledger_before']}→{134 + len(fits)}/200; "
            f"{len(fits)} new pairs / {2 * len(fits)} phase fits. "
            "No empirical neural failure/retry. One preparation-only checker correction "
            "occurred before any neural start and is disclosed below."
        ),
        "## Executive result",
        notes.get("executive", "Scientific interpretation awaits the completed frozen scores."),
        "## Frozen objective, model and chronology",
        (
            "A=abs(log(P_endpoint/P_origin)); Ahat=s·torch.softplus(z). Loss is"
            " mean session → mean origin → mean20 ((Ahat−A)/s)^2. Positive "
            "prefix s is the weighted left median of raw A, floored at1e−8. "
            "This changes the objective, output link and target-appropriate "
            "checkpoint monitor together; it does not isolate only an algebraic"
            " loss change."
        ),
        (
            "The shared LSTM remains 48×16 FT16, one H32 layer, final-hidden "
            "dropout0.10, scalar linear head, zero state per window and6,433 "
            "parameters. CPU float32, seed42, AdamW .001/(.9,.999)/eps1e−8, "
            "matrix decay.01/bias0, clip1,16 complete sessions per batch; "
            "shuffle RNG42+epoch. Qualify first finite nonnegative score, then "
            "loss≤.999×qualified best; min12,patience10,max60. Fresh "
            "same-seed/empty-optimizer September refit uses the selected count."
            " No EVENT head/weight, alternative link, calibration or new "
            "information."
        ),
        b.markdown(
            counts[
                [
                    "year",
                    "role",
                    "start",
                    "cutoff",
                    "first_date",
                    "last_date",
                    "sessions",
                    "origins",
                    "stock_rows",
                ]
            ]
        ),
        (
            "Roles reuse the saved S4 eligibility and unchanged executed Design"
            " A role-mask code/cutoffs; exact derived row indices are in "
            "role_indices.npz and all seven slot counts/maturity limits in "
            "role_counts.csv. All original OOS keys match in tensor order. "
            "First of48 completed scheduled steps is after the preceding "
            "cutoff; genuine targets span240 trading minutes, including "
            "existing crossings. October–December remains reserved and entirely"
            " excluded from O1 fitting/selection; no O1 calibration predictions"
            " or map were made."
        ),
        b.markdown(
            fits[
                [
                    "year",
                    "selector_epochs",
                    "selected_epoch",
                    "raw_minimum_epoch",
                    "qualified_scaled_MSE",
                    "raw_minimum_scaled_MSE",
                    "initial_scale",
                    "restricted_scale",
                ]
            ]
        ),
        b.markdown(
            fits[
                [
                    "year",
                    "seconds",
                    "peak_rss",
                    "reload_error",
                    "minimum_prediction",
                    "maximum_prediction",
                    "zero_rows",
                ]
            ]
        ),
        (
            "All eight phase recipes were recomputed before the first neural "
            "start and every FT16 field matched the saved causal predecessor "
            "exactly (phase_parity.json). The initial whole-record checker stopped "
            "because the source F21 S4 record also has five unused target metadata "
            "keys: epsilon,t2_scale,s4_contexts,task,target_minutes. The correction "
            "recognizes only these exact source-only fields; every scaler, floor, "
            "fallback, input key and fitting quantity remains checked exactly. "
            "No canonical recipe was overwritten, and no model had started at "
            "that stop. execution.log preserves it; execution_002.log is the "
            "subsequent successful preparation/fitting log. "
            "Phase scales are recomputed on legal prefixes, not borrowed from "
            "full-December refits. Raw minimum and qualifying selected epochs "
            "are recorded separately in selection.json; raw minimum need not be"
            " selected."
        ),
        "## Matched annual and equal-year proper scores",
        (
            "Weight/unit spot-check: a one-origin day and a two-origin day, "
            "all20 stocks/origin, forecasts0.02 versus true magnitudes0.01/0.02/0.04, "
            "s=0.01, give scaled loss0.5×1+0.25×0+0.25×4=1.5 and "
            "raw MSE0.00015 squared log-return units. Naive equal-origin loss is5/3. "
            "Flipping every signed return leaves O1 loss/gradients unchanged."
        ),
        b.markdown(
            m[
                [
                    "year",
                    "arm",
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "bias",
                    "ratio",
                    "magnitude_IC",
                ]
            ]
        ),
        (
            "Raw means/MAE/bias use absolute log-return units; MSE uses squared"
            " log-return units. Weights are equal stocks within origin → equal "
            "origins within session → equal sessions within year → arithmetic "
            "equal years. EQ ratio is the ratio of equal-year means. No "
            "equal-row pooling. B0-RMED targets a stock median and is primarily"
            " an MAE control, not a raw-mean model."
        ),
        (
            "Frozen controls fit through September: B0-RMEAN is a stock raw mean; "
            "B0-RMED a weighted left median; B0-CLOCK a stock×slot mean shrunk by "
            "50 origin-equivalent observations toward stock means. B0-VOL has27 "
            "columns: intercept,19 stock indicators (VZ reference),six clocks "
            "(09:30 reference),prefix-standardized log(decoded FT16 V2 RMS60). "
            "Its archived ridge penalty is0.001 in each fold. Stock/clock identities "
            "are known baseline inputs, not newly added neural channels. No reference "
            "coefficient or prediction was refitted here."
        ),
        "## Paired O1-minus-comparator raw MSE",
        b.markdown(p.loc[p.reference.isin(["C0", "C1a", "M1", "B0-VOL"])]),
        (
            "Negative deltas favor O1. All seven reference contrasts are in "
            "paired_MSE.csv. Annual intervals reuse "
            "whole-calendar-month400-draw bootstrap seed22042. Equal-year "
            "intervals independently resample months within each year, then "
            "average four annual session means. All stocks/overlapping origins "
            "stay in their session. Intervals are descriptive95% percentile "
            "bounds conditional on fitted models, not selection/search-adjusted"
            " confirmation; four folds are not IID replications."
        ),
        "## Clocks, ordinary periods and large moves",
        notes.get("groups", ""),
        b.markdown(
            g.loc[
                g.year.ne("EQ") & g.arm.eq("O1") & g.group.isin(["PREFIX95", "PREFIX99"]),
                ["year", "group", "rows", "sessions", "origins", "weight_mass", "false_low_rank"],
            ]
        ),
        b.markdown(
            g.loc[
                g.year.eq("EQ") & g.arm.eq("O1") & g.field.isin(["category", "slot", "tail"]),
                [
                    "field",
                    "group",
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "ratio",
                    "weight_mass",
                    "raw_MSE_loss_share",
                    "O1_abs_dLdz_share",
                    "percent_MSE_vs_C0",
                    "percent_MSE_vs_C1a",
                    "percent_MSE_vs_M1",
                ],
            ]
        )
        if complete
        else "Four-year group summary unavailable.",
        (
            "Annual subgroup counts/sessions and paired point differences are "
            "in groups.csv. Conditional errors normalize the original weights "
            "within group, then average years; loss shares use equal-year "
            "unconditional contribution divided by total loss. Prefix95/99 "
            "strict thresholds come from the saved restricted-September fitting"
            " population, not OOS. Group differences are paired point "
            "descriptions, not independent subgroup tests or new targets. No "
            "separate overnight model was fitted."
        ),
        "## Magnitude and event discrimination",
        notes.get("ranking", ""),
        b.markdown(
            m.loc[
                m.year.eq("EQ") | m.arm.eq("O1"),
                [
                    "year",
                    "arm",
                    "magnitude_IC",
                    "pair_concordance",
                    "top4",
                    "bottom4",
                    "tie_rate",
                    "constant_rate",
                ],
            ]
        ),
        (
            "Magnitude IC uses within-origin average ranks then "
            "origin/session/year aggregation. Undefined constant-output IC is "
            "omitted and its rate reported. Pair concordance excludes actual "
            "ties and gives half credit to predicted ties (chance.5). "
            "Top/bottom4 uses fractional boundary-tie membership (chance.2). No"
            " alphabetical tie advantage or signed-return interpretation."
        ),
        b.markdown(
            g.loc[
                g.year.eq("EQ") & g.group.isin(["PREFIX95", "PREFIX99"]),
                [
                    "arm",
                    "group",
                    "event_prevalence",
                    "event_AP",
                    "event_AUC",
                    "false_low_rank",
                    "top4_event_recall",
                    "top4_event_precision",
                ],
            ]
        )
        if complete
        else "Four-year event summary unavailable.",
        (
            "Event AP/AUC reuse the executed threshold-grouped weighted "
            "routines on continuous scores and prefix-defined raw-A events. "
            "These annual pooled scores can reflect stock/calendar risk levels;"
            " EQ averages annual AP/AUC, not pooled rows. Constant-score AP "
            "equals event prevalence; AUC chance.5. False-low rate is event "
            "mass at within-origin midrank≤10.5 divided by event mass, then "
            "mean years; top4 recall is event mass captured by fractional top4."
            " Magnitudes are not event probabilities. Stock-prior comparator "
            "unavailable: archived EVENT labels use |TG20|, not the same raw-A "
            "prefix95/99 labels. Earlier E1/S9-EVENT results therefore "
            "establish no complementary event benefit here."
        ),
        "## Descriptive reliability",
        b.markdown(
            g.loc[
                g.year.eq("EQ") & g.arm.eq("O1") & g.field.eq("O1_decile"),
                ["group", "observed", "predicted", "ratio", "raw_MSE", "raw_MAE"],
            ]
        )
        if complete
        else "Four-year reliability unavailable.",
        (
            "Ten weighted empirical O1 score deciles per annual OOS population;"
            " same bins for every comparator. Numeric ranges, counts and "
            "sessions are in groups.csv. These are descriptive percentile bins,"
            " not future calibration boundaries. Equal-year deciles average "
            "corresponding annual percentile bins without claiming common "
            "numerical cutpoints. No correction is fitted on these diagnostics."
        ),
        "## Historical context and interpretation",
        notes.get("decision", ""),
        b.markdown(historical),
        (
            "HIST_MAG refit through December and is contextual only: no primary"
            " paired causal comparison or model selection uses it. Its archived"
            " transformed MSE0.232454 is a different objective/scale and cannot"
            " be the raw-mean O1 promotion score. The original price-only label"
            " begins before approximate origin+2min issuance. Endpoint "
            "magnitude is not integrated variance, option-IV mispricing, "
            "execution P&L or a tradability result."
        ),
        "## Reproduction, preservation and stop",
        (
            "Run IDs: HF20-O1-F{21,22,23,24}-DESIGNA-S42. Under this report root, "
            "F21/F22/F23/F24 each contain restricted_final.pt, selected_initial.pt, "
            "oos_scores.parquet, initial_recipe.json, restricted_recipe.json, "
            "phases.json, selection.json, training.csv and result.json. Source entry "
            "point: src/lstm_data/hf20_mag_o1.py; focused fixtures: "
            "tests/test_hf20_mag_o1.py. Aggregate outputs are metrics.csv, "
            "paired_MSE.csv and groups.csv. interpretation.json stores the reviewed "
            "post-fit narrative, not fitting choices. No predecessor predictions "
            "or bulk feature store were copied."
        ),
        (
            "`.venv/bin/python -m lstm_data.hf20_mag_o1 "
            f"--out {out} --report` replays saved scores only; --run is single-use. "
            "protocol.json fixes all choices before fitting. phases.json, selection.json "
            "and result.json bind each new run to recipes/scales, fresh initialization, "
            "selected epoch and final checkpoint. Comparator scores remain referenced "
            "from Session2/2B and are never copied or refitted. New O1 stores contain "
            "only its keys/labels/weights/z/O1 forecasts."
        ),
        (
            f"Source allowlist: {b.S4}/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv; "
            "174 existing adjusted-hourly partitions2010-07 through2024-12; same S4 "
            "target/eligibility and original S9 OOS keys. No minute reconstruction, "
            "download, protected2026 numerical read/hash or opportunistic2025 exploration. "
            "No prior artifact/dashboard/ledger history was overwritten; only the "
            "current append-only successor pointer changes."
        ),
        (
            "Final verification is in verification.json and the mandatory session "
            "report reports/codex_sessions/2026-10-28_004000_hf20_s9_mag_session3_o1.md. "
            "No automatic O2–O7, C3, new "
            "architecture/seed, overnight target, options/backtest or protected"
            " confirmation. STOP for researcher review."
        ),
        verified.get("final_summary", "Final verification not yet recorded."),
    ]
    (out / "S9_MAG_STAGE1_SESSION3_O1_REPORT.md").write_text("\n\n".join(sections) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    out = args.out
    if args.report:
        report(out)
        return
    if (out / "neural_starts.jsonl").exists():
        raise SystemExit("NO_RETRY: O1 namespace already has a charged lifecycle")
    if args.run:
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
    grid, rows, plans, protocol = preflight(out)
    print(
        json.dumps(
            dict(
                status="PREFLIGHT_PASS",
                folds=protocol["folds"],
                resources=protocol["resources"],
                workload=protocol["workload"],
            ),
            indent=2,
        ),
        flush=True,
    )
    if not args.run:
        return
    (out / ".gitignore").write_text("*.parquet\n*.pt\n")
    c, r = b.source_components(grid, rows)
    prepare_recipes(out, c, rows, protocol)
    for fold in protocol["folds"]:
        year = fold["year"]
        run_fold(out, year, c, rows, r, plans[year], fold)
        b.write(
            out / "continuation.json",
            dict(
                completed_years=list(range(2021, year + 1)),
                pending_years=list(range(year + 1, 2025)),
                retry=False,
            ),
        )
        report(out)


if __name__ == "__main__":
    main()
