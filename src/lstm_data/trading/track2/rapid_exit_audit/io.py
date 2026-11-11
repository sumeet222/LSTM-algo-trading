"""Validated table and immutable-record boundaries for the offline audit."""

import csv
import json
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd


def json_at(path: Path) -> dict:
    return json.loads(path.read_text())


def csv_at(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def table(value: object) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise ValueError("EXPECTED_FRAME")
    return value


def column(frame: pd.DataFrame, name: str) -> pd.Series:
    value = frame[name]
    if not isinstance(value, pd.Series):
        raise ValueError("AMBIGUOUS_COLUMN " + name)
    return value


def near(actual: Decimal, expected: Decimal, label: str) -> None:
    if (
        not actual.is_finite()
        or not expected.is_finite()
        or abs(actual - expected) > Decimal("1e-7")
    ):
        raise ValueError(label + " " + str(actual) + " vs " + str(expected))


def drawdown(nav: pd.Series, dates: pd.Series, initial: float) -> dict:
    wealth = np.r_[initial, nav.to_numpy(float)]
    labels = ["INITIAL", *map(str, dates)]
    high = np.maximum.accumulate(wealth)
    dd = wealth / high - 1
    trough = int(np.argmin(dd))
    peak = int(np.flatnonzero(wealth[: trough + 1] == high[trough])[-1])
    recovery = np.flatnonzero(wealth[trough + 1 :] >= wealth[peak])
    best, start, end, streak = 0, 0, 0, 0
    for n, x in enumerate(dd):
        streak = streak + 1 if x < 0 else 0
        if streak > best:
            best, start, end = streak, n - streak + 1, n
    return {
        "max_drawdown": float(dd[trough]),
        "dd_peak": labels[peak],
        "dd_trough": labels[trough],
        "dd_recovery": labels[trough + 1 + int(recovery[0])] if recovery.size else "UNRECOVERED",
        "underwater_sessions": best,
        "underwater_first": labels[start],
        "underwater_last": labels[end],
    }


def as_rows(frame: pd.DataFrame) -> list[SimpleNamespace]:
    if not all(isinstance(k, str) for k in frame.columns):
        raise ValueError("NON_STRING_COLUMN")
    return [SimpleNamespace(**{str(k): v for k, v in r.items()}) for r in frame.to_dict("records")]


def decimal_scalar(encoded: object) -> Decimal:
    if isinstance(encoded, dict) and set(encoded) == {"decimal"}:
        value = Decimal(encoded["decimal"])
        if value.is_finite():
            return value
    raise ValueError("INVALID_DECIMAL_SNAPSHOT")
