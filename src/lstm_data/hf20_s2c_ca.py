"One prospective C-A masked auxiliary experiment; original full four-hour task."

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
from torch import nn

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_mag_o1 as o1
from . import hf20_overnight_specialist as prior
from . import hf20_stage2_bcd as clock
from .hf20_s4_clock import sessions
from .neural_engine import seed_all

OUT = Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28")
AUDIT = Path(("reports/experiments/hf20_s9_mag_stage2_s2c_s2d_readonly_coverage_audit_2026-10-28"))
COMPONENTS = ("origin_to_close", "close_to_next_open", "next_open_to_exit")
RAW = "S2C-RAW"
CAL = "S2C-C3"


class ComponentMAG(clock.ClockMAG):
    "Identical seeded S2-B trunk/main head, three independent linear aux rows."

    def __init__(self) -> None:
        super().__init__()
        self.auxiliary = nn.Linear(42, 3)

    def all_heads(self, x: torch.Tensor, known: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if known.shape != (len(x), 10) or not bool(torch.isfinite(known).all()):
            raise ValueError("TEN_CAUSAL_CLOCK_VALUES_REQUIRED")
        representation = torch.cat([self.dropout(self.encode(x)), known], dim=1)
        return self.head(representation).squeeze(-1), self.auxiliary(representation)


def model_for_components() -> ComponentMAG:
    """Fresh seed/optimizer per phase, with unchanged main initialization."""
    seed_all(42)
    model = ComponentMAG().float()
    assert sum(p.numel() for p in model.parameters()) == 6572
    return model


def phase_aux_weights(
    rows: pd.DataFrame, pos: np.ndarray, mask: np.ndarray
) -> tuple[np.ndarray, dict]:
    """Global masked overnight hierarchy; never normalize within a minibatch."""
    g = rows.iloc[pos]
    night = g.category.eq("OVERNIGHT").to_numpy()
    if not night.any():
        raise ValueError("EMPTY_OVERNIGHT_PHASE")
    w = np.zeros((len(rows), 20), dtype=np.float64)
    w[pos[night]] = np.repeat(
        (b.origin_weights(g.loc[night, "session_date_et"].to_numpy()) / 20)[:, None], 20, axis=1
    )
    w *= mask
    mass = float(w.sum())
    if not np.isfinite(mass) or mass <= 0:
        raise ValueError("EMPTY_OR_NONFINITE_AUX_PHASE")
    w /= mass
    return w, dict(
        phase_sessions=g.session_date_et.nunique(),
        overnight_sessions=g.loc[night, "session_date_et"].nunique(),
        overnight_origins=int(night.sum()),
        supported_cells=int(mask[pos].sum()),
        global_masked_base_mass=mass,
        normalized_aux_mass=float(w.sum()),
    )


def masked_aux_loss(
    normalized_prediction: torch.Tensor,
    signed_labels: torch.Tensor,
    mask: torch.Tensor,
    global_weights: torch.Tensor,
    scale: float,
    sampling_multiplier: float,
) -> torch.Tensor:
    "Mean of three signed normalized risks; missing labels never enter arithmetic."
    assert normalized_prediction.shape == signed_labels.shape == (*mask.shape, 3)
    assert global_weights.shape == mask.shape and scale > 0
    if not bool(mask.any()):
        return normalized_prediction.sum() * 0
    error = normalized_prediction[mask] - signed_labels[mask] / scale
    return (error.square() * global_weights[mask, None]).sum() * (sampling_multiplier / 3)


def preflight(
    out: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict, np.ndarray, np.ndarray, np.ndarray]:
    """All four folds, source/action/identity and original keys before any fit."""
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*.pt\n*.parquet\n")
    pointer = b.read(b.POINTER)
    oldjournal = Path(pointer["real_journal"])
    last = json.loads(oldjournal.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 158
    assert pointer["effective_ceiling"] == 300 and 158 + 4 <= 300
    assert oldjournal == clock.OUT / "neural_starts.jsonl"
    bind = [
        oldjournal,
        clock.TARGET,
        o1.OUT / "role_indices.npz",
        AUDIT / "S2C_ROLE_SUMMARY.csv",
        clock.OUT / "s2c_decomposition/protocol.json",
        clock.OUT / "s2b_clock/protocol.json",
        clock.OUT / "planning_receipt_v2.json",
        b.S4 / "opening_reaudit_v2/S4_SOURCE_POLICY.json",
        b.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv",
    ]
    protocol = dict(
        kind="S2C_CA_PROSPECTIVE_AMENDMENT_V1",
        seed=42,
        parameters=6572,
        main=("original complete20 240-XNYS-minute absolute endpoint magnitude; transformed M MSE"),
        mask="one common complete-triple stock mask; no C-B or reconstructed components",
        auxiliary="normalized signed linear heads; L=main+.10*(pre+gap+post)/3",
        auxiliary_weights=(
            "overnight session/origin/20 fixed weights times mask/global phase masked"
            " mass; batch factor S_phase/B_batch"
        ),
        selector="main unrestricted M loss only; .999 qualified best; min12 patience10 max60",
        calibration=(
            "own frozen September encoder; own Oct-Dec C3 IO kappa25; calibrated "
            "primary, raw diagnostic"
        ),
        source_stop="2024-12-31",
        no_2025_2026_market_access=True,
        clock_contract=b.read(clock.OUT / "s2b_clock/protocol.json")["clock"],
        previous_pointer=pointer,
        ledger_before=158,
        ceiling=300,
        max_charged_starts=4,
        max_phase_fits=8,
        preservation_bindings={str(p): b.digest(p) for p in bind},
        blocked_original_not_overwritten=True,
        no_S2D_or_deferred_route=True,
        uncertainty=dict(draws=400, seed=22042, unit="whole months within years; equal years"),
    )
    clock.freeze(out / "S2C_CA_PROTOCOL.json", protocol)
    grid, rows = b.metadata()
    plans = clock.saved_plans(rows)
    calendar = sessions("2010-07-01", "2025-01-10")
    clocks, following = clock.clock_values(rows, calendar)
    first = np.full(len(rows), "0000", dtype=object)
    good = rows.first_step.ge(0)
    first[good] = grid.session_date_et.to_numpy()[rows.loc[good, "first_step"].to_numpy(int)]
    f = pd.read_parquet(clock.TARGET)
    np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.origin_id)
    assert f.ticker.tolist() == list(b.SYMBOLS) * len(rows)
    assert not f[["origin_id", "ticker"]].duplicated().any()
    r = f.direct_return.to_numpy().reshape(-1, 20)
    labels = f[list(COMPONENTS)].to_numpy().reshape(-1, 20, 3)
    mask = f.decomposition_supported.to_numpy().reshape(-1, 20)
    assert not mask[rows.category.eq("INTRADAY")].any()
    assert np.array_equal(np.isfinite(labels).all(2), mask)
    maximum = 0.0
    # Only supported source prices are examined; no proxy/repair or new minute IO.
    for name in [
        "entry_source_price",
        "exit_source_price",
        "genuine_session_end_price",
        "next_session_open",
    ]:
        values = f[name].to_numpy().reshape(-1, 20)[mask]
        assert np.isfinite(values).all() and (values > 0).all()
    total = r[mask]
    summed = labels[mask].sum(1)
    np.testing.assert_allclose(summed, total, atol=1e-12, rtol=1e-11)
    maximum = float(np.max(abs(summed - total)))
    endpoints = rows.exit_end_utc.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
    nextdays = (
        pd.to_datetime(following, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.strftime("%Y-%m-%d")
    )
    any_supported = mask.any(1)
    assert endpoints[any_supported].eq(nextdays[any_supported]).all()
    cop = b.SYMBOLS.index("COP")
    assert not mask[rows.session_date_et.lt("2012-05-01").ne(endpoints.lt("2012-05-01")), cop].any()
    oldcounts = pd.read_csv(o1.REF / "role_counts.csv")
    audited = pd.read_csv(AUDIT / "S2C_ROLE_SUMMARY.csv")
    coverage = []
    keybindings = {}
    for y in b.YEARS:
        for role, ix in plans[y].items():
            item = oldcounts.loc[oldcounts.year.eq(y) & oldcounts.role.eq(role)].iloc[0]
            expected = np.flatnonzero(
                b.role_mask(rows, first, item.start, item.cutoff, item.embargo_after)
            )
            np.testing.assert_array_equal(ix, expected)
            assert rows.iloc[ix].entry_index.sub(rows.iloc[ix].first_step).eq(47).all()
            assert np.isfinite(r[ix]).all() and rows.iloc[ix].trading_minutes.eq(240).all()
            a = audited.loc[audited.fold.eq(y) & audited.role.eq(role)].iloc[0]
            night = rows.iloc[ix].category.eq("OVERNIGHT").to_numpy()
            assert int(night.sum()) == a.original_overnight_origins
            assert int(mask[ix].sum()) == a.valid_complete_triples
            assert int(mask[ix[night]].all(1).sum()) == a.all20_triple_origins
            assert mask[ix[night]].any(1).all()
            if role in ("inner_train", "restricted_refit"):
                _, summary = phase_aux_weights(rows, ix, mask)
            else:
                summary = dict(supported_cells=int(mask[ix].sum()))
            coverage.append(
                dict(
                    year=y,
                    role=role,
                    sessions=rows.iloc[ix].session_date_et.nunique(),
                    origins=len(ix),
                    rows=len(ix) * 20,
                    **{f"aux_{k}": v for k, v in summary.items()},
                )
            )
            if role == "selector":
                slots = rows.iloc[ix].slot.value_counts()
                assert rows.iloc[ix].session_date_et.nunique() >= 50 and slots.min() >= 25
            if role in ("calibration", "oos"):
                ref = pd.read_parquet(c3.root(y) / f"{role}_scores.parquet", columns=c3.META)
                new = pd.read_parquet(
                    clock.OUT / f"s2b_clock/F{y % 100}/{role}_scores.parquet", columns=c3.META
                )
                pd.testing.assert_frame_equal(ref, new)
                np.testing.assert_array_equal(ref.origin_id.iloc[::20], rows.iloc[ix].origin_id)
                assert ref.ticker.tolist() == list(b.SYMBOLS) * len(ix)
                np.testing.assert_allclose(
                    ref.weight,
                    np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20),
                    rtol=1e-13,
                    atol=1e-15,
                )
                assert not ref[["origin_id", "ticker"]].duplicated().any()
                keybindings[f"{y}_{role}"] = dict(
                    keys_sha256=__import__("hashlib")
                    .sha256(ref[["origin_id", "ticker"]].to_csv(index=False).encode())
                    .hexdigest(),
                    original=str(c3.root(y) / f"{role}_scores.parquet"),
                    clock=str(clock.OUT / f"s2b_clock/F{y % 100}/{role}_scores.parquet"),
                )
        for left, right in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(plans[y][left], plans[y][right]).size
    oo = [v for v in coverage if v["role"] == "oos"]
    assert (
        sum(v["rows"] for v in oo) == 80260
        and sum(v["origins"] for v in oo) == 4013
        and sum(v["sessions"] for v in oo) == 793
    )
    pd.DataFrame(coverage).to_csv(out / "auxiliary_coverage.csv", index=False)
    # Full stock/month/slot missingness is the unchanged audit, referenced rather than copied.
    clock.freeze(
        out / "S2C_CA_PREFLIGHT.json",
        dict(
            status="PASS_ALL_FOUR_SOURCE_KEYS_CHRONOLOGY",
            counts=coverage,
            additivity_max_error=maximum,
            key_bindings=keybindings,
            resources=b.resources(out),
            mask_concentration_reference=str(AUDIT / "S2C_MASKING_COVERAGE.csv"),
            prefit_calibration=(
                "tail category coverage verified; own residual moments must pass after "
                "checkpoint freeze"
            ),
            ledger_before=158,
            ceiling=300,
        ),
    )
    return grid, rows, plans, clocks, labels, mask


def prepare_phases(
    out: Path, c: b.Components, rows: pd.DataFrame, r: np.ndarray, plans: dict
) -> dict:
    """Independently fit legal prefix recipes/scales; verify exact S2-B parity."""
    folds = {}
    for y in b.YEARS:
        dest = out / f"F{y % 100}"
        dest.mkdir()
        old = b.read(clock.OUT / f"s2b_clock/F{y % 100}/phases.json")
        phases = {}
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            previous = old["phases"][phase]
            cutoff = previous["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(c.grid, rows, cutoff), cutoff, approved=True
            )
            assert recipe == b.read(Path(previous["recipe_reference"]))
            ix = plans[y][role]
            weights = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(r[ix]).ravel(), 0.5, weights), 1e-8)
            assert scale == previous["scale"]
            phases[phase] = dict(
                scale=scale, cutoff=cutoff, recipe_reference=previous["recipe_reference"]
            )
        folds[y] = dict(year=y, phases=phases, thresholds=old["thresholds"])
        clock.freeze(dest / "phases.json", folds[y])
    clock.freeze(out / "phase_parity.json", dict(status="ALL_EIGHT_EXACT", folds=folds))
    return folds


def journal(out: Path, y: int, status: str, detail: dict) -> None:
    """One charged selector/refit pair per year; append only, no retries."""
    protocol = b.read(out / "S2C_CA_PROTOCOL.json")
    path = out / "neural_starts.jsonl"
    history = [json.loads(v) for v in path.read_text().splitlines()] if path.exists() else []
    starts = sum(v["status"] == "STARTED" for v in history)
    pointer = b.read(b.POINTER)
    if not history:
        assert pointer == protocol["previous_pointer"]
    else:
        assert pointer["real_journal"] == str(path)
    if status == "STARTED":
        assert (
            starts < 4
            and y == b.YEARS[starts]
            and (not history or history[-1]["status"] == "COMPLETED")
        )
        assert b.read(out / "readiness.json")["status"] == "PASS"
        b.resources(out)
    record = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        experiment="S2C-CA",
        year=y,
        status=status,
        global_started_pairs=158 + starts + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
    )
    with path.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    binding = dict(
        path=str(out / "S2C_CA_PROTOCOL.json"), sha256=b.digest(out / "S2C_CA_PROTOCOL.json")
    )
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=30,
            definition=binding,
            plan=binding,
            real_journal=str(path),
            previous_journal=dict(
                path=protocol["previous_pointer"]["real_journal"],
                sha256=protocol["preservation_bindings"][
                    protocol["previous_pointer"]["real_journal"]
                ],
            ),
            fit_permission=False,
        ),
    )


def train_epoch(
    view: b.View,
    pos: np.ndarray,
    model: ComponentMAG,
    opt: torch.optim.AdamW,
    epoch: int,
    clocks: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray,
    auxweights: np.ndarray,
    phase_sessions: int,
) -> dict:
    "Uniform complete-session sampling implements global auxiliary normalization."
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + epoch).shuffle(days)
    norms = []
    main_values = []
    aux_values = []
    model.train()
    for k in range(0, len(days), 16):
        batchdays = days[k : k + 16]
        ix = pos[np.concatenate([groups[d] for d in batchdays])]
        x = view.x(ix)
        assert x.shape[1:] == (20, 48, 16)
        opt.zero_grad()
        main, aux = model.all_heads(
            torch.from_numpy(x.reshape(-1, 48, 16)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
        )
        main = main.reshape(-1, 20)
        aux = aux.reshape(-1, 20, 3)
        mloss = prior.weighted_loss(
            main,
            torch.from_numpy(view.r[ix].astype(np.float32)),
            view.scale,
            b.origin_weights(view.rows.iloc[ix].session_date_et.to_numpy()),
        )
        aloss = masked_aux_loss(
            aux,
            torch.from_numpy(labels[ix].astype(np.float32)),
            torch.from_numpy(mask[ix]),
            torch.from_numpy(auxweights[ix].astype(np.float32)),
            view.scale,
            phase_sessions / len(batchdays),
        )
        loss = mloss + 0.10 * aloss
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_MAIN_OR_AUX_LOSS")
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True)
        norms.append(float(norm))
        main_values.append(float(mloss.detach()))
        aux_values.append(float(aloss.detach()))
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms),
        gradient_norm_max=max(norms),
        clipped_batches=sum(v > 1 for v in norms),
        batch_main_mean=float(np.mean(main_values)),
        batch_aux_three_head_mean=float(np.mean(aux_values)),
    )


def predict_all(
    view: b.View, pos: np.ndarray, model: ComponentMAG, clocks: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    "Post-fit signed-head diagnostics on the same already selected checkpoint."
    model.eval()
    main = []
    aux = []
    with torch.inference_mode():
        for k in range(0, len(pos), 32):
            ix = pos[k : k + 32]
            m, u = model.all_heads(
                torch.from_numpy(view.x(ix).reshape(-1, 48, 16)),
                torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
            )
            main.append(m.numpy().reshape(-1, 20))
            aux.append(u.numpy().reshape(-1, 20, 3) * view.scale)
    return np.concatenate(main), np.concatenate(aux)


def run_fold(
    out: Path,
    y: int,
    c: b.Components,
    rows: pd.DataFrame,
    r: np.ndarray,
    pos: dict,
    fold: dict,
    clocks: np.ndarray,
    labels: np.ndarray,
    mask: np.ndarray,
) -> None:
    dest = out / f"F{y % 100}"
    started = time.monotonic()
    trace = []
    initial = fold["phases"]["initial"]
    restricted = fold["phases"]["restricted"]
    inner = b.View(c, rows, r, b.read(Path(initial["recipe_reference"])), initial["scale"])
    model = model_for_components()
    initsha = b.initial_hash(model)
    opt = b.optimizer(model)
    assert not opt.state
    weights, auxreceipt = phase_aux_weights(rows, pos["inner_train"], mask)
    selector = b.Selector()
    best = {}
    journal(
        out,
        y,
        "STARTED",
        dict(run_id=f"HF20-S2C-CA-F{y % 100}-S42", phase="initial", parameters=6572),
    )
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            tick = time.monotonic()
            train = train_epoch(
                inner,
                pos["inner_train"],
                model,
                opt,
                n,
                clocks,
                labels,
                mask,
                weights,
                auxreceipt["phase_sessions"],
            )
            z = clock.predict_clock(inner, pos["selector"], model, clocks)
            target = torch.log1p(
                torch.from_numpy(r[pos["selector"]].astype(np.float32)).abs() / initial["scale"]
            ).numpy()
            val = float(
                b.origin_weights(rows.iloc[pos["selector"]].session_date_et.to_numpy())
                @ ((z - target) ** 2).mean(1)
            )
            if selector.observe(val):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_main_M_MSE=val,
                    selected=selector.selected,
                    seconds=time.monotonic() - tick,
                    **train,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2C-CA", y, "selector", n, val, "selected", selector.selected, flush=True)
        model.load_state_dict(best)
        clock.freeze(
            dest / "selection.json",
            dict(
                vars(selector),
                initial_scale=initial["scale"],
                selected_initial_sha256=b.initial_hash(model),
                auxiliary_normalization=auxreceipt,
            ),
        )
        journal(
            out, y, "SELECTED", dict(epoch=selector.selected, raw_minimum_epoch=selector.raw_epoch)
        )
        del model, opt, best
        gc.collect()
        refit = b.View(
            c, rows, r, b.read(Path(restricted["recipe_reference"])), restricted["scale"]
        )
        model = model_for_components()
        assert b.initial_hash(model) == initsha
        opt = b.optimizer(model)
        assert not opt.state
        weights, auxreceipt = phase_aux_weights(rows, pos["restricted_refit"], mask)
        clock.freeze(dest / "aux_refit_normalization.json", auxreceipt)
        journal(out, y, "REFITTING", dict(epochs=selector.selected, cutoff=restricted["cutoff"]))
        for n in range(1, selector.selected + 1):
            tick = time.monotonic()
            train = train_epoch(
                refit,
                pos["restricted_refit"],
                model,
                opt,
                n,
                clocks,
                labels,
                mask,
                weights,
                auxreceipt["phase_sessions"],
            )
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - tick, **train))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2C-CA", y, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        zcal = clock.predict_clock(refit, pos["calibration"], model, clocks)
        cal = pd.read_parquet(c3.root(y) / "calibration_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(cal.A, abs(r[pos["calibration"]]).ravel())
        cal["Mhat"] = zcal.ravel()
        coeff = c3.fit_categories(cal, restricted["scale"])
        pd.DataFrame(coeff).to_csv(dest / "calibration_coefficients.csv", mode="x", index=False)
        cal.to_parquet(dest / "calibration_scores.parquet", index=False, compression="zstd")
        # All weights/epochs/scalars frozen before outer prediction or diagnostic scoring.
        z, aux = predict_all(refit, pos["oos"], model, clocks)
        reloaded = model_for_components()
        reloaded.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, clock.predict_clock(refit, pos["oos"], reloaded, clocks))
        assert b.initial_hash(model) == frozen
        f = pd.read_parquet(c3.root(y) / "oos_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(f.A, abs(r[pos["oos"]]).ravel())
        f["Mhat"] = z.ravel()
        f[RAW] = prior.raw_decode(z, restricted["scale"]).ravel()
        factors = {v["group"]: v["c_star"] for v in coeff}
        f[CAL] = c3.decode(z.ravel(), restricted["scale"], f.category.map(factors).to_numpy())
        f.to_parquet(dest / "oos_scores.parquet", index=False, compression="zstd")
        records = []
        oo = pos["oos"]
        for j, name in enumerate(COMPONENTS):
            for ticker in ["ALL", *b.SYMBOLS]:
                use = mask[oo].copy()
                if ticker != "ALL":
                    use[:, np.arange(20) != b.SYMBOLS.index(ticker)] = False
                a = labels[oo, :, j][use]
                p = aux[:, :, j][use]
                ww = np.repeat(f.weight.to_numpy().reshape(-1, 20), 1, axis=1)[use]
                ww /= ww.sum()
                ac = a - float(ww @ a)
                pc = p - float(ww @ p)
                denominator = float(np.sqrt((ww @ (ac * ac)) * (ww @ (pc * pc))))
                records.append(
                    dict(
                        year=y,
                        component=name,
                        ticker=ticker,
                        rows=len(a),
                        sessions=rows.iloc[oo[np.any(use, axis=1)]].session_date_et.nunique(),
                        signed_MSE=float(ww @ ((p - a) ** 2)),
                        signed_MAE=float(ww @ abs(p - a)),
                        observed_signed_mean=float(ww @ a),
                        predicted_signed_mean=float(ww @ p),
                        weighted_Pearson=float(ww @ (ac * pc) / denominator)
                        if denominator > 0
                        else None,
                    )
                )
        pd.DataFrame(records).to_csv(dest / "auxiliary_diagnostics.csv", index=False)
        result = dict(
            year=y,
            status="COMPLETED",
            run_id=f"HF20-S2C-CA-F{y % 100}-S42",
            parameters=6572,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_scale=initial["scale"],
            scale=restricted["scale"],
            initial_sha256=initsha,
            frozen_parameter_sha256=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            seconds=time.monotonic() - started,
            peak_rss_bytes=b.memory(),
        )
        clock.freeze(dest / "result.json", result)
        journal(out, y, "COMPLETED", result)
        del inner, refit, model, opt, reloaded
        gc.collect()
    except BaseException as exc:
        journal(out, y, "FAILED", dict(error=repr(exc), retry=False))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.preflight:
        preflight(OUT)
        return
    if args.report:
        report(OUT)
        return
    if not args.run:
        parser.error("choose --preflight, --run or --report")
    assert not (OUT / "neural_starts.jsonl").exists(), "SINGLE_USE_NO_RETRY"
    assert b.read(OUT / "readiness.json")["status"] == "PASS"
    grid, rows = b.metadata()
    plans = clock.saved_plans(rows)
    calendar = sessions("2010-07-01", "2025-01-10")
    clocks, _ = clock.clock_values(rows, calendar)
    f = pd.read_parquet(clock.TARGET, columns=[*COMPONENTS, "decomposition_supported"])
    labels = f[list(COMPONENTS)].to_numpy().reshape(-1, 20, 3)
    mask = f.decomposition_supported.to_numpy().reshape(-1, 20)
    c, r = b.source_components(grid, rows)
    folds = prepare_phases(OUT, c, rows, r, plans)
    for y in b.YEARS:
        run_fold(OUT, y, c, rows, r, plans[y], folds[y], clocks, labels, mask)
    report(OUT)


def report(out: Path) -> None:
    """Saved-output report; no new fit or model forward pass."""
    # Implemented before first start; this entry point never authorizes fits.
    write_report(out)


def write_report(out: Path) -> None:
    """Summarize the fixed full-panel experiment from frozen keyed outputs."""
    years = [y for y in b.YEARS if (out / f"F{y % 100}/result.json").exists()]
    if not years:
        return
    arms = [
        CAL,
        RAW,
        "CLOCK-C3",
        "CLOCK-RAW",
        "C3",
        "M1",
        "C1a",
        "C0",
        "B0-VOL",
        "B0-CLOCK",
        "B0-RMEAN",
        "B0-RMED",
        "O1",
    ]
    records = []
    groups = []
    frames = {}
    fits = []
    coefficients = []
    auxiliary = []
    for y in years:
        f = pd.read_parquet(c3.root(y) / "oos_scores.parquet")
        new = pd.read_parquet(out / f"F{y % 100}/oos_scores.parquet")
        known = pd.read_parquet(clock.OUT / f"s2b_clock/F{y % 100}/oos_scores.parquet")
        for h in [new, known]:
            pd.testing.assert_frame_equal(f[[*c3.META, "A"]], h[[*c3.META, "A"]], check_dtype=False)
        for arm in [CAL, RAW]:
            f[arm] = new[arm]
        for arm in ["CLOCK-C3", "CLOCK-RAW"]:
            f[arm] = known[arm]
        f["C3"] = prior.frozen_c3(f, y)
        oldo = pd.read_parquet(
            o1.OUT / f"F{y % 100}/oos_scores.parquet", columns=["origin_id", "ticker", "O1"]
        )
        np.testing.assert_array_equal(f[["origin_id", "ticker"]], oldo[["origin_id", "ticker"]])
        f["O1"] = oldo.O1
        frames[y] = f
        fit = b.read(out / f"F{y % 100}/result.json")
        fits.append(fit)
        coef = pd.read_csv(
            out / f"F{y % 100}/calibration_coefficients.csv", float_precision="round_trip"
        )
        coef.insert(0, "year", y)
        coefficients.append(coef)
        auxiliary.append(pd.read_csv(out / f"F{y % 100}/auxiliary_diagnostics.csv"))
        for scope, h in [
            ("FULL", f),
            ("INTRADAY", f.loc[f.category.eq("INTRADAY")]),
            ("OVERNIGHT", f.loc[f.category.eq("OVERNIGHT")]),
        ]:
            for arm in arms:
                records.append(
                    dict(
                        year=str(y),
                        scope=scope,
                        arm=arm,
                        **b.metrics(h, arm),
                        **b.rank_metrics(h, arm),
                    )
                )
        thresholds = b.read(out / f"F{y % 100}/phases.json")["thresholds"]
        cuts = np.unique(
            [b.quantile(f.C0.to_numpy(), q, f.weight.to_numpy()) for q in np.arange(0.1, 1, 0.1)]
        )
        bins = np.searchsorted(cuts, f.C0, side="left") + 1
        masks = [("slot", v, f.slot.eq(v)) for v in b.SLOTS]
        early = (
            f.entry_end_utc.dt.tz_convert("America/New_York").dt.hour * 60
            + f.entry_end_utc.dt.tz_convert("America/New_York").dt.minute
        )
        # Known calendar early-close date set; never classify by outcomes.
        cal = sessions(f"{y}-01-01", f"{y}-12-31")
        earlydays = set(
            cal.index[(cal.close - cal.open).dt.total_seconds() < 390 * 60].astype(str).str[:10]
        )
        masks += [
            ("calendar", "EARLY_CLOSE", f.session_date_et.isin(earlydays)),
            ("calendar", "NORMAL", ~f.session_date_et.isin(earlydays)),
        ]
        del early
        for scope, base in [
            ("ALL", pd.Series(True, index=f.index)),
            ("INTRADAY", f.category.eq("INTRADAY")),
            ("OVERNIGHT", f.category.eq("OVERNIGHT")),
        ]:
            for level in [95, 99]:
                event = f.A.gt(thresholds[str(level)])
                masks += [
                    (f"tail_{scope}", f"PREFIX{level}", base & event),
                    (f"tail_{scope}", f"LE_PREFIX{level}", base & ~event),
                ]
        masks += [
            ("C0_decile", str(v), pd.Series(bins == v, index=f.index)) for v in np.unique(bins)
        ]
        for arm in [CAL, RAW, "CLOCK-C3", "CLOCK-RAW", "C3", "M1", "C0", "B0-VOL", "B0-CLOCK"]:
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
                        raw_MSE_contribution=contribution,
                        raw_MSE_loss_share=contribution / total,
                        false_low_rank=float(np.average(low.loc[take], weights=h.weight)),
                        C0_min=float(h.C0.min()),
                        C0_max=float(h.C0.max()),
                    )
                )
    m = pd.DataFrame(records)
    g = pd.DataFrame(groups)
    if len(years) == 4:
        eq = []
        for (scope, arm), h in m.groupby(["scope", "arm"], sort=False):
            val = {
                k: float(h[k].mean())
                for k in h.columns
                if k not in ["year", "scope", "arm", "rows", "origins", "sessions", "ratio"]
            }
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
            val = {
                k: float(h[k].mean())
                for k in [
                    "observed",
                    "predicted",
                    "bias",
                    "raw_MSE",
                    "raw_MAE",
                    "weight_mass",
                    "raw_MSE_contribution",
                    "false_low_rank",
                ]
            }
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
    paired = []
    for scope in ["FULL", "OVERNIGHT", "INTRADAY"]:
        for ref in ["CLOCK-C3", "C3", "M1", "C0", "B0-VOL"]:
            months = {}
            for y, f in frames.items():
                h = f if scope == "FULL" else f.loc[f.category.eq(scope)]
                daily = (
                    pd.DataFrame(
                        dict(
                            day=h.session_date_et,
                            numerator=h.weight * ((h[CAL] - h.A) ** 2 - (h[ref] - h.A) ** 2),
                            mass=h.weight,
                        )
                    )
                    .groupby("day")[["numerator", "mass"]]
                    .sum()
                )
                months[y] = daily
            for row in prior.paired_months(months):
                year = row["year"]
                base = float(
                    m.loc[m.year.eq(year) & m.scope.eq(scope) & m.arm.eq(ref), "raw_MSE"].iloc[0]
                )
                paired.append(
                    dict(
                        scope=scope,
                        reference=ref,
                        **row,
                        percent_change=100 * row["delta"] / base,
                        interval_includes_zero=row["low"] <= 0 <= row["high"],
                    )
                )
    m.to_csv(out / "metrics.csv", index=False)
    g.to_csv(out / "groups.csv", index=False)
    pd.DataFrame(paired).to_csv(out / "paired_mse.csv", index=False)
    pd.DataFrame(fits).to_csv(out / "fit_summary.csv", index=False)
    pd.concat(coefficients).to_csv(out / "calibration_coefficients.csv", index=False)
    pd.concat(auxiliary).to_csv(out / "auxiliary_diagnostics.csv", index=False)
    protocol = b.read(out / "S2C_CA_PROTOCOL.json")
    for path, sha in protocol["preservation_bindings"].items():
        assert b.digest(Path(path)) == sha, path
    selected = m.loc[
        m.scope.eq("FULL"),
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
        ],
    ]
    eq = m.loc[m.year.eq("EQ") & m.scope.eq("FULL")].set_index("arm") if len(years) == 4 else None
    verdict = "PARTIAL"
    if eq is not None:
        verdict = (
            "PRIMARY_MSE_WIN_TRADEOFF_REVIEW_REQUIRED"
            if eq.loc[CAL, "raw_MSE"] < min(eq.loc["CLOCK-C3", "raw_MSE"], eq.loc["C3", "raw_MSE"])
            else "NO_INCREMENTAL_PRIMARY_EVIDENCE_RETAIN_CLOCK_C3"
        )
    notes = b.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    sections = [
        "# S2-C C-A masked signed decomposition-assisted four-hour MAG",
        (
            f"**Status: {'COMPLETE' if len(years) == 4 else 'PARTIAL'} — {len(years)}/4 folds.** "
            f"Exploratory/post-search. Verdict: **{verdict}**."
        ),
        notes.get(
            "executive",
            (
                "Primary result is the matched raw-MSE comparison below; no automatic "
                "next experiment."
            ),
        ),
        "## Frozen design and primary cohort",
        (
            "Same20-name panel,48 completed scheduled-hour FT16×16 own-stock inputs, "
            "one-layerH32, final hidden dropout.10,10 fixed S2-B clock values and "
            "identical primary head initialization. Three signed linear aux rows "
            "add129 parameters:6572 total. Head outputs u represent Rhat=s*u. No "
            "future labels or availability flag enters inputs. Main loss remains "
            "complete-panel transformed M MSE; selector monitors only it. Aux "
            "objective is .10 times mean of the three global normalized masked signed"
            " squared risks. Complete triples only; no imputation, C-B, "
            "absolute-component addition or gap-task reinterpretation."
        ),
        (
            "Initial/selector/September-refit/Oct–Dec/annual-OOS roles are exactly "
            "Design A; own independently fitted legal prefix FT16 "
            "recipe/weighted-left-median scale matches all8 S2-B recipes/scales. "
            "Seed42 AdamW lr.001 beta(.9,.999)eps1e-8, matrix decay.01 bias0, norm "
            "clip1,16 complete sessions, seeded shuffle42+epoch. Fresh "
            "optimizer/refit at qualified epoch; main .999 best "
            "rule,min12,patience10,max60. Batch aux weight is phase-global masked "
            "overnight hierarchy times S_phase/B_batch; no minibatch denominator or "
            "missing-stock redistribution. Empty aux batch gives zero gradient. "
            "Calibrated primary uses own independent tail C3 IO kappa25; raw "
            "diagnostic is not an OOS-selected alternative."
        ),
        (
            "Original OOS population80260 stock-origin rows/4013 origins/793 "
            "sessions,20 per origin. Primary target starts at nominal origin before "
            "approximately+2min issuance; it is price-only, not verified executable "
            "returns. All2021–24 history is repeatedly inspected. No2025 market/2026 "
            "protected access, minute rebuild/download, options/backtest, S2-D or "
            "deferred route."
        ),
        "## Fit and source receipts",
        b.markdown(pd.DataFrame(fits)),
        b.markdown(pd.DataFrame(b.read(out / "S2C_CA_PREFLIGHT.json")["counts"])),
        (
            "Supported source prices were checked positive/finite using only saved "
            "genuine adjusted quarantine-filtered entry/exit/last-minute "
            "close/next09:30 open. Signed identity atol1e-12 rtol1e-11, actual "
            "maximum "
        )
        + str(b.read(out / "S2C_CA_PREFLIGHT.json")["additivity_max_error"])
        + (
            ". One-closure calendar geometry and COP action basis verified. No "
            "primary key deleted; no all20 aux gate. Source concentration in MS/MRK "
            "and historical MA remains; original audit stock/month/slot marginals are"
            " referenced rather than copied, and masks are identical to audit counts."
            " No MCAR assumption. Labels mature before each legal phase cutoff and "
            "remain outside features. All previous source/control artifacts preserve "
            "their bound hashes."
        ),
        "## Primary annual and equal-year comparisons",
        b.markdown(selected),
        (
            "Raw errors/means in absolute log-return units; MSE in squared units. "
            "Equal-stock/origin/session/year hierarchy, arithmetic equal-year scores,"
            " ratio of equal-year means. Four years are not seeds."
        ),
        "## Paired whole-calendar-month descriptive uncertainty",
        b.markdown(pd.DataFrame(paired)),
        (
            "400 draws,seed22042, whole months within year and equal years. Full "
            "correlated stock/origin/session blocks retained. No IID row inference, "
            "selection-adjusted p-values or independent confirmation; intervals "
            "condition on selected encoders and fitted calibration factors."
        ),
        "## Independent calibration",
        b.markdown(pd.concat(coefficients)),
        (
            "Each factor uses own frozen September network/scale and only Oct–Dec "
            "outcomes. q uses unconstrained main Mhat; finite positivity and "
            "concentration guards apply without trimming. Calibration tail scores are"
            " not OOS. Within-origin raw/cal ranks must coincide absent new clamp "
            "ties; output files record finite nonnegative predictions."
        ),
        "## Clock, reliability and ordinary/tail trade-offs",
        b.markdown(m.loc[m.year.eq("EQ") & m.arm.isin([CAL, RAW, "CLOCK-C3", "C3", "M1", "C0"])]),
        b.markdown(
            g.loc[
                g.year.eq("EQ")
                & g.arm.isin([CAL, "CLOCK-C3", "C3"])
                & g.field.isin(["slot", "calendar", "tail_ALL"]),
                [
                    "arm",
                    "field",
                    "group",
                    "rows",
                    "raw_MSE",
                    "raw_MAE",
                    "ratio",
                    "raw_MSE_loss_share",
                    "false_low_rank",
                ],
            ]
        ),
        (
            "groups.csv also contains all annual seven clocks, actual early-close "
            "cases, conditional intraday/overnight prefix95/99 events and "
            "complements, and shared C0-score weighted-decile membership (fixed "
            "q=.1.. .9, descriptive only). False-low is average-tie within-origin "
            "bottom-half rank <=10.5, weighted on event cohorts; not a calibrated "
            "event probability. Cohorts use saved restricted-prefix95/99 raw-A "
            "thresholds, never OOS fitted. Tail loss contributions use unchanged "
            "unconditional row weights. Within-origin "
            "IC/pair/top4/bottom4/ties/constant rates appear in metrics.csv; "
            "top/bottom chance .2, pair chance .5, canonical tie handling reused. "
            "Tail-underprediction alone is not proof of conditional-mean "
            "miscalibration."
        ),
        "## Auxiliary signed diagnostics (separate task quantities)",
        b.markdown(pd.concat(auxiliary).loc[lambda f: f.ticker.eq("ALL")]),
        (
            "auxiliary_diagnostics.csv gives all20 stocks and pooled "
            "per-year/component weighted signed MSE/MAE/Pearson with genuine "
            "supported-cell/session denominators. These are signed-return auxiliary "
            "tasks, not primary magnitude MSE or gap-forecast model results. They are"
            " post-fit and were not used for model choice. Correlations are "
            "descriptive and selected source support may be nonrandom."
        ),
        "## Decision and limitations",
        notes.get(
            "decision",
            (
                "Apply primary raw-MSE criterion versus both CLOCK-C3/C3, then inspect "
                "annual, MAE, rank, ordinary/tail and clock costs; retain CLOCK-C3 if no "
                "incremental evidence. No aux coefficient or model is retuned."
            ),
        ),
        (
            "Any benefit is an auxiliary-supervision/extra-head/optimization package;"
            " no ablation isolates capacity from supervision. No signed alpha, causal"
            " jump mechanism or option profitability claim is supported. Intraday "
            "C0/C3 preference and deferred routed test remain unresolved. STOP for "
            "researcher review."
        ),
        "## Reproduction and preservation",
        (
            "Commands: `.venv/bin/python -m lstm_data.hf20_s2c_ca --preflight`, "
            "focused tests/Ruff/full static as recorded in readiness/session handoff,"
            " then one single-use `--run`; `--report` reads only saved outputs. Do "
            "not rerun --run on this namespace. No commit/push. Only new "
            "module/test/output namespace/session handoff and permitted successor "
            "registry pointer/journal; old assets never overwritten. See "
            "protocol,preflight,readiness,phase_parity,verification and journal for "
            "sources,tests,budget/resources. Model state dicts/prediction Parquets "
            "are local ignored artifacts; no old scores/inputs duplicated."
        ),
    ]
    (out / "S2C_CA_REPORT.md").write_text("\n\n".join(sections) + "\n")
    last = json.loads((out / "neural_starts.jsonl").read_text().splitlines()[-1])
    clock.freeze(
        out / "verification.json",
        dict(
            status="COMPLETE" if len(years) == 4 else "PARTIAL",
            verdict=verdict,
            folds=years,
            ledger_before=158,
            ledger_after=last["global_started_pairs"],
            ceiling=300,
            charged_pairs=len(years),
            phase_fits=2 * len(years),
            no_retries=True,
            old_bindings_unchanged=True,
            exact_primary_keys=True,
            checkpoint_reload_max_error=0,
            resources=b.resources(out),
        ),
    ) if not (out / "verification.json").exists() else None


if __name__ == "__main__":
    main()
