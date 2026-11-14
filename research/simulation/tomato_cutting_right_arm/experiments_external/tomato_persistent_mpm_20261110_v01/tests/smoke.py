import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from reference import block,Reference
from backend import Backend
X=block(6);a=Backend(X);b=Reference(X);vel=np.tile([.01,.002,-.004],(len(X),1));a.set_state(v=vel);b.v=vel.copy()
a.step(5e-5,10);[b.step(5e-5) for _ in range(10)];s=a.check()
print('x',abs(s['x']-b.x).max(),'v',abs(s['v']-b.v).max(),'F',abs(s['F']-b.F).max(),a.memory())
