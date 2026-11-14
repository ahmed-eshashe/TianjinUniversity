from pathlib import Path
import sys,json,time,numpy as np
from scipy.integrate import quad_vec
W=Path(__file__).resolve().parent;R=W.parents[1]
from adaptive_contact import AdaptiveContact,query_mesh
sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from edge_contact import material_edges
old=W.parent/'disect_edge_contact_20261109_v26'
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation']
T=np.array(json.loads((old/'probe_placement.json').read_text())['loaded_component_hold_translation_m'])
vertices=np.array(d['vertices'])@rot.T+T;faces=np.array(d['triangles'])
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
rows=[]
for name in ['coarse','fine']:
 state=np.load(old/f'corrected_probe_{name}_final.npz');q=state['x'];v=state['v'];values=[]
 for atol,rtol in [(1e-10,1e-6),(1e-11,1e-7)]:
  c=AdaptiveContact(mesh,force_atol=atol,rtol=rtol)
  start=time.perf_counter();ev=c.evaluate(q,v,vertices,faces,np.zeros(3),T,kd=1.)
  values.append(ev)
  rows.append(dict(run=name,force_atol_N=atol,rtol=rtol,wall_s=time.perf_counter()-start,
                   force_norm_N=float(np.linalg.norm(ev['force'])),energy_J=ev['energy_J'],
                   inside_intervals=ev['inside_intervals'],subintervals=ev['accepted_subintervals'],
                   samples=len(ev['phi']),estimated_force_error_N=ev['estimated_force_error_N']))
 error=float(np.linalg.norm(values[0]['force']-values[1]['force'])/max(np.linalg.norm(values[1]['force']),1e-6))
 rows[-1]['refinement_relative']=error;assert error<=.05
 # Independent plane/least-squares triangle intersections, then SciPy's
 # Gauss-Kronrod rule instead of our Moller-Trumbore/Gauss 8/16 recursion.
 c=AdaptiveContact(mesh);reference_force=np.zeros_like(q)
 for edge_index,(i,j) in enumerate(c.edges):
  direction=q[j]-q[i]
  if not np.all((np.maximum(q[i],q[j])>=vertices.min(0))&(np.minimum(q[i],q[j])<=vertices.max(0))):continue
  hits=[0.,1.]
  for face in faces:
   a,b,cc=vertices[face];normal=np.cross(b-a,cc-a);den=normal@direction
   if abs(den)<1e-20:continue
   t=(normal@(a-q[i]))/den
   if not 0<t<1:continue
   uv=np.linalg.lstsq(np.column_stack((b-a,cc-a)),q[i]+t*direction-a,rcond=None)[0]
   if min(uv)>=-1e-12 and sum(uv)<=1+1e-12:hits.append(float(t))
  hits=np.unique(np.round(hits,14))
  for left,right in zip(hits[:-1],hits[1:]):
   mid=(left+right)/2
   if query_mesh(vertices,faces,(q[i]+mid*direction)[None])['phi'][0]>=0:continue
   def integrand(u):
    result=query_mesh(vertices,faces,(q[i]+u*direction)[None]);phi=result['phi'][0];n=result['normal'][0]
    vel=(1-u)*v[i]+u*v[j];vn=vel@n;tangent=vel-vn*n;speed=np.linalg.norm(tangent)
    elastic=2000*max(-phi,0)
    # mu=.5 eliminates the second Brown term exactly.
    friction=elastic*.5*np.tanh(4*speed/2500)
    force=(elastic+max(-vn,0))*n-friction*tangent/max(speed,1e-300)
    return np.r_[(1-u)*force,u*force]*c.edge_weights[edge_index]
   integral,error_est=quad_vec(integrand,left,right,epsabs=1e-11,epsrel=1e-7,limit=1000)
   reference_force[i]+=integral[:3];reference_force[j]+=integral[3:]
 err=float(np.max(abs(reference_force-values[0]['force'])))
 rows[-1]['independent_max_force_error_N']=err;assert err<1e-8
 # Virtual-work check at a real active material coordinate, zero velocity.
 active=int(np.argmax(np.linalg.norm(values[0]['force'],axis=1)))
 zero=np.zeros_like(q);elastic=c.evaluate(q,zero,vertices,faces,np.zeros(3),T)
 axis=int(np.argmax(abs(elastic['force'][active])));eps=1e-9
 qp=q.copy();qm=q.copy();qp[active,axis]+=eps;qm[active,axis]-=eps
 ep=c.evaluate(qp,zero,vertices,faces,np.zeros(3),T)['energy_J']
 em=c.evaluate(qm,zero,vertices,faces,np.zeros(3),T)['energy_J']
 grad_error=abs((ep-em)/(2*eps)+elastic['force'][active,axis])
 rows[-1]['real_state_energy_gradient_error_N']=float(grad_error);assert grad_error<1e-7
out=dict(scope='Adaptive contact integration controls at immutable saved coupled states; no new physical trajectory',rows=rows,passed=True,gate_a_complete=False)
(W/'controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
