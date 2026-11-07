from pathlib import Path
import ast,json,hashlib,re
import numpy as np
from scipy.spatial.transform import Rotation
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');run=R/'runs/native/live_clear_assembly_20261102_01';out=R/'work/live_clear_assembly_20261102/independent_readback01';out.mkdir(exist_ok=False)
m=json.loads((run/'measurements.json').read_text());s=json.loads((run/'supervisor_result.json').read_text());manifest=json.loads((run/'input_manifest.json').read_text());rows=[json.loads(x)for x in(run/'assembly_trace.jsonl').read_text().splitlines()];robots=json.loads((run/'robot_trace.json').read_text());z=np.load(run/'live_target_trace.npz');x=z['x_world'];v=z['velocity'];shown=z['display_points'];initial=z['initial_x_world'];reference=z['reference_x_world'];fixed=z['fixed'];mass=z['mass'];cells=z['cells'];volumes=z['volumes'];blade=z['blade_vertices'];poses=z['held_tool_poses'];design=json.loads((R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());protocol=json.loads((R/'work/nonfracturing_contact_plan_20261102/contact_test_contract.json').read_text())
assert s['passed']and not s['remaining_live_group_members']and len(rows)==240 and len(robots)==24 and x.shape==(240,4032,3)and v.shape==x.shape and shown.shape==x.shape
assert np.array_equal(z['triangles'],np.array([t for p in design['pieces']for t in p['triangles']]))
assert len(fixed)==25 and not any(design['nodes'][int(i)]['side']=='slice'for i in fixed)
assert np.array_equal(x[:,fixed],np.broadcast_to(reference[fixed],x[:,fixed].shape))
assert np.isfinite(x).all()and np.isfinite(v).all()
max_display=float(abs(shown-x).max());assert np.array_equal(shown,x.astype(np.float32).astype(float))and max_display<=1e-7
minimum_gap=float('inf');minimum_vertical=float('inf');minimumJ=float('inf');max_penetration=0.;max_linear=max_angular=0.;max_energy=0.
initial_energy=rows[0]['target_audit']['energy']['total_j']
for i,row in enumerate(rows):
 assert row['target_step']==i+1 and abs(row['target_time_s']-(i+1)/2400)<1e-15 and abs(row['robot_completed_time_s']-(i//10)/240)<1e-15
 assert row['generated_blade_contact_count']==0 and not np.any(row['returned_tool_wrench'])
 rot=Rotation.from_quat(poses[i,3:]).as_matrix();vertices=blade@rot.T+poses[i,:3];gap=float(np.maximum(x[i].min(0)-vertices.max(0),vertices.min(0)-x[i].max(0)).max());vertical=float(vertices[:,2].min()-x[i,:,2].max());assert abs(gap-row['CAD_convex_bound_gap_m'])<1e-12 and gap>.015
 ratios=np.linalg.det(x[i][cells[:,1:]]-x[i][cells[:,:1]])/(6*volumes);assert abs(ratios.min()-row['minimum_volume_ratio'])<1e-10 and ratios.min()>.1
 pen=float(max(0.,-x[i,:,2].min()));assert abs(pen-row['board_penetration_m'])<1e-12 and pen<=.0001
 audit=row['target_audit'];p=(mass[:,None]*v[i]).sum(0);L=np.cross(x[i],mass[:,None]*v[i]).sum(0);external=np.array(audit['gravity_board_fixture_impulse_ns']).sum(0);external_L=np.array(audit['gravity_board_fixture_angular_impulse_nms']).sum(0);lin=float(np.linalg.norm(p-external));ang=float(np.linalg.norm(L-external_L));assert abs(lin-audit['linear_impulse_residual_ns'])<1e-12 and abs(ang-audit['angular_impulse_residual_nms'])<1e-12
 assert audit['cumulative_absolute_nodal_impulse_residual_ns']<=1e-4 and lin<=1e-4 and ang<=1e-5
 minimum_gap=min(minimum_gap,gap);minimum_vertical=min(minimum_vertical,vertical);minimumJ=min(minimumJ,float(ratios.min()));max_penetration=max(max_penetration,pen);max_linear=max(max_linear,lin);max_angular=max(max_angular,ang);max_energy=max(max_energy,row['energy_increase_j'])
for i,row in enumerate(robots):
 assert row['robot_step']==i+1 and row['matched_target_steps']==(i+1)*10
 assert abs(row['matched_robot_time_s']-row['matched_target_time_s'])<1e-15
 assert row['maximum_rigid_contact_force_n']<=.1 and row['right_tracking_error_rad']<.03 and row['mount_position_error_m']<2e-5 and row['mount_angle_error_rad']<2e-4
 xx=x[(i+1)*10-1];pose=np.array(row['tool_pose']);verts=blade@Rotation.from_quat(pose[3:]).as_matrix().T+pose[:3];gap=float(np.maximum(xx.min(0)-verts.max(0),verts.min(0)-xx.max(0)).max());assert abs(gap-row['post_robot_CAD_gap_m'])<1e-12 and gap>.015;minimum_gap=min(minimum_gap,gap);minimum_vertical=min(minimum_vertical,float(verts[:,2].min()-xx[:,2].max()))
# Read the exported USD ASCII independently, without importing a native SDK.
scene=(run/'live_clear_inspection_scene.usda').read_text();section=scene.split('def Mesh "LiveNewtonTomato"',1)[1];match=re.search(r'point3f\[\] points = (\[.*?\])',section,re.S);assert match
exported=np.array(ast.literal_eval(match.group(1)),float);export_error=float(abs(exported-x[-1]).max());assert export_error<1e-7
assert re.search(r'over "CuttingTargetVisual"\s*\(\s*active = false',scene)
closure=json.loads((run/'source_closure.json').read_text())['source_sha256'];changed=[p for p,h in closure.items()if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not changed
actual_state_change=float(abs(x-initial).max());forces=np.array(rows[-1]['target_audit']['gravity_board_fixture_force_n']);checks=dict(counts_and_matched_clocks=True,all_state_geometry_and_fixed_freecap_checks=True,all_display_points_actual_float32_nodes=True,exported_scene_points_match=True,old_static_visual_hidden=True,all_interval_positive_CAD_bound_clearance=True,raw_target_momentum_ledger_matches=True,original_impulse_volume_board_gates=True,source_closure_preserved=True)
report=dict(passed=all(checks.values()),checks=checks,target_steps=240,matched_physx_steps=24,setup_physx_steps=3,total_physx_steps=27,duration_s=.1,minimum_CAD_bound_gap_m=minimum_gap,minimum_vertical_blade_target_gap_m=minimum_vertical,maximum_display_error_m=max_display,maximum_exported_scene_error_m=export_error,maximum_actual_target_motion_m=actual_state_change,minimum_volume_ratio=minimumJ,maximum_board_penetration_m=max_penetration,maximum_linear_impulse_residual_ns=max_linear,maximum_angular_impulse_residual_nms=max_angular,maximum_energy_increase_j=max_energy,final_gravity_board_fixture_force_n=forces.tolist(),verified_source_files=len(closure),scope='Live clear assembly hold at explicitly initialized standoff. Supported equilibrium has no measurable state motion; displayed state equality is verified, not visual deformation under load. Positive AABB separation using actual CAD vertices excludes all triangle contact. No populated force adapter, touch, robot energy qualification, replay, cutting or training.',source_sha256={str(run/p):hashlib.sha256((run/p).read_bytes()).hexdigest()for p in ['measurements.json','input_manifest.json','supervisor_result.json','assembly_trace.jsonl','robot_trace.json','live_target_trace.npz','live_clear_inspection_scene.usda','source_closure.json']});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
