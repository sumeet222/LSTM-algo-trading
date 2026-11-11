"""Exactly four fresh initial/refit pairs; refuse unpassed gates or any restart."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
from dataclasses import asdict
from datetime import datetime,timezone
import gc
import json
import resource
import time
import numpy as np
import pandas as pd
import dataset
import features
import model
import evaluation
from geometry import STOCKS,MINUTE

RUN=boundary.PHASE/"artifacts/run"


def ledger(event: str,**fields) -> None:
    row={"utc":datetime.now(timezone.utc).isoformat(),"event":event,**fields}
    with (RUN/"replication_ledger.jsonl").open("a") as handle:
        handle.write(json.dumps(row,allow_nan=False)+"\n"); handle.flush()
    print(json.dumps(row),flush=True)


def metadata(data: dict,ix: np.ndarray) -> pd.DataFrame:
    o=data["origins"].iloc[ix]; a=data["arrays"]; weights=np.repeat(model.origin_weights(o.date.to_numpy())/20,20)
    frame=pd.DataFrame({"origin_id":np.repeat([pd.Timestamp(t,unit="ns",tz="UTC").isoformat() for t in o.t],20),
        "session_date_et":np.repeat(o.date.to_numpy(),20),"slot":np.repeat(np.array(["09:30","10:30","11:30","12:30","13:30","14:30","15:30"])[o.slot_index.to_numpy()],20),
        "category":np.repeat(o.category.to_numpy(),20),"ticker":np.tile(STOCKS,len(ix)),"weight":weights,
        "entry_end_utc":pd.to_datetime(np.repeat(o.t.to_numpy(),20),utc=True),"exit_end_utc":pd.to_datetime(np.repeat(o.e.to_numpy(),20),utc=True),
        "label_maturity_utc":pd.to_datetime(np.repeat(o.maturity.to_numpy(),20),utc=True),"issue_utc":pd.to_datetime(np.repeat(o.t.to_numpy()+2*MINUTE,20),utc=True),
        "A":np.abs(a["R"][ix]).ravel(),"R":a["R"][ix].ravel(),"early_close":np.repeat(o.early_close.to_numpy(),20),"aux_supported":a["aux_mask"][ix].ravel()})
    for j,name in enumerate(("pre","gap","post")): frame[f"R_{name}"]=a["aux"][ix,:,j].ravel()
    return frame


def phase(data: dict,ix: np.ndarray,common: np.ndarray,m2: np.ndarray,scale: float) -> model.PhaseData:
    o=data["origins"].iloc[ix]; a=data["arrays"]
    return model.PhaseData(o.date.to_numpy(),a["R"][ix],o.category.eq("OVERNIGHT").to_numpy(),a["aux"][ix],a["aux_mask"][ix],features.assembler(data,ix,common,m2),scale)


def inputs(data: dict,c: dict,fold: str,name: str) -> tuple[dict,np.ndarray,np.ndarray]:
    recipe=json.loads((boundary.PHASE/"artifacts"/f"{fold}_{name}_recipe.json").read_text())
    x,m=features.native(data,c,recipe); x,m=features.transform(x,m,recipe)
    return recipe,x,m


def run() -> None:
    gate=json.loads((boundary.PHASE/"audit/PREFIT_ACCEPTANCE.json").read_text())
    if gate["status"]!="PASS" or set(gate["gates"])!={"D0","A","B","C","D"}: raise RuntimeError("All prefit acceptance gates required")
    for item in gate["code_lock"]:
        path=boundary.PHASE/item["path"]
        if boundary.sha256(path)!=item["sha256"]: raise RuntimeError(f"Prefit code changed: {path.name}")
    RUN.mkdir(exist_ok=False)
    start=time.monotonic(); ledger("RUN_START",real_phase_limit=8,seed=42,runtime=model.configure_runtime())
    scores=[]; calibrations={}; thresholds={}; reload_checks=[]
    try:
        data=dataset.load_fresh_geometry(); c=features.components(data)
        roles=json.loads((boundary.PHASE/"artifacts/roles.json").read_text())
        for fold,item in roles.items():
            year=int(item["year"]); idx={k:np.array(v,dtype=np.int64) for k,v in item["roles"].items()}
            initial,x,m=inputs(data,c,fold,"initial")
            train=phase(data,idx["inner_train"],x,m,float(initial["phase_scale"])); selector=phase(data,idx["selector"],x,m,float(initial["phase_scale"]))
            ledger("PHASE_START",fold=fold,phase="initial")
            selected=model.train_selector(train,selector,output_dir=RUN/fold/"initial",progress=lambda r:ledger("EPOCH",fold=fold,phase="initial",**asdict(r)))
            epochs=selected.selected_epochs; initial_digest=selected.initial_digest
            ledger("PHASE_COMPLETE",fold=fold,phase="initial",selected_epochs=epochs,executed_epochs=len(selected.records))
            del selected,train,selector,x,m; gc.collect()
            refit,x,m=inputs(data,c,fold,"refit"); fit=phase(data,idx["restricted_refit"],x,m,float(refit["phase_scale"]))
            ledger("PHASE_START",fold=fold,phase="refit",epochs=epochs)
            fitted=model.train_refit(fit,epochs,output_dir=RUN/fold/"refit",progress=lambda r:ledger("EPOCH",fold=fold,phase="refit",**asdict(r)))
            if fitted.initial_digest!=initial_digest: raise RuntimeError("Fresh initial/refit parameter identity failed")
            ledger("PHASE_COMPLETE",fold=fold,phase="refit",epochs=epochs,final_digest=fitted.final_digest)
            identity=evaluation.ModelIdentity(boundary.sha256(boundary.PHASE/"artifacts"/f"{fold}_refit_recipe.json"),boundary.sha256(RUN/fold/"refit/final_state.pt"))
            cal_get=features.assembler(data,idx["calibration"],x,m); oos_get=features.assembler(data,idx["oos"],x,m)
            cm,ca=model.predict_heads(fitted.model,cal_get,len(idx["calibration"]))
            om,oa=model.predict_heads(fitted.model,oos_get,len(idx["oos"]))
            loaded=model.load_state(RUN/fold/"refit/final_state.pt")
            cm2,ca2=model.predict_heads(loaded,cal_get,len(idx["calibration"])); om2,oa2=model.predict_heads(loaded,oos_get,len(idx["oos"]))
            for first,second in ((cm,cm2),(ca,ca2),(om,om2),(oa,oa2)):
                if not np.array_equal(first,second): raise RuntimeError("Checkpoint reload predictions differ")
            reload_checks.append({"fold":fold,"status":"PASS","calibration_and_oos_main_aux_exact":True,"checkpoint_sha256":identity.checkpoint_sha256})
            cal=metadata(data,idx["calibration"]); cal["Mhat"]=cm.ravel()
            for j,name in enumerate(("pre","gap","post")): cal[f"Rhat_{name}"]=ca[:,:,j].ravel()*float(refit["phase_scale"])
            cutoff=pd.Timestamp(item["calibration_stop"],tz="America/New_York")+pd.Timedelta(hours=20)
            finalization=pd.Timestamp(f"{year}-01-01",tz="America/New_York")
            if not isinstance(cutoff,pd.Timestamp) or not isinstance(finalization,pd.Timestamp): raise ValueError("Invalid calibration frontier")
            calibration=evaluation.fit_c3(cal,float(refit["phase_scale"]),identity,role_cutoff_utc=cutoff,finalized_at_utc=finalization)
            cal.to_parquet(RUN/fold/"calibration_predictions.parquet",index=False)
            (RUN/fold/"calibration.json").write_text(json.dumps(asdict(calibration),indent=2,allow_nan=False))
            out=metadata(data,idx["oos"])
            for j,name in enumerate(("pre","gap","post")): out[f"Rhat_{name}"]=oa[:,:,j].ravel()*float(refit["phase_scale"])
            out=evaluation.build_score_frame(out,om.ravel(),calibration,identity)
            out.to_parquet(RUN/fold/"oos_scores.parquet",index=False)
            scores.append(out); calibrations[year]=calibration
            thresholds[year]=evaluation.fit_tail_thresholds(metadata(data,idx["restricted_refit"]))
            ledger("FOLD_COMPLETE",fold=fold,score_rows=len(out),checkpoint_reload="EXACT",peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            del fitted,loaded,fit,x,m; gc.collect()
        bundle=evaluation.write_score_bundle(RUN/"score_bundle",pd.concat(scores,ignore_index=True),calibrations,thresholds,run_id="independent-modeling-layer-s2c-ca-phase2")
        result=evaluation.evaluate_scores(pd.concat(scores,ignore_index=True),thresholds)
        metrics=RUN/"metrics"; metrics.mkdir()
        for name in ("scalars","ranks","events","signed","clamping"): getattr(result,name).to_csv(metrics/f"{name}.csv",index=False)
        replay=evaluation.report_only_replay(bundle,RUN/"replay_metrics")
        for name in ("scalars","ranks","events","signed","clamping"):
            pd.testing.assert_frame_equal(getattr(result,name),getattr(replay,name),check_exact=True)
        (RUN/"replay_and_reload.json").write_text(json.dumps({"status":"PASS","metric_replay":"EXACT","checkpoints":reload_checks},indent=2))
        ledger("RUN_COMPLETE",real_phases=8,elapsed_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        (RUN/"completed.json").write_text(json.dumps({"status":"COMPLETE","real_phases":8,"elapsed_seconds":time.monotonic()-start,"peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2))
    except BaseException as error:
        ledger("FAILED_STOP_NO_RETRY",error_type=type(error).__name__,message=str(error))
        (RUN/"failure.json").write_text(json.dumps({"status":"FAILED_STOP_NO_RETRY","error_type":type(error).__name__,"message":str(error)},indent=2))
        raise

if __name__=="__main__": run()
