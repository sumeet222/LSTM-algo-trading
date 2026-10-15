# Offline reproduction

Use README's authoritative `.venv` setup and declared dependencies. Supply only legitimately owned source files referenced by the engineering profile, the archived raw daily formation/control/minute/SPY/action manifests and their exact hashes; a Git clone alone does not contain ignored archives. No .env or credentials are needed. Missing files or changed hashes must fail closed; do not run downloader/acquisition CLIs or fabricate replacement data. Use the same exchange-calendar dependency version. No model fitting, features, labels or economic metrics are constructed below.

Exact current checks:

```sh
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q tests/test_candidate_quality.py tests/test_stock_source.py tests/test_candle_cleanup.py tests/test_p2_handoff.py tests/test_clocks.py tests/test_labels.py tests/test_market_source.py
.venv/bin/python -B -m pytest -q tests/test_evidence.py tests/test_ft0_transforms.py tests/test_corporate_actions.py tests/test_stock_features.py tests/test_fullpeer_sp3.py
```

The exact local Pylance path is recorded in final_static_commands.json; substitute the installed extension dist on another machine. Expected0errors/0warnings, RuffPASS and109+109tests. Full-suite command `.venv/bin/python -B -m pytest -q` was not rerun in this reports-only session; inherited_full_suite_binding.json authenticates unchanged source/tests/scripts and the703-pass release. A future functional change requires a fresh stabilized full suite.

Reconstruct compact source/formation/calendar evidence below using existing validators and calendars. Choose a new output folder if ta_post_p411_reproduction already exists; never overwrite prior results. These are command transcripts, not new project modules or a parallel feature pipeline. Only symbol/timestamp/source_timeframe are deserialized for confirmation; numeric validators receive partitions ending before2024-07-01ET. Expected89,985keys,5×60formationrows,0gaps and calendar maxima1502/248/248. The source and code are bound in preflight/source_hash_verification/inherited_full_suite_binding.

```sh
.venv/bin/python -B - <<'PY'
import json, hashlib
from pathlib import Path
from collections import Counter
import pandas as pd
import pyarrow.parquet as pq
from lstm_data.calendar import schedule
from lstm_data.candidate_quality import audit_native, liquidity60, quality_summary
from lstm_data.fast_inventory import saved_session_audit
from lstm_data.fast_screen import verified_frame
from lstm_data.config import digest
from lstm_data.clocks import session_clock, execution_plan
out=Path('reports/data_audit/ta_post_p411_reproduction')
out.mkdir(exist_ok=False)
prior=Path('reports/data_audit/ta_provisional_source_integration_2026-10-13_163141')
profile=json.loads(Path('configs/track_a_provisional_engineering_v1.json').read_text())
manifest=Path(profile['source_manifest']);assert digest(manifest)==profile['source_manifest_sha256']
m=json.loads(manifest.read_text());symbols=tuple(profile['symbols']);assert tuple(m['ordered_universe'])==symbols==('AAPL','COST','CMCSA','SBUX','CME')
def save(name,d): (out/name).write_text(json.dumps(d,indent=2,default=str)+'\n')
allrefs={r['data']:r for refs in m['source_by_stock'].values() for r in refs}
keys={}; schemas=Counter(); ver=[]
for path,ref in allrefs.items():
 assert digest(Path(path))==ref['sha256'] and digest(Path(ref['manifest']))==ref['manifest_sha256']
 meta=json.loads(Path(ref['manifest']).read_text());assert meta['params']==ref['params'] and meta['sha256']==ref['sha256']
 p=ref['params'];assert all(p[k]==v for k,v in dict(timeframe='30Min',feed='sip',currency='USD',adjustment='split',asof='2025-06-30').items())
 assert meta.get('terminal_page_verified',meta.get('pagination_exhausted',False)) or 'All API pages exhausted' in meta.get('coverage_status','')
 f=pq.read_table(path,columns=['symbol','timestamp','source_timeframe']).to_pandas()
 assert not f.duplicated(['symbol','timestamp']).any() and len(f)==meta['rows']
 assert (f.source_timeframe=='30Min').all()
 assert f.timestamp.dt.tz is not None and (f.timestamp>=pd.Timestamp(p['start'])).all() and (f.timestamp<=pd.Timestamp(p['end'])).all()
 schema=pq.read_schema(path);schemas[str(schema)]+=1
 keys[path]=f
 ver.append(dict(data=path,sha256=ref['sha256'],manifest=ref['manifest'],manifest_sha256=ref['manifest_sha256'],status='PASS',rows=len(f),historical_available_at_column='available_at' in schema.names,confirmation_price_columns_read=False))
print('verified',len(ver),flush=True)
rows=[];annual=[];early=[];numeric=[];projection={}
cal=schedule('2019-12-18','2025-06-30')
for symbol in symbols:
 refs=m['source_by_stock'][symbol];frames={r['data']:keys[r['data']][keys[r['data']].symbol==symbol] for r in refs};days=[]
 for stamp,clock in cal.iterrows():
  matches=[r for r in refs if pd.Timestamp(r['params']['start'])<=clock.open and pd.Timestamp(r['params']['end'])>=clock.close-pd.Timedelta(nanoseconds=1)]
  assert len(matches)==1,(symbol,str(stamp),len(matches))
  ref=matches[0];f=frames[ref['data']]
  row=saved_session_audit(f,symbol,stamp.strftime('%Y-%m-%d'),clock.open,clock.close);row.update(source=ref['data'],source_sha256=ref['sha256'])
  days.append(row)
  if row['expected']!=13:early.append(row)
 for period,start,stop in [('PREHISTORY','2019-12-18','2020-06-30'),('MAIN','2020-07-01','2025-06-30')]:
  ds=[d for d in days if start<=d['session_et']<=stop];q=quality_summary(symbol,ds,[]);q.update(period=period,status='MEASURED',numeric_scope='KEYS_ONLY; malformed numeric inherited separately',first_session=ds[0]['session_et'],last_session=ds[-1]['session_et']);rows.append(q)
 for year in range(2020,2026):
  ds=[d for d in days if d['session_et']>='2020-07-01' and d['session_et'].startswith(str(year))];q=quality_summary(symbol,ds,[]);q.update(year=year,native95_pass=q['coverage_percent']>=95,status='MEASURED_KEYS');annual.append(q)
 allowed=[r for r in refs if pd.Timestamp(r['params']['end'])<pd.Timestamp('2024-07-01T04:00Z')]
 qa=audit_native(allowed,symbol,'2019-12-18','2024-06-30');assert qa['summary']['full_interval_verified']
 numeric.append(qa['summary'])
 allkeys=pd.concat(list(frames.values()),ignore_index=True);rth=sum(d['actual'] for d in days)
 projection[symbol]={'all_source_keys':len(allkeys),'RTH_keys':rth,'excluded_non_RTH_keys':len(allkeys)-rth,'duplicates_across_partitions':int(allkeys.duplicated(['symbol','timestamp']).sum())}
 print(symbol,rth,flush=True)
pd.DataFrame(rows).to_csv(out/'five_stock_native_quality.csv',index=False)
save('complete_five_stock_qa.json',dict(status='MEASURED',ordered_universe=symbols,source_manifest=str(manifest),source_manifest_sha256=digest(manifest),key_counts=rows,annual=annual,early_close_sessions=early,non_RTH=projection,numeric_train_development_and_prehistory=numeric,confirmation_numeric='NOT_REMEASURED; prior SHA-bound genuine_native_quality_summary.json malformed=0; only schema and keys read now',corporate_actions={s:'HOLD: independent vintage, price/inverse-volume units and complete cash-action evidence absent' for s in symbols},full_grid='SOURCE_GRID_COMPLETE',model_ready=False))
save('source_hash_verification.json',dict(status='PASS',unique_archives=len(ver),source_pairs=ver,schema_variants=dict(schemas),source_manifest_sha256=digest(manifest),publication='UNKNOWN; no available_at column in native archives'))
# Formation: existing exact raw daily archives only; existing validator and calculator.
liquid=[]
for symbol in symbols:
 for p in sorted(Path('data/raw').rglob('*.manifest.json')):
  meta=json.loads(p.read_text());par=meta.get('params',{})
  if par.get('timeframe')!='1Day' or symbol not in par.get('symbols','').split(','):continue
  if par.get('adjustment')!='raw' or par.get('asof')!='2020-07-01':continue
  data=p.with_name(p.name.replace('.manifest.json','.parquet'))
  ref=dict(data=str(data),manifest=str(p),sha256=digest(data),manifest_sha256=digest(p),params=par)
  f=verified_frame(ref);q=liquidity60(f,symbol);q.update(symbol=symbol,source=ref,evidence_class='RETROSPECTIVE_VENDOR_PROXY',original_records='ACTUAL_SOURCE_RECORD',PIT='UNKNOWN');liquid.append(q);break
assert len(liquid)==5
save('formation_liquidity_qa.json',dict(status='MEASURED',formation='2020-07-01',true_preceding_sessions=[str(d.date()) for d in schedule('2020-04-06','2020-06-30').index],stocks=liquid,independent_historical_membership='NOT_CERTIFIED'))
# Calendar-only denominators: no prices, features, labels, regimes or outcomes.
windows=[]
for label,start,stop in [('TRAIN','2020-07-01','2023-06-30'),('WF1','2023-07-01','2023-12-31'),('WF2','2024-01-01','2024-06-30')]:
 days=[str(d.date()) for d in schedule(start,stop).index];plans=[execution_plan(session_clock(d),i) for d in days for i in (1,2)]
 valid=[p for p in plans if p.calendar_valid];windows.append(dict(period=label,sessions=len(days),scheduled_origins=len(plans),calendar_compatible_origins=len(valid),calendar_incompatible=len(plans)-len(valid),by_origin={str(i):sum(p.origin==i for p in valid) for i in (1,2)},upper_bound=len(valid),inner_last63_sessions=days[-63:],measurement='MEASURED_CALENDAR_ONLY',retention='NOT_MEASURED',bound='CONDITIONAL_BOUND'))
save('calendar_source_upper_bound.json',dict(status='CONDITIONAL_BOUND',windows=windows,no_feature_target_or_outcome_computation=True))
# Verify existing sparse zero-overlay and all code bindings, without materializing full prices.
b=json.loads((prior/'candle_overlay_binding.json').read_text())
for pk,hk in [('fills_path','fills_sha256'),('unresolved_path','unresolved_sha256')]:
 p=Path(b[pk]);assert digest(p)==b[hk] and len(pd.read_csv(p))==0
for ref in b['code_bindings']:assert digest(Path(ref['path']))==ref['sha256']
assert digest(Path(b['profile']))==b['profile_sha256'] and digest(Path(b['source_manifest']))==b['source_manifest_sha256']
save('overlay_reconciliation.json',dict(status='PASS',binding_path=str(prior/'candle_overlay_binding.json'),binding_sha256=digest(prior/'candle_overlay_binding.json'),fills_path=b['fills_path'],fills_sha256=b['fills_sha256'],fills_rows=0,unresolved_path=b['unresolved_path'],unresolved_sha256=b['unresolved_sha256'],unresolved_rows=0,native_missing=sum(r['missing'] for r in rows),no_overlay_materialization=True,scientific_activation=False))
print('CENSUS_AND_FORMATION_PASS',flush=True)

q=json.loads((out/"complete_five_stock_qa.json").read_text())
for row in q["key_counts"]+q["annual"]:
 row["malformed_numeric_prior_sha_bound"]=row.pop("malformed");row["malformed_numeric_current_full_horizon"]="NOT_MEASURED";row["numeric_scope"]="Fresh numeric schema/plausibility only through2024-06-30; confirmation numeric zero inherited by unchanged source hash"
save("complete_five_stock_qa.json",q)
pd.DataFrame(q["key_counts"]).to_csv(out/"five_stock_native_quality.csv",index=False)
PY
```

Then reconstruct small action/unit, minute-key, SPY-identity and chronology examples. Raw controls/actual action records are preconfirmation; market/minute inventories read only key columns. No returns or labels are computed. ExpectedAAPL4×volume identity and raw-price differences0–$0.02; COSTmatchedone-candle identity;17,197SPYRTHkeys;12chronologyrows.

```sh
.venv/bin/python -B - <<'PY'
import json, hashlib
from pathlib import Path
from collections import Counter
from decimal import Decimal
import pandas as pd
import pyarrow.parquet as pq
from lstm_data.config import digest
from lstm_data.corporate_actions import raw_price_from_split_adjusted
from lstm_data.clocks import session_clock, execution_plan
from lstm_data.fast_screen import verified_frame
out=Path('reports/data_audit/ta_post_p411_reproduction');prior=Path('reports/data_audit/ta_provisional_source_integration_2026-10-13_163141');m=json.loads((prior/'complete_genuine_source_manifest.json').read_text());symbols=m['ordered_universe']
def save(n,d): (out/n).write_text(json.dumps(d,indent=2,default=str)+'\n')
def safe_full(ref):
 assert pd.Timestamp(ref['params']['end'])<pd.Timestamp('2024-07-01T04:00Z'),'CONFIRMATION_OUTCOME_READ_DENIED'
 return verified_frame(ref)
# Retained genuine original action records, not completeness or publication certificates.
action_path=Path('data/raw/alpaca/track_a_close_v1/actions-d7e39f2015b86602ac9c.json');ap=action_path.with_name(action_path.stem+'.manifest.json');am=json.loads(ap.read_text());assert digest(action_path)==am['sha256']
actions=json.loads(action_path.read_text())['corporate_actions'];split=next(r for r in actions['forward_splits'] if r['symbol']=='AAPL');divs=[r for r in actions['cash_dividends'] if r['symbol']=='AAPL' and r['ex_date'] in ['2020-05-08','2020-08-07','2020-11-06']]
rawp=next(Path('data/raw/alpaca/track_a_close_v1').glob('split_raw_30min_anchor*.manifest.json'));rm=json.loads(rawp.read_text());rawdata=rawp.with_name(rawp.name.replace('.manifest.json','.parquet'));assert digest(rawdata)==rm['sha256'];raw=pd.read_parquet(rawdata).iloc[0]
r=next(r for r in m['source_by_stock']['AAPL'] if pd.Timestamp(r['params']['start'])<=raw.timestamp<=pd.Timestamp(r['params']['end']));f=safe_full(r);adj=f[(f.symbol=='AAPL')&(f.timestamp==raw.timestamp)].iloc[0]
ratio=Decimal(str(split['new_rate']))/Decimal(str(split['old_rate']))
example=dict(symbol='AAPL',timestamp=str(raw.timestamp),split_record=split,raw_source=str(rawdata),raw_sha256=digest(rawdata),adjusted_source=r['data'],adjusted_sha256=r['sha256'],candidate_factor=str(ratio),OHLC={k:dict(raw=float(raw[k]),split_adjusted=float(adj[k]),converted=str(raw_price_from_split_adjusted(adj[k],ratio)),absolute_difference=str(abs(raw_price_from_split_adjusted(adj[k],ratio)-Decimal(str(raw[k]))))) for k in ['open','high','low','close']},volume=dict(raw=float(raw.volume),split_adjusted=float(adj.volume),expected_raw_times_factor=float(raw.volume)*float(ratio)),interpretation='RETROSPECTIVE_UNIT_SAMPLE_ONLY; archive publication=None; factor not certified for causal use')
# COST retained raw/split control on one prehistory day.
cp=next(Path('data/raw/alpaca/track_a_backup_candidate_v1/raw_split_control').glob('*.manifest.json'));cm=json.loads(cp.read_text());cd=cp.with_name(cp.name.replace('.manifest.json','.parquet'));assert digest(cd)==cm['sha256'];cf=pd.read_parquet(cd);ct=pd.Timestamp('2019-12-18T14:30Z');cr=cf[(cf.symbol=='COST')&(cf.timestamp==ct)].iloc[0]
rr=next(r for r in m['source_by_stock']['COST'] if pd.Timestamp(r['params']['start'])<=ct<=pd.Timestamp(r['params']['end']));af=safe_full(rr);ca=af[(af.symbol=='COST')&(af.timestamp==ct)].iloc[0]
cost=dict(timestamp=str(ct),raw_source=str(cd),raw_sha256=digest(cd),adjusted_source=rr['data'],adjusted_sha256=rr['sha256'],raw_close=float(cr.close),adjusted_close=float(ca.close),raw_volume=float(cr.volume),adjusted_volume=float(ca.volume),interpretation='One matched candle; equality cannot establish no later splits, cash actions, complete vintage or historical publication')
save('corporate_action_unit_samples.json',dict(status='PARTIAL',action_archive=str(action_path),sha256=digest(action_path),archive_requested_symbols=am['params']['symbols'],historical_publication=am['publication_time'],AAPL=example,AAPL_original_dividend_records=divs,dividend_arithmetic={'hypothetical_pre_split_one_share':'0.82 USD receivable for record rate 0.82; payment 2020-08-13 in original record','post_split_equivalent':'4 shares * 0.205 USD = 0.82 USD; cross-date rate arithmetic, not constant dividend policy or simultaneous entitlement'},COST=cost,CMCSA='NO_LOCAL_ACTION_ARCHIVE_FOR_SYMBOL',SBUX='NO_LOCAL_ACTION_ARCHIVE_FOR_SYMBOL',CME='NO_LOCAL_ACTION_ARCHIVE_FOR_SYMBOL; 2012 issuer split citation precedes prehistory and is not exhaustive',COST_cash_actions='NO_LOCAL_ACTION_ARCHIVE_FOR_SYMBOL; cash/special distributions and pay/record/ex dates require evidence',full_historical_conversion='HOLD'))
# Minute reference keys only; do not turn samples into a price panel or compute labels.
minute_refs=[];counts={s:Counter() for s in symbols}
for p in sorted(Path('data/raw').rglob('*.manifest.json')):
 meta=json.loads(p.read_text());q=meta.get('params',{})
 if q.get('timeframe')!='1Min':continue
 data=p.with_name(p.name.replace('.manifest.json','.parquet'));assert digest(data)==meta['sha256']
 f=pq.read_table(data,columns=['symbol','timestamp']).to_pandas();et=f.timestamp.dt.tz_convert('America/New_York')
 for s in symbols:
  for h in ['10:33','11:33','14:33','15:33']:
   counts[s][h]+=int(((f.symbol==s)&(et.dt.strftime('%H:%M')==h)).sum())
 minute_refs.append(dict(manifest=str(p),manifest_sha256=digest(p),data=str(data),sha256=digest(data),rows=len(f),params=q))
save('minute_reference_inventory.json',dict(status='PARTIAL',key_counts={s:dict(c) for s,c in counts.items()},source_refs=minute_refs,complete_five_stock_reference_source=False,prices_read=False,raw_minute_samples_not_fills=True,publication_and_units='NOT_CERTIFIED'))
# Same immutable SPY source identity as the last release, key/schema only even in confirmation.
old=json.loads(Path('reports/data_audit/ta_p4_11_2026-10-14_123129/raw_hashes_before.json').read_text());spy=[];spykeys=[]
for p in sorted(Path('data/raw/alpaca/track_a_spy_v1').glob('*.manifest.json')):
 meta=json.loads(p.read_text());q=meta['params'];data=p.with_name(p.name.replace('.manifest.json','.parquet'))
 assert q['symbols']=='SPY' and q['feed']=='sip' and q['adjustment']=='raw' and q['timeframe']=='30Min'
 assert digest(data)==meta['sha256']==old[str(data)]['sha256'] and digest(p)==old[str(p)]['sha256']
 f=pq.read_table(data,columns=['symbol','timestamp']).to_pandas();spykeys.extend(f.timestamp.tolist());spy.append(dict(manifest=str(p),sha256=digest(p),data=str(data),data_sha256=digest(data),rows=len(f),available_at_column='available_at' in pq.read_schema(data).names))
from lstm_data.calendar import schedule
expected=[t for _,r in schedule('2020-03-19','2025-06-30').iterrows() for t in pd.date_range(r.open,r.close,freq='30min',inclusive='left')];found=set(spykeys)
save('spy_source_identity.json',dict(status='MEASURED',config='configs/track_a_market_spy_v3.json',config_sha256=digest(Path('configs/track_a_market_spy_v3.json')),source_version='ALPACA_SIP_SPY_RAW_30MIN_V1',archives=spy,identical_to_prior_release_raw_hashes=True,RTH_expected=len(expected),RTH_observed=len(set(expected)&found),RTH_missing=len(set(expected)-found),publication='UNKNOWN',freshness='NOT_CERTIFIED',U1_U5='STRUCTURALLY_FEASIBLE_ONLY; no market features computed',course_series='data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv',course_sha256=digest(Path('data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv')),course_outcomes_read=False,course_obligation='NOT_RETIRED; explicit jointly reviewed amendment/compliance evidence pending',SPY_is_sixth_stock=False))
# Calendar with actual source key references; issuance and fills remain hypothetical.
chron=[]
for day,case in [('2020-07-01','ORDINARY'),('2021-03-12','PRE_DST'),('2021-03-15','POST_DST'),('2020-11-27','EARLY_CLOSE'),('2020-08-28','PRE_AAPL_SPLIT'),('2020-08-31','AAPL_SPLIT_EX_DATE')]:
 c=session_clock(day)
 for origin in (1,2):
  plan=execution_plan(c,origin);hour=c.hours[origin-1];ref=next(r for r in m['source_by_stock']['AAPL'] if pd.Timestamp(r['params']['start'])<=hour.start and pd.Timestamp(r['params']['end'])>=hour.end)
  chron.append(dict(case=case,session=day,origin=origin,raw_halfhour_starts_UTC=[str(hour.start),str(hour.start+pd.Timedelta(minutes=30))],source=ref['data'],source_sha256=ref['sha256'],completed_hour_end_UTC=str(hour.end),cutoff_ET=str(hour.end.tz_convert('America/New_York')),feature_market_own_step_available_at='UNKNOWN',issuance_kind=plan.issuance_kind,nominal_issuance_ET=str(plan.issuance.tz_convert('America/New_York')),hypothetical_minute_entry_ET=str(plan.entry.tz_convert('America/New_York')),hypothetical_minute_exit_ET=str(plan.exit.tz_convert('America/New_York')),calendar_reason=plan.reason,full_hours=len(c.hours),terminal_stub_start_UTC=str(c.terminal_stub.start),terminal_stub_end_UTC=str(c.terminal_stub.end),label_maturity='UNKNOWN; after nominal exit and all five genuine source publications',forecast_issuable='HOLD_SOURCE_PUBLICATION',entry_eligible='NOT_ESTABLISHED; independent of future label',label_valid='NOT_MEASURED',exit_filled='NOT_MEASURED'))
pd.DataFrame(chron).to_csv(out/'audit_chronology.csv',index=False)
print('SEMANTICS_PACKET_PASS');print('AAPL arithmetic',example['OHLC'],example['volume']);print('minute counts',counts)
PY
```

Decision/status narratives are manual evidence-qualified reports; recreate them from these observations and unchanged governing/ledger hashes, not by manufacturing a certificate. Inventory verification: recompute SHA-256 for each changed_paths_sha256.csv path; the inventory excludes itself and its detached SHA seal to avoid recursive hashes. Conservation: compare all preflight tracked/raw hashes with current bytes. No local temporary helper is required once these command transcripts are available.
