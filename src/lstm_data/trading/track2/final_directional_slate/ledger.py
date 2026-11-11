"""Compact captures around unchanged V2 fixed and V3 dynamic accounting."""

from dataclasses import dataclass, field

from ..rapid_final_diag.book import DiagnosticLedger
from ..rapid_v2_diagnostics.book import Ledger


@dataclass
class DynamicLedger(DiagnosticLedger):
    def record(self, kind: str, at: int, **fields) -> None:
        super().record(kind, at, **fields)
        if kind == "OGN_EXTERNAL_DISPOSAL" and self.stats.physical_rows:
            self.physical_records.append({"case": self.arm, **self.stats.physical_rows[-1]})


@dataclass
class FixedLedger(Ledger):
    completed_records: list[dict] = field(default_factory=list)
    physical_records: list[dict] = field(default_factory=list)
    exit_tape: list[dict] = field(default_factory=list)

    def record(self, kind: str, at: int, **fields) -> None:
        super().record(kind, at, **fields)
        if (kind == "FILL" and fields["external"]) or kind == "OGN_EXTERNAL_DISPOSAL":
            self.physical_records.append({"case": self.arm, **self.stats.physical_rows[-1]})

    def aggregate_trade(self, row: dict, date: str, rth_index) -> None:
        role, causes = self.exit_notes.get(row["key"], ("OPEN", ()))
        forced = row["key"] in self.any_forced
        cause = (
            (
                "RISK_NAME_CAP"
                if "NAME_CAP" in causes
                else "RISK_VINTAGE_CAP"
                if "VINTAGE_CAP" in causes
                else "RISK_OTHER_CAP"
            )
            if forced
            else "FIXED_T480"
        )
        self.completed_records.append(
            {
                **row,
                "case": self.arm,
                "date": date,
                "cause": cause,
                "triggers": "|".join(causes),
                "scheduled_minutes": rth_index(row["exit_at"]) - rth_index(row["entry_at"])
                if row["entry_at"] is not None and row["exit_at"] is not None
                else None,
                "final_role": role,
            }
        )
        super().aggregate_trade(row, date, rth_index)
