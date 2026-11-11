"""Original FT16 producer. No target panel, View, score keys or evaluation readers.

Original build/native/scaled arithmetic is reused without fitting. Unrequested stocks
are NaN placeholders in the original fixed20 structural axis, never issued inputs.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import math
import json
import numpy as np
import pandas as pd
from lstm_data.hf1m_ft16_math import build
from lstm_data.hf1m_ft16_fit import native
from lstm_data.hf1m_ft16_source import COMMON, ORDER
from lstm_data.hf20_s4_preflight import field_masks, input_valid
from lstm_data.hf20_s4_witnesses import scaled
from .calendar_schedule import MarketClock
from .contracts import Observation, FeatureSnapshot, utc
from .model_registry import SYMBOLS, Bundle
from .original_feature_pure import locked_m2

BASIS='SPLIT_CONSISTENT_20260331'


@dataclass(frozen=True)
class Abstention:
    ticker: str
    nominal_origin_utc: str
    reason: str


@dataclass(frozen=True)
class ObservationLineage:
    feature: str
    source_role: str
    earliest_end: str
    latest_end: str
    available_at: str
    dependency_hash: str
    source_inventory_hash: str
    qualification: str = 'inherited retrospective adjustment/quarantine; assumed receipt'


@dataclass(frozen=True)
class CausalFeatureAudit:
    ticker: str
    origin: str
    lineage: tuple[ObservationLineage,...]
    input_hash: str
    masked_cells: int


def padded_hours(hours: pd.DataFrame, clock: MarketClock, asof: datetime) -> pd.DataFrame:
    """Restore complete scheduled slots incl missing data; no future VALUES enter build."""
    records=[]
    day=str(asof.astimezone(ZoneInfo('America/New_York')).date())
    for date,row in clock.calendar.loc[:day].iterrows():
        for k in range(6):
            start=row['open']+pd.Timedelta(hours=k);end=start+pd.Timedelta(hours=1)
            if end<=row['close']:
                for ticker in SYMBOLS:
                    records.append((start,end,str(pd.Timestamp(str(date)).date()),ticker))
    base=pd.DataFrame(records,columns=['hour_start_utc','hour_end_utc','session_date_et','ticker'])
    # Keep future scheduled positions as missing, so current-day calendar classification
    # cannot depend on future observed bars. All source values after cutoff are removed.
    source=hours.loc[(hours.hour_end_utc<=asof)&~hours.is_stub].copy()
    if source.duplicated(['hour_start_utc','ticker']).any():
        raise ValueError('DUPLICATE_SOURCE_HOUR')
    fields=[c for c in source.columns if c not in base.columns]
    base=base.merge(source[['hour_start_utc','ticker',*fields]],on=['hour_start_utc','ticker'],how='left',validate='one_to_one')
    base['is_stub']=False
    base['hour_id']=base.ticker+':'+base.hour_start_utc.astype(str)
    base['price_basis_id']=np.where(base.ticker.eq('COP'),np.where(base.session_date_et<'2012-05-01','COP_PRE_SPINOFF','COP_POST_SPINOFF'),BASIS)
    for key in ('missing_count','quarantine_count','conflict_count','invalid_minutes','genuine_count','proxy_count','longest_gap_minutes'):
        base[key]=base[key].fillna(60 if key in ('missing_count','longest_gap_minutes') else 0)
    base['expected_minutes']=60
    base['observed_volume_complete']=base.observed_volume_complete.fillna(False).astype(bool)
    return base


class OriginalInputOnlySnapshotProducer:
    def __init__(self, hours: pd.DataFrame, prices: dict[tuple[str,datetime,str],float],
                 facts: list[dict], clock: MarketClock, inventory_hash: str):
        if hours.session_date_et.max()>'2024-12-31':
            raise ValueError('POST2024_SOURCE_DENIED')
        self.hours,self.prices,self.facts,self.clock,self.inventory_hash=hours,prices,facts,clock,inventory_hash
        self.last_origin: datetime | None=None
        self.components=None

    def produce(self, bundle: Bundle, ticker: str, origin: datetime,
                receipt_minutes: int=2) -> tuple[FeatureSnapshot,CausalFeatureAudit] | Abstention:
        origin=utc(origin);day=str(origin.astimezone(ZoneInfo('America/New_York')).date())
        if ticker not in SYMBOLS or int(day[:4])!=bundle.year:
            raise ValueError('FOLD_TICKER_MISMATCH')
        if ticker not in set(self.hours.ticker):
            return Abstention(ticker,origin.isoformat(),'TICKER_OUTSIDE_SOURCE_PROJECTION')
        if origin not in self.clock.origins(day):
            return Abstention(ticker,origin.isoformat(),'INVALID_CALENDAR_ORIGIN')
        if receipt_minutes not in (1,2,5):
            raise ValueError('INVALID_RECEIPT_SCENARIO')
        bundle.verify()
        if self.last_origin!=origin:
            self.components=None
            h=padded_hours(self.hours,self.clock,origin)
            self.components=build(h,field_masks(h,self.facts))
            self.last_origin=origin
        c=self.components
        if c is None:
            raise ValueError('COMPONENTS_REQUIRED')
        slots=self.clock.full_hour_slots(origin)
        indices=c.grid.index[c.grid.hour_end_utc.isin(slots)].to_numpy(int)
        if len(indices)!=48:
            return Abstention(ticker,origin.isoformat(),'MISSING_SCHEDULED_SLOT')
        j=SYMBOLS.index(ticker)
        if not input_valid(c)[indices[-1],j]:
            return Abstention(ticker,origin.isoformat(),'ORIGINAL_INPUT_GATE')
        # New arrays, never mutate original2-context component cache.
        import copy
        view=copy.copy(c)
        view.m2_mean=np.full((len(c.grid),20,7),np.nan)
        view.m2_rms=np.full_like(view.m2_mean,np.nan)
        context=6 if origin.astimezone(ZoneInfo('America/New_York')).hour==9 else origin.astimezone(ZoneInfo('America/New_York')).hour-10
        m2ends=[]
        for input_day in c.grid.loc[indices,'session_date_et'].unique():
            mean,rms,ends=locked_m2(self.clock,str(input_day),context,ticker,self.prices)
            ix=indices[c.grid.loc[indices,'session_date_et'].to_numpy()==input_day]
            view.m2_mean[ix,j,context]=mean;view.m2_rms[ix,j,context]=rms;m2ends.extend(ends)
        # Original COP dependency mask on components, with ARCHIVED fitted floors.
        blocked=c.hours.pivot(index='hour_start_utc',columns='ticker',values='cop_dependency').reindex(index=c.grid.hour_start_utc,columns=SYMBOLS).to_numpy(bool)
        view.m2_mean[blocked]=np.nan;view.m2_rms[blocked]=np.nan
        recipe=json.loads(bundle.recipe.read_text())
        raw,m2=native(view,recipe['floors']); common,scaled_m2=scaled(view,recipe)
        values=np.empty((48,16),np.float32);masks=np.empty((48,16),bool)
        for k,name in enumerate(ORDER):
            values[:,k]=scaled_m2[indices,j,context] if name=='M2' else common[indices,j,COMMON.index(name)]
            masks[:,k]=~np.isfinite(m2[indices,j,context] if name=='M2' else raw[indices,j,COMMON.index(name)])
        cal=self.clock.calendar;session=cal.loc[day:day].iloc[0]
        closed=session['close'].to_pydatetime();following=cal.loc[cal.index>pd.Timestamp(day)].iloc[0]['open'].to_pydatetime()
        remaining=(closed-origin).total_seconds()/60
        category='OVERNIGHT' if remaining<240 else 'INTRADAY'
        slot_index=(origin.astimezone(ZoneInfo('America/New_York')).hour-9)
        clock_values=tuple(float(v) for v in np.asarray([*(1. if k==slot_index else 0. for k in range(7)),remaining/240,float(remaining<240),(following.astimezone(ZoneInfo('America/New_York')).date()-origin.astimezone(ZoneInfo('America/New_York')).date()).days/7],dtype=np.float32))
        latest=slots[-1];first=self.clock.calendar.iloc[0]['open'].to_pydatetime()
        deps=[Observation('hourly_history:'+self.inventory_hash,first,latest,latest+timedelta(minutes=receipt_minutes),BASIS)]
        if m2ends:
            last=max(m2ends)
            deps.append(Observation('matured_M2_source:'+self.inventory_hash,min(m2ends),last,last+timedelta(minutes=2),BASIS))
        if slot_index==0:
            opening=self.prices.get((ticker,origin,'open'),float('nan'))
            if not math.isfinite(opening) or opening<=0:
                return Abstention(ticker,origin.isoformat(),'MISSING_GENUINE_OPEN_REFERENCE')
            deps.append(Observation('origin_open_reference',origin,origin+timedelta(minutes=1),origin+timedelta(minutes=receipt_minutes+1),BASIS))
            # Protocol2-minute opening scenario is09:32: completion09:31 plus1minute.
            deps[-1]=Observation('origin_open_reference',origin,origin+timedelta(minutes=1),origin+timedelta(minutes=max(1,receipt_minutes)),BASIS)
        snap=FeatureSnapshot(ticker,origin,slots,tuple(tuple(float(v) for v in r) for r in values),clock_values,tuple(tuple(bool(v) for v in r) for r in masks),tuple(deps),bundle.identities[1],BASIS,category)
        input_hash=hashlib.sha256(values.tobytes()+np.asarray(clock_values,np.float32).tobytes()+masks.tobytes()).hexdigest()
        lineage=[]
        for name in (*ORDER,*(f'CLOCK{k}' for k in range(10))):
            end=max(m2ends) if name=='M2' and m2ends else latest
            start=min(m2ends) if name=='M2' and m2ends else first
            role='day-open locked prior60 regular-origin source ratios' if name=='M2' else 'calendar only' if name.startswith('CLOCK') else 'original own-stock hourly history; conservative recursive-history envelope'
            dh=hashlib.sha256(f'{ticker}|{name}|{start}|{end}|{self.inventory_hash}|{bundle.identities[1]}'.encode()).hexdigest()
            lineage.append(ObservationLineage(name,role,start.isoformat(),end.isoformat(),(end+timedelta(minutes=2 if name=='M2' else receipt_minutes)).isoformat(),dh,self.inventory_hash))
        return snap,CausalFeatureAudit(ticker,origin.isoformat(),tuple(lineage),input_hash,int(masks.sum()))
