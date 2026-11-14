"""Offline proposed integration layout only. Does not enable or change forces."""
from cohesive_transfer import Transfer
import numpy as np,json
from pathlib import Path
s=Transfer();m=s.mesh;faces=m['cut_minus'];x=m['x'];tri=x[faces];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
# Three positive interior quadrature points per triangle cover every vertex.
bary=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
points=np.einsum('qi,tij->tqj',bary,tri).reshape(-1,3);raw_weight=np.repeat(area/3,3)
centers=[]
for p in s.registry['patches']:
 ids=p['pair_indices'];centers.append(np.average(s.mapping['source_pair_coordinates'][ids],axis=0,weights=p['weights']))
centers=np.array(centers);groups=np.argmin(np.linalg.norm(points[:,None]-centers[None],axis=2),axis=1);counts=np.bincount(groups,minlength=47);sums=np.bincount(groups,weights=raw_weight,minlength=47)
weights=raw_weight/sums[groups];covered=np.unique(faces);out=dict(scope='Reviewable offline quadrature proposal only; NOT approved or active dynamics',triangles=len(faces),points=len(points),patch_groups=47,empty_groups=int((counts==0).sum()),minimum_points_per_group=int(counts.min()),maximum_points_per_group=int(counts.max()),covered_interface_nodes=len(covered),interface_nodes=len(m['ties']),group_assignment='Nearest original weighted patch centroid in reference cut plane; prospective discretization, not the old local distribution',weights='Triangle areas / 3, normalized separately within each original patch; preserves each patch stiffness and fracture budget for uniform opening',preserved=['Outside shape, total mass, support locations and cut plane','47 original bilinear laws, patch stiffnesses and total fracture budget','Moving-frame force derivatives and irreversible history'],changes=['Local spatial distribution of cohesive stiffness and damage sampling','Original patch boundaries approximated by nearest-centroid partition'],required_checks=['All cut-face modes covered','Uniform opening/shear reproduce original patch response and energy budget','Nonuniform field force/energy/tangent controls','Quadrature partition/refinement sensitivity before dynamics','Cut-face closure after failure, assembled settling and blade-contact refinement','Runtime remains an independent failed gate'])
np.savez_compressed(Path(__file__).with_name('quadrature_proposal.npz'),faces=np.repeat(faces,3,axis=0),barycentric=np.tile(bary,(len(faces),1)),points=points,groups=groups,weights=weights)
Path(__file__).with_name('quadrature_proposal.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
