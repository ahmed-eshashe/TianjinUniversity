"""Concrete authored-blade facet fixtures, no changed blade geometry or runtime."""
import math
from tomato_native_coupon import validate_blade_export
from tomato_wrench_contract import cross,dot
from tomato_triangle_distance import sub,add,scale,point_mesh
from tomato_facet_distance import triangle_triangle


def facet_mesh_distance(facet,vertices,triangles):
    if not triangles or len(triangles)>1000:raise ValueError('Small authored mesh required for brute-force fixture oracle')
    best=None
    for i,t in enumerate(triangles):
        if len(t)!=3 or any(type(j)is not int or not 0<=j<len(vertices) for j in t):raise ValueError('Invalid blade triangle')
        r=triangle_triangle(facet,[vertices[j] for j in t])
        if best is None or r['distance_m']<best['distance_m']:best={**r,'blade_triangle_id':i}
    return best


def build_fixtures(blade,*,probe_halfspan_m):
    validate_blade_export(blade)
    if type(probe_halfspan_m) not in (int,float) or not math.isfinite(probe_halfspan_m) or probe_halfspan_m<=0:raise ValueError('Explicit positive diagnostic fixture span required')
    vertices=blade['vertices'];triangles=blade['triangles'];areas=[]
    for i,t in enumerate(triangles):
        a,b,c=[vertices[j] for j in t];areas.append((math.hypot(*cross(sub(b,a),sub(c,a))),i))
    area,i=max(areas)
    if area<=0:raise ValueError('Nondegenerate source facet required')
    a,b,c=[vertices[j] for j in triangles[i]];center=tuple(math.fsum(v[k] for v in (a,b,c))/3 for k in range(3))
    n=cross(sub(b,a),sub(c,a));n=scale(n,1/math.hypot(*n));t=sub(b,a);t=scale(t,1/math.hypot(*t));h=probe_halfspan_m
    positive=[add(center,scale(n,h)),sub(center,scale(n,h)),add(add(center,scale(t,h)),scale(n,h))]
    extent=max(p[0] for p in vertices)-min(p[0] for p in vertices)
    translation=(extent+.01+4*h,0.,0.);negative=[add(p,translation) for p in positive]
    out=[]
    for name,facet in [('edge_through_authored_blade_face',positive),('translated_clear_negative_control',negative)]:
        out.append({'id':name,'soft_diagnostic_facet_m':facet,
            'vertex_unsigned_clearances_m':[point_mesh(p,vertices,triangles)['distance_m'] for p in facet],
            'finite_facet_oracle':facet_mesh_distance(facet,vertices,triangles),
            'execution_enabled':False,'native_contact_validated':False})
    return {'frame':'blade_local','units':'m','blade_source_sha256':blade['source_sha256'],
        'selected_blade_triangle_id':i,'probe_halfspan_m':h,
        'fixture_span_is_acceptance_tolerance':False,'blade_geometry_modified':False,
        'cases':out,'runtime_collision_indices_and_filter_mapping_pending':True}
