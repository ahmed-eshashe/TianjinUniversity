"""Offline mesh topology and prescribed coupon motion; no native execution.

Initial AABB clearance is a geometric certificate only. Later AABB overlap
does not demonstrate contact, nonpenetration, damage or a successful cut.
"""
import math
from collections import Counter
from tomato_wrench_contract import cross, dot, vector, rotation

R=((0.,0.,1.),(1.,0.,0.),(0.,1.,0.))


def audit_closed_surface(vertices, triangles):
    points=[vector(p) for p in vertices]
    if not points or not triangles:
        raise ValueError('Empty surface')
    edges=Counter();directions=Counter();seen=set();areas=[];volumes=[]
    for tri in triangles:
        if len(tri)!=3 or len(set(tri))!=3 or any(type(i)is not int or not 0<=i<len(points) for i in tri):
            raise ValueError('Invalid surface triangle')
        key=tuple(sorted(tri))
        if key in seen:raise ValueError('Duplicate triangle')
        seen.add(key)
        a,b,c=[points[i] for i in tri]
        ab=tuple(y-x for x,y in zip(a,b));ac=tuple(y-x for x,y in zip(a,c))
        area=.5*math.hypot(*cross(ab,ac))
        if not math.isfinite(area) or area<=0:raise ValueError('Degenerate triangle')
        areas.append(area);volumes.append(dot(a,cross(b,c))/6)
        for i,j in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
            e=tuple(sorted((i,j)));edges[e]+=1;directions[e]+=1 if i<j else -1
    if any(n!=2 for n in edges.values()) or any(d!=0 for d in directions.values()):
        raise ValueError('Nonmanifold, open or inconsistently wound surface')
    volume=math.fsum(volumes)
    if not math.isfinite(volume) or volume<=0:raise ValueError('Nonpositive oriented volume')
    return {'vertices':len(points),'triangles':len(triangles),'edges':len(edges),
            'signed_volume_m3':volume,'minimum_triangle_area_m2':min(areas),
            'closed_oriented_manifold':True,'self_intersection_tested':False,
            'native_sdf_validated':False}


def trajectory_config(blade_vertices, coupon_positions):
    rotation(R)
    points=[tuple(dot(row,vector(p)) for row in R) for p in blade_vertices]
    coupon=[vector(p) for p in coupon_positions]
    if not points or not coupon:raise ValueError('Nonempty geometry required')
    lo=[min(p[i] for p in points) for i in range(3)]
    hi=[max(p[i] for p in points) for i in range(3)]
    top=max(p[2] for p in coupon)
    centre=[math.fsum(p[i] for p in coupon)/len(coupon) for i in range(2)]
    xy=[centre[i]-(lo[i]+hi[i])/2 for i in range(2)]
    clear,indent=.002,.00025
    return {'rotation':R,'start_translation_m':xy+[top+clear-lo[2]],
            'end_translation_m':xy+[top-indent-lo[2]],'initial_clearance_m':clear,
            'maximum_prescribed_bounds_overlap_m':indent,'dt_s':1/1200,
            'stages':[['rest',.05],['indent',.5],['hold',.1],['withdraw',.5],['clear_hold',.05]],
            'profile':'cubic_smoothstep_zero_boundary_velocity',
            'cutting_success':False,'native_contact_validated':False}


def pose_at(config, time_s):
    t=float(time_s)
    stages=config['stages'];total=math.fsum(d for _,d in stages)
    if not math.isfinite(t) or not 0<=t<=total:raise ValueError('Time outside prescribed experiment')
    cursor=0.
    for index,(stage,duration) in enumerate(stages):
        if t<=cursor+duration or index==len(stages)-1:break
        cursor+=duration
    start=vector(config['start_translation_m']);end=vector(config['end_translation_m'])
    if stage in {'rest','clear_hold'}:p=start;v=(0.,0.,0.)
    elif stage=='hold':p=end;v=(0.,0.,0.)
    else:
        u=min(1.,max(0.,(t-cursor)/duration));s=u*u*(3-2*u);rate=6*u*(1-u)/duration
        a,b=(start,end) if stage=='indent' else (end,start)
        p=tuple(x+s*(y-x) for x,y in zip(a,b));v=tuple(rate*(y-x) for x,y in zip(a,b))
    return {'stage':stage,'translation_m':p,'rotation':config['rotation'],
            'linear_velocity_m_s':v,'angular_velocity_rad_s':(0.,0.,0.)}
