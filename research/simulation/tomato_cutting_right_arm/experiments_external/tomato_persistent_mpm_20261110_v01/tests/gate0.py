from pathlib import Path
import json,subprocess,sys,time,numpy as np,datetime
W=Path(__file__).resolve().parents[1];R=W/'runs/gate0';R.mkdir(exist_ok=False)
records=[]
for angle in (0,17):
 for mode in ('held','absent','far'):
  prefix=R/f'{mode}_{angle}';t=time.monotonic()
  p=subprocess.run([str(W/'cressim_control'),mode,'mls',str(prefix),'1','0.0001',str(angle)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=600)
  prefix.with_suffix('.log').write_text(p.stdout)
  a=np.genfromtxt(str(prefix)+'_trace.csv',delimiter=',',names=True)
  j=json.loads(Path(str(prefix)+'_summary.json').read_text());m=float(np.max(abs(a['vz1']))/.01)
  records.append({'mode':mode,'angle_deg':angle,'peak_undriven_velocity_fraction':m,'final_driven_velocity_fraction':float(a['vz0'][-1]/.01),'exit':p.returncode,'mass_relative_error':abs(j['final_mass']/j['initial_mass']-1),'seconds':time.monotonic()-t,'evidence':str(prefix)})
checks={'absent_failure_detected':all(r['peak_undriven_velocity_fraction']>.01 for r in records if r['mode']=='absent'),'wide_gap_isolates':all(r['peak_undriven_velocity_fraction']<=.01 for r in records if r['mode']=='far'),'held_control_finite':all(r['exit']==0 for r in records if r['mode']=='held'),'mass_unchanged':all(r['mass_relative_error']<=1e-6 for r in records)}
result={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'cases':records,'meaning':'Gate0 harness sensitivity and architecture readiness only; rotated held-tool leakage is retained as an upstream limitation','timestamp':datetime.datetime.now().astimezone().isoformat()}
(W/'gate0.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
