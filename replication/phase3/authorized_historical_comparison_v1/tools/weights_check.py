import sys,pathlib,json,hashlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]/'.venv/lib/python3.14/site-packages'));sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from review_io import R,O,P,A,record,js
import numpy as np,pandas as pd,torch
rows=[];initial=[]
for year in range(2021,2025):
 f=f'F{year%100}';res=js(A/f/'result.json');old=torch.load(record(A/f/'restricted_final.pt','Safe weights-only comparison, no model instantiation/forward'),weights_only=True,map_location='cpu');new=torch.load(P/f'artifacts/run/{f}/refit/final_state.pt',weights_only=True,map_location='cpu')
 h=hashlib.sha256()
 for k,v in old.items():h.update(k.encode());h.update(v.numpy().tobytes())
 assert h.hexdigest()==res['frozen_parameter_sha256']
 assert sum(v.numel() for v in old.values())==6572==sum(v.numel() for v in new.values())
 for k,v in old.items():
  nk=k.replace('head.','main.');x=v.numpy().ravel().astype(float);y=new[nk].numpy().ravel().astype(float);d=abs(x-y);rows.append({'fold':f,'original_parameter':k,'independent_parameter':nk,'n':len(x),'max_abs_difference':float(d.max()),'mean_abs_difference':float(d.mean()),'p99_abs_difference':float(np.quantile(d,.99)),'equal':bool(np.array_equal(x,y))})
 for phase in ['initial','refit']:
  n=torch.load(P/f'artifacts/run/{f}/{phase}/initial_state.pt',weights_only=True,map_location='cpu');h=hashlib.sha256()
  for k,v in n.items():h.update(k.replace('main.','head.').encode());h.update(v.numpy().tobytes())
  initial.append({'fold':f,'phase':phase,'computed_original_tensor_digest':h.hexdigest(),'archival_initial_tensor_digest':res['initial_sha256'],'equal':h.hexdigest()==res['initial_sha256'],'serialization_comparison':False})
pd.DataFrame(rows).to_csv(O/'comparisons/checkpoint_parameter_differences.csv',index=False,float_format='%.17g');pd.DataFrame(initial).to_csv(O/'comparisons/initial_tensor_digest_checks.csv',index=False)
print('initial allmatched',all(x['equal'] for x in initial),'final max',max(x['max_abs_difference'] for x in rows))
