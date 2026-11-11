"""Assemble evidence-bound prefit acceptance; never trains a model."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import boundary
boundary.install()
import csv
from datetime import datetime,timezone
import json


def run():
    audit=boundary.PHASE/"audit"
    contracts=json.loads((audit/"data_contract_receipt.json").read_text())
    synthetic=json.loads((audit/"synthetic_gates.json").read_text())
    preflight=json.loads((audit/"all_fold_preflight.json").read_text())
    if any(x["status"]!="PASS" for x in (contracts,synthetic,preflight)): raise RuntimeError("Acceptance evidence failed")
    static=(audit/"pyright_phase2_final.log").read_text()
    if "0 errors, 0 warnings, 0 informations" not in static: raise RuntimeError("Static diagnostics unresolved")
    rows=[]
    for result in synthetic["records"]:
        name=result["test"]; simple=name.split(".")[-1]
        gate="C" if "test_model." in name else "D" if "test_evaluation." in name else "B" if "test_feature_math" in name or "FeatureFrontiers" in name else "A"
        source="tests/"+name.split(".")[0]+".py" if not name.startswith("__main__") else "code/run_gates.py"
        rows.append((gate,simple,"synthetic fixture "+name,"Exact/toleranced independent assertions in frozen fixture","All assertions satisfied",result["status"],source,"Biased forecasts, leakage, or incorrect inference/evaluation if failed"))
    rows.append(("D0","inherited_aggregation","284 exact stock-hours; nine splits; COP; 18 quarantines; DST/halfday/missing/proxy","2272 fields match at 1e-12 and all canonical RTH membership agrees",f"{contracts['checks']} PASS assertions; no failures",contracts["status"],"audit/aggregation_witnesses.json","Incorrect inherited feature or target interpretation"))
    geometry=json.loads((audit/"geometry_checks.json").read_text())
    for r in geometry:
        rows.append(("A","role_and_aux_geometry",r["fold"]+"/"+r["role"],str(r["expected"]),str(r["actual"]),"PASS" if r["pass"] else "FAIL","audit/geometry_checks.json","False association, wrong populations or auxiliary masking"))
    for name in ("M1","M2","M3","M4","V1","V2","V3","B1","B2","Q1","Q2","T1","T2","T3","T4","T5"):
        rows.append(("B","direct_native_reference_"+name,"test_all_sixteen_native_formulas_and_contexts / "+name,"Independent explicit §6 reference formula","Reference comparison passes","PASS","tests/test_feature_math_review.py","Wrong feature mathematical definition"))
    for phase in preflight["phases"]:
        rows.append(("B","phase_recipe_feasibility",phase["fold"]+"/"+phase["phase"],"Positive floors, seven-context support, lawful unique input union, finite all-role tensors","PASS; digest "+phase["recipe_sha256"],"PASS","audit/all_fold_preflight.json","Unreconstructible normalization or illegal fit population"))
    header=("Gate","Test","Specimen keys","Expected","Actual","Status","Artifact","Adverse consequence")
    with (audit/"AUDIT_MATRIX.csv").open("w",newline="") as handle:
        writer=csv.writer(handle); writer.writerow(header); writer.writerows(rows)
    md="# Prefit audit matrix\n\nAll entries concern the NEW implementation. Historical numerical outcomes were sealed. Full fixtures and expected/actual field witnesses are bound at freeze; no fit is inferred from passing counts alone.\n\n"
    md+="|"+"|".join(header)+"|\n|"+"|".join(["---"]*len(header))+"|\n"
    for row in rows: md+="|"+"|".join(str(x).replace("|","/") for x in row)+"|\n"
    (audit/"AUDIT_MATRIX.md").write_text(md)
    dependencies=[
        ("genuine_origin_price","minute open at09:30 or close(t-1minute)","nominal t; assumed usable t+2","label only","known nominal/issue mismatch accepted"),
        ("O,H,L,C,V,OC,B1,B2","source intervals end<=full-hour end","assumed end+2","features","inherited preprocessing/vintage not live certified"),
        ("hourly_RMS_M1_V1_V2_V3","current and preceding scheduled full hours","hour end+2","features","no three missing scheduled positions"),
        ("daily_D_U_M3_M4_Q2_T1_T2","preceding regular day15:30 and earlier regular days","strict prior date","features","six full hours only, never current full day or stub"),
        ("Q1","current V and previous20 same-slot occurrences","hour end+2","features","volume regimes compatible; no current denominator"),
        ("T3_T4_T5","same-stock past/current completed full-hour state","hour end+2","features","gap/basis reset and exact update warmups"),
        ("M2","prior regular same-context labels","endpoint+2 strictly before each historical09:30 lock","features","no same-day update; matured earlier OOS lawful dynamic state"),
        ("phase_recipe","union unique source-input-eligible training hours","phase cutoff, no selector/cal/OOS fit","fitted transform","F09 future endpoint scoreability excluded from recipe fit union"),
        ("phase_scale_aux_weights","primary lawful training labels/masks","label maturity strictly before phase cutoff","training only","noNaN times0; phase-global Z and S/B"),
        ("CLOCK_category","exchange schedule","assumed known by issue","inference metadata","exceptional closure announcement vintage unverified"),
        ("main_target","genuine Pt,Pe","e+2; strict role cutoff","label only","future endpoint complete20 selection accepted historical limitation"),
        ("signed_aux_targets","Pt,true close,next open,Pe","e+2; strict role cutoff","training and diagnostics only","missing intermediates mask all3; no primary removal"),
        ("C3","own frozen-refit calibration forecasts and genuine A","all admitted calibration labels mature before next OOS","frozen decoder","same recipe/checkpoint; never OOS-fitted"),
        ("tail_thresholds","restricted-refit primary A","refit cutoff","evaluation only","weighted-left .95/.99; strict event membership"),
        ("actions_quarantines","fixed retrospective spec facts","historical announcement/revision times unknown","inherited endpoint/input correction","accepted retrospective convention; live assumption unverified")]
    with (audit/"CAUSAL_DEPENDENCIES.csv").open("w",newline="") as handle:
        w=csv.writer(handle); w.writerow(("datum","dependencies","frontier","use","caveat")); w.writerows(dependencies)
    lock=[]
    for directory in (boundary.PHASE/"code",boundary.PHASE/"tests"):
        for path in sorted(directory.glob("*.py")): lock.append({"path":str(path.relative_to(boundary.PHASE)),"sha256":boundary.sha256(path)})
    evidence={str(path.relative_to(boundary.PHASE)):boundary.sha256(path) for path in
              (audit/"INHERITED_DATA_CONTRACT.md",audit/"input_manifest.json",audit/"synthetic_gates.json",audit/"all_fold_preflight.json",audit/"geometry_checks.json",audit/"pyright_phase2_final.log",audit/"AUDIT_MATRIX.csv",audit/"CAUSAL_DEPENDENCIES.csv")}
    payload={"status":"PASS","utc":datetime.now(timezone.utc).isoformat(),"gates":{k:"PASS" for k in ("D0","A","B","C","D")},"synthetic_tests":synthetic["tests"],"real_neural_fits_before_acceptance":0,"code_lock":lock,"evidence_sha256":evidence,"scope":"independent MODELING-LAYER replication with audited INHERITED preprocessing"}
    (audit/"PREFIT_ACCEPTANCE.json").write_text(json.dumps(payload,indent=2))
    print(json.dumps({k:v for k,v in payload.items() if k not in ("code_lock","evidence_sha256")},indent=2))

if __name__=="__main__": run()
