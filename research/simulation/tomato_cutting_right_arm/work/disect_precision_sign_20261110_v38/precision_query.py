"""Resolve uncertain winding arithmetic at two higher precisions, never relax it.

Distance/nearest feature/normal remain the validated float64 CAD calculation.
Only when the original query raises its unchanged winding test do we repeat
that winding sum at 40 and 80 digits. Ambiguous or disagreeing signs still stop.
No distance snapping, force truncation, geometry or constitutive change.
"""
import math,numpy as np,mpmath as mp
from fast_cad_query import fast_query,_kernel,_cache
stats={'fallback_calls':0,'fallback_points':0,'max_distance_m':0.}
def high_precision_winding(vertices,faces,point,dps):
 with mp.workdps(dps):
  pp=list(map(lambda x:mp.mpf(float(x)),point));total=mp.mpf(0)
  for face in faces:
   a,b,c=[[mp.mpf(float(x))-px for x,px in zip(vertices[j],pp)] for j in face]
   dot=lambda u,w:sum(x*y for x,y in zip(u,w))
   cross=[b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0]]
   la,lb,lc=[mp.sqrt(dot(q,q)) for q in [a,b,c]]
   total+=2*mp.atan2(dot(a,cross),la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb)
  return total/(4*mp.pi)
def resolved_winding(vertices,faces,point):
 a=high_precision_winding(vertices,faces,point,40);b=high_precision_winding(vertices,faces,point,80)
 with mp.workdps(80):
  # Stricter certification, not a new tolerance for the original 1e-6 test.
  if min(abs(b),abs(abs(b)-1))>mp.mpf('1e-20') or abs(a-b)>mp.mpf('1e-20'):
   raise ValueError('Uncertain solid-angle sign remains at higher precision')
  if (abs(a)>mp.mpf('.5'))!=(abs(b)>mp.mpf('.5')):raise ValueError('Higher-precision sign disagreement')
 return float(b)
def precise_query(vertices,faces,points):
 try:return fast_query(vertices,faces,points)
 except ValueError as exc:
  if str(exc)!='Uncertain solid-angle sign':raise
 v=np.ascontiguousarray(vertices,dtype=np.float64);f=np.ascontiguousarray(faces,dtype=np.int64);p=np.ascontiguousarray(points,dtype=np.float64).reshape(-1,3)
 if not np.isfinite(p).all():raise ValueError('Finite query points required')
 values=_kernel(_cache['tri'],_cache['edge'],_cache['coeff'],p)
 bad=np.flatnonzero(values[-1]);
 if len(bad)>64:raise ValueError('Higher-precision query work budget exceeded')
 for i in bad:
  wind=resolved_winding(v,f,p[i]);old_sign=-1. if abs(values[4][i])>.5 else 1.;sign=-1. if abs(wind)>.5 else 1.
  values[0][i]=sign*abs(values[0][i]);values[1][i]*=sign/old_sign;values[4][i]=wind
 stats['fallback_calls']+=1;stats['fallback_points']+=len(bad)
 if len(bad):stats['max_distance_m']=max(stats['max_distance_m'],float(np.max(np.abs(values[0][bad]))))
 return values[:-1]
