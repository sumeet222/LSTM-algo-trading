"""Predeclared original-source signal-only dry run. No orders, fills or P&L."""
from dataclasses import asdict,replace
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import math
import pandas as pd
import numpy as np
import torch
from .calendar_schedule import MarketClock
from .contracts import utc
from .historical_source_store import HistoricalSourceStore,file_hash
from .historical_input_only import OriginalInputOnlySnapshotProducer,Abstention,BASIS
from .model_registry import ModelRegistry,SYMBOLS
from .original_feature_pure import cached_endpoint,cached_origins
from .sign_scheduler import SessionSignScheduler,scheduled_signal
from .signal_pipeline import issue
from .risk_reference_prepare import MaturedPrefixObservation,prepare,write_manifest,load_reference


def save(path: Path,payload: object) -> None:
    if path.exists():raise ValueError('APPEND_ONLY_OUTPUT_REQUIRED')
    path.write_text(json.dumps(payload,indent=2,default=lambda x:utc(x).isoformat())+'\n')


def prefix_references(store: HistoricalSourceStore,clock: MarketClock,facts: list[dict],run: Path) -> tuple[Path,str,str]:
    """Offline-only source outcome reader; never reachable from signal producer."""
    prices=store.minutes('risk_prefix',facts)
    observations=[]
    inventory=[r for r in store.plan['sources'] if r['role']=='risk_prefix']
    invhash=hashlib.sha256(json.dumps(inventory,sort_keys=True).encode()).hexdigest()
    for d in clock.calendar.loc['2019-01-02':'2019-06-28'].index:
        day=str(d.date());origins=cached_origins(clock,day)
        for t in origins:
            end=cached_endpoint(clock,t);slot=t.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')
            field,at=('open',t) if t==origins[0] else ('close',t-timedelta(minutes=1))
            for ticker in SYMBOLS:
                a=prices.get((ticker,at,field));b=prices.get((ticker,end-timedelta(minutes=1),'close'))
                if a is None or b is None or not all(math.isfinite(v) and v>0 for v in (a,b)):continue
                observations.append(MaturedPrefixObservation(ticker,slot,t,end,end+timedelta(minutes=2),abs(math.log(b/a)),BASIS,invhash))
    folds=json.loads(Path('trading/track2/stage012/ORIGINAL_FOLD_PREFIX_CUTOFFS.json').read_text())
    records=[]
    # No global/oos/calibration fallback; every group can independently fail support.
    for fold,meta in folds.items():
        start=datetime.fromisoformat(meta['fit_start']).replace(tzinfo=ZoneInfo('America/New_York'))
        cutoff=datetime.fromisoformat(meta['fit_stop_inclusive']).replace(tzinfo=ZoneInfo('America/New_York'))+timedelta(hours=20)
        for ticker in SYMBOLS:
            for slot in ('09:30','10:30','11:30','12:30','13:30','14:30','15:30'):
                records.append(prepare(tuple(observations),fold,ticker,slot,start,cutoff,BASIS,invhash))
    path=run/'RISK_REFERENCE_MANIFEST.json';checksum=write_manifest(path,records,inventory)
    save(run/'risk_preparation_receipt.json',{'scope':'OFFLINE2019_PREFIX_ONLY','records':len(records),'ready':sum(r['status']=='READY' for r in records),'counts_min':min(r['count'] for r in records),'counts_max':max(r['count'] for r in records),'checksum':checksum,'inventory_hash':invhash,'units':'absolute_log_return','retrospective_source_corrections':'unknown historical vintage; inherited static cleaned source, not certified PIT'})
    return path,checksum,invhash


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--plan-sha256',required=True)
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    args.run_dir.mkdir(parents=True,exist_ok=False)
    clock=MarketClock('2010-07-01','2025-01-10')
    store=HistoricalSourceStore(Path('.'),args.plan,args.plan_sha256)
    facts=json.loads(Path('configs/hf1m_p019_verified_event_facts_v1.json').read_text())['events']
    print('Reading projected hourly source genesis for two stocks',flush=True)
    hours=store.hours()
    print('Hourly projected rows',len(hours),'Reading bounded M2 source anchors',flush=True)
    prices=store.minutes('m2_source',facts)
    producer=OriginalInputOnlySnapshotProducer(hours,prices,facts,clock,store.inventory_hash)
    model=ModelRegistry(Path('.'),Path('trading/track2/stage012/original_bundles.json')).load(2024)
    scheduler=SessionSignScheduler(clock)
    saved=[];audit=[];diagnostics=[];in_memory=[]
    for key in store.plan['samples']:
        origin=datetime.fromisoformat(key['origin_utc']);ticker=key['ticker']
        outcome=scheduled_signal(producer,model,scheduler,ticker,origin)
        if isinstance(outcome,Abstention):
            saved.append({'abstention':asdict(outcome)});print('ABSTAIN',key,outcome.reason,flush=True);continue
        record,lineage,frozen=outcome
        snapshot_result=producer.produce(model.bundle,ticker,origin)
        if isinstance(snapshot_result,Abstention):raise AssertionError('NONDETERMINISTIC_INPUT_GATE')
        snapshot=snapshot_result[0]
        with torch.inference_mode():
            z=float(model.model(torch.tensor(snapshot.values,dtype=torch.float32)[None],torch.tensor(snapshot.clock,dtype=torch.float32)[None])[0])
        diagnostics.append({'ticker':ticker,'origin_id':origin.isoformat(),'Mhat':z,'raw_magnitude':float(model.scale*np.expm1(max(z,0.))),'calibrated_magnitude':record.calibrated_magnitude,'snapshot_hash':lineage.input_hash,'masked_cells':lineage.masked_cells})
        saved.append({'signal':json.loads(record.to_json()),'session_sign_lineage':frozen.lineage_hash})
        audit.append(asdict(lineage));in_memory.append((snapshot,record,frozen))
        print('ISSUED',ticker,origin.isoformat(),record.calibrated_magnitude,'sign',record.direction,flush=True)
    save(args.run_dir/'signals_without_risk.json',saved)
    save(args.run_dir/'feature_lineage.json',audit)
    save(args.run_dir/'forecast_diagnostics.json',diagnostics)
    # Exact predeclared keys, prediction columns only; no score/label universe selection.
    old=Path('reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/F24/oos_scores.parquet')
    archive=pd.read_parquet(old,columns=['origin_id','ticker','Mhat','S2C-C3'],filters=[('ticker','in',['AAPL','COP']),('origin_id','in',[k['origin_utc'] for k in store.plan['samples']])])
    comparisons=[]
    for diag in diagnostics:
        rows=archive.loc[(archive.ticker==diag['ticker'])&(archive.origin_id==diag['origin_id'])]
        if len(rows)==1:
            r=rows.iloc[0]
            comparisons.append({'ticker':diag['ticker'],'origin_id':diag['origin_id'],'Mhat_delta':diag['Mhat']-float(r['Mhat']),'C3_delta':diag['calibrated_magnitude']-float(r['S2C-C3'])})
    save(args.run_dir/'original_forecast_parity.json',{'archive_path':str(old),'archive_sha256':file_hash(old),'shared_keys':len(comparisons),'not_universe_selection':True,'native_tensor_parity':'NOT_COMPARABLE:original full matched tensors not archived','comparisons':comparisons})
    # Bounded adversarial twins: mutate only in-memory source, never on disk.
    if in_memory:
        snap,rec,frozen=in_memory[0]
        delayed=replace(snap,dependencies=snap.dependencies+(replace(snap.dependencies[0],key='delayed_test',available_at=snap.nominal_origin+timedelta(minutes=10)),))
        later=issue(delayed,model,frozen.sign,clock)
        assert later.decision_utc>=snap.nominal_origin+timedelta(minutes=10)
        before=rec.to_json();future=(snap.ticker,clock.endpoint(snap.nominal_origin)-timedelta(minutes=1),'close')
        previous=producer.prices.pop(future,None)
        twin=issue(snap,model,frozen.sign,clock)
        assert twin.to_json()==before
        if previous is not None:producer.prices[future]=previous
        mutated=hours.loc[~((hours.ticker==snap.ticker)&(hours.hour_end_utc==snap.slots[-1]))].copy()
        missing=OriginalInputOnlySnapshotProducer(mutated,prices,facts,clock,store.inventory_hash).produce(model.bundle,snap.ticker,snap.nominal_origin)
        assert isinstance(missing,Abstention)
        invalid=producer.produce(model.bundle,'AAPL',datetime(2024,11,29,13,30,tzinfo=ZoneInfo('America/New_York')))
        assert isinstance(invalid,Abstention)
        save(args.run_dir/'adversarial_historical_twins.json',{'future_endpoint_deleted_or_absent':True,'prior_signal_unchanged':True,'delayed_decision_utc':later.decision_utc,'earliest_after_delay_utc':later.earliest_executable_observation_utc,'missing_current_input':asdict(missing),'half_day_after_close':asdict(invalid),'source_files_modified':False})
    print('Preparing isolated2019 prefix references',flush=True)
    path,checksum,invhash=prefix_references(store,clock,facts,args.run_dir)
    final=[]
    for snapshot,record,frozen in in_memory:
        slot=snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')
        reference=load_reference(path,record.fold_id,record.ticker,slot,BASIS,checksum,invhash)
        sized=issue(snapshot,model,frozen.sign,clock,reference)
        assert sized.calibrated_magnitude==record.calibrated_magnitude and sized.direction==record.direction
        final.append({'signal':json.loads(sized.to_json()),'session_sign_lineage':frozen.lineage_hash})
    save(args.run_dir/'signals_with_prefix_risk.json',final)
    save(args.run_dir/'source_reads.json',store.reads)
    save(args.run_dir/'session_sign_cache.json',[asdict(v) for v in scheduler.cache.values()])
    save(args.run_dir/'completion.json',{'status':'SIGNAL_ONLY_RUN_COMPLETE','issued':len(in_memory),'abstained':len(saved)-len(in_memory),'risk_sized':len(final),'orders_or_fills':0,'pnl_calculations':0,'post2024_market_reads':0,'plan_sha256':args.plan_sha256})


if __name__=='__main__':main()
