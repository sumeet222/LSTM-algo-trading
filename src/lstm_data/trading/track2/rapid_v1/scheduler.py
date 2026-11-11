"""Online, calendar-only scan and physical entry-order budgets."""

from dataclasses import dataclass, field
from datetime import date

from ..stage012.calendar_schedule import MarketClock
from ..stage35.final_backtest_v4.market import minute


def weekly_scan_dates(clock: MarketClock) -> set[str]:
    seen: set[tuple[int, int]] = set()
    chosen: set[str] = set()
    for day, row in clock.calendar.iterrows():
        label = str(day)[:10]
        iso = date.fromisoformat(label).isocalendar()
        key = (iso.year, iso.week)
        if key in seen:
            continue
        if minute(row["close"]) - minute(row["open"]) == 390:
            chosen.add(label)
            seen.add(key)
    return chosen


@dataclass
class EntryBudget:
    mode: str
    counts: dict[str, int] = field(default_factory=dict)

    def key(self, session: str) -> str:
        if self.mode == "MICRO_PRO":
            return session
        iso = date.fromisoformat(session).isocalendar()
        return f"{iso.year}-W{iso.week:02d}"

    def remaining(self, session: str) -> int:
        return (6 if self.mode == "MICRO_PRO" else 5) - self.counts.get(self.key(session), 0)

    def reserve(self, session: str, physical_entry_orders: int) -> None:
        if physical_entry_orders < 0 or physical_entry_orders > self.remaining(session):
            raise ValueError("ENTRY_BUDGET_EXCEEDED")
        key = self.key(session)
        self.counts[key] = self.counts.get(key, 0) + physical_entry_orders
