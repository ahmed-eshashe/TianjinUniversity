from pathlib import Path
import sys
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'))
import numpy as np,torch
from scipy.spatial.transform import Rotation
from tomato_objective_cohesion_reference import make_patch,response
# Registry requires native initialization; reuse saved actual arrays/material JSON.
import json
from tomato_surface_cohesion import SurfaceCohesion
from tomato_coupled_contact import cut_pairs
s=r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((s/'surface_design.json').read_text());x0=np.array([n['position_m'] for n in design['nodes']]);pairs=cut_pairs(design);cohesion=SurfaceCohesion(design,pairs,0.);right=np.unique(pairs[:,1]);rotation=Rotation.from_rotvec([.3,.6,-.2]).as_matrix();torch.set_num_threads(1);output={}
for label,gap,rotate in [('rest',[0,0,0],False),('tensile',[.0005,0,0],False),('mixed_open',[.002,.0003,.0002],False),('mixed_compressed',[-.0002,.002,.0003],False),('rotated_mixed',[.002,.0003,.0002],True),('pure_compression',[-.001,0,0],False)]:
 pos=x0.copy();pos[right]+=gap
 if rotate:pos=pos@rotation.T+[.2,-.1,.3]
 blocks=np.zeros((len(pos),3,3))
 for patch in cohesion.patches:
  ids=pairs[patch['indices']];l=patch['law'];m=make_patch(x0[ids],patch['weights'],patch['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m));x=torch.tensor(pos[ids],dtype=torch.float64,requires_grad=True)
  def effective(y):
   mid=y.mean(1);a,b,c=m['anchors'];u=mid[b]-mid[a];v=mid[c]-mid[a];t=u/torch.linalg.vector_norm(u);cross=torch.linalg.cross(u,v);n=m['sign']*cross/torch.linalg.vector_norm(cross);frame=torch.stack([n,t,torch.linalg.cross(n,t)],dim=1);local=(y[:,1]-y[:,0])@frame;return torch.cat([torch.clamp(local[:,:1],min=0),local[:,1:]],dim=1)
  jac=torch.autograd.functional.jacobian(effective,x).detach().numpy();d=response(pos[ids],m,eligible=True)['trial_history'][1]
  for local_node,node in enumerate(ids.ravel()):
   j=jac[:,:,local_node//2,local_node%2,:];blocks[node]+=(1-d)*np.einsum('q,qai,ab,qbj->ij',m['weights'],j,m['local_k'],j)
 output[label+'_positions']=pos;output[label+'_blocks']=blocks
np.savez(r/'work/integration_20261102/objective_gn_reference.npz',**output)
print('Prepared six independent full-registry moving-frame Gauss-Newton references')
