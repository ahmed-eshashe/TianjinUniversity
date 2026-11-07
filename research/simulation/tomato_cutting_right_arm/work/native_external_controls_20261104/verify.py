from pathlib import Path
import csv,json,numpy as np,hashlib
w=Path(__file__).resolve().parent;r=w.parents[1];M=np.array([[5.,3.],[3.,3.]]);results={}
for name in ['zero','driven_on']:
 d=w/name;lines=(d/'external.csv').read_text().splitlines();assert lines[0]=='TOMATO_EXTERNAL_IMPULSE_TRACE_V1' and lines[-1]=='END count=128 dropped=0 passes=64';rows=list(csv.DictReader(lines[1:-1]));assert len(rows)==128;states=list(csv.DictReader((d/'states.csv').open()));previous=np.zeros(2);checks=[];force=np.array([0.,0.]) if name=='zero' else np.array([1.,2.])
 for i in range(2):
  block=[x for x in rows if i*32<int(x['event'])<=(i+1)*32];J=np.zeros(2)
  for x in block:
   assert all(np.isfinite(float(v)) for k,v in x.items() if k!='articulation');J[int(x['dof'])]+=float(x['actuation_impulse'])
  v=np.array([float(states[i]['v1']),float(states[i]['v2'])]);momentum_error=float(np.max(abs(M@(v-previous)-J)));work=float(J@(.5*(v+previous)));dk=float(.5*(v@M@v-previous@M@previous));expected=np.linalg.solve(M,force)*(i+1)/240
  check={'step':i,'actuation_impulse':J.tolist(),'momentum_error':momentum_error,'energy_error_j':abs(work-dk),'analytic_velocity_error':float(np.max(abs(v-expected))),'impulse_error':float(np.max(abs(J-force/240)))};check['passed']=momentum_error<=1e-7 and abs(work-dk)<=1e-8 and check['analytic_velocity_error']<=1e-7 and check['impulse_error']<=1e-7;checks.append(check);previous=v
 results[name]=checks
results['off_on_states_identical']=(w/'driven_off/states.csv').read_bytes()==(w/'driven_on/states.csv').read_bytes();results['all_exits_clean']=all(json.loads((w/n/'result.json').read_text())['exit_code']==0 and not (w/n/'stderr.log').read_text() for n in ['zero','driven_off','driven_on']);results['fixture_passed']=all(x['passed']for n in ['zero','driven_on']for x in results[n]) and results['off_on_states_identical'] and results['all_exits_clean'];results['robot_work_qualified']=False;results['limitation']='Constant-mass, no gravity/damping/contact/implicit drives. Endpoint midpoint identity valid here; not a proof for the full robot.'
(w/'verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
