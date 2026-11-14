"""Freeze larger, family/face-labelled development and untouched evaluation sets."""
from pathlib import Path
import json, sys
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Usd, UsdGeom

W=Path(__file__).resolve().parent
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
sys.path.insert(0,str(R/'scripts'))
from reach_kinematics import ArmKinematics, PALM_OFFSET
c=json.loads((W/'scene_config.json').read_text())
g=json.loads((W/'reports/pinch_geometry02.json').read_text())
cal=json.loads((W/'hybrid_calibration_v01.json').read_text())
H0=np.array(cal['nominal_hand_target_world'])
p0=np.array(json.loads((W/'runs/camera01/result.json').read_text())['knife_pose'])
local_pivot=np.array([-.0860033812,.0076461609,.001586524])
pivot=p0[:3]+Rotation.from_quat(p0[3:]).apply(local_pivot)
reset=np.array(c['knife_pose_xyzw'])
lo,hi=np.array(c['board_world_bounds'])
rng=np.random.default_rng(2026111407)
assets={'short':'knife_short_blade_v02.usda','wide':'compact_wide_handle_v01.usda',
        'medium':'medium_original_handle_v01.usda'}
kin=None;rows=[]
for family,asset in assets.items():
    stage=Usd.Stage.Open(str(W/asset))
    if kin is None:kin=ArmKinematics(stage)
    points=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(c['knife_path'])).GetPointsAttr().Get())
    for face in [0,180]:
        counts=[('train',32)]
        for split,n in counts:
            accepted=0
            for attempt in range(400):
                if accepted==n:break
                dx,dy,yaw=float(rng.uniform(-.065,.065)),float(rng.uniform(-.09,0.)),float(rng.uniform(-25,25))
                Q=Rotation.from_euler('z',yaw,degrees=True).as_matrix()
                shift=pivot-Q@pivot+np.array([dx,dy,0.])
                M=Q@Rotation.from_quat(reset[3:]).as_matrix()
                pos=Q@reset[:3]+shift
                oldpivot=pos+M@local_pivot
                M=M@Rotation.from_euler('x',face,degrees=True).as_matrix()
                pos=oldpivot-M@local_pivot
                v=points@M.T+pos
                margin=float(np.minimum(v[:,:2].min(0)-lo[:2],hi[:2]-v[:,:2].max(0)).min())
                if margin<.008:continue
                D=np.eye(4);D[:3,:3]=Q;D[:3,3]=shift
                H=D@H0
                # Check a modest longitudinal grasp adjustment too; this does not
                # certify the continuous path or physical pickup.
                offset={'short':0.,'wide':.018,'medium':-.008,'novel':-.006}[family]
                H[:3,3]+=Q@Rotation.from_quat(p0[3:]).as_matrix()[:,0]*offset
                seed=g['q'];errors=[]
                for z in [0.,.045,.12]:
                    seed,pe,re=kin.solve(H[:3,3]+[0,0,z]+H[:3,:3]@PALM_OFFSET,H[:3,:3],seed)
                    errors.append([pe,re])
                if max(x[0] for x in errors)>.0003 or max(x[1] for x in errors)>.003:continue
                rows.append(dict(id=f'extra_{split}_{family}_face{face}_{accepted:02d}',split=split,
                                 family=family,scene=str(W/asset),rest_roll_deg=face,dx=dx,dy=dy,
                                 yaw_deg=yaw,board_margin_m=margin,ik_errors=errors))
                accepted+=1
            assert accepted==n,(family,face,split,accepted)
dest=W/'extra_training_curriculum_v02.json';assert not dest.exists()
dest.write_text(json.dumps(dict(seed=2026111407,episodes=rows,
    scope='Four related knife geometry variants, two settled faces, larger bounded board region; not arbitrary knives or all possible poses.',
    partition='Novel narrower-handle family has no training or validation images. Test images and physics outcomes remain unseen until candidate freeze.',
    proposed_test_gate='At least 12/14 successful pickups; at least one success per family/face; zero blade/contact-load violations. Same physical criteria as v32.',
    geometric_screen='Full-tool footprint and endpoint IK only; continuous path/contact qualification still required.'),indent=2))
print({s:sum(x['split']==s for x in rows) for s in ['train','validation','test']})
