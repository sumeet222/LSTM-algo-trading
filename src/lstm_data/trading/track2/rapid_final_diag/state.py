"""Content-bound exactly-once session restart for the diagnostic ledger."""

import gzip
import json
from datetime import date, timedelta
from pathlib import Path

from ..rapid_v1.paths import canonical
from ..rapid_v1.state import decode
from ..rapid_v2_diagnostics.state import binding
from ..rapid_v3_dynamic.state import FIELDS, checkpoint, snapshot
from .book import DiagnosticLedger

__all__ = ["checkpoint", "snapshot", "restore"]


def restore(path: Path, engine) -> None:
    envelope = json.loads(gzip.decompress(path.read_bytes()))
    b = envelope["body"]
    if (
        canonical(b) != envelope["sha256"]
        or b["binding"] != binding(engine)
        or b["legacy"] != engine.legacy
    ):
        raise ValueError("DIAGNOSTIC_CHECKPOINT_BINDING")
    state, accounts = decode(b["state"]), decode(b["accounts"])
    if not isinstance(state, dict) or set(state) != set(FIELDS) or not isinstance(accounts, list):
        raise ValueError("DIAGNOSTIC_CHECKPOINT_SCHEMA")
    if not state["last_completed"] or [a["arm"] for a in accounts] != list(engine.case_by_key):
        raise ValueError("DIAGNOSTIC_CHECKPOINT_CENSUS")
    for k in FIELDS:
        setattr(engine, k, state[k])
    engine.dynamic_accounts = [DiagnosticLedger(**a) for a in accounts]
    engine.fast_accounts = list(engine.dynamic_accounts)
    engine.accounts = list(engine.dynamic_accounts)
    for a in engine.dynamic_accounts:
        a.reconcile()
    if any(
        len(r) != engine.days_completed or r[-1]["date"] != engine.last_completed
        for r in engine.daily_rows.values()
    ):
        raise ValueError("DIAGNOSTIC_DAILY_FRONTIER")
    engine.market.first = (
        date.fromisoformat(engine.last_completed) + timedelta(days=1)
    ).isoformat()
    engine.risk_cache.clear()
