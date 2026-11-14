"""Registered CAD cutting front and a geometric partition of the cut surface.

The partition controls geometric eligibility only. It does not replace the
saved traction quadrature, patch stiffness, or fracture-energy areas.
"""
import numpy as np

def register_front(blade):
 vertices=np.asarray(blade['vertices'],dtype=float);faces=np.asarray(blade['triangles'],dtype=int);pairs=[]
 for i in range(len(vertices)):
  for j in range(i+1,len(vertices)):
   if np.linalg.norm(vertices[i,:2]-vertices[j,:2])<1e-6 and .0001<abs(vertices[i,2]-vertices[j,2])<.0015:pairs.append((i,j))
 if not pairs:raise ValueError('No finite cutting-edge band registered')
 ids=np.asarray(pairs).ravel()
 if len(set(ids))!=len(ids):raise ValueError('Ambiguous opposite edge-band vertex pairs')
 thin=set(ids.tolist());normal=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]]);area2=np.linalg.norm(normal,axis=1)
 if np.any(area2<=0):raise ValueError('Degenerate authored blade facet')
 normal/=area2[:,None];front=np.array([i for i,t in enumerate(faces) if all(int(node) in thin for node in t) and normal[i,1]<-.1],dtype=int)
 if len(front)==0:raise ValueError('No down-facing finite cutting band')
 selected=set(front.tolist());seen=set();components=0
 while selected-seen:
  components+=1;stack=[min(selected-seen)]
  while stack:
   face=stack.pop()
   if face in seen:continue
   seen.add(face);nodes=set(faces[face].tolist());stack.extend(other for other in selected-seen if len(nodes.intersection(faces[other]))>=2)
 if components!=1:raise ValueError('Cutting-front registration is not one connected band')
 used=set(faces[front].ravel().tolist());edge_pairs=[pair for pair in pairs if set(pair)<=used];thickness=[abs(vertices[i,2]-vertices[j,2]) for i,j in edge_pairs]
 return dict(face_ids=front,vertex_pairs=np.array(edge_pairs,dtype=int),minimum_thickness_m=float(min(thickness)),maximum_thickness_m=float(max(thickness)),method='Actual down-facing facets joining opposite CAD edge-band vertices, XY match <=1 um and edge width 0.1–1.5 mm and front-normal Y < -0.1; no invented zero-thickness edge.',limitations='Finite blunt CAD edge; not a measured razor edge or experimental cutting calibration.')

def cut_topology(design):
 from tomato_coupled_contact import cut_pairs
 pairs=cut_pairs(design);lookup={int(a):i for i,(a,b) in enumerate(pairs)};piece=design['pieces'][0];faces=np.asarray([tri for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut'],dtype=int);triangles=np.array([[lookup[int(i)] for i in tri] for tri in faces],dtype=int)
 return pairs,triangles

def _clip_polygon(bary,triangle_yz,normal,offset):
 if len(bary)==0:return bary
 values=bary@triangle_yz@normal-offset;result=[]
 for index,current in enumerate(bary):
  previous=bary[index-1];fc=values[index];fp=values[index-1];inside=fc<=0.;previous_inside=fp<=0.
  if inside!=previous_inside:
   alpha=fp/(fp-fc);result.append(previous+alpha*(current-previous))
  if inside:result.append(current)
 return np.asarray(result,dtype=float).reshape(-1,3)

def make_footprints(design):
 pairs,triangles=cut_topology(design);reference=np.array([node['position_m'] for node in design['nodes']]);mid=reference[pairs].mean(1);anchors=np.array([p['anchor_yz_m'] for p in design['interface_patches']]);parents=[];owners=[];barycentric=[];areas=[]
 for parent,tri in enumerate(triangles):
  yz=mid[tri,1:]
  for patch,a in enumerate(anchors):
   polygon=np.eye(3)
   for other,b in enumerate(anchors):
    if patch==other:continue
    polygon=_clip_polygon(polygon,yz,2*(b-a),float(b@b-a@a))
    if len(polygon)<3:break
   for k in range(1,len(polygon)-1):
    weights=polygon[[0,k,k+1]];q=weights@mid[tri];area=float(np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))/2)
    if area>1e-14:parents.append(parent);owners.append(patch);barycentric.append(weights);areas.append(area)
 parents=np.asarray(parents,dtype=int);owners=np.asarray(owners,dtype=int);barycentric=np.asarray(barycentric);areas=np.asarray(areas);original=np.linalg.norm(np.cross(mid[triangles[:,1]]-mid[triangles[:,0]],mid[triangles[:,2]]-mid[triangles[:,0]]),axis=1)/2;by_patch=np.bincount(owners,weights=areas,minlength=len(anchors));saved=np.array([p['area_m2'] for p in design['interface_patches']])
 if np.any(by_patch<=0) or abs(areas.sum()-original.sum())>1e-12 or np.max(abs(barycentric.sum(2)-1))>1e-10 or barycentric.min()<-1e-10:raise ValueError('Cut footprint partition lost coverage or positive material interpolation')
 return dict(pairs=pairs,triangles=triangles,parent=parents,patch=owners,barycentric=barycentric,reference_area_m2=areas,patch_geometric_area_m2=by_patch,patch_saved_area_m2=saved,partition_area_error_m2=float(abs(areas.sum()-original.sum())),scope='Voronoi cells of saved reference patch anchors, clipped exactly to the triangulated material mid-surface. Saved cohesive force/energy areas stay unchanged.')

def current_footprints(positions,registration):
 positions=np.asarray(positions,dtype=float);mid=positions[registration['pairs']].mean(1);tri=mid[registration['triangles'][registration['parent']]];return np.einsum('fij,fjk->fik',registration['barycentric'],tri)
