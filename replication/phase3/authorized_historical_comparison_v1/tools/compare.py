"""Independent saved-array arithmetic only. No project-module imports, fits or forwards."""
import sys,pathlib,json,hashlib,datetime,math,csv
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]/'.venv/lib/python3.14/site-packages'))
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from review_io import R,O,P,A,record,js
import numpy as np
import pandas as pd
STOCKS='VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO'.split(',')
C=O/'comparisons'; chain=[]; forecasts=[]; recipes=[]; traces=[]; cals=[]; witnesses=[]; metrics=[]; replay=[]; rankdiff=[]
def save(name,rows):pd.DataFrame(rows).to_csv(C/name,index=False,float_format='%.17g')
def csvread(p):
 if P not in p.parents:record(p)
 return pd.read_csv(p,float_precision='round_trip',keep_default_na=False)
def arrstats(x,y):
 x=np.asarray(x,dtype=float).ravel();y=np.asarray(y,dtype=float).ravel();ok=np.isfinite(x)&np.isfinite(y);d=np.abs(y[ok]-x[ok]);rel=d/np.maximum(np.abs(x[ok]),np.finfo(float).tiny)
 return {'n_expected':len(x),'n_matched':int(ok.sum()),'n_missing':int((~ok).sum()),'max_abs_difference':float(d.max()) if len(d) else None,'mean_abs_difference':float(d.mean()) if len(d) else None,'median_abs_difference':float(np.median(d)) if len(d) else None,'p95_abs_difference':float(np.quantile(d,.95)) if len(d) else None,'p99_abs_difference':float(np.quantile(d,.99)) if len(d) else None,'max_relative_difference':float(rel.max()) if len(d) else None,'exact':bool(np.array_equal(x,y,equal_nan=True))}
def compare(f,stage,q,x,y,old,new,tol='saved precision',extra=None):
 st=arrstats(x,y); row={'fold':f,'stage':stage,'quantity':q,'original_source':str(old.relative_to(R)) if isinstance(old,pathlib.Path) else old,'phase2_source':str(new.relative_to(R)) if isinstance(new,pathlib.Path) else new,'comparison_method':'Direct saved numeric values','tolerance_class':tol,'status':'PASS' if st['exact'] else 'NEAR' if st['max_abs_difference'] is not None and st['max_abs_difference']<=1e-12 else 'DIFFER','root_cause_or_limit':'',**st}
 if extra:row.update(extra)
 chain.append(row);return row

def memberships(v):
 s=pd.Series(v);lo=s.rank(method='min',ascending=False).to_numpy();hi=s.rank(method='max',ascending=False).to_numpy();return np.clip((5-lo)/(hi-lo+1),0,1)
def rank_origin(g,col):
 a=g.A.to_numpy();v=g[col].to_numpy();ra=pd.Series(a).rank().to_numpy();rp=pd.Series(v).rank().to_numpy();ac=ra-ra.mean();pc=rp-rp.mean();den=np.sqrt(ac@ac*(pc@pc));ii,jj=np.triu_indices(20,1);da=np.sign(a[ii]-a[jj]);dp=np.sign(v[ii]-v[jj]);valid=da!=0
 return {'origin_id':g.origin_id.iloc[0],'session_date_et':g.session_date_et.iloc[0],'category':g.category.iloc[0],'slot':g.slot.iloc[0],'spearman_ic':float(ac@pc/den) if den else np.nan,'pair_concordance':float(np.mean(np.where(dp[valid]==0,.5,(dp[valid]==da[valid]).astype(float)))) if valid.any() else np.nan,'top4_retrieval':float(memberships(a)@memberships(v)/4),'bottom4_retrieval':float(memberships(-a)@memberships(-v)/4),'tie_rate':float(np.mean(dp==0)),'constant_rate':float(np.ptp(v)==0)}
def scalar(d,col):
 w=d.weight.to_numpy();a=d.A.to_numpy();p=d[col].to_numpy();mass=w.sum(); mse=float(w@((p-a)**2)/mass)
 return {'observed':float(w@a/mass),'predicted':float(w@p/mass),'bias':float(w@(p-a)/mass),'mae':float(w@np.abs(p-a)/mass),'mse':mse,'ratio':float((w@p)/(w@a)),'original_mass':float(mass),'loss_contribution':float(w@((p-a)**2))}

oldall=[];newall=[];calold=[];calnew=[];parity=js(A/'phase_parity.json');oldmetrics=csvread(A/'metrics.csv');newsc=csvread(P/'artifacts/report_recovery_v1/metrics/scalars.csv');newra=csvread(P/'artifacts/report_recovery_v1/metrics/ranks.csv')
for year in range(2021,2025):
 f=f'F{year%100}';
 for role,on,nn in [('oos','oos_scores.parquet','oos_scores.parquet'),('calibration','calibration_scores.parquet','calibration_predictions.parquet')]:
  op=record(A/f/on);npth=P/f'artifacts/run/{f}/{nn}';od=pd.read_parquet(op);nd=pd.read_parquet(npth)
  keys=['origin_id','ticker'];assert not od.duplicated(keys).any() and not nd.duplicated(keys).any()
  assert od.groupby('origin_id',sort=False).ticker.apply(list).map(lambda x:x==STOCKS).all();assert nd.groupby('origin_id',sort=False).ticker.apply(list).map(lambda x:x==STOCKS).all()
  od=od.set_index(keys).sort_index();nd=nd.set_index(keys).sort_index();assert od.index.equals(nd.index),f'{f}/{role} KEY MISMATCH'
  for name in ['session_date_et','slot','category','entry_end_utc','exit_end_utc','label_maturity_utc']:
   assert np.array_equal(od[name].to_numpy(),nd[name].to_numpy()),f'{f}/{role}/{name} MISMATCH'
  chain.append({'fold':f,'stage':'C1','quantity':role+' exact keys and timing/category metadata','original_source':str(op.relative_to(R)),'phase2_source':str(npth.relative_to(R)),'comparison_method':'Unique full-key sorted index and exact metadata arrays; fixed stock order','n_expected':len(od),'n_matched':len(nd),'n_missing':0,'tolerance_class':'exact','status':'PASS','root_cause_or_limit':'R and auxiliary row values absent in original main score schema'})
  for name in ['A','weight','Mhat']+(['S2C-RAW','S2C-C3'] if role=='oos' else []):
   x=od[name].to_numpy();y=nd[name].to_numpy();row=compare(f,'C1' if name in ['A','weight'] else 'C5',role+'/'+name,x,y,op,npth)
   if name in ['A','weight']:assert row['max_abs_difference']<=1e-12,f'LABEL/WEIGHT {f}/{role}'
   nz=np.flatnonzero(x!=y)
   if len(nz):
    i=nz[0];witnesses.append({'fold':f,'role':role,'quantity':name,'origin_id':od.index[i][0],'ticker':od.index[i][1],'original':float(x[i]),'independent':float(y[i]),'delta':float(y[i]-x[i])})
   if role=='oos' and name not in ['A','weight']:
    frame=od.reset_index();frame['_x']=x;frame['_y']=y
    partitions=[('all','ALL',frame)]
    for dim in ['ticker','slot','category']:
     partitions.extend((dim,str(g),s) for g,s in frame.groupby(dim))
    t=parity['folds'][str(year)]['thresholds']
    for q,cut in t.items():partitions.append(('tail','p'+q,frame[frame.A>cut]))
    for dim,g,s in partitions:
     xx=s._x.to_numpy();yy=s._y.to_numpy();forecasts.append({'year':year,'dimension':dim,'group':g,'quantity':name,**arrstats(xx,yy),'correlation':float(np.corrcoef(xx,yy)[0,1]) if len(xx)>1 else None,'signed_mean_difference':float(np.mean(yy-xx)),'original_zeros':int((xx==0).sum()),'independent_zeros':int((yy==0).sum()),'float32_diagnostic_exceedances':int((np.abs(yy-xx)>1e-6+1e-5*np.abs(xx)).sum())})
  od=od.reset_index();nd=nd.reset_index();od['year']=year;nd['year']=year
  if role=='oos':oldall.append(od);newall.append(nd)
  else:calold.append(od);calnew.append(nd)
 # All saved recipes, not re-estimated.
 for phase,oldphase in [('initial','initial'),('refit','restricted')]:
  spec=parity['folds'][str(year)]['phases'][oldphase];op=R/spec['recipe_reference'];ro=js(op);npth=P/f'artifacts/{f}_{phase}_recipe.json';rn=json.loads(npth.read_text())
  assert ro['fit_hour_indices']==rn['fit_indices'];compare(f,'C2',phase+'/fit_hour_indices',ro['fit_hour_indices'],rn['fit_indices'],op,npth,'exact')
  compare(f,'C2',phase+'/unique_day_count',[ro['unique_m2_day_timestamps']],[rn['fit_unique_days']],op,npth,'exact')
  for i,ticker in enumerate(STOCKS):
   for kind in ['hourly_floor','daily_floor','m2_floor']:
    x=ro['floors'][i][kind];y=rn[kind][i];recipes.append({'fold':f,'phase':phase,'quantity':kind,'stock':ticker,'original':x,'independent':y,'delta':y-x,'relative_delta':(y-x)/x})
   for k,v in ro['floors'][i]['volume_pseudocounts'].items():
    regime=k.rsplit(':',1)[1]
    for j,kind in enumerate(['hour','day']):
     x=v[kind];y=rn['pseudocounts'][i][regime][j];recipes.append({'fold':f,'phase':phase,'quantity':'pseudocount_'+kind,'stock':ticker,'regime':regime,'original':x,'independent':y,'delta':y-x,'relative_delta':(y-x)/x})
  common=['M1','M3','M4','V1','V2','V3','B1','B2','Q1','Q2','T1','T2','T3','T4','T5']
  for j,k in enumerate(common+['M2']):
   for field in ['center','scale']:
    x=ro['scalers'][k][field];y=rn[field+'s'][j] if k!='M2' else rn['m2_'+field]
    recipes.append({'fold':f,'phase':phase,'quantity':k+'/'+field,'stock':'ALL','original':x,'independent':y,'delta':y-x,'relative_delta':(y-x)/abs(x) if x else None})
  started=json.loads((P/f'artifacts/run/{f}/{phase}/started.json').read_text());compare(f,'C3',phase+'/target_scale',[spec['scale']],[started['scale']],A/'phase_parity.json',P/f'artifacts/run/{f}/{phase}/started.json','exact')
 # selector/refit trace compare
 tr=csvread(A/f/'training.csv');sel=js(A/f/'selection.json');res=js(A/f/'result.json');ns=json.loads((P/f'artifacts/run/{f}/initial/selector_state.json').read_text())
 compare(f,'C3','selected/selector/raw epochs',[res['selected_epoch'],res['selector_epochs'],res['raw_minimum_epoch']],[ns['selected'],ns['epoch'],ns['raw_epoch']],A/f/'result.json',P/f'artifacts/run/{f}/initial/selector_state.json','exact')
 for phase,oldphase in [('initial','selector'),('refit','refit')]:
  nt=[json.loads(s) for s in (P/f'artifacts/run/{f}/{phase}/trace.jsonl').read_text().splitlines()];ot=tr[tr.phase==oldphase]
  assert len(ot)==len(nt),(f,phase,len(ot),len(nt))
  for (_,rr),nr in zip(ot.iterrows(),nt):
   for oc,nc in [('steps','updates'),('batch_main_mean','batch_main_mean'),('batch_aux_three_head_mean','batch_aux_three_head_mean'),('gradient_norm_max','maximum_preclip_norm')]+([('validation_main_M_MSE','validation'),('selected','selected_epoch')] if phase=='initial' else []):
    x=float(rr[oc]);y=float(nr[nc]);traces.append({'fold':f,'phase':phase,'epoch':int(rr.epoch),'quantity':oc,'original':x,'independent':y,'delta':y-x})
 # C3 arithmetic verification, independently on both saved arrays, no new coefficient fitting/output substitution.
 cc=csvread(A/f/'calibration_coefficients.csv');nc=json.loads((P/f'artifacts/run/{f}/calibration.json').read_text());scale=nc['scale'];ca=calold[-1];cn=calnew[-1]
 for source,d in [('original',ca),('independent',cn)]:
  w=d.weight.to_numpy();q=np.exp(np.log1p(d.A.to_numpy()/scale)-d.Mhat.to_numpy().astype(float));c0=float(w@q/w.sum())
  for group,g in d.groupby('category'):
   mask=d.category==group;wg=w[mask];qg=q[mask];mass=g.groupby('session_date_et').weight.sum().to_numpy();ne=float(mass.sum()**2/(mass@mass));rho=ne/(ne+25);cg=float(wg@qg/wg.sum());factor=c0+rho*(cg-c0)
   saved=cc[cc.group==group].iloc[0].c_star if source=='original' else next(x['factor'] for x in nc['categories'] if x['category']==group)
   replay.append({'year':year,'source':source,'category':group,'quantity':'C3_saved_formula','calculated':factor,'saved':saved,'difference':factor-saved})
 for cat in nc['categories']:
  row=cc[cc.group==cat['category']].iloc[0]
  for oc,val in [('scale',scale),('c0',nc['global_moment']),('c_raw',cat['moment']),('n_eff',cat['effective_sessions']),('rho',cat['rho']),('c_star',cat['factor']),('weight_mass',cat['original_mass'])]:
   x=float(row[oc]);cals.append({'year':year,'category':cat['category'],'quantity':oc,'original':x,'independent':val,'delta':val-x,'relative_delta':(val-x)/x if x else None})
old=pd.concat(oldall,ignore_index=True);new=pd.concat(newall,ignore_index=True)
# Independent hierarchical and rank arithmetic on both arrays; no evaluator imports.
ranktables={};derived=[]
for source,d in [('original',old),('independent',new)]:
 for year,g in d.groupby('year'):
  for model in ['S2C-RAW','S2C-C3']:
   rt=pd.DataFrame([rank_origin(z,model) for _,z in g.groupby('origin_id',sort=False)]);ranktables[(source,year,model)]=rt
   for scope,z in [('FULL',g),*[(c,v) for c,v in g.groupby('category')]]:
    sc=scalar(z,model);rsel=rt if scope=='FULL' else rt[rt.category==scope];rvals=rsel.groupby('session_date_et')[['spearman_ic','pair_concordance','top4_retrieval','bottom4_retrieval','tie_rate','constant_rate']].mean().mean().to_dict()
    derived.append({'source':source,'year':str(year),'model':model,'scope':scope,**sc,**rvals})
    saved_scalar=newsc[(newsc.year.astype(str)==str(year))&(newsc.model==model)&(newsc.dimension==('all' if scope=='FULL' else 'category'))&(newsc.group==('ALL' if scope=='FULL' else scope))] if source=='independent' else oldmetrics[(oldmetrics.year.astype(str)==str(year))&(oldmetrics.arm==model)&(oldmetrics.scope==scope)]
    saved_rank=newra[(newra.year.astype(str)==str(year))&(newra.model==model)&(newra.dimension==('all' if scope=='FULL' else 'category'))&(newra.group==('ALL' if scope=='FULL' else scope))] if source=='independent' else saved_scalar
    if len(saved_scalar):
     for k,v in sc.items():
      oc={'mse':'raw_MSE','mae':'raw_MAE'}.get(k,k) if source=='original' else k
      if oc in saved_scalar:replay.append({'year':year,'source':source,'model':model,'scope':scope,'quantity':k,'calculated':v,'saved':float(saved_scalar.iloc[0][oc]),'difference':v-float(saved_scalar.iloc[0][oc])})
    if len(saved_rank):
     for k,v in rvals.items():
      oc={'spearman_ic':'magnitude_IC','top4_retrieval':'top4','bottom4_retrieval':'bottom4'}.get(k,k) if source=='original' else k
      if oc in saved_rank:replay.append({'year':year,'source':source,'model':model,'scope':scope,'quantity':k,'calculated':v,'saved':float(saved_rank.iloc[0][oc]),'difference':v-float(saved_rank.iloc[0][oc])})
# Quantify pair order changes, ties, and margins per-origin; only compact grouped results saved.
for year,g in old.groupby('year'):
 ng=new[new.year==year].set_index(['origin_id','ticker']).loc[g.set_index(['origin_id','ticker']).index].reset_index();ii,jj=np.triu_indices(20,1)
 for model in ['Mhat','S2C-RAW','S2C-C3']:
  for (key,z),(_,nz) in zip(g.groupby('origin_id',sort=False),ng.groupby('origin_id',sort=False)):
   x=z[model].to_numpy();y=nz[model].to_numpy();dx=x[ii]-x[jj];dy=y[ii]-y[jj];mask=np.sign(dx)!=np.sign(dy)
   if mask.any():rankdiff.append({'year':year,'origin_id':key,'slot':z.slot.iloc[0],'category':z.category.iloc[0],'quantity':model,'pairs':190,'changed_pairs':int(mask.sum()),'max_original_margin_changed':float(np.max(abs(dx[mask]))),'original_ties':int((dx==0).sum()),'independent_ties':int((dy==0).sum())})
# Compare all available archival table cells with matched independent table estimands.
def metricrow(year,model,scope,q,x,y,source):
 x=float(x);y=float(y);delta=y-x;rel=delta/abs(x) if x else None; tol=1e-4 if q in ['mse','mae'] else .0005 if q=='spearman_ic' else None
 status='PASS' if x==y else ('NEAR' if (abs(rel)<=tol if q in ['mse','mae'] and rel is not None else abs(delta)<=tol) else 'DIFFER') if tol is not None else 'DIFFER'
 metrics.append({'year':year,'model':model,'scope':scope,'metric':q,'original':x,'independent':y,'delta':delta,'absolute_difference':abs(delta),'relative_difference':rel,'tolerance':tol,'status':status,'original_source':source})
for _,row in oldmetrics[oldmetrics.arm.isin(['S2C-C3','S2C-RAW'])].iterrows():
 for table,mapping in [(newsc,{'observed':'observed','predicted':'predicted','bias':'bias','ratio':'ratio','raw_MAE':'mae','raw_MSE':'mse'}),(newra,{'magnitude_IC':'spearman_ic','pair_concordance':'pair_concordance','top4':'top4_retrieval','bottom4':'bottom4_retrieval','tie_rate':'tie_rate','constant_rate':'constant_rate'})]:
  dim='all' if row.scope=='FULL' else 'category';grp='ALL' if row.scope=='FULL' else row.scope
  z=table[(table.year.astype(str)==str(row.year))&(table.model==row.arm)&(table.dimension==dim)&(table.group==grp)]
  if len(z):
   for oc,nc in mapping.items():metricrow(row.year,row.arm,row.scope,nc,row[oc],z.iloc[0][nc],'metrics.csv')
# Conditional slots/calendar/tails; comparator-dependent deciles explicitly excluded.
gr=csvread(A/'groups.csv');print('old groups',gr.field.unique(),gr.group.unique()[:30])
for _,row in gr[gr.arm.isin(['S2C-C3','S2C-RAW'])&~gr.field.str.contains('decile',case=False)].iterrows():
 dim={'slot':'slot','calendar':'calendar','tail':'tail','ticker':'stock'}.get(row.field,row.field);grp=str(row.group)
 if row.field=='calendar' and grp=='NORMAL':grp='REGULAR'
 if str(row.field).startswith('tail_'):
  dim='tail';grp=str(row.field)[5:]+':p'+('95' if '95' in grp else '99')+(':'+('complement' if grp.startswith('LE_') else 'event'))
 z=newsc[(newsc.year.astype(str)==str(row.year))&(newsc.model==row.arm)&(newsc.dimension==dim)&(newsc.group==grp)]
 if len(z):
  for oc,nc in {'observed':'observed','predicted':'predicted','bias':'bias','ratio':'ratio','raw_MAE':'mae','raw_MSE':'mse','weight_mass':'original_mass','raw_MSE_contribution':'loss_contribution','raw_MSE_loss_share':'loss_share'}.items():metricrow(row.year,row.arm,dim+'/'+grp,nc,row[oc],z.iloc[0][nc],'groups.csv')
ev=csvread(A/'event_retrieval.csv');nv=csvread(P/'artifacts/report_recovery_v1/metrics/events.csv')
for _,row in ev[ev.arm.isin(['S2C-C3','S2C-RAW'])].iterrows():
 z=nv[(nv.year.astype(str)==str(row.year))&(nv.model==row.arm)&(nv.scope==row.scope)&(nv['quantile']=='p'+str(row.prefix_percentile))]
 if len(z):
  for oc,nc in {'event_prevalence':'prevalence','event_top4_recall':'top4_recall','top4_event_precision':'top4_precision','false_low_rank':'false_low_rank','event_rows':'event_rows'}.items():metricrow(row.year,row.arm,row.scope+'/p'+str(row.prefix_percentile),nc,row[oc],z.iloc[0][nc],'event_retrieval.csv')
aux=csvread(A/'auxiliary_diagnostics.csv');na=csvread(P/'artifacts/report_recovery_v1/metrics/signed.csv');cm={'origin_to_close':'pre','close_to_next_open':'gap','next_open_to_exit':'post'}
print('components',aux.component.unique(),'newscalar groups',newsc.groupby('dimension').group.unique().to_dict())
for _,row in aux.iterrows():
 component=cm.get(row.component,row.component);z=na[(na.year.astype(str)==str(row.year))&(na.stock==row.ticker)&(na.component==component)]
 if len(z):
  for oc,nc in {'signed_MSE':'mse','signed_MAE':'mae','observed_signed_mean':'observed','predicted_signed_mean':'predicted','weighted_Pearson':'pearson','rows':'rows'}.items():
   if row[oc]!='' and z.iloc[0][nc]!='':metricrow(row.year,'signed',str(row.ticker)+'/'+component,nc,row[oc],z.iloc[0][nc],'auxiliary_diagnostics.csv')
save('recipe_values.csv',recipes);save('training_trace_differences.csv',traces);save('calibration_differences.csv',cals);save('first_difference_witnesses.csv',witnesses);save('independent_metric_recomputation.csv',replay);save('recomputed_primary.csv',derived);save('pair_order_disagreements.csv',rankdiff)
pd.DataFrame(chain).to_csv(O/'CHAIN_COMPARISON.csv',index=False,float_format='%.17g');pd.DataFrame(forecasts).to_csv(O/'FORECAST_PARITY.csv',index=False,float_format='%.17g');pd.DataFrame(metrics).to_csv(O/'ORIGINAL_VS_INDEPENDENT_METRICS.csv',index=False,float_format='%.17g')
print('primary C3 full');print(pd.DataFrame(metrics).query("model=='S2C-C3' and scope=='FULL' and metric in ['mse','mae','spearman_ic']").to_string(index=False));print('max replay',pd.DataFrame(replay).groupby(['source','quantity']).difference.agg(lambda x:np.max(np.abs(x))).to_string());print('recipe deviations >1e-10',sum(abs(x['delta'])>1e-10 for x in recipes))
