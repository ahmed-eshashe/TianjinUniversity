from pathlib import Path
import json,numpy as np
rng=np.random.default_rng(42);n=100000;R=.0002;r=.0001;b=.4*(R-r);w=rng.dirichlet(np.ones(4),n);delta=rng.normal(size=(n,4,3));delta*=rng.uniform(0,b,size=(n,4,1))/np.linalg.norm(delta,axis=2)[:,:,None];mapped=np.einsum('ni,nij->nj',w,delta);maximum=float(np.linalg.norm(mapped,axis=1).max());assert maximum<=b
lower=R-2*b;assert lower>r
result=dict(samples=n,positive_convex_embedding_maximum_displacement_m=maximum,physical_bound_m=b,detection_radius_m=R,interaction_radius_m=r,undetected_pair_minimum_end_distance_m=lower,remaining_activation_clearance_m=lower-r,known_pair_minimum_fraction=.2,scope='Analytic Lipschitz/convex-combination motion bound plus random embedding checks; assumes complete detector candidates and excludes separately declared local topology filters. Not a general IPC/CCD certificate.')
Path('work/integration_20261102/contact_motion_bound_check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
