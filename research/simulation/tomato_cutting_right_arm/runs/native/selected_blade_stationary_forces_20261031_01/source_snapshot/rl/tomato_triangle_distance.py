"""Independent brute-force unsigned point/authored-triangle distance oracle.

No SDF, optimization helper, native engine, inside/outside sign or collision
acceptance. Point queries cannot establish triangle-interior contact completeness.
"""
import math
from tomato_wrench_contract import vector,dot,cross


def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,s):return tuple(x*s for x in a)


def closest_segment(point,a,b):
    edge=sub(b,a);denom=dot(edge,edge)
    if denom<=0:raise ValueError('Zero-length edge')
    t=min(1.,max(0.,dot(sub(point,a),edge)/denom))
    return add(a,scale(edge,t)),t


def point_triangle(point,a,b,c):
    point,a,b,c=[vector(v) for v in (point,a,b,c)]
    ab,ac=sub(b,a),sub(c,a);normal=cross(ab,ac);nn=dot(normal,normal)
    if nn<=0 or not math.isfinite(nn):raise ValueError('Degenerate or overflowing triangle')
    projected=sub(point,scale(normal,dot(sub(point,a),normal)/nn))
    v0,v1,v2=ab,ac,sub(projected,a)
    d00,d01,d11,d20,d21=dot(v0,v0),dot(v0,v1),dot(v1,v1),dot(v2,v0),dot(v2,v1)
    denom=d00*d11-d01*d01
    if denom<=0 or not math.isfinite(denom):raise ValueError('Numerically singular triangle; no silent clamp')
    v=(d11*d20-d01*d21)/denom;w=(d00*d21-d01*d20)/denom;u=1-v-w
    candidates=[]
    if min(u,v,w)>=0:candidates.append((projected,(u,v,w),'face_or_boundary'))
    for x,y,indices in [(a,b,(0,1)),(b,c,(1,2)),(c,a,(2,0))]:
        q,t=closest_segment(point,x,y);bary=[0.,0.,0.];bary[indices[0]]=1-t;bary[indices[1]]=t
        candidates.append((q,tuple(bary),'edge_or_vertex'))
    q,bary,feature=min(candidates,key=lambda item:dot(sub(point,item[0]),sub(point,item[0])))
    distance=math.hypot(*sub(point,q))
    if not math.isfinite(distance):raise ValueError('Nonfinite geometric distance')
    return {'distance_m':distance,'closest_point_m':q,'barycentric':bary,'feature':feature}


def point_mesh(point,vertices,triangles):
    if not triangles or len(triangles)>10000:raise ValueError('Bounded nonempty authored triangle list required')
    best=None
    for i,tri in enumerate(triangles):
        if len(tri)!=3 or len(set(tri))!=3 or any(type(j)is not int or not 0<=j<len(vertices) for j in tri):raise ValueError('Invalid triangle registry')
        r=point_triangle(point,*(vertices[j] for j in tri))
        if best is None or r['distance_m']<best['distance_m']:best={**r,'triangle_id':i}
    return {**best,'distance_kind':'unsigned_authored_surface','native_contact_validated':False,
            'inside_outside_classification_supplied':False,'normal_accuracy_validated':False}
