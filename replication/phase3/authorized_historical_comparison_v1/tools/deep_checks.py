import pathlib,sys,json,math,hashlib,decimal
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]/'.venv/lib/python3.14/site-packages'));sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from review_io import R,O,P,A,record,js
import pandas as pd,numpy as np
C=O/'comparisons';out=[]
def save(n,x):pd.DataFrame(x).to_csv(C/n,index=False,float_format='%.17g')
# Independently aligned complete candidate labels and saved role indices; no generation.
sp=record(R/'reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet');old=pd.read_parquet(sp)
orig=pd.read_parquet(P/'artifacts/origins.parquet');grid=pd.read_parquet(P/'artifacts/grid.parquet');a=np.load(P/'artifacts/source_geometry.npz',allow_pickle=False)
stocks='VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO'.split(',')
ids=pd.to_datetime(orig.t,utc=True).map(lambda t:t.isoformat()).to_numpy();expected=pd.MultiIndex.from_product([ids,stocks],names=['origin_id','ticker']);old=old.set_index(['origin_id','ticker']);assert not old.index.duplicated().any() and set(old.index)==set(expected);old=old.loc[expected]
x=old.direct_return.to_numpy().reshape(-1,20);y=a['R'];both=np.isfinite(x)&np.isfinite(y);nanmismatch=np.isfinite(x)!=np.isfinite(y)
out.append({'quantity':'all_candidate_signed_R','rows':x.size,'nan_mismatches':int(nanmismatch.sum()),'max_abs_difference':float(np.max(np.abs(x[both]-y[both]))),'exact_finite':bool(np.array_equal(x[both],y[both]))})
# Archived decomposition support is genuine one-closure support; direct masks checked.
xmask=old.decomposition_supported.to_numpy().reshape(-1,20);ymask=a['aux_mask'];out.append({'quantity':'all_candidate_aux_mask','rows':xmask.size,'mismatches':int((xmask!=ymask).sum())})
for i,k in enumerate(['origin_to_close','close_to_next_open','next_open_to_exit']):
 xx=old[k].to_numpy().reshape(-1,20);yy=a['aux'][:,:,i];mask=xmask&ymask;out.append({'quantity':k,'rows':int(mask.sum()),'max_abs_difference':float(np.max(abs(xx[mask]-yy[mask])))})
rolepath=record(R/'reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28/role_indices.npz');ro=np.load(rolepath,allow_pickle=False);rn=json.loads((P/'artifacts/roles.json').read_text());rr=[]
for f,d in rn.items():
 for role,ix in d['roles'].items():
  ref=ro[f+'_'+role];new=np.array(ix);assert np.array_equal(ref,new),(f,role)
  z=orig.iloc[ix];rr.append({'fold':f,'role':role,'origins':len(ix),'indices_exact':True,'first_date':z.date.min(),'last_date':z.date.max(),'sessions':z.date.nunique(),'signed_label_nan_mismatch':int(nanmismatch[ix].sum()),'aux_mask_mismatch':int((xmask[ix]!=ymask[ix]).sum())})
  assert not nanmismatch[ix].any() and not (xmask[ix]!=ymask[ix]).any()
  # No refitting: integer hierarchy oracle verifies saved quantiles from saved R and role keys.
  if role in ('inner_train','restricted_refit'):
   cnt=z.groupby('date').size();lcm=math.lcm(*map(int,cnt.unique()));mass=np.repeat(np.array([lcm//cnt[d] for d in z.date],dtype=np.int64),20);val=np.abs(y[ix]).ravel();order=np.argsort(val,kind='stable');cum=np.cumsum(mass[order]);total=int(cum[-1]);phase='initial' if role=='inner_train' else 'refit';s=json.loads((P/f'artifacts/run/{f}/{phase}/started.json').read_text())['scale']
   quantiles=[(1,2,'scale',s)]
   if role=='restricted_refit':
    thresholds=js(A/'phase_parity.json')['folds'][str(2000+int(f[1:]))]['thresholds'];quantiles.extend([(95,100,'p95',thresholds['95']),(99,100,'p99',thresholds['99'])])
   for num,den,name,saved in quantiles:
    pos=int(np.searchsorted(cum,(num*total+den-1)//den,side='left'));v=float(val[order[pos]]);out.append({'quantity':'integer_quantile/'+f+'/'+phase+'/'+name,'original':saved,'independent_oracle':v,'exact':saved==v});assert saved==v
# COP prefit union envelope witness; only stored flags and key sets, no recomputed feature pipeline.
for f in rn:
 for phase in ['initial','refit']:
  r=json.loads((P/f'artifacts/{f}_{phase}_recipe.json').read_text());ix=np.array(r['fit_indices']);b=ix[~a['cop_window'][ix]&(grid.date.to_numpy()[ix]>='2012-05-01')]
  out.append({'quantity':'COP_blocked_fit_union/'+f+'/'+phase,'count':len(b),'first_grid_index':int(b[0]) if len(b) else None,'first_date':grid.iloc[b[0]].date if len(b) else None,'last_date':grid.iloc[b[-1]].date if len(b) else None})
# Explicit additional Q2 current/prior regime guard, from saved geometry only.
regular_sessions=grid.groupby('session').size();regular_sessions=regular_sessions[regular_sessions==6].index;last=grid[grid.session.isin(regular_sessions)].groupby('session').tail(1).index.to_numpy();p=a['p'];safe=np.maximum(p,0);different=(a['volume_regime'][last[safe]]!=a['volume_regime'])&(p[:,None]>=0);q2=[]
for k,j in zip(*np.where(different)):
 q2.append({'date':grid.iloc[k].date,'ticker':stocks[j],'slot':int(grid.iloc[k].slot),'grid_index':int(k),'prior_regular_date':grid.iloc[last[safe[k]]].date,'current_regime':int(a['volume_regime'][k,j]),'prior_regime':int(a['volume_regime'][last[safe[k]],j]),'interpretation':'new native line141 masks Q2 here; historical native has no current/prior guard; actual old native value not archived'})
save('geometry_and_integer_checks.csv',out);save('role_membership_exact.csv',rr);save('q2_guard_witnesses.csv',q2)
# A second arithmetic method independent of compare.py: Python math.fsum of stock/origin/session means.
second=[]
for year in range(2021,2025):
 f=f'F{year%100}'
 for source,path in [('original',A/f/'oos_scores.parquet'),('independent',P/f'artifacts/run/{f}/oos_scores.parquet')]:
  if source=='original':record(path)
  d=pd.read_parquet(path);assert not d.duplicated(['origin_id','ticker']).any();assert d.groupby('origin_id').size().eq(20).all()
  for model in ['S2C-RAW','S2C-C3']:
   day={};rankday={}
   for (date,origin),g in d.groupby(['session_date_et','origin_id'],sort=False):
    true=g.A.tolist();pred=g[model].tolist();err=[p-a for p,a in zip(pred,true)];values={'mse':math.fsum(e*e for e in err)/20,'mae':math.fsum(abs(e) for e in err)/20,'observed':math.fsum(true)/20,'predicted':math.fsum(pred)/20}
    def rank(v):return [1+sum(z<x for z in v)+(sum(z==x for z in v)-1)/2 for x in v]
    ra=rank(true);rp=rank(pred);a0=[x-10.5 for x in ra];p0=[x-10.5 for x in rp];den=math.sqrt(math.fsum(x*x for x in a0)*math.fsum(x*x for x in p0));values['spearman_ic']=math.fsum(x*z for x,z in zip(a0,p0))/den if den else float('nan')
    day.setdefault(date,[]).append(values)
   results={k:math.fsum(math.fsum(x[k] for x in rows)/len(rows) for rows in day.values())/len(day) for k in ['mse','mae','observed','predicted','spearman_ic']}
   results['ratio']=results['predicted']/results['observed']
   first=pd.read_csv(C/'recomputed_primary.csv',float_precision='round_trip');row=first[(first.source==source)&(first.year==year)&(first.model==model)&(first.scope=='FULL')].iloc[0]
   for k,v in results.items():second.append({'year':year,'source':source,'model':model,'quantity':k,'second_calculation':v,'first_calculation':float(row[k]),'difference':v-float(row[k])})
save('independent_second_arithmetic.csv',second)
print('geometry',out[:5]);print('Q2guardcells',len(q2),'secondmax',max(abs(x['difference']) for x in second))
