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
  reference=ROOT/'rl/tomato_global_energy_cpu_reference.py';captured=ROOT/'runs/native/rebased_local_preflight_20261102_01/first_bad_update.npz';pins=capture_sources(out,[Path(__file__),reference],inputs=[captured])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_board_support import nodal_plane_stiffness
  from tomato_global_implicit import GlobalImplicitCandidate,global_volume_path
  from tomato_global_ledger import collect_world_external
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];fixed=np.array(data['design']['fixture']['node_ids']);model=build_relative_model(data,fixed_nodes=fixed);s=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=nodal_plane_stiffness(data));e=s.surface_contact=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;g=GlobalImplicitCandidate(s,data,fixed);n=len(data['x']);dt=1/4800;directions=np.random.default_rng(409).normal(size=(3,n,3));directions/=abs(directions).max();directions[1]=0;directions[1,np.unique(data['pairs'][:,1]),0]=1;directions[2]=0;directions[2,:,2]=1;directions[:,fixed]=0
  write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,energy_reference_absolute_budget_j=1e-10,energy_reference_relative_budget=1e-9,finite_work_absolute_budget_j=1e-11,finite_work_relative_budget=.01,perturbations_m=[1e-8,5e-9,2.5e-9],scope='Potential/force, path-admissibility and float64 ledger controls for the explicit global GN candidate only. No physical integration, support or cutting qualification.'))
  for label,x in [('rest',data['x'].copy()),('affine',data['x']@np.array([[.74,.015,0],[0,.76,.01],[0,0,.85]]).T),('captured_contact',np.load(captured)['x'])]:
   xw=wp.array(x,dtype=wp.vec3d);target=x.copy();target[fixed]=x[fixed];free=g.assembly.free.numpy().astype(bool);target[free]+=[0,0,-9.81*dt*dt];g.target.assign(target);g.force(xw,dt);G=g.energy(xw,dt);force=g.rhs.numpy();count=int(e.stencil_count.numpy()[0]);inputpath=out/f'{label}_energy_inputs.npz';np.savez(inputpath,x=x,source_x=data['x'],free=g.assembly.free.numpy(),mass=data['mass'],dt=np.array([dt]),target=target,spring_pairs=data['springs'],spring_k=data['k'],cells=data['cells'],volumes=data['volumes'],cohesive_pairs=s.pairs.numpy(),cohesive_counts=s.counts.numpy(),anchors=s.objective_anchors.numpy(),sign=s.objective_sign.numpy(),weights=s.objective_weights.numpy(),local_k=s.objective_stiffness.numpy(),history=s.objective_history.numpy(),eligible=s.eligible.numpy(),proxy=e.precise_position.numpy(),endpoint=e.endpoint.numpy()[:count],kind=e.kind.numpy()[:count],threshold=e.mollifier_threshold.numpy()[:count],radius=np.array([e.margin]),contact_k=np.array([e.model.soft_contact_ke]),board_k=s.board_stiffness.numpy(),board_height=np.array([s.board_height]),native_energy=np.array([G]));refout=out/f'{label}_energy_reference.json'
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
   cases.append(dict(case=label,incremental_energy_j=G,directional_work_checks=work))
  path_controls=[];x=data['x'];bad=wp.zeros(1,dtype=int)
  for label,end,expect in [('translation',x+[.0001,0,0],False),('collapsed_end',x*.4,True),('positive_ends_bad_middle',x@np.diag([-1.,-1.,1.]),True)]:
   bad.zero_();wp.launch(global_volume_path,dim=len(data['cells']),inputs=[wp.array(x,dtype=wp.vec3d),wp.array(end,dtype=wp.vec3d),s.cells,s.volumes64],outputs=[bad]);observed=bool(bad.numpy()[0])
   if observed!=expect:raise ValueError('Global path-volume control failed')
   path_controls.append(dict(case=label,rejected=observed))
  # Float64 collector field convention: exact freefall has no local impulse error.
  mass=np.array([.001,.002,.003]);positions=np.array([[0,0,.02],[.01,0,.03],[0,.01,.04]]);vel=np.tile([0,0,-9.81*dt],(3,1));zero=wp.zeros(3,dtype=wp.vec3d);previous=wp.zeros(3,dtype=wp.vec3d);impulse=wp.zeros(3,dtype=wp.vec3d);angular=wp.zeros(3,dtype=wp.vec3d);instant=wp.zeros(3,dtype=wp.vec3d);total=wp.zeros(1,dtype=wp.float64);last=wp.zeros(1,dtype=wp.float64);maximum=wp.zeros(1,dtype=wp.float64);wp.launch(collect_world_external,dim=3,inputs=[wp.array(positions,dtype=wp.vec3d),wp.array(vel,dtype=wp.vec3d),previous,wp.array(mass,dtype=wp.float64),wp.zeros(3,dtype=int),zero,zero,zero,wp.zeros(3,dtype=float),wp.float64(dt)],outputs=[impulse,angular,instant,total,last,maximum]);ledger_error=float(total.numpy()[0])
  if ledger_error>1e-15:raise ValueError('Float64 collector field convention failed')
  if not sources_unchanged(pins):raise ValueError('Global energy sources changed')
  write(out,'global_energy_measurements.json',dict(cases=cases,path_controls=path_controls,float64_ledger_freefall_error_ns=ledger_error,scope='Three independent full-model potential values and force/work controls, safe-path controls and exact float64 freefall ledger. Zero mechanical steps; no integration/support/cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,global_energy_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
