"""Offline slice graph refinement using its existing positive-volume cells."""
import copy
import itertools
import numpy as np
from tomato_surface_mechanics import volume_lumping


def refine_slice_cloud(design,layout):
    """Insert half-spacing lattice samples strictly inside the existing slice.

    Keep coarse material nodes and the exact boundary/cut mesh. Skip new points
    within 2% of coarse spacing of that boundary to avoid unresolved thin layers.
    """
    result=copy.deepcopy(design);piece=next(p for p in result['pieces'] if p['side']=='slice')
    nodes=result['nodes'];existing=np.asarray([n['position_m'] for n in nodes if n['side']=='slice'])
    semiaxes=np.asarray(layout['dimensions_m'])/2;centre=np.array([0.,0.,semiaxes[2]])
    h=layout['spacing_m'];step=h/2;origin=np.array([layout['cut_x_m']+h/2,0.,centre[2]])
    lower=centre-semiaxes;upper=centre+semiaxes;upper[0]=layout['cut_x_m']
    ranges=[range(int(np.floor((a-o)/step)),int(np.ceil((b-o)/step))+1) for a,b,o in zip(lower,upper,origin)]
    candidates=np.asarray([origin+step*np.asarray(index) for index in itertools.product(*ranges)])
    candidates=candidates[np.sum(((candidates-centre)/semiaxes)**2,axis=1)<1]
    positions=np.asarray([n['position_m'] for n in nodes]);face=positions[np.asarray(piece['triangles'])]
    normals=np.cross(face[:,1]-face[:,0],face[:,2]-face[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
    clearance=np.full(len(candidates),-np.inf)
    for offset in range(0,len(normals),128):
        ns=normals[offset:offset+128];anchors=face[offset:offset+128,0]
        clearance=np.maximum(clearance,(candidates@ns.T-np.einsum('ni,ni->n',ns,anchors)).max(axis=1))
    added=[]
    for position,distance in zip(candidates,clearance):
        if distance>-.02*h:continue
        if np.min(np.linalg.norm(existing-position,axis=1))<1e-10:continue
        idx=len(nodes);nodes.append({'id':idx,'position_m':position.tolist(),'side':'slice',
                                     'mass_kg':0.,'role':'half-spacing interior slice node'})
        added.append(idx)
    if len(nodes)>7000:raise ValueError('Slice refinement exceeds unchanged node budget')
    ids=[n['id'] for n in nodes if n['side']=='slice'];points=np.asarray([nodes[i]['position_m'] for i in ids])
    total_mass=sum(n['mass_kg'] for n in nodes if n['side']=='slice')
    _,_,lumps,_,_=volume_lumping(points)
    for idx,weight in zip(ids,lumps):nodes[idx]['mass_kg']=float(total_mass*weight/lumps.sum())
    result['slice_cloud_refinement']={'added_nodes':len(added),'interior_spacing_m':step,
                                     'minimum_new_boundary_clearance_m':.02*h,
                                     'existing_positions_changed':False,'new_constraints':False}
    return result


def add_slice_cell_edges(design):
    """Make every slice integration-cell edge mechanically connected, once only.

    Existing positions, original bonds, interface registry and material assignment
    rule are unchanged. New edges receive the existing positive isotropic recipe.
    This is a graph refinement, not tetrahedral FEM or an affine constraint.
    """
    result=copy.deepcopy(design)
    ids=[n['id'] for n in result['nodes'] if n['side']=='slice']
    points=np.asarray([result['nodes'][i]['position_m'] for i in ids])
    cells,*_=volume_lumping(points)
    edges={tuple(sorted((ids[a],ids[b]))) for cell in cells for a,b in itertools.combinations(cell,2)}
    existing={tuple(sorted(b['nodes'])) for b in result['bonds']}
    missing=sorted(edges-existing)
    if len(result['bonds'])+len(missing)>50000:raise ValueError('Slice cell edges exceed unchanged bond budget')
    for a,b in missing:
        length=float(np.linalg.norm(np.asarray(result['nodes'][a]['position_m'])-result['nodes'][b]['position_m']))
        if length<1e-9:raise ValueError('Unresolved slice cell edge')
        result['bonds'].append({'id':len(result['bonds']),'nodes':[a,b],'kind':'slice',
                                'rest_length_m':length,'role':'slice volume-cell edge; stiffness unset'})
    result['slice_cell_edge_refinement']={'added_edges':len(missing),'cell_edges':len(edges),
                                          'new_constraints':False,'material_coefficients_changed':False}
    return result
