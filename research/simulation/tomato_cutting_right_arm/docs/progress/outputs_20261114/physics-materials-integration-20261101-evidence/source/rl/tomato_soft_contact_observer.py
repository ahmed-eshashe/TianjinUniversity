"""Read-only native observer source and offline contact-buffer checks.

The kernel reuses a version-pinned private solver helper: reaction logging is
not an independent physics audit. Factory execution is disabled by default.
"""
import hashlib
from pathlib import Path


def check_contact_layout(*, total_count, total_capacity, body_counts,
                         body_capacity, body_indices, record_bodies,
                         independent_reference_counts=None):
    values=[total_count,total_capacity,body_capacity,*body_counts]
    if any(type(x)is not int or x<0 for x in values) or total_capacity==0 or body_capacity==0:
        raise ValueError('Explicit finite contact counts/capacities required')
    if total_count>=total_capacity:
        raise ValueError('Soft-contact buffer saturated or overflowing')
    if len(body_counts)!=len(body_indices) or len(record_bodies)!=total_count:
        raise ValueError('Missing contact/adjacency metadata')
    if any(type(b)is not int or not -1<=b<len(body_counts) for b in record_bodies):
        raise ValueError('Invalid contact body mapping')
    expected=[[] for _ in body_counts]
    for index,body in enumerate(record_bodies):
        if body>=0:expected[body].append(index)
    for body,(count,indices) in enumerate(zip(body_counts,body_indices)):
        if count>=body_capacity:
            raise ValueError('Per-body adjacency saturated or truncated')
        if len(indices)!=count or any(type(i)is not int or not 0<=i<total_count for i in indices):
            raise ValueError('Invalid retained contact indices')
        if len(indices)!=len(set(indices)) or sorted(indices)!=expected[body]:
            raise ValueError('Retained contact stream differs from solve adjacency')
    if independent_reference_counts is not None:
        if any(type(x)is not int or x<0 for x in independent_reference_counts):
            raise ValueError('Invalid independent reference counts')
        if list(independent_reference_counts)!=list(body_counts):
            raise ValueError('Independent candidate reference count mismatch')
    return {'retained_stream_matches_adjacency':True,
            'independent_candidate_completeness_supplied':independent_reference_counts is not None,
            'broad_phase_completeness_proven':False,'native_runtime_validated':False}


def make_native_observer(*, expected_helper_sha256, native_execution_authorized=False):
    """Source-only factory, to be bound by the future guarded native worker.

    Caller must validate layout and snapshot the same current/previous state and
    contact/material buffers consumed by the solve. Output is world force then
    world moment about each body's COM, not a joint/sensor wrench.
    """
    if native_execution_authorized is not True:
        raise PermissionError('Observer native execution disabled during preparation')
    helper=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/rigid_vbd_kernels.py')
    if not expected_helper_sha256 or hashlib.sha256(helper.read_bytes()).hexdigest()!=expected_helper_sha256:
        raise ValueError('Private helper source version mismatch')
    import warp as wp
    from newton._src.solvers.vbd.rigid_vbd_kernels import _eval_soft_ef_contact

    @wp.kernel(enable_backward=False)
    def observe(dt:float, particle_q:wp.array[wp.vec3], particle_q_prev:wp.array[wp.vec3],
                particle_radius:wp.array[float], body_q:wp.array[wp.transform],
                body_q_prev:wp.array[wp.transform], body_qd:wp.array[wp.spatial_vector],
                body_com:wp.array[wp.vec3], friction_epsilon:float,
                penalty_k:wp.array[float], material_kd:wp.array[float], material_mu:wp.array[float],
                soft_count:wp.array[int], corners:wp.array[wp.vec3i], bary:wp.array[wp.vec3],
                contact_shape:wp.array[int], contact_body_pos:wp.array[wp.vec3],
                contact_body_vel:wp.array[wp.vec3], contact_normal:wp.array[wp.vec3],
                shape_margin:wp.array[float], shape_body:wp.array[int], capacity:int,
                body_counts:wp.array[int], body_indices:wp.array[int],
                out_wrench:wp.array[wp.spatial_vector], out_invalid:wp.array[int]):
        body=wp.tid()
        force=wp.vec3(0.0);moment=wp.vec3(0.0);bad=int(0)
        com=wp.transform_point(body_q[body],body_com[body])
        count=body_counts[body]
        if count>=capacity:
            bad=1
        else:
            for j in range(count):
                index=body_indices[body*capacity+j]
                if index<0 or index>=soft_count[0]:
                    bad=1
                else:
                    cs=corners[index]
                    shape=contact_shape[index]
                    if cs[0]<0 or cs[0]>=particle_q.shape[0] or cs[1]<-1 or cs[1]>=particle_q.shape[0] or cs[2]<-1 or cs[2]>=particle_q.shape[0]:
                        bad=1
                    elif shape<0 or shape>=shape_body.shape[0]:
                        bad=1
                    elif shape_body[shape]!=body:
                        bad=1
                    else:
                        fp,hess,point=_eval_soft_ef_contact(index,cs,bary[index],particle_q,
                            particle_q_prev,particle_radius,penalty_k[index],material_kd[index],
                            material_mu[index],friction_epsilon,shape_body,body_q,body_q_prev,
                            body_qd,body_com,contact_shape,contact_body_pos,contact_body_vel,
                            contact_normal,shape_margin,dt)
                        reaction=-fp
                        force+=reaction;moment+=wp.cross(point-com,reaction)
        out_wrench[body]=wp.spatial_vector(force,moment)
        out_invalid[body]=bad
    return observe
