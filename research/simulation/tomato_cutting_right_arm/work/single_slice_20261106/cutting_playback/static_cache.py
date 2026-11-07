from pathlib import Path
import numpy as np
from pxr import Usd
w=Path(__file__).parent;s=Usd.Stage.Open(str(w/'recorded_incomplete_cut.usda'));records=[];paths=[];times=None
for p in s.Traverse():
 for a in p.GetAttributes():
  ts=a.GetTimeSamples()
  if not ts:continue
  if times is None:times=ts
  paths.append(str(a.GetPath()));records.append(np.array([a.Get(t) for t in ts]));first=a.Get(ts[0]);a.Clear();a.Set(first)
np.savez(w/'playback_arrays.npz',times=times,paths=np.array(paths),**{'a'+str(i):a for i,a in enumerate(records)})
s.GetRootLayer().Export(str(w/'playback_static.usdc'))
print(len(paths))
