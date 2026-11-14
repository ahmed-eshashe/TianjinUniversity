"""Pure translation of the simulation frame; source physical quantities retained."""
import numpy as np
import warp as wp

def translated_registry(data,origin):
 origin=np.asarray(origin,dtype=float)
 if origin.shape!=(3,)or not np.isfinite(origin).all():raise ValueError('Finite translation required')
 shifted=dict(data);shifted['x']=data['x']-origin;rest=np.linalg.norm(data['x'][data['springs'][:,1]]-data['x'][data['springs'][:,0]],axis=1)
 return shifted,rest

@wp.kernel(enable_backward=False)
def translate_points(local:wp.array[wp.vec3d],origin:wp.vec3d,world:wp.array[wp.vec3d]):
 i=wp.tid();world[i]=local[i]+origin

def retain_canonical_material(holder,world_data,source_rest):
 """Keep source anchor choices under translation, including exact tie breaks."""
 from tomato_objective_cohesion_reference import make_patch
 anchors=[];sign=[];stiffness=[]
 for p in world_data['cohesion'].patches:
  ids=world_data['pairs'][p['indices']];law=p['law'];m=make_patch(world_data['x'][ids],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));anchors.append(m['anchors']);sign.append(m['sign']);stiffness.append(m['local_k'])
 holder.relative_spring_rest.assign(source_rest);holder.objective_anchors.assign(np.asarray(anchors,dtype=np.int32));holder.objective_sign.assign(np.asarray(sign));holder.objective_stiffness.assign(np.asarray(stiffness));return holder
