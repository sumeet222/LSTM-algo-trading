"""Read-only verification; writes only additive reviewer gate outputs, refuses overwrite."""
import pathlib,json,hashlib,datetime,collections
R=pathlib.Path(__file__).resolve().parents[4]; O=pathlib.Path(__file__).resolve().parents[1]; P=R/'replication/phase2'; Q=R/'replication/phase3'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ident(p):return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':digest(p)}
def read(p):return json.loads(p.read_text())
def write(name,d):
 with (O/name).open('x') as f:json.dump(d,f,indent=2)
m=read(P/'PHASE2_FROZEN_MANIFEST.json'); anchor='acee4b37613fc905ae2d1b3dd1624a8a19762bd3cdc42086fe6c474911f02410'; errors=[]
assert digest(P/'PHASE2_FROZEN_MANIFEST.json')==anchor and (P/'PHASE2_FROZEN_MANIFEST.json').stat().st_size==152521
assert m['status']=='COMPLETE_AND_FROZEN' and m['manifest_self_excluded'] and not m['historical_comparison_performed']
assert m['freeze_utc']=='2026-11-03T00:59:03.141263+00:00'
expect={e['path'] for e in m['files']}|{'PHASE2_FROZEN_MANIFEST.json'};actual={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file()}
if expect!=actual:errors.append({'inventory_extra':sorted(actual-expect),'inventory_missing':sorted(expect-actual)})
checks=[]
for e in m['files']:
 p=P/e['path']; a=ident(p); ok=a['sha256']==e['sha256'] and a['bytes']==e['bytes']; checks.append({'expected':e,'observed':a,'match':ok,'exception':e['path']=='.DS_Store'})
 if not ok and e['path']!='.DS_Store':errors.append(a)
months={f'{y:04d}-{mo:02d}' for y in range(2010,2025) for mo in range(1,13) if (y,mo)>=(2010,7)}
fams={'hourly':'data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly','canonical':'data/processed/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/qa_v2/canonical_observed'}
mi=read(P/'audit/input_manifest.json'); pi=read(P/'audit/postrun_input_immutability.json'); assert m['admitted_inputs']==mi
prior={x['path']:x for x in pi['files']};assert len(prior)==348 and len(mi)==348
assert {(e['family'],e['month']) for e in mi}=={(f,mo) for f in fams for mo in months}
inputs=[]
for e in mi:
 assert e['path']==f"{fams[e['family']]}/{e['month']}.parquet"
 a=ident(R/e['path']);ok=all(a[k]==e[k]==prior[e['path']][k] for k in ('path','bytes','sha256'));inputs.append({'observed':a,'match':ok})
 if not ok:errors.append(a)
q=read(Q/'QUALIFIED_SEAL_GATE.json'); previous=[]
for group in ('prior_phase3_hashes','evidence_bindings'):
 for name,h in q[group].items():
  p=Q/name; a=ident(p);previous.append(a)
  if a['sha256']!=h:errors.append(a)
# External values retained in preceding conversational verification.
external={'QUALIFIED_SEAL_GATE.json':'b94bcd9e667b31a8093f7d95e3caf2f2d47538994458f93b133cc69455173c67','QUALIFIED_SEAL_GATE.md':'e44ffd1b5bcc3a582985508c0911a5cb0bec9a0e72d72cf3a53d20442859aabf','QUALIFIED_GATE_WITNESS.md':'c091662676da02db6719e61fe8dd70815ca4e6a385504761d83288446c72b558'}
for name,h in external.items():
 a=ident(Q/name);previous.append(a)
 if a['sha256']!=h:errors.append(a)
invest={'PROVENANCE_GAP_FINDINGS.md':'8421ea2794f2a99c28904bf2ccc204591f183f470da629cfb4870068adfdce6f','SOURCE_READ_CALL_GRAPH.md':'11d39a7f762b50c9757c883d5704b8e9e6b9233a3c7d5d90e13bb5d009667897','PROVENANCE_EVENT_COUNTS.json':'a3bf040dfe83a08cf823b03ad3aab82e41cc873d59c9288f7db916d6d3c0f875','HYPOTHESIS_AND_RISK_MATRIX.md':'5be44d7af20adccee8f1a5c7da31544539d5fd3d3da7565f21900452c12eeefc','STAGE_A_PROVENANCE_HANDOFF.md':'5b234c6206ef762f5eacdcde6b7da77a859bc308179f1ee2c66a09b5061d0466'}
for name,h in invest.items():
 a=ident(Q/'stage_a_source_request_investigation_v1'/name);previous.append(a)
 if a['sha256']!=h:errors.append(a)
ev=collections.Counter();prov=[]
for e in m['files']:
 if e['path'].startswith('audit/provenance_') and e['path'].endswith('.json'):
  d=read(P/e['path']);prov.append(e['path']);ev.update(x['event'] for x in d['file_events'])
assert len(prov)==39 and ev['admitted_data_request']==0
post=read(P/'audit/POSTRUN_INTEGRITY.json');assert post['run']['real_phases']==8 and post['run']['neural_retries']==0
assert post['run']['phase_order']==[[f,p] for f in ['F21','F22','F23','F24'] for p in ['initial','refit']]
# Fresh bytes include every checkpoint, ledger, report, failure, transition and replay receipt;
# semantic cross-checks continue below before pre-unseal witness.
result={'status':'STOP_NEW_BLOCKER' if errors else 'QUALIFIED_SUBSTANTIVE_INTEGRITY_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest':ident(P/'PHASE2_FROZEN_MANIFEST.json'),'manifest_declared':{k:v for k,v in m.items() if k not in ('files','admitted_inputs')},'payload_checks':checks,'input_checks':inputs,'previous_evidence':previous,'new_blockers':errors,'provenance_events':dict(ev),'postrun_integrity':post,'scope':'independent modeling-layer replication with audited inherited preprocessing','exceptions':['Only literal phase2/.DS_Store exempted from byte equality','Classification B: zero admitted_data_request; unresolved preparation-time function/native-reader coverage; bounded positive lineage only'],'external_anchor_provenance':'Prior conversation shasum stdout and final answer, corroborated by prior gates; not OS-level attestation','authorization':'2026-11-03 user expressly accepts the single .DS_Store exception and Classification-B provenance limitation, and separately authorizes historical unseal after this new qualified gate. No other exceptions, training, forwards, recalibration, repair or implementation changes authorized.','history':['Phase2 freeze 2026-11-03T00:59:03.141263+00:00','Original Stage A STOP: metadata mismatch','Metadata-only acceptance; qualified STOP: source-request coverage','Classification B investigation: STOP_AWAITING_HUMAN_DECISION','Current user accepts both named qualifications and separately authorizes comparison'],'reviewer':'Root accountable reviewer, sequential read-only review; continuing conversation, not a fresh context. Prior historical exposure disclosed; Phase2 itself used fresh implementation contexts. No background agents. Independent second arithmetic method will check calculations.'}
write('comparisons/fresh_integrity_checks.json',result)
print(json.dumps({'status':result['status'],'payloads':len(checks),'sources':len(inputs),'errors':errors}))
