import sys,pathlib,json,hashlib,math
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]/'.venv/lib/python3.14/site-packages'));sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from review_io import R,O,P,A,record,js
import numpy as np,pandas as pd
C=O/'comparisons';reports=[]
def csv(p):
 if P not in p.parents:record(p)
 return pd.read_csv(p,float_precision='round_trip')
# Historical source path identity receipts, only previously bound pre2025 receipt.
src=csv(R/'reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv');new=json.loads((P/'audit/input_manifest.json').read_text());nd={x['path']:x for x in new};src=src[src.purpose=='permitted adjusted hourly source'];assert len(src)==174
for _,r in src.iterrows():assert all(str(r[k])==str(nd[r.path][k]) for k in ['sha256','bytes','rows'])
reports.append({'check':'Original174hourly identities vs admitted inputs','count':174,'status':'EXACT'})
# Role dates, counts and slot membership independently from frozen origins/indices.
rc=csv(R/'reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/role_counts.csv');o=pd.read_parquet(P/'artifacts/origins.parquet');roles=json.loads((P/'artifacts/roles.json').read_text());cr=[]
for _,r in rc.iterrows():
 f=f'F{int(r.year)%100}';z=o.iloc[roles[f]['roles'][r.role]];vals={'origins':len(z),'sessions':z.date.nunique(),'stock_rows':len(z)*20,'first_date':z.date.min(),'last_date':z.date.max()};vals.update({f'{9+k:02d}:30':int((z.slot_index==k).sum()) for k in range(7)})
 for k,v in vals.items():assert v==r[k],(f,r.role,k,v,r[k]);cr.append({'fold':f,'role':r.role,'quantity':k,'original':r[k],'independent':v,'exact':True})
pd.DataFrame(cr).to_csv(C/'role_date_slot_checks.csv',index=False)
can=csv(R/'reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/selector_candidates.csv');nc=json.loads((P/'audit/selector_candidates.json').read_text());cand=[]
for n in nc:
 r=can[(can.year==2000+int(n['fold'][1:]))&(can.start==n['start'])].iloc[0];assert r.initial_stop==n['initial_stop'] and r.sessions==n['sessions'];assert [r[f'{9+k:02d}:30'] for k in range(7)]==n['slot_counts'];cand.append({'fold':n['fold'],'start':n['start'],'exact':True})
pd.DataFrame(cand).to_csv(C/'selector_candidate_checks.csv',index=False)
# Source-bound original main module hash; transitive historical versions remain imperfectly pinned.
ready=js(A/'readiness.json');p=record(R/'src/lstm_data/hf20_s2c_ca.py');assert hashlib.sha256(p.read_bytes()).hexdigest()==ready['code_sha256']['src/lstm_data/hf20_s2c_ca.py']
# Single synthetic mathematical Q2 boundary witness from stored arrays and saved recipe.
a=np.load(P/'artifacts/source_geometry.npz',allow_pickle=False);g=pd.read_parquet(P/'artifacts/grid.parquet');target=g[(g.date=='2012-08-13')&(g.slot==0)].index[0];s=11
regular=g.groupby('session').size();regdays=regular[regular==6].index;groups=[x.index.to_numpy() for _,x in g[g.session.isin(regdays)].groupby('session')];prior=int(a['p'][target]);window=groups[prior-59:prior+1];U=[]
for ix in window:
 v=a['V'][ix,s];ok=np.isfinite(v).all() and a['volume_regime'][ix[0],s]==a['volume_regime'][ix[-1],s];U.append(v.sum() if ok else np.nan)
U=np.array(U);assert len(U)==60 and np.isfinite(U).sum()>=57 and np.isfinite(U[-5:]).all();assert not np.any(np.convolve((~np.isfinite(U)).astype(int),np.ones(3,dtype=int),'valid')==3)
recipe=js(R/'reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28/F21/initial_recipe.json');q=recipe['floors'][s]['volume_pseudocounts']['KO:AS_REPORTED_SHARE_REGIME:1']['day'];native=float(np.log((U[-5:].mean()+q)/(np.nanmean(U)+q)))
w={'interpretation':'Independent bounded arithmetic witness on saved geometry, not original regenerated features or new fit','ticker':'KO','date':'2012-08-13','grid_index':int(target),'native_from_historical_formula':native,'new_native_after_explicit_regime_guard':'NaN','new_scaled_fallback':0.0,'prior_regime':0,'current_regime':1,'finite_daily_observations':int(np.isfinite(U).sum()),'saved_new_unit_daily_pseudocount':q,'original_old_unit_daily_window':True}
(C/'q2_first_difference_witness.json').write_text(json.dumps(w,indent=2))
# All8 phase aux-normalizer values, scalar saved values no re-estimation.
pre=js(A/'S2C_CA_PREFLIGHT.json');aux=[]
for r in pre['counts']:
 f=f'F{r["year"]%100}'
 if r['role'] in ['inner_train','restricted_refit']:
  phase='initial' if r['role']=='inner_train' else 'refit';n=json.loads((P/f'artifacts/run/{f}/{phase}/started.json').read_text())
  for ok,nk in [('aux_phase_sessions','sessions'),('aux_overnight_sessions','auxiliary_sessions'),('aux_global_masked_base_mass','auxiliary_global_mass')]:aux.append({'fold':f,'phase':phase,'quantity':ok,'original':r[ok],'independent':n[nk],'delta':n[nk]-r[ok]})
pd.DataFrame(aux).to_csv(C/'auxiliary_normalization.csv',index=False,float_format='%.17g')
(C/'additional_checks.json').write_text(json.dumps({'checks':reports,'role_date_slots':len(cr),'selector_candidates':len(cand),'q2_witness':w},indent=2))
print(w)
