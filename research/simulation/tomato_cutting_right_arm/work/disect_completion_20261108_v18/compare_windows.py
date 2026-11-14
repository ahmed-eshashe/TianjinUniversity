from pathlib import Path
import numpy as np,json,sys
W=Path(__file__).resolve().parent;a_name,b_name=sys.argv[1:3];a=np.load(W/(a_name+'_trajectory.npz'));b=np.load(W/(b_name+'_trajectory.npz'));rows=[]
for i,t in enumerate(a['t']):
 j=int(abs(b['t']-t).argmin())
 if abs(b['t'][j]-t)>1e-10:continue
 rows.append(dict(t_s=float(t),position_m=float(np.linalg.norm(a['x'][i]-b['x'][j],axis=1).max()),velocity_m_s=float(np.linalg.norm(a['v'][i]-b['v'][j],axis=1).max()),internal_force_relative=float(np.linalg.norm(a['force'][i]-b['force'][j])/max(np.linalg.norm(b['force'][j]),1e-12))))
mx={k:max(r[k] for r in rows) for k in ['position_m','velocity_m_s','internal_force_relative']};results=[json.loads((W/(n+'_result.json')).read_text()) for n in [a_name,b_name]]
out=dict(scope='Same-mesh fresh-state timestep comparison; internal material/cohesive/closure force, not mounted-blade force',runs=[a_name,b_name],thresholds=dict(position_m=.0001,velocity_m_s=.005,internal_force_relative=.05),maxima=mx,common_end_s=rows[-1]['t_s'],complete=all(r['stop']=='completed' for r in results),wall_seconds_per_simulated_second=[r['wall_s']/max(r['rows'][-1]['sim_s'],1e-30) for r in results],rows=rows)
out['accuracy_passed']=bool(out['complete'] and mx['position_m']<=.0001 and mx['velocity_m_s']<=.005 and mx['internal_force_relative']<=.05);out['speed_passed']=bool(max(out['wall_seconds_per_simulated_second'])<=120)
(W/'timestep_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
