"""Bounded saved-output HF20 diagnosis. No model, optimizer, fitting, or network API."""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROLES = ("inner_train", "inner_validation", "refit", "development")
COUNTS = ((4428, 2513), (766, 459), (5210, 2980), (183, 109))
BASE = Path("artifacts/hf20_hf1m_long_v1/p028_approved_runs")
P028 = Path(
    "reports/experiments/ta028_market_state_2026-10-24_064442_execution_v1/checkpoint_completion_v2"
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class Reader:
    """Exact manifest allowlist is checked before any numerical filesystem call."""

    def __init__(self, out: Path):
        self.manifest = json.loads((out / "input_manifest.json").read_text())
        self.refs = {r["path"]: r for r in self.manifest["evidence"]}
        extra = out / "supplement_read_manifest.json"
        if extra.is_file():
            self.refs.update({r["path"]: r for r in json.loads(extra.read_text())["evidence"]})
        self.reads: list[str] = []

    def path(self, path: Path, role: str) -> Path:
        if role not in ROLES:
            raise ValueError("PROTECTED_OR_UNKNOWN_ROLE_BEFORE_IO")
        r = self.refs.get(str(path))
        if r is None or not r["access"].startswith("PRE2026"):
            raise ValueError("NONALLOWLISTED_NUMERICAL_PATH_BEFORE_IO")
        if digest(path) != r["sha256"]:
            raise ValueError("SOURCE_BYTES_CHANGED")
        self.reads.append(str(path))
        return path

    def table(self, path: Path, role: str, columns: list[str] | None = None) -> pd.DataFrame:
        f = pd.read_parquet(self.path(path, role), columns=columns)
        if "session_date_et" in f and f.session_date_et.astype(str).ge("2026-01-01").any():
            raise ValueError("HISTORICAL_SOURCE_CONTRACT_VIOLATION")
        return f


def weights(f: pd.DataFrame) -> np.ndarray:
    if f.duplicated(["origin_id", "ticker"]).any():
        raise ValueError("DUPLICATE_KEYS")
    sizes = f.groupby("origin_id", sort=False).size()
    if not sizes.eq(20).all():
        raise ValueError("INCOMPLETE_ORIGIN")
    counts = f.groupby("session_date_et").origin_id.nunique()
    return 1.0 / (len(counts) * f.session_date_et.map(counts).to_numpy() * 20)


def ranked(values: np.ndarray, keys: pd.DataFrame, percent: int) -> np.ndarray:
    order = np.lexsort((keys.stock_order.to_numpy(), keys.origin_id.to_numpy(), -values))
    mask = np.zeros(len(values), dtype=bool)
    mask[order[: len(values) * percent // 100]] = True
    return mask


def rank_metrics(y: np.ndarray, p: np.ndarray) -> dict[str, np.ndarray]:
    """Midranks; undefined constant correlation, no jitter; half-credit predicted ties."""
    yr = pd.DataFrame(y).rank(axis=1, method="average").to_numpy()
    pr = pd.DataFrame(p).rank(axis=1, method="average").to_numpy()
    yc, pc = yr - yr.mean(1)[:, None], pr - pr.mean(1)[:, None]
    denom = np.sqrt((yc * yc).sum(1) * (pc * pc).sum(1))
    ic = np.divide((yc * pc).sum(1), denom, out=np.full(len(y), np.nan), where=denom > 0)
    i, j = np.triu_indices(20, 1)
    a, b = np.sign(y[:, i] - y[:, j]), np.sign(p[:, i] - p[:, j])
    valid = a != 0
    concord = np.divide(
        ((a == b) * valid + 0.5 * (b == 0) * valid).sum(1),
        valid.sum(1),
        out=np.full(len(y), np.nan),
        where=valid.sum(1) > 0,
    )

    # Fractional membership for a tie spanning the four-name retrieval boundary.
    def membership(v: np.ndarray, top: bool) -> np.ndarray:
        s = v if top else -v
        cut = np.sort(s, axis=1)[:, -4]
        above, at = s > cut[:, None], s == cut[:, None]
        return above + at * ((4 - above.sum(1)) / at.sum(1))[:, None]

    top = (membership(y, True) * membership(p, True)).sum(1) / 4
    bottom = (membership(y, False) * membership(p, False)).sum(1) / 4
    sorted_p = np.sort(p, axis=1)
    return dict(
        ic=ic,
        concordance=concord,
        rank_mae=np.abs(yr - pr).mean(1) / 19,
        rank_mse=(((yr - pr) / 19) ** 2).mean(1),
        top4=top,
        bottom4=bottom,
        score_sd=p.std(1),
        tie_pair_rate=(b == 0).mean(1),
        min_gap=np.diff(sorted_p, axis=1).min(1),
        median_gap=np.median(np.diff(sorted_p, axis=1), axis=1),
        constant_score=(p.max(1) == p.min(1)).astype(float),
    )


def decomposition(y: np.ndarray, p: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    total = ((y - p) ** 2).mean(1)
    common = (y.mean(1) - p.mean(1)) ** 2
    centered = ((y - y.mean(1)[:, None] - p + p.mean(1)[:, None]) ** 2).mean(1)
    np.testing.assert_allclose(total, common + centered, rtol=1e-13, atol=1e-13)
    return total, common, centered


def aggregate_origins(f: pd.DataFrame) -> dict:
    numeric = list(f.select_dtypes(include="number").columns)
    return f.groupby("session_date_et")[numeric].mean().mean().to_dict()


def table(out: Path, name: str, rows: list[dict] | pd.DataFrame) -> None:
    pd.DataFrame(rows).to_csv(out / name, index=False)


def loss_audit(out: Path, reader: Reader, contract: dict, recipes: dict) -> None:
    symbols = contract["symbols"]
    summaries, cohorts, origin_frames, strata, reconciliations, examples = [], [], [], [], [], []
    reported = pd.read_csv(P028 / "scientific_closeout_v1/four_role_metrics.csv")
    oldcohorts = pd.read_csv(P028 / "scientific_closeout_v1/objective_cohorts.csv")
    fixed_training: dict[str, pd.DataFrame] = {}
    for role, (n, days) in zip(ROLES, COUNTS):
        phase = "inner" if role.startswith("inner") else "refit"
        scale = recipes[phase]["t2_scale"]
        root = BASE / "A7_immediate_diagnostics" / role
        b = reader.table(root / "T2_S42.parquet", role)
        b["stock_order"] = b.ticker.map({s: i for i, s in enumerate(symbols)})
        b = b.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
        assert len(b) == 20 * n and b.session_date_et.nunique() == days
        assert b.groupby("origin_id").ticker.agg(tuple).map(lambda v: v == tuple(symbols)).all()
        if role in ("inner_train", "refit"):
            fixed_training[phase] = b
        training = fixed_training[phase]
        w = weights(b)
        y = b.TG20.to_numpy(float)
        y32 = y.astype(np.float32)
        tz = torch.asinh(torch.from_numpy(y32) / scale)
        yy = y.reshape(-1, 20)
        bp = b.pred_original_TG20.to_numpy(float)
        bz = b.raw_net_output.to_numpy(np.float32).copy()
        byloss = (y - bp) ** 2
        bzloss = (torch.from_numpy(bz) - tz).square().numpy().astype(float)
        assert b.t2_scale.eq(scale).all() and b.inverse_count.eq(1).all()
        np.testing.assert_allclose(bp, scale * np.sinh(bz.astype(float)), rtol=7e-7, atol=1e-7)
        np.testing.assert_allclose(
            y, b.numerator / (b.cross_section_mad + b.epsilon), rtol=1e-11, atol=1e-11
        )
        np.testing.assert_allclose(b.epsilon, recipes[phase]["epsilon"], rtol=0, atol=0)
        origins = b.iloc[::20][["origin_id", "session_date_et", "entry_end_utc"]].reset_index(
            drop=True
        )
        origins["slot"] = (
            pd.to_datetime(origins.entry_end_utc, utc=True)
            .dt.tz_convert("America/New_York")
            .dt.strftime("%H:%M")
        )
        origins["month"], origins["year"] = (
            origins.session_date_et.str[:7],
            origins.session_date_et.str[:4],
        )
        masks: dict[str, np.ndarray] = {
            "ALL": np.ones(len(b), bool),
            "POS": y > 0,
            "NEG": y < 0,
            "ZERO": y == 0,
        }
        # Reproduce the P028 role-ranked diagnostic conventions exactly.
        for pct in (1, 5):
            target = ranked(abs(y), b, pct)
            masks[f"TARGET_TOP{pct}"] = target
            masks[f"TARGET_TOP{pct}_COMPLEMENT"] = ~target
            num = ranked(abs(b.numerator.to_numpy()), b, pct)
            selected = (
                b.drop_duplicates("origin_id")
                .sort_values(["cross_section_mad", "origin_id"])
                .iloc[: n * pct // 100]
            )
            mad = b.origin_id.isin(selected.origin_id).to_numpy()
            for label, m in [
                ("NUM_ONLY", num & ~mad),
                ("MAD_ONLY", mad & ~num),
                ("BOTH", num & mad),
                ("NEITHER", ~(num | mad)),
            ]:
                masks[f"{label}_{pct}"] = m
        # Existing P020 training-frozen diagnostic threshold flags (different from role ranks).
        for label in ["large_numerator", "small_mad"]:
            assert label not in b  # This provenance comes from the candidate joined target table.
        for q in (0.95, 0.99):
            threshold = float(np.quantile(abs(training.TG20.to_numpy()), q))
            for side, mask in [
                ("ABS", abs(y) > threshold),
                ("POS", y > threshold),
                ("NEG", y < -threshold),
            ]:
                masks[f"TRAIN_EVENT_{q}_{side}"] = mask
        for frac in (0.95, 0.99):
            masks[f"RANGE_ABS_{frac}"] = abs(y) >= frac * abs(training.TG20).max()
        masks["MAD_LE_EPSILON"] = b.cross_section_mad.to_numpy() <= b.epsilon.to_numpy()
        for model in ("T2_S42", "A7", "A12"):
            f = (
                b.copy()
                if model == "T2_S42"
                else reader.table(
                    BASE / f"{model}_immediate_diagnostics" / role / "population.parquet", role
                )
            )
            f["stock_order"] = f.ticker.map({s: i for i, s in enumerate(symbols)})
            f = f.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
            assert f[["origin_id", "ticker", "session_date_et", "fit_version"]].equals(
                b[["origin_id", "ticker", "session_date_et", "fit_version"]]
            )
            np.testing.assert_array_equal(f.TG20, b.TG20)
            np.testing.assert_allclose(f.return_4h, b.return_4h, rtol=0, atol=0)
            assert f.checkpoint_sha256.nunique() == 1 and f.t2_scale.eq(scale).all()
            p = f.pred_original_TG20.to_numpy(float)
            z = f.raw_net_output.to_numpy(np.float32).copy()
            np.testing.assert_allclose(p, scale * np.sinh(z.astype(float)), rtol=7e-7, atol=1e-7)
            ey = (y - p) ** 2
            ez = (torch.from_numpy(z) - tz).square().numpy().astype(float)
            mm = {**masks}
            for pct in (1, 5):
                for name, v in [
                    ("OWN_Y_ERROR", ey),
                    ("OWN_Z_ERROR", ez),
                    ("T2_Y_ERROR", byloss),
                    ("T2_Z_ERROR", bzloss),
                ]:
                    mask = ranked(v, b, pct)
                    mm[f"{name}_TOP{pct}"] = mask
                    mm[f"{name}_TOP{pct}_COMPLEMENT"] = ~mask
            if model != "T2_S42":
                ln = f.large_numerator.to_numpy(bool)
                sm = f.small_mad.to_numpy(bool)
                for name, mask in [
                    ("NUM_ONLY", ln & ~sm),
                    ("MAD_ONLY", sm & ~ln),
                    ("BOTH", ln & sm),
                    ("NEITHER", ~(ln | sm)),
                ]:
                    mm["P020_FROZEN_" + name] = mask
                for col in ("V1_state", "quality", "fallback_state"):
                    for value in sorted(set(f[col].astype(str))):
                        mm[f"{col}:{value}"] = f[col].astype(str).eq(value).to_numpy()
            dy, dz = ey - byloss, ez - bzloss
            for label, mask in mm.items():
                mass = float(w[mask].sum())
                row = dict(
                    role=role,
                    model=model,
                    cohort=label,
                    rows=int(mask.sum()),
                    sessions=b.loc[mask, "session_date_et"].nunique(),
                    origins=b.loc[mask, "origin_id"].nunique(),
                    weight_mass=mass,
                    y_loss=float(w[mask] @ ey[mask]),
                    z_loss=float(w[mask] @ ez[mask]),
                    y_delta=float(w[mask] @ dy[mask]),
                    z_delta=float(w[mask] @ dz[mask]),
                    y_conditional=float(w[mask] @ ey[mask] / mass) if mass else np.nan,
                    z_conditional=float(w[mask] @ ez[mask] / mass) if mass else np.nan,
                    target_min=float(y[mask].min()) if mask.any() else np.nan,
                    target_max=float(y[mask].max()) if mask.any() else np.nan,
                )
                for name, delta in [("y", dy), ("z", dz)]:
                    total = float(w @ delta)
                    row[name + "_fraction_total_change"] = (
                        float(row[name + "_delta"]) / total if total else np.nan
                    )
                cohorts.append(row)
            for pct in (1, 5):
                parts = [mm[f"{k}_{pct}"] for k in ("NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER")]
                np.testing.assert_array_equal(np.sum(parts, axis=0), np.ones(len(b)))
                np.testing.assert_allclose(
                    sum(w[m] @ ey[m] for m in parts), w @ ey, rtol=1e-13, atol=1e-13
                )
                np.testing.assert_allclose(
                    sum(w[m] @ ez[m] for m in parts), w @ ez, rtol=1e-13, atol=1e-13
                )
            total, common, centered = decomposition(yy, p.reshape(-1, 20))
            bt, bc, be = decomposition(yy, bp.reshape(-1, 20))
            o = origins.copy()
            o["role"], o["model"] = role, model
            for col, v in {
                "mse": total,
                "common": common,
                "centered": centered,
                "delta_mse": total - bt,
                "delta_common": common - bc,
                "delta_centered": centered - be,
                **rank_metrics(yy, p.reshape(-1, 20)),
            }.items():
                o[col] = v
            origin_frames.append(o)
            summary = dict(
                role=role,
                model=model,
                rows=len(f),
                origins=n,
                sessions=days,
                scale=scale,
                epsilon=recipes[phase]["epsilon"],
                checkpoint=f.checkpoint_sha256.iloc[0],
                z_mse=float(w @ ez),
                zero_mse=float(w @ (y * y)),
                energy=float(w @ (p * p)),
                alignment=float(w @ (y * p)),
                **aggregate_origins(o.drop(columns=["role", "model"])),
            )
            summary["daily_ic"] = summary.pop("ic")
            summaries.append(summary)
            if model != "T2_S42":
                old = reported.loc[reported.arm.eq(model) & reported.role.eq(role)].iloc[0]
                np.testing.assert_allclose(float(summary["mse"]), old.mse, rtol=1e-13, atol=1e-13)
                np.testing.assert_allclose(
                    float(summary["z_mse"]), old.optimized_z_mse, rtol=5e-7, atol=1e-8
                )
                np.testing.assert_allclose(
                    float(summary["daily_ic"]), old.daily_ic, rtol=1e-12, atol=1e-12
                )
                for pct in (1, 5):
                    oldrow = oldcohorts.loc[
                        oldcohorts.arm.eq(model)
                        & oldcohorts.role.eq(role)
                        & oldcohorts.cohort.eq(f"TARGET_RANK_TOP{pct}")
                    ].iloc[0]
                    current = float(w[mm[f"TARGET_TOP{pct}"]] @ ez[mm[f"TARGET_TOP{pct}"]])
                    # Determine the historical contribution field explicitly, never infer units.
                    oldvalue = float(oldrow["weighted_objective"])
                    np.testing.assert_allclose(current, oldvalue, rtol=5e-7, atol=1e-8)
                reconciliations.append(
                    dict(
                        role=role,
                        model=model,
                        mse_error=float(summary["mse"]) - old.mse,
                        z_error=float(summary["z_mse"]) - old.optimized_z_mse,
                        ic_error=summary["daily_ic"] - old.daily_ic,
                    )
                )
                for group in ["ticker", "quality", "fallback_state", "V1_state"]:
                    for label, idx in f.groupby(group).indices.items():
                        mass = w[idx].sum()
                        strata.append(
                            dict(
                                role=role,
                                model=model,
                                group=group,
                                label=str(label),
                                rows=len(idx),
                                weight_mass=mass,
                                y_delta=float(w[idx] @ dy[idx]),
                                z_delta=float(w[idx] @ dz[idx]),
                            )
                        )
                for group in ("NUM_ONLY_5", "MAD_ONLY_5", "BOTH_5", "NEITHER_5"):
                    indices = np.flatnonzero(mm[group])
                    if len(indices):
                        ix = indices[np.argmax(abs(y[indices]))]
                        examples.append(
                            dict(
                                role=role,
                                model=model,
                                cohort=group,
                                **f.iloc[ix][
                                    [
                                        "origin_id",
                                        "ticker",
                                        "numerator",
                                        "cross_section_mad",
                                        "epsilon",
                                        "TG20",
                                        "raw_net_output",
                                        "pred_original_TG20",
                                    ]
                                ].to_dict(),
                                y_error=ey[ix],
                                z_error=ez[ix],
                                row_weight=w[ix],
                                source=(
                                    "existing keyed population; "
                                    "source-candle witnesses reused by reference"
                                ),
                            )
                        )
    table(out, "four_role_metrics.csv", summaries)
    table(out, "matched_loss_cohorts.csv", cohorts)
    allorigins = pd.concat(origin_frames, ignore_index=True)
    # Compact origin records, no copied market-price windows or per-arm feature tensors.
    table(out, "origin_ranking_and_decomposition.csv", allorigins)
    periods = []
    for group in ("month", "year", "slot"):
        keys = (
            allorigins[["role", "model", group]]
            .drop_duplicates()
            .sort_values(["role", "model", group])
        )
        for key in keys.to_dict("records"):
            role, model, label = key["role"], key["model"], key[group]
            g = allorigins.loc[
                allorigins.role.eq(role) & allorigins.model.eq(model) & allorigins[group].eq(label)
            ]
            periods.append(
                dict(
                    role=role,
                    model=model,
                    group=group,
                    label=str(label),
                    origins=len(g),
                    sessions=g.session_date_et.nunique(),
                    **aggregate_origins(g),
                )
            )
    table(out, "ranking_periods.csv", periods)
    table(out, "matched_stock_quality_strata.csv", strata)
    table(out, "metric_reconciliation.csv", reconciliations)
    table(out, "extreme_examples.csv", examples)


def feature_audit(out: Path, reader: Reader, contract: dict, recipes: dict) -> None:
    origins = reader.table(Path(contract["files"]["origins"]["path"]), "refit")
    grid = reader.table(Path(contract["files"]["grid"]["path"]), "refit")
    quality = reader.table(Path(contract["files"]["candles_quality"]["path"]), "refit")
    arrays = np.load(
        reader.path(Path(contract["files"]["components"]["path"]), "refit"), allow_pickle=False
    )
    feature_order = contract["feature_order"]
    common_order = [k for k in feature_order if k != "M2"]
    rows, window_rows, associations, case_rows = [], [], [], []
    # Frozen before outcome inspection: these four documented channels, no score combination.
    shortlist = ("M1", "M2", "Q1", "V1")
    for role, (expected, sessions) in zip(ROLES, COUNTS):
        phase = "inner" if role.startswith("inner") else "refit"
        selected = (
            origins.loc[origins[role + "_admitted"]].sort_values("origin_id").reset_index(drop=True)
        )
        assert len(selected) == expected and selected.session_date_et.nunique() == sessions
        starts = selected.first_step.to_numpy(int)
        ends = selected.entry_index.to_numpy(int)
        assert (ends - starts == 47).all()
        assert (
            pd.to_datetime(selected.label_maturity_utc, utc=True)
            .lt(pd.Timestamp("2026-01-01", tz="UTC"))
            .all()
        )
        slots = (
            pd.to_datetime(selected.entry_end_utc, utc=True)
            .dt.tz_convert("America/New_York")
            .dt.hour.to_numpy()
            - 10
        )
        union = np.zeros(len(grid), bool)
        for a, b in zip(starts, ends):
            union[a : b + 1] = True
        # Materialize each shared channel once; gather endpoints and prefix counts only.
        native = arrays[phase + "_native_common"]
        scaled = arrays[phase + "_scaled_common"]
        fallback = arrays[phase + "_fallback_common"]
        nm2 = arrays[phase + "_native_m2"]
        sm2 = arrays[phase + "_scaled_m2"]
        fm2 = arrays[phase + "_fallback_m2"]
        target = reader.table(BASE / "A7_immediate_diagnostics" / role / "T2_S42.parquet", role)
        target["stock_order"] = target.ticker.map({s: i for i, s in enumerate(contract["symbols"])})
        target = target.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
        assert target.iloc[::20].origin_id.tolist() == selected.origin_id.tolist()
        y = target.TG20.to_numpy(float).reshape(-1, 20)
        for channel in feature_order:
            if channel == "M2":
                sv = sm2[ends, :, slots]
                fb = fm2[ends, :, slots]
                # Unique (step, origin context, stock) union, not arbitrary all contexts.
                union_context = np.zeros((len(grid), 2), bool)
                for a, b, slot in zip(starts, ends, slots):
                    union_context[a : b + 1, slot] = True
                samples = nm2.transpose(0, 2, 1)[union_context].reshape(-1)
                masks = fm2.transpose(0, 2, 1)[union_context].reshape(-1)
                counts = np.empty((len(selected), 20), int)
                for slot in (0, 1):
                    prefix = np.vstack([np.zeros((1, 20), int), fm2[:, :, slot].cumsum(0)])
                    choice = slots == slot
                    counts[choice] = prefix[ends[choice] + 1] - prefix[starts[choice]]
            else:
                j = common_order.index(channel)
                sv = scaled[ends, :, j]
                fb = fallback[ends, :, j]
                samples = native[union, :, j].reshape(-1)
                masks = fallback[union, :, j].reshape(-1)
                prefix = np.vstack([np.zeros((1, 20), int), fallback[:, :, j].cumsum(0)])
                counts = prefix[ends + 1] - prefix[starts]
            assert np.array_equal(~np.isfinite(samples), masks)
            rows.append(
                dict(
                    role=role,
                    channel=channel,
                    unique_cells=len(samples),
                    native_missing=int(masks.sum()),
                    fallback_rate=float(masks.mean()),
                    endpoint_fallback_rate=float(fb.mean()),
                    windows_stock_any_fallback=int((counts > 0).sum()),
                    origins_any_fallback=int((counts > 0).any(1).sum()),
                    window_cell_fallback_rate=float(counts.sum() / (len(selected) * 20 * 48)),
                    native_p01=float(np.nanquantile(samples, 0.01)),
                    native_p50=float(np.nanmedian(samples)),
                    native_p99=float(np.nanquantile(samples, 0.99)),
                    scaled_endpoint_min=float(sv.min()),
                    scaled_endpoint_max=float(sv.max()),
                )
            )
            for slot in (0, 1):
                for year in sorted(set(selected.session_date_et.str[:4])):
                    choice = (slots == slot) & selected.session_date_et.str.startswith(
                        year
                    ).to_numpy()
                    if choice.any():
                        window_rows.append(
                            dict(
                                role=role,
                                channel=channel,
                                slot=slot + 1,
                                year=year,
                                origins=int(choice.sum()),
                                fallback_cells=int(counts[choice].sum()),
                                window_cell_rate=float(
                                    counts[choice].sum() / (choice.sum() * 20 * 48)
                                ),
                            )
                        )
            if channel in shortlist:
                ic = rank_metrics(y, sv)["ic"]
                for group, labels in [
                    ("ALL", np.repeat("ALL", len(selected))),
                    ("slot", slots.astype(str)),
                    ("year", selected.session_date_et.str[:4].to_numpy()),
                ]:
                    for label in sorted(set(labels)):
                        choice = labels == label
                        temp = pd.DataFrame(
                            dict(day=selected.loc[choice, "session_date_et"], ic=ic[choice])
                        )
                        associations.append(
                            dict(
                                role=role,
                                channel=channel,
                                group=group,
                                label=label,
                                origins=int(choice.sum()),
                                defined_origins=int(np.isfinite(ic[choice]).sum()),
                                daily_spearman=float(temp.groupby("day").ic.mean().mean()),
                                status="DESCRIPTIVE_ONLY_NO_FIT_NO_SELECTION",
                            )
                        )
        if role == "development":
            # Predeclared source-case selection by calendar/source metadata, never model errors.
            choices = {}
            for label, cond in [("ORIGIN1", slots == 0), ("ORIGIN2", slots == 1)]:
                positions = np.flatnonzero(cond)
                if len(positions):
                    choices[int(positions[0])] = label
            hours = pd.to_datetime(grid.hour_end_utc, utc=True)
            gaps = hours.diff().dt.total_seconds().fillna(3600).to_numpy()
            for label, cond in [("WEEKEND", gaps > 48 * 3600), ("OVERNIGHT", gaps > 8 * 3600)]:
                for i, (a, b) in enumerate(zip(starts, ends)):
                    if cond[a : b + 1].any():
                        choices.setdefault(i, label)
                        break
            # Include a genuine fallback/proxy witness from preserved case catalogue elsewhere.
            for i, label in choices.items():
                r = selected.iloc[i]
                a, b = int(r.first_step), int(r.entry_index)
                sequence = grid.iloc[a : b + 1]
                assert len(sequence) == 48 and pd.Timestamp(
                    sequence.hour_end_utc.iloc[-1]
                ) == pd.Timestamp(r.entry_end_utc)
                case_rows.append(
                    dict(
                        case=label,
                        origin_id=r.origin_id,
                        session_date_et=r.session_date_et,
                        input_first_utc=str(sequence.hour_end_utc.iloc[0]),
                        input_last_utc=str(sequence.hour_end_utc.iloc[-1]),
                        source_available_at=str(r.source_publication_available_at),
                        issuance_utc=str(r.issuance_utc),
                        target_start_utc=str(r.entry_end_utc),
                        target_end_utc=str(r.exit_end_utc),
                        maturity_utc=str(r.label_maturity_utc),
                        full48_clock_json=json.dumps(sequence.hour_end_utc.astype(str).tolist()),
                        gap_hours_max=float(gaps[a : b + 1].max() / 3600),
                        interval_starts_before_issuance=True,
                        availability_status="ASSUMED_TWO_MINUTE_NOT_VENDOR_ATTESTED",
                    )
                )
    table(out, "channel_by_role_quality.csv", rows)
    table(out, "fallback_by_slot_year.csv", window_rows)
    table(out, "feature_rank_associations.csv", associations)
    table(out, "clock_cases.csv", case_rows)
    # Unique source cells only; no multiplying overlapping windows.
    stats = []
    for year, g in quality.groupby(quality.session_date_et.str[:4]):
        stats.append(
            dict(
                year=year,
                hour_stock_rows=len(g),
                missing_assumed_zero=int(g.assumed_zero_missing_count.sum()),
                proxy_close_hours=int(g.proxy_count.gt(0).sum()),
                incomplete_extrema_hours=int((~g.extrema_complete).sum()),
                poor_volume_hours=int((~g.volume_usable_for_feature).sum()),
                observed_zero_volume_hours=int(g.observed_volume.eq(0).sum()),
                unknown_volume_minutes=int(g.quarantine_volume_unknown_count.sum()),
                source_age_max_minutes=(
                    "NOT_INDEPENDENTLY_PUBLISHED; cap5 proxy age inspect source references"
                ),
            )
        )
    table(out, "source_quality_by_year.csv", stats)
    arrays.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    if out.parent != Path("reports/diagnostics") or not (out / "input_manifest.json").is_file():
        raise ValueError("ISOLATED_PREFLIGHT_NAMESPACE_REQUIRED")
    if (out / "four_role_metrics.csv").exists():
        raise ValueError("NO_OVERWRITE_USE_NEW_REPORT_NAMESPACE")
    start = time.monotonic()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    reader = Reader(out)
    contract = json.loads(Path(reader.manifest["source_contract"]["path"]).read_text())
    recipes = json.loads(Path(contract["fit_recipes"]["path"]).read_text())
    loss_audit(out, reader, contract, recipes)
    feature_audit(out, reader, contract, recipes)
    receipt = dict(
        status="NUMERICAL_CHECKS_PASS",
        read_files=sorted(set(reader.reads)),
        role_counts=COUNTS,
        optimizer_steps=0,
        model_forward_calls=0,
        new_starts=0,
        protected_numeric_reads=0,
        elapsed_seconds=time.monotonic() - start,
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        code_sha256=digest(Path(__file__)),
    )
    (out / "numerical_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "read_files"}))


if __name__ == "__main__":
    main()
