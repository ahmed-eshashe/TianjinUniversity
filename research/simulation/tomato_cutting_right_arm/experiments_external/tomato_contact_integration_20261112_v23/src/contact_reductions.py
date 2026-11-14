"""Parallel force pullback and deterministic staged force-stop reduction."""
import warp as wp
@wp.kernel(module='unique')
def pullback_parallel(ptr:wp.array(dtype=int),ids:wp.array(dtype=int),w:wp.array(dtype=float),cf:wp.array(dtype=wp.vec3),external:wp.array(dtype=wp.vec3),n:int):
 t=wp.tid();i=t//32;lane=t%32;f=wp.vec3(0.)
 if i<n:
  for k in range(ptr[i]+lane,ptr[i+1],32):f+=w[k]*cf[ids[k]]
 total=wp.tile_sum(wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32)),axis=1)
 wp.tile_store(external,total,offset=(t//128)*4)
@wp.kernel
def force_parts(cf:wp.array(dtype=wp.vec3),sums:wp.array(dtype=wp.vec3),magnitudes:wp.array(dtype=float),n:int):
 b=wp.tid();f=wp.vec3(0.);m=float(0.)
 for i in range(b*128,wp.min((b+1)*128,n)):f+=cf[i];m+=wp.length(cf[i])
 sums[b]=f;magnitudes[b]=m
@wp.kernel
def force_guard(sums:wp.array(dtype=wp.vec3),magnitudes:wp.array(dtype=float),bad:wp.array(dtype=int),peak:wp.array(dtype=float),n:int):
 if wp.tid()==0:
  f=wp.vec3(0.);m=float(0.)
  for b in range(n):f+=sums[b];m+=magnitudes[b]
  value=wp.max(m,wp.length(f));peak[0]=wp.max(peak[0],value)
  if value>2. or not wp.isfinite(value):wp.atomic_max(bad,0,3)
