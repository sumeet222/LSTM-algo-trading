"""Coverage-only common-history selection and conditional input/endpoint geometry."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .hf_hourly_audit import Census
from .stock_source import numeric


def coarse_sectors(path: Path) -> dict[str, str]:
    """Read the simple publisher symbol→ETF map; not a PIT sector certification."""
    result = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            key, sep, value = line.partition(":")
            if not sep or not value.strip().startswith("XL"):
                raise ValueError("SIMPLE_PUBLISHER_SECTOR_MAP_REQUIRED")
            result[key.strip()] = value.strip()
    return result


def geometry(c: Census) -> tuple[pd.DataFrame, np.ndarray]:
    """Presence/quality only: 48 historical hours and four same-session future hour endpoints."""
    missing = np.vstack(
        (np.zeros((1, len(c.symbols)), dtype=np.int64), np.cumsum(~c.usable, axis=0))
    )
    rows, admitted = [], []
    for day, g in c.full.groupby("session", sort=True):
        if len(g) != 6:
            continue  # No two original origins with four complete subsequent hours on half days.
        for origin in (1, 2):
            index = int(g.index[origin - 1])
            target = index + 4
            historical = (
                (missing[index + 1] - missing[index - 47] == 0)
                if index >= 47
                else np.zeros(len(c.symbols), dtype=bool)
            )
            endpoints = c.usable[index] & c.usable[target]
            future = missing[index + 5] - missing[index + 1] == 0
            rows.append(
                dict(
                    session=day,
                    origin=origin,
                    input_END_UTC=str(c.full.iloc[index].end),
                    endpoint_END_UTC=str(c.full.iloc[target].end),
                    endpoint_stocks=int(endpoints.sum()),
                    history48_stocks=int(historical.sum()),
                    history48_and4h_stocks=int((historical & future & endpoints).sum()),
                )
            )
            admitted.append(historical & future & endpoints)
    return pd.DataFrame(rows), np.asarray(admitted, dtype=bool)


def qualifying(c: Census, start: str, end: str, config: dict) -> np.ndarray:
    """No relaxed coverage thresholds; actual missing scheduled hours, invalids and duplicates."""
    selected = c.full.session.between(start, end).to_numpy()
    values = c.usable[selected]
    if not len(values):
        return np.zeros(len(c.symbols), dtype=bool)
    result = values.mean(axis=0) >= config["minimum_hour_coverage"]
    for j, symbol in enumerate(c.symbols):
        from .hf_hourly_audit import max_gap

        if max_gap(values[:, j]) > config["maximum_consecutive_missing_hours"]:
            result[j] = False
        daily = (
            pd.DataFrame(dict(day=c.full.loc[selected, "session"].to_numpy(), present=values[:, j]))
            .groupby("day")
            .present.sum()
        )
        if int(daily.eq(0).sum()) > config["maximum_missing_entire_sessions"]:
            result[j] = False
        invalid = c.frame.loc[
            c.frame.symbol.eq(symbol) & c.frame.session.between(start, end) & ~c.frame.valid
        ]
        if len(invalid):
            result[j] = False
        if symbol in config.get("identity_caution_exclusions", []):
            result[j] = False
    return result


def best_overlap(c: Census, config: dict) -> dict:
    """Enumerate month-boundary intervals, using prefix counts and exact missing-run guards."""
    months = sorted(c.monthly.month.unique())
    n = len(c.symbols)
    observed = c.monthly.set_index(["month", "symbol"])
    coverage = np.asarray(
        [[observed.loc[(m, s), "usable_full_hours"] for s in c.symbols] for m in months],
        dtype=float,
    )
    expected = np.asarray(
        [int(numeric(observed.loc[(m, c.symbols[0]), "expected_full_hours"])) for m in months]
    )
    missingdays = np.asarray(
        [[observed.loc[(m, s), "no_usable_aligned_sessions"] for s in c.symbols] for m in months],
        dtype=float,
    )
    invalid = np.asarray(
        [[observed.loc[(m, s), "invalid_rows"] for s in c.symbols] for m in months], dtype=float
    )
    pc = np.vstack((np.zeros((1, n)), coverage.cumsum(axis=0)))
    pe = np.r_[0, expected.cumsum()]
    pdays = np.vstack((np.zeros((1, n)), missingdays.cumsum(axis=0)))
    pinvalid = np.vstack((np.zeros((1, n)), invalid.cumsum(axis=0)))
    missing = (~c.usable).astype(np.int16)
    max_allowed = int(config["maximum_consecutive_missing_hours"])
    run = np.zeros_like(c.usable)
    run[max_allowed:] = True
    for k in range(max_allowed + 1):
        run[max_allowed:] &= missing[max_allowed - k : len(missing) - k].astype(bool)
    prun = np.vstack((np.zeros((1, n), dtype=np.int64), run.cumsum(axis=0)))
    bounds = [np.flatnonzero(c.full.session.str.startswith(m).to_numpy()) for m in months]
    best = None
    periods = []
    maximum = 0
    for a in range(len(months)):
        for b in range(a + 1, len(months) + 1):
            count = pe[b] - pe[a]
            if not count:
                continue
            good = (pc[b] - pc[a]) / count >= config["minimum_hour_coverage"]
            good &= (pdays[b] - pdays[a]) <= config["maximum_missing_entire_sessions"]
            good &= (pinvalid[b] - pinvalid[a]) == 0
            good &= np.asarray(
                [s not in config.get("identity_caution_exclusions", []) for s in c.symbols]
            )
            first, last = int(bounds[a][0]), int(bounds[b - 1][-1]) + 1
            good &= (prun[last] - prun[min(last, first + max_allowed)]) == 0
            total = int(good.sum())
            maximum = max(maximum, total)
            if total < int(config["minimum_cohort"]):
                continue
            start, end = str(c.full.iloc[first].session), str(c.full.iloc[last - 1].session)
            duration = (pd.Timestamp(end) - pd.Timestamp(start)).days
            candidate = dict(
                start=start,
                end=end,
                calendar_months=b - a,
                calendar_sessions=len(set(c.full.iloc[first:last].session)),
                expected_hours_per_stock=int(count),
                qualifying_symbols=[s for s, ok in zip(c.symbols, good) if ok],
            )
            if best is None or (duration, end) > (best[0], best[1]):
                best = (duration, end, candidate)
    # Also expose exact year scopes, even when no20-name history survives.
    for year in sorted(c.frame.year.unique()):
        start, end = year + "-01-01", min(year + "-12-31", str(c.frame.session.max()))
        good = qualifying(c, start, end, config)
        periods.append(
            dict(
                start=start,
                end=end,
                qualifying_count=int(good.sum()),
                symbols=[s for s, v in zip(c.symbols, good) if v],
            )
        )
    return dict(
        best=best[2] if best else None,
        maximum_qualifying_count=maximum,
        year_scopes=periods,
        search=(
            "All calendar-month boundary intervals; last endpoint may be latest "
            "partial month; no price-return criterion"
        ),
    )


def balanced_shortlist(
    c: Census, names: list[str], start: str, end: str, sectors: dict[str, str]
) -> list[str]:
    groups: dict[str, list[str]] = {}
    selected = c.full.session.between(start, end).to_numpy()
    for name in names:
        groups.setdefault(sectors.get(name, "UNVERIFIED"), []).append(name)
    for sector, values in groups.items():
        values.sort(key=lambda s: (int((~c.usable[selected, c.symbols.index(s)]).sum()), s))
    ordered = []
    while any(groups.values()):
        for sector in sorted(groups):
            if groups[sector]:
                ordered.append(groups[sector].pop(0))
    return ordered


def evaluate(c: Census, config: dict, sectors: dict[str, str], out: Path) -> dict:
    strict = qualifying(c, config["strict_start"], config["strict_end"], config)
    warmup = qualifying(c, config["strict_prehistory_start"], config["strict_end"], config)
    overlap = best_overlap(c, config)
    origin_table, origin_masks = geometry(c)
    origin_table.to_csv(out / "origin_geometry_by_session.csv", index=False)
    per_stock = []
    for j, symbol in enumerate(c.symbols):
        selected = origin_table.session.between(
            config["strict_start"], config["strict_end"]
        ).to_numpy()
        per_stock.append(
            dict(
                symbol=symbol,
                original_period_potential_origins=int(selected.sum()),
                original_48hour_plus4hour_complete_origins=int(origin_masks[selected, j].sum()),
                all_available_geometry_origins=int(origin_masks[:, j].sum()),
            )
        )
    pd.DataFrame(per_stock).to_csv(out / "per_symbol_origin_geometry.csv", index=False)
    proposal = None
    shortlist = []
    if overlap["best"]:
        best = overlap["best"]
        ordered = balanced_shortlist(
            c, best["qualifying_symbols"], best["start"], best["end"], sectors
        )
        shortlist = ordered[: config["minimum_cohort"]]
        expected = c.full.loc[c.full.session.between(best["start"], best["end"])]
        days = sorted(expected.session.unique())
        selected_columns = [c.symbols.index(s) for s in shortlist]
        warmup_days = 126
        required_regular = config.get("minimum_warmup_complete_regular_sessions")
        completed_regular = 0
        if required_regular is not None:
            for position, day in enumerate(days, 1):
                daily = c.full.loc[c.full.session.eq(day)]
                stubs = c.grid.loc[c.grid.session.eq(day) & c.grid.stub, "start"]
                present_stubs = c.frame.loc[
                    c.frame.symbol.isin(shortlist) & c.frame.valid & c.frame.UTC.isin(stubs),
                    "symbol",
                ].nunique()
                if (
                    len(daily) == 6
                    and c.usable[daily.index][:, selected_columns].all()
                    and present_stubs == len(shortlist)
                ):
                    completed_regular += 1
                if completed_regular >= required_regular:
                    warmup_days = position
                    break
            else:
                warmup_days = len(days)
        fitting = days[warmup_days:]
        first = int(len(fitting) * 0.6)
        second = int(len(fitting) * 0.8)
        if first and second > first and len(fitting) > second:
            splits = {
                "train": fitting[:first],
                "development": fitting[first:second],
                "held_out": fitting[second:],
            }
            common = origin_masks[:, selected_columns].all(axis=1)
            split_rows = []
            for label, part in splits.items():
                wanted = origin_table.session.isin(part).to_numpy()
                valid = wanted & common
                split_rows.append(
                    dict(
                        partition=label,
                        start=part[0],
                        end=part[-1],
                        calendar_sessions=len(part),
                        potential_origins=int(wanted.sum()),
                        complete_48historical_and4future_hours_origins=int(valid.sum()),
                        complete_origin_sessions=origin_table.loc[valid, "session"].nunique(),
                        target_values_created=0,
                        features_created=0,
                    )
                )
            subset = c.usable[expected.index][:, selected_columns]
            proposal = dict(
                primary=shortlist,
                backups=ordered[len(shortlist) :],
                start=best["start"],
                end=best["end"],
                warmup=dict(
                    start=days[0],
                    end=days[warmup_days - 1],
                    calendar_sessions=warmup_days,
                    complete_regular_sessions=completed_regular if required_regular else None,
                    caution=(
                        "126calendar sessions do not certify original FT0 daily/EMA warmups; "
                        "new methodology needs explicit regular/early-close policy"
                    ),
                ),
                splits=split_rows,
                expected_stock_hours=int(subset.size),
                usable_stock_hours=int(subset.sum()),
                common_complete_hour_positions=int(subset.all(axis=1).sum()),
                missing_stock_hours=int((~subset).sum()),
                coverage=float(subset.mean()),
                immutable_test_policy=(
                    "No model outcomes inspected; raw source quality audited "
                    "only. Freeze held_out dates before modeling; "
                    "no model-selection use."
                ),
                methodology_status="PROPOSAL_ONLY_NO_SOURCE_OR_INPUT_MIGRATION",
            )
            pd.DataFrame(split_rows).to_csv(out / "revised_chronology_geometry.csv", index=False)
    flags = [
        "RIGHTS_UNRESOLVED",
        "ADJUSTMENT_HOLD",
        "ORIGINAL_FT0_NOT_EXACTLY_REPRODUCIBLE_FROM_1H",
    ]
    if proposal:
        flags.append("REVISED_CHRONOLOGY_POSSIBLE")
    else:
        flags.append("INSUFFICIENT_COVERAGE")
    result = dict(
        flags=flags,
        strict_calendar_qualifying_count=int(strict.sum()),
        strict_with_required_prehistory_qualifying_count=int(warmup.sum()),
        strict_compatible=False,
        overlap=overlap,
        proposal=proposal,
        original_candidate_present={
            s: s in c.symbols for s in ("AAPL", "COST", "CMCSA", "SBUX", "CME")
        },
        coarse_sectors=sectors,
        sector_classification=(
            "Publisher static ETF proxy, not date-specific sector/PIT universe evidence"
        ),
        rights="UNRESOLVED_LOCAL_EXPLORATORY_ONLY",
        neural_pairs_before=28,
        neural_pairs_after=28,
        original_confirmation_numeric_reads=0,
        new_vendor_quality_audit_all_splits=True,
        confirmation_labels_created=0,
        model_training=False,
    )
    write_json(out / "feasibility_decision.json", result)
    return result
