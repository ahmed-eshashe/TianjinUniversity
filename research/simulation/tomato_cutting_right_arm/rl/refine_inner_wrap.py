"""Bounded offline search for inner-surface wrap proposals. No simulator imports."""
import itertools
import json
from pathlib import Path
import resource
import time

import numpy as np
from pxr import Usd, UsdGeom
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

from offline_grasp_audit import (ROOT, FINGERS, collider_inventory, convex_distance,
                                clip_inner, conditional_load_check, full_robot_self_check)
from plan_contact_seating import HandGeometry
from reach_kinematics import PALM_OFFSET


def inner_surface_points(vertices, depth):
    """Sample the real convex-hull exterior; never the artificial clipping face."""
    hull = ConvexHull(vertices); mean = vertices.mean(0)
    axis = np.linalg.svd(vertices - mean, full_matrices=False)[2][0]
    if abs((vertices @ axis).min()) > abs((vertices @ axis).max()): axis = -axis
    end = float((vertices @ axis).max()); bound = end - depth
    points = [v for v in vertices[hull.vertices] if v @ axis <= bound + 1e-12]
    for tri in vertices[hull.simplices]:
        polygon = []
        for a, b in zip(tri, np.roll(tri, -1, axis=0)):
            da, db = a @ axis - bound, b @ axis - bound
            if da <= 0: polygon.append(a)
            if (da < 0 < db) or (db < 0 < da): polygon.append(a + da / (da-db) * (b-a))
        if polygon:
            points.extend(polygon); points.append(np.mean(polygon, axis=0))
    if not points: raise ValueError('No inner exterior sample')
    return np.unique(np.round(points, 12), axis=0), axis, end


class SearchDeadline(Exception):
    pass


def main():
    start = time.monotonic(); deadline = start + 120.
    output = ROOT / 'runs/offline/grasp_refinement_01'
    stage = Usd.Stage.Open(str(ROOT / 'rl/scene/phase3_grasp.usda')); model = HandGeometry(stage)
    inventory, geometry = collider_inventory(stage, model)
    original = json.loads((ROOT / 'docs/rl/refined_supported_wrap.json').read_text())
    meta = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    frozen = json.loads((ROOT / 'docs/rl/phase3_grasp_criteria.json').read_text())['criteria']
    pose = np.array(original['supported_sample']['knife_pose_xyzw']); kr = Rotation.from_quat(pose[3:]).as_matrix()
    handle = np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get())
    blade = np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionBlade')).GetPointsAttr().Get())
    hh, bh = ConvexHull(handle), ConvexHull(blade)
    centre = (handle.min(0)+handle.max(0))/2
    cross = np.linalg.svd(handle-centre, full_matrices=False)[2][1:]
    hulls = {}; samples = {}
    for name, meshes in geometry.items():
        if len(meshes) != 1: raise ValueError('Search requires one collider per body; audit retains unions')
        v = meshes[0][0]; hull = ConvexHull(v)
        hulls[name] = (v[hull.vertices], hull.equations)
        if name.endswith('_distal') and 'thumb' not in name:
            samples[name] = inner_surface_points(v, frozen['inner_distance_m'])[0]
        else:
            samples[name] = np.r_[v[hull.vertices], v[hull.simplices].mean(1)]
    trials = []
    for seed_index, trio in [(0, ['index','middle','ring']), (2, ['index','middle','pinky']),
                              (0, ['index','middle','pinky']), (2, ['index','middle','ring'])]:
        if time.monotonic() >= deadline: break
        seed = original['candidates'][seed_index]
        r0 = kr.T @ np.array(seed['hand_rotation_world'])
        t0 = centre-r0 @ np.array(seed['handle_in_hand_m'])
        q0 = np.deg2rad([seed['thumb_yaw_deg'],seed['thumb_pitch_deg'],*[max(61,seed['finger_degrees'][f]) for f in FINGERS]])
        initial = np.r_[t0, [0.]*3, q0]
        lower = np.r_[t0-.025, [-.6]*3, [.2, .03], [frozen['minimum_curl_rad']/1.89]*4]
        upper = np.r_[t0+.025, [.6]*3, [.9, .315], [np.deg2rad(85)]*4]
        best = {'cost': float('inf'), 'x': initial.copy()}; evaluations = 0
        def state(x):
            r = Rotation.from_rotvec(x[3:6]).as_matrix() @ r0; t = x[:3]; links = model.transforms(x[6:])
            transformed = {}; gaps = {}; blade_gaps = []; board_gaps = []; penetration = []
            for name, (v, eq) in hulls.items():
                tr = links[name]; br = r @ tr[:3,:3]; bp = t+r @ tr[:3,3]
                vv = v @ br.T+bp; transformed[name] = (br,bp)
                def sat(other, oe):
                    ov = (other-bp) @ br
                    return max(float((ov @ eq[:,:3].T+eq[:,3]).min(0).max()),
                               float((vv @ oe[:,:3].T+oe[:,3]).min(0).max()))
                gaps[name] = sat(handle,hh.equations); blade_gaps.append(sat(blade,bh.equations))
                penetration.append(max(0.,-gaps[name]-.00015))
                board_gaps.append(float((vv @ kr.T+pose[:3])[:,2].min()-meta['board_world_bounds'][1][2]))
            return r,t,links,transformed,gaps,np.array(blade_gaps),np.array(board_gaps),np.array(penetration)
        def residual(x):
            nonlocal evaluations
            if time.monotonic() >= deadline: raise SearchDeadline()
            evaluations += 1
            r,t,links,tr,gaps,bg,bog,penetration = state(x)
            names = ['right_rh_hand_base_link','right_rh_thumb_distal',*['right_rh_'+f+'_distal' for f in trio]]
            contact_residual = []; radial = []
            for name in names:
                br,bp = tr[name]; vv = samples[name] @ br.T+bp
                signed = (vv @ hh.equations[:,:3].T+hh.equations[:,3]).max(1)
                i = np.argmin(abs(signed-.00015))
                contact_residual.append((signed[i]-.00015)*1000)
                rv = cross @ (vv[i]-centre); radial.append(rv/max(np.linalg.norm(rv),1e-8))
            thumb = radial[1]
            opposition = [max(0.,float(thumb @ v)+.60)*4 for v in radial[2:]]
            # Palm, opposition and eligible exterior contact are scored together.
            result = np.r_[contact_residual, opposition,
                           np.maximum(.002-bg,0)*3000, np.maximum(.002-bog,0)*3000,
                           penetration*5000, (x[:3]-t0)*2, x[3:6]*.02, (x[6:]-q0)*.01]
            cost = float(result @ result)
            if cost < best['cost']: best.update(cost=cost,x=x.copy())
            return result
        status = 'completed bounded local optimization'
        try:
            least_squares(residual, initial, bounds=(lower,upper), max_nfev=90,
                          ftol=1e-6,xtol=1e-7,gtol=1e-6,diff_step=1e-4)
        except SearchDeadline: status = 'search wall budget reached'
        x=best['x']; r,t,links,tr,g,bg,bog,pen=state(x)
        trial = {'seed_candidate':seed_index,'target_fingers':trio,'score':best['cost'],'evaluations':evaluations,
                 'status':status,'hand_root_in_knife_m':t.tolist(),'hand_rotation_in_knife':r.tolist(),
                 'joint_rad':x[6:].tolist(),'approximate_handle_gaps_m':g,
                 'approximate_min_blade_gap_m':float(bg.min()),'board_plane_clearance_m':float(bog.min())}
        trials.append(trial)
        print(json.dumps({k:trial[k] for k in ['seed_candidate','target_fingers','score','status','evaluations']}),flush=True)
        (output/'search_progress.json').write_text(json.dumps({'trials':trials,'training':False,'simulator_launched':False},indent=2))
    # Keep proposals separate from the active controller plan; exact screening
    # includes all mesh bodies and never declares physical success.
    selected=[]
    for trial in sorted(trials,key=lambda c:c['score'])[:2]:
        t=np.array(trial['hand_root_in_knife_m']);r=np.array(trial['hand_rotation_in_knife']);q=np.array(trial['joint_rad']);links=model.transforms(q)
        contacts=[]; inner=[]; near=[]
        for name,meshes in geometry.items():
            tr=links[name];br=r @ tr[:3,:3];bp=t+r @ tr[:3,3]
            for v,approx in meshes:
                dist=convex_distance(v @ br.T+bp,handle);iw=None
                if name.endswith('_distal') and 'thumb' not in name:
                    _,axis,end=inner_surface_points(v,frozen['inner_distance_m'])
                    clipped=clip_inner(v,axis,end,frozen['inner_distance_m'])
                    if clipped is not None:iw=convex_distance(clipped @ br.T+bp,handle)
                elif name.endswith('_proximal'):iw=dist
                contacts.append({'body':name,'approximation':approx,**dist,'inner_witness':iw,
                                 'inner_region_distance_m':None if iw is None else iw['distance_m']})
        for f in FINGERS:
            fc=[c for c in contacts if c['body'].startswith('right_rh_'+f+'_')]
            if any(c['distance_m']<=.001 for c in fc):near.append(f)
            if any(c['inner_witness'] and c['inner_region_distance_m']<=.001 for c in fc):inner.append(f)
        arm,pe,re=model.kin.solve(pose[:3]+kr @ (t+r @ PALM_OFFSET),kr @ r,original['supported_sample']['q_rad'][:7])
        load=conditional_load_check(model,links,q,r,t,kr,pose,contacts,handle,arm)
        full=full_robot_self_check(stage,model,arm,q)
        trial.update(exact_contact_geometry=contacts,near_fingers_within_1mm=near,inner_fingers_within_1mm=inner,
                     arm_ik={'q_rad':arm.tolist(),'position_error_m':pe,'rotation_error_rad':re},
                     conditional_load=load,full_robot_self_envelopes=full,
                     terminal_feasibility_certified=False,physical_success=False)
        selected.append(trial)
    result={'scope':'Offline proposals only; no active plan update, no simulator, no physical proof',
            'search_budget_s':120,'wall_s':time.monotonic()-start,'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            'search_reference_knife_pose_xyzw':pose.tolist(),'trials':trials,'audited_candidates':selected}
    (output/'refined_candidates.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({'wall_s':result['wall_s'],'audited_candidates':len(selected),'output':str(output/'refined_candidates.json')}),flush=True)


if __name__=='__main__':main()
