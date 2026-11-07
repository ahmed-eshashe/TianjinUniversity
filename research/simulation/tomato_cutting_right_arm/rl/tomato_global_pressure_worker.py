"""Full-registry frozen-pressure assembly controls, zero mechanical steps."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Global pressure operators stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  fixture=ROOT/'runs/offline/physical_pressure_20261102_02/operator_fixtures.npz';pins=capture_sources(out,[Path(__file__)],inputs=[fixture])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from warp import sparse
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_board_support import nodal_plane_stiffness
  from tomato_failed_safe_global import FailedSafeFractionCandidate
  from tomato_global_pressure import GlobalPressureCandidate
  from tomato_physical_pressure_reference import evaluate_pressure
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world,source_rest);holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);holder.surface_contact.physical_colors=model.particle_colors;base=FailedSafeFractionCandidate(holder,data,fixed);candidate=GlobalPressureCandidate(holder,data,fixed);x=wp.array(data['x'],dtype=wp.vec3d);dt=1/2400;base.target.assign(data['x']);candidate.target.assign(data['x']);z=np.load(fixture);node_ids=np.array([0,1,2],dtype=np.int32)
  free=base.assembly.free.numpy().astype(bool)
  if not free[node_ids].all():raise ValueError('Pressure fixture requires three free source nodes')
  write(out,'input_manifest.json',dict(cases=3,force_budget_n=1e-9,energy_budget_j=1e-12,pressure_matrix_action_budget_n=1e-8,finite_work_absolute_budget_n=1e-7,newton_steps=0,deformable_steps=0,controlled_steps=0,physical_time_advanced_s=0.,scope='Full original source registry with one frozen reference-area planar CAD-feature packet. Independent host force/energy and complete barycentric matrix actions. No generated-contact coverage, blade route, physical steps, support, robot or work-closure qualification.'))
  rng=np.random.default_rng(4402);directions=rng.normal(size=(3,len(data['x']),3))*1e-7;directions[:,~free]=0
  for i in range(3):
   a={key:z[f'case{i}_{key}']for key in ['barycentric','areas','closest_local','normals_local','rotation','com_local']};ids=node_ids[None];R=a['rotation'];normal=R@a['normals_local'][0];soft=(a['barycentric'][0,:,None]*data['x'][node_ids]).sum(0);gap=50e-6 if i==2 else -50e-6;tangent=R[:,0]-np.dot(R[:,0],normal)*normal
   if np.linalg.norm(tangent)<.1:tangent=R[:,1]-np.dot(R[:,1],normal)*normal
   tangent/=np.linalg.norm(tangent);translation=soft-R@a['closest_local'][0]-gap*normal+(.003*tangent if i else 0);args=dict(indices=ids,barycentric=a['barycentric'],areas=a['areas'],closest_local=a['closest_local'],normals_local=a['normals_local'],rotation=R,translation=translation,com_local=a['com_local']);reference=evaluate_pressure(data['x'],**args);candidate.pressure.set(**args,source_scope='full-registry frozen planar operator fixture')
   base.force(x,dt);f0=base.rhs.numpy();E0=base.energy(x,dt);candidate.force(x,dt);f1=candidate.rhs.numpy();E1=candidate.energy(x,dt);force_error=float(abs((f1-f0)-reference['force']).max());energy_error=float(abs(E1-E0-reference['energy_j']));reaction_error=float(abs(candidate.pressure.reaction()-reference['body_wrench']).max());base.assembly.assemble(x,dt);base_actions=[]
   for direction in directions:
    result=wp.zeros(len(data['x']),dtype=wp.vec3d);sparse.bsr_mv(base.assembly.matrix,wp.array(direction,dtype=wp.vec3d),result);base_actions.append(result.numpy())
   candidate.force(x,dt);candidate.energy(x,dt);candidate.assembly.assemble(x,dt);action_errors=[];finite_work=[]
   for direction,base_action in zip(directions,base_actions):
    result=wp.zeros(len(data['x']),dtype=wp.vec3d);sparse.bsr_mv(candidate.assembly.matrix,wp.array(direction,dtype=wp.vec3d),result);expected=np.zeros_like(data['x']);point_motion=np.einsum('ni,nij->nj',a['barycentric'],direction[ids]);sample_h=(1.75e9*a['areas'][0])*np.outer(normal,normal) if gap<0 else np.zeros((3,3))
    for corner,node in enumerate(node_ids):expected[node]+=a['barycentric'][0,corner]*(sample_h@point_motion[0])
    action_errors.append(float(abs(result.numpy()-base_action-expected).max()));unit=direction/np.linalg.norm(direction);eps=1e-7;ep=candidate.energy(wp.array(data['x']+eps*unit,dtype=wp.vec3d),dt,trial=True);em=candidate.energy(wp.array(data['x']-eps*unit,dtype=wp.vec3d),dt,trial=True);finite_work.append(float(abs(-(ep-em)/(2*eps)-np.sum(f1*unit))))
   row=dict(case=i,force_error_n=force_error,energy_error_j=energy_error,reaction_wrench_error_n_or_nm=reaction_error,pressure_matrix_action_errors_n=action_errors,finite_work_errors_n=finite_work,reference_pressure_energy_j=reference['energy_j'],scope='Frozen planar packet only, all original material/contact forces retained')
   if force_error>1e-9 or energy_error>1e-12 or reaction_error>1e-10 or max(action_errors)>1e-8 or max(finite_work)>1e-7:raise ValueError(row)
   if i==2 and(np.any(candidate.pressure.force.numpy())or np.any(candidate.pressure.reaction())or reference['energy_j']):raise ValueError('Clear pressure packet not zero')
   refused=False
   try:candidate.step(None,None,None,None,dt)
   except ValueError:refused=True
   if not refused:raise ValueError('Unqualified mounted interval unexpectedly stepped')
   row['unqualified_step_refused']=True;cases.append(row)
  if not sources_unchanged(pins):raise ValueError('Pressure integration operator source changed')
  write(out,'global_pressure_measurements.json',dict(cases=cases,scope='Three full-registry frozen planar force/energy/complete cross-node search-matrix controls. Zero physical steps. No generated CAD coverage, actual robot interval work, equilibrium, support or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,global_pressure_operator_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
