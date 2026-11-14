"""Read-only geometry-to-adapter registry audit. Does not construct native assets.

Mass comes from the saved assignment registry; mesh and material side identities
are retained. Offline cohesive operators are not replaced with native springs.
"""
import math
from collections import Counter


def contact_allowed(side_a, side_b, *, adjacent_same_side=False):
    """Only true local same-side adjacency is excluded by this reference rule."""
    valid = {'slice', 'remainder', 'blade', 'board', 'fixture'}
    if side_a not in valid or side_b not in valid:
        raise ValueError('Unknown material/contact body')
    if adjacent_same_side:
        if side_a != side_b or side_a not in {'slice', 'remainder'}:
            raise ValueError('Cannot exclude cross-cut or external contact as adjacency')
        return False
    return True


def inspect_geometry(design, assignments):
    nodes, bonds = design['nodes'], design['bonds']
    if [n['id'] for n in nodes] != list(range(len(nodes))):
        raise ValueError('Native mapping requires explicit contiguous original node IDs')
    side = [n['side'] for n in nodes]
    if set(side) != {'slice', 'remainder'}:
        raise ValueError('Two distinct material identities required')
    def node_id(i):
        if type(i) is not int or not 0 <= i < len(nodes):
            raise ValueError('Invalid global node reference')
        return i
    for n in nodes:
        p = n['position_m']
        if len(p) != 3 or not all(math.isfinite(x) for x in p):
            raise ValueError('Invalid material coordinates')
    masses, bulk_bonds = {}, set()
    for a in assignments:
        ids, values = a['global_node_ids'], a['node_mass_kg']
        if len(ids) != len(values):
            raise ValueError('Mass mapping dimensions differ')
        for i, mass in zip(ids, values):
            node_id(i)
            if i in masses or not math.isfinite(mass) or mass <= 0:
                raise ValueError('Duplicate or invalid lumped mass')
            masses[i] = mass
        for b in a['bond_ids']:
            if type(b) is not int or not 0 <= b < len(bonds) or b in bulk_bonds:
                raise ValueError('Duplicate/invalid assigned bulk bond')
            bulk_bonds.add(b)
        for cell in a['integration_cells_global_ids']:
            if len({side[node_id(i)] for i in cell}) != 1:
                raise ValueError('Hidden cross-cut volume coupling')
    if set(masses) != set(range(len(nodes))):
        raise ValueError('Missing particle mass assignment')
    edges, interface = set(), set()
    min_rest = math.inf
    for i,b in enumerate(bonds):
        if b['id'] != i or len(b['nodes']) != 2:
            raise ValueError('Invalid bond identity')
        a,c = map(node_id,b['nodes']);edge=tuple(sorted((a,c)))
        length = b['rest_length_m']
        if a == c or edge in edges or not math.isfinite(length) or length <= 0:
            raise ValueError('Duplicate, collapsed or invalid spring')
        edges.add(edge);min_rest=min(min_rest,length)
        if side[a] != side[c]:
            interface.add(i)
            if b['kind'] != 'interface' or i in bulk_bonds:
                raise ValueError('Hidden bulk spring across cut')
        elif i not in bulk_bonds:
            raise ValueError('Unassigned same-side bulk spring')
    patch_bonds=[]
    for patch in design['interface_patches']:
        if not math.isfinite(patch['area_m2']) or patch['area_m2'] <= 0:
            raise ValueError('Invalid patch area')
        patch_bonds.extend(patch['bond_ids'])
    if len(patch_bonds) != len(set(patch_bonds)) or set(patch_bonds) != interface:
        raise ValueError('Interface patch registry incomplete or duplicated')
    surfaces=[]
    for piece in design['pieces']:
        if len(piece['triangles']) != len(piece['face_tags']):
            raise ValueError('Missing surface tags')
        for tri in piece['triangles']:
            if len(tri) != 3 or len(set(tri)) != 3 or any(side[node_id(i)] != piece['side'] for i in tri):
                raise ValueError('Invalid or cross-cut surface triangle')
        surfaces.append({'side':piece['side'],'triangles':len(piece['triangles']),
                         'tags':dict(Counter(piece['face_tags']))})
    for i in design['fixture']['node_ids']:
        if side[node_id(i)] != 'remainder':
            raise ValueError('Fixture constrains the slice')
    return {'nodes':len(nodes),'bonds':len(bonds),'bulk_bonds':len(bulk_bonds),
            'interface_bonds':len(interface),'patches':len(design['interface_patches']),
            'total_mass_kg':math.fsum(masses.values()),'minimum_rest_length_m':min_rest,
            'surface_registry':surfaces,'fixture_nodes':len(design['fixture']['node_ids']),
            'numerical_rest_gap_m':design['numerical_rest_gap_m'],
            'native_asset_created':False,'native_constitutive_equivalence':False,
            'unresolved':['native damage/energy equivalence','zero-gap cut-face contact and exclusion behavior',
                          'surface orientation/intersection and contact completeness at runtime']}
