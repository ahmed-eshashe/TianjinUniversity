"""Actual Newton contact activates the implicit cohesive coupon; outside control freezes history."""
import argparse,signal,traceback,math
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;cases=[]
 def stop(*args):raise InterruptedError('Material/contact diagnostic stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 def result():return dict(shutdown_requested=app is not None,diagnostic_passed=passed,material_contact_passed=passed,newton_steps=steps,controlled_steps=steps,material_contact_cases=len(cases),material_calibrated=False)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import warp as wp
  import newton
  import newton.solvers
  from tomato_native_cohesive_operator import CohesiveVBD
  from tomato_half_step_reaction import collect_reaction
  wp.init();wp.set_device('cuda:0')
  for connected in (True,False):
   builder=newton.ModelBuilder(gravity=(0.,0.,0.));builder.add_particle(wp.vec3(-.02,0.,0.),wp.vec3(0.),0.,radius=0.);builder.add_particle(wp.vec3(.0025,0.,0.),wp.vec3(0.),.001,radius=0.)
   body=builder.add_body(xform=wp.transform(wp.vec3(-.002 if connected else -.005,0.,0.),wp.quat_identity()),mass=.02,inertia=wp.mat33(.0001,0.,0.,0.,.0001,0.,0.,0.,.0001),is_kinematic=True)
   builder.add_shape_box(body,hx=.005,hy=.005,hz=.005,cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.))
   builder.color();builder.set_coloring([[0],[1]]);model=builder.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
   solver=CohesiveVBD(model,iterations=24,rigid_compliant_alm=True,integrate_with_external_rigid_solver=True,rigid_avbd_beta=0.)
   history=wp.zeros(1,dtype=wp.vec2);eligible=wp.zeros(1,dtype=int);rest=wp.array([[.021,0.,0.]],dtype=wp.vec3)
   solver.configure_cohesion(wp.array([[0,1]],dtype=wp.vec2i),rest,wp.array([[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]],dtype=wp.mat33),wp.array([[100.,.001,.004]],dtype=wp.vec3),history,eligible)
   sin=model.state();sout=model.state();pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=8,rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True);contacts=pipeline.contacts()
   pipeline.collide(sin,contacts);wp.synchronize();count=int(contacts.soft_contact_count.numpy()[0])
   if count!=int(connected):raise ValueError('Native eligibility control mismatch')
   eligible.assign(wp.array([int(count>0)],dtype=int))
   pos=sin.particle_q.numpy().tolist();refx=pos[0][0]+rest.numpy().tolist()[0][0];q0=pos[1][0]-refx;mp=float(model.particle_mass.numpy()[1]);masscoeff=mp/DT**2
   surface=float(sin.body_q.numpy()[0][0])+float(model.shape_scale.numpy()[0][0])
   if connected:expected=(masscoeff*q0+1750*(surface-refx)-100*.001*.004/.003)/(masscoeff+1750-100*.001/.003)
   else:expected=masscoeff*q0/(masscoeff+100)
   solver.step(sin,sout,None,contacts,DT);wp.synchronize();steps+=1
   actual=sout.particle_q.numpy().tolist()[1][0]-refx
   if abs(actual-expected)>1e-7 or history.numpy().tolist()!=[[0.,0.]]:raise ValueError('Contact-driven trial response mismatch')
   reaction=collect_reaction(model,sout,sin,contacts,solver) if count else None
   if connected:
    force=reaction['force'][0];expected_force=1750*(surface-refx-expected)
    if abs(force[0]-expected_force)>2e-5 or force[0]<=0.:raise ValueError('Contact/reaction mismatch')
   solver.commit_cohesion(sout);wp.synchronize();state=history.numpy().tolist()[0]
   if connected and not 0<state[1]<1.:raise ValueError('Actual contact did not activate damage')
   if not connected and state!=[0.,0.]:raise ValueError('No-contact control evolved damage')
   cases.append(dict(id='native_contact' if connected else 'outside_control',contact_count=count,expected_gap_m=expected,actual_gap_m=actual,position_error_m=abs(actual-expected),committed_history=state,native_reaction=reaction,eligibility_from_generated_contact=True,proxy_is_analytic_box=True))
  if steps!=2 or len(cases)!=2:raise ValueError('Unexpected material/contact counts')
  write(out,'material_contact_measurements.json',dict(cases=cases,newton_steps=steps,scope='One-pair fixed-frame coupon with actual analytic-box contact; not a real blade or whole tomato.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',result())
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
