"""Bounded diagnostic from recorded material state; not a coupled-run resume."""
from pathlib import Path
import sys,json,time,signal,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
out=w/'softening_element01';out.mkdir(exist_ok=True);start=time.monotonic()
def log(**row):
 row['wall_s']=time.monotonic()-start
 with (out/'progress.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def timeout(*args):raise TimeoutError('Bounded diagnostic exceeded 360 seconds')
signal.signal(signal.SIGALRM,timeout);signal.alarm(360)
try:
 import warp as wp
 from tomato_native_full_model import registry
 from tomato_pose_packet_refresh import refresh_packet
 from tomato_element_frame_live import PatchFrameLiveCAD as LiveCADCandidate
 import tomato_pose_packet_refresh as refresh_module
 wp.init();wp.set_device('cuda:0')
 checkpoint=w/'softening_replay02/checkpoint.npz';z=np.load(checkpoint);origin=np.array([-.0225,0,.0295]);rot=z['blade_rotation'];pose=np.r_[z['blade_translation']+origin,Rotation.from_matrix(rot).as_quat()];com=np.array(json.loads((w/'robot_cut02/coupling_scope.json').read_text())['tool_com_local'])
 base_force=LiveCADCandidate.force
 def traced_force(self,x,dt):
  value=base_force(self,x,dt)
  log(stage='force',dt=dt,iteration=len(self.last_trace),residual=value,previous_iteration=self.last_trace[-1] if self.last_trace else None)
  return value
 LiveCADCandidate.force=traced_force
 from tomato_element_frame_slice_engine import subcycled_engine
 g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);next(g)
 for step in range(20):
  goal=pose.copy();goal[:3]+=np.array([rot[2,2]/rot[0,2],0,-1])*.02/2400*(step+1)
  log(stage='advance',step=step);state=g.send({'pose':goal,'dt':1/2400})
  log(stage='accepted',step=step,max_damage=float(state['history'][:,1].max()));state['checkpoint_writer'](out/'accepted_checkpoint.npz',step=step)
 np.savez(out/'accepted.npz',x=state['x'],v=state['v'],history=state['history'])

except BaseException as e:
 log(stage='failure',error=repr(e),traceback=traceback.format_exc())
finally:signal.alarm(0)
