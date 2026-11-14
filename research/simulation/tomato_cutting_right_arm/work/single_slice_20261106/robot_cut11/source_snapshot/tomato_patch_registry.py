"""Lossless fixed-frame surface-cohesion parameter export, not native mechanics."""
import dataclasses
import math
from tomato_bonds import CohesiveLaw


def export_registry(design,cohesion,*,source_sha256):
    if len(design['interface_patches'])!=len(cohesion.patches):raise ValueError('Patch identity mismatch')
    rows=[]
    for index,p in enumerate(cohesion.patches):
        law=dataclasses.asdict(p['law'])
        rows.append({'id':p['id'],'original_patch_index':index,
            'area_m2':design['interface_patches'][index]['area_m2'],
            'pair_indices':p['indices'].tolist(),'weights':p['weights'].tolist(),
            'stiffness_n_m':p['stiffness'].tolist(),'law':law,
            'fracture_budget_j':law['area_m2']*law['fracture_energy_j_m2']})
    result={'version':1,'units':{'position':'m','stiffness':'N/m','area':'m2','fracture_budget':'J'},
        'frame_scope':'fixed_material_normal_x','source_sha256':dict(source_sha256),
        'positions_m':[n['position_m'] for n in design['nodes']],
        'node_sides':[n['side'] for n in design['nodes']],
        'pairs':cohesion.pairs.tolist(),'reference_gaps_m':cohesion.reference_gaps.tolist(),
        'patches':rows,'material_calibrated':False,'native_runtime_validated':False,
        'surface_cohesive_damping_supplied':False,'native_spring_replacement_allowed':False}
    validate_registry(result)
    return result


def validate_registry(data):
    if data.get('version')!=1 or data.get('frame_scope')!='fixed_material_normal_x':raise ValueError('Versioned fixed material frame required')
    if data.get('native_spring_replacement_allowed') is not False or data.get('native_runtime_validated') is not False:raise ValueError('Parameter export cannot claim native spring replacement or validation')
    if data.get('units')!={'position':'m','stiffness':'N/m','area':'m2','fracture_budget':'J'}:raise ValueError('Exact SI schema required')
    sources=data.get('source_sha256')
    if not isinstance(sources,dict) or not sources or any(not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h) for h in sources.values()):raise ValueError('Source digests required')
    x=data['positions_m'];sides=data['node_sides'];pairs=data['pairs'];refs=data['reference_gaps_m']
    if not x or len(sides)!=len(x) or not pairs or len(refs)!=len(pairs):raise ValueError('Complete node/pair registry required')
    for v in x+refs:
        if len(v)!=3 or any(type(a) not in (int,float) or not math.isfinite(a) for a in v):raise ValueError('Finite SI vectors required')
    if len({tuple(pair) for pair in pairs})!=len(pairs):raise ValueError('Duplicate node pairs')
    for pair,rest in zip(pairs,refs):
        if len(pair)!=2 or any(type(i)is not int or not 0<=i<len(x) for i in pair):raise ValueError('Pair index invalid')
        a,b=pair
        if sides[a]!='slice' or sides[b]!='remainder':raise ValueError('Pair orientation must be slice to remainder')
        if any(rest[j]!=x[b][j]-x[a][j] for j in range(3)):raise ValueError('Reference gap differs from material coordinates')
    used=set();ids=set();budgets=[];asymmetries=[]
    for expected,p in enumerate(data['patches']):
        if p['id'] in ids or p['original_patch_index']!=expected:raise ValueError('Patch identity/order changed')
        ids.add(p['id']);indices=p['pair_indices'];w=p['weights'];k=p['stiffness_n_m'];law=CohesiveLaw(**p['law'])
        if not indices or len(indices)!=len(w) or len(set(indices))!=len(indices) or any(type(i)is not int or not 0<=i<len(pairs) for i in indices):raise ValueError('Patch quadrature indices invalid')
        if any(type(a) not in (int,float) or not math.isfinite(a) or a<=0 for a in w) or abs(math.fsum(w)-1)>1e-12:raise ValueError('Patch quadrature normalization changed')
        if len(k)!=3 or any(len(r)!=3 or any(type(a) not in (int,float) or not math.isfinite(a) for a in r) for r in k):raise ValueError('Finite patch stiffness required')
        asymmetry=max(abs(k[i][j]-k[j][i]) for i in range(3) for j in range(3));asymmetries.append(asymmetry)
        if asymmetry>1e-12 or any(k[0][j]!=0 for j in (1,2)):raise ValueError('Original symmetric decoupled normal frame required')
        if k[0][0]!=law.stiffness_n_m or k[1][1]<=0 or k[2][2]<=0 or k[1][1]*k[2][2]-k[1][2]**2<=0:raise ValueError('Patch stiffness/law mismatch or indefinite shear')
        if p['area_m2']!=law.area_m2 or p['fracture_budget_j']!=law.area_m2*law.fracture_energy_j_m2:raise ValueError('One area/fracture budget per patch required')
        budgets.append(p['fracture_budget_j']);used.update(indices)
    if not ids:raise ValueError('Nonempty patch registry required')
    return {'patch_count':len(ids),'pair_count':len(pairs),'quadrature_uncovered_pairs':len(pairs)-len(used),
        'maximum_stiffness_asymmetry_n_m':max(asymmetries),'strict_exact_symmetry_reference_adapter_compatible':all(a==0 for a in asymmetries),
        'total_patch_fracture_budget_j':math.fsum(budgets),'native_runtime_validated':False,
        'area_budget_must_not_be_multiplied_again':True,'native_spring_replacement_allowed':False}
