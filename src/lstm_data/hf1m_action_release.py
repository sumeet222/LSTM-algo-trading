"""P019B event closure and review publishing; no features, labels or training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import ActivePanel, digest
from .hf1m_action_source import price_factors, publish_json, publish_table


def prepare_events(out: Path) -> None:
    """Bind the two newly exposed RTH opening gaps to dated external evidence."""
    source_config = json.loads(Path("configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(Path.cwd(), source_config)
    panel.verify_all()
    supplement_path = Path("configs/hf1m_action_qa_supplement_v1.json")
    supplement = json.loads(supplement_path.read_text())
    scan = json.loads((out / "post_adjustment_scan_receipt.json").read_text())
    unknown = [c for c in scan["candidates"] if c["status"] == "STOP_SYSTEMIC_ACTION_RISK"]
    expected = {(e["ticker"], e["date"]) for e in supplement["events"]}
    actual = {
        (e["ticker"], str(pd.Timestamp(e["timestamp_utc"]).tz_convert("America/New_York").date()))
        for e in unknown
    }
    if actual != expected:
        raise ValueError("STOP_SYSTEMIC_ACTION_RISK: supplemental event set mismatch")
    events = json.loads((out / "unresolved_event_ledger.json").read_text())
    private = Path(json.loads((out / "adjusted_hourly_manifest.json").read_text())["private_root"])
    examples = []
    for fact in supplement["events"]:
        month = next(m for m in panel.months if m["month"] == fact["date"][:7])
        frame = panel.read(month["derived_files"]["canonical_observed"]["path"])
        frame = frame.loc[frame.is_rth & frame.ticker.eq(fact["ticker"])].sort_values("timestamp")
        timestamp = pd.Timestamp(fact["date"] + " 09:30", tz="America/New_York").tz_convert("UTC")
        after = frame.loc[frame.timestamp.eq(timestamp)].iloc[0]
        before = frame.loc[frame.timestamp.lt(timestamp)].iloc[-1]
        raw = panel.read(month["raw_path"])
        for endpoint, value in (("before", before), ("after", after)):
            match = raw.loc[
                raw.ticker.eq(fact["ticker"])
                & raw.timestamp.eq(value.timestamp)
                & raw.source_row.eq(value.source_row)
            ]
            if len(match) != 1 or not np.array_equal(
                match.iloc[0][["open", "high", "low", "close", "volume"]].to_numpy(),
                value[["open", "high", "low", "close", "volume"]].to_numpy(),
            ):
                raise ValueError("SUPPLEMENTAL_RAW_LINEAGE_MISMATCH")
            examples.append({"event_id": fact["event_id"], "endpoint": endpoint, **value.to_dict()})
        if abs(np.log(after.open / before.close)) <= np.log(1.25):
            raise ValueError("SUPPLEMENTAL_DETECTOR_MISMATCH")
        event = {
            **fact,
            "timestamp_utc": str(timestamp),
            "timestamp_et": str(timestamp.tz_convert("America/New_York")),
            "after_is_rth": True,
            "original_018d": False,
            "discovery": "P019B_RTH_RESCAN",
            "raw_record_id": f"{fact['ticker']}:{month['month']}:{after.source_row}",
            "raw_path": month["raw_path"],
            "raw_linkage_hash": month["raw_sha256"],
            "canonical_event_id": f"VERIFIED_GENUINE_MOVE_RETAINED:{fact['ticker']}:{fact['date']}",
            "exclusion_activated": False,
            "open_ratio": float(after.open / before.close),
            "close_ratio": float(after.close / before.close),
            "access_date": supplement["access_date"],
            "treatment": "RETAIN_GENUINE_PRICE_MOVE; FACTOR1; NO_REPLACEMENT_PRICE",
        }
        events.append(event)
    if len(events) != 69 or len({e["event_id"] for e in events}) != 69:
        raise ValueError("STOP_REGISTER_INCOMPLETE")
    # Public ledgers contain ratios and minimal identifiers, never actual OHLCV.
    publish_json(out / "unresolved_event_ledger_v2.json", events)
    pd.DataFrame(
        [
            {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in e.items()}
            for e in events
        ]
    ).to_csv(out / "unresolved_event_ledger_v2.csv", index=False)
    publish_table(private / "supplemental_boundary_examples.parquet", pd.DataFrame(examples))
    publish_json(
        out / "action_disposition_release.json",
        {
            "base_scan_sha256": digest(out / "post_adjustment_scan_receipt.json"),
            "event_ledger": "unresolved_event_ledger_v2.json",
            "event_ledger_sha256": digest(out / "unresolved_event_ledger_v2.json"),
            "supplement_config_sha256": digest(supplement_path),
            "original_candidates": 67,
            "newly_exposed_verified_moves": 2,
            "total_candidates": 69,
            "original_excluded_candidates": 46,
            "uncontrolled_remaining": 0,
            "source_hourly_changed_after_rescan": False,
            "note": (
                "Original scan flags retained; two new openings independently sourced before "
                "final mask counting. Only scoped quarantine/source QA closure, "
                "no FT/TG/training authority."
            ),
        },
    )


def boundary_proofs(out: Path) -> None:
    """Check exact action direction on original genuine RTH endpoints, not EH quotes."""
    from .hf1m_action_masks import load_hours

    hours = load_hours(out / "adjusted_hourly_manifest.json")
    old = Path("reports/data_audit/ta019_hf1m_actions_2026-10-22_193000_v3")
    receipt = json.loads((old / "scan_receipt.json").read_text())
    path = Path(receipt["private_inventory"]) / "event_inventory.parquet"
    if digest(path) != receipt["inventory_sha256"]:
        raise ValueError("EVENT_INVENTORY_CHANGED")
    inventory = pd.read_parquet(path)
    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]
    proofs = []
    for fact in facts:
        if fact["kind"] != "SPLIT":
            continue
        event = inventory.loc[
            inventory.original_018d
            & inventory.after_ticker.eq(fact["ticker"])
            & inventory.timestamp_et.dt.tz_localize(None)
            .dt.normalize()
            .eq(pd.Timestamp(fact["date"]))
        ].iloc[0]
        before_date = str(event.before_timestamp.tz_convert("America/New_York").date())
        after_date = str(event.after_timestamp.tz_convert("America/New_York").date())
        before_factor = price_factors(fact["ticker"], pd.Series([before_date]), facts)[0]
        after_factor = price_factors(fact["ticker"], pd.Series([after_date]), facts)[0]
        if not np.isclose(after_factor / before_factor, fact["factor_denominator"], rtol=1e-12):
            raise ValueError("SPLIT_FACTOR_DIRECTION")
        ratio = float(event.after_close * after_factor / (event.before_close * before_factor))
        if abs(np.log(ratio)) > np.log(1.25):
            raise ValueError("SPLIT_BOUNDARY_STILL_MATERIAL")
        proofs.append(
            {
                "ticker": fact["ticker"],
                "ex_date": fact["date"],
                "event_id": event.event_id,
                "denominator": fact["factor_denominator"],
                "before_factor": before_factor,
                "after_factor": after_factor,
                "ratio_before": event.close_ratio,
                "ratio_after": ratio,
                "no_double_adjustment": True,
                "sources": fact["sources"],
            }
        )
    ko = hours.loc[
        hours.ticker.eq("KO") & hours.session_date_et.between("2012-08-10", "2012-08-14")
    ]
    publish_json(
        out / "split_boundary_proof.json",
        {
            "events": proofs,
            "count": len(proofs),
            "all_monthly_endpoint_factor_checks": True,
            "all_monthly_volume_conservation_checks": True,
            "ko_rth_basis_consistent_after_split": bool(ko.price_basis_id.nunique() == 1),
            "eh_inputs_in_rth_or_factor_fit": 0,
            "limitations": (
                "Volume not restated; no total-return dividend/spinoff reconstruction; "
                "ex-post split units require origin-safe representation in future feature code."
            ),
        },
    )


def finalize_field_masks(out: Path) -> None:
    """Publish field/basis overlays and a current ledger without changing source prices."""
    from .hf1m_action_masks import full_window, load_hours

    manifest = json.loads((out / "adjusted_hourly_manifest.json").read_text())
    private = Path(manifest["private_root"])
    hours = load_hours(out / "adjusted_hourly_manifest.json")
    fields = [
        "ticker",
        "hour_id",
        "hour_start_utc",
        "hour_end_utc",
        "session_date_et",
        "is_stub",
        "price_basis_id",
        "genuine_open",
        "genuine_close",
        "hour_usable_price_endpoints",
        "hour_proxy_price_usable",
        "extrema_complete",
        "observed_volume_complete",
        "quarantine_count",
        "anomaly_event_ids",
        "untrusted_fields",
        "action_boundary",
    ] + [str(c) for c in hours if str(c).startswith("hour_field_usable_")]
    overlay = hours[fields].copy()
    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]
    ordinal = np.zeros(len(overlay), dtype=int)
    for fact in facts:
        if fact["kind"] == "SPLIT":
            ordinal += (
                overlay.ticker.eq(fact["ticker"]) & overlay.session_date_et.ge(fact["date"])
            ).to_numpy()
    overlay["volume_basis_id"] = (
        overlay.ticker
        + ":AS_REPORTED_SHARE_REGIME:"
        + pd.Series(ordinal, index=overlay.index).astype(str)
    )
    full = overlay.loc[~overlay.is_stub]
    grid = (
        full[["hour_start_utc", "session_date_et"]]
        .drop_duplicates()
        .sort_values("hour_start_utc")
        .reset_index(drop=True)
    )
    regular = np.asarray(
        [str(day) for day, part in grid.groupby("session_date_et", sort=True) if len(part) == 6]
    )
    previous = np.searchsorted(regular, grid.session_date_et.to_numpy(), side="left") - 1
    basis_ok = np.ones(len(grid), dtype=bool)
    for index in np.flatnonzero(grid.session_date_et.ge("2012-05-01")):
        p = previous[index]
        basis_ok[index] = p >= 125 and regular[p - 125] >= "2012-05-01"
    crossing = ~full_window(basis_ok[:, None], 48)[:, 0]
    # Initial structural startup is handled separately, not misattributed to COP.
    crossing &= grid.session_date_et.ge("2012-05-01").to_numpy()
    times = set(grid.loc[crossing, "hour_start_utc"])
    overlay["hour_feature_dependency_action_crossing"] = overlay.ticker.eq(
        "COP"
    ) & overlay.hour_start_utc.isin(times)
    ref = publish_table(private / "hour_field_masks_v1.parquet", overlay)
    dep = pd.read_csv(out / "event_to_hour_dependency.csv")
    extra = overlay.loc[overlay.hour_feature_dependency_action_crossing]
    added = pd.DataFrame(
        {
            "event_id": "P019-042",
            "ticker": "COP",
            "hour_id": extra.hour_id,
            "dependency": "COP125D_PLUS_CONTEXT48",
            "close_excluded": False,
            "is_stub": False,
        }
    )
    pd.concat([dep, added], ignore_index=True).to_csv(
        out / "event_to_hour_dependency_v2.csv", index=False
    )
    events = json.loads((out / "unresolved_event_ledger_v2.json").read_text())
    for event in events:
        reason = event["disposition"]
        included = bool(event["after_is_rth"]) and reason != "UNVERIFIED_RTH_LOCAL_QUARANTINE"
        event["record_disposition_activated"] = True
        event["candidate_minute_used_in_rth"] = included
        event["adjustment_activated_for_rth_segment"] = reason == "VERIFIED_SPLIT_ADJUSTED"
        date = str(pd.Timestamp(event["timestamp_utc"]).tz_convert("America/New_York").date())
        event["applied_price_factor"] = (
            float(price_factors(event["ticker"], pd.Series([date]), facts)[0]) if included else None
        )
        event["applied_volume_factor"] = 1.0 if included else None
        event["post_treatment_status"] = "DISPOSITION_ACTIVATED_SOURCE_ONLY"
        event["treatment"] = reason
    publish_json(out / "unresolved_event_ledger_v3.json", events)
    pd.DataFrame(
        [
            {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in e.items()}
            for e in events
        ]
    ).to_csv(out / "unresolved_event_ledger_v3.csv", index=False)
    publish_json(
        out / "canonical_event_ledger_pointer.json",
        {
            "path": "unresolved_event_ledger_v3.json",
            "sha256": digest(out / "unresolved_event_ledger_v3.json"),
            "predecessor": "unresolved_event_ledger_v2.json",
            "candidate_ids_unchanged": True,
        },
    )
    publish_json(
        out / "hour_field_mask_manifest.json",
        {
            "namespace": manifest["namespace"],
            "file": ref,
            "cop_dependent_full_hours": len(extra),
            "prices_changed": False,
            "event_to_hour_dependency": "event_to_hour_dependency_v2.csv",
            "event_to_hour_sha256": digest(out / "event_to_hour_dependency_v2.csv"),
            "volume_units": (
                "AS_REPORTED; crossing split regimes requires channel masking "
                "or separately justified share conversion"
            ),
        },
    )


def verify_samples(out: Path) -> None:
    """Independently reconstruct actions, quarantines and control hourly candles."""
    from .hf1m_action_masks import load_hours

    config = json.loads(Path("configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(Path.cwd(), config)
    panel.verify_all()
    hours = load_hours(out / "adjusted_hourly_manifest.json")
    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())["events"]
    events = json.loads((out / "unresolved_event_ledger_v3.json").read_text())
    quarantined = {
        (e["ticker"], pd.Timestamp(e["timestamp_utc"]))
        for e in events
        if e["disposition"] == "UNVERIFIED_RTH_LOCAL_QUARANTINE"
    }
    chosen = set(hours.loc[hours.quarantine_count.gt(0), "hour_id"])
    for fact in facts:
        own = hours.loc[hours.ticker.eq(fact["ticker"]) & ~hours.is_stub].sort_values(
            "hour_start_utc"
        )
        same = own.loc[own.session_date_et.eq(fact["date"])]
        prior = own.loc[own.session_date_et.lt(fact["date"])]
        if len(same):
            chosen.add(same.iloc[0].hour_id)
        if len(prior):
            chosen.add(prior.iloc[-1].hour_id)
    for date in ["2011-12-15", "2019-11-29", "2020-03-09", "2020-11-02"]:
        chosen.update(
            hours.loc[hours.ticker.eq("AAPL") & hours.session_date_et.eq(date), "hour_id"]
        )
    selected = hours.loc[hours.hour_id.isin(chosen)]
    checks, examples = [], []
    for month, rows in selected.groupby("source_month"):
        record = next(m for m in panel.months if m["month"] == month)
        canonical = panel.read(record["derived_files"]["canonical_observed"]["path"])
        for row in rows.itertuples():
            source = canonical.loc[
                canonical.is_rth
                & canonical.ticker.eq(row.ticker)
                & canonical.timestamp.ge(row.hour_start_utc)
                & canonical.timestamp.lt(row.hour_end_utc)
            ].sort_values("timestamp")
            source = source.loc[
                ~source.timestamp.map(lambda timestamp: (row.ticker, timestamp) in quarantined)
            ]
            factor = price_factors(str(row.ticker), pd.Series([row.session_date_et]), facts)[0]
            expected = {
                "observed_high": float(source.high.max() * factor),
                "observed_low": float(source.low.min() * factor),
                "observed_volume": float(source.volume.sum()),
            }
            for field, value in expected.items():
                if not np.isclose(
                    getattr(row, field), value, rtol=1e-12, atol=1e-8, equal_nan=True
                ):
                    raise ValueError("INDEPENDENT_HOURLY_RECONSTRUCTION_FAILED")
            for field, endpoint in (
                ("open", row.hour_start_utc),
                ("close", pd.Timestamp(str(row.hour_end_utc)) - pd.Timedelta(minutes=1)),
            ):
                found = source.loc[source.timestamp.eq(endpoint)]
                expected_value = float(found[field].iloc[0] * factor) if len(found) else np.nan
                if not np.isclose(getattr(row, field), expected_value, rtol=1e-12, equal_nan=True):
                    raise ValueError("INDEPENDENT_GENUINE_ENDPOINT_FAILED")
            checks.append(
                {
                    "hour_id": row.hour_id,
                    "month": month,
                    "genuine_rows": len(source),
                    "quarantine_count": row.quarantine_count,
                    "source_sha256": record["derived_files"]["canonical_observed"]["sha256"],
                    "all_checks_passed": True,
                }
            )
            examples.append(
                {
                    "hour_id": row.hour_id,
                    "open": row.open,
                    "high": row.high,
                    "low": row.low,
                    "close": row.close,
                    **expected,
                }
            )
    private = Path(json.loads((out / "adjusted_hourly_manifest.json").read_text())["private_root"])
    ref = publish_table(private / "independent_hour_examples.parquet", pd.DataFrame(examples))
    publish_json(
        out / "independent_reconstruction_receipt.json",
        {"sample_hours": len(checks), "checks": checks, "private_examples": ref, "result": "PASS"},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare-events", action="store_true")
    parser.add_argument("--boundary-proofs", action="store_true")
    parser.add_argument("--finalize-fields", action="store_true")
    parser.add_argument("--verify-samples", action="store_true")
    args = parser.parse_args()
    if args.prepare_events:
        prepare_events(args.out)
    if args.boundary_proofs:
        boundary_proofs(args.out)
    if args.finalize_fields:
        finalize_field_masks(args.out)
    if args.verify_samples:
        verify_samples(args.out)


if __name__ == "__main__":
    main()
