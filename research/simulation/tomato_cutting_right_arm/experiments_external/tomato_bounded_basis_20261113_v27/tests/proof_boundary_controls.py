from pathlib import Path
import sys,os,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from blade_geometry import CAD,certify
from convex_guard import ConvexGuard
from convex_guard_gpu import GPUConvexGuard
cad=CAD();cpu=ConvexGuard(cad);gpu=GPUConvexGuard(cad);rng=np.random.default_rng(813);cases=[]
# Move small, positive-volume tetrahedra through original faces. Include
# acceptable shallow contact, the limit, deeper contact, outside and slivers.
faces=rng.choice(len(cad.faces),size=12,replace=False)
for face in faces:
 tri=cad.vertices[cad.faces[face]];center=tri.mean(0);n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n)
 for depth in [-.0002,.00005,.000095,.00011,.0004]:
  p=center-depth*n;size=1e-6;tet=p+size*np.array([[1,0,0],[0,1,0],[0,0,1],[-1,-1,-1]])
  for shape in ['regular','thin']:
   t=tet.copy()
   if shape=='thin':t[:,2]=p[2]+(t[:,2]-p[2])*1e-10
   old=certify(t[None],cad,np.zeros(3),np.eye(3),maxdepth=28);c=cpu.certify(t[None],np.zeros(3),np.eye(3),maxdepth=28);g=gpu.certify(t[None],np.zeros(3),np.eye(3),maxdepth=28)
   cases.append(dict(face=int(face),depth=depth,shape=shape,reference=old['passed'],cpu=c['passed'],gpu=g['passed'],gpu_fallback=g['fallback_tets'],observed_m=old.get('observed_m'),agree=old['passed']==c['passed']==g['passed']))
# Swept-motion allowance must prevent a static pass from authorizing too long
# an unchecked movement. More motion may not change a reject into a pass.
tet=np.array([[0,0,0],[1e-5,0,0],[0,1e-5,0],[0,0,1e-5]])+cad.vertices.mean(0)+[0,.1,0]
normal=gpu.certify(tet[None],np.zeros(3),np.eye(3));large=gpu.certify(tet[None],np.zeros(3),np.eye(3),motion=.000101)
checks=dict(all_cases=all(c['agree'] for c in cases),has_pass=any(c['gpu'] for c in cases),has_reject=any(not c['gpu'] for c in cases),sliver_fallback=any(c['shape']=='thin' and c['gpu_fallback'] for c in cases),motion_budget=normal['passed'] and not large['passed']);out=dict(passed=all(checks.values()),checks=checks,cases=cases);(W/'reports/proof_boundary_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(passed=out['passed'],checks=checks,cases=len(cases)),indent=2));assert out['passed']
