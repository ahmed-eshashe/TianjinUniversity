"""Analytic released-interface branch of the unchanged bilinear fracture law."""
import numpy as np
from tomato_objective_cohesion_reference import response

def released_safe_response(positions,patch,*,history=(0.,0.),eligible=False,tangent=False):
 x=np.asarray(positions,dtype=float);old=np.asarray(history,dtype=float)
 if old.shape!=(2,)or not np.isfinite(old).all()or old[0]<0 or not 0<=old[1]<=1:raise ValueError('Valid canonical history required')
 expected=0. if old[0]<=patch['onset'] else 1. if old[0]>=patch['failure'] else patch['failure']*(old[0]-patch['onset'])/(old[0]*(patch['failure']-patch['onset']))
 if abs(old[1]-expected)>1e-10:raise ValueError('History is inconsistent with the same bilinear law')
 if x.shape!=patch['reference'].shape or not np.isfinite(x).all():raise ValueError('Finite prescribed paired geometry required')
 if old[1]<1:return response(x,patch,history=history,eligible=eligible,tangent=tangent)
 result=dict(force_n=np.zeros_like(x),stored_energy_j=0.,incremental_potential_j=0.,undamaged_energy_j=None,equivalent_separation_m=None,trial_history=tuple(old),frame_evaluated=False)
 if tangent:result['force_jacobian_n_m']=np.zeros((x.size,x.size))
 return result

def fracture_dissipation(history,law):
 h=np.asarray(history,dtype=float);l=np.asarray(law,dtype=float);kn,onset,failure=l.T;q=np.minimum(failure,np.maximum(onset,h[:,0]));return .5*kn*onset*failure/(failure-onset)*(q-onset)
