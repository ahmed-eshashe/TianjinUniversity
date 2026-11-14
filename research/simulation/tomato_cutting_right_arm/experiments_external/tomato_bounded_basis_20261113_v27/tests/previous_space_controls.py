"""Existing cracks must retain their complete admissible displacement space."""
from pathlib import Path
import os,sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from local_continuity import Aggregate
paths=[Path('/home/omen/Documents/Codex/experiments/tomato_local_continuity_20261113_v26/runs/paid_opening_r1/event_candidate.npz'),W/'runs/space_guard_matched_3ms/last_accepted.npz']
rows=[]
for p in paths:
 b=Body.restore(p);a=Aggregate(b);audit=a.audit();checks=dict(previous_space=a.report['previous_space_error']<1e-9,positive_mass=audit['min_mass_eigenvalue']>0,elastic_rank=audit['rank']==audit['expected_rank'],mass=a.report['mass_relative_error']<1e-6,projection_position=a.transfer['position_m']<1e-4,projection_velocity=a.transfer['weighted_velocity_bound_m_s']<.005)
 rows.append(dict(input=str(p),checks=checks,report=a.report,audit=audit))
report=dict(passed=all(all(x['checks'].values()) for x in rows),cases=rows,scope='Preserve all previously admissible affine material fields, not only the currently sampled displacement. No crack-opening or full-slice qualification is inferred from low trajectory error alone.');(W/'reports/previous_space_controls.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item() if hasattr(x,"item") else x));print(json.dumps(report,indent=2,default=lambda x:x.item() if hasattr(x,"item") else x));assert report['passed']
