# Reproduction and safe review

Use the repository's documented `.venv` setup with declared dev/neural extras. Run commands from the repository root. No manual PYTHONPATH or machine-specific raw path is needed. The Git HEAD is bb654a8f541b184d7f649b45f29507b23fb710f8 with the uncommitted changes enumerated in changed_file_inventory.csv; this work is not yet available from HEAD alone.

Supply the exact legitimately accessible archives/manifests named in canonical_source_action_clock_manifest.json. Raw data and local compressed conditional stores are intentionally gitignored. Their redistribution/teammate transfer is not authorized by the present rights assumption; another machine needs its own legitimate access and the exact approved source identities. No download, subscription, credential or provider GET is performed by these recipes.

Reconstruct to a NEW output namespace, retaining the original evidence. This reproduces numerical feature/target populations; actual construction timestamps and derived artifact identities appropriately change on a new run. The existing snapshot's SHA identities are authoritative for reviewing this packet. `constructed_at` is factual preprocessing completion metadata; `window.fitted_at` is the request-time clock recorded before preprocessing. Neither is a historical model/publication timestamp. Historical stop boundaries identify fitting membership only.

```sh
.venv/bin/python -B -m lstm_data.pretraining_g3 \
  --authority-binding reports/data_audit/ta_pretraining_g3_2026-10-14_185935/preparation_authority_binding.json \
  --report reports/data_audit/ta_pretraining_g3_rebuild_NEW
```

The CLI refuses an existing dataset manifest; immutable old outputs are never overwritten. It binds the exact human responses, source manifests, source bytes, code and candidate universe; missing/changed source or approval evidence fails closed. Numerical reads are Arrow-filtered before pandas materialization to dates strictly before July2024.

Review the active conditional stock input safely:

```sh
.venv/bin/python -B - <<'END_CANDIDATE_REVIEW'
from pathlib import Path
from lstm_data.config import digest
from lstm_data.pretraining_store import load_candidate_view
root = Path.cwd()
p = Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935/canonical_dataset_manifest.json')
view = load_candidate_view(root, {'path': str(p), 'sha256': digest(p)}, 'WF1_REFIT')
x, y = view.window('2023-07-05', 1)
assert x.shape == (5, 48, 16) and y.shape == (5,)
print(x.shape, y.shape, view.preparation.preparation_id)
# view is candidate review data. It is not a scientific neural Permission or FitData.
END_CANDIDATE_REVIEW
```

The loader returns float64 audit arrays. A future reviewed model adapter must validate finite float32 conversion and all model/session-batching contracts; no synthetic flag or old checkpoint is an admissible fallback. The present package forbids model fitting and pair reservation regardless of successful preprocessing.

Optional SPY reconstruction, all-window validation and descriptive state diagnostics below use maintained guarded source/math/loader functions. These are audit glue transcripts, not hidden data modifications. Change the output namespace when reconstructing; keep the original packet immutable.


## Optional separately approved SPY build


```python
from pathlib import Path
import json
from lstm_data.pretraining_policy import load_authority
from lstm_data.pretraining_store import load_tables,read_preparation
from lstm_data.pretraining_market import run_market
root=Path.cwd();out=Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935');build=out/'build_v4'
m=json.loads((build/'canonical_dataset_manifest.json').read_text());b=m['authority']
a=load_authority(root,b['policy_ref'],b['approval_ref'])
base=load_tables(a,m['canonical_store'])
preps={key:read_preparation(root,ref) for key,ref in m['preparations'].items()}
annex=json.loads((out/'SPY_annex_binding.json').read_text())
report=out/'market_v2';report.mkdir()
summary=run_market(base,preps,annex,report)
print(json.dumps({'candidate_preparation_computed':summary['candidate_preparation_computed'],'matched_masks':summary['matched_masks']}))
```


## All genuine windows and targets audit


```python
from pathlib import Path
import json,hashlib
import numpy as np
from lstm_data.config import digest
from lstm_data.pretraining_store import load_candidate_view
out=Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935');p=out/'canonical_dataset_manifest.json'
ref={'path':str(p),'sha256':digest(p)};rows=[json.loads(s) for s in (out/'build_v4/origin_admission.jsonl').read_text().splitlines()]
summary={};hasher=hashlib.sha256()
for period,key in [('TRAIN','WF1_REFIT'),('WF1','WF1_REFIT'),('WF2','WF2_REFIT')]:
 v=load_candidate_view(Path.cwd(),ref,key);count=0;totalcells=0
 for row in rows:
  if row['period']!=period:continue
  x,y=v.window(row['session'],row['origin']);assert x.shape==(5,48,16) and y.shape==(5,)
  assert np.isfinite(x).all() and np.isfinite(y).all()
  hasher.update(x.astype('<f8').tobytes());hasher.update(y.astype('<f8').tobytes())
  count+=1;totalcells+=x.size
 summary[period]={'origins_materialized_and_checked':count,'finite_FT0_cells':totalcells,'finite_TG0_targets':count*5,'dense_windows_saved':False,'preparation_id':v.preparation.preparation_id}
summary['transient_numeric_trace_sha256']=hasher.hexdigest();summary['NOT_FOR_TRAINING']=True
(out/'all_real_windows_and_targets_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
```


## Conditional descriptive regime retention


```python
from pathlib import Path
import gzip,json,math
import numpy as np
import pandas as pd
from lstm_data.config import digest
from lstm_data.pretraining_store import load_candidate_view
from lstm_data.pretraining_market import conditional_vector
from lstm_data.market_features import MarketMeasures
from lstm_data.regime_diagnostics import Regime,occupancy
out=Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935');root=Path.cwd();build=out/'build_v4'
manifest=json.loads((build/'canonical_dataset_manifest.json').read_text())
market=json.loads((out/'market_v2/conditional_market_retention.json').read_text())
blob=out/'market_v2/canonical_market_components.json.gz';assert digest(blob)==market['canonical_store']['sha256']
raw=json.loads(gzip.decompress(blob.read_bytes()))
measures=[]
for item in raw['measures']:
 r=dict(item);r['timestamp']=pd.Timestamp(r['timestamp']);r['evidence_ids']=tuple(r['evidence_ids']);measures.append(MarketMeasures(**r))
admissions=[json.loads(line) for line in (build/'origin_admission.jsonl').read_text().splitlines()]
regimes={};state_rows=[]
for period,key,start,stop in [('TRAIN','WF1_REFIT','2020-07-01','2023-07-01'),('WF1','WF1_REFIT','2023-07-01','2024-01-01'),('WF2','WF2_REFIT','2024-01-01','2024-07-01')]:
 p=raw['preparations'][key];w=p['window'];lo=pd.Timestamp(w['start']);hi=pd.Timestamp(w['stop'])
 vectors={r.timestamp:conditional_vector(r,p['hourly_floor'],p['daily_floor']) for r in measures}
 fitted=[v[1] for at,v in vectors.items() if lo<=at<hi and v is not None]
 threshold=float(np.median(fitted))
 states=[];selected=[r for r in admissions if r['period']==period]
 for row in selected:
  at=pd.Timestamp(row['cutoff']);v=vectors[at];assert v is not None
  # Volatility uses training-only U2 median; positive robust scaling preserves this split.
  # Trend uses standardized U5 exactly as existing regime_diagnostics.classify.
  std_u5=(v[4]-p['centers'][4])/p['scales'][4] if p['methods'][4]!='CONSTANT' else 0.
  trend='BULL' if std_u5>0 else 'BEAR' if std_u5<0 else 'NEUTRAL'
  vol='HIGH' if v[1]>threshold else 'LOW'
  states.append(Regime((row['session'],row['origin']),trend,vol,'CANDIDATE:'+row['cutoff'],key,at))
  state_rows.append({'period':period,'session':row['session'],'origin':row['origin'],'trend_standardized_U5':trend,'raw_U5_sign':'POSITIVE' if v[4]>0 else 'NEGATIVE' if v[4]<0 else 'ZERO','volatility':vol,'candidate_admissible':row['candidate_supervised_admissible']})
 days=tuple(d for d in load_candidate_view(root,{'path':str(build/'canonical_dataset_manifest.json'),'sha256':digest(build/'canonical_dataset_manifest.json')},key).base.history.calendar.days if start<=d<stop)
 summary=occupancy(tuple(states),days)
 byvol={}
 for label in ['HIGH','LOW']:
  rows=[r for r in state_rows if r['period']==period and r['volatility']==label]
  byvol[label]={'nominal':len(rows),'eligible':sum(r['candidate_admissible'] for r in rows),'retention':sum(r['candidate_admissible'] for r in rows)/len(rows) if rows else None}
 summary.update({'training_only_raw_U2_median':threshold,'training_unique_timestamps':len(fitted),'volatility_retention':byvol,'retention_gap_percentage_points':100*abs(byvol['HIGH']['retention']-byvol['LOW']['retention']) if all(byvol[l]['retention'] is not None for l in byvol) else None,'designation':'ASSUMPTION_CONDITIONAL_NO_PERFORMANCE_INFERENCE','trend_basis':'STANDARDIZED_U5_SIGN_AS_EXISTING_regime_diagnostics.classify; raw U5 sign retained separately'})
 regimes[period]=summary
(out/'conditional_regime_retention.json').write_text(json.dumps(regimes,indent=2)+'\n')
(out/'conditional_origin_states.jsonl').write_text('\n'.join(json.dumps(r,sort_keys=True) for r in state_rows)+'\n')
# One final package manifest refers to one active stock store and one market-state store.
manifest['base_build_manifest']={'path':str(build/'canonical_dataset_manifest.json'),'sha256':digest(build/'canonical_dataset_manifest.json')}
manifest['market_annex']=json.loads((out/'SPY_annex_binding.json').read_text())
manifest['market_components']=market['canonical_store']
manifest['market_recipe']='lstm_data.pretraining_market.conditional_vector + bound prefix floor/scaler recipes; 46/48 separate masks; neutral fill only after standardization if needed'
manifest['final_scope']='PERMANENT_CANDIDATE_PREPARATION_ONLY_PER_LIVE_USER_DECISION'
manifest['historical_build_attempts']={'build_v1':'Nonrelease development observation before independent oracle integration','build_v2':'Intentionally fail-closed on code change during build; evidence retained','build_v3':'Superseded before release by stricter nonsynthetic-prefix guard', 'build_v4':'Active guarded canonical build, all independent oracles pass'}
(out/'canonical_dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
r=json.loads((build/'genuine_G3_population_and_retention.json').read_text())
r['base_build_retention_ref']={'path':str(build/'genuine_G3_population_and_retention.json'),'sha256':digest(build/'genuine_G3_population_and_retention.json')}
r['regime_retention']={'path':str(out/'conditional_regime_retention.json'),'sha256':digest(out/'conditional_regime_retention.json')}
r['market_candidate_measured']={'TRAIN':1502,'WF1':248,'WF2':248,'exact_intersection_with_stock':True,'all_required_endpoints_valid':True,'all_windows_at_least46_of48':True,'market_source':'RAW_SPY_ETF_PRICE_STATE_PROXY','NOT_FOR_TRAINING':True}
r['MC0_MC1_E5']='CONDITIONAL_STOCK_MARKET_INPUTS_COMPUTED; EXTERNAL_AND_PRODUCTION_TRAINING_HOLD; E5_PEER_DERIVATION_NOT_ACTIVATED'
r['scope']='CANDIDATE_ONLY; both observed clocks and rights remain uncertified'
(out/'genuine_G3_population_and_retention.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:{'HIGH':v['volatility_retention']['HIGH'],'LOW':v['volatility_retention']['LOW'],'gap_pp':v['retention_gap_percentage_points']} for k,v in regimes.items()}))
```


## Warmup, clipping counts and training target diagnostics


```python
from pathlib import Path
from collections import Counter
import json,math
import numpy as np
from lstm_data.config import digest
from lstm_data.ft0_transforms import ORDER,SCALED
from lstm_data.pretraining_store import load_candidate_view
out=Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935');p=out/'canonical_dataset_manifest.json'
v=load_candidate_view(Path.cwd(),{'path':str(p),'sha256':digest(p)},'WF1_REFIT');base=v.base
flags=Counter(flag for c in base.components.values() for flag in c.flags)
first=min(base.origin_steps);positions=base.origin_steps[first];earliest=base.history.calendar.steps[positions[0]]
q={'quality_flags':dict(flags),'first_nominal_origin':first,'first_window_step':{'session':earliest.session,'slot':earliest.slot,'end':str(earliest.end)},'zero_range_note':'If no real zero-range occurs, explicit zero-range oracle remains synthetic; never fabricate a real example','M2_actual_first_window_histories':{str(o):{'prior60_sessions':base.history.calendar.previous_origins(earliest,o)[-60:],'all_five_history_valid':all(base.m2[s,earliest.session,o].reason=='M2_HISTORY_VALID' for s in v.base.history.authority.policy['universe'])} for o in (1,2)}}
# Clip diagnostics use canonical keys, not repeated 48-step appearances.
unique={}
for (day,origin),indices in base.origin_steps.items():
 if day>='2023-07-01':continue
 for pos in indices:
  step=base.history.calendar.steps[pos]
  if step.session<'2020-07-01':continue
  for symbol in v.base.history.authority.policy['universe']:
   values=v.row(symbol,pos,origin)
   if values is None:continue
   for feature in SCALED:
    key=(symbol,feature,step.session,origin if feature=='M2' else step.slot)
    val=values[ORDER.index(feature)]
    if key in unique:assert unique[key]==val
    unique[key]=val
clipping={}
for feature in SCALED:
 a=np.asarray([val for key,val in unique.items() if key[1]==feature])
 clipping[feature]={'canonical_training_observations':len(a),'hypothetical_abs_gt':{str(level):int(np.sum(np.abs(a)>level)) for level in (3,5,10)},'actually_clipped':False}
q['hypothetical_clipping']=clipping
rows=[r for r in base.panels.values() if '2020-07-01'<=r.session<'2023-07-01'];mads=[r.median_mad[1] for r in rows if r.median_mad is not None]
q['training_target_diagnostics']={'origins':len(rows),'zero_MAD':sum(m==0 for m in mads),'MAD_below_epsilon':sum(m<v.preparation.target_epsilon for m in mads),'epsilon':v.preparation.target_epsilon,'MAD_median':float(np.median(mads)),'maximum_absolute_TG0':max(abs(x) for r in rows for x in v.window(r.session,r.origin)[1]),'no_clipping':True,'no_model_performance_computed':True}
(out/'conditional_feature_quality_and_warmup.json').write_text(json.dumps(q,indent=2)+'\n')
print(json.dumps({'quality_flags':q['quality_flags'],'first_window_step':q['first_window_step'],'training_target_diagnostics':q['training_target_diagnostics']}))
```


## Exact verification commands

```sh
env VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B -m pytest -q
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-vscode-pylance-extension>/dist
.venv/bin/ruff check .
git diff --check
```

The exact local Option A Pylance path and command result are in types_final_command.json and checks.json. In VS Code, select the repository `.venv/bin/python`, keep basic checking and installed Pylance stubs, reload the Python language server/Problems view, and verify zero error-level diagnostics. Final editor refresh/Problems parity is human-confirmed, not claimed from a CLI run.

No Git staging/commit/push is authorized. For later integration, review the explicit inventory and session report; stage only approved source, test, narrow .gitignore, decision and metadata/report paths. Exclude compressed conditional tables, raw data, vendor journals, secrets and unrelated prior work. Fetch and reassess the dirty shared branch before any separately authorized integration; do not stash/reset/pull over these changes.

## Actual market-window,21-channel and independent U1–U5 audit

```python
from pathlib import Path
import json,gzip,hashlib,math
import numpy as np
import pandas as pd
from lstm_data.config import digest
from lstm_data.pretraining_store import load_candidate_view
from lstm_data.pretraining_market import conditional_vector,ensure_annex,load_conditional_spy
from lstm_data.market_features import MarketMeasures
out=Path('reports/data_audit/ta_pretraining_g3_2026-10-14_185935');p=out/'canonical_dataset_manifest.json'
m=json.loads(p.read_text());ref={'path':str(p),'sha256':digest(p)}
blob=Path(m['market_components']['path']);assert digest(blob)==m['market_components']['sha256']
market=json.loads(gzip.decompress(blob.read_bytes()))
measures=[]
for item in market['measures']:
 r=dict(item);r['timestamp']=pd.Timestamp(r['timestamp']);r['evidence_ids']=tuple(r['evidence_ids']);measures.append(MarketMeasures(**r))
rows=[json.loads(line) for line in (out/'build_v4/origin_admission.jsonl').read_text().splitlines()]
summary={};h=hashlib.sha256()
for period,key in [('TRAIN','WF1_REFIT'),('WF1','WF1_REFIT'),('WF2','WF2_REFIT')]:
 view=load_candidate_view(Path.cwd(),ref,key);ensure_annex(view.base.history.authority,m['market_annex'])
 recipe=market['preparations'][key];vectors={r.timestamp:conditional_vector(r,recipe['hourly_floor'],recipe['daily_floor']) for r in measures}
 centers=np.asarray(recipe['centers']);scales=np.asarray(recipe['scales']);constant=np.asarray([k=='CONSTANT' for k in recipe['methods']])
 count=0
 for row in rows:
  if row['period']!=period:continue
  x,y=view.window(row['session'],row['origin']);indices=view.base.origin_steps[row['session'],row['origin']]
  raw=[vectors.get(view.base.history.calendar.steps[pos].end) for pos in indices]
  mask=np.asarray([v is not None for v in raw]);assert mask[-1] and int(mask.sum())>=46
  transformed=np.asarray([(np.asarray(v)-centers)/scales if v is not None else np.zeros(5) for v in raw]);transformed[:,constant]=0.
  joined=np.concatenate([x,np.broadcast_to(transformed,(5,48,5))],axis=2)
  assert joined.shape==(5,48,21) and np.isfinite(joined).all()
  assert np.isfinite(joined.astype(np.float32)).all() and np.isfinite(y.astype(np.float32)).all()
  h.update(joined.astype('<f8').tobytes());h.update(mask.tobytes());count+=1
 summary[period]={'origins_materialized_and_checked':count,'finite_market_history_cells':count*48*5,'finite_joined_21channel_cells':count*5*48*21,'finite_float32_conversion':True,'stock_market_masks_complete':True,'dense_windows_saved':False}
# Independent U1-U5 real oracle from actual raw SPY OHLC and prior session closes.
view=load_candidate_view(Path.cwd(),ref,'WF1_REFIT');history,_=load_conditional_spy(view.base.history.authority,m['market_annex'])
recipe=market['preparations']['WF1_REFIT'];cal=history.calendar
step=next(s for s in cal.steps if s.session=='2020-07-01' and s.slot==1);pos=cal.steps.index(step)
returns=np.asarray([math.log(history.hours[s.end].close/history.hours[s.end].open) for s in cal.steps[pos-59:pos+1]])
days=[d for d in history.days if d<step.session];prices=np.asarray([history.closes[d].close for d in days[-64:]])
short=float(np.sqrt(np.mean(returns[-12:]**2)));long=float(np.sqrt(np.mean(returns**2)));daily=float(np.sqrt(np.mean(np.log(prices[1:]/prices[:-1])**2)))
hour=max(long,recipe['hourly_floor']);day=max(daily,recipe['daily_floor'])
expected=np.asarray([returns[-1]/hour,math.log(hour),math.log(max(short,recipe['hourly_floor'])/hour),math.log(prices[-1]/prices[-6])/(math.sqrt(5)*day),math.log(prices[-1]/prices[-21])/(math.sqrt(20)*day)])
actual=np.asarray(conditional_vector(history.measures(step),recipe['hourly_floor'],recipe['daily_floor']));assert np.allclose(actual,expected,rtol=0,atol=1e-10)
scaled=(actual-np.asarray(recipe['centers']))/np.asarray(recipe['scales'])
summary['independent_U1_U5_oracle']={'session':step.session,'slot':step.slot,'raw_SPY_hour_open':history.hours[step.end].open,'raw_SPY_hour_close':history.hours[step.end].close,'independent_raw_U1_U5':expected.tolist(),'calculator_raw_U1_U5':actual.tolist(),'scaled_U1_U5':scaled.tolist(),'max_abs_difference':float(np.max(np.abs(actual-expected))),'observed_publication':'UNKNOWN','ideal_clock_age_seconds':0,'source_action_vintage_verified':False}
summary['transient_numeric_trace_sha256']=h.hexdigest();summary['NOT_FOR_TRAINING']=True
(out/'all_market_tensors_and_oracle_audit.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
```
