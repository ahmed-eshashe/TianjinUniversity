"""Independent floating-point finite-feature distance/intersection witnesses.

No exact-arithmetic predicates, penetration depth, signed volume, SDF or native
contact acceptance. Near-degenerate configurations require further robustness
review. This detects noncoplanar edge-through-face cases missed by vertex tests.
"""
import math
from tomato_triangle_distance import point_triangle,closest_segment,sub,add,scale
from tomato_wrench_contract import vector,dot,cross


def segment_segment(a,b,c,d):
    a,b,c,d=[vector(p) for p in (a,b,c,d)]
    u,v=sub(b,a),sub(d,c);aa,cc=dot(u,u),dot(v,v)
    if min(aa,cc)<=0:raise ValueError('Nonzero segments required')
    candidates=[]
    for p in (a,b):
        q,_=closest_segment(p,c,d);candidates.append((p,q))
    for q in (c,d):
        p,_=closest_segment(q,a,b);candidates.append((p,q))
    normal=cross(u,v);det=dot(normal,normal)
    if det>0:
        w=sub(a,c);bb,dd,ee=dot(u,v),dot(u,w),dot(v,w)
        s=(bb*ee-cc*dd)/det;t=(aa*ee-bb*dd)/det
        if 0<=s<=1 and 0<=t<=1:candidates.append((add(a,scale(u,s)),add(c,scale(v,t))))
    p,q=min(candidates,key=lambda pair:math.hypot(*sub(*pair)))
    return {'distance_m':math.hypot(*sub(p,q)),'segment_point_m':p,'other_segment_point_m':q}


def segment_triangle(a,b,triangle):
    if len(triangle)!=3:raise ValueError('Triangle required')
    a,b=[vector(p) for p in (a,b)];p,q,r=[vector(v) for v in triangle]
    endpoint_a=point_triangle(a,p,q,r);endpoint_b=point_triangle(b,p,q,r)
    candidates=[{'distance_m':endpoint_a['distance_m'],'segment_point_m':a,'triangle_point_m':endpoint_a['closest_point_m'],'feature':'endpoint'},
                {'distance_m':endpoint_b['distance_m'],'segment_point_m':b,'triangle_point_m':endpoint_b['closest_point_m'],'feature':'endpoint'}]
    for x,y in ((p,q),(q,r),(r,p)):
        edge=segment_segment(a,b,x,y);candidates.append({'distance_m':edge['distance_m'],'segment_point_m':edge['segment_point_m'],'triangle_point_m':edge['other_segment_point_m'],'feature':'edge_edge'})
    n=cross(sub(q,p),sub(r,p));da,db=dot(sub(a,p),n),dot(sub(b,p),n)
    if da!=db:
        t=da/(da-db)
        if 0<=t<=1:
            x=add(a,scale(sub(b,a),t));projection=point_triangle(x,p,q,r)
            if projection['feature']=='face_or_boundary':
                candidates.append({'distance_m':projection['distance_m'],'segment_point_m':x,'triangle_point_m':projection['closest_point_m'],'feature':'edge_through_face'})
    result=min(candidates,key=lambda c:c['distance_m'])
    return {**result,'native_contact_validated':False,'exact_predicates_used':False}


def triangle_triangle(first,second):
    if len(first)!=3 or len(second)!=3:raise ValueError('Two finite triangles required')
    # Validate both even if an early edge yields a zero-distance witness.
    point_triangle(first[0],*first);point_triangle(second[0],*second)
    candidates=[]
    for side,(edges,face) in enumerate(((first,second),(second,first))):
        for i,j in ((0,1),(1,2),(2,0)):
            r=segment_triangle(edges[i],edges[j],face);candidates.append({**r,'edge_owner':side,'edge_vertices':[i,j]})
    return {**min(candidates,key=lambda c:c['distance_m']),'distance_kind':'unsigned_finite_facet_distance',
            'penetration_depth_supplied':False,'contact_force_or_normal_validated':False}
