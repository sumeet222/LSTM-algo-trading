"""V3 action/due/carry bridge around unchanged V2 causal fill/accounting engine.

Historical funded replay remains release-gated before loader or output creation.
This module is exercised financially only with fabricated tapes in this session.
"""

from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable

from ...stage012.calendar_schedule import MarketClock
from ..common import D
from ..completion_v2.engine import ReplayEngine, ReplayEvent
from ..completion_v2.release import VerifiedRelease
from ..completion_v2.settlement import V2Book, carry_to, split_order_units
from .book_bridge import apply_action
from .event_ledger import sha
from .tapes import ET, TapeEvent


class EconomicReplayV3(ReplayEngine):
    def __init__(
        self,
        account: str,
        arm: str,
        book: V2Book,
        clock: MarketClock,
        release: VerifiedRelease | None = None,
    ):
        super().__init__(account, arm, book, clock)
        self.release = release
        self.action_receipts: list[dict] = []

    def advance_carry(self, through: datetime) -> None:
        if self.last_processed is None:
            return
        next_day = self.last_processed.astimezone(ET).date() + timedelta(days=1)
        while True:
            boundary = datetime.combine(next_day, time.min, ET).astimezone(timezone.utc)
            if boundary > through:
                break
            for position in sorted(self.book.positions, key=lambda p: p.ticker):
                if (
                    position.quantity < 0
                    and position.borrow_asof
                    and position.borrow_asof < boundary
                ):
                    self.book = carry_to(
                        self.book,
                        position.ticker,
                        boundary,
                        self.rates.get(position.ticker, D(".02")),
                        boundary,
                        f"V3_DUE_CARRY:{position.ticker}:{boundary.isoformat()}",
                    )
            next_day += timedelta(days=1)

    def replay(self, events: tuple[ReplayEvent | TapeEvent, ...]) -> None:
        ordered = sorted(
            events,
            key=lambda e: (
                e.available_at if isinstance(e, TapeEvent) else e.available,
                e.priority,
                e.event_id,
            ),
        )
        for event in ordered:
            received = event.available_at if isinstance(event, TapeEvent) else event.available
            if self.last_processed and received < self.last_processed:
                raise ValueError("V3_RECEIPT_REORDER_REPLAY_REQUIRED")
            self.advance_carry(received)
            if isinstance(event, ReplayEvent):
                super().process((event,))
                continue
            if event.action is None:
                if event.kind != "CARRY_DUE":
                    raise ValueError("MISSING_ACTION_RECORD")
                self.last_processed = received
                continue
            if event.source_hash != sha(event.action.record()):
                raise ValueError("ACTION_CONTENT_HASH_MISMATCH")
            self.book = apply_action(self.book, event, received, self.release)
            if (
                event.kind == "SPLIT"
                and event.action.split_ratio_new_old
                and event.action.event_id in self.book.action_keys
            ):
                for key, pending in tuple(self.pending.items()):
                    if pending.ticker == event.symbol:
                        self.pending[key] = split_order_units(
                            pending,
                            event.action.split_ratio_new_old,
                            event.effective_at,
                            event.available_at,
                        )
            self.action_receipts.append(
                {
                    "event_id": event.event_id,
                    "source_hash": event.source_hash,
                    "truth": event.truth,
                    "availability_rule": event.simulation_availability_rule,
                    "effective_at": event.effective_at,
                    "received_at": received,
                    "book_hash": self.book.digest(),
                    "unpriced_asset_claims": [
                        {
                            "lot_id": lot.cohort.cohort_id,
                            "asset": "OGN_UNPRICED",
                            "signed_quantity": str(lot.quantity / D(10)),
                            "truth": event.truth,
                            "valuation": "HOLD_NO_VALUE_CIL_UNKNOWN",
                        }
                        for lot in self.book.lots
                        if event.kind == "SPINOFF"
                        and event.action.sub_type == "OGN_PER_MRK_0.1"
                        and lot.cohort.ticker == "MRK"
                        and lot.quantity
                    ],
                }
            )
            self.last_processed = received


def historical_entry_v3(
    gate: Path,
    binding: dict,
    public_key: Path,
    signature: Path,
    output: Path,
    loader: Callable[
        [VerifiedRelease], tuple[EconomicReplayV3, tuple[ReplayEvent | TapeEvent, ...]]
    ],
) -> None:
    """Refuse before *any* loader, mkdir, historical ledger or financial artifact."""
    import json

    from .release import verify_v3

    release = verify_v3(gate, binding, public_key, signature)
    engine, events = loader(release)
    if engine.release != release:
        raise PermissionError("EXACT_V3_ENGINE_RELEASE_REQUIRED")
    # V2 price/settlement guards remain intact. A type flag cannot admit real bars.
    from ..completion_v2.engine import ReleasedBar

    if any(
        isinstance(e, ReplayEvent)
        and e.bar is not None
        and (not isinstance(e.bar, ReleasedBar) or e.bar.release != release)
        for e in events
    ):
        raise PermissionError("V3_REAL_BAR_RELEASE_BINDING_REQUIRED")
    engine.replay(events)
    if output.exists():
        raise ValueError("APPEND_ONLY_RELEASED_FINANCIAL_OUTPUT")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(engine.snapshot(), default=str, indent=2) + "\n")
