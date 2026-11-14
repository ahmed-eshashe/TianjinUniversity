"""Host body-sum references for fixed-base robot mass, gravity and work.

COM inertias are expressed in COM-local axes, as specified by Omni Physics.
These algebraic checks do not qualify actuator work or dynamic constraints.
"""
import numpy as np
def body_sum_reference(mass,inertia_com_local,rotation_com_world,jacobian_com_world,armature):
 mass=np.asarray(mass,dtype=float);inertia=np.asarray(inertia_com_local,dtype=float);R=np.asarray(rotation_com_world,dtype=float);J=np.asarray(jacobian_com_world,dtype=float);armature=np.asarray(armature,dtype=float);B=len(mass);D=len(armature)
 if inertia.shape!=(B,3,3)or R.shape!=(B,3,3)or J.shape!=(B,6,D)or any(not np.isfinite(a).all()for a in [mass,inertia,R,J,armature])or np.any(mass<0)or np.any(armature<0):raise ValueError('Finite body mass/COM-inertia/Jacobian inputs required')
 if np.max(abs(np.swapaxes(R,1,2)@R-np.eye(3)))>1e-6 or np.max(abs(inertia-np.swapaxes(inertia,1,2)))>1e-8:raise ValueError('Proper COM frame and symmetric local inertia required')
 I=R@inertia@np.swapaxes(R,1,2);linear=J[:,:3];angular=J[:,3:];M=np.einsum('bki,b,bkj->ij',linear,mass,linear)+np.einsum('bki,bkl,blj->ij',angular,I,angular);g=-np.einsum('bki,bk->i',linear,mass[:,None]*np.array([0.,0.,-9.81]));return dict(body_mass_matrix=M,mass_matrix_with_armature=M+np.diag(armature),gravity_compensation=g,inertia_world=I)

def kinetic_energy(mass,inertia_world,body_com_velocity_world,armature,joint_velocity):
 mass=np.asarray(mass);I=np.asarray(inertia_world);v=np.asarray(body_com_velocity_world);qd=np.asarray(joint_velocity);a=np.asarray(armature)
 if v.shape!=(len(mass),6)or I.shape!=(len(mass),3,3)or a.shape!=qd.shape or any(not np.isfinite(x).all()for x in [mass,I,v,qd,a]):raise ValueError('Finite COM and joint velocity inputs required')
 return float(.5*np.sum(mass[:,None]*v[:,:3]**2)+.5*np.einsum('bi,bij,bj->',v[:,3:],I,v[:,3:])+.5*np.sum(a*qd**2))
