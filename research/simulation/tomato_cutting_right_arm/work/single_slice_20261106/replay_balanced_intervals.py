from pathlib import Path
import sys,json,time,signal,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'balanced_replay01';out.mkdir(exist_ok=False);source=w/'robot_cut03';checkpoint=source/'checkpoints/step_001500.npz';z=np.load(checkpoint);meta=json.loads(checkpoint.with_suffix('.json').read_text());route=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());F=np.array(route['target_rotation']);P=np.array(route['target_translation']);com=np.array(json.loads((source/'coupling_scope.json').read_text())['tool_com_local']);start=time.monotonic();records=[]
def timeout(*_):raise TimeoutError('Diagnostic wall bound')
signal.signal(signal.SIGALRM,timeout);signal.alarm(1200)
try:
 from tomato_balanced_slice_engine import subcycled_engine
 pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);next(g)
 for k in range(1501,1544):
  row=json.loads((source/'robot_intervals'/f'step_{k:06d}.json').read_text());tp=np.array(row['after']['tool_pose']);R=Rotation.from_quat(tp[3:]).as_matrix();pose=np.r_[F.T@(tp[:3]-P),Rotation.from_matrix(F.T@R).as_quat()];state=g.send({'pose':pose,'dt':1/2400});record=dict(step=k,elapsed=state['elapsed'],maximum_damage=float(state['history'][:,1].max()),wall_s=time.monotonic()-start);records.append(record);(out/'progress.json').write_text(json.dumps(record));print(record,flush=True)
  state['checkpoint_writer'](out/'accepted_checkpoint.npz',source_robot_step=k)
 result=dict(passed=True,accepted_steps=len(records),completed_original_failed_increment=True,scope='Measured-pose material replay only; fresh robot continuation still required')
except BaseException as e:result=dict(passed=False,error=repr(e),traceback=traceback.format_exc(),accepted_steps=len(records))
finally:signal.alarm(0)
(out/'result.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
