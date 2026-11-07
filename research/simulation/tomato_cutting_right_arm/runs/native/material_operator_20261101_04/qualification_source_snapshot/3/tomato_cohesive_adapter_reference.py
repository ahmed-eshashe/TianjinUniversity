"""Stdlib packing/reference for preserved fixed-frame surface cohesion.

Not native dynamics. No damping or objective rotating-frame law is invented.
Area is already included in the supplied patch stiffness: do not multiply again.
"""
import math


def patch_reference(gaps,weights,stiffness,damage):
    if not gaps or len(weights)!=len(gaps) or len(stiffness)!=3 or any(len(r)!=3 for r in stiffness):raise ValueError('Patch dimensions invalid')
    if type(damage) not in (int,float) or not math.isfinite(damage) or not 0<=damage<=1:raise ValueError('Invalid damage')
    if any(len(g)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in g) for g in gaps):raise ValueError('Finite gaps required')
    if any(type(w) not in (int,float) or not math.isfinite(w) or w<=0 for w in weights) or abs(math.fsum(weights)-1.)>1e-12:raise ValueError('Normalized positive quadrature required')
    k=stiffness
    if any(type(x) not in (int,float) or not math.isfinite(x) for r in k for x in r):raise ValueError('Finite stiffness required')
    # Match original allclose(rtol=0,atol=1e-12) symmetry validation.
    # Preserve tiny stored asymmetry verbatim; never round/symmetrize coefficients.
    asymmetry=max(abs(k[i][j]-k[j][i]) for i in range(3) for j in range(3))
    if asymmetry>1e-12 or any(k[0][j]!=0 for j in (1,2)):
        raise ValueError('Original symmetry tolerance and zero normal-row coupling required')
    if k[0][0]<=0 or k[1][1]<=0 or k[2][2]<=0 or k[1][1]*k[2][2]-k[2][1]**2<=0:raise ValueError('Positive definite patch stiffness required')
    gradients=[];tangents=[];terms=[]
    for g,w in zip(gaps,weights):
        effective=[max(g[0],0.),g[1],g[2]]
        grad=[(1-damage)*w*math.fsum(effective[j]*k[j][i] for j in range(3)) for i in range(3)]
        h=[[(1-damage)*w*x for x in row] for row in k]
        if g[0]<0:h[0][0]=0.
        gradients.append(grad);tangents.append(h);terms.append(.5*math.fsum(a*b for a,b in zip(effective,grad)))
    energy=math.fsum(terms)
    if not math.isfinite(energy) or any(not math.isfinite(x) for row in gradients for x in row):raise ValueError('Constitutive arithmetic overflow')
    return {'energy_j':energy,'gap_gradient_n':gradients,'frozen_damage_tangent_n_m':tangents,
        'force_on_first_n':gradients,'force_on_second_n':[[-x for x in row] for row in gradients],
        'stiffness_asymmetry_n_m':asymmetry,'exact_symmetric_stiffness':asymmetry==0.,
        'original_roundoff_convention_preserved':True,
        'native_runtime_validated':False,'frame_scope':'fixed_material_normal_x',
        'damping_supplied':False,'algorithmic_softening_tangent_supplied':False}
