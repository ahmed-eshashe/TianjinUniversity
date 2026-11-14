from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
from separation import SeparationEvaluator
s=FullSurface();e=SeparationEvaluator(s);h=np.zeros((47,2));failed=np.c_[s.fail.numpy(),np.ones(47)];rows=[]
for name,hist,expected in [('intact',h,False),('one_remaining_bridge',np.r_[failed[:46],h[46:]],False),('partial_damage',np.c_[np.full(47,.002),np.full(47,2/3)],False),('known_disconnected_fixture',failed,True)]:
 r=e.evaluate(hist);rows.append(dict(name=name,expected=expected,result=r,passed=r['separation_passed']==expected))
x=s.mesh['x'].copy();x[e.side_nodes[1],0]+=.02;r=e.evaluate(h,x);rows.append(dict(name='visible_gap_with_live_bonds',passed=not r['separation_passed']))
# A separate isolated tiny particle cannot make a live-bond assembly a slice.
import copy
s2=copy.copy(s);s2.mesh=dict(s.mesh);s2.mesh['x']=np.r_[s.mesh['x'],[[1,1,1]]];s2.mesh['mass']=np.r_[s.mesh['mass'],[1e-12]];tiny=SeparationEvaluator(s2).evaluate(h);rows.append(dict(name='isolated_tiny_fragment',result=tiny,passed=not tiny['separation_passed']))
out=dict(scope='Evaluator synthetic positive/negative fixtures only; NOT actual tomato separation',rows=rows,passed=all(r['passed'] for r in rows));(W/'separation_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
