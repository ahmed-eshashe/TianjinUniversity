from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import Cells
from volume_guard import jacobians
out={}
for name in ['edge_clock','edge_clock_half','broad_clock','broad_clock_half','recontact_rhs_fixed','recontact_rhs_fixed_half','recontact_spectral','paid_cut','paid_cut_refined_guard']:
 f=np.load(W/f'runs/{name}/final.npz');g=Cells(f['X'],f['codes']);tr=np.load(W/f'runs/{name}/trajectory.npz');low=10.;high=0.;first=None
 for t,x in zip(tr['t'],tr['x']):
  J=np.linalg.det(jacobians(g.corners(x),g.spacing));low=min(low,float(J.min()));high=max(high,float(J.max()))
  if first is None and (J.min()<=.1 or J.max()>=10):first=float(t)
 Fg=np.einsum('nki,kj->nij',g.corners(f['x']),(2*g.bits-1)/(4*g.spacing));out[name]={'recorded_frame_corner_J_min':low,'recorded_frame_corner_J_max':high,'first_recorded_volume_failure_s':first,'final_F_mismatch_max':float(np.linalg.norm(Fg-f['F'],axis=(1,2)).max()),'final_F_mismatch_rms':float(np.sqrt(np.mean((Fg-f['F'])**2))),'scope':'Observed recorded-frame corners; not a bound on every unsaved state. New runtime volume guard separately supplies interval bounds.'}
(W/'reports/saved_geometry_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
