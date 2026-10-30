"""Source-grounded grid estimates and analytic-surface query diagnostics.

Grid spacing is not an SDF distance error bound. No SDF is cooked or queried here.
The source formula follows installed sdf_texture._create_texture_sdf_from_source.
"""
import math


def grid_estimate(vertices,*,padding_m,max_resolution):
    if not vertices or any(len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p) for p in vertices):raise ValueError('Finite nonempty 3D vertices required')
    if type(padding_m) not in (int,float) or not math.isfinite(padding_m) or padding_m<0:raise ValueError('Explicit nonnegative cooking padding required')
    if type(max_resolution)is not int or not 0<max_resolution<65536 or max_resolution%8:raise ValueError('Reviewed builder resolution must be positive multiple of eight below 65536')
    raw=[max(p[i] for p in vertices)-min(p[i] for p in vertices) for i in range(3)]
    ext=[x+2*padding_m for x in raw]
    if min(ext)<=0:raise ValueError('Positive 3D cooking extent required')
    scalar=max(ext)/max_resolution
    dims=[math.ceil(x/scalar)+1 for x in ext]
    cells=[x/(d-1) for x,d in zip(ext,dims)]
    return {'raw_extent_m':raw,'padded_extent_m':ext,'grid_dimensions':dims,
        'cell_size_m':cells,'dense_grid_points':math.prod(dims),
        'spacing_is_distance_error_bound':False,'sparse_memory_or_cooking_cost_measured':False,
        'native_sdf_validated':False}


def surface_probes(vertices,triangles):
    """All authored vertices, unique edge midpoints and triangle-interior centers.

    Each point lies on an authored facet; SDF zero-distance checks can therefore
    use exact reference zero. This does not test signed inside/outside samples,
    normals, self-intersection, collision generation or thin-edge preservation.
    """
    grid_estimate(vertices,padding_m=0.,max_resolution=8)
    probes=[{'id':f'vertex:{i}','kind':'vertex','point_m':list(p),'reference_distance_m':0.} for i,p in enumerate(vertices)]
    edges=set()
    for i,t in enumerate(triangles):
        if len(t)!=3 or len(set(t))!=3 or any(type(j)is not int or not 0<=j<len(vertices) for j in t):raise ValueError('Valid triangle indices required')
        p=[vertices[j] for j in t]
        ab=[p[1][k]-p[0][k] for k in range(3)];ac=[p[2][k]-p[0][k] for k in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        if math.hypot(*cross)<=0:raise ValueError('Degenerate facet')
        probes.append({'id':f'face:{i}','kind':'face_interior','point_m':[math.fsum(v[k] for v in p)/3 for k in range(3)],'reference_distance_m':0.})
        for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:edges.add(tuple(sorted((a,b))))
    for a,b in sorted(edges):probes.append({'id':f'edge:{a}:{b}','kind':'edge','point_m':[(vertices[a][k]+vertices[b][k])/2 for k in range(3)],'reference_distance_m':0.})
    return probes


def compare_surface_queries(probes,queries,*,distance_budget_m,budget_status):
    if budget_status not in ('draft','frozen') or type(distance_budget_m) not in (int,float) or not math.isfinite(distance_budget_m) or distance_budget_m<=0:raise ValueError('Explicit positive scoped distance budget and status required')
    expected={p['id'] for p in probes}
    if not expected or len(expected)!=len(probes) or set(queries)!=expected:raise ValueError('Every distinct probe must have exactly one query')
    errors=[]
    for p in probes:
        value=queries[p['id']]
        if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('Finite SDF samples required')
        errors.append(abs(value-p['reference_distance_m']))
    return {'maximum_surface_distance_error_m':max(errors),'surface_distance_within_budget':max(errors)<=distance_budget_m,
        'budget_status':budget_status,'qualification_enabled':False,
        'native_contact_completeness_proven':False,'native_sdf_validated':False}
