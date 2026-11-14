"""Read-only diagnostic of error norms. Does not alter any acceptance criterion."""
from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from reference_gpu_v17 import GPU
from aggregation import Aggregate,vertex_fields
from response import snap,diff,passes
start=time.perf_counter();b=Body(n=4);b.u[:,1]=-.01*b.grid[:,1];b.u[:,0]=.005*b.grid[:,2];b.split([1,-1,1],1e-6);a=Aggregate(b,1e-16);g=GPU(b.clone(),.0625e-6);gh=GPU(b.clone(),.03125e-6);ptr=np.r_[0,np.cumsum([len(p) for p in b.polys])];rows=[];ta=[];tr=[];trh=[]
e0=b.metrics()['U'];m=b.rho*b.V
for sample in range(20):
 for _ in range(160):a.step(1.5625e-6)
 g.step(4000);g.export();gh.step(8000);gh.export();s=snap(a.body);r=snap(g.body);rh=snap(gh.body);ta.append(s);tr.append(r);trh.append(rh)
 dv=np.linalg.norm(s['v']-rh['v'],axis=1);dx=np.linalg.norm(s['x']-rh['x'],axis=1);pm=np.maximum.reduceat(dv,ptr[:-1]);weighted_bound=float(np.sqrt(m@(pm*pm)/m.sum()));violation=pm>.005
 rows.append({'time_s':(sample+1)*.00025,'position_max_m':float(dx.max()),'velocity_max_m_s':float(dv.max()),'velocity_mass_weighted_RMS_upper_bound_m_s':weighted_bound,'material_mass_fraction_in_regions_exceeding_pointwise_limit':float(m[violation].sum()/m.sum()),'energy_residual_relative':abs(s['energy']-e0)/e0})
ref=diff(tr,trh);cross=diff(ta,trh);result={'status':'diagnostic_only_no_criterion_change','duration_s':.005,'sample_interval_s':.00025,'reference_halfstep':ref,'reference_halfstep_pass':passes(ref),'cross_model':cross,'max_mass_weighted_RMS_upper_bound_m_s':max(r['velocity_mass_weighted_RMS_upper_bound_m_s'] for r in rows),'max_violating_material_mass_fraction':max(r['material_mass_fraction_in_regions_exceeding_pointwise_limit'] for r in rows),'energy_residual_relative_max':max(r['energy_residual_relative'] for r in rows),'rows':rows,'wall_s':time.perf_counter()-start}
(W/'velocity_metric_audit.json').write_text(json.dumps(result,indent=2));a.body.save(W/'states/heldout_candidate_5ms.npz');gh.body.save(W/'states/heldout_reference_5ms.npz');print({k:v for k,v in result.items() if k!='rows'},flush=True)
