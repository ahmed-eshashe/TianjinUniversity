"""Actual-cache native reaction collector for the fixed 1/2400 s diagnostic."""
def collect_reaction(model, state, state_in, contacts, solver):
    import warp as wp
    from newton._src.solvers.vbd.rigid_vbd_kernels import _eval_soft_ef_contact
    count = int(contacts.soft_contact_count.numpy()[0])
    if not 0 < count < contacts.soft_contact_max:
        raise ValueError('Nonempty unsaturated contact stream required')
    ke=solver.body_particle_contact_penalty_k
    kd=solver.body_particle_contact_material_kd
    mu=solver.body_particle_contact_material_mu
    previous_particle=solver.particle_q_prev
    previous_body=state_in.body_q

    @wp.kernel(enable_backward=False)
    def evaluate(pos: wp.array[wp.vec3], previous_pos: wp.array[wp.vec3], radius: wp.array[float],
                 body_q: wp.array[wp.transform], body_prev: wp.array[wp.transform],
                 body_qd: wp.array[wp.spatial_vector], body_com: wp.array[wp.vec3],
                 shape_body: wp.array[int], corners: wp.array[wp.vec3i], bary: wp.array[wp.vec3],
                 shapes: wp.array[int], points: wp.array[wp.vec3], velocities: wp.array[wp.vec3],
                 normals: wp.array[wp.vec3], margins: wp.array[float], k: wp.array[float],
                 damping: wp.array[float], friction: wp.array[float], eps: float, dt: float,
                 force: wp.array[wp.vec3], hessian: wp.array[wp.mat33], rigid_point: wp.array[wp.vec3],
                 body_wrench: wp.array[wp.spatial_vector]):
        i = wp.tid()
        f, h, point = _eval_soft_ef_contact(i, corners[i], bary[i], pos, previous_pos, radius,
            k[i], damping[i], friction[i], eps, shape_body, body_q, body_prev, body_qd, body_com,
            shapes, points, velocities, normals, margins, dt)
        body = shape_body[shapes[i]]
        com = wp.transform_point(body_q[body], body_com[body])
        reaction = -f
        force[i] = f; hessian[i] = h; rigid_point[i] = point
        body_wrench[i] = wp.spatial_vector(reaction, wp.cross(point-com, reaction))

    force = wp.zeros(count, dtype=wp.vec3); hessian = wp.zeros(count, dtype=wp.mat33)
    point = wp.zeros(count, dtype=wp.vec3); wrench = wp.zeros(count, dtype=wp.spatial_vector)
    wp.launch(evaluate, dim=count, inputs=[state.particle_q, previous_particle, model.particle_radius,
        state.body_q, previous_body, state.body_qd, model.body_com, model.shape_body,
        contacts.soft_contact_indices, contacts.soft_contact_barycentric, contacts.soft_contact_shape,
        contacts.soft_contact_body_pos, contacts.soft_contact_body_vel, contacts.soft_contact_normal,
        model.shape_margin, ke, kd, mu, solver.friction_epsilon, 1/2400],
        outputs=[force, hessian, point, wrench], device=model.device)
    wp.synchronize()
    return {'ke': ke.numpy().tolist(), 'kd': kd.numpy().tolist(), 'mu': mu.numpy().tolist(),
             'force': force.numpy().tolist(),
            'hessian': hessian.numpy().tolist(), 'rigid_point': point.numpy().tolist(), 'wrench': wrench.numpy().tolist()}

