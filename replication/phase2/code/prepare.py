"""All-four no-fit preflight; produces only fresh geometry/recipes and audit receipts."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import json
import resource
import time
import numpy as np
import pandas as pd
import dataset
import features
import model

EXPECTED={
"F21":[(2100,11449,6474,128566,5613),(57,349,195,3890,185),(2164,11846,6697,133012,5822),(56,283,165,3256,131),(188,955,533,10465,421)],
"F22":[(2301,12560,7103,141061,6169),(58,278,152,2901,86),(2366,12888,7286,144561,6273),(50,245,137,2729,126),(210,1180,665,13167,570)],
"F23":[(2526,13776,7793,154640,6719),(59,313,177,3477,148),(2592,14137,7998,158667,6889),(48,258,139,2763,122),(187,887,505,9978,389)],
"F24":[(2719,14824,8380,166238,7202),(69,291,167,3291,124),(2795,15167,8578,170146,7354),(40,163,90,1782,72),(208,991,570,11251,433)]}


def run():
    start=time.time(); data=dataset.load_fresh_geometry() if "--load-fresh-geometry" in sys.argv else dataset.build(); roles=dataset.design_roles(data)
    print("Fresh geometry and roles built",flush=True)
    counts=pd.read_csv(boundary.PHASE/"audit/role_counts.csv"); checks=[]
    for fold,rows in EXPECTED.items():
        for name,expected in zip(("inner_train","selector","restricted_refit","calibration","oos"),rows):
            row=counts.loc[(counts.fold==fold)&(counts.role==name)].iloc[0]
            actual=tuple(int(row[k]) for k in ("sessions","origins","overnight_origins","supported_triples","all20_supported_origins"))
            checks.append({"fold":fold,"role":name,"expected":expected,"actual":actual,"pass":expected==actual})
    (boundary.PHASE/"audit/geometry_checks.json").write_text(json.dumps(checks,indent=2))
    if not all(row["pass"] for row in checks):
        print(json.dumps([x for x in checks if not x["pass"]],indent=2),flush=True)
        raise RuntimeError("Fresh geometry differs from specification; investigate before fitting")
    c=features.components(data); print("FT16 causal components built",flush=True)
    receipts=[]; fallback=[]
    for fold,item in roles.items():
        for phase,role_name,stop in (("initial","inner_train",item["initial_stop"]),("refit","restricted_refit",item["refit_stop"])):
            recipe,x,m=features.fit_recipe(data,c,stop); ix=item["roles"][role_name]; o=data["origins"].iloc[ix]; a=data["arrays"]
            scale=model.fit_scale(a["R"][ix],o.date.to_numpy()); weights=model.auxiliary_weights(o.date.to_numpy(),o.category.eq("OVERNIGHT").to_numpy(),a["aux_mask"][ix])
            recipe.update({"phase_scale":scale,"auxiliary_Z":weights.mass,"auxiliary_sessions":weights.overnight_sessions,"primary_sessions":weights.sessions})
            destination=boundary.PHASE/"artifacts"/f"{fold}_{phase}_recipe.json"
            destination.write_text(json.dumps(recipe,indent=2,allow_nan=False))
            tx,tm=features.transform(x,m,recipe)
            for role_name2,indices in item["roles"].items():
                getter=features.assembler(data,indices,tx,tm)
                for lo in range(0,len(indices),32):
                    X,clock=getter(np.arange(lo,min(lo+32,len(indices))))
                    assert X.shape==(len(X),20,48,16) and np.isfinite(X).all() and np.isfinite(clock).all()
                # Incidence counted over windows deliberately, not estimator weighting.
                ro=data["origins"].iloc[indices]
                for slot in range(7):
                    sel=np.flatnonzero(ro.slot_index.to_numpy()==slot)
                    if not len(sel): continue
                    steps=ro.first_step.to_numpy()[sel,None]+np.arange(48)[None,:]
                    common_missing=~np.isfinite(x[steps]); ctx=int(ro.context.iloc[sel[0]])
                    m_missing=~np.isfinite(m[steps,: ,ctx])
                    for s,stock in enumerate(__import__("geometry").STOCKS):
                        for j,channel in enumerate(features.COMMON):
                            fallback.append((fold,phase,role_name2,slot,stock,features.CHANNELS[channel],int(common_missing[:,:,s,j].sum()),len(sel)*48))
                        fallback.append((fold,phase,role_name2,slot,stock,"M2",int(m_missing[:,:,s].sum()),len(sel)*48))
            receipts.append({"fold":fold,"phase":phase,"status":"PASS","recipe_sha256":boundary.sha256(destination),"fit_hours":recipe["fit_hour_count"],"fit_unique_days":recipe["fit_unique_days"],"scale":scale,"aux_Z":weights.mass})
            print(fold,phase,"recipe and all role tensors PASS",flush=True)
    pd.DataFrame(fallback,columns=["fold","phase","role","clock_slot_index","ticker","channel","fallback_steps","total_steps"]).to_csv(boundary.PHASE/"audit/fallback_incidence.csv",index=False)
    result={"status":"PASS","real_neural_fits":0,"phases":receipts,"elapsed_seconds":time.time()-start,"peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (boundary.PHASE/"audit/all_fold_preflight.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=="__main__": run()
