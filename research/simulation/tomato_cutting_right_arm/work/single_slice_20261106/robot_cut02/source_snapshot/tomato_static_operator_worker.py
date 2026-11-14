"""Global potential/force and admissibility operators; no mechanics advanced."""
import argparse,json,signal,subprocess,sys,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Global energy check stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  reference=ROOT/'rl/tomato_static_energy_cpu_reference.py';captured=ROOT/'runs/native/rebased_local_preflight_20261102_01/first_bad_update.npz';pins=capture_sources(out,[Path(__file__),reference],inputs=[captured])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_static_gravity import StaticGravityCandidate as GlobalImplicitCandidate,static_rhs,static_node_energy
  from tomato_global_ledger import collect_world_external
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];fixed=np.array(data['design']['fixture']['node_ids']);model=build_relative_model(data,fixed_nodes=fixed);s=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=nodal_plane_stiffness(data));e=s.surface_contact=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;g=GlobalImplicitCandidate(s,data,fixed);n=len(data['x']);dt=1/4800;directions=np.random.default_rng(409).normal(size=(3,n,3));directions/=abs(directions).max();directions[1]=0;directions[1,np.unique(data['pairs'][:,1]),0]=1;directions[2]=0;directions[2,:,2]=1;directions[:,fixed]=0
  write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,energy_reference_absolute_budget_j=1e-10,energy_reference_relative_budget=1e-9,finite_work_absolute_budget_j=1e-11,finite_work_relative_budget=.01,perturbations_m=[1e-8,5e-9,2.5e-9],scope='Static original potential/force plus gravity controls and analytical mass-spring equilibrium. No inertia or material damping, physical time, support hold or cutting qualification.'))
  for label,x in [('rest',data['x'].copy()),('affine',data['x']@np.array([[.74,.015,0],[0,.76,.01],[0,0,.85]]).T),('captured_contact',np.load(captured)['x'])]:
   xw=wp.array(x,dtype=wp.vec3d);target=x.copy();target[fixed]=x[fixed];free=g.assembly.free.numpy().astype(bool);g.target.assign(target);g.force(xw,dt);G=g.energy(xw,dt);force=g.rhs.numpy().copy();g.force(xw,dt*10.);alternate_energy=g.energy(xw,dt*10.);regularizer_force_difference=float(abs(g.rhs.numpy()-force).max());regularizer_energy_difference=abs(alternate_energy-G)
   if regularizer_force_difference>1e-8 or regularizer_energy_difference>1e-12:raise ValueError('Static numerical regularizer leaked into physical force/potential')
   count=int(e.stencil_count.numpy()[0]);inputpath=out/f'{label}_energy_inputs.npz';np.savez(inputpath,gravity=np.array([0.,0.,-9.81]),gravity_reference=data['x'],x=x,source_x=data['x'],free=g.assembly.free.numpy(),mass=data['mass'],dt=np.array([dt]),target=target,spring_pairs=data['springs'],spring_k=data['k'],cells=data['cells'],volumes=data['volumes'],cohesive_pairs=s.pairs.numpy(),cohesive_counts=s.counts.numpy(),anchors=s.objective_anchors.numpy(),sign=s.objective_sign.numpy(),weights=s.objective_weights.numpy(),local_k=s.objective_stiffness.numpy(),history=s.objective_history.numpy(),eligible=s.eligible.numpy(),proxy=e.precise_position.numpy(),endpoint=e.endpoint.numpy()[:count],kind=e.kind.numpy()[:count],threshold=e.mollifier_threshold.numpy()[:count],radius=np.array([e.margin]),contact_k=np.array([e.model.soft_contact_ke]),board_k=s.board_stiffness.numpy(),board_height=np.array([s.board_height]),native_energy=np.array([G]));refout=out/f'{label}_energy_reference.json'
   with (out/f'{label}_reference.log').open('w')as log:result=subprocess.run([sys.executable,str(reference),'--input',str(inputpath),'--output',str(refout)],stdout=log,stderr=subprocess.STDOUT,timeout=180,check=False)
   if result.returncode or not json.loads(refout.read_text())['passed']:raise ValueError('Independent global energy failed '+label)
   work=[];initial_history=s.objective_history.numpy().copy()
   for direction in directions:
    checks=[]
    for step in [1e-8,5e-9,2.5e-9]:
     plus=x+step*direction;minus=x-step*direction;observed=g.energy(wp.array(plus,dtype=wp.vec3d),dt,trial=True)-g.energy(wp.array(minus,dtype=wp.vec3d),dt,trial=True);expected=-float(np.sum(force*(plus-minus)));absolute=abs(observed-expected);relative=absolute/max(abs(observed),abs(expected),1e-14);checks.append(dict(step_m=step,energy_difference_j=observed,negative_force_work_j=expected,absolute_error_j=absolute,relative_error=relative))
    if not any(row['absolute_error_j']<=1e-11 or row['relative_error']<=.01 for row in checks):write(out,'finite_work_failure.json',dict(case=label,checks=checks));raise ValueError('Global potential is inconsistent with the unchanged force field')
    work.append(checks)
   if not np.array_equal(initial_history,s.objective_history.numpy()):raise ValueError('Energy trials mutated material history')
   cases.append(dict(case=label,static_potential_j=G,regularizer_force_difference_n=regularizer_force_difference,regularizer_energy_difference_j=regularizer_energy_difference,directional_work_checks=work))
  # Independent one-particle gravity/spring equilibrium and force units.
  z=1.-9.81/100.;point=wp.array([[0.,0.,z]],dtype=wp.vec3d);mass=wp.array([1.],dtype=wp.float64);free=wp.ones(1,dtype=int);bulk=wp.array([[0.,0.,100.*(1.-z)]],dtype=wp.vec3d);zero=wp.zeros(1,dtype=wp.vec3d);bk=wp.zeros(1,dtype=float);rhs=wp.zeros(1,dtype=wp.vec3d);total=wp.zeros(1,dtype=wp.float64);maximum=wp.zeros(1,dtype=wp.float64);wp.launch(static_rhs,dim=1,inputs=[point,mass,free,wp.vec3d(0.,0.,-9.81),bulk,zero,zero,bk,wp.float64(-10.)],outputs=[rhs,total,maximum]);force_error=float(abs(rhs.numpy()).max());parts=wp.zeros(2,dtype=wp.float64);wp.launch(static_node_energy,dim=1,inputs=[point,wp.array([[0.,0.,1.]],dtype=wp.vec3d),mass,free,wp.vec3d(0.,0.,-9.81),bk,wp.float64(-10.)],outputs=[parts]);root_energy=float(parts.numpy().sum()+.5*100.*(z-1.)**2);energy_error=abs(root_energy-(-.5*9.81**2/100.))
  if force_error>1e-12 or energy_error>1e-12:raise ValueError('Static gravity root/energy control failed')
  if not sources_unchanged(pins):raise ValueError('Global energy sources changed')
  write(out,'static_operator_measurements.json',dict(cases=cases,analytic_root_force_error_n=force_error,analytic_root_energy_error_j=energy_error,scope='Three independent full-registry static-potential values and force/work checks, analytical gravity/spring equilibrium. Zero physical steps; no transient, support hold or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,static_operator_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
