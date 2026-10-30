"""Convert actual PhysX points and link poses to reward-independent grasp evidence."""
import numpy as np
from pxr import UsdGeom
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from native_contacts import numpy


class ContactEvidence:
    def __init__(self,env):
        self.env=env
        self.meta=env.manifest
        s=env.sim.stage; kp=self.meta['knife_path']
        self.knife_points=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp)).GetPointsAttr().Get())
        self.handle=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp+'/CollisionHandle')).GetPointsAttr().Get())
        self.blade=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp+'/CollisionBlade')).GetPointsAttr().Get())
        self.handle_hull=ConvexHull(self.handle).equations
        self.blade_hull=ConvexHull(self.blade).equations
        self.centre=(self.handle.min(0)+self.handle.max(0))/2
        _,_,axes=np.linalg.svd(self.handle-self.centre,full_matrices=False)
        self.cross_axes=axes[1:]
        self.tips={}
        xc=UsdGeom.XformCache()
        for path in env.contact_monitor.bodies:
            name=path.rsplit('/',1)[-1]
            if not name.startswith('right_rh_') or not name.endswith('_distal'):continue
            body=s.GetPrimAtPath(path); inv=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)
            points=[]
            from pxr import Usd
            for p in Usd.PrimRange(body):
                if p.IsA(UsdGeom.Mesh):
                    m=inv@np.array(xc.GetLocalToWorldTransform(p)).T
                    v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())
                    points.append(v@m[:3,:3].T+m[:3,3])
            v=np.concatenate(points);mean=v.mean(0);_,_,axes=np.linalg.svd(v-mean,full_matrices=False)
            axis=axes[0];projections=v@axis
            # Distal tip is the end farther from the link's joint origin.
            if abs(projections.min())>abs(projections.max()):axis=-axis;projections=-projections
            self.tips[name]=(axis,float(projections.max()))
        self.board_lo,self.board_hi=np.array(self.meta['board_world_bounds'])
        cp=s.GetPrimAtPath(self.meta['counter_path']);m=np.array(xc.GetLocalToWorldTransform(cp)).T
        pts=np.array(UsdGeom.Mesh(cp).GetPointsAttr().Get());pts=pts@m[:3,:3].T+m[:3,3]
        self.counter_lo,self.counter_hi=pts.min(0),pts.max(0)

    def sample(self):
        e=self.env; monitor=e.contact_monitor
        force,point,normal,separation,count,start=[numpy(x) for x in monitor.view.get_contact_data(dt=1/240)]
        matrix=numpy(monitor.view.get_contact_force_matrix(dt=1/240))
        transforms=numpy(e.robot.root_view.get_link_transforms())[0]
        names=e.robot.body_names; q=e.robot.data.joint_pos.torch[0].numpy()
        pose=e.knife.data.root_link_pose_w.torch[0].numpy()
        kr=Rotation.from_quat(pose[3:]).as_matrix()
        handle_world=kr@self.centre+pose[:3]
        palm=transforms[names.index('right_rh_hand_base_link')]
        pr=Rotation.from_quat(palm[3:]).as_matrix()
        contacts=[]; blade_contact=False; unknown=False
        ki=monitor.filters.index(self.meta['knife_path'])
        for bi,body in enumerate(monitor.bodies):
            name=body.rsplit('/',1)[-1]
            if not name.startswith('right_rh_'):continue
            body_pose=transforms[names.index(name)];br=Rotation.from_quat(body_pose[3:]).as_matrix()
            for ci in range(int(start[bi,ki]),int(start[bi,ki]+count[bi,ki])):
                f=float(force[ci,0])
                if f<.05:continue
                local=kr.T@(point[ci]-pose[:3])
                on_handle=bool(np.max(self.handle_hull[:,:3]@local+self.handle_hull[:,3])<=.003)
                on_blade=bool(np.max(self.blade_hull[:,:3]@local+self.blade_hull[:,3])<=.003)
                blade_contact |= on_blade and not on_handle
                unknown |= not on_handle and not on_blade
                part='palm' if name=='right_rh_hand_base_link' else name.removeprefix('right_rh_').split('_')[0]
                tip_distance=0.
                if name in self.tips:
                    axis,end=self.tips[name];tip_distance=end-float(axis@(br.T@(point[ci]-body_pose[:3])))
                curl=0.
                if part in ('index','middle','ring','pinky'):
                    curl=sum(float(q[e.robot.joint_names.index('right_rh_'+part+suffix)]) for suffix in ['_mcp_pitch','_dip'])
                contacts.append({'part':part,'body':name,'force_n':f,'on_handle':on_handle,
                    'radial_vector':(self.cross_axes@(local-self.centre)).tolist(),'curl_rad':curl,
                    'proximal':name.endswith('_proximal'),'distance_from_tip_m':tip_distance})
        body_index=monitor.bodies.index(self.meta['knife_path'])
        support=sum(float(np.linalg.norm(matrix[body_index,monitor.filters.index(path)])) for path in [self.meta['board_path'],self.meta['counter_path']])
        world=self.knife_points@kr.T+pose[:3];clearances=[]
        for lo,hi in [(self.board_lo,self.board_hi),(self.counter_lo,self.counter_hi)]:
            mask=np.all(world[:,:2]>=lo[:2],axis=1)&np.all(world[:,:2]<=hi[:2],axis=1)
            if mask.any():clearances.append(float(np.min(world[mask,2]-hi[2])))
        limits=e.robot.data.soft_joint_pos_limits.torch[0].numpy()
        summary=monitor.summary()
        unsafe=unknown or any(x['force_n']>5 and '/right_rh_' not in x['body'] and ('/Indoor/' in x['other'] or 'knife' in x['other']) for x in summary if x['body']!=self.meta['knife_path'])
        from pxr import UsdPhysics
        attached=any(self.meta['knife_path'] in [str(x) for rel in [UsdPhysics.Joint(p).GetBody0Rel(),UsdPhysics.Joint(p).GetBody1Rel()] for x in rel.GetTargets()]
                     for p in e.sim.stage.Traverse() if p.IsA(UsdPhysics.Joint))
        return {'handle_height_m':float(handle_world[2]),'handle_in_palm_m':(pr.T@(handle_world-palm[:3])).tolist(),
            'contacts':contacts,'blade_contact':bool(blade_contact),'unsafe_contact':bool(unsafe),
            'support_force_n':support,'support_clearance_m':min(clearances,default=100.),
            'attachment':attached,'joint_limit_violation':bool(np.any(q<limits[:,0]-.005) or np.any(q>limits[:,1]+.005)),
            'contact_buffer_full':bool(int(count.sum())>=4096),'dropped':bool(handle_world[2]<self.board_hi[2]-.04)}
