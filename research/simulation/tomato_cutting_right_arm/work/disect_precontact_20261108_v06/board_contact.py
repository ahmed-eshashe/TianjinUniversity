"""Finite saved-board top footprint, inherited uncalibrated nodal penalty law."""
import numpy as np
def inside(q,mapping):
    world=np.asarray(q)@mapping['rotation'].T+mapping['translation']
    return np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2],axis=1)<=0
def force(q,v,mapping,mask=None):
    q=np.asarray(q);v=np.asarray(v);active=inside(q,mapping).astype(float)
    if mask is not None:active*=mask
    depth=np.maximum(.001-q[:,1],0.);out=np.zeros_like(q);out[:,1]=1000*depth
    out[:,0]=-np.clip(1000*v[:,0],-.2*1000*depth,.2*1000*depth);out[:,2]=-np.clip(1000*v[:,2],-.2*1000*depth,.2*1000*depth)
    return out*active[:,None]
