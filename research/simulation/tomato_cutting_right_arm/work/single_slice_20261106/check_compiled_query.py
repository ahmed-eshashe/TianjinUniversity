from pathlib import Path
import sys,json,time,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
from tomato_host_blade_geometry import query_mesh as original
from tomato_compiled_blade_query import query_mesh as compiled
b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());v=np.asarray(b['vertices']);faces=np.asarray(b['triangles']);rng=np.random.default_rng(654)
p=np.concatenate([rng.uniform(v.min(0)-.01,v.max(0)+.01,(2000,3)),v[faces].mean(1)+rng.normal(0,1e-7,(len(faces),3))])
compiled(v,faces,p[:2]);t=time.monotonic();a=original(v,faces,p);old=time.monotonic()-t;t=time.monotonic();c=compiled(v,faces,p);new=time.monotonic()-t
error={key:float(np.max(np.abs(a[key]-c[key]))) for key in ['phi','normal','closest','winding']}
# Normals at exact vertices are zero; tied nearest faces need not share an ID.
assert error['phi']<1e-12 and error['closest']<1e-10 and error['normal']<1e-6
out=dict(passed=True,points=len(p),errors=error,original_s=old,compiled_s=new)
(w/'compiled_query_check.json').write_text(json.dumps(out,indent=2));print(out)
