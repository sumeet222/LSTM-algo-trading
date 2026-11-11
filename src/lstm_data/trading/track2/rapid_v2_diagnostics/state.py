"""Content-bound snapshots of compact case state at committed session boundaries."""

import gzip
import json
from datetime import date, timedelta
from pathlib import Path

from ..rapid_v1.paths import canonical
from ..rapid_v1.state import decode, encode
from .book import Ledger

STATE = (
    "integrals",
    "last_prices",
    "known_closes",
    "known_marks",
    "known_volumes",
    "cursor",
    "special",
    "special_pending",
    "ogn_borrow_cursors",
    "done_due",
    "budgets",
    "paired_lots",
    "daily_rows",
    "account_holds",
    "days_completed",
    "last_completed",
    "last_market_end",
    "policy_counts",
)


def binding(engine) -> dict:
    return {
        "registry": engine.registry["identity"],
        "cache": engine.cache.manifest["identity"],
        "first": engine.first,
        "last": engine.last,
        "cases": list(engine.case_by_key),
        "variant_registry": engine.variant_registry,
    }


def snapshot(engine) -> dict:
    return {
        "binding": binding(engine),
        "state": encode({k: getattr(engine, k) for k in STATE}),
        "accounts": encode([vars(a) for a in engine.fast_accounts]),
    }


def checkpoint(path: Path, engine) -> None:
    body = snapshot(engine)
    data = gzip.compress(
        json.dumps({"body": body, "sha256": canonical(body)}, sort_keys=True).encode(),
        compresslevel=3,
        mtime=0,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("IMMUTABLE_CHECKPOINT")
        return
    tmp = path.with_suffix(".tmp")
    with tmp.open("xb") as stream:
        stream.write(data)
    tmp.replace(path)


def restore(path: Path, engine) -> None:
    envelope = json.loads(gzip.decompress(path.read_bytes()))
    body = envelope["body"]
    if envelope["sha256"] != canonical(body) or body["binding"] != binding(engine):
        raise ValueError("CHECKPOINT_CONTENT_OR_BINDING")
    state = decode(body["state"])
    accounts = decode(body["accounts"])
    if not isinstance(state, dict) or set(state) != set(STATE) or not isinstance(accounts, list):
        raise ValueError("CHECKPOINT_SCHEMA")
    if not state["last_completed"]:
        raise ValueError("CHECKPOINT_MISSING_COMMITTED_DAY")
    expected = list(engine.case_by_key)
    if [a["arm"] for a in accounts] != expected:
        raise ValueError("CHECKPOINT_CASE_AXIS")
    for k in STATE:
        setattr(engine, k, state[k])
    engine.fast_accounts = [Ledger(**a) for a in accounts]
    engine.accounts = list(engine.fast_accounts)
    for a in engine.fast_accounts:
        a.reconcile()
    if any(
        len(rows) != engine.days_completed or rows[-1]["date"] != engine.last_completed
        for rows in engine.daily_rows.values()
    ):
        raise ValueError("CHECKPOINT_NAV_FRONTIER")
    engine.market.first = (
        date.fromisoformat(engine.last_completed) + timedelta(days=1)
    ).isoformat()
    engine.risk_cache.clear()
