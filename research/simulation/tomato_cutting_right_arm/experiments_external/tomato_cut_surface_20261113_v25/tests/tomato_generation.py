from pathlib import Path
import sys,os,json,numpy as np,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from tomato_generator import generate
from fast_aggregation import Aggregate,vertex_fields
rows=[];checks={}
for name,scale in [('baseline',[1,1,1]),('small',[.8]*3),('large',[1.2]*3),('ellipsoid',[1.2,1/1.2,1])]:
 b,exterior=generate(scale=scale);a=Aggregate(b);out=W/'states'/('tomato_'+name);b.save(str(out)+'.npz');np.savez_compressed(str(out)+'_exterior.npz',**exterior);meta=b.tomato_metadata;meta['aggregation']=a.report;checks[name+'_mass']=meta['volume_relative_error']<1e-6;checks[name+'_one_component']=len(np.unique(b.components()[0]))==1;checks[name+'_no_cuts']=not b.history and np.all(b.codes==0);checks[name+'_affine']=a.report['affine_error']<1e-10;checks[name+'_no_unresolved']=len(a.report['unresolved_nodes'])==0
 # The same source is transformed at reset. No deformation state survives.
 checks[name+'_fresh_state']=np.max(abs(a.q))+np.max(abs(a.v))==0;rows.append(meta);print(name,json.dumps({k:v for k,v in meta.items() if k!='aggregation'}),flush=True)
out=dict(passed=all(checks.values()),checks={k:bool(v) for k,v in checks.items()},cases=rows,physical_cut=False,rl_ready=False,scope='Reset geometry and mass only; original exterior preserved. No cutting, contact or training qualification inherited.')
(W/'reports/tomato_generation.json').write_text(json.dumps(out,indent=2));assert out['passed']
