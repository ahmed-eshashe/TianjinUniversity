"""Offline reconstruction of omitted descendant feedforward bias in CPU TGS force queries.

Only for the evidenced fixed-base, revolute/fixed articulation with
external forces applied every TGS iteration. This changes observations, never
simulation state or commands. It does not itself qualify motor work.
"""
import numpy as np
from scipy.spatial.transform import Rotation

def skew(v):
 x,y,z=v
 return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])

class FeedforwardReadback:
 def __init__(self, body_names, joint_names, snapshot, mass, inertia_link, armature):
  self.bn=list(body_names);self.jn=list(joint_names);self.mass=np.asarray(mass,dtype=float);self.I=np.asarray(inertia_link,dtype=float).reshape(-1,3,3);self.A=np.asarray(armature,dtype=float);self.joints={j['child'].split('/')[-1]:j for j in snapshot['joints']};self.parents={};self.depth={};self.frames={};self.axes={};self.qi={}
  for i,n in enumerate(self.bn):
   cur=n;depth=0;seen=set()
   while cur in self.joints:
    if cur in seen:raise ValueError('Non-tree articulation')
    seen.add(cur);depth+=1;cur=self.joints[cur]['parent'].split('/')[-1]
   self.depth[i]=depth
   if n not in self.joints:continue
   j=self.joints[n];par=j['parent'].split('/')[-1]
   if par in self.bn:self.parents[i]=self.bn.index(par)
   self.frames[i]=np.linalg.inv(np.asarray(j['inverse_child_joint_matrix'],dtype=float))
   if j['name']in self.jn:
    self.qi[i]=self.jn.index(j['name']);self.axes[i]=np.asarray(j['axis'],dtype=float)
  if len(self.qi)!=len(self.jn):raise ValueError('Missing or duplicate movable joints')
  if self.mass.shape!=(len(self.bn),)or self.A.shape!=(len(self.jn),)or np.any(self.mass<=0)or np.any(self.A<0):raise ValueError('Invalid physical parameter shapes/values')
 def calculate(self, before_pose,before_com,after_pose,after_com,explicit_effort,raw_incoming_user_order):
  pose=np.asarray(before_pose,dtype=float);com=np.asarray(before_com,dtype=float)[:,:3];after=np.asarray(after_pose,dtype=float);cafter=np.asarray(after_com,dtype=float)[:,:3];tau=np.asarray(explicit_effort,dtype=float);raw=np.asarray(raw_incoming_user_order,dtype=float)
  if not all(np.isfinite(x).all()for x in [pose,com,after,cafter,tau,raw]):raise ValueError('Nonfinite input')
  rot=Rotation.from_quat(pose[:,3:]).as_matrix();rnew=Rotation.from_quat(after[:,3:]).as_matrix();Iw=rot@self.I@np.transpose(rot,(0,2,1));IA=np.zeros((len(self.bn),6,6));bias=np.zeros((len(self.bn),6));IA[:,:3,:3]=self.mass[:,None,None]*np.eye(3);IA[:,3:,3:]=Iw
  for i in sorted(self.parents,key=lambda i:self.depth[i],reverse=True):
   p=self.parents[i];ii=IA[i].copy();b=bias[i].copy()
   if i in self.qi:
    qi=self.qi[i];T=self.frames[i];a=rot[i]@T[:3,:3]@self.axes[i];anchor=pose[i,:3]+rot[i]@T[:3,3];S=np.r_[np.cross(a,com[i]-anchor),a];U=ii@S;d=float(S@U+self.A[qi])
    if d<=0:raise ValueError('Nonpositive articulated pivot inertia')
    ii-=np.outer(U,U)/d;b+=U*(tau[qi]-S@b)/d
   X=np.eye(6);X[3:,:3]=skew(com[i]-com[p]);IA[p]+=X@ii@X.T;bias[p]+=X@b
  correction=np.zeros_like(raw)
  for i in self.parents:
   T=self.frames[i];Q=rnew[i]@T[:3,:3];anchor=after[i,:3]+rnew[i]@T[:3,3];correction[i,:3]=Q.T@bias[i,:3];correction[i,3:]=Q.T@(bias[i,3:]+np.cross(cafter[i]-anchor,bias[i,:3]))
  corrected=raw+correction;generalized=np.zeros(len(self.jn))
  for i,qi in self.qi.items():generalized[qi]=corrected[i,3:]@self.axes[i]
  return dict(correction_child_joint=correction,corrected_child_joint=corrected,projected_corrected=generalized,bias_world_at_com=bias)
