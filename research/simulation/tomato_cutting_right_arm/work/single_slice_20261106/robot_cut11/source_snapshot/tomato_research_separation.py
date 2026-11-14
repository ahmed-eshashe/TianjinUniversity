"""Read-only connectivity and motion measurements for the original research model.

No history is changed. A remaining active cohesive patch is a material bond,
not a visually separated mesh. Full experimental/coupled qualification is not
inferred from these component measurements.
"""
import numpy as np

def measure(data,positions,velocities,history):
 x=np.asarray(positions);v=np.asarray(velocities);history=np.asarray(history);n=len(data['mass']);patches=data['cohesion'].patches
 if x.shape!=(n,3) or v.shape!=(n,3) or history.shape!=(len(patches),2) or not np.isfinite(x).all() or not np.isfinite(v).all() or not np.isfinite(history).all():raise ValueError('Invalid separation measurement state')
 parent=np.arange(n)
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def join(a,b):
  a,b=root(int(a)),root(int(b))
  if a!=b:parent[b]=a
 for a,b in data['springs']:join(a,b)
 for cell in data['cells']:
  for j in cell[1:]:join(cell[0],j)
 for patch,h in zip(patches,history):
  if h[1]<1.:
   nodes=np.unique(data['pairs'][patch['indices']])
   for j in nodes[1:]:join(nodes[0],j)
 roots=np.array([root(i)for i in range(n)]);labels=np.array([a['side']for a in data['design']['nodes']]);fixture=set(data['design']['fixture']['node_ids']);pieces=[]
 for label in np.unique(labels):
  ids=np.flatnonzero(labels==label);mass=data['mass'][ids];total=float(mass.sum());pieces.append(dict(label=str(label),mass_kg=total,component_count=len(np.unique(roots[ids])),fixed_node_count=len(set(ids.tolist())&fixture),center_m=(mass@x[ids]/total).tolist(),mean_velocity_m_s=(mass@v[ids]/total).tolist(),minimum_z_m=float(x[ids,2].min()),maximum_z_m=float(x[ids,2].max())))
 mixed=any(len(np.unique(labels[roots==k]))>1 for k in np.unique(roots));separated=not mixed and len(pieces)==2 and all(p['component_count']==1 for p in pieces)
 return dict(topological_separation=bool(separated),component_count=len(np.unique(roots)),failed_patches=int(np.sum(history[:,1]>=1.)),remaining_material_patches=int(np.sum(history[:,1]<1.)),pieces=pieces,robot_coupled=False,post_withdrawal_support_verified=False,experimental_validation=False)
