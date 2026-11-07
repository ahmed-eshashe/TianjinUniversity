"""Host-only reachable approach planning using the measured robot joint graph."""
from pathlib import Path
import json,hashlib,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation,Slerp
from tomato_exported_robot import ExportedRobot
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=R/'runs/offline/near_approach_plan_20261102_01';out.mkdir(exist_ok=False);start=time.monotonic()
paths=[R/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json',R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json',R/'runs/offline/prepared_contact_candidate_20261102_03/measurements.json',R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz',R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json',R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json',R/'rl/tomato_exported_robot.py',Path(__file__)]
pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
protocol=dict(scope='New closer dry route only; no target contact, dynamic target, fracture or force/energy experiment.',waypoints='home -> aligned high above target -> stop with blade minimum z20mm above highest reference/prepared target point -> withdraw to high -> return home',orientation='Use existing host candidate orientation aligned to the prepared material plane; this does not qualify that candidate for contact.',samples_per_phase=120,substeps_per_sample=8,dt_s=1/240,route_duration_s=16.03333333333333,planned_stop_vertical_gap_m=.020,original_native_minimum_target_aabb_gap_m=.015,tracking_allowance_m=.001,planned_inflated_other_body_target_gap_m=.010,body_bound_inflation_m=.002,planned_board_height_m=.004,planned_fixture_aabb_gap_m=.010,planned_blade_other_body_aabb_gap_m=.010,ik_position_budget_m=.000002,ik_orientation_budget_rad=.00002,prospective_tracking_targets='Same prior dry-controller1mm max/0.25mm final/0.002rad orientation and left hold; inherited mount/board/contact/speed/joint limits unchanged.',stopping_rule='One planned route, one protected visible native run and independent readback. Retain any failure and stop before contact. No solver/controller sweep.',source_sha256=pins)
(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
try:
 base=json.loads(paths[0].read_text());robot=ExportedRobot(paths[1]);candidate=json.loads(paths[2].read_text());assert candidate['host_candidate_passed'];prepared=np.load(paths[3])['x'];design=json.loads(paths[4].read_text());reference=np.array([n['position_m']for n in design['nodes']])+[0,0,.002];target=np.concatenate([reference,prepared]);lo=target.min(0);hi=target.max(0);blade=np.array(json.loads(paths[5].read_text())['vertices']);home=np.array([base['home_rad'][n]for n in robot.names]);T0=robot.knife_pose(base['home_rad']);R0=T0[:3,:3];Rc=np.array(candidate['planned_knife_rotation']);tc=np.array(candidate['planned_knife_translation_world_m']);up=Rc@np.array(base['knife_rotation']).T@np.array([0,0,1.]);assert up[2]>.98
 bottom=float((blade@Rc.T+tc)[:,2].min());near=tc+(hi[2]+.020-bottom)/up[2]*up;high=near+(.080-.020)/up[2]*up
 positions=[T0[:3,3],high,near,high,T0[:3,3]];orientations=[R0,Rc,Rc,Rc,R0];qroute=[];records=[];seed=home
 for phase in range(4):
  rotation_path=Slerp([0.,1.],Rotation.from_matrix([orientations[phase],orientations[phase+1]]))
  for sample in range(121):
   if phase and sample==0:continue
   u=sample/120;blend=u*u*u*(10+u*(-15+6*u));position=(1-blend)*positions[phase]+blend*positions[phase+1];orientation=rotation_path([blend]).as_matrix()[0]
   if phase==0 and sample==0:q=home.copy();pe=ae=0.
   else:q,pe,ae=robot.solve_knife(position,orientation,seed)
   if pe>2e-6 or ae>2e-5:raise ValueError(('Unreachable approach waypoint',phase,sample,pe,ae))
   qroute.append(q.tolist());records.append(dict(phase=phase,index=sample,position=position.tolist(),rotation=orientation.tolist(),ik_position_m=pe,ik_angle_rad=ae));seed=q
  print('PLANNED_PHASE',phase,flush=True)
 # Exact return to original commanded home; record any difference as a planning error, not a reset.
 endpoint=robot.knife_pose(seed);home_error=float(np.linalg.norm(endpoint[:3,3]-T0[:3,3]));assert home_error<2e-6
 qroute[-1]=home.tolist()
 audit=json.loads((R/'runs/offline/robot_scene_20261101_01/scene_audit.json').read_text());flo,fhi=np.array(audit['fixture_bounds_m']);minimum=dict(target=float('inf'),board=float('inf'),fixture=float('inf'),other_body_target=float('inf'),blade_other_body=float('inf'),joint_margin=float('inf'));offending=[]
 # Screen the actual per-step linear joint interpolation, not only Cartesian endpoints.
 for i,q in enumerate(qroute):
  q=np.array(q);qprev=np.array(qroute[max(0,i-1)])
  for sub in range(8):
   actual=qprev+((sub+1)/8)*(q-qprev);pose=robot.knife_pose(actual);vertices=blade@pose[:3,:3].T+pose[:3,3];bl=vertices.min(0);bh=vertices.max(0);tg=float(np.maximum(lo-bh,bl-hi).max());board=float(bl[2]);fixture=float(np.maximum(flo-bh,bl-fhi).max());joint_margin=float(np.minimum(actual-robot.lower,robot.upper-actual).min());other=float('inf');bodygap=float('inf')
   for body in robot.body_boxes(actual):
    low=body['minimum_world'];highb=body['maximum_world']
    if body['name']!='MountedKnife':other=min(other,float(np.maximum(lo-(highb+.002),(low-.002)-hi).max()))
    if body['name']!='MountedKnife'and body['path']!=robot.hand:bodygap=min(bodygap,float(np.maximum(low-bh,bl-highb).max()))
   for k,v in [('target',tg),('board',board),('fixture',fixture),('other_body_target',other),('blade_other_body',bodygap),('joint_margin',joint_margin)]:minimum[k]=min(minimum[k],v)
   if tg<.019 or board<=.004 or fixture<=.010 or other<=.010 or bodygap<=.010 or joint_margin<=0:offending.append(dict(sample=i,substep=sub,target=tg,board=board,fixture=fixture,other=other,blade_other=bodygap,joint_margin=joint_margin))
 if offending:raise ValueError(('Planned dry-route clearance failed',offending[:4]))
 plan=dict(base);plan.update(right_joint_route_rad=qroute,samples=len(qroute),substeps_per_sample=8,original_substeps_per_sample=4,route_kind='near_target_dry_approach',route_labels=['reposition above target','approach to20mm vertical gap','withdraw','return'],planned_knife_pose_records=records,clearance_target_world_m=target.tolist(),clearance_target_definition='Union of original reference nodes at scene offset and saved prepared equilibrium nodes; neither is stepped during this dry test.',source_sha256={**base['source_sha256'],**pins,str(out/'protocol.json'):hashlib.sha256((out/'protocol.json').read_bytes()).hexdigest()})
 (out/'near_approach_plan.json').write_text(json.dumps(plan,indent=2)+'\n');report=dict(host_preflight_passed=True,samples=len(qroute),screened_joint_interpolation_states=len(qroute)*8,target_bounds_m=[lo.tolist(),hi.tolist()],minimum_planned_clearances_m=minimum,maximum_ik_position_error_m=max(x['ik_position_m']for x in records),maximum_ik_orientation_error_rad=max(x['ik_angle_rad']for x in records),stop_pose_world=robot.knife_pose(qroute[240]).tolist(),home_return_error_m=home_error,elapsed_wall_s=time.monotonic()-start,scope='Reachability and conservative authored-bounds screen at commanded physics-step configurations only. Native tracking/collisions and swept guarantees not inferred.',source_sha256=pins);(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
except BaseException:
 (out/'failure.json').write_text(json.dumps(dict(traceback=traceback.format_exc(),source_sha256=pins),indent=2)+'\n');raise
