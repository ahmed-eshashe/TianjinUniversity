"""Offline closed, cut-conforming contact-surface design. No simulator imports."""
import itertools
import math
from collections import defaultdict


def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):return math.sqrt(dot(a,a))


def vertex_face_eligible(nodes, vertex_id, triangle):
    """Offline exclusion policy only: cross-piece faces remain eligible at zero gap."""
    face_sides={nodes[i]['side'] for i in triangle}
    if len(face_sides)!=1:raise ValueError('Triangle bridges material sides')
    if nodes[vertex_id]['side'] not in face_sides:return True
    return vertex_id not in triangle


def build_surfaces(layout, angular_segments=64, max_meridian_step=math.pi/36, surface_mass_fraction=.25):
    """Closed clipped-ellipsoid meshes; 25% same-piece mass reassignment is provisional."""
    if angular_segments not in (32,64,128) or max_meridian_step not in (math.pi/36, math.pi/72):
        raise ValueError('Unbounded surface resolution')
    if not 0<surface_mass_fraction<1:raise ValueError('Invalid mass split')
    ax,ay,az=[v/2 for v in layout['dimensions_m']];cut=layout['cut_x_m']
    nodes=[dict(n,position_m=list(n['position_m'])) for n in layout['nodes']]
    original_count=len(nodes);bonds=[dict(b) for b in layout['bonds']]
    pieces=[]
    for side in ('slice','remainder'):
        first_surface=len(nodes);surface_ids=[];triangles=[];tags=[]
        original_ids=[n['id'] for n in nodes[:original_count] if n['side']==side]
        piece_mass=sum(nodes[i]['mass_kg'] for i in original_ids)
        interior_x=(-ax+cut)/2 if side=='slice' else (cut+ax)/2
        reference=(interior_x,0.,az)
        def vertex(pos):
            idx=len(nodes);nodes.append({'id':idx,'side':side,'position_m':list(pos),'mass_kg':0.,'role':'surface mechanical node'})
            surface_ids.append(idx);return idx
        def face(a,b,c,tag):
            p,q,r=[nodes[i]['position_m'] for i in (a,b,c)]
            if dot(cross(sub(q,p),sub(r,p)),sub(p,reference))<0:b,c=c,b
            triangles.append([a,b,c]);tags.append(tag)
        theta_cut=math.acos(cut/ax)
        theta_pole=math.pi if side=='slice' else 0.
        pole=vertex((-ax if side=='slice' else ax,0.,az))
        rings=[]
        count=math.ceil(abs(theta_cut-theta_pole)/max_meridian_step)
        for ring in range(1,count+1):
            theta=theta_pole+(theta_cut-theta_pole)*ring/count
            # Last ring lies exactly on the shared cut plane.
            x=cut if ring==count else ax*math.cos(theta)
            radial=math.sqrt(max(0.,1-(x/ax)**2))
            ids=[vertex((x,ay*radial*math.cos(2*math.pi*j/angular_segments),
                         az+az*radial*math.sin(2*math.pi*j/angular_segments))) for j in range(angular_segments)]
            if not rings:
                for j in range(angular_segments):face(pole,ids[j],ids[(j+1)%angular_segments],'exterior')
            else:
                old=rings[-1]
                for j in range(angular_segments):
                    k=(j+1)%angular_segments
                    face(old[j],old[k],ids[k],'exterior');face(old[j],ids[k],ids[j],'exterior')
            rings.append(ids)
        outer=rings[-1];radial=math.sqrt(1-(cut/ax)**2)
        for fraction in (.75,.5,.25):
            inner=[vertex((cut,ay*radial*fraction*math.cos(2*math.pi*j/angular_segments),
                           az+az*radial*fraction*math.sin(2*math.pi*j/angular_segments))) for j in range(angular_segments)]
            for j in range(angular_segments):
                k=(j+1)%angular_segments
                face(outer[j],outer[k],inner[k],'cut');face(outer[j],inner[k],inner[j],'cut')
            outer=inner
        centre=vertex((cut,0.,az))
        for j in range(angular_segments):face(outer[j],outer[(j+1)%angular_segments],centre,'cut')
        # Surface lump weights from represented triangle areas, explicitly not volume-calibrated.
        weights=defaultdict(float)
        for tri in triangles:
            p,q,r=[nodes[i]['position_m'] for i in tri];area=norm(cross(sub(q,p),sub(r,p)))/2
            for i in tri:weights[i]+=area/3
        total=sum(weights.values())
        for i in original_ids:nodes[i]['mass_kg']*=1-surface_mass_fraction
        for i in surface_ids:nodes[i]['mass_kg']=piece_mass*surface_mass_fraction*weights[i]/total
        # Finite, own-side tethers spanning three directions at each new node.
        worst_rank=1.
        for idx in surface_ids:
            pos=nodes[idx]['position_m']
            closest=sorted(original_ids,key=lambda i:dot(sub(nodes[i]['position_m'],pos),sub(nodes[i]['position_m'],pos)))[:12]
            vectors={i:sub(nodes[i]['position_m'],pos) for i in closest}
            best=None;quality=-1.
            for trio in itertools.combinations(closest,3):
                u,v,w=[vectors[i] for i in trio];denom=norm(u)*norm(v)*norm(w)
                score=abs(dot(u,cross(v,w)))/denom if denom>1e-27 else 0.
                if score>quality:best=trio;quality=score
            if quality<.01:raise ValueError('Insufficient tether directional rank')
            worst_rank=min(worst_rank,quality)
            selected=list(best)+[i for i in closest if i not in best][:1]
            for other in selected:
                length=norm(vectors[other])
                if length<1e-9:raise ValueError('Coincident material/tether node')
                bonds.append({'id':len(bonds),'nodes':[idx,other],'rest_length_m':length,'kind':side,'role':'surface tether; stiffness unset'})
        # Surface edges resist unresolved in-plane shape modes, never bridge the cut.
        edges={tuple(sorted((a,b))) for tri in triangles for a,b in zip(tri,tri[1:]+tri[:1])}
        for a,b in sorted(edges):
            length=norm(sub(nodes[a]['position_m'],nodes[b]['position_m']))
            if length<1e-9:raise ValueError('Degenerate surface edge')
            bonds.append({'id':len(bonds),'nodes':[a,b],'rest_length_m':length,'kind':side,'role':'surface edge; stiffness unset'})
        pieces.append({'side':side,'surface_node_ids':surface_ids,'triangles':triangles,'face_tags':tags,
                       'reference_interior_m':reference,'original_mass_kg':piece_mass,
                       'minimum_normalized_tether_determinant':worst_rank,'first_surface_node_id':first_surface})
    if len(nodes)>7000 or len(bonds)>50000:raise ValueError('Offline expanded geometry budget exceeded')
    return {'status':'offline surface and mechanical-topology proposal; no asset or dynamics',
            'nodes':nodes,'bonds':bonds,'pieces':pieces,'cut_x_m':cut,'dimensions_m':layout['dimensions_m'],
            'original_node_count':original_count,'original_bond_count':len(layout['bonds']),
            'interface_patches':layout['interface_patches'],'fixture':layout['fixture'],
            'surface_mass_fraction':surface_mass_fraction,'mass_lumping_calibrated':False,
            'angular_segments':angular_segments,'max_meridian_step_rad':max_meridian_step,
            'numerical_rest_gap_m':0.,'contact_pipeline_implemented':False}


def audit_piece(design,piece):
    nodes=design['nodes'];triangles=piece['triangles'];ids=piece['surface_node_ids']
    edge_uses=defaultdict(list);link_edges=defaultdict(list);areas=[];vol=0.;support_violation=0.;ref=piece['reference_interior_m']
    for tri,tag in zip(triangles,piece['face_tags']):
        a,b,c=tri;p,q,r=[nodes[i]['position_m'] for i in tri];normal=cross(sub(q,p),sub(r,p));length=norm(normal)
        areas.append(length/2);vol+=dot(sub(p,ref),cross(sub(q,ref),sub(r,ref)))/6
        for u,v in zip(tri,tri[1:]+tri[:1]):edge_uses[tuple(sorted((u,v)))].append((u,v))
        for v,u,w in ((a,b,c),(b,c,a),(c,a,b)):link_edges[v].append((u,w))
        if length>0:
            # Convex supporting-plane certificate also rules out nonlocal self crossings
            # for this constructed convex mesh, beyond merely counting manifold edges.
            nx,ny,nz=normal;px,py,pz=p
            for i in ids:
                x,y,z=nodes[i]['position_m']
                support_violation=max(support_violation,(nx*(x-px)+ny*(y-py)+nz*(z-pz))/length)
    link_ok=True
    for v,edges in link_edges.items():
        graph=defaultdict(set)
        for a,b in edges:graph[a].add(b);graph[b].add(a)
        seen=set();todo=[next(iter(graph))]
        while todo:
            k=todo.pop()
            if k in seen:continue
            seen.add(k);todo.extend(graph[k]-seen)
        link_ok &= len(seen)==len(graph) and all(len(n)==2 for n in graph.values())
    cut_tris=[tri for tri,tag in zip(triangles,piece['face_tags']) if tag=='cut']
    cut_area=sum(areas[i] for i,tag in enumerate(piece['face_tags']) if tag=='cut')
    direction=1. if piece['side']=='slice' else -1.
    cut_normals=all(cross(sub(nodes[t[1]]['position_m'],nodes[t[0]]['position_m']),
                          sub(nodes[t[2]]['position_m'],nodes[t[0]]['position_m']))[0]*direction>0 for t in cut_tris)
    checks={'two_opposite_uses_per_edge':all(len(v)==2 and v[0]==v[1][::-1] for v in edge_uses.values()),
            'vertex_links_single_cycles':link_ok,'euler_characteristic_two':len(ids)-len(edge_uses)+len(triangles)==2,
            'positive_triangle_areas':min(areas)>1e-14,'positive_oriented_volume':vol>0,
            'convex_support_plane_certificate':support_violation<1e-10,'outward_cut_normals':cut_normals,
            'side_identity':all(nodes[i]['side']==piece['side'] for tri in triangles for i in tri),
            'exact_cut_plane':all(nodes[i]['position_m'][0]==design['cut_x_m'] for t in cut_tris for i in t)}
    return {'passed':all(checks.values()),'checks':checks,'surface_nodes':len(ids),'triangles':len(triangles),
            'cut_triangles':len(cut_tris),'cut_area_m2':cut_area,'signed_volume_m3':vol,
            'maximum_support_plane_violation_m':support_violation,'minimum_triangle_area_m2':min(areas)}


def segment_triangle_hit(start,end,triangle,tolerance=1e-10):
    """Analytic segment/triangle crossing, including endpoint and edge hits; not CCD integration."""
    a,b,c=triangle;n=cross(sub(b,a),sub(c,a));denom=dot(n,sub(end,start))
    if abs(denom)<1e-18:return None
    t=dot(n,sub(a,start))/denom
    if not -tolerance<=t<=1+tolerance:return None
    point=tuple(x+t*(y-x) for x,y in zip(start,end))
    u=sub(b,a);v=sub(c,a);w=sub(point,a);uu=dot(u,u);uv=dot(u,v);vv=dot(v,v)
    det=uu*vv-uv*uv
    if det<=1e-28:return None
    beta=(dot(w,u)*vv-dot(w,v)*uv)/det;gamma=(dot(w,v)*uu-dot(w,u)*uv)/det
    if min(beta,gamma,1-beta-gamma)<-tolerance:return None
    return {'fraction':t,'barycentric':[1-beta-gamma,beta,gamma],'point_m':point}
