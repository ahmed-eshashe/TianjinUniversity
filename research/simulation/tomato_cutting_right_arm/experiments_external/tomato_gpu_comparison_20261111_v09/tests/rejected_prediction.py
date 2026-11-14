"""Negative control: reject a volume-invalid prediction from a valid start."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from multicut import MultiCut
from reference import block
from gpu_backend import GPUReference,wp
def make():
    g=GPUReference(MultiCut(block(8,.0015)))
    v=np.zeros((g.ng,3));v[:,1]=-.2/g.dt*g.q.numpy()[:,1];g.v.assign(v)
    return g
a=make()
for _ in range(8):a.one()
wp.synchronize_device(a.device)
accepted=int(a.clock.numpy()[0]);flag=int(a.bad.numpy()[0])
b=make();before={n:getattr(b,n).numpy() for n in ['q','v','impulse','moment','clock']};rejected=False
try:b.step(8)
except RuntimeError:rejected=True
checks={'late_prediction_detected':flag!=0 and 0<accepted<8,'trial_rejected':rejected,'all_state_rolled_back':all(np.array_equal(v,getattr(b,n).numpy()) for n,v in before.items()) and b.steps==0}
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'unwrapped_kernel_accepted_steps_before_guard':accepted,'guard_code':flag,'scope':'Deliberately excessive inward velocity, valid initial geometry. This is a rejection test, not an allowed action or a physical cutting trajectory.'}
(W/'rejection_control.json').write_text(json.dumps(out,indent=2));print(out);assert all(checks.values())
