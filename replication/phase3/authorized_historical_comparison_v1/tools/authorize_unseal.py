import json,pathlib,hashlib,datetime,collections
O=pathlib.Path(__file__).resolve().parents[1];R=O.parents[2];P=R/'replication/phase2'
def rd(p):return json.loads(p.read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(n,d):
 with (O/n).open('x') as f:json.dump(d,f,indent=2)
g=rd(O/'comparisons/fresh_integrity_checks.json');assert not g['new_blockers']
lock=rd(P/'audit/PREFIT_ACCEPTANCE.json'); trans=rd(P/'audit/report_source_transition.json')
for e in lock['code_lock']:
 p=P/(trans['old']['executed_snapshot'] if e['path']=='code/evaluation.py' else e['path']);assert h(p)==e['sha256']
assert h(P/'code/evaluation.py')==trans['new']['sha256']
for n,x in lock['evidence_sha256'].items():assert h(P/n)==x
protected=rd(P/'audit/FITTED_ARTIFACTS_BEFORE_REPORT_RECOVERY.json')['files'];assert len(protected)==80
for e in protected:assert h(P/e['path'])==e['sha256'] and (P/e['path']).stat().st_size==e['bytes']
for n in ['scalars','ranks','events','signed','clamping']:
 assert h(P/f'artifacts/report_recovery_v1/metrics/{n}.csv')==h(P/f'artifacts/report_recovery_v1/replay_metrics/{n}.csv')
ledger=[json.loads(x) for x in (P/'artifacts/run/replication_ledger.jsonl').read_text().splitlines()]
starts=[(e['fold'],e['phase']) for e in ledger if e['event']=='PHASE_START']; assert starts==[(f,p) for f in ['F21','F22','F23','F24'] for p in ['initial','refit']]
rec=rd(P/'artifacts/report_recovery_v1/completed.json');assert all(rec[k]==0 for k in ['neural_fit_calls','calibration_fit_calls','threshold_fit_calls'])
reload=rd(P/'artifacts/report_recovery_v1/checkpoint_reload.json');assert len(reload['checks'])==8
for e in reload['checks']:assert e['status']=='EXACT' and h(P/f"artifacts/run/{e['fold']}/refit/final_state.pt")==e['checkpoint_sha256']
assert rd(P/'artifacts/run/failure.json')['message']=='output array is read-only'
g['fresh_semantic_checks']={'prefit_code_test_bindings':18,'prefit_evidence':8,'report_only_transition':'Original executed snapshot and new digest verified; no retroactive all-code-unchanged claim','protected_artifacts':80,'exact_replay_table_pairs':5,'recorded_exact_reload_checks':8,'phase_start_order':starts,'recovery_fit_calls':0,'ledger_event_counts':dict(collections.Counter(e['event'] for e in ledger))}
g['gate_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();g['HISTORICAL_RESULTS_NOT_YET_OPENED']=True
g['metadata_hash_history']=['9aac4a413b64844a3421cc8559c0945311e9b54362c9935fde6a5e7464bde046','77ef9beb43df6065b818ee38da6557d23e082637bad735bc6e32c55099181b9a','40e05edea1150c86288110905314a29852e327bf188df5a0d9413c52fc2a7c70']
wr('QUALIFIED_AUTHORIZATION_AND_SEAL_GATE.json',g)
text=f'''# Qualified authorization and seal gate\n\n**QUALIFIED_SUBSTANTIVE_INTEGRITY_PASS**, {g['gate_utc']}.\n\nThe 2026-11-03 human explicitly accepts only (1) the literal Phase2 `.DS_Store` drift and (2) Classification-B missing-request provenance uncertainty, and separately authorizes historical comparison after this gate. Prior STOPs remain accurate historical records and untouched. No new exception or scientific change is authorized.\n\nFresh verification: anchored manifest152,521bytes;232/232 nonexempt payloads match;233 inventoried entries with no additions/deletions;348/348 allowed source paths/months/families/bytes/SHA match both input receipts;18 original code/test and8 evidence bindings verified with documented report-only transition;80 protected artifacts unchanged;five replay pairs byte-identical;four checkpoint hashes support eight recorded exact reload checks;eight ordered phase starts;zero recovery fit calls. No neural forward or fit was executed here.\n\nExactly two qualifications remain: metadata byte drift; source consumption is supported only by bounded lineage evidence, not exhaustive native-read logging. Zero request events remain among39 receipts. The postrun path aggregation is not a native-read certificate. This is not FULL_FREEZE_INTACT or NATIVE_SOURCE_ACCESS_VERIFIED.\n\nAll prior gate/witness and investigation digests are listed and verified in the JSON; chronology and all known metadata hashes are retained. Current observed metadata hash is in payload_checks. The manifest anchor is conversationally preserved, not an OS recorder.\n\nReviewer: root, sequential review in the continuing conversation; prior historical exposure disclosed. No background agents. Phase2 fitting used separate fresh contexts. Independent arithmetic formulations will cross-check results; no claim of a newly fresh adjudicator context.\n\nHistorical results have not yet been opened for this continuation. Next intended read: `replication/ORIGINAL_RESULTS_SEALED.md`.\n'''
with (O/'QUALIFIED_AUTHORIZATION_AND_SEAL_GATE.md').open('x') as f:f.write(text)
w={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HISTORICAL_RESULTS_NOT_YET_OPENED':True,'next_intended_archive':'replication/ORIGINAL_RESULTS_SEALED.md','reviewer':'Root sequential accountable reviewer; no separate background agent; independent second arithmetic check required','gate_files':[{'path':n,'bytes':(O/n).stat().st_size,'sha256':h(O/n)} for n in ['QUALIFIED_AUTHORIZATION_AND_SEAL_GATE.md','QUALIFIED_AUTHORIZATION_AND_SEAL_GATE.json']]}
wr('PRE_UNSEAL_WITNESS.json',w)
print(json.dumps({'status':g['status'],'witness_sha256':h(O/'PRE_UNSEAL_WITNESS.json'),'utc':w['utc']}))
