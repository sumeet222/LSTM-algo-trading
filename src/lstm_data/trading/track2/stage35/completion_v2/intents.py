"""V2 price-free intents: expiry10, unchanged model horizon, delayed exit marker."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from ...stage012.calendar_schedule import MarketClock
from ...stage012.model_registry import SYMBOLS
from ..common import D
from ..intents import SignalIntent


def from_full_signal(row: pd.Series, arm: str, clock: MarketClock) -> SignalIntent:
    if arm not in ("EQUAL", "S2C_RISK", "ROLLING_RISK", "EWMA_RISK"):
        raise ValueError("UNKNOWN_ARM")
    origin = datetime.fromisoformat(pd.Timestamp(str(row["origin"])).isoformat())
    decision = datetime.fromisoformat(pd.Timestamp(str(row["issued_at"])).isoformat())
    endpoint = datetime.fromisoformat(pd.Timestamp(str(row["endpoint"])).isoformat())
    expected = json.loads(Path("trading/track2/stage012/original_bundles.json").read_text())[
        "bundles"
    ][str(origin.year)]["sha256"]
    if tuple(row[k] for k in ("checkpoint_hash", "recipe_hash", "c3_hash")) != tuple(expected[:3]):
        raise ValueError("ORIGINAL_BUNDLE_MISMATCH")
    g = D(str(row["g_" + arm]))
    direction = int(str(row["direction"]))
    if (
        not g.is_finite()
        or str(row["input_eligible"]) not in ("True", "true")
        or direction not in (-1, 1)
    ):
        raise ValueError("ARM_OR_SOURCE_ABSTENTION")
    if (
        not D(".5") <= g <= D("1.5")
        or decision < origin
        or str(row["ticker"]) not in SYMBOLS
        or origin not in clock.origins(str(origin.astimezone(ZoneInfo("America/New_York")).date()))
        or endpoint != clock.endpoint(origin)
    ):
        raise ValueError("SIZE_OR_ORIGIN_OR_ENDPOINT")
    marker = clock.next_observation(decision)
    expiry = origin + timedelta(minutes=10)
    if marker > expiry:
        raise ValueError("ENTRY_DEADLINE_UNREACHABLE")
    return SignalIntent(
        "|".join((str(row["checkpoint_hash"]), origin.isoformat(), str(row["ticker"]), arm)),
        str(row["ticker"]),
        arm,
        origin,
        decision,
        marker,
        expiry,
        endpoint,
        endpoint + timedelta(minutes=2),
        direction,
        g,
        str(row["checkpoint_hash"]),
        str(row["recipe_hash"]),
        str(row["c3_hash"]),
        str(row["risk_reference"]),
        str(row["source_hash"]) + ":" + str(row["input_hash"]),
        "TRACK2_STAGE35_COMPLETION_V2",
    )


def exit_marker(
    intent: SignalIntent, clock: MarketClock, latest_dependency: datetime | None = None
) -> datetime:
    decision = max(intent.exit_decision, latest_dependency or intent.exit_decision)
    return clock.next_observation(decision)
