"""Conservative fixed-frame, zero-thickness surface cohesion for offline coupons.

Normal compression is exclusively unilateral contact's responsibility. This is a
model revision, not a clamp on interior spring force. No friction, frame update,
dynamics, blade eligibility detector or evolving coupled damage is supplied.
"""
import numpy as np
from scipy.sparse import coo_matrix
from offline_tomato_patch_sweep import patch_data
from tomato_bonds import DamageState, update_damage


def patch_response(gaps, weights, stiffness, damage, *, tangent=False):
    """One patch's area-weighted potential and its exact gap derivatives.

    U=(1-D)/2 sum w [Kn <gn>+^2 + gt.T Kt gt]. At zero gn use
    the tensile-side generalized Hessian; the gradient is continuous there.
    Fixed material frame x/y/z is only suitable for the supported normal coupons.
    """
    gaps=np.asarray(gaps,dtype=float);weights=np.asarray(weights,dtype=float)
    stiffness=np.asarray(stiffness,dtype=float)
    if (gaps.ndim!=2 or gaps.shape[1]!=3 or weights.shape!=(len(gaps),)
        or stiffness.shape!=(3,3) or not np.isfinite(gaps).all()
        or not np.isfinite(weights).all() or np.any(weights<=0)
        or not np.isclose(weights.sum(),1.,rtol=0,atol=1e-12)
        or not np.isfinite(stiffness).all() or not 0<=damage<=1
        or not np.allclose(stiffness,stiffness.T,rtol=0,atol=1e-12)
        or np.any(stiffness[0,1:]!=0) or np.linalg.eigvalsh(stiffness).min()<=0):
        raise ValueError('Invalid cohesive quadrature or stiffness')
    effective=gaps.copy();effective[:,0]=np.maximum(gaps[:,0],0.)
    gradient=(1-damage)*weights[:,None]*(effective@stiffness)
    energy=float(.5*np.sum(effective*gradient))
    result={'energy_j':energy,'gradient_n':gradient}
    if tangent:
        h=(1-damage)*weights[:,None,None]*np.broadcast_to(stiffness,(len(gaps),3,3)).copy()
        h[gaps[:,0]<0,0,0]=0.
        result['tangent_n_m']=h
    return result


def update_surface_damage(law,state,gaps,weights,stiffness,*,eligible=False):
    """One patch/one energy budget; eligibility remains explicitly external.

    Compression-plus-shear fracture is still outside the validated coupon law.
    Compression alone neither stores normal energy nor drives damage.
    """
    gaps=np.asarray(gaps)
    if np.any((gaps[:,0]<-1e-12)&(np.linalg.norm(gaps[:,1:],axis=1)>1e-12)):
        raise ValueError('Compression-plus-shear fracture remains unsupported')
    energy=patch_response(gaps,weights,stiffness,0.)['energy_j']
    equivalent=np.sqrt(2*energy/law.stiffness_n_m)
    return update_damage(law,state,float(equivalent),eligible=eligible)


class SurfaceCohesion:
    def __init__(self,design,pairs,damage):
        if not np.isfinite(damage) or not 0<=damage<=1:raise ValueError('Invalid damage')
        self.pairs=np.asarray(pairs);self.damage=damage;self.patches=[]
        points=np.asarray([n['position_m'] for n in design['nodes']])
        # Lumped face areas with a normalized local eight-vertex kernel per
        # original patch. Overlapping kernels preserve each patch energy budget;
        # this provisional transfer is not a calibrated spatial material map.
        areas=np.zeros(len(points))
        for tri,tag in zip(design['pieces'][0]['triangles'],design['pieces'][0]['face_tags']):
            if tag=='cut':
                a,b,c=points[tri];area=np.linalg.norm(np.cross(b-a,c-a))/2
                areas[tri]+=area/3
        anchors=np.asarray([p['anchor_yz_m'] for p in design['interface_patches']])
        distances=np.sum((points[pairs[:,0],None,1:]-anchors[None,:,:])**2,axis=2)
        for index,patch in enumerate(design['interface_patches']):
            ids=np.argsort(distances[:,index],kind='stable')[:8]
            weights=areas[pairs[ids,0]]/(distances[ids,index]+.005**2)
            weights=weights/weights.sum()
            rest,k,law=patch_data(design,patch)
            directions=np.asarray(rest)/np.linalg.norm(rest,axis=1)[:,None]
            old_tangent=np.einsum('n,ni,nj->ij',k,directions,directions)
            matrix=np.zeros((3,3));matrix[0,0]=law.stiffness_n_m
            matrix[1:,1:]=old_tangent[1:,1:]
            self.patches.append({'id':patch['id'],'indices':ids,'weights':weights,
                                 'stiffness':matrix,'law':law})
        self.reference_gaps=points[pairs[:,1]]-points[pairs[:,0]]

    def damage_for_patch(self,index):
        return self.damage

    def evaluate(self,x,*,tangent=False):
        gaps=x[self.pairs[:,1]]-x[self.pairs[:,0]]-self.reference_gaps
        energy=0.;gradient=np.zeros_like(x);blocks=np.zeros((len(self.pairs),3,3)) if tangent else None
        for index,patch in enumerate(self.patches):
            ids=patch['indices'];pairs=self.pairs[ids]
            response=patch_response(gaps[ids],patch['weights'],patch['stiffness'],self.damage_for_patch(index),tangent=tangent)
            energy+=response['energy_j']
            np.add.at(gradient,pairs[:,0],-response['gradient_n'])
            np.add.at(gradient,pairs[:,1], response['gradient_n'])
            if tangent:np.add.at(blocks,ids,response['tangent_n_m'])
        result={'energy_j':energy,'gradient_n':gradient}
        if tangent:
            rows=[];cols=[];values=[]
            for a,b,sign in [(0,0,1),(1,1,1),(0,1,-1),(1,0,-1)]:
                rows.append(np.broadcast_to((3*self.pairs[:,a,None]+np.arange(3))[:,:,None],blocks.shape).reshape(-1))
                cols.append(np.broadcast_to((3*self.pairs[:,b,None]+np.arange(3))[:,None,:],blocks.shape).reshape(-1))
                values.append((sign*blocks).reshape(-1))
            result['tangent_n_m']=coo_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(x.size,x.size)).tocsr()
        return result
