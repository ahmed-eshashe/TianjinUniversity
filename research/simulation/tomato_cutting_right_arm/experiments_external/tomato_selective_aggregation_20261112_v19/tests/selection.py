from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body,strain_audit
from aggregation import Aggregate
rows=[]
for name,n,d,front in [('oblique',[1,.27,.13],.001,None),('partial',[1,.27,.13],.001,([0,-1,0],0))]+[(f'corner{d}',[1,1,1],d,None) for d in [1.3e-4,1e-5,1e-6,1e-7]]:
 b=Body(n=4);b.split(n,d,front=front);a=Aggregate(b);row={'case':name,'base':strain_audit(b),'selected':a.audit(),'construction':a.report};rows.append(row);print(name,'aggregated',a.report['aggregated_nodes'],'massfraction',a.report['aggregated_original_inertia_fraction'],'dt',row['base']['linearized_stability_dt_s'],row['selected']['linearized_stability_dt_s'],flush=True)
(W/'selection.json').write_text(json.dumps({'rows':rows,'speed_qualified':False},indent=2))
