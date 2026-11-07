from pathlib import Path
import sys,json,numpy as np,fcl
from pxr import Usd,UsdGeom
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'scripts'));from reach_kinematics import ArmKinematics
plan=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());stage=Usd.Stage.Open(plan['scene']);kin=ArmKinematics(stage);xc=UsdGeom.XformCache();shapes=json.loads((w/'wrist_collision_shapes.json').read_text());models={}
for row in shapes:
 prim=stage.GetPrimAtPath(row['path']);m=UsdGeom.Mesh(prim);counts=np.array(m.GetFaceVertexCountsAttr().Get());assert np.all(counts==3)
 v=np.array(m.GetPointsAttr().Get(),float);faces=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);T=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(stage.GetPrimAtPath(row['owner']))).T)@np.array(xc.GetLocalToWorldTransform(prim)).T;v=v@T[:3,:3].T+T[:3,3]
 model=fcl.BVHModel();model.beginModel(len(v),len(faces));model.addSubModel(v,faces);model.endModel();models[row['owner']]=model

def evaluate(transforms,label):
 objs=[fcl.CollisionObject(model,fcl.Transform(transforms[path][:3,:3],transforms[path][:3,3]))for path,model in models.items()];res=fcl.CollisionResult();count=fcl.collide(*objs,fcl.CollisionRequest(num_max_contacts=20,enable_contact=True),res);dist=fcl.distance(*objs,fcl.DistanceRequest(enable_nearest_points=True),fcl.DistanceResult());return dict(label=label,intersections=count,minimum_distance_m=float(dist),contacts=[dict(depth=float(c.penetration_depth),point=c.pos.tolist())for c in res.contacts])
rows=[];route=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());cut=[x for x in route['rows']if x['phase']=='cut']
for i in [0,100,180,len(cut)-1]:rows.append(evaluate(kin.transforms(cut[i]['q']),f'cut_waypoint_{i}'))
source=w/'collision_state01/collision_state.json'
if source.exists():
 a=json.loads(source.read_text());transforms={}
 for path in models:
  pose=np.array(a['body_poses'][a['body_names'].index(path.rsplit('/',1)[-1])]);T=np.eye(4);T[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();T[:3,3]=pose[:3];transforms[path]=T
 rows.append(evaluate(transforms,'actual_first_native_contact'))
(w/'wrist_original_mesh_check.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
