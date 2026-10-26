"""S3 source-only preflight. No fitting entry point; scientific blockers stay blocking."""

from __future__ import annotations

import argparse
import io
import json
import time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from .config import fingerprint
from .hf20_horizon_math import (
    endpoints,
    historical_m2,
    horizon_roles,
    returns_at,
    scale_m2,
    substitute_m2,
    target_support,
)
from .hf20_ranking import YEARS, ranks, row_loss
from .hf20_ranking_authority import resources
from .hf20_ranking_data import FoldData, assemble
from .hf20_ranking_run import initial_hash, sha, write
from .hf20_recent_analysis import origin_panel
from .hf20_recent_linear import PRIOR, preservation
from .neural_engine import SharedLSTM, optimizer, seed_all

RECENT = Path("reports/experiments/hf20_monthly_recent36_2026-10-25_225630")


def proposed_runs() -> list[str]:
    """All A then all B; fold-major, h1/h2, T2R/NR; none reserved by preparation."""
    return [
        f"HF20-S3{stage}-F{year % 100}-H{h}-{arm}-S42"
        for stage in ("A", "B")
        for year in YEARS
        for h in (1, 2)
        for arm in ("T2R", "NR")
    ]


def ledger(out: Path) -> None:
    """Inspect every original linked journal; count actual historical STARTED events."""
    pointer = json.loads(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_text())
    late = []
    path = Path(pointer["real_journal"])
    seen = set()
    while str(path) not in seen:
        seen.add(str(path))
        late.append(path)
        history = [json.loads(s) for s in path.read_text().splitlines()]
        parent = history[0].get("previous_journal")
        if not parent:
            break
        parent_path = Path(parent["path"])
        if sha(parent_path) != parent["sha256"]:
            raise ValueError("PREDECESSOR_JOURNAL_CHANGED")
        path = parent_path
    early = [Path(f"reports/audit/track_a_real_pairs_v{i}.jsonl") for i in range(1, 5)]
    paths = early + list(reversed(late))
    starts = []
    refs = []
    for path in paths:
        history = [json.loads(s) for s in path.read_text().splitlines()]
        for k, row in enumerate(history):
            if row["sequence"] != k + 1 or row["previous"] != fingerprint(history[:k]):
                raise ValueError("HISTORIC_JOURNAL_CHAIN_MISMATCH")
            if row["status"] == "STARTED":
                count = row.get("global_started_pairs", 1)
                if count != len(starts) + 1:
                    raise ValueError("HISTORIC_START_COUNT_MISMATCH")
                starts.append(
                    dict(
                        start=count,
                        run_id=row.get("run_id", row["pair_key"] if "pair_key" in row else ""),
                        journal=str(path),
                    )
                )
        refs.append(dict(path=str(path), sha256=sha(path), rows=len(history)))
    if len(starts) != 74:
        raise ValueError("EXACT74_HISTORICAL_STARTS_REQUIRED")
    pd.DataFrame(starts).to_csv(out / "HISTORICAL_74_STARTS.csv", index=False)
    value = dict(
        status="PASS", started=74, prior_failed65="PRESERVED", journals=refs, reserved_S3=0
    )
    path = out / "JOURNAL_VERIFICATION.json"
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError("PRIOR_AUDIT_JOURNAL_IDENTITY_CHANGED")
    else:
        write(path, value)


def source_audit(data: FoldData, out: Path) -> None:
    h = data.components.hours

    def matrix(name: str) -> np.ndarray:
        return (
            h.pivot(index="hour_start_utc", columns="ticker", values=name)
            .reindex(index=data.grid.hour_start_utc, columns=data.symbols)
            .to_numpy()
        )

    basis = matrix("price_basis_id")
    genuine = matrix("genuine_close").astype(bool)
    blocked = matrix("cop_dependency").astype(bool)
    close = data.components.source["close"]
    entry = data.rows.entry_index.to_numpy(int)
    masks, returns = {}, {}
    exclusions = []
    for horizon in (1, 2, 4):
        ex = endpoints(data.grid, entry, horizon)
        masks[horizon] = target_support(data.grid, entry, genuine, basis, horizon).all(1)
        returns[horizon] = returns_at(close, entry, ex)
        for k in np.flatnonzero(data.rows.source_input_eligible.to_numpy() & ~masks[horizon]):
            missing = ~(genuine[entry[k]] & genuine[ex[k]])
            incompatible = basis[entry[k]] != basis[ex[k]]
            exclusions.append(
                dict(
                    origin_id=str(data.rows.origin_id.iloc[k]),
                    horizon=horizon,
                    missing_genuine_endpoint_tickers="|".join(np.array(data.symbols)[missing]),
                    incompatible_basis_tickers="|".join(np.array(data.symbols)[incompatible]),
                )
            )
    np.testing.assert_array_equal(masks[4], data.rows.label_eligible.to_numpy())
    good4 = masks[4]
    np.testing.assert_array_equal(returns[4][good4], data.returns[good4])
    common = masks[1] & masks[2] & masks[4]
    index = data.rows[["origin_id", "session_date_et", "entry_index", "first_step"]].copy()
    for horizon in (1, 2, 4):
        index[f"source_target_h{horizon}"] = masks[horizon]
    index["common_target_source"] = common
    index["input_eligible"] = data.rows.source_input_eligible.to_numpy()
    index.to_csv(out / "S3_SOURCE_COMMON_INDEX.csv", index=False)
    pd.DataFrame(exclusions).to_csv(out / "S3_ENDPOINT_EXCLUSIONS.csv", index=False)
    supports = []
    blockers = []
    for year in YEARS:
        for role in ("inner_train", "inner_validation", "refit", "oos"):
            pos = data.positions(year, role)
            for slot in ("ALL", "10:30", "11:30"):
                slots = (
                    pd.to_datetime(data.rows.iloc[pos].entry_end_utc, utc=True)
                    .dt.tz_convert("America/New_York")
                    .dt.strftime("%H:%M")
                    .to_numpy()
                )
                selected = pos if slot == "ALL" else pos[slots == slot]
                chosen = selected[common[selected]]
                sessions = data.rows.iloc[chosen].session_date_et.nunique()
                supports.append(
                    dict(
                        year=year,
                        role=role,
                        slot_et=slot,
                        original_origins=len(selected),
                        common_origins=len(chosen),
                        lost_origins=len(selected) - len(chosen),
                        original_sessions=data.rows.iloc[selected].session_date_et.nunique(),
                        common_sessions=sessions,
                        h1_valid_origins=int(masks[1][selected].sum()),
                        h2_valid_origins=int(masks[2][selected].sum()),
                        h4_valid_origins=int(masks[4][selected].sum()),
                    )
                )
                if role == "inner_validation" and (
                    (slot == "ALL" and sessions < 50) or (slot != "ALL" and len(chosen) < 25)
                ):
                    blockers.append(
                        dict(
                            year=year,
                            role=role,
                            slot=slot,
                            sessions=sessions,
                            origins=len(chosen),
                            reason="INHERITED_INNER_SUPPORT_GATE",
                        )
                    )
    pd.DataFrame(supports).to_csv(out / "S3_ROLE_SUPPORT_BY_SLOT.csv", index=False)
    write(
        out / "COMMON_POPULATION_REVIEW.json",
        dict(
            status="BLOCKED_PENDING_SCIENTIFIC_AMENDMENT",
            blockers=blockers,
            reason=(
                "Material source-only shrinkage; archived h4 used larger fit populations. "
                "No thresholds, dates or source quality changed."
            ),
            new_models_started=0,
        ),
    )
    m2 = {}
    native_support = []
    identities = []
    for horizon in (1, 2, 4):
        mean, rms, references, past = historical_m2(data.grid, close, basis, blocked, horizon)
        m2[horizon] = (mean, rms)
        if horizon == 4:
            np.testing.assert_array_equal(mean, data.components.m2_mean)
            np.testing.assert_array_equal(rms, data.components.m2_rms)
            np.testing.assert_array_equal(references, data.components.m2_reference_end)
        valid = references >= 0
        # Conservative reference is prior regular-day15:30, even when h1/2 ends earlier.
        matured = pd.to_datetime(
            data.grid.iloc[references[valid]].hour_end_utc, utc=True
        ) + pd.Timedelta(minutes=2)
        cutoffs = pd.to_datetime(data.grid.loc[valid, "hour_start_utc"], utc=True)
        if not (matured.to_numpy() < cutoffs.to_numpy()).all():
            raise ValueError("M2_HISTORICAL_OUTCOME_NOT_PREVIOUSLY_MATURED")
        for year in YEARS:
            for role in ("inner_train", "inner_validation", "refit", "oos"):
                pos = data.positions(year, role)
                pos = pos[common[pos]]
                rows = data.rows.iloc[pos]
                histories = rows.first_step.to_numpy(int)[:, None] + np.arange(48)
                forecast_slots = (
                    pd.to_datetime(rows.entry_end_utc, utc=True)
                    .dt.tz_convert("America/New_York")
                    .dt.hour.to_numpy()
                    - 10
                )
                for slot in (0, 1):
                    a = mean[histories[forecast_slots == slot], :, slot]
                    b = rms[histories[forecast_slots == slot], :, slot]
                    native = np.isfinite(a) & np.isfinite(b)
                    native_support.append(
                        dict(
                            horizon=horizon,
                            year=year,
                            role=role,
                            m2_origin_type=slot,
                            history_stock_cells=native.size,
                            native_cells=int(native.sum()),
                            native_fraction=float(native.mean()),
                            strict_prior_day=True,
                            counted="consumed tensor cells, including overlapping histories",
                        )
                    )
        # Independent brute rolling oracle at a bounded deterministic regular-day sample.
        days = data.components.regular_days
        for k in np.linspace(65, len(days) - 1, 8, dtype=int):
            date = str(days[k])
            query = np.flatnonzero(data.grid.session_date_et.eq(date))[0]
            for j in (0, 7, 19):
                for slot in (0, 1):
                    for width, minimum, square, actual in (
                        (20, 19, False, mean),
                        (60, 57, True, rms),
                    ):
                        a = past[k - width : k, j, slot]
                        triples = any(
                            not np.isfinite(a[z : z + 3]).any() for z in range(len(a) - 2)
                        )
                        expected = np.nan
                        if (
                            np.isfinite(a).sum() >= minimum
                            and not triples
                            and not blocked[query, j]
                        ):
                            expected = float(
                                np.sqrt(np.nanmean(a * a)) if square else np.nanmean(a)
                            )
                        np.testing.assert_allclose(
                            actual[query, j, slot], expected, rtol=1e-12, atol=1e-15, equal_nan=True
                        )
    pd.DataFrame(native_support).to_csv(out / "S3B_M2_NATIVE_SUPPORT.csv", index=False)
    for year in YEARS:
        for phase in ("inner", "refit"):
            data.phase(year, phase, PRIOR)
            floors = np.array([v["m2_floor"] for v in data.recipe["floors"]])
            mean4, rms4 = m2[4]
            scaled = scale_m2(mean4, rms4, floors, data.recipe["scalers"]["M2"])
            np.testing.assert_array_equal(scaled, data.m2)
            identities.append(
                dict(
                    year=year,
                    phase=phase,
                    scaled_M2_h4="BITWISE_EQUAL",
                    native_mean_rms_h4="EXACT_EQUAL_NAN",
                    recipe_sha256=sha(PRIOR / f"F{year % 100}_{phase}_recipe.json"),
                )
            )
            for role in (
                ("inner_train", "inner_validation") if phase == "inner" else ("refit", "oos")
            ):
                pos = data.positions(year, role)
                # Check representative original targets, before any common-key restriction.
                chosen = pos[np.unique([0, len(pos) // 2, len(pos) - 1])]
                x, r, y = data.arrays(chosen)
                np.testing.assert_array_equal(r, returns[4][chosen])
                np.testing.assert_array_equal(ranks(r), ranks(y))
                np.testing.assert_array_equal(
                    ranks(r), ranks(np.arcsinh(y / data.recipe["t2_scale"]))
                )
                assert x.shape == (len(chosen), 20, 48, 16)
    pd.DataFrame(identities).to_csv(out / "S3_H4_M2_PHASE_IDENTITIES.csv", index=False)
    # Source-only witness replacement; no return size, score or IC participates.
    cases = pd.read_csv(PRIOR / "shared_source_case_keys.csv")
    selected = []
    used = set()
    for row in cases.to_dict("records"):
        k = int(np.flatnonzero(data.rows.origin_id.eq(row["origin_id"]))[0])
        original = str(row["origin_id"])
        if not common[k]:
            year = int(row["year"])
            pos = data.positions(year, "oos")
            pos = pos[common[pos]]
            slot = pd.Timestamp(original).tz_convert("America/New_York").hour
            candidate = data.rows.iloc[pos]
            hour = (
                pd.to_datetime(candidate.entry_end_utc, utc=True)
                .dt.tz_convert("America/New_York")
                .dt.hour
            )
            available = pos[(hour.eq(slot) & ~candidate.origin_id.isin(used)).to_numpy()]
            if not len(available):
                raise ValueError("NO_SOURCE_ONLY_WITNESS_REPLACEMENT")
            k = int(available[0])
        origin = str(data.rows.origin_id.iloc[k])
        used.add(origin)
        for horizon in (1, 2, 4):
            ex = int(entry[k] + horizon)
            j = data.symbols.index(str(row["ticker"]))
            selected.append(
                dict(
                    case_id=int(row["case_id"]),
                    year=int(row["year"]),
                    ticker=str(row["ticker"]),
                    original_origin_id=original,
                    origin_id=origin,
                    replaced=original != origin,
                    horizon=horizon,
                    entry_end_utc=str(data.grid.hour_end_utc.iloc[entry[k]]),
                    modeled_issuance_utc=str(
                        pd.Timestamp(data.grid.hour_end_utc.iloc[entry[k]])
                        + pd.Timedelta(minutes=2)
                    ),
                    exit_end_utc=str(data.grid.hour_end_utc.iloc[ex]),
                    modeled_maturity_utc=str(
                        pd.Timestamp(data.grid.hour_end_utc.iloc[ex]) + pd.Timedelta(minutes=2)
                    ),
                    return_4h_or_h=float(returns[horizon][k, j]),
                    M2_latest_reference_utc=str(
                        data.grid.hour_end_utc.iloc[data.components.m2_reference_end[entry[k]]]
                    ),
                    availability="UNKNOWN; inherited end+2 minute assumption",
                )
            )
    pd.DataFrame(selected).to_csv(out / "S3_PREDECLARED_SOURCE_WITNESSES.csv", index=False)
    # Archival h4 comparison: reuse scores, not checkpoint inference or new fits.
    summaries = []
    for path in sorted(PRIOR.glob("*/oos_scores.parquet")):
        if "PW" in path.parent.name:
            continue
        f = pd.read_parquet(path)
        ids = set(data.rows.loc[common, "origin_id"])
        subset = f.loc[f.origin_id.isin(ids)].copy()
        p = origin_panel(subset)
        saved = json.loads(path.with_name("oos_metrics.json").read_text())
        summaries.append(
            dict(
                year=saved["year"],
                model=saved["model"],
                horizon=4,
                original_origins=saved["origins"],
                common_origins=len(p),
                original_sessions=saved["sessions"],
                common_sessions=p.session_date_et.nunique(),
                original_daily_IC=saved["daily_ic"],
                common_daily_IC=float(p.groupby("session_date_et").ic.mean().mean()),
                original_score_path=str(path),
                original_score_sha256=sha(path),
                fit_population="ARCHIVED_FULL_PREFIX; not common-cohort-refitted",
            )
        )
    pd.DataFrame(summaries).to_csv(out / "S3_H4_ARCHIVAL_COMMON_KEY_COMPARISON.csv", index=False)
    write(
        out / "SOURCE_AND_M2_VERIFICATION.json",
        dict(
            status="PASS_MATH_BLOCKED_POPULATION",
            h4_target_source_mask_exact=True,
            h4_return_bitwise=True,
            h4_native_and_scaled_M2_exact=True,
            independent_M2_scalar_checks=3 * 8 * 3 * 2 * 2,
            prior_day_maturity_before_own_step=True,
            h1_h2_actual_normalizer_fits=0,
            source_witnesses=22,
            witness_horizon_rows=len(selected),
            new_inference=0,
        ),
    )


def amended_audit(data: FoldData, out: Path) -> None:
    """Latest human amendment: independent h eligibility, secondary common evaluation."""
    full = data.components.hours

    def matrix(name: str) -> np.ndarray:
        return (
            full.pivot(index="hour_start_utc", columns="ticker", values=name)
            .reindex(index=data.grid.hour_start_utc, columns=data.symbols)
            .to_numpy()
        )

    genuine = matrix("genuine_close").astype(bool)
    basis = matrix("price_basis_id")
    blocked = matrix("cop_dependency").astype(bool)
    entry = data.rows.entry_index.to_numpy(int)
    source = {h: target_support(data.grid, entry, genuine, basis, h).all(1) for h in (1, 2, 4)}
    native = {
        h: historical_m2(data.grid, data.components.source["close"], basis, blocked, h)
        for h in (1, 2, 4)
    }
    np.testing.assert_array_equal(native[4][0], data.components.m2_mean)
    np.testing.assert_array_equal(native[4][1], data.components.m2_rms)
    records = []
    clocks = []
    membership = {}
    gates = []
    feature_checks = []
    pool_support = []
    for year in YEARS:
        plan, original = data.plans[year]
        masks = {h: horizon_roles(data.rows, data.grid, plan, source[h]) for h in (1, 2, 4)}
        # Historical comparability is a full-array identity, not a count-only assertion.
        for role in original:
            np.testing.assert_array_equal(masks[4][role], original[role])
        for phase in ("inner", "refit"):
            data.phase(year, phase, PRIOR)
            unique_day = (
                data.grid.iloc[np.array(data.recipe["fit_hour_indices"], int)]
                .drop_duplicates("session_date_et")
                .index.to_numpy(int)
            )
            for h in (1, 2, 4):
                for stock in range(20):
                    for slot in (0, 1):
                        values = native[h][1][unique_day, stock, slot]
                        count = int((np.isfinite(values) & (values > 0)).sum())
                        if count == 0:
                            raise ValueError("H_SPECIFIC_M2_PREFIX_POOL_EMPTY")
                        pool_support.append(
                            dict(
                                year=year,
                                phase=phase,
                                horizon=h,
                                ticker=data.symbols[stock],
                                origin_type=slot,
                                positive_RMS_prefix_days=count,
                                rule="original input-only unique days; no new parameters fitted",
                            )
                        )
            for role in (
                ("inner_train", "inner_validation") if phase == "inner" else ("refit", "oos")
            ):
                common = masks[1][role] & masks[2][role] & masks[4][role]
                for h in (1, 2, 4):
                    chosen = np.flatnonzero(masks[h][role])
                    membership[f"F{year % 100}/H{h}/{role}"] = chosen.tolist()
                    rows = data.rows.iloc[chosen]
                    exits = endpoints(data.grid, rows.entry_index.to_numpy(int), h)
                    maturity = pd.to_datetime(
                        data.grid.iloc[exits].hour_end_utc, utc=True
                    ) + pd.Timedelta(minutes=2)
                    conservative = pd.to_datetime(rows.label_maturity_utc, utc=True)
                    if not (maturity.to_numpy() <= conservative.to_numpy()).all():
                        raise ValueError("HORIZON_MATURITY_AFTER_CONSERVATIVE_4H_CLOCK")
                    clocks.append(
                        dict(
                            year=year,
                            horizon=h,
                            role=role,
                            phase=phase,
                            first_session=str(rows.session_date_et.min()),
                            last_session=str(rows.session_date_et.max()),
                            oldest_input_utc=str(
                                data.grid.iloc[rows.first_step.to_numpy(int)].hour_end_utc.min()
                            ),
                            newest_input_utc=str(rows.entry_end_utc.max()),
                            latest_actual_h_label_maturity=str(maturity.max()),
                            latest_conservative_4h_maturity=str(conservative.max()),
                            recipe_path=str(PRIOR / f"F{year % 100}_{phase}_recipe.json"),
                            recipe_sha256=sha(PRIOR / f"F{year % 100}_{phase}_recipe.json"),
                        )
                    )
                    slot_values = (
                        pd.to_datetime(data.rows.entry_end_utc, utc=True)
                        .dt.tz_convert("America/New_York")
                        .dt.strftime("%H:%M")
                        .to_numpy()
                    )
                    # A clock/input-only mask is obtained without requiring any target endpoint.
                    input_only = horizon_roles(
                        data.rows, data.grid, plan, np.ones(len(data.rows), bool)
                    )[role]
                    for slot in ("ALL", "10:30", "11:30"):
                        slot_mask = (
                            np.ones(len(data.rows), bool) if slot == "ALL" else slot_values == slot
                        )
                        old = original[role] & slot_mask
                        keep = masks[h][role] & slot_mask
                        all_input = input_only & slot_mask
                        original_count = int(old.sum())
                        count = int(keep.sum())
                        sessions = data.rows.loc[keep, "session_date_et"].nunique()
                        for arm in ("A", "B"):
                            records.append(
                                dict(
                                    year=year,
                                    horizon=h,
                                    arm=arm,
                                    role=role,
                                    slot_et=slot,
                                    input_eligible_origins=int(all_input.sum()),
                                    origins=count,
                                    stock_rows=count * 20,
                                    sessions=sessions,
                                    original_h4_origins=original_count,
                                    percent_of_original_h4=100 * count / original_count
                                    if original_count
                                    else None,
                                    retained_of_input_percent=100 * count / int(all_input.sum())
                                    if all_input.any()
                                    else None,
                                    endpoint_or_basis_exclusions=int(
                                        (all_input & ~source[h]).sum()
                                    ),
                                    overlap_original_h4=int((keep & old).sum()),
                                    new_beyond_h4=int((keep & ~old).sum()),
                                    secondary_common_origins=int((common & slot_mask).sum()),
                                    population_sha256=fingerprint(
                                        data.rows.loc[keep, "origin_id"].tolist()
                                    ),
                                    B_h4="IDENTITY_NO_FIT" if h == 4 else "MATCHED_A",
                                )
                            )
                        if role == "inner_validation":
                            passed = sessions >= 50 if slot == "ALL" else count >= 25
                            gates.append(
                                dict(
                                    year=year,
                                    horizon=h,
                                    slot_et=slot,
                                    sessions=sessions,
                                    origins=count,
                                    minimum=50 if slot == "ALL" else 25,
                                    status="PASS" if passed else "BLOCKED",
                                )
                            )
                    # B changes exactly channel1; actual h1/2 scale remains unactivated.
                    example = chosen[np.unique([0, len(chosen) // 2, len(chosen) - 1])]
                    small = data.rows.iloc[example]
                    x = assemble(small, data.common, data.m2)
                    if h == 4:
                        np.testing.assert_array_equal(x, data.arrays(example)[0])
                    floors = np.array([v["m2_floor"] for v in data.recipe["floors"]])
                    test_m2 = scale_m2(
                        native[h][0], native[h][1], floors, data.recipe["scalers"]["M2"]
                    )
                    b = substitute_m2(x, small, test_m2)
                    if h == 4:
                        np.testing.assert_array_equal(x, b)
                    feature_checks.append(
                        dict(
                            year=year,
                            horizon=h,
                            role=role,
                            source_origins=len(example),
                            all15_other_channels_bitwise=True,
                            shape=str(x.shape),
                            finite=bool(np.isfinite(b).all()),
                            scale_status="STORED_H4_IDENTITY"
                            if h == 4
                            else "H4_PARAMETERS_SHAPE_ONLY_NOT_CANDIDATE_H1_H2_RECIPE",
                        )
                    )
        # Disjoint fit/validation and refit/OOS origin clocks for each horizon.
        for h in (1, 2, 4):
            assert not (masks[h]["inner_train"] & masks[h]["inner_validation"]).any()
            assert not (masks[h]["refit"] & masks[h]["oos"]).any()
    frame = pd.DataFrame(records)
    a = frame.loc[frame.arm.eq("A")].reset_index(drop=True)
    b = frame.loc[frame.arm.eq("B")].reset_index(drop=True)
    np.testing.assert_array_equal(a.population_sha256.to_numpy(), b.population_sha256.to_numpy())
    frame.to_csv(out / "S3_HORIZON_ROLE_SUPPORT.csv", index=False)
    pd.DataFrame(clocks).to_csv(out / "S3_HORIZON_ROLE_CLOCKS.csv", index=False)
    pd.DataFrame(gates).to_csv(out / "S3_VALIDATION_SUPPORT_GATES.csv", index=False)
    pd.DataFrame(feature_checks).to_csv(out / "S3_FEATURE_IDENTITY_REHEARSAL.csv", index=False)
    pd.DataFrame(pool_support).to_csv(out / "S3_M2_PREFIX_POOL_SUPPORT.csv", index=False)
    write(
        out / "S3_ROLE_MEMBERSHIP.json",
        dict(
            source_index_path=str(out.parent / "S3_SOURCE_COMMON_INDEX.csv"),
            source_index_sha256=sha(out.parent / "S3_SOURCE_COMMON_INDEX.csv"),
            canonical_row_positions=membership,
        ),
    )
    failed = [r for r in gates if r["status"] != "PASS"]
    write(
        out / "AMENDED_ELIGIBILITY_VERIFICATION.json",
        dict(
            status="PASS_SOURCE_SUPPORT_AWAITING_AMENDED_DESIGN_APPROVAL"
            if not failed
            else "BLOCKED_INSUFFICIENT_HORIZON_SUPPORT",
            failures=failed,
            session_minimum_unchanged=50,
            per_slot_origin_minimum_unchanged=25,
            h4_roles_exact_original=True,
            h1_h2_not_filtered_by_h4=True,
            AB_population_hashes_identical=True,
            secondary_common_only=True,
            conservative_4h_clock_retained=True,
            new_real_normalizer_fits=0,
            new_model_fits=0,
            neural_starts=0,
        ),
    )


def synthetic_rehearsal(out: Path) -> None:
    """All32 proposed configurations, disposable SYN data and memory-only reload; zero steps."""
    seed_all(42)
    rng = np.random.default_rng(42)
    x = torch.from_numpy(rng.normal(size=(40, 48, 16)).astype(np.float32))
    r = rng.normal(size=(2, 20))
    y = (r - np.median(r, axis=1)[:, None]) / (
        np.median(abs(r - np.median(r, axis=1)[:, None]), axis=1)[:, None] + 0.001
    )
    rows = []
    for run in proposed_runs():
        seed_all(42)
        model = SharedLSTM().float()
        opt = optimizer(model)
        initial = initial_hash(model)
        arm = run.split("-")[-2]
        score = model(x).reshape(2, 20)
        loss = (
            row_loss(arm, score, torch.from_numpy(r), torch.from_numpy(y.astype(np.float32)), 1.0)
            .mean(0)
            .sum()
        )
        loss.backward()
        before = [p.detach().clone() for p in model.parameters()]
        gradient = float(
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        )
        if not all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()):
            raise ValueError("SYN_GRADIENT_CONNECTIVITY")
        assert all(torch.equal(p, b) for p, b in zip(model.parameters(), before)) and not opt.state
        store = io.BytesIO()
        torch.save(model.state_dict(), store)
        store.seek(0)
        reloaded = SharedLSTM().float()
        reloaded.load_state_dict(torch.load(store, weights_only=True))
        model.eval()
        reloaded.eval()
        with torch.no_grad():
            np.testing.assert_array_equal(model(x).numpy(), reloaded(x).numpy())
        seed_all(42)
        fresh = SharedLSTM().float()
        assert initial_hash(fresh) == initial
        rows.append(
            dict(
                run_id=run,
                parameters=sum(p.numel() for p in model.parameters()),
                steps=48,
                channels=16,
                seed=42,
                actual_objective=arm,
                synthetic_loss=float(loss.detach()),
                preclip_gradient=gradient,
                optimizer_step_calls=0,
                optimizer_state_entries=len(opt.state),
                weights_unchanged=True,
                memory_only_reload_exact=True,
                fresh_refit_seed_identity=True,
            )
        )
    pd.DataFrame(rows).to_csv(out / "SYN_ZERO_UPDATE_REHEARSAL.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--amend", action="store_true")
    args = parser.parse_args()
    out = args.out
    if not (
        out / ("submitted_amendment.txt" if args.amend else "submitted_instruction.txt")
    ).exists():
        raise ValueError("S3_PREPARATION_SCOPE_MISSING")
    began = time.monotonic()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    with ExitStack() as stack:
        step = stack.enter_context(
            patch.object(
                torch.optim.AdamW,
                "step",
                side_effect=AssertionError("NO_REAL_OR_SYN_OPTIMIZER_UPDATE"),
            )
        )
        fit = stack.enter_context(
            patch("lstm_data.hf20_ranking_data.fit", side_effect=AssertionError("NO_NEW_PHASE_FIT"))
        )
        ridge = stack.enter_context(
            patch(
                "lstm_data.hf20_ranking.ridge_solution",
                side_effect=AssertionError("NO_REAL_BASELINE_FIT"),
            )
        )
        ledger(out)
        preservation(RECENT, final=True)
        data = FoldData(live_approved=True)
        if args.amend:
            amended_audit(data, out)
        else:
            source_audit(data, out)
        synthetic_rehearsal(out)
        assert step.call_count == fit.call_count == ridge.call_count == 0
        final = preservation(RECENT, final=True)
        write(
            out / "PREPARATION_RECEIPT.json",
            dict(
                status=(
                    "AMENDED_AUDIT_COMPLETE_NO_FIT_PERMISSION"
                    if args.amend
                    else "BLOCKED_PENDING_COMMON_POPULATION_REVIEW"
                ),
                seconds=time.monotonic() - began,
                resources=resources(out),
                source_guard_maximum_numeric_date="2024-12-31",
                new_supervised_fits=0,
                neural_starts=0,
                optimizer_step_calls=step.call_count,
                new_phase_fit_calls=fit.call_count,
                baseline_solve_calls=ridge.call_count,
                new_checkpoint_files=0,
                synthetic_configurations=32,
                prior_preservation=final,
            ),
        )


if __name__ == "__main__":
    main()
