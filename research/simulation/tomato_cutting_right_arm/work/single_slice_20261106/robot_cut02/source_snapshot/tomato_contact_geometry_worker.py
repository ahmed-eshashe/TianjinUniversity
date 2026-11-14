"""Native short-edge and parallel-edge work controls, isolated from solver motion."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Geometry controls stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp
  from tomato_mollified_self_contact import current_contact
  wp.init();wp.set_device('cuda:0')
  @wp.kernel(enable_backward=False)
  def query_segments(epsilon:float,result:wp.array[wp.vec3]):
   result[0]=wp.closest_point_edge_edge(wp.vec3(-.0005,0.,0.),wp.vec3(.0005,0.,0.),wp.vec3(0.,-.0005,.00005),wp.vec3(0.,.0005,.00005),epsilon)
  for label,eps in [('default_squared_length_threshold',1e-5),('resolved_short_edges',1e-16)]:
   result=wp.zeros(1,dtype=wp.vec3);wp.launch(query_segments,dim=1,inputs=[eps],outputs=[result]);value=result.numpy()[0];distance=float(value[2]);cases.append(dict(id=label,epsilon_m2=eps,closest_parameters=value[:2].tolist(),distance_m=distance,analytic_distance_m=.00005))
   if eps==1e-16 and abs(distance-.00005)>1e-10:raise ValueError('Short-edge crossing missed by corrected squared-length threshold')
   if eps==1e-5 and distance<=.0001:raise ValueError('Expected installed default short-edge limitation not reproduced')
  ids=wp.array([[i,i,i,i] for i in range(4)],dtype=wp.vec4i);weights=wp.array([[1.,0.,0.,0.]]*4,dtype=wp.vec4d);endpoints=wp.array([[0,1,2,3]],dtype=wp.vec4i);count=wp.ones(1,dtype=int);force=wp.zeros(4,dtype=wp.vec3d);h=wp.zeros(4,dtype=wp.mat33d);pf=wp.zeros(4,dtype=wp.vec3d);ph=wp.zeros(4,dtype=wp.mat33d);energy=wp.zeros(1,dtype=wp.float64);invalid=wp.zeros(1,dtype=int)
  def evaluate(pos,kind,threshold):
   for a in [force,h,pf,ph,energy,invalid]:a.zero_()
   wp.launch(current_contact,dim=1,inputs=[wp.array(pos,dtype=wp.vec3d),ids,weights,endpoints,wp.array([kind],dtype=int),wp.array([threshold],dtype=wp.float64),count,1,wp.float64(.0001),wp.float64(1000.)],outputs=[force,h,pf,ph,energy,invalid]);wp.synchronize()
   if int(invalid.numpy()[0]):raise ValueError('Invalid minimal contact fixture')
   return force.numpy().copy(),float(energy.numpy()[0])
  pos=np.array([[-.0005,0.,0.],[.0005,0.,0.],[-.0005,-.000005,.00005],[.0005,.000005,.00005]]);threshold=.001*np.sum((pos[1]-pos[0])**2)*np.sum((pos[3]-pos[2])**2);f,e=evaluate(pos,1,threshold);numeric=np.zeros_like(pos);step=1e-9
  for i in range(4):
   for j in range(3):
    a=pos.copy();b=pos.copy();a[i,j]+=step;b[i,j]-=step;numeric[i,j]=-(evaluate(a,1,threshold)[1]-evaluate(b,1,threshold)[1])/(2*step)
  error=float(abs(f-numeric).max());scale=float(abs(f).max());balance=float(np.linalg.norm(f.sum(0)));moment=float(np.linalg.norm(np.cross(pos,f).sum(0)));cases.append(dict(id='parallel_edge_mollifier_gradient',force_reference_error_n=error,maximum_force_n=scale,net_force_n=balance,net_moment_nm=moment,energy_j=e))
  if error>1e-7+1e-4*scale or balance>1e-9 or moment>1e-10:raise ValueError('Parallel mollifier derivative/work control failed')
  pos=np.array([[.0002,.0002,.00005],[0.,0.,0.],[.001,0.,0.],[0.,.001,0.]]);f,e=evaluate(pos,0,0.);shifted=pos.copy();shifted[0,0]+=.0001;f1,e1=evaluate(shifted,0,0.);cases.append(dict(id='flat_face_frictionless_slide',tangential_force_n=float(np.linalg.norm(f[0,:2])),potential_change_j=e1-e,normal_force_n=float(f[0,2])))
  if np.linalg.norm(f[0,:2])>1e-12 or abs(e1-e)>1e-15 or f[0,2]<=0:raise ValueError('Spurious flat-face sliding force')
  files=[Path(__file__),ROOT/'rl/tomato_mollified_self_contact.py'];write(out,'contact_geometry_measurements.json',dict(cases=cases,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},scope='Minimal geometric/work operator controls. No claim of contact manifold invariance, collision-free dynamics or full-fruit convergence.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,contact_geometry_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
