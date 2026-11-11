"""Year-end compact V3 state and exactly-once restart."""

import gzip
import json
from datetime import date, timedelta
from pathlib import Path

from ..rapid_v1.paths import canonical
from ..rapid_v1.state import decode, encode
from ..rapid_v2_diagnostics.state import STATE, binding
from .book import DynamicLedger

FIELDS = (*STATE, "factor_history")


def snapshot(engine) -> dict:
    return {
        "binding": binding(engine),
        "legacy": engine.legacy,
        "state": encode({k: getattr(engine, k) for k in FIELDS}),
        "accounts": encode([vars(a) for a in engine.dynamic_accounts]),
    }


def checkpoint(path: Path, engine) -> None:
    b = snapshot(engine)
    data = gzip.compress(
        json.dumps({"body": b, "sha256": canonical(b)}, sort_keys=True).encode(),
        compresslevel=3,
        mtime=0,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("IMMUTABLE_V3_CHECKPOINT")
        return
    tmp = path.with_suffix(".tmp")
    with tmp.open("xb") as f:
        f.write(data)
    tmp.replace(path)


def restore(path: Path, engine) -> None:
    envelope = json.loads(gzip.decompress(path.read_bytes()))
    b = envelope["body"]
    if (
        canonical(b) != envelope["sha256"]
        or b["binding"] != binding(engine)
        or (b["legacy"] != engine.legacy)
    ):
        raise ValueError("V3_CHECKPOINT_BINDING")
    state, accounts = decode(b["state"]), decode(b["accounts"])
    if not isinstance(state, dict) or set(state) != set(FIELDS) or not isinstance(accounts, list):
        raise ValueError("V3_CHECKPOINT_SCHEMA")
    if not state["last_completed"] or [a["arm"] for a in accounts] != list(engine.case_by_key):
        raise ValueError("V3_CHECKPOINT_CENSUS")
    for k in FIELDS:
        setattr(engine, k, state[k])
    engine.dynamic_accounts = [DynamicLedger(**a) for a in accounts]
    engine.fast_accounts = list(engine.dynamic_accounts)
    engine.accounts = list(engine.dynamic_accounts)
    for a in engine.dynamic_accounts:
        a.reconcile()
    if any(
        len(r) != engine.days_completed or r[-1]["date"] != engine.last_completed
        for r in engine.daily_rows.values()
    ):
        raise ValueError("V3_CHECKPOINT_DAILY_FRONTIER")
    engine.market.first = (
        date.fromisoformat(engine.last_completed) + timedelta(days=1)
    ).isoformat()
    engine.risk_cache.clear()
