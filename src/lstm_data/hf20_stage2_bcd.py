"""Three separately gated Stage2 tasks; no cross-task scoring or deferred router."""

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
from . import hf20_overnight_specialist as previous
from .hf20_s4_clock import sessions
from .neural_engine import seed_all

OUT = Path("reports/experiments/hf20_s9_mag_stage2_bcd_2026-10-28")
TASK_DIRS = {"B": "s2b_clock", "C": "s2c_decomposition", "D": "s2d_overnight_hold"}
REPORTS = {
    "B": "S2B_CLOCK_REPORT.md",
    "C": "S2C_DECOMPOSITION_REPORT.md",
    "D": "S2D_OVERNIGHT_HOLD_REPORT.md",
}
TARGET = b.S4 / "opening_reaudit_v2/S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet"


def plan_path(out: Path) -> Path:
    """The append-only D metadata clarification supersedes the first receipt."""
    name = (
        ("planning_receipt_v2.json")
        if (out / ("planning_receipt_v2.json")).exists()
        else ("planning_receipt.json")
    )
    return out / name


def freeze(path: Path, data: dict) -> None:
    if path.exists():
        assert b.read(path) == data, f"FROZEN_SPEC_CHANGED:{path}"
    else:
        b.write(path, data, new=True)


def budget_amendment(out: Path) -> dict:
    """Prospective ceiling change only; preserve counter and every historical event."""
    path = out / "budget_amendment_300.json"
    pointer = b.read(b.POINTER)
    if path.exists():
        receipt = b.read(path)
        assert pointer["effective_ceiling"] == 300
        assert pointer["budget_amendment"] == dict(path=str(path), sha256=b.digest(path))
        return pointer
    prior_history = Path(pointer["real_journal"])
    last = json.loads(prior_history.read_text().splitlines()[-1])
    assert last["status"] == "COMPLETED" and last["global_started_pairs"] == 154
    assert pointer["effective_ceiling"] == 200 and pointer["counts_started_including_failed"]
    assert (
        b.digest(Path(pointer["budget_amendment"]["path"])) == pointer["budget_amendment"]["sha256"]
    )
    receipt = dict(
        id="HF20_BUDGET_200_TO_300_2026_10_28_V1",
        actor_type="human",
        recorded_at=pd.Timestamp.now(tz="UTC").isoformat(),
        old_ceiling=200,
        new_ceiling=300,
        opening_started=154,
        prospective_only=True,
        fit_permission=False,
        scope=(
            "Ceiling only; this B/C/D campaign at most12 starts/24 phases, subject to three gates"
        ),
        verbatim_authorization=(
            "Extend the existing cumulative neural-start budget from 200 to 300 starts (+100)."
        ),
        previous_pointer=pointer,
        immutable_prior_journal=dict(path=str(prior_history), sha256=b.digest(prior_history)),
    )
    b.write(path, receipt, new=True)
    amended = dict(
        pointer,
        schema_version=28,
        effective_ceiling=300,
        budget_amendment=dict(path=str(path), sha256=b.digest(path)),
        fit_permission=False,
    )
    b.write(b.POINTER, amended)
    return amended


def clock_values(rows: pd.DataFrame, calendar: pd.DataFrame) -> tuple[np.ndarray, pd.Series]:
    """Only scheduled slot, remaining session time, crossing and next-session dates."""
    dates = calendar.index.astype(str).str[:10]
    next_open = pd.Series(calendar.open.to_numpy()[1:], index=dates[:-1])
    following = rows.session_date_et.map(next_open)
    if following.isna().any():
        raise ValueError("MISSING_NEXT_SCHEDULED_SESSION")
    remaining = (rows.session_close - rows.entry_end_utc).dt.total_seconds().to_numpy() / 60
    crosses = remaining < 240
    np.testing.assert_array_equal(crosses, rows.category.eq("OVERNIGHT"))
    next_dates = (
        pd.to_datetime(following, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.tz_localize(None)
        .dt.normalize()
    )
    day_gap = (next_dates - pd.to_datetime(rows.session_date_et)).dt.days.to_numpy()
    onehot = np.eye(7)[rows.slot.map({v: k for k, v in enumerate(b.SLOTS)}).to_numpy(int)]
    values = np.column_stack([onehot, remaining / 240, crosses, day_gap / 7]).astype(np.float32)
    assert values.shape == (len(rows), 10) and np.isfinite(values).all()
    return values, following


def protocol_specs(out: Path, rows: pd.DataFrame, pointer: dict) -> None:
    """Freeze estimands/designs before projecting any numerical endpoint/return labels."""
    roles = b.read(o1.OUT / "protocol.json")["folds"]
    common = dict(
        seed=42,
        folds=roles,
        model="own-stock48x16 FT16;one-layerH32;final hidden dropout.10;CPU float32",
        optimizer=(
            "AdamW lr.001 betas(.9,.999) eps1e-8 matrix decay.01 bias0;clip1;16 "
            "complete sessions;shuffle42+epoch"
        ),
        selector=(
            "primary transformed magnitude loss only;first finite "
            "nonnegative;<=.999 qualified best;min12 patience10 max60"
        ),
        fresh_refit=True,
        maximum_starts=4,
        maximum_phase_fits=8,
        epoch_cutoffs=(
            "exact saved Design A role indices/cutoffs;48 completed-step "
            "embargo;task-specific maturity"
        ),
        source=str(TARGET),
        source_sha256=b.digest(TARGET),
        role_index_source=str(o1.OUT / "role_indices.npz"),
        source_read_receipt=str(b.S4 / "opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv"),
        protected=(
            "No2025/2026 prices/outcomes/metrics/hashes;calendar-only next-session "
            "dates may extend into January2025"
        ),
        uncertainty=dict(
            draws=400, seed=22042, unit="whole calendar months within year, then equal years"
        ),
        caps=b.CAPS,
        no_deferred_C0_M1_router=True,
        intraday_preference_unresolved=True,
    )
    clock = dict(
        fields=[
            *[f"slot_{v}" for v in b.SLOTS],
            "remaining_trading_minutes/240",
            "target_crosses_session",
            "calendar_days_to_next_scheduled_session/7",
        ],
        dimension=10,
        scale="fixed, no fitting",
        placement=(
            "concatenate to dropped final H32 hidden state before scalar head;metadata not dropped"
        ),
        calendar="executed XNYS schedule and actual early closes;no outcomes used",
    )
    configs = {
        "B": dict(
            kind="HF20_S2B_CLOCK_V1",
            estimand="original A_total=abs(log(Pexit/Pentry)) over240 trading minutes",
            primary="CLOCK-C3 raw MSE vs frozen C3 on all original keys",
            objective="canonical transformed M_total MSE",
            clock=clock,
            parameters=6443,
            calibration="new encoder's own C3 IO session-shrunk smear kappa25;raw diagnostic",
            source_gate=(
                "exact original complete20 keys and unchanged input/target "
                "recipes;selector50 sessions,25 per slot;both calibration groups "
                "nonempty"
            ),
        ),
        "C": dict(
            kind="HF20_S2C_DECOMPOSITION_V1",
            estimand="same original A_total;three signed training-only auxiliary components",
            primary="COMPONENT-C3 raw MSE vs S2B and frozen C3 on identical original keys",
            objective=(
                "L_M_all + .10*(L_pre_N+L_gap_N+L_post_N)/3;each aux conditional "
                "group-session/origin/stock mean of ((R-Rhat)/s)^2"
            ),
            clock=clock,
            parameters=6572,
            aux_heads=(
                "three independent42→1 linear normalized signed heads;Rhat=s*u;intraday"
                " aux masked, not zero-labelled"
            ),
            calibration="own independent-tail C3 IO smear kappa25;main head only",
            source_gate=(
                "all original N observations in every role require all20 genuine "
                "components,one closure,additivity atol1e-12 rtol1e-11;otherwise "
                "BLOCKED, no attrition rescue"
            ),
        ),
        "D": dict(
            kind="HF20_S2D_OVERNIGHT_HOLD_V1",
            estimand=(
                "A_gap=abs(log(next09:30 genuine minute open / actual16:00 genuine "
                "end-of-session price))"
            ),
            primary=(
                "GAP-SMEAR raw A_gap MSE vs all same-gap controls, strongest observed "
                "comparator explicitly descriptive"
            ),
            objective="canonical M_gap transformed MSE",
            parameters=6433,
            clock=None,
            population=(
                "one normal full-session15:30 origin/session;input source "
                "eligibility,all20 genuine close/open,same action basis;new gap "
                "maturity nextopen+2min and48-step embargo"
            ),
            scale=(
                "independent phase-prefix weighted left median A_gap, "
                "floor1e-8;original input-only FT16 prefix recipes"
            ),
            minimums=dict(
                prefix_sessions=252,
                selector_sessions=50,
                calibration_sessions=25,
                oos_sessions=100,
                selector_calibration_sessions_per_month=5,
                oos_months=12,
            ),
            baselines=[
                "prefix per-stock raw gap mean",
                "prefix weighted-left-median raw gap",
                (
                    "mean of last20 genuinely matured valid gaps per stock;at least20, no "
                    "current/future gap, no parameter selection"
                ),
            ],
            calibration=(
                "predeclared primary one global own-tail smear;raw diagnostic, never choose by OOS"
            ),
            tails="own legal prefix95/99 gap thresholds;no cross-task comparison",
            source_gate=(
                "genuine current close/next open all20;exclude early closes and "
                "COP2012-05-01 basis crossing;rebuild admissions using gap maturity, "
                "not4h eligibility"
            ),
        ),
    }
    for task, config in configs.items():
        dest = out / TASK_DIRS[task]
        dest.mkdir(exist_ok=True)
        freeze(dest / "protocol.json", dict(common, **config))
    freeze(
        out / "source_policy.json",
        dict(
            prior_pointer=pointer,
            maximum_new_starts=12,
            maximum_phase_fits=24,
            starting_count=154,
            ceiling=300,
            sequence=["B", "C", "D"],
            source_metadata_rows=len(rows),
            no_new_source=True,
            no_deferred_router=True,
        ),
    )


def preflight(out: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    out.mkdir(exist_ok=True)
    pointer = budget_amendment(out)
    assert b.read(previous.OUT / "verification.json")["status"] == "COMPLETE"
    assert b.read(previous.OUT / "verification.json")["ledger_after"] == 154
    grid, rows = b.metadata()
    protocol_specs(out, rows, pointer)
    calendar = sessions("2010-07-01", "2025-01-10")
    clocks, next_open = clock_values(rows, calendar)
    dictionary = pd.DataFrame(
        clocks, columns=b.read(out / TASK_DIRS["B"] / "protocol.json")["clock"]["fields"]
    )
    dictionary.insert(0, "slot", rows.slot.to_numpy())
    dictionary.drop_duplicates().to_csv(out / "clock_dictionary.csv", index=False)
    # Designs are already frozen. Source proof reads saved prices/components only;
    # no source reconstruction or performance statistic is used to choose a design.
    values = pd.read_parquet(TARGET)
    np.testing.assert_array_equal(values.origin_id.iloc[::20], rows.origin_id)
    assert values.ticker.tolist() == list(b.SYMBOLS) * len(rows)
    supported = values.decomposition_supported.to_numpy().reshape(-1, 20).all(1)
    close = values.genuine_session_end_price.to_numpy().reshape(-1, 20)
    opened = values.next_session_open.to_numpy().reshape(-1, 20)
    valid_gap = (
        np.isfinite(close).all(1)
        & (close > 0).all(1)
        & np.isfinite(opened).all(1)
        & (opened > 0).all(1)
    )
    following_day = (
        pd.to_datetime(next_open, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.strftime("%Y-%m-%d")
    )
    basis = rows.session_date_et.lt("2012-05-01").eq(following_day.lt("2012-05-01"))
    gap_input = rows.source_input_eligible & rows.regular_session & rows.slot.eq("15:30")
    gap_valid = gap_input & valid_gap & basis
    gap_maturity = pd.to_datetime(next_open, utc=True) + pd.Timedelta(minutes=2)
    first = np.full(len(rows), "0000", dtype=object)
    good = rows.first_step.ge(0)
    first[good] = grid.session_date_et.to_numpy()[rows.loc[good, "first_step"].to_numpy(int)]
    indices = np.load(o1.OUT / "role_indices.npz")
    counts = pd.read_csv(o1.REF / "role_counts.csv")
    records = []
    component_coverage = []
    gap_coverage = []
    plans = {}
    blocked_c = []
    blocked_d = []
    for year in b.YEARS:
        plans[year] = {"B": {}, "C": {}, "D": {}}
        for item in counts.loc[counts.year.eq(year)].to_dict("records"):
            role = str(item["role"])
            ix = indices[f"F{year % 100}_{role}"]
            expected = np.flatnonzero(
                b.role_mask(
                    rows, first, str(item["start"]), str(item["cutoff"]), str(item["embargo_after"])
                )
            )
            np.testing.assert_array_equal(ix, expected)
            plans[year]["B"][role] = ix
            plans[year]["C"][role] = ix
            g = rows.iloc[ix]
            night = ix[g.category.eq("OVERNIGHT").to_numpy()]
            missing = night[~supported[night]]
            component_coverage.append(
                dict(
                    year=year,
                    role=role,
                    N_origins=len(night),
                    complete20_origins=int(supported[night].sum()),
                    missing_origins=len(missing),
                )
            )
            if len(missing):
                blocked_c.append(
                    f"F{year % 100}/{role}:{len(missing)} original overnight origins "
                    "lack complete20 genuine components"
                )
            records.append(
                dict(
                    year=year,
                    role=role,
                    origins=len(g),
                    sessions=g.session_date_et.nunique(),
                    rows=len(g) * 20,
                )
            )
            take = (
                gap_valid
                & rows.session_date_et.between(str(item["start"]), str(item["cutoff"]))
                & (first > str(item["embargo_after"]))
                & gap_maturity.lt(b.limit(str(item["cutoff"])))
            )
            gi = np.flatnonzero(take)
            plans[year]["D"][role] = gi
            h = rows.iloc[gi]
            months = h.session_date_et.str[:7].value_counts().sort_index()
            needed = (
                252
                if role in ("inner_train", "restricted_refit")
                else {"selector": 50, "calibration": 25, "oos": 100}[role]
            )
            reasons = []
            if len(h) < needed:
                reasons.append(f"sessions{len(h)}<{needed}")
            if role in ("selector", "calibration"):
                # Selector nominal window can be3/4/5 months; require every scheduled month.
                span = pd.period_range(
                    str(item["start"])[:7], str(item["cutoff"])[:7], freq="M"
                ).astype(str)
                if months.reindex(span, fill_value=0).min() < 5:
                    reasons.append("one role month has fewer than5 sessions")
            if role == "oos" and len(months) != 12:
                reasons.append("not all12 OOS months represented")
            gap_coverage.append(
                dict(
                    year=year,
                    role=role,
                    sessions=len(h),
                    origins=len(h),
                    rows=len(h) * 20,
                    months=len(months),
                    minimum_month_sessions=int(months.min()) if len(months) else 0,
                    first_date=str(h.session_date_et.min()),
                    last_date=str(h.session_date_et.max()),
                    status="BLOCKED" if reasons else "PASS",
                    reason=";".join(reasons),
                )
            )
            if reasons:
                blocked_d.append(f"F{year % 100}/{role}:" + ";".join(reasons))
    projected_starts = 4 * (1 + int(not blocked_c) + int(not blocked_d))
    receipt = dict(
        status="PREFLIGHT_COMPLETE",
        B=dict(status="READY", reasons=[]),
        C=dict(status="BLOCKED" if blocked_c else "READY", reasons=blocked_c),
        D=dict(status="BLOCKED" if blocked_d else "READY", reasons=blocked_d),
        ledger_before=154,
        ceiling=300,
        remaining_capacity=146,
        resources=b.resources(out),
        source_gate="saved genuine endpoint/component artifact only;no minute read",
        component_coverage=component_coverage,
        gap_coverage=gap_coverage,
        role_counts=records,
        projected_new_starts=projected_starts,
        projected_after=154 + projected_starts,
        protocols={
            t: dict(path=str(out / d / "protocol.json"), sha256=b.digest(out / d / "protocol.json"))
            for t, d in TASK_DIRS.items()
        },
    )
    freeze(out / "planning_receipt.json", receipt)
    pd.DataFrame(component_coverage).to_csv(out / "component_coverage.csv", index=False)
    pd.DataFrame(gap_coverage).to_csv(out / "gap_coverage.csv", index=False)
    print(
        json.dumps(
            {
                k: receipt[k]
                for k in [
                    "B",
                    "C",
                    "D",
                    "ledger_before",
                    "ceiling",
                    "projected_new_starts",
                    "resources",
                ]
            },
            indent=2,
        ),
        flush=True,
    )
    return grid, rows, plans, receipt


class ClockMAG(b.SharedLSTM):
    """Unchanged recurrent trunk; ten fixed schedule values enter only the head."""

    def __init__(self) -> None:
        nn.Module.__init__(self)
        self.input_dim = 16
        self.lstm = nn.LSTM(16, 32, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.10)
        self.head = nn.Linear(42, 1)

    def forward(self, x: torch.Tensor, clock: torch.Tensor | None = None) -> torch.Tensor:
        if clock is None or clock.shape != (len(x), 10) or not bool(torch.isfinite(clock).all()):
            raise ValueError("FINITE_TEN_KNOWN_CLOCK_VALUES_REQUIRED")
        return self.head(torch.cat([self.dropout(self.encode(x)), clock], dim=1)).squeeze(-1)


def model_for_clock() -> ClockMAG:
    seed_all(42)
    model = ClockMAG().float()
    assert sum(p.numel() for p in model.parameters()) == 6443
    return model


def saved_plans(rows: pd.DataFrame) -> dict[int, dict]:
    indices = np.load(o1.OUT / "role_indices.npz")
    return {
        year: {
            role: indices[f"F{year % 100}_{role}"]
            for role in ["inner_train", "selector", "restricted_refit", "calibration", "oos"]
        }
        for year in b.YEARS
    }


def source_validation(out: Path, rows: pd.DataFrame) -> None:
    """Explain the genuine-component blocker without repairing or expanding source."""
    f = pd.read_parquet(TARGET)
    close = f.genuine_session_end_price.to_numpy().reshape(-1, 20)
    opened = f.next_session_open.to_numpy().reshape(-1, 20)
    support = f.decomposition_supported.to_numpy().reshape(-1, 20)
    pieces = [
        f[k].to_numpy().reshape(-1, 20)
        for k in ["origin_to_close", "close_to_next_open", "next_open_to_exit"]
    ]
    total = f.direct_return.to_numpy().reshape(-1, 20)
    composed = pieces[0] + pieces[1] + pieces[2]
    np.testing.assert_allclose(composed[support], total[support], atol=1e-12, rtol=1e-11)
    details = []
    examples = []
    for y, p in saved_plans(rows).items():
        for role, ix in p.items():
            night = ix[rows.iloc[ix].category.eq("OVERNIGHT").to_numpy()]
            missing_close = ~np.isfinite(close[night]).all(1)
            missing_open = ~np.isfinite(opened[night]).all(1)
            details.append(
                dict(
                    year=y,
                    role=role,
                    night_origins=len(night),
                    missing_close20=int(missing_close.sum()),
                    missing_open20=int(missing_open.sum()),
                )
            )
            if role == "oos" and len(examples) < 4:
                absent = night[missing_close | missing_open]
                if len(absent):
                    i = int(absent[0])
                    ticker = int(
                        np.flatnonzero(~np.isfinite(close[i]) | ~np.isfinite(opened[i]))[0]
                    )
                    examples.append(
                        dict(
                            year=y,
                            origin_id=rows.iloc[i].origin_id,
                            ticker=b.SYMBOLS[ticker],
                            genuine_close_missing=not bool(np.isfinite(close[i, ticker])),
                            next_open_missing=not bool(np.isfinite(opened[i, ticker])),
                        )
                    )
    receipt = dict(
        source=str(TARGET),
        source_policy=str(b.S4 / "opening_reaudit_v2/S4_SOURCE_POLICY.json"),
        price_lineage=(
            "executed hf20_s4_preflight.load_source/price_matrix: adjusted "
            "quarantine-filtered genuine minute close at session_close-1min and "
            "minute open at next09:30;no hourly proxy"
        ),
        tolerance="atol1e-12 rtol1e-11",
        max_signed_additivity_error=float(np.max(abs(composed[support] - total[support]))),
        provenance=(
            "existing saved vendor references, not verified execution "
            "fills;original COP action-basis crossing excluded"
        ),
        details=details,
        examples=examples,
        new_minute_reads=0,
        repairs=0,
    )
    freeze(out / "source_validation.json", receipt)


def verify_before_fits(out: Path, grid: pd.DataFrame, rows: pd.DataFrame, plans: dict) -> None:
    """Small same-key/decoder and phase contract checks, no new model inference."""
    receipt = b.read(plan_path(out))
    assert (
        receipt["B"]["status"] == "READY"
        and receipt["C"]["status"] == receipt["D"]["status"] == "BLOCKED"
    )
    pointer = b.read(b.POINTER)
    assert pointer["effective_ceiling"] == 300
    prior = b.read(out / "budget_amendment_300.json")["immutable_prior_journal"]
    assert b.digest(Path(prior["path"])) == prior["sha256"]
    assert b.digest(Path(pointer["plan"]["path"])) == pointer["plan"]["sha256"]
    archived = pd.read_csv(c3.OUT / "metrics.csv", dtype={"year": str})
    counts = pd.read_csv(o1.REF / "role_counts.csv")
    first = np.full(len(rows), "0000", dtype=object)
    valid = rows.first_step.ge(0)
    first[valid] = grid.session_date_et.to_numpy()[rows.loc[valid, "first_step"].to_numpy(int)]
    early = set(b.read(previous.OUT / "protocol.json")["early_close_dates"])
    for year, p in plans.items():
        for record in counts.loc[counts.year.eq(year)].to_dict("records"):
            ix = p[str(record["role"])]
            g = rows.iloc[ix]
            expected = np.flatnonzero(
                b.role_mask(
                    rows,
                    first,
                    str(record["start"]),
                    str(record["cutoff"]),
                    str(record["embargo_after"]),
                )
            )
            np.testing.assert_array_equal(ix, expected)
            assert g.entry_index.sub(g.first_step).eq(47).all() and g.trading_minutes.eq(240).all()
            if record["role"] == "selector":
                assert (
                    g.session_date_et.nunique() >= 50
                    and g.groupby("slot").size().reindex(b.SLOTS, fill_value=0).min() >= 25
                )
        for left, right in [
            ("inner_train", "selector"),
            ("restricted_refit", "calibration"),
            ("selector", "calibration"),
            ("calibration", "oos"),
        ]:
            assert not np.intersect1d(p[left], p[right]).size
        f = pd.read_parquet(c3.root(year) / "oos_scores.parquet")
        c3.validate_panel(f, early)
        np.testing.assert_array_equal(f.origin_id.iloc[::20], rows.iloc[p["oos"]].origin_id)
        f["C3"] = previous.frozen_c3(f, year)
        old = archived.loc[archived.year.eq(str(year)) & archived.arm.eq(c3.ARM)].iloc[0]
        for name, value in {**b.metrics(f, "C3"), **b.rank_metrics(f, "C3")}.items():
            np.testing.assert_allclose(value, old[name], atol=1e-14, rtol=1e-13)
    source_validation(out, rows)
    trace = pd.concat([pd.read_csv(previous.OUT / f"F{y % 100}/training.csv") for y in b.YEARS])
    execution = dict(
        status="ALL_FOUR_B_READY_C_D_BLOCKED",
        maximum_new_pairs=4,
        maximum_phase_fits=8,
        maximum_after=158,
        ceiling=300,
        remaining_after_planned=142,
        seed=42,
        threads=[4, 1],
        maximum_epochs=480,
        reference_epoch_p95=float(trace.seconds.quantile(0.95)),
        rough_max_seconds=480 * float(trace.seconds.quantile(0.95)),
        preservation_bindings={
            str(TARGET): b.digest(TARGET),
            prior["path"]: prior["sha256"],
            str(o1.OUT / "role_indices.npz"): b.digest(o1.OUT / "role_indices.npz"),
        },
        resources=b.resources(out),
        no_deferred_router=True,
    )
    path = out / "execution_plan.json"
    if path.exists():
        assert b.read(path)["preservation_bindings"] == execution["preservation_bindings"]
    else:
        freeze(path, execution)


def journal(out: Path, year: int, status: str, detail: dict) -> None:
    """Four permitted B pairs; historical journals/counters are never rewritten."""
    path = out / "neural_starts.jsonl"
    policy = b.read(out / "source_policy.json")
    history = [json.loads(v) for v in path.read_text().splitlines()] if path.exists() else []
    starts = [r for r in history if r["status"] == "STARTED"]
    pointer = b.read(b.POINTER)
    assert (
        pointer == policy["prior_pointer"] if not history else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert len(starts) < 4 and year == b.YEARS[len(starts)]
        assert not history or history[-1]["status"] == "COMPLETED"
        assert b.read(plan_path(out))["B"]["status"] == "READY"
        b.resources(out)
    record = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        experiment="S2-B",
        year=year,
        status=status,
        global_started_pairs=154 + len(starts) + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
        previous_journal=b.read(out / "budget_amendment_300.json")["immutable_prior_journal"],
        plan=dict(path=str(plan_path(out)), sha256=b.digest(plan_path(out))),
        task_protocol=b.read(plan_path(out))["protocols"]["B"],
    )
    with path.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=29,
            definition=record["plan"],
            plan=record["plan"],
            real_journal=str(path),
            previous_journal=record["previous_journal"],
            fit_permission=False,
        ),
    )


def predict_clock(view: b.View, pos: np.ndarray, model: ClockMAG, clocks: np.ndarray) -> np.ndarray:
    model.eval()
    chunks = []
    with torch.inference_mode():
        for k in range(0, len(pos), 32):
            ix = pos[k : k + 32]
            x = torch.from_numpy(view.x(ix).reshape(-1, 48, 16))
            known = torch.from_numpy(np.repeat(clocks[ix], 20, axis=0))
            chunks.append(model(x, known).numpy().reshape(-1, 20))
    result = np.concatenate(chunks)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_CLOCK_FORECAST")
    return result


def train_clock(
    view: b.View,
    pos: np.ndarray,
    model: ClockMAG,
    opt: torch.optim.AdamW,
    n: int,
    clocks: np.ndarray,
) -> dict:
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + n).shuffle(days)
    norms = []
    model.train()
    for k in range(0, len(days), 16):
        ix = pos[np.concatenate([groups[d] for d in days[k : k + 16]])]
        x = view.x(ix)
        assert x.shape[1:] == (20, 48, 16)
        opt.zero_grad()
        mhat = model(
            torch.from_numpy(x.reshape(-1, 48, 16)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
        ).reshape(-1, 20)
        loss = previous.weighted_loss(
            mhat,
            torch.from_numpy(view.r[ix].astype(np.float32)),
            view.scale,
            b.origin_weights(view.rows.iloc[ix].session_date_et.to_numpy()),
        )
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_CLOCK_LOSS")
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True)
        norms.append(float(norm))
        b.memory()
        opt.step()
    assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(v > 1 for v in norms)
    )


def prepare_phases(
    out: Path, c: b.Components, rows: pd.DataFrame, r: np.ndarray, plans: dict
) -> dict[int, dict]:
    result = {}
    for y in b.YEARS:
        dest = out / TASK_DIRS["B"] / f"F{y % 100}"
        dest.mkdir(exist_ok=True)
        old = b.read(o1.OUT / f"F{y % 100}/phases.json")
        phases = {}
        for phase, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            cutoff = old["phases"][phase]["cutoff"]
            recipe, _ = b.fit_expanded(
                c, b.feature_fit_hours(c.grid, rows, cutoff), cutoff, approved=True
            )
            assert recipe == b.read(o1.OUT / f"F{y % 100}/{phase}_recipe.json")
            ix = plans[y][role]
            w = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(r[ix]).ravel(), 0.5, w), 1e-8)
            assert scale == old["phases"][phase]["scale"]
            phases[phase] = dict(
                scale=scale,
                cutoff=cutoff,
                recipe_reference=str(o1.OUT / f"F{y % 100}/{phase}_recipe.json"),
            )
        result[y] = dict(year=y, phases=phases, thresholds=old["thresholds"])
        freeze(dest / "phases.json", result[y])
    freeze(out / TASK_DIRS["B"] / "phase_parity.json", dict(status="PASS_ALL_EIGHT", folds=result))
    return result


def run_clock_fold(
    out: Path,
    y: int,
    c: b.Components,
    rows: pd.DataFrame,
    r: np.ndarray,
    pos: dict,
    fold: dict,
    clocks: np.ndarray,
) -> None:
    dest = out / TASK_DIRS["B"] / f"F{y % 100}"
    started = time.monotonic()
    trace = []
    initial = fold["phases"]["initial"]
    restricted = fold["phases"]["restricted"]
    inner = b.View(c, rows, r, b.read(Path(initial["recipe_reference"])), initial["scale"])
    model = model_for_clock()
    init_sha = b.initial_hash(model)
    opt = b.optimizer(model)
    assert not opt.state
    selector = b.Selector()
    best = {}
    journal(
        out,
        y,
        "STARTED",
        dict(phase="initial", run_id=f"HF20-S2B-F{y % 100}-CLOCK-S42", parameters=6443),
    )
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            tick = time.monotonic()
            train = train_clock(inner, pos["inner_train"], model, opt, n, clocks)
            z = predict_clock(inner, pos["selector"], model, clocks)
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
                    validation_M_MSE=val,
                    selected=selector.selected,
                    seconds=time.monotonic() - tick,
                    **train,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2-B", y, "selector", n, val, "selected", selector.selected, flush=True)
        model.load_state_dict(best)
        freeze(
            dest / "selection.json",
            dict(
                vars(selector),
                initial_scale=initial["scale"],
                selected_initial_sha256=b.initial_hash(model),
            ),
        )
        journal(
            out, y, "SELECTED", dict(epoch=selector.selected, raw_minimum_epoch=selector.raw_epoch)
        )
        del model, opt, best
        gc.collect()
        scale = restricted["scale"]
        refit = b.View(c, rows, r, b.read(Path(restricted["recipe_reference"])), scale)
        model = model_for_clock()
        assert b.initial_hash(model) == init_sha
        opt = b.optimizer(model)
        assert not opt.state
        journal(out, y, "REFITTING", dict(epochs=selector.selected, cutoff=restricted["cutoff"]))
        for n in range(1, selector.selected + 1):
            tick = time.monotonic()
            train = train_clock(refit, pos["restricted_refit"], model, opt, n, clocks)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - tick, **train))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S2-B", y, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        zcal = predict_clock(refit, pos["calibration"], model, clocks)
        cal = pd.read_parquet(c3.root(y) / "calibration_scores.parquet")
        cal = cal[[*c3.META, "A"]].copy()
        np.testing.assert_array_equal(cal.A, abs(r[pos["calibration"]]).ravel())
        cal["Mhat"] = zcal.ravel()
        coeff = c3.fit_categories(cal, scale)
        pd.DataFrame(coeff).to_csv(dest / "calibration_coefficients.csv", mode="x", index=False)
        cal.to_parquet(dest / "calibration_scores.parquet", index=False, compression="zstd")
        factors = {v["group"]: v["c_star"] for v in coeff}
        z = predict_clock(refit, pos["oos"], model, clocks)
        reloaded = model_for_clock()
        reloaded.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, predict_clock(refit, pos["oos"], reloaded, clocks))
        assert b.initial_hash(model) == frozen
        original = pd.read_parquet(c3.root(y) / "oos_scores.parquet")
        frame = original[[*c3.META, "A"]].copy()
        np.testing.assert_array_equal(frame.A, abs(r[pos["oos"]]).ravel())
        frame["Mhat"] = z.ravel()
        frame["CLOCK-RAW"] = previous.raw_decode(z, scale).ravel()
        frame["CLOCK-C3"] = c3.decode(z.ravel(), scale, frame.category.map(factors).to_numpy())
        frame.to_parquet(dest / "oos_scores.parquet", index=False, compression="zstd")
        result = dict(
            year=y,
            status="COMPLETED",
            run_id=f"HF20-S2B-F{y % 100}-CLOCK-S42",
            parameters=6443,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_scale=initial["scale"],
            scale=scale,
            initial_sha256=init_sha,
            frozen_parameter_sha256=frozen,
            reload_max_error=0,
            optimizer_fresh=True,
            seconds=time.monotonic() - started,
            peak_rss_bytes=b.memory(),
        )
        freeze(dest / "result.json", result)
        journal(out, y, "COMPLETED", result)
        del inner, refit, model, opt, reloaded
        gc.collect()
    except BaseException as exc:
        journal(out, y, "FAILED", dict(error=repr(exc), retry=False))
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
    if not args.run:
        if plan_path(out).exists():
            print(json.dumps(b.read(plan_path(out)), indent=2))
            return
        preflight(out)
        return
    if (out / "neural_starts.jsonl").exists():
        raise SystemExit("NO_RETRY_STARTED_NAMESPACE")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    grid, rows = b.metadata()
    plans = saved_plans(rows)
    verify_before_fits(out, grid, rows, plans)
    clocks, _ = clock_values(rows, sessions("2010-07-01", "2025-01-10"))
    report(out)
    (out / ".gitignore").write_text("*.pt\n*.parquet\n")
    c, r = b.source_components(grid, rows)
    phases = prepare_phases(out, c, rows, r, plans)
    for y in b.YEARS:
        run_clock_fold(out, y, c, rows, r, plans[y], phases[y], clocks)
        b.write(
            out / "continuation.json",
            dict(
                completed_B=list(range(2021, y + 1)),
                pending_B=list(range(y + 1, 2025)),
                C="BLOCKED",
                D="BLOCKED",
                retry=False,
            ),
        )
        report(out)


def report(out: Path) -> None:
    """Separate task verdicts; completed B scores only, no new model calls."""
    receipt = b.read(plan_path(out))
    proof = (
        b.read(out / "source_validation.json") if (out / "source_validation.json").exists() else {}
    )
    for task, field in [("C", "component_coverage"), ("D", "gap_coverage")]:
        title = (
            "decomposition-assisted four-hour MAG"
            if task == "C"
            else "dedicated close-to-open gap magnitude"
        )
        parts = [
            f"# S2-{task} — {title}",
            "**Status: BLOCKED. Zero neural/non-neural fits and no forecast metrics.**",
            (
                "This is a separate scientific task, not an adverse score or a result "
                "of S2-B. No alternative label/population/architecture was substituted."
            ),
            "## Frozen specification",
            (
                f"Protocol: `{receipt['protocols'][task]['path']}`. The original scientific "
                "specification preceded numerical source proof and fits. D's append-only "
                "v2 removes inherited four-hour scale/threshold reference fields from "
                "chronology metadata; no gate or scientific design changed. No gap "
                "scale or threshold was fitted or transferred."
            ),
            "\n".join("- " + r for r in receipt[task]["reasons"]),
            b.markdown(pd.DataFrame(receipt[field])),
            "## Source and timing proof",
        ]
        if task == "C":
            parts += [
                (
                    "The saved S4 artifact explicitly stores original entry/exit, genuine "
                    "end-of-session price, next09:30 minute open, and signed pre/gap/post "
                    "returns. The executed reader used adjusted, "
                    "quarantined-source-filtered genuine minute close at actual "
                    "session_close−1min and genuine next-session minute open; no15:30 "
                    "surrogate, hourly proxy, synthetic target or new minute read is "
                    "permitted. Original source/masks remain unchanged."
                ),
                b.markdown(pd.DataFrame(proof.get("details", []))),
                b.markdown(pd.DataFrame(proof.get("examples", []))),
                (
                    "Signed additivity on supported cells passes atol1e−12/rtol1e−11; "
                    f"maximum error {proof.get('max_signed_additivity_error', 'NOT CHECKED')}. "
                    "This does not fill missing components. abs(total) is not a sum "
                    "of component magnitudes; auxiliary labels are never inputs."
                ),
                (
                    "The all-original-key auxiliary source gate fails in every fold. "
                    "Dropping these observations, imputing components or using a "
                    "differently defined close would change this frozen experiment. No S2-C"
                    " model, aux head fit, calibration or B/C performance comparison was "
                    "run."
                ),
            ]
        else:
            parts += [
                (
                    "The eligibility calculation is new: normal full sessions only, "
                    "one15:30 origin, source-input eligibility, all20 genuine current16:00 "
                    "end-of-session references and next09:30 minute opens, original "
                    "action-basis safeguard, next-open+2min maturity and the48-step role "
                    "embargo. It does not reuse4h label eligibility/maturity. For example, "
                    "F21 selector has53 eligible gap sessions rather than47 original4h15:30"
                    " origins. Early closes are excluded by the known calendar; no "
                    "remapping to another origin."
                ),
                (
                    "Minimums were declared before counting:252 training/refit sessions,50 "
                    "selector,25 calibration,100 OOS; at least5 sessions in every "
                    "selector/calibration month and all12 OOS months. F22 has31 selector "
                    "sessions and a month with3; F23 has48 and a month with4. These were "
                    "not relaxed. Other admissible years were not fitted into a different "
                    "partial design after an any-fold gate failed."
                ),
                (
                    "The intended primary is own-gap global-smear LSTM, with raw "
                    "diagnostic, own phase s_gap and stock raw mean/median/last20 genuinely"
                    " matured gap controls. None was fitted. No 4h scale, predictor or "
                    "baseline was relabeled as a gap forecast; no gap metric is compared "
                    "numerically with4h MSE. A15:32 forecast precedes the16:00-to-next09:30"
                    " holding interval; actual execution/auction fills are unverified."
                ),
            ]
        parts += [
            "## Decision and boundaries",
            (
                "Reconsider only through a separate researcher decision about this "
                "exact source/coverage blocker. No new source, proxy, selector "
                "extension, minimum reduction, extra fold or future-data release is "
                "approved.2021–24 are exploratory/post-search;2025 outcomes and "
                "protected2026 values/hashes remain unused. No trading/options/strategy"
                " or deferred C0-intraday/M1-overnight route was run."
            ),
        ]
        (out / TASK_DIRS[task] / REPORTS[task]).write_text("\n\n".join(parts) + "\n")
    dest = out / TASK_DIRS["B"]
    years = [y for y in b.YEARS if (dest / f"F{y % 100}/result.json").exists()]
    status = "COMPLETE" if len(years) == 4 else "PARTIAL" if years else "READY"
    notes = b.read(out / "interpretation.json") if (out / "interpretation.json").exists() else {}
    header = [
        "# S2-B — explicit clock/calendar MAG",
        (
            f"**Status: {status} — {len(years)}/4 folds.** "
            "Original four-hour target, exploratory/post-search."
        ),
        notes.get(
            "executive",
            "Four-fold verdict will be based on the frozen same-target comparisons below.",
        ),
        "## Design and fairness",
        (
            "One shared H32/one-layer LSTM on the original48×16 own-stock FT16 "
            "windows; seed42/CPU float32. Ten known schedule values enter the "
            "scalar head after final-hidden dropout.10: seven slot one-hots, "
            "current-session remaining trading minutes/240, known horizon-crossing "
            "flag, and calendar days until next scheduled XNYS session/7. No "
            "metadata sequence, stock/peer ID, event input, proxy or future return "
            "enters the model. The trunk is unchanged; head32→1 becomes42→1, "
            "increasing parameters6,433→6,443. This tests input/head/optimization "
            "together, not information isolated from parameter capacity."
        ),
        (
            "Calendar entries follow the executed XNYS schedule and actual early "
            "closes. The complete distinct vector dictionary is "
            "clock_dictionary.csv; regular09:30 has390/240 remaining and crossing0,"
            " early-close09:30 has210/240 and crossing1. Metadata is repeated "
            "identically across20 stocks at an origin and is not dropped. Last15:30"
            " input history still contains48 completed scheduled full hours; its "
            "closing stub is not an input hour. The calendar-only lookup may "
            "include January2025 dates; no2025 market observation is read."
        ),
        (
            "Original M=log1p(abs(R_total)/own_phase_s) transformed MSE, original "
            "qualified-best selector and exact Design A role indices/cutoffs are "
            "preserved. Phase target scales and input recipes are independently "
            "verified on legal prefixes before starts. Each selected count gets a "
            "fresh seed42 model/empty optimizer through September. Reserved Oct–Dec"
            " is only for this new encoder’s own fixed C3 IO smearing (session "
            "shrinkage kappa25); all coefficients freeze before next-year scores. "
            "Raw decoder is diagnostic. No new calibration choice or post-OOS "
            "rescue."
        ),
        b.markdown(pd.DataFrame(receipt["role_counts"])),
        (
            "Frozen C3/M1/C0/C1a/B0 comparisons retain original keys, labels, "
            "scales and forecast vectors. C0-vs-C3 intraday preference remains "
            "metric-dependent and unresolved. No deferred C0-intraday/M1-overnight "
            "routed experiment is created."
        ),
    ]
    if years:
        records = []
        group_records = []
        fits = []
        coeffs = []
        frames = {}
        arms = [
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
        ]
        for y in years:
            f = pd.read_parquet(c3.root(y) / "oos_scores.parquet")
            new = pd.read_parquet(dest / f"F{y % 100}/oos_scores.parquet")
            pd.testing.assert_frame_equal(
                f[[*c3.META, "A"]], new[[*c3.META, "A"]], check_dtype=False
            )
            f["C3"] = previous.frozen_c3(f, y)
            for arm in arms[:2]:
                f[arm] = new[arm]
            frames[y] = f
            fits.append(b.read(dest / f"F{y % 100}/result.json"))
            co = pd.read_csv(
                dest / f"F{y % 100}/calibration_coefficients.csv", float_precision="round_trip"
            )
            co.insert(0, "year", y)
            coeffs.append(co)
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
            threshold = b.read(dest / f"F{y % 100}/phases.json")["thresholds"]
            cuts = np.unique(
                [
                    b.quantile(f.C3.to_numpy(), q, f.weight.to_numpy())
                    for q in np.arange(0.1, 1, 0.1)
                ]
            )
            bins = np.searchsorted(cuts, f.C3, side="left") + 1
            masks = [("slot", v, f.slot.eq(v)) for v in b.SLOTS]
            quarter = pd.to_datetime(f.session_date_et).dt.to_period("Q").astype(str).str[-2:]
            masks += [("quarter", v, quarter.eq(v)) for v in sorted(quarter.unique())]
            for group, base_mask in [
                ("ALL", pd.Series(True, index=f.index)),
                ("INTRADAY", f.category.eq("INTRADAY")),
                ("OVERNIGHT", f.category.eq("OVERNIGHT")),
            ]:
                for level in [95, 99]:
                    event = f.A.gt(threshold[str(level)])
                    masks += [
                        (f"tail_{group}", f"PREFIX{level}", event & base_mask),
                        (f"tail_{group}", f"LE_PREFIX{level}", ~event & base_mask),
                    ]
            masks += [
                ("C3_decile", str(v), pd.Series(bins == v, index=f.index)) for v in np.unique(bins)
            ]
            for arm in ["CLOCK-C3", "CLOCK-RAW", "C3", "M1", "C0", "B0-VOL", "B0-CLOCK"]:
                total = b.metrics(f, arm)["raw_MSE"]
                low = f.groupby("origin_id")[arm].rank(method="average").le(10.5)
                for field, label, take in masks:
                    h = f.loc[take]
                    if h.empty:
                        continue
                    contribution = float((h.weight * (h[arm] - h.A) ** 2).sum())
                    group_records.append(
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
                            C3_min=float(h.C3.min()),
                            C3_max=float(h.C3.max()),
                        )
                    )
        m = pd.DataFrame(records)
        g = pd.DataFrame(group_records)
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
                    m.loc[
                        m.year.eq("EQ") & m.scope.eq("FULL") & m.arm.eq(str(arm)), "raw_MSE"
                    ].iloc[0]
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
            ("FULL", "CLOCK-C3", "C3"),
            ("FULL", "CLOCK-C3", "M1"),
            ("FULL", "CLOCK-C3", "B0-VOL"),
            ("FULL", "CLOCK-RAW", "C0"),
            ("INTRADAY", "CLOCK-C3", "C3"),
            ("OVERNIGHT", "CLOCK-C3", "C3"),
        ]:
            months = {}
            for y, f in frames.items():
                h = f if scope == "FULL" else f.loc[f.category.eq(scope)]
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
            for result in previous.paired_months(months):
                reference = float(
                    m.loc[
                        m.year.eq(result["year"]) & m.scope.eq(scope) & m.arm.eq(right), "raw_MSE"
                    ].iloc[0]
                )
                pairs.append(
                    dict(
                        scope=scope,
                        left=left,
                        right=right,
                        **result,
                        percent=100 * result["delta"] / reference,
                        includes_zero=result["low"] <= 0 <= result["high"],
                    )
                )
        paired = pd.DataFrame(pairs)
        m.to_csv(dest / "metrics.csv", index=False)
        g.to_csv(dest / "groups.csv", index=False)
        paired.to_csv(dest / "paired_mse.csv", index=False)
        pd.DataFrame(fits).to_csv(dest / "fit_summary.csv", index=False)
        pd.concat(coeffs).to_csv(dest / "calibration_coefficients.csv", index=False)
        header += [
            "## Fits and independent calibration",
            b.markdown(
                pd.DataFrame(fits)[
                    [
                        "year",
                        "selected_epoch",
                        "selector_epochs",
                        "raw_minimum_epoch",
                        "initial_scale",
                        "scale",
                        "parameters",
                        "seconds",
                        "peak_rss_bytes",
                    ]
                ]
            ),
            b.markdown(
                pd.concat(coeffs)[
                    [
                        "year",
                        "group",
                        "c0",
                        "c_raw",
                        "n_eff",
                        "rho",
                        "c_star",
                        "q_max",
                        "top10_share",
                        "top1pct_share",
                    ]
                ]
            ),
            (
                "These are new model-specific calibration moments, not transferred "
                "historical C3 coefficients. q uses unconstrained Mhat. "
                "Finite/nonnegative decoder guards and exact selected checkpoint reload"
                " equality are required. F24 tail precision remains limited; no q "
                "trimming or alternative scalar map is fitted."
            ),
            "## Same-target annual and equal-year results",
            b.markdown(
                m.loc[
                    (
                        m.scope.eq("FULL")
                        & m.arm.isin(
                            ["CLOCK-C3", "CLOCK-RAW", "C3", "M1", "C0", "B0-VOL", "B0-CLOCK"]
                        )
                    ),
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
                    ],
                ]
            ),
            (
                "All baselines and both category scopes are in metrics.csv. Raw MSE "
                "uses squared absolute-log-return units; MAE/means/bias use absolute "
                "log-return units. Annual weights are equal "
                "stocks→origins/session→sessions/year; conditional raw scores restrict "
                "and normalize the original weights. EQ averages four annual metrics, "
                "ratio of equal-year means. Ranking uses existing midrank "
                "origin→session→year reducer. Four years are not four seeds or "
                "independent confirmation."
            ),
            "## Paired month-block uncertainty",
            b.markdown(paired),
            (
                "400 draws/seed22042 whole-calendar-month blocks within year, then "
                "equal years. Conditional numerator and original group weight mass are "
                "sampled together. No IID rows; intervals condition on selected "
                "encoders/scalars and repeated research, not selection-adjusted "
                "significance."
            ),
            "## Clocks, calendar periods, tails and ranking",
            notes.get(
                "groups",
                (
                    "Annual/EQ seven-slot, quarter, shared C3 decile, category-prefix95/99 "
                    "cohort/complement statistics are in groups.csv."
                ),
            ),
            b.markdown(
                g.loc[
                    g.year.eq("EQ")
                    & g.arm.eq("CLOCK-C3")
                    & g.field.isin(["slot", "tail_OVERNIGHT"]),
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
            (
                "Outcome-selected tails are retrospective diagnostics, not event "
                "probabilities; their underforecast amplitudes alone do not prove "
                "conditional-mean bias. False-low means average within-origin magnitude"
                " rank≤10.5. Reliability groups use identical saved-C3 decile "
                "membership across arms, with explicit annual numeric ranges/counts; no"
                " map is fitted on the bins. Quarter/clock/stock observations are "
                "dependent, not independent replications."
            ),
            b.markdown(
                m.loc[
                    m.year.eq("EQ") & m.scope.eq("FULL"),
                    [
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
                "Clock metadata enters as a common additive term in the linear M head "
                "for all stocks at an origin; it cannot itself reorder those stocks "
                "absent clamp ties. Changed rankings can arise through newly trained "
                "trunk/head weights. Do not interpret level correction or a nonzero "
                "clock-head gradient as new cross-sectional information. Pair ties get "
                "half credit (chance.5); retrieval uses fractional boundary ties "
                "(chance.2)."
            ),
            "## Scientific decision",
            notes.get(
                "decision",
                (
                    "Do not launch another experiment. The primary criterion is calibrated "
                    "raw MSE versus frozen same-task C3, with MAE/ordinary/tail/rank "
                    "trade-offs."
                ),
            ),
            "## Reproduction and integrity",
            notes.get(
                "verification",
                "Tests/static/resource receipts are in the combined session handoff.",
            ),
            (
                "Run `.venv/bin/python -m lstm_data.hf20_stage2_bcd --report` for "
                "saved-score replay only; no training/inference or raw-source numerical"
                " reads. The original `--run` is single use and refuses a started "
                "namespace. No future data, source repairs, unselected forecasts, "
                "deferred router, dashboard, options/trading, extra seed or automatic "
                "next stage."
            ),
        ]
    (dest / REPORTS["B"]).write_text("\n\n".join(header) + "\n")
    overall = "PARTIAL (S2-B complete; S2-C/D blocked)" if len(years) == 4 else "IN PROGRESS"
    handoff = [
        "# Stage2 combined research handoff",
        f"**Overall execution: {overall}.** Independent targets and verdicts, no pooled winner.",
        b.markdown(
            pd.DataFrame(
                [
                    dict(
                        experiment="S2-B",
                        target="original4h absolute endpoint return",
                        population="original7-slot complete20 keys",
                        status=status,
                        primary_reference="frozen C3",
                        report=str(dest / REPORTS["B"]),
                    ),
                    dict(
                        experiment="S2-C",
                        target="same4h magnitude plus signed auxiliary labels",
                        population="original4h keys require genuine components",
                        status="BLOCKED",
                        primary_reference="S2-B and C3, not evaluated",
                        report=str(out / TASK_DIRS["C"] / REPORTS["C"]),
                    ),
                    dict(
                        experiment="S2-D",
                        target="pure genuine close-to-next-open gap magnitude",
                        population="normal-session15:30 only, new maturity",
                        status="BLOCKED",
                        primary_reference="own-gap controls, not fitted",
                        report=str(out / TASK_DIRS["D"] / REPORTS["D"]),
                    ),
                ]
            )
        ),
        notes.get(
            "executive",
            "S2-B result awaits completion; two independent gates failed before any neural start.",
        ),
        (
            "S2-C fails genuine component completeness; S2-D fails the predeclared "
            "selector session/month coverage. Neither was silently converted into a"
            " different task. No S2-D MSE is compared against four-hour MSE. No new"
            " gap baseline was fitted and no auxiliary label was used as an "
            "inference feature."
        ),
        (
            "Budget ceiling amendment200→300 preserved opening count154 and all "
            "historical journals. Campaign maximum12 starts/24 phases; only S2-B "
            f"is feasible, {len(years)} completed starts/{2 * len(years)} phases so far; "
            "planned final158/300. Capacity is not authority for more experiments."
        ),
        (
            "Intraday C0-MAE versus C3-MSE preference is unresolved. The deferred "
            "C0-intraday/M1-overnight whole-panel route was not created or "
            "scored.2025 outcomes and protected2026 data/hashes remain untouched. "
            "No network source, minute rebuild, bulk copy, strategy/options/P&L, "
            "commit or push."
        ),
        notes.get(
            "verification", "See final tests/static/editor verification in the Codex handoff."
        ),
        (
            "STOP after the three reports. Researcher review is required before "
            "changing a gate, label, clock feature, route, model or confirmation "
            "protocol."
        ),
    ]
    (out / "STAGE2_COMBINED_RESEARCH_HANDOFF.md").write_text("\n\n".join(handoff) + "\n")


if __name__ == "__main__":
    main()
