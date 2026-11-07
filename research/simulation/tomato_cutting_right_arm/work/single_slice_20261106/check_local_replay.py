from pathlib import Path
import sys,json,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'local_replay01';out.mkdir(exist_ok=True);source=w/'robot_cut08';checkpoint=source/'checkpoints/step_003250.npz';z=np.load(checkpoint);route=json.loads((w/'clear_entry_robot_plan_v8.json').read_text());F=np.array(route['target_rotation']);P=np.array(route['target_translation']);com=np.array(json.loads((source/'coupling_scope.json').read_text())['tool_com_local']);start=time.monotonic();rows=[]
try:
 from tomato_local_slice_engine import subcycled_engine
 pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()];g=subcycled_engine(pose,com,checkpoint=checkpoint,padding_m=.001,diagnostic_directory=out);state=next(g)
 for k in range(3251,3259):
  row=json.loads((source/'robot_intervals'/f'step_{k:06d}.json').read_text());tp=np.array(row['after']['tool_pose']);R=Rotation.from_quat(tp[3:]).as_matrix();pose=np.r_[F.T@(tp[:3]-P),Rotation.from_matrix(F.T@R).as_quat()];state=g.send(dict(pose=pose,dt=1/2400));row=dict(step=k,elapsed=state['elapsed'],wall_s=time.monotonic()-start,maximum_damage=float(state['history'][:,1].max()));rows.append(row);(out/'progress.json').write_text(json.dumps(row));print(row,flush=True)
 state['checkpoint_writer'](out/'accepted_checkpoint.npz');baseline=np.load(source/'material_before_failed_microstep.npz');status=next(q for q in json.loads((source/'cutting_trace.json').read_text()) if q['step']==3258);ref=np.array(status['current_reaction_canonical']);error=dict(position_m=float(np.linalg.norm(state['x']-(baseline['x']+[-.0225,0,.0295]),axis=1).max()),velocity_m_s=float(np.linalg.norm(state['v']-baseline['v'],axis=1).max()),damage=float(abs(state['history'][:,1]-baseline['history'][:,1]).max()),opening_m=float(abs(state['history'][:,0]-baseline['history'][:,0]).max()),force_N=float(np.linalg.norm(state['wrench'][:3]-ref[:3])));c=json.loads((w/'local_replay_criteria.json').read_text());passed=error['position_m']<=c['position_difference_max_m'] and error['velocity_m_s']<=c['velocity_difference_max_m_s'] and error['damage']<=c['damage_difference_max'] and error['opening_m']<=c['opening_difference_max_m'] and error['force_N']<=.01*np.linalg.norm(ref[:3])+1e-5
 if not passed:raise ValueError(('Numerical sensitivity bounds failed',error))
 meta=json.loads((source/'material_before_failed_microstep.json').read_text());assert meta['completed_interval']==0.;state=g.send(dict(pose=meta['goal_pose'],dt=meta['outer_interval']));state['checkpoint_writer'](out/'after_former_failure.npz')
 result=dict(passed=True,accepted_reference_intervals=len(rows),original_failed_interval_passed=True,errors=error,criteria=c,wall_s=time.monotonic()-start,scope='Measured-pose numerical diagnostic only; physical law unchanged; not a coupled cut or experimental qualification')
except BaseException as e:result=dict(passed=False,error=repr(e),traceback=traceback.format_exc(),accepted_intervals=len(rows),wall_s=time.monotonic()-start)
(out/'result.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
