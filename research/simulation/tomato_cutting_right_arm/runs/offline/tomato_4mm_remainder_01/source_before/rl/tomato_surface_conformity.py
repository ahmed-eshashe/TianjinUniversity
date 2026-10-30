"""Offline convex boundary refinement to include fixed same-side bulk nodes."""
import copy
import numpy as np
from scipy.spatial import ConvexHull
from tomato_surfaces import sub,cross,dot,norm


def conform_to_bulk(design,layout):
    """Preserve coordinates/cut registry; insert exposed bulk nodes into outer surface."""
    result=copy.deepcopy(design);nodes=result['nodes'];positions=np.array([n['position_m'] for n in nodes])
    records=[];changed=False
    for piece in result['pieces']:
        original=[n['id'] for n in nodes[:result['original_node_count']] if n['side']==piece['side']]
        triangles=np.asarray(piece['triangles']);p=positions[triangles]
        normals=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
        outside=np.zeros(len(original));points=positions[original]
        for offset in range(0,len(normals),128):
            ns=normals[offset:offset+128];anchors=p[offset:offset+128,0]
            distances=points@ns.T-np.einsum('ni,ni->n',ns,anchors)
            outside=np.maximum(outside,distances.max(axis=1))
        ids=[i for i,distance in zip(original,outside) if distance>1e-10]
        record={'side':piece['side'],'outside_original_ids_before':ids,
                'maximum_original_outside_m_before':float(outside.max()),'coordinates_moved':False}
        if ids:
            changed=True
            all_ids=[n['id'] for n in nodes if n['side']==piece['side']]
            hull=ConvexHull(positions[all_ids]/.005)
            exterior=[]
            for local in hull.simplices:
                tri=[all_ids[i] for i in local]
                if all(abs(nodes[i]['position_m'][0]-result['cut_x_m'])<1e-12 for i in tri):continue
                a,b,c=[nodes[i]['position_m'] for i in tri]
                if dot(cross(sub(b,a),sub(c,a)),sub(a,piece['reference_interior_m']))<0:tri=tri[::-1]
                exterior.append(tri)
            cap=[tri for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut']
            triangles=exterior+cap
            surface=sorted({i for tri in triangles for i in tri})
            if not set(piece['surface_node_ids'])<=set(surface):raise ValueError('Conformity lost an existing surface node')
            record['bulk_nodes_promoted_to_boundary']=sorted(set(surface)-set(piece['surface_node_ids']))
            piece['triangles']=triangles;piece['face_tags']=['exterior']*len(exterior)+['cut']*len(cap)
            piece['surface_node_ids']=surface
        else:record['bulk_nodes_promoted_to_boundary']=[]
        piece['boundary_conformity']=record;records.append(record)
    if changed:
        # Rebuild only newly proposed surface edges. Original bonds and patch IDs remain intact.
        bonds=[copy.deepcopy(b) for b in result['bonds'] if b.get('role')!='surface edge; stiffness unset']
        for i,b in enumerate(bonds):b['id']=i
        existing={tuple(sorted(b['nodes'])) for b in bonds}
        for piece in result['pieces']:
            edges={tuple(sorted((a,b))) for tri in piece['triangles'] for a,b in zip(tri,tri[1:]+tri[:1])}
            for a,b in sorted(edges-existing):
                length=norm(sub(nodes[a]['position_m'],nodes[b]['position_m']))
                if length<1e-9:raise ValueError('Zero-length conformity edge')
                bonds.append({'id':len(bonds),'nodes':[a,b],'rest_length_m':length,'kind':piece['side'],'role':'surface edge; stiffness unset'})
                existing.add((a,b))
        result['bonds']=bonds
        # Preserve accounting for the intermediate proposal; later analysis replaces it with volume lumping.
        for n in nodes:n['mass_kg']=layout['nodes'][n['id']]['mass_kg']*(1-result['surface_mass_fraction']) if n['id']<len(layout['nodes']) else 0.
        for piece in result['pieces']:
            weights={i:0. for i in piece['surface_node_ids']}
            for tri in piece['triangles']:
                a,b,c=[nodes[i]['position_m'] for i in tri];area=norm(cross(sub(b,a),sub(c,a)))/2
                for i in tri:weights[i]+=area/3
            total=sum(weights.values())
            for i,weight in weights.items():nodes[i]['mass_kg']+=piece['original_mass_kg']*result['surface_mass_fraction']*weight/total
    result['boundary_conformity_records']=records
    if len(result['nodes'])>7000 or len(result['bonds'])>50000:raise ValueError('Conforming geometry exceeds existing offline caps')
    return result
