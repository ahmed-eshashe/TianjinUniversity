"""Approximate elastic bond network with irreversible work-paid knife cutting.

Not DiSECt, MPM, continuum FEM, official CRESSim, or experimental tomato data.
Material volume is represented by non-overlapping collidable particle spheres;
massless elastic bonds represent effective cohesion across their small gaps.
"""
import numpy as np,warp as wp

@wp.kernel
def grid_motion_guard(x:wp.array(dtype=wp.vec3),reference:wp.array(dtype=wp.vec3),bad:wp.array(dtype=int),skin:float,n:int):
 i=wp.tid()
 if wp.length(x[i]-reference[i])>skin:wp.atomic_max(bad,i//n,5)

@wp.kernel
def particle_contacts(grid:wp.uint64,x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),radius:float,skin:float,dt:float,n:int):
 i=wp.tid();e=i//n
 if bad[e]!=0:return
 neighbors=wp.hash_grid_query(grid,x[i],2.*radius+skin)
 for j in neighbors:
  if j>i and j//n==e:
   delta=x[j]-x[i];distance=wp.length(delta)
   if distance<2.*radius and distance>1e-8:
    normal=delta/distance;rel=v[j]-v[i];speed=wp.dot(rel,normal);reduced=mass[i%n]*mass[j%n]/(mass[i%n]+mass[j%n]);damping=.4*wp.sqrt(1000.*reduced)
    magnitude=wp.max(1000.*(2.*radius-distance)-damping*speed,0.);tangent=rel-speed*normal;slip=wp.length(tangent);friction=wp.vec3(0.)
    if slip>1e-10:friction=-wp.min(.2*magnitude,reduced*slip/dt)*tangent/slip
    f=magnitude*normal+friction;wp.atomic_sub(force,i,f);wp.atomic_add(force,j,f);wp.atomic_add(ledger,e,5,wp.max(damping*speed*speed-wp.dot(friction,rel),0.)*dt)

@wp.kernel
def clear_step(x:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),reaction:wp.array(dtype=wp.vec3),normal_load:wp.array(dtype=float),drive:wp.array(dtype=wp.vec3),tool:wp.array(dtype=wp.vec3),action:wp.array(dtype=wp.vec3),angular_action:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),clock:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,n:int):
 i=wp.tid();e=i//n;force[i]=wp.vec3(0.,-9.81*mass[i%n],0.)
 if i%n==0:
  reaction[e]=wp.vec3(0.);normal_load[e]=0.;drive[e]=action[e]
  if bad[e]==0:
   tool[e]+=dt*action[e];angular_velocity[e]=angular_action[e];omega=wp.length(angular_action[e])
   if omega>1e-10:rotation[e]=wp.normalize(wp.quat_from_axis_angle(angular_action[e]/omega,omega*dt)*rotation[e])
   clock[e]+=dt*20000.

@wp.kernel
def bonds(x:wp.array(dtype=wp.vec3),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),edge:wp.array(dtype=wp.vec2i),rest:wp.array(dtype=float),stiffness:wp.array(dtype=float),mass:wp.array(dtype=float),area:wp.array(dtype=float),alive:wp.array(dtype=int),paid:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),bad:wp.array(dtype=int),h:float,dt:float,n:int,nb:int,half_length:float,cut_enabled:int):
 idx=wp.tid();e=idx//nb;b=idx%nb
 if bad[e]!=0 or alive[idx]==0:return
 ends=edge[b];i=e*n+ends[0];j=e*n+ends[1];delta=x[j]-x[i];length=wp.length(delta)
 if length<1e-8:wp.atomic_max(bad,e,2);return
 direction=delta/length;strain=length-rest[b];relative=wp.dot(v[j]-v[i],direction);reduced=mass[ends[0]]*mass[ends[1]]/(mass[ends[0]]+mass[ends[1]]);damping=2.*.02*wp.sqrt(stiffness[b]*reduced);f=(stiffness[b]*strain+damping*relative)*direction
 wp.atomic_add(force,i,f);wp.atomic_sub(force,j,f);wp.atomic_add(ledger,e,0,damping*relative*relative*dt)
 if cut_enabled==0:return
 a=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);c=wp.quat_rotate_inv(rotation[e],x[j]-tool[e])
 if a[0]*c[0]>=0.:return
 t=a[0]/(a[0]-c[0]);p=a+t*(c-a)
 if wp.abs(p[2])>half_length or p[1]<-.5*h or p[1]>.03:return
 midpoint_v=(1.-t)*v[i]+t*v[j];blade_velocity=velocity[e]+wp.cross(angular_velocity[e],(1.-t)*x[i]+t*x[j]-tool[e]);rel=blade_velocity-midpoint_v;local=wp.quat_rotate_inv(rotation[e],rel);advance=wp.max(-local[1],0.)+.25*wp.abs(local[2]);speed=wp.length(rel);budget=80.*area[b];remaining=wp.max(budget-paid[idx],0.)
 if advance<=0. or speed<=1e-8 or remaining<=0.:return
 # Idealized slicing benefit: work depends on normal progress plus declared sawing slip; the
 # resisting force acts against total relative motion, including sawing.
 dwork=wp.min(remaining,budget/h*advance*dt);resistance=dwork/(speed*dt)*rel/speed
 wp.atomic_add(force,i,(1.-t)*resistance);wp.atomic_add(force,j,t*resistance);wp.atomic_sub(reaction,e,resistance);wp.atomic_add(load,e,wp.length(resistance));wp.atomic_add(ledger,e,1,dwork);wp.atomic_add(ledger,e,2,wp.dot(resistance,blade_velocity)*dt);paid[idx]+=dwork
 if paid[idx]>=budget*(1.-1e-5):
  alive[idx]=0;wp.atomic_add(ledger,e,3,.5*stiffness[b]*strain*strain)

@wp.func
def box_normal(p:wp.vec3,half:wp.vec3):
 q=wp.vec3(wp.abs(p[0]),wp.abs(p[1]),wp.abs(p[2]))-half;outside=wp.vec3(wp.max(q[0],0.),wp.max(q[1],0.),wp.max(q[2],0.));distance=wp.length(outside);normal=wp.vec3(0.)
 if distance>1e-12:
  normal=wp.vec3(wp.sign(p[0])*outside[0],wp.sign(p[1])*outside[1],wp.sign(p[2])*outside[2])/distance
 else:
  axis=int(0)
  if q[1]>q[axis]:axis=1
  if q[2]>q[axis]:axis=2
  normal[axis]=1. if p[axis]>=0. else -1.;distance=q[axis]
 return normal,distance

@wp.func
def knife_normal(p:wp.vec3,half_length:float):
 # Exact signed distance to a finite triangular prism (0..30 mm tall).
 q=wp.vec2(p[0],p[1]);best=float(1e9);near=wp.vec2(0.)
 for k in range(3):
  a=wp.vec2(0.,0.);b=wp.vec2(.0005,.03)
  if k==1:a=wp.vec2(.0005,.03);b=wp.vec2(-.0005,.03)
  if k==2:a=wp.vec2(-.0005,.03);b=wp.vec2(0.,0.)
  ab=b-a;t=wp.clamp(wp.dot(q-a,ab)/wp.dot(ab,ab),0.,1.);point=a+t*ab;d=wp.length(q-point)
  if d<best:best=d;near=point
 inside=p[1]>=0. and p[1]<=.03 and wp.abs(p[0])<=p[1]/60.
 normal2=wp.vec2(1.,0.);distance2=best
 if best>1e-12:normal2=(q-near)/best
 if inside:distance2=-best;normal2=-normal2
 dz=wp.abs(p[2])-half_length;az=wp.max(dz,0.);axy=wp.max(distance2,0.);distance=wp.sqrt(az*az+axy*axy)+wp.min(wp.max(distance2,dz),0.);normal=wp.vec3(normal2[0],normal2[1],0.)
 if dz>distance2 and distance2<=0.:normal=wp.vec3(0.,0.,wp.sign(p[2]))
 elif az>0.:
  norm=wp.sqrt(az*az+axy*axy);normal=wp.vec3(axy*normal2[0],axy*normal2[1],az*wp.sign(p[2]))/norm
 return normal,distance

@wp.kernel
def integrate(x:wp.array(dtype=wp.vec3),fixed:wp.array(dtype=int),v:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),mass:wp.array(dtype=float),tool:wp.array(dtype=wp.vec3),velocity:wp.array(dtype=wp.vec3),angular_velocity:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),ledger:wp.array2d(dtype=float),penetration_peak:wp.array(dtype=float),bad:wp.array(dtype=int),dt:float,radius:float,n:int,half_length:float,knife_enabled:int):
 i=wp.tid();e=i//n
 if bad[e]!=0:return
 if fixed[i]!=0:
  if knife_enabled!=0:
   p=wp.quat_rotate_inv(rotation[e],x[i]-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance
   wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))
   if penetration>.0001:wp.atomic_max(bad,e,4)
  return
 m=mass[i%n];newv=v[i]+dt*force[i]/m;newx=x[i]+dt*newv
 if knife_enabled!=0:
  p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length);penetration=radius-distance
  wp.atomic_max(penetration_peak,e,wp.max(penetration,0.))
  if penetration>.0001:wp.atomic_max(bad,e,4);return
  if penetration>0.:
   normal=wp.quat_rotate(rotation[e],normal);correction=penetration*normal;impulse=m/dt*correction;newx+=correction;newv+=impulse/m
   blade_velocity=velocity[e]+wp.cross(angular_velocity[e],newx-tool[e]);rel=newv-blade_velocity;tangent=rel-wp.dot(rel,normal)*normal;length=wp.length(tangent);friction=wp.vec3(0.)
   if length>1e-12:friction=-wp.min(.2*wp.length(impulse),m*length)*tangent/length;newv+=friction/m
   total=impulse+friction;wp.atomic_sub(reaction,e,total/dt);wp.atomic_add(load,e,wp.length(total)/dt);wp.atomic_add(ledger,e,2,wp.dot(total,blade_velocity));wp.atomic_add(ledger,e,4,-wp.dot(friction,rel))
 if newx[1]<radius:
  old_ke=.5*m*wp.dot(newv,newv)
  newx[1]=radius
  if newv[1]<0.:
   normal_speed=-newv[1];newv[1]=0.;horizontal=wp.vec3(newv[0],0.,newv[2]);speed=wp.length(horizontal)
   if speed>1e-12:newv-=wp.min(.4*normal_speed,speed)*horizontal/speed
  wp.atomic_add(ledger,e,6,wp.max(old_ke-.5*m*wp.dot(newv,newv),0.))
 if knife_enabled!=0:
  p=wp.quat_rotate_inv(rotation[e],newx-tool[e]);normal,distance=knife_normal(p,half_length)
  if radius-distance>.0001:wp.atomic_max(bad,e,4)
 if not wp.isfinite(newx[0]) or not wp.isfinite(newx[1]) or not wp.isfinite(newx[2]) or wp.length(newv)>10.:wp.atomic_max(bad,e,2)
 x[i]=newx;v[i]=newv

@wp.kernel
def finish_step(reaction:wp.array(dtype=wp.vec3),load:wp.array(dtype=float),peak:wp.array(dtype=float),bad:wp.array(dtype=int),tool:wp.array(dtype=wp.vec3),rotation:wp.array(dtype=wp.quat),knife_enabled:int,stop_force:float):
 e=wp.tid();peak[e]=wp.max(peak[e],load[e])
 if load[e]>stop_force or not wp.isfinite(load[e]):wp.atomic_max(bad,e,3)
 if knife_enabled!=0:
  minimum=float(1e9)
  for k in range(6):
   p=wp.vec3(0.,0.,-.06 if k<3 else .06)
   if k%3==1:p[0]=.0005;p[1]=.03
   if k%3==2:p[0]=-.0005;p[1]=.03
   world=tool[e]+wp.quat_rotate(rotation[e],p);minimum=wp.min(minimum,world[1])
  if minimum<0.:wp.atomic_max(bad,e,6)

class Solver:
 def __init__(self,model,envs=1,dt=.0001,cut=True,knife=True,stop_force=2.,recontact=True,support=True,grid_interval=1,adaptive=False):
  self.model=model;self.envs=envs;self.n=len(model['x']);self.nb=len(model['edges']);self.dt=dt;self.cut=int(cut);self.knife=int(knife);self.stop_force=stop_force;self.graphs={};self.steps=0;self.recontact=recontact;self.grid_interval=grid_interval;self.grid_skin=.0005 if grid_interval>1 else 0.;self.base_dt=dt;self.active_dt=dt;self.adaptive=adaptive;self.refinements=0;self.last_attempts=[]
  positions=np.tile(model['x'],(envs,1));positions[:,0]+=np.repeat(np.arange(envs)*.2,self.n);self.offset=np.c_[np.arange(envs)*.2,np.zeros(envs),np.zeros(envs)].astype(np.float32)
  def arr(name,x,dtype):setattr(self,name,wp.array(x,dtype=dtype,device='cuda:0'))
  arr('x',positions,wp.vec3);arr('v',np.zeros_like(positions),wp.vec3);arr('force',np.zeros_like(positions),wp.vec3)
  fixed=np.isclose(model['x'][:,1],model['x'][:,1].min()).astype(np.int32) if support else np.zeros(self.n,np.int32)
  arr('fixed',np.tile(fixed,envs),int);arr('edge',model['edges'],wp.vec2i);arr('rest',model['length'],float);arr('stiffness',model['stiffness'],float);arr('mass',model['mass'],float);arr('area',model['fracture_area'],float)
  arr('alive',np.ones(envs*self.nb,np.int32),int);arr('paid',np.zeros(envs*self.nb),float);arr('tool',self.offset+[0.,float(model['x'][:,1].max())+.01,0.],wp.vec3)
  for key in ['velocity','action','angular_action','angular_velocity','reaction']:arr(key,np.zeros((envs,3)),wp.vec3)
  arr('rotation',np.tile([0,0,0,1.],(envs,1)),wp.quat)
  for key in ['load','peak','penetration_peak','clock']:arr(key,np.zeros(envs),float)
  arr('bad',np.zeros(envs,np.int32),int);arr('ledger',np.zeros((envs,7)),float)
  self.grid=wp.HashGrid(32,32,32,device='cuda:0');self.grid.reserve(self.n*envs);self.grid.build(self.x,2.*model['radius'])
  self.grid_reference=wp.clone(self.x)
  self.save_initial()
 def save_initial(self):
  self.initial={k:wp.clone(getattr(self,k)) for k in ['x','v','fixed','force','alive','paid','tool','rotation','ledger','bad','peak','reaction','load','penetration_peak','action','velocity','angular_action','angular_velocity','clock']}
 def one(self,index=0):
  wp.launch(clear_step,self.n*self.envs,[self.x,self.force,self.mass,self.reaction,self.load,self.velocity,self.tool,self.action,self.angular_action,self.angular_velocity,self.rotation,self.clock,self.bad,self.dt,self.n])
  if self.recontact:
   if index%self.grid_interval==0:
    self.grid.build(self.x,2.*self.model['radius']);wp.copy(self.grid_reference,self.x)
   wp.launch(grid_motion_guard,self.n*self.envs,[self.x,self.grid_reference,self.bad,self.grid_skin,self.n])
   wp.launch(particle_contacts,self.n*self.envs,[self.grid.id,self.x,self.v,self.force,self.mass,self.ledger,self.bad,self.model['radius'],self.grid_skin,self.dt,self.n])
  wp.launch(bonds,self.nb*self.envs,[self.x,self.v,self.force,self.edge,self.rest,self.stiffness,self.mass,self.area,self.alive,self.paid,self.tool,self.velocity,self.angular_velocity,self.rotation,self.reaction,self.load,self.ledger,self.bad,self.model['h'],self.dt,self.n,self.nb,.06,self.cut])
  wp.launch(integrate,self.n*self.envs,[self.x,self.fixed,self.v,self.force,self.mass,self.tool,self.velocity,self.angular_velocity,self.rotation,self.reaction,self.load,self.ledger,self.penetration_peak,self.bad,self.dt,self.model['radius'],self.n,.06,self.knife])
  wp.launch(finish_step,self.envs,[self.reaction,self.load,self.peak,self.bad,self.tool,self.rotation,self.knife,self.stop_force])
 def graph(self,n):
  key=(n,self.dt)
  if key not in self.graphs:
   wp.load_module(device='cuda:0');wp.capture_begin()
   try:
    for index in range(n):self.one(index)
   finally:self.graphs[key]=wp.capture_end()
  return self.graphs[key]
 def step(self,action,n=200):
  duration=n*self.base_dt;a=np.asarray(action,np.float32);a=np.broadcast_to(a,(self.envs,a.shape[-1])).copy();self.last_attempts=[]
  if self.adaptive:
   if not hasattr(self,'backup'):self.backup={k:wp.empty_like(getattr(self,k)) for k in self.initial}
   for k,v in self.backup.items():wp.copy(v,getattr(self,k))
  trial_dt=self.active_dt
  while True:
   self.dt=trial_dt;self.action.assign(a[:,:3]);self.angular_action.assign(a[:,3:] if a.shape[-1]==6 else np.zeros((self.envs,3),np.float32));wp.capture_launch(self.graph(round(duration/trial_dt)));wp.synchronize();bad=self.bad.numpy();peak=self.peak.numpy()
   retry=self.adaptive and np.any(np.isin(bad,[2,4])) and np.all(peak<=self.stop_force) and trial_dt>.00005+1e-12
   self.last_attempts.append({'dt':trial_dt,'bad':bad.tolist(),'rejected':bool(retry)})
   if not retry:break
   for k,v in self.backup.items():wp.copy(getattr(self,k),v)
   trial_dt=max(trial_dt*.5,.00005);self.refinements+=1
  self.active_dt=trial_dt;self.dt=self.base_dt;self.steps+=n
  return bad
 def reset(self):
  for k,v in self.initial.items():wp.copy(getattr(self,k),v)
  self.steps=0;self.active_dt=self.base_dt;self.refinements=0
 def components(self,env=0):
  from scipy.sparse import coo_matrix
  from scipy.sparse.csgraph import connected_components
  alive=self.alive.numpy().reshape(self.envs,self.nb)[env].astype(bool);e=self.model['edges'][alive];graph=coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(self.n,self.n));return connected_components(graph,directed=False)
