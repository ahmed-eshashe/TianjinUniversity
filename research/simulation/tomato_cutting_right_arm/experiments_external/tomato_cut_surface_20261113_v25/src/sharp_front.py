"""Reference measures of the actual straight lower CAD segment.

Only this straight segment is admitted here. Curved or reversing sweeps are
not inferred from a tool bounding box, plane or unsigned proximity alone.
"""
import numpy as np
from scipy.spatial import ConvexHull

def blade_edge(cad,T,R):
 # Original lower-perimeter vertices, not a replacement collision geometry.
 return np.array([(cad.vertices[14]+cad.vertices[15])/2,(cad.vertices[16]+cad.vertices[17])/2])@R.T+T

def polygon_area(poly):
 if len(poly)<3:return 0.
 return float(np.linalg.norm(np.cross(poly[1:-1]-poly[0],poly[2:]-poly[0]).sum(0))/2)

def plane_polygon(poly,n,d):
 vals=poly@n-d
 if vals.min()>=0 or vals.max()<=0:return np.empty((0,3))
 h=ConvexHull(poly);edges=set()
 for tri in h.simplices:
  for i,j in [(0,1),(1,2),(2,0)]:edges.add(tuple(sorted((int(tri[i]),int(tri[j])))))
 pts=list(poly[vals==0])
 for i,j in edges:
  if vals[i]*vals[j]<0:pts.append(poly[i]+vals[i]/(vals[i]-vals[j])*(poly[j]-poly[i]))
 pts=np.unique(np.asarray(pts),axis=0);nn=n/np.linalg.norm(n);axis=np.eye(3)[np.argmin(abs(nn))];u=np.cross(nn,axis);u/=np.linalg.norm(u);v=np.cross(nn,u);xy=pts@np.array([u,v]).T;return pts[ConvexHull(xy).vertices]

def clip_polygon(p,n,d):
 if not len(p):return p
 vals=p@n-d;out=[]
 for i,x in enumerate(p):
  j=(i+1)%len(p)
  if vals[i]<=0:out.append(x)
  if vals[i]*vals[j]<0:out.append(x+vals[i]/(vals[i]-vals[j])*(p[j]-x))
 return np.asarray(out).reshape(-1,3)

def current_sections(a,edge,direction,cut_id=0):
 b=a.body;pos,vel,F=b.fields();trans=pos-np.einsum('pij,pj->pi',F,b.X);tangent=edge[1]-edge[0];normal=np.cross(tangent,direction);normal/=np.linalg.norm(normal);d=float(normal@edge[0]);regions=[]
 for i,p in enumerate(b.polys):
  if (b.codes[i]//3**cut_id)%3:continue
  nr=F[i].T@normal;dr=d-normal@trans[i];section=plane_polygon(p,nr,dr)
  if len(section):regions.append((i,section,F[i].T@direction,float(direction@trans[i])))
 return normal,d,regions

def novel_area(a,regions,direction,front):
 total=0.
 for i,section,nr,shift in regions:total+=polygon_area(clip_polygon(section,nr,front-shift))
 return total

def line_resistance(a,edge,direction,cut_id=0):
 b=a.body;pos,vel,F=b.fields();trans=pos-np.einsum('pij,pj->pi',F,b.X);intervals=[]
 for i,p in enumerate(b.polys):
  if (b.codes[i]//3**cut_id)%3:continue
  points=np.linalg.solve(F[i],(edge-trans[i]).T).T;origin=points[0];delta=points[1]-points[0];h=ConvexHull(p);lo=0.;hi=1.
  for plane in h.equations:
   f=plane[:3]@origin+plane[3];s=plane[:3]@delta
   if abs(s)<1e-18:
    if f>1e-12:hi=-1.;break
   elif s>0:hi=min(hi,-f/s)
   else:lo=max(lo,-f/s)
  if hi>lo+1e-14:intervals.append((lo,hi,i,origin,delta))
 if not intervals:return None
 # Partition shared-boundary overlaps once, avoiding double toughness.
 knots=sorted(set([x for v in intervals for x in v[:2]]));B=np.zeros_like(a.q);c=np.zeros(3);width=0.;pieces=[]
 for lo,hi in zip(knots[:-1],knots[1:]):
  mid=(lo+hi)/2;owners=[v for v in intervals if v[0]<=mid<=v[1]]
  if not owners:continue
  _,_,i,origin,delta=min(owners,key=lambda v:v[2]);point=origin+mid*delta;length=np.linalg.norm(delta)*(hi-lo);advance=np.linalg.solve(F[i],direction);tref=delta/np.linalg.norm(delta);advance-=tref*(advance@tref);advance/=np.linalg.norm(advance);covector=np.linalg.solve(F[i].T,advance);N=np.r_[1.,point]@b.inv[i];marker=np.asarray(N@a.E[b.ids[i]].toarray());B+=length*marker[:,None]*covector;c+=length*covector;width+=length;pieces.append(dict(owner=i,reference_width_m=float(length),reference_point=point.tolist()))
 if width==0:return None
 return dict(B=B/width,c=c/width,width=width,pieces=pieces)
