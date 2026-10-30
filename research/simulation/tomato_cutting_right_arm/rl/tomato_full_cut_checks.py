"""Offline full-cut qualification checks, independent of the endpoint solver."""
import math


def material_components(design, assignments, patch_indices, damage, pairs):
    """Material connectivity includes bulk springs AND volume-cell couplings.

    Unilateral face contact is intentionally not a material bond.
    """
    if len(patch_indices)!=len(damage) or any(not math.isfinite(d) or not 0<=d<=1 for d in damage):
        raise ValueError('Invalid patch registry or damage')
    parent=list(range(len(design['nodes'])))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):parent[find(a)]=find(b)
    cross_bulk=0
    for assignment in assignments:
        for i in assignment['bond_ids']:
            a,b=design['bonds'][i]['nodes'];union(a,b)
            cross_bulk+=design['nodes'][a]['side']!=design['nodes'][b]['side']
        for cell in assignment['integration_cells_global_ids']:
            for v in cell[1:]:union(cell[0],v)
            cross_bulk+=len({design['nodes'][i]['side'] for i in cell})>1
    for ids,d in zip(patch_indices,damage):
        if d<1.:
            for i in ids:union(*pairs[i])
    groups={}
    for i,n in enumerate(design['nodes']):groups.setdefault(find(i),set()).add(n['side'])
    return {'components':len(groups),'cross_bulk_couplings':cross_bulk,
            'components_spanning_both_pieces':sum(len(g)>1 for g in groups.values()),
            'active_cohesive_patches':sum(d<1. for d in damage),
            'all_patches_failed':all(d==1. for d in damage),
            'materially_disconnected':len(groups)==2 and all(len(g)==1 for g in groups.values())}


def cap_contact_witness(z_values, tip, slope, cap):
    """One triangle witness where nodal contact misses finite facet penetration.

    Set every vertex exactly on the capped bevel. At a triangle-edge crossing
    of the bevel-cap plane, barycentric interpolation underestimates the cap.
    This is a synthetic feasible nodal configuration, not an observed state.
    """
    if not all(math.isfinite(x) for x in (*z_values,tip,slope,cap)) or slope<=0 or cap<=0:
        raise ValueError('Invalid wedge inputs')
    widths=[min(max(slope*(z-tip),0.),cap) for z in z_values]
    crest=tip+cap/slope;worst=0.
    for i,j in [(0,1),(1,2),(2,0)]:
        a,b=z_values[i],z_values[j]
        if min(a,b)<crest<max(a,b):
            t=(crest-a)/(b-a);linear=(1-t)*widths[i]+t*widths[j]
            worst=max(worst,(cap-linear)/2)
    return worst


def separation_status(topology, *, blade_absent, minimum_gap_m, relative_translation_verified, no_healing):
    """Never accept blade depth or material damage alone as slice separation."""
    return bool(topology['materially_disconnected'] and topology['all_patches_failed']
                and blade_absent and minimum_gap_m>1e-4
                and relative_translation_verified and no_healing)
