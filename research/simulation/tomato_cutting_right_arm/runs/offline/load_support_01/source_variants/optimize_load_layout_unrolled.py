"""Bounded load-aware hand-pose proposals; entirely offline and inactive."""
import json
import time
import resource
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from multipoint_load_audit import ROOT,LoadScene,CAPS
from contact_load_model import solve_contact_load
from refine_load_support import geometry_screen
from reach_kinematics import PALM_OFFSET
from offline_grasp_audit import full_robot_self_check


class Deadline(Exception):pass


def main():
    started=time.monotonic();folder=ROOT/'runs/offline/load_support_01';scene=LoadScene()
    old=json.loads((ROOT/'runs/offline/grasp_refinement_01/polished_candidates.json').read_text())
    pose=np.array(old['reference_knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix()
    com=np.array(scene.physics['knife_com_local_m']);gravity=kr.T@np.array([0,0,-scene.physics['knife_mass_kg']*9.81])
    frozen=json.loads((ROOT/'docs/rl/phase3_grasp_criteria.json').read_text())['criteria'];results=[]
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());board_z=meta['board_world_bounds'][1][2]
    from pxr import UsdGeom
    blade=np.array(UsdGeom.Mesh(scene.stage.GetPrimAtPath(meta['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());bh=ConvexHull(blade)
    hulls={name:(v[ConvexHull(v).vertices],ConvexHull(v).equations) for name,meshes in scene.geometry.items() for v,_ in meshes}
    for seed_index,base in enumerate(old['candidates']):
        deadline=time.monotonic()+90.;r0=np.array(base['hand_rotation_in_knife']);t0=np.array(base['hand_root_in_knife_m']);q0=np.array(base['joint_rad'])
        patches=scene.contacts(base,kr,max_gap=.001);initial=np.r_[t0,[0.]*3,q0]
        lower=np.r_[t0-.025,[-.6]*3,[.2,.03],[frozen['minimum_curl_rad']/1.89]*4]
        upper=np.r_[t0+.025,[.6]*3,[.9,.315],[np.deg2rad(85)]*4]
        best={'cost':float('inf'),'x':initial.copy()};calls=0
        def evaluate(x):
            r=Rotation.from_rotvec(x[3:6]).as_matrix()@r0;t=x[:3];q=x[6:];links=scene.model.transforms(q)
            plus=[]
            for j in range(6):
                dq=q.copy();dq[j]+=1e-5;plus.append(scene.model.transforms(dq))
            points=[];signed=[];outside=[]
            for p in patches:
                l=links[p['body']];local=np.array(p['local']);a=t+r@(l[:3,3]+l[:3,:3]@local)
                n=np.array(p['normal']);b0=np.array(p['point']);d=float(n@(a-b0));b=a-d*n
                jac=np.zeros((3,13))
                for j in range(6):
                    tr=plus[j][p['body']];jac[:,7+j]=(t+r@(tr[:3,3]+tr[:3,:3]@local)-a)/1e-5
                points.append({**p,'point':b.tolist(),'hand_point':a.tolist(),'jacobian':jac.tolist(),'signed_gap_m':d})
                signed.append(d);outside.append(max(0.,float(np.max(scene.eq[:,:3]@b+scene.eq[:,3]))))
            load=solve_contact_load(points,com,gravity,scale=1.25,required_parts=['palm','thumb',*base['target_fingers']],
                required_inner=['index',base['target_fingers'][-1]],torque_caps=CAPS,minimize_budget_scale=True)
            if 'required_budget_scale' not in load:return 1e6,None,None,None,None
            normal=np.array(load['normal_force_per_point_n']);weights=np.minimum(1.,normal/.06)
            board_pen=[];blade_pen=[];handle_pen=[]
            for name,(v,eq) in hulls.items():
                l=links[name];br=r@l[:3,:3];bp=t+r@l[:3,3];vv=v@br.T+bp
                def gap(other,oe):return max(float(((other-bp)@br@eq[:,:3].T+eq[:,3]).min(0).max()),float((vv@oe[:,:3].T+oe[:,3]).min(0).max()))
                handle_pen.append(max(0.,-.00005-gap(scene.handle,scene.eq))*5000)
                blade_pen.append(max(0.,.002-gap(blade,bh.equations))*3000)
                board_pen.append(max(0.,.002-float((vv@kr.T+pose[:3])[:,2].min()-board_z))*3000)
            cost=(max(0.,load['required_budget_scale']-.8)*3)**2
            cost+=float(np.sum((weights*np.array(signed)*1500)**2)+np.sum((weights*np.array(outside)*3000)**2))
            cost+=float(np.sum(np.square(handle_pen))+np.sum(np.square(blade_pen))+np.sum(np.square(board_pen)))
            cost+=float(np.sum(((t-t0)*3)**2)+np.sum((x[3:6]*.03)**2))
            return cost,load,r,t,q
        def objective(x):
            nonlocal calls
            if time.monotonic()>deadline:raise Deadline()
            calls+=1;cost,load,r,t,q=evaluate(x)
            if cost<best['cost']:best.update(cost=cost,x=x.copy(),required_budget_scale=None if load is None else load['required_budget_scale'])
            if calls%50==0:
                print(json.dumps({'seed':seed_index,'calls':calls,'best_cost':best['cost'],'budget_scale':best.get('required_budget_scale')}),flush=True)
            return cost
        status='bounded local optimization completed'
        try:minimize(objective,initial,method='Powell',bounds=list(zip(lower,upper)),options={'maxfev':550,'maxiter':12,'xtol':1e-4,'ftol':1e-4})
        except Deadline:status='90 second search bound reached'
        x=best['x'];cost,relaxed,r,t,q=evaluate(x)
        c={'seed_index':seed_index,'target_fingers':base['target_fingers'],'joint_rad':q.tolist(),
           'hand_rotation_in_knife':r.tolist(),'hand_root_in_knife_m':t.tolist(),'search_status':status,
           'search_calls':calls,'search_cost':cost,'fixed_patch_diagnostic':relaxed}
        arm,pe,re=scene.model.kin.solve(pose[:3]+kr@(t+r@PALM_OFFSET),kr@r,np.array(base['arm_ik']['q_rad']))
        c['arm_ik']={'q_rad':arm.tolist(),'position_error_m':pe,'rotation_error_rad':re}
        # Fresh closest geometry and surface points, not the search's fixed
        # contact-plane approximation, decide the reported load result.
        geo=geometry_screen(scene,c,kr,pose,details=True);c['exact_contact_geometry']=geo['contacts']
        fresh=scene.contacts(c,kr,max_gap=.001)
        c.update(geometry=geo,fresh_surface_points=fresh,
                 fresh_nominal=scene.solve(fresh,c,kr),fresh_margin=scene.solve(fresh,c,kr,scale=1.25),
                 full_robot_self_envelopes=full_robot_self_check(scene.stage,scene.model,arm,q),
                 physical_success=False,active=False)
        results.append(c)
        (folder/'load_optimized_candidates.json').write_text(json.dumps({'scope':'Fixed-patch search followed by fresh geometric/load checks; no physical proof',
            'reference_knife_pose_xyzw':pose.tolist(),'candidates':results,'wall_s':time.monotonic()-started,
            'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024},indent=2,allow_nan=False))
        print(json.dumps({'seed':seed_index,'fresh_nominal':c['fresh_nominal']['feasible'],'fresh_margin':c['fresh_margin']['feasible'],'cost':cost}),flush=True)


if __name__=='__main__':main()
