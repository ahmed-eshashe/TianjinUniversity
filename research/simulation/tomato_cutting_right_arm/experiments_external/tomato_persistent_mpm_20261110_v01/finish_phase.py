from pathlib import Path
import json,datetime,hashlib,os,shutil
W=Path(__file__).resolve().parent
now=datetime.datetime.now().astimezone();start=datetime.datetime.fromisoformat('2026-11-10T18:21:26+08:00')
for filename in ['gate0.json','intact_controls.json','persistent_cut_controls.json','gate2_supplement.json']:
 assert json.loads((W/filename).read_text())['status']=='pass',filename
assert json.loads((W/'preservation_check.json').read_text())['pass']
q=json.loads((W/'persistent_cut_controls.partial.json').read_text());pid=q['pid'];alive=False
try:
 cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
 alive='tests/gate2.py' in cmd
except FileNotFoundError:pass
assert not alive,'test worker still running'
status={'updated':now.isoformat(),'status':'initial_phase_complete_component_pass','phase_started':start.isoformat(),'elapsed_wall_minutes':(now-start).total_seconds()/60,'budget_hours':8,'worker_pid':None,'simulation_running':False,'last_completed_gate':2,'gates':{str(i):('pass_component_scope' if i<=2 else 'pending') for i in range(9)},'evidence':{0:'gate0.json',1:'intact_controls.json',2:['persistent_cut_controls.json','gate2_supplement.json']},'next_action':'Gate 3: physical resistance/failure and tool/fragment contact; measured speed remains a major unresolved issue','adopted':False,'physical_tomato_qualified':False,'RL_ready':False,'existing_simulation_setup_changed':False,'experimental_validation':'pending','report':str(W/'REPORT.txt')}
(W/'status.json').write_text(json.dumps(status,indent=2))
# The only write outside this isolated experiment is plan-tracking metadata.
P=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm/docs/rl/ASTRA_HIGH_TOMATO_MODEL_EXECUTION_STATUS_20261110.json')
snapshot=W/'reports/original_plan_status.json'
if not snapshot.exists():shutil.copy2(P,snapshot)
p=json.loads(P.read_text());p.update({'status':'initial_phase_complete_component_pass','updated':now.isoformat(),'candidate_directory':str(W),'execution_status_path':str(W/'status.json'),'new_candidate_adopted':False,'existing_solver_modified':False,'simulation_running':False,'experimental_validation':'pending','runtime_qualification':'unresolved; 61-88 wall seconds per simulated second in short physics-only windows'})
for g in p['gates']:
 if g['id']<3:
  g['status']='pass_component_scope';f=status['evidence'][g['id']];g['evidence']=[str(W/x) for x in (f if isinstance(f,list) else [f])]
P.write_text(json.dumps(p,indent=2))
paths=[]
for folder in ['src','tests','configs','runs','reports']:
 paths += [f for f in (W/folder).rglob('*') if f.is_file()]
paths += [f for f in W.glob('*') if f.is_file() and f.name not in ['evidence_hashes.json','cressim_control']]
paths += [W/'upstream_diagnostic/cutoff_only.patch']
hashes={str(f.relative_to(W)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(set(paths))}
(W/'evidence_hashes.json').write_text(json.dumps({'sealed_at':now.isoformat(),'files':hashes},indent=2))
print(json.dumps({'status':status['status'],'elapsed_minutes':status['elapsed_wall_minutes'],'artifacts_hashed':len(hashes),'plan_status_updated':str(P),'worker_running':alive},indent=2))
