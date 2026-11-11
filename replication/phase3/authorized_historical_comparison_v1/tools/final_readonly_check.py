"""Second integrity implementation: file_digest, literal inventories; no pipeline imports."""
from pathlib import Path
import hashlib,json,datetime,collections
O=Path(__file__).resolve().parents[1]; R=O.parents[2]; P=R/'replication/phase2'
def read(p): return json.loads(p.read_text())
def ident(p):
 with p.open('rb') as f: h=hashlib.file_digest(f,'sha256').hexdigest()
 return {'bytes':p.stat().st_size,'sha256':h}
def matches(p,e):
 a=ident(p); assert a['bytes']==e['bytes'] and a['sha256']==e['sha256'],str(p)
 return {'path':str(p.relative_to(R)),**a}
m=read(P/'PHASE2_FROZEN_MANIFEST.json'); anchor='acee4b37613fc905ae2d1b3dd1624a8a19762bd3cdc42086fe6c474911f02410'
assert ident(P/'PHASE2_FROZEN_MANIFEST.json')=={'bytes':152521,'sha256':anchor}
actual={str(p.relative_to(P)) for p in P.rglob('*') if p.is_file()}
assert actual=={e['path'] for e in m['files']}|{'PHASE2_FROZEN_MANIFEST.json'}
payload=[matches(P/e['path'],e) for e in m['files'] if e['path']!='.DS_Store']; assert len(payload)==232
mi=read(P/'audit/input_manifest.json'); post=read(P/'audit/postrun_input_immutability.json'); assert m['admitted_inputs']==mi
post={e['path']:e for e in post['files']}; assert len(mi)==len(post)==348
months={f'{y:04d}-{mo:02d}' for y in range(2010,2025) for mo in range(1,13) if (y,mo)>=(2010,7)}
fams={'hourly':'data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly','canonical':'data/processed/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/qa_v2/canonical_observed'}
assert {(e['family'],e['month']) for e in mi}=={(f,mo) for f in fams for mo in months}
inputs=[]
for e in mi:
 assert e['path']==f"{fams[e['family']]}/{e['month']}.parquet"
 assert all(e[k]==post[e['path']][k] for k in ['path','bytes','sha256'])
 inputs.append(matches(R/e['path'],e))
fresh=read(O/'comparisons/fresh_integrity_checks.json'); prior=[matches(R/e['path'],e) for e in fresh['previous_evidence']]
w=read(O/'PRE_UNSEAL_WITNESS.json'); gate=[matches(O/e['path'],e) for e in w['gate_files']]
assert ident(O/'PRE_UNSEAL_WITNESS.json')['sha256']=='8732172b8d382e4708ee2d8985169d2baa08d577377975ce20c9b4d559db1c3a'
refs=read(O/'comparisons/reference_reads.json'); original=[matches(R/e['path'],e) for e in refs]
assert min(e['opened_utc'] for e in refs)>w['utc']
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'QUALIFIED_SUBSTANTIVE_IDENTITIES_STILL_MATCH','algorithm':'Independent hashlib.file_digest implementation; fresh full bytes; exact literal inventory and month/family Cartesian product','manifest_anchor':anchor,'nonexempt_payloads':payload,'admitted_inputs':inputs,'prior_evidence':prior,'immutable_preunseal_gate':gate,'reference_files':original,'source_family_counts':dict(collections.Counter(e['family'] for e in mi)),'metadata_exception_current':ident(P/'.DS_Store'),'provenance_qualification':'Classification B remains; identity verification is not exhaustive runtime source-read proof','historical_read_after_witness':True,'mismatches':[]}
with (O/'comparisons/final_readonly_verification.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps({'status':result['status'],'payloads':len(payload),'inputs':len(inputs),'prior_evidence':len(prior),'references':len(original),'mismatches':0}))
