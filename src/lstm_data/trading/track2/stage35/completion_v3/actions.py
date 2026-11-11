"""Typed evidence-preserving corporate actions, no market forecast/price reads."""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import date
from decimal import Decimal
from enum import Enum

D = Decimal


class Truth(str, Enum):
    VERIFIED_MULTI_SOURCE = "VERIFIED_MULTI_SOURCE"
    VERIFIED_PRIMARY = "VERIFIED_PRIMARY"
    OBSERVED_UNCORROBORATED = "OBSERVED_UNCORROBORATED"
    ASSUMED_ORDINARY = "ASSUMED_ORDINARY"
    ASSUMED_YIELD_PROXY = "ASSUMED_YIELD_PROXY"
    CONFLICTED_HOLD = "CONFLICTED_HOLD"
    SPECIAL_ACTION_HOLD = "SPECIAL_ACTION_HOLD"
    NO_EVENT_VERIFIED = "NO_EVENT_VERIFIED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Evidence:
    source_id: str
    endpoint: str
    payload_sha256: str
    locator: str
    retrieved_at: str
    priority: int = 30
    published_date: str | None = None


@dataclass(frozen=True)
class Action:
    event_id: str
    symbol: str
    action_type: str
    ex_date: date | None
    record_date: date | None
    payable_date: date | None
    amount: Decimal | None
    status: Truth
    sources: tuple[Evidence, ...]
    security_id: str = ""
    sub_type: str = ""
    special: bool = False
    declared_at: date | None = None
    publication_available_at_or_unknown: str | None = None
    effective_date: date | None = None
    currency: str = "USD"
    split_ratio_new_old: Decimal | None = None
    spinoff_distribution_terms: str = ""
    disagreements: tuple[str, ...] = ()
    proof_of_no_dividend_if_asserted: str = ""
    inferred_fields: tuple[str, ...] = ()
    assumption_rule_id: str = ""
    assumption_params: tuple[tuple[str, str], ...] = ()
    confidence: str = "OBSERVED_NOT_PIT_CERTIFIED"
    accrual_rule: str = "SIGNED_SHARES_HELD_IMMEDIATELY_BEFORE_EX_DATE"
    economic_basis: str = "RAW_COMMON_SHARE"
    effect_on_books: str = "EX_ACCRUAL_PAY_CASH_ONCE"
    source_replay_receipt: str = "RETROSPECTIVE_COLLECTION;SIMULATED_AVAILABILITY_MUST_BE_SEPARATE"

    def validate(self) -> None:
        if self.sub_type == "OGN_PER_MRK_0.1" and self.symbol != "MRK":
            raise ValueError("ISSUER_SECURITY_MISMATCH")
        if (
            any(s.source_id.startswith("APPLE_ISSUER:") for s in self.sources)
            and self.symbol != "AAPL"
        ):
            raise ValueError("ISSUER_SECURITY_MISMATCH")
        if not self.event_id or not self.symbol or self.currency != "USD":
            raise ValueError("ACTION_ID_SECURITY_OR_CURRENCY")
        if self.amount is not None and (not self.amount.is_finite() or self.amount < 0):
            raise ValueError("INVALID_DISTRIBUTION_AMOUNT")
        if self.action_type == "CASH_DIVIDEND" and self.economic_basis != "RAW_COMMON_SHARE":
            raise ValueError("DIVIDEND_UNIT_CONVERSION_REQUIRED")
        if (
            self.action_type == "CASH_DIVIDEND"
            and not self.special
            and self.payable_date
            and self.ex_date
            and self.payable_date < self.ex_date
        ):
            raise ValueError("PAY_BEFORE_EX_REQUIRES_SPECIAL_REVIEW")
        if (
            self.status in (Truth.VERIFIED_PRIMARY, Truth.VERIFIED_MULTI_SOURCE)
            and self.inferred_fields
        ):
            raise ValueError("INFERRED_FIELD_CANNOT_BE_VERIFIED")
        if self.status == Truth.NO_EVENT_VERIFIED and not self.proof_of_no_dividend_if_asserted:
            raise ValueError("EMPTY_FEED_IS_NOT_ZERO_PROOF")

    def record(self) -> dict:
        value = asdict(self)
        value["status"] = self.status.value
        for key in ("ex_date", "record_date", "payable_date", "declared_at", "effective_date"):
            at = value[key]
            value[key] = at.isoformat() if at else None
        value["amount_per_share_raw_basis"] = str(self.amount) if self.amount is not None else None
        value.pop("amount")
        value["split_ratio_new_old"] = (
            str(self.split_ratio_new_old) if self.split_ratio_new_old is not None else None
        )
        value["source_refs"] = value.pop("sources")
        value["original_payload_sha256"] = [s.payload_sha256 for s in self.sources]
        return value


def identifier(symbol: str, kind: str, anchor: date | None, amount: Decimal | None) -> str:
    number = str(amount.quantize(D(".00000001"))) if amount is not None else ""
    text = f"{symbol}|{kind}|{anchor}|{number}"
    return "CA3:" + hashlib.sha256(text.encode()).hexdigest()[:24]


def parse_date(value: object) -> date | None:
    if value in (None, "", "N/A", "--"):
        return None
    text = str(value)
    if "/" in text:
        month, day, year = text.split("/")
        return date(int(year), int(month), int(day))
    return date.fromisoformat(text[:10])


def normalize_alpaca(
    payload: dict, source: Evidence, symbols: tuple[str, ...]
) -> tuple[Action, ...]:
    output = []
    for family, rows in payload.get("corporate_actions", {}).items():
        if not isinstance(rows, list):
            raise ValueError("PROVIDER_SCHEMA_CHANGED")
        for n, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError("PROVIDER_RECORD_SCHEMA")
            symbol = str(row.get("symbol", ""))
            sub = ""
            effect = "EX_ACCRUAL_PAY_CASH_ONCE"
            if not symbol and row.get("acquirer_symbol") in symbols:
                symbol = str(row["acquirer_symbol"])
                sub = "ACQUIRER_INFORMATION_ONLY:" + str(row.get("acquiree_symbol", "UNKNOWN"))
                effect = "NO_DIRECT_COMMON_HOLDER_ENTITLEMENT"
            if symbol not in symbols:
                continue
            ex = parse_date(row.get("ex_date"))
            effective = parse_date(row.get("effective_date")) or ex
            anchor = effective or parse_date(row.get("process_date"))
            if anchor is None or not date(2020, 1, 1) <= anchor <= date(2024, 12, 31):
                continue
            evidence = replace(source, locator=f"corporate_actions.{family}[{n}]")
            rate = (
                D(str(row["rate"]))
                if "rate" in row and not sub.startswith("ACQUIRER_INFORMATION_ONLY")
                else None
            )
            status = Truth.OBSERVED_UNCORROBORATED
            kind = (
                "CASH_DIVIDEND"
                if family == "cash_dividends"
                else "SPLIT"
                if family in ("forward_splits", "reverse_splits")
                else family.upper()
            )
            special = bool(row.get("special", False))
            ratio = D(str(row["new_rate"])) / D(str(row["old_rate"])) if kind == "SPLIT" else None
            if kind == "CASH_DIVIDEND" and "special" not in row:
                status = Truth.SPECIAL_ACTION_HOLD
                sub = "CLASSIFICATION_MISSING"
            if special:
                status = Truth.SPECIAL_ACTION_HOLD
            if kind not in ("CASH_DIVIDEND", "SPLIT") and not sub.startswith(
                "ACQUIRER_INFORMATION_ONLY"
            ):
                status = Truth.SPECIAL_ACTION_HOLD
            action = Action(
                identifier(symbol, kind, ex or anchor, rate),
                symbol,
                kind,
                ex,
                parse_date(row.get("record_date")),
                parse_date(row.get("payable_date")),
                rate,
                status,
                (evidence,),
                security_id=str(row.get("cusip") or row.get("acquirer_cusip") or ""),
                sub_type=sub,
                special=special,
                declared_at=parse_date(row.get("declaration_date")),
                effective_date=effective,
                split_ratio_new_old=ratio,
                effect_on_books=effect,
            )
            action.validate()
            output.append(action)
    return tuple(output)


def normalize_nasdaq(payload: dict, source: Evidence, symbol: str) -> tuple[Action, ...]:
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("dividends"), dict):
        raise ValueError("NASDAQ_SCHEMA_OR_EMPTY_RESPONSE")
    rows = data["dividends"].get("rows")
    if rows is None:
        return ()  # NOT a no-dividend assertion
    result = []
    for n, row in enumerate(rows):
        ex = parse_date(row.get("exOrEffDate"))
        if ex is None or not date(2020, 1, 1) <= ex <= date(2024, 12, 31):
            continue
        amount = D(str(row["amount"]).replace("$", "").replace(",", ""))
        kind = "CASH_DIVIDEND"
        result.append(
            Action(
                identifier(symbol, kind, ex, amount),
                symbol,
                kind,
                ex,
                parse_date(row.get("recordDate")),
                parse_date(row.get("paymentDate")),
                amount,
                Truth.OBSERVED_UNCORROBORATED,
                (replace(source, locator=f"data.dividends.rows[{n}]"),),
                declared_at=parse_date(row.get("declarationDate")),
                effective_date=ex,
                sub_type="EXCHANGE_FEED_CASH",
                currency=str(row.get("currency") or "USD"),
            )
        )
    return tuple(result)


def reconcile(
    events: tuple[Action, ...], tolerance: Decimal = D(".00000001")
) -> tuple[Action, ...]:
    """Deduplicate repeats, do not pool conflicts or merge distinct COP cash series."""
    grouped: dict[tuple, list[Action]] = {}
    for event in events:
        event.validate()
        if event.inferred_fields or event.status in (
            Truth.ASSUMED_ORDINARY,
            Truth.ASSUMED_YIELD_PROXY,
        ):
            raise ValueError("OBSERVED_RECONCILIATION_BEFORE_FALLBACK")
        # Record-date anchors catch disagreement in ex dates without using a price.
        key = (
            event.symbol,
            event.action_type,
            event.record_date or event.ex_date or event.effective_date,
            str(event.amount.quantize(tolerance)) if event.amount is not None else event.sub_type,
        )
        grouped.setdefault(key, []).append(event)
    amounts: dict[tuple, dict[str, set[Decimal]]] = {}
    for event in events:
        if event.amount is None:
            continue
        anchor = (event.symbol, event.action_type, event.record_date or event.ex_date)
        for source in event.sources:
            amounts.setdefault(anchor, {}).setdefault(source.source_id.split(":")[0], set()).add(
                event.amount
            )
    disputed = {
        key
        for key, families in amounts.items()
        if len(families) > 1
        and all(len(v) == 1 for v in families.values())
        and len(set.union(*families.values())) > 1
    }
    output = []
    for rows in grouped.values():
        ordered = sorted(rows, key=lambda row: (min(s.priority for s in row.sources), row.event_id))
        first = ordered[0]
        sources = tuple(
            sorted(
                set(s for row in ordered for s in row.sources),
                key=lambda s: (s.priority, s.source_id, s.locator),
            )
        )
        conflicts = []
        if (first.symbol, first.action_type, first.record_date or first.ex_date) in disputed:
            conflicts.append("amount_per_share:cross_source_disagreement")
        for field in ("ex_date", "payable_date", "record_date", "split_ratio_new_old"):
            known = {getattr(row, field) for row in ordered if getattr(row, field) is not None}
            if len(known) > 1:
                conflicts.append(field + ":" + ",".join(sorted(str(v) for v in known)))
        # Two provider IDs alone are not independent; repeated pages keep one source.
        source_families = {s.source_id.split(":")[0] for s in sources}
        status = Truth.CONFLICTED_HOLD if conflicts else first.status
        if not conflicts and status == Truth.OBSERVED_UNCORROBORATED and len(source_families) >= 2:
            status = Truth.VERIFIED_MULTI_SOURCE
        fields = {}
        for field in ("ex_date", "payable_date", "record_date", "declared_at"):
            fields[field] = next(
                (getattr(row, field) for row in ordered if getattr(row, field) is not None), None
            )
        output.append(
            replace(first, sources=sources, status=status, disagreements=tuple(conflicts), **fields)
        )
    return tuple(
        sorted(
            output,
            key=lambda row: (
                row.effective_date or row.ex_date or date.min,
                row.symbol,
                row.event_id,
            ),
        )
    )


def canonical_hash(events: tuple[Action, ...]) -> str:
    return hashlib.sha256(
        json.dumps([e.record() for e in events], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
