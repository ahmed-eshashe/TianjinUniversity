from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'tomato_approx_rl_20261113_v28/src'));sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from coupled_environment import CuttingEnv
E=CuttingEnv(1);g=E.g;z=np.load(W/'runs/cut01/material_final.npz')
for k in z.files:getattr(g,k).assign(z[k])
rows=[];quiet=0
for i in range(750):
 g.step(np.zeros(6),200)
 if i%5==4:
  _,info=E.observe();row=dict(additional_s=(i+1)*.02,speed=float(info['max_speed_m_s'][0]),supported=bool(info['supported'][0]),bad=int(info['bad'][0]));rows.append(row);quiet=quiet+1 if row['supported'] else 0
  if quiet>=5 or row['bad']:break
(W/'reports/settling_probe.json').write_text(json.dumps(rows,indent=2));print(rows[-1]);print('quiet_checks',quiet)
