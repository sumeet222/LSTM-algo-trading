"""Pinned Stage3 input-only minute certification; no targets, models or inference."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("reports/experiments/hf20_s9_mag_stage3_session2_minute_BC_2026-10-28")
S4 = Path("reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation")
SOURCE = S4 / "opening_reaudit_v2"
O1 = Path("reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28")
SYMBOLS = tuple(
    "VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO".split()
)
REVISION = "776328445b7ac6e7815ef3a483e9c8ded1eb6d56"


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def write(path: Path, value: dict) -> None:
    if path.exists():
        if read(path) != value:
            raise ValueError("IMMUTABLE_METADATA_CHANGED", str(path))
        return
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def metadata() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    contract = read(
        Path(
            "reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/model_input_contract.json"
        )
    )
    grid = pd.read_parquet(
        contract["files"]["grid"]["path"],
        columns=["hour_start_utc", "hour_end_utc", "session_date_et"],
        filters=[("session_date_et", "<=", "2024-12-31")],
    )
    rows = pd.read_parquet(SOURCE / "S4_ORIGIN_SOURCE_ELIGIBILITY.parquet")
    assert rows.session_date_et.lt("2025").all()
    assert grid.session_date_et.lt("2025").all()
    assert (grid.hour_end_utc - grid.hour_start_utc).eq(pd.Timedelta(hours=1)).all()
    assert tuple(read(S4 / "S4_FROZEN_EXPERIMENT_CARD.json")["symbols"]) == SYMBOLS
    roles = np.load(O1 / "role_indices.npz")
    return grid, rows, {k: roles[k] for k in roles.files}


def fitting_hours(grid: pd.DataFrame, rows: pd.DataFrame, stop: str) -> np.ndarray:
    """Exact input-only prefix union used by executed Design A, no label selection."""
    mask = np.zeros(len(grid), bool)
    for a, b in rows.loc[
        rows.source_input_eligible & rows.session_date_et.between("2011-04-01", stop),
        ["first_step", "entry_index"],
    ].to_numpy(int):
        mask[a : b + 1] = True
    return mask & grid.session_date_et.between("2011-04-01", stop).to_numpy()


def c_regime_gate(
    grid: pd.DataFrame, rows: pd.DataFrame, roles: dict[str, np.ndarray]
) -> list[dict]:
    """An unseen share regime cannot have a frozen same-regime prefix median."""
    facts = read(Path("configs/hf1m_p019_verified_event_facts_v1.json"))["events"]
    splits = [e for e in facts if e["kind"] == "SPLIT" and e["date"] < "2025"]
    slots = grid.hour_start_utc.dt.tz_convert("America/New_York").dt.strftime("%H:%M").to_numpy()
    dates = grid.session_date_et.to_numpy()
    failures = []
    for year in range(2021, 2025):
        phases = read(O1 / f"F{year % 100}/phases.json")["phases"]
        for phase, later in [("initial", "selector"), ("restricted", "oos")]:
            stop = phases[phase]["cutoff"]
            fit = fitting_hours(grid, rows, stop)
            requested = rows.iloc[roles[f"F{year % 100}_{later}"]].entry_index.to_numpy(int)
            for symbol in SYMBOLS:
                regime = np.zeros(len(grid), int)
                for action in splits:
                    if action["ticker"] == symbol:
                        regime += dates >= action["date"]
                available = set(zip(slots[fit], regime[fit]))
                for slot, unit in sorted(set(zip(slots[requested], regime[requested])) - available):
                    bad = requested[(slots[requested] == slot) & (regime[requested] == unit)]
                    failures.append(
                        dict(
                            year=year,
                            phase=phase,
                            role=later,
                            ticker=symbol,
                            slot=slot,
                            share_regime=int(unit),
                            prefix_stop=stop,
                            first_required_input_date=str(dates[bad].min()),
                            affected_origins=len(bad),
                            reason=(
                                "NO_SAME_REGIME_PREFIX_VOLUME_MEDIAN; "
                                "no approved cross-regime fallback"
                            ),
                        )
                    )
    return failures


def path_features(prices: np.ndarray, volume: np.ndarray, observed: np.ndarray) -> np.ndarray:
    """Raw RV plus four bounded summaries and P,V; no fitted floor or scaler."""
    if (
        prices.shape != (*observed.shape, 4)
        or volume.shape != observed.shape
        or observed.shape[-1] != 60
    ):
        raise ValueError("MINUTE_TEMPLATE_SHAPE")
    complete = observed.all(-1)
    valid_volume = complete & np.isfinite(volume).all(-1) & (volume >= 0).all(-1)
    result = np.zeros((*complete.shape, 7), float)
    result[..., 4] = 0.25
    result[..., 5] = complete
    result[..., 6] = valid_volume
    c = prices[..., 3][complete]
    if len(c):
        r = np.log(c[:, 1:] / c[:, :-1])
        square = r**2
        rv = square.sum(1)
        result[..., 0][complete] = rv
        result[..., 1][complete] = np.divide(
            (square * np.sign(r)).sum(1), rv, out=np.zeros(len(c)), where=rv > 0
        )
        early, late = square[:, :29].sum(1), square[:, 30:].sum(1)
        result[..., 2][complete] = np.divide(
            late - early, late + early, out=np.zeros(len(c)), where=late + early > 0
        )
        total = np.abs(r).sum(1)
        result[..., 3][complete] = np.divide(
            np.abs(r.sum(1)), total, out=np.zeros(len(c)), where=total > 0
        )
    v = volume[valid_volume]
    if len(v):
        total = v.sum(1)
        result[..., 4][valid_volume] = np.divide(
            v[:, 45:].sum(1), total, out=np.full(len(v), 0.25), where=total > 0
        )
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_MINUTE_SUMMARY")
    return result


def quarantine(hours: pd.DataFrame) -> set[tuple[str, pd.Timestamp]]:
    """Read only the early historical metadata prefix needed by permitted hours."""
    required: set[str] = set()
    for text in hours.loc[hours.quarantine_count.gt(0), "anomaly_event_ids"]:
        required.update(str(text).split("|"))
    result: set[tuple[str, pd.Timestamp]] = set()
    if not required:
        return result
    with Path(
        "reports/data_audit/ta019b_action_qa_2026-10-22_201224/unresolved_event_ledger_v3.csv"
    ).open() as stream:
        for row in csv.DictReader(stream):
            if row["event_id"] in required:
                if (
                    row["timestamp_utc"] >= "2025"
                    or row["disposition"] != "UNVERIFIED_RTH_LOCAL_QUARANTINE"
                ):
                    raise ValueError("UNPERMITTED_QUARANTINE_METADATA")
                result.add((row["ticker"], pd.Timestamp(row["timestamp_utc"])))
                required.remove(row["event_id"])
            if not required:
                break
    if required:
        raise ValueError("MISSING_HISTORICAL_QUARANTINE_KEYS")
    return result


def numeric_blocks(
    ref: dict, hours: pd.DataFrame, excluded: set[tuple[str, pd.Timestamp]]
) -> tuple[np.ndarray, dict]:
    """Bounded projected genuine paths, matched to adjusted-hourly action basis."""
    path = Path(ref["path"])
    if not "2010-07" <= path.stem <= "2024-12":
        raise ValueError("SOURCE_MONTH_BEFORE_IO")
    if path.stat().st_size != int(ref["bytes"]) or digest(path) != ref["sha256"]:
        raise ValueError("PINNED_MINUTE_IDENTITY")
    starts = pd.DatetimeIndex(sorted(hours.hour_start_utc.unique()))
    utc_ns = starts.tz_localize(None).to_numpy(dtype="datetime64[ns]")
    expected_ns = utc_ns.view(np.int64)[:, None] + np.arange(60)[None, :] * 60_000_000_000
    times = pd.DatetimeIndex(pd.to_datetime(expected_ns.ravel(), unit="ns", utc=True))
    minute = pd.read_parquet(
        path,
        columns=[
            "ticker",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "is_rth",
            "is_genuine",
            "is_imputed",
            "source_revision",
        ],
        filters=[("timestamp", "in", times.tolist()), ("is_rth", "==", True)],
    )
    if minute.duplicated(["ticker", "timestamp"]).any():
        raise ValueError("DUPLICATE_GENUINE_MINUTE")
    assert minute.is_genuine.all() and not minute.is_imputed.any()
    assert minute.source_revision.eq(REVISION).all()
    raw = minute[["open", "high", "low", "close", "volume"]].to_numpy(float)
    valid = np.isfinite(raw).all(1) & (raw[:, :4] > 0).all(1) & (raw[:, 4] >= 0)
    valid &= (raw[:, 1] >= np.maximum(raw[:, 0], raw[:, 3])) & (
        np.minimum(raw[:, 0], raw[:, 3]) >= raw[:, 2]
    )
    if not valid.all():
        raise ValueError("INVALID_CANONICAL_MINUTE_OHLCV", int((~valid).sum()))
    excluded_mask = np.asarray(
        [(s, t) in excluded for s, t in zip(minute.ticker, minute.timestamp)], bool
    )
    minute = minute.loc[~excluded_mask]
    mapping = pd.Series(np.repeat(np.arange(len(starts)), 60), index=times)
    hour = minute.timestamp.map(mapping).to_numpy(int)
    stock = minute.ticker.map({s: j for j, s in enumerate(SYMBOLS)}).to_numpy(int)
    stamps = minute.timestamp.dt.tz_localize(None).to_numpy(dtype="datetime64[ns]")
    position = ((stamps - utc_ns[hour]) / np.timedelta64(1, "m")).astype(int)
    assert ((position >= 0) & (position < 60)).all()
    table = hours.set_index(["hour_start_utc", "ticker"]).reindex(
        pd.MultiIndex.from_product([starts, SYMBOLS])
    )
    factors = table.price_factor.to_numpy(float).reshape(len(starts), 20)
    assert np.isfinite(factors).all() and (factors > 0).all()
    values = minute[["open", "high", "low", "close", "volume"]].to_numpy(float, copy=True)
    values[:, :4] *= factors[hour, stock, None]
    tensor = np.full((len(starts), 20, 60, 5), np.nan)
    tensor[hour, stock, position] = values
    present = np.isfinite(tensor[..., 3])
    np.testing.assert_array_equal(present.sum(-1).ravel(), table.genuine_count)
    # Reproduce the source's genuine first/last and observed extrema/sum conventions.
    candidates = {"open": tensor[:, :, 0, 0], "close": tensor[:, :, -1, 3]}
    nonempty = present.any(-1)
    extrema = np.where(present[..., None], tensor[..., :4], np.nan)
    for name, col in [("high", 1), ("low", 2)]:
        a = np.full(nonempty.shape, np.nan)
        a[nonempty] = (np.nanmax if name == "high" else np.nanmin)(
            extrema[..., col][nonempty], axis=-1
        )
        a[table.quarantine_count.to_numpy().reshape(len(starts), 20) > 0] = np.nan
        candidates[name] = a
    volume = np.nansum(tensor[..., 4], axis=-1)
    volume[~nonempty] = np.nan
    candidates["observed_volume"] = volume
    discrepancies = {}
    for field, computed in candidates.items():
        old = table[field].to_numpy(float).reshape(len(starts), 20)
        np.testing.assert_array_equal(np.isnan(computed), np.isnan(old))
        finite = np.isfinite(old)
        np.testing.assert_allclose(computed[finite], old[finite], atol=1e-10, rtol=1e-10)
        discrepancies[field] = (
            float(np.max(abs(computed[finite] - old[finite]))) if finite.any() else 0.0
        )
    features = path_features(tensor[..., :4], tensor[..., 4], present)
    return features, dict(
        path=str(path),
        sha256=ref["sha256"],
        rows_read=len(raw),
        quarantined_rows=int(excluded_mask.sum()),
        scheduled_hours=len(starts),
        expected_stock_minutes=len(starts) * 20 * 60,
        genuine_stock_minutes=int(present.sum()),
        observed_zero_volume_minutes=int((raw[:, 4] == 0).sum()),
        mathematical_source_reconciliation=discrepancies,
        complete_stock_hours=int(present.all(-1).sum()),
        max_timestamp=str(minute.timestamp.max()),
        min_timestamp=str(minute.timestamp.min()),
    )


def certify() -> None:
    """Two-stage source gate then compact unique-hour summaries, never model calls."""
    assert (OUT / "frozen_protocol.json").exists()
    if (OUT / "source_certification.json").exists():
        raise ValueError("SINGLE_USE_SOURCE_CERTIFICATION")
    grid, rows, roles = metadata()
    positions = np.unique(np.concatenate(list(roles.values())))
    needed = np.unique(
        np.concatenate(
            [
                np.arange(a, b + 1)
                for a, b in rows.iloc[positions][["first_step", "entry_index"]].to_numpy(int)
            ]
        )
    )
    assert (rows.iloc[positions].entry_index - rows.iloc[positions].first_step).eq(47).all()
    gate_c = c_regime_gate(grid, rows, roles)
    pd.DataFrame(gate_c).to_csv(OUT / "S3C/normalizer_blockers.csv", index=False)
    write(
        OUT / "S3C/readiness.json",
        dict(
            status="BLOCKED" if gate_c else "REGIME_METADATA_PASS_NUMERIC_U_NOT_YET_FITTED",
            blockers=gate_c,
            fits=0,
        ),
    )
    refs = pd.read_csv(SOURCE / "S4_NUMERICAL_SOURCE_READS.csv")
    hourly = refs.loc[refs.purpose.eq("permitted adjusted hourly source")]
    minutes = refs.loc[refs.purpose.eq("permitted genuine minute endpoints; no proxy")]
    fields = [
        "ticker",
        "hour_start_utc",
        "hour_end_utc",
        "is_stub",
        "price_factor",
        "price_basis_id",
        "quarantine_count",
        "anomaly_event_ids",
        "genuine_count",
        "expected_minutes",
        "open",
        "close",
        "high",
        "low",
        "observed_volume",
    ]
    batches = []
    for ref in hourly.to_dict("records"):
        month = Path(ref["path"]).stem
        if not "2010-07" <= month <= "2024-12":
            raise ValueError("UNPERMITTED_HOURLY_PATH")
        starts = grid.loc[
            grid.index.isin(needed) & grid.session_date_et.str.startswith(month), "hour_start_utc"
        ].tolist()
        if starts:
            assert digest(Path(ref["path"])) == ref["sha256"]
            h = pd.read_parquet(
                ref["path"], columns=fields, filters=[("hour_start_utc", "in", starts)]
            )
            assert not h.is_stub.any() and h.expected_minutes.eq(60).all()
            batches.append((month, h))
    hours = pd.concat([h for _, h in batches], ignore_index=True)
    excluded = quarantine(hours)
    # A tiny deterministic source check spans all stocks, eras, early closes/actions.
    sample_dates = [
        "2011-03-25",
        "2011-06-23",
        "2014-06-09",
        "2015-11-27",
        "2020-08-31",
        "2022-06-06",
        "2024-07-15",
        "2024-12-24",
    ]
    sample = []
    for month, h in batches:
        dates = h.hour_start_utc.dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
        chosen = h.loc[dates.isin(sample_dates)]
        if len(chosen):
            chosen = chosen.loc[
                chosen.hour_start_utc.isin(sorted(chosen.hour_start_utc.unique())[:2])
            ]
            ref = minutes.loc[minutes.path.str.endswith(month + ".parquet")].iloc[0].to_dict()
            _, record = numeric_blocks(ref, chosen, excluded)
            sample.append(record)
    if not sample:
        raise ValueError("EMPTY_STRATIFIED_NUMERIC_SAMPLE")
    write(
        OUT / "sample_source_certification.json",
        dict(
            status="SAMPLE_SOURCE_CERTIFIED",
            tolerance=dict(atol=1e-10, rtol=1e-10),
            examples=sample,
        ),
    )
    features = np.zeros((len(grid), 20, 7), float)
    receipts = []
    for month, h in batches:
        ref = minutes.loc[minutes.path.str.endswith(month + ".parquet")].iloc[0].to_dict()
        result, record = numeric_blocks(ref, h, excluded)
        ix = grid.index[grid.hour_start_utc.isin(h.hour_start_utc.unique())].to_numpy(int)
        features[ix] = result
        receipts.append(record)
        print(
            "SOURCE",
            month,
            record["genuine_stock_minutes"],
            "complete",
            record["complete_stock_hours"],
            flush=True,
        )
    np.savez_compressed(
        OUT / "minute_summary_primitives.npz", features=features, required_hours=needed
    )
    coverage = []
    for name, pos in roles.items():
        ix = rows.iloc[pos].first_step.to_numpy(int)[:, None] + np.arange(48)
        valid = features[ix, :, 5]
        for j, symbol in enumerate(SYMBOLS):
            coverage.append(
                dict(
                    fold=name[:3],
                    role=name[4:],
                    ticker=symbol,
                    origins=len(pos),
                    stock_hours=len(pos) * 48,
                    genuine_complete_stock_hours=int(valid[:, :, j].sum()),
                    complete_fraction=float(valid[:, :, j].mean()),
                    newest_complete_fraction=float(valid[:, -1, j].mean()),
                    basis="exhaustive exact role inputs, overlapping hours/roles",
                )
            )
    pd.DataFrame(coverage).to_csv(OUT / "coverage.csv", index=False)
    write(
        OUT / "source_access_receipt.json",
        dict(
            source_grant=read(OUT / "frozen_protocol.json")["source_grant"],
            all_numeric_reads=receipts,
            raw_minute_store_copied=False,
            future_outcome_columns_read=False,
            allowed_input_only=True,
            first_source_date=str(grid.session_date_et.iloc[needed].min()),
            last_source_date=str(grid.session_date_et.iloc[needed].max()),
        ),
    )
    write(
        OUT / "source_certification.json",
        dict(
            status="SOURCE_CERTIFIED_HISTORICAL_TIMING_PROXY",
            numeric_sample_pass=True,
            exhaustive_used_blocks_pass=True,
            required_grid_hours=len(needed),
            origin_windows=len(positions),
            stock_hours=len(needed) * 20,
            no_new_input_steps=True,
            no_primary_key_drops=True,
            quarantine_keys=len(excluded),
            rows_read=sum(x["rows_read"] for x in receipts),
            complete_stock_hours=int(features[needed, :, 5].sum()),
            publication_timing="assumed byorigin+2min,not measured",
            C_status="BLOCKED_NORMALIZER" if gate_c else "REQUIRES_NUMERIC_U_GATE",
        ),
    )


def supplement_prefix() -> None:
    """Certify additional input-only normalizer keys, preserving the first receipt."""
    if (OUT / "minute_summary_primitives_v2.npz").exists():
        raise ValueError("SINGLE_USE_PREFIX_SUPPLEMENT")
    grid, rows, _ = metadata()
    old = np.load(OUT / "minute_summary_primitives.npz")
    features = old["features"]
    seen = np.zeros(len(grid), bool)
    seen[old["required_hours"]] = True
    fit = np.zeros(len(grid), bool)
    for year in range(2021, 2025):
        for item in read(O1 / f"F{year % 100}/phases.json")["phases"].values():
            fit |= fitting_hours(grid, rows, item["cutoff"])
    missing = np.flatnonzero(fit & ~seen)
    refs = pd.read_csv(SOURCE / "S4_NUMERICAL_SOURCE_READS.csv")
    hours = refs.loc[refs.purpose.eq("permitted adjusted hourly source")]
    minutes = refs.loc[refs.purpose.eq("permitted genuine minute endpoints; no proxy")]
    fields = [
        "ticker",
        "hour_start_utc",
        "hour_end_utc",
        "is_stub",
        "price_factor",
        "price_basis_id",
        "quarantine_count",
        "anomaly_event_ids",
        "genuine_count",
        "expected_minutes",
        "open",
        "close",
        "high",
        "low",
        "observed_volume",
    ]
    receipts = []
    for month in sorted(set(grid.session_date_et.iloc[missing].str[:7])):
        ix = missing[grid.session_date_et.iloc[missing].str.startswith(month).to_numpy()]
        starts = grid.hour_start_utc.iloc[ix].tolist()
        ref = hours.loc[hours.path.str.endswith(month + ".parquet")].iloc[0]
        assert digest(Path(ref["path"])) == ref["sha256"]
        h = pd.read_parquet(ref["path"], columns=fields, filters=[("hour_start_utc", "in", starts)])
        values, receipt = numeric_blocks(
            minutes.loc[minutes.path.str.endswith(month + ".parquet")].iloc[0].to_dict(),
            h,
            quarantine(h),
        )
        features[ix] = values
        receipts.append(receipt)
    np.savez_compressed(
        OUT / "minute_summary_primitives_v2.npz",
        features=features,
        required_hours=np.union1d(old["required_hours"], missing),
    )
    write(
        OUT / "source_normalizer_supplement.json",
        dict(
            status="SOURCE_CERTIFIED_ADDITIONAL_INPUT_ONLY_PREFIX_KEYS",
            added_unique_hours=len(missing),
            source_reads=receipts,
            old_role_source_receipt="source_certification.json",
            new_primitives="minute_summary_primitives_v2.npz",
            no_neural_starts=True,
            no_outcome_or_score_selection=True,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supplement-prefix", action="store_true")
    options = parser.parse_args()
    if options.supplement_prefix:
        supplement_prefix()
    else:
        certify()
