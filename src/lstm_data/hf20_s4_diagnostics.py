"""S4 role exports, independent reconciliation and complete cohort supplements."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import digest
from .hf20_ranking_continue_report import cohort_tables
from .hf20_ranking_diagnostics import export_diagnostics, verify_exports
from .hf20_s4_data import ROLES, S4Data


def export(
    data: S4Data, year: int, role: str, arm: str, scores: np.ndarray, dest: Path, execution: str
) -> dict:
    result = export_diagnostics(data, year, role, arm, scores, dest)
    p = dest / f"{role}_scores.parquet"
    f = pd.read_parquet(p)
    positions = data.positions(year, role)
    rows = data.rows.iloc[positions]
    for key in [
        "slot",
        "category",
        "context",
        "conditional_open",
        "regular_session",
        "trading_minutes",
        "true_session_close_complete20",
        "opening_latency",
    ]:
        f[key] = np.repeat(rows[key].to_numpy(), 20)
    f["input_last_full_hour_end_utc"] = np.repeat(
        data.grid.hour_end_utc.iloc[rows.entry_index.to_numpy(int)].to_numpy(), 20
    )
    f["execution_sha256"] = execution
    f["target_contract"] = "S4A240_REGULAR_MINUTES_PRICE_ONLY_REFERENCE_ORIGIN_PLUS2_ISSUE"
    if data.target_components is not None:
        f = join_components(f, data.target_components)
    f.to_parquet(p, index=False)
    return result


def join_components(f: pd.DataFrame, components: pd.DataFrame) -> pd.DataFrame:
    """Exact-key join with direct/component return conservation; no fabricated prices."""
    fields = [
        "origin_id",
        "ticker",
        "direct_return",
        "origin_to_close",
        "close_to_next_open",
        "next_open_to_exit",
        "decomposition_supported",
        "decomposition_status",
    ]
    f = f.merge(
        components[fields],
        on=["origin_id", "ticker"],
        validate="one_to_one",
        how="left",
    )
    np.testing.assert_array_equal(f.return_4h, f.direct_return)
    supported = f.decomposition_supported.fillna(False).to_numpy(bool)
    np.testing.assert_allclose(
        (f.origin_to_close + f.close_to_next_open + f.next_open_to_exit)[supported],
        f.return_4h[supported],
        atol=1e-12,
        rtol=1e-11,
    )
    return f


def verify(data: S4Data, year: int, dest: Path, *, rehearsal: bool = False) -> dict:
    """All4 roles must reconcile before a real run can publish its PASS gate."""
    paths = [dest / f"{role}_scores.parquet" for role in ROLES]
    checks = verify_exports(dest.parent, paths)
    strata = []
    for role, p in zip(ROLES, paths):
        f = pd.read_parquet(p)
        pos = data.positions(year, role)
        np.testing.assert_array_equal(f.ticker, np.tile(data.symbols, len(pos)))
        np.testing.assert_array_equal(f.origin_id.to_numpy()[::20], data.rows.iloc[pos].origin_id)
        np.testing.assert_array_equal(f.return_4h.to_numpy().reshape(-1, 20), data.returns[pos])
        if (
            not pd.to_datetime(f.input_last_full_hour_end_utc, utc=True)
            .le(pd.to_datetime(f.entry_end_utc, utc=True))
            .all()
        ):
            raise ValueError("S4_UNFINISHED_INPUT")
        a, b, c, d = cohort_tables(p)
        for name, table in [
            ("energy_and_objective_cohorts", a),
            ("stock_month_sector_quality", b),
            ("error_ranked_cohorts", c),
            ("paired_cohort_difficulty", d),
        ]:
            table.to_csv(dest / f"{role}_{name}.csv", index=False)
        origins = pd.read_csv(dest / f"{role}_origins.csv")
        labels = data.rows.iloc[pos][["origin_id", "category", "conditional_open"]]
        o = origins.merge(labels, on="origin_id", validate="one_to_one")
        for label, mask in [
            ("ALL", np.ones(len(o), bool)),
            ("OLD_MORNING", o.slot.isin(["10:30", "11:30"])),
            ("NEW_AFTERNOON", o.slot.isin(["12:30", "13:30", "14:30", "15:30"])),
            ("OPENING", o.conditional_open),
            *((v, o.category.eq(v)) for v in ["INTRADAY", "OVERNIGHT"]),
        ]:
            q = o.loc[mask]
            if q.empty:
                strata.append(
                    dict(role=role, group=label, status="UNAVAILABLE", origins=0, sessions=0)
                )
                continue
            daily = q.groupby("session_date_et")[
                ["ic", "top4", "bottom4", "concordance", "rank_mse"]
            ].mean()
            strata.append(
                dict(
                    role=role,
                    group=label,
                    status="EXPLORATORY",
                    origins=len(q),
                    sessions=len(daily),
                    **daily.mean().to_dict(),
                )
            )
        # Primary all-origin and fixed secondary equal-category weights are distinct.
        cat = (
            o.groupby(["category", "session_date_et"])[["ic", "top4", "bottom4", "concordance"]]
            .mean()
            .groupby("category")
            .mean()
        )
        strata.append(
            dict(
                role=role,
                group="EQUAL_CATEGORY_SECONDARY",
                status="DESCRIPTIVE_DEPENDENT",
                origins=len(o),
                sessions=o.session_date_et.nunique(),
                **{str(k): float(v) for k, v in cat.mean().items()},
            )
        )
        shared = o.groupby(["session_date_et", "category"]).ic.mean().unstack("category")
        if {"INTRADAY", "OVERNIGHT"}.issubset(shared.columns):
            shared = shared.dropna(subset=["INTRADAY", "OVERNIGHT"])
            if len(shared):
                shared["difference"] = shared.OVERNIGHT - shared.INTRADAY
                shared["month"] = shared.index.astype(str).str[:7]
                bins = shared.groupby("month").difference.agg(["sum", "count"])
                rng = np.random.default_rng(22042)
                draw = rng.integers(len(bins), size=(400, len(bins)))
                sampled = bins["sum"].to_numpy()[draw].sum(1) / bins["count"].to_numpy()[draw].sum(
                    1
                )
                lo, hi = np.quantile(sampled, [0.025, 0.975])
                strata.append(
                    dict(
                        role=role,
                        group="MATCHED_SESSION_OVERNIGHT_MINUS_INTRADAY",
                        status="DESCRIPTIVE_SHARED_SESSIONS_WHOLE_MONTH_BLOCKS",
                        sessions=len(shared),
                        ic=float(shared.difference.mean()),
                        low=float(lo),
                        high=float(hi),
                        replicates=400,
                    )
                )
                shared.to_csv(dest / f"{role}_matched_category_sessions.csv")
    pd.DataFrame(strata).to_csv(dest / "category_and_anchor_metrics.csv", index=False)
    receipt = dict(
        status="PASS_NUMERICAL",
        roles=checks,
        rehearsal=rehearsal,
        new_fits=0 if rehearsal else None,
    )
    (dest / "NUMERICAL_DIAGNOSTICS_PASS.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def gate(dest: Path, extra: dict) -> None:
    """Plots and numerical evidence are both mandatory, never performance-threshold gates."""
    for name in ("NUMERICAL_DIAGNOSTICS_PASS.json", "VISUAL_DIAGNOSTICS_PASS.json"):
        if not (dest / name).exists():
            raise ValueError("S4_COMPLETE_DIAGNOSTICS_GATE_REQUIRED:" + name)
        receipt = json.loads((dest / name).read_text())
        expected = (
            "PASS_NUMERICAL" if name.startswith("NUMERICAL") else "PASS_RECONCILED_VISUAL_PAYLOAD"
        )
        if receipt.get("status") != expected:
            raise ValueError("S4_DIAGNOSTIC_STATUS_NOT_PASS:" + name)
    files = {
        str(p): digest(p) for p in sorted(dest.rglob("*")) if p.is_file() and p.name != "PASS.json"
    }
    with (dest / "PASS.json").open("x") as f:
        json.dump(
            dict(status="PASS_TECHNICAL_AND_DIAGNOSTICS", files=files, **extra),
            f,
            indent=2,
            allow_nan=False,
        )
