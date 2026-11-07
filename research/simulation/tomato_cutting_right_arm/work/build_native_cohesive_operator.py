from pathlib import Path
import ast,textwrap
root=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');backend=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/solver_vbd.py')
s=backend.read_text();tree=ast.parse(s);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SolverVBD');fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_solve_particle_iteration');method='\n'.join(s.splitlines()[fn.lineno-1:fn.end_lineno])+'\n'
needle='        for color in range(len(self.model.particle_color_groups)):\n'
inject='''            wp.launch(cohesive_blocks,dim=self.pairs.shape[0],inputs=[color,model.particle_colors,state_in.particle_q,self.pairs,self.rest,self.stiffness,self.law,self.history,self.eligible,self.invalid],outputs=[self.particle_forces,self.particle_hessians],device=self.device)
'''
assert needle in method;method=method.replace(needle,needle+inject)
head='''"""Isolated fixed-frame cohesive VBD extension; no installed code modifications.

Consistent loading-side diagonal blocks and immutable trial history. This is a
one-pair-per-patch diagnostic, not a general objective tomato material model.
Import only inside a guarded native worker after AppLauncher.
"""
import warp as wp
from newton._src.solvers.vbd.solver_vbd import (SolverVBD,SolverBase,accumulate_particle_body_contact_force_and_hessian,
 accumulate_spring_force_and_hessian,accumulate_self_contact_force_and_hessian,solve_elasticity_tile,
 solve_elasticity,TILE_SIZE_TRI_MESH_ELASTICITY_SOLVE)

@wp.kernel
def cohesive_blocks(color:int,colors:wp.array[int],x:wp.array[wp.vec3],pairs:wp.array[wp.vec2i],rest:wp.array[wp.vec3],
 stiffness:wp.array[wp.mat33],law:wp.array[wp.vec3],history:wp.array[wp.vec2],eligible:wp.array[int],invalid:wp.array[int],
 forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 i=wp.tid();pair=pairs[i];g=x[pair[1]]-x[pair[0]]-rest[i]
 if g[0]<-1.e-12 and wp.length(wp.vec2(g[1],g[2]))>1.e-12:
  wp.atomic_add(invalid,0,1)
 e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);k=stiffness[i];grad=k*e
 q=wp.sqrt(wp.max(wp.dot(e,grad)/law[i][0],0.));a=law[i][1];b=law[i][2];old=history[i]
 d=old[1];derivative=float(0.)
 if eligible[i]!=0 and q>=old[0]:
  if q>=b:d=1.
  elif q>a:
   candidate=b*(q-a)/(q*(b-a))
   if candidate>=d:
    d=candidate;derivative=b*a/((b-a)*q*q)
 h=k
 if g[0]<0.:h[0,0]=0.
 h=(1.-d)*h
 if derivative>0.:h=h-derivative/(law[i][0]*q)*wp.outer(grad,grad)
 force=(1.-d)*grad
 for side in range(2):
  node=pair[side]
  if colors[node]==color:
   sign=float(1.)
   if side==1:sign=-1.
   wp.atomic_add(forces,node,sign*force);wp.atomic_add(hessians,node,h)

@wp.kernel
def commit_history(x:wp.array[wp.vec3],pairs:wp.array[wp.vec2i],rest:wp.array[wp.vec3],stiffness:wp.array[wp.mat33],
 law:wp.array[wp.vec3],eligible:wp.array[int],history:wp.array[wp.vec2]):
 i=wp.tid()
 if eligible[i]!=0:
  pair=pairs[i];g=x[pair[1]]-x[pair[0]]-rest[i];e=wp.vec3(wp.max(g[0],0.),g[1],g[2]);q=wp.sqrt(wp.max(wp.dot(e,stiffness[i]*e)/law[i][0],0.))
  old=history[i];a=law[i][1];b=law[i][2];maximum=wp.max(q,old[0]);d=old[1]
  if maximum>=b:d=1.
  elif maximum>a:d=wp.max(d,b*(maximum-a)/(maximum*(b-a)))
  history[i]=wp.vec2(maximum,d)

class CohesiveVBD(SolverVBD):
 def configure_cohesion(self,pairs,rest,stiffness,law,history,eligible):
  self.pairs=pairs;self.rest=rest;self.stiffness=stiffness;self.law=law;self.history=history;self.eligible=eligible
  self.invalid=wp.zeros(1,dtype=int,device=self.device)
 def commit_cohesion(self,state):
  if int(self.invalid.numpy()[0]):raise ValueError('Unsupported compression/shear trial; history not committed')
  wp.launch(commit_history,dim=self.pairs.shape[0],inputs=[state.particle_q,self.pairs,self.rest,self.stiffness,self.law,self.eligible,self.history],device=self.device)
'''
# Retain the installed iteration implementation verbatim apart from one per-color force/Hessian hook.
(root/'rl/tomato_native_cohesive_operator.py').write_text(head+'\n'+textwrap.indent(textwrap.dedent(method),' '))
