"""Read-only, finite-fixture closest-surface and sampled-minimum ambiguity audit."""
import math
from tomato_triangle_distance import point_triangle, sub
from tomato_wrench_contract import cross, dot

BANDS_M=(1e-12,1e-9,1e-7)  # Reporting sensitivity bands, not physical tolerances.


def audit_point(point, vertices, triangles):
    if not 0 < len(triangles) <= 144:
        raise ValueError('Bounded nonempty facet list required')
    rows=[]
    for index,triangle in enumerate(triangles):
        a,b,c=[vertices[j] for j in triangle]
        result=point_triangle(point,a,b,c)
        normal=cross(sub(b,a),sub(c,a));size=math.hypot(*normal)
        if not size > 0:raise ValueError('Degenerate facet')
        rows.append({'triangle_id':index,'distance_m':result['distance_m'],
                     'closest_point_m':result['closest_point_m'],'face_normal':[v/size for v in normal]})
    rows.sort(key=lambda row:(row['distance_m'],row['triangle_id']))
    nearest=rows[0]
    different=[r for r in rows if dot(r['face_normal'],nearest['face_normal']) < 1.-1e-6]
    opposite=[r for r in different if dot(r['face_normal'],nearest['face_normal']) < 0.]
    def gap(branch):return branch[0]['distance_m']-nearest['distance_m'] if branch else None
    return {'point_m':list(point),'nearest':nearest,
        'nearest_different_normal_facet':different[0] if different else None,
        'different_normal_distance_gap_m':gap(different),
        'nearest_opposing_normal_facet':opposite[0] if opposite else None,
        'opposing_normal_distance_gap_m':gap(opposite),
        'bands':[{'band_m':band,
            'nearby_facet_count':sum(r['distance_m']-nearest['distance_m']<=band for r in rows),
            'different_normal_branch_present':any(r['distance_m']-nearest['distance_m']<=band for r in different)}
            for band in BANDS_M],
        'normal_grouping_scope':'dot < 1-1e-6 labels different face directions for reporting only; not a force/manifold rule.'}


def audit_sampled_minimum(rows):
    if not rows:return {'sample_count':0,'bands':[]}
    if len(rows)>=2048:raise ValueError('Sample capacity saturated')
    best=max(row['reference_penetration_m'] for row in rows)
    if not math.isfinite(best):raise ValueError('Finite depths required')
    bands=[]
    for band in BANDS_M:
        near=[row for row in rows if best-row['reference_penetration_m']<=band]
        if any(not math.isfinite(row['reference_penetration_m']) for row in rows):
            raise ValueError('Finite depths required')
        minimum_dot=min(dot(a['normal_world'],b['normal_world']) for a in near for b in near)
        spread=max(math.dist(a['soft_point_world_m'],b['soft_point_world_m']) for a in near for b in near)
        bands.append({'depth_band_m':band,'near_best_sample_count':len(near),
                      'maximum_location_spread_m':spread,'minimum_normal_dot':minimum_dot})
    return {'sample_count':len(rows),'deepest_sampled_penetration_m':best,'bands':bands,
            'global_minimum_certified':False}
