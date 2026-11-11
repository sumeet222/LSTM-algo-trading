"""Fresh endpoint labels, full-hour geometry, source eligibility and Design A roles."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import boundary
from geometry import STOCKS,QUARANTINE_NS,MINUTE,schedule,grids,factor,volume_regime,price_basis


def rolling(values: np.ndarray, n: int, minimum: int, regimes: np.ndarray | None=None) -> np.ndarray:
    """Scheduled-position mean; full window, finite minimum and no 3-NaN run."""
    x=np.asarray(values,dtype=np.float64); single=x.ndim==1
    if single: x=x[:,None]
    good=np.isfinite(x)
    counts=np.vstack([np.zeros((1,x.shape[1]),dtype=np.int64),np.cumsum(good,axis=0)])
    triple=np.zeros_like(good); triple[2:]=~good[2:]&~good[1:-1]&~good[:-2]
    tc=np.vstack([np.zeros((1,x.shape[1]),dtype=np.int64),np.cumsum(triple,axis=0)])
    out=np.full_like(x,np.nan)
    if len(x)>=n:
        k=counts[n:]-counts[:-n]; ok=k>=minimum
        if n>=3: ok&=(tc[n:]-tc[2:len(x)-n+3])==0
        if regimes is not None:
            r=np.asarray(regimes); r=r[:,None] if r.ndim==1 else r
            ok&=r[n-1:]==r[:len(x)-n+1]
        # Window-local sums cannot subtract a remote large historical prefix.
        # Blocked views bound memory while preserving scheduled positions.
        views=np.lib.stride_tricks.sliding_window_view(x,n,axis=0)
        vals=np.full_like(k,np.nan,dtype=float)
        for lo in range(0,len(views),512):
            v=views[lo:lo+512]; total=np.where(np.isfinite(v),v,0).sum(axis=2)
            vals[lo:lo+512]=np.divide(total,k[lo:lo+512],out=np.full_like(total,np.nan),where=k[lo:lo+512]>0)
        out[n-1:]=np.where(ok,vals,np.nan)
    return out[:,0] if single else out


def build() -> dict:
    contract=json.loads((boundary.PHASE/"audit/data_contract_receipt.json").read_text())
    if contract["status"]!="PASS": raise RuntimeError("D0 data contract not passed")
    sched=schedule(); h,o=grids(sched); n=len(h)
    arrays: dict[str,np.ndarray]={k:np.full((n,20),np.nan) for k in ("O","H","L","C","G","V")}
    ends=h.end.to_numpy(); stock_map={s:i for i,s in enumerate(STOCKS)}
    source_counts=[]
    # Only endpoint references retained from monthly canonical scans, never a duplicate minute store.
    op=sched.open.astype("int64").to_numpy(); close=sched.close.astype("int64").to_numpy()
    needed=np.unique(np.concatenate([o.t.to_numpy()-MINUTE,o.t.to_numpy(),o.e.to_numpy()-MINUTE,close[:-1]-MINUTE,op]))
    ref_open=np.full((len(needed),20),np.nan); ref_close=ref_open.copy()
    for month in boundary.MONTHS:
        cols=["ticker","hour_end_utc","is_stub","open","high","low","close_input_cap5","close","volume","genuine_count","absent_minutes","longest_gap_minutes","conflict_count","quarantine_count","invalid_minutes"]
        f=pq.read_table(boundary.data_path("hourly",month),columns=cols).to_pandas()
        f=f.loc[~f.is_stub]; ix=np.searchsorted(ends,f.hour_end_utc.astype("int64")); si=f.ticker.map(stock_map).to_numpy()
        assert np.array_equal(ends[ix],f.hour_end_utc.astype("int64"))
        for dest,source in (("O","open"),("H","high"),("L","low"),("C","close_input_cap5"),("G","close")):
            arrays[dest][ix,si]=f[source]
        valid=(f.genuine_count>0)&(f.absent_minutes<=5)&(f.longest_gap_minutes<=5)&(f.conflict_count==0)&(f.quarantine_count==0)&(f.invalid_minutes==0)
        arrays["V"][ix,si]=np.where(valid,f.volume,np.nan)
        c=pq.read_table(boundary.data_path("canonical",month),columns=["ticker","timestamp","open","close","is_rth","is_genuine","is_imputed"]).to_pandas()
        c=c.loc[c.is_rth&c.is_genuine&~c.is_imputed]
        ns=c.timestamp.astype("int64").to_numpy(); k=np.searchsorted(needed,ns); k=np.minimum(k,len(needed)-1)
        c=c.loc[needed[k]==ns].copy(); ns=c.timestamp.astype("int64").to_numpy(); k=np.searchsorted(needed,ns)
        q=np.array([(s,int(t)) in QUARANTINE_NS for s,t in zip(c.ticker,ns)],dtype=bool)
        c=c.loc[~q]; k=k[~q]
        for stock in STOCKS:
            pick=c.ticker.eq(stock).to_numpy(); dates=c.loc[pick,"timestamp"].dt.tz_convert("America/New_York").dt.tz_localize(None).to_numpy(dtype="datetime64[D]").astype(str)
            fac=factor(stock,dates); j=stock_map[stock]
            ref_open[k[pick],j]=c.loc[pick,"open"].to_numpy()*fac
            ref_close[k[pick],j]=c.loc[pick,"close"].to_numpy()*fac
        source_counts.append({"month":month,"source_full_hour_rows":len(f),"endpoint_reference_rows":len(c)})
    session=h.session.to_numpy(); dates=h.date.to_numpy(); regular=sched.index[~sched.early_close & (sched.date<="2024-12-31")].to_numpy()
    regular_dates=sched.iloc[regular].date.to_numpy(); p=np.searchsorted(regular_dates,dates,side="left")-1
    cop_ok=np.ones(n,dtype=bool); after=dates>="2012-05-01"; safe=p>=125
    cop_ok[after]=safe[after]&(regular_dates[np.maximum(p[after]-125,0)]>="2012-05-01")
    cop_window=rolling(cop_ok.astype(float),48,48)==1
    all48=rolling(np.isfinite(arrays["C"]).astype(float),48,48)==1
    stock_gate=all48&(p[:,None]>=125)&(np.cumsum(np.isfinite(arrays["G"]),axis=0)>=360)
    stock_gate[:,1]&=cop_window
    source_gate=stock_gate.all(axis=1)
    ei=o.entry_index.to_numpy(); source=np.zeros(len(o),dtype=bool); valid=ei>=47; source[valid]=source_gate[ei[valid]]
    entry_close=ref_close[np.searchsorted(needed,o.t.to_numpy()-MINUTE)]
    entry_open=ref_open[np.searchsorted(needed,o.t.to_numpy())]
    entry=np.where((o.slot_index.to_numpy()==0)[:,None],entry_open,entry_close)
    end=ref_close[np.searchsorted(needed,o.e.to_numpy()-MINUTE)]
    compatible=np.ones_like(entry,dtype=bool)
    exit_dates=sched.iloc[o.exit_session.to_numpy()].date.to_numpy()
    compatible[:,1]=(o.date.to_numpy()<"2012-05-01")== (exit_dates<"2012-05-01")
    valid_label=np.isfinite(entry)&np.isfinite(end)&(entry>0)&(end>0)&compatible
    R=np.full_like(entry,np.nan); R[valid_label]=np.log(end[valid_label]/entry[valid_label])
    eligible=source&valid_label.all(axis=1)&(o.date.to_numpy()>="2011-04-01")
    curclose=ref_close[np.searchsorted(needed,close[o.session.to_numpy()]-MINUTE)]
    nextopen=ref_open[np.searchsorted(needed,op[o.session.to_numpy()+1])]
    overnight=o.category.eq("OVERNIGHT").to_numpy()
    supported=valid_label&np.isfinite(curclose)&np.isfinite(nextopen)&(curclose>0)&(nextopen>0)&overnight[:,None]
    assert np.all(o.exit_session.to_numpy()[overnight]==o.session.to_numpy()[overnight]+1)
    aux=np.full((*entry.shape,3),np.nan)
    for j,(a,b) in enumerate(((curclose,entry),(nextopen,curclose),(end,nextopen))):
        aux[:,:,j][supported]=np.log(a[supported]/b[supported])
    np.testing.assert_allclose(aux.sum(axis=2)[supported],R[supported],atol=1e-12,rtol=1e-11)
    o["source_input_eligible"]=source; o["eligible"]=eligible
    first=o.first_step.to_numpy(); o["first_date"]=np.where(first>=0,dates[np.maximum(first,0)],"0000")
    arrays.update({"R":R,"aux":aux,"aux_mask":supported,"cop_window":cop_window,"p":p,
                   "price_regime":np.stack([price_basis(s,dates) for s in STOCKS],axis=1),
                   "volume_regime":np.stack([volume_regime(s,dates) for s in STOCKS],axis=1)})
    o.drop(columns="clock").to_parquet(boundary.PHASE/"artifacts/origins.parquet",index=False)
    h.to_parquet(boundary.PHASE/"artifacts/grid.parquet",index=False)
    np.savez_compressed(boundary.PHASE/"artifacts/source_geometry.npz",allow_pickle=False,**arrays,clock=np.stack(o.clock))
    (boundary.PHASE/"audit/source_counts.json").write_text(json.dumps(source_counts,indent=2))
    return {"schedule":sched,"grid":h,"origins":o,"arrays":arrays,"regular":regular}


def role(o: pd.DataFrame,start: str,stop: str,embargo: str="0000") -> np.ndarray:
    cutoff=(pd.Timestamp(stop,tz="America/New_York")+pd.Timedelta(hours=20)).tz_convert("UTC").value
    return np.flatnonzero(o.eligible.to_numpy()&(o.date.to_numpy()>=start)&(o.date.to_numpy()<=stop)&(o.first_date.to_numpy()>embargo)&(o.maturity.to_numpy()<cutoff))


def load_fresh_geometry() -> dict:
    """Load only this replication's newly produced compact source geometry."""
    sched=schedule(); h=pd.read_parquet(boundary.PHASE/"artifacts/grid.parquet"); o=pd.read_parquet(boundary.PHASE/"artifacts/origins.parquet")
    with np.load(boundary.PHASE/"artifacts/source_geometry.npz",allow_pickle=False) as bundle:
        arrays={key:bundle[key] for key in bundle.files}
    o["clock"]=list(arrays.pop("clock"))
    regular=sched.index[~sched.early_close&(sched.date<="2024-12-31")].to_numpy()
    return {"schedule":sched,"grid":h,"origins":o,"arrays":arrays,"regular":regular}


def design_roles(data: dict) -> dict:
    o=data["origins"]; h=data["grid"]; roles={}; counts=[]; candidates=[]
    for y in range(2021,2025):
        prev=y-1; sep=h.loc[h.date<=f"{prev}-09-30","date"].iloc[-1]; dec=h.loc[h.date<=f"{prev}-12-31","date"].iloc[-1]
        chosen=None
        for month in (7,6,5):
            start=f"{prev}-{month:02d}-01"; stop=h.loc[h.date<start,"date"].iloc[-1]; ix=role(o,start,sep,stop)
            slots=o.iloc[ix].slot_index.value_counts().reindex(range(7),fill_value=0); sessions=o.iloc[ix].date.nunique()
            passes=sessions>=50 and slots.min()>=25
            candidates.append({"fold":f"F{y%100}","start":start,"initial_stop":stop,"sessions":sessions,"slot_counts":slots.tolist(),"passes":bool(passes)})
            if passes: chosen=(start,stop,ix); break
        if chosen is None: raise RuntimeError(f"Coverage rule failed F{y%100}")
        start,stop,selector=chosen
        fold={"inner_train":role(o,"2011-04-01",stop),"selector":selector,"restricted_refit":role(o,"2011-04-01",sep),"calibration":role(o,f"{prev}-10-01",dec,sep),"oos":role(o,f"{y}-01-01",f"{y}-12-31",dec)}
        requests={"inner_train":("2011-04-01",stop,"0000"),"selector":(start,sep,stop),"restricted_refit":("2011-04-01",sep,"0000"),"calibration":(f"{prev}-10-01",dec,sep),"oos":(f"{y}-01-01",f"{y}-12-31",dec)}
        source_origins=o.assign(eligible=o.source_input_eligible)
        for name,ix in fold.items():
            row=o.iloc[ix]; mask=data["arrays"]["aux_mask"][ix]
            counts.append({"fold":f"F{y%100}","role":name,"sessions":row.date.nunique(),"origins":len(ix),"rows":len(ix)*20,"first_date":row.date.min(),"last_date":row.date.max(),"overnight_origins":int(row.category.eq("OVERNIGHT").sum()),"supported_triples":int(mask.sum()),"all20_supported_origins":int(mask.all(axis=1).sum()),"source_available_in_nominal_dates":int(((o.date>=row.date.min())&(o.date<=row.date.max())&o.source_input_eligible).sum())})
            counts[-1]["source_available_origins"]=len(role(source_origins,*requests[name]))
            counts[-1]["scoreable_origins"]=len(ix)
        roles[f"F{y%100}"]={"roles":fold,"initial_stop":stop,"refit_stop":sep,"calibration_stop":dec,"year":y}
    pd.DataFrame(counts).to_csv(boundary.PHASE/"audit/role_counts.csv",index=False)
    (boundary.PHASE/"audit/selector_candidates.json").write_text(json.dumps(candidates,indent=2))
    (boundary.PHASE/"artifacts/roles.json").write_text(json.dumps({fold:{**item,"roles":{k:v.tolist() for k,v in item["roles"].items()}} for fold,item in roles.items()},indent=2))
    return roles
