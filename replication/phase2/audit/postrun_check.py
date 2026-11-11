"""Post-run integrity/freeze utility; never imports numerical/modeling modules."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import boundary
boundary.install()
import atexit
from datetime import datetime,timezone
import json
import os

PHASE=boundary.PHASE
AUDIT=PHASE/"audit"
RUN=PHASE/"artifacts/run"


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path,payload) -> None:
    path.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n")


def verify_prefit() -> dict:
    receipt=read(AUDIT/"PREFIT_ACCEPTANCE.json")
    transition=read(AUDIT/"report_source_transition.json")
    changed=[]
    for item in receipt["code_lock"]:
        current=boundary.sha256(PHASE/item["path"])
        if current!=item["sha256"]:
            assert item["path"]==transition["old"]["path"]=="code/evaluation.py"
            assert item["sha256"]==transition["old"]["sha256"]
            assert boundary.sha256(PHASE/transition["old"]["executed_snapshot"])==item["sha256"]
            assert current==transition["new"]["sha256"]
            old=(PHASE/transition["old"]["executed_snapshot"]).read_text()
            new=(PHASE/item["path"]).read_text()
            assert new==old.replace('selected = rows["aux_supported"].to_numpy(dtype=bool)','selected = rows["aux_supported"].to_numpy(dtype=bool).copy()',1)
            changed.append(item["path"])
    for relative,digest in receipt["evidence_sha256"].items():
        assert boundary.sha256(PHASE/relative)==digest,relative
    assert changed==["code/evaluation.py"]
    return {"status":"PASS_WITH_EXPLICIT_REPORT_ONLY_TRANSITION","code_test_files":len(receipt["code_lock"]),"evidence_files":len(receipt["evidence_sha256"]),"report_only_changed_files":changed,"transition":"report_source_transition.json","original_prefit_lock_unchanged":True}


def verify_inputs() -> dict:
    items=read(AUDIT/"input_manifest.json")
    assert len(items)==348
    checked=[]
    for item in items:
        path=boundary.ROOT/item["path"]
        assert str(path) in boundary.ALLOWED_DATA
        assert item["family"] in ("hourly","canonical")
        assert path.stat().st_size==item["bytes"],str(path)
        digest=boundary.sha256(path)
        assert digest==item["sha256"],str(path)
        checked.append({"path":item["path"],"bytes":item["bytes"],"sha256":digest})
    return {"status":"PASS","utc":datetime.now(timezone.utc).isoformat(),"checked_inputs":348,"changed":0,"files":checked}


def imports() -> dict:
    observed={}; events=[]; pids=[]; forbidden=[]
    for path in sorted(AUDIT.glob("provenance_*.json")):
        receipt=read(path); pids.append(receipt["pid"])
        events.extend(receipt["file_events"])
        for name,filename in receipt["modules"].items():
            if "lstm_data" in name or "__editable__" in name: forbidden.append((name,filename))
            source=Path(filename)
            if boundary.ROOT in source.parents and not (PHASE in source.parents or boundary.ROOT/".venv" in source.parents): forbidden.append((name,filename))
            observed[(name,filename)]=None
    assert not forbidden,forbidden
    entries=[]
    for name,filename in sorted(observed):
        path=Path(filename)
        entry={"module":name,"observed_path":filename}
        if path.is_file():
            entry.update({"bytes":path.stat().st_size,"sha256":boundary.sha256(path)})
        else: entry["status"]="NO_ON_DISK_FILE"
        entries.append(entry)
    admitted=[e for e in events if e["path"] in boundary.ALLOWED_DATA]
    denied=[e for e in events if e["event"].startswith("DENIED:")]
    assert all(Path(e["path"]).name=="FORBIDDEN_BOUNDARY_PROBE" for e in denied)
    return {"status":"PASS","process_ids":sorted(set(pids)),"modules":entries,"original_project_modules":0,
        "admitted_input_paths_observed":sorted({e["path"] for e in admitted}),"denied_events":denied,
        "source_version_transition":read(AUDIT/"report_source_transition.json"),
        "scope":"Python module __file__ origins and project-path audit events; file hashes are measured at postrun collection, not at each earlier import. Original executed evaluation source and its report-only version transition are separately bound. Explicit admitted-data requests cover native-reader entry points. Not an OS sandbox or exhaustive transitive native-library/syscall inventory."}


def verify_run() -> dict:
    recovery=PHASE/"artifacts/report_recovery_v1"
    completion=read(recovery/"completed.json"); assert completion["status"]=="REPORT_RECOVERY_COMPLETE"
    assert completion["neural_fit_calls"]==completion["calibration_fit_calls"]==completion["threshold_fit_calls"]==0
    ledger=[json.loads(line) for line in (RUN/"replication_ledger.jsonl").read_text().splitlines()]
    expected=[(fold,phase) for fold in ("F21","F22","F23","F24") for phase in ("initial","refit")]
    for event in ("PHASE_START","PHASE_COMPLETE"):
        assert [(r["fold"],r["phase"]) for r in ledger if r["event"]==event]==expected
    failures=[r for r in ledger if "FAIL" in r["event"]]
    assert len(failures)==1 and failures[0]["error_type"]=="ValueError" and failures[0]["message"]=="output array is read-only"
    assert ledger.index(failures[0])>max(i for i,r in enumerate(ledger) if r["event"]=="FOLD_COMPLETE")
    phases=[]
    for fold in ("F21","F22","F23","F24"):
        initial=read(RUN/fold/"initial/started.json"); refit=read(RUN/fold/"refit/started.json")
        assert initial["initial_digest"]==refit["initial_digest"]
        chosen=read(RUN/fold/"initial/completed.json"); final=read(RUN/fold/"refit/completed.json")
        assert chosen["selected_epochs"]==final["epochs_executed"]
        assert initial["initial_optimizer_state_entries"]==refit["initial_optimizer_state_entries"]==0
        phases.append({"fold":fold,"initial_epochs":chosen["epochs_executed"],"selected_epochs":chosen["selected_epochs"],"refit_epochs":final["epochs_executed"],"initial_digest":initial["initial_digest"],"refit_final_digest":final["final_digest"]})
    reload=read(recovery/"checkpoint_reload.json"); assert reload["status"]=="PASS" and len(reload["checks"])==8
    assert all(r["status"]=="EXACT" for r in reload["checks"])
    assert completion["metric_replay"]=="EXACT"
    for name in ("scalars","ranks","events","signed","clamping"):
        assert boundary.sha256(recovery/"metrics"/f"{name}.csv")==boundary.sha256(recovery/"replay_metrics"/f"{name}.csv")
    snapshot=read(AUDIT/"FITTED_ARTIFACTS_BEFORE_REPORT_RECOVERY.json")
    for item in snapshot["files"]:
        assert (PHASE/item["path"]).stat().st_size==item["bytes"] and boundary.sha256(PHASE/item["path"])==item["sha256"],item["path"]
    return {"status":"PASS_AFTER_REPORT_ONLY_RECOVERY","real_phases":8,"neural_retries":0,"report_failures":1,"audited_report_retries":1,"phase_order":expected,"phases":phases,"metric_replay":"EXACT","reload":"EXACT","protected_files_unchanged":len(snapshot["files"]),"successful_fold_peak_rss_bytes":max(r["peak_rss_bytes"] for r in ledger if r["event"]=="FOLD_COMPLETE"),"failed_original_process_total_peak":"NOT-VERIFIABLE after exit; successful fold peak and recovery peak retained","completion":completion}


def check() -> None:
    run=verify_run(); prefit=verify_prefit(); original_inputs=verify_inputs()
    # Persist this validator's opens before collecting module/file receipts.
    boundary.receipt()
    lock=imports()
    write(AUDIT/"postrun_input_immutability.json",original_inputs)
    write(AUDIT/"IMPORT_LOCK.json",lock)
    files=[p for p in PHASE.rglob("*") if p.is_file()]
    size=sum(p.stat().st_size for p in files)
    preflight=read(AUDIT/"all_fold_preflight.json")
    resource={"status":"PASS" if size<2_500_000_000 and max(preflight["peak_rss_bytes"],run["completion"]["peak_rss_bytes"])<2_000_000_000 else "FAIL",
        "new_output_bytes_before_final_documents_and_manifest":size,"new_output_limit_bytes":2_500_000_000,
        "report_recovery_peak_rss_bytes":run["completion"]["peak_rss_bytes"],"successful_fold_peak_rss_bytes":run["successful_fold_peak_rss_bytes"],"prefit_peak_rss_bytes":preflight["peak_rss_bytes"],
        "failed_original_process_total_peak":"NOT-VERIFIABLE; final reporting failure happened after last fold resource receipt",
        "process_memory_intent_bytes":2_000_000_000,"project_total_size":"NOT-VERIFIABLE under no global/protected path inventory boundary"}
    assert resource["status"]=="PASS"
    write(AUDIT/"POSTRUN_INTEGRITY.json",{"status":"PASS","utc":datetime.now(timezone.utc).isoformat(),"prefit":prefit,"run":run,"resources":resource,"inputs":"postrun_input_immutability.json","imports":"IMPORT_LOCK.json"})
    print(json.dumps({"status":"PASS","real_phases":8,"input_hashes":348,"original_project_imports":0,"resources":resource},indent=2))


def freeze() -> None:
    integrity=read(AUDIT/"POSTRUN_INTEGRITY.json"); assert integrity["status"]=="PASS"
    verify_prefit()
    assert "COMPLETE_AND_FROZEN" in (PHASE/"PHASE2_HANDOFF.md").read_text()
    target=PHASE/"PHASE2_FROZEN_MANIFEST.json"
    if target.exists(): raise RuntimeError("Never overwrite a freeze manifest")
    # No atexit write may appear after the immutable manifest is generated.
    boundary.receipt(); atexit.unregister(boundary.receipt)
    paths=sorted(p for p in PHASE.rglob("*") if p.is_file())
    files=[{"path":str(p.relative_to(PHASE)),"bytes":p.stat().st_size,"sha256":boundary.sha256(p)} for p in paths]
    manifest={"status":"COMPLETE_AND_FROZEN","freeze_utc":datetime.now(timezone.utc).isoformat(),"scope":"independent MODELING-LAYER replication with audited INHERITED preprocessing",
        "historical_comparison_performed":False,"manifest_self_excluded":True,"manifest_self_reason":"A file cannot contain its own stable cryptographic digest; all pre-existing Phase2 files are inventoried.",
        "new_output_bytes_excluding_this_manifest":sum(x["bytes"] for x in files),"files":files,"admitted_inputs":read(AUDIT/"input_manifest.json"),
        "postrun_input_immutability_sha256":boundary.sha256(AUDIT/"postrun_input_immutability.json"),"import_lock_sha256":boundary.sha256(AUDIT/"IMPORT_LOCK.json"),
        "prefit_acceptance_sha256":boundary.sha256(AUDIT/"PREFIT_ACCEPTANCE.json"),"postrun_integrity_sha256":boundary.sha256(AUDIT/"POSTRUN_INTEGRITY.json"),
        "residuals":["nominal t versus assumed issue t+2 preserved","inherited preprocessing and retrospective source decisions","fixed survivor sample/F09 scoreability","unverified historical/live provenance","literal raw OOS-forward/C3 call-order deviation; dependency-equivalent","synthetic floating quantile boundary FAIL; all actual thresholds/scales and tail memberships verified unaffected","one reporting failure corrected by explicit boolean-mask copy; one saved-output-only report retry, zero neural retries","comparators deferred"],
        "phase3":"Separate reviewer/authorization required; verify this manifest first. Do not unseal historical outcomes into this implementing context."}
    write(target,manifest); os.chmod(target,0o444)
    # Read-only self-verification of exact inventory identities after writing.
    assert all((PHASE/x["path"]).stat().st_size==x["bytes"] and boundary.sha256(PHASE/x["path"])==x["sha256"] for x in files)
    print(json.dumps({"status":"COMPLETE_AND_FROZEN","files":len(files),"manifest_sha256":boundary.sha256(target),"new_output_bytes_including_manifest":sum(x["bytes"] for x in files)+target.stat().st_size},indent=2))

if __name__=="__main__":
    if "--freeze" in sys.argv: freeze()
    else: check()
