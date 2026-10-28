"""Bounded S2-A/S2-E: four fixed loss weights, past-only selection, hard routing."""

from __future__ import annotations

import argparse
import gc
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_mag_o1 as o1

OUT = Path("reports/experiments/hf20_s9_mag_stage2_session1_overnight_specialist_2026-10-28")
LAMBDAS = (0.0, 0.10, 0.25, 0.50)
NIGHT = "OVERNIGHT"
NEW = ("ROUTE-RAW", "ROUTE-SMEAR", "OLD-N-SMEAR-MATCHED")
ARMS = (*NEW, "C3", "M1", "C1a", "C0", "O1", "B0-VOL", "B0-CLOCK", "B0-RMEAN", "B0-RMED")


def conditional_weights(days: np.ndarray, category: np.ndarray, group: str) -> np.ndarray:
    """Separate equal-session/origin group mean, zero outside the category."""
    mask = category == group
    if not mask.any():
        raise ValueError("EMPTY_CONDITIONAL_LOSS_GROUP")
    w = np.zeros(len(days), dtype=float)
    w[mask] = b.origin_weights(days[mask])
    return w


def loss_weights(days: np.ndarray, category: np.ndarray, lam: float) -> np.ndarray:
    if lam not in LAMBDAS:
        raise ValueError("UNAUTHORIZED_LAMBDA")
    return conditional_weights(days, category, NIGHT) + lam * conditional_weights(
        days, category, "INTRADAY"
    )


def weighted_loss(
    mhat: torch.Tensor, returns: torch.Tensor, scale: float, weights: np.ndarray
) -> torch.Tensor:
    assert mhat.shape == returns.shape and mhat.ndim == 2 and mhat.shape[1] == 20
    target = torch.log1p(returns.abs() / scale)
    w = torch.from_numpy(weights).to(dtype=mhat.dtype, device=mhat.device)
    return ((mhat - target).square().mean(1) * w).sum()


def choose_candidate(records: list[dict]) -> dict:
    """Predefined raw selector loss, exact ties prefer larger lambda."""
    if len(records) != 4 or {r["lambda"] for r in records} != set(LAMBDAS):
        raise ValueError("FOUR_CANDIDATES_REQUIRED")
    if not all(np.isfinite(r["selector_raw_MSE"]) for r in records):
        raise ValueError("NONFINITE_SELECTOR_SCORE")
    return min(records, key=lambda r: (r["selector_raw_MSE"], -r["lambda"]))


def route(old: np.ndarray, night: np.ndarray, category: np.ndarray) -> np.ndarray:
    """All twenty stocks in an origin take the same deterministic branch."""
    if old.shape != night.shape or old.shape != category.shape:
        raise ValueError("ROUTER_SHAPE_MISMATCH")
    if not np.isin(category, c3.GROUPS).all():
        raise ValueError("UNKNOWN_ROUTER_CATEGORY")
    result = np.where(category == NIGHT, night, old)
    if not np.isfinite(result).all() or (result < 0).any():
        raise ValueError("INVALID_ROUTED_FORECAST")
    np.testing.assert_array_equal(result[category != NIGHT], old[category != NIGHT])
    return result


def frozen_c3(f: pd.DataFrame, year: int) -> np.ndarray:
    coef = pd.read_csv(c3.OUT / "calibration_coefficients.csv", float_precision="round_trip")
    co = coef.loc[coef.year.eq(year)].set_index("group")
    assert co.scale.nunique() == 1
    return c3.decode(
        f.Mhat.to_numpy(), float(co.scale.iloc[0]), f.category.map(co.c_star).to_numpy()
    )


def preflight(out: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[int, dict], dict]:
    """Exact saved roles/recipes and projected OOS keys; no OOS outcomes read."""
    pointer = b.read(b.POINTER)
    history = Path(pointer["real_journal"])
    last = json.loads(history.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 138
    assert pointer["effective_ceiling"] == 200 and 138 + 16 <= 200
    assert b.digest(Path(pointer["plan"]["path"])) == pointer["plan"]["sha256"]
    prior = b.read(c3.OUT / "protocol.json")
    for path, sha in prior["preservation_bindings"].items():
        assert b.digest(Path(path)) == sha, f"PREDECESSOR_CHANGED:{path}"
    grid, rows = b.metadata()
    indices = np.load(o1.OUT / "role_indices.npz")
    role_counts = pd.read_csv(o1.REF / "role_counts.csv")
    first = np.full(len(rows), "0000", dtype=object)
    mask = rows.first_step.ge(0)
    first[mask] = grid.session_date_et.to_numpy()[rows.loc[mask, "first_step"].to_numpy(int)]
    early = set(
        rows.loc[
            rows.session_close.dt.tz_convert("America/New_York").dt.strftime("%H:%M").lt("16:00"),
            "session_date_et",
        ]
    )
    plans: dict[int, dict] = {}
    counts, folds = [], []
    bindings = {
        path: sha for path, sha in prior["preservation_bindings"].items() if path != str(b.POINTER)
    }
    for year in b.YEARS:
        fold = b.read(o1.OUT / f"F{year % 100}/phases.json")
        plans[year] = {}
        for record in role_counts.loc[role_counts.year.eq(year)].to_dict("records"):
            role = str(record["role"])
            ix = indices[f"F{year % 100}_{role}"]
            derived = np.flatnonzero(
                b.role_mask(
                    rows,
                    first,
                    str(record["start"]),
                    str(record["cutoff"]),
                    str(record["embargo_after"]),
                )
            )
            np.testing.assert_array_equal(ix, derived)
            g = rows.iloc[ix]
            assert len(g) == record["origins"] and g.session_date_et.nunique() == record["sessions"]
            assert g.entry_index.sub(g.first_step).eq(47).all() and g.trading_minutes.eq(240).all()
            assert g.label_maturity_utc.lt(b.limit(str(record["cutoff"]))).all()
            assert (first[ix] > str(record["embargo_after"])).all()
            plans[year][role] = ix
            for group in c3.GROUPS:
                sub = g.loc[g.category.eq(group)]
                assert len(sub), "BLOCKED_EMPTY_ROLE_GROUP"
                w = conditional_weights(g.session_date_et.to_numpy(), g.category.to_numpy(), group)
                counts.append(
                    dict(
                        year=year,
                        role=role,
                        group=group,
                        sessions=sub.session_date_et.nunique(),
                        origins=len(sub),
                        rows=len(sub) * 20,
                        conditional_weight_sum=float(w.sum()),
                        minimum_origin_weight=float(w[w > 0].min()),
                        maximum_origin_weight=float(w.max()),
                        first_date=sub.session_date_et.min(),
                        last_date=sub.session_date_et.max(),
                    )
                )
            if role == "selector":
                assert g.session_date_et.nunique() >= 50
                assert g.groupby("slot").size().reindex(b.SLOTS, fill_value=0).min() >= 25
            if role in ("calibration", "oos"):
                f = pd.read_parquet(
                    c3.root(year) / f"{role}_scores.parquet",
                    columns=[*c3.META, "Mhat", "C0", "C1a", "M1"],
                )
                c3.validate_panel(f, early)
                np.testing.assert_array_equal(f.origin_id.iloc[::20], g.origin_id)
                np.testing.assert_array_equal(f.category.iloc[::20], g.category)
                assert np.isfinite(frozen_c3(f, year)).all()
                coeff = b.read(c3.root(year) / "coefficients.json")
                np.testing.assert_allclose(
                    c3.decode(f.Mhat.to_numpy(), fold["phases"]["restricted"]["scale"], coeff["c"]),
                    f.C1a,
                    atol=1e-14,
                    rtol=1e-13,
                )
        p = plans[year]
        for a, z in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("selector", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(p[a], p[z]).size
        assert np.isin(p["selector"], p["restricted_refit"]).all()
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            recipe_path = o1.OUT / f"F{year % 100}/{phase}_recipe.json"
            recipe = b.read(recipe_path)
            cutoff = fold["phases"][phase]["cutoff"]
            assert recipe["fit_stop_inclusive"] == cutoff
            np.testing.assert_array_equal(
                recipe["fit_hour_indices"], np.flatnonzero(b.feature_fit_hours(grid, rows, cutoff))
            )
            assert fold["phases"][phase]["scale"] > 0
            bindings[str(recipe_path)] = b.digest(recipe_path)
        folds.append(fold)
    manifest = pd.read_csv(b.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv")
    manifest = manifest.loc[manifest.purpose.eq("permitted adjusted hourly source")]
    assert len(manifest) == 174
    for item in manifest.to_dict("records"):
        path = Path(str(item["path"]))
        assert (
            not path.is_absolute()
            and ".." not in path.parts
            and "2010-07" <= path.stem <= "2024-12"
        )
        assert path.is_file() and path.stat().st_size == item["bytes"]
    traces = pd.concat([pd.read_csv(c3.root(y) / "training.csv") for y in b.YEARS])
    resources = b.resources(out)
    protocol = dict(
        kind="HF20_STAGE2_S2A_S2E_OVERNIGHT_SPECIALIST_V1",
        folds=folds,
        lambdas=list(LAMBDAS),
        loss="L_N+lambda L_D; separate equal group-session/origin/20-stock means",
        batches=(
            "16 complete sessions; full-role conditional origin weights multiplied "
            "by all_role_sessions/batch_sessions; missing group contributes zero; "
            "batch-session-weighted epoch reduction equals population loss at fixed"
            " parameters"
        ),
        epoch_monitor=(
            "overnight-only transformed MSE; first finite nonnegative; <=.999 best;"
            " min12 patience10 max60"
        ),
        lambda_selection=(
            "selected checkpoints overnight raw MSE; exact ties larger lambda, then candidate order"
        ),
        calibration=(
            "one overnight-only smear for selected refit plus same-operation frozen"
            " old control; canonical calibration row weights restricted and "
            "renormalized; no shrink/trim"
        ),
        routing=(
            "frozen C3 on saved INTRADAY; selected specialist on saved OVERNIGHT "
            "including early closes; no mixing within origin"
        ),
        information=(
            "unchanged own-stock FT16 48x16; H32 one layer dropout.10 linear M head;6433 parameters"
        ),
        optimizer=(
            "CPU float32;seed42;AdamW lr.001 betas(.9,.999) eps1e-8 matrix decay.01"
            " bias0;clip1;16sessions"
        ),
        scoring=(
            "original stock/origin/session/year weights; conditional "
            "renormalization for group OOS; equal four years"
        ),
        uncertainty=dict(
            draws=400, seed=22042, unit="whole months within year; weighted group mass preserved"
        ),
        bins="10 weighted saved C3 score deciles per year, common arm membership, descriptive",
        tails=(
            "existing September prefix95/99 strict raw A exceedance and "
            "complements; no new thresholds"
        ),
        ledger_before=138,
        maximum_new_starts=16,
        maximum_neural_phase_fits=20,
        maximum_after=154,
        ledger_units=(
            "one charged candidate start; selected candidate fresh refit part of "
            "its same pair; unselected starts remain charged"
        ),
        prior_pointer=pointer,
        preservation_bindings=bindings,
        early_close_dates=sorted(early),
        caps=b.CAPS,
        resources=resources,
        source_partitions=174,
        source_end="2024-12-31",
        workload=dict(
            maximum_epochs=1200,
            reference_epoch_seconds_p95=float(traces.seconds.quantile(0.95)),
            rough_max_seconds=1200 * float(traces.seconds.quantile(0.95)),
            artifact_reserve_bytes=40_000_000,
        ),
        no_oos_outcomes_in_preflight=True,
        protection=(
            "No2025/2026 numerical source/hash; only saved authorized pre2025 "
            "hourly read receipt; no minute rebuild/download"
        ),
        git_start="5f7bb86a35d5aaff34ff79ef8f471117de6d3e42",
    )
    out.mkdir(exist_ok=True)
    if (out / "protocol.json").exists():
        old = b.read(out / "protocol.json")
        assert old["folds"] == folds and old["preservation_bindings"] == bindings
    else:
        b.write(out / "protocol.json", protocol, new=True)
    b.write(
        out / "preflight.json", dict(status="PASS", counts=counts, resources=resources, ledger=138)
    )
    print(pd.DataFrame(counts).to_string(index=False), flush=True)
    return grid, rows, plans, protocol


def event(out: Path, year: int, lam: float, status: str, detail: dict) -> None:
    """Candidate starts charged once, final selected refit uncharged as a separate pair."""
    protocol = b.read(out / "protocol.json")
    path = out / "neural_starts.jsonl"
    history = [json.loads(v) for v in path.read_text().splitlines()] if path.exists() else []
    starts = [v for v in history if v["status"] == "STARTED"]
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["prior_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert len(starts) < 16 and not any(
            v["year"] == year and v["lambda"] == lam for v in starts
        )
        assert not history or history[-1]["status"] in ("CANDIDATE_COMPLETED", "COMPLETED")
        b.resources(out)
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        year=year,
        **{"lambda": lam},
        status=status,
        global_started_pairs=138 + len(starts) + int(status == "STARTED"),
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
            schema_version=27,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def train_epoch(
    view: b.View,
    pos: np.ndarray,
    model: b.SharedLSTM,
    opt: torch.optim.AdamW,
    epoch: int,
    lam: float,
) -> dict:
    role = view.rows.iloc[pos]
    w = loss_weights(role.session_date_et.to_numpy(), role.category.to_numpy(), lam)
    groups = role.groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + epoch).shuffle(days)
    model.train()
    norms = []
    for k in range(0, len(days), 16):
        batchdays = days[k : k + 16]
        local = np.concatenate([groups[d] for d in batchdays])
        selected = pos[local]
        x = view.x(selected)
        assert x.shape[1:] == (20, 48, 16)
        opt.zero_grad()
        mhat = model(torch.from_numpy(x.reshape(-1, 48, 16))).reshape(-1, 20)
        loss = weighted_loss(
            mhat,
            torch.from_numpy(view.r[selected].astype(np.float32)),
            view.scale,
            w[local] * (len(days) / len(batchdays)),
        )
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_SPECIALIST_LOSS")
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True)
        norms.append(float(norm))
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(v > 1 for v in norms)
    )


def raw_decode(mhat: np.ndarray, scale: float) -> np.ndarray:
    result = scale * np.expm1(np.maximum(mhat.astype(float), 0))
    if not np.isfinite(result).all() or (result < 0).any():
        raise ValueError("INVALID_RAW_DECODE")
    return result


def run_fold(
    out: Path, year: int, c: b.Components, rows: pd.DataFrame, r: np.ndarray, pos: dict, fold: dict
) -> None:
    dest = out / f"F{year % 100}"
    dest.mkdir(exist_ok=True)
    start = time.monotonic()
    initial_scale = fold["phases"]["initial"]["scale"]
    inner = b.View(c, rows, r, b.read(o1.OUT / f"F{year % 100}/initial_recipe.json"), initial_scale)
    selections = []
    traces = []
    current = 0.0
    try:
        for lam in LAMBDAS:
            current = lam
            model = b.model_for("MAG")
            opt = b.optimizer(model)
            assert not opt.state and sum(p.numel() for p in model.parameters()) == 6433
            initial = b.initial_hash(model)
            assert (
                initial
                == b.read(b.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/configuration.json")[
                    "initial_sha256"
                ]
            )
            selector = b.Selector()
            best = {}
            event(out, year, lam, "STARTED", dict(phase="initial"))
            while selector.status == "CALIBRATING":
                n = selector.epoch + 1
                tick = time.monotonic()
                train = train_epoch(inner, pos["inner_train"], model, opt, n, lam)
                ix = pos["selector"]
                g = rows.iloc[ix]
                night = ix[g.category.eq(NIGHT).to_numpy()]
                z = b.predict(inner, night, model)
                target = torch.log1p(
                    torch.from_numpy(r[night].astype(np.float32)).abs() / initial_scale
                ).numpy()
                w = b.origin_weights(rows.iloc[night].session_date_et.to_numpy())
                val = float(w @ ((z - target) ** 2).mean(1))
                if selector.observe(val):
                    best = {k: v.detach().clone() for k, v in model.state_dict().items()}
                traces.append(
                    dict(
                        year=year,
                        phase="selector",
                        **{"lambda": lam},
                        epoch=n,
                        validation_N_transformed_MSE=val,
                        selected=selector.selected,
                        seconds=time.monotonic() - tick,
                        **train,
                    )
                )
                pd.DataFrame(traces).to_csv(dest / "training.csv", index=False)
                print(year, lam, "selector", n, val, "selected", selector.selected, flush=True)
            model.load_state_dict(best)
            z = b.predict(inner, night, model)
            raw = raw_decode(z, initial_scale)
            rec = dict(
                year=year,
                **{"lambda": lam},
                selected_epoch=selector.selected,
                selector_epochs=selector.epoch,
                selector_transformed_MSE=selector.best,
                selector_raw_MSE=float(w @ ((raw - abs(r[night])) ** 2).mean(1)),
                raw_minimum_epoch=selector.raw_epoch,
                initial_sha256=initial,
                selected_checkpoint_sha256=b.initial_hash(model),
                status=selector.status,
            )
            selections.append(rec)
            event(out, year, lam, "CANDIDATE_COMPLETED", rec)
            del model, opt, best
            gc.collect()
        chosen = choose_candidate(selections)
        lam = chosen["lambda"]
        current = lam
        for rec in selections:
            rec["chosen"] = rec["lambda"] == lam
            rec["raw_tie"] = rec["selector_raw_MSE"] == chosen["selector_raw_MSE"]
        pd.DataFrame(selections).to_csv(dest / "selection.csv", index=False)
        scale = fold["phases"]["restricted"]["scale"]
        refit = b.View(c, rows, r, b.read(o1.OUT / f"F{year % 100}/restricted_recipe.json"), scale)
        model = b.model_for("MAG")
        opt = b.optimizer(model)
        assert not opt.state and b.initial_hash(model) == chosen["initial_sha256"]
        event(out, year, lam, "REFITTING", dict(epochs=chosen["selected_epoch"]))
        for n in range(1, chosen["selected_epoch"] + 1):
            tick = time.monotonic()
            train = train_epoch(refit, pos["restricted_refit"], model, opt, n, lam)
            traces.append(
                dict(
                    year=year,
                    phase="refit",
                    **{"lambda": lam},
                    epoch=n,
                    seconds=time.monotonic() - tick,
                    **train,
                )
            )
            pd.DataFrame(traces).to_csv(dest / "training.csv", index=False)
            print(year, lam, "refit", n, "of", chosen["selected_epoch"], flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        # The same frozen refit produces genuine calibration forecasts before OOS is projected.
        cp = pos["calibration"]
        cp = cp[rows.iloc[cp].category.eq(NIGHT).to_numpy()]
        m = b.predict(refit, cp, model)
        cal = pd.read_parquet(c3.root(year) / "calibration_scores.parquet")
        cal = cal.loc[cal.category.eq(NIGHT)].copy().reset_index(drop=True)
        np.testing.assert_array_equal(cal.origin_id.iloc[::20], rows.iloc[cp].origin_id)
        old_q = c3.residual_exp(cal, scale)
        wcal = cal.weight.to_numpy(float)
        old_factor = float(wcal @ old_q / wcal.sum())
        newcal = cal[[*c3.META, "A"]].copy()
        newcal["Mhat"] = m.ravel()
        np.testing.assert_array_equal(newcal.A, abs(r[cp]).ravel())
        q = c3.residual_exp(newcal, scale)
        factor = float(wcal @ q / wcal.sum())
        assert np.isfinite(factor) and factor > 0
        coefficients = dict(
            year=year,
            scale=scale,
            c_N=factor,
            old_c_N=old_factor,
            sessions=cal.session_date_et.nunique(),
            origins=len(cp),
            rows=len(cal),
            n_eff=c3.effective_sessions(cal),
            **c3.concentration(q, wcal),
            frozen_parameter_sha256=frozen,
        )
        b.write(dest / "coefficients.json", coefficients, new=True)
        newcal.to_parquet(dest / "calibration_scores.parquet", compression="zstd", index=False)
        oo = pos["oos"]
        oo = oo[rows.iloc[oo].category.eq(NIGHT).to_numpy()]
        z = b.predict(refit, oo, model)
        reloaded = b.model_for("MAG")
        reloaded.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, b.predict(refit, oo, reloaded))
        assert b.initial_hash(model) == frozen
        original = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        frame = (
            original.loc[original.category.eq(NIGHT), [*c3.META, "A"]].copy().reset_index(drop=True)
        )
        np.testing.assert_array_equal(frame.origin_id.iloc[::20], rows.iloc[oo].origin_id)
        np.testing.assert_array_equal(frame.A, abs(r[oo]).ravel())
        frame["Mhat"] = z.ravel()
        frame["N-RAW"] = raw_decode(z, scale).ravel()
        frame["N-SMEAR"] = c3.decode(z, scale, factor).ravel()
        frame.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
        result = dict(
            year=year,
            status="COMPLETED",
            **{"lambda": lam},
            selected_epoch=chosen["selected_epoch"],
            initial_scale=initial_scale,
            scale=scale,
            initial_sha256=chosen["initial_sha256"],
            frozen_parameter_sha256=frozen,
            reload_max_error=0,
            phase_fits=5,
            charged_starts=4,
            seconds=time.monotonic() - start,
            peak_rss_bytes=b.memory(),
            optimizer_fresh=True,
        )
        b.write(dest / "result.json", result, new=True)
        event(out, year, lam, "COMPLETED", result)
        del inner, refit, model, opt, reloaded
        gc.collect()
    except BaseException as exc:
        event(out, year, current, "FAILED", dict(error=repr(exc), retry=False))
        raise


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
        raise SystemExit("NO_RETRY: started namespace; use --report")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    grid, rows, plans, protocol = preflight(out)
    if not args.run:
        return
    (out / ".gitignore").write_text("*.pt\n*.parquet\n")
    c, r = b.source_components(grid, rows)
    # Recheck exact eight phase-prefix recipes/scales before the first neural start.
    parity = []
    for fold in protocol["folds"]:
        y = fold["year"]
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            cutoff = fold["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(grid, rows, cutoff), cutoff, approved=True
            )
            assert recipe == b.read(o1.OUT / f"F{y % 100}/{phase}_recipe.json")
            ix = plans[y][role]
            w = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(r[ix]).ravel(), 0.5, w), 1e-8)
            assert scale == fold["phases"][phase]["scale"]
            parity.append(dict(year=y, phase=phase, scale=scale, exact=True))
    b.write(out / "phase_parity.json", dict(status="PASS_ALL_EIGHT", checks=parity), new=True)
    for fold in protocol["folds"]:
        y = fold["year"]
        run_fold(out, y, c, rows, r, plans[y], fold)
        b.write(
            out / "continuation.json",
            dict(
                completed_years=list(range(2021, y + 1)),
                pending_years=list(range(y + 1, 2025)),
                retry=False,
            ),
        )
        report(out)


def paired_months(months: dict[int, pd.DataFrame]) -> list[dict]:
    """Existing month-block convention, retaining conditional weight denominators.

    Full-panel session mass is constant: this reduces to the historical routine.
    For conditional cohorts, resample month numerator and mass together instead
    of silently giving low-coverage sessions the same mass as full ones.
    """
    records = []
    eq_draws = []
    eq_means = []
    eq_rng = np.random.default_rng(22042)
    for year, g in months.items():
        bins = g.groupby(g.index.astype(str).str[:7]).sum()

        def draws(rng: np.random.Generator) -> np.ndarray:
            ix = rng.integers(len(bins), size=(400, len(bins)))
            return bins.numerator.to_numpy()[ix].sum(1) / bins.mass.to_numpy()[ix].sum(1)

        samples = draws(np.random.default_rng(22042))
        lo, hi = np.quantile(samples, [0.025, 0.975])
        mean = float(g.numerator.sum() / g.mass.sum())
        records.append(dict(year=str(year), delta=mean, low=float(lo), high=float(hi)))
        eq_draws.append(draws(eq_rng))
        eq_means.append(mean)
    if len(months) == 4:
        lo, hi = np.quantile(np.mean(eq_draws, axis=0), [0.025, 0.975])
        records.append(
            dict(year="EQ", delta=float(np.mean(eq_means)), low=float(lo), high=float(hi))
        )
    return records


def report(out: Path) -> None:
    """Saved selected-score comparisons only; no model calls or new fitting."""
    protocol = b.read(out / "protocol.json")
    for path, sha in protocol["preservation_bindings"].items():
        assert b.digest(Path(path)) == sha, path
    completed = [y for y in b.YEARS if (out / f"F{y % 100}/result.json").exists()]
    if not completed:
        return
    records = []
    groups = []
    frames = {}
    selections = []
    fits = []
    coefficients = []
    archived = pd.read_csv(c3.OUT / "metrics.csv", dtype={"year": str})
    for y in completed:
        dest = out / f"F{y % 100}"
        receipt = b.read(dest / "result.json")
        fits.append(receipt)
        coef = b.read(dest / "coefficients.json")
        coefficients.append(coef)
        selections.append(pd.read_csv(dest / "selection.csv"))
        f = pd.read_parquet(c3.root(y) / "oos_scores.parquet")
        c3.validate_panel(f, set(protocol["early_close_dates"]))
        new = pd.read_parquet(dest / "oos_scores.parquet")
        mask = f.category.eq(NIGHT)
        pd.testing.assert_frame_equal(
            f.loc[mask, [*c3.META, "A"]].reset_index(drop=True),
            new[[*c3.META, "A"]],
            check_dtype=False,
        )
        f["C3"] = frozen_c3(f, y)
        o = pd.read_parquet(
            o1.OUT / f"F{y % 100}/oos_scores.parquet", columns=["origin_id", "ticker", "O1"]
        )
        np.testing.assert_array_equal(f[["origin_id", "ticker"]], o[["origin_id", "ticker"]])
        f["O1"] = o.O1
        for arm, newarm in [("ROUTE-RAW", "N-RAW"), ("ROUTE-SMEAR", "N-SMEAR")]:
            candidate = f.C3.to_numpy(copy=True)
            candidate[mask] = new[newarm]
            f[arm] = route(f.C3.to_numpy(), candidate, f.category.to_numpy())
            np.testing.assert_array_equal(f.loc[~mask, arm], f.loc[~mask, "C3"])
        old = c3.decode(f.Mhat.to_numpy(), coef["scale"], coef["old_c_N"])
        f["OLD-N-SMEAR-MATCHED"] = route(f.C3.to_numpy(), old, f.category.to_numpy())
        for key, value in {**b.metrics(f, "C3"), **b.rank_metrics(f, "C3")}.items():
            expected = archived.loc[archived.year.eq(str(y)) & archived.arm.eq(c3.ARM), key].iloc[0]
            np.testing.assert_allclose(value, expected, atol=1e-14, rtol=1e-13)
        frames[y] = f
        for scope, part in [("FULL", f), ("OVERNIGHT", f.loc[mask])]:
            for arm in ARMS:
                records.append(
                    dict(
                        year=str(y),
                        scope=scope,
                        arm=arm,
                        **b.metrics(part, arm),
                        **b.rank_metrics(part, arm),
                    )
                )
        cuts = np.unique(
            [b.quantile(f.C3.to_numpy(), q, f.weight.to_numpy()) for q in np.arange(0.1, 1, 0.1)]
        )
        bins = np.searchsorted(cuts, f.C3, side="left") + 1
        masks = [("category", str(v), f.category.eq(v)) for v in c3.GROUPS]
        masks += [("slot", str(v), f.slot.eq(v)) for v in b.SLOTS]
        masks += [
            ("early_close", str(v), f.session_date_et.isin(protocol["early_close_dates"]).eq(v))
            for v in [True, False]
        ]
        threshold = next(v for v in protocol["folds"] if v["year"] == y)["thresholds"]
        for level in [95, 99]:
            event_mask = f.A.gt(threshold[str(level)])
            for category, cm in [
                ("ALL", pd.Series(True, index=f.index)),
                (NIGHT, mask),
                ("INTRADAY", ~mask),
            ]:
                masks += [
                    (f"tail_{category}", f"PREFIX{level}", event_mask & cm),
                    (f"tail_{category}", f"LE_PREFIX{level}", ~event_mask & cm),
                ]
        masks += [
            ("C3_decile", str(v), pd.Series(bins == v, index=f.index)) for v in np.unique(bins)
        ]
        masks += [
            ("N_C3_decile", str(v), pd.Series(bins == v, index=f.index) & mask)
            for v in np.unique(bins)
        ]
        for arm in [*NEW, "C3", "M1", "C0", "B0-VOL"]:
            total = b.metrics(f, arm)["raw_MSE"]
            low = f.groupby("origin_id")[arm].rank(method="average").le(10.5)
            for field, label, take in masks:
                h = f.loc[take]
                if h.empty:
                    continue
                contribution = float((h.weight * (h[arm] - h.A) ** 2).sum())
                groups.append(
                    dict(
                        year=str(y),
                        arm=arm,
                        field=field,
                        group=label,
                        **b.metrics(h, arm),
                        weight_mass=float(h.weight.sum()),
                        n_eff=c3.effective_sessions(h),
                        raw_MSE_contribution=contribution,
                        raw_MSE_loss_share=contribution / total,
                        false_low_rank=float(np.average(low.loc[take], weights=h.weight)),
                        C3_min=float(h.C3.min()),
                        C3_max=float(h.C3.max()),
                    )
                )
    m = pd.DataFrame(records)
    g = pd.DataFrame(groups)
    if len(completed) == 4:
        eq = []
        for (scope, arm), h in m.groupby(["scope", "arm"], sort=False):
            numeric = [
                k
                for k in h.columns
                if k not in ["year", "scope", "arm", "rows", "origins", "sessions", "ratio"]
            ]
            val = {k: float(h[k].mean()) for k in numeric}
            eq.append(
                dict(
                    year="EQ",
                    scope=scope,
                    arm=arm,
                    rows=int(h.rows.sum()),
                    origins=int(h.origins.sum()),
                    sessions=int(h.sessions.sum()),
                    ratio=val["predicted"] / val["observed"],
                    **val,
                )
            )
        m = pd.concat([m, pd.DataFrame(eq)], ignore_index=True)
        eq = []
        for (arm, field, label), h in g.groupby(["arm", "field", "group"], sort=False):
            if len(h) != 4:
                continue
            numeric = [
                "observed",
                "predicted",
                "bias",
                "raw_MSE",
                "raw_MAE",
                "weight_mass",
                "raw_MSE_contribution",
                "false_low_rank",
            ]
            val = {k: float(h[k].mean()) for k in numeric}
            total = float(
                m.loc[m.year.eq("EQ") & m.scope.eq("FULL") & m.arm.eq(str(arm)), "raw_MSE"].iloc[0]
            )
            eq.append(
                dict(
                    year="EQ",
                    arm=arm,
                    field=field,
                    group=label,
                    rows=int(h.rows.sum()),
                    origins=int(h.origins.sum()),
                    sessions=int(h.sessions.sum()),
                    ratio=val["predicted"] / val["observed"],
                    raw_MSE_loss_share=val["raw_MSE_contribution"] / total,
                    **val,
                )
            )
        g = pd.concat([g, pd.DataFrame(eq)], ignore_index=True)
    pairs = []
    for scope, left, right in [
        ("FULL", "ROUTE-SMEAR", "C3"),
        ("FULL", "ROUTE-SMEAR", "M1"),
        ("FULL", "ROUTE-SMEAR", "B0-VOL"),
        ("OVERNIGHT", "ROUTE-SMEAR", "C3"),
        ("OVERNIGHT", "ROUTE-SMEAR", "M1"),
        ("OVERNIGHT", "ROUTE-SMEAR", "OLD-N-SMEAR-MATCHED"),
        ("OVERNIGHT", "ROUTE-RAW", "C0"),
    ]:
        months = {}
        for y, f in frames.items():
            h = f if scope == "FULL" else f.loc[f.category.eq(NIGHT)]
            months[y] = (
                pd.DataFrame(
                    dict(
                        day=h.session_date_et,
                        numerator=h.weight * ((h[left] - h.A) ** 2 - (h[right] - h.A) ** 2),
                        mass=h.weight,
                    )
                )
                .groupby("day")
                .sum()
            )
        for result in paired_months(months):
            year = result["year"]
            reference = float(
                m.loc[m.year.eq(year) & m.scope.eq(scope) & m.arm.eq(right), "raw_MSE"].iloc[0]
            )
            delta = (
                float(
                    m.loc[m.year.eq(year) & m.scope.eq(scope) & m.arm.eq(left), "raw_MSE"].iloc[0]
                )
                - reference
            )
            np.testing.assert_allclose(delta, result["delta"], atol=1e-15, rtol=1e-10)
            pairs.append(
                dict(
                    scope=scope,
                    left=left,
                    right=right,
                    **result,
                    percent=100 * delta / reference,
                    includes_zero=result["low"] <= 0 <= result["high"],
                )
            )
    paired = pd.DataFrame(pairs)
    pd.concat(selections).to_csv(out / "selection.csv", index=False)
    pd.DataFrame(fits).to_csv(out / "fit_summary.csv", index=False)
    pd.DataFrame(coefficients).to_csv(out / "calibration_coefficients.csv", index=False)
    m.to_csv(out / "annual_and_equal_year_metrics.csv", index=False)
    g.to_csv(out / "conditional_groups.csv", index=False)
    paired.to_csv(out / "paired_mse.csv", index=False)
    verify = dict(
        status="COMPLETE" if len(completed) == 4 else "PARTIAL",
        completed=completed,
        intraday_bit_identical=True,
        old_C3_metrics_reproduced=True,
        unselected_oos_predictions=0,
        source_bindings_unchanged=True,
        ledger_after=138 + 4 * len(completed),
        resources=b.resources(out),
    )
    b.write(out / "verification.json", verify)
    notes = b.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    view = m.loc[m.year.eq("EQ")] if len(completed) == 4 else m
    annual = m.loc[
        ~m.year.eq("EQ") & m.arm.isin(["ROUTE-SMEAR", "C3", "M1", "OLD-N-SMEAR-MATCHED"])
    ]
    parts = [
        "# S2-A / S2-E overnight specialization",
        (
            f"**Status: {verify['status']} — {len(completed)}/4 folds.** "
            "Exploratory/post-search research, not independent confirmation."
        ),
        notes.get(
            "executive", "Scientific verdict follows the frozen selected-model evidence below."
        ),
        "## Frozen experiment and preflight",
        (
            "Same FT16 48×16 own-stock input, 20-stock tensor axis, one-layer H32 "
            "LSTM/final-hidden dropout0.10/scalar M head,6,433 parameters, seed42, "
            "CPU float32. Same raw A=|log(Pendpoint/Porigin)| and M=log1p(A/s); no "
            "input step or origin is removed. Saved calendar/endpoint categories "
            "govern early-close morning exceptions. Price-only labels start before "
            "approximate origin+2-minute issuance; no executable-return claim."
        ),
        (
            "Design A initial/selector/September-refit/Oct–Dec calibration/OOS "
            "indices exactly match Session2B/3. Eight phase recipes and positive "
            "left-median target scales reproduce before any start. No Oct–Dec label"
            " enters optimizer/epoch/lambda/scale fitting. No2025/2026 numerical "
            "access, hash, source scan, download or minute rebuild. Preflight reads"
            " OOS keys/predictors but not outcomes. Allowed hourly partitions match"
            " the original174-partition read receipt2010-07–2024-12."
        ),
        (
            "Training L_N + lambda L_D uses separate equal "
            "category-session/origin/20-stock means. Full-prefix conditional origin"
            " weights are multiplied by all-role-session-count / "
            "minibatch-session-count. Thus a missing category contributes zero and "
            "the batch-session-weighted mean of fixed-model batch losses exactly "
            "equals the declared population objective. Global group denominators do"
            " not depend on a batch's category mix. AdamW/clip/session shuffle are "
            "unchanged. Selector overnight transformed MSE uses "
            "min12/patience10/max60 and0.999 qualification; selected checkpoints "
            "compete on initial-scale raw overnight MSE; exact ties prefer larger "
            "lambda. Dual selector reuse introduces selection optimism."
        ),
        b.markdown(
            pd.DataFrame(b.read(out / "preflight.json")["counts"])[
                ["year", "role", "group", "sessions", "origins", "rows", "conditional_weight_sum"]
            ]
        ),
        "## Candidate selection and fits",
        b.markdown(
            pd.concat(selections)[
                [
                    "year",
                    "lambda",
                    "selector_epochs",
                    "selected_epoch",
                    "selector_transformed_MSE",
                    "selector_raw_MSE",
                    "raw_minimum_epoch",
                    "chosen",
                    "raw_tie",
                ]
            ]
        ),
        b.markdown(
            pd.DataFrame(fits)[
                [
                    "year",
                    "lambda",
                    "selected_epoch",
                    "initial_scale",
                    "scale",
                    "seconds",
                    "peak_rss_bytes",
                    "phase_fits",
                    "charged_starts",
                ]
            ]
        ),
        (
            "Four independent initial candidates plus exactly one fresh selected "
            "refit per completed year. No warm start or unselected OOS inference. "
            "Each candidate is one charged start; the selected candidate's refit is"
            " part of the same ledger pair. Maximum16 starts and20 phase fits, "
            "not20 ledger pairs. Selected checkpoint is reloaded for exact "
            "prediction equality; the same frozen model/scale produces calibration "
            "and OOS forecasts."
        ),
        "## Calibration and attribution",
        b.markdown(
            pd.DataFrame(coefficients)[
                [
                    "year",
                    "c_N",
                    "old_c_N",
                    "sessions",
                    "origins",
                    "rows",
                    "n_eff",
                    "q_max",
                    "top10_share",
                    "top1pct_share",
                ]
            ]
        ),
        (
            "One predefined overnight smear per selected model, plus the identical "
            "operation on saved old C0. Both use original calibration row weights "
            "restricted to overnight and normalized, and the same September scale. "
            "No partial pooling, multiplier choice, trimming or OOS repair. N-RAW "
            "remains the historical inverse. ROUTE-RAW/ROUTE-SMEAR denote "
            "N-RAW/N-SMEAR in the OVERNIGHT rows; full rows hard-route frozen C3 "
            "intraday. OLD-N-SMEAR-MATCHED full rows also retain C3 intraday; its "
            "scientific role is the overnight matched-calibration control. F24 has "
            "limited calibration-tail precision."
        ),
        "## Annual and equal-year matched scores",
        b.markdown(annual[["year", "scope", "arm", "raw_MSE", "raw_MAE", "ratio", "magnitude_IC"]]),
        "All arms, including raw routed, O1 and the four B0 controls:",
        b.markdown(
            view[
                [
                    "year",
                    "scope",
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
            "Raw MSE is in squared log-return units; MAE/means/bias in absolute "
            "log-return units. Full-panel weights are unchanged, never50/50 by "
            "category. Conditional raw scores restrict and renormalize canonical "
            "weights within year. Ranking uses existing within-origin "
            "midrank→group-session→year reducer. EQ averages annual metrics and "
            "uses the ratio of equal-year means. No four-year value is produced "
            "before four valid folds."
        ),
        "## Paired uncertainty",
        b.markdown(paired),
        (
            "400 whole-month draws, seed22042, year-stratified EQ; full "
            "stocks/origins/sessions remain together. The existing month-bootstrap "
            "construction is extended only to retain group weight numerator and "
            "mass together, avoiding incorrect equal weighting of low-coverage "
            "category sessions. Full-panel results reduce to the old convention. "
            "Intervals are descriptive, conditional on selected networks and "
            "scalars; lambda/epoch selection and calibration uncertainty are not "
            "propagated or selection-adjusted."
        ),
        "## Clocks, ordinary periods, tails and magnitude ordering",
        notes.get(
            "groups",
            (
                "See conditional_groups.csv for seven slots, scheduled early-close "
                "exceptions, category-specific prefix95/99 cohorts/complements and "
                "common saved-C3 deciles."
            ),
        ),
        b.markdown(
            g.loc[
                g.year.eq("EQ")
                & g.arm.eq("ROUTE-SMEAR")
                & g.field.isin(["category", "slot", "tail_OVERNIGHT"]),
                [
                    "field",
                    "group",
                    "rows",
                    "sessions",
                    "raw_MSE",
                    "raw_MAE",
                    "ratio",
                    "raw_MSE_loss_share",
                    "false_low_rank",
                ],
            ]
        ),
        b.markdown(
            view.loc[
                view.arm.isin([*NEW, "C3", "M1", "C0"]),
                [
                    "scope",
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
            "Prefix95/99 thresholds are unchanged September-prefix quantiles. Tail "
            "loss shares are unconditional contributions to the full routed score; "
            "conditional tables normalize their own mass. False-low means "
            "within-origin average rank≤10.5; denominator is the declared cohort's "
            "original weight. These outcome-selected cohorts are retrospective, not"
            " calibrated event probabilities. Shared reliability memberships are "
            "ten saved-C3 weighted deciles per year, with separate overnight rows; "
            "no bin is fitted into a correction. Pair ties get half credit; true "
            "ties are excluded; retrieval uses fractional boundary ties. New night "
            "weights may change stock ordering, unlike scalar-only calibration."
        ),
        "## Scientific decision",
        notes.get(
            "decision",
            (
                "No next experiment is launched. Review network versus old matched "
                "calibration, not just versus C3 amplitude."
            ),
        ),
        "## Reproduction, integrity and stop",
        (
            "`.venv/bin/python -m lstm_data.hf20_overnight_specialist --preflight`;"
            " initial `--run` executes only this frozen campaign; `--report` "
            "replays completed saved selected scores without inference/refitting. "
            "Started namespaces cannot be rerun. Source inputs/old predictors are "
            "referenced, never copied; only selected new night scores and one final"
            " checkpoint per year are saved. Protocol contains source/recipe/role "
            "bindings and resource caps; selection/training traces contain no "
            "unselected OOS scores."
        ),
        notes.get(
            "verification",
            "Focused tests and repository static-check results are recorded in the Codex handoff.",
        ),
        (
            "STOP. No S2-B/C/D, event head, alternate seed/lambda, new jump target,"
            " trade/options analysis or protected confirmation."
        ),
    ]
    (out / "S2A_S2E_OVERNIGHT_SPECIALIZATION_REPORT.md").write_text("\n\n".join(parts) + "\n")


if __name__ == "__main__":
    main()
