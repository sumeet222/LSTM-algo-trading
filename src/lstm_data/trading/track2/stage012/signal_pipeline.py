"""Input-only issuance boundary; future scoreability is deliberately absent."""
from datetime import datetime
from zoneinfo import ZoneInfo
from .contracts import FeatureSnapshot, SignalRecord, TrendSignal
from .calendar_schedule import MarketClock, availability
from .model_registry import MagnitudeForecaster
from .risk_sizing import RiskReference


def issue(snapshot: FeatureSnapshot, forecaster: MagnitudeForecaster, sign: TrendSignal,
          clock: MarketClock, reference: RiskReference | None = None, delay: int = 2,
          inference_seconds: float = 0) -> SignalRecord:
    if snapshot.slots != clock.full_hour_slots(snapshot.nominal_origin):
        raise ValueError('MISSING_OR_COMPRESSED_SCHEDULED_SLOTS')
    if snapshot.nominal_origin not in clock.origins(str(snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).date())):
        raise ValueError('NOT_AN_ORIGIN')
    day = str(snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).date())
    closed = clock.calendar.loc[day:day].iloc[0]['close']
    if not isinstance(closed, datetime):
        raise ValueError('INVALID_CALENDAR_CLOSE')
    expected_category = 'INTRADAY' if clock.endpoint(snapshot.nominal_origin) <= closed else 'OVERNIGHT'
    if snapshot.category != expected_category:
        raise ValueError('CALENDAR_CATEGORY_MISMATCH')
    fields = snapshot.dependencies + sign.references
    receipt, ready, decision = availability(snapshot.nominal_origin, fields, delay,
                                             inference_seconds=inference_seconds)
    magnitude = forecaster.predict(snapshot) if snapshot.valid else None
    slot = snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')
    fold = f'F{forecaster.bundle.year % 100}'
    if reference and (reference.ticker, reference.fold, reference.slot) != (snapshot.ticker, fold, slot):
        raise ValueError('RISK_REFERENCE_KEY_MISMATCH')
    multiplier = reference.multiplier(magnitude, decision) if reference and magnitude is not None else None
    reason = ('INPUT_INELIGIBLE' if magnitude is None else 'NO_DIRECTION' if not sign.direction
              else 'RISK_REFERENCE_UNAVAILABLE' if multiplier is None else 'READY_FOR_RISK_GATE')
    b = forecaster.bundle
    return SignalRecord('track2-stage012-v1', 'HF20-fixed-survivors-v1', snapshot.ticker, fold,
                        f'S2C-CA-{fold}', b.identities[0], b.identities[1], b.identities[2],
                        snapshot.price_basis, clock.id, snapshot.nominal_origin,
                        snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).isoformat(),
                        max(o.interval_end for o in fields), ready, receipt, decision, decision,
                        decision, clock.next_observation(decision), clock.endpoint(snapshot.nominal_origin),
                        magnitude, tuple(o.key for o in sign.references), sign.alpha, sign.direction,
                        multiplier, '' if multiplier is not None else 'PREFIX_REFERENCE_NOT_PREPARED',
                        snapshot.valid, reason, f'ASSUMED_WALL_MINUTES_{delay}',
                        ('HISTORICAL_RECEIPT_UNMEASURED', 'RETROSPECTIVE_ACTION_QA', 'FIXED_SURVIVORS',
                         'SNAPSHOT_SUPPLIER_LINEAGE_REQUIRES_REVIEW'))
