from pathlib import Path
import sys,json,hashlib
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'))
from tomato_checkpoint_learning_record import record
w=r/'work/single_slice_20261106';out=Path(__file__).parent;frames={}
for run in ['robot_cut11','robot_cut12','robot_cut13','robot_cut14','robot_cut15']:
 names=json.loads((w/run/'runtime_joint_limits.json').read_text())['names']
 for p in sorted((w/run/'checkpoints').glob('step_*.json')):
  m=json.loads(p.read_text())
  if 'robot_state' in m and p.with_suffix('.npz').exists():frames[round(m['clock'],8)]=(p,m,names)
rows=[];truth=[]
for clock,(p,m,names) in sorted(frames.items()):
 obs=record(m,names);obs.update(episode_id='single_slice_continuous_attempt_11_to_15',sample_index=len(rows),source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),joint_names=names);rows.append(obs)
 truth.append({'sample_index':obs['sample_index'],'time_s':clock,'material_checkpoint':str(p.with_suffix('.npz')),'sha256':hashlib.sha256(p.with_suffix('.npz').read_bytes()).hexdigest(),'simulated_reaction_canonical':m.get('reaction'),'applied_previous_wrench_world':m.get('applied_wrench'),'scope':'Evaluator only; not a measured wrist sensor; not actor input'})
(out/'observations.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));(out/'evaluator_provenance.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in truth));summary={'samples':len(rows),'episodes':1,'split':'unassigned; all resumed segments must remain in one split','successful_demonstrations':0,'action_labels_available':False,'training_ready':False,'source_runs':['robot_cut11','robot_cut12','robot_cut13','robot_cut14','robot_cut15'],'scope':'Read-only sparse checkpoint export; no new measurements, actions, physics or reset qualification','simulation_resume_checkpoint':'robot_cut15/checkpoints/step_005425.npz'};(out/'export_report.json').write_text(json.dumps(summary,indent=2));print(summary)
