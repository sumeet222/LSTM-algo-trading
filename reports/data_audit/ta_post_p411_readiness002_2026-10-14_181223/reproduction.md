# Offline reproduction

Use README's authoritative environment setup with the repository `.venv`, declared packages and installed Pylance extension. Supply legitimately owned exact ignored native/SPY/daily/action/minute archives and journals referenced by the sealed evidence. A clone alone does not contain the raw sources. No .env, credentials, provider GET or subscription is needed. Missing or altered source hashes must fail closed.

The conditional D1 event is already registered; do not append it again. Read-only verification:

```sh
.venv/bin/python -B - <<'PY'
from pathlib import Path
import json
from lstm_data.ledger import verify_decision, read_ledger, current_blockers, pair_budget
ref = json.loads(Path('reports/data_audit/ta_post_p411_readiness002_2026-10-14_181223/decision_registration.json').read_text())['decision_ref']
verify_decision(Path('.').resolve(), ref)
events = read_ledger(Path('reports/audit/track_a_events.jsonl'))
assert sum(e['event_id'] == ref['decision_id'] for e in events) == 1
assert len(current_blockers(events)) == 7
assert pair_budget(events)['attempted_pairs'] == 0
print('Conditional decision present; production/scientific blockers preserved')
PY
```

Fresh check commands (exact argv, times and output are in the corresponding *_command.json / .txt):

```sh
.venv/bin/python -B -m pytest -q tests/test_candidate_quality.py tests/test_stock_source.py tests/test_candle_cleanup.py tests/test_p2_handoff.py tests/test_clocks.py tests/test_labels.py tests/test_market_source.py tests/test_evidence.py
.venv/bin/python -B -m pytest -q tests/test_stock_features.py tests/test_market_features.py tests/test_p2_market_closure.py tests/test_ft0_transforms.py tests/test_m2.py tests/test_fullpeer_sp3.py::test_indexed_view_shared_tables_masks_forgery_duplicates_and_real_rejection tests/test_fullpeer_sp3.py::test_strict_upstream_causality_and_policy_negatives
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
.venv/bin/ruff check .
git diff --check
```

Expected 143+113 cases, basic 155 Python files with 0 errors / 0 warnings, Ruff and diff PASS. Substitute the installed Pylance extension dist; the actual local path is in types_final_command.json. These synthetic source/feature/target/admission tests perform no real model fitting. The 703-test full-suite result is INHERITED, NOT FRESH, with identical source/tests/scripts/dependency/config bindings. A functional change requires a new stabilized full suite. The incidental duplicate during transcript generation was stopped and is excluded from release totals; completed green release logs remain intact.

This exact transcript recreates the new source/minute/window/calendar/sensitivity/count evidence using the existing readers, calendar and frozen dependency functions. It creates a NEW output folder and fails if that folder exists. Only source keys/schema and metadata are read in confirmation; no confirmation OHLCV, features, targets, returns or model performance are loaded/computed. No scientific certificate or fitted object is created. The existing T2 absence helper uses symbolic presence only: zero forced absence losses is not actual T2 validity.

```sh
.venv/bin/python -B - <<'PY'
from pathlib import Path
import json,csv,hashlib
from collections import Counter
import pandas as pd
import pyarrow.parquet as pq
from lstm_data.config import digest,fingerprint
from lstm_data.stock_source import StockCalendar
from lstm_data.m2 import scheduled_window
from lstm_data.clocks import execution_plan
from lstm_data.calendar import schedule
from lstm_data.remediation_plan import dependency_calendar
from lstm_data.universe_screen import t2_absence_bound
out=Path('reports/data_audit/ta002_offline_reproduction')
out.mkdir(exist_ok=False)
prior=Path('reports/data_audit/ta_post_p411_readiness_2026-10-14_150813')
eng=Path('reports/data_audit/ta_provisional_source_integration_2026-10-13_163141');mp=eng/'complete_genuine_source_manifest.json';m=json.loads(mp.read_text());symbols=tuple(m['ordered_universe']);assert symbols==('AAPL','COST','CMCSA','SBUX','CME')
def save(n,d):(out/n).write_text(json.dumps(d,indent=2,default=str)+'\n')
def csvsave(n,rows):
 with (out/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
allrefs={r['data']:r for refs in m['source_by_stock'].values() for r in refs};frames={};schemas=set();latest_receipts=[]
for path,ref in allrefs.items():
 assert digest(Path(path))==ref['sha256'] and digest(Path(ref['manifest']))==ref['manifest_sha256']
 meta=json.loads(Path(ref['manifest']).read_text());assert meta['params']==ref['params'] and meta['sha256']==ref['sha256'];p=ref['params']
 assert all(p[k]==v for k,v in dict(feed='sip',currency='USD',timeframe='30Min',adjustment='split',asof='2025-06-30').items())
 schema=pq.read_schema(path);assert not {'engineering_only','is_synthetic','available_at'}&set(schema.names);schemas.add(str(schema))
 f=pq.read_table(path,columns=['symbol','timestamp','source_timeframe']).to_pandas();assert len(f)==meta['rows'] and not f.duplicated(['symbol','timestamp']).any() and (f.source_timeframe=='30Min').all();frames[path]=f
 latest_receipts.append(meta.get('retrieved_at',meta.get('created_at','UNKNOWN')))
keys={s:set(pd.concat([frames[r['data']].loc[frames[r['data']].symbol==s,'timestamp'] for r in m['source_by_stock'][s]],ignore_index=True)) for s in symbols}
full=schedule('2019-12-18','2025-06-30');pregrid={t for day,c in full.iterrows() if day.strftime('%Y-%m-%d')<'2020-07-01' for t in pd.date_range(c.open,c.close,freq='30min',inclusive='left')};maingrid={t for day,c in full.iterrows() if day.strftime('%Y-%m-%d')>='2020-07-01' for t in pd.date_range(c.open,c.close,freq='30min',inclusive='left')}
source_rows=[]
for s in symbols:
 assert len(keys[s]&pregrid)==len(pregrid)==1736 and len(keys[s]&maingrid)==len(maingrid)==16261
 refs=m['source_by_stock'][s];r=next(r for r in refs if r['params']['start'].startswith('2020-07'))
 source_rows.append(dict(symbol=s,status='OBSERVED',archive_ref_manifest=str(mp),archive_ref_manifest_sha256=digest(mp),selector='source_by_stock.'+s,all_reference_pairs_digest=fingerprint([(x['data'],x['sha256'],x['manifest_sha256']) for x in refs]),archive_pairs=len(refs),sample_archive=r['data'],sample_archive_sha256=r['sha256'],sample_manifest=r['manifest'],sample_manifest_sha256=r['manifest_sha256'],feed='sip',adjustment='split',asof='2025-06-30',currency='USD',fields=pq.read_schema(r['data']).names,timestamp_basis='UTC interval start per immutable contract; independent original publisher vintage UNVERIFIED',request_parameters_observed=True,full_RTH_keys=17997,synthetic_markers=False,actual_publication='UNVERIFIED',action_version_available_at='UNVERIFIED',source_rights='UNVERIFIED',vendor_convention='DOCUMENTED_VENDOR_CONVENTION_IN_CACHED_REPO_NOTES; asof maps identity, not publication vintage',proxy='RESEARCHER_PROXY_PROPOSED only if separately selected'))
print('201 source pairs and89985keys reconciled',flush=True)
# True minute keys only; do not load prices or construct labels.
minute_refs=json.loads((prior/'minute_reference_inventory.json').read_text())['source_refs'];minute_keys={s:set() for s in symbols};minute_proof=[]
for r in minute_refs:
 assert digest(Path(r['manifest']))==r['manifest_sha256'] and digest(Path(r['data']))==r['sha256']
 f=pq.read_table(r['data'],columns=['symbol','timestamp']).to_pandas();q=r['params'];assert q['timeframe']=='1Min' and pd.Timestamp(q['end'])<pd.Timestamp('2024-07-01T04:00Z')
 if q['adjustment']=='raw' and q['feed']=='sip':
  for s in symbols:minute_keys[s].update(f.loc[f.symbol==s,'timestamp'])
 minute_proof.append(dict(manifest=r['manifest'],manifest_sha256=r['manifest_sha256'],data_sha256=r['sha256'],rows=len(f),adjustment=q['adjustment']))
cal=StockCalendar('2019-12-18','2024-06-30');plans=[]
for d in cal.days:
 if d<'2020-07-01':continue
 for o in (1,2):
  plan=execution_plan(cal.clock(d),o);period='TRAIN' if d<='2023-06-30' else 'WF1' if d<='2023-12-31' else 'WF2';plans.append((period,d,o,plan))
coverage=[];maskrows=[]
for period in ['TRAIN','WF1','WF2']:
 for origin in (1,2):
  ps=[(d,p) for pe,d,o,p in plans if pe==period and o==origin];valid=[(d,p) for d,p in ps if p.calendar_valid]
  for s in symbols:
   entry=sum(p.entry in minute_keys[s] for _,p in valid);exitn=sum(p.exit in minute_keys[s] for _,p in valid);both=sum(p.entry in minute_keys[s] and p.exit in minute_keys[s] for _,p in valid)
   coverage.append(dict(period=period,origin=origin,symbol=s,scheduled_origins=len(ps),calendar_compatible_origin_bound=len(valid),required_minute_keys=2*len(valid),observed_raw_entry_keys=entry,observed_raw_exit_keys=exitn,observed_both_endpoint_pairs=both,missing_required_keys=2*len(valid)-entry-exitn,reference_presence_status='MEASURED_SOURCE_KEYS_ONLY',actual_publication='UNKNOWN',label_valid='NOT_MEASURED',fill_status='NOT_EVIDENCED',genuine_G3_retention='NOT_MEASURED'))
   good=0
   for d,p in valid:
    steps=scheduled_window(cal,d,origin);assert len(steps)==48
    good+=all(st.start in keys[s] and st.start+pd.Timedelta(minutes=30) in keys[s] for st in steps)
   maskrows.append(dict(period=period,origin=origin,symbol=s,calendar_compatible_origin_bound=len(valid),all48_two_native_halfhours_present=good,publication_certified_origins='NOT_CERTIFIED',action_units_certified='NOT_CERTIFIED',FT0_48x16_status='NOT_MEASURED',status='MEASURED_NATIVE_KEY_MASK_ONLY'))
csvsave('minute_execution_coverage.csv',coverage);csvsave('native_window_key_bounds.csv',maskrows)
validplans=[(pe,d,o,p) for pe,d,o,p in plans if p.calendar_valid];complete_five=sum(all(p.entry in minute_keys[s] and p.exit in minute_keys[s] for s in symbols) for _,_,_,p in validplans)
save('minute_key_inventory.json',dict(status='MEASURED_KEYS_ONLY',source_proofs=minute_proof,source_inventory_sha256=digest(prior/'minute_reference_inventory.json'),nominal_valid_origins=len(validplans),required_symbol_minute_keys=sum(r['required_minute_keys'] for r in coverage),observed_required_keys=sum(r['observed_raw_entry_keys']+r['observed_raw_exit_keys'] for r in coverage),complete_five_endpoint_origin_keys=complete_five,not_a_G3_retention_rate=True,source_publication_and_units='UNKNOWN',prices_read=False,all_cached_minute_intersections={s:len(v) for s,v in minute_keys.items()}))
# Existing calendar-only warm-up dependency implementation; not real feature evaluation.
dep=dependency_calendar();zero_loss=t2_absence_bound(cal,())
save('structural_source_bounds.json',dict(status='CONDITIONAL_BOUND',bound_only=True,stock_rows=maskrows,native_complete_48_windows_all_five=sum(all(all(st.start in keys[s] and st.start+pd.Timedelta(minutes=30) in keys[s] for st in scheduled_window(cal,d,o)) for s in symbols) for _,d,o,p in validplans),source_grid_complete=89985,prehistory_per_stock=1736,existing_warmup_dependency=dep,T2_source_absence_forced_training_failures=len(zero_loss),T2_values_evaluated=False,indicator_warmup_actual='NOT_MEASURED; expected slot capacity is not valid feature updates',M2_fully_mature_five_stock_outcomes='NOT_MEASURED',no_scaler_floor_or_feature_fit=True))
# Read-only proposed latency sensitivity counts. These are hypothetical schedules, never source certificates.
sens=[]
for latency in [0,30,60,120,300,301]:
 for pe in ['TRAIN','WF1','WF2']:
  ps=[p for period,_,_,p in validplans if period==pe]
  sens.append(dict(policy_id='RESEARCHER_PROXY_PROPOSED:LATENCY:v1',period=pe,latency_seconds=latency,calendar_origin_bound=len(ps),latest_step_available_at_own_cutoff_if_assumed=len(ps) if latency==0 else 0,latest_step_available_by_nominal_issue_if_assumed=len(ps) if latency<=120 else 0,latest_step_available_by_max5minute_issue_if_assumed=len(ps) if latency<=300 else 0,actual_source_certified=False,scientific_G2='HOLD',feature_or_label_values_computed=False))
csvsave('latency_sensitivity_counts.csv',sens)
# Compact source/market evidence, using exact unchanged source references.
spy=json.loads((prior/'spy_source_identity.json').read_text())
for r in spy['archives']:
 assert digest(Path(r['manifest']))==r['sha256'] and digest(Path(r['data']))==r['data_sha256']
source_rows.append(dict(symbol='SPY',status='OBSERVED',archive_ref_manifest=str(prior/'spy_source_identity.json'),archive_ref_manifest_sha256=digest(prior/'spy_source_identity.json'),selector='archives',archive_pairs=len(spy['archives']),feed='sip',adjustment='raw',asof='2025-06-30',currency='USD',fields=pq.read_schema(spy['archives'][0]['data']).names,full_RTH_keys=17197,actual_publication='UNVERIFIED',action_version_available_at='UNVERIFIED',source_rights='UNVERIFIED',course_equivalence='REJECTED: ETF proxy is not independent course-series certificate'))
save('source_evidence_matrix.json',dict(namespace='CAND:TRACK_A_CORE5:PREPARATION:002',status_vocabulary=['OBSERVED','DOCUMENTED_VENDOR_CONVENTION','RESEARCHER_PROXY_PROPOSED','UNVERIFIED','REJECTED'],evidence=source_rows,source_pairs_verified=201,SPY_pairs_verified=11,fields_deserialized='Only symbol,timestamp,source_timeframe; schema and metadata for prices, no confirmation OHLCV deserialized',publisher_receipt_basis='Retrospective received_at/http200 are acquisition evidence, not historical publication',corporate_action_unit_sample=dict(path=str(prior/'corporate_action_unit_samples.json'),sha256=digest(prior/'corporate_action_unit_samples.json')),formation_liquidity=dict(path=str(prior/'formation_liquidity_qa.json'),sha256=digest(prior/'formation_liquidity_qa.json')),right_to_use_or_transfer='UNVERIFIED'))
# Bounded acquisition proposal only. Historical M2 prehistory references are additional to train/dev.
first_day=min(dep['lower_bounds'][f'M2_origin{i}_60_matured_sessions'] for i in (1,2));need_days=[d for d in cal.days if first_day<=d<'2020-07-01' and all(execution_plan(cal.clock(d),o).calendar_valid for o in (1,2))]+sorted({d for _,d,_,_ in validplans})
required={(s,p.entry) for d in need_days for o in (1,2) for p in [execution_plan(cal.clock(d),o)] for s in symbols}|{(s,p.exit) for d in need_days for o in (1,2) for p in [execution_plan(cal.clock(d),o)] for s in symbols}
existing=sum(t in minute_keys[s] for s,t in required);query_windows=len({t for _,t in required});pilot=['2020-07-01','2020-08-31','2021-03-12','2021-03-15']
save('minute_acquisition_plan_NOT_AUTHORIZED.json',dict(status='PROPOSED_NOT_AUTHORIZED_NO_GET',purpose='Exact nominal raw1Min endpoint references; does not establish real fills, slippage, borrow or latency',candidate_symbols=symbols,train_development_keys=sum(r['required_minute_keys'] for r in coverage),historical_M2_prehistory_start=first_day,extra_prehistory_days=len(need_days)-len({d for _,d,_,_ in validplans}),required_symbol_minute_keys_including_M2_prehistory=len(required),existing_exact_raw_keys=existing,new_symbol_minute_keys_needed=len(required)-existing,pilot=dict(dates=pilot,base_requests=16,max_pages_per_request=2,max_lifetime_attempts_per_page=3,worst_additional_transport_attempts=96,max_new_archive_and_journal_bytes=16*1024**2),full_endpoint_only_plan=dict(base_requests=query_windows,max_pages_per_request=2,max_lifetime_attempts_per_page=3,worst_additional_transport_attempts=query_windows*6,page_limit=10000,max_response_bytes=65536,storage_hard_cap_bytes=128*1024**2,expected_bar_rows_upper_bound=len(required),estimated_raw_record_bytes_at128=len(required)*128,minute_intervals='One-minute UTC intervals at each required event, all missing symbols grouped; reuse cached keys, reject wider/unapproved intervals; dates stop2024-06-30',pacing='At most100sends/minute if later authorized'),inherited_source_completion_budget='292/1000 prior source sends;708remaining recorded, not a new authorization. Full endpoint plan exceeds that ceiling; requires explicit reconciled plan/budget amendment. No counter reset or reservation.',permission_required=['Entitlement and allowed use','Exact requests/feed/raw/asof/currency/timeframe','Cumulative,page,lifetime,pacing/storage bounds','Historical publication/action/source evidence acceptance','No confirmation queries'],no_queries_executed=True))
# Chronology with overnight event separation and explicit source/entry/label flags.
cases=[]
for day,label in [('2020-07-01','ORDINARY'),('2021-03-12','DST_FRIDAY'),('2021-03-15','DST_MONDAY'),('2020-11-27','EARLY_CLOSE'),('2020-08-28','PRE_SPLIT_FRIDAY'),('2020-08-31','SPLIT_MONDAY')]:
 for origin in (1,2):
  clock=cal.clock(day);p=execution_plan(clock,origin);step=clock.hours[origin-1];prev=cal.steps[cal._positions[(day,origin)]-1];ref=next(r for r in m['source_by_stock']['AAPL'] if pd.Timestamp(r['params']['start'])<=step.start<=pd.Timestamp(r['params']['end']))
  cases.append(dict(case=label,day=day,origin=origin,raw_starts_UTC=[str(step.start),str(step.start+pd.Timedelta(minutes=30))],hour_end_UTC=str(step.end),hour_end_ET=str(step.end.tz_convert('America/New_York')),stock_market_available_at='UNKNOWN',required_feature_cutoff=str(p.cutoff),nominal_issue=str(p.issuance),issuance_kind=p.issuance_kind,nominal_entry=str(p.entry),nominal_exit=str(p.exit),calendar_reason=p.reason,minutes_if_valid=240 if p.calendar_valid else None,previous_full_step_end=str(prev.end),previous_full_step_session=prev.session,terminal_stub=[str(clock.terminal_stub.start),str(clock.terminal_stub.end)],archive=ref['data'],sha256=ref['sha256'],source_keys_present=all(step.start+pd.Timedelta(minutes=n) in keys['AAPL'] for n in [0,30]),forecast_issuable='UNKNOWN_PUBLICATION_ACTION_UNITS',entry_eligible='NOT_ESTABLISHED; FUTURE_EXIT_NOT_AN_INPUT',all_five_label_reference_keys_present=all(p.entry in minute_keys[s] and p.exit in minute_keys[s] for s in symbols) if p.calendar_valid else False,label_valid='NOT_MEASURED',label_maturity='UNKNOWN; >=scheduled exit and every actual source publication',exit_filled='NOT_EVIDENCED',share_epoch='AAPL source splits applied retrospectively asof2025; pre/post2020-08-31 economic epoch recorded separately, publication UNKNOWN'))
save('chronology_cases.json',dict(status='CALENDAR_AND_SOURCE_KEYS_ONLY',cases=cases,overnight_rule='No synthetic overnight hourly steps; last full Friday15:30ET -> first full Monday10:30ET. Friday terminal stub16:00ET is daily source only. Daily histories locked to prior completed session; no Monday close in Monday morning.',real_prices_or_targets_computed=False))
print('OFFLINE_OBSERVATIONS_PASS',dict(required_train_dev_keys=sum(r['required_minute_keys'] for r in coverage),observed=sum(r['observed_raw_entry_keys']+r['observed_raw_exit_keys'] for r in coverage),complete_five=complete_five,firstM2=first_day,fullqueries=query_windows,required_all=len(required),existing=existing),flush=True)
PY
```

Expected: 89,985 native RTH keys; 1,998 complete 48-step native-key windows; 19,980 nominal train/development minute keys, 4 observed and zero complete five-stock endpoint cohorts. M2 prehistory starts 2020-03-25 and adds 68 days; the thin full plan covers 21,340 symbol-minute keys and 4,268 base queries. All acquisition numbers are proposals; no GET is executed. These measurements are source/calendar coverage and bounds, never genuine FT0/TG0 retention.

Existing synthetic tests and nonpromotion_checks.json verify source/clock/certificate/order/engineering-mode guards; no real candidate source object exists to promote. Decision registration uses the existing source-controlled append_event API and the immutable recorded human-attributed decision. Temporary local helpers are not required project dependencies; the read-only command transcripts here reproduce the factual outputs on the same verified archives. Documentary narrative conclusions are evidence-qualified reports, not generated approvals.
