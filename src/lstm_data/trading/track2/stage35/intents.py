"""Bridge frozen Stage012 signals into price-free strategy candidates."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from ..stage012.cohort_state import Cohort
from ..stage012.contracts import SignalRecord, utc
from ..stage012.model_registry import SYMBOLS


@dataclass(frozen=True)
class SignalIntent:
    cohort_id: str
    ticker: str
    arm: str
    origin: datetime
    decision: datetime
    earliest_entry: datetime
    entry_deadline: datetime
    endpoint: datetime
    exit_decision: datetime
    direction: int
    multiplier: Decimal
    model_hash: str
    recipe_hash: str
    c3_hash: str
    risk_reference_id: str
    source_lineage: str
    constraints_revision: str = "TRACK2_STAGE35_CANDIDATE_V1"

    def cohort(self, quantity: Decimal, budget: Decimal, execution_basis: str) -> Cohort:
        if quantity * self.direction <= 0:
            raise ValueError("INTENT_DIRECTION_MISMATCH")
        if Decimal(str(float(quantity))) != quantity:
            raise ValueError("LEGACY_COHORT_FLOAT_ROUNDTRIP_UNSAFE")
        return Cohort(
            self.cohort_id,
            self.ticker,
            float(quantity),
            float(budget),
            self.origin,
            self.endpoint,
            self.entry_deadline,
            execution_basis,
            (self.model_hash, self.recipe_hash, self.c3_hash, self.source_lineage),
        )


def from_signal(
    signal: SignalRecord, arm: str, multiplier: Decimal, risk_id: str, lineage: str
) -> SignalIntent:
    year = signal.nominal_origin_utc.astimezone(ZoneInfo("America/New_York")).year
    fold = f"F{year % 100}"
    registry = json.loads(Path("trading/track2/stage012/original_bundles.json").read_text())[
        "bundles"
    ]
    if (
        str(year) not in registry
        or signal.fold_id != fold
        or not signal.model_id.endswith("-" + fold)
    ):
        raise ValueError("FOLD_IDENTITY_MISMATCH")
    expected = registry[str(year)]["sha256"]
    if (signal.checkpoint_hash, signal.feature_recipe_id, signal.c3_calibration_id) != tuple(
        expected[:3]
    ):
        raise ValueError("ORIGINAL_MODEL_RECIPE_C3_MISMATCH")
    if (
        signal.ticker not in SYMBOLS
        or not signal.input_validity
        or not signal.direction
        or signal.calibrated_magnitude is None
    ):
        raise ValueError("SIGNAL_ABSTENTION")
    if signal.eligibility_reason != "READY_FOR_RISK_GATE" or not risk_id or not lineage:
        raise ValueError("RISK_OR_LINEAGE_UNAVAILABLE")
    if not Decimal(".5") <= multiplier <= Decimal("1.5"):
        raise ValueError("SIZE_CLIP")
    deadline = signal.nominal_origin_utc + timedelta(minutes=5)
    if utc(signal.earliest_executable_observation_utc) > utc(deadline):
        raise ValueError("ENTRY_DEADLINE_UNREACHABLE")
    key = "|".join(
        (signal.model_id, utc(signal.nominal_origin_utc).isoformat(), signal.ticker, arm)
    )
    return SignalIntent(
        key,
        signal.ticker,
        arm,
        signal.nominal_origin_utc,
        signal.decision_utc,
        signal.earliest_executable_observation_utc,
        deadline,
        signal.nominal_endpoint_utc,
        signal.nominal_endpoint_utc + timedelta(minutes=2),
        signal.direction,
        multiplier,
        signal.checkpoint_hash,
        signal.feature_recipe_id,
        signal.c3_calibration_id,
        risk_id,
        hashlib.sha256((signal.to_json() + lineage).encode()).hexdigest(),
    )


def signal_from_payload(payload: dict) -> SignalRecord:
    values = dict(payload)
    for name, field in SignalRecord.__dataclass_fields__.items():
        if field.type == datetime:
            values[name] = datetime.fromisoformat(values[name])
    for name in ("trend_reference_keys", "provenance_flags"):
        values[name] = tuple(values[name])
    return SignalRecord(**values)
