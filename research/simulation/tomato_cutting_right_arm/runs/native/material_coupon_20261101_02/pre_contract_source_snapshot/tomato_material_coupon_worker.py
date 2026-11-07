"""Native fixed-frame interface coupon: damage energy, release, closure contact and reset."""
import argparse,signal,traceback,hashlib,math
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;probes=0;records=[]
 def stop(*args):raise InterruptedError('Material coupon stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 def result():return dict(shutdown_requested=app is not None,diagnostic_passed=passed,coupon_checks_passed=passed,newton_steps=steps,controlled_steps=steps,opening_probes=probes,coupon_cases_completed=len(records),material_calibrated=False,robot_validated=False)
 try:
  write(out,'input_manifest.json',dict(source_sha256={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [Path(__file__),ROOT/'rl/tomato_native_cohesive_operator.py',ROOT/'rl/tomato_half_step_reaction.py',ROOT/'rl/tomato_bonds.py',ROOT/'rl/tomato_isaac_startup_guard.py']},scope='Prescribed fixed-frame one-pair interface opening, native implicit post-failure contact; not a volumetric tomato or real-blade cut.',newton_step_cap=4,opening_probe_cap=802))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import warp as wp
  import newton
  import newton.solvers
  from tomato_native_cohesive_operator import CohesiveVBD,cohesive_blocks
  from tomato_half_step_reaction import collect_reaction
  wp.init();wp.set_device('cuda:0')
  builder=newton.ModelBuilder(gravity=(0.,0.,0.));builder.add_particle(wp.vec3(-.02,0.,0.),wp.vec3(0.),0.,radius=0.);builder.add_particle(wp.vec3(.001,0.,0.),wp.vec3(0.),.001,radius=0.)
  builder.add_spring(0,1,0.,0.,0.)
  proxy=builder.add_body(xform=wp.transform(wp.vec3(-.005,0.,0.),wp.quat_identity()),mass=.02,inertia=wp.mat33(.0001,0.,0.,0.,.0001,0.,0.,0.,.0001),is_kinematic=True)
  builder.add_shape_box(proxy,hx=.005,hy=.005,hz=.005,cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.,gap=0.,margin=0.))
  builder.color();model=builder.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
  solver=CohesiveVBD(model,iterations=16,rigid_compliant_alm=True,integrate_with_external_rigid_solver=True,rigid_avbd_beta=0.)
  pairs=wp.array([[0,1]],dtype=wp.vec2i);rest=wp.array([[.021,0.,0.]],dtype=wp.vec3);matrix=wp.array([[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]],dtype=wp.mat33);law=wp.array([[100.,.001,.004]],dtype=wp.vec3);history=wp.zeros(1,dtype=wp.vec2);eligible=wp.array([1],dtype=int)
  solver.configure_cohesion(pairs,rest,matrix,law,history,eligible);sin=model.state();sout=model.state()
  pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=8,rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True);contacts=pipeline.contacts()
  forces=wp.zeros(2,dtype=wp.vec3);hessians=wp.zeros(2,dtype=wp.mat33)
  def probe(gap):
   nonlocal probes
   sin.particle_q.assign(wp.array([[-.02,0.,0.],[.001+gap,0.,0.]],dtype=wp.vec3));forces.zero_();hessians.zero_()
   for color in range(len(model.particle_color_groups)):
    wp.launch(cohesive_blocks,dim=1,inputs=[color,model.particle_colors,sin.particle_q,pairs,rest,matrix,law,history,eligible,solver.invalid],outputs=[forces,hessians])
   wp.synchronize();before=history.numpy().tolist()[0];solver.commit_cohesion(sin);wp.synchronize();probes+=1
   return dict(gap_m=gap,force_n=forces.numpy().tolist()[0][0],damage=history.numpy().tolist()[0][1],kappa_m=history.numpy().tolist()[0][0],history_before=before)
  def loading():
   path=[]
   for i in range(401):
    if (out/'stop.request').exists():raise InterruptedError('Stopped during controlled coupon path')
    path.append(probe(.0041*i/400))
   work=sum(.5*(a['force_n']+b['force_n'])*(b['gap_m']-a['gap_m']) for a,b in zip(path,path[1:]));target=.5*100*.001*.004
   if abs(work-target)>.01*target+1e-12 or path[-1]['damage']!=1. or path[-1]['force_n']!=0.:raise ValueError('Native coupon fracture-energy mismatch')
   return path,work
  baseline,work=loading();records.append(dict(id='opening_energy',fracture_work_j=work,target_fracture_work_j=.0002,relative_error=abs(work-.0002)/.0002,history=baseline,eligibility='Explicit controlled material test, not blade-derived.'))
  # Fully failed link must permit independent free flight.
  def prepare(x,v):
   for state in (sin,sout):
    state.particle_q.assign(wp.array([[-.02,0.,0.],[x,0.,0.]],dtype=wp.vec3));state.particle_qd.assign(wp.array([[0.,0.,0.],[v,0.,0.]],dtype=wp.vec3));state.clear_forces()
  prepare(.0051,.1);pipeline.collide(sin,contacts);wp.synchronize()
  if int(contacts.soft_contact_count.numpy()[0])!=0:raise ValueError('Unexpected free-release contact')
  solver.step(sin,sout,None,contacts,DT);wp.synchronize();steps+=1
  if abs(sout.particle_qd.numpy().tolist()[1][0]-.1)>2e-5:raise ValueError('Broken interface resisted free release')
  records.append(dict(id='independent_release',damage=history.numpy().tolist()[0][1],velocity_after=sout.particle_qd.numpy().tolist()[1],cohesive_bond_active=False))
  # Reclosure is an explicit control; Newton collision supplies compression, never healed cohesion.
  prepare(-.0001,0.);pipeline.collide(sin,contacts);wp.synchronize()
  if int(contacts.soft_contact_count.numpy()[0])!=1:raise ValueError('Expected one reclosure contact')
  solver.step(sin,sout,None,contacts,DT);wp.synchronize();steps+=1
  reaction=collect_reaction(model,sout,sin,contacts,solver);force=reaction['force'][0];mp=float(model.particle_mass.numpy()[1]);expected=1750*.0001/(1+1750*DT*DT/mp)
  if abs(force[0]-expected)>2e-5 or math.hypot(*force[1:])>2e-5 or history.numpy().tolist()[0][1]!=1.:raise ValueError('Post-failure compression/healing mismatch')
  records.append(dict(id='post_failure_reclosure',native_reaction=reaction,expected_repulsive_force_n=expected,damage_unchanged=True,particle_repositioned_explicitly=True))
  prepare(.001,0.);pipeline.collide(sin,contacts);wp.synchronize()
  if int(contacts.soft_contact_count.numpy()[0])!=0:raise ValueError('Reclosure did not clear')
  solver.step(sin,sout,None,contacts,DT);wp.synchronize();steps+=1
  if math.hypot(*sout.particle_qd.numpy().tolist()[1])>1e-7:raise ValueError('Stale post-cut contact force')
  records.append(dict(id='clear_control',contact_count=0,velocity_after=sout.particle_qd.numpy().tolist()[1],damage=history.numpy().tolist()[0][1]))
  # An explicit episode reset must restore history, states and contact prefix.
  for state in (sin,sout):solver.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD);state.clear_forces()
  history.zero_();solver.invalid.zero_();pipeline.reset_contact_matching();contacts.clear()
  solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1
  if history.numpy().tolist()!=[[0.,0.]]:raise ValueError('Material reset failed')
  replay,again=loading()
  if replay!=baseline or work!=again:raise ValueError('Coupon history replay mismatch')
  records.append(dict(id='reset_replay',exact=True,work_j=again))
  if steps!=4 or probes!=802 or len(records)!=5:raise ValueError('Unexpected coupon counts')
  write(out,'material_coupon_measurements.json',dict(cases=records,newton_steps=steps,opening_probes=probes,scope='One-pair fixed-frame cohesive interface; synthetic, non-volumetric, controlled opening; no real blade.'))
  passed=True
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',result())
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
