"""Host-only slab contact comparisons; not a new native contact model.

Slab |z| <= h, edge endpoints -L and +L, zero radii/margins.
The normalized edge-parameter integral is an alternative mathematical reference,
not Newton's per-feature penalty or a calibrated line/area traction model.
"""
import math


def validate(h, length, stiffness):
    if not all(math.isfinite(x) for x in (h,length,stiffness)) or not 0 < h < length or stiffness <= 0:
        raise ValueError('Require finite 0 < slab half-thickness < endpoint halfspan and positive stiffness')


def point_penalty(z, h, stiffness):
    if not all(math.isfinite(x) for x in (z,h,stiffness)) or h <= 0 or stiffness <= 0:
        raise ValueError('Finite coordinate and positive parameters required')
    penetration=max(0.,h-abs(z))
    energy=.5*stiffness*penetration**2
    if z == 0:
        return {'phi_m':-h,'energy_j':energy,'force_n':None,'normal':None,
                'status':'ambiguous_medial_plane'}
    normal=1. if z > 0 else -1.
    return {'phi_m':abs(z)-h,'energy_j':energy,'force_n':normal*stiffness*penetration,
            'normal':normal,'status':'unique_branch' if penetration>0 else 'clear_or_touch'}


def normalized_integral_reference(h, length, stiffness):
    validate(h,length,stiffness)
    endpoint=stiffness*h**3/(12*length**2)
    return {'energy_j':stiffness*h**3/(6*length),
            'endpoint_forces_n':[-endpoint,endpoint],'net_force_n':0.}


def sample_slab(h, length, stiffness, *, subdivisions_per_side=1):
    """Two-point Gauss on each half-slab subinterval, plus unweighted comparison.

    Quadrature weights integrate dt = dz/(2L), so sum to h/L over the active
    segment; these weights would require a different coefficient/energy model
    from native per-contact Newton penalties. No native material value is set.
    """
    validate(h,length,stiffness)
    if type(subdivisions_per_side) is not int or not 1 <= subdivisions_per_side <= 64:
        raise ValueError('Bounded positive integer subdivision count required')
    weighted=[0.,0.]; raw=[0.,0.]; weighted_energy=0.; raw_energy=0.; weight_sum=0.
    nodes=[]
    for side in (-1.,1.):
        for index in range(subdivisions_per_side):
            lo=h*index/subdivisions_per_side; hi=h*(index+1)/subdivisions_per_side
            for node in (-1/math.sqrt(3),1/math.sqrt(3)):
                z=side*((lo+hi)/2+(hi-lo)*node/2)
                qweight=(hi-lo)/(4*length)
                result=point_penalty(z,h,stiffness)
                bary=[(length-z)/(2*length),(length+z)/(2*length)]
                for j in (0,1):
                    raw[j]+=bary[j]*result['force_n']
                    weighted[j]+=qweight*bary[j]*result['force_n']
                weighted_energy+=qweight*result['energy_j'];raw_energy+=result['energy_j'];weight_sum+=qweight
                nodes.append({'z_m':z,'quadrature_weight':qweight,'barycentric':bary,
                              'point_force_n':result['force_n']})
    return {'sample_count':len(nodes),'weight_sum':weight_sum,'weighted_endpoint_forces_n':weighted,
            'raw_endpoint_forces_n':raw,'weighted_net_force_n':sum(weighted),'raw_net_force_n':sum(raw),
            'weighted_energy_j':weighted_energy,'raw_energy_j':raw_energy,'nodes':nodes}
