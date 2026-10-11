"""Bounded process-date SPY metadata inspection; no certified absence or vintage claim."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .alpaca import DataAccessError, credentials
from .config import digest
from .market_source import (
    ACTION_ENDPOINT,
    ACTION_FOLLOWUP_PARAMS,
    ACTION_PARAMS,
    AttemptBudget,
    MarketSource,
)
from .spy_completion import (
    ReplayTransport,
    storage_guard,
    verify_historical_journal,
    write_bounded_report,
)


def inspect_actions(
    source: MarketSource, report: Path, env_file: Path | None, *, late_process: bool = False,
) -> dict:
    """At most two pages, three sends per page globally; incomplete scope remains HOLD."""
    if source.config.get("acquisition_policy_version") != 3:
        raise ValueError("SPY_ACTION_INSPECTION_REQUIRES_APPROVED_V3")
    if env_file:
        load_dotenv(env_file, override=False)
    key, secret = credentials()
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "SPY003_ACTIONS", 900,
                           tuple(source.partitions()))
    query = ACTION_FOLLOWUP_PARAMS if late_process else ACTION_PARAMS
    result: dict = {"status": "HOLD_UNVERIFIED_SCOPE", "params": query,
                    "endpoint": ACTION_ENDPOINT, "process_date_filter_not_effective_date": True,
                    "source_version": source.config["source_version"],
                    "raw_price_basis": "Unadjusted prices include distribution effects; "
                        "no cash/total return leg",
                    "certified_no_splits": False, "publication_verified": False,
                    "issuer_evidence": {
                        "quarterly_distributions": "https://www.ssga.com/us/en/intermediary/etfs/"
                            "state-street-spdr-sp-500-etf-trust-spy",
                        "historical_sample": "https://www.ssga.com/library-content/announcements/"
                            "etfs/au/20200320-SPY-Distribution-Announcement.pdf",
                        "sample_ex_date": "2020-03-20", "sample_rate_usd": 1.405559,
                        "sample_us_pay_date": "2020-04-30",
                        "scope": "Sample only, no exhaustive split or distribution certification"},
                    "provider_reference": "https://docs.alpaca.markets/us/reference/corporateactions-1",
                    "records": [], "pages": [], "exhausted": False}
    lock = source.store / ".acquire.lock"
    with lock.open("x"):
        pass
    try:
        verify_historical_journal(source, budget)
        budget.before_write = lambda size: storage_guard(source, report, size)
        transport = ReplayTransport(budget, budget.used, diagnostic=False)
        start = budget.used
        token = None
        seen = set()
        for _ in range(2):
            params = query | ({"page_token": token} if token else {})
            response = transport.get(ACTION_ENDPOINT, params=params,
                headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret},
                timeout=30, allow_redirects=False)
            result["pages"].append({"status": response.status_code,
                                    "response_bytes": len(response.content)})
            if response.status_code != 200:
                result["reason"] = f"METADATA_HTTP_{response.status_code}_NO_FALLBACK"
                break
            payload = response.json()
            actions = payload.get("corporate_actions")
            if not isinstance(actions, dict):
                raise DataAccessError("SPY_ACTION_RESPONSE_SCHEMA_MISMATCH")
            for kind, rows in actions.items():
                if not isinstance(rows, list):
                    raise DataAccessError("SPY_ACTION_LIST_REQUIRED")
                for row in rows:
                    if not isinstance(row, dict) or row.get("symbol") != "SPY":
                        raise DataAccessError("SPY_ACTION_SYMBOL_MISMATCH")
                    fields = ("id", "symbol", "process_date", "ex_date", "record_date",
                              "payable_date", "old_rate", "new_rate", "rate", "cash", "status")
                    result["records"].append({"type": kind}
                                             | {k: row[k] for k in fields if k in row})
            token = payload.get("next_page_token")
            if not token:
                result["exhausted"] = True
                break
            if token in seen:
                raise DataAccessError("SPY_ACTION_CONTINUATION_CYCLE")
            seen.add(token)
        result["new_metadata_attempts"] = budget.used - start
        result["transport_attempts"] = budget.used
        result["journal_sha256"] = digest(budget.journal)
        result["reason"] = result.get("reason", "CURRENT_PROCESS_DATE_METADATA_IS_NOT_"
                                      "COMPLETE_HISTORICAL_ACTION_SCOPE_OR_PUBLICATION")
        return result
    finally:
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_market_spy_v3.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--late-process", action="store_true",
                        help="Bounded July 2025 process-date follow-up for June 2025 ex-dates")
    args = parser.parse_args()
    source = MarketSource.load(args.config)
    result = inspect_actions(source, args.report, args.env_file,
                             late_process=args.late_process)
    filename = ("corporate_action_followup.json" if args.late_process
                else "corporate_action_scope.json")
    write_bounded_report(source, args.report, args.report / filename, result)
    print({"status": result["status"], "records": len(result["records"]),
           "metadata_attempts": result["new_metadata_attempts"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
