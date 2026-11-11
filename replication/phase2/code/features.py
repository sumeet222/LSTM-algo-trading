"""Independent FT16 causal components and phase-fitted recipes."""
from __future__ import annotations
import statistics
import numpy as np
import pandas as pd
from dataset import rolling
from geometry import STOCKS,volume_regime,price_basis

CHANNELS=("M1","M2","M3","M4","V1","V2","V3","B1","B2","Q1","Q2","T1","T2","T3","T4","T5")
COMMON=np.array([0,*range(2,16)])


def quantile(x: np.ndarray,q: float,w: np.ndarray | None=None) -> float:
    x=np.asarray(x,dtype=np.float64)
    if not len(x) or not np.isfinite(x).all(): raise ValueError("Quantile needs finite support")
    if w is None: return float(np.quantile(x,q))
    w=np.asarray(w,dtype=np.float64)
    if not np.isfinite(w).all() or (w<=0).any(): raise ValueError("Quantile needs positive finite mass")
    ix=np.argsort(x,kind="stable"); c=np.cumsum(w[ix]); pos=min(int(np.searchsorted(c/np.sum(w),q,side="left")),len(x)-1)
    return float(x[ix[pos]])


def robust(x: np.ndarray,w: np.ndarray | None=None) -> tuple[float,float,str]:
    center=quantile(x,.5,w); scale=quantile(np.abs(x-center),.5,w); used="MAD"
    if scale<=0: scale=(quantile(x,.75,w)-quantile(x,.25,w))/1.349; used="IQR"
    if scale<=0:
        mean=float(np.average(x,weights=w)); scale=float(np.sqrt(np.average((x-mean)**2,weights=w))); used="SD"
    if scale<=0: scale=1.; used="CONSTANT"
    return center,scale,used


def indicators(C: np.ndarray,regimes: np.ndarray) -> np.ndarray:
    out=np.full((*C.shape,3),np.nan); valid72=np.isfinite(rolling(C,72,69))
    for s in range(C.shape[1]):
        ema=None; count=0; missing=0; previous=np.nan; pending=[]; gains=None; losses=None; updates=0
        for j,c in enumerate(C[:,s]):
            if j and regimes[j,s]!=regimes[j-1,s]:
                ema=None; count=0; missing=0; previous=np.nan; pending=[]; gains=None; losses=None; updates=0
            if not np.isfinite(c):
                missing+=1; previous=np.nan
                if gains is None: pending=[]
                if missing>=3: ema=None; count=0; pending=[]; gains=None; losses=None; updates=0
                continue
            missing=0
            if ema is None: ema=np.full(4,c); count=0
            else:
                alpha=2/(np.array([6.,18.,24.,72.])+1); ema=alpha*c+(1-alpha)*ema; count+=1
            if np.isfinite(previous):
                change=c-previous
                if gains is None:
                    pending.append(change)
                    if len(pending)==14:
                        gains=statistics.fmean(max(v,0) for v in pending)
                        losses=statistics.fmean(max(-v,0) for v in pending); updates=0
                else:
                    assert losses is not None  # Wilder gain/loss state is initialized together.
                    gains=(13*gains+max(change,0))/14; losses=(13*losses+max(-change,0))/14; updates+=1
            previous=c
            if valid72[j,s] and count>=360:
                out[j,s,0]=(ema[0]-ema[1])/c; out[j,s,1]=(ema[2]-ema[3])/c
            if valid72[j,s] and gains is not None and updates>=140:
                assert losses is not None
                out[j,s,2]=0 if gains==0 and losses==0 else 1 if losses==0 else -1 if gains==0 else 1-2/(1+gains/losses)
    return out


def components(data: dict) -> dict:
    a=data["arrays"]; h=data["grid"]; o=data["origins"]; sched=data["schedule"]; regular=data["regular"]
    p=a["p"]; safe=np.maximum(p,0); n=len(h); C=a["C"]; V=a["V"]; reg=a["price_regime"]; vreg=a["volume_regime"]
    with np.errstate(invalid="ignore",divide="ignore"):
        oc=np.log(C/a["O"]); rms12=np.sqrt(rolling(oc**2,12,12)); rms60=np.sqrt(rolling(oc**2,60,57))
    regular_ix=[]; U=[]; D=[]
    for d in regular:
        ix=np.flatnonzero(h.session.to_numpy()==d); assert len(ix)==6
        regular_ix.append(ix[-1]); D.append(a["G"][ix[-1]])
        ok=np.isfinite(V[ix]).all(axis=0)&(vreg[ix[0]]==vreg[ix[-1]])
        U.append(np.where(ok,V[ix].sum(axis=0),np.nan))
    D=np.array(D); U=np.array(U); ridx=np.array(regular_ix)
    dreg=reg[ridx]; ureg=vreg[ridx]
    delta=np.full_like(D,np.nan)
    with np.errstate(invalid="ignore",divide="ignore"):
        delta[1:]=np.where(dreg[1:]==dreg[:-1],np.log(D[1:]/D[:-1]),np.nan)
    rms63=np.sqrt(rolling(delta**2,63,60)); sma=rolling(D,20,19,dreg)
    u5=rolling(U,5,5,ureg); u60=rolling(U,60,57,ureg); sign20=rolling(np.sign(delta),20,19)
    mom5=np.full_like(D,np.nan); mom105=np.full_like(D,np.nan)
    with np.errstate(invalid="ignore",divide="ignore"):
        mom5[5:]=np.log(D[5:]/D[:-5]); mom105[125:]=np.log(D[105:-20]/D[:-125])
    qmean=np.full_like(V,np.nan)
    for slot in range(6):
        ix=np.flatnonzero(h.slot.to_numpy()==slot); shifted=np.vstack([np.full((1,20),np.nan),V[ix[:-1]]])
        val=rolling(shifted,20,19,vreg[ix]); original=np.ones_like(val,dtype=bool)
        original[20:]=vreg[ix[20:]]==vreg[ix[:-20]]
        qmean[ix]=np.where(original,val,np.nan)
    ind=indicators(C,reg)
    mean2=np.full((len(sched),20,7),np.nan); rms2=mean2.copy()
    R=a["R"]; regular_dates=sched.iloc[regular].date.to_numpy()
    # Scheduled regular-origin slots remain present when invalid/immature.
    slotR=np.full((len(regular),20,7),np.nan); maturity=np.zeros((len(regular),7),dtype=np.int64)
    for k,d in enumerate(regular):
        ix=np.flatnonzero(o.session.to_numpy()==d)
        for i in ix:
            context=int(o.iloc[i].context); slotR[k,:,context]=R[i]; maturity[k,context]=int(o.iloc[i].maturity)
    for d,row in sched.iterrows():
        prior=int(np.searchsorted(regular_dates,row.date,side="left")); lock=row.open.value
        for length,minimum,dest,square in ((20,19,mean2,False),(60,57,rms2,True)):
            if prior<length or row.early_close and prior<60: continue
            vals=slotR[prior-length:prior].copy()
            vals=np.where((maturity[prior-length:prior]<lock)[:,None,:],vals,np.nan)
            flat=vals.reshape(length,-1); result=rolling(flat**2 if square else flat,length,minimum)[-1]
            dest[int(d)]=np.sqrt(result).reshape(20,7) if square else result.reshape(20,7)
    return {"oc":oc,"rms12":rms12,"rms60":rms60,"D":D,"U":U,"rms63":rms63,"sma":sma,"u5":u5,"u60":u60,"sign20":sign20,"mom5":mom5,"mom105":mom105,"qmean":qmean,"ind":ind,"mean2":mean2,"rms2":rms2,"ridx":ridx,"daily_vreg":ureg}


def fit_indices(data: dict,stop: str) -> tuple[np.ndarray,np.ndarray]:
    o=data["origins"]; h=data["grid"]
    ix=np.flatnonzero(o.source_input_eligible.to_numpy()&(o.date.to_numpy()>="2011-04-01")&(o.date.to_numpy()<=stop))
    difference=np.zeros(len(h)+1,dtype=np.int64)
    np.add.at(difference,o.first_step.to_numpy()[ix],1); np.add.at(difference,o.entry_index.to_numpy()[ix]+1,-1)
    select=(np.cumsum(difference[:-1])>0)&(h.date.to_numpy()>="2011-04-01")&(h.date.to_numpy()<=stop)
    union=np.flatnonzero(select); _,first=np.unique(h.date.to_numpy()[union],return_index=True)
    return union,union[first]


def native(data: dict,c: dict,recipe: dict) -> tuple[np.ndarray,np.ndarray]:
    a=data["arrays"]; h=data["grid"]; p=a["p"]; safe=np.maximum(p,0); n=len(h)
    C=a["C"]; high=a["H"]; low=a["L"]; V=a["V"]; vf=a["volume_regime"]
    hf=np.array(recipe["hourly_floor"]); df=np.array(recipe["daily_floor"]); mf=np.array(recipe["m2_floor"])
    x=np.full((n,20,16),np.nan)
    qh=np.full_like(C,np.nan); qd=qh.copy()
    for s in range(20):
        for regime,qs in recipe["pseudocounts"][s].items():
            mask=vf[:,s]==int(regime); qh[mask,s]=qs[0]; qd[mask,s]=qs[1]
    with np.errstate(invalid="ignore",divide="ignore"):
        x[:,:,0]=c["oc"]/np.maximum(c["rms60"],hf)
        x[:,:,2]=c["mom5"][safe]/(np.sqrt(5)*np.maximum(c["rms63"][safe],df))
        x[:,:,3]=c["mom105"][safe]/(np.sqrt(105)*np.maximum(c["rms63"][safe],df))
        x[:,:,4]=np.log(np.maximum(c["rms12"],hf)); x[:,:,5]=np.log(np.maximum(c["rms60"],hf)); x[:,:,6]=x[:,:,4]-x[:,:,5]
        x[:,:,7]=np.log(high/low); width=high-low
        b2=(2*C-high-low)/width; b2=np.where(np.isfinite(width)&(width==0),0,b2); b2=np.where(np.abs(b2)>1+1e-10,np.nan,b2); x[:,:,8]=b2
        x[:,:,9]=np.log((V+qh)/(c["qmean"]+qh)); x[:,:,10]=np.log((c["u5"][safe]+qd)/(c["u60"][safe]+qd))
        x[:,:,10]=np.where(c["daily_vreg"][safe]==vf,x[:,:,10],np.nan)
        x[:,:,11]=np.log(C/c["sma"][safe]); x[:,:,12]=c["sign20"][safe]; x[:,:,13:16]=c["ind"]
        m2=c["mean2"][h.session.to_numpy()]/np.maximum(c["rms2"][h.session.to_numpy()],mf[None,:,None])
    x[p<0,:,2:4]=np.nan; x[p<0,:,10:13]=np.nan
    blocked=~a["cop_window"]&(h.date.to_numpy()>="2012-05-01")
    x[blocked,1,:]=np.nan; m2[blocked,1,:]=np.nan
    return x[:,:,COMMON],m2


def fit_recipe(data: dict,c: dict,stop: str) -> tuple[dict,np.ndarray,np.ndarray]:
    ix,unique=fit_indices(data,stop); a=data["arrays"]; h=data["grid"]; p=a["p"]; sd=h.session.to_numpy()[unique]
    recipe={"stop":stop,"fit_hour_count":len(ix),"fit_unique_days":len(unique),"hourly_floor":[],"daily_floor":[],"m2_floor":[],"pseudocounts":[]}
    for s in range(20):
        hour=np.concatenate([c["rms12"][ix,s],c["rms60"][ix,s]]); hour=hour[np.isfinite(hour)&(hour>0)]
        daily=c["rms63"][p[unique],s]; daily=daily[np.isfinite(daily)&(daily>0)]
        recipe["hourly_floor"].append(quantile(hour,.05)); recipe["daily_floor"].append(quantile(daily,.05))
        vals=[]; weights=[]
        for ctx in range(7):
            v=c["rms2"][sd,s,ctx]; v=v[np.isfinite(v)&(v>0)]
            if not len(v): raise ValueError(f"No M2 floor support {STOCKS[s]} context{ctx}")
            vals.extend(v); weights.extend(np.full(len(v),1/(7*len(v))))
        recipe["m2_floor"].append(quantile(np.array(vals),.05,np.array(weights)))
        pairs={}; ddates=h.date.to_numpy()[c["ridx"]]; dclip=(ddates>="2011-04-01")&(ddates<=stop)
        for regime in np.unique(a["volume_regime"][ix,s]):
            v=a["V"][ix,s]; v=v[(a["volume_regime"][ix,s]==regime)&np.isfinite(v)&(v>0)]
            u=c["U"][:,s]; u=u[dclip&(c["daily_vreg"][:,s]==regime)&np.isfinite(u)&(u>0)]
            if len(v) and len(u): pairs[str(int(regime))]=[.01*float(np.median(v)),.01*float(np.median(u))]
        recipe["pseudocounts"].append(pairs)
    x,m2=native(data,c,recipe); centers=[]; scales=[]; methods=[]
    for j,channel in enumerate(COMMON):
        if channel in (8,12,15): center,scale,method=0.,1.,"BOUNDED_IDENTITY"
        else:
            vals=x[ix,:,j].ravel(); vals=vals[np.isfinite(vals)]; center,scale,method=robust(vals)
        centers.append(center); scales.append(scale); methods.append(method)
    vals=[]; weights=[]
    for ctx in range(7):
        v=m2[unique,:,ctx].ravel(); v=v[np.isfinite(v)]
        if not len(v): raise ValueError("No M2 scaler context support")
        vals.extend(v); weights.extend(np.full(len(v),1/(7*len(v))))
    center,scale,method=robust(np.array(vals),np.array(weights))
    recipe.update({"centers":centers,"scales":scales,"scale_methods":methods,"m2_center":center,"m2_scale":scale,"m2_scale_method":method,"fit_indices":ix.tolist(),"unique_day_indices":unique.tolist()})
    return recipe,x,m2


def transform(common: np.ndarray,m2: np.ndarray,recipe: dict) -> tuple[np.ndarray,np.ndarray]:
    center=np.array(recipe["centers"]); scale=np.array(recipe["scales"])
    x=((np.where(np.isfinite(common),common,center)-center)/scale).astype(np.float32)
    m=((np.where(np.isfinite(m2),m2,recipe["m2_center"])-recipe["m2_center"])/recipe["m2_scale"]).astype(np.float32)
    if not np.isfinite(x).all() or not np.isfinite(m).all(): raise ValueError("Nonfinite transformed float32 inputs")
    return x,m


def assembler(data: dict,indices: np.ndarray,common: np.ndarray,m2: np.ndarray):
    o=data["origins"].iloc[indices]; first=o.first_step.to_numpy(); context=o.context.to_numpy(); clock=np.stack(o.clock)
    def get_inputs(local_indices: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
        steps=first[local_indices,None]+np.arange(48)[None,:]
        v=common[steps].transpose(0,2,1,3)
        selected=m2[steps[:,:,None],np.arange(20)[None,None,:],context[local_indices,None,None]].transpose(0,2,1)
        x=np.empty((*v.shape[:-1],16),dtype=np.float32); x[:,:,:,COMMON]=v; x[:,:,:,1]=selected
        return x,clock[local_indices]
    return get_inputs
