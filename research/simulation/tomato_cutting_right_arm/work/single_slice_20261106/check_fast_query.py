from pathlib import Path
import sys,json,numpy as np,time
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_exact_blade_queries import query
from tomato_fast_exact_cad import fast_query
wp.init();wp.set_device('cuda:0');b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());v=np.array(b['vertices']);f=np.array(b['triangles']);rng=np.random.default_rng(322);face_points=np.einsum('ni,nij->nj',rng.dirichlet([1,1,1],20000),v[f[rng.integers(0,len(f),20000)]])+rng.normal(0,1e-9,(20000,3));p=np.concatenate([rng.uniform(v.min(0)-.01,v.max(0)+.01,(30000,3)),face_points]);n=len(p)
inputs=[wp.array(v,dtype=wp.vec3d),wp.array(f,dtype=wp.vec3i),wp.array(p,dtype=wp.vec3d)]
def run(kernel):
 output=[wp.empty(n,dtype=wp.float64),wp.zeros(n,dtype=wp.vec3d),wp.empty(n,dtype=wp.vec3d),wp.empty(n,dtype=int),wp.empty(n,dtype=wp.float64)]
 wp.launch(kernel,dim=n,inputs=inputs,outputs=output);wp.synchronize();start=time.monotonic();wp.launch(kernel,dim=n,inputs=inputs,outputs=output);wp.synchronize();duration=time.monotonic()-start
 return [a.numpy() for a in output],duration
old,ot=run(query);new,nt=run(fast_query);errors={name:float(np.max(abs(old[i]-new[i]))) for i,name in [(0,'distance'),(1,'normal'),(2,'closest')]};sign_diff=int(np.sum(np.sign(old[0])!=np.sign(new[0])));assert sign_diff==0 and errors['distance']<1e-12 and errors['normal']<1e-6 and errors['closest']<1e-12
result=dict(passed=True,points=n,errors=errors,sign_differences=sign_diff,original_s=ot,fast_s=nt);(w/'fast_query_check.json').write_text(json.dumps(result,indent=2));print(result)
