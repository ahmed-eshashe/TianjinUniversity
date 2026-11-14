"""Host reference for a frozen planar CAD-contact quadrature packet.

Physical world coordinates only. Area weights refer to material reference area.
This does not generate quadrature, perform collision detection, integrate a
robot, or qualify full-target contact. No damping/friction term is introduced.
"""
import numpy as np

def evaluate_pressure(x,indices,barycentric,areas,closest_local,normals_local,rotation,translation,com_local,*,pressure=1.75e9):
 x=np.asarray(x,dtype=float);indices=np.asarray(indices,dtype=int);barycentric=np.asarray(barycentric,dtype=float);areas=np.asarray(areas,dtype=float);rotation=np.asarray(rotation,dtype=float);translation=np.asarray(translation,dtype=float);normals_local=np.asarray(normals_local,dtype=float);closest_local=np.asarray(closest_local,dtype=float)
 n=len(areas)
 if indices.shape!=(n,3) or barycentric.shape!=(n,3) or closest_local.shape!=(n,3) or normals_local.shape!=(n,3) or np.any(areas<=0) or np.any(barycentric<0) or np.max(abs(barycentric.sum(1)-1),initial=0)>1e-12:raise ValueError('Invalid positive reference-area packet')
 if abs(np.linalg.det(rotation)-1)>1e-10 or np.max(abs(rotation.T@rotation-np.eye(3)))>1e-10 or np.max(abs(np.linalg.norm(normals_local,axis=1)-1),initial=0)>1e-10:raise ValueError('Invalid rigid frame or unit normal')
 if not np.isfinite(x).all() or pressure<=0:raise ValueError('Invalid physical state or penalty')
 points=np.einsum('ni,nij->nj',barycentric,x[indices]);q=closest_local@rotation.T+translation;normal=normals_local@rotation.T;gap=np.einsum('ni,ni->n',points-q,normal);negative=np.minimum(gap,0);stiffness=pressure*areas;sample_force=-stiffness[:,None]*negative[:,None]*normal;force=np.zeros_like(x);blocks=np.zeros((len(x),3,3));active=gap<0
 for corner in range(3):
  w=barycentric[:,corner];np.add.at(force,indices[:,corner],w[:,None]*sample_force);np.add.at(blocks,indices[:,corner],(active*stiffness*w*w)[:,None,None]*normal[:,:,None]*normal[:,None,:])
 com=translation+rotation@np.asarray(com_local);body_force=-sample_force.sum(0);body_moment=np.cross(points-com,-sample_force).sum(0)
 return dict(force=force,diagonal_blocks=blocks,sample_force=sample_force,sample_point=points,gap=gap,energy_j=float(.5*np.sum(stiffness*negative**2)),body_wrench=np.r_[body_force,body_moment],body_com=com,scope='Frozen planar quadrature operator only, current physical soft point used for body moment; full CAD geometry changes and robot exchange require separate qualification.')
