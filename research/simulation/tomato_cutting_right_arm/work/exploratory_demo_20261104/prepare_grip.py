from pathlib import Path
import sys,json
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;sys.path.insert(0,str(r/'scripts'))
import search_wrap_grasp as g
from pxr import Usd,UsdGeom
candidate=json.loads((r/'work/wrap_grasp_candidates.json').read_text())[0]
rot=g.old@Rotation.from_euler('y',candidate['tilt'],degrees=True).as_matrix();A=rot.T@g.km[:3,:3];A=A/np.linalg.norm(A,axis=0)
stage=Usd.Stage.Open(str(r/'rl/scene/phase3.usda'));meta=json.loads((r/'rl/scene/manifest.json').read_text());prim=stage.GetPrimAtPath(meta['knife_path']);points=np.array(UsdGeom.Mesh(prim).GetPointsAttr().Get());handle=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hc=(handle.min(0)+handle.max(0))/2;kv=(handle-hc)@A.T
meshes=g.geometry(candidate['finger'],candidate['yaw'],candidate['pitch']);eqs=[ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations for _,v in meshes];names=[n for n,_ in meshes]
def gaps(c):return np.array([np.max(e[:,:3]@c+e[:,3]) for e in eqs])
selected=[i for i,n in enumerate(names) if 'distal' in n or 'hand_base_link' in n]
def residual(c):
 d=gaps(c);return np.r_[np.maximum(.0003-d,0)*20,(d[selected]-.001),.1*(c-np.array(candidate['center_xyz']))]
res=least_squares(residual,candidate['center_xyz'],max_nfev=150);c=res.x;mount=np.eye(4);mount[:3,:3]=A;mount[:3,3]=c-A@hc
joints={'right_rh_thumb_cmc_yaw':np.deg2rad(candidate['yaw']),'right_rh_thumb_cmc_pitch':np.deg2rad(candidate['pitch']),'right_rh_thumb_ip':np.deg2rad(1.86*candidate['pitch'])}
for f in ['index','middle','ring','pinky']:joints['right_rh_'+f+'_mcp_pitch']=np.deg2rad(candidate['finger']);joints['right_rh_'+f+'_dip']=np.deg2rad(.89*candidate['finger'])
d={'mount_hand_from_knife':mount.tolist(),'hand_joint_rad':joints,'handle_in_hand_m':c.tolist(),'convex_handle_gaps_m':dict(zip(names,gaps(c).tolist())),'scope':'Offline proposed visible wrap with ideal fixed attachment; not friction grasp or native validation','fixed_attachment_disclosed':True};(w/'grip_candidate.json').write_text(json.dumps(d,indent=2)+'\n')
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
fig=plt.figure(figsize=(14,5));knife=points@A.T+mount[:3,3]
for i,(elev,az) in enumerate([(15,-70),(25,20),(85,-90)]):
 ax=fig.add_subplot(1,3,i+1,projection='3d');
 for n,v in meshes:ax.add_collection3d(Poly3DCollection(v[ConvexHull(v).simplices],facecolor='#93a4b6',edgecolor='none',alpha=.65))
 ax.add_collection3d(Poly3DCollection(knife[ConvexHull(knife).simplices],facecolor='#d7b16c',edgecolor='none',alpha=.9));lo=np.minimum(knife.min(0),np.vstack([v for _,v in meshes]).min(0));hi=np.maximum(knife.max(0),np.vstack([v for _,v in meshes]).max(0));mid=(lo+hi)/2;half=max(hi-lo)/2
 ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half));ax.view_init(elev,az);ax.set_box_aspect((1,1,1));ax.set_axis_off()
fig.suptitle('Proposed hand–knife placement — geometry preview, fixed attachment');fig.tight_layout();fig.savefig(w/'grip_preview.png',dpi=150);print(json.dumps(d,indent=2))
