"""Exact rational ray predicates for rare uncertain floating-point CAD signs.

Inputs are interpreted as their exact binary floating-point values. No spatial
band, force threshold, area deletion or geometric perturbation is introduced.
"""
from fractions import Fraction as Q
from functools import lru_cache

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
@lru_cache(maxsize=4)
def rational_vertices(vertices):return tuple(tuple(Q(float(x))for x in v)for v in vertices)
def classify(vertices,faces,point):
 v=rational_vertices(tuple(tuple(float(x)for x in row)for row in vertices));p=tuple(Q(float(x))for x in point)
 for ray in ((1,2,3),(17,29,43),(-11,13,7),(101,-53,31),(97,193,-43)):
  hits=0;ambiguous=False
  for ids in faces:
   a,b,c=(v[int(i)]for i in ids);e1=sub(b,a);e2=sub(c,a);h=cross(ray,e2);det=dot(e1,h)
   if det==0:continue
   s=sub(p,a);u=dot(s,h)/det
   if u<0 or u>1:continue
   q=cross(s,e1);vv=dot(ray,q)/det
   if vv<0 or u+vv>1:continue
   t=dot(e2,q)/det
   if t==0:return 0 # Exact boundary, not a proximity tolerance.
   if t<0:continue
   if u==0 or vv==0 or u+vv==1:ambiguous=True;break
   hits+=1
  if not ambiguous:return -1 if hits%2 else 1
 raise ValueError('All exact ray directions hit mesh edges; classification unresolved')
