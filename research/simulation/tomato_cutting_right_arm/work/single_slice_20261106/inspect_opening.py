from pathlib import Path
import sys,json
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_native_full_model import registry
from tomato_objective_cohesion_reference import make_patch
from tomato_cut_geometry import current_footprints
from tomato_exact_blade_coverage import coverage
data=registry();f=sorted((w/'robot_cut02/material_states').glob('step_*.npz'))[-1]
z=np.load(f);x=z['x'];h=z['history'];pose=z['actual_tool_pose'];rows=[]
reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz')
solid=json.loads((r/'work/exact_blade_cells.json').read_text());mat=current_footprints(x,reg)
local=(mat.reshape(-1,3)-pose[:3])@Rotation.from_quat(pose[3:]).as_matrix()
c=coverage(solid['vertices'],solid['cells'],local,np.arange(len(local)).reshape(-1,3),capacity=131072)
overlap={int(reg['patch'][row['id']]) for row in c['triangles'] if row['covered_area_m2']>1e-16}
for i,p in enumerate(data['cohesion'].patches):
 ids=data['pairs'][p['indices']];law=p['law'];m=make_patch(data['x'][ids],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m))
 xx=x[ids];mid=xx.mean(1);a,b,cc=m['anchors'];u=mid[b]-mid[a];v=mid[cc]-mid[a];t=u/np.linalg.norm(u);n=m['sign']*np.cross(u,v)/np.linalg.norm(np.cross(u,v));q=np.column_stack([n,t,np.cross(n,t)])
 gap=(xx[:,1]-xx[:,0])@q;gap[:,0]=np.maximum(gap[:,0],0)
 energy=.5*np.sum(p['weights'][:,None]*gap*(gap@m['local_k']))
 rows.append(dict(patch=i,current_opening_mm=float(np.sqrt(2*energy/law.stiffness_n_m)*1000),history_opening_mm=float(h[i,0]*1000),damage=float(h[i,1]),current_overlap=i in overlap))
result=dict(frame=f.name,overlap_count=len(overlap),patches=rows)
(w/'robot_cut02/opening_inspection.json').write_text(json.dumps(result,indent=2))
print(json.dumps(dict(frame=f.name,overlap_count=len(overlap),largest=sorted(rows,key=lambda p:p['current_opening_mm'],reverse=True)[:10]),indent=2))
