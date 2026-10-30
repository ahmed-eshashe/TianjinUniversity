"""Offline contact-preserving hand path. Planning constraints never attach the knife."""
import json,sys,time,argparse,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import Usd,UsdGeom,UsdPhysics
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
FINGERS=['index','middle','ring','pinky']

class HandGeometry:
 def __init__(self,stage):
  self.kin=ArmKinematics(stage);self.root=self.kin.hand_path;self.paths={};self.meshes={};xc=UsdGeom.XformCache()
  for p in Usd.PrimRange(stage.GetPrimAtPath(self.root)):
   if not p.IsA(UsdGeom.Mesh):continue
   body=p
   while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
   if not body:continue
   name=body.GetName();self.paths[name]=str(body.GetPath())
   rel=np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T)@np.array(xc.GetLocalToWorldTransform(p)).T
   v=np.array(UsdGeom.Mesh(p).GetPointsAttr().Get());v=v@rel[:3,:3].T+rel[:3,3]
   hull=ConvexHull(v);self.meshes[name]=(v[hull.vertices],hull.equations)
 def transforms(self,q):
  values={'right_rh_thumb_cmc_yaw':q[0],'right_rh_thumb_cmc_pitch':q[1],'right_rh_thumb_ip':1.86*q[1]}
  for i,f in enumerate(FINGERS):values['right_rh_'+f+'_mcp_pitch']=q[i+2];values['right_rh_'+f+'_dip']=.89*q[i+2]
  cache={self.root:np.eye(4)}
  def transform(path):
   if path in cache:return cache[path]
   parent,child,a,b,axis,name=self.kin.by_child[path];r=np.eye(4)
   if axis is not None:r[:3,:3]=Rotation.from_rotvec(axis*values.get(name,0.)).as_matrix()
   cache[path]=transform(parent)@a@r@b;return cache[path]
  return {name:transform(path) for name,path in self.paths.items()}


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--steps',type=int,default=40);p.add_argument('--seconds',type=float,default=150);p.add_argument('--normal-weight',type=float,default=.06);p.add_argument('--sample',type=Path);p.add_argument('--anchor-parts',nargs=2,default=['thumb','index']);p.add_argument('--resume',type=Path);p.add_argument('--output',type=Path,default=ROOT/'docs/rl/contact_seating_plan.json');a=p.parse_args()
 s=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(s)
 proposal=json.loads((ROOT/'docs/rl/refined_supported_wrap.json').read_text());sample=proposal['supported_sample'];goal=proposal['candidates'][0]
 if a.sample:
  sample=json.loads(a.sample.read_text());sample=sample.get('sample',sample)
 if a.anchor_parts[0]!='thumb' or a.anchor_parts[1] not in FINGERS:raise ValueError('Require thumb and one measured finger anchor')
 pose=np.array(sample['knife_pose_xyzw']);kr=Rotation.from_quat(pose[3:]).as_matrix();q0=np.array(sample['q_rad'][7:]);reference_palm,rworld=model.kin.pose(sample['q_rad'][:7]);rootworld=reference_palm-rworld@PALM_OFFSET
 r0=kr.T@rworld;t0=kr.T@(rootworld-pose[:3]);transforms0=model.transforms(q0)
 anchors=[]
 for part in a.anchor_parts:
  c=max((c for c in sample['contacts'] if c['part']==part and c['on_handle'] and c['force_n']>.3),key=lambda c:c['force_n'])
  bt=transforms0[c['body']];bodyworld_r=rworld@bt[:3,:3];bodyworld_p=rootworld+rworld@bt[:3,3]
  point_local=bodyworld_r.T@(np.array(c['point_world_m'])-bodyworld_p)
  normal_local=bodyworld_r.T@np.array(c['normal_world'])
  anchors.append({'body':c['body'],'point_local':point_local,'normal_local':normal_local,
   'point_knife':kr.T@(np.array(c['point_world_m'])-pose[:3]),'normal_knife':kr.T@np.array(c['normal_world'])})
 meta=json.loads((ROOT/'rl/scene/manifest.json').read_text());kp=meta['knife_path'];board_hi=np.array(meta['board_world_bounds'])[1]
 handle=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp+'/CollisionHandle')).GetPointsAttr().Get());blade=np.array(UsdGeom.Mesh(s.GetPrimAtPath(kp+'/CollisionBlade')).GetPointsAttr().Get())
 centre=(handle.min(0)+handle.max(0))/2;hh=ConvexHull(handle);handle=handle[hh.vertices];bh=ConvexHull(blade);blade=blade[bh.vertices]
 rf=Rotation.from_quat(proposal['supported_sample']['knife_pose_xyzw'][3:]).as_matrix().T@np.array(goal['hand_rotation_world']);tf=centre-rf@np.array(goal['handle_in_hand_m'])
 qf=np.deg2rad([goal['thumb_yaw_deg'],goal['thumb_pitch_deg'],*[goal['finger_degrees'][f] for f in FINGERS]])
 omega_goal=Rotation.from_matrix(r0.T@rf).as_rotvec();names=list(model.meshes)
 def state(x):
  r=r0@Rotation.from_rotvec(x[3:6]).as_matrix();t=x[:3];q=x[6:];links=model.transforms(q);anchor_errors=[];normal_errors=[]
  for c in anchors:
   link=links[c['body']];br=r@link[:3,:3];bp=t+r@link[:3,3]
   anchor_errors.extend(br@c['point_local']+bp-c['point_knife'])
   normal_errors.extend(br@c['normal_local']-c['normal_knife'])
  gaps={};blade_gaps=[];board_gaps=[]
  for name in names:
   v,eq=model.meshes[name];link=links[name];br=r@link[:3,:3];bp=t+r@link[:3,3];vknife=v@br.T+bp
   def sat(other,other_eq):
    # Face-normal separating-axis lower bound, supplemented by runtime contact checks.
    ov=(other-bp)@br
    return max(float((ov@eq[:,:3].T+eq[:,3]).min(0).max()),float((vknife@other_eq[:,:3].T+other_eq[:,3]).min(0).max()))
   gaps[name]=sat(handle,hh.equations);blade_gaps.append(sat(blade,bh.equations))
   world=vknife@kr.T+pose[:3]
   board_gaps.append(float(world[:,2].min()-board_hi[2]))
  return r,np.array(anchor_errors),np.array(normal_errors),gaps,np.array(blade_gaps),np.array(board_gaps)
 x=np.r_[t0,np.zeros(3),q0];start=time.monotonic();waypoints=[];status='complete';initial=state(x)
 print('Initial gaps',float(initial[-1].min()),float(initial[-2].min()),'anchor',float(np.max(np.abs(initial[1]))),flush=True)
 lower=np.r_[t0-.10,[-.8]*3,[.2,0.,*[.1]*4]];upper=np.r_[t0+.10,[.8]*3,[.90,.315,*[np.deg2rad(85)]*4]]
 resume_fraction=-1.
 if a.resume:
  prior=json.loads(a.resume.read_text());waypoints=[w for w in prior['waypoints'] if not w.get('rejected')];last=waypoints[-1]
  if prior['reference_sample']!=sample or prior.get('anchor_parts',['thumb','index'])!=a.anchor_parts:raise ValueError('Resume must retain measured reference and anchors')
  if prior['normal_weight']!=a.normal_weight:raise ValueError('Resume must retain normal weight')
  x=np.r_[last['hand_root_in_knife_m'],Rotation.from_matrix(r0.T@np.array(last['hand_rotation_in_knife'])).as_rotvec(),last['joint_rad']];resume_fraction=last['fraction']
 for fraction in np.linspace(0,1,a.steps+1):
  if fraction<=resume_fraction+1e-9:continue
  if time.monotonic()-start>a.seconds:status='offline wall bound';break
  target_t=t0+fraction*(tf-t0);target_omega=fraction*omega_goal;target_q=q0+fraction*(qf-q0);previous=x.copy()
  def residual(z):
   r,ae,ne,g,bg,bog=state(z)
   desired_touch=[g['right_rh_hand_base_link']]
   for f in ['middle','ring']:desired_touch.append(min(abs(g['right_rh_'+f+'_proximal']),abs(g['right_rh_'+f+'_distal'])))
   return np.r_[ae*1000.,ne*a.normal_weight,(z[:3]-target_t)*30.,(z[3:6]-target_omega)*.08,
    (z[6:]-target_q)*.035,np.maximum(-.001-np.array(list(g.values())),0)*400.,
    np.maximum(.002-bg,0)*500.,np.maximum(.002-bog,0)*500.,np.array(desired_touch)*fraction*50.,
    (z-previous)*.003]
  sol=least_squares(residual,x,bounds=(lower,upper),max_nfev=100,ftol=2e-7,xtol=2e-7,gtol=1e-7)
  x=sol.x;r,ae,ne,g,bg,bog=state(x);error=float(np.linalg.norm(ae.reshape(2,3),axis=1).max())
  waypoint={'fraction':float(fraction),'hand_root_in_knife_m':x[:3].tolist(),'hand_rotation_in_knife':r.tolist(),
   'joint_rad':x[6:].tolist(),'anchor_error_m':error,'normal_error':float(np.linalg.norm(ne.reshape(2,3),axis=1).max()),
   'handle_gaps_m':g,'min_blade_gap_m':float(bg.min()),'min_board_gap_m':float(bog.min()),'solver_evaluations':int(sol.nfev),
   'desired_hand_root_error_m':float(np.linalg.norm(x[:3]-target_t))}
  if error>.0005 or bg.min()<0. or bog.min()<0. or min(g.values())<-.002:
   status='geometric contact/clearance limit';waypoint['rejected']=True;waypoints.append(waypoint);break
  waypoints.append(waypoint)
  print('Path',round(float(fraction),3),'anchor mm',round(error*1000,3),'palm gap mm',round(g['right_rh_hand_base_link']*1000,2),flush=True)
 out={'scope':'Offline touching-point path constraints only; no physics attachment, knife commands or training',
  'status':status,'waypoints':waypoints,'reference_sample':sample,'target':goal,'elapsed_wall_s':time.monotonic()-start,
  'normal_weight':a.normal_weight,'anchor_parts':a.anchor_parts,'reference_anchors':[{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in c.items()} for c in anchors],
  'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 a.output.write_text(json.dumps(out,indent=2));print('Status',status,'waypoints',len(waypoints),flush=True)

if __name__=='__main__':main()
