from pathlib import Path
import numpy as np,json,hashlib,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1]
def compare(a,b):
 fields={};count=0
 for p in sorted(a.glob('interval_*.npz')):
  with np.load(p) as x,np.load(b/p.name) as y:
   assert set(x.files)==set(y.files)
   for k in x.files:fields[k]=fields.get(k,True) and bool(np.array_equal(x[k],y[k]))
  count+=1
 return {'intervals':count,'fields':fields,'all_identical':all(fields.values()) and count==120}
result={'off_on':compare(w/'capture_off03',w/'capture_on01'),'original_off':compare(r/'runs/native/motor_effort_capture_20261102_01',w/'capture_off03'),'trace':json.loads(subprocess.check_output(['python3',str(w/'validate_trace.py'),str(w/'capture_on01/native_trace.csv')],text=True)),'supervisor_passes':{n:json.loads((w/n/'supervisor_result.json').read_text())['passed'] for n in ['capture_off03','capture_on01']},'production_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in json.loads((w/'build_manifest.json').read_text())['production_pins'].items()),'motor_work_qualified':False,'clock_mapping_qualified':False}
result['instrumentation_fixture_passed']=result['off_on']['all_identical'] and result['original_off']['all_identical'] and all(result['supervisor_passes'].values()) and result['production_unchanged']
(w/'shutdown_resolution_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
