from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_fracture_20261109_v23';sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'));sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'))
from full_surface import FullSurface
from blade_contact import CADBlade
s=FullSurface();cad=CADBlade();q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];a=json.loads((V/'edge_alignment_diagnostic.json').read_text());p0=np.array(a['target_top_interface_midpoint_m']);pairs=s.mesh['ties'];copy=dict(pairs);mid=q.copy()
for l,r in pairs:mid[l]=.5*(q[l]+q[r])
segments=[]
for tri in np.unique(s.quad['faces'],axis=0):
 cross=[]
 for i,j in [(0,1),(1,2),(2,0)]:
  p=mid[tri[i]];r=mid[tri[j]];z=p0[2]
  if abs(p[2]-z)<1e-12:cross.append(p)
  if (p[2]-z)*(r[2]-z)<0:cross.append(p+(z-p[2])/(r[2]-p[2])*(r-p))
 if cross:
  cross=np.unique(np.round(cross,13),axis=0)
  if len(cross)==2:segments.append(cross)
path=[]
for depth in np.linspace(0,.008,33):
 y=p0[1]-depth;xs=[]
 for p,r in segments:
  if abs(p[1]-y)<1e-10:xs.append(p[0])
  if (p[1]-y)*(r[1]-y)<0:xs.append(p[0]+(y-p[1])/(r[1]-p[1])*(r[0]-p[0]))
 if not xs:
  if depth==0:xs=[p0[0]]
  else:raise RuntimeError('No prepared interface intersection at cut front')
 if np.ptp(xs)>1e-5:raise RuntimeError('Ambiguous front plane')
 path.append([float(depth),float(np.mean(xs)-p0[0])])
T=np.array(a['edge_aligned_translation_m']);ids=np.union1d(np.unique(s.mesh['outer']),np.unique(pairs));phi=cad.query(q[ids],T)['phi'];assert phi.min()>0
old=json.loads((V/'shallow_plan.json').read_text());old.update(scope='One diagnosed geometry correction: center the actual cutting edge on the prepared interface and follow its settled cross-section; original law, CAD orientation and force limits unchanged',selected={'translation_m':T.tolist(),'minimum_interface_clearance_m':float(phi.min())},downward_stroke_m=.008,durations_s=[.16,.08,.02],total_s=.26,wall_cap_s=7200,front_lateral_path_m=path,reason='v23 loading: both banks pushed in the same direction, opening only0.0063mm versus1mm onset; actual edge was laterally off by0.494mm. Exact CAD width1.238mm at2mm and2.526mm at8mm motivates a bounded8mm partial stroke; no imposed opening/damage and no guarantee of initiation. Preserve the same peak downward speed as the original2mm/40ms stroke.',launch_requires='v23 attempt finished and reviewed; Gate A controls pass');(W/'correction_plan.json').write_text(json.dumps(old,indent=2));print(json.dumps({'initial':T.tolist(),'front_path':path,'minimum_clearance_m':float(phi.min()),'scope':old['scope']},indent=2))
