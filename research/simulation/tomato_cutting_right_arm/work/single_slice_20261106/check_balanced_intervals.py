from pathlib import Path
import numpy as np,json
rng=np.random.default_rng(441);minimum_ratio=1.;maximum_error=0.
for _ in range(10000):
 total=1/2400;completed=0.;limit=10**rng.uniform(-6,-3.4)
 for step in range(4096):
  remaining=total-completed
  if remaining<=1e-15:break
  micro=remaining/max(1,int(np.ceil(remaining/limit)))
  assert 0<micro<=limit*(1+1e-14)
  if remaining>limit:minimum_ratio=min(minimum_ratio,micro/limit)
  completed+=micro;limit=min(1/2400,limit*rng.uniform(.7,1.4))
 else:raise AssertionError('Partition did not terminate')
 maximum_error=max(maximum_error,abs(total-completed))
assert minimum_ratio>=.5 and maximum_error<=1e-15
result=dict(passed=True,random_schedules=10000,minimum_fraction_of_cap=minimum_ratio,maximum_clock_error_s=maximum_error,no_interval_skipped=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2));print(result)
