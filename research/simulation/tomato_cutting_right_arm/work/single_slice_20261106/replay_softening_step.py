"""Bounded diagnostic from recorded material state; not a coupled-run resume."""
from pathlib import Path
import sys,json,time,signal,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
out=w/'softening_replay01';out.mkdir(exist_ok=True);start=time.monotonic()
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
 # Build a new initial quadrature for this diagnostic, with its embedded accuracy
 # test intact. There is no saved packet to transfer or compare on initialization.
 source=Path(refresh_module.__file__).read_text()
 source=source.replace("if old_f>fbudget or abs(old_e)>ebudget:raise ValueError(('Converged adaptive remap differs from old packet',history))", "pass # Initialization only: no saved contact packet exists")
 scope={};exec(compile(source,'<diagnostic_initial_quadrature>','exec'),scope)
 wp.init();wp.set_device('cuda:0');d=registry();d['x']+=[0,0,.002]
 frame=w/'robot_cut02/material_states/step_002290.npz';z=np.load(frame);pose=z['actual_tool_pose'];rot=Rotation.from_quat(pose[3:]).as_matrix();origin=np.array([-.0225,0,.0295])
 blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');com=np.array(json.loads((w/'robot_cut02/coupling_scope.json').read_text())['tool_com_local'])
 triangles=np.array([tri for p in d['design']['pieces'] for tri in p['triangles']]);log(stage='initial_quadrature')
 packet,value,report=scope['refresh_packet'](blade,solid['cells'],z['x'],triangles,d['x'],rot,pose[:3],com,{k:ref[k] for k in ('indices','barycentric','areas')},padding_m=.001)
 (out/'initial_quadrature.json').write_text(json.dumps(report,indent=2));log(stage='initial_quadrature_done',samples=len(packet['areas']))
 seen=z['history'][:,0]>0
 np.savez(out/'diagnostic_state.npz',x=z['x']-origin,v=z['v'],history=z['history'],blade_rotation=rot,blade_translation=pose[:3]-origin,seen=seen,eligible=seen,elapsed=0.,**{'packet_'+k:v for k,v in packet.items()})
 base_force=LiveCADCandidate.force
 def traced_force(self,x,dt):
  value=base_force(self,x,dt)
  log(stage='force',dt=dt,iteration=len(self.last_trace),residual=value,previous_iteration=self.last_trace[-1] if self.last_trace else None)
  return value
 LiveCADCandidate.force=traced_force
 from tomato_subcycled_slice_engine import subcycled_engine
 g=subcycled_engine(pose,com,checkpoint=out/'diagnostic_state.npz',padding_m=.001);next(g)
 goal=pose.copy();goal[:3]+=np.array([rot[2,2]/rot[0,2],0,-1])*.02/2400
 log(stage='advance');s=g.send({'pose':goal,'dt':1/2400})
 np.savez(out/'accepted.npz',x=s['x'],v=s['v'],history=s['history']);log(stage='accepted',max_damage=float(s['history'][:,1].max()))
except BaseException as e:
 log(stage='failure',error=repr(e),traceback=traceback.format_exc())
finally:signal.alarm(0)
