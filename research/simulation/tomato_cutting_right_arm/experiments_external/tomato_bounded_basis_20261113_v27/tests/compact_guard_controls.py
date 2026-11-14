from pathlib import Path
import sys,os,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp')
from blade_geometry import CAD,certify
from convex_guard import ConvexGuard
from compact_proof import CompactProof
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from sharp_front import blade_edge
cad=CAD();guard=ConvexGuard(cad);ang=np.pi/6;R=np.array([[1.,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])@cad.R;edge0=blade_edge(cad,np.zeros(3),R);T0=np.array([.00013,.00304+.003*abs((edge0[1,1]-edge0[0,1])/(edge0[1,2]-edge0[0,2])),0.])-edge0.mean(0);rows=[]
for name,t in [('advance_6ms_checkpoint',.0092),('contact_limit_resolution',.0093)]:
 a=Aggregate(Body.restore(W/'runs'/name/'last_accepted.npz'));s=Surface(a);T=T0+np.array([0.,-.0012,0.])*.5*(1-np.cos(np.pi*t/.03));tets=s.tets(a.q);start=time.perf_counter();old=certify(tets,cad,T,R,maxdepth=28);oldwall=time.perf_counter()-start;new=guard.certify(tets,T,R,maxdepth=28);start=time.perf_counter();warm=guard.certify(tets,T,R,maxdepth=28);warmwall=time.perf_counter()-start;compact=CompactProof(a,s,guard);start=time.perf_counter();grouped=compact(a.q,T,R,maxdepth=28);groupwall=time.perf_counter()-start;row=dict(compact=grouped,compact_wall_s=groupwall,case=name,reference=old,candidate=new,warm=warm,reference_wall_s=oldwall,warm_wall_s=warmwall,agreement=old['passed']==new['passed']==warm['passed']==grouped['passed']);rows.append(row);print(json.dumps(row),flush=True)
# Known positive-volume material wholly inside a thick knife region must fail.
z=np.load(W/'assets/blade_partition.npz');cells=z['x'][z['tets']];centers=cells.mean(1);q=cad.query(centers,T=np.zeros(3),R=np.eye(3));i=int(np.argmin(q['phi']));center=centers[i];tiny=center+1e-4*(cells[i]-center);negative=guard.certify(tiny[None],np.zeros(3),np.eye(3));rows.append(dict(case='deep_penetration_negative_control',candidate=negative,agreement=not negative['passed']));out=dict(passed=all(r['agreement'] for r in rows),cases=rows,scope='Whole-material original-CAD penetration proof, unchanged 0.1 mm limit and 2 micrometre allowance. Convex-distance bound with legacy fallback; no physics or material change.');(W/'reports/compact_guard_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
