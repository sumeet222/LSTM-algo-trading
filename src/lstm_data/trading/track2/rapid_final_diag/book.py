"""Compact captures before the tested ledger discards completed attribution rows."""

from dataclasses import dataclass, field

from ..rapid_v3_dynamic.book import DynamicLedger, cap_causes


@dataclass
class DiagnosticLedger(DynamicLedger):
    completed_records: list[dict] = field(default_factory=list)
    physical_records: list[dict] = field(default_factory=list)
    entry_reserves: list[dict] = field(default_factory=list)
    monitor_totals: dict[str, int] = field(default_factory=dict)
    risk_samples: list[dict] = field(default_factory=list)

    def record(self, kind: str, at: int, **fields) -> None:
        super().record(kind, at, **fields)
        if kind == "FILL" and fields["external"]:
            row = self.stats.physical_rows[-1]
            self.physical_records.append({"case": self.arm, **row})
        if kind == "OBSERVED_MARKED_CAP_BREACH" and len(self.risk_samples) < 100:
            self.risk_samples.append(
                {
                    "at": at,
                    "NAV": self.nav(),
                    "gross": self.gross(),
                    "restricted": self.restricted(),
                    "cash": self.cash,
                    "causes": "|".join(cap_causes(self)),
                }
            )

    def aggregate_trade(self, row: dict, date: str, rth_index) -> None:
        detail = self.closing.get(row["key"], {})
        group = self.groups.get(self.group_of.get(row["key"], ""), {})
        if row["entry_at"] is not None:
            self.completed_records.append(
                {
                    **row,
                    "case": self.arm,
                    "date": date,
                    "cause": detail.get("primary"),
                    "triggers": "|".join(detail.get("triggers", ())),
                    "entry_strength": detail.get("entry_strength"),
                    "exit_strength": detail.get("aligned_exit_strength"),
                    "base": group.get("base"),
                    "trail_distance": group.get("trail_distance"),
                    "scheduled_minutes": rth_index(row["exit_at"]) - rth_index(row["entry_at"])
                    if row["exit_at"] is not None
                    else None,
                }
            )
            for key in ("deferred_checks", "recovered_checks", "missing_checks"):
                self.monitor_totals[key] = self.monitor_totals.get(key, 0) + group.get(key, 0)
        super().aggregate_trade(row, date, rth_index)
