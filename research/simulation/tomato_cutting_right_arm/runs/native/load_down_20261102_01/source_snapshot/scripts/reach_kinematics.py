"""Forward/inverse kinematics from the authored USD joint frames (metres/radians)."""
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from pxr import Usd, UsdGeom, UsdPhysics

PALM_OFFSET = np.array([0.,0.,0.065])

def frame(pos,quat):
    t=np.eye(4);t[:3,3]=pos
    t[:3,:3]=Rotation.from_quat([*quat.GetImaginary(),quat.GetReal()]).as_matrix()
    return t

class ArmKinematics:
    def __init__(self,stage,side="right"):
        root=stage.GetPrimAtPath('/dual_ar5_o6')
        self.root=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(root)).T
        self.joints={}; self.by_child={};self.home={}; self.limits={}
        xc=UsdGeom.XformCache()
        self.hand_path=next(str(p.GetPath()) for p in Usd.PrimRange(root) if p.GetName()==('right_rh_hand_base_link' if side=='right' else 'left_lh_hand_base_link'))
        for p in Usd.PrimRange(root):
            if not p.IsA(UsdPhysics.Joint):continue
            j=UsdPhysics.Joint(p);b0=j.GetBody0Rel().GetTargets();b1=j.GetBody1Rel().GetTargets()
            if not b1:continue
            a=frame(j.GetLocalPos0Attr().Get(),j.GetLocalRot0Attr().Get())
            b=frame(j.GetLocalPos1Attr().Get(),j.GetLocalRot1Attr().Get())
            axis=None
            if p.IsA(UsdPhysics.RevoluteJoint):
                rev=UsdPhysics.RevoluteJoint(p);axis=np.eye(3)['XYZ'.index(rev.GetAxisAttr().Get())]
                self.limits[p.GetName()]=np.deg2rad([rev.GetLowerLimitAttr().Get(),rev.GetUpperLimitAttr().Get()])
                w0=np.array(xc.GetLocalToWorldTransform(stage.GetPrimAtPath(b0[0]))).T
                w1=np.array(xc.GetLocalToWorldTransform(stage.GetPrimAtPath(b1[0]))).T
                rel=np.linalg.inv(w0@a)@(w1@b)
                self.home[p.GetName()]=float(Rotation.from_matrix(rel[:3,:3]).as_rotvec()@axis)
            item=(str(b0[0]) if b0 else None,str(b1[0]),a,np.linalg.inv(b),axis,p.GetName())
            self.joints[p.GetName()]=item; self.by_child[str(b1[0])]=item
        self.names=[f'{side}_AR5_5_07{"R" if side=="right" else "L"}_W4C4A2_joint_{i}' for i in range(1,8)]
        self.lower=np.array([self.limits[n][0] for n in self.names])+0.002
        self.upper=np.array([self.limits[n][1] for n in self.names])-0.002
        chain=[];path=self.hand_path
        while path in self.by_child:
            j=self.by_child[path];chain.append(j);path=j[0]
        assert path=='/dual_ar5_o6',path
        self.chain=chain[::-1]

    def transforms(self,q):
        values=dict(zip(self.names,q));t=self.root.copy();out={}
        for parent,child,a,b,axis,name in self.chain:
            rot=np.eye(4)
            if axis is not None:rot[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0)).as_matrix()
            t=t@a@rot@b;out[child]=t.copy()
        return out

    def pose(self,q):
        t=self.transforms(q)[self.hand_path]
        return t[:3,3]+t[:3,:3]@PALM_OFFSET,t[:3,:3]

    def solve(self,position,orientation,seed):
        def residual(q):
            p,r=self.pose(q)
            return np.r_[p-position,0.15*Rotation.from_matrix(orientation@r.T).as_rotvec(),0.0002*(q-seed)]
        sol=least_squares(residual,np.clip(seed,self.lower,self.upper),bounds=(self.lower,self.upper),max_nfev=400,ftol=1e-10,xtol=1e-10,gtol=1e-10)
        p,r=self.pose(sol.x)
        return sol.x,float(np.linalg.norm(p-position)),float(np.linalg.norm(Rotation.from_matrix(orientation@r.T).as_rotvec()))
