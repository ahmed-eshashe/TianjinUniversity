"""Float64 body COM kinematics/energy from measured native generalized state.

Pure host algebra; no SDK imports or state/parameter modification. This is an
independent reference, not proof that native Cartesian velocity sensors pass.
"""
import numpy as np
from tomato_exported_robot import ExportedRobot

class ArticulationKinematicReference:
    def __init__(self,snapshot_path,body_names,joint_names,local_com,mass,inertia_link,armature):
        self.robot=ExportedRobot(snapshot_path);self.body_names=list(body_names);self.joint_names=list(joint_names);self.index={name:i for i,name in enumerate(joint_names)}
        self.paths=[next(b['path']for b in self.robot.bodies if b['name']==name)for name in body_names]
        self.com=np.asarray(local_com,dtype=float);self.mass=np.asarray(mass,dtype=float);self.I=np.asarray(inertia_link,dtype=float);self.armature=np.asarray(armature,dtype=float)
        if self.com.shape!=(len(body_names),3)or self.I.shape!=(len(body_names),3,3)or self.mass.shape!=(len(body_names),)or self.armature.shape!=(len(joint_names),):raise ValueError('Ordered full-body COM/mass/inertia and joint-armature data required')

    def state(self,q,qd=None):
        q=np.asarray(q,dtype=float);qd=np.zeros_like(q)if qd is None else np.asarray(qd,dtype=float)
        if q.shape!=(len(self.joint_names),)or qd.shape!=q.shape or not np.isfinite(q).all()or not np.isfinite(qd).all():raise ValueError('Finite measured native q/qd required')
        poses=self.robot.forward(dict(zip(self.joint_names,q)));T=np.array([poses[path]for path in self.paths]);R=T[:,:3,:3];c=np.einsum('bij,bj->bi',R,self.com)+T[:,:3,3];J=np.zeros((len(self.paths),6,len(q)))
        for body,path in enumerate(self.paths):
            current=path
            while current in self.robot.joints:
                j=self.robot.joints[current]
                if j['axis']is not None and j['name']in self.index:
                    parent_joint=poses[j['parent']]@np.array(j['parent_joint_matrix']);axis=parent_joint[:3,:3]@np.array(j['axis']);i=self.index[j['name']];J[body,:3,i]=np.cross(axis,c[body]-parent_joint[:3,3]);J[body,3:,i]=axis
                current=j['parent']
        Iworld=R@self.I@np.swapaxes(R,1,2);velocity=np.einsum('bki,i->bk',J,qd);linear=J[:,:3];angular=J[:,3:];M=np.einsum('bki,b,bkj->ij',linear,self.mass,linear)+np.einsum('bki,bkl,blj->ij',angular,Iworld,angular);gravity=-np.einsum('bki,bk->i',linear,self.mass[:,None]*np.array([0.,0.,-9.81]));K=float(.5*np.sum(self.mass[:,None]*velocity[:,:3]**2)+.5*np.einsum('bi,bij,bj->',velocity[:,3:],Iworld,velocity[:,3:])+.5*np.sum(self.armature*qd**2))
        return dict(body_link_matrix=T,body_COM_world=c,body_COM_jacobian_world=J,body_COM_velocity_world=velocity,inertia_world=Iworld,body_mass_matrix=M,gravity_compensation=gravity,kinetic_energy_j=K)
