"""Zero-step actual CAD/full-registry pressure qualification; no robot feedback."""
import argparse,signal,traceback,json
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('CAD pressure controls stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  references=[ROOT/'runs/offline/prepared_contact_candidate_20261102_03/fixed_cad_pressure_reference.npz',ROOT/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz'];blade_path=ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';parents=[ROOT/'runs/offline/prepared_contact_candidate_20261102_03/measurements.json',ROOT/'runs/offline/padded_cad_packet_20261102_01/measurements.json']
  for parent in parents:
   result=json.loads(parent.read_text())
   if not result.get('passed',result.get('host_candidate_passed',False)):raise ValueError(('Host parent not qualified',str(parent)))
  pins=capture_sources(out,[Path(__file__)],inputs=references+[blade_path]+parents+[ROOT/'runs/offline/integration_contract_20261102_26/contract.json'])
  write(out,'input_manifest.json',dict(cases=6,force_budget_n=1e-9,energy_budget_j=1e-12,wrench_budget_n_or_nm=1e-10,query_distance_budget_m=1e-12,query_normal_budget=1e-6,pressure_matrix_action_budget_n=1e-8,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,scope='Two positive fixed-material actual-CAD packets, each nominal, common proper rigid transform, and clear. Full original material registry and complete barycentric search blocks. Independent NumPy geometry/force/energy/matrix reference. ZERO mechanics/robot/work/CCD/cutting qualification.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from warp import sparse
  from tomato_native_full_model import registry,configure_solver
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_local_frame import translated_registry,retain_canonical_material
  from tomato_board_support import nodal_plane_stiffness
  from tomato_failed_safe_global import FailedSafeFractionCandidate
  from tomato_cad_pressure import CADPressureCandidate
  from tomato_host_fixed_pressure import evaluate_fixed
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);holder=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(holder,world,source_rest);holder.surface_contact=RelativeSurfaceContact(data,holder.spatial_reference,margin=.0001,capacity=256);holder.surface_contact.physical_colors=model.particle_colors;base=FailedSafeFractionCandidate(holder,data,fixed);candidate=CADPressureCandidate(holder,data,fixed);dt=1/2400;free=base.assembly.free.numpy().astype(bool);blade=json.loads(blade_path.read_text());rng=np.random.default_rng(7721);Q=Rotation.from_rotvec([.27,-.19,.31]).as_matrix();offset=np.array([.007,-.004,.003])
  for packet_index,path in enumerate(references):
   z=np.load(path);packet={key:z[key]for key in ['indices','barycentric','areas']};x0=z['x_sim'];R0=z['rotation'];t0=z['translation']-z['world_from_sim_translation_m'];com=z['com_local']
   for kind in ['nominal','common_rigid','clear']:
    xh=x0 if kind!='common_rigid'else x0@Q.T+offset;R=R0 if kind!='common_rigid'else Q@R0;t=t0 if kind!='common_rigid'else Q@t0+offset
    if kind=='clear':t=t+np.array([0.,0.,.25])
    ref=evaluate_fixed(blade,xh,packet,R,t,com);x=wp.array(xh,dtype=wp.vec3d);base.target.assign(xh);candidate.target.assign(xh);candidate.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=com,source_scope='Host-qualified actual CAD material packet '+str(path))
    base.force(x,dt);f0=base.rhs.numpy();E0=base.energy(x,dt);candidate.force(x,dt);f1=candidate.rhs.numpy();E1=candidate.energy(x,dt);expected=ref['force_n'].copy();expected[~free]=0;force_error=float(abs(f1-f0-expected).max());energy_error=float(abs(E1-E0-ref['energy_j']));reaction_error=float(abs(candidate.pressure.reaction()-ref['body_wrench']).max());distance_error=float(abs(candidate.pressure.phi.numpy()-ref['query']['phi']).max());normal_error=float(abs(candidate.pressure.normals.numpy()-ref['query']['normal']).max())
    directions=rng.normal(size=(3,len(xh),3))*1e-7;directions[:,~free]=0;base.assembly.assemble(x,dt);base_actions=[]
    for direction in directions:
     result=wp.zeros(len(xh),dtype=wp.vec3d);sparse.bsr_mv(base.assembly.matrix,wp.array(direction,dtype=wp.vec3d),result);base_actions.append(result.numpy())
    candidate.force(x,dt);candidate.assembly.assemble(x,dt);matrix_errors=[];normal=ref['query']['normal']@R.T;active=ref['query']['phi']<0
    for direction,base_action in zip(directions,base_actions):
     motion=np.einsum('ni,nij->nj',packet['barycentric'],direction[packet['indices']]);sample=(1.75e9*packet['areas']*active*np.sum(normal*motion,axis=1))[:,None]*normal;expected_action=np.zeros_like(xh)
     for corner in range(3):np.add.at(expected_action,packet['indices'][:,corner],packet['barycentric'][:,corner,None]*sample)
     expected_action[~free]=0;result=wp.zeros(len(xh),dtype=wp.vec3d);sparse.bsr_mv(candidate.assembly.matrix,wp.array(direction,dtype=wp.vec3d),result);matrix_errors.append(float(abs(result.numpy()-base_action-expected_action).max()))
    row=dict(packet_index=packet_index,case=kind,samples=len(packet['areas']),force_error_n=force_error,energy_error_j=energy_error,wrench_error_n_or_nm=reaction_error,query_distance_error_m=distance_error,query_normal_error=normal_error,pressure_matrix_action_errors_n=matrix_errors,pressure_energy_j=ref['energy_j'],pressure_force_l1_n=float(np.linalg.norm(ref['force_n'],axis=1).sum()),actual_faces=sorted(set(candidate.pressure.face.numpy()[active].tolist())))
    write(out,'measurements_partial.json',dict(cases=cases+[row]))
    if force_error>1e-9 or energy_error>1e-12 or reaction_error>1e-10 or distance_error>1e-12 or normal_error>1e-6 or max(matrix_errors)>1e-8:raise ValueError(row)
    if kind=='clear'and(np.any(candidate.pressure.force.numpy())or ref['energy_j']or np.any(candidate.pressure.reaction())):raise ValueError('Clear CAD field did not clear')
    refused=False
    try:candidate.step(None,None,None,None,dt)
    except ValueError:refused=True
    if not refused:raise ValueError('Unqualified mounted interval stepped')
    row['unqualified_step_refused']=True;cases.append(row);write(out,'measurements_partial.json',dict(cases=cases))
  if not sources_unchanged(pins):raise ValueError('CAD pressure controls source/input changed')
  write(out,'cad_pressure_measurements.json',dict(passed=True,cases=cases,scope='Six ZERO-step actual authored CAD/full-registry force, energy, wrench, double query and complete cross-node positive normal search-matrix controls. No actual robot feedback, dynamic target/contact accuracy, CCD, work closure or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,cad_pressure_operator_passed=passed,cases_completed=len(cases),physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
