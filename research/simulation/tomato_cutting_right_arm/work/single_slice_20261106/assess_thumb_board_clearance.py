"""Read-only geometry assessment of the recorded native thumb-board stop."""
from pathlib import Path
import json,numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];out=w/'fitted_motion_check01';state=json.loads((out/'collision_state.json').read_text());plan=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());stage=Usd.Stage.Open(plan['scene']);cache=UsdGeom.XformCache();path=json.loads((out/'collision_pairs.json').read_text())[0][0];prim=stage.GetPrimAtPath(path);root=np.array(cache.GetLocalToWorldTransform(prim)).T;pose=np.array(state['body_poses'][state['body_names'].index('right_rh_thumb_distal')]);R=Rotation.from_quat(pose[3:]).as_matrix();points=[]
for child in Usd.PrimRange(prim,Usd.TraverseInstanceProxies()):
 if child.IsA(UsdGeom.Mesh):
  raw=np.asarray(UsdGeom.Mesh(child).GetPointsAttr().Get());T=np.linalg.inv(root)@np.array(cache.GetLocalToWorldTransform(child)).T;points.append((raw@T[:3,:3].T+T[:3,3])@R.T+pose[:3])
if not points:raise ValueError('No thumb mesh found')
p=np.concatenate(points);route=json.loads((w/'fitted_continuation_plan_v2.json').read_text());F=np.array(route['target_rotation']);placement=np.array(route['target_translation']);z=np.load(w/'robot_cut13/checkpoints/step_005375.npz');target=(z['x']+[-.0225,0,.0295])@F.T+placement;b=json.loads((w/'board_footprint_v02.json').read_text());half=np.array(b['halfspaces']);cases=[]
for shift in [.04,.06,.08]:
 delta=np.array([-shift,0]);h=half.copy();h[:,2]-=h[:,:2]@delta;cases.append(dict(additional_board_shift_x_m=-shift,all_target_inside=bool(np.max(target[:,:2]@h[:,:2].T+h[:,2])<=-.001),minimum_target_edge_margin_m=float(-np.max(target[:,:2]@h[:,:2].T+h[:,2])),board_right_edge_m=b['world_max'][0]-shift,thumb_mesh_left_edge_m=float(p[:,0].min()),horizontal_clearance_m=float(p[:,0].min()-(b['world_max'][0]-shift))))
result=dict(scope='Recorded thumb CAD and frozen target only; requires future native check and relaxed-target footprint check',thumb_min=p.min(0).tolist(),thumb_max=p.max(0).tolist(),cases=cases);(w/'thumb_board_clearance_assessment.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
