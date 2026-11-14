from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import Cells
out={}
for name in ['edge_clock','paid_cut']:
 d=np.load(W/f'runs/{name}/final.npz');g=Cells(d['X'],d['codes']);corn=g.corners(d['x']);grad=(2*g.bits-1)/(4*g.spacing);Fg=np.einsum('nki,kj->nij',corn,grad);err=np.linalg.norm(Fg-d['F'],axis=(1,2));out[name]={'max_position_displacement_m':float(np.linalg.norm(d['x']-d['X'],axis=1).max()),'max_geometry_vs_stress_F_frobenius':float(err.max()),'rms_geometry_vs_stress_F':float(np.sqrt(np.mean(err**2))),'stored_F_det_min':float(np.linalg.det(d['F']).min()),'reconstructed_center_det_min':float(np.linalg.det(Fg).min()),'reconstructed_center_det_max':float(np.linalg.det(Fg).max()),'max_stored_F_change':float(np.linalg.norm(d['F']-np.eye(3),axis=(1,2)).max()),'max_reconstructed_F_change':float(np.linalg.norm(Fg-np.eye(3),axis=(1,2)).max())}
(W/'reports/geometry_strain_diagnosis.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
