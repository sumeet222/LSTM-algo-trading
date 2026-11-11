import pathlib,json,hashlib,datetime
O=pathlib.Path(__file__).resolve().parents[1];R=O.parents[2];P=R/'replication/phase2';A=R/'reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28'
def record(p,purpose='Historical comparison'):
 p=pathlib.Path(p); reg=O/'comparisons/reference_reads.json';d=json.loads(reg.read_text()); key=str(p.relative_to(R))
 if not any(x['path']==key for x in d):
  b=p.read_bytes();d.append({'path':key,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'opened_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':purpose,'evidence_grade':'Direct archived object; meaning adjudicated in report'});reg.write_text(json.dumps(d,indent=2))
 return p
def js(p):return json.loads(record(p).read_text())
