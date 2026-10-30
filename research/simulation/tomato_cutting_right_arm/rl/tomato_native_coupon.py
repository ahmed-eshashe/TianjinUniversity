"""Source-only candidate native contact coupon. CLI never runs an engine.

Builder calls follow inspected installed Newton examples. Native construction
is unexecuted; real blade export, reaction logging and launch integration remain
required. This diagnostic tetrahedron is not the accepted tomato model.
"""
import argparse
import json
import math
from itertools import combinations


def coupon_description():
    return {'kind':'synthetic_nonfracturing_tetra_contact_coupon',
            'positions_m':[[0.,0.,0.],[.01,0.,0.],[0.,.01,0.],[0.,0.,.01]],
            'triangles':[[0,2,1],[0,1,3],[0,3,2],[1,2,3]],
            'springs':[list(x) for x in combinations(range(4),2)],
            'fixed_particle_ids':[0,1,2],'free_particle_mass_kg':.001,
            'spring_ke_n_m':10.,'spring_kd_ns_m':0.,'particle_radius_m':0.,
            'gravity_m_s2':[0.,0.,0.],'triangle_elastic_stiffness':0.,
            'damage_enabled':False,'material_calibrated':False,
            'tomato_equivalence':False,'native_runtime_validated':False}


def validate_blade_export(blade):
    """Require an explicit measured SI export; never substitute a thick box."""
    if blade.get('units')!='m' or blade.get('frame')!='blade_local':
        raise ValueError('Blade needs explicit SI local coordinates')
    digest=blade.get('source_sha256','')
    if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Original blade asset hash required')
    v,f=blade.get('vertices'),blade.get('triangles')
    if not isinstance(v,list) or len(v)<4 or not isinstance(f,list) or len(f)<4:
        raise ValueError('Complete original blade surface export required')
    for p in v:
        if len(p)!=3 or not all(math.isfinite(x) for x in p):
            raise ValueError('Invalid blade vertices')
    for tri in f:
        if len(tri)!=3 or len(set(tri))!=3 or any(type(i)is not int or not 0<=i<len(v) for i in tri):
            raise ValueError('Invalid blade triangle indices')
    return blade


def build_native_candidate(blade, *, native_execution_authorized=False):
    """Unexecuted native builder; must only be called by a later reviewed guard.

    Even authorization here is not a replacement for the launch watchdog. There
    is intentionally no command-line execution route during preparation.
    """
    if native_execution_authorized is not True:
        raise PermissionError('Native construction disabled during preparation')
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
    shape.configure_sdf(max_resolution=128,force_sdf=True)
    mesh=newton.Mesh(np.asarray(blade['vertices'],dtype=np.float32),
                     np.asarray(blade['triangles'],dtype=np.int32).reshape(-1))
    builder.add_shape_mesh(body,mesh=mesh,cfg=shape,label='real_blade_collision')
    builder.color()
    model=builder.finalize()
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


def main():
    parser=argparse.ArgumentParser(description='Print source-only coupon description; no native execution')
    parser.add_argument('--config',required=False)
    args=parser.parse_args()
    print(json.dumps({'execution_enabled':False,'coupon':coupon_description(),
        'requested_config':args.config,'pending':['verified real blade SI export/pose',
        'SDF accuracy and capacity','soft contact reaction collector',
        'trajectory/state export and two-piece case','reviewed native watchdog integration']},indent=2))


if __name__=='__main__':
    main()
