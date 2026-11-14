"""Installed mesh-SDF API adapter. Original coupon mechanics remain unchanged.

SDF resolution and default 0.05 m cooking padding are explicit. CUDA is
required by the installed texture-SDF implementation; the CPU PhysX robot is
not constructed, migrated or coupled by this isolated diagnostic.
"""
from tomato_native_coupon import coupon_description, validate_blade_export


def build_runtime_candidate(blade, *, native_execution_authorized=False, sdf_resolution=128, sdf_padding_m=0.05):
    """Runtime adapter for the guarded isolated stationary diagnostic.

    Even authorization here is not a replacement for the launch watchdog. There
    is intentionally no command-line execution route during preparation.
    """
    if native_execution_authorized is not True:
        raise PermissionError('Native construction disabled during preparation')
    if type(sdf_resolution) is not int or sdf_resolution not in (128, 256, 512, 1024):
        raise ValueError('Only reviewed SDF comparison resolutions allowed')
    if type(sdf_padding_m) not in (int, float) or sdf_padding_m not in (0.05, 0.005):
        raise ValueError('Only reviewed SDF cooking bounds allowed')
    validate_blade_export(blade)
    import numpy as np
    import warp as wp
    import newton
    import newton.solvers
    cfg=coupon_description()
    builder=newton.ModelBuilder(gravity=tuple(cfg['gravity_m_s2']))
    for i,p in enumerate(cfg['positions_m']):
        builder.add_particle(wp.vec3(*p),wp.vec3(0.),
            0. if i in cfg['fixed_particle_ids'] else cfg['free_particle_mass_kg'],
            radius=cfg['particle_radius_m'])
    for a,b in cfg['springs']:
        builder.add_spring(a,b,cfg['spring_ke_n_m'],cfg['spring_kd_ns_m'],0.)
    for a,b,c in cfg['triangles']:
        builder.add_triangle(a,b,c,tri_ke=0.,tri_ka=0.,tri_kd=0.)
    body=builder.add_body(is_kinematic=True,label='prescribed_real_blade')
    shape=newton.ModelBuilder.ShapeConfig(density=0.,mu=0.)
    shape.configure_sdf(force_sdf=True)
    mesh=newton.Mesh(np.asarray(blade['vertices'],dtype=np.float32),
                     np.asarray(blade['triangles'],dtype=np.int32).reshape(-1))
    mesh.build_sdf(device="cuda:0", max_resolution=sdf_resolution, margin=sdf_padding_m)
    builder.add_shape_mesh(body,mesh=mesh,cfg=shape,label='real_blade_collision')
    builder.color()
    model=builder.finalize(device="cuda:0")
    model.soft_contact_ke=1000.
    model.soft_contact_kd=0.
    model.soft_contact_mu=0.
    solver=newton.solvers.SolverVBD(model,iterations=5,rigid_compliant_alm=True,
        integrate_with_external_rigid_solver=False,rigid_body_contact_buffer_size=512)
    pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,
        enable_rigid_soft_full_surface_contact=True)
    return {'model':model,'solver':solver,'pipeline':pipeline,
            'contacts':pipeline.contacts(),'state0':model.state(),'state1':model.state(),
            'control':model.control(),'blade_body_id':body,
            'validation_status':'UNEXECUTED_CANDIDATE_NOT_A_CUTTING_PASS'}

