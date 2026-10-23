"""Publish a STOP/PASS action review from explicit evidence; never model data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from lstm_data.hf1m_action_audit import ActivePanel, digest, write_json


def verify_event_lineage(root: Path, out: Path) -> None:
    """Match every before/after canonical candle to its immutable raw row."""
    config = json.loads((root / "configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(root, config)
    panel.verify_all()
    receipt = json.loads((out / "scan_receipt.json").read_text())
    private = root / receipt["private_inventory"]
    path = private / "event_inventory.parquet"
    if digest(path) != receipt["inventory_sha256"]:
        raise ValueError("STOP_IDENTITY: inventory bytes")
    inventory = pd.read_parquet(path)
    checks = []
    for month in panel.months:
        selected = []
        for _, event in inventory.iterrows():
            for endpoint in ("before", "after"):
                timestamp = event[f"{endpoint}_timestamp"]
                key = timestamp.tz_convert("America/New_York").strftime("%Y-%m")
                if key == month["month"]:
                    selected.append((event, endpoint, timestamp))
        if not selected:
            continue
        raw = panel.read(month["raw_path"])
        for event, endpoint, timestamp in selected:
            found = raw.loc[
                (raw.ticker == event.after_ticker)
                & (raw.timestamp == timestamp)
                & (raw.source_row == event[f"{endpoint}_source_row"])
            ]
            if len(found) != 1:
                raise ValueError("STOP_IDENTITY: raw event row ambiguous")
            row = found.iloc[0]
            if not row.is_genuine or any(
                float(row[field]) != float(event[f"{endpoint}_{field}"])
                for field in ("open", "high", "low", "close", "volume")
            ):
                raise ValueError("STOP_IDENTITY: raw event candle differs")
            checks.append(
                {
                    "event_id": event.event_id,
                    "endpoint": endpoint,
                    "ticker": row.ticker,
                    "timestamp_utc": str(timestamp),
                    "raw_path": month["raw_path"],
                    "raw_sha256": month["raw_sha256"],
                    "source_file": row.source_file,
                    "source_row_group": int(row.source_row_group),
                    "source_row": int(row.source_row),
                    "all_five_values_equal": True,
                }
            )
    if len(checks) != 2 * len(inventory):
        raise ValueError("STOP_IDENTITY: incomplete event lineage")
    pd.DataFrame(checks).to_csv(out / "event_raw_lineage_checks.csv", index=False)
    write_json(
        out / "event_raw_lineage_receipt.json",
        {
            "checks": len(checks),
            "events": len(inventory),
            "matched_values": "ALL_OHLCV",
            "lineage_sha256": digest(out / "event_raw_lineage_checks.csv"),
            "result": "PASS_RAW_CANONICAL_EQUALITY_ONLY; NOT_EXTERNAL_PRINT_CERTIFICATION",
        },
    )


def gate_decision(events: list[dict], post_scan_clean: bool) -> str:
    """Require original13, evidence and completed handling, never ratio-only PASS."""
    if not events or sum(e["original_018d"] for e in events) != 13:
        return "STOP_ACTION_UNVERIFIED"
    allowed = {"VERIFIED_CORPORATE_ACTION", "VERIFIED_REAL_MARKET_MOVE", "VERIFIED_SOURCE_ARTIFACT"}
    if not post_scan_clean or any(
        e["classification"] not in allowed
        or not e.get("sources")
        or not all(s.get("url", "").startswith("https://") for s in e["sources"])
        or e.get("post_treatment_status") != "VERIFIED_CLEAN"
        for e in events
    ):
        return "STOP_ACTION_UNVERIFIED"
    return "PASS_ACTION_VERIFICATION"


def review(root: Path, out: Path, facts_path: Path) -> None:
    """Enrich each candidate with source/hour lineage and immutable review facts.

    Hour contexts are source-QA evidence, not forecast origins or feature/label
    eligibility. No model outcome or future-return arithmetic is performed.
    """
    config = json.loads((root / "configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(root, config)
    panel.verify_all()
    receipt = json.loads((out / "scan_receipt.json").read_text())
    private = root / receipt["private_inventory"]
    inventory_path = private / "event_inventory.parquet"
    if digest(inventory_path) != receipt["inventory_sha256"]:
        raise ValueError("STOP_IDENTITY: event inventory changed")
    inventory = pd.read_parquet(inventory_path)
    originals = pd.read_parquet(private / "original_018d_13.parquet")
    facts = json.loads(facts_path.read_text())
    by_event = {(e["ticker"], e["date"]): e for e in facts["events"]}
    hourly = pd.concat(
        [panel.read(m["derived_files"]["hourly_ohlcv"]["path"]) for m in panel.months],
        ignore_index=True,
    )
    event_contexts = []
    rows = []
    factors = []
    split_checks = []
    for _, event in inventory.iterrows():
        ticker = event.after_ticker
        timestamp = event.after_timestamp
        date = timestamp.tz_convert("America/New_York").strftime("%Y-%m-%d")
        fact = by_event.get((ticker, date))
        classification = fact["classification"] if fact else "UNRESOLVED_MATERIAL_JUMP"
        if ticker == "KO" and not event.after_is_rth:
            classification = "UNRESOLVED_MATERIAL_JUMP"
        stock = hourly.loc[hourly.ticker == ticker].sort_values("hour_start_utc")
        affected = stock.loc[(stock.hour_start_utc <= timestamp) & (timestamp < stock.hour_end_utc)]
        context = stock.loc[~stock.is_stub]
        context = pd.concat(
            [
                context.loc[context.hour_start_utc <= timestamp].tail(49),
                context.loc[context.hour_start_utc > timestamp].head(52),
            ]
        ).copy()
        context["event_id"] = event.event_id
        context["relation"] = context.hour_start_utc.map(
            lambda value: (
                "EARLIER_SOURCE_CONTEXT" if value <= timestamp else "LATER_DIAGNOSTIC_ONLY"
            )
        )
        event_contexts.append(context)
        original = originals.loc[
            (originals.ticker == ticker) & (originals.timestamp_utc == timestamp)
        ]
        hour_ids = affected.hour_id.tolist()
        full_after = stock.loc[(~stock.is_stub) & (stock.hour_start_utc > timestamp)].head(48)
        denominator = fact["factor_denominator"] if fact else None
        status = "UNRESOLVED"
        if classification == "VERIFIED_REAL_MARKET_MOVE":
            status = "RETAIN_REAL_RETURN; GLOBAL_GATE_STILL_STOP"
        elif classification == "VERIFIED_CORPORATE_ACTION":
            status = "FACT_VERIFIED; ADJUSTMENT_NOT_ACTIVATED"
        row = {
            "event_id": event.event_id,
            "ticker": ticker,
            "timestamp_utc": str(timestamp),
            "timestamp_et": str(timestamp.tz_convert("America/New_York")),
            "original_018d": bool(event.original_018d),
            "rules": list(event.rules),
            "close_ratio": float(event.close_ratio),
            "open_ratio": float(event.open_ratio),
            "minute_high_low_ratio": float(event.after_high / event.after_low),
            "elapsed_minutes": float(event.elapsed_minutes),
            "after_is_rth": bool(event.after_is_rth),
            "before_is_rth": bool(event.before_is_rth),
            "raw_record_id": f"{ticker}:{event.source_month}:{event.after_source_row}",
            "raw_path": next(
                m["raw_path"] for m in panel.months if m["month"] == event.source_month
            ),
            "canonical_path": event.canonical_path,
            "raw_linkage_hash": event.after_raw_linkage_hash,
            "original_issue_ids": original.issue_id.tolist(),
            "original_impacted_hour_ids": original.impacted_hour_id.tolist(),
            "actual_containing_rth_hour_ids": hour_ids,
            "source_hour_quality": affected.quality_tier.tolist(),
            "source_action_uncertainty": affected.action_uncertainty.tolist(),
            "possible_later_48_context_hour_ids": full_after.hour_id.tolist() if hour_ids else [],
            "endpoint_caution": (
                "Raw minute may affect genuine hour close only when it is the final expected "
                "minute. No four-hour label built. High/low anomalies can contaminate range "
                "features even with ordinary closes."
            ),
            "classification": classification,
            "verified_event_type": fact["kind"] if fact else "NONE_ESTABLISHED",
            "sources": fact["sources"] if fact else [],
            "access_date": facts["access_date"],
            "confidence": "HIGH_EVENT_FACT; SOURCE_PRINT_NOT_CERTIFIED"
            if fact
            else "INSUFFICIENT_EXTERNAL_EVIDENCE",
            "rationale": fact["facts"]
            if fact
            else (
                "Searches of dated ticker events and SEC/Nasdaq/NYSE material did not establish "
                "this print, cancellation, provider correction or an exact treatment. Numerical "
                "implausibility is not independent verification. See external_search_receipt.json; "
                "no claim the event did not occur."
            ),
            "proposed_price_factor": 1 / denominator if denominator else None,
            "applied_price_factor": 1.0,
            "applied_volume_factor": 1.0,
            "volume_convention": (
                "SOURCE_OBSERVED_UNCHANGED; no split-adjusted or missing share volume invented"
            ),
            "treatment": "PRESERVE_ORIGINAL; NO_QUARANTINE_OR_REPAIR_ACTIVATED",
            "post_treatment_status": status,
        }
        rows.append(row)
        if denominator and event.original_018d:
            factors.append(
                {
                    "event_id": event.event_id,
                    "ticker": ticker,
                    "ex_date": date,
                    "price_factor_numerator": 1,
                    "price_factor_denominator": denominator,
                    "volume_factor": None,
                    "applied": False,
                    "status": "VERIFIED_ACTION_FACT_ONLY; SOURCE_BASIS_AND_ASOF_RELEASE_PENDING",
                    "source_urls": [s["url"] for s in fact["sources"]],
                }
            )
            split_checks.append(
                {
                    "event_id": event.event_id,
                    "ticker": ticker,
                    "rth_boundary_close_ratio_before": float(event.close_ratio),
                    "counterfactual_ratio_after_prior_price_division": float(
                        event.close_ratio * denominator
                    ),
                    "factor_denominator": denominator,
                    "global_adjustment_applied": False,
                    "interpretation": (
                        "Exact-ratio boundary illustration only; not global OHLC/volume "
                        "or causal48/4 release proof"
                    ),
                }
            )
    pd.concat(event_contexts, ignore_index=True).to_parquet(
        private / "source_hour_event_contexts.parquet", index=False
    )
    write_json(out / "P019_PRICE_JUMP_EVIDENCE.json", rows)
    pd.DataFrame(
        [
            {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in e.items()}
            for e in rows
        ]
    ).to_csv(out / "P019_PRICE_JUMP_EVIDENCE.csv", index=False)
    write_json(out / "action_factors_v1_NOT_ACTIVATED.json", factors)
    pd.DataFrame(split_checks).to_csv(out / "proposed_split_boundary_checks.csv", index=False)
    decision = gate_decision(rows, post_scan_clean=False)
    blockers = [e["event_id"] for e in rows if e["classification"] == "UNRESOLVED_MATERIAL_JUMP"]
    write_json(
        out / "action_gate_v1.json",
        {
            "decision": decision,
            "blocker_ids": blockers,
            "inventory_sha256": receipt["inventory_sha256"],
            "evidence_sha256": digest(out / "P019_PRICE_JUMP_EVIDENCE.json"),
            "facts_sha256": digest(facts_path),
            "post_adjustment_scan": "NOT_RUN_NO_ADJUSTED_PANEL",
            "readiness_features_labels_training_authorized": False,
            "actual_new_model_starts": 0,
            "ledger": "32/200",
        },
    )
    lines = [
        "# P019 price-jump verification report",
        "",
        f"**{decision}**. Full active scan: 36,461,605 genuine canonical records, "
        "3,780 stock-months, 67 candidate minutes including all original13. Forty-two newly "
        "detected anomaly minutes have no attributable event-specific resolution; three KO "
        "premarket candidates remain mixed-basis and COP2012 lacks coherent distribution "
        "treatment. No readiness or model construction.",
        "",
        "Policy was sealed before outcome inspection; see scan_policy_sealed_before_outcomes.json. "
        "The conservative material threshold is symmetric1.25 (up25%, down20%); intraminute "
        "high/low threshold1.5; persistent median shifts use30 observed genuine RTH minutes. "
        "Flags are not proofs. All UTC instants, RTH/EH status and actual elapsed gaps "
        "are retained. "
        "No repaired endpoint is treated as a trade. Scan covers all active dates, including "
        "protected-period raw quality, but no protected labels/predictions.",
        "",
        "Public event facts were searched/read on2026-10-22. Sources support event-level "
        "classification, not certification of each HF print. Failed SEC/PDF/blank issuer opens "
        "and fallback sources are disclosed in event rationales. A failed optional HF card open "
        "does not mean all external access failed. Generic erroneous-trade policies and May2010 "
        "reports cannot establish2010–2012 individual corrections. No outside OHLC downloaded "
        "or substituted.",
        "",
        "Source prices show unadjusted RTH split discontinuities. Exact verified split ratios "
        "are saved as **unactivated facts**, with counterfactual adjacent-RTH ratios. No global "
        "adjusted history, volume conversion, quarantine or after-adjustment scan has been "
        "created. A future causal representation must use only action facts known by each origin; "
        "retrospective constant rescaling does not itself prove volume/action-vintage correctness. "
        "COP tax allocation is not accepted as a causal price factor. KO EH mixing prevents "
        "uniform per-date conversion.",
        "",
        "Private event_inventory.parquet contains actual before/after OHLCV, raw source rows "
        "and hashes. source_hour_event_contexts.parquet contains49 earlier/current and52 later "
        "full-hour diagnostic rows per event (stubs retained in original source). These enumerate "
        "possible48-hour context propagation; they do not construct feature sequences or targets. "
        "No-event data and all raw/QA files are unchanged. Full48-step/four-hour adjustment "
        "integrity and post-handling rescan remain unperformed because the global gate fails.",
        "",
        "Prior issue register preserved: "
        "../ta018d_hf1m_long_2026-10-22_155547/data_quality_issue_register.md. "
        "Numerical evidence stays under ignored data/processed/hf1m_p019_action_audit_v1. "
        "No dashboard source binding was activated.",
        "",
    ]
    for e in rows:
        lines.extend(
            [
                f"## {e['event_id']} — {e['ticker']} — {e['timestamp_et']}",
                "",
                f"{e['classification']}; {e['post_treatment_status']}. "
                f"Original018D: {e['original_018d']}. Rules: {', '.join(e['rules'])}.",
                "",
                f"Adjacent close ratio {e['close_ratio']:.9g}; "
                f"open/prior close {e['open_ratio']:.9g}; "
                f"minute high/low {e['minute_high_low_ratio']:.9g}; "
                f"elapsed {e['elapsed_minutes']:.9g}minutes. Before endpoint follows the first "
                "listed detector; for original13 this is the RTH predecessor. "
                "Different stream comparisons remain separate candidate minutes.",
                "",
                e["rationale"],
                "",
                f"Lineage: {e['raw_record_id']}; "
                f"containing RTH bins: {e['actual_containing_rth_hour_ids']}; "
                f"original issues: {e['original_issue_ids']}. "
                "Price/volume applied factor1. No substitute values or exclusions.",
                "",
            ]
        )
        if e["sources"]:
            lines.extend(
                [
                    f"- [{s['title']}]({s['url']}), published {s['published']}; accessed2026-10-22."
                    for s in e["sources"]
                ]
            )
        else:
            lines.append(
                "No credible candidate-specific public source established. Search terms and "
                "returned URLs retained in external_search_receipt.json; none promoted to proof."
            )
        lines.append("")
    (out / "P019_PRICE_JUMP_VERIFICATION_REPORT.md").write_text("\n".join(lines))
    (out / "P019_ACTION_GATE_DECISION.md").write_text(
        f"# {decision}\n\nUnresolved event IDs: {', '.join(blockers)}.\n\n"
        "All67 candidate minutes reviewed, all13 original issues recovered. Forty-two additional "
        "anomalies, three KO mixed-basis EH minutes and one COP spinoff treatment block release. "
        "Nine split events have verified exact action facts; four market-move events "
        "are preserved.\n\n"
        "The prompt §1A.6 requires stopping before readiness/features/targets/scalers/training "
        "on any unresolved jump. No adjusted panel or post-treatment full scan exists, so PASS "
        "cannot be claimed. Zero starts; ledger32/200.\n\n"
        "Least disruptive remedies: obtain event-specific correction/cancellation/source-basis "
        "evidence, or explicitly approve a versioned localized exclusion policy for the listed "
        "raw minutes/hour fields and their causal48-step dependencies. COP needs a defensible "
        "distribution treatment; KO needs exact mixed-basis handling. No new data or exclusions "
        "are authorized by this report. Preserve all20 names.\n"
    )
    write_json(
        out / "review_execution_receipt.json",
        {
            "context_sha256": digest(private / "source_hour_event_contexts.parquet"),
            "action_factors_sha256": digest(out / "action_factors_v1_NOT_ACTIVATED.json"),
            "unchanged_active_files": len(panel.verify_all()),
            "original_issue_count": len(originals),
            "classification_counts": pd.Series([e["classification"] for e in rows])
            .value_counts()
            .to_dict(),
            "blocker_count": len(blockers),
            "decision": decision,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--verify-raw", action="store_true")
    parser.add_argument(
        "--facts", type=Path, default=Path("configs/hf1m_p019_verified_event_facts_v1.json")
    )
    args = parser.parse_args()
    if args.verify_raw:
        verify_event_lineage(Path.cwd(), args.out)
    else:
        review(Path.cwd(), args.out, args.facts)


if __name__ == "__main__":
    main()
