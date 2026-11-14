"""Independent host reference for VBD diagonal contact scatter; no native imports."""


def scatter_reference(force,hessian,corners,weights,particle_count,*,colors=None,active_color=None):
    if len(corners)!=3 or len(weights)!=3 or particle_count<=0:
        raise ValueError('Three padded corners/weights and positive particle count required')
    active=[i for i in corners if i>=0]
    if len(set(active))!=len(active) or any(i>=particle_count for i in active):
        raise ValueError('Distinct registered particle corners required')
    forces=[[0.,0.,0.] for _ in range(particle_count)]
    matrices=[[[0.,0.,0.] for _ in range(3)] for _ in range(particle_count)]
    for corner,weight in zip(corners,weights):
        if corner<0:
            if weight!=0:raise ValueError('Padded corner requires zero weight')
            continue
        if active_color is not None and colors[corner]!=active_color:continue
        forces[corner]=[weight*v for v in force]
        matrices[corner]=[[weight**2*v for v in row] for row in hessian]
    return forces,matrices
