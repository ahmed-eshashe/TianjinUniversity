"""Offline convex boundary refinement to include fixed same-side bulk nodes."""
import copy
import itertools
import numpy as np
from scipy.spatial import ConvexHull
from tomato_surfaces import sub,cross,dot,norm


def conform_to_bulk(design,layout,refine_near_boundary=False):
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
        added=[]
        if refine_near_boundary:
            # A geometry-only trigger, independent of displacement, load or solver result.
            # Refine the faceted ellipsoid above material nodes within 2% of lattice spacing.
            exterior=p[np.asarray(piece['face_tags'])=='exterior']
            en=np.cross(exterior[:,1]-exterior[:,0],exterior[:,2]-exterior[:,0])
            en/=np.linalg.norm(en,axis=1)[:,None]
            distance=np.full(len(original),-np.inf)
            for offset in range(0,len(en),128):
                ns=en[offset:offset+128];anchors=exterior[offset:offset+128,0]
                distance=np.maximum(distance,(points@ns.T-np.einsum('ni,ni->n',ns,anchors)).max(axis=1))
            semiaxes=np.asarray(layout['dimensions_m'])/2;centre=np.array([0.,0.,semiaxes[2]])
            trigger=.02*layout['spacing_m'];surface=set(piece['surface_node_ids'])
            triggers=[]
            for idx,d in zip(original,distance):
                if idx in surface or d < -trigger:continue
                v=positions[idx]-centre;radius=np.linalg.norm(v/semiaxes)
                projected=centre+v/radius
                if (piece['side']=='slice' and projected[0]>=result['cut_x_m']-1e-12) or (piece['side']=='remainder' and projected[0]<=result['cut_x_m']+1e-12):
                    raise ValueError('Local exterior refinement would alter cut boundary')
                # Exact analytic-boundary originals are promoted by the existing hull path.
                if norm(sub(projected,positions[idx]))<1e-9:continue
                matches=np.flatnonzero(np.linalg.norm(positions-projected,axis=1)<1e-9)
                if len(matches):
                    if len(matches)==1 and nodes[int(matches[0])]['side']==piece['side']:
                        continue  # Already sampled by an earlier refinement pass.
                    raise ValueError('Ambiguous or opposite-side refinement coincidence')
                new_id=len(nodes);nodes.append({'id':new_id,'side':piece['side'],'position_m':projected.tolist(),
                                               'mass_kg':0.,'role':'local exterior refinement node'})
                positions=np.array([n['position_m'] for n in nodes])
                added.append(new_id);triggers.append(idx)
                # Same four-anchor, rank-tested tether rule as the base surface generator.
                # Do not create a near-zero, buckling-prone spring to the bulk
                # point directly beneath the new sample. Use resolved anchors.
                eligible=[i for i in original if norm(sub(nodes[i]['position_m'],projected))>=.25*layout['spacing_m']]
                closest=sorted(eligible,key=lambda i:norm(sub(nodes[i]['position_m'],projected)))[:12]
                if len(closest)<4:raise ValueError('Insufficient resolved refinement anchors')
                vectors={i:sub(nodes[i]['position_m'],projected) for i in closest}
                def quality(trio):
                    u,v,w=[vectors[i] for i in trio]
                    return abs(dot(u,cross(v,w)))/(norm(u)*norm(v)*norm(w))
                best=max(itertools.combinations(closest,3),key=quality)
                if quality(best)<.01:raise ValueError('Insufficient refinement tether rank')
                selected=list(best)+[i for i in closest if i not in best][:1]
                for other in selected:
                    result['bonds'].append({'id':len(result['bonds']),'nodes':[new_id,other],
                                            'rest_length_m':norm(vectors[other]),'kind':piece['side'],
                                            'role':'surface tether; stiffness unset'})
            record.update({'refinement_trigger_clearance_m':trigger,'refinement_trigger_original_ids':triggers,
                           'added_exterior_node_ids':added})
            if added:positions=np.array([n['position_m'] for n in nodes])
        if ids or added:
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
            record['bulk_nodes_promoted_to_boundary']=sorted(i for i in set(surface)-set(piece['surface_node_ids'])
                                                              if i<result['original_node_count'])
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
