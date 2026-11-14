"""Bounded host reference candidate search, NOT a full contact backend.

Surface intersections only seed a finite search. Negative winding-classified
distance and an unambiguous outward face projection are required for a record.
No global minimum, complete manifold, exact predicates, or dynamics guarantee.
"""
import math
from itertools import combinations
from tomato_triangle_distance import point_triangle, point_mesh, sub, add, scale
from tomato_sdf_native_probe import signed_reference
from tomato_mesh_contact_contract import review_record
from tomato_wrench_contract import cross, dot

NUMERIC_M = 1e-10  # Seed/projection arithmetic only; not physical contact slop.


def segment_face_witness(a, b, face):
    normal = cross(sub(face[1], face[0]), sub(face[2], face[0]))
    da, db = dot(sub(a, face[0]), normal), dot(sub(b, face[0]), normal)
    if da == db:
        return None  # Coplanar overlap is explicitly unsupported by this seed.
    t = da/(da-db)
    if not 0 <= t <= 1:
        return None
    p = add(a, scale(sub(b, a), t))
    projected = point_triangle(p, *face)
    return p if projected['distance_m'] <= NUMERIC_M else None


def generate_seeds(vertices, triangles, soft, *, witness_capacity=64, candidate_capacity=2048):
    if len(soft) != 3 or not 0 < len(triangles) <= 144:
        raise ValueError('Bounded triangle fixture and blade required')
    point_triangle(soft[0], *soft)  # Reject singular soft facet.
    witnesses = set()
    for tri in triangles:
        rigid = [vertices[i] for i in tri]
        for edges, face in ((soft, rigid), (rigid, soft)):
            for i,j in ((0,1),(1,2),(2,0)):
                p = segment_face_witness(edges[i], edges[j], face)
                if p is not None:
                    witnesses.add(tuple(p))
                    if len(witnesses) >= witness_capacity:
                        raise ValueError('Witness capacity saturated; no silent truncation')
    ordered = sorted(witnesses)
    seeds = {tuple(p) for p in soft}
    seeds.add(tuple(math.fsum(p[k] for p in soft)/3 for k in range(3)))
    if ordered:
        seeds.add(tuple(math.fsum(p[k] for p in ordered)/len(ordered) for k in range(3)))
    for a,b in combinations(ordered,2):
        seeds.add(tuple((x+y)/2 for x,y in zip(a,b)))
        if len(seeds) >= candidate_capacity:
            raise ValueError('Candidate capacity saturated; no silent truncation')
    return {'surface_witnesses': ordered, 'seeds': sorted(seeds)}


def search_reference_records(blade, soft):
    vertices, triangles = blade['vertices'], blade['triangles']
    seeds = generate_seeds(vertices, triangles, soft)
    identity={'rotation':[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],'translation_m':[0.,0.,0.]}
    context={'step':0,'dt_s':1/1200,'body_id':0,'shape_id':0,
        'particles_world_m':soft,'particle_radius_m':[0.,0.,0.],'shape_margin_m':0.,
        'rigid_vertices_shape_m':vertices,'rigid_triangles':triangles,
        'shape_to_body':identity,'body_to_world':identity}
    accepted=[]; exclusions={'off_facet':0,'surface_ambiguous':0,'outside':0,'non_face_normal':0}
    for seed in seeds['seeds']:
        soft_projection=point_triangle(seed,*soft)
        if soft_projection['distance_m'] > NUMERIC_M:
            exclusions['off_facet']+=1;continue
        weights=soft_projection['barycentric']
        # Use exactly the point represented by solver-support barycentric weights.
        p=tuple(math.fsum(w*q[k] for w,q in zip(weights,soft)) for k in range(3))
        closest=point_mesh(p,vertices,triangles)
        if closest['distance_m'] <= 1e-12:
            exclusions['surface_ambiguous']+=1;continue
        signed=signed_reference(p,vertices,triangles)
        if signed['reference_signed_distance_m'] >= 0:
            exclusions['outside']+=1;continue
        a,b,c=[vertices[i] for i in triangles[closest['triangle_id']]]
        normal=cross(sub(b,a),sub(c,a)); length=math.hypot(*normal);normal=tuple(v/length for v in normal)
        q=closest['closest_point_m'];gap=dot(normal,sub(p,q))
        tangent=sub(sub(p,q),scale(normal,gap))
        if gap >= 0 or math.hypot(*tangent)>1e-12 or math.dist(normal,signed['reference_normal'])>1e-8:
            exclusions['non_face_normal']+=1;continue
        record={'id':f'candidate:{len(accepted)}','source_kind':'signed_surface_reference',
            'normal_source':'outward_rigid_face_reference','step':0,'shape_id':0,'body_id':0,
            'feature':'face','corners':[0,1,2],'barycentric':list(weights),
            'rigid_triangle_id':closest['triangle_id'],'rigid_barycentric':list(closest['barycentric']),
            'rigid_surface_body_m':list(q),'normal_world':list(normal),
            'projected_signed_gap_m':gap,'rigid_surface_velocity_body_m_s':[0.,0.,0.]}
        review=review_record(record,context)
        if abs(gap-signed['reference_signed_distance_m'])>1e-12:
            raise ValueError('Projected gap and independently signed closest distance disagree')
        accepted.append({'record':record,'review':review,'winding_number':signed['winding_number']})
    accepted.sort(key=lambda row:row['review']['reference_penetration_m'],reverse=True)
    return {'witness_count':len(seeds['surface_witnesses']),'seed_count':len(seeds['seeds']),
        'accepted_count':len(accepted),'exclusions':exclusions,
        'deepest_sampled_candidate':accepted[0] if accepted else None,
        'all_accepted_candidates':accepted,'context':context,
        'global_minimum_or_manifold_validated':False,'native_contact_write_enabled':False}
