from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
b=Body(n=2,h=.003);b.split([1,0,0],.0001);a=Aggregate(b);A,B=sys.argv[1:3];r=json.loads((W/'runs'/A/'result.json').read_text());s=json.loads((W/'runs'/B/'result.json').read_text());x=np.load(W/'runs'/A/'trajectory.npz');y=np.load(W/'runs'/B/'trajectory.npz');assert len(r['rows'])==len(s['rows'])==52
errorq=(x['q']-y['q']);errorv=x['v']-y['v'];pos=0.;vRMS=0.;localmax=0.
for q,v in zip(errorq,errorv):
 q=a.E@q;v=a.E@v;maxvs=[]
 for p,ids,inv in zip(b.polys,b.ids,b.inv):
  N=np.c_[np.ones(len(p)),p]@inv;pos=max(pos,float(np.linalg.norm(N@q[ids],axis=1).max()));maxvs.append(float(np.linalg.norm(N@v[ids],axis=1).max()))
 vRMS=max(vRMS,float(np.sqrt(np.array(maxvs)**2@b.V/b.V.sum())));localmax=max(localmax,max(maxvs))
def rel(k,floor):
 aa=np.array([v[k] for v in r['rows']]);bb=np.array([v[k] for v in s['rows']]);diff=np.linalg.norm(aa-bb,axis=1) if aa.ndim>1 else abs(aa-bb);scale=np.linalg.norm(bb,axis=1) if bb.ndim>1 else abs(bb);return float(np.max(diff/np.maximum(scale,floor)))
metrics={'position_m':pos,'material_weighted_velocity_upper_RMS_m_s':vRMS,'max_physical_vertex_velocity_error_m_s':localmax,'force_relative':rel('reaction',1e-4),'impulse_relative':rel('material_impulse',1e-7),'tool_work_relative':rel('tool_work_J',1e-8),'friction_work_relative':rel('friction_J',1e-8)};checks={k:v<(.0001 if k=='position_m' else .005 if k=='material_weighted_velocity_upper_RMS_m_s' else .05) for k,v in metrics.items() if k!='max_physical_vertex_velocity_error_m_s'};out={'a':A,'b':B,'metrics':metrics,'checks':checks,'passed':all(checks.values())};(W/'reports'/sys.argv[3]).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
