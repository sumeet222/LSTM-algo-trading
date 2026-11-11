"""Typed JSON checkpoints; only an explicit registry can be reconstructed.

No pickle/import-by-name or source-type relabeling. Checksums detect interruption
and byte drift; runtime admission and source hashes remain independently required.
"""

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

import numpy as np

from ..completion_v3.actions import Action, Evidence, Truth
from .book import Account, Lot, Order, Request
from .paths import canonical
from .protocol import Scenario
from .special import Distribution, DistributionLot, OGNQuote

REGISTRY = {
    c.__name__: c
    for c in (
        Account,
        Lot,
        Order,
        Request,
        Scenario,
        Distribution,
        DistributionLot,
        OGNQuote,
        Action,
        Evidence,
    )
}


def encode(value: object) -> object:
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, datetime):
        return {"datetime": value.isoformat()}
    if isinstance(value, date):
        return {"date": value.isoformat()}
    if isinstance(value, Enum):
        if not isinstance(value, Truth):
            raise ValueError("UNKNOWN_CHECKPOINT_ENUM")
        return {"enum": "Truth", "value": value.value}
    if isinstance(value, np.ndarray):
        return {"array": value.tolist(), "dtype": str(value.dtype)}
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "class": type(value).__name__,
            "fields": {f.name: encode(getattr(value, f.name)) for f in fields(value)},
        }
    if isinstance(value, dict):
        return {"mapping": [[encode(k), encode(v)] for k, v in value.items()]}
    if isinstance(value, (list, tuple, set)):
        items = sorted(value, key=repr) if isinstance(value, set) else value
        return {"sequence": type(value).__name__, "items": [encode(v) for v in items]}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("UNSUPPORTED_CHECKPOINT_VALUE:" + type(value).__name__)


def decode(value: object) -> object:
    if not isinstance(value, dict):
        return value
    if "decimal" in value:
        return Decimal(value["decimal"])
    if "datetime" in value:
        return datetime.fromisoformat(value["datetime"])
    if "date" in value:
        return date.fromisoformat(value["date"])
    if "enum" in value:
        if value["enum"] != "Truth":
            raise ValueError("UNKNOWN_CHECKPOINT_ENUM")
        return Truth(value["value"])
    if "array" in value:
        return np.asarray(value["array"], dtype=value["dtype"])
    if "mapping" in value:
        return {decode(k): decode(v) for k, v in value["mapping"]}
    if "sequence" in value:
        items = [decode(v) for v in value["items"]]
        return {"list": list, "tuple": tuple, "set": set}[value["sequence"]](items)
    if value.get("class") in REGISTRY:
        cls = REGISTRY[value["class"]]
        supplied = value["fields"]
        required = {f.name for f in fields(cls)}
        if set(supplied) != required:
            raise ValueError("CHECKPOINT_FIELD_SCHEMA")
        result = object.__new__(cls)
        for key, encoded in supplied.items():
            object.__setattr__(result, key, decode(encoded))
        if isinstance(result, Action):
            result.validate()
        if isinstance(result, Distribution):
            result.validate()
        if isinstance(result, Account):
            result.reconcile()
        return result
    raise ValueError("UNKNOWN_CHECKPOINT_SCHEMA")


def seal(value: object) -> dict:
    encoded = encode(value)
    return {"schema": "HF20_V4_CHECKPOINT_1", "body": encoded, "sha256": canonical(encoded)}


def unseal(value: dict) -> object:
    if value.get("schema") != "HF20_V4_CHECKPOINT_1" or canonical(value["body"]) != value["sha256"]:
        raise ValueError("CHECKPOINT_CORRUPT")
    return decode(value["body"])
