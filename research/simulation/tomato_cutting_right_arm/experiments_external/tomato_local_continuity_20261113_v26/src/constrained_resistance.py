"""Work-conjugate v02 ideal resistance, with affine area and exact constraints.

Gc and the irreversible-work criterion are unchanged. This function prepares
an impulse; it does not authorize a geometric split or debit a fracture ledger.
"""
import numpy as np
from scipy.linalg import cho_factor,cho_solve

def inverse_free(a,rhs,fixed):
 fixed=np.asarray(fixed,bool)
 if not fixed.any():return a.solve(rhs)
 free=np.flatnonzero(~fixed);key=tuple(np.flatnonzero(fixed));cache=getattr(a,'_constraint_factor',None)
 if cache is None or cache[0]!=key:
  factor=cho_factor(a.M[free][:,free].toarray(),lower=True);a._constraint_factor=(key,free,factor)
 else:_,free,factor=cache
 out=np.zeros_like(rhs);out[free]=cho_solve(factor,rhs[free]);return out

def trial(a,marker,normal_ref,F,tool_velocity,dt,width_ref,fixed=None,eligible=True,Gc=80.):
 marker=np.asarray(marker,float);normal_ref=np.asarray(normal_ref,float);F=np.asarray(F,float);tool_velocity=np.asarray(tool_velocity,float)
 if marker.shape!=(len(a.q),) or abs(marker.sum()-1)>1e-10:raise ValueError('affine marker required')
 if abs(np.linalg.norm(normal_ref)-1)>1e-10 or dt<=0 or width_ref<=0:raise ValueError('positive patch/time and unit reference normal required')
 if not all(np.isfinite(x).all() for x in [marker,normal_ref,F,tool_velocity,a.v]):raise ValueError('finite trial required')
 if np.linalg.det(F)<=.1 or np.linalg.det(F)>=10:raise ValueError('inadmissible material map')
 fixed=np.zeros(len(a.q),bool) if fixed is None else np.asarray(fixed,bool)
 if np.any(abs(a.v[fixed])>1e-12):raise ValueError('stationary support contract requires zero fixed velocity')
 covector=np.linalg.solve(F.T,normal_ref);B=marker[:,None]*covector;mobility=inverse_free(a,B,fixed);inverse_mass=float(np.sum(B*mobility));relative=float(tool_velocity@covector-np.sum(B*a.v));Y=Gc*width_ref
 if inverse_mass<=0:raise ValueError('immobile cutting marker cannot pay a slip event')
 J=min(Y*dt,max(relative,0.)/inverse_mass) if eligible else 0.;velocity=a.v+J*mobility;post_relative=relative-J*inverse_mass;slip=max(post_relative,0.) if eligible and J>=Y*dt*(1-1e-10) else 0.;area=width_ref*slip*dt;fracture=Gc*area;tool_work=J*float(tool_velocity@covector);numerical_loss=.5*J*J*inverse_mass
 deltaK=.5*float(np.sum(velocity*(a.M@velocity))-np.sum(a.v*(a.M@a.v)));support=a.M@(velocity-a.v)-J*B
 return dict(velocity=velocity,impulse_vector_Ns=J*covector,impulse_scalar_Ns=J,force_vector_N=J/dt*covector,area_m2=area,fracture_J=fracture,tool_work_J=tool_work,numerical_loss_J=numerical_loss,kinetic_change_J=deltaK,energy_residual_J=tool_work-deltaK-fracture-numerical_loss,support_impulses_Ns=support,reference_slip_m=slip*dt,marker_inverse_mass=inverse_mass,topology_authorized=False)
