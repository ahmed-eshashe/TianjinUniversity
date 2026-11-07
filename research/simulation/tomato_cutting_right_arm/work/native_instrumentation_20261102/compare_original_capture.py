from pathlib import Path
import json,numpy as np,hashlib
w=Path(__file__).resolve().parent;r=w.parents[1];old=r/'runs/native/motor_effort_capture_20261102_01';new=w/'capture_off01';fields={};count=0
for a in sorted(old.glob('interval_*.npz')):
 b=new/a.name
 if not b.exists():raise ValueError('Missing interval '+str(b))
 with np.load(a) as x,np.load(b) as y:
  if set(x.files)!=set(y.files):raise ValueError('Schema differs')
  for k in x.files:
   v=fields.setdefault(k,{'identical':True,'max_absolute_difference':0.0})
   v['identical'] &= bool(np.array_equal(x[k],y[k]));v['max_absolute_difference']=max(v['max_absolute_difference'],float(np.max(np.abs(x[k].astype(float)-y[k].astype(float)))))
 count+=1
out={'intervals':count,'original':str(old),'rebuilt_trace_off':str(new),'fields':fields,'all_arrays_identical':all(v['identical'] for v in fields.values()),'qualification':False,'limitation':'Saved-data comparison only; rebuilt run crashed during shutdown, trace-on has not run. No observer-equivalence or motor-work pass.'}
(w/'original_backend_comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
