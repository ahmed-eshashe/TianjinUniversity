from pathlib import Path
import json,numpy as np
rows=[]
for factor in [1,4,8]:
 dt=np.float32(1/(2400*factor));n=24*factor;g=np.float32(-9.81)
 for mode in ['world','relative']:
  origin=np.array([.005,.02,.035,.06],np.float32);q=origin.copy() if mode=='world' else np.zeros(4,np.float32);v=np.zeros_like(q)
  for _ in range(n):
   previous=q.copy();velocity=v+g*dt;q=q+velocity*dt;v=(q-previous)/dt
  error=float(np.max(abs(v.astype(float)+9.81*(1/(2400*factor))*n)));rows.append(dict(dt_factor=factor,storage=mode,velocity_error_m_s=error,final_v_m_s=v.tolist()))
Path('work/integration_20261102/position_cancellation_host.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
