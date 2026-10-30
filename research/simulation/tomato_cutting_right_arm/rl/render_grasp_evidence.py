"""Offline mesh reconstruction of recorded physics states, explicitly not a camera image."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from pxr import Usd,UsdGeom,UsdPhysics
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics

p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args()
run=a.run.resolve();records=json.loads((run/'trajectory.json').read_text())
cfg=json.loads((run/'run_configuration.json').read_text());meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));k=ArmKinematics(stage);xc=UsdGeom.XformCache()
cache=[]
for prim in stage.Traverse():
    if not prim.IsA(UsdGeom.Mesh):continue
    path=str(prim.GetPath());name=prim.GetName()
    if '/Collision' in path or 'left_' in path:continue
    kind=None
    if path==meta['board_path']:kind='board'
    elif path==meta['knife_path']:kind='knife'
    elif '/right_rh_' in path:kind='hand'
    if kind is None:continue
    mesh=UsdGeom.Mesh(prim);v=np.array(mesh.GetPointsAttr().Get());ids=np.array(mesh.GetFaceVertexIndicesAttr().Get());counts=np.array(mesh.GetFaceVertexCountsAttr().Get());offset=np.r_[0,np.cumsum(counts)]
    triangles=[]
    for i,c in enumerate(counts):
        ix=ids[offset[i]:offset[i+1]]
        for j in range(1,c-1):triangles.append([ix[0],ix[j],ix[j+1]])
    triangles=np.asarray(triangles)[::max(1,len(triangles)//2500)]
    if kind=='hand':triangles=ConvexHull(v).simplices
    world=np.array(xc.GetLocalToWorldTransform(prim)).T
    body=prim
    while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
    rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@world if body and kind=='hand' else world
    cache.append((kind,str(body.GetPath()) if body else None,v,triangles,rel))

initial=records[min(29,len(records)-1)]
grip=next((x for x in reversed(records) if x['phase'] in ['thumb_contact_feedback','fingers_then_thumb']),records[-1])
final=records[-1]
fig=plt.figure(figsize=(14,5));centre=np.mean(meta['board_world_bounds'],axis=0)
for index,(title,sample) in enumerate(zip(['Flat central reset','Contact before lifting','Last recorded state'],[initial,grip,final])):
    ax=fig.add_subplot(1,3,index+1,projection='3d',computed_zorder=False)
    values=dict(zip(json.loads((ROOT/'docs/rl/phase1_inventory.json').read_text())['right_arm_independent']+
                         json.loads((ROOT/'docs/rl/phase1_inventory.json').read_text())['right_hand_independent'],sample['q_rad']))
    for finger in ['index','middle','ring','pinky']:values['right_rh_'+finger+'_dip']=.89*values['right_rh_'+finger+'_mcp_pitch']
    values['right_rh_thumb_ip']=1.86*values['right_rh_thumb_cmc_pitch']
    transforms={'/dual_ar5_o6':k.root}
    def tr(path):
        if path in transforms:return transforms[path]
        parent,child,before,after,axis,name=k.by_child[path];rot=np.eye(4)
        if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0.)).as_matrix()
        transforms[path]=tr(parent)@before@rot@after
        return transforms[path]
    for kind,body,vertices,faces,mat in cache:
        if kind=='hand':m=tr(body)@mat
        elif kind=='knife':
            pose=np.array(sample['knife_pose_xyzw']);m=np.eye(4);m[:3,:3]=Rotation.from_quat(pose[3:]).as_matrix();m[:3,3]=pose[:3]
        else:m=mat
        v=vertices@m[:3,:3].T+m[:3,3]
        color={'hand':'#7d8792','knife':'#454b50','board':'#c68d50'}[kind]
        ax.add_collection3d(Poly3DCollection(v[faces],facecolor=color,edgecolor='none',alpha=1.,zorder={'board':1,'knife':2,'hand':3}[kind]))
    for c in sample['contacts']:
        if 'point_world_m' in c:
            pt=c['point_world_m'];ax.scatter(*pt,color='#d52525',s=18,depthshade=False,zorder=4)
    ax.set_xlim(centre[0]-.25,centre[0]+.25);ax.set_ylim(centre[1]-.28,centre[1]+.28);ax.set_zlim(.83,1.18)
    ax.set_box_aspect((1,1.12,.7));ax.view_init(28,35);ax.set_axis_off()
    lift=(sample['handle_height_m']-records[29]['handle_height_m'])*1000
    ax.set_title(f"{title}\nHandle change {lift:.1f} mm | board/counter support {sample['support_force_n']:.2f} N",fontsize=10)
fig.suptitle('Recorded states with convex hand meshes — not camera images',fontsize=12,y=.98)
fig.tight_layout(rect=(0,0,1,.88));fig.savefig(run/'physics_evidence.png',dpi=150);plt.close(fig)
print(run/'physics_evidence.png')
