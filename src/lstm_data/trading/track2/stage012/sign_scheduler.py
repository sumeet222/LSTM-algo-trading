"""Signal-only session orchestration; first-decision abstention is frozen too."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import hashlib
import json
from .contracts import Observation, TrendSignal, SignalRecord, utc
from .calendar_schedule import MarketClock, availability
from .trend_direction import trend
from .historical_input_only import OriginalInputOnlySnapshotProducer, Abstention, CausalFeatureAudit, BASIS
from .model_registry import MagnitudeForecaster, SYMBOLS
from .signal_pipeline import issue
from .risk_sizing import RiskReference


@dataclass(frozen=True)
class FrozenSessionSign:
    ticker: str
    session: str
    first_decision_utc: datetime
    calendar_id: str
    sign: TrendSignal
    lineage_hash: str


class SessionSignScheduler:
    def __init__(self, clock: MarketClock):
        self.clock=clock
        self.cache: dict[tuple[str,str],FrozenSessionSign]={}

    def freeze(self,ticker: str,day: str,first_decision: datetime,
               references: dict[str,tuple[float,Observation]],basis: str) -> FrozenSessionSign:
        key=(ticker,day)
        if key in self.cache:
            frozen=self.cache[key]
            if utc(first_decision)<frozen.first_decision_utc:
                raise ValueError('SIGN_CACHE_TIME_REVERSAL')
            return frozen
        if str(first_decision.astimezone(ZoneInfo('America/New_York')).date())!=day or not self.clock.origins(day):
            raise ValueError('SIGN_SESSION_MISMATCH')
        prior=tuple(str(d.date()) for d in self.clock.calendar.loc[:day].index if str(d.date())<day)[-6:]
        sign=trend(prior,references,first_decision,basis)
        payload={'ticker':ticker,'day':day,'first_decision':utc(first_decision).isoformat(),'basis':basis,
                 'references':[(o.key,o.available_at.isoformat()) for o in sign.references],'alpha':sign.alpha,'reason':sign.reason}
        result=FrozenSessionSign(ticker,day,utc(first_decision),self.clock.id,sign,hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest())
        self.cache[key]=result
        return result

    def reject_revision(self, replacement: FrozenSessionSign) -> None:
        previous=self.cache.get((replacement.ticker,replacement.session))
        if previous is not None and previous!=replacement:
            raise ValueError('SESSION_SIGN_IMMUTABLE')


def historical_references(producer: OriginalInputOnlySnapshotProducer,ticker: str,day: str,
                          delay: int=2) -> dict[str,tuple[float,Observation]]:
    refs={}
    for d in producer.clock.calendar.loc[:day].index:
        date=str(d.date())
        if date>=day:
            continue
        t=datetime.fromisoformat(date+'T15:30').replace(tzinfo=ZoneInfo('America/New_York'))
        if t not in producer.clock.origins(date):
            continue
        # Hourly genuine close at15:30, NOT proxy/stub. Producer source is already adjusted.
        rows=producer.hours.loc[(producer.hours.ticker==ticker)&(producer.hours.hour_end_utc==t)&~producer.hours.is_stub]
        if len(rows)==1:
            value=float(rows.iloc[0]['close'])
            refs[date]=(value,Observation(f'{ticker}:{date}:genuine1530',t,t,t+timedelta(minutes=delay),BASIS))
    return refs


def scheduled_signal(producer: OriginalInputOnlySnapshotProducer, forecaster: MagnitudeForecaster,
                     scheduler: SessionSignScheduler,ticker: str,origin: datetime,
                     reference: RiskReference | None=None,delay: int=2
                     ) -> tuple[SignalRecord,CausalFeatureAudit,FrozenSessionSign] | Abstention:
    result=producer.produce(forecaster.bundle,ticker,origin,delay)
    if isinstance(result,Abstention):
        return result
    snapshot,audit=result
    _,_,decision=availability(origin,snapshot.dependencies,delay)
    if decision>origin+timedelta(minutes=5):
        return Abstention(ticker,utc(origin).isoformat(),'DECISION_AFTER_ENTRY_DEADLINE')
    day=str(origin.astimezone(ZoneInfo('America/New_York')).date())
    frozen=scheduler.freeze(ticker,day,decision,historical_references(producer,ticker,day,delay),snapshot.price_basis)
    record=issue(snapshot,forecaster,frozen.sign,producer.clock,reference,delay)
    return record,audit,frozen


def session_opportunities(clock: MarketClock,day: str) -> tuple[tuple[str,datetime],...]:
    """All140 normal/80 half-day fixed-universe keys, before any input gate."""
    return tuple((ticker,origin) for origin in clock.origins(day) for ticker in SYMBOLS)
