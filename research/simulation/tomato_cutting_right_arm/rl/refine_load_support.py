"""Bounded offline contact-layout search; no simulator, scene edits or training."""
import json
import time
import resource
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull
from multipoint_load_audit import ROOT,LoadScene
from reach_kinematics import PALM_OFFSET
from offline_grasp_audit import convex_distance,clip_inner,full_robot_self_check,overlap_radius


def geometry_screen(scene,c,kr,pose,details=False):
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());board=meta['board_world_bounds'][1][2]
    from pxr import UsdGeom
    blade=np.array(UsdGeom.Mesh(scene.stage.GetPrimAtPath(meta['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());bh=ConvexHull(blade)
    r=np.array(c['hand_rotation_in_knife']);t=np.array(c['hand_root_in_knife_m']);links=scene.model.transforms(c['joint_rad'])
    board_gap=100.;blade_gap=100.;contacts=[];intersections=[]
    for name,meshes in scene.geometry.items():
        v=meshes[0][0];h=ConvexHull(v);l=links[name];br=r@l[:3,:3];bp=t+r@l[:3,3];vv=v@br.T+bp
        board_gap=min(board_gap,float((vv@kr.T+pose[:3])[:,2].min()-board))
        gap=max(float(((blade-bp)@br@h.equations[:,:3].T+h.equations[:,3]).min(0).max()),float((vv@bh.equations[:,:3].T+bh.equations[:,3]).min(0).max()))
        blade_gap=min(blade_gap,gap)
        if details:
            dist=convex_distance(vv,scene.handle);iw=None
            if name.endswith('_proximal'):iw=dist
            elif name.endswith('_distal') and 'thumb' not in name:
                axis,end=scene.tips[name];inner=clip_inner(v,axis,end,.015)
                if inner is not None:iw=convex_distance(inner@br.T+bp,scene.handle)
            contacts.append({'body':name,'approximation':meshes[0][1],**dist,'inner_witness':iw,'inner_region_distance_m':None if iw is None else iw['distance_m']})
            rad=overlap_radius(vv,scene.handle)
            if rad>1e-6:intersections.append({'body':name,'inscribed_intersection_radius_m':rad})
    return {'board_plane_clearance_m':board_gap,'blade_clearance_lower_bound_m':blade_gap,'contacts':contacts,'handle_intersections':intersections}


def main():
    start=time.monotonic();deadline=start+150;folder=ROOT/'runs/offline/load_support_01';scene=LoadScene()
    source=json.loads((ROOT/'runs/offline/grasp_refinement_01/polished_candidates.json').read_text())
    pose=np.array(source['reference_knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
    centre=(scene.handle.min(0)+scene.handle.max(0))/2;trials=[];qualified=[]
    for seed_index,base in enumerate(source['candidates']):
        for yaw in [0.,np.pi]:
            for shift in [-.05,-.035,-.02,0.,.015]:
                if time.monotonic()>deadline:break
                rotation=Rotation.from_rotvec(np.array([0.,0.,yaw])).as_matrix()
                r=rotation@np.array(base['hand_rotation_in_knife'])
                t=centre+rotation@(np.array(base['hand_root_in_knife_m'])-centre)+np.array([shift,0,0])
                c={'seed_index':seed_index,'yaw_flip_rad':yaw,'axial_shift_m':shift,'target_fingers':base['target_fingers'],
                   'joint_rad':base['joint_rad'],'hand_rotation_in_knife':r.tolist(),'hand_root_in_knife_m':t.tolist()}
                geo=geometry_screen(scene,c,kr,pose)
                if geo['board_plane_clearance_m']<.002 or geo['blade_clearance_lower_bound_m']<.002:
                    trials.append({**c,'geometry':geo,'rejected':'support-plane/blade envelope clearance'});continue
                arm,pe,re=scene.model.kin.solve(pose[:3]+kr@(t+r@PALM_OFFSET),kr@r,np.array(base['arm_ik']['q_rad']))
                c['arm_ik']={'q_rad':arm.tolist(),'position_error_m':pe,'rotation_error_rad':re}
                if pe>.001 or re>.01:trials.append({**c,'rejected':'arm IK precision'});continue
                # Recompute witnesses for the new pose; never reuse old-pose
                # closest points as if they were current surface contacts.
                geo=geometry_screen(scene,c,kr,pose,details=True);c['exact_contact_geometry']=geo['contacts']
                points=scene.contacts(c,kr,max_gap=.001)
                if not points:trials.append({**c,'rejected':'no nearby surface points'});continue
                nominal=scene.solve(points,c,kr);margin=scene.solve(points,c,kr,scale=1.25)
                no_act=scene.solve(points,c,kr,scale=1.25,actuators=False)
                c.update(geometry=geo,surface_points=points,nominal=nominal,margin=margin,margin_without_actuators=no_act)
                trials.append(c)
                print(json.dumps({'seed':seed_index,'yaw':yaw,'shift':shift,'points':len(points),'nominal':nominal['feasible'],'margin':margin['feasible'],'no_act':no_act['feasible']}),flush=True)
                if margin['feasible']:qualified.append(c)
                (folder/'load_refinement_progress.json').write_text(json.dumps({'trials':trials},indent=2))
    out={'scope':'Rigid grip-layout sensitivities; <=1 mm hypothetical gaps; no contact or active plan changed',
         'search_budget_s':150,'wall_s':time.monotonic()-start,'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
         'reference_knife_pose_xyzw':pose.tolist(),'trials':trials,'conditional_margin_candidates':qualified,
         'physical_grasp_success':False,'simulator_launched':False}
    (folder/'load_refinement.json').write_text(json.dumps(out,indent=2,allow_nan=False))


if __name__=='__main__':main()
