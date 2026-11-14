from pathlib import Path
import json,sys,time,numpy as np
from scipy.interpolate import PchipInterpolator
from distributed_contact import DistributedContact
W=Path(__file__).resolve().parent;R=W.parents[1]
sys.path.insert(0,str(R/'rl'))
from tomato_compiled_blade_query import query_mesh

def cube_query(p):
    # Independent analytic signed-distance gradient for a 2 mm cube.
    half=.001;d=np.abs(p)-half;outside=np.maximum(d,0)
    norm=np.linalg.norm(outside,axis=1)
    phi=norm+np.minimum(np.max(d,axis=1),0)
    normal=np.zeros_like(p);out=norm>1e-20
    normal[out]=outside[out]*np.sign(p[out])/norm[out,None]
    ids=np.flatnonzero(~out);axis=np.argmax(d[ids],axis=1)
    normal[ids,axis]=np.sign(p[ids,axis])
    return dict(phi=phi,normal=normal)

def single_edge(order):
    x=DistributedContact.__new__(DistributedContact)
    x.edges=np.array([[0,1]]);x.node_count=2;x.cut=np.array([1]);x.outer=np.array([],int)
    u,w=np.polynomial.legendre.leggauss(order)
    x.coordinates=(u+1)/2;x.gauss_weights=w/2;x.edge_weights=np.ones(1)
    return x

c=single_edge(128);q=np.array([[-.002,.00013,.00021],[.002,.00013,.00021]])
zero=np.zeros_like(q);args=(zero,cube_query,np.zeros(3),np.zeros(3))
a=c.evaluate(q,*args,kd=0)
gradient=np.zeros_like(q);h=1e-9
for i in range(2):
 for j in range(3):
  qp=q.copy();qm=q.copy();qp[i,j]+=h;qm[i,j]-=h
  gradient[i,j]=(c.evaluate(qp,*args,kd=0)['energy_J']-c.evaluate(qm,*args,kd=0)['energy_J'])/(2*h)
error=float(np.max(abs(gradient+a['force'])));assert error<1e-7
assert a['active_samples']>0
assert np.linalg.norm(a['reaction']+a['force'].sum(0))<1e-12
assert np.linalg.norm(a['moment']+np.cross(q,a['force']).sum(0))<1e-12
# Same grazing geometry that rejected the entry-plane candidate, in millimetres.
continuity=[]
for eps in [1e-6,1e-8,1e-10,1e-12]:
 es=[]
 for sign in [-1,1]:
  qp=np.array([[-.002,0,.0002],[0,.002+sign*eps,.0002]])
  es.append(c.evaluate(qp,zero,cube_query,np.zeros(3),np.zeros(3),kd=0)['energy_J'])
 continuity.append(dict(epsilon_m=eps,energy_J=es,jump_J=abs(es[1]-es[0])))
assert continuity[-1]['jump_J']<1e-12
# Normal damping/Brown friction must dissipate work relative to the blade.
velocity=np.array([[.03,-.01,.02],[-.02,.04,-.01]])
full=c.evaluate(q,velocity,cube_query,np.zeros(3),np.zeros(3))
elastic=c.evaluate(q,zero,cube_query,np.zeros(3),np.zeros(3),kd=0)
dissipative_power=float(np.sum((full['force']-elastic['force'])*velocity))
assert dissipative_power<=1e-12

old=W.parent/'disect_shallow_20261109_v25';p=json.loads((old/'correction_plan.json').read_text())
u=.04/p['durations_s'][0];depth=p['downward_stroke_m']*(10*u**3-15*u**4+6*u**5)
curve=PchipInterpolator(*np.array(p['front_lateral_path_m']).T)
T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0]
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
vertices=np.array(d['vertices'])@rot.T+T;faces=np.array(d['triangles'])
lo,hi=vertices.min(0),vertices.max(0)
def query(points):
 keep=np.all((points>=lo)&(points<=hi),axis=1)
 phi=np.ones(len(points));normal=np.zeros_like(points)
 if keep.any():
  result=query_mesh(vertices,faces,points[keep]);phi[keep]=result['phi'];normal[keep]=result['normal']
 return dict(phi=phi,normal=normal)
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
audit=json.loads((old/'edge_crossing_verification.json').read_text())
rows=[];last=None
for order in [64,128,256,512]:
 contact=DistributedContact(mesh,order)
 state=np.load(old/'coarse0040_final.npz');q=state['x'];v=state['v']
 start=time.perf_counter();r=contact.evaluate(q,v,query,np.zeros(3),T)
 detected=[]
 for row in audit['rows']:
  if row['run']!='coarse0040':continue
  e=np.flatnonzero(np.all(contact.edges==[row['interior_node'],row['cut_node']],axis=1))
  detected.append(bool(len(e) and np.any(r['phi'][e]<0)))
 current=dict(order=order,wall_s=time.perf_counter()-start,energy_J=r['energy_J'],
              active_samples=r['active_samples'],force_norm_N=float(np.linalg.norm(r['force'])),
              saved_crossings_with_interior_samples=sum(detected),total_saved_crossings=len(detected))
 if last is not None:
  current['force_refinement_relative']=float(np.linalg.norm(r['force']-last['force'])/max(np.linalg.norm(r['force']),1e-6))
  current['energy_refinement_relative']=abs(r['energy_J']-last['energy_J'])/max(r['energy_J'],1e-12)
 rows.append(current);last=r
out=dict(scope='Conservative distributed candidate controls; no coupled run or engine adoption',
 fixed_embedding_energy_gradient_error_N=error,grazing_feature_continuity=continuity,
 dissipative_relative_power_W=dissipative_power,saved_state_quadrature=rows,
 conservative_controls_passed=True,quadrature_refinement_passed=bool(rows[-1]['force_refinement_relative']<=.05 and rows[-1]['energy_refinement_relative']<=.05),
 gate_a_complete=False,coupled_contact_qualification_pending=True)
(W/'distributed_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
