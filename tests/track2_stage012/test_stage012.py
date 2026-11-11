"""Synthetic-only Stage 0–2 adversarial witnesses; no portfolio returns."""
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import pytest
import torch
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock, availability
from lstm_data.trading.track2.stage012.contracts import Observation, FeatureSnapshot, TrendSignal
from lstm_data.trading.track2.stage012.model_registry import ModelRegistry
from lstm_data.trading.track2.stage012.risk_sizing import RiskReference
from lstm_data.trading.track2.stage012.signal_pipeline import issue
from lstm_data.trading.track2.stage012.trend_direction import trend
from lstm_data.trading.track2.stage012.cohort_state import Cohort, Event, EventKind
from lstm_data.trading.track2.stage012.order_netting import net_order, allocate_external_fill, ReservationBook
from lstm_data.trading.track2.stage012.policy import FixedHorizonPolicy, DynamicRebalancePolicy

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'trading/track2/stage012'


def et(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo('America/New_York'))


@pytest.fixture(scope='module')
def clock():
    return MarketClock('2012-10-01', '2025-01-10')


@pytest.mark.parametrize('slot,end', [('09:30','2024-01-08T13:30'), ('10:30','2024-01-08T14:30'),
 ('11:30','2024-01-08T15:30'), ('12:30','2024-01-09T10:00'), ('13:30','2024-01-09T11:00'),
 ('14:30','2024-01-09T12:00'), ('15:30','2024-01-09T13:00')])
def test_seven_exact(clock, slot, end):
    t = et('2024-01-08T'+slot)
    assert clock.endpoint(t) == et(end)
    _, _, decision = availability(t, (Observation('x', t, t, t, 'adjusted'),))
    assert decision == t + timedelta(minutes=2)
    assert clock.next_observation(decision) == t + timedelta(minutes=3)


@pytest.mark.parametrize('origin,end', [
 ('2024-01-12T15:30','2024-01-16T13:00'),
 ('2024-11-29T09:30','2024-12-02T10:00'),
 ('2024-11-29T12:30','2024-12-02T13:00'),
 ('2024-03-08T15:30','2024-03-11T13:00'),
 ('2024-11-01T15:30','2024-11-04T13:00'),
 ('2012-10-26T15:30','2012-10-31T13:00'),
 ('2018-12-04T15:30','2018-12-06T13:00')])
def test_closures(clock, origin, end):
    assert clock.endpoint(et(origin)) == et(end)


def test_half_opening_exit_and_wall_delay(clock):
    assert len(clock.origins('2024-11-29')) == 4
    assert not clock.origins('2018-12-05')
    t = et('2024-01-08T09:30')
    slots = clock.full_hour_slots(t)
    assert len(slots) == 48 and slots[-1] == et('2024-01-05T15:30')
    end = clock.endpoint(et('2024-01-08T10:30'))
    assert clock.next_observation(end + timedelta(minutes=2)) == et('2024-01-08T14:33')
    assert clock.next_observation(et('2024-01-08T23:30')) == et('2024-01-09T09:30')
    field = Observation('late', t, t+timedelta(minutes=1), t+timedelta(minutes=10), 'x')
    assert availability(t, (field,))[2] == t + timedelta(minutes=10)
    for delay in (1,2,5):
        assert availability(t, (Observation('x',t,t,t,'x'),), delay)[2] == t+timedelta(minutes=delay)


def test_six_prior_sessions(clock):
    days = ('2023-12-28','2023-12-29','2024-01-02','2024-01-03','2024-01-04','2024-01-05')
    refs = {d:(100.+i, Observation(d,et(d+'T15:30'),et(d+'T15:30'),et(d+'T15:32'),'split')) for i,d in enumerate(days)}
    sign = trend(days,refs,et('2024-01-08T09:32'),'split')
    import math
    assert sign.alpha == math.log(105/100) and sign.direction == 1
    assert trend(days,refs,et('2024-01-08T09:32'),'raw').direction == 0
    del refs[days[-1]]
    assert trend(days,refs,et('2024-01-08T09:32'),'split').direction == 0


@pytest.mark.parametrize('m,expected', [(0,1.5),(.01,1),(.1,.5)])
def test_sizing(m, expected):
    t=et('2024-01-08T10:32')
    r=RiskReference('AAPL','F24','10:30',.01,.001,t-timedelta(days=1),t-timedelta(days=1),'synthetic')
    assert r.multiplier(m,t)==expected
    with pytest.raises(ValueError):
        replace(r,matured_at=t).multiplier(m,t)
    p=FixedHorizonPolicy()
    assert p.candidate_notional(-1,100,expected)==-p.candidate_notional(1,100,expected)


@pytest.fixture(scope='module')
def forecasts():
    return {y:ModelRegistry(ROOT,DOC/'original_bundles.json').load(y) for y in range(2021,2025)}


def snapshot(clock, ticker='AAPL', origin='2024-01-08T11:30'):
    t=et(origin)
    from json import loads
    row=loads((DOC/'original_bundles.json').read_text())['bundles'][str(t.year)]
    return FeatureSnapshot(ticker,t,clock.full_hour_slots(t),tuple((0.,)*16 for _ in range(48)),
                           (0.,)*10,tuple((False,)*16 for _ in range(48)),
                           (Observation('synthetic_hour',t-timedelta(hours=1),t,t+timedelta(minutes=2),'synthetic'),),
                           row['sha256'][1],'synthetic', 'INTRADAY' if t.hour<12 else 'OVERNIGHT')


@pytest.mark.parametrize('year', [2021,2022,2023,2024])
def test_original_load_eval_nonmutation(forecasts, year, clock):
    f=forecasts[year]
    paths=(f.bundle.checkpoint,f.bundle.recipe,f.bundle.calibration,f.bundle.phases)
    before=tuple((p.stat().st_mtime_ns,p.read_bytes()) for p in paths)
    s=snapshot(clock, origin=f'{year}-01-08T11:30')
    assert sum(p.numel() for p in f.model.parameters())==6572
    assert f.predict(s)==f.predict(s)
    assert not f.model.training and all(not p.requires_grad and p.grad is None for p in f.model.parameters())
    assert before==tuple((p.stat().st_mtime_ns,p.read_bytes()) for p in paths)
    with pytest.raises(ValueError):
        f.predict(replace(s,recipe_hash='PHASE2'))


@pytest.mark.parametrize('ticker', ['AAPL','COP'])
@pytest.mark.parametrize('origin', ['2024-01-08T09:30','2024-01-08T11:30','2024-01-08T15:30','2024-11-29T09:30'])
def test_input_only_signal(clock, forecasts, ticker, origin):
    s=snapshot(clock,ticker,origin)
    # Category is calendar-dependent, including opening on a half day.
    closed=clock.calendar.loc[origin[:10]:origin[:10]].iloc[0]['close']
    s=replace(s,category='INTRADAY' if clock.endpoint(s.nominal_origin)<=closed else 'OVERNIGHT')
    sign=TrendSignal(.01,1,(),'SYNTHETIC')
    record=issue(s,forecasts[2024],sign,clock)
    serialized=record.to_json()
    for future_price in (None,0,100,1000000):
        future_store={'endpoint_price':future_price, 'F09_complete':False}
        assert issue(s,forecasts[2024],sign,clock).to_json()==serialized
        assert future_store['F09_complete'] is False
    assert record.size_multiplier is None and record.eligibility_reason=='RISK_REFERENCE_UNAVAILABLE'
    assert 'endpoint_price' not in serialized and 'realized' not in serialized
    assert record.earliest_executable_observation_utc>record.decision_utc
    delayed=replace(s,dependencies=(replace(s.dependencies[0],available_at=s.nominal_origin+timedelta(minutes=10)),))
    assert issue(delayed,forecasts[2024],sign,clock).decision_utc==s.nominal_origin+timedelta(minutes=10)
    with pytest.raises(ValueError):
        replace(s,dependencies=())
    with pytest.raises(ValueError):
        replace(s,slots=s.slots[1:])
    with pytest.raises(ValueError):
        replace(s,price_basis='raw')
    with pytest.raises(ValueError):
        replace(s,dependencies=(replace(s.dependencies[0],interval_end=s.nominal_origin+timedelta(minutes=1)),))


def cohort(quantity=10):
    return Cohort('S2C-F24|2024-01-08T15:30Z|AAPL|synthetic','AAPL',quantity,100,
                  et('2024-01-08T10:30'),et('2024-01-08T14:30'),et('2024-01-08T10:35'),
                  'raw',('synthetic',))


def test_fixed_partial_exit_and_overnight():
    c=cohort()
    c=c.apply(Event('order',EventKind.ENTRY,et('2024-01-08T10:32')))
    c=c.apply(Event('partial',EventKind.FILL,et('2024-01-08T10:33'),4,100,basis='raw'))
    assert c.status=='PARTIALLY_FILLED'
    c=c.apply(Event('filled',EventKind.FILL,et('2024-01-08T10:34'),6,101,basis='raw'))
    assert c.shares==10 and c.status=='OPEN'
    assert FixedHorizonPolicy().on_new_origin((c,))==(c,)
    with pytest.raises(ValueError):
        c.apply(Event('early',EventKind.EXIT,et('2024-01-08T11:30')))
    with pytest.raises(RuntimeError):
        DynamicRebalancePolicy().rebalance()
    c=c.apply(Event('exit',EventKind.EXIT,c.endpoint))
    c=c.apply(Event('closed',EventKind.FILL,c.endpoint+timedelta(minutes=1),-10,102,basis='raw'))
    assert c.shares==0 and c.status=='CLOSED' and len(c.events)==5


@pytest.mark.parametrize('kind', [EventKind.SPLIT,EventKind.DIVIDEND,EventKind.HALT,EventKind.BUY_IN,EventKind.BORROW_CHARGE])
def test_unresolved_action(kind):
    c=cohort().apply(Event('action',kind,et('2024-01-08T10:32')))
    assert c.status=='UNRESOLVED'


def test_netting_and_reservations():
    assert net_order('AAPL',(('old',10),('new',-6))).quantity==4
    assert net_order('AAPL',(('old_exit',-10),)).quantity==-10
    assert 4-10==-6
    with pytest.raises(ValueError,match='INTERNAL_CROSS'):
        allocate_external_fill(net_order('AAPL',(('a',10),('b',-6))),4)
    for filled in (1,5,10):
        parts=allocate_external_fill(net_order('AAPL',(('a',4),('b',6))),filled,1)
        assert sum(p[1] for p in parts)==filled and sum(p[2] for p in parts)==1
    b=ReservationBook(1000,1000).reserve('a','AAPL',60)
    with pytest.raises(ValueError):
        b.reserve('b','AAPL',50)
    with pytest.raises(ValueError):
        b.reserve('b','COP',-50)
    b=b.reserve('b','COP',-50,True)
    assert sum(r.cash_collateral for r in b.reservations)==110
    with pytest.raises(ValueError):
        b.release(cohort())


def test_missing_late_fill_and_rebalance():
    c=cohort().apply(Event('order',EventKind.ENTRY,et('2024-01-08T10:32')))
    with pytest.raises(ValueError):
        c.apply(Event('late',EventKind.FILL,et('2024-01-08T10:36'),10,100,basis='raw'))
    assert c.apply(Event('cancel',EventKind.CANCEL,et('2024-01-08T10:36'))).status=='REJECTED'
    with pytest.raises(ValueError):
        c.apply(Event('resize',EventKind.REBALANCE,et('2024-01-08T11:32')))


def test_protocol_and_intents(clock, forecasts):
    from lstm_data.trading.track2.stage012.protocol import ProtocolContract
    from lstm_data.trading.track2.stage012.intents import candidate, cohort_from_intent
    protocol=ProtocolContract.load(DOC/'protocol.json')
    assert protocol.gross_cap==1 and protocol.name_cap==.1 and protocol.sleeve_cap==.2
    assert protocol.clip==(.5,1.5) and not protocol.dynamic_rebalancing_enabled
    s=snapshot(clock)
    t=s.nominal_origin
    ref=RiskReference('AAPL','F24','11:30',.01,.001,t-timedelta(days=1),t-timedelta(days=1),'synthetic-only')
    signal=issue(s,forecasts[2024],TrendSignal(.01,1,(),'SYNTHETIC'),clock,ref)
    intent=candidate(signal,100)
    c=cohort_from_intent(intent,1,t,t+timedelta(minutes=5),'raw')
    assert c.endpoint==signal.nominal_endpoint_utc and c.provenance==(signal.to_json(),)
    assert FixedHorizonPolicy().on_new_origin((c,))[0].requested==1


def test_opening_bar_receipt(clock, forecasts):
    s=snapshot(clock,origin='2024-01-08T09:30')
    t=s.nominal_origin
    prior=s.slots[-1]
    s=replace(s,dependencies=(Observation('prior_hour',prior-timedelta(hours=1),prior,prior,'synthetic'),
                              Observation('origin_open_reference',t,t+timedelta(minutes=1),t+timedelta(minutes=2),'synthetic')))
    signal=issue(s,forecasts[2024],TrendSignal(0,0,(),'synthetic'),clock)
    assert signal.source_latest_observed_end_utc==t+timedelta(minutes=1)
    assert signal.decision_utc==t+timedelta(minutes=2)
    assert s.slots[-1]<t


def test_aggregate_capacity_and_fees():
    b=ReservationBook(1000,1000)
    for i in range(10):
        b=b.reserve(str(i),str(i),100)
    with pytest.raises(ValueError):
        b.reserve('extra','new',1)
    assert sum(r.cash_collateral for r in b.reservations)==1000
    with pytest.raises(ValueError):
        ReservationBook(1000,50).reserve('a','AAPL',60)
    for n in range(1,20):
        order=net_order('AAPL',tuple((str(i),float(i+1)) for i in range(n)))
        parts=allocate_external_fill(order,order.quantity/2,.37)
        assert sum(x[1] for x in parts)==pytest.approx(order.quantity/2)
        assert sum(x[2] for x in parts)==pytest.approx(.37)
