"""Run only after the previous GPU simulation exits."""
from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_fracture_20261109_v23';sys.path.insert(0,str(V))
from damage_blade import DamageBlade,s,tensor,torch
b=DamageBlade();saved=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz');p=json.loads((W/'correction_plan.json').read_text());T=np.array(p['selected']['translation_m']);h=p['dt_s']
def load(q,v,hist):
 b.reset();b.x.copy_(tensor(q));b.v.copy_(tensor(v));b.fracture.load_state_dict({'history':hist});b.blade_enabled=True;b.blade_translation=T.copy();b.blade_velocity=np.zeros(3)
def step():
 r=b.implicit(h);assert r['relative_residual']<=1e-9 and r['inner_max_residual']<=1e-9;b.accept_fracture();return b.arrays(),b.fracture.state_dict()['history']
# Include genuine canonical partial damage as a manufactured restart fixture, not a cutting result.
hist=np.c_[np.full(47,.002),np.full(47,2/3)];load(saved['x'],saved['v'],hist);(q,v),h1=step();(q2,v2),h2=step();np.savez_compressed(W/'restart_fixture.npz',x=q,v=v,history=h1);r=np.load(W/'restart_fixture.npz');load(r['x'],r['v'],r['history']);(qr,vr),hr=step();pe=float(abs(qr-q2).max());ve=float(abs(vr-v2).max());he=float(abs(hr-h2).max());out=dict(scope='Manufactured partially damaged dynamic checkpoint fixture; not blade-induced damage or cutting qualification',position_max_error_m=pe,velocity_max_error_m_s=ve,history_max_error=he,passed=bool(pe<=1e-12 and ve<=1e-9 and he<=1e-12));(W/'restart_controls_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
