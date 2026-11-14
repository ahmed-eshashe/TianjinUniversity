from pathlib import Path
import json,hashlib,datetime,numpy as np
W=Path(__file__).resolve().parents[1];run=W/'runs'
import sys;sys.path.insert(0,str(W/'src'))
from compiled_body import Body
b=Body(n=2,h=.003)
def compare(A,B):
 a=json.loads((run/A/'result.json').read_text());c=json.loads((run/B/'result.json').read_text());sa=np.load(run/A/'trajectory.npz');sc=np.load(run/B/'trajectory.npz');fa=np.array([r['reaction'] for r in a['rows']]);fc=np.array([r['reaction'] for r in c['rows']]);fe=np.linalg.norm(fa-fc,axis=1)/np.maximum(np.linalg.norm(fc,axis=1),1e-4)
 dx=sa['q']-sc['q'];dv=sa['v']-sc['v'];local=np.linalg.norm(dv[:,b.ids],axis=3).max(axis=2);vrms=np.sqrt(np.sum(local**2*b.V,axis=1)/sum(b.V))
 def rel(key, floor):
  aa=np.array([r[key] for r in a['rows']]);cc=np.array([r[key] for r in c['rows']]);return float(np.max(np.linalg.norm(aa-cc,axis=1)/np.maximum(np.linalg.norm(cc,axis=1),floor))) if aa.ndim>1 else float(np.max(abs(aa-cc)/np.maximum(abs(cc),floor)))
 metrics={'position_m':float(np.linalg.norm(dx,axis=2).max()),'velocity_material_weighted_upper_RMS_m_s':float(vrms.max()),'velocity_max_pointwise_m_s':float(np.linalg.norm(dv,axis=2).max()),'force_relative_max':float(fe.max()),'force_absolute_max_N':float(np.linalg.norm(fa-fc,axis=1).max()),'impulse_relative_max':rel('material_impulse',1e-7),'tool_work_relative_max':rel('tool_work_J',1e-8),'friction_work_relative_max':rel('friction_J',1e-8)}
 checks={'positions':metrics['position_m']<=1e-4,'velocity':metrics['velocity_material_weighted_upper_RMS_m_s']<=.005,'force':metrics['force_relative_max']<=.05,'impulse':metrics['impulse_relative_max']<=.05,'tool_work':metrics['tool_work_relative_max']<=.05,'friction_work':metrics['friction_work_relative_max']<=.05}
 return {'a':A,'b':B,'metrics':metrics,'checks':checks,'passed':all(checks.values()),'worst_force_time_s':a['rows'][int(fe.argmax())]['t'],'worst_force_A_N':fa[int(fe.argmax())].tolist(),'worst_force_B_N':fc[int(fe.argmax())].tolist()}
if __name__=='__main__':
 import sys
 result=compare(sys.argv[1],sys.argv[2]);print(json.dumps(result,indent=2))
 if len(sys.argv)>3:(W/'reports'/sys.argv[3]).write_text(json.dumps(result,indent=2))
