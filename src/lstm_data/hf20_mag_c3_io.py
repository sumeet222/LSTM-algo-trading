"""One fixed two-category smearing calibration; saved scores only, no neural calls."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import hf20_mag_designa as saved
from .hf20_mag_designa_continue import bootstrap_equal_year

OUT = Path("reports/experiments/hf20_s9_mag_stage1_session4_c3_io_2026-10-28")
PARENT = saved.DEFAULT_OUT
CONT = Path("reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27")
O1 = Path("reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28")
ARM = "C3-IO-SMEAR"
GROUPS = ("INTRADAY", "OVERNIGHT")
KAPPA = 25.0
ARMS = (ARM, "C1a", "M1", "C0", "O1", "B0-VOL", "B0-CLOCK", "B0-RMEAN", "B0-RMED")
META = [
    "origin_id",
    "session_date_et",
    "slot",
    "category",
    "entry_end_utc",
    "exit_end_utc",
    "label_maturity_utc",
    "ticker",
    "weight",
]


def root(year: int) -> Path:
    return (PARENT if year == 2021 else CONT) / f"F{year % 100}"


def clock_group(slot: str) -> str:
    if slot not in saved.SLOTS:
        raise ValueError("UNKNOWN_ORIGIN_SLOT")
    return "INTRADAY" if slot in saved.SLOTS[:3] else "OVERNIGHT"


def validate_panel(f: pd.DataFrame, early_close_days: set[str] | None = None) -> None:
    """Exact complete-panel order and original session/origin/stock weights."""
    assert len(f) and len(f) % 20 == 0
    assert not f.duplicated(["origin_id", "ticker"]).any()
    origins = f.origin_id.iloc[::20].to_numpy()
    assert len(np.unique(origins)) == len(origins)
    np.testing.assert_array_equal(f.origin_id, np.repeat(origins, 20))
    assert f.ticker.tolist() == list(saved.SYMBOLS) * len(origins)
    nominal = f.slot.map(clock_group)
    assert f.category.isin(GROUPS).all()
    mismatch = f.category.ne(nominal)
    if mismatch.any():
        assert f.loc[mismatch, "category"].eq("OVERNIGHT").all()
        assert nominal.loc[mismatch].eq("INTRADAY").all()
        assert f.loc[mismatch, "session_date_et"].isin(early_close_days or set()).all()
    assert f.groupby("origin_id").category.nunique().eq(1).all()
    assert f.session_date_et.lt("2025-01-01").all()
    w = f.weight.to_numpy(float)
    assert np.isfinite(w).all() and (w > 0).all()
    expected = np.repeat(saved.origin_weights(f.session_date_et.iloc[::20].to_numpy()) / 20, 20)
    np.testing.assert_allclose(w, expected, atol=1e-15, rtol=1e-13)
    exit_day = f.exit_end_utc.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
    assert (
        exit_day.loc[f.category.eq("INTRADAY")]
        .eq(f.loc[f.category.eq("INTRADAY"), "session_date_et"])
        .all()
    )
    assert (
        exit_day.loc[f.category.eq("OVERNIGHT")]
        .gt(f.loc[f.category.eq("OVERNIGHT"), "session_date_et"])
        .all()
    )


def effective_sessions(f: pd.DataFrame) -> float:
    """Information units are weighted whole sessions, never stock-row counts."""
    if f.empty:
        raise ValueError("BLOCKED_EMPTY_CALIBRATION_CATEGORY")
    mass = f.groupby("session_date_et").weight.sum().to_numpy(float)
    if not np.isfinite(mass).all() or (mass <= 0).any():
        raise ValueError("INVALID_SESSION_WEIGHT_MASS")
    p = mass / mass.sum()
    return float(1 / (p @ p))


def residual_exp(f: pd.DataFrame, scale: float) -> np.ndarray:
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("POSITIVE_RESTRICTED_SCALE_REQUIRED")
    a, m = f.A.to_numpy(float), f.Mhat.to_numpy(float)
    if not np.isfinite(a).all() or (a < 0).any() or not np.isfinite(m).all():
        raise ValueError("INVALID_CALIBRATION_TARGET_OR_SCORE")
    with np.errstate(over="raise", invalid="raise"):
        q = np.exp(np.log1p(a / scale) - m)
    if not np.isfinite(q).all() or (q <= 0).any():
        raise ValueError("INVALID_RESIDUAL_EXPONENTIAL")
    return q


def decode(mhat: np.ndarray, scale: float, factor: np.ndarray | float) -> np.ndarray:
    """Unconstrained Mhat; clamp only the decoded raw magnitude."""
    if (
        not math.isfinite(scale)
        or scale <= 0
        or not np.isfinite(factor).all()
        or np.any(np.asarray(factor) <= 0)
    ):
        raise ValueError("INVALID_DECODER_SCALE_OR_FACTOR")
    with np.errstate(over="raise", invalid="raise"):
        p = scale * np.maximum(0, np.exp(mhat.astype(float)) * factor - 1)
    if not np.isfinite(p).all() or (p < 0).any():
        raise ValueError("INVALID_DECODED_MAGNITUDE")
    return p


def concentration(q: np.ndarray, w: np.ndarray) -> dict[str, float]:
    contribution = w * q
    ordered = np.sort(contribution)[::-1]
    total = float(ordered.sum())
    return dict(
        q_max=float(q.max()),
        top10_share=float(ordered[:10].sum() / total),
        top1pct_share=float(ordered[: max(1, len(q) // 100)].sum() / total),
    )


def fit_categories(cal: pd.DataFrame, scale: float) -> list[dict]:
    """The sole new fitted arm; this interface accepts no OOS labels or forecasts."""
    q = residual_exp(cal, scale)
    w = cal.weight.to_numpy(float)
    if not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError("INVALID_CALIBRATION_WEIGHTS")
    c0 = float(w @ q / w.sum())
    global_diag = concentration(q, w)
    result = []
    for group in GROUPS:
        mask = cal.category.eq(group).to_numpy()
        g = cal.loc[mask]
        n = effective_sessions(g)
        ww = w[mask]
        qq = q[mask]
        raw = float(ww @ qq / ww.sum())
        rho = n / (n + KAPPA)
        pooled = c0 + rho * (raw - c0)
        if not all(math.isfinite(x) and x > 0 for x in (c0, raw, pooled, n)):
            raise ValueError("INVALID_CATEGORY_MOMENT")
        result.append(
            dict(
                group=group,
                scale=scale,
                c0=c0,
                c_raw=raw,
                n_eff=n,
                kappa=KAPPA,
                rho=rho,
                c_star=pooled,
                delta_from_global=pooled - c0,
                sessions=g.session_date_et.nunique(),
                origins=g.origin_id.nunique(),
                rows=len(g),
                weight_mass=float(ww.sum()),
                **concentration(qq, ww),
                **{f"global_{k}": v for k, v in global_diag.items()},
            )
        )
    return result


def preflight(out: Path) -> tuple[dict, dict[int, pd.DataFrame]]:
    """All-four saved-artifact gate; OOS outcomes are deliberately not projected."""
    pointer = saved.read(saved.POINTER)
    journal = Path(pointer["real_journal"])
    last = json.loads(journal.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 138
    assert pointer["effective_ceiling"] == 200
    assert saved.digest(Path(pointer["plan"]["path"])) == pointer["plan"]["sha256"]
    old_pre = saved.read(CONT / "preflight.json")
    roles = pd.read_csv(CONT / "role_counts.csv")
    indices = np.load(O1 / "role_indices.npz")
    canonical = pd.read_parquet(
        saved.S4 / "opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet",
        columns=[
            "origin_id",
            "session_date_et",
            "slot",
            "category",
            "first_step",
            "entry_index",
            "label_maturity_utc",
            "eligible",
            "trading_minutes",
            "session_close",
        ],
    )
    assert canonical.session_date_et.lt("2025-01-01").all()
    closing = canonical.session_close.dt.tz_convert("America/New_York").dt.strftime("%H:%M")
    early_days = set(canonical.loc[closing.lt("16:00"), "session_date_et"].unique())
    prior_proof = saved.read(O1 / "verification.json")
    assert prior_proof["status"] == "COMPLETE" and prior_proof["postfit_checks"] == "PASS"
    bindings = {
        str(saved.POINTER): saved.digest(saved.POINTER),
        str(journal): saved.digest(journal),
    }
    calibrations = {}
    folds = []
    coverage = []
    exceptions = []
    for fold in old_pre["folds"]:
        year = fold["year"]
        source = root(year)
        target = saved.read(source / "restricted_target.json")
        receipt = saved.read(source / "result.json")
        coeff = saved.read(source / "coefficients.json")
        recipe = saved.read(source / "restricted_recipe.json")
        assert receipt["status"] == "COMPLETED" and receipt["reload_max_error"] == 0
        scale = float(target["scale"])
        assert (
            scale == receipt["scale"]
            and recipe["fit_stop_inclusive"] == fold["cutoffs"]["september"]
        )
        cal = pd.read_parquet(source / "calibration_scores.parquet")
        oo = pd.read_parquet(source / "oos_scores.parquet", columns=[*META, "Mhat", *saved.ARMS])
        for role, f in [("calibration", cal), ("oos", oo)]:
            validate_panel(f, early_days)
            unusual = f.loc[
                f.category.ne(f.slot.map(clock_group)),
                ["origin_id", "session_date_et", "slot", "category", "exit_end_utc"],
            ].drop_duplicates("origin_id")
            exceptions.extend(
                dict(year=year, role=role, **{str(k): v for k, v in item.items()})
                for item in unusual.astype({"exit_end_utc": str}).to_dict("records")
            )
            ix = indices[f"F{year % 100}_{role}"]
            c = canonical.iloc[ix]
            np.testing.assert_array_equal(f.origin_id.iloc[::20], c.origin_id)
            assert c.eligible.all() and c.trading_minutes.eq(240).all()
            assert c.entry_index.sub(c.first_step).eq(47).all()
            for key in ["session_date_et", "slot", "category", "label_maturity_utc"]:
                np.testing.assert_array_equal(f[key].iloc[::20], c[key])
            old_role = roles.loc[roles.year.eq(year) & roles.role.eq(role)].iloc[0]
            assert (
                f.session_date_et.nunique() == old_role.sessions and len(f) == old_role.stock_rows
            )
            assert f.label_maturity_utc.lt(saved.limit(str(old_role.cutoff))).all()
            assert f.session_date_et.between(
                str(old_role.first_date), str(old_role.last_date)
            ).all()
        assert cal.session_date_et.str.startswith(str(year - 1)).all()
        assert cal.session_date_et.between(f"{year - 1}-10-01", f"{year - 1}-12-31").all()
        assert oo.session_date_et.str.startswith(str(year)).all()
        assert cal.label_maturity_utc.max() < oo.entry_end_utc.min()
        assert not np.intersect1d(cal.origin_id.unique(), oo.origin_id.unique()).size
        original = pd.read_parquet(
            saved.S9 / f"HF20-S9-F{year % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "weight"],
        )
        np.testing.assert_array_equal(
            oo[["origin_id", "ticker"]], original[["origin_id", "ticker"]]
        )
        np.testing.assert_allclose(oo.weight, original.weight, atol=1e-15, rtol=1e-13)
        o1 = pd.read_parquet(
            O1 / f"F{year % 100}/oos_scores.parquet", columns=["origin_id", "ticker", "O1"]
        )
        np.testing.assert_array_equal(oo[["origin_id", "ticker"]], o1[["origin_id", "ticker"]])
        q = residual_exp(cal, scale)
        w = cal.weight.to_numpy(float)
        c0 = float(w @ q / w.sum())
        np.testing.assert_allclose(c0, coeff["c"], atol=1e-14, rtol=1e-13)
        for f in [cal, oo]:
            np.testing.assert_allclose(
                decode(f.Mhat.to_numpy(), scale, c0), f.C1a, atol=1e-14, rtol=1e-13
            )
            base = scale * np.expm1(np.maximum(f.Mhat.to_numpy(float), 0))
            np.testing.assert_allclose(base, f.C0, atol=1e-14, rtol=1e-13)
            np.testing.assert_allclose(coeff["k"] * base, f.M1, atol=1e-14, rtol=1e-13)
        for group in GROUPS:
            g = cal.loc[cal.category.eq(group)]
            coverage.append(
                dict(
                    year=year,
                    group=group,
                    sessions=g.session_date_et.nunique(),
                    origins=g.origin_id.nunique(),
                    rows=len(g),
                    weight_mass=float(g.weight.sum()),
                    n_eff=effective_sessions(g),
                    first_date=g.session_date_et.min(),
                    last_date=g.session_date_et.max(),
                )
            )
        folds.append(
            dict(
                year=year,
                source=str(source),
                scale=scale,
                thresholds=target["thresholds"],
                september=fold["cutoffs"]["september"],
                calibration_cutoff=fold["cutoffs"]["december"],
                model_identity=receipt["frozen_parameter_sha256"],
                global_c0=c0,
                calibration_sessions=cal.session_date_et.nunique(),
                **concentration(q, w),
            )
        )
        calibrations[year] = cal
        for path in [
            source / "calibration_scores.parquet",
            source / "oos_scores.parquet",
            O1 / f"F{year % 100}/oos_scores.parquet",
        ]:
            bindings[str(path)] = saved.digest(path)
    protocol = dict(
        kind="HF20_STAGE1_SESSION4_C3_IO_SMEAR_V1",
        kappa=KAPPA,
        groups=list(GROUPS),
        regular_session_slot_map={s: clock_group(s) for s in saved.SLOTS},
        category_rule=(
            "Original saved category/endpoint keys govern; verify scheduled "
            "early-close morning crossing exceptions; no outcome-based relabeling"
        ),
        early_close_dates=sorted(set(item["session_date_et"] for item in exceptions)),
        early_close_exceptions=exceptions,
        folds=folds,
        coverage=coverage,
        q="exp(log1p(A/s)-unconstrained_Mhat)",
        moment="original calibration row weights normalized within group",
        n_eff="1/sum_d(p_gd^2); p_gd=group row weight mass per session / group total weight",
        pooling="rho=n_eff/(n_eff+25); c_star=c0+rho*(c_raw-c0); no renormalization/search",
        decode="s*max(0,exp(Mhat)*c_star-1)",
        weights="stock→origin→session→year, then equal years",
        reliability=(
            "10 weighted empirical C0 score bins per OOS year, shared across arms, descriptive only"
        ),
        paired=dict(
            comparators=["C1a", "M1"],
            draws=400,
            seed=22042,
            method="existing whole-month within-year; equal years",
        ),
        no_oos_labels_in_preflight=True,
        no_neural_fits=True,
        no_neural_forward_passes=True,
        ledger_before=138,
        raw_source_reads=0,
        protected=(
            "No2025/2026 numerical reads/hashes; no underlying source, FT16 rebuild or checkpoints"
        ),
        preservation_bindings=bindings,
        source_rows="saved S4 eligibility metadata; exact O1/DesignA role indices",
        git_start="5f7bb86a35d5aaff34ff79ef8f471117de6d3e42",
    )
    out.mkdir(exist_ok=True)
    path = out / "protocol.json"
    if path.exists():
        assert saved.read(path) == protocol, "FROZEN_PROTOCOL_CHANGED"
    else:
        saved.write(path, protocol, new=True)
    print(pd.DataFrame(coverage).to_string(index=False), flush=True)
    return protocol, calibrations


def evaluate(out: Path) -> None:
    """Only frozen coefficients and saved predictions; no refitting on replay."""
    protocol = saved.read(out / "protocol.json")
    for path, sha in protocol["preservation_bindings"].items():
        assert saved.digest(Path(path)) == sha, f"ORIGINAL_CHANGED:{path}"
    co = pd.read_csv(out / "calibration_coefficients.csv", float_precision="round_trip")
    assert len(co) == 8 and not co.duplicated(["year", "group"]).any()
    np.testing.assert_allclose(co.rho, co.n_eff / (co.n_eff + 25), atol=1e-15, rtol=1e-13)
    np.testing.assert_allclose(
        co.c_star, co.c0 + co.rho * (co.c_raw - co.c0), atol=1e-15, rtol=1e-13
    )
    records = []
    group_records = []
    frames: dict[int, pd.DataFrame] = {}
    rank_checks = []
    old_metrics = pd.read_csv(O1 / "metrics.csv", dtype={"year": str})
    for fold in protocol["folds"]:
        y = fold["year"]
        source = Path(fold["source"])
        f = pd.read_parquet(source / "oos_scores.parquet")
        validate_panel(f, set(protocol["early_close_dates"]))
        # This is the first projection of OOS outcomes in this experiment, after coefficient freeze.
        original = pd.read_parquet(
            saved.S9 / f"HF20-S9-F{y % 100}-H4-MAG-S42/oos_scores.parquet",
            columns=["origin_id", "ticker", "return_4h"],
        )
        np.testing.assert_array_equal(f[["origin_id", "ticker"]], original[["origin_id", "ticker"]])
        np.testing.assert_array_equal(f.A, abs(original.return_4h))
        o1 = pd.read_parquet(
            O1 / f"F{y % 100}/oos_scores.parquet", columns=["origin_id", "ticker", "A", "O1"]
        )
        np.testing.assert_array_equal(
            f[["origin_id", "ticker", "A"]], o1[["origin_id", "ticker", "A"]]
        )
        f["O1"] = o1.O1
        factors = co.loc[co.year.eq(y)].set_index("group").c_star.to_dict()
        f[ARM] = decode(f.Mhat.to_numpy(), fold["scale"], f.category.map(factors).to_numpy(float))
        old_rank = f.groupby("origin_id").C0.rank(method="average")
        new_rank = f.groupby("origin_id")[ARM].rank(method="average")
        same = bool(np.array_equal(old_rank.to_numpy(), new_rank.to_numpy()))
        strictly_monotone = f.Mhat.ge(0).all() and f[ARM].gt(0).all()
        if strictly_monotone:
            assert same, "UNEXPECTED_WITHIN_ORIGIN_RANK_CHANGE"
        rank_checks.append(
            dict(year=y, rank_vectors_identical=same, clamp_rows=int(f[ARM].eq(0).sum()))
        )
        frames[y] = f
        cuts = np.unique(
            [
                saved.quantile(f.C0.to_numpy(), q, f.weight.to_numpy())
                for q in np.arange(0.1, 1, 0.1)
            ]
        )
        bins = np.searchsorted(cuts, f.C0, side="left") + 1
        masks = [
            (field, str(label), f[field].eq(label))
            for field in ["category", "slot"]
            for label in f[field].unique()
        ]
        for p in [95, 99]:
            event = f.A.gt(fold["thresholds"][str(p)])
            masks.extend([("tail", f"PREFIX{p}", event), ("tail", f"LE_PREFIX{p}", ~event)])
        masks.extend(
            ("C0_decile", str(n), pd.Series(bins == n, index=f.index)) for n in np.unique(bins)
        )
        for arm in ARMS:
            stat = saved.metrics(f, arm)
            ranked = saved.rank_metrics(f, arm)
            records.append(dict(year=str(y), arm=arm, **stat, **ranked))
            if arm != ARM:
                archived = old_metrics.loc[
                    old_metrics.year.eq(str(y)) & old_metrics.arm.eq(arm)
                ].iloc[0]
                for key, value in {**stat, **ranked}.items():
                    np.testing.assert_allclose(value, archived[key], atol=1e-14, rtol=1e-13)
            if arm in ("B0-RMEAN", "B0-RMED"):
                continue
            low = f.groupby("origin_id")[arm].rank(method="average").le(10.5)
            for field, label, mask in masks:
                g = f.loc[mask]
                s = saved.metrics(g, arm)
                contribution = float((g.weight * (g[arm] - g.A) ** 2).sum())
                s.update(
                    year=str(y),
                    arm=arm,
                    field=field,
                    group=label,
                    weight_mass=float(g.weight.sum()),
                    raw_MSE_contribution=contribution,
                    raw_MSE_loss_share=contribution / stat["raw_MSE"],
                )
                if field == "tail":
                    s["false_low_rank"] = float(np.average(low.loc[mask], weights=g.weight))
                if field == "C0_decile":
                    s.update(C0_min=float(g.C0.min()), C0_max=float(g.C0.max()))
                group_records.append(s)
    assert sum(len(f) for f in frames.values()) == 80260
    assert sum(f.origin_id.nunique() for f in frames.values()) == 4013
    assert sum(f.session_date_et.nunique() for f in frames.values()) == 793
    m = pd.DataFrame(records)
    g = pd.DataFrame(group_records)
    eq = []
    for arm, h in m.groupby("arm", sort=False):
        value = {
            name: float(h[name].mean())
            for name in [
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
        }
        value["ratio"] = value["predicted"] / value["observed"]
        eq.append(
            dict(
                year="EQ",
                arm=arm,
                rows=int(h.rows.sum()),
                origins=int(h.origins.sum()),
                sessions=int(h.sessions.sum()),
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
                origins=int(h.origins.sum()),
                sessions=int(h.sessions.sum()),
                **value,
            )
        )
    g = pd.concat([g, pd.DataFrame(eqg)], ignore_index=True)
    for reference in ["C1a", "M1"]:
        daily: dict[int, pd.Series] = {}
        for y, f in frames.items():
            data = (
                pd.DataFrame(
                    dict(
                        day=f.session_date_et,
                        w=f.weight,
                        d=f.weight * ((f[ARM] - f.A) ** 2 - (f[reference] - f.A) ** 2),
                    )
                )
                .groupby("day")
                .sum()
            )
            daily[y] = data.d / data.w
            interval = saved.block_interval(daily[y])
            mask = m.year.eq(str(y)) & m.arm.eq(ARM)
            baseline = float(m.loc[m.year.eq(str(y)) & m.arm.eq(reference), "raw_MSE"].iloc[0])
            for name, v in interval.items():
                m.loc[mask, f"C3_minus_{reference}_{name}"] = v
            m.loc[mask, f"C3_minus_{reference}_percent"] = 100 * interval["mean"] / baseline
        interval = bootstrap_equal_year(daily)
        mask = m.year.eq("EQ") & m.arm.eq(ARM)
        baseline = float(m.loc[m.year.eq("EQ") & m.arm.eq(reference), "raw_MSE"].iloc[0])
        for name, v in interval.items():
            m.loc[mask, f"C3_minus_{reference}_{name}"] = v
        m.loc[mask, f"C3_minus_{reference}_percent"] = 100 * interval["mean"] / baseline
    for reference in ["C0", "C1a", "M1"]:
        match = g.loc[g.arm.eq(reference), ["year", "field", "group", "raw_MSE"]].rename(
            columns={"raw_MSE": f"MSE_{reference}"}
        )
        g = g.merge(match, on=["year", "field", "group"], validate="many_to_one")
        g[f"delta_MSE_vs_{reference}"] = g.raw_MSE - g[f"MSE_{reference}"]
        g[f"percent_MSE_vs_{reference}"] = (
            100 * g[f"delta_MSE_vs_{reference}"] / g[f"MSE_{reference}"]
        )
    m.to_csv(out / "metrics.csv", index=False)
    g.to_csv(out / "groups.csv", index=False)
    verify = dict(
        status="PASS",
        neural_fits=0,
        neural_forward_passes=0,
        ledger_before=138,
        ledger_after=138,
        population=dict(rows=80260, origins=4013, sessions=793),
        rank_checks=rank_checks,
        c1a_reproduction="PASS_ALL_FOUR",
        no_oos_labels_before_factor_freeze=True,
    )
    for path, sha in protocol["preservation_bindings"].items():
        assert saved.digest(Path(path)) == sha
    if (out / "verification.json").exists():
        verify.update(
            {
                key: value
                for key, value in saved.read(out / "verification.json").items()
                if key not in verify
            }
        )
    saved.write(out / "verification.json", verify)
    write_report(out, protocol, co, m, g, verify)


def write_report(
    out: Path, protocol: dict, co: pd.DataFrame, m: pd.DataFrame, g: pd.DataFrame, verify: dict
) -> None:
    notes = (
        saved.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    )
    parts = [
        "# C3 IO calibration — HF20 Stage1 / Session4",
        (
            "**Status: COMPLETE — four valid folds.** One fixed C3-IO-SMEAR "
            "arm; zero neural fits or forward passes. All results "
            "exploratory/post-search."
        ),
        "## Executive decision",
        notes.get("executive", "Scientific interpretation follows the frozen numerical results."),
        "## Experiment and preflight",
        (
            "A=abs(log(P_endpoint/P_origin)); existing four-trading-hour "
            "endpoints and the exact original20-stock tensor order are "
            "preserved. On regular full sessions, origin slots09:30/10:30/11:30 map to "
            "INTRADAY;12:30/13:30/14:30/15:30 map to saved OVERNIGHT, meaning "
            "overnight-crossing. On saved scheduled early-close days, some morning "
            "origins also cross sessions. Executed category and endpoint keys take "
            "precedence over the prompt's simplified slot map: these existing labels "
            "are preserved, verified against saved exchange session-close metadata, "
            "and enumerated in protocol.json. No outcome-based regrouping occurs. "
            "The closing stub, genuine endpoints and "
            "price-only timing before approximate origin+2min issuance are "
            "unchanged. No new jump label or information set."
        ),
        (
            "The saved September-restricted encoder/scale supplies both "
            "October–December independent calibration and next-year C0 scores. "
            "OOS keys are matched to saved S4 eligibility/DesignA role indices "
            "and original S9 score keys, preserving the previously "
            "verified48-step embargo. Calibration labels mature before the "
            "saved December cutoff and outer evaluation. Receipts/result hashes"
            " bind the same frozen network across both populations; no "
            "checkpoint is opened or called here."
        ),
        saved.markdown(pd.DataFrame(protocol["coverage"])),
        (
            "q=exp(log1p(A/s)−unconstrained_Mhat). c0=Ecal,w[q]; "
            "c_raw,g=Ecal,w[q|g]. Session mass is each group's existing "
            "row-weight sum per session, normalized over sessions with that "
            "group. n_eff=1/sum(p_day²), rho=n_eff/(n_eff+25), "
            "c_star=c0+rho(c_raw−c0). Ahat_C3=s*max(0,exp(Mhat)*c_star−1). κ=25"
            " session-equivalents was fixed before category moments; no grid, "
            "stock effects, seven-slot fitting, clipping, trimming or post-hoc "
            "renormalization."
        ),
        (
            "All-four preflight and protocol.json were saved before calculating"
            " new category moments. Preflight projected OOS keys/predictions "
            "but no OOS labels. All eight factors were frozen in "
            "calibration_coefficients.csv before OOS outcomes were read for "
            "scoring. Existing global c0 and saved C1a/C0/M1 decoders reproduce"
            " on both calibration and OOS rows within atol1e−14/rtol1e−13. This"
            " is reconstruction of old controls, not a new arm. Empty/nonfinite"
            " category moments block rather than fall back."
        ),
        "## Coefficients and precision",
        saved.markdown(
            co[
                [
                    "year",
                    "group",
                    "scale",
                    "c0",
                    "c_raw",
                    "n_eff",
                    "rho",
                    "c_star",
                    "delta_from_global",
                ]
            ]
        ),
        saved.markdown(
            co[
                [
                    "year",
                    "group",
                    "sessions",
                    "origins",
                    "rows",
                    "weight_mass",
                    "q_max",
                    "top10_share",
                    "top1pct_share",
                    "global_q_max",
                    "global_top10_share",
                    "global_top1pct_share",
                ]
            ]
        ),
        (
            "n_eff is a weight-concentration measure in sessions, not an "
            "independent-observation count or posterior probability. Shrinkage "
            "is a fixed convention. Calibration tails have56/50/48/40 sessions;"
            " F24 precision remains limited. Top10/top1% shares use weighted q "
            "contributions, not the largest q alone. No trimming is used. All "
            "values remain finite; concentration diagnostics are reported "
            "without OOS repair."
        ),
        "## Annual and equal-year matched scores",
        saved.markdown(
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
            "Means/MAE/bias are raw absolute log-return units; MSE is squared "
            "log-return units. Annual weights: equal20 stocks/origin → equal "
            "eligible origins/session → equal sessions/year. EQ averages four "
            "annual metrics; EQ ratio is the ratio of equal-year means. Other "
            "B0 arms remain included; B0-RMED targets a median and is chiefly "
            "an MAE comparator. All eight existing comparator forecasts are "
            "read unchanged, never refitted."
        ),
        "Paired C3-minus-calibrated raw MSE (negative favors C3):",
        saved.markdown(
            m.loc[
                m.arm.eq(ARM),
                [
                    "year",
                    "C3_minus_C1a_mean",
                    "C3_minus_C1a_low",
                    "C3_minus_C1a_high",
                    "C3_minus_C1a_percent",
                    "C3_minus_M1_mean",
                    "C3_minus_M1_low",
                    "C3_minus_M1_high",
                    "C3_minus_M1_percent",
                ],
            ]
        ),
        (
            "400 whole-calendar-month bootstrap draws, seed22042, using "
            "executed annual routine and year-stratified equal-year routine. "
            "Full sessions/stocks/overlapping origins remain together. Bounds "
            "are descriptive95% intervals conditional on these fitted "
            "encoders/factors; they do not refit calibration tails or adjust "
            "for model/hypothesis/κ selection after repeated research. No IID "
            "stock-row or four-year significance claim."
        ),
        "## Clocks, tails and ordinary periods",
        notes.get("groups", ""),
        saved.markdown(
            g.loc[
                g.year.eq("EQ") & g.arm.eq(ARM) & g.field.ne("C0_decile"),
                [
                    "field",
                    "group",
                    "rows",
                    "sessions",
                    "raw_MSE",
                    "raw_MAE",
                    "observed",
                    "predicted",
                    "ratio",
                    "weight_mass",
                    "raw_MSE_loss_share",
                    "percent_MSE_vs_C1a",
                    "percent_MSE_vs_M1",
                ],
            ]
        ),
        (
            "All annual clocks/categories, prefix95/99 cohorts and complements "
            "are in groups.csv. Thresholds are the saved September-prefix "
            "weighted raw-A quantiles, never OOS-fitted. Conditional errors "
            "normalize original group weight within year, then average years. "
            "Event loss shares average unconditional annual contributions "
            "divided by equal-year total MSE; no equal-row pooling or "
            "independent-strata claim. These are retrospective outcome cohorts,"
            " not a fitted event detector; even an ideal conditional mean can "
            "underpredict a cohort selected on large realized outcomes."
        ),
        "## Ranking and reliability",
        saved.markdown(
            m.loc[
                m.year.eq("EQ") | m.arm.eq(ARM),
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
        saved.markdown(pd.DataFrame(verify["rank_checks"])),
        (
            "Every stock at an origin shares the same positive category factor "
            "and scale. With no clamp-induced ties, the decoder is strictly "
            "increasing, so within-origin ranks must remain identical. This is "
            "calibration, not new rank/jump information. Spearman uses average "
            "ranks; pair concordance gives score ties half credit and excludes "
            "actual ties (chance0.5). Top/bottom4 uses fractional boundary-tie "
            "membership (chance0.2). Any clamp/tie exception is disclosed "
            "above."
        ),
        saved.markdown(
            g.loc[
                g.year.eq("EQ") & g.arm.eq(ARM) & g.field.eq("C0_decile"),
                ["group", "observed", "predicted", "ratio", "raw_MSE", "raw_MAE"],
            ]
        ),
        (
            "Reliability bins are ten predeclared weighted empirical C0-score "
            "deciles per year, shared across arms. Numeric "
            "ranges/counts/session coverage are in groups.csv. Boundaries are "
            "descriptive historical bins, not future calibration thresholds. EQ"
            " bins average corresponding annual percentile groups."
        ),
        "## Scientific decision and limits",
        notes.get("decision", "Decision awaits reviewed frozen results."),
        "## Reproduction, preservation and stop",
        (
            f"`.venv/bin/python -m lstm_data.hf20_mag_c3_io --out {out} --preflight` "
            "performs saved-artifact checks; initial `--run` computes only this C3 arm once. "
            "`--report` reuses frozen coefficient CSV, never refits, and replays the "
            "saved-score tables. The coefficient file is single-use/exclusive; no C3 "
            "score Parquet or historical predictor copy is needed because old Mhat "
            "plus fixed coefficients reproduces the vector."
        ),
        (
            "Sources: Session2 F21 parent and Session2B F22–F24 roots listed in"
            " protocol.json; each "
            "calibration_scores.parquet/oos_scores.parquet, "
            "restricted_target.json, restricted_recipe.json, coefficients.json "
            "and result.json. O1 scores remain under "
            "Session3/Fxx/oos_scores.parquet. Saved S4 eligibility metadata, "
            "original S9 keys and Session3 role_indices.npz verify identity. No"
            " raw/minute/hourly feature observations, checkpoint, training "
            "runner or source rebuild is used."
        ),
        (
            "New files only: protocol.json, calibration_coefficients.csv, "
            "metrics.csv, groups.csv, verification.json, interpretation.json, "
            "this report, one module and focused fixtures, plus the usual "
            "reports/codex_sessions handoff. The neural registry/journal and "
            "all previous assets remain unchanged at138/200. No2025/2026 "
            "numerical access/hash, data download, dashboard edit, strategy or "
            "extra fitting arm."
        ),
        verify.get("final_summary", "Final static/replay verification is recorded before handoff."),
        (
            "STOP for researcher review. No Stage2 target/model, additional "
            "calibration/objective, event head, trading threshold, "
            "options/backtest or protected confirmation."
        ),
    ]
    (out / "C3_IO_CALIBRATION_REPORT.md").write_text("\n\n".join(parts) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    out = args.out
    if args.report:
        evaluate(out)
        return
    if (out / "calibration_coefficients.csv").exists():
        raise SystemExit("NO_REFIT: C3 coefficients already frozen; use --report")
    protocol, calibrations = preflight(out)
    if args.run:
        rows = []
        for fold in protocol["folds"]:
            rows.extend(
                dict(year=fold["year"], **r)
                for r in fit_categories(calibrations[fold["year"]], fold["scale"])
            )
        pd.DataFrame(rows).to_csv(out / "calibration_coefficients.csv", index=False, mode="x")
        evaluate(out)


if __name__ == "__main__":
    main()
