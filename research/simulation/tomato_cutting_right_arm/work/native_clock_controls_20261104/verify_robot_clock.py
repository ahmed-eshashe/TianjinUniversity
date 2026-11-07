from pathlib import Path
import json,csv,subprocess,hashlib,numpy as np
w=Path(__file__).resolve().parent;r=w.parents[1];old=r/'work/native_instrumentation_20261102';on=w/'robot_on01';off=w/'robot_off02'
a=json.loads((on/'trace_boundaries.json').read_text());m={x['label']:x['pass_count'] for x in a};ordering=json.loads((on/'ordering.json').read_text());lines=(on/'native_trace.csv').read_text().splitlines();rows=list(csv.DictReader(lines[1:-1]));mapping={int(x['dof']):int(x['link']) for x in rows};expected={b:ordering['joint_child_backend'][u] for u,b in enumerate(ordering['user_to_backend_joint'])}
def same(x,y):
 for i in range(120):
  with np.load(x/f'interval_{i:03d}.npz') as a,np.load(y/f'interval_{i:03d}.npz') as b:
   if set(a.files)!=set(b.files) or not all(np.array_equal(a[k],b[k]) for k in a.files):return False
 return True
result={'initialization_passes':m['after_robot_initialization']-m['before_robot_initialization'],'monitor_passes':m['after_monitor_control']-m['after_robot_initialization'],'captured_steps':120,'every_capture_step_has_40_passes':all(m[f'before_step_{i}']==240+40*i and m[f'after_step_{i}']==280+40*i for i in range(120)),'dof_child_link_matches_backend_order':mapping==expected,'observed_mapping':mapping,'expected_mapping':expected,'off_on_arrays_identical':same(off,on),'original_arrays_identical':same(off,r/'runs/native/motor_effort_capture_20261102_01'),'supervisors_passed':all(json.loads((p/'supervisor_result.json').read_text())['passed'] for p in [off,on]),'trace_sanity':json.loads(subprocess.check_output(['python3',str(old/'validate_trace.py'),str(on/'native_trace.csv')],text=True)),'production_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in json.loads((old/'build_manifest.json').read_text())['production_pins'].items()),'motor_work_qualified':False}
result['clock_and_order_fixture_passed']=all(result[k] for k in ['every_capture_step_has_40_passes','dof_child_link_matches_backend_order','off_on_arrays_identical','original_arrays_identical','supervisors_passed','production_unchanged'])
(w/'robot_clock_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if 'mapping' not in k},indent=2))
