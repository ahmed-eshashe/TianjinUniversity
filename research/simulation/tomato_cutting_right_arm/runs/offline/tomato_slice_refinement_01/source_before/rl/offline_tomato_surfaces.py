"""Bounded closed-surface geometry checks. No simulation or model import."""
import argparse
import fcntl
import hashlib
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def inspect_design(layout,design):
    from tomato_surfaces import (audit_piece,sub,cross,norm,segment_triangle_hit,
                                 vertex_face_eligible)
    from tomato_layout import components
    pieces=[audit_piece(design,p) for p in design['pieces']]
    nodes=design['nodes'];bonds=design['bonds'];cut=design['cut_x_m']
    coords=[];cut_faces=[]
    for piece in design['pieces']:
        triangles=[tri for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut']
        faces=[tuple(sorted(tuple(nodes[i]['position_m']) for i in tri)) for tri in triangles]
        coords.append(set(p for f in faces for p in f));cut_faces.append(set(faces))
    interface={b['id'] for b in bonds if b['kind']=='interface'}
    separated=components(design,interface)
    checks={'pieces_closed_oriented_convex':all(p['passed'] for p in pieces),
            'disjoint_piece_node_ids':not set(design['pieces'][0]['surface_node_ids'])&set(design['pieces'][1]['surface_node_ids']),
            'coincident_cut_coordinates':coords[0]==coords[1],
            'matching_cut_triangulations':cut_faces[0]==cut_faces[1],
            'no_zero_length_bonds':all(b['rest_length_m']>1e-9 for b in bonds),
            'original_bonds_unchanged':bonds[:len(layout['bonds'])]==layout['bonds'],
            'original_patch_registry_unchanged':design['interface_patches']==layout['interface_patches'],
            'no_new_cross_cut_bonds':interface=={b['id'] for b in layout['bonds'] if b['kind']=='interface'},
            'unique_bonds':len({tuple(sorted(b['nodes'])) for b in bonds})==len(bonds),
            'positive_mass':all(n['mass_kg']>0 for n in nodes),
            'mass_preserved':abs(sum(n['mass_kg'] for n in nodes)-sum(n['mass_kg'] for n in layout['nodes']))<1e-12,
            'per_piece_mass_preserved':all(abs(sum(n['mass_kg'] for n in nodes if n['side']==p['side'])-p['original_mass_kg'])<1e-12 for p in design['pieces']),
            'initial_single_component':len(components(design))==1,
            'exactly_two_sides_after_interface_removal':len(separated)==2 and all(len({nodes[i]['side'] for i in g})==1 for g in separated),
            'fixture_unchanged':design['fixture']==layout['fixture'],
            'no_rest_volume_overlap':all(n['position_m'][0]<=cut for n in nodes if n['side']=='slice') and all(n['position_m'][0]>=cut for n in nodes if n['side']=='remainder')}
    # Every cut triangle has an interior and edge sample tested against analytic segment intersection.
    misses=[];false_hits=0;sample_count=0
    for piece in design['pieces']:
        for tri,tag in zip(piece['triangles'],piece['face_tags']):
            if tag!='cut':continue
            points=[nodes[i]['position_m'] for i in tri]
            sample=[sum(p[j] for p in points)/3 for j in range(3)]
            edge=[(points[0][j]+points[1][j])/2 for j in range(3)]
            for p in (sample,edge,points[0]):
                start=(cut-.001,p[1],p[2]);end=(cut+.001,p[1],p[2])
                sample_count+=1
                if segment_triangle_hit(start,end,points) is None:misses.append(tri)
            if segment_triangle_hit((cut+.001,sample[1],sample[2]),(cut+.002,sample[1],sample[2]),points):false_hits+=1
    checks['triangle_centres_edges_vertices_detected']=not misses
    checks['noncrossing_segments_not_misclassified']=false_hits==0
    ax,ay,az=[v/2 for v in design['dimensions_m']]
    area=math.pi*ay*az*(1-(cut/ax)**2)
    polygon_area=area*math.sin(2*math.pi/design['angular_segments'])/(2*math.pi/design['angular_segments'])
    # Original interior nodes must remain inside the new polygonal solids.
    containment=[]
    for piece in design['pieces']:
        maximum=0.
        interior=[n['position_m'] for n in nodes[:design['original_node_count']] if n['side']==piece['side']]
        for tri in piece['triangles']:
            a,b,c=[nodes[i]['position_m'] for i in tri]
            n=cross(sub(b,a),sub(c,a));length=norm(n);nx,ny,nz=n;px,py,pz=a
            for x,y,z in interior:
                maximum=max(maximum,(nx*(x-px)+ny*(y-py)+nz*(z-pz))/length)
        containment.append(maximum)
    checks['original_nodes_inside_closed_surfaces']=all(v<1e-10 for v in containment)
    checks['unique_coordinates_per_piece']=all(len({tuple(nodes[i]['position_m']) for i in p['surface_node_ids']})==len(p['surface_node_ids']) for p in design['pieces'])
    checks['cut_area_tiles_polygon']=all(abs(p['cut_area_m2']/polygon_area-1)<1e-10 for p in pieces)
    cap=math.pi*ay*az*((cut-cut**3/(3*ax*ax))-(-ax+ax/3))
    analytic=[cap,4*math.pi*ax*ay*az/3-cap]
    volume_errors=[p['signed_volume_m3']/v-1 for p,v in zip(pieces,analytic)]
    checks['volume_error_below_one_percent']=all(abs(v)<.01 for v in volume_errors)
    # Near-plane face exclusion probes; an entire cross-piece class stays eligible.
    checks['cross_piece_has_no_shared_topological_vertices']=all(
        nodes[i]['side']==piece['side'] for piece in design['pieces'] for tri in piece['triangles'] for i in tri)
    cut_ids=[];cut_triangles=[]
    for piece in design['pieces']:
        tris=[t for t,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut']
        cut_triangles.append(tris);cut_ids.append({i for t in tris for i in t})
    pair_probes=0;excluded_cross_pairs=0
    for side in (0,1):
        for vertex in cut_ids[side]:
            for tri in cut_triangles[1-side]:
                pair_probes+=1
                excluded_cross_pairs+=not vertex_face_eligible(nodes,vertex,tri)
    checks['opposing_cut_vertex_face_pairs_never_excluded']=excluded_cross_pairs==0
    checks['own_incident_vertex_faces_excluded']=all(not vertex_face_eligible(nodes,i,tri) for piece in design['pieces'] for tri in piece['triangles'] for i in tri)
    rules={'status':'offline policy design, not a native filter implementation',
           'same_side_incident_vertex_face':'exclude only actual incident own-side topology',
           'cross_side_faces':'always contact eligible regardless of rest distance or intact interface bonds',
           'rest_shape_proximity_exclusion_radius_m':0.,'blanket_particle_radius_inflation':False,
           'shared_cut_face_positions_but_not_ids':True,
           'blade_piece_pairs':'both eligible at every damage state',
           'potential_cut_face_triangle_pairs':len(cut_faces[0])*len(cut_faces[1]),
           'tested_cross_piece_vertex_face_pairs':pair_probes,'excluded_cross_piece_pairs':excluded_cross_pairs,
           'native_contact_completeness_validated':False}
    return {'passed':all(checks.values()),'checks':checks,'piece_checks':pieces,
            'total_nodes':len(nodes),'total_bonds':len(bonds),'added_surface_nodes':len(nodes)-len(layout['nodes']),
            'added_same_side_bonds':len(bonds)-len(layout['bonds']),'component_sizes_after_cut':list(map(len,separated)),
            'matched_cut_vertices':len(coords[0]),'original_node_max_outside_distance_m':containment,'cut_area_relative_error_vs_analytic':pieces[0]['cut_area_m2']/area-1,
            'piece_volume_relative_errors':volume_errors,'analytic_crossing_samples':sample_count,'missed_crossings':len(misses),
            'collision_pair_policy':rules,'physical_contact_validated':False,
            'limitations':['rest geometry only; runtime surface crossing prevention not demonstrated',
                           'surface mass split 25 percent is provisional; inertia/continuum convergence not validated',
                           'surface tether and edge stiffness unset; added mechanics needs compression/shear checks',
                           'zero rest gap deliberately retained; native coincident-face handling untested']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    def timeout(signum,frame):raise TimeoutError('Offline geometry wall budget exceeded')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(55);started=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        from tomato_surfaces import build_surfaces
        source=ROOT/'runs/offline/tomato_layout_02/layout.json';layout=json.loads(source.read_text())
        design=build_surfaces(layout);result=inspect_design(layout,design)
        (args.output/'surface_design.json').write_text(json.dumps(design,indent=2)+'\n')
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Unexpected simulation imports')
        result.update({'runtime_s':time.monotonic()-started,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                       'limits':{'address_space_bytes':256*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True},
                       'layout_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                       'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'rl/tomato_surfaces.py']},
                       'simulator_imports_or_launches':False,'training':False})
        (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');signal.alarm(0)
        print(json.dumps(result,indent=2))
        if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
