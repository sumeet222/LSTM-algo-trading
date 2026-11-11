"""One deterministic reconciliation pass over sealed, cached action responses.

No network, market prices, forecast values, economic performance or label reads.
Provider absence is never proof of nonpayment. Source truth survives every export.
"""

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from html import unescape
from pathlib import Path

from ...stage012.model_registry import SYMBOLS
from .acquire import ROOT, classify, write_once
from .actions import (
    Action,
    Evidence,
    Truth,
    canonical_hash,
    identifier,
    normalize_alpaca,
    normalize_nasdaq,
    reconcile,
)

D = Decimal


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cached(root: Path, key: str, family: str, priority: int = 30) -> tuple[dict, Evidence]:
    receipt = json.loads((root / f"audits/{key}.receipt.json").read_text())
    path = Path(receipt["payload_path"])
    if digest(path) != receipt["stored_payload_sha256"] or receipt["http_status"] != 200:
        raise ValueError("CACHED_SOURCE_HASH_OR_HTTP:" + key)
    return json.loads(path.read_text()), Evidence(
        family + ":" + key,
        receipt["endpoint"],
        receipt["original_payload_sha256"],
        "",
        receipt["retrieval_utc"],
        priority,
    )


def plain(payload: dict) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", payload["non_json_body"])))


def issuer_apple(payload: dict, source: Evidence) -> tuple[Action, ...]:
    """Issuer explicitly reports contemporaneous, non-split-adjusted cash amounts."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", payload["non_json_body"], re.S | re.I)
    events = []
    for index, row in enumerate(rows):
        fields = {
            key: unescape(re.sub(r"<[^>]*>", "", value)).strip()
            for key, value in re.findall(
                r'<td[^>]*data-heading="([^"]+)"[^>]*>(.*?)</td>', row, re.S
            )
        }
        if not fields or fields.get("Type") != "Regular Cash":
            continue

        def day(key: str) -> date:
            text = re.sub(r"\s*,\s*", ", ", fields[key]).strip()
            try:
                return datetime.strptime(text, "%B %d, %Y").date()
            except ValueError:
                return datetime.strptime(text, "%b %d, %Y").date()

        record = day("Record")
        if not date(2020, 1, 1) <= record <= date(2024, 12, 31):
            continue
        amount = D(fields["Amount"].replace("$", ""))
        events.append(
            Action(
                identifier("AAPL", "CASH_DIVIDEND", record, amount),
                "AAPL",
                "CASH_DIVIDEND",
                None,
                record,
                day("Payable"),
                amount,
                Truth.VERIFIED_PRIMARY,
                (replace(source, locator=f"Regular Cash table row {index}"),),
                declared_at=day("Declared"),
                sub_type="ISSUER_REGULAR_CASH_NO_EXDATE",
            )
        )
    if len(events) != 20:
        raise ValueError("APPLE_HISTORY_SCHEMA_OR_COVERAGE_CHANGED")
    return tuple(events)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    content = "".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows)
    if path.exists() and path.read_text() != content:
        raise ValueError("IMMUTABLE_JSONL:" + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content) if not path.exists() else None


def build(root: Path = ROOT) -> tuple[Action, ...]:
    events: list[Action] = []
    for key in ("network_v2_alpaca_0", "boundary_alpaca_2025pay"):
        data, evidence = cached(root, key, "ALPACA")
        events.extend(normalize_alpaca(data, evidence, SYMBOLS))
    data, evidence = cached(root, "network_v2_nasdaq_probe", "NASDAQ", 20)
    events.extend(normalize_nasdaq(data, evidence, "AAPL"))
    data, evidence = cached(root, "boundary_apple_history", "APPLE_ISSUER", 1)
    events.extend(issuer_apple(data, evidence))
    original_path = Path("configs/hf1m_p019_verified_event_facts_v1.json")
    original = json.loads(original_path.read_text())
    original_digest = digest(original_path)
    # Cross-check only original splits, never infer new actions from prices.
    for n, fact in enumerate(original["events"]):
        if fact["date"] > "2024-12-31" or fact["kind"] != "SPLIT":
            continue
        at = date.fromisoformat(fact["date"])
        fact_source = Evidence(
            "ORIGINAL_FACTS:" + fact["ticker"],
            fact["sources"][0]["url"],
            original_digest,
            f"events[{n}]",
            "2026-10-22",
            5,
        )
        matches = [
            e
            for e in events
            if e.symbol == fact["ticker"] and e.action_type == "SPLIT" and e.ex_date == at
        ]
        if matches:
            for event in matches:
                if event.split_ratio_new_old != D(str(fact["factor_denominator"])):
                    raise ValueError("ORIGINAL_SPLIT_RATIO_CONFLICT")
                events.remove(event)
                events.append(
                    replace(
                        event,
                        status=Truth.VERIFIED_MULTI_SOURCE,
                        sources=event.sources + (fact_source,),
                    )
                )
        else:
            events.append(
                Action(
                    identifier(fact["ticker"], "SPLIT", at, None),
                    fact["ticker"],
                    "SPLIT",
                    at,
                    None,
                    None,
                    None,
                    Truth.VERIFIED_PRIMARY,
                    (fact_source,),
                    effective_date=at,
                    split_ratio_new_old=D(str(fact["factor_denominator"])),
                )
            )
    # Observed mandatory special economics: terms known, OGN valuation/CIL not supplied.
    data, evidence = cached(root, "extra_mrk_declaration", "MERCK_ISSUER", 1)
    text = plain(data)
    if "one-tenth" not in text or "May 17, 2021" not in text:
        raise ValueError("MERCK_TERMS_NOT_IN_SOURCE")
    data2, evidence2 = cached(root, "boundary_mrk_completion", "MERCK_COMPLETION", 1)
    if "June 3, 2021" not in plain(data2):
        raise ValueError("MERCK_COMPLETION_DATE_NOT_IN_SOURCE")
    events.append(
        Action(
            identifier("MRK", "SPINOFF", date(2021, 6, 3), None),
            "MRK",
            "SPINOFF",
            date(2021, 6, 3),
            date(2021, 5, 17),
            date(2021, 6, 2),
            None,
            Truth.SPECIAL_ACTION_HOLD,
            (evidence, evidence2),
            special=True,
            declared_at=date(2021, 5, 7),
            effective_date=date(2021, 6, 3),
            sub_type="OGN_PER_MRK_0.1",
            spinoff_distribution_terms="1 OGN per 10 MRK; fractional cash terms/value unresolved",
            confidence="TERMS_PRIMARY_VALUE_UNRESOLVED",
            effect_on_books="SIGNED_OGN_ASSET_CLAIM;NO_INVENTED_VALUE_OR_CIL",
        )
    )
    # Voluntary exchange: existing common shares receive nothing without election.
    data, evidence = cached(root, "jnj_alternate_exchange", "JNJ_ISSUER", 1)
    if "exchange offer" not in plain(data).lower():
        raise ValueError("JNJ_EXCHANGE_SOURCE")
    events.append(
        Action(
            identifier("JNJ", "VOLUNTARY_EXCHANGE", date(2023, 7, 24), None),
            "JNJ",
            "VOLUNTARY_EXCHANGE",
            None,
            None,
            None,
            None,
            Truth.VERIFIED_PRIMARY,
            (evidence,),
            effective_date=date(2023, 7, 24),
            sub_type="KENVUE_OPTIONAL_NO_ELECTION_SCENARIO",
            effect_on_books="NO_VOLUNTARY_ELECTION;NOT_MANDATORY_DISTRIBUTION",
        )
    )
    zero_evidence: dict[str, tuple[Evidence, ...]] = {}
    data, evidence = cached(root, "primary_tsla_policy", "TESLA_SEC", 1)
    if "We have never declared or paid cash dividends on our common stock" not in plain(data):
        raise ValueError("TESLA_NONPAYER_ASSERTION_MISSING")
    zero_evidence["TSLA"] = (evidence,)
    data, evidence = cached(root, "primary_ba_policy", "BOEING_SEC_2024", 1)
    data2, evidence2 = cached(root, "corrected_primary_ba_2022", "BOEING_SEC_2022", 1)
    if "did not pay any dividends to common shareholders in 2024, 2023 and 2022" not in plain(data):
        raise ValueError("BOEING_2024_NONPAYMENT_ASSERTION_MISSING")
    if "did not pay any dividends in 2022 and 2021" not in plain(data2):
        raise ValueError("BOEING_2021_NONPAYMENT_ASSERTION_MISSING")
    zero_evidence["BA"] = (evidence, evidence2)
    coverage = []
    assumptions = []
    for symbol in SYMBOLS:
        for year in range(2021, 2025):
            dividends = [
                e
                for e in events
                if e.symbol == symbol
                and e.action_type == "CASH_DIVIDEND"
                and e.ex_date
                and e.ex_date.year == year
            ]
            if symbol in zero_evidence:
                status = Truth.NO_EVENT_VERIFIED
                sources = zero_evidence[symbol]
                events.append(
                    Action(
                        identifier(symbol, "NO_CASH_DIVIDEND", date(year, 1, 1), D(0)),
                        symbol,
                        "NO_CASH_DIVIDEND",
                        None,
                        None,
                        None,
                        D(0),
                        status,
                        sources,
                        effective_date=date(year, 1, 1),
                        proof_of_no_dividend_if_asserted=(
                            f"SEC common-stock nonpayment covers {year}"
                        ),
                        effect_on_books="NO_ORDINARY_CASH_EVENT",
                    )
                )
            elif not dividends:
                status = Truth.UNKNOWN
                assumptions.append(
                    {
                        "symbol": symbol,
                        "year": year,
                        "rule_id": "F_STANDALONE_ONLY",
                        "type": "UNVERIFIED_DIVIDEND_YIELD_PROXY",
                        "annual_rate": ".015",
                        "low": "0",
                        "high": ".03",
                        "status": "ASSUMED_YIELD_PROXY",
                        "not_a_cash_action": True,
                        "book_into_action_ledger": False,
                        "reason": (
                            "empty Alpaca; issuer/SEC evidence insufficient for verified zero"
                        ),
                        "overlap_policy": (
                            "suppress entire security/year if any supported "
                            "cash event or verified zero"
                        ),
                        "affected_interval": [f"{year}-01-01", f"{year}-12-31"],
                        "source_attempts": ["ALPACA", "issuer FAQ", "FY2024 SEC"],
                        "exposure_amount": "NOT_COMPUTED;NO_HISTORICAL_PORTFOLIO",
                    }
                )
            else:
                status = Truth.OBSERVED_UNCORROBORATED
            coverage.append(
                {
                    "symbol": symbol,
                    "year": year,
                    "coverage_status": status.value,
                    "provider_cash_records": len(dividends),
                    "completeness": "NOT_CERTIFIED;CADENCE_IS_A_DIAGNOSTIC",
                    "special_action_scan": "BOUNDED_PRIMARY_PLUS_PROVIDER;NOT_EXHAUSTIVE_PIT",
                    "annual_raw_cash_sum": str(sum((e.amount or D(0) for e in dividends), D(0))),
                    "annual_sum_comparable_units": symbol != "AVGO" or year != 2024,
                }
            )
    merged = reconcile(tuple(events))
    # Original output IDs cannot depend on which provider row supplied an ex date.
    merged = tuple(
        replace(
            e,
            event_id=identifier(
                e.symbol, e.action_type, e.ex_date or e.effective_date or e.record_date, e.amount
            ),
        )
        for e in merged
    )
    for e in merged:
        e.validate()
    oos = tuple(
        e
        for e in merged
        if date(2021, 1, 1)
        <= (e.ex_date or e.effective_date or e.record_date or date.min)
        <= date(2024, 12, 31)
    )
    prefix = tuple(
        e
        for e in merged
        if (e.ex_date or e.effective_date or e.record_date or date.max) < date(2021, 1, 1)
    )
    # Coverage must use reconciled events, never the sum of provider duplicates.
    for item in coverage:
        unique = [
            e
            for e in oos
            if e.symbol == item["symbol"]
            and e.action_type == "CASH_DIVIDEND"
            and e.ex_date
            and e.ex_date.year == item["year"]
        ]
        item["provider_cash_records"] = len(unique)
        item["annual_raw_cash_sum"] = str(sum((e.amount or D(0) for e in unique), D(0)))
        item["event_status_counts"] = dict(Counter(e.status.value for e in unique))
    # Unknown publication time is an assumption, not an inferred factual announcement.
    for event in oos:
        if event.action_type not in ("CASH_DIVIDEND", "SPLIT"):
            continue
        assumptions.append(
            {
                "event_id": event.event_id,
                "symbol": event.symbol,
                "rule_id": "RETROSPECTIVE_DATE_ONLY_EVENT_AVAILABILITY",
                "inferred_fields": ["simulated_available_at"],
                "actual_publication_receipt": event.publication_available_at_or_unknown,
                "actual_source_collection": [s.retrieved_at for s in event.sources],
                "simulation_rule": "effective day 00:00 America/New_York;strict PIT not certified",
                "truth_preserved": event.status.value,
                "severity": "CONDITIONAL_RETROSPECTIVE_STUDY",
                "source_refs": [s.source_id for s in event.sources],
            }
        )
    rows = [e.record() for e in oos]
    write_jsonl(root / "ACTION_PROVENANCE_V3.jsonl", rows)
    write_jsonl(root / "ACTION_PREFIX_PRE2021_V3.jsonl", [e.record() for e in prefix])
    write_jsonl(root / "ORDINARY_DIVIDEND_ASSUMPTIONS_V3.jsonl", assumptions)
    csv_path = root / "CORPORATE_ACTION_CANONICAL_V3.csv"
    if not csv_path.exists():
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: json.dumps(v, sort_keys=True)
                        if isinstance(v, (dict, list, tuple))
                        else v
                        for k, v in row.items()
                    }
                )
    write_once(
        root / "ACTION_COVERAGE_V3.json",
        {
            "ticker_years": coverage,
            "symbols": list(SYMBOLS),
            "ticker_year_count": len(coverage),
            "canonical_count": len(oos),
            "status_counts": dict(Counter(e.status.value for e in oos)),
            "type_counts": dict(Counter(e.action_type for e in oos)),
            "canonical_content_sha256": canonical_hash(oos),
            "prefix_count": len(prefix),
            "assumption_count": len(assumptions),
            "ordinary_field_imputations": 0,
            "yield_proxy_security_years": sum(
                a["rule_id"] == "F_STANDALONE_ONLY" for a in assumptions
            ),
            "post2024_pay_claims": [
                e.event_id for e in oos if e.payable_date and e.payable_date.year > 2024
            ],
            "payout_coverage_not_certified": True,
            "financial_performance_computed": False,
        },
    )
    reassessed = []
    for receipt_path in sorted((root / "audits").glob("*.receipt.json")):
        r = json.loads(receipt_path.read_text())
        if "payload_path" not in r:
            continue
        path = Path(r["payload_path"])
        payload = json.loads(path.read_text())
        new = classify(r["http_status"], payload)
        if r["status"] != new:
            reassessed.append(
                {
                    "receipt": str(receipt_path),
                    "old_status": r["status"],
                    "reassessed": new,
                    "reason": "HTML premium/apikey words are not provider error envelopes",
                }
            )
    write_once(root / "audits/PROVIDER_STATUS_REASSESSMENT_V3.json", reassessed)
    return oos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    build(args.root)
