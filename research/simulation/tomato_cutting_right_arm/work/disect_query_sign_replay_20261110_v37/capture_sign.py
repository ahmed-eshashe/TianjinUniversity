from pathlib import Path
import numpy as np
from fast_cad_query import fast_query,_kernel,_cache
W=Path(__file__).resolve().parent
def capturing_query(vertices,faces,points):
 try:return fast_query(vertices,faces,points)
 except ValueError as e:
  if 'Uncertain solid-angle sign' in str(e) and not (W/'first_uncertain_query.npz').exists():
   values=_kernel(_cache['tri'],_cache['edge'],_cache['coeff'],np.ascontiguousarray(points,dtype=np.float64).reshape(-1,3))
   np.savez_compressed(W/'first_uncertain_query.npz',vertices=vertices,faces=faces,points=points,phi=values[0],normal=values[1],closest=values[2],face=values[3],winding=values[4],errors=values[5])
  raise
