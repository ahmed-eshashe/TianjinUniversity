"""Offline volume lumping and small-strain spring checks, not a simulation backend."""
import math
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu


def closed_volume_moments(design,piece):
    """Independent boundary-fan integration to check the interior tessellation."""
    points=np.array([n['position_m'] for n in design['nodes']])
    face=points[np.asarray(piece['triangles'])]
    ref=np.asarray(piece['reference_interior_m'])
    volumes=np.einsum('ni,ni->n',face[:,0]-ref,np.cross(face[:,1]-ref,face[:,2]-ref))/6
    if np.any(volumes<=0):raise ValueError('Boundary fan needs outward convex faces')
    vertices=np.concatenate([np.broadcast_to(ref,(len(face),1,3)),face],axis=1)
    sums=vertices.sum(axis=1)
    return float(volumes.sum()),(volumes[:,None]*sums/4).sum(axis=0)


def volume_lumping(points):
    """Tetrahedra are integration cells only; no FEM forces are added."""
    points=np.asarray(points,dtype=float)
    cells=Delaunay(points/.005).simplices
    p=points[cells]
    signed=np.linalg.det(p[:,1:]-p[:,:1])/6
    keep=np.abs(signed)>1e-20
    cells=cells[keep];signed=signed[keep]
    backwards=signed<0
    cells[backwards,0],cells[backwards,1]=cells[backwards,1].copy(),cells[backwards,0].copy()
    volumes=np.abs(signed);lumps=np.zeros(len(points))
    np.add.at(lumps,cells.reshape(-1),np.repeat(volumes/4,4))
    if np.any(lumps<=0):raise ValueError('Volume tessellation left massless nodes')
    p=points[cells];s=p.sum(axis=1)
    first=(volumes[:,None]*s/4).sum(axis=0)
    second=(volumes[:,None,None]*(np.einsum('nki,nkj->nij',p,p)+s[:,:,None]*s[:,None,:])/20).sum(axis=0)
    return cells,volumes,lumps,first,second


def isotropic_orientation_weights(directions, base):
    """Positive minimum-relative-entropy correction to isotropic fourth moments."""
    n=np.asarray(directions);base=np.asarray(base)
    powers=[(a,b,4-a-b) for a in range(5) for b in range(5-a)]
    basis=np.array([np.prod(n**np.array(p),axis=1) for p in powers])
    target=np.array([.2 if 4 in p else (1/15 if sorted(p)==[0,2,2] else 0.) for p in powers])
    lam=np.zeros(15)
    for iteration in range(40):
        weights=base*np.exp(basis.T@lam)
        grad=basis@weights-target
        if np.max(np.abs(grad))<1e-11:break
        hessian=(basis*weights)@basis.T
        direction=np.linalg.solve(hessian+np.eye(15)*1e-14,-grad)
        step=1.
        while step>1e-7:
            candidate=lam+step*direction;exponent=basis.T@candidate
            if np.max(np.abs(exponent))<60:
                # Exact objective difference, without subtracting two O(1) values
                # near convergence. The old subtraction could falsely reject descent.
                shift=step*(basis.T@direction)
                change=weights@(np.expm1(shift)-shift)+step*(grad@direction)
                if change<=1e-4*step*(grad@direction):break
            step*=.5
        if step<=1e-7:raise ValueError('Orientation correction failed descent')
        lam=candidate
    else:raise ValueError('Orientation correction failed convergence')
    residual=float(np.max(np.abs(basis@weights-target)))
    if residual>1e-9 or np.any(weights<=0):raise ValueError('Invalid orientation weights')
    return weights,{'iterations':iteration,'max_fourth_moment_residual':residual,
                    'min_multiplier':float(np.min(weights/base)),'max_multiplier':float(np.max(weights/base))}


def stiffness_matrix(points,pairs,stiffness):
    points=np.asarray(points);pairs=np.asarray(pairs);k=np.asarray(stiffness)
    if np.any(k<=0) or not np.isfinite(k).all():raise ValueError('Nonpositive/nonfinite spring stiffness')
    delta=points[pairs[:,1]]-points[pairs[:,0]];length=np.linalg.norm(delta,axis=1)
    if np.any(length<1e-9):raise ValueError('Zero spring length')
    n=delta/length[:,None];ii,jj=np.meshgrid(np.arange(3),np.arange(3),indexing='ij')
    block=(k[:,None,None]*n[:,:,None]*n[:,None,:]).reshape(-1,9)
    a=3*pairs[:,0,None]+ii.reshape(1,9);b=3*pairs[:,1,None]+ii.reshape(1,9)
    c=3*pairs[:,0,None]+jj.reshape(1,9);d=3*pairs[:,1,None]+jj.reshape(1,9)
    rows=np.concatenate([a,a,b,b]).reshape(-1);cols=np.concatenate([c,d,c,d]).reshape(-1)
    data=np.concatenate([block,-block,-block,block]).reshape(-1)
    result=coo_matrix((data,(rows,cols)),shape=(3*len(points),3*len(points))).tocsr()
    result.eliminate_zeros()
    return result


def finite_spring_energy(points,displacements,pairs,stiffness):
    p=np.asarray(points);u=np.asarray(displacements);ids=np.asarray(pairs)
    initial=np.linalg.norm(p[ids[:,1]]-p[ids[:,0]],axis=1)
    current=np.linalg.norm((p+u)[ids[:,1]]-(p+u)[ids[:,0]],axis=1)
    return float(.5*np.dot(stiffness,(current-initial)**2))


def analyse_piece(design,piece,young_pa=30000.,density_mass=None):
    """Synthetic nu=0.25 central-force material, all surface DOFs prescribed in probes."""
    side=piece['side'];global_ids=[n['id'] for n in design['nodes'] if n['side']==side]
    mapping={i:j for j,i in enumerate(global_ids)}
    points=np.array([design['nodes'][i]['position_m'] for i in global_ids])
    cells,volumes,lumps,first,second=volume_lumping(points);volume=volumes.sum()
    boundary_volume,boundary_first=closed_volume_moments(design,piece)
    mass=sum(design['nodes'][i]['mass_kg'] for i in global_ids) if density_mass is None else density_mass
    density=mass/volume;mass_lumps=lumps*density
    centre=first/volume;mass_centre=mass_lumps@points/mass
    volume_second=second/volume-np.outer(centre,centre)
    exact_inertia=mass*(np.trace(volume_second)*np.eye(3)-volume_second)
    centred=points-centre
    point_second=np.einsum('n,ni,nj->ij',mass_lumps,centred,centred)
    lump_inertia=np.trace(point_second)*np.eye(3)-point_second
    selected=[b for b in design['bonds'] if b['kind']==side]
    pairs=np.array([[mapping[i] for i in b['nodes']] for b in selected]);ids=[b['id'] for b in selected]
    degrees=np.bincount(pairs.reshape(-1),minlength=len(points));delta=points[pairs[:,1]]-points[pairs[:,0]]
    lengths=np.linalg.norm(delta,axis=1);directions=delta/lengths[:,None]
    base=(lumps[pairs[:,0]]/degrees[pairs[:,0]]+lumps[pairs[:,1]]/degrees[pairs[:,1]])/volume
    weights,fit=isotropic_orientation_weights(directions,base)
    # Central-force isotropy enforces the Cauchy relation lambda=G, hence nu=0.25.
    bulk=young_pa/(3*(1-2*.25));shear=young_pa/(2*(1+.25))
    k=9*bulk*volume*weights/lengths**2
    matrix=stiffness_matrix(points,pairs,k)
    fixed_nodes=np.array([mapping[i] for i in piece['surface_node_ids']])
    fixed=np.sort((3*fixed_nodes[:,None]+np.arange(3)).reshape(-1))
    free=np.setdiff1d(np.arange(3*len(points)),fixed)
    lu=splu(matrix[free][:,free].tocsc())
    modes=[];eps=.002
    for name,axes in [('compression_x',(0,0)),('compression_y',(1,1)),('compression_z',(2,2)),
                      ('shear_xy',(0,1)),('shear_xz',(0,2)),('shear_yz',(1,2))]:
        for sign in ([1.] if name.startswith('compression') else [-1.,1.]):
            affine=np.zeros_like(points)
            a,b=axes
            affine[:,a]=(-eps if a==b else sign*eps)*(points[:,b]-centre[b])
            vector=affine.reshape(-1).copy()
            vector[free]=lu.solve(-(matrix[free][:,fixed]@vector[fixed]))
            relaxed=vector.reshape(-1,3)
            force=matrix@vector
            affine_energy=float(.5*affine.reshape(-1)@(matrix@affine.reshape(-1)))
            energy=float(.5*vector@force)
            finite_energy=finite_spring_energy(points,relaxed,pairs,k)
            deformed=points+relaxed;p=deformed[cells]
            signed=np.linalg.det(p[:,1:]-p[:,:1])/6
            residual=float(np.linalg.norm(force[free])/max(np.linalg.norm(force[fixed]),1e-15))
            expected=.5*(bulk+4*shear/3 if a==b else shear)*volume*eps**2
            ratio=energy/affine_energy
            modes.append({'mode':name,'sign':sign,'strain_magnitude':eps,
                          'affine_energy_j':affine_energy,'affine_isotropic_energy_relative_error':affine_energy/expected-1,
                          'relaxed_linear_energy_j':energy,'relaxed_to_affine_energy_ratio':ratio,
                          'constrained_apparent_stiffness_pa':2*energy/(volume*eps**2),
                          'finite_spring_energy_j':finite_energy,'finite_vs_linear_energy_relative_error':finite_energy/energy-1,
                          'free_force_residual_fraction':residual,
                          'volume_ratio':float(signed.sum()/volume),'min_cell_volume_ratio':float(np.min(signed/volumes)),
                          'passed':bool(residual<1e-7 and .1<ratio<=1+1e-8 and np.all(signed>0) and abs(finite_energy/energy-1)<.03 and abs(affine_energy/expected-1)<1e-7)})
    inertia_error=float(np.linalg.norm(lump_inertia-exact_inertia)/np.linalg.norm(exact_inertia))
    omega2_bound=float(np.max(np.asarray(abs(matrix).sum(axis=1)).reshape(-1)/np.repeat(mass_lumps,3)))
    record={'side':side,'nodes':len(points),'integration_cells':len(cells),'volume_m3':float(volume),
            'mass_kg':mass,'previous_piece_mass_kg':sum(design['nodes'][i]['mass_kg'] for i in global_ids),
            'effective_synthetic_density_kg_m3':float(density),
            'tessellation_vs_closed_volume_relative_error':float(volume/boundary_volume-1),
            'tessellation_vs_boundary_centre_error_m':float(np.linalg.norm(first/volume-boundary_first/boundary_volume)),
            'surface_mass_fraction':float(mass_lumps[fixed_nodes].sum()/mass),
            'min_node_mass_kg':float(mass_lumps.min()),'mass_relative_error':float(mass_lumps.sum()/mass-1),
            'centre_of_mass_error_m':float(np.linalg.norm(centre-mass_centre)),
            'lumped_inertia_relative_error':inertia_error,'min_inertia_eigenvalue':float(np.linalg.eigvalsh(lump_inertia).min()),
            'isotropic_direction_correction':fit,'min_stiffness_n_m':float(k.min()),'max_stiffness_n_m':float(k.max()),
            'conservative_undamped_explicit_step_limit_s':2/math.sqrt(omega2_bound),
            'modes':modes,'passed':bool(all(m['passed'] for m in modes) and inertia_error<.05 and np.all(mass_lumps>0) and np.linalg.norm(centre-mass_centre)<1e-10 and abs(volume/boundary_volume-1)<1e-9 and np.linalg.norm(first/volume-boundary_first/boundary_volume)<1e-10)}
    assignments={'global_node_ids':global_ids,'node_volume_m3':lumps.tolist(),'node_mass_kg':mass_lumps.tolist(),
                 'bond_ids':ids,'bond_stiffness_n_m':k.tolist(),
                 'integration_cells_global_ids':[[global_ids[i] for i in t] for t in cells],
                 'integration_cells_role':'volume quadrature and inversion diagnostics only; no FEM forces'}
    return record,assignments
