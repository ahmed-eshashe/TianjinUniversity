from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from volume_guard_corrected import WholeVolumeGuard
class Cube:
    vertices=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)*.001
    triangles=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]])
    rotation=np.eye(3)
rows=[]
for depth,expected in [(60e-6,True),(85e-6,True),(90e-6,True),(94e-6,True),(97e-6,True),(102e-6,False)]:
 q=np.array([[.001-depth,0,0],[.001-depth+1e-7,0,0],[.001-depth,1e-7,0],[.001-depth,0,1e-7]])
 guard=WholeVolumeGuard(Cube(),np.array([[0,1,2,3]]))
 proof=guard.check(q,np.zeros(3),step_motion=1e-6)
 assert proof['passed']==expected
 rows.append(dict(depth_m=depth,expected_pass=expected,proof=proof))
out=dict(scope='Proof-method controls: 80 um cache target must not replace 100 um physical limit',passed=True,rows=rows)
(W/'guard_corrected_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
