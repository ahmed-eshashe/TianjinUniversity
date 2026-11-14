from pathlib import Path
import json,sys,numpy as np
from scipy.interpolate import PchipInterpolator
from edge_contact import evaluate,material_edges

W=Path(__file__).resolve().parent
R=W.parents[1]
v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
            [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
            [3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
rows=[]
for sign in [-1,1]:
 for end in [0.,.5,1.5,2.5]:
  q=np.array([[sign*2.,.13,.21],[sign*end,.13,.21]])
  e=np.array([[0,1]])
  args=(q,np.zeros_like(q),e,v,f,np.zeros(3),np.zeros(3))
  a=evaluate(*args,kd=0);b=evaluate(*args,kd=0,reference=True)
  error=float(np.max(abs(a['force']-b['force'])))
  assert error < 1e-9
  expected = end < 1
  # An endpoint beyond the opposite face remains behind its entry plane.
  if end==0: assert a['active_nodes']==1
  if end>2: assert a['active_nodes']==0
  grad=np.zeros_like(q);h=1e-6
  for i in range(len(q)):
   for j in range(3):
    qp=q.copy();qm=q.copy();qp[i,j]+=h;qm[i,j]-=h
    grad[i,j]=(evaluate(qp,*args[1:],kd=0)['energy_J']-evaluate(qm,*args[1:],kd=0)['energy_J'])/(2*h)
  gradient_error=float(np.max(abs(a['force']+grad)))
  assert gradient_error < 1e-5
  dup=evaluate(q,np.zeros_like(q),np.repeat(e,4,axis=0),v,f,np.zeros(3),np.zeros(3),kd=0)
  assert np.array_equal(a['force'],dup['force'])
  rows.append(dict(bank=sign,endpoint=end,CPU_force_error_N=error,energy_gradient_error_N=gradient_error))
# Entirely outside endpoints with a segment passing through the blade.
q=np.array([[-2.,.13,.21],[2.,.13,.21]])
a=evaluate(q,np.zeros_like(q),np.array([[0,1]]),v,f,np.zeros(3),np.zeros(3),kd=0)
assert a['active_nodes']==1 and a['maximum_penetration_m']==3.
angle=.471;rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
shift=np.array([4.,2.,-1.])
b=evaluate(q@rot.T+shift,np.zeros_like(q),np.array([[0,1]]),v@rot.T+shift,f,np.zeros(3),shift,kd=0)
assert np.max(abs(b['force']-a['force']@rot.T)) < 1e-9
assert abs(b['energy_J']-a['energy_J']) < 1e-9
assert np.linalg.norm(a['reaction']+a['force'].sum(0)) < 1e-12
assert np.linalg.norm(a['moment']+np.cross(q,a['force']).sum(0)) < 1e-12
# Tangential entry-feature switch at a convex corner. A conservative contact
# energy must remain continuous. Endpoints stay away from the triangle plane.
feature=[]
for eps in [1e-3,1e-5,1e-7,1e-9]:
 es=[]
 for d in [-eps,eps]:
  q=np.array([[-2.,0.,.2],[0.,2.+d,.2]])
  es.append(evaluate(q,np.zeros_like(q),np.array([[0,1]]),v,f,np.zeros(3),np.zeros(3),kd=0)['energy_J'])
 feature.append(dict(epsilon_m=eps,energy_J=es,jump_J=abs(es[1]-es[0])))

# Exact saved CAD fixtures, reference uses plane/least-squares rather than ray MT.
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
rotation=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
old=W.parent/'disect_shallow_20261109_v25'
p=json.loads((old/'correction_plan.json').read_text());u=.04/p['durations_s'][0]
depth=p['downward_stroke_m']*(10*u**3-15*u**4+6*u**5)
curve=PchipInterpolator(*np.array(p['front_lateral_path_m']).T)
T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0]
vertices=np.array(d['vertices'])@rotation.T+T;faces=np.array(d['triangles'])
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');edges=material_edges(mesh)
audit=json.loads((old/'edge_crossing_verification.json').read_text());fixtures=[]
for name in ['coarse0040','fine0040']:
 state=np.load(old/f'{name}_final.npz');q=state['x'];vel=state['v']
 a=evaluate(q,vel,edges,vertices,faces,np.zeros(3),T)
 examples=[r for r in audit['rows'] if r['run']==name]
 test_edges=np.array([[r['interior_node'],r['cut_node']] for r in examples])
 b=evaluate(q,vel,test_edges,vertices,faces,np.zeros(3),T,reference=True)
 c=evaluate(q,vel,test_edges,vertices,faces,np.zeros(3),T)
 assert np.max(abs(b['force']-c['force'])) < 1e-9
 detected=[bool(a['gap'][r['cut_node']]<0) for r in examples]
 assert all(detected)
 fixtures.append(dict(run=name,missed_edges_detected=sum(detected),total_missed_edges=len(detected),
                      reference_force_error_N=float(np.max(abs(b['force']-c['force']))),
                      maximum_oriented_gap_m=a['maximum_penetration_m'],
                      active_nodes=a['active_nodes'],intersecting_edges=a['intersecting_edges']))
out=dict(scope='Separate experimental contact candidate; no coupled simulation or adoption',
         fixed_face_controls_passed=True,fixed_face_rows=rows,saved_crossing_fixtures=fixtures,
         feature_continuity=feature,feature_continuity_passed=feature[-1]['jump_J']<1e-6,
         gate_a_complete=False,coupled_runs_authorized_by_controls=False)
(W/'controls_result.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
