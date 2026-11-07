from pathlib import Path
import json,numpy as np
maximum=1/2400;cap=.0001953125;rows=[]
for k in range(20):
 completed=0.;count=0
 while completed<maximum-1e-15:
  remaining=maximum-completed;micro=remaining/max(1,int(np.ceil(remaining/cap)));assert micro<=cap*(1+1e-14);completed+=micro;count+=1
 assert abs(completed-maximum)<1e-15
 cap=min(maximum,cap*1.25);rows.append(dict(interval=k,substeps=count,cap=cap))
assert rows[4]['substeps']==1
result=dict(passed=True,original_stalled_cap_s=.0001953125,full_interval_preserved=True,recovered_to_maximum=True,rows=rows)
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2));print(result)
