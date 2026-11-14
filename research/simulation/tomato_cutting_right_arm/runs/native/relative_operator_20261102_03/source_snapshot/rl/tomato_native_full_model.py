"""Additive native integration of the saved spring/barrier/cohesive tomato model.

Fixed world material frame. Rest geometry and masses retain their saved values;
no tetrahedral elastic material is substituted for the original central springs.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import warp as wp
import newton
from tomato_native_group_cohesion import GroupCohesiveVBD,group_blocks
from newton import State,Contacts
from newton._src.solvers.vbd.solver_vbd import (SolverBase,accumulate_particle_body_contact_force_and_hessian,accumulate_spring_force_and_hessian,accumulate_self_contact_force_and_hessian,solve_elasticity_tile,solve_elasticity,TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE)
from tomato_surface_cohesion import SurfaceCohesion
from tomato_coupled_contact import cut_pairs
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'

@wp.kernel
def volume_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[float],invalid:wp.array[int],force:wp.array[wp.vec3],hessian:wp.array[wp.mat33]):
 i=wp.tid();ids=cells[i];d1=x[ids[1]]-x[ids[0]];d2=x[ids[2]]-x[ids[0]];d3=x[ids[3]]-x[ids[0]];v=volumes[i]
 j=wp.dot(d1,wp.cross(d2,d3))/(6.*v)
 if j<=.1:wp.atomic_add(invalid,0,1)
 elif j<.5:
  r=(j-.1)/.4;prime=(1.-1./r)/.4;second=1./(r*r*.16)
  g1=wp.cross(d2,d3)/(6.*v);g2=wp.cross(d3,d1)/(6.*v);g3=wp.cross(d1,d2)/(6.*v)
  for n in range(4):
   node=ids[n]
   if colors[node]==color:
    g=-g1-g2-g3
    if n==1:g=g1
    elif n==2:g=g2
    elif n==3:g=g3
    wp.atomic_add(force,node,-10000.*v*prime*g)
    wp.atomic_add(hessian,node,10000.*v*second*wp.outer(g,g))

def registry():
 expected={'surface_design.json':'c5e87acf2255875ace869d5fdceb18390a9a51d5fad8e5737738e09fdd8a7f34','mass_stiffness_assignments.json':'e08053a4cfc9b4fe0710081be5f08eca8997d0d24fd80667ac31ab2d32f64bc8'}
 for name,digest in expected.items():
  if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Actual-mesh qualification input changed: '+name)
 design=json.loads((SOURCE/'surface_design.json').read_text());assignments=json.loads((SOURCE/'mass_stiffness_assignments.json').read_text())
 if [n['id'] for n in design['nodes']]!=list(range(len(design['nodes']))):raise ValueError('Contiguous actual node identity required')
 x=np.asarray([n['position_m'] for n in design['nodes']],dtype=float);mass=np.zeros(len(x));springs=[];k=[];cells=[]
 for a in assignments:
  mass[a['global_node_ids']]=a['node_mass_kg'];springs.extend(design['bonds'][i]['nodes'] for i in a['bond_ids']);k.extend(a['bond_stiffness_n_m']);cells.extend(a['integration_cells_global_ids'])
 pairs=cut_pairs(design);cohesion=SurfaceCohesion(design,pairs,0.);cells=np.asarray(cells,dtype=int);d=x[cells[:,1:]]-x[cells[:,:1]];volumes=np.linalg.det(d)/6
 if np.min(mass)<=0 or np.min(volumes)<=0:raise ValueError('Positive actual masses and cell volumes required')
 graph=[set() for _ in x]
 def clique(ids):
  for i in ids:graph[i].update(j for j in ids if i!=j)
 for pair in springs:clique(pair)
 for tet in cells:clique(tet)
 for patch in cohesion.patches:clique(sorted(set(pairs[patch['indices']].ravel().tolist())))
 colors=[-1]*len(x)
 for i in sorted(range(len(x)),key=lambda i:(-len(graph[i]),i)):
  taken={colors[j] for j in graph[i] if colors[j]>=0};c=0
  while c in taken:c+=1
  colors[i]=c
 groups=[[i for i,c in enumerate(colors) if c==color] for color in range(max(colors)+1)]
 return dict(design=design,x=x,mass=mass,springs=np.asarray(springs),k=np.asarray(k),cells=cells,volumes=volumes,pairs=pairs,cohesion=cohesion,colors=groups)

def build_model(data,*,fixed=False,body=False,fixed_nodes=()):
 b=newton.ModelBuilder(gravity=(0.,0.,0.))
 fixed_nodes=set(fixed_nodes)
 for i,(x,m) in enumerate(zip(data['x'],data['mass'])):b.add_particle(wp.vec3(*x),wp.vec3(0.),0. if fixed or i in fixed_nodes else float(m),radius=0.)
 for (a,c),k in zip(data['springs'],data['k']):b.add_spring(int(a),int(c),float(k),0.,0.)
 for piece in data['design']['pieces']:
  for tri in piece['triangles']:b.add_triangle(*tri,tri_ke=0.,tri_ka=0.,tri_kd=0.)
 if body:
  index=b.add_body(is_kinematic=True)
  b.add_shape_box(index,hx=.005,hy=.005,hz=.005,cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.))
 b.color();b.set_coloring(data['colors']);model=b.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
 return model

def configure_solver(model,data,iterations=32,solver_class=None,**solver_options):
 s=(solver_class or FullTomatoVBD)(model,iterations=iterations,**solver_options)
 patches=data['cohesion'].patches;max_pairs=max(len(p['indices']) for p in patches);max_nodes=max(len(set(data['pairs'][p['indices']].ravel().tolist())) for p in patches)
 pairs=np.zeros((len(patches),max_pairs,2),dtype=int);rest=np.zeros((len(patches),max_pairs,3));weights=np.zeros((len(patches),max_pairs));nodes=np.zeros((len(patches),max_nodes),dtype=int);counts=[];node_counts=[];stiffness=[];law=[]
 for i,p in enumerate(patches):
  ids=p['indices'];n=len(ids);pn=sorted(set(data['pairs'][ids].ravel().tolist()));pairs[i,:n]=data['pairs'][ids];rest[i,:n]=data['cohesion'].reference_gaps[ids];weights[i,:n]=p['weights'];nodes[i,:len(pn)]=pn;counts.append(n);node_counts.append(len(pn));stiffness.append(p['stiffness']);l=p['law'];law.append([l.stiffness_n_m,l.onset_m,l.failure_m])
 s.configure(wp.array(pairs,dtype=wp.vec2i),wp.array(rest,dtype=wp.vec3),wp.array(weights,dtype=float),wp.array(counts,dtype=int),wp.array(nodes,dtype=int),wp.array(node_counts,dtype=int),wp.array(stiffness,dtype=wp.mat33),wp.array(law,dtype=wp.vec3),wp.zeros(len(patches),dtype=wp.vec2),wp.zeros(len(patches),dtype=int))
 s.cells=wp.array(data['cells'],dtype=wp.vec4i);s.volumes=wp.array(data['volumes'],dtype=float);s.volume_invalid=wp.zeros(1,dtype=int)
 from tomato_native_full_gather import adjacency
 s.spring_offsets,s.spring_ids=adjacency(data['springs'],model.particle_count)
 s.patch_offsets,s.patch_ids=adjacency([set(data['pairs'][p['indices']].ravel().tolist()) for p in patches],model.particle_count)
 s.cell_offsets,s.cell_ids=adjacency(data['cells'],model.particle_count)
 s.volume_step_fraction=wp.ones(1,dtype=float);s.volume_clip_count=wp.zeros(1,dtype=int)
 return s

class FullTomatoVBD(GroupCohesiveVBD):
 def _penetration_free_truncation(self,particle_q_out=None):
  from tomato_native_volume_steps import predictor_fraction,apply_predictor
  if self.particle_enable_self_contact:raise NotImplementedError('Full-model volume stepping and mesh self-contact need combined bounds')
  if particle_q_out is None:raise ValueError('Full-model trial position required')
  self.volume_step_fraction.fill_(1.)
  wp.launch(predictor_fraction,dim=len(self.cells),inputs=[self.pos_prev_collision_detection,self.particle_displacements,self.cells,self.volumes],outputs=[self.volume_step_fraction,self.volume_invalid],device=self.device)
  wp.launch(apply_predictor,dim=self.model.particle_count,inputs=[particle_q_out,self.pos_prev_collision_detection,self.particle_displacements,self.volume_step_fraction],device=self.device)
 def _volume_safe_update(self,color,positions):
  from tomato_native_volume_steps import colored_step
  wp.launch(colored_step,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,positions,self.pos_prev_collision_detection,self.particle_displacements,self.cell_offsets,self.cell_ids,self.cells,self.volumes],outputs=[self.volume_invalid,self.volume_clip_count],device=self.device)
 def _gather_blocks(self,color,state,dt):
  from tomato_native_full_gather import gather
  wp.launch(gather,dim=self.model.particle_count,inputs=[color,self.model.particle_colors,state.particle_q,self.particle_q_prev,dt,self.spring_offsets,self.spring_ids,self.model.spring_indices,self.model.spring_rest_length,self.model.spring_stiffness,self.model.spring_damping,self.patch_offsets,self.patch_ids,self.pairs,self.rest,self.weights,self.counts,self.stiffness,self.law,self.history,self.eligible,self.invalid,self.cell_offsets,self.cell_ids,self.cells,self.volumes,self.volume_invalid],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
 def commit_cohesion(self,state):
  if int(self.volume_invalid.numpy()[0]):raise ValueError('Native trial crossed the original volume floor')
  from tomato_native_volume_steps import validate_final_material
  self.invalid.zero_()
  wp.launch(validate_final_material,dim=self.pairs.shape[0],inputs=[state.particle_q,self.pairs,self.rest,self.counts,self.history,self.eligible],outputs=[self.invalid],device=self.device)
  super().commit_cohesion(state)

 def _solve_particle_iteration(
     self, state_in: State, state_out: State, contacts: Contacts | None, dt: float, iter_num: int
 ):
     """Solve one VBD iteration for particles."""
     model = self.model

     # Select rigid-body poses for particle-rigid contact evaluation
     if self.integrate_with_external_rigid_solver:
         body_q_for_particles = state_out.body_q
         body_q_prev_for_particles = state_in.body_q
         body_qd_for_particles = state_out.body_qd
     else:
         body_q_for_particles = state_in.body_q
         if model.body_count > 0:
             body_q_prev_for_particles = self.body_q_prev
         else:
             body_q_prev_for_particles = None
         body_qd_for_particles = state_in.body_qd

     # Early exit if no particles
     if model.particle_count == 0:
         return

     # Update collision detection if needed (penetration-free mode only)
     if self.particle_enable_self_contact:
         _Frequency = SolverBase.CollisionFrequencyType
         if (self._sc_mode_this_step == _Frequency.PRE_POST_INIT and iter_num == 0) or (
             self._sc_mode_this_step == _Frequency.ITERATIONS and (iter_num + 1) % self._sc_freq_this_step == 0
         ):
             self._collision_detection_penetration_free(state_in)

     # Zero out forces and hessians
     self.particle_forces.zero_()
     self.particle_hessians.zero_()

     # Iterate over color groups
     for color in range(len(self.model.particle_color_groups)):
         self._gather_blocks(color,state_in,dt)
         if contacts is not None:
             wp.launch(
                 kernel=accumulate_particle_body_contact_force_and_hessian,
                 dim=contacts.soft_contact_max,
                 inputs=[
                     dt,
                     color,
                     self.particle_q_prev,
                     state_in.particle_q,
                     model.particle_colors,
                     # body-particle contact
                     self.friction_epsilon,
                     model.particle_radius,
                     contacts.soft_contact_indices,
                     contacts.soft_contact_count,
                     contacts.soft_contact_max,
                     self.body_particle_contact_penalty_k,
                     self.body_particle_contact_material_ke,
                     self.body_particle_contact_material_kd,
                     self.body_particle_contact_material_mu,
                     model.shape_body,
                     body_q_for_particles,
                     body_q_prev_for_particles,
                     body_qd_for_particles,
                     model.body_com,
                     contacts.soft_contact_shape,
                     contacts.soft_contact_body_pos,
                     contacts.soft_contact_body_vel,
                     contacts.soft_contact_normal,
                     model.shape_margin,
                     contacts.soft_contact_barycentric,
                 ],
                 outputs=[
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 device=self.device,
             )

         if self.particle_enable_self_contact:
             wp.launch(
                 kernel=accumulate_self_contact_force_and_hessian,
                 dim=self.particle_self_contact_evaluation_kernel_launch_size,
                 inputs=[
                     dt,
                     color,
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_colors,
                     self.model.tri_indices,
                     self.model.edge_indices,
                     # self-contact
                     self.trimesh_collision_info,
                     self.particle_self_contact_margin,
                     self.model.soft_contact_ke,
                     self.model.soft_contact_kd,
                     self.model.soft_contact_mu,
                     self.friction_epsilon,
                     self._self_contact_edge_edge_parallel_epsilon,
                 ],
                 outputs=[self.particle_forces, self.particle_hessians],
                 device=self.device,
                 max_blocks=self.model.device.sm_count,
             )
         if self.use_particle_tile_solve:
             wp.launch(
                 kernel=solve_elasticity_tile,
                 dim=self.model.particle_color_groups[color].size * TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE,
                 block_dim=TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE,
                 inputs=[
                     dt,
                     self.model.particle_color_groups[color],
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_mass,
                     self.inertia,
                     self.model.particle_flags,
                     self.model.tri_indices,
                     self.model.tri_poses,
                     self.model.tri_materials,
                     self.model.tri_areas,
                     self.model.edge_indices,
                     self.model.edge_rest_angle,
                     self.model.edge_rest_length,
                     self.model.edge_bending_properties,
                     self.model.tet_indices,
                     self.model.tet_poses,
                     self.model.tet_materials,
                     self.particle_adjacency,
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 outputs=[
                     self.particle_displacements,
                 ],
                 device=self.device,
             )
         else:
             wp.launch(
                 kernel=solve_elasticity,
                 dim=self.model.particle_color_groups[color].size,
                 inputs=[
                     dt,
                     self.model.particle_color_groups[color],
                     self.particle_q_prev,
                     state_in.particle_q,
                     self.model.particle_mass,
                     self.inertia,
                     self.model.particle_flags,
                     self.model.tri_indices,
                     self.model.tri_poses,
                     self.model.tri_materials,
                     self.model.tri_areas,
                     self.model.edge_indices,
                     self.model.edge_rest_angle,
                     self.model.edge_rest_length,
                     self.model.edge_bending_properties,
                     self.model.tet_indices,
                     self.model.tet_poses,
                     self.model.tet_materials,
                     self.particle_adjacency,
                     self.particle_forces,
                     self.particle_hessians,
                 ],
                 outputs=[
                     self.particle_displacements,
                 ],
                 device=self.device,
             )
         self._volume_safe_update(color,state_in.particle_q)

     wp.copy(state_out.particle_q, state_in.particle_q)
