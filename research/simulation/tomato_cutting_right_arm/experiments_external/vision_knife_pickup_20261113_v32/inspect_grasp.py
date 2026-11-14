from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pxr import Usd,UsdGeom
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
from plan_contact_seating import HandGeometry
s=Usd.Stage.Open(str(W/'head_vision_pickup_v02.usda'));m=HandGeometry(s);x=json.loads((W/'runs/pickup01/before_lift.json').read_text());q=np.array(x['q'])[[19,29,20,21,22,23]];tp=np.array(x['knife_pose']);hp=np.array(x['hand_pose']);kr=Rotation.from_quat(tp[3:]).as_matrix();hr=Rotation.from_quat(hp[3:]).as_matrix();trans=m.transforms(q);fig,axes=plt.subplots(1,3,figsize=(18,6));axesplanes=[(0,1),(0,2),(1,2)];colors={'thumb':'tab:orange','index':'tab:green','middle':'tab:purple','ring':'tab:pink','pinky':'tab:cyan','hand':'gray'}
for name,(vertices,eq) in m.meshes.items():
 t=trans[name];v=vertices@t[:3,:3].T+t[:3,3];v=((v@hr.T+hp[:3])-tp[:3])@kr;part=name.removeprefix('right_rh_').split('_')[0]
 print(name,'center',v.mean(0),'zmin-world', (vertices@t[:3,:3].T+t[:3,3])@hr.T[:,2]+hp[2] if False else (v@kr.T+tp[:3])[:,2].min())
 for ax,(i,j) in zip(axes,axesplanes):ax.scatter(v[:,i],v[:,j],s=3,c=colors.get(part,'black'),alpha=.5,label=part)
for kind in ['CollisionHandle','CollisionBlade']:
 v=np.array(UsdGeom.Mesh(s.GetPrimAtPath('/dual_ar5_o6/MountedKnife/'+kind)).GetPointsAttr().Get())
 for ax,(i,j) in zip(axes,axesplanes):ax.scatter(v[:,i],v[:,j],s=1,c='brown' if kind.endswith('Handle') else 'blue',alpha=.4)
for ax,(i,j) in zip(axes,axesplanes):ax.set_aspect('equal');ax.set_xlabel('xyz'[i]);ax.set_ylabel('xyz'[j]);ax.set_xlim(-.22,.06);handles,labels=ax.get_legend_handles_labels();d=dict(zip(labels,handles));ax.legend(d.values(),d.keys());ax.grid()
fig.savefig(W/'reports/pickup01_geometry.png',dpi=130)
