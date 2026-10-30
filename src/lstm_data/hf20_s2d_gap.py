"One separately gated genuine overnight-gap study on a masked stock-day panel."

from __future__ import annotations

import argparse
import gc
import hashlib
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
from . import hf20_overnight_specialist as previous
from .hf20_s4_clock import sessions

OUT = Path("reports/experiments/hf20_s9_mag_stage2_s2d_masked_gap_2026-10-28")
AUDIT = Path(("reports/experiments/hf20_s9_mag_stage2_s2c_s2d_readonly_coverage_audit_2026-10-28"))
PARENT = Path("reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28")
SOURCE = b.S4 / "opening_reaudit_v2"
TARGET = SOURCE / "S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet"
RAW = "S2D-RAW"
SMEAR = "S2D-SMEAR"
MEAN = "B0-GAP-RMEAN"
MEDIAN = "B0-GAP-RMED"
LOCKED = "B0-GAP-RECENT20-LOCKED"
LIVE = "B0-GAP-RECENT20-LIVE"
ARMS = (SMEAR, RAW, MEAN, MEDIAN, LOCKED, LIVE)
ROLES = ("inner_train", "selector", "restricted_refit", "calibration", "oos")


def freeze(path: Path, data: dict) -> None:
    """Immutable receipts; no historical output may be overwritten."""
    with path.open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)


def panel_weights(mask: np.ndarray) -> np.ndarray:
    """Equal valid stocks/date then equal dates; no global equal-row pooling."""
    n = mask.sum(1)
    if mask.ndim != 2 or mask.shape[1] != 20 or (n < 10).any():
        raise ValueError("ADMITTED_TEN_TO_TWENTY_PANEL_REQUIRED")
    return mask / (len(mask) * n[:, None])


def masked_loss(
    mhat: torch.Tensor, signed: torch.Tensor, mask: torch.Tensor, scale: float
) -> torch.Tensor:
    "Missing labels never enter target arithmetic; uniform sampled session mean."
    assert mhat.shape == signed.shape == mask.shape and scale > 0
    n = mask.sum(1)
    if bool(n.lt(10).any()):
        raise ValueError("TEN_LABEL_GATE_BEFORE_LOSS")
    target = torch.log1p(signed[mask].abs() / scale)
    weights = (1 / n.to(mhat.dtype))[:, None].expand_as(mhat)[mask] / len(mask)
    return ((mhat[mask] - target).square() * weights).sum()


def calendar_and_sources(
    rows: pd.DataFrame, *, numeric: bool
) -> tuple[np.ndarray, np.ndarray, pd.Series, np.ndarray]:
    """Gap source/maturity is independent of four-hour label eligibility."""
    calendar = sessions("2010-07-01", "2025-01-10")
    dates = calendar.index.astype(str).str[:10]
    next_open = rows.session_date_et.map(pd.Series(calendar.open.to_numpy()[1:], index=dates[:-1]))
    if next_open.isna().any():
        raise ValueError("NEXT_SCHEDULED_OPEN_MISSING")
    next_day = (
        pd.to_datetime(next_open, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.strftime("%Y-%m-%d")
    )
    candidate = (rows.regular_session & rows.slot.eq("15:30")).to_numpy()
    selected = np.flatnonzero(candidate)
    f = pd.read_parquet(
        TARGET,
        columns=["origin_id", "ticker", "genuine_session_end_price", "next_session_open"],
        filters=[("origin_id", "in", rows.iloc[selected].origin_id.tolist())],
    )
    np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.iloc[selected].origin_id)
    assert f.ticker.tolist() == list(b.SYMBOLS) * len(selected)
    close = np.full((len(rows), 20), np.nan)
    opened = close.copy()
    close[selected] = f.genuine_session_end_price.to_numpy().reshape(-1, 20)
    opened[selected] = f.next_session_open.to_numpy().reshape(-1, 20)
    basis = np.ones_like(close, dtype=bool)
    basis[:, b.SYMBOLS.index("COP")] = rows.session_date_et.lt("2012-05-01").eq(
        next_day.lt("2012-05-01")
    )
    valid = (
        candidate[:, None]
        & np.isfinite(close)
        & (close > 0)
        & np.isfinite(opened)
        & (opened > 0)
        & basis
    )
    gap = np.full(close.shape, np.nan)
    if numeric:
        gap[valid] = np.log(opened[valid] / close[valid])
        assert np.isfinite(gap[valid]).all()
    return valid, gap, pd.to_datetime(next_open, utc=True) + pd.Timedelta(minutes=2), candidate


def first_dates(grid: pd.DataFrame, rows: pd.DataFrame) -> np.ndarray:
    result = np.full(len(rows), "0000", dtype=object)
    good = rows.first_step.ge(0)
    result[good] = grid.session_date_et.to_numpy()[rows.loc[good, "first_step"].to_numpy(int)]
    return result


def role_positions(
    rows: pd.DataFrame, first: np.ndarray, valid: np.ndarray, maturity: pd.Series, item: dict
) -> np.ndarray:
    """No four-hour eligible/label-maturity flag participates in admission."""
    take = (
        rows.source_input_eligible
        & rows.regular_session
        & rows.slot.eq("15:30")
        & rows.session_date_et.between(item["start"], item["cutoff"])
        & (first > item["embargo_after"])
        & maturity.lt(b.limit(item["cutoff"]))
        & (valid.sum(1) >= 10)
    )
    return np.flatnonzero(take)


def available_history(
    bank: np.ndarray, valid: np.ndarray, maturity: pd.Series, issuance: pd.Timestamp, ticker: int
) -> np.ndarray:
    """Only previously matured genuine observed gaps, never the current night."""
    return bank[valid[bank, ticker] & maturity.iloc[bank].lt(issuance).to_numpy()]


def preflight(out: Path) -> None:
    "Freeze protocol before bounded price certification; all folds before fitting."
    out.mkdir(exist_ok=False)
    (out / ".gitignore").write_text("*.pt\n*.parquet\n")
    pointer = b.read(b.POINTER)
    journal = Path(pointer["real_journal"])
    last = json.loads(journal.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 162
    assert pointer["effective_ceiling"] == 300 and 162 + 4 <= 300
    assert journal == PARENT / "neural_starts.jsonl"
    assert b.read(PARENT / "verification.json")["status"] == "COMPLETE"
    paths = [
        TARGET,
        SOURCE / "S4_ORIGIN_SOURCE_ELIGIBILITY.parquet",
        SOURCE / "S4_SOURCE_POLICY.json",
        SOURCE / "S4_NUMERICAL_SOURCE_READS.csv",
        AUDIT / "S2D_ROLE_GATES.csv",
        AUDIT / "audit_receipt.json",
        o1.REF / "role_counts.csv",
        journal,
        PARENT / "S2C_CA_PROTOCOL.json",
        Path(
            (
                "reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28/s2d_overnight_hold/protocol_v2.json"
            )
        ),
    ]
    protocol = dict(
        kind="S2D_GENUINE_GAP_MASKED_PANEL_V1",
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        seed=42,
        target=(
            "A_gap=abs(log(genuine adjusted next09:30 minute open / genuine current "
            "full-session final-minute close))"
        ),
        forecast=(
            "normal full-session15:30 only; approximate15:32 issuance before "
            "future16:00 close; not executable fills"
        ),
        population=(
            "all20 original FT16 input eligibility; >=10 genuine labels/date; one "
            "stock-date gap; no early close"
        ),
        weights=(
            "1/(eligible_role_sessions*n_valid_date); zero on missing labels; equal annual years"
        ),
        chronology=(
            "exact saved DesignA nominal roles; independently derived gap "
            "next-open+2min maturity and48-step first-input embargo"
        ),
        minimums=dict(
            prefix_sessions=252,
            selector_sessions=50,
            calibration_sessions=25,
            oos_sessions=100,
            selector_calibration_per_month=5,
            oos_months=12,
        ),
        model=(
            "original one-layerH32/48x16 FT16/6433 params/final hidden "
            "dropout.10/scalar linear M_gap; no clock vector or auxiliaries"
        ),
        optimizer=(
            "seed42 CPUfloat32;AdamW lr.001 betas(.9,.999)eps1e-8,matrix "
            "decay.01,bias0,clip1,16 sessions;shuffle42+epoch"
        ),
        selector=(
            "main gap M-MSE;first finite "
            "nonnegative,qualified<=.999best,min12,patience10,max60;fresh "
            "selected-epoch refit"
        ),
        scale=(
            "own gap-phase weighted-left-median A_gap, floor1e-8; independent "
            "input-only FT16 prefix recipes"
        ),
        calibration=(
            "own frozen September model/scale,own Oct-Dec gap residual global exp "
            "moment;primary SMEAR;RAW diagnostic;no variants/trimming"
        ),
        baselines=dict(
            primary=MEAN,
            selection="NONE;all named comparisons retained",
            mean=MEAN,
            median=MEDIAN,
            recent_locked=LOCKED,
            recent_live=LIVE,
            locked_history="through-September role only;recent20 observed per stock",
            live_history=(
                "normal15:30,input-eligible,>=10 valid source bank since2011-04-01;20 "
                "most recent per-stock gaps matured strictly before each15:32 issuance; "
                "includes past calibration/OOS labels;more information diagnostic"
            ),
            history_minimum=20,
            optional_EWMA="NOT_INCLUDED;not already verified/reused",
        ),
        baseline_weighting=(
            "per-stock mean/left-median conditional on phase panel weights;recent20 "
            "arithmetic mean of20 actual observed mature gaps;no missing-value "
            "fallback"
        ),
        ranking=(
            "same valid stocks/date;average ranks;undefined Spearman excluded and "
            "valid-session count disclosed;fractional top/bottom4 ties;chance4/n;pair"
            " ties.5;false-low fractional bottom half"
        ),
        reliability=(
            "fixed descriptive RAW-score deciles per outer year;shared membership "
            "across arms;not deployable calibration"
        ),
        tails=("own restricted gap-prefix weighted95/99,not OOS thresholds;ordinary complements"),
        uncertainty=dict(
            draws=400,
            seed=22042,
            blocks=(
                "whole calendar months/session panels,year stratified equal "
                "years;descriptive conditional only"
            ),
        ),
        protected=(
            "No2025 market or protected2026 values/paths/hashes;calendar-only "
            "next-session dates throughJan2025"
        ),
        no_network=True,
        caps=b.CAPS,
        ledger_before=162,
        ceiling=300,
        max_charged_starts=4,
        max_neural_phases=8,
        previous_pointer=pointer,
        preservation_bindings={str(p): b.digest(p) for p in paths},
        original_four_hour_models_frozen=True,
        strict20_blocked_namespace_preserved=True,
    )
    freeze(out / "protocol.json", protocol)
    grid, rows = b.metadata()
    first = first_dates(grid, rows)
    # Price availability certification only, no gap outcomes/score inspected yet.
    valid, _, maturity, candidate = calendar_and_sources(rows, numeric=False)
    assert not rows.loc[candidate, "session_date_et"].duplicated().any()
    assert rows.loc[candidate, "slot"].eq("15:30").all()
    assert (
        (rows.loc[candidate, "session_close"] - rows.loc[candidate, "entry_end_utc"])
        .eq(pd.Timedelta(minutes=30))
        .all()
    )
    good = candidate & rows.source_input_eligible.to_numpy()
    assert rows.loc[good, "entry_index"].sub(rows.loc[good, "first_step"]).eq(47).all()
    ends = grid.hour_end_utc.to_numpy()[rows.loc[good, "entry_index"].to_numpy(int)]
    np.testing.assert_array_equal(ends, rows.loc[good, "entry_end_utc"])
    assert (grid.hour_end_utc - grid.hour_start_utc).eq(pd.Timedelta(hours=1)).all()
    basis_failure = (
        rows.session_date_et.lt("2012-05-01")
        != (maturity - pd.Timedelta(minutes=2))
        .dt.tz_convert("America/New_York")
        .dt.strftime("%Y-%m-%d")
        .lt("2012-05-01")
    ).to_numpy()
    assert not valid[basis_failure, b.SYMBOLS.index("COP")].any()
    audit = b.read(AUDIT / "audit_receipt.json")
    assert b.digest(TARGET) == audit["source_paths"][str(TARGET)]["sha256"]
    counts = pd.read_csv(o1.REF / "role_counts.csv")
    expected = pd.read_csv(AUDIT / "S2D_ROLE_GATES.csv")
    expected = expected.loc[expected.threshold.eq(10)]
    bank = np.flatnonzero(
        candidate
        & rows.source_input_eligible.to_numpy()
        & rows.session_date_et.ge("2011-04-01").to_numpy()
        & (valid.sum(1) >= 10)
    )
    plans = {}
    records = []
    stock = []
    history = []
    failures = []
    monthly = []
    excluded = []
    for y in b.YEARS:
        plans[y] = {}
        for item in counts.loc[counts.year.eq(y)].to_dict("records"):
            role = item["role"]
            ix = role_positions(rows, first, valid, maturity, item)
            plans[y][role] = ix
            n = valid[ix].sum(1)
            w = panel_weights(valid[ix])
            assert np.isclose(w.sum(), 1) and np.allclose(w.sum(1), 1 / len(ix))
            h = rows.iloc[ix]
            span = pd.period_range(
                str(item["start"])[:7], str(item["cutoff"])[:7], freq="M"
            ).astype(str)
            monthcounts = h.session_date_et.str[:7].value_counts().reindex(span, fill_value=0)
            need = (
                252
                if role in ["inner_train", "restricted_refit"]
                else {"selector": 50, "calibration": 25, "oos": 100}[role]
            )
            reasons = []
            if len(ix) < need:
                reasons.append("SESSIONS_BELOW_MINIMUM")
            if role in ["selector", "calibration"] and monthcounts.min() < 5:
                reasons.append("MONTH_BELOW5")
            if role == "oos" and int(monthcounts.gt(0).sum()) != 12:
                reasons.append("OOS_MISSING_MONTH")
            old = expected.loc[expected.fold.eq(y) & expected.role.eq(role)].iloc[0]
            if len(ix) != old.sessions or int(n.sum()) != old.valid_stock_days:
                reasons.append("AUDIT_COUNT_MISMATCH")
            if reasons:
                failures.append(f"F{y % 100}/{role}:" + ";".join(reasons))
            records.append(
                dict(
                    year=y,
                    role=role,
                    start=item["start"],
                    cutoff=item["cutoff"],
                    embargo_after=item["embargo_after"],
                    sessions=len(ix),
                    stock_days=int(n.sum()),
                    min_valid_stocks=int(n.min()),
                    max_valid_stocks=int(n.max()),
                    months=int(monthcounts.gt(0).sum()),
                    minimum_month_sessions=int(monthcounts.min()),
                    first_date=h.session_date_et.min(),
                    last_date=h.session_date_et.max(),
                    status="BLOCKED" if reasons else "PASS",
                    reason=";".join(reasons),
                    mask_sha256=hashlib.sha256(valid[ix].tobytes()).hexdigest(),
                    role_index_sha256=hashlib.sha256(ix.tobytes()).hexdigest(),
                )
            )
            for month, number in monthcounts.items():
                monthly.append(dict(year=y, role=role, month=month, sessions=int(number)))
            for j, ticker in enumerate(b.SYMBOLS):
                for month in (
                    ["ALL", *span] if role in ["selector", "calibration", "oos"] else ["ALL"]
                ):
                    take = (
                        np.ones(len(ix), bool)
                        if month == "ALL"
                        else h.session_date_et.str.startswith(month).to_numpy()
                    )
                    stock.append(
                        dict(
                            year=y,
                            role=role,
                            month=month,
                            ticker=ticker,
                            admitted_dates=int(take.sum()),
                            valid_gap_stock_days=int(valid[ix[take], j].sum()),
                            missing_gap_on_admitted_dates=int((~valid[ix[take], j]).sum()),
                        )
                    )
            base = (
                candidate & rows.session_date_et.between(item["start"], item["cutoff"]).to_numpy()
            )
            inp = rows.source_input_eligible.to_numpy()
            emb = first > item["embargo_after"]
            mat = maturity.lt(b.limit(item["cutoff"])).to_numpy()
            excluded.append(
                dict(
                    year=y,
                    role=role,
                    nominal_normal_1530=int(base.sum()),
                    input_excluded=int((base & ~inp).sum()),
                    embargo_excluded=int((base & inp & ~emb).sum()),
                    maturity_excluded=int((base & inp & emb & ~mat).sum()),
                    fewer10_excluded=int((base & inp & emb & mat & (valid.sum(1) < 10)).sum()),
                )
            )
        for left, right in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(plans[y][left], plans[y][right]).size
        for phase, role, apply_roles in [
            ("initial", "inner_train", ["selector"]),
            ("restricted", "restricted_refit", ["calibration", "oos"]),
        ]:
            train = plans[y][role]
            for j, ticker in enumerate(b.SYMBOLS):
                n = int(valid[train, j].sum())
                hcount = min(
                    len(
                        available_history(
                            bank, valid, maturity, pd.Timestamp(rows.issuance_utc.iloc[pos]), j
                        )
                    )
                    for apply in apply_roles
                    for pos in plans[y][apply]
                )
                if min(n, hcount) < 20:
                    failures.append(f"F{y % 100}/{phase}/{ticker}:BASELINE_HISTORY_LT20")
                history.append(
                    dict(
                        year=y,
                        phase=phase,
                        ticker=ticker,
                        prefix_genuine_gap_count=n,
                        minimum_mature_history_at_evaluation=hcount,
                        all_required_baselines_available=min(n, hcount) >= 20,
                    )
                )
    pd.DataFrame(records).to_csv(out / "role_counts.csv", index=False)
    pd.DataFrame(stock).to_csv(out / "stock_month_coverage.csv", index=False)
    pd.DataFrame(monthly).to_csv(out / "monthly_role_counts.csv", index=False)
    pd.DataFrame(excluded).to_csv(out / "eligibility_exclusions.csv", index=False)
    pd.DataFrame(history).to_csv(out / "baseline_history.csv", index=False)
    np.savez_compressed(
        out / "role_masks.npz",
        gap_valid=valid,
        history_bank=bank,
        **{f"F{y % 100}_{role}": ix for y, roles in plans.items() for role, ix in roles.items()},
    )
    freeze(
        out / "source_validation.json",
        dict(
            status="PASS" if not failures else "BLOCKED",
            source=str(TARGET),
            source_sha256=b.digest(TARGET),
            source_policy=str(SOURCE / "S4_SOURCE_POLICY.json"),
            certification=(
                "only saved normal15:30 genuine close/open finite "
                "positive/action-compatible; no raw minute or new source"
            ),
            per_stock_positive_finite=True,
            cop_basis_excluded=True,
            true_close=(
                "session_close minus1min genuine minute close;not15:30 or official auction claim"
            ),
            open="next scheduled09:30 genuine minute open",
            original_48_full_hour_input_end="exactly15:30, strictly before future16:00 close",
            market_source_stop="2024-12-31",
            numeric_gap_values_used=False,
            source_version_matches_audit=True,
        ),
    )
    freeze(
        out / "preflight.json",
        dict(
            status="PASS_ALL_FOUR" if not failures else "BLOCKED",
            failures=failures,
            role_counts=records,
            ledger_before=162,
            ceiling=300,
            role_masks_sha256=b.digest(out / "role_masks.npz"),
            resources=b.resources(out),
            baselines_history_minimum=min(x["prefix_genuine_gap_count"] for x in history),
            minimum_asof_bank_history=min(
                x["minimum_mature_history_at_evaluation"] for x in history
            ),
            no_OOS_gap_values_or_scores_inspected=True,
        ),
    )
    if failures:
        (out / "S2D_MASKED_GAP_REPORT.md").write_text(
            "# S2-D masked gap\n\n**BLOCKED before fitting.**\n\n" + "\n".join(failures)
        )
        raise ValueError("BLOCKED_ALL_FOLD_GATE", failures)


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
    elif args.run:
        run(OUT)
    elif args.report:
        report(OUT)
    else:
        parser.error("choose --preflight, --run or --report")


def load_roles(out: Path) -> tuple[dict, np.ndarray, np.ndarray]:
    data = np.load(out / "role_masks.npz", allow_pickle=False)
    plans = {y: {role: data[f"F{y % 100}_{role}"] for role in ROLES} for y in b.YEARS}
    return plans, data["gap_valid"], data["history_bank"]


def prefix_baselines(
    rows: pd.DataFrame, pos: np.ndarray, valid: np.ndarray, gap: np.ndarray
) -> dict:
    "Only admitted gap-prefix labels; stock mean/median condition panel weights."
    weights = panel_weights(valid[pos])
    a = abs(gap[pos])
    means = []
    medians = []
    recent = []
    counts = []
    dates = []
    for j in range(20):
        take = valid[pos, j]
        values = a[take, j]
        w = weights[take, j]
        if len(values) < 20:
            raise ValueError("BASELINE_PREFIX_HISTORY_LT20")
        means.append(float(w @ values / w.sum()))
        medians.append(b.quantile(values, 0.5, w))
        recent.append(float(values[-20:].mean()))
        counts.append(len(values))
        selected = pos[take][-20:]
        dates.append(
            dict(
                first=str(rows.session_date_et.iloc[selected[0]]),
                last=str(rows.session_date_et.iloc[selected[-1]]),
            )
        )
    return dict(
        stock_order=list(b.SYMBOLS),
        mean=means,
        median=medians,
        recent20=recent,
        counts=counts,
        recent20_dates=dates,
        selection="NONE;fixed RMEAN primary;all controls reported",
    )


def recent_live(
    rows: pd.DataFrame,
    pos: np.ndarray,
    bank: np.ndarray,
    valid: np.ndarray,
    gap: np.ndarray,
    maturity: pd.Series,
) -> np.ndarray:
    result = np.empty((len(pos), 20))
    for k, index in enumerate(pos):
        for j in range(20):
            history = available_history(
                bank, valid, maturity, pd.Timestamp(rows.issuance_utc.iloc[index]), j
            )
            if len(history) < 20:
                raise ValueError("LIVE_HISTORY_LT20_NO_FALLBACK")
            chosen = history[-20:]
            assert maturity.iloc[chosen].lt(rows.issuance_utc.iloc[index]).all()
            result[k, j] = abs(gap[chosen, j]).mean()
    return result


def prepare(
    out: Path, c: b.Components, rows: pd.DataFrame, gap: np.ndarray, valid: np.ndarray, plans: dict
) -> dict:
    """All8 feature recipes and own gap scales before first neural STARTED."""
    folds = {}
    for y in b.YEARS:
        dest = out / f"F{y % 100}"
        dest.mkdir()
        old = b.read(o1.OUT / f"F{y % 100}/phases.json")
        phases = {}
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            cutoff = old["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(c.grid, rows, cutoff), cutoff, approved=True
            )
            ref = o1.OUT / f"F{y % 100}/{phase}_recipe.json"
            assert recipe == b.read(ref)
            ix = plans[y][role]
            mask = valid[ix]
            w = panel_weights(mask)[mask]
            a = abs(gap[ix][mask])
            scale = max(b.quantile(a, 0.5, w), 1e-8)
            phases[phase] = dict(
                scale_gap=scale,
                cutoff=cutoff,
                input_recipe_reference=str(ref),
                prefix_sessions=len(ix),
                prefix_stock_days=int(mask.sum()),
                baselines=prefix_baselines(rows, ix, valid, gap),
                gap_tail_thresholds={str(q): b.quantile(a, q / 100, w) for q in [95, 99]},
            )
        folds[y] = dict(year=y, phases=phases)
        freeze(dest / "phase_recipes.json", folds[y])
    freeze(
        out / "phase_parity.json",
        dict(status="EIGHT_INPUT_RECIPES_EXACT_OWN_GAP_SCALES", folds=folds),
    )
    return folds


def gap_frame(
    rows: pd.DataFrame, pos: np.ndarray, valid: np.ndarray, gap: np.ndarray, maturity: pd.Series
) -> pd.DataFrame:
    """Only new genuine gap keys; explicitly named A_gap and gap maturity."""
    fields = ["origin_id", "session_date_et", "slot", "entry_end_utc", "issuance_utc"]
    f = rows.iloc[pos][fields].loc[rows.iloc[pos].index.repeat(20)].reset_index(drop=True)
    f["ticker"] = np.tile(b.SYMBOLS, len(pos))
    f["gap_maturity_utc"] = np.repeat(maturity.iloc[pos].to_numpy(), 20)
    f["n_valid"] = np.repeat(valid[pos].sum(1), 20)
    f["weight"] = panel_weights(valid[pos]).ravel()
    f["A_gap"] = abs(gap[pos]).ravel()
    f = f.loc[valid[pos].ravel()].reset_index(drop=True)
    assert not f[["session_date_et", "ticker"]].duplicated().any()
    assert np.allclose(f.groupby("session_date_et").weight.sum(), 1 / len(pos))
    assert np.isfinite(f.A_gap).all() and f.A_gap.ge(0).all()
    return f


def journal(out: Path, y: int, status: str, detail: dict) -> None:
    path = out / "neural_starts.jsonl"
    protocol = b.read(out / "protocol.json")
    history = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    count = sum(x["status"] == "STARTED" for x in history)
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["previous_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert (
            count < 4
            and y == b.YEARS[count]
            and (not history or history[-1]["status"] == "COMPLETED")
        )
        assert b.read(out / "readiness.json")["status"] == "PASS"
        assert (
            b.read(out / "phase_parity.json")["status"]
            == "EIGHT_INPUT_RECIPES_EXACT_OWN_GAP_SCALES"
        )
        b.resources(out)
    record = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        experiment="S2D-MASKED-GAP",
        year=y,
        status=status,
        global_started_pairs=162 + count + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
    )
    with path.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    binding = dict(path=str(out / "protocol.json"), sha256=b.digest(out / "protocol.json"))
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=31,
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
    model: b.SharedLSTM,
    opt: torch.optim.AdamW,
    number: int,
    valid: np.ndarray,
) -> dict:
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + number).shuffle(days)
    norms = []
    losses = []
    model.train()
    for k in range(0, len(days), 16):
        ix = pos[np.concatenate([groups[d] for d in days[k : k + 16]])]
        x = view.x(ix)
        assert x.shape == (len(ix), 20, 48, 16)
        opt.zero_grad()
        mhat = model(torch.from_numpy(x.reshape(-1, 48, 16))).reshape(-1, 20)
        loss = masked_loss(
            mhat,
            torch.from_numpy(view.r[ix].astype(np.float32)),
            torch.from_numpy(valid[ix]),
            view.scale,
        )
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_GAP_LOSS")
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True)
        norms.append(float(norm))
        losses.append(float(loss.detach()))
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms),
        gradient_norm_max=max(norms),
        clipped_batches=sum(v > 1 for v in norms),
        batch_loss_mean=float(np.mean(losses)),
    )


def run_fold(
    out: Path,
    y: int,
    c: b.Components,
    rows: pd.DataFrame,
    gap: np.ndarray,
    valid: np.ndarray,
    pos: dict,
    fold: dict,
    maturity: pd.Series,
    bank: np.ndarray,
) -> None:
    dest = out / f"F{y % 100}"
    started = time.monotonic()
    trace = []
    initial = fold["phases"]["initial"]
    restricted = fold["phases"]["restricted"]
    inner = b.View(
        c, rows, gap, b.read(Path(initial["input_recipe_reference"])), initial["scale_gap"]
    )
    model = b.model_for("MAG")
    assert sum(p.numel() for p in model.parameters()) == 6433
    initial_hash = b.initial_hash(model)
    opt = b.optimizer(model)
    assert not opt.state
    selector = b.Selector()
    best = {}
    journal(
        out,
        y,
        "STARTED",
        dict(run_id=f"HF20-S2D-GAP-F{y % 100}-S42", parameters=6433, phase="initial"),
    )
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            tick = time.monotonic()
            train = train_epoch(inner, pos["inner_train"], model, opt, n, valid)
            z = b.predict(inner, pos["selector"], model)
            value = float(
                masked_loss(
                    torch.from_numpy(z),
                    torch.from_numpy(gap[pos["selector"]].astype(np.float32)),
                    torch.from_numpy(valid[pos["selector"]]),
                    initial["scale_gap"],
                )
            )
            if selector.observe(value):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_gap_M_MSE=value,
                    selected=selector.selected,
                    seconds=time.monotonic() - tick,
                    **train,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2D-GAP", y, "selector", n, value, "selected", selector.selected, flush=True)
        model.load_state_dict(best)
        freeze(
            dest / "selection.json",
            dict(
                vars(selector),
                initial_scale_gap=initial["scale_gap"],
                selected_initial_hash=b.initial_hash(model),
            ),
        )
        journal(
            out, y, "SELECTED", dict(epoch=selector.selected, raw_minimum_epoch=selector.raw_epoch)
        )
        del model, opt, best
        gc.collect()
        scale = restricted["scale_gap"]
        refit = b.View(c, rows, gap, b.read(Path(restricted["input_recipe_reference"])), scale)
        model = b.model_for("MAG")
        assert b.initial_hash(model) == initial_hash
        opt = b.optimizer(model)
        assert not opt.state
        journal(out, y, "REFITTING", dict(epochs=selector.selected, cutoff=restricted["cutoff"]))
        for n in range(1, selector.selected + 1):
            tick = time.monotonic()
            train = train_epoch(refit, pos["restricted_refit"], model, opt, n, valid)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - tick, **train))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2D-GAP", y, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        zcal = b.predict(refit, pos["calibration"], model)
        cal = gap_frame(rows, pos["calibration"], valid, gap, maturity)
        cal["Mhat_gap"] = zcal[valid[pos["calibration"]]]
        q = c3.residual_exp(cal.rename(columns={"A_gap": "A", "Mhat_gap": "Mhat"}), scale)
        w = cal.weight.to_numpy()
        assert np.isclose(w.sum(), 1)
        factor = float(w @ q)
        if not math.isfinite(factor) or factor <= 0:
            raise ValueError("BLOCKED_GAP_SMEAR_FACTOR")
        coeff = dict(
            year=y,
            scale_gap=scale,
            c_gap=factor,
            sessions=cal.session_date_et.nunique(),
            stock_days=len(cal),
            effective_sessions=c3.effective_sessions(cal),
            **c3.concentration(q, w),
        )
        freeze(dest / "calibration.json", coeff)
        cal.to_parquet(dest / "calibration_scores.parquet", index=False, compression="zstd")
        # Encoder, own gap scale and scalar now frozen; only selected OOS is generated.
        z = b.predict(refit, pos["oos"], model)
        reload = b.model_for("MAG")
        reload.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, b.predict(refit, pos["oos"], reload))
        assert b.initial_hash(model) == frozen
        f = gap_frame(rows, pos["oos"], valid, gap, maturity)
        take = valid[pos["oos"]]
        f["Mhat_gap"] = z[take]
        f[RAW] = previous.raw_decode(z, scale)[take]
        f[SMEAR] = c3.decode(z, scale, factor)[take]
        base = restricted["baselines"]
        for arm, field in [(MEAN, "mean"), (MEDIAN, "median"), (LOCKED, "recent20")]:
            f[arm] = np.tile(np.asarray(base[field]), (len(pos["oos"]), 1))[take]
        f[LIVE] = recent_live(rows, pos["oos"], bank, valid, gap, maturity)[take]
        assert np.isfinite(f[list(ARMS)].to_numpy()).all() and f[list(ARMS)].ge(0).all().all()
        f.to_parquet(dest / "oos_scores.parquet", index=False, compression="zstd")
        result = dict(
            year=y,
            status="COMPLETED",
            run_id=f"HF20-S2D-GAP-F{y % 100}-S42",
            parameters=6433,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_scale_gap=initial["scale_gap"],
            restricted_scale_gap=scale,
            initial_hash=initial_hash,
            frozen_parameter_hash=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            seconds=time.monotonic() - started,
            peak_rss_bytes=b.memory(),
        )
        freeze(dest / "result.json", result)
        journal(out, y, "COMPLETED", result)
        del inner, refit, model, opt, reload
        gc.collect()
    except BaseException as exc:
        journal(out, y, "FAILED", dict(error=repr(exc), retry=False))
        raise


def membership(values: np.ndarray, k: float, high: bool) -> np.ndarray:
    score = pd.Series(values if high else -values)
    first = score.rank(method="min", ascending=False).to_numpy()
    last = score.rank(method="max", ascending=False).to_numpy()
    return np.clip((k + 1 - first) / (last - first + 1), 0, 1)


def ranking(f: pd.DataFrame, arm: str) -> dict:
    "Native average-rank association on each variable valid-stock cross-section."
    records = []
    for _, g in f.groupby("session_date_et", sort=False):
        a = g.A_gap.to_numpy()
        p = g[arm].to_numpy()
        n = len(g)
        assert 10 <= n <= 20
        ic = float(b.origin_ic(a[None, :], p[None, :])[0])
        i, j = np.triu_indices(n, 1)
        ad = np.sign(a[i] - a[j])
        pdiff = np.sign(p[i] - p[j])
        keep = ad != 0
        concordance = (
            float(((ad[keep] * pdiff[keep] > 0) + 0.5 * (pdiff[keep] == 0)).mean())
            if keep.any()
            else float("nan")
        )
        records.append(
            dict(
                magnitude_IC=ic,
                pair_concordance=concordance,
                top4=float(membership(a, 4, True) @ membership(p, 4, True) / 4),
                bottom4=float(membership(a, 4, False) @ membership(p, 4, False) / 4),
                tie_rate=float((pdiff == 0).mean()),
                constant_rate=float(np.ptp(p) == 0),
                chance_top4=4 / n,
                n_valid=n,
            )
        )
    table = pd.DataFrame(records)
    return dict(
        **{str(k): float(v) for k, v in table.mean().items()},
        IC_valid_sessions=int(table.magnitude_IC.notna().sum()),
    )


def gap_metrics(f: pd.DataFrame, arm: str) -> dict:
    """Existing weighted arithmetic, with explicitly renamed gap estimand."""
    return b.metrics(f.rename(columns={"A_gap": "A"}), arm)


def run(out: Path) -> None:
    assert not (out / "neural_starts.jsonl").exists(), "SINGLE_USE_NO_RETRY"
    assert b.read(out / "readiness.json")["status"] == "PASS"
    assert b.read(out / "preflight.json")["status"] == "PASS_ALL_FOUR"
    for path, sha in b.read(out / "protocol.json")["preservation_bindings"].items():
        assert b.digest(Path(path)) == sha, path
    grid, rows = b.metadata()
    plans, mask, bank = load_roles(out)
    valid, gap, maturity, _ = calendar_and_sources(rows, numeric=True)
    np.testing.assert_array_equal(valid, mask)
    # Original four-hour returns are used only inside unchanged FT16 historical M2 construction.
    # They never determine gap targets, role admission, scales, baselines or losses.
    c, _ = b.source_components(grid, rows)
    folds = prepare(out, c, rows, gap, valid, plans)
    for y in b.YEARS:
        run_fold(out, y, c, rows, gap, valid, plans[y], folds[y], maturity, bank)
    report(out)


def report(out: Path) -> None:
    "Saved new-gap predictions only; no neural, calibration or baseline fitting."
    years = [y for y in b.YEARS if (out / f"F{y % 100}/result.json").exists()]
    if not years:
        return
    for path, sha in b.read(out / "protocol.json")["preservation_bindings"].items():
        assert b.digest(Path(path)) == sha, path
    frames = {}
    records = []
    groups = []
    fits = []
    coeff = []
    for y in years:
        f = pd.read_parquet(out / f"F{y % 100}/oos_scores.parquet")
        frames[y] = f
        fits.append(b.read(out / f"F{y % 100}/result.json"))
        coeff.append(b.read(out / f"F{y % 100}/calibration.json"))
        assert f.groupby("session_date_et").ticker.size().between(10, 20).all()
        assert np.allclose(
            f.groupby("session_date_et").weight.sum(), 1 / f.session_date_et.nunique()
        )
        threshold = b.read(out / f"F{y % 100}/phase_recipes.json")["phases"]["restricted"][
            "gap_tail_thresholds"
        ]
        cuts = np.unique(
            [b.quantile(f[RAW].to_numpy(), q, f.weight.to_numpy()) for q in np.arange(0.1, 1, 0.1)]
        )
        bins = np.searchsorted(cuts, f[RAW], side="left") + 1
        masks = [("tail", f"PREFIX{q}", f.A_gap.gt(threshold[str(q)])) for q in [95, 99]]
        masks += [("tail", f"LE_PREFIX{q}", f.A_gap.le(threshold[str(q)])) for q in [95, 99]]
        masks += [
            ("month", v, f.session_date_et.str.startswith(v))
            for v in sorted(f.session_date_et.str[:7].unique())
        ]
        masks += [("stock", v, f.ticker.eq(v)) for v in b.SYMBOLS]
        masks += [
            ("RAW_decile", str(v), pd.Series(bins == v, index=f.index)) for v in np.unique(bins)
        ]
        for lo, hi, label in [
            (10, 14, "10-14"),
            (15, 17, "15-17"),
            (18, 19, "18-19"),
            (20, 20, "20"),
        ]:
            masks.append(("n_valid", label, f.n_valid.between(lo, hi)))
        nextday = (
            f.gap_maturity_utc.dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
        )
        separation = (nextday - pd.to_datetime(f.session_date_et)).dt.days
        masks += [("calendar_days", str(v), separation.eq(v)) for v in sorted(separation.unique())]
        for arm in ARMS:
            metric = gap_metrics(f, arm)
            rank = ranking(f, arm)
            records.append(dict(year=str(y), arm=arm, **metric, **rank))
            top = pd.Series(index=f.index, dtype=float)
            low = top.copy()
            for _, h in f.groupby("session_date_et", sort=False):
                top.loc[h.index] = membership(h[arm].to_numpy(), 4, True)
                low.loc[h.index] = membership(h[arm].to_numpy(), len(h) / 2, False)
            for field, label, take in masks:
                h = f.loc[take]
                if h.empty:
                    continue
                loss_contribution = float((h.weight * (h[arm] - h.A_gap) ** 2).sum())
                groups.append(
                    dict(
                        year=str(y),
                        arm=arm,
                        field=field,
                        group=label,
                        **gap_metrics(h, arm),
                        weight_mass=float(h.weight.sum()),
                        raw_MSE_contribution=loss_contribution,
                        raw_MSE_loss_share=loss_contribution / metric["raw_MSE"],
                        false_low_rank=float(np.average(low.loc[take], weights=h.weight)),
                        forecast_top4_membership=float(np.average(top.loc[take], weights=h.weight)),
                        RAW_min=float(h[RAW].min()),
                        RAW_max=float(h[RAW].max()),
                    )
                )
    m = pd.DataFrame(records)
    g = pd.DataFrame(groups)
    if len(years) == 4:
        eq = []
        for arm, h in m.groupby("arm", sort=False):
            val = {
                k: float(h[k].mean())
                for k in h.columns
                if k
                not in ["year", "arm", "rows", "origins", "sessions", "ratio", "IC_valid_sessions"]
            }
            eq.append(
                dict(
                    year="EQ",
                    arm=arm,
                    rows=int(h.rows.sum()),
                    origins=int(h.origins.sum()),
                    sessions=int(h.sessions.sum()),
                    IC_valid_sessions=int(h.IC_valid_sessions.sum()),
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
                    "forecast_top4_membership",
                ]
            }
            total = float(m.loc[m.year.eq("EQ") & m.arm.eq(str(arm)), "raw_MSE"].iloc[0])
            eq.append(
                dict(
                    year="EQ",
                    arm=arm,
                    field=field,
                    group=label,
                    rows=int(h.rows.sum()),
                    sessions=int(h.sessions.sum()),
                    origins=int(h.origins.sum()),
                    ratio=val["predicted"] / val["observed"],
                    raw_MSE_loss_share=val["raw_MSE_contribution"] / total,
                    **val,
                )
            )
        g = pd.concat([g, pd.DataFrame(eq)], ignore_index=True)
    paired = []
    for ref in [MEAN, LOCKED, MEDIAN, LIVE, RAW]:
        months = {}
        for y, f in frames.items():
            months[y] = (
                pd.DataFrame(
                    dict(
                        day=f.session_date_et,
                        numerator=f.weight * ((f[SMEAR] - f.A_gap) ** 2 - (f[ref] - f.A_gap) ** 2),
                        mass=f.weight,
                    )
                )
                .groupby("day")[["numerator", "mass"]]
                .sum()
            )
        for row in previous.paired_months(months):
            base = float(m.loc[m.year.eq(row["year"]) & m.arm.eq(ref), "raw_MSE"].iloc[0])
            paired.append(
                dict(
                    reference=ref,
                    **row,
                    percent_change=100 * row["delta"] / base,
                    interval_includes_zero=row["low"] <= 0 <= row["high"],
                )
            )
    m.to_csv(out / "metrics.csv", index=False)
    g.to_csv(out / "groups.csv", index=False)
    pd.DataFrame(paired).to_csv(out / "paired_MSE.csv", index=False)
    pd.DataFrame(fits).to_csv(out / "fit_summary.csv", index=False)
    pd.DataFrame(coeff).to_csv(out / "calibration_coefficients.csv", index=False)
    verdict = "PARTIAL_NO_FOUR_YEAR_CLAIM"
    if len(years) == 4:

        def score(arm: str) -> float:
            values = m.loc[m.year.eq("EQ") & m.arm.eq(arm), "raw_MSE"].to_numpy(float)
            assert len(values) == 1
            return float(values[0])

        verdict = (
            "LOWER_MSE_THAN_BOTH_FROZEN_MEAN_CONTROLS_REVIEW_TRADEOFFS"
            if score(SMEAR) < min(score(MEAN), score(LOCKED))
            else "NO_CLEAR_INCREMENTAL_EVIDENCE_AGAINST_FROZEN_GAP_CONTROLS"
        )
    notes = b.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    sections = [
        "# S2-D genuine overnight-gap magnitude — masked stock-day panel",
        (
            f"**Status: {'COMPLETE' if len(years) == 4 else 'PARTIAL'} — {len(years)}/4 folds.** "
            f"{verdict}. Exploratory/post-search."
        ),
        notes.get(
            "executive", "Report all gap-specific baselines; do not choose an OOS-best reference."
        ),
        "## Target, timing and population",
        (
            "A_gap=abs(log(next scheduled genuine09:30 minute open/current genuine "
            "final-minute regular-session close)). One normal full-day15:30 forecast "
            "per stock/session, approximate15:32 issuance before16:00 close. This is "
            "not15:32-to-open execution, a four-hour endpoint target, signed alpha, "
            "integrated variance or option profit. Source references are "
            "vendor-adjusted/quarantine-filtered last-minute closes and minute opens,"
            " not verified auction fills. No early close remapping, synthetic price, "
            "duplicate nightly label or future gap input."
        ),
        (
            "This is an explicit prospective amendment of the strict20 blocked S2-D: "
            "original20-name universe and all20 FT16 input eligibility remain, but "
            "only sessions with>=10 genuinely labeled stocks are admitted and actual "
            "valid stocks receive equal weight within each date. Source support is "
            "retrospective, not known as a future tradable stock-selection rule. "
            "Missing labels never become zero or a small realized gap. All arrays "
            "retain canonical tensor order; no label support is a neural feature. "
            "Main four-hour S2-B/C studies are untouched and no four-hour MSE appears"
            " in the comparison."
        ),
        "## All-fold gate, source and coverage",
        b.markdown(
            pd.read_csv(out / "role_counts.csv")[
                [
                    "year",
                    "role",
                    "sessions",
                    "stock_days",
                    "min_valid_stocks",
                    "max_valid_stocks",
                    "months",
                    "minimum_month_sessions",
                    "status",
                ]
            ]
        ),
        (
            "All20 role session/stock-day counts reproduce the coverage audit under "
            "the fixed>=10 rule after positive/finite source certification. "
            "Selector>=50 and monthly>=5,calibration>=25 and "
            "monthly>=5,OOS>=100/all12 months,prefix>=252 remain binding. Gap "
            "maturity is next-open+2min, and first-of48 input-step date must exceed "
            "role embargo. The future four-hour endpoint/label-eligible flag is never"
            " used for gap admission. Original15:30 inputs end exactly15:30 and every"
            " grid step is a completed full60 minutes;16:00 close is future "
            "label-only."
        ),
        (
            "source_validation.json binds source versions and exact allowed "
            "columns/semantics. stock_month_coverage.csv,monthly_role_counts.csv and "
            "eligibility_exclusions.csv disclose label/input/embargo/maturity "
            "attrition;baseline_history.csv proves all20 required controls have>=20 "
            "genuine historical gaps. The audit's2-stock selector date is excluded by"
            " the fixed>=10 gate. Source selection concentrates in MS/MRK and other "
            "historical provider gaps, not assumed random. Role arrays/stock masks "
            "and hashes are in role_masks.npz/preflight.json. Prefix monthly minimum0"
            " is descriptive only; the monthly5 gate applies only to "
            "selector/calibration. No source repair, minute store,2025 market or2026 "
            "protected access."
        ),
        "## Frozen model, phase fitting and baselines",
        (
            "Original H32 one-layer48×16 shared LSTM,6433 parameters,scalar "
            "transformed-gap head,final hidden dropout.10,zero recurrent state per "
            "window,seed42,CPUfloat32. No S2-B clock vector or S2-C heads. AdamW "
            "lr.001 betas(.9,.999)eps1e-8,matrix decay.01,bias0,clip1;16 full "
            "sessions shuffled42+epoch. Loss is equal valid-stock M_gap squared error"
            " within each admitted date, then equal dates; masked cells never enter "
            "target arithmetic and have zero loss gradient. Selector monitors this "
            "same gap M risk with .999 qualified best,min12,patience10,max60,followed"
            " by fresh same-seed/empty-optimizer September refit at selected epochs."
        ),
        (
            "Every phase independently fits its own weighted-left-median gap s "
            "(floor1e-8); no four-hour scale/threshold/coef is borrowed. Own "
            "input-only-prefix recipes exactly reproduce the inherited FT16 recipes "
            "at the same cutoffs. The native FT16 M2 construction may read historical"
            " original four-hour returns as part of its unchanged causal features; "
            "these are not gap targets or admission criteria. Own September "
            "checkpoint/recipe/s generates both independent Oct–Dec and following OOS"
            " predictions unchanged."
        ),
        (
            "The fixed principal mean-target reference is B0-GAP-RMEAN,not an OOS "
            "winner. Also report stock weighted median (MAE-oriented),frozen "
            "September stock RECENT20 and live-updated RECENT20. Mean/median use only"
            " legal phase prefix labels weighted by the masked panel; stock "
            "normalization conditions those weights. RECENT20 is the arithmetic mean "
            "of20 actual observed matured gaps per stock; no imputed or current-night"
            " observations. Locked uses only September role. LIVE uses an explicitly "
            "more-current normal15:30 input/source-admissible>=10 bank with maturity "
            "strictly before issuance,including preceding calibration/OOS labels;it "
            "is not an identical-history principal control or a tuning signal. No "
            "baseline selection,fit on test outcomes,EWMA/GARCH/HAR expansion or "
            "fallback. Optional lagged EWMA/RMS: NOT INCLUDED, no already-verified "
            "gap implementation reused."
        ),
        b.markdown(
            pd.DataFrame(fits)[
                [
                    "year",
                    "selected_epoch",
                    "selector_epochs",
                    "raw_minimum_epoch",
                    "initial_scale_gap",
                    "restricted_scale_gap",
                    "seconds",
                    "peak_rss_bytes",
                ]
            ]
        ),
        "## Annual and equal-year gap scores",
        b.markdown(
            m[
                [
                    "year",
                    "arm",
                    "rows",
                    "sessions",
                    "observed",
                    "predicted",
                    "bias",
                    "ratio",
                    "raw_MSE",
                    "raw_MAE",
                    "magnitude_IC",
                    "top4",
                    "chance_top4",
                ]
            ]
        ),
        (
            "A_gap/MAE/means/bias are absolute log-return units; MSE is squared "
            "log-return units. Equal surviving stocks/date→equal "
            "dates/year→arithmetic equal years; ratio is equal-year "
            "predicted/observed means. No naive equal-stock-day pooling. "
            "Variable-size cross-sectional IC uses average ranks within the same10–20"
            " source-supported names; undefined constant cross-sections are excluded "
            "and counts disclosed. Pair concordance excludes realized ties, gives "
            "forecast ties.5;top/bottom4 use fractional tie membership and "
            "chance4/n_valid,not a fixed20%. Constant/tie/pair/bottom retrieval and "
            "valid IC count in metrics.csv."
        ),
        "## Paired dependent-time uncertainty",
        b.markdown(pd.DataFrame(paired)),
        (
            "400 draws,seed22042,whole-calendar-month blocks with full correlated "
            "stock/session panels;year-stratified equal-year aggregation. Point "
            "differences are SMEAR minus each explicitly named control (negative "
            "favors LSTM). These are post-search descriptive95% intervals conditional"
            " on fitted weights,calibrator and repeated adjacent-year research;not "
            "selection-adjusted inference. No IID stock-row tests or independent "
            "confirmation. LIVE's history advantage and median's different functional"
            " remain explicit."
        ),
        "## Independent own-gap smearing",
        b.markdown(pd.DataFrame(coeff)),
        (
            "Only one global own-gap exp(log1p(A_gap/s)-Mhat_gap) weighted moment is "
            "fitted on reserved Oct–Dec with the exact frozen September model/scale. "
            "Residual uses unclamped Mhat;raw decode alone maxes Mhat at0. No double "
            "inverse,borrowed C3 factors,conditional map,trimming or chosen raw "
            "winner. Calibration counts/effective sessions and top10/top1% "
            "weighted-moment concentrations above describe stability,not OOS "
            "performance. F24 tail is smaller; uncertainty does not refit the scalar."
        ),
        "## Reliability, tails, month and stock diagnostics",
        b.markdown(
            g.loc[
                g.year.eq("EQ") & g.field.eq("tail"),
                [
                    "arm",
                    "group",
                    "rows",
                    "sessions",
                    "raw_MSE",
                    "raw_MAE",
                    "ratio",
                    "weight_mass",
                    "raw_MSE_loss_share",
                    "forecast_top4_membership",
                    "false_low_rank",
                ],
            ]
        ),
        (
            "groups.csv includes "
            "annual/month/stock/variable-panel-size/known-calendar-day separation and"
            " RAW-score decile aggregates. Deciles are predeclared descriptive "
            "weighted RAW-score quantiles per year,shared across arms,never a fitted "
            "map. Tail95/99 thresholds are weighted genuine-gap restricted-prefix "
            "quantiles;ordinary complements retain original population weights. Loss "
            "contributions use unconditional annual masked-panel weights. Event top4 "
            "membership and fractional bottom-half false-low are computed in each "
            "full valid-stock cross-section before conditioning on true historical "
            "events;they are not deployable event probabilities. Equal-year group "
            "summaries require a nonempty cohort in all4 years. "
            "Missingness/population and repeated dates/stocks are not independent "
            "replications."
        ),
        "## Scientific decision and limitations",
        notes.get(
            "decision",
            (
                "Judge primary raw gap MSE against every frozen mean-target control,not "
                "four-hour losses or the best-looking secondary metric. Keep median MAE "
                "and live-updated comparison separate. No automatic promotion or further "
                "experiment."
            ),
        ),
        (
            "This gap task cannot be compared numerically with original four-hour "
            "magnitude MSE to infer a winner. Even genuine gap predictability does "
            "not imply signed return alpha,option mispricing or profitable auction "
            "execution. The strict20 BLOCKED study remains archived;this is a new "
            "masked study. STOP for researcher review."
        ),
        "## Reproduction and preservation",
        (
            "Entry point: `.venv/bin/python -m lstm_data.hf20_s2d_gap "
            "--preflight`,then mandatory focused tests/Ruff/basic static gate,and one"
            " single-use `--run`;`--report` replays only this task's saved selected "
            "forecasts without neural/baseline/calibration fitting. No "
            "retry/namespace overwrite. Source and prior journals/control assets are "
            "hash-bound in protocol. New checkpoints/forecast Parquets are local "
            "ignored artifacts;small JSON/CSV/reports/code/tests are reviewable. "
            "Exact commands,tests,resources,current registry and all changed paths "
            "are in readiness/final_checks and the standard Codex session handoff. No"
            " commit/push."
        ),
    ]
    (out / "S2D_MASKED_GAP_REPORT.md").write_text("\n\n".join(sections) + "\n")
    if not (out / "verification.json").exists():
        last = json.loads((out / "neural_starts.jsonl").read_text().splitlines()[-1])
        freeze(
            out / "verification.json",
            dict(
                status="COMPLETE" if len(years) == 4 else "PARTIAL",
                verdict=verdict,
                folds=years,
                ledger_before=162,
                ledger_after=last["global_started_pairs"],
                ceiling=300,
                charged_starts=len(years),
                neural_phases=2 * len(years),
                no_retries=True,
                old_bindings_unchanged=True,
                checkpoint_reload_max_error=0,
                resources=b.resources(out),
            ),
        )


if __name__ == "__main__":
    main()
