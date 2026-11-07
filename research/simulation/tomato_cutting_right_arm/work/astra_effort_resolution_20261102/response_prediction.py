"""Unfitted articulated feedforward-response prediction from saved physical parameters."""
from pathlib import Path
import numpy as np,json
from scipy.spatial.transform import Rotation
R=Path(__file__).resolve().parents[2];p=R/'runs/native/motor_effort_capture_20261102_01';o=json.loads((p/'ordering.json').read_text());s=json.loads((R/'runs/native/load_down_20261102_01/robot_kinematic_snapshot.json').read_text());z=np.load(p/'interval_000.npz');pa=np.load(R/'runs/native/effort_split_20261102_01/parameters.npz');mass=pa['mass'];I=pa['inertia'].reshape(-1,3,3);A=pa['armature'][o['user_to_backend_joint']];bn=o['body_names'];jn=o['joint_names'];bychild={j['child'].split('/')[-1]:j for j in s['joints']};js={j['name']:j for j in s['joints']if j.get('name')};poses=z['after_body_pose'].astype(float);com=z['after_body_com_pose'][:,:3].astype(float);rot=Rotation.from_quat(poses[:,3:]).as_matrix();J=np.zeros((len(bn),6,len(jn)));anchors={};axes={};desc={}
for n in jn:
 j=js[n];idx=bn.index(j['child'].split('/')[-1]);T=np.linalg.inv(j['inverse_child_joint_matrix']);anchors[n]=poses[idx,:3]+rot[idx]@T[:3,3];axes[n]=rot[idx]@T[:3,:3]@j['axis'];desc[n]=[]
for bi,name in enumerate(bn):
 cur=name
 while cur in bychild:
  j=bychild[cur];n=j['name']
  if n in jn:
   qi=jn.index(n);J[bi,:3,qi]=np.cross(axes[n],com[bi]-anchors[n]);J[bi,3:,qi]=axes[n];desc[n].append(bi)
  cur=j['parent'].split('/')[-1]
Iw=np.einsum('bij,bjk,bkl->bil',rot,I,np.transpose(rot,(0,2,1)));M=np.diag(A.astype(float))
for b in range(len(bn)):M+=mass[b]*(J[b,:3].T@J[b,:3])+J[b,3:].T@Iw[b]@J[b,3:]
tau=z['gravity_feedforward'].astype(float);qacc=np.linalg.solve(M,tau);acc=np.einsum('bij,j->bi',J,qacc)
for n in ['left_AR5_5_07L_W4C4A2_joint_2','right_AR5_5_07R_W4C4A2_joint_1','right_AR5_5_07R_W4C4A2_joint_2']:
 ids=desc[n];F=np.sum(mass[ids,None]*acc[ids,:3],axis=0);T=np.sum(np.einsum('bij,bj->bi',Iw[ids],acc[ids,3:])+np.cross(com[ids]-anchors[n],mass[ids,None]*acc[ids,:3]),axis=0);idx=jn.index(n);raw=z['measured_effort_backend'][o['user_to_backend_joint'][idx]];print(n,'predicted unconstrained response moment',T@axes[n],'gravity-minus-reported',tau[idx]-raw,'qacc',qacc[idx])
def skew(v):
 x,y,z=v;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
IA=np.zeros((len(bn),6,6));bias=np.zeros((len(bn),6));parent={};depth={}
for i,n in enumerate(bn):
 IA[i,:3,:3]=mass[i]*np.eye(3);IA[i,3:,3:]=Iw[i];cur=n;dep=0
 while cur in bychild:dep+=1;cur=bychild[cur]['parent'].split('/')[-1]
 depth[i]=dep
 if n in bychild and bychild[n]['parent'].split('/')[-1] in bn:parent[i]=bn.index(bychild[n]['parent'].split('/')[-1])
for i in sorted(parent,key=lambda i:depth[i],reverse=True):
 pidx=parent[i];j=bychild[bn[i]];n=j['name'];ii=IA[i].copy();b=bias[i].copy()
 if n in jn:
  qi=jn.index(n);S=J[i,:,qi];U=ii@S;d=float(S@U+A[qi]);ii-=np.outer(U,U)/d;b+=U*(tau[qi]-S@b)/d
 X=np.eye(6);X[3:,:3]=skew(com[i]-com[pidx]);IA[pidx]+=X@ii@X.T;bias[pidx]+=X@b
for n in ['left_AR5_5_07L_W4C4A2_joint_2','right_AR5_5_07R_W4C4A2_joint_1','right_AR5_5_07R_W4C4A2_joint_2']:
 i=jn.index(n);bi=bn.index(js[n]['child'].split('/')[-1]);f=bias[bi,:3];tor=bias[bi,3:]+np.cross(com[bi]-anchors[n],f);print(n,'descendant effort bias',tor@axes[n],'required gap',tau[i]-z['measured_effort_backend'][o['user_to_backend_joint'][i]],'biasF',f)
