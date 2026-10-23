"""P019B split-consistent RTH source derivation; no indicators or model targets."""

from __future__ import annotations

import argparse
import json
import os
import pickle
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS, ActivePanel, digest, scan_stock
from .hf_minute_long_qa import calendar_frame

try:
    import resource
except ImportError:  # Optional resource telemetry on non-POSIX platforms.
    resource = None

PRICE = ("open", "high", "low", "close")
NAMESPACE = "HF20_HF1M_LONG_v1_ACTION_QA_v1"


def publish_json(path: Path, value: object) -> None:
    """Atomic publication; idempotent identical replay, never replace other evidence."""
    data = (json.dumps(value, indent=2, default=str) + "\n").encode()
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"IMMUTABLE_OUTPUT_CHANGED: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        stream.write(data)
        temporary = Path(stream.name)
    os.replace(temporary, path)


def publish_table(path: Path, frame: pd.DataFrame) -> dict:
    """Atomic local numerical table; checkpoints use exact file hashes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
    frame.to_parquet(temporary, index=False, compression="zstd")
    if path.exists():
        if digest(path) != digest(temporary):
            raise ValueError("IMMUTABLE_TABLE_CHANGED")
        temporary.unlink()
        return {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            "rows": len(frame),
        }
    os.replace(temporary, path)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "rows": len(frame),
    }


def price_factors(
    ticker: str, dates: pd.Series, facts: list[dict], asof: str = "2026-03-31"
) -> np.ndarray:
    """Exact split direction; optional as-of prefix excludes future actions."""
    factor = np.ones(len(dates), dtype=float)
    for action in facts:
        if action["ticker"] == ticker and action["kind"] == "SPLIT" and action["date"] <= asof:
            factor[dates.to_numpy() < action["date"]] /= action["factor_denominator"]
    return factor


def adjust_prices(frame: pd.DataFrame, facts: list[dict], asof: str = "2026-03-31") -> pd.DataFrame:
    """Adjust RTH OHLC only, idempotently; volume remains observed source units."""
    if "price_adjustment_version" in frame:
        if not frame.price_adjustment_version.eq(NAMESPACE + ":" + asof).all():
            raise ValueError("PRICE_BASIS_MISMATCH")
        return frame.copy()
    if not frame.is_rth.all():
        raise ValueError("EH_PRICE_INPUT_FORBIDDEN")
    result = frame.copy()
    dates = result.timestamp.dt.tz_convert("America/New_York").dt.tz_localize(None)
    dates = pd.Series(dates.to_numpy(dtype="datetime64[D]").astype(str), index=result.index)
    result["price_factor"] = 1.0
    for symbol in SYMBOLS:
        mask = result.ticker.eq(symbol)
        result.loc[mask, "price_factor"] = price_factors(symbol, dates[mask], facts, asof)
    result[list(PRICE)] = result[list(PRICE)].mul(result.price_factor, axis=0)
    result["price_adjustment_version"] = NAMESPACE + ":" + asof
    return result


def event_dispositions(evidence: list[dict]) -> list[dict]:
    """Every P019 candidate gets exactly one disposition; aliases retain all IDs."""
    if len(evidence) != 67 or len({e["event_id"] for e in evidence}) != 67:
        raise ValueError("STOP_REGISTER_INCOMPLETE")
    rows = []
    for event in evidence:
        ticker = event["ticker"]
        date = str(pd.Timestamp(event["timestamp_utc"]).tz_convert("America/New_York").date())
        if ticker == "KO" and date == "2012-08-13" and not event["after_is_rth"]:
            reason = "KO_MIXED_BASIS_PREMARKET"
        elif ticker == "COP" and date == "2012-05-01":
            reason = "COP_2012_SPINOFF_LOCAL_BOUNDARY"
        elif event["classification"] == "VERIFIED_REAL_MARKET_MOVE":
            reason = "VERIFIED_GENUINE_MOVE_RETAINED"
        elif event["classification"] == "VERIFIED_CORPORATE_ACTION":
            reason = "VERIFIED_SPLIT_ADJUSTED"
        elif event["after_is_rth"]:
            reason = "UNVERIFIED_RTH_LOCAL_QUARANTINE"
        else:
            reason = "UNVERIFIED_EH_OUT_OF_SCOPE"
        row = dict(event)
        row["disposition"] = reason
        row["canonical_event_id"] = f"{reason}:{ticker}:{date}"
        row["exclusion_activated"] = reason in {
            "KO_MIXED_BASIS_PREMARKET",
            "COP_2012_SPINOFF_LOCAL_BOUNDARY",
            "UNVERIFIED_RTH_LOCAL_QUARANTINE",
            "UNVERIFIED_EH_OUT_OF_SCOPE",
        }
        rows.append(row)
    counts = pd.Series([r["disposition"] for r in rows]).value_counts().to_dict()
    if counts != {
        "UNVERIFIED_EH_OUT_OF_SCOPE": 24,
        "UNVERIFIED_RTH_LOCAL_QUARANTINE": 18,
        "VERIFIED_SPLIT_ADJUSTED": 17,
        "VERIFIED_GENUINE_MOVE_RETAINED": 4,
        "KO_MIXED_BASIS_PREMARKET": 3,
        "COP_2012_SPINOFF_LOCAL_BOUNDARY": 1,
    }:
        raise ValueError("STOP_REGISTER_INCOMPLETE: disposition reconciliation")
    return rows


def derive_month(
    canonical: pd.DataFrame,
    original: pd.DataFrame,
    proxies: pd.DataFrame,
    sensitivity: pd.DataFrame,
    month: str,
    facts: list[dict],
    events: list[dict],
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Aggregate only genuine unquarantined RTH; original calendar bins are conserved."""
    grid = calendar_frame(month)
    if not canonical.timestamp.isin(grid.timestamp).eq(canonical.is_rth).all():
        raise ValueError("STOP_IDENTITY: RTH calendar mismatch")
    rth = canonical.loc[canonical.is_rth].copy()
    rth = rth.merge(grid, on="timestamp", how="left", validate="many_to_one")
    rth["hour_id"] = rth.ticker + ":" + rth.session_date_et + ":" + rth.hour_slot.astype(str)
    rth["quarantined"] = False
    event_hours: dict[str, list[str]] = {}
    for event in events:
        if event["disposition"] != "UNVERIFIED_RTH_LOCAL_QUARANTINE":
            continue
        mask = rth.ticker.eq(event["ticker"]) & rth.timestamp.eq(
            pd.Timestamp(event["timestamp_utc"])
        )
        if mask.any():
            if mask.sum() != 1:
                raise ValueError("QUARANTINE_RAW_KEY_AMBIGUOUS")
            rth.loc[mask, "quarantined"] = True
            hour_id = rth.loc[mask, "hour_id"].iloc[0]
            event_hours.setdefault(hour_id, []).append(event["event_id"])
    adjusted = adjust_prices(rth, facts)
    safe = adjusted.loc[~adjusted.quarantined].sort_values(["ticker", "timestamp"])
    agg = safe.groupby("hour_id", sort=False).agg(
        observed_open=("open", "first"),
        observed_close=("close", "last"),
        observed_high=("high", "max"),
        observed_low=("low", "min"),
        observed_volume=("volume", "sum"),
        first_minute=("timestamp", "min"),
        last_minute=("timestamp", "max"),
        genuine_count=("timestamp", "size"),
    )
    original = original.rename(columns={field: field + "_018d" for field in PRICE + ("volume",)})
    hours = original.merge(
        agg, on="hour_id", how="left", validate="one_to_one", suffixes=("_018d", "")
    )
    hours["quarantine_count"] = (
        hours.hour_id.map(rth.loc[rth.quarantined].groupby("hour_id").size()).fillna(0).astype(int)
    )
    hours["genuine_count"] = hours.genuine_count.fillna(0).astype(int)
    hours["genuine_open"] = hours.first_minute.eq(hours.hour_start_utc)
    hours["genuine_close"] = hours.last_minute.eq(hours.hour_end_utc - pd.Timedelta(minutes=1))
    hours["open"] = hours.observed_open.where(hours.genuine_open)
    hours["close"] = hours.observed_close.where(hours.genuine_close)
    hours["high"] = hours.observed_high.where(hours.quarantine_count.eq(0))
    hours["low"] = hours.observed_low.where(hours.quarantine_count.eq(0))
    hours["volume"] = hours.observed_volume
    hours["observed_volume_complete"] = hours.genuine_count.eq(hours.expected_minutes)
    hours["hour_field_usable_open"] = hours.genuine_open
    hours["hour_field_usable_close"] = hours.genuine_close
    for field in ("high", "low"):
        hours[f"hour_field_usable_{field}"] = hours[field].notna()
    hours["hour_field_usable_complete_volume"] = hours.observed_volume_complete
    hours["extrema_complete"] = hours.observed_volume_complete
    hours["missing_count"] = hours.absent_minutes
    hours["conflict_count"] = hours.ambiguous_minutes
    hours["anomaly_event_ids"] = hours.hour_id.map(
        lambda key: "|".join(event_hours.get(str(key), []))
    )
    hours["untrusted_fields"] = np.where(hours.quarantine_count.gt(0), "high|low|volume", "")
    sensitivity = sensitivity.set_index("hour_id")
    hours["proxy_count"] = hours.hour_id.map(sensitivity.filled_cap5).fillna(0).astype(int)
    blocked = hours.quarantine_count.gt(0)
    hours.loc[blocked, "proxy_count"] = 0
    hours["close_input_cap0"] = hours["close"]
    hours["close_input_cap5"] = hours["close"]
    if len(proxies):
        if proxies.is_genuine.any() or not proxies.is_imputed.all():
            raise ValueError("PROXY_LINEAGE_CHANGED")
        terminal = proxies.merge(
            hours[["hour_id", "hour_end_utc"]], on="hour_id", validate="many_to_one"
        )
        terminal = terminal.loc[
            terminal.timestamp.eq(terminal.hour_end_utc - pd.Timedelta(minutes=1))
        ]
        terminal = terminal.set_index("hour_id")
        eligible = (~blocked) & hours.hour_id.isin(terminal.index) & ~hours.genuine_close
        # Original proxies were causal at completed-hour clock; do not invent new ones.
        for symbol in SYMBOLS:
            own = eligible & hours.ticker.eq(symbol)
            factor = price_factors(symbol, hours.loc[own, "session_date_et"], facts)
            hours.loc[own, "close_input_cap5"] = (
                hours.loc[own, "hour_id"].map(terminal.close).to_numpy() * factor
            )
    hours["hour_usable_price_endpoints"] = hours.genuine_close
    hours["hour_proxy_price_usable"] = hours.close_input_cap5.notna()
    hours["action_boundary"] = False
    for action in facts:
        if action["kind"] not in {"SPLIT", "SPINOFF"}:
            continue
        own = hours.ticker.eq(action["ticker"]) & hours.session_date_et.eq(action["date"])
        hours.loc[
            own & hours.hour_start_utc.eq(hours.loc[own, "hour_start_utc"].min()), "action_boundary"
        ] = True
    hours["price_basis_id"] = "SPLIT_CONSISTENT_20260331"
    cop = hours.ticker.eq("COP")
    hours.loc[cop & hours.session_date_et.lt("2012-05-01"), "price_basis_id"] = "COP_PRE_SPINOFF"
    hours.loc[cop & hours.session_date_et.ge("2012-05-01"), "price_basis_id"] = "COP_POST_SPINOFF"
    hours["price_factor"] = 1.0
    for symbol in SYMBOLS:
        own = hours.ticker.eq(symbol)
        hours.loc[own, "price_factor"] = price_factors(
            symbol, hours.loc[own, "session_date_et"], facts
        )
    hours["volume_factor"] = 1.0
    hours["price_adjustment_version"] = NAMESPACE
    hours["is_rth"] = True
    if len(hours) != len(original) or hours.hour_id.duplicated().any():
        raise ValueError("HOUR_GRID_CHANGED")
    if not (hours.genuine_count + hours.quarantine_count).eq(hours.genuine_minutes).all():
        raise ValueError("GENUINE_MINUTE_CONSERVATION")
    removed = rth.loc[rth.quarantined].groupby("ticker").volume.sum().reindex(SYMBOLS, fill_value=0)
    expected = original.groupby("ticker").observed_volume.sum().reindex(SYMBOLS) - removed
    actual = hours.groupby("ticker").observed_volume.sum().reindex(SYMBOLS)
    if not np.allclose(expected.to_numpy(), actual.to_numpy(), rtol=0, atol=1e-6):
        raise ValueError("OBSERVED_VOLUME_NOT_CONSERVED")
    for field in ("open", "close"):
        mask = hours[f"genuine_{field}"]
        if not np.allclose(
            hours.loc[mask, field],
            hours.loc[mask, field + "_018d"] * hours.loc[mask, "price_factor"],
            rtol=1e-12,
        ):
            raise ValueError("NON_QUARANTINED_ENDPOINT_CHANGED")
    receipt = {
        "month": month,
        "rth_canonical": len(rth),
        "quarantined_minutes": int(rth.quarantined.sum()),
        "hour_rows": len(hours),
        "affected_hours": int(blocked.sum()),
        "observed_volume_conserved": True,
        "endpoint_factors_match_original": True,
        "grid_counts_unchanged": True,
    }
    hours["source_quality_tier_018d"] = hours.quality_tier
    hours["source_action_uncertainty_018d"] = hours.action_uncertainty
    hours["action_uncertainty"] = blocked
    hours["volume_is_complete"] = hours.observed_volume_complete
    hours["close_is_genuine"] = hours.genuine_close
    hours["open_is_genuine"] = hours.genuine_open
    hours["filled_minutes"] = hours.proxy_count
    hours["unfilled_minutes"] = hours.expected_minutes - hours.genuine_count - hours.proxy_count
    hours["partial_hour"] = ~hours.observed_volume_complete
    hours["zero_observed_hours"] = hours.genuine_count.eq(0)
    hours["all_ohlc_genuine_or_complete"] = hours.observed_volume_complete
    hours["strict_candidate"] = hours.observed_volume_complete
    hours["moderate_candidate"] = (
        (hours.genuine_count + hours.proxy_count).eq(hours.expected_minutes)
        & hours.genuine_open
        & hours.genuine_close
        & ~blocked
    )
    hours["broad_candidate"] = hours.genuine_count.gt(0)
    hours.loc[blocked, "quality_tier"] = "QUARANTINED_EXTREMA_VOLUME"
    hours["training_eligibility_suggestion"] = "PREFEATURE_DEPENDENCY_MASKS_REQUIRED"
    # Original prices remain addressable through the source manifest, not an
    # unadjusted fallback column in the activated source layer.
    hours = hours.drop(columns=[f + "_018d" for f in PRICE + ("volume", "observed_volume")])
    return hours, safe, receipt


def run(out: Path, config_path: Path) -> None:
    root = config_path.resolve().parent.parent
    config = json.loads(config_path.read_text())
    panel = ActivePanel(root, json.loads((root / config["source_config"]).read_text()))
    refs = panel.verify_all()
    old = root / config["p019"]
    evidence_path = old / "P019_PRICE_JUMP_EVIDENCE.json"
    facts_path = root / config["facts"]
    if (
        digest(evidence_path) != config["evidence_sha256"]
        or digest(facts_path) != config["facts_sha256"]
    ):
        raise ValueError("STOP_IDENTITY: evidence binding changed")
    events = event_dispositions(json.loads(evidence_path.read_text()))
    facts = json.loads(facts_path.read_text())["events"]
    private = Path("data/processed/hf20_hf1m_long_v1_action_qa_v1") / out.name
    private.mkdir(parents=True, exist_ok=True)
    contract = {
        "namespace": NAMESPACE,
        "config_sha256": digest(config_path),
        "source_code_sha256": digest(Path(__file__)),
        "source_manifest_sha256": panel.config["manifest_sha256"],
    }
    if (out / "execution_contract.json").exists():
        original_contract = json.loads((out / "execution_contract.json").read_text())
        if original_contract != contract:
            amendment = json.loads((out / "source_execution_amendment_v2.json").read_text())
            if (
                amendment["previous_code_sha256"] != original_contract["source_code_sha256"]
                or amendment["current_code_sha256"] != contract["source_code_sha256"]
                or any(
                    original_contract[k] != contract[k]
                    for k in contract
                    if k != "source_code_sha256"
                )
            ):
                raise ValueError("EXECUTION_CONTRACT_CHANGED")
            contract = original_contract
    publish_json(out / "execution_contract.json", contract)
    publish_json(out / "active_input_hash_receipt.json", refs)
    publish_json(out / "unresolved_event_ledger.json", events)
    publish_json(out / "split_factor_ledger.json", [e for e in facts if e["kind"] == "SPLIT"])
    states: dict[str, dict[str, pd.DataFrame]] = {s: {} for s in SYMBOLS}
    rescans = []
    receipts = []
    started = time.monotonic()
    for month in panel.months:
        checkpoint = out / "months" / (month["month"] + ".json")
        if checkpoint.exists():
            record = json.loads(checkpoint.read_text())
            for ref in record["files"].values():
                if digest(Path(ref["path"])) != ref["sha256"]:
                    raise ValueError("CHECKPOINT_CHANGED")
            # A resumed scan restores scan state from compact saved genuine tails.
            state_path = private / "scan_state" / (month["month"] + ".pkl")
            if digest(state_path) != record["scan_state_sha256"]:
                raise ValueError("SCAN_STATE_CHANGED")
            states = pd.read_pickle(state_path)
            rescans.extend(record["rescan_candidates"])
            receipts.append(record)
            continue
        d = month["derived_files"]
        hourly, safe, record = derive_month(
            panel.read(d["canonical_observed"]["path"]),
            panel.read(d["hourly_ohlcv"]["path"]),
            panel.read(d["fill_proxies_cap5"]["path"]),
            panel.read(d["fill_sensitivity"]["path"]),
            month["month"],
            facts,
            events,
        )
        candidates = []
        for symbol in SYMBOLS:
            for event in scan_stock(safe.loc[safe.ticker.eq(symbol)], states[symbol], 1.25, 1.5):
                timestamp = event["after_timestamp"]
                date = str(timestamp.tz_convert("America/New_York").date())
                match = [
                    e
                    for e in events
                    if e["ticker"] == symbol
                    and str(pd.Timestamp(e["timestamp_utc"]).tz_convert("America/New_York").date())
                    == date
                ]
                allowed = [
                    e
                    for e in match
                    if e["disposition"]
                    in {"VERIFIED_GENUINE_MOVE_RETAINED", "COP_2012_SPINOFF_LOCAL_BOUNDARY"}
                ]
                candidates.append(
                    {
                        "ticker": symbol,
                        "timestamp_utc": str(timestamp),
                        "rules": event["rules"],
                        "mapped_event_ids": [e["event_id"] for e in allowed],
                        "status": "RETAIN_VERIFIED_MOVE"
                        if allowed and allowed[0]["disposition"] == "VERIFIED_GENUINE_MOVE_RETAINED"
                        else "BOUNDARY_MASK"
                        if allowed
                        else "STOP_SYSTEMIC_ACTION_RISK",
                    }
                )
        record["rescan_candidates"] = candidates
        record["files"] = {
            "hourly": publish_table(private / "hourly" / (month["month"] + ".parquet"), hourly)
        }
        state_path = private / "scan_state" / (month["month"] + ".pkl")
        state_path.parent.mkdir(exist_ok=True)
        with state_path.open("wb") as stream:
            pickle.dump(states, stream, protocol=pickle.HIGHEST_PROTOCOL)
        record["scan_state_sha256"] = digest(state_path)
        publish_json(checkpoint, record)
        receipts.append(record)
        rescans.extend(candidates)
        print(
            month["month"],
            "hours",
            len(hourly),
            "quarantine",
            record["quarantined_minutes"],
            flush=True,
        )
    publish_json(
        out / "post_adjustment_scan_receipt.json",
        {
            "scope": "ALL20_RTH_GENUINE_UNQUARANTINED; noEH",
            "rth_rows": sum(r["rth_canonical"] for r in receipts),
            "candidates": rescans,
            "uncontrolled": sum(r["status"] == "STOP_SYSTEMIC_ACTION_RISK" for r in rescans),
        },
    )
    if (out / "adjusted_hourly_manifest.json").exists():
        print("ALREADY_COMPLETE_VERIFIED_CHECKPOINT_REPLAY", flush=True)
        panel.verify_all()
        return
    publish_json(
        out / "adjusted_hourly_manifest.json",
        {
            **contract,
            "private_root": str(private),
            "monthly": receipts,
            "source_inputs_reverified": len(panel.verify_all()),
            "wall_seconds": time.monotonic() - started,
            "peak_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if resource
            else None,
            "no_features_targets_or_training": True,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/hf1m_action_qa_v1.json"))
    args = parser.parse_args()
    run(args.out, args.config)


if __name__ == "__main__":
    main()
