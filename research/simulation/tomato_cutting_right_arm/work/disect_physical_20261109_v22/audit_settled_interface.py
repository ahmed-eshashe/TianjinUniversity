from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
import torch
s=FullSurface(device='cpu');q=np.load(W/'settle_contact_final.npz')['x'];U=s.energies(s.T(q)).detach().numpy();eq=np.sqrt(np.maximum(2*U/s.kn.numpy(),0));ratio=eq/s.on.numpy()
out=dict(scope='Read-only constitutive audit of settled state; no damage enabled or committed',stored_cohesive_energy_j=float(U.sum()),maximum_effective_opening_m=float(eq.max()),maximum_ratio_to_damage_onset=float(ratio.max()),groups_above_onset=int((ratio>1).sum()),history_unchanged=bool(np.all(s.history==0)))
(W/'settled_interface_audit.json').write_text(json.dumps(out,indent=2));print(out)
