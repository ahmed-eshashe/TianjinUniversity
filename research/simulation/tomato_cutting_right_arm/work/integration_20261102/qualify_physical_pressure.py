from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'));from tomato_physical_pressure_reference import evaluate_pressure
blade_path=r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';blade=json.loads(blade_path.read_text());v=np.array(blade['vertices']);f=np.array(blade['triangles']);a=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);face=int(np.argmax(np.linalg.norm(a,axis=1)));tri=v[f[face]];normal=a[face]/np.linalg.norm(a[face]);q=tri.mean(0);tangent=(tri[1]-tri[0]);tangent/=np.linalg.norm(tangent);bary=np.array([[.2,.3,.5]]);idx=np.array([[0,1,2]]);com=np.array([-.1909371614,.0050265919,.0013825955]);cases=[]
for name,penetration,slide,axis in [('normal',50e-6,0,[0,0,1]),('tangential_offset',50e-6,.003,[1,2,3]),('clear',-50e-6,.003,[2,-1,3])]:
 local=q+slide*tangent-penetration*normal;nodes=np.tile(local,(3,1));rot=Rotation.from_rotvec(np.array(axis)*.12).as_matrix();trans=np.array([.06,-.1,.2]);x=nodes@rot.T+trans;args=dict(indices=idx,barycentric=bary,areas=[1e-6],closest_local=[q],normals_local=[normal],rotation=rot,translation=trans,com_local=com);out=evaluate_pressure(x,**args);eps=1e-7;fd=[]
 for i in range(3):
  xp=x.copy();xm=x.copy();xp[1,i]+=eps;xm[1,i]-=eps;fd.append(-(evaluate_pressure(xp,**args)['energy_j']-evaluate_pressure(xm,**args)['energy_j'])/(2*eps))
 force_error=float(abs(np.array(fd)-out['force'][1]).max());wrench_fd=[]
 for i in range(6):
  if i<3:
   t=np.eye(3)[i]*eps;ap={**args,'translation':trans+t};am={**args,'translation':trans-t}
  else:
   w=np.eye(3)[i-3]*eps;rp=Rotation.from_rotvec(w).as_matrix()@rot;rm=Rotation.from_rotvec(-w).as_matrix()@rot;ap={**args,'rotation':rp,'translation':out['body_com']-rp@com};am={**args,'rotation':rm,'translation':out['body_com']-rm@com}
  wrench_fd.append(-(evaluate_pressure(x,**ap)['energy_j']-evaluate_pressure(x,**am)['energy_j'])/(2*eps))
 wrench_error=float(abs(np.array(wrench_fd)-out['body_wrench']).max());force_balance=float(np.linalg.norm(out['force'].sum(0)+out['body_wrench'][:3]));moment_balance=float(np.linalg.norm(np.cross(x,out['force']).sum(0)+np.cross(out['body_com'],out['body_wrench'][:3])+out['body_wrench'][3:]));legacy_moment=np.cross(q@rot.T+trans-out['body_com'],-out['sample_force'][0]);legacy_gap=float(np.linalg.norm(legacy_moment-out['body_wrench'][3:]));row=dict(case=name,force_derivative_error_n=force_error,wrench_derivative_error_n_or_nm=wrench_error,force_balance_n=force_balance,moment_balance_nm=moment_balance,legacy_frozen_closest_point_moment_difference_nm=legacy_gap,energy_j=out['energy_j'])
 if max(force_error,wrench_error)>1e-8 or force_balance>1e-12 or moment_balance>1e-12:raise ValueError(row)
 if name=='tangential_offset' and legacy_gap<1e-5:raise ValueError('Missing off-center moment control')
 if name=='clear' and (out['energy_j'] or np.any(out['body_wrench'])):raise ValueError('Clear control failed')
 cases.append(row)
out=r/'runs/offline/physical_pressure_20261102_01';out.mkdir(exist_ok=True);report=dict(passed=True,cases=cases,scope='Independent finite-energy derivatives for a physical-coordinate frozen planar contact packet on an actual CAD facet. Not a native kernel, generated full-target contact, actual robot run or whole-system work closure.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [blade_path,r/'rl/tomato_physical_pressure_reference.py',Path(__file__)]});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(cases)
