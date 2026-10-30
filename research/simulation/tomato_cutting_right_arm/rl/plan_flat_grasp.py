"""Offline original-mesh screen for a board-clear initial grasp. No simulator or training."""
import itertools
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd, UsdGeom

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from search_wrap_grasp import geometry
from reach_kinematics import ArmKinematics,PALM_OFFSET
from reset_sampler import FlatResetSampler

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seated',action='store_true')
    parser.add_argument('--pad-aware',action='store_true')
    args=parser.parse_args()
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3.usda'))
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
    points=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path'])).GetPointsAttr().Get())
    hv=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get())
    hc=(hv.min(0)+hv.max(0))/2
    hv=hv[ConvexHull(hv).vertices]-hc
    lo,hi=np.array(meta['board_world_bounds']);sampler=FlatResetSampler(points,[lo,hi])
    centre=(lo[:2]+hi[:2])/2
    # Keep the entire knife on the board, starting flat at its centre.
    case=sampler.at(centre,np.deg2rad(67.5 if args.seated or args.pad_aware else 112.5));assert case['valid']
    kr=Rotation.from_quat(case['pose_xyzw'][3:]).as_matrix()
    handle=kr@hc+np.array(case['pose_xyzw'][:3]);handle[2]-=.003
    ys=[-.035,-.02,0.,.015] if args.seated or args.pad_aware else [.015,.03,.045]
    grid=np.array(list(itertools.product(np.arange(.015,.066,.005),ys,np.arange(.065,.136,.005))))
    candidates=[]
    choices=([180,220,240,260,270],[25,40,55,70],[10,25]) if args.pad_aware else ([180,200,220,240,260,270],[35,55,70,85],[15,30])
    for roll,finger,pitch in itertools.product(*choices):
        a=np.deg2rad(roll)
        hand_in_knife=np.array([[0.,-1.,0.],[np.cos(a),0.,-np.sin(a)],[np.sin(a),0.,np.cos(a)]])
        kv=hv@hand_in_knife
        thumb_yaw=50 if args.pad_aware else 60
        meshes=geometry(finger,thumb_yaw,pitch)
        moved=dict(geometry(finger+2,thumb_yaw,pitch+2)) if args.pad_aware else {}
        gaps=[];normals=[];heights=[];names=[];closing_velocities=[]
        for name,v in meshes:
            hull=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3))
            eq=hull.equations;dd=grid@eq[:,:3].T+eq[:,3];index=dd.argmax(1)
            gaps.append(dd[np.arange(len(grid)),index]);normals.append(eq[index,:3]);names.append(name)
            if args.pad_aware:
                ns=eq[index,:3];vertex=(ns@v.T).argmax(1)
                closing_velocities.append(np.sum(ns*(moved[name]-v)[vertex],axis=1))
            heights.append((v@hand_in_knife[2]).min()-grid@hand_in_knife[2]+handle[2]-hi[2])
        gaps=np.array(gaps);normals=np.array(normals);heights=np.array(heights)
        ix=lambda n:names.index('right_rh_'+n)
        fg=np.array([gaps[ix(f+'_distal')] for f in ['index','middle','ring','pinky']])
        thumb=gaps[ix('thumb_distal')];palm=gaps[ix('hand_base_link')]
        opposition=np.min(np.array([np.sum(normals[ix('thumb_distal')]*normals[ix(f+'_distal')],axis=1) for f in ['index','middle','ring','pinky']]),axis=0)
        # Predict shallow contact, opposed normals, and no initial board penetration.
        cost=(np.sort(np.abs(fg-.0015),axis=0)[:3]**2).sum(0)*1e5+(thumb-.0015)**2*1e5
        cost+=np.maximum(-.0005-gaps,0).sum(0)*2e4
        cost+=np.maximum(.001-heights.min(0),0)*2e4
        cost+=np.maximum(opposition+.4,0)*50
        cost+=np.maximum(palm-.012,0)**2*1e4
        if args.pad_aware:
            # Closing must move the contact surface TOWARDS the handle, rather than touch its back.
            velocities=np.array(closing_velocities)
            choices_f=[];choices_n=[]
            for f in ['index','middle','ring','pinky']:
                indices=[ix(f+'_proximal'),ix(f+'_distal')]
                gs=np.array([np.where(velocities[i]>.00005,np.abs(gaps[i]-.0015),1.) for i in indices])
                choose=gs.argmin(0);choices_f.append(gs.min(0));choices_n.append(normals[np.array(indices)[choose],np.arange(len(grid))])
            errors=np.array(choices_f);which=errors.argmin(0)
            opposing=np.sum(normals[ix('thumb_distal')]*np.array(choices_n)[which,np.arange(len(grid))],axis=1)
            cost=errors.min(0)**2*1e5+np.sort(errors,axis=0)[1]**2*2e4+(thumb-.0015)**2*1e5
            cost+=np.maximum(-.0005-gaps,0).sum(0)*2e4
            cost+=np.where(heights.min(0)<.001,1e6,0.)
            cost+=np.where(velocities[ix('thumb_distal')]>.00005,0.,1e5)
            cost+=np.maximum(opposing+.5,0)*1e3
            opposition=opposing
        j=cost.argmin()
        candidates.append({'cost':float(cost[j]),'roll_deg':roll,'finger_deg':finger,'thumb_pitch_deg':pitch,'thumb_yaw_deg':thumb_yaw,
            'handle_in_hand_m':grid[j].tolist(),'hand_rotation_world':(kr@hand_in_knife).tolist(),
            'minimum_hand_board_gap_m':float(heights[:,j].min()),'gaps_m':dict(zip(names,gaps[:,j].tolist())),
            'opposed_normal_cosine':float(opposition[j])})
        if args.pad_aware:
            candidates[-1]['closing_surface_motion_m_per_2deg']=dict(zip(names,velocities[:,j].tolist()))
            candidates[-1]['predicted_pad_error_m']=float(errors[:,j].min())
    candidates.sort(key=lambda x:x['cost'])
    kin=ArmKinematics(stage);home=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())['home_rad']
    seed=np.array([home[n] for n in kin.names])
    for c in candidates[:12]:
        rotation=np.array(c['hand_rotation_world']);target=handle-rotation@(np.array(c['handle_in_hand_m'])-PALM_OFFSET)
        q,error,angle=kin.solve(target,rotation,seed)
        c.update(palm_world_m=target.tolist(),q_rad=q.tolist(),ik_position_error_m=error,ik_angle_error_rad=angle)
    report={'reset':case,'handle_world_m':handle.tolist(),'candidates':candidates,
            'scope':'Offline conservative convex screen, not physical grasp validation; no knife is moved in an episode'}
    output='flat_grasp_pad_aware.json' if args.pad_aware else 'flat_grasp_seated.json' if args.seated else 'flat_grasp_geometry.json'
    (ROOT/'docs/rl'/output).write_text(json.dumps(report,indent=2))
    print(json.dumps(report['candidates'][:3],indent=2))

if __name__=='__main__':main()
