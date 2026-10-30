"""Offline terminal supports with knife axial roll; never changes a scene or plan."""
import json
import time
import numpy as np
from scipy.spatial.transform import Rotation
from multipoint_load_audit import ROOT,LoadScene,FINGERS
from refine_load_support import geometry_screen
from offline_grasp_audit import full_robot_self_check
from reach_kinematics import PALM_OFFSET


def load_layout(points,normal_forces,scene,q):
    centre=(scene.handle.min(0)+scene.handle.max(0))/2;axes=np.linalg.svd(scene.handle-centre,full_matrices=False)[2][1:]
    loaded=[];fingers=set();inner=set();thumb=[];fv=[];palm=False
    for p,n in zip(points,normal_forces):
        if n<.05:continue
        part=p['part'];v=axes@(np.array(p['point'])-centre)
        if np.linalg.norm(v)<1e-8:continue
        v/=np.linalg.norm(v);loaded.append(v)
        if part=='palm':palm=True
        elif part=='thumb':thumb.append(v)
        elif part in FINGERS and 1.89*q[2+FINGERS.index(part)]>=np.deg2rad(115):
            fingers.add(part);fv.append(v)
            if p['inner']:inner.add(part)
    angles=sorted(float(np.arctan2(v[1],v[0])%(2*np.pi)) for v in loaded)
    gap=float(max(np.diff(angles+[angles[0]+2*np.pi]))) if angles else 2*np.pi
    opposed=any(a@b<-.5 for a in thumb for b in fv)
    return {'palm':palm,'fingers':sorted(fingers),'inner_fingers':sorted(inner),'opposed':bool(opposed),'enclosed':gap<=np.pi+.05,
            'geometric_wrap_under_hypothetical_load':bool(palm and opposed and gap<=np.pi+.05 and len(fingers)>=3 and len(inner)>=2),
            'scope':'Loaded points from an offline LP, not measured simulator contacts or a positive oracle example'}


def main():
    start=time.monotonic();folder=ROOT/'runs/offline/load_support_01';scene=LoadScene()
    source=json.loads((ROOT/'runs/offline/grasp_refinement_01/polished_candidates.json').read_text());base=source['candidates'][1]
    oldpose=np.array(source['reference_knife_pose_xyzw']);oldr=Rotation.from_quat(oldpose[3:]).as_matrix();hc=(scene.handle.min(0)+scene.handle.max(0))/2
    centre_world=oldr@hc+oldpose[:3];out=[]
    # Keep the less-intersecting original proposal. Axial roll preserves the
    # blade's long-axis outward direction. It does NOT satisfy the current
    # separate 20-degree in-place diagnostic bound and is never activated here.
    for angle in [60.,75.,90.]:
        kr=oldr@Rotation.from_euler('x',angle,degrees=True).as_matrix();pose=np.r_[centre_world-kr@hc,Rotation.from_matrix(kr).as_quat()]
        c={'source_proposal':'B','knife_axial_roll_change_deg':angle,'target_fingers':base['target_fingers'],
           'joint_rad':base['joint_rad'],'hand_rotation_in_knife':base['hand_rotation_in_knife'],'hand_root_in_knife_m':base['hand_root_in_knife_m']}
        # A mathematical terminal pose is raised to clear the entire knife and
        # hand, not just the handle. No reset/trajectory is executed.
        g=geometry_screen(scene,c,kr,pose)
        from pxr import UsdGeom
        meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());board=meta['board_world_bounds'][1][2]
        kv=np.array(UsdGeom.Mesh(scene.stage.GetPrimAtPath(meta['knife_path'])).GetPointsAttr().Get())
        knife_min=float((kv@kr.T+pose[:3])[:,2].min())
        rise=max(.05,.005-g['board_plane_clearance_m'],board+.005-knife_min)
        pose[2]+=rise
        r=np.array(c['hand_rotation_in_knife']);t=np.array(c['hand_root_in_knife_m'])
        arm,pe,re=scene.model.kin.solve(pose[:3]+kr@(t+r@PALM_OFFSET),kr@r,np.array(base['arm_ik']['q_rad']))
        c['arm_ik']={'q_rad':arm.tolist(),'position_error_m':pe,'rotation_error_rad':re}
        g=geometry_screen(scene,c,kr,pose,details=True);c['exact_contact_geometry']=g['contacts']
        points=scene.contacts(c,kr,max_gap=.001);nominal=scene.solve(points,c,kr);margin=scene.solve(points,c,kr,scale=1.25)
        c.update(knife_pose_xyzw=pose.tolist(),mathematical_terminal_rise_m=rise,geometry=g,surface_points=points,
                 nominal=nominal,margin=margin,full_robot_self_envelopes=full_robot_self_check(scene.stage,scene.model,arm,np.array(c['joint_rad'])),
                 loaded_geometry=load_layout(points,margin['normal_force_per_point_n'],scene,np.array(c['joint_rad'])) if margin['feasible'] else None,
                 active=False,physical_grasp_success=False,route_from_flat_start_validated=False,
                 within_existing_20_degree_in_place_diagnostic_bound=False)
        out.append(c)
        print(json.dumps({'roll':angle,'nominal':nominal['feasible'],'margin':margin['feasible'],'arm_error_m':pe,'rise_m':rise,'loaded_geometry':c['loaded_geometry']}),flush=True)
    (folder/'oriented_support_candidates.json').write_text(json.dumps({'scope':'Inactive mathematical terminal proposals only; old motion bound not changed or bypassed',
        'wall_s':time.monotonic()-start,'candidates':out},indent=2,allow_nan=False))


if __name__=='__main__':main()
