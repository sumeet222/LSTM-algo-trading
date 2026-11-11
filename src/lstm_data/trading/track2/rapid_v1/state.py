"""Lossless allowlisted annual/frontier state, never daily journal checkpoints."""

import gzip
import json
from collections import Counter
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import numpy as np

from ..stage35.final_backtest_v4.protocol import Scenario
from ..stage35.final_backtest_v5.special import Distribution, DistributionLot, OGNQuote
from .costs import CostReference
from .diagnostics import PendingOutcome, QualityBook
from .paths import canonical
from .portfolio import CompactStats, FastAccount, Lot, Order, Request
from .scheduler import EntryBudget
from .strategies import DirectionIntent

CLASSES = {
    c.__name__: c
    for c in (
        FastAccount,
        CompactStats,
        Lot,
        Order,
        Request,
        Scenario,
        CostReference,
        PendingOutcome,
        QualityBook,
        EntryBudget,
        DirectionIntent,
        Distribution,
        DistributionLot,
        OGNQuote,
    )
}
STATE_FIELDS = (
    "accounts",
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
    "quality",
    "daily_rows",
    "signal_rows",
    "account_holds",
    "days_completed",
    "last_completed",
    "last_market_end",
    "policy_counts",
)


def encode(value: object) -> object:
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, datetime):
        return {"datetime": value.isoformat()}
    if isinstance(value, date):
        return {"date": value.isoformat()}
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return {"array": value.tolist(), "dtype": str(value.dtype)}
    if is_dataclass(value) and not isinstance(value, type):
        if type(value).__name__ not in CLASSES:
            raise ValueError("UNREGISTERED_STATE_CLASS")
        return {
            "class": type(value).__name__,
            "fields": {f.name: encode(getattr(value, f.name)) for f in fields(value)},
        }
    if isinstance(value, Counter):
        return {"counter": [[encode(k), encode(v)] for k, v in value.items()]}
    if isinstance(value, dict):
        return {"mapping": [[encode(k), encode(v)] for k, v in value.items()]}
    if isinstance(value, (list, tuple, set)):
        items = sorted(value, key=repr) if isinstance(value, set) else value
        return {"sequence": type(value).__name__, "items": [encode(v) for v in items]}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("UNSUPPORTED_STATE:" + type(value).__name__)


def decode(value):
    if not isinstance(value, dict):
        return value
    if "decimal" in value:
        return Decimal(value["decimal"])
    if "datetime" in value:
        return datetime.fromisoformat(value["datetime"])
    if "date" in value:
        return date.fromisoformat(value["date"])
    if "array" in value:
        return np.asarray(value["array"], dtype=value["dtype"])
    if "counter" in value:
        counter: Counter = Counter()
        for key, count in value["counter"]:
            if not isinstance(count, int):
                raise ValueError("STATE_COUNTER_VALUE")
            counter[decode(key)] = count
        return counter
    if "mapping" in value:
        return {decode(k): decode(v) for k, v in value["mapping"]}
    if "sequence" in value:
        return {"list": list, "tuple": tuple, "set": set}[value["sequence"]](
            [decode(v) for v in value["items"]]
        )
    if value.get("class") in CLASSES:
        cls = CLASSES[value["class"]]
        if set(value["fields"]) != {f.name for f in fields(cls)}:
            raise ValueError("STATE_FIELD_SCHEMA")
        result = object.__new__(cls)
        for k, v in value["fields"].items():
            object.__setattr__(result, k, decode(v))
        if isinstance(result, (FastAccount, Distribution)):
            result.reconcile() if isinstance(result, FastAccount) else result.validate()
        return result
    raise ValueError("UNKNOWN_STATE_SCHEMA")


def write_state(path: Path, engine) -> None:
    body = {
        "registry": engine.registry["identity"],
        "cache": engine.cache.manifest["identity"],
        "first": engine.first,
        "last": engine.last,
        "state": encode({k: getattr(engine, k) for k in STATE_FIELDS}),
    }
    envelope = {"schema": "HF20_RAPID_STATE_1", "body": body, "sha256": canonical(body)}
    data = gzip.compress(json.dumps(envelope, sort_keys=True).encode(), compresslevel=3, mtime=0)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("IMMUTABLE_STATE")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def restore_state(path: Path, engine) -> None:
    value = json.loads(gzip.decompress(path.read_bytes()))
    if value["schema"] != "HF20_RAPID_STATE_1" or value["sha256"] != canonical(value["body"]):
        raise ValueError("STATE_CORRUPT")
    body = value["body"]
    if (body["registry"], body["cache"], body["first"], body["last"]) != (
        engine.registry["identity"],
        engine.cache.manifest["identity"],
        engine.first,
        engine.last,
    ):
        raise ValueError("STATE_BINDING")
    state = decode(body["state"])
    if not isinstance(state, dict) or set(state) != set(STATE_FIELDS):
        raise ValueError("STATE_SCHEMA")
    for k in STATE_FIELDS:
        setattr(engine, k, state[k])
    engine.fast_accounts = engine.accounts
    for a in engine.fast_accounts:
        a.reconcile()
        if a.initial != 100000:
            raise ValueError("STATE_CAPITAL_RESET")
    if engine.last_completed is None:
        raise ValueError("EMPTY_STATE_FRONTIER")
    if any(
        rows and rows[-1]["date"] != engine.last_completed for rows in engine.daily_rows.values()
    ):
        raise ValueError("STATE_DAY_CURSOR")
    next_day = (date.fromisoformat(engine.last_completed) + timedelta(days=1)).isoformat()
    engine.market.first = next_day
    engine.risk_cache.clear()
