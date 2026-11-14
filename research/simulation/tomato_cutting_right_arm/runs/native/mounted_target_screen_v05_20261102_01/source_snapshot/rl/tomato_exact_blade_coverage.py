"""Float64 triangle/solid-cell clipping on an unchanged authored blade.

Constrained tetrahedra supply candidate coverage, not the contact normal. Contact
samples use the original exterior mesh. This is finite-area quadrature, not a
unique contact manifold or an exact-arithmetic collision certificate.
"""
import numpy as np
NUMERIC_M=1e-12

def cell_planes(vertices,cells):
 result=[]
 for cell in cells:
  p=vertices[cell];planes=[]
  for face,other in [((0,1,2),3),((0,1,3),2),((0,2,3),1),((1,2,3),0)]:
   a,b,c=p[list(face)];n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
   if n@(p[other]-a)>0:n=-n
   planes.append((n,a))
  result.append(planes)
 return result

def clip_polygon(polygon,soft,normal,anchor):
 if not polygon:return []
 output=[];previous=polygon[-1];dp=normal@(previous@soft-anchor)
 for current in polygon:
  dc=normal@(current@soft-anchor);ip=dp<=0.;ic=dc<=0.
  if ip!=ic:
   fraction=dp/(dp-dc);output.append(previous+fraction*(current-previous))
  if ic:output.append(current)
  previous=current;dp=dc
 return output

def coverage(vertices,cells,positions,triangles,*,capacity=16384,reference_positions=None,quadrature_level=None):
 vertices=np.asarray(vertices,dtype=float);cells=np.asarray(cells,dtype=int);positions=np.asarray(positions,dtype=float);triangles=np.asarray(triangles,dtype=int)
 if not np.isfinite(positions).all() or not np.isfinite(vertices).all() or len(cells)>512:raise ValueError('Finite bounded coverage input required')
 reference_positions=positions if reference_positions is None else np.asarray(reference_positions,dtype=float)
 planes=cell_planes(vertices,cells);tetpoints=vertices[cells];lo=tetpoints.min(axis=1);hi=tetpoints.max(axis=1);samples=[];per_triangle=[]
 for index,ids in enumerate(triangles):
  soft=positions[ids];area=.5*np.linalg.norm(np.cross(soft[1]-soft[0],soft[2]-soft[0]));candidates=[]
  if area<=1e-20:raise ValueError('Degenerate soft triangle')
  broad=np.flatnonzero(np.all(hi>=soft.min(axis=0)-NUMERIC_M,axis=1)&np.all(lo<=soft.max(axis=0)+NUMERIC_M,axis=1))
  for cell in broad:
   polygon=[np.array([1.,0.,0.]),np.array([0.,1.,0.]),np.array([0.,0.,1.])]
   for normal,anchor in planes[cell]:
    polygon=clip_polygon(polygon,soft,normal,anchor)
    if len(polygon)<3:break
   if len(polygon)<3:continue
   # Fan integration yields exact polygon area and first moment in float64.
   total=0.;moment=np.zeros(3)
   for j in range(1,len(polygon)-1):
    tri=np.array([polygon[0],polygon[j],polygon[j+1]]);xyz=tri@soft;a=.5*np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]));total+=a;moment+=a*tri.mean(axis=0)
   if total<=1e-20:continue
   weights=moment/total;point=weights@soft
   # A plane coincident with an internal cell face belongs to one cell only.
   duplicate=False
   for earlier in broad[broad<cell]:
    if all(n@(point-a)<=NUMERIC_M for n,a in planes[earlier]):
     if all(n@(q@soft-a)<=NUMERIC_M for q in polygon for n,a in planes[earlier]):duplicate=True;break
   if duplicate:continue
   if quadrature_level is None:
    candidates.append(dict(triangle_id=index,corners=ids.tolist(),barycentric=weights.tolist(),point_m=point.tolist(),area_m2=float(total),physical_area_m2=float(total),cell_id=int(cell)))
   else:
    if not 0<=quadrature_level<=5:raise ValueError('Bounded quadrature level required')
    local_triangles=[np.array([polygon[0],polygon[j],polygon[j+1]]) for j in range(1,len(polygon)-1)]
    for _ in range(quadrature_level):
     refined=[]
     for triangle in local_triangles:
      a,b,c=triangle;ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2;refined.extend([np.array([a,ab,ca]),np.array([ab,b,bc]),np.array([ca,bc,c]),np.array([ab,bc,ca])])
     local_triangles=refined
    for triangle in local_triangles:
     physical=triangle@soft;material=triangle@reference_positions[ids];reference_area=.5*np.linalg.norm(np.cross(material[1]-material[0],material[2]-material[0]));physical_area=.5*np.linalg.norm(np.cross(physical[1]-physical[0],physical[2]-physical[0]))
     for gauss in ((2/3,1/6,1/6),(1/6,2/3,1/6),(1/6,1/6,2/3)):
      bary=np.asarray(gauss)@triangle;candidate_point=bary@soft
      candidates.append(dict(triangle_id=index,corners=ids.tolist(),barycentric=bary.tolist(),point_m=candidate_point.tolist(),area_m2=float(reference_area/3),physical_area_m2=float(physical_area/3),cell_id=int(cell)))
  covered=sum(p['physical_area_m2'] for p in candidates)
  if covered>area*(1+1e-8)+1e-18:raise ValueError('Clipped area exceeds soft area; internal ownership failed')
  samples.extend(candidates);per_triangle.append(dict(id=index,soft_area_m2=float(area),covered_area_m2=float(covered),cells=len(candidates)))
  if len(samples)>=capacity:raise ValueError('Exact mesh candidate capacity saturated')
 return dict(samples=samples,triangles=per_triangle,capacity=capacity,geometry_epsilon_m=NUMERIC_M,feature_coverage='Every positive-area triangle/solid-cell intersection is considered; zero-area tangencies have zero penalty work at zero radius/margin.',contact_manifold_unique=False)


def verify_cells(blade,cell_data):
 from collections import Counter
 vertices=np.asarray(cell_data['vertices'],dtype=float);cells=np.asarray(cell_data['cells'],dtype=int)
 if not np.array_equal(vertices[:len(blade['vertices'])],blade['vertices']):raise ValueError('Blade source vertices changed')
 if cells.ndim!=2 or cells.shape[1]!=4 or min(cells.ravel())<0 or max(cells.ravel())>=len(vertices):raise ValueError('Invalid solid cell registry')
 volumes=np.linalg.det(vertices[cells[:,1:]]-vertices[cells[:,:1]])/6
 if np.min(volumes)<=0:raise ValueError('Nonpositive solid cell')
 def signed_key(face):
  inversions=sum(face[i]>face[j] for i in range(3) for j in range(i+1,3));return tuple(sorted(face)),(-1 if inversions%2 else 1)
 chain=Counter()
 for cell in cells:
  for face in ((0,2,1),(0,1,3),(0,3,2),(1,2,3)):
   key,sign=signed_key([int(cell[j]) for j in face]);chain[key]+=sign
 expected=Counter()
 for face in blade['triangles']:
  key,sign=signed_key(face);expected[key]+=sign
 if {k:v for k,v in chain.items() if v}!={k:v for k,v in expected.items() if v}:raise ValueError('Oriented cell boundary differs from original blade')
 return dict(positive_cells=len(cells),oriented_boundary_identical=True,volume_m3=float(sum(volumes)))
