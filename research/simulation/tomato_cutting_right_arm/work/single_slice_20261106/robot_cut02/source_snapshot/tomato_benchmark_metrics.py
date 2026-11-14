"""Geometry-only nominal end-cap evaluator; release must be certified separately."""
import numpy as np

def reference_geometry(design):
 x=np.asarray([n['position_m'] for n in design['nodes']],dtype=float);p=design['pieces'][0]
 if p['side']!='slice':raise ValueError('Expected saved slice component')
 faces=np.asarray(p['triangles'],dtype=int);cut=np.asarray(p['face_tags'])=='cut';ids=np.asarray(p['surface_node_ids'],dtype=int);weights=np.zeros(len(x));areas=np.linalg.norm(np.cross(x[faces[:,1]]-x[faces[:,0]],x[faces[:,2]]-x[faces[:,0]]),axis=1)/2
 for j in range(3):np.add.at(weights,faces[:,j],areas/3)
 yz=x[faces[cut].ravel(),1:];lo=yz.min(0);hi=yz.max(0);c=(hi+lo)/2;dy=(hi[0]-lo[0])/4;dz=(hi[1]-lo[1])/4
 samples=np.array([c,c+[dy,0],c+[-dy,0],c+[0,dz],c+[0,-dz]])
 return dict(reference=x,faces=faces,cut=cut,surface_ids=ids,weights=weights[ids],sample_yz=samples)

def rigid_register(current,reference,weights):
 """Area-weighted proper rigid fit, with no scale/shear or deformable fitting."""
 weights=np.asarray(weights,dtype=float);weights=weights/weights.sum();c=np.sum(current*weights[:,None],axis=0);r=np.sum(reference*weights[:,None],axis=0);u,_,vt=np.linalg.svd((current-c).T@(weights[:,None]*(reference-r)));rotation=u@np.diag([1.,1.,np.linalg.det(u@vt)])@vt;translation=r-c@rotation
 return rotation,translation

def profile(positions,geometry):
 x=np.asarray(positions);faces=geometry['faces'];tri=x[faces];values=[]
 for sample in geometry['sample_yz']:
  hits=[[],[]]
  for t,is_cut in zip(tri,geometry['cut']):
   a=(t[1:,1:]-t[0,1:]).T
   if abs(np.linalg.det(a))<1e-16:continue
   uv=np.linalg.solve(a,sample-t[0,1:]);b=np.r_[1-uv.sum(),uv]
   if b.min()>=-1e-10:hits[int(is_cut)].append(float(b@t[:,0]))
  unique=[np.unique(np.round(v,12)) for v in hits]
  if any(len(v)!=1 for v in unique):raise ValueError('Profile ray is missing or multiply intersects a tagged surface; quality unavailable')
  width=float(unique[1][0]-unique[0][0])
  if width<=0:raise ValueError('Cap profile has reversed surfaces')
  values.append(width)
 return np.array(values)

def evaluate_cap(positions,geometry):
 x=np.asarray(positions,dtype=float);ref=geometry['reference'];ids=geometry['surface_ids'];rotation,translation=rigid_register(x[ids],ref[ids],geometry['weights']);registered=x@rotation+translation;expected=profile(ref,geometry);actual=profile(registered,geometry)
 return dict(reference_profile_m=expected.tolist(),released_profile_m=actual.tolist(),profile_error_m=(actual-expected).tolist(),maximum_profile_error_m=float(abs(actual-expected).max()),registration_rotation=rotation.tolist(),registration_translation_m=translation.tolist(),scope='Shape metric only, area-weighted rigid alignment without scaling. Requires independently certified release, intact surfaces, and known node correspondence; never a success detector alone.')

def symmetric_refinement_error(a,b,absolute_floor):
 if absolute_floor<=0:raise ValueError('Positive absolute floor required')
 return abs(float(a)-float(b))/max(abs(float(a)),abs(float(b)),float(absolute_floor))
