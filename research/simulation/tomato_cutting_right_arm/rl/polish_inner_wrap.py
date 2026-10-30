"""Exact-distance polishing of two offline proposals, never an active grasp plan."""
import json
import time
import resource

import numpy as np
from pxr import Usd, UsdGeom
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

from offline_grasp_audit import ROOT, FINGERS, collider_inventory, convex_distance, clip_inner, conditional_load_check, full_robot_self_check
from refine_inner_wrap import inner_surface_points, SearchDeadline
from plan_contact_seating import HandGeometry
from reach_kinematics import PALM_OFFSET


def main():
    start=time.monotonic();deadline=start+120
    folder=ROOT/'runs/offline/grasp_refinement_01'
    old=json.loads((folder/'refined_candidates.json').read_text());pose=np.array(old['search_reference_knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(stage);_,geometry=collider_inventory(stage,model)
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());original=json.loads((ROOT/'docs/rl/refined_supported_wrap.json').read_text())
    handle=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());hh=ConvexHull(handle)
    blade=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());bh=ConvexHull(blade)
    centre=(handle.min(0)+handle.max(0))/2;cross=np.linalg.svd(handle-centre,full_matrices=False)[2][1:]
    frozen=json.loads((ROOT/'docs/rl/phase3_grasp_criteria.json').read_text())['criteria']
    hulls={};inners={}
    for name,meshes in geometry.items():
        v=meshes[0][0];h=ConvexHull(v);hulls[name]=(v[h.vertices],h.equations)
        if name.endswith('_proximal'):inners[name]=v[h.vertices]
        elif name.endswith('_distal') and 'thumb' not in name:
            _,axis,end=inner_surface_points(v,frozen['inner_distance_m']);inners[name]=clip_inner(v,axis,end,frozen['inner_distance_m'])
    results=[]
    for candidate in old['audited_candidates']:
        if time.monotonic()>=deadline:break
        r0=np.array(candidate['hand_rotation_in_knife']);t0=np.array(candidate['hand_root_in_knife_m']);q0=np.array(candidate['joint_rad'])
        trio=candidate['target_fingers'];second=trio[-1]
        targets=[('right_rh_hand_base_link',False),('right_rh_thumb_distal',False),
                 ('right_rh_index_proximal',True),('right_rh_middle_distal',False),('right_rh_'+second+'_distal',True)]
        initial=np.r_[t0,[0.]*3,q0];lower=np.r_[t0-.012,[-.3]*3,[.2,.03],[frozen['minimum_curl_rad']/1.89]*4];upper=np.r_[t0+.012,[.3]*3,[.9,.315],[np.deg2rad(85)]*4]
        best={'cost':float('inf'),'x':initial.copy()};count=0
        def state(x):
            r=Rotation.from_rotvec(x[3:6]).as_matrix()@r0;t=x[:3];links=model.transforms(x[6:]);world={};sat={};bg=[];bog=[]
            for name,(v,eq) in hulls.items():
                l=links[name];br=r@l[:3,:3];bp=t+r@l[:3,3];vv=v@br.T+bp;world[name]=(br,bp,vv)
                def gap(other,oe):return max(float(((other-bp)@br@eq[:,:3].T+eq[:,3]).min(0).max()),float((vv@oe[:,:3].T+oe[:,3]).min(0).max()))
                sat[name]=gap(handle,hh.equations);bg.append(gap(blade,bh.equations));bog.append(float((vv@kr.T+pose[:3])[:,2].min()-meta['board_world_bounds'][1][2]))
            return r,t,links,world,sat,np.array(bg),np.array(bog)
        def residual(x):
            nonlocal count
            if time.monotonic()>=deadline:raise SearchDeadline()
            count+=1;r,t,links,world,sat,bg,bog=state(x);touch=[];radial=[]
            for name,inner in targets:
                br,bp,vv=world[name]
                if inner:vv=inners[name]@br.T+bp
                d=convex_distance(vv,handle)
                touch.append((d['distance_m']-.0001)*1800)
                v=cross@(np.array(d['b_m'])-centre);radial.append(v/max(np.linalg.norm(v),1e-8))
            opposition=[max(0.,float(radial[1]@v)+.6)*3 for v in radial[2:]]
            out=np.r_[touch,opposition,np.maximum(.00005-np.array(list(sat.values())),0)*5000,
                      np.maximum(.002-bg,0)*3000,np.maximum(.002-bog,0)*3000,(x[:3]-t0)*3,x[3:6]*.02,(x[6:]-q0)*.01]
            cost=float(out@out)
            if cost<best['cost']:best.update(cost=cost,x=x.copy())
            return out
        status='completed bounded exact-distance optimization'
        try:least_squares(residual,initial,bounds=(lower,upper),max_nfev=25,diff_step=1e-4,ftol=1e-6,xtol=1e-7,gtol=1e-6)
        except SearchDeadline:status='polish wall budget reached'
        except RuntimeError as e:status='distance certificate refused optimization sample: '+str(e)
        x=best['x'];r,t,links,world,sat,bg,bog=state(x);contacts=[]
        for name,(br,bp,vv) in world.items():
            d=convex_distance(vv,handle);iw=convex_distance(inners[name]@br.T+bp,handle) if name in inners else None
            contacts.append({'body':name,'approximation':geometry[name][0][1],**d,'inner_witness':iw,'inner_region_distance_m':None if iw is None else iw['distance_m']})
        arm,pe,re=model.kin.solve(pose[:3]+kr@(t+r@PALM_OFFSET),kr@r,original['supported_sample']['q_rad'][:7])
        load=conditional_load_check(model,links,x[6:],r,t,kr,pose,contacts,handle,arm)
        result={'target_fingers':trio,'status':status,'score':best['cost'],'evaluations':count,
                'hand_root_in_knife_m':t.tolist(),'hand_rotation_in_knife':r.tolist(),'joint_rad':x[6:].tolist(),
                'exact_contact_geometry':contacts,'face_axis_handle_gaps_m':sat,'blade_clearance_lower_bound_m':float(bg.min()),
                'board_plane_clearance_m':float(bog.min()),'arm_ik':{'q_rad':arm.tolist(),'position_error_m':pe,'rotation_error_rad':re},
                'conditional_load':load,'full_robot_self_envelopes':full_robot_self_check(stage,model,arm,x[6:]),
                'terminal_feasibility_certified':False,'physical_success':False}
        results.append(result);print(json.dumps({'status':status,'score':best['cost'],'evaluations':count,'load':load['status']}),flush=True)
    out={'scope':'Offline exact-distance refinement only; candidate surface and load assumptions require physical validation',
         'search_budget_s':120,'wall_s':time.monotonic()-start,'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
         'reference_knife_pose_xyzw':pose.tolist(),'candidates':results}
    (folder/'polished_candidates.json').write_text(json.dumps(out,indent=2,allow_nan=False))


if __name__=='__main__':main()
