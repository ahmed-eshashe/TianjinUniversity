"""Candidate complete-surface self-contact on fixed barycentric collision proxies.

Only collision geometry near the zero-gap seam is recessed. Original mechanical
nodes/cells/springs/masses remain unchanged. J^T maps forces back; the scattered
positive contact blocks are a preconditioner, not the full contact Hessian.
"""
import numpy as np
import warp as wp
import newton
from newton._src.geometry.kernels import triangle_closest_point
from newton._src.geometry.tri_mesh_collision import TriMeshCollisionInfo
from newton._src.solvers.vbd.solver_vbd import SolverVBD,accumulate_self_contact_force_and_hessian
from tomato_collision_embedding import build_embedding
from tomato_collision_local_filters import local_filter_maps

@wp.kernel
def embed_positions(x:wp.array[wp.vec3],indices:wp.array[wp.vec4i],weights:wp.array[wp.vec4d],proxy:wp.array[wp.vec3]):
 i=wp.tid();p=wp.vec3d(0.)
 for j in range(4):
  a=x[indices[i][j]];p+=weights[i][j]*wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]))
 proxy[i]=wp.vec3(float(p[0]),float(p[1]),float(p[2]))

@wp.kernel
def map_contact(color:int,colors:wp.array[int],offsets:wp.array[int],rows:wp.array[wp.vec2i],weights:wp.array[wp.vec4d],pf:wp.array[wp.vec3],ph:wp.array[wp.mat33],force:wp.array[wp.vec3],hessian:wp.array[wp.mat33]):
 node=wp.tid()
 if color<0 or colors[node]==color:
  f=wp.vec3d(0.);h=wp.mat33(0.)
  for k in range(offsets[node],offsets[node+1]):
   row=rows[k];w=weights[row[0]][row[1]];a=pf[row[0]];f+=w*wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]));h+=float(w*w)*ph[row[0]]
  force[node]+=wp.vec3(float(f[0]),float(f[1]),float(f[2]));hessian[node]+=h

@wp.kernel
def contact_bounds(x:wp.array[wp.vec3],triangles:wp.array2d[int],edges:wp.array2d[int],info_array:wp.array[TriMeshCollisionInfo],relaxation:float,epsilon:float,bounds:wp.array[float],invalid:wp.array[int]):
 source=wp.tid();info=info_array[0]
 if source<info.vertex_colliding_triangles_count.shape[0]:
  count=info.vertex_colliding_triangles_count[source];capacity=info.vertex_colliding_triangles_buffer_sizes[source];offset=info.vertex_colliding_triangles_offsets[source]
  if capacity>0 and count>=capacity:wp.atomic_add(invalid,0,1)
  for j in range(wp.min(count,capacity)):
   v=info.vertex_colliding_triangles[2*(offset+j)];t=info.vertex_colliding_triangles[2*(offset+j)+1];a=triangles[t,0];b=triangles[t,1];c=triangles[t,2];point,bary,feature=triangle_closest_point(x[a],x[b],x[c],x[v]);distance=wp.length(x[v]-point)
   if distance<=0.:wp.atomic_add(invalid,0,1)
   bound=relaxation*distance
   wp.atomic_min(bounds,v,bound);wp.atomic_min(bounds,a,bound);wp.atomic_min(bounds,b,bound);wp.atomic_min(bounds,c,bound)
 if source<info.edge_colliding_edges_count.shape[0]:
  count=info.edge_colliding_edges_count[source];capacity=info.edge_colliding_edges_buffer_sizes[source];offset=info.edge_colliding_edges_offsets[source]
  if capacity>0 and count>=capacity:wp.atomic_add(invalid,0,1)
  for j in range(wp.min(count,capacity)):
   e0=info.edge_colliding_edges[2*(offset+j)];e1=info.edge_colliding_edges[2*(offset+j)+1];a=edges[e0,2];b=edges[e0,3];c=edges[e1,2];d=edges[e1,3];st=wp.closest_point_edge_edge(x[a],x[b],x[c],x[d],epsilon);distance=st[2]
   if distance<=0.:wp.atomic_add(invalid,0,1)
   bound=relaxation*distance
   wp.atomic_min(bounds,a,bound);wp.atomic_min(bounds,b,bound);wp.atomic_min(bounds,c,bound);wp.atomic_min(bounds,d,bound)

@wp.kernel
def physical_bounds(offsets:wp.array[int],rows:wp.array[wp.vec2i],proxy_bound:wp.array[float],bound:wp.array[float]):
 node=wp.tid();value=float(wp.inf)
 for k in range(offsets[node],offsets[node+1]):value=wp.min(value,proxy_bound[rows[k][0]])
 bound[node]=value

@wp.kernel
def cap_displacements(color:int,colors:wp.array[int],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],query_position:wp.array[wp.vec3],bounds:wp.array[float]):
 i=wp.tid()
 if color<0 or colors[i]==color:
  target=baseline[i]+displacement[i];delta=target-query_position[i];length=wp.length(delta)
  if length>bounds[i]:displacement[i]=query_position[i]+delta*(bounds[i]/length)-baseline[i]

class EmbeddedSelfContact:
 def __init__(self,data,*,margin=.0001,stiffness=1000.,capacity=128,edge_epsilon=1e-5):
  self.embedding=build_embedding(data['design'],data['cells'],interaction_distance_m=margin);e=self.embedding;self.margin=margin;self.query_radius=2*margin;self.node_count=len(data['x']);self.relaxation=.4
  # Embedding is built in source coordinates; runtime shifts/rotations map exactly.
  self.indices=wp.array(e['indices'],dtype=wp.vec4i);self.weights=wp.array(e['weights'],dtype=wp.vec4d)
  vertex_map,edge_filter,reference_edges=local_filter_maps(e,data['design'],radius=1.01*margin)
  self.local_filter_counts=dict(vertex_pairs=sum(map(len,vertex_map.values())),edge_pairs=sum(map(len,edge_filter.values())),cross_piece_excluded=0)
  b=newton.ModelBuilder(gravity=(0.,0.,0.))
  for p in e['reference_positions']:b.add_particle(wp.vec3(*p),wp.vec3(0.),0.,radius=0.)
  edge_map={}
  for tri in e['triangles']:
   b.add_triangle(*tri,tri_ke=0.,tri_ka=0.,tri_kd=0.)
   for a,c,opposite in [(tri[0],tri[1],tri[2]),(tri[1],tri[2],tri[0]),(tri[2],tri[0],tri[1])]:edge_map.setdefault(tuple(sorted([int(a),int(c)])),[]).append(int(opposite))
  for (a,c),opposite in sorted(edge_map.items()):
   if len(opposite)!=2:raise ValueError('Closed manifold proxy surface required')
   b.add_edge(opposite[0],opposite[1],a,c,rest=0.,edge_ke=0.,edge_kd=0.)
  b.color();self.model=b.finalize(device='cuda:0');self.model.soft_contact_ke=stiffness;self.model.soft_contact_kd=0.;self.model.soft_contact_mu=0.
  self.solver=SolverVBD(self.model,iterations=1,particle_enable_self_contact=True,particle_self_contact_margin=margin,particle_self_contact_gap=margin,particle_rest_shape_contact_exclusion_radius=0.,particle_topological_contact_filter_threshold=2,particle_edge_parallel_epsilon=edge_epsilon,particle_vertex_contact_buffer_size=capacity,particle_edge_contact_buffer_size=capacity,particle_external_vertex_contact_filtering_map=vertex_map,particle_external_edge_contact_filtering_map=edge_filter)
  self.state=self.model.state();self.previous=wp.clone(self.state.particle_q);self.colors=wp.zeros(self.model.particle_count,dtype=int);self.force=wp.zeros(self.model.particle_count,dtype=wp.vec3d);self.hessian=wp.zeros(self.model.particle_count,dtype=wp.mat33d);self.proxy_bounds=wp.empty(self.model.particle_count,dtype=float);self.bounds=wp.empty(self.node_count,dtype=float);self.query_physical=wp.empty(self.node_count,dtype=wp.vec3);self.invalid=wp.zeros(1,dtype=int)
  adjacency=[[] for _ in range(self.node_count)]
  for proxy,(nodes,weights) in enumerate(zip(e['indices'],e['weights'])):
   for j,(node,w) in enumerate(zip(nodes,weights)):
    if w>0:adjacency[node].append([proxy,j])
  offsets=[0];rows=[]
  for row in adjacency:rows.extend(row);offsets.append(len(rows))
  self.offsets=wp.array(offsets,dtype=int);self.rows=wp.array(rows,dtype=wp.vec2i)
  self.stencil_capacity=131072;self.endpoint=wp.empty(self.stencil_capacity,dtype=wp.vec4i);self.coefficient=wp.empty(self.stencil_capacity,dtype=wp.vec4d);self.stencil_count=wp.zeros(1,dtype=int);self.physical_ids=wp.empty((self.stencil_capacity,16),dtype=int);self.physical_coeff=wp.empty((self.stencil_capacity,16),dtype=wp.float64);self.precise_position=wp.empty(self.model.particle_count,dtype=wp.vec3d);self.physical_force=wp.zeros(self.node_count,dtype=wp.vec3d);self.physical_hessian=wp.zeros(self.node_count,dtype=wp.mat33d);self.contact_energy=wp.zeros(1,dtype=wp.float64)

 def detect(self,physical):
  from tomato_canonical_self_contact import precise_embedding,build_stencils,embed_stencils
  wp.copy(self.query_physical,physical);wp.launch(precise_embedding,dim=self.model.particle_count,inputs=[physical,self.indices,self.weights],outputs=[self.precise_position,self.state.particle_q]);wp.copy(self.previous,self.state.particle_q);self.solver._collision_detection_penetration_free(self.state);self.proxy_bounds.fill_(self.relaxation*self.query_radius)
  wp.launch(contact_bounds,dim=max(self.model.particle_count,self.model.edge_count),inputs=[self.state.particle_q,self.model.tri_indices,self.model.edge_indices,self.solver.trimesh_collision_info,self.relaxation,self.solver._self_contact_edge_edge_parallel_epsilon],outputs=[self.proxy_bounds,self.invalid])
  wp.launch(physical_bounds,dim=self.node_count,inputs=[self.offsets,self.rows,self.proxy_bounds],outputs=[self.bounds])
  self.stencil_count.zero_();wp.launch(build_stencils,dim=max(self.model.particle_count,self.model.edge_count),inputs=[self.precise_position,self.model.tri_indices,self.model.edge_indices,self.solver.trimesh_collision_info,self.stencil_capacity],outputs=[self.endpoint,self.coefficient,self.stencil_count,self.invalid]);wp.launch(embed_stencils,dim=self.stencil_capacity,inputs=[self.endpoint,self.coefficient,self.stencil_count,self.stencil_capacity,self.indices,self.weights],outputs=[self.physical_ids,self.physical_coeff])

 def evaluate(self,physical,dt):
  from tomato_canonical_self_contact import evaluate_stencils
  self.force.zero_();self.hessian.zero_();self.physical_force.zero_();self.physical_hessian.zero_();self.contact_energy.zero_()
  wp.launch(evaluate_stencils,dim=self.stencil_capacity,inputs=[physical,self.physical_ids,self.physical_coeff,self.endpoint,self.coefficient,self.stencil_count,self.stencil_capacity,wp.float64(self.margin),wp.float64(self.model.soft_contact_ke)],outputs=[self.physical_force,self.physical_hessian,self.force,self.hessian,self.contact_energy,self.invalid],device=self.model.device)

 def scatter(self,color,colors,force,hessian):
  from tomato_canonical_self_contact import add_physical_contact
  wp.launch(add_physical_contact,dim=self.node_count,inputs=[color,colors,self.physical_force,self.physical_hessian],outputs=[force,hessian])

 def cap(self,color,colors,baseline,displacements):
  wp.launch(cap_displacements,dim=self.node_count,inputs=[color,colors,baseline,displacements,self.query_physical,self.bounds])
