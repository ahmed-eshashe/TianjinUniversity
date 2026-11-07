"""Host-only current-geometry contact candidate, not an executed robot route."""
from pathlib import Path
import json,hashlib,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation,Slerp
from tomato_exact_blade_coverage import coverage,verify_cells
from tomato_host_blade_geometry import evaluate_pose,query_mesh
from tomato_exported_robot import ExportedRobot
from tomato_host_fixed_pressure import packet_from_samples,evaluate_fixed
R=Path(__file__).resolve().parents[2];out=R/'runs/offline/prepared_contact_candidate_20261102_03';out.mkdir(exist_ok=False);paths=dict(design=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json',prepared=R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz',geometry=R/'runs/offline/prepared_interface_geometry_20261102_01/measurements.json',blade=R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json',cells=R/'work/exact_blade_cells.json',front=R/'runs/offline/cut_front_registration_20261102_02/registration.json',robot=R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json',plan=R/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json',mounted_component=R/'runs/native/mounted_contact_20261102_03/mounted_contact_measurements.json');pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in list(paths.values())+[Path(__file__),R/'rl/tomato_exported_robot.py',R/'rl/tomato_host_blade_geometry.py',R/'rl/tomato_exact_blade_coverage.py',R/'rl/tomato_host_fixed_pressure.py']};(out/'input_manifest.json').write_text(json.dumps(dict(source_sha256=pins,scope='CPU static geometry, force estimate and FK/IK candidate only. No native route, synchronized motion, swept clearance, actual controller/feedback or cut qualification.',desired_sum_absolute_sample_forces_n=.002,minimum_achieved_force_n=.0015,maximum_achieved_force_n=.005,quadrature_relative_force_budget=.01,quadrature_absolute_force_budget_n=1e-5,active_features_must_be_registered_front=False,requires_general_CAD_feature_force_energy_checks=True,fixed_packet_fd_budget_n_or_nm=1e-7,translation_fd_eps_m=[1e-7,1e-8,1e-9,1e-10,1e-11],rotation_fd_eps_rad=[1e-6,1e-7,1e-8,1e-9,1e-10],maximum_geometric_penetration_m=.0001,ik_position_budget_m=1e-6,ik_orientation_budget_rad=1e-5,forbidden_robot_target_inflated_aabb_gap_m=.01,authored_body_bound_inflation_m=.002,minimum_blade_board_clearance_m=.004,minimum_fixture_point_distance_m=.005),indent=2)+'\n');start=time.monotonic()
try:
 d=json.loads(paths['design'].read_text());z=np.load(paths['prepared']);x=z['x'];reference=z['reference_world'];triangles=np.array([tri for piece in d['pieces']for tri in piece['triangles']]);blade=json.loads(paths['blade'].read_text());cells=json.loads(paths['cells'].read_text());cell_check=verify_cells(blade,cells);front=json.loads(paths['front'].read_text())['front'];plan=json.loads(paths['plan'].read_text());g=json.loads(paths['geometry'].read_text());n=np.array(g['best_fit_plane_normal_world']);center=np.array(g['midface_centroid_world_m']);axis=np.cross([1.,0,0],n);angle=np.arctan2(np.linalg.norm(axis),n[0]);Q=Rotation.from_rotvec(axis/np.linalg.norm(axis)*angle).as_matrix();orientation=Q@np.array(plan['knife_rotation']);up=Q@np.array([0.,0,1.]);v=np.array(blade['vertices']);pairs=np.array(front['vertex_pairs']);mid=v[pairs].mean(1);selected=int(np.argmin(abs(mid[:,0]-v[:,0].mean())));control=mid[selected];base=center-orientation@control;top=float(np.max(x@up));bottom=float(np.min((v@orientation.T)@up));h_clear=top+.005-(base@up+bottom);fixed=np.array(d['fixture']['node_ids']);com=np.array(json.loads(paths['mounted_component'].read_text())['local_tool_com']);trace=[]
 def overlap(h):
  result=coverage(np.array(cells['vertices'])@orientation.T+base+h*up,np.array(cells['cells']),x,triangles,reference_positions=reference,quadrature_level=0);return bool(result['samples'])
 if overlap(h_clear):raise ValueError('Constructed global separating clear pose overlaps')
 high=h_clear;low=None
 for index in range(1,101):
  h=h_clear-index*.001
  if overlap(h):low=h;break
  high=h
 if low is None:raise ValueError('No first overlap found within bounded 100mm search')
 for _ in range(22):
  h=(low+high)/2
  if overlap(h):low=h
  else:high=h
 contact_height=(low+high)/2
 def pressure(depth,level=1):
  t=base+(contact_height-depth)*up;p=evaluate_pose(blade,cells,x,triangles,reference,orientation,t,com,level=level);row=dict(depth_from_first_overlap_m=depth,reference_area_level=level,contact_samples=p['contact_samples'],sum_absolute_sample_forces_n=p['sum_absolute_sample_forces_n'],maximum_penetration_m=p['maximum_penetration_m'],pressure_energy_j=p['energy_j'],body_wrench_at_com=p['body_wrench'].tolist(),active_closest_face_ids=p['face_ids']);trace.append(row);print('pose',row,flush=True);return p
 clear_pressure=pressure(-.00005)
 if clear_pressure['sum_absolute_sample_forces_n']!=0 or clear_pressure['energy_j']!=0:raise ValueError('Precontact clear control already has pressure')
 depth_low=0.;depth_high=None
 for depth in [2e-6,5e-6,1e-5,2e-5,5e-5,1e-4]:
  p=pressure(depth)
  if p['maximum_penetration_m']>.0001:raise ValueError('Static pose search exceeded fixed penetration ceiling')
  if p['sum_absolute_sample_forces_n']>=.002:depth_high=depth;break
  depth_low=depth
 if depth_high is None:raise ValueError('Target geometric force not reached inside bounded search')
 for _ in range(12):
  depth=(depth_low+depth_high)/2;p=pressure(depth)
  if p['sum_absolute_sample_forces_n']>=.002:depth_high=depth
  else:depth_low=depth
 chosen=(depth_low+depth_high)/2;pose=base+(contact_height-chosen)*up;coarse=pressure(chosen,level=1);converged=False;quad_history=[]
 for level in [2,3,4,5]:
  fine=pressure(chosen,level=level);force_difference=float(np.linalg.norm(fine['force_n']-coarse['force_n']));scale=max(float(np.linalg.norm(fine['force_n'])),float(np.linalg.norm(coarse['force_n'])),1e-12);quad_history.append(dict(level=level,force_difference_n=force_difference,force_scale_n=scale))
  if force_difference<=.01*scale+1e-5:converged=True;break
  coarse=fine
 if not converged:raise ValueError('General CAD quadrature did not meet unchanged original budget through level5')

 if not converged:raise ValueError('General CAD quadrature not qualified')
 robot=ExportedRobot(paths['robot']);seed=np.array([robot.values[name]for name in robot.names]);home=robot.knife_pose(seed);preclear=base+(contact_height+.03)*up;interpolator=Slerp([0.,1.],Rotation.from_matrix(np.array([home[:3,:3],orientation])));waypoints=[]
 targets=[((1-u)*home[:3,3]+u*preclear,interpolator([u]).as_matrix()[0],'clear_approach')for u in np.linspace(0,1,9)]
 targets += [(base+(contact_height+height)*up,orientation,'near_contact'if height>0 else'planned_low_force')for height in [.01,.002,.0002,.00005,0.,-chosen]]
 for position,rotation,phase in targets:
  q,pe,ae=robot.solve_knife(position,rotation,seed);actual=robot.knife_pose(q);gaps=robot.target_box_gaps(q,x);forbidden=[b for b in gaps if b['name']!='MountedKnife'];min_gap=min(b['inflated_aabb_axis_separation_m']for b in forbidden);board=float((v@actual[:3,:3].T+actual[:3,3])[:,2].min());fixture_distance=float(query_mesh(v,np.array(blade['triangles']),(x[fixed]-actual[:3,3])@actual[:3,:3])['phi'].min());row=dict(phase=phase,q_right_rad=q.tolist(),planned_knife_position_world_m=position.tolist(),planned_knife_rotation=rotation.tolist(),ik_position_error_m=pe,ik_rotation_error_rad=ae,minimum_forbidden_robot_target_inflated_aabb_gap_m=min_gap,minimum_blade_board_clearance_m=board,minimum_fixture_point_distance_m=fixture_distance,coarse_forbidden_body_gaps=forbidden);waypoints.append(row)
  if pe>1e-6 or ae>1e-5 or min_gap<=.01 or board<=.004 or fixture_distance<=.005:raise ValueError(('Static candidate fails pose/clearance gate',row))
  seed=q
 achieved=robot.knife_pose(seed);achieved_pressure=evaluate_pose(blade,cells,x,triangles,reference,achieved[:3,:3],achieved[:3,3],com,level=level)
 if achieved_pressure['maximum_penetration_m']>.0001 or achieved_pressure['sum_absolute_sample_forces_n']>.005 or achieved_pressure['sum_absolute_sample_forces_n']<.0015 :raise ValueError('Achieved IK pose exceeds low-force geometry envelope')
 packet=packet_from_samples(fine['clipped']['samples']);fixed=evaluate_fixed(blade,x,packet,orientation,pose,com);np.savez(out/'pre_fd_pressure_packet.npz',x=x,rotation=orientation,translation=pose,com_local=com,force=fixed['force_n'],body_wrench=fixed['body_wrench'],energy=np.array([fixed['energy_j']]),**packet);(out/'ik_waypoints.json').write_text(json.dumps(waypoints,indent=2)+'\n');fd_cases=[];body_center=pose+orientation@com
 for axis in range(6):
  errors=[]
  for eps in ([1e-7,1e-8,1e-9,1e-10,1e-11]if axis<3 else[1e-6,1e-7,1e-8,1e-9,1e-10]):
   if axis<3:
    delta=np.eye(3)[axis]*eps;plus=evaluate_fixed(blade,x,packet,orientation,pose+delta,com)['energy_j'];minus=evaluate_fixed(blade,x,packet,orientation,pose-delta,com)['energy_j']
   else:
    delta=np.eye(3)[axis-3]*eps;rp=Rotation.from_rotvec(delta).as_matrix()@orientation;rm=Rotation.from_rotvec(-delta).as_matrix()@orientation;plus=evaluate_fixed(blade,x,packet,rp,body_center-rp@com,com)['energy_j'];minus=evaluate_fixed(blade,x,packet,rm,body_center-rm@com,com)['energy_j']
   errors.append(float(abs(-(plus-minus)/(2*eps)-fixed['body_wrench'][axis])))
  fd_cases.append(dict(case='body_axis_'+str(axis),errors_n_or_nm=errors));(out/'fd_partial.json').write_text(json.dumps(fd_cases,indent=2)+'\n')
  if not np.isfinite(errors).all()or max(errors[-2:])>1e-7:raise ValueError(('Fixed full-CAD body potential derivative failed',fd_cases[-1]))
 rng=np.random.default_rng(103);active=np.unique(packet['indices'])
 for direction_index in range(3):
  direction=np.zeros_like(x);direction[active]=rng.normal(size=(len(active),3));direction/=np.linalg.norm(direction);errors=[]
  for eps in [1e-7,1e-8,1e-9,1e-10,1e-11]:
   plus=evaluate_fixed(blade,x+eps*direction,packet,orientation,pose,com)['energy_j'];minus=evaluate_fixed(blade,x-eps*direction,packet,orientation,pose,com)['energy_j'];errors.append(float(abs(-(plus-minus)/(2*eps)-np.sum(fixed['force_n']*direction))))
  fd_cases.append(dict(case='nodal_direction_'+str(direction_index),errors_n_or_nm=errors));(out/'fd_partial.json').write_text(json.dumps(fd_cases,indent=2)+'\n')
  if not np.isfinite(errors).all()or max(errors[-2:])>1e-7:raise ValueError(('Fixed full-CAD nodal potential derivative failed',fd_cases[-1]))
 np.savez(out/'fixed_cad_pressure_reference.npz',x=x,x_sim=z['x_sim'],world_from_sim_translation_m=z['world_from_sim_translation_m'],rotation=orientation,translation=pose,com_local=com,force=fixed['force_n'],body_wrench=fixed['body_wrench'],energy=np.array([fixed['energy_j']]),phi=fixed['query']['phi'],normal_local=fixed['query']['normal'],closest_local=fixed['query']['closest'],face=fixed['query']['face'],**packet)
 if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in pins.items()):raise ValueError('Host planning source changed')
 report=dict(host_candidate_passed=True,finer_difference_note='03 retains all physical geometry/force/penetration/IK/clearance and 1e-7 derivative gates. 02 finite differences crossed closest-feature changes; 03 adds 100/10pm translations and 1e-9/1e-10rad rotations and requires BOTH finest errors pass, preserving 02 failure. Checkpoints permit independent nonsmooth-feature diagnosis.',scope_change_from_failed_01='01 remains failed at its initial two-level quadrature check; its intended front-only approximation also cannot represent observed whole-fruit contact. 02 is explicitly a general-CAD-feature host candidate with additional fixed-packet force/energy derivative checks; unchanged force, penetration, quadrature and reach/clearance bounds. No native contact qualification.',fixed_packet_derivative_cases=fd_cases,quadrature_history=quad_history,scope='Static host current-geometry pose/force/IK and conservative authored robot-target AABB screen only. Positive disjoint boxes certify this static geometry; overlapping intended tool/target is allowed. No swept, native tracking, collision-cooking, local tissue dynamics, actual mounted force/work or cutting qualification.',first_overlap_height_parameter_m=contact_height,selected_real_front_vertex_pair=pairs[selected].tolist(),control_point_local_m=control.tolist(),target_plane_normal_world=n.tolist(),planned_knife_rotation=orientation.tolist(),planned_knife_translation_world_m=pose.tolist(),planned_depth_from_first_overlap_m=chosen,quad_force_difference_n=force_difference,quad_force_scale_n=float(np.linalg.norm(fine['force_n'])),achieved_ik_sum_absolute_sample_force_n=achieved_pressure['sum_absolute_sample_forces_n'],achieved_ik_maximum_penetration_m=achieved_pressure['maximum_penetration_m'],achieved_ik_closest_face_ids=achieved_pressure['face_ids'],cell_geometry_verification=cell_check,waypoints=waypoints,static_pose_trace=trace,elapsed_wall_s=time.monotonic()-start,source_sha256=pins);(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');np.savez(out/'candidate_pose.npz',rotation=orientation,translation=pose,achieved_rotation=achieved[:3,:3],achieved_translation=achieved[:3,3],target_x=x,reference_world=reference,triangles=triangles);print('HOST_CANDIDATE_PASS',report['elapsed_wall_s'],flush=True)
except BaseException:
 (out/'failure.json').write_text(json.dumps(dict(traceback=traceback.format_exc(),scope='Incomplete host planning only; no native/physical gate attempted.',source_sha256=pins),indent=2)+'\n');raise
