"""Standard-library offline lattice layout, not a collision mesh or simulator asset."""
import itertools
import math


def components(layout, removed_bonds=()):
    removed = set(removed_bonds)
    adjacency = [[] for _ in layout['nodes']]
    for bond in layout['bonds']:
        if bond['id'] not in removed:
            a,b = bond['nodes']; adjacency[a].append(b); adjacency[b].append(a)
    seen = set(); groups = []
    for node in range(len(adjacency)):
        if node in seen:
            continue
        stack = [node]; seen.add(node); group = []
        while stack:
            a = stack.pop(); group.append(a)
            for b in adjacency[a]:
                if b not in seen:
                    seen.add(b); stack.append(b)
        groups.append(group)
    return groups


def build_layout(spacing_m=.005, dimensions_m=(.065,.065,.055), end_depth_m=.010,
                 density_kg_m3=1000., area_radial=32, area_angular=128):
    """Synthetic density is explicit in output. Interface patch areas use disk quadrature."""
    if len(dimensions_m) != 3 or any(not math.isfinite(v) or v <= 0 for v in (*dimensions_m,spacing_m,density_kg_m3)):
        raise ValueError('Invalid dimensions/density')
    if not math.isfinite(end_depth_m) or not 0 < end_depth_m < dimensions_m[0]:
        raise ValueError('Invalid cut depth')
    if any(v < .04 or v > .09 for v in dimensions_m):
        raise ValueError('Offline specimen restricted to 40–90 mm dimensions')
    if spacing_m < .004 or spacing_m > .006 or area_radial not in range(8,65) or area_angular not in range(32,257):
        raise ValueError('Offline layout restricted to coarse 4–6 mm and bounded quadrature')
    ax,ay,az = [v/2 for v in dimensions_m]; cut = -ax+end_depth_m
    # The cut is between x lattice layers; no coincident nodes or zero rest lengths.
    x_origin = cut+spacing_m/2
    indices = range(-math.ceil(max(dimensions_m)/spacing_m)*2, math.ceil(max(dimensions_m)/spacing_m)*2+1)
    nodes = []; grid = {}
    for i,j,k in itertools.product(indices,repeat=3):
        x=x_origin+i*spacing_m; y=j*spacing_m; z=az+k*spacing_m
        if (x/ax)**2+(y/ay)**2+((z-az)/az)**2 > 1+1e-12:
            continue
        # Boundary cell-volume fraction, then normalize to exact ellipsoid volume.
        inside=0
        for u,v,w in itertools.product((-.3333333333,0.,.3333333333),repeat=3):
            inside += ((x+u*spacing_m)/ax)**2+((y+v*spacing_m)/ay)**2+((z-az+w*spacing_m)/az)**2 <= 1
        node={'id':len(nodes),'grid':[i,j,k],'position_m':[x,y,z], 'side':'slice' if x<cut else 'remainder',
              'cell_weight_m3':spacing_m**3*inside/27}
        nodes.append(node); grid[(i,j,k)]=node['id']
    if not nodes or len(nodes)>2500:
        raise ValueError('Node budget or empty layout')
    volume=4*math.pi*ax*ay*az/3; weight=sum(n['cell_weight_m3'] for n in nodes)
    for n in nodes:
        n['represented_volume_m3']=volume*n.pop('cell_weight_m3')/weight
        n['mass_kg']=density_kg_m3*n['represented_volume_m3']
    bonds=[]; anchors=[]
    offsets=[v for v in itertools.product((-1,0,1),repeat=3) if v>(0,0,0)]
    for n in nodes:
        i,j,k=n['grid']
        for dx,dy,dz in offsets:
            other=grid.get((i+dx,j+dy,k+dz))
            if other is None:
                continue
            m=nodes[other]; cross=n['side']!=m['side']; a=n['position_m']; b=m['position_m']
            bond={'id':len(bonds),'nodes':[n['id'],other], 'rest_length_m':math.dist(a,b),
                  'kind':'interface' if cross else n['side'], 'offset':[dx,dy,dz]}
            if cross:
                t=(cut-a[0])/(b[0]-a[0]); bond['cut_point_yz_m']=[a[h]+t*(b[h]-a[h]) for h in (1,2)]
                if dy==0 and dz==0:
                    anchors.append(bond['cut_point_yz_m'])
            bonds.append(bond)
    if not anchors or len(bonds)>30000:
        raise ValueError('No interface anchors or bond budget exceeded')
    radius_factor=math.sqrt(1-(cut/ax)**2); ry=ay*radius_factor; rz=az*radius_factor
    patches=[{'id':i,'anchor_yz_m':p,'area_m2':0.,'bond_ids':[],
              'material':'effective_skin' if (p[0]/ry)**2+((p[1]-az)/rz)**2 > .65 else 'flesh'} for i,p in enumerate(anchors)]
    def nearest(y,z):
        return min(range(len(anchors)),key=lambda i:(anchors[i][0]-y)**2+(anchors[i][1]-z)**2)
    area=math.pi*ry*rz
    # Equal-area polar samples partition the full analytic cut ellipse by nearest anchor.
    for radial in range(area_radial):
        rho=math.sqrt((radial+.5)/area_radial)
        for angular in range(area_angular):
            theta=2*math.pi*(angular+.5)/area_angular
            patch=nearest(ry*rho*math.cos(theta),az+rz*rho*math.sin(theta))
            patches[patch]['area_m2']+=area/(area_radial*area_angular)
    for bond in bonds:
        if bond['kind']=='interface':
            bond['patch_id']=nearest(*bond['cut_point_yz_m']); patches[bond['patch_id']]['bond_ids'].append(bond['id'])
    cells=[]
    corners=list(itertools.product((0,1),repeat=3))
    for key in grid:
        ids=[grid.get(tuple(a+b for a,b in zip(key,corner))) for corner in corners]
        if all(v is not None for v in ids):
            cells.append({'nodes':ids,'reference_signed_volume_m3':spacing_m**3,
                          'straddles_cut':len({nodes[v]['side'] for v in ids})>1,
                          'role':'diagnostic only; no force or constraint'})
    fixture=[n['id'] for n in nodes if n['side']=='remainder' and n['position_m'][0]>ax-spacing_m*1.8 and n['position_m'][2]<az]
    if len(fixture)<3 or any(p['area_m2']<=0 or not p['bond_ids'] for p in patches):
        raise ValueError('Invalid fixture or interface patch')
    layout={'status':'offline topology only; no Newton asset or collision surface','dimensions_m':dimensions_m,'spacing_m':spacing_m,
            'cut_x_m':cut,'synthetic_density_kg_m3':density_kg_m3,'calibrated_material':False,
            'raw_boundary_volume_estimate_m3':weight,'analytic_volume_m3':volume,'analytic_cut_area_m2':area,'area_quadrature':[area_radial,area_angular],
            'nodes':nodes,'bonds':bonds,'interface_patches':patches,'diagnostic_cells':cells,
            'fixture':{'node_ids':fixture,'constraint':'proposed fixed xyz; not implemented','slice_nodes_constrained':False},
            'limitations':['voxel mass weights globally normalized; boundary convergence unvalidated',
                           'patch areas are approximate nearest-anchor Voronoi quadrature; total area is analytic',
                           'effective skin is a synthetic outer annulus, not measured skin thickness',
                           'no stiffness assigned, no collision faces, no contact or dynamics','interface registry is the only cross-cut force path proposed']}
    return layout


def audit_layout(layout):
    nodes=layout['nodes']; bonds=layout['bonds']; patches=layout['interface_patches']
    interface={b['id'] for b in bonds if b['kind']=='interface'}
    listed=[v for p in patches for v in p['bond_ids']]
    groups=components(layout,interface)
    fixture=layout['fixture']['node_ids']
    checks={'unique_pairs':len({tuple(sorted(b['nodes'])) for b in bonds})==len(bonds),
            'positive_mass_and_length':all(n['mass_kg']>0 for n in nodes) and all(b['rest_length_m']>1e-9 for b in bonds),
            'registered_once':set(listed)==interface and len(listed)==len(interface),
            'cut_classification':all((nodes[b['nodes'][0]]['side']!=nodes[b['nodes'][1]]['side'])==(b['kind']=='interface') for b in bonds),
            'area_partition':abs(sum(p['area_m2'] for p in patches)/layout['analytic_cut_area_m2']-1)<1e-10,
            'mass_accounting':abs(sum(n['mass_kg'] for n in nodes)/(layout['analytic_volume_m3']*layout['synthetic_density_kg_m3'])-1)<1e-10,
            'initial_connected':len(components(layout))==1,
            'two_connected_sides_after_complete_removal':len(groups)==2 and all(len({nodes[i]['side'] for i in g})==1 for g in groups),
            'fixture_remainder_only':len(fixture)>=3 and all(nodes[i]['side']=='remainder' for i in fixture),
            'budgets':len(nodes)<=2500 and len(bonds)<30000}
    return {'passed':all(checks.values()),'checks':checks,'nodes':len(nodes),'bonds':len(bonds),
            'interface_bonds':len(interface),'patches':len(patches),'fixture_nodes':len(fixture),
            'diagnostic_cells':len(layout['diagnostic_cells']), 'removed_graph_component_sizes':list(map(len,groups)),
            'physical_separation_tested':False}
