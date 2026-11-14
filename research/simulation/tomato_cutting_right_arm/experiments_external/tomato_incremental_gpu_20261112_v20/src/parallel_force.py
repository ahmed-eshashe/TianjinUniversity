"""One warp cooperatively sums a node's incidences; same force law."""
import warp as wp

@wp.struct
class Incidence:
 ptr:wp.array(dtype=int)
 idx:wp.array(dtype=int)
 grad:wp.array(dtype=wp.vec3)
 P:wp.array(dtype=wp.mat33)

@wp.func
def lane_force(lane:int,i:int,data:Incidence):
 f=wp.vec3(0.0)
 for e in range(data.ptr[i]+lane,data.ptr[i+1],32):f-=data.P[data.idx[e]]*data.grad[e]
 return f

@wp.kernel(module='unique')
def gather_parallel(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3)):
 i=wp.tid()
 data=Incidence()
 data.ptr=ptr
 data.idx=idx
 data.grad=grad
 data.P=P
 lanes=wp.tile_arange(32,dtype=int)
 values=wp.tile_map(lane_force,lanes,i,data)
 total=wp.tile_sum(values)
 wp.tile_store(force,total+wp.tile_full(1,value=external[i],dtype=wp.vec3),offset=i)

@wp.kernel(module='unique')
def gather_packed(ptr:wp.array(dtype=int),idx:wp.array(dtype=int),grad:wp.array(dtype=wp.vec3),P:wp.array(dtype=wp.mat33),external:wp.array(dtype=wp.vec3),force:wp.array(dtype=wp.vec3),n:int):
 t=wp.tid()
 i=t//32
 lane=t%32
 f=wp.vec3(0.0)
 if i<n:
  for e in range(ptr[i]+lane,ptr[i+1],32):f-=P[idx[e]]*grad[e]
  if lane==0:f+=external[i]
 values=wp.tile_reshape(wp.tile(f,preserve_type=True),(4,32))
 total=wp.tile_sum(values,axis=1)
 wp.tile_store(force,total,offset=(t//128)*4)
