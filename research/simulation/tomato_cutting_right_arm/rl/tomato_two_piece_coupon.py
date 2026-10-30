"""Independent synthetic contact solids; no fracture or native validation claim."""
from itertools import combinations


def description():
    # Identical outward-oriented cubes separated along x. Outer faces are fixtures.
    positions=[]
    triangles=[]
    springs=[]
    fixed=[]
    faces=((0,2,3),(0,3,1),(4,5,7),(4,7,6),(0,1,5),(0,5,4),
           (2,6,7),(2,7,3),(0,4,6),(0,6,2),(1,3,7),(1,7,5))
    for side,(lo,hi) in enumerate(((-.0105,-.0005),(.0005,.0105))):
        start=len(positions)
        positions.extend([[x,y,z] for x in (lo,hi) for y in (0.,.01) for z in (0.,.01)])
        triangles.extend([[start+i for i in reversed(tri)] for tri in faces])
        springs.extend([[start+a,start+b] for a,b in combinations(range(8),2)])
        fixed.extend(range(start+(0 if side==0 else 4),start+(4 if side==0 else 8)))
    return {'kind':'synthetic_two_piece_nonfracturing_contact_diagnostic',
        'positions_m':positions,'triangles':triangles,'springs':springs,
        'piece_particle_ids':[list(range(8)),list(range(8,16))],
        'fixed_particle_ids':fixed,'initial_face_gap_m':.001,
        'free_particle_mass_kg':.001,'spring_ke_n_m':10.,'spring_kd_ns_m':0.,
        'triangle_elastic_stiffness':0.,'gravity_m_s2':[0.,0.,0.],
        'self_contact_solver_options':{
            'particle_enable_self_contact':True,
            'particle_self_contact_margin':.0001,
            'particle_self_contact_gap':.0001,
            'particle_rest_shape_contact_exclusion_radius':0.,
            'particle_topological_contact_filter_threshold':2,
            'particle_vertex_contact_buffer_size':32,
            'particle_edge_contact_buffer_size':64},
        'native_runtime_validated':False,'material_calibrated':False,
        'cut_or_release_pass':False,
        'pending':['prescribed fixture motion and native binding',
                   'independent particle-particle reaction and work observer',
                   'candidate completeness and buffer overflow detection',
                   'face, edge, rim, off-plane and withdrawal runtime cases']}


def native_solver_options(*,native_execution_authorized=False):
    """Explicit guard prevents this preparation helper from enabling execution."""
    if native_execution_authorized is not True:
        raise PermissionError('Native execution disabled during preparation')
    return description()['self_contact_solver_options'].copy()


def build_native_candidate(*,native_execution_authorized=False):
    """Unexecuted source binding; later launch guard and authorization required.

    No prescribed closure or force collector is attached. A resting separated
    model is not a successful contact test. Triangle elasticity is zero because
    springs supply the diagnostic solid's elastic response.
    """
    options=native_solver_options(native_execution_authorized=native_execution_authorized)
    import warp as wp
    import newton
    import newton.solvers
    d=description()
    builder=newton.ModelBuilder(gravity=tuple(d['gravity_m_s2']))
    for i,p in enumerate(d['positions_m']):
        builder.add_particle(wp.vec3(*p),wp.vec3(0.),
            0. if i in d['fixed_particle_ids'] else d['free_particle_mass_kg'],radius=0.)
    for a,b in d['springs']:
        builder.add_spring(a,b,d['spring_ke_n_m'],d['spring_kd_ns_m'],0.)
    for a,b,c in d['triangles']:
        builder.add_triangle(a,b,c,tri_ke=0.,tri_ka=0.,tri_kd=0.)
    builder.color()
    model=builder.finalize()
    model.soft_contact_ke=1000.
    model.soft_contact_kd=0.
    model.soft_contact_mu=0.
    solver=newton.solvers.SolverVBD(model,iterations=5,rigid_compliant_alm=True,**options)
    return {'model':model,'solver':solver,'state0':model.state(),'state1':model.state(),
            'control':model.control(),'description':d,
            'validation_status':'UNEXECUTED_TWO_PIECE_SOURCE_ONLY'}
