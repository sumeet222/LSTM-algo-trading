"""Boolean source-dependency potential only: no FT, TG, fitted or return values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS, digest
from .hf1m_action_source import NAMESPACE, publish_json, publish_table


def load_hours(manifest_path: Path) -> pd.DataFrame:
    """Exact new-source manifest only; reject legacy roots/revisions and raw fallbacks."""
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("namespace") != NAMESPACE:
        raise ValueError("ACTION_SOURCE_NAMESPACE_REQUIRED")
    expected = Path("data/processed/hf20_hf1m_long_v1_action_qa_v1") / manifest_path.parent.name
    if Path(manifest["private_root"]) != expected:
        raise ValueError("ACTION_SOURCE_PATH_REQUIRED")
    frames = []
    for record in manifest["monthly"]:
        ref = record["files"]["hourly"]
        path = Path(ref["path"])
        if path != expected / "hourly" / (record["month"] + ".parquet"):
            raise ValueError("ACTION_SOURCE_PATH_REQUIRED")
        if path.stat().st_size != ref["bytes"] or digest(path) != ref["sha256"]:
            raise ValueError("ACTION_SOURCE_BYTES_CHANGED")
        frames.append(pd.read_parquet(path))
    result = pd.concat(frames, ignore_index=True)
    if not result.is_rth.all() or not result.price_adjustment_version.eq(NAMESPACE).all():
        raise ValueError("RTH_ADJUSTMENT_IDENTITY_CHANGED")
    return result


def full_window(valid: np.ndarray, count: int) -> np.ndarray:
    """Scheduled-position AND; missing rows are never compressed out of history."""
    return pd.DataFrame(valid).rolling(count, min_periods=count).sum().eq(count).to_numpy()


def no_boundary_crossing(basis: np.ndarray, entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Levels can be valid individually while a return across their bases is invalid."""
    return basis[entry] == basis[exit_]


def origin_masks(hours: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Two closing-price envelopes plus OHLC/volume diagnostics and longer warmup.

    These are source availability upper bounds. Incomplete FT channels still need
    a separately approved causal feature-level policy; nothing is imputed here.
    Future endpoint validity is separate and cannot modify past input eligibility.
    """
    full = hours.loc[~hours.is_stub].copy()
    grid = (
        full[["hour_start_utc", "hour_end_utc", "session_date_et"]]
        .drop_duplicates()
        .sort_values("hour_start_utc")
        .reset_index(drop=True)
    )
    if len(full) != len(grid) * len(SYMBOLS):
        raise ValueError("ALL20_HOURLY_GRID_REQUIRED")

    def matrix(field: str) -> np.ndarray:
        return (
            full.pivot(index="hour_start_utc", columns="ticker", values=field)
            .reindex(index=grid.hour_start_utc, columns=SYMBOLS)
            .to_numpy()
        )

    close0 = matrix("genuine_close").astype(bool)
    close5 = matrix("hour_proxy_price_usable").astype(bool)
    basis = matrix("price_basis_id")
    ohlc = (
        matrix("hour_field_usable_open")
        & matrix("hour_field_usable_high")
        & matrix("hour_field_usable_low")
    )
    volume = matrix("observed_volume_complete").astype(bool)
    groups = grid.groupby("session_date_et", sort=True).indices
    regular = [
        (str(day), np.asarray(pos, dtype=int)) for day, pos in groups.items() if len(pos) == 6
    ]
    regular_days = np.asarray([day for day, _ in regular])
    previous = np.searchsorted(regular_days, grid.session_date_et.to_numpy(), side="left") - 1
    # Structural warmup includes125 regular-session lags and at least360 genuine
    # hourly updates. It does not compute an EMA, momentum or historical return.
    daily_end = np.asarray([pos[-1] for _, pos in regular], dtype=int)
    warmup = previous >= 125
    prefix = np.cumsum(close0, axis=0) >= 360
    basis_ok = np.ones_like(close0)
    cop = SYMBOLS.index("COP")
    for index in range(len(grid)):
        if previous[index] >= 125:
            oldest = daily_end[previous[index] - 125]
            basis_ok[index, cop] = basis[oldest, cop] == basis[index, cop]
        elif grid.session_date_et.iloc[index] >= "2012-05-01":
            basis_ok[index, cop] = False
    # A window containing earlier pre-boundary feature steps must also reset;
    # this extends COP propagation by48 scheduled positions, not arbitrary years.
    causal_basis_48 = full_window(basis_ok, 48)
    warm = warmup[:, None] & prefix
    inputs0_before = full_window(close0, 48) & warm
    inputs5_before = full_window(close5, 48) & warm
    inputs0 = inputs0_before & causal_basis_48
    inputs5 = inputs5_before & causal_basis_48
    ohlc48 = inputs5 & full_window(ohlc, 48)
    before_ohlc48 = inputs5_before & full_window(
        matrix("genuine_open") & (matrix("genuine_minutes") > 0), 48
    )
    volume48 = full_window(volume, 48)
    volume_basis = np.ones_like(close0)
    dates = grid.session_date_et.to_numpy()
    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]
    for action in facts:
        if action["kind"] != "SPLIT":
            continue
        j = SYMBOLS.index(action["ticker"])
        for index in np.flatnonzero(dates >= action["date"]):
            p = previous[index]
            if p >= 59 and regular_days[p - 59] < action["date"]:
                volume_basis[index, j] = False
    records = []
    origin_meta = []
    for date, positions in regular:
        for slot in (0, 1):
            entry = positions[slot]
            exit_ = positions[slot + 4]
            future = close0[entry] & close0[exit_] & (basis[entry] == basis[exit_])
            if grid.hour_end_utc.iloc[exit_] - grid.hour_end_utc.iloc[entry] != pd.Timedelta(
                hours=4
            ):
                raise ValueError("FOUR_SAME_SESSION_COMPLETE_HOURS_REQUIRED")
            origin_id = grid.hour_end_utc.iloc[entry].isoformat()
            origin_meta.append(
                {
                    "origin_id": origin_id,
                    "session_date_et": date,
                    "entry_index": int(entry),
                    "exit_index": int(exit_),
                    "entry_end_utc": grid.hour_end_utc.iloc[entry],
                    "exit_end_utc": grid.hour_end_utc.iloc[exit_],
                }
            )
            for j, symbol in enumerate(SYMBOLS):
                records.append(
                    {
                        "origin_id": origin_id,
                        "ticker": symbol,
                        "session_date_et": date,
                        "origin_input_48_cap0": bool(inputs0[entry, j]),
                        "origin_input_48_cap5": bool(inputs5[entry, j]),
                        "origin_input_48_eligible": bool(inputs5[entry, j]),
                        "origin_input_ohlc48_potential": bool(ohlc48[entry, j]),
                        "before_action_masks_ohlc48_potential": bool(before_ohlc48[entry, j]),
                        "origin_volume48_complete": bool(volume48[entry, j]),
                        "origin_volume_history_basis_consistent": bool(volume_basis[entry, j]),
                        "before_action_masks_input_cap0": bool(inputs0_before[entry, j]),
                        "before_action_masks_input_cap5": bool(inputs5_before[entry, j]),
                        "action_crossing_input": not bool(causal_basis_48[entry, j]),
                        "origin_entry_genuine": bool(close0[entry, j]),
                        "origin_exit_genuine": bool(close0[exit_, j]),
                        "origin_future_4h_eligible": bool(future[j]),
                        "warmup_structural_ready": bool(warm[entry, j]),
                    }
                )
    result = pd.DataFrame(records)
    meta = pd.DataFrame(origin_meta)
    intersection = result.groupby("origin_id").origin_future_4h_eligible.all()
    result["origin_cross_section_20_eligible"] = result.origin_id.map(intersection)
    return (
        result,
        meta,
        {
            "full_hours": len(grid),
            "regular_sessions": len(regular),
            "candidate_origins": len(meta),
            "grid": grid,
        },
    )


def dependencies(
    hours: pd.DataFrame, masks: pd.DataFrame, meta: pd.DataFrame, events: list[dict]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Trace field-local and basis-local impact, preserving EH/stub zero effects."""
    full = hours.loc[~hours.is_stub]
    grid = (
        full[["hour_start_utc", "hour_end_utc", "session_date_et"]]
        .drop_duplicates()
        .sort_values("hour_start_utc")
        .reset_index(drop=True)
    )
    hour_deps = []
    origin_deps = []
    for event in events:
        reason = event["disposition"]
        if reason == "UNVERIFIED_RTH_LOCAL_QUARANTINE":
            own = hours.loc[
                hours.anomaly_event_ids.str.split("|").map(lambda ids: event["event_id"] in ids)
            ]
            for row in own.itertuples():
                hour_deps.append(
                    {
                        "event_id": event["event_id"],
                        "ticker": row.ticker,
                        "hour_id": row.hour_id,
                        "dependency": "HIGH_LOW_VOLUME_UNTRUSTED",
                        "close_excluded": not row.genuine_close,
                        "is_stub": row.is_stub,
                    }
                )
                where = (
                    np.flatnonzero(grid.hour_start_utc.eq(row.hour_start_utc))
                    if not row.is_stub
                    else []
                )
                if len(where):
                    index = int(where[0])
                    impacted = meta.loc[
                        (meta.entry_index >= index) & (meta.entry_index < index + 48)
                    ]
                    for origin in impacted.itertuples():
                        origin_deps.append(
                            {
                                "event_id": event["event_id"],
                                "ticker": row.ticker,
                                "origin_id": origin.origin_id,
                                "dependency": "OHLC_CHANNEL_CONTEXT48",
                                "price_input_excluded": False,
                                "future_endpoint_excluded": False,
                                "ohlc_context_untrusted": True,
                            }
                        )
        elif reason == "COP_2012_SPINOFF_LOCAL_BOUNDARY":
            affected = masks.loc[
                masks.ticker.eq("COP")
                & masks.session_date_et.ge("2012-05-01")
                & masks.action_crossing_input
            ]
            for origin in affected.itertuples():
                origin_deps.append(
                    {
                        "event_id": event["event_id"],
                        "ticker": "COP",
                        "origin_id": origin.origin_id,
                        "dependency": "COP125D_PLUS_CONTEXT48",
                        "price_input_excluded": True,
                        "future_endpoint_excluded": False,
                        "ohlc_context_untrusted": False,
                    }
                )
            boundary = hours.loc[
                hours.ticker.eq("COP")
                & hours.session_date_et.eq("2012-05-01")
                & hours.action_boundary
            ]
            for row in boundary.itertuples():
                hour_deps.append(
                    {
                        "event_id": event["event_id"],
                        "ticker": "COP",
                        "hour_id": row.hour_id,
                        "dependency": "UNTREATED_SPINOFF_BASIS_BOUNDARY",
                        "close_excluded": False,
                        "is_stub": row.is_stub,
                    }
                )
    return pd.DataFrame(hour_deps), pd.DataFrame(origin_deps)


def summarize(masks: pd.DataFrame, start: str, stop: str) -> dict:
    """Count source potential on proposed date intervals; no split stores are built."""
    chosen = masks.loc[masks.session_date_et.between(start, stop)]
    grouped = chosen.groupby("origin_id")
    future = grouped.origin_future_4h_eligible.all()
    result = {"schedule_origins": len(grouped), "future20": int(future.sum())}
    for scheme in ("cap0", "cap5"):
        result["input20_" + scheme] = int(grouped["origin_input_48_" + scheme].all().sum())
        result["joint20_" + scheme] = int(
            (grouped["origin_input_48_" + scheme].all() & future).sum()
        )
        result["before_joint20_" + scheme] = int(
            (grouped["before_action_masks_input_" + scheme].all() & future).sum()
        )
    result["ohlc_joint20"] = int((grouped.origin_input_ohlc48_potential.all() & future).sum())
    result["before_ohlc_joint20"] = int(
        (grouped.before_action_masks_ohlc48_potential.all() & future).sum()
    )
    result["complete_volume48_joint20"] = int(
        (grouped.origin_volume48_complete.all() & future).sum()
    )
    return result


def run(out: Path) -> None:
    release = json.loads((out / "action_disposition_release.json").read_text())
    if (
        release["uncontrolled_remaining"] != 0
        or digest(out / "post_adjustment_scan_receipt.json") != release["base_scan_sha256"]
    ):
        raise ValueError("EVENT_DISPOSITIONS_NOT_COMPLETE")
    ledger = out / release["event_ledger"]
    if digest(ledger) != release["event_ledger_sha256"]:
        raise ValueError("EVENT_DISPOSITION_BYTES_CHANGED")
    manifest_path = out / "adjusted_hourly_manifest.json"
    hours = load_hours(manifest_path)
    masks, meta, context = origin_masks(hours)
    events = json.loads(ledger.read_text())
    hour_dep, origin_dep = dependencies(hours, masks, meta, events)
    private = Path(json.loads(manifest_path.read_text())["private_root"])
    refs = {
        "stock_origin_masks": publish_table(private / "origin_masks_v2.parquet", masks),
        "origin_clock": publish_table(private / "origin_clock.parquet", meta),
    }
    hour_dep.to_csv(out / "event_to_hour_dependency.csv", index=False)
    origin_dep.to_csv(out / "event_to_origin_dependency.csv", index=False)
    masks["year"] = masks.session_date_et.str[:4].astype(int)
    masks.groupby(["ticker", "year"])[[c for c in masks if masks[c].dtype == bool]].sum().to_csv(
        out / "stock_year_candidate_counts_v2.csv"
    )
    hourly_counts = (
        hours.assign(year=hours.session_date_et.str[:4].astype(int))
        .groupby(["ticker", "year"])
        .agg(
            rth_hours_and_stubs=("hour_id", "size"),
            expected_minutes=("expected_minutes", "sum"),
            genuine_minutes=("genuine_count", "sum"),
            missing_minutes=("missing_count", "sum"),
            conflict_minutes=("conflict_count", "sum"),
            proxy_minutes=("proxy_count", "sum"),
            quarantine_minutes=("quarantine_count", "sum"),
            genuine_closes=("genuine_close", "sum"),
            complete_volume_hours=("observed_volume_complete", "sum"),
        )
    )
    hourly_counts.to_csv(out / "stock_year_hour_quality.csv")
    windows = {
        "full_source": ("2010-07-01", "2026-03-31"),
        "research_proposal": ("2011-04-01", "2026-03-31"),
        "train_proposal": ("2011-04-01", "2025-06-30"),
        "development_proposal": ("2025-07-01", "2025-12-31"),
        "protected_source_quality_only": ("2026-01-01", "2026-03-31"),
    }
    counts = {name: summarize(masks, *bounds) for name, bounds in windows.items()}
    train = masks.loc[masks.session_date_et.between(*windows["train_proposal"])].copy()
    train["potential"] = train.origin_input_48_cap5 & train.origin_future_4h_eligible
    weak = train.groupby("ticker").potential.sum().sort_values(kind="stable").index[:2].tolist()
    counterfactual = []
    for exclude in [[symbol] for symbol in SYMBOLS] + [weak]:
        counterfactual.append(
            {
                "hypothetical_excluded": ",".join(exclude),
                "retained_names": len(SYMBOLS) - len(exclude),
                **summarize(train.loc[~train.ticker.isin(exclude)], *windows["train_proposal"]),
            }
        )
    pd.DataFrame(counterfactual).to_csv(out / "weak_stock_counterfactuals_v2.csv", index=False)
    years = {
        str(year): summarize(masks, f"{year}-01-01", f"{year}-12-31") for year in range(2010, 2027)
    }
    publish_json(out / "yearwide_candidate_counts_v2.json", years)
    publish_json(
        out / "candidate_origin_summary_v2.json",
        {
            "counts": counts,
            "weakest_two_training_coverage_only": weak,
            "structural": {k: v for k, v in context.items() if k != "grid"},
            "before_counts_are_unsafe_presence_only": True,
            "input_envelopes_are_not_final16_feature_admission": True,
            "features_targets_transforms_fitted": False,
            "files": refs,
            "unique_origins_with_event_dependency": int(origin_dep.origin_id.nunique()),
            "unique_price_input_boundary_origins": int(
                origin_dep.loc[origin_dep.price_input_excluded, "origin_id"].nunique()
            ),
            "unique_ohlc_channel_dependency_origins": int(
                origin_dep.loc[origin_dep.ohlc_context_untrusted, "origin_id"].nunique()
            ),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.out)


if __name__ == "__main__":
    main()
