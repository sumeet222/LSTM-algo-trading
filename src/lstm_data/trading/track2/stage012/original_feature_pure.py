"""Source-only extraction of original day-locked M2 and scheduled hourly grid.

No evaluation arrays are accepted. Historical endpoint ratios are feature ingredients
only after their own observation completion+2min precedes the INPUT DAY open.
"""
from datetime import datetime, timedelta
import math
from functools import lru_cache
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from lstm_data.hf1m_ft16_math import rolling
from .calendar_schedule import MarketClock


@lru_cache(maxsize=32768)
def cached_origins(clock: MarketClock, day: str) -> tuple[datetime,...]:
    return clock.origins(day)


@lru_cache(maxsize=32768)
def cached_endpoint(clock: MarketClock, origin: datetime) -> datetime:
    return clock.endpoint(origin)


def source_ratio(opened: datetime, ended: datetime, ticker: str,
                 observations: dict[tuple[str, datetime, str], float], day_open: datetime) -> float:
    """Original open anchor versus preceding-minute close, strictly matured."""
    if ended + timedelta(minutes=2) >= day_open:
        return float('nan')
    if ticker == 'COP' and (opened.date() < datetime(2012,5,1).date()) != (ended.date() < datetime(2012,5,1).date()):
        return float('nan')
    local = opened.astimezone(ZoneInfo('America/New_York'))
    field, at = ('open',opened) if local.strftime('%H:%M') == '09:30' else ('close',opened-timedelta(minutes=1))
    a = observations.get((ticker,at,field),float('nan'))
    b = observations.get((ticker,ended-timedelta(minutes=1),'close'),float('nan'))
    if not all(math.isfinite(v) and v>0 for v in (a,b)):
        return float('nan')
    return math.log(b/a)


def locked_m2(clock: MarketClock, input_day: str, context: int, ticker: str,
              observations: dict[tuple[str, datetime, str], float]) -> tuple[float,float,tuple[datetime,...]]:
    """Original last20/60 REGULAR-origin slots,19/57 support,max2misses; no compression."""
    cal=clock.calendar
    regular=cal.loc[(cal.close-cal.open)==pd.Timedelta(minutes=390)]
    days=[str(d.date()) for d in regular.index if str(d.date())<input_day][-60:]
    if len(days)<60:
        return float('nan'),float('nan'),()
    day_open=cal.loc[input_day:input_day].iloc[0]['open'].to_pydatetime()
    values=[]; ends=[]
    for day in days:
        origins=cached_origins(clock,day)
        origin=origins[0 if context==6 else context+1]
        end=cached_endpoint(clock,origin)
        values.append(source_ratio(origin,end,ticker,observations,day_open))
        if end+timedelta(minutes=2)<day_open:
            ends.append(end)
    x=np.asarray(values,dtype=float)[:,None]
    return float(rolling(x[-20:],20,19)[-1,0]),float(rolling(x,60,57,True)[-1,0]),tuple(ends)
