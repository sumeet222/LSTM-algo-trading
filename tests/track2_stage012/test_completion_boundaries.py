from datetime import datetime,timedelta
from dataclasses import replace
from pathlib import Path
from zoneinfo import ZoneInfo
import ast
import json
import math
import pytest
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.contracts import Observation
from lstm_data.trading.track2.stage012.sign_scheduler import SessionSignScheduler
from lstm_data.trading.track2.stage012.original_feature_pure import source_ratio,locked_m2
from lstm_data.trading.track2.stage012.risk_reference_prepare import MaturedPrefixObservation,prepare,RiskRecipe,write_manifest,load_reference


def et(s):return datetime.fromisoformat(s).replace(tzinfo=ZoneInfo('America/New_York'))


def test_runtime_call_boundary():
    root=Path('src/lstm_data/trading/track2/stage012')
    for name in ('historical_input_only.py','original_feature_pure.py','sign_scheduler.py'):
        tree=ast.parse((root/name).read_text())
        calls=[n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else '' for n in ast.walk(tree) if isinstance(n,ast.Call)]
        assert not {'View','source_components','expanded_m2','read_parquet','load_model_input','prepare','fit','fit_expanded'}&set(calls)
        assert 'risk_reference_prepare' not in (root/name).read_text()


def test_m2_maturity_and_cop_boundary():
    t=et('2024-01-05T15:30');end=et('2024-01-08T13:00')
    p={('AAPL',t-timedelta(minutes=1),'close'):100.,('AAPL',end-timedelta(minutes=1),'close'):110.}
    assert math.isnan(source_ratio(t,end,'AAPL',p,et('2024-01-08T09:30')))
    assert source_ratio(t,end,'AAPL',p,et('2024-01-09T09:30'))==math.log(1.1)
    assert math.isnan(source_ratio(et('2012-04-30T15:30'),et('2012-05-01T13:00'),'COP',{},et('2012-05-02T09:30')))
    # Strict equality at original maturity frontier is not available.
    assert math.isnan(source_ratio(t,end,'AAPL',p,end+timedelta(minutes=2)))


def test_session_freeze_and_missing_first():
    clock=MarketClock('2023-12-01','2024-01-10');sched=SessionSignScheduler(clock)
    dates=('2023-12-28','2023-12-29','2024-01-02','2024-01-03','2024-01-04','2024-01-05')
    refs={d:(100.+i,Observation(d,et(d+'T15:30'),et(d+'T15:30'),et(d+'T15:32'),'x')) for i,d in enumerate(dates)}
    frozen=sched.freeze('AAPL','2024-01-08',et('2024-01-08T09:32'),refs,'x')
    refs[dates[-1]]=(1.,refs[dates[-1]][1])
    assert sched.freeze('AAPL','2024-01-08',et('2024-01-08T15:32'),refs,'x') is frozen
    assert frozen.sign.alpha==math.log(105/100)
    with pytest.raises(ValueError):sched.reject_revision(replace(frozen,lineage_hash='revised'))
    abstain=sched.freeze('COP','2024-01-08',et('2024-01-08T09:32'),{},'x')
    assert sched.freeze('COP','2024-01-08',et('2024-01-08T10:32'),refs,'x') is abstain
    assert abstain.sign.direction==0


def risk_rows():
    t=et('2019-01-02T10:30')
    return tuple(MaturedPrefixObservation('AAPL','10:30',t+timedelta(days=i),t+timedelta(days=i,hours=4),t+timedelta(days=i,hours=4,minutes=2),.01+i*.0001,'x','source') for i in range(50))


def test_prefix_fit_and_postcutoff_invariance(tmp_path):
    rows=risk_rows();start=et('2011-04-01T00:00');cut=et('2020-09-30T20:00')
    r=prepare(rows,'F21','AAPL','10:30',start,cut,'x','inventory')
    future=replace(rows[0],origin=cut,endpoint=cut+timedelta(hours=4),available_at=cut+timedelta(hours=4,minutes=2),magnitude=-1,basis='wrong')
    r2=prepare(rows+(future,),'F21','AAPL','10:30',start,cut,'x','inventory')
    assert (r['b'],r['m_floor'])==(r2['b'],r2['m_floor'])
    assert r['m_floor']==max(1e-6,.25*r['b'])
    path=tmp_path/'reference.json';checksum=write_manifest(path,[r],[])
    ref=load_reference(path,'F21','AAPL','10:30','x',checksum,'inventory')
    assert ref.b==r['b']
    for m in (0,.001,.01,1,100):assert .5<=ref.multiplier(m,et('2021-01-08T10:32'))<=1.5
    with pytest.raises(ValueError):load_reference(path,'F22','AAPL','10:30','x',checksum,'inventory')
    with pytest.raises(ValueError):load_reference(path,'F21','AAPL','10:30','wrong',checksum,'inventory')
    assert prepare(rows[:39],'F21','AAPL','10:30',start,cut,'x','inventory')['status']!='READY'
    assert prepare(tuple(replace(x,magnitude=0) for x in rows),'F21','AAPL','10:30',start,cut,'x','inventory')['status']!='READY'
    with pytest.raises(ValueError):prepare((replace(rows[0],late_corrected=True),),'F21','AAPL','10:30',start,cut,'x','inventory')
    for v in (-1,float('nan')):
        with pytest.raises(ValueError):prepare((replace(rows[0],magnitude=v),),'F21','AAPL','10:30',start,cut,'x','inventory')


def test_original_producer_synthetic_source_frontier():
    import pandas as pd
    from lstm_data.trading.track2.stage012.historical_input_only import OriginalInputOnlySnapshotProducer,Abstention
    from lstm_data.trading.track2.stage012.model_registry import ModelRegistry
    clock=MarketClock('2022-01-03','2024-01-10');origin=et('2024-01-08T11:30')
    records=[];prices={}
    for rawday,row in clock.calendar.iterrows():
        day=pd.Timestamp(str(rawday))
        for k in range(6):
            start=row['open']+pd.Timedelta(hours=k);end=start+pd.Timedelta(hours=1)
            if end>row['close']:continue
            for ticker in ('AAPL','COP'):
                v=100+len(records)*.0001
                records.append(dict(ticker=ticker,hour_start_utc=start,hour_end_utc=end,session_date_et=str(day.date()),is_stub=False,
                   open=v,close=v+.01,high=v+.02,low=v-.01,close_input_cap5=v+.01,observed_volume=100.,observed_volume_complete=True,
                   genuine_count=60,missing_count=0,quarantine_count=0,conflict_count=0,invalid_minutes=0,proxy_count=0,longest_gap_minutes=0))
        for t in clock.origins(str(day.date())):
            for ticker in ('AAPL','COP'):
                prices[(ticker,t,'open')]=100.
                prices[(ticker,t-timedelta(minutes=1),'close')]=100.
                try:end=clock.endpoint(t)
                except ValueError:continue
                prices[(ticker,end-timedelta(minutes=1),'close')]=101.
    hours=pd.DataFrame(records)
    model=ModelRegistry(Path('.'),Path('trading/track2/stage012/original_bundles.json')).load(2024)
    producer=OriginalInputOnlySnapshotProducer(hours,prices,[],clock,'synthetic')
    result=producer.produce(model.bundle,'AAPL',origin)
    assert not isinstance(result,Abstention)
    snapshot,audit=result
    assert len(snapshot.values)==48 and len(snapshot.clock)==10 and len(audit.lineage)==26
    hours.loc[hours.hour_end_utc>origin,['open','close','high','low','close_input_cap5']]=999999.
    twin=OriginalInputOnlySnapshotProducer(hours,prices,[],clock,'synthetic').produce(model.bundle,'AAPL',origin)
    assert not isinstance(twin,Abstention)
    assert twin[0]==snapshot and twin[1].input_hash==audit.input_hash
    assert all(o.interval_end<=origin for o in snapshot.dependencies)


def test_original_q2_and_cop_mask_semantics():
    import numpy as np
    import pandas as pd
    from lstm_data.hf1m_ft16_math import Components
    from lstm_data.hf1m_ft16_fit import native
    from lstm_data.hf1m_ft16_source import COMMON
    from lstm_data.hf20_s4_preflight import field_masks
    from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
    v={k:np.ones((1,20)) for k in ('OC','RMS60','MOM5','MOM105','RMS63','RMS12','VOLUME_H','Q1_MEAN','Q2_5','Q2_60','B1','B2','T1','T2','T3','T4','T5')}
    v['Q2_5']*=2
    c=Components(pd.DataFrame(),pd.DataFrame(),{'close':np.ones((1,20))},v,np.array([]),np.empty((0,20)),np.empty((0,20)),np.empty((0,20),object),np.full((1,20),'new_regime',object),np.ones((1,20,7)),np.ones((1,20,7)),np.array([0]),np.array([0]),pd.DataFrame())
    floors=[dict(hourly_floor=.1,daily_floor=.1,m2_floor=.1,volume_pseudocounts={'new_regime':{'hour':1.,'day':10.}}) for _ in SYMBOLS]
    raw,_=native(c,floors)
    assert raw[0,0,COMMON.index('Q2')]==pytest.approx(math.log(12/11))
    clock=MarketClock('2012-01-03','2013-01-04');rows=[]
    for date,part in clock.calendar.iterrows():
        for k in range(6):
            t=part['open']+pd.Timedelta(hours=k)
            if t+pd.Timedelta(hours=1)<=part['close']:
                for ticker in ('COP','AAPL'):
                    rows.append(dict(hour_id=ticker+str(t),ticker=ticker,hour_start_utc=t,session_date_et=str(pd.Timestamp(str(date)).date()),is_stub=False))
    masked=field_masks(pd.DataFrame(rows),[])
    assert masked.loc[(masked.ticker=='COP')&(masked.session_date_et=='2012-05-01'),'hour_feature_dependency_action_crossing'].all()
    assert not masked.loc[masked.ticker=='AAPL','hour_feature_dependency_action_crossing'].any()
    assert not masked.loc[(masked.ticker=='COP')&(masked.session_date_et=='2012-12-28'),'hour_feature_dependency_action_crossing'].any()


def test_prefix_straddling_cutoff_and_manifest_repeat(tmp_path):
    rows=risk_rows();start=et('2011-04-01T00:00');cut=et('2020-09-30T20:00')
    r=prepare(rows,'F21','AAPL','10:30',start,cut,'x','inventory')
    boundary=replace(rows[0],origin=cut-timedelta(hours=3),endpoint=cut+timedelta(hours=1),available_at=cut+timedelta(hours=1,minutes=2),magnitude=9999.)
    twin=prepare(rows+(boundary,),'F21','AAPL','10:30',start,cut,'x','inventory')
    assert (r['b'],r['m_floor'],r['count'])==(twin['b'],twin['m_floor'],twin['count'])
    assert write_manifest(tmp_path/'a.json',[r],[])==write_manifest(tmp_path/'b.json',[r],[])
    with pytest.raises(ValueError):prepare(rows,'F21','AAPL','10:30',start,cut,'x','inventory',RiskRecipe(units='sigma'))


def test_future_partition_rejected_before_io():
    from lstm_data.trading.track2.stage012.historical_source_store import HistoricalSourceStore
    store=HistoricalSourceStore.__new__(HistoricalSourceStore)
    with pytest.raises(ValueError,match='BEFORE_IO'):
        store.checked({'path':'data/processed/hf20_hf1m_long_v1/2025-01.parquet','sha256':'bad'})


def test_all_twenty_calendar_opportunities_no_future_gate():
    from lstm_data.trading.track2.stage012.sign_scheduler import session_opportunities
    clock=MarketClock('2024-01-01','2024-12-10')
    before=session_opportunities(clock,'2024-01-08')
    assert len(before)==140
    future_labels={'F09_complete':False,'endpoint':None}
    assert session_opportunities(clock,'2024-01-08')==before
    assert future_labels['endpoint'] is None
    assert len(session_opportunities(clock,'2024-11-29'))==80
    assert not session_opportunities(clock,'2024-11-28')
