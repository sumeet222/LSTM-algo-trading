"""Date-only conditional action tape; actual collection and simulation clocks differ."""

import json
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from .acquire import ROOT, write_once
from .actions import Action, Evidence, Truth
from .event_ledger import sha
from .inventory import digest

ET = ZoneInfo("America/New_York")


def midnight(day: date) -> datetime:
    return datetime.combine(day, time.min, ET).astimezone(timezone.utc)


def load_actions(root: Path = ROOT) -> tuple[Action, ...]:
    result = []
    for line in (root / "ACTION_PROVENANCE_V3.jsonl").read_text().splitlines():
        row = json.loads(line)

        def day(key: str) -> date | None:
            return date.fromisoformat(row[key]) if row[key] else None

        result.append(
            Action(
                row["event_id"],
                row["symbol"],
                row["action_type"],
                day("ex_date"),
                day("record_date"),
                day("payable_date"),
                Decimal(row["amount_per_share_raw_basis"])
                if row["amount_per_share_raw_basis"] is not None
                else None,
                Truth(row["status"]),
                tuple(Evidence(**s) for s in row["source_refs"]),
                security_id=row["security_id"],
                sub_type=row["sub_type"],
                special=row["special"],
                declared_at=day("declared_at"),
                publication_available_at_or_unknown=row["publication_available_at_or_unknown"],
                effective_date=day("effective_date"),
                currency=row["currency"],
                split_ratio_new_old=Decimal(row["split_ratio_new_old"])
                if row["split_ratio_new_old"] is not None
                else None,
                spinoff_distribution_terms=row["spinoff_distribution_terms"],
                disagreements=tuple(row["disagreements"]),
                proof_of_no_dividend_if_asserted=row["proof_of_no_dividend_if_asserted"],
                inferred_fields=tuple(row["inferred_fields"]),
                assumption_rule_id=row["assumption_rule_id"],
                assumption_params=tuple(tuple(v) for v in row["assumption_params"]),
                confidence=row["confidence"],
                accrual_rule=row["accrual_rule"],
                economic_basis=row["economic_basis"],
                effect_on_books=row["effect_on_books"],
                source_replay_receipt=row["source_replay_receipt"],
            )
        )
    for event in result:
        event.validate()
    if len({event.event_id for event in result}) != len(result):
        raise ValueError("DUPLICATE_CANONICAL_EVENT_IDS")
    return tuple(result)


@dataclass(frozen=True)
class TapeEvent:
    event_id: str
    symbol: str
    kind: str
    effective_at: datetime
    available_at: datetime
    priority: int
    action: Action | None
    source_hash: str
    truth: str
    simulation_availability_rule: str = "RETROSPECTIVE_DATE_ONLY_NOT_PIT"


def compile_events(
    actions: tuple[Action, ...], start: date, end: date, active_carry_symbols: tuple[str, ...] = ()
) -> tuple[TapeEvent, ...]:
    result = []
    for event in actions:
        day = event.ex_date or event.effective_date
        if day is None or event.action_type == "NO_CASH_DIVIDEND":
            continue
        source_hash = sha(event.record())
        if start <= day <= end:
            effective = midnight(day)
            result.append(
                TapeEvent(
                    event.event_id + ":EFFECTIVE",
                    event.symbol,
                    event.action_type,
                    effective,
                    effective,
                    0 if event.action_type == "SPLIT" else 1,
                    event,
                    source_hash,
                    event.status.value,
                )
            )
        if event.action_type == "CASH_DIVIDEND" and event.payable_date:
            if start <= event.payable_date <= end:
                at = midnight(event.payable_date)
                result.append(
                    TapeEvent(
                        event.event_id + ":PAY",
                        event.symbol,
                        "CASH_SETTLEMENT",
                        at,
                        at,
                        2,
                        event,
                        source_hash,
                        event.status.value,
                    )
                )
    day = start
    while day <= end:
        for symbol in sorted(set(active_carry_symbols)):
            at = midnight(day)
            result.append(
                TapeEvent(
                    f"CARRY_DUE:{symbol}:{day}",
                    symbol,
                    "CARRY_DUE",
                    at,
                    at,
                    -1,
                    None,
                    "CONDITIONAL_2PCT_ACT365",
                    "CONDITIONAL_ACADEMIC_SHORT",
                )
            )
        day += timedelta(days=1)
    return tuple(sorted(result, key=lambda e: (e.available_at, e.priority, e.event_id)))


def daily_batches(
    events: tuple[TapeEvent, ...], after_id: str | None = None
) -> Iterator[tuple[TapeEvent, ...]]:
    ids = [e.event_id for e in events]
    if after_id is not None and after_id not in ids:
        raise ValueError("RESUME_CURSOR_NOT_IN_BOUND_TAPE")
    start = ids.index(after_id) + 1 if after_id is not None else 0
    batch = []
    previous = None
    for event in events[start:]:
        day = event.available_at.astimezone(ET).date()
        if previous is not None and day != previous:
            yield tuple(batch)
            batch = []
        batch.append(event)
        previous = day
    if batch:
        yield tuple(batch)


def checkpoint(path: Path, event: TapeEvent, binding: dict, state_hash: str) -> None:
    write_once(
        path,
        {
            "cursor": event.event_id,
            "available_at": event.available_at.isoformat(),
            "binding": binding,
            "state_hash": state_hash,
        },
    )


def manifest(root: Path = ROOT) -> None:
    actions = load_actions(root)
    events = compile_events(actions, date(2021, 1, 1), date(2025, 3, 31))
    path = root / "ACTION_AND_DUE_TAPE_V3.jsonl"
    from .inventory import write_jsonl

    write_jsonl(
        path,
        [
            {**asdict(event), "action": event.action.record() if event.action else None}
            for event in events
        ],
    )
    write_once(
        root / "HISTORICAL_ACTION_AND_CARRY_TAPE_MANIFEST_V3.json",
        {
            "events": len(events),
            "action_inventory_sha256": digest(root / "ACTION_PROVENANCE_V3.jsonl"),
            "tape_sha256": digest(path),
            "payment_events_past2024": sum(
                event.kind == "CASH_SETTLEMENT" and event.effective_at.year > 2024
                for event in events
            ),
            "prices_past2024": False,
            "carry_policy": (
                "automatic active physical shorts only;ACT365;known prior mark and rate required"
            ),
            "carry_without_active_accounts": "NOT_INSTANTIATED_NO_PORTFOLIO",
            "actual_publication_receipts": "UNKNOWN;not replaced by modeled availability",
            "readiness": "ENGINEERING_CONDITIONAL;MRK_OGN_UNPRICED_HOLD",
            "financial_booking": False,
        },
    )


if __name__ == "__main__":
    manifest()
