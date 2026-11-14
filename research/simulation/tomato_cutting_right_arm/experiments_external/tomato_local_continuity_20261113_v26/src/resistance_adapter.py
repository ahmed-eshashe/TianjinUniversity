"""Existing v02 cutting resistance, mapped through the exact v22 reduced inertia.

This component does NOT authorize topology changes. The caller must supply a
current, previously unpaid, sharp-edge patch and verified contact evidence.
"""
import numpy as np

def trial(a,marker,direction,tool_velocity,dt,width,eligible=True,Gc=80.):
 marker=np.asarray(marker,float);d=np.asarray(direction,float)
 if marker.shape!=(len(a.q),) or abs(marker.sum()-1)>1e-10:raise ValueError('affine marker required')
 if abs(np.linalg.norm(d)-1)>1e-10 or dt<=0 or width<=0:raise ValueError('finite positive patch and unit direction required')
 if not all(np.isfinite(x).all() for x in [marker,d,np.asarray(tool_velocity),a.v]):raise ValueError('finite state required')
 # Exact generalized inverse mass. The old particle-mass shortcut is invalid
 # after basis aggregation and must not be imported into this runtime.
 force_map=marker[:,None]*d;mobility=a.solve(force_map);inv_mass=float(np.sum(force_map*mobility))
 if inv_mass<=0:raise ValueError('positive marker mobility required')
 vtool=float(d@tool_velocity);vmat=float(d@(marker@a.v));rel=vtool-vmat;Y=Gc*width
 impulse=min(Y*dt,max(rel,0.)/inv_mass) if eligible else 0.
 vnew=a.v+impulse*mobility;slip=max(0.,vtool-float(d@(marker@vnew))) if eligible and impulse>=Y*dt*(1-1e-10) else 0.
 area=width*slip*dt;fracture=Gc*area
 before=.5*float(np.sum(a.v*(a.M@a.v)));after=.5*float(np.sum(vnew*(a.M@vnew)));toolwork=impulse*vtool;loss=.5*impulse**2*inv_mass
 return dict(velocity=vnew,impulse_Ns=impulse,force_N=impulse/dt,area_m2=area,fracture_J=fracture,tool_work_J=toolwork,numerical_loss_J=loss,kinetic_change_J=after-before,energy_residual_J=toolwork-(after-before)-fracture-loss,marker_inverse_mass=inv_mass,topology_authorized=False)
