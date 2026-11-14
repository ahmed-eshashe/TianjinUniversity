from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from blade_geometry import CAD
from independent_cad_query import query_mesh
from sharp_front import blade_edge
old=Aggregate(Body.restore(W/'runs/continue_paid_r2/last_accepted.npz'));new=Aggregate(Body.restore(W/'runs/continue_paid_r2/pending_candidate.npz'));s0,s1=Surface(old),Surface(new)
# Parent boundaries enclosing the cube are exterior. All other exposed facets
# should be paired crack surfaces; independently count their normals and areas.
summary=[]
for a,s in [(old,s0),(new,s1)]:
 cube_face=np.any(np.all(np.isclose(abs(s.triangles),.003,atol=1e-13,rtol=0),axis=1),axis=1);interior=~cube_face;groups={}
 for i in np.flatnonzero(interior):
  normal=s.ref_normals[i];normal*=np.sign(normal[np.argmax(abs(normal))]);key=str(np.round(normal,6).tolist());groups[key]=groups.get(key,0)+float(s.tri_area[i])/2
 summary.append(dict(total=s.tri_area.sum(),outside=s.tri_area[cube_face].sum(),inside_half=s.tri_area[interior].sum()/2,normal_groups=groups,triangles=int(interior.sum())))
cad=CAD();ang=np.pi/6;R=np.array([[1.,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])@cad.R;edge0=blade_edge(cad,np.zeros(3),R);T0=np.array([.00013,.00304+.003*abs((edge0[1,1]-edge0[0,1])/(edge0[1,2]-edge0[0,2])),0.])-edge0.mean(0);t=.003875;T=T0+np.array([0,-.0012,0])*.5*(1-np.cos(np.pi*t/.03));positions=s1.positions(new.q).reshape(-1,3,3);points=positions[interior].reshape(-1,3);query=query_mesh(cad.vertices,cad.faces,(points-T)@R);out=dict(geometry=summary,exterior_change_m2=summary[1]['outside']-summary[0]['outside'],crack_inside_CAD_vertex_phi_min_m=float(query['phi'].min()),crack_inside_CAD_vertex_phi_max_m=float(query['phi'].max()));print(json.dumps(out,indent=2));(W/'reports/new_area_audit.json').write_text(json.dumps(out,indent=2))
