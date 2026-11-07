import json
from pathlib import Path
import numpy as np,torch
from tomato_surface_cohesion import SurfaceCohesion
from tomato_coupled_contact import cut_pairs
from tomato_objective_cohesion_reference import make_patch,response
r=Path(__file__).resolve().parents[2];d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());x=np.array([n['position_m'] for n in d['nodes']]);pairs=cut_pairs(d);patches=SurfaceCohesion(d,pairs,0.).patches;pos=x.copy();pos[np.unique(pairs[:,1])]+=[.002,.0003,.0002];force=np.zeros_like(x);hess=np.zeros((len(x),3,3));torch.set_num_threads(1)
for p in patches:
 ids=pairs[p['indices']];l=p['law'];model=make_patch(x[ids],p['weights'],p['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m));result=response(pos[ids],model,eligible=True,tangent=True);np.add.at(force,ids.reshape(-1),result['force_n'].reshape(-1,3));matrix=-result['force_jacobian_n_m']
 for j,node in enumerate(ids.reshape(-1)):hess[node]+=matrix[j*3:j*3+3,j*3:j*3+3]
np.savez(r/'work/integration_20261102/objective_tangent_reference.npz',positions=pos,forces=force,hessians=hess)
print('Prepared independent full-registry loading tangent: maximum absolute stiffness',np.abs(hess).max())
