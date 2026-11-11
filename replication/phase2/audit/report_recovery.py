"""Audited saved-output-only reporting recovery; no optimizer or fitting calls."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import boundary
boundary.install()
from datetime import datetime,timezone
import json
import resource
import time
import numpy as np
import pandas as pd
import dataset
import features
import model
import evaluation
from geometry import STOCKS

PHASE=boundary.PHASE
OUT=PHASE/"artifacts/report_recovery_v1"


def protect() -> None:
    snapshot=json.loads((PHASE/"audit/FITTED_ARTIFACTS_BEFORE_REPORT_RECOVERY.json").read_text())
    for item in snapshot["files"]:
        path=PHASE/item["path"]
        assert path.stat().st_size==item["bytes"] and boundary.sha256(path)==item["sha256"],item["path"]


def record(event: str,**values) -> None:
    row={"utc":datetime.now(timezone.utc).isoformat(),"event":event,**values}
    with (OUT/"report_recovery_ledger.jsonl").open("a") as stream: stream.write(json.dumps(row)+"\n")
    print(json.dumps(row),flush=True)


def run() -> None:
    protect(); OUT.mkdir(exist_ok=False); start=time.monotonic()
    record("REPORT_RECOVERY_START",neural_fit_calls=0,calibration_fit_calls=0,threshold_fit_calls=0)
    try:
        data=dataset.load_fresh_geometry(); c=features.components(data)
        roles=json.loads((PHASE/"artifacts/roles.json").read_text()); reload=[]
        for fold,item in roles.items():
            recipe=json.loads((PHASE/"artifacts"/f"{fold}_refit_recipe.json").read_text())
            common,m2=features.native(data,c,recipe); common,m2=features.transform(common,m2,recipe)
            restored=model.load_state(PHASE/"artifacts/run"/fold/"refit/final_state.pt")
            for role,filename in (("calibration","calibration_predictions.parquet"),("oos","oos_scores.parquet")):
                ix=np.array(item["roles"][role],dtype=np.int64)
                mh,ah=model.predict_heads(restored,features.assembler(data,ix,common,m2),len(ix))
                saved=pd.read_parquet(PHASE/"artifacts/run"/fold/filename)
                np.testing.assert_array_equal(saved.ticker.to_numpy(),np.tile(STOCKS,len(ix)))
                saved_origins=pd.DatetimeIndex(saved.origin_id).tz_convert("UTC").as_unit("ns").asi8
                np.testing.assert_array_equal(saved_origins,np.repeat(data["origins"].iloc[ix].t.to_numpy(),20))
                np.testing.assert_array_equal(saved.Mhat.to_numpy(),mh.ravel())
                for j,name in enumerate(("pre","gap","post")):
                    np.testing.assert_array_equal(saved[f"Rhat_{name}"].to_numpy(),ah[:,:,j].ravel()*float(recipe["phase_scale"]))
                reload.append({"fold":fold,"role":role,"status":"EXACT","rows":len(saved),"checkpoint_sha256":boundary.sha256(PHASE/"artifacts/run"/fold/"refit/final_state.pt")})
            record("CHECKPOINT_RELOAD_EXACT",fold=fold)
        (OUT/"checkpoint_reload.json").write_text(json.dumps({"status":"PASS","neural_fit_calls":0,"checks":reload},indent=2))
        bundle=PHASE/"artifacts/run/score_bundle/manifest.json"
        scores,_,thresholds=evaluation.read_score_bundle(bundle)
        record("SAVED_SCORE_BUNDLE_VERIFIED",rows=len(scores))
        tables=evaluation.evaluate_scores(scores,thresholds)
        (OUT/"metrics").mkdir()
        for name in ("scalars","ranks","events","signed","clamping"): getattr(tables,name).to_csv(OUT/"metrics"/f"{name}.csv",index=False)
        record("METRICS_COMPLETE")
        replay=evaluation.report_only_replay(bundle,OUT/"replay_metrics")
        for name in ("scalars","ranks","events","signed","clamping"):
            pd.testing.assert_frame_equal(getattr(tables,name),getattr(replay,name),check_exact=True)
            assert boundary.sha256(OUT/"metrics"/f"{name}.csv")==boundary.sha256(OUT/"replay_metrics"/f"{name}.csv")
        protect()
        result={"status":"REPORT_RECOVERY_COMPLETE","neural_fit_calls":0,"calibration_fit_calls":0,"threshold_fit_calls":0,
                "checkpoints_reloaded":4,"checkpoint_predictions":"EXACT","metric_replay":"EXACT","protected_files_unchanged":80,
                "elapsed_seconds":time.monotonic()-start,"peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "original_run_failure":"../run/failure.json","source_transition":"../../audit/report_source_transition.json"}
        (OUT/"completed.json").write_text(json.dumps(result,indent=2)); record("REPORT_RECOVERY_COMPLETE",**{k:v for k,v in result.items() if k!="status"})
    except BaseException as error:
        (OUT/"failure.json").write_text(json.dumps({"status":"REPORT_RECOVERY_FAILED","type":type(error).__name__,"message":str(error)},indent=2))
        record("REPORT_RECOVERY_FAILED",message=str(error)); raise

if __name__=="__main__": run()
