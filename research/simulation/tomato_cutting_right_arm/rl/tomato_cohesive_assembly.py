"""Fixed-frame cohesive global force/Hessian assembly reference, no native solver.

Frozen damage Hessian is not the active softening algorithmic tangent. Injecting
these forces only through particle_f does not implement implicit VBD cohesion.
"""
import math
from tomato_cohesive_adapter_reference import patch_reference


def assemble(positions,pairs,reference_gaps,patches):
    if len(pairs)!=len(reference_gaps) or not positions:raise ValueError('Complete pair/reference registry required')
    if any(len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p) for p in positions):raise ValueError('Finite nodal positions required')
    gaps=[]
    for pair,rest in zip(pairs,reference_gaps):
        if len(pair)!=2 or pair[0]==pair[1] or any(type(i)is not int or not 0<=i<len(positions) for i in pair) or len(rest)!=3 or not all(math.isfinite(x) for x in rest):raise ValueError('Invalid pair/reference')
        a,b=pair;gaps.append([positions[b][j]-positions[a][j]-rest[j] for j in range(3)])
    force=[[0.,0.,0.] for _ in positions];hessian={};energies=[];ids=set()
    for patch in patches:
        if patch['id'] in ids:raise ValueError('Duplicate patch identity')
        ids.add(patch['id']);local=patch['indices']
        if not local or len(set(local))!=len(local) or any(type(i)is not int or not 0<=i<len(pairs) for i in local):raise ValueError('Invalid patch quadrature registry')
        response=patch_reference([gaps[i] for i in local],patch['weights'],patch['stiffness'],patch['damage'])
        energies.append(response['energy_j'])
        for idx,g,h in zip(local,response['gap_gradient_n'],response['frozen_damage_tangent_n_m']):
            a,b=pairs[idx]
            for j in range(3):force[a][j]+=g[j];force[b][j]-=g[j]
            for node1,sign1 in [(a,-1),(b,1)]:
                for node2,sign2 in [(a,-1),(b,1)]:
                    for j in range(3):
                        for k in range(3):
                            key=(3*node1+j,3*node2+k);hessian[key]=hessian.get(key,0.)+sign1*sign2*h[j][k]
    return {'energy_j':math.fsum(energies),'nodal_force_n':force,
            'frozen_damage_energy_hessian_triplets':[[a,b,v] for (a,b),v in sorted(hessian.items()) if v!=0.],
            'native_runtime_validated':False,'implicit_softening_stability_validated':False}
