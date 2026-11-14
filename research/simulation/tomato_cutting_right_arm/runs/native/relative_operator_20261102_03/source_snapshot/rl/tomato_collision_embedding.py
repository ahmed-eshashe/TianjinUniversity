"""Fixed positive barycentric collision embedding for a coincident cut seam.

The mechanical mesh is unchanged. Only collision proxy vertices near the seam
are recessed into their own material. Forces map back with the transpose of the
same fixed linear embedding. This candidate requires contact/refinement audits.
"""
import numpy as np

def build_embedding(design,cells,*,interaction_distance_m=.0001,clearance_guard_m=1e-7):
 x=np.asarray([n['position_m'] for n in design['nodes']],float);cells=np.asarray(cells,int);cut=design['cut_x_m'];surface=sorted(set(i for p in design['pieces'] for i in p['surface_node_ids']));lookup={node:i for i,node in enumerate(surface)};triangles=np.asarray([[lookup[i] for i in tri] for p in design['pieces'] for tri in p['triangles']],int);reference_triangles=np.asarray([tri for p in design['pieces'] for tri in p['triangles']],int)
 indices=np.repeat(np.asarray(surface)[:,None],4,axis=1);weights=np.zeros((len(surface),4));weights[:,0]=1.;target=x[surface].copy();records=[];half=(interaction_distance_m+clearance_guard_m)/2
 for p in design['pieces']:
  side=-1 if p['side']=='left' else 1
  # Saved design uses slice/remainder names in some registries; geometry decides.
  vertices=np.asarray(p['surface_node_ids']);mean=float(x[vertices,0].mean());side=-1 if mean<cut else 1;center=np.asarray(p['reference_interior_m']);depth=side*(x[cells].mean(1)[:,0]-cut);owned=np.flatnonzero(depth>0);a=x[cells[owned,0]];matrix=(x[cells[owned,1:]]-a[:,None]).transpose(0,2,1);inverse=np.linalg.inv(matrix);lo=x[cells[owned]].min(1);hi=x[cells[owned]].max(1)
  for node in vertices:
   d=side*(x[node,0]-cut)
   if d>=half:continue
   center_d=side*(center[0]-cut)
   if center_d<=half:raise ValueError('Reference interior cannot support seam recession')
   alpha=(half-d)/(center_d-d);point=(1-alpha)*x[node]+alpha*center;candidates=np.flatnonzero(np.all(point>=lo-1e-12,axis=1)&np.all(point<=hi+1e-12,axis=1))
   if not len(candidates):raise ValueError('Collision point outside owned volume')
   uv=np.einsum('nij,nj->ni',inverse[candidates],point-a[candidates]);bary=np.column_stack([1-uv.sum(1),uv]);j=int(np.argmax(bary.min(1)));w=bary[j].copy();cell=int(owned[candidates[j]])
   if w.min() < -1e-10:raise ValueError('No positive local embedding for seam proxy')
   # Explicitly recorded projection of roundoff-scale negative weights.
   w=np.maximum(w,0.);w/=w.sum();w[np.argmax(w)]+=1.-w.sum();point_mapped=w@x[cells[cell]];error=float(np.linalg.norm(point_mapped-point))
   if error>1e-10:raise ValueError('Embedding fit error exceeds geometry budget')
   at=lookup[int(node)];indices[at]=cells[cell];weights[at]=w;target[at]=point_mapped;records.append(dict(node=int(node),cell=cell,shift_m=float(np.linalg.norm(point_mapped-x[node])),fit_error_m=error,minimum_weight=float(w.min())))
 actual=np.einsum('ni,nij->nj',weights,x[indices]);old=x[reference_triangles];new=actual[triangles];n0=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);n1=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0]);alignment=np.sum(n0*n1,axis=1)/(np.linalg.norm(n0,axis=1)*np.linalg.norm(n1,axis=1))
 if not np.isfinite(alignment).all() or alignment.min()<=0:raise ValueError('Collision recession inverted a surface facet')
 return dict(surface_node_ids=np.array(surface),indices=indices,weights=weights,triangles=triangles,reference_positions=actual,interaction_distance_m=interaction_distance_m,clearance_guard_m=clearance_guard_m,records=records,maximum_recession_m=max((r['shift_m'] for r in records),default=0.),minimum_normal_alignment=float(alignment.min()))

def mapped_positions(x,embedding):return np.einsum('ni,nij->nj',embedding['weights'],np.asarray(x)[embedding['indices']])

def mapped_force(force,embedding,node_count):
 f=np.zeros((node_count,3));np.add.at(f,embedding['indices'].reshape(-1),(embedding['weights'][:,:,None]*np.asarray(force)[:,None]).reshape(-1,3));return f
