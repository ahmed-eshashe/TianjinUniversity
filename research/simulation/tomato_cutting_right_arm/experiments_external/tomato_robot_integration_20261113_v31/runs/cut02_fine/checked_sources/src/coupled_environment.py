"""Batched approximate cutting task, NOT an articulated-robot environment.

Action: [vx,vy,vz,wx,wy,wz] in m/s and rad/s, material Y-up frame.
Actor observations exclude hidden damage and connectivity; privileged critic information is returned separately in info.
Success requires two substantial disconnected pieces, supported/slow material,
knife withdrawal and no force/penetration/numerical stop. No auto-reset ambiguity:
call reset(ids) after terminal transitions. All state restoration is included.
"""
import numpy as np,warp as wp
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from model import lattice
from instrumented_solver import Solver,knife_normal

@wp.kernel
def clearance(x:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),out:wp.array(dtype=float),radius:float,n:int):
 i=wp.tid();e=i//n;p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);normal,d=knife_normal(p,.06);out[i]=d-radius

class CuttingEnv:
 action_limits=np.array([.15,.01,.15,1.,1.,1.],np.float32)
 def __init__(self,num_envs=8,scale=1.,dt=.0001,max_steps=5000,shape='tomato',offset=.00175):
  self.model=lattice(shape=shape,scale=scale);self.g=Solver(self.model,num_envs,dt,adaptive=True);self.num_envs=num_envs;self.dt=dt;self.substeps=round(.02/dt);self.max_steps=max_steps
  tool=self.g.tool.numpy();tool[:,0]+=offset;self.g.tool.assign(tool);self.g.save_initial();self.g.graph(self.substeps)
  self.clearances=wp.zeros(self.g.n*num_envs,dtype=float,device='cuda:0');self.count=np.zeros(num_envs,int);self.prev_paid=np.zeros(num_envs);self.done=np.zeros(num_envs,bool)
  self.last_alive=[None]*num_envs;self.labels=[np.zeros(self.g.n,int) for _ in range(num_envs)];self.parts=np.ones(num_envs,int);self.second_mass=np.zeros(num_envs)
  self.reset()
  from gymnasium.spaces import Box
  from gymnasium.vector.utils import batch_space
  self.single_action_space=Box(-self.action_limits,self.action_limits,dtype=np.float32)
  self.single_observation_space=Box(-np.inf,np.inf,shape=(self.observe()[0].shape[1],),dtype=np.float32)
  self.action_space=batch_space(self.single_action_space,num_envs);self.observation_space=batch_space(self.single_observation_space,num_envs)
 def reset(self,ids=None):
  ids=np.arange(self.num_envs) if ids is None else np.asarray(ids,int)
  for key,initial in self.g.initial.items():
   a=getattr(self.g,key);width=len(a)//self.num_envs
   # Warp offsets count array elements. For array2d, copy rows via slices.
   for e in ids:
    if a.ndim==2:wp.copy(a.flatten(),initial.flatten(),dest_offset=int(e*a.shape[1]),src_offset=int(e*a.shape[1]),count=a.shape[1])
    else:wp.copy(a,initial,dest_offset=int(e*width),src_offset=int(e*width),count=width)
  if len(ids)==self.num_envs:self.g.active_dt=self.g.base_dt
  self.count[ids]=0;self.prev_paid[ids]=0;self.done[ids]=False
  for e in ids:self.last_alive[e]=None
  return self.observe()[0],{'reset_ids':ids.tolist()}
 def observe(self):
  g=self.g;alive=g.alive.numpy().reshape(self.num_envs,g.nb);paid=g.paid.numpy().reshape(self.num_envs,g.nb);x=g.x.numpy().reshape(self.num_envs,g.n,3)-g.offset[:,None,:];v=g.v.numpy().reshape(self.num_envs,g.n,3)
  for e in range(self.num_envs):
   if self.last_alive[e] is None or not np.array_equal(self.last_alive[e],alive[e]):
    edge=self.model['edges'][alive[e]!=0];graph=coo_matrix((np.ones(len(edge)),(edge[:,0],edge[:,1])),shape=(g.n,g.n));parts,labels=connected_components(graph,directed=False);masses=np.bincount(labels,weights=self.model['mass']);masses.sort();self.parts[e]=parts;self.labels[e]=labels;self.second_mass[e]=masses[-2]/self.model['mass_total'] if parts>1 else 0.;self.last_alive[e]=alive[e].copy()
  wp.launch(clearance,g.n*self.num_envs,[g.x,g.tool,g.rotation,self.clearances,self.model['radius'],g.n],device='cuda:0');clear=self.clearances.numpy().reshape(self.num_envs,g.n).min(1)
  cm=np.average(x,axis=1,weights=self.model['mass']);speed=np.max(np.linalg.norm(v,axis=2),axis=1);load=g.load.numpy();bad=g.bad.numpy();tool=g.tool.numpy()-g.offset;damage=(1-alive).mean(1);work=paid.sum(1);supported=(x[:,:,1].min(1)>=self.model['radius']-.0001)&(speed<.03);separated=self.second_mass>=.05
  obs=np.c_[tool,g.rotation.numpy(),g.velocity.numpy(),g.angular_velocity.numpy(),g.reaction.numpy(),load,cm,np.std(x,axis=1),clear,self.count*.02].astype(np.float32)
  info={'critic_observation':np.c_[damage,work,self.second_mass].astype(np.float32),'bad':bad,'parts':self.parts.copy(),'second_mass_fraction':self.second_mass.copy(),'clearance_m':clear,'supported':supported,'max_speed_m_s':speed,'fracture_work_J':work,'broken':np.sum(alive==0,axis=1),'peak_force_N':g.peak.numpy(),'peak_penetration_m':g.penetration_peak.numpy(),'separated':separated,'integration_dt_s':g.active_dt,'refinements':g.refinements}
  return obs,info
 def step(self,actions):
  if self.done.any():raise RuntimeError("Reset finished environment IDs before the next batch step.")
  action=np.broadcast_to(np.asarray(actions,np.float32),(self.num_envs,6)).copy();invalid=~np.isfinite(action).all(1)
  action[invalid]=0;action=np.clip(action,-self.action_limits,self.action_limits);action[self.done]=0
  self.g.step(action,self.substeps);self.count[~self.done]+=1;obs,info=self.observe();success=info['separated']&(info['parts']==2)&info['supported']&(info['clearance_m']>.002)&(info['bad']==0)&~invalid
  terminated=((info['bad']!=0)|invalid|success)&~self.done;truncated=(self.count>=self.max_steps)&~terminated&~self.done
  reward=10*(info['fracture_work_J']-self.prev_paid)-.001-.002*np.sum(action**2,axis=1);reward+=10*success-5*((info['bad']!=0)|invalid);reward[self.done]=0
  self.prev_paid=info['fracture_work_J'].copy();self.done|=terminated|truncated;info['success']=success;info['applied_action']=action;info['scope']='Approximate kinematic-blade cutting task; robot and learned policy excluded.'
  return obs,reward.astype(np.float32),terminated,truncated,info
