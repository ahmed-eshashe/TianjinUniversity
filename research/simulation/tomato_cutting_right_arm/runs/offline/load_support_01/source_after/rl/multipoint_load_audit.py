"""Read-only finite-surface load comparisons and helpers for offline refinement."""
import json
import time
import resource
import numpy as np
from pxr import Usd,UsdGeom
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from offline_grasp_audit import ROOT,FINGERS,collider_inventory
from plan_contact_seating import HandGeometry
from contact_load_model import solve_contact_load

CAPS=np.r_[[80.]*7,[1.,1.],[.3]*4]


def exterior_samples(v,resolution=4):
    h=ConvexHull(v);samples=[v[h.vertices]]
    tri=v[h.simplices]
    for i in range(resolution+1):
        for j in range(resolution+1-i):
            a=i/resolution;b=j/resolution
            samples.append(tri[:,0]*a+tri[:,1]*b+tri[:,2]*(1-a-b))
    return np.unique(np.round(np.concatenate(samples),12),axis=0)


def point_jacobian(model,q,r,t,arm,kr,body,local):
    links=model.transforms(q);l=links[body];a=t+r@(l[:3,3]+l[:3,:3]@local)
    j=[]
    for i in range(6):
        changed=q.copy();changed[i]+=1e-5;tr=model.transforms(changed)[body]
        j.append((t+r@(tr[:3,3]+tr[:3,:3]@local)-a)/1e-5)
    root=model.kin.transforms(arm)[model.root];ap=root[:3,3]+root[:3,:3]@(l[:3,3]+l[:3,:3]@local)
    ja=[]
    for i in range(7):
        changed=np.array(arm);changed[i]+=1e-5;tr=model.kin.transforms(changed)[model.root]
        ja.append(kr.T@((tr[:3,3]+tr[:3,:3]@(l[:3,3]+l[:3,:3]@local)-ap)/1e-5))
    return np.c_[np.array(ja).T,np.array(j).T]


class LoadScene:
    def __init__(self):
        self.stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));self.model=HandGeometry(self.stage)
        _,self.geometry=collider_inventory(self.stage,self.model)
        meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
        self.handle=np.array(UsdGeom.Mesh(self.stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get())
        self.eq=np.unique(np.round(ConvexHull(self.handle).equations,12),axis=0)
        self.samples={};self.tips={}
        for name,meshes in self.geometry.items():
            if len(meshes)!=1:raise ValueError('Surface sampler requires one collider per body')
            v=meshes[0][0];self.samples[name]=exterior_samples(v)
            axis=np.linalg.svd(v-v.mean(0),full_matrices=False)[2][0]
            if abs((v@axis).min())>abs((v@axis).max()):axis=-axis
            self.tips[name]=(axis,float((v@axis).max()))
        self.physics=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())

    def contacts(self,candidate,kr,max_gap=.001,max_per_body=8):
        q=np.array(candidate['joint_rad']);r=np.array(candidate['hand_rotation_in_knife']);t=np.array(candidate['hand_root_in_knife_m']);arm=np.array(candidate['arm_ik']['q_rad'])
        links=self.model.transforms(q);allowed=['palm','thumb',*candidate['target_fingers']];pool=[]
        for name,local_points in self.samples.items():
            part='palm' if name=='right_rh_hand_base_link' else name.removeprefix('right_rh_').split('_')[0]
            if part not in allowed:continue
            if part=='thumb' and name!='right_rh_thumb_distal':continue
            if part in FINGERS and 1.89*q[2+FINGERS.index(part)]<np.deg2rad(115):continue
            l=links[name];br=r@l[:3,:3];bp=t+r@l[:3,3]
            points=local_points@br.T+bp;signed=points@self.eq[:,:3].T+self.eq[:,3]
            face=np.argmax(signed,axis=1);dist=signed[np.arange(len(points)),face]
            chosen=[]
            for i in np.flatnonzero((dist>=1e-8)&(dist<=max_gap)):
                n=self.eq[face[i],:3];b=points[i]-dist[i]*n
                # A projection onto an edge extension is not on the handle.
                if np.max(self.eq[:,:3]@b+self.eq[:,3])>1e-8:continue
                axis,end=self.tips[name];inner=name.endswith('_proximal') or (name.endswith('_distal') and end-local_points[i]@axis>=.015-1e-9)
                chosen.append({'body':name,'part':part,'point':b.tolist(),'normal':n.tolist(),
                               'hand_point':points[i].tolist(),'local':local_points[i].tolist(),
                               'gap_m':float(dist[i]),'inner':bool(inner),'origin':'exterior barycentric sample'})
            # Exact closest witnesses supplement the grid, including edge normals.
            for item in candidate.get('exact_contact_geometry',[]):
                if item['body']!=name:continue
                for witness in [item,item.get('inner_witness')]:
                    if not witness:continue
                    a=np.array(witness['a_m']);b=np.array(witness['b_m']);d=np.linalg.norm(a-b)
                    if not 1e-8<d<=max_gap:continue
                    local=br.T@(a-bp);heq=ConvexHull(self.geometry[name][0][0]).equations
                    if abs(np.max(heq[:,:3]@local+heq[:,3]))>1e-6:continue
                    axis,end=self.tips[name];inner=name.endswith('_proximal') or (name.endswith('_distal') and end-local@axis>=.015-1e-9)
                    chosen.append({'body':name,'part':part,'point':b.tolist(),'normal':((a-b)/d).tolist(),
                                   'hand_point':a.tolist(),'local':local.tolist(),'gap_m':float(d),'inner':bool(inner),'origin':'exact exterior witness'})
            if not chosen:continue
            chosen.sort(key=lambda c:c['gap_m']);keep=[chosen[0]]
            inner_candidates=[c for c in chosen if c['inner']]
            if inner_candidates and not keep[0]['inner']:keep.append(inner_candidates[0])
            # Spread points along the real finite surface, without increasing
            # the shared part force/torque budget.
            remaining=[c for c in chosen if c is not keep[0] and all(c is not k for k in keep)]
            while remaining and len(keep)<max_per_body:
                def diversity(c):return min(np.linalg.norm(np.array(c['point'])-k['point'])+.005*np.linalg.norm(np.array(c['normal'])-k['normal']) for k in keep)
                c=max(remaining,key=diversity);remaining.remove(c);keep.append(c)
            for c in keep:
                c['jacobian']=point_jacobian(self.model,q,r,t,arm,kr,name,np.array(c['local'])).tolist()
            pool.extend(keep)
        return pool

    def solve(self,contacts,candidate,kr,scale=1.,actuators=True,mu=.6):
        gravity=kr.T@np.array([0.,0.,-self.physics['knife_mass_kg']*9.81])
        return solve_contact_load(contacts,self.physics['knife_com_local_m'],gravity,mu=mu,scale=scale,
            required_parts=['palm','thumb',*candidate['target_fingers']],
            required_inner=['index',candidate['target_fingers'][-1]],torque_caps=CAPS if actuators else None)


def main():
    start=time.monotonic();folder=ROOT/'runs/offline/load_support_01';scene=LoadScene()
    original=json.loads((ROOT/'runs/offline/grasp_refinement_01/polished_candidates.json').read_text())
    kr=Rotation.from_quat(original['reference_knife_pose_xyzw'][3:]).as_matrix();results=[]
    for index,c in enumerate(original['candidates']):
        comparisons=[]
        for gap in [.00025,.0005,.001,.002,.004]:
            points=scene.contacts(c,kr,max_gap=gap)
            if not points:continue
            # Identical force/torque/friction budget for one representative point
            # per part and finite-surface expansion. Representative selection is
            # fixed before solving; it is not a global single-point optimum.
            single=[]
            for part in ['palm','thumb',*c['target_fingers']]:
                group=[p for p in points if p['part']==part]
                if not group:continue
                if part in ['index',c['target_fingers'][-1]]:
                    inner=[p for p in group if p['inner']]
                    if inner:group=inner
                single.append(min(group,key=lambda p:p['gap_m']))
            case={'max_hypothetical_contact_gap_m':gap,'single_points':single,'surface_points':points,
                  'single_nominal':scene.solve(single,c,kr),'surface_nominal':scene.solve(points,c,kr),
                  'surface_margin':scene.solve(points,c,kr,scale=1.25),
                  'surface_margin_without_actuator_limits':scene.solve(points,c,kr,scale=1.25,actuators=False)}
            comparisons.append(case)
            print(json.dumps({'candidate':index,'gap_mm':gap*1000,'points':len(points),
                 'single':case['single_nominal']['feasible'],'surface':case['surface_nominal']['feasible'],
                 'margin':case['surface_margin']['feasible'],'no_actuators':case['surface_margin_without_actuator_limits']['feasible']}),flush=True)
        results.append({'candidate_index':index,'target_fingers':c['target_fingers'],'comparisons':comparisons})
    result={'scope':'Finite sampled surface sensitivity; positive gaps hypothetical, no contacts activated; per-part budgets shared',
            'wall_s':time.monotonic()-start,'peak_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'cases':results}
    (folder/'multipoint_load_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
