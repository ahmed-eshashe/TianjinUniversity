"""Bounded diagnostic from recorded material state; not a coupled-run resume."""
from pathlib import Path
import sys,json,time,signal,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
out=w/'softening_replay03';out.mkdir(exist_ok=True);start=time.monotonic()
def log(**row):
 row['wall_s']=time.monotonic()-start
 with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def timeout(*args):raise TimeoutError('Bounded diagnostic exceeded 360 seconds')
signal.signal(signal.SIGALRM,timeout);signal.alarm(360)
try:
 import warp as wp
 from tomato_native_full_model import registry
 from tomato_pose_packet_refresh import refresh_packet
 from tomato_live_cad_candidate import LiveCADCandidate
 import tomato_pose_packet_refresh as refresh_module
 wp.init();wp.set_device('cuda:0')
 checkpoint=w/'softening_replay02/checkpoint.npz';z=np.load(checkpoint);origin=np.array([-.0225,0,.0295]);rot=z['blade_rotation'];pose=np.r_[z['blade_translation']+origin,Rotation.from_matrix(rot).as_quat()];com=np.array(json.loads((w/'robot_cut02/coupling_scope.json').read_text())['tool_com_local'])
 base_force=LiveCADCandidate.force
 def traced_force(self,x,dt):
  value=base_force(self,x,dt)
  log(stage='force',dt=dt,iteration=len(self.last_trace),residual=value,previous_iteration=self.last_trace[-1] if self.last_trace else None)
  if len(self.last_trace)>=30:
   xx=x.numpy();rhs=self.rhs.numpy();node=int(np.argmax(np.linalg.norm(rhs,axis=1)));checks=[]
   for axis in range(3):
    for eps in (1e-8,1e-9,1e-10):
     plus=xx.copy();minus=xx.copy();plus[node,axis]+=eps;minus[node,axis]-=eps
     ep=self.energy(wp.array(plus,dtype=wp.vec3d),dt,trial=True);em=self.energy(wp.array(minus,dtype=wp.vec3d),dt,trial=True)
     checks.append(dict(node=node,axis=axis,eps=eps,observed_force=-(ep-em)/(2*eps),reported_force=float(rhs[node,axis])))
   log(stage='gradient_check',checks=checks)
   p=self.pressure;h=self.holder
   np.savez(out/'stalled_solver.npz',x=xx,previous=self.previous.numpy(),target=self.target.numpy(),rhs=rhs,dt=dt,history=h.objective_history.numpy(),eligible=h.eligible.numpy(),pressure_force=p.force.numpy(),bulk_force=self.bulk_force.numpy(),cohesive_force=h.objective_force.numpy(),self_contact_force=h.surface_contact.physical_force.numpy(),rotation=p.rotation.numpy()[0],translation=p.translation.numpy()[0],packet_indices=p.indices.numpy(),packet_barycentric=p.bary.numpy(),packet_areas=p.area.numpy())
   raise RuntimeError('Captured nonlinear iteration for independent diagnosis')
  return value
 LiveCADCandidate.force=traced_force
 from tomato_subcycled_slice_engine import subcycled_engine
 g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001);next(g)
 goal=pose.copy();goal[:3]+=np.array([rot[2,2]/rot[0,2],0,-1])*.02/2400
 log(stage='advance');s=g.send({'pose':goal,'dt':1/2400})
 np.savez(out/'accepted.npz',x=s['x'],v=s['v'],history=s['history']);log(stage='accepted',max_damage=float(s['history'][:,1].max()))
except BaseException as e:
 log(stage='failure',error=repr(e),traceback=traceback.format_exc())
finally:signal.alarm(0)
