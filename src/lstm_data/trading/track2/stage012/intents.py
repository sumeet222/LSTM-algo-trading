"""Pure candidate intent conversion; not a broker or a simulator."""
from dataclasses import dataclass
from datetime import datetime
from .contracts import SignalRecord
from .policy import FixedHorizonPolicy
from .cohort_state import Cohort


@dataclass(frozen=True)
class DirectionAndSizeIntent:
    cohort_id: str
    ticker: str
    direction: int
    signed_notional: float
    decision_at: datetime
    endpoint: datetime
    signal_json: str


def candidate(signal: SignalRecord, base_notional: float) -> DirectionAndSizeIntent:
    if (signal.eligibility_reason != 'READY_FOR_RISK_GATE' or signal.size_multiplier is None
            or not signal.input_validity or signal.direction == 0):
        raise ValueError('SIGNAL_NOT_READY')
    key = '|'.join((signal.model_id,signal.nominal_origin_utc.isoformat(),signal.ticker,signal.strategy_id))
    size = FixedHorizonPolicy().candidate_notional(signal.direction,base_notional,signal.size_multiplier)
    return DirectionAndSizeIntent(key, signal.ticker,signal.direction,size,signal.decision_utc,
                                  signal.nominal_endpoint_utc,signal.to_json())


def cohort_from_intent(intent: DirectionAndSizeIntent, quantity: float, origin: datetime,
                       deadline: datetime, execution_basis: str) -> Cohort:
    """Quantity conversion requires a later approved raw-price sizing policy."""
    if quantity * intent.direction <= 0 or deadline <= intent.decision_at:
        raise ValueError('INVALID_ENTRY_INTENT')
    return Cohort(intent.cohort_id,intent.ticker,quantity,abs(intent.signed_notional),origin,
                  intent.endpoint,deadline,execution_basis,(intent.signal_json,))
