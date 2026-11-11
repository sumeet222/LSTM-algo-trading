"""Independent full frozen-table arithmetic; no imported research evaluator."""
import sys,pathlib,json,math
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]/'.venv/lib/python3.14/site-packages'));sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from review_io import R,O,P,A,record
import numpy as np,pandas as pd
C=O/'comparisons';base=P/'artifacts/report_recovery_v1/metrics';checks=[]
def csv(p):return pd.read_csv(p,float_precision='round_trip')
def member(x):
 s=pd.Series(x);lo=s.rank(method='min',ascending=False).to_numpy();hi=s.rank(method='max',ascending=False).to_numpy();return np.clip((5-lo)/(hi-lo+1),0,1)
def add(table,row,key,v):
 s=float(row[key]);checks.append({'table':table,'year':row['year'],'key':'|'.join(str(row.get(x,'')) for x in ['model','dimension','group','scope','quantile','stock','component']),'quantity':key,'computed':v,'saved':s,'difference':v-s if np.isfinite(v) and np.isfinite(s) else np.nan,'undefined_agrees':bool(np.isnan(v)==np.isnan(s))})
allframes=[];rank_cache={};tops={};ranks={}
for year in range(2021,2025):
 d=pd.read_parquet(P/f'artifacts/run/F{year%100}/oos_scores.parquet');d['year']=year;allframes.append(d)
 for model in ['S2C-RAW','S2C-C3']:
  rr=[];tp=pd.Series(index=d.index,dtype=float);pr=tp.copy()
  for oid,g in d.groupby('origin_id',sort=False):
   a=g.A.to_numpy();p=g[model].to_numpy();ra=pd.Series(a).rank().to_numpy();rp=pd.Series(p).rank().to_numpy();tp.loc[g.index]=member(p);pr.loc[g.index]=rp;ac=ra-10.5;pc=rp-10.5;den=np.sqrt((ac@ac)*(pc@pc));ii,jj=np.triu_indices(20,1);da=np.sign(a[ii]-a[jj]);dp=np.sign(p[ii]-p[jj]);valid=da!=0
   rr.append({'origin_id':oid,'date':g.session_date_et.iloc[0],'category':g.category.iloc[0],'slot':g.slot.iloc[0],'early_close':bool(g.early_close.iloc[0]),'spearman_ic':ac@pc/den if den else np.nan,'pair_concordance':np.mean(np.where(dp[valid]==0,.5,dp[valid]==da[valid])),'top4_retrieval':member(a)@member(p)/4,'bottom4_retrieval':member(-a)@member(-p)/4,'tie_rate':np.mean(dp==0),'constant_rate':float(np.ptp(p)==0)})
  rank_cache[(year,model)]=pd.DataFrame(rr);tops[(year,model)]=tp;ranks[(year,model)]=pr
frames={int(d.year.iloc[0]):d for d in allframes}; thresholds={y:json.loads((A/f'F{y%100}/phases.json').read_text())['thresholds'] for y in frames}
def subset(d,dim,group,year):
 if dim=='all':return d
 if dim in ['category','slot']:return d[d[dim]==group]
 if dim=='stock':return d[d.ticker==group]
 if dim=='calendar':return d[d.early_close==(group=='EARLY_CLOSE')]
 scope,q,kind=group.split(':');e=d if scope=='ALL' else d[d.category==scope];cut=thresholds[year][q[1:]];return e[e.A>cut] if kind=='event' else e[e.A<=cut]
for table in ['scalars','ranks','events','signed']:
 saved=csv(base/(table+'.csv')); cache={}
 for _,row in saved[saved.year.astype(str)!='EQ'].iterrows():
  y=int(row.year);d=frames[y]
  if table=='scalars':
   g=subset(d,row.dimension,row.group,y);w=g.weight.to_numpy();a=g.A.to_numpy();p=g[row.model].to_numpy();mass=w.sum();err=p-a;full=float(d.weight@((d[row.model]-d.A)**2));vals={'rows':len(g),'origins':g.origin_id.nunique(),'sessions':g.session_date_et.nunique(),'original_mass':mass,'observed':w@a/mass,'predicted':w@p/mass,'bias':w@err/mass,'mae':w@abs(err)/mass,'mse':w@(err**2)/mass,'ratio':w@p/(w@a),'loss_contribution':w@(err**2),'loss_share':w@(err**2)/full};key=(row.model,row.dimension,row.group)
  elif table=='ranks':
   g=rank_cache[(y,row.model)]
   if row.dimension in ['category','slot']:g=g[g[row.dimension]==row.group]
   if row.dimension=='calendar':g=g[g.early_close==(row.group=='EARLY_CLOSE')]
   cols=['spearman_ic','pair_concordance','top4_retrieval','bottom4_retrieval','tie_rate','constant_rate'];vals=g.groupby('date')[cols].mean().mean().to_dict();key=(row.model,row.dimension,row.group)
  elif table=='events':
   g=d if row.scope=='ALL' else d[d.category==row.scope];event=g.A>row.threshold;w=g.weight;top=tops[(y,row.model)].loc[g.index];rank=ranks[(y,row.model)].loc[g.index];mass=float(w[event].sum());numer=float((w[event]*top[event]).sum());vals={'event_rows':int(event.sum()),'prevalence':mass/w.sum(),'top4_recall':numer/mass if mass else np.nan,'top4_precision':numer/float((w*top).sum()),'false_low_rank':float(w[event&(rank<=10.5)].sum())/mass if mass else np.nan};key=(row.model,row['quantile'],row.scope)
  else:
   g=d[d.aux_supported];g=g if row.stock=='ALL' else g[g.ticker==row.stock];w=g.weight.to_numpy();w=w/w.sum();a=g['R_'+row.component].to_numpy();p=g['Rhat_'+row.component].to_numpy().astype(float);am=w@a;pm=w@p;cov=w@((a-am)*(p-pm));den=np.sqrt((w@((a-am)**2))*(w@((p-pm)**2)));vals={'rows':len(g),'sessions':g.session_date_et.nunique(),'observed':am,'predicted':pm,'mse':w@((p-a)**2),'mae':w@abs(p-a),'covariance':cov,'pearson':cov/den if den else np.nan};key=(row.stock,row.component)
  cache[(y,*key)]=vals
  for k,v in vals.items():add(table,row,k,float(v))
 for _,row in saved[saved.year.astype(str)=='EQ'].iterrows():
  key=(row.model,row.dimension,row.group) if table in ['scalars','ranks'] else (row.model,row['quantile'],row.scope) if table=='events' else (row.stock,row.component)
  vs=[cache[(y,*key)] for y in range(2021,2025)];vals={k:float(np.mean([x[k] for x in vs])) for k in vs[0]}
  for k in ['rows','origins','sessions','event_rows']:
   if k in vals:vals[k]=sum(x[k] for x in vs)
  if table=='scalars':
   vals['ratio']=vals['predicted']/vals['observed'];full=np.mean([cache[(y,row.model,'all','ALL')]['mse'] for y in range(2021,2025)]);vals['loss_share']=vals['loss_contribution']/full
  for k,v in vals.items():add(table,row,k,float(v))
# Per-origin clamping/tie census.
saved=csv(base/'clamping.csv')
for _,r in saved.iterrows():
 d=frames[int(r.year)];g=d[d.origin_id==r.origin_id];p=g[r.model].to_numpy();z=g.Mhat.to_numpy();ii,jj=np.triu_indices(20,1)
 for k,v in {'zero_predictions':int((p==0).sum()),'tied_pairs':int((p[ii]==p[jj]).sum()),'new_ties_vs_mhat':int(((p[ii]==p[jj])&(z[ii]!=z[jj])).sum())}.items():add('clamping',r,k,v)
pd.DataFrame(checks).to_csv(C/'all_frozen_metric_checks.csv',index=False,float_format='%.17g');dd=pd.DataFrame(checks);print(dd.groupby('table').difference.agg(['count',lambda x:np.nanmax(abs(x))]).to_string());print('undefined mismatch',int((~dd.undefined_agrees).sum()))
