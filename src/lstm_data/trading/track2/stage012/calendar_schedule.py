"""Reuse audited S4 XNYS arithmetic; execution events denote minute starts."""
from datetime import datetime, timedelta
import pandas as pd
from lstm_data.hf20_s4_clock import sessions, endpoint
from .contracts import Observation, utc


class MarketClock:
    def __init__(self, start: str, stop: str):
        self.calendar = sessions(start, stop)
        self.id = 'XNYS:exchange_calendars:minute-start:[open,close)'

    def origins(self, day: str) -> tuple[datetime, ...]:
        rows = self.calendar.loc[day:day]
        if rows.empty:
            return ()
        opened, closed = rows.iloc[0][['open', 'close']]
        return tuple((opened + pd.Timedelta(hours=k)).to_pydatetime() for k in range(7)
                     if opened + pd.Timedelta(hours=k) < closed)

    def endpoint(self, origin: datetime) -> datetime:
        stamp = pd.Timestamp(utc(origin))
        if not isinstance(stamp, pd.Timestamp):
            raise ValueError('INVALID_ORIGIN')
        return endpoint(stamp, self.calendar).to_pydatetime()

    def next_observation(self, submission: datetime) -> datetime:
        """Strictly subsequent minute START; execution price remains unknown."""
        t = pd.Timestamp(utc(submission)).floor('min') + pd.Timedelta(minutes=1)
        for opened, closed in self.calendar[['open', 'close']].itertuples(index=False, name=None):
            candidate = max(t, opened)
            if candidate < closed:
                result = candidate.to_pydatetime()
                if not isinstance(result, datetime):
                    raise ValueError('INVALID_CALENDAR_OBSERVATION')
                return result
        raise ValueError('CALENDAR_EXHAUSTED')

    def full_hour_slots(self, origin: datetime) -> tuple[datetime, ...]:
        slots = []
        for opened, closed in self.calendar[['open', 'close']].itertuples(index=False, name=None):
            for k in range(1, 7):
                t = opened + pd.Timedelta(hours=k)
                if t <= closed and t <= pd.Timestamp(origin):
                    slots.append(t.to_pydatetime())
        if len(slots) < 48:
            raise ValueError('INSUFFICIENT_SCHEDULE_HISTORY')
        return tuple(slots[-48:])


def availability(origin: datetime, fields: tuple[Observation, ...], delay: int = 2,
                 feature_seconds: float = 0, inference_seconds: float = 0
                 ) -> tuple[datetime, datetime, datetime]:
    if delay not in (1, 2, 5) or min(feature_seconds, inference_seconds) < 0 or not fields:
        raise ValueError('INVALID_LATENCY_OR_DEPENDENCIES')
    receipt = max(utc(origin) + timedelta(minutes=delay), *(utc(o.available_at) for o in fields))
    ready = receipt + timedelta(seconds=feature_seconds)
    return receipt, ready, ready + timedelta(seconds=inference_seconds)
