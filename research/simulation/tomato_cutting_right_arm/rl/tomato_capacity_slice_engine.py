"""Existing research material driven by measured blade poses.

Transactional target step only. The caller owns robot stepping and explicit
reaction-force exchange. No motor-work or experimental qualification implied.
"""
from pathlib import Path
import json,sys
import numpy as np
import warp as wp
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]

def subcycled_engine(initial_pose,com_local,*,checkpoint=None,padding_m=4e-5,diagnostic_directory=None):
 from tomato_native_full_model import registry,configure_solver
 from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
 from tomato_relative_contact import RelativeSurfaceContact
 from tomato_local_frame import translated_registry,retain_canonical_material
 from tomato_board_support import nodal_plane_stiffness
 from tomato_element_frame_live import PatchFrameLiveCAD as LiveCADCandidate,configure_patch_frame
 from tomato_capacity_cad_pressure import CapacityCADPressurePacket as CachedCADPressurePacket
 from tomato_grouped_pressure_assembly import GroupedPressureAssembly
 from tomato_capacity_packet_refresh import refresh_packet
 from tomato_cut_eligibility import CutEligibility,freeze
 from tomato_swept_front import SweptFrontDetector
 from tomato_research_separation import measure
 sys.path.insert(0,str(ROOT/'.deps/ipctk-1.6.1-local-cp312'))
 import ipctk
 wp.init();wp.set_device('cuda:0');ipctk.set_num_threads(1)
 world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);model=build_relative_model(data,fixed_nodes=fixed)
 h=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=nodal_plane_stiffness(world),board_height=-origin[2]);retain_canonical_material(h,world,source_rest);configure_patch_frame(h,world)
 h.surface_contact=RelativeSurfaceContact(data,h.spatial_reference,margin=.0001,capacity=256);h.surface_contact.physical_colors=model.particle_colors
 s=LiveCADCandidate(h,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6,declared_duration_s=.1);s.pressure=CachedCADPressurePacket(s.n);s.assembly=GroupedPressureAssembly(s.assembly.base,s.pressure)
 a,b=s.state(),s.state();prepared=np.load(ROOT/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');a.particle_q.assign(prepared['x_sim']);a.particle_qd.zero_()
 blade=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((ROOT/'work/exact_blade_cells.json').read_text());vertices=np.asarray(blade['vertices']);cells=np.asarray(solid['cells']);triangles=np.array([tri for piece in world['design']['pieces']for tri in piece['triangles']]);ref=np.load(ROOT/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
 pose=np.asarray(initial_pose,dtype=float);R=Rotation.from_quat(pose[3:]).as_matrix();t=pose[:3]-origin;com=np.asarray(com_local,dtype=float)
 packet={key:ref[key] for key in ('indices','barycentric','areas')};reg=np.load(ROOT/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz');front=json.loads((ROOT/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids']
 elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,np.r_[ref['translation'],Rotation.from_matrix(ref['rotation']).as_quat()])
 elapsed=0.;steps=0
 if checkpoint is not None:
  z=np.load(checkpoint);a.particle_q.assign(z['x']);a.particle_qd.assign(z['v']);h.objective_history.assign(z['history']);h.history.assign(z['history'].astype(np.float32));R=z['blade_rotation'];t=z['blade_translation'];pose=np.r_[t+origin,Rotation.from_matrix(R).as_quat()];packet={k:z['packet_'+k] for k in ('indices','barycentric','areas')};elig.world=freeze(z['x']+origin);elig.pose=freeze(pose);elig.seen=freeze(z['seen']);elig.eligible=freeze(z['eligible']);elapsed=float(z['elapsed'])
 else:elig.reset(prepared['x_sim']+origin,pose)
 def bind():
  s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=com,source_scope='Measured-pose research contact; original material')
  s.bind_domain(a.particle_q.numpy(),vertices,R,t);s.domain_bound_m=padding_m/2
 bind()
 def output():
  s.pressure.evaluate(a.particle_q);x=a.particle_q.numpy()+origin;v=a.particle_qd.numpy();hist=h.objective_history.numpy();force=s.pressure.force.numpy();wrench=s.pressure.reaction();center=t+origin+R@com
  expected=np.r_[-force.sum(0),-np.cross(x-center,force).sum(0)]
  if np.linalg.norm(expected[:3]-wrench[:3])>1e-8 or np.linalg.norm(expected[3:]-wrench[3:])>1e-9:raise ValueError('Reaction sign or COM moment mismatch')
  return dict(x=x,v=v,history=hist,pose=pose.copy(),elapsed=elapsed,steps=steps,wrench=wrench,force=force,separation=measure(data,x,v,hist),eligible=elig.eligible.copy(),checkpoint_writer=save_checkpoint,solver_iterations=len(s.last_trace) if hasattr(s,'last_trace') else 0)
 def save_checkpoint(path,**metadata):
  path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
  temporary=path.with_suffix('.tmp.npz')
  np.savez(temporary,x=a.particle_q.numpy(),v=a.particle_qd.numpy(),history=h.objective_history.numpy(),blade_rotation=R,blade_translation=t,seen=elig.seen,eligible=elig.eligible,elapsed=elapsed,adaptive_dt_cap=adaptive_dt_cap,**{'packet_'+k:v for k,v in packet.items()})
  temporary.replace(path)
  path.with_suffix('.json').write_text(json.dumps(dict(steps=steps,elapsed=elapsed,**metadata),indent=2))
 def advance_one(new_pose,dt):
  nonlocal a,b,R,t,pose,elapsed,steps,packet
  new_pose=np.asarray(new_pose,float);dt=float(dt);new_R=Rotation.from_quat(new_pose[3:]).as_matrix();new_t=new_pose[:3]-origin
  if new_pose.shape!=(7,) or not np.isfinite(new_pose).all() or abs(np.linalg.norm(new_pose[3:])-1)>1e-10 or not np.isfinite(dt) or dt<=0:raise ValueError('Invalid measured pose or interval')
  motion=float(np.linalg.norm(vertices@new_R.T+new_t-(vertices@R.T+t),axis=1).max())
  if motion>padding_m/2:raise ValueError(('Measured blade exceeds covered interval',motion))
  lookahead=(a.particle_q.numpy()+origin+a.particle_qd.numpy()*dt,new_t+origin,new_R)
  for attempt in range(8):
   packet,_,pre_report=refresh_packet(blade,cells,a.particle_q.numpy()+origin,triangles,world['x'],R,t+origin,com,packet,padding_m=padding_m,lookahead=lookahead);bind();s.pressure.pose(new_R,new_t);candidate={}
   def audit(start,end,old,new,mask,interval):
    x=end.particle_q.numpy();v=end.particle_qd.numpy();ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
    if not(np.isfinite(x).all() and np.isfinite(v).all() and ratios.min()>.1 and np.array_equal(x[fixed],prepared['x_sim'][fixed]) and np.all(new>=old-1e-14) and np.array_equal(new[~mask],old[~mask])):return False
    candidate['lookahead']=(x+origin,new_t+origin,new_R);candidate['geometry']=elig.trial(x+origin,new_pose)
    candidate['post']=refresh_packet(blade,cells,x+origin,triangles,world['x'],new_R,new_t+origin,com,packet,padding_m=padding_m);return True
   try:s.audited_step(a,b,dt,eligibility=elig.eligible.copy(),acceptance_audit=audit)
   except ValueError as error:
    if 'differs from old packet' in str(error) and 'lookahead' in candidate:
     lookahead=candidate['lookahead'];s.pressure.pose(R,t);continue
    raise
   break
  else:raise ValueError('No accepted measured-pose material candidate')
  elig.commit(candidate['geometry'],accepted=True);a,b=b,a;R=new_R;t=new_t;pose=new_pose.copy();elapsed+=dt;steps+=1;packet=candidate['post'][0];bind()

 adaptive_dt_cap=float(z['adaptive_dt_cap']) if checkpoint is not None and 'adaptive_dt_cap' in z else 1/2400
 request=yield output()
 while request is not None:
  goal=np.asarray(request['pose'],float);interval=float(request['dt']);start_pose=pose.copy();start_R=R.copy();goal_R=Rotation.from_quat(goal[3:]).as_matrix();rotation_delta=Rotation.from_matrix(goal_R@start_R.T).as_rotvec();end_center=goal[:3]+goal_R@com
  if not np.isfinite(interval) or interval<=0:raise ValueError('Invalid robot interval')
  completed=0.;impulse=np.zeros(6);substeps=0;retried=False
  while completed<interval-1e-15:
   maximum_speed=float(np.linalg.norm(a.particle_qd.numpy(),axis=1).max());blade_speed=float(np.linalg.norm(vertices@goal_R.T+goal[:3]-(vertices@start_R.T+start_pose[:3]),axis=1).max())/interval
   remaining=interval-completed;limit=min(adaptive_dt_cap,padding_m/(4*max(maximum_speed,blade_speed,1e-9)));micro=remaining/max(1,int(np.ceil(remaining/limit)))
   for retry in range(12):
    fraction=(completed+micro)/interval;rr=Rotation.from_rotvec(rotation_delta*fraction).as_matrix()@start_R;pp=start_pose[:3]+fraction*(goal[:3]-start_pose[:3]);trial=np.r_[pp,Rotation.from_matrix(rr).as_quat()]
    try:advance_one(trial,micro)
    except ValueError as error:
     if diagnostic_directory is not None:
      save_checkpoint(Path(diagnostic_directory)/'material_before_failed_microstep.npz',error=str(error),goal_pose=goal.tolist(),outer_interval=interval,completed_interval=completed,micro_interval=micro,trial_pose=trial.tolist(),solver_trace=s.last_trace)
     if any(word in str(error)for word in ('descending','iteration budget','coverage bound','covered interval','true-residual')) and micro>1/1228800:micro*=.5;adaptive_dt_cap=micro;retried=True;continue
     raise
    break
   else:raise ValueError('No admissible target substep for actual robot motion')
   s.pressure.evaluate(a.particle_q);reaction=s.pressure.reaction();center=t+origin+R@com;reaction[3:]+=np.cross(center-end_center,reaction[:3]);impulse+=micro*reaction;completed+=micro;substeps+=1
   if substeps>4096:raise ValueError('Excessive target subcycling; stop robot episode')
  if not retried:adaptive_dt_cap=min(1/2400,adaptive_dt_cap*1.25)
  result=output();result.update(interval_substeps=substeps,interval_impulse_at_end_com=impulse,average_wrench_at_end_com=impulse/interval)
  request=yield result
