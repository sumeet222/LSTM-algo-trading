"""Typed JSON checkpoints; only an explicit registry can be reconstructed.

No pickle/import-by-name or source-type relabeling. Checksums detect interruption
and byte drift; runtime admission and source hashes remain independently required.
"""

import gzip
import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

import numpy as np

from ..completion_v3.actions import Action, Evidence, Truth
from ..final_backtest_v4.special import Distribution, DistributionLot, OGNQuote
from .book import Account, Lot, Order, Request
from .paths import canonical
from .protocol import Scenario

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
    return {"schema": "HF20_V5_CHECKPOINT_1", "body": encoded, "sha256": canonical(encoded)}


def unseal(value: dict) -> object:
    if value.get("schema") != "HF20_V5_CHECKPOINT_1" or canonical(value["body"]) != value["sha256"]:
        raise ValueError("CHECKPOINT_CORRUPT")
    return decode(value["body"])


def write_checkpoint(path: Path, value: dict) -> None:
    """Lossless, deterministic, atomic daily state; retain every checkpoint."""
    packed = gzip.compress(
        json.dumps(value, sort_keys=True, default=str).encode(), compresslevel=3, mtime=0
    )
    if path.exists():
        if path.read_bytes() != packed:
            raise ValueError("IMMUTABLE_CHECKPOINT")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(packed)
    temporary.replace(path)


def read_checkpoint(path: Path) -> dict:
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    return json.loads(raw)
