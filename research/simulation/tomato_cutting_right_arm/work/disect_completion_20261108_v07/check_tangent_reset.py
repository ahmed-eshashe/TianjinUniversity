from cohesive_transfer import Transfer
import numpy as np,json
from pathlib import Path
s=Transfer();x=s.mesh['x'].copy();plus=np.unique(s.mesh['tets'][s.mesh['tet_side']>0]);x[plus]+=[.0015,.0002,0]
rng=np.random.default_rng(23);v=rng.normal(size=x.shape);v/=np.linalg.norm(v);eps=1e-7;eligible=np.ones(47,bool)
a=s.tangent_action(x,v,eligible);fd=(s.evaluate(x+eps*v,eligible)['force']-s.evaluate(x-eps*v,eligible)['force'])/(2*eps)
e=np.linalg.norm(a-fd)/np.linalg.norm(fd)
r=s.evaluate(x,eligible);s.commit(r['trial_history']);damage=s.history[:,1].copy();r2=s.evaluate(s.mesh['x'],eligible);noheal=bool(np.all(r2['trial_history'][:,1]>=damage-1e-12));s.reset();fresh=Transfer();reset=bool(np.array_equal(s.history,fresh.history) and np.array_equal(s.evaluate(x)['force'],fresh.evaluate(x)['force']))
out=dict(scope='Exact reference tangent pullback and component history/reset; no loaded simulator reset qualification',tangent_relative_error=float(e),partial_damage_min=float(damage.min()),partial_damage_max=float(damage.max()),no_healing=noheal,reset_matches_fresh=reset,passed=bool(e<1e-5 and noheal and reset))
Path(__file__).with_name('tangent_reset_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
