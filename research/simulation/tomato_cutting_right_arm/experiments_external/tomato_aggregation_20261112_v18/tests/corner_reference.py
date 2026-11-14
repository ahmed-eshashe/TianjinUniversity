"""Matched small-state stability spectrum, not a speed or accuracy benchmark."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body,strain_audit
from aggregation import Aggregate
rows=[]
for d in [1.3e-4,1e-5,1e-6,1e-7]:
 b=Body(n=4);b.split([1,1,1],d);r=strain_audit(b);a=Aggregate(b);aa=a.audit();row={'offset_m':d,'n':4,'extent_m':.024,'h_m':.006,'v17':r,'v18':aa};rows.append(row);print(d,r['linearized_stability_dt_s'],aa['linearized_stability_dt_s'],flush=True)
(W/'corner_reference.json').write_text(json.dumps({'rows':rows,'linearized_only':True,'qualified_timestep':False,'physical_cut':False},indent=2))
