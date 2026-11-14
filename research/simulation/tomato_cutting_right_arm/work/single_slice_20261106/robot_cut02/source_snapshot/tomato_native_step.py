"""Unexecuted single-blade coupon step binding; no native imports at load.

This binds a version-inspected VBD cadence only. Software ordering tests do not
establish Warp compatibility, native force accuracy or contact completeness.
"""
import math
from tomato_soft_contact_observer import check_contact_layout

EVENTS=('pose','clear_forces','collide','solve','observe','commit')


class StepCadence:
    def __init__(self, step, start_s, dt_s):
        if type(step)is not int or step<0 or not math.isfinite(start_s) or start_s<0 or not math.isfinite(dt_s) or dt_s<=0:
            raise ValueError('Invalid step metadata')
        self.step,self.start_s,self.dt_s=step,start_s,dt_s
        self.events=[]

    def mark(self,event):
        if len(self.events)>=len(EVENTS) or event!=EVENTS[len(self.events)]:
            raise ValueError('Missing, duplicated or out-of-order step event')
        self.events.append(event)

    def complete(self):
        if tuple(self.events)!=EVENTS:raise ValueError('Incomplete step cannot be committed')
        return dict(step=self.step,start_s=self.start_s,dt_s=self.dt_s,events=list(self.events))


def step_native_once(bundle, pose, *, step, start_s, dt_s, observer_kernel,
                     first_step=False, native_execution_authorized=False):
    """Source-only binder for the isolated one-rigid-body coupon.

    first_step is required after construction/reset so previous body pose is
    rebaselined exactly as VBD's first/reset step. Mid-episode reset is forbidden
    here: rebuild/reset through a separate validated episode path.
    """
    if native_execution_authorized is not True:
        raise PermissionError('Native stepping disabled during preparation')
    if (step==0)!=bool(first_step):raise ValueError('First-step history flag mismatch')
    cadence=StepCadence(step,start_s,dt_s)
    if pose['rotation'] not in [((0.,0.,1.),(1.,0.,0.),(0.,1.,0.)),[[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]]:
        raise ValueError('Only reviewed fixed cyclic blade orientation supported')
    import warp as wp
    model,solver=bundle['model'],bundle['solver']
    s0,s1=bundle['state0'],bundle['state1']
    contacts,pipeline=bundle['contacts'],bundle['pipeline']
    if model.body_count!=1 or bundle['blade_body_id']!=0:
        raise ValueError('Observer route supports exactly one isolated blade body')
    q=s0.body_q.numpy().copy();qd=s0.body_qd.numpy().copy()
    q[0,:3]=pose['translation_m'];q[0,3:]=(.5,.5,.5,.5)
    qd[0,:3]=pose['linear_velocity_m_s'];qd[0,3:]=(0.,0.,0.)
    s0.body_q.assign(wp.array(q,dtype=wp.transform,device=model.device))
    s0.body_qd.assign(wp.array(qd,dtype=wp.spatial_vector,device=model.device))
    cadence.mark('pose')
    body_prev=wp.clone(s0.body_q if first_step else solver.body_q_prev)
    s0.clear_forces();cadence.mark('clear_forces')
    pipeline.collide(s0,contacts);cadence.mark('collide')
    solver.step(s0,s1,bundle['control'],contacts,dt_s);cadence.mark('solve')
    # forward_step sets particle_q_prev from incoming particle_q. Finalization
    # computes velocity but leaves particle_q_prev intact (inspected source).
    total=int(contacts.soft_contact_count.numpy()[0]);capacity=int(contacts.soft_contact_max)
    body_counts=[int(x) for x in solver.body_particle_contact_counts.numpy()]
    per_body=int(solver.body_particle_contact_buffer_pre_alloc)
    flat=solver.body_particle_contact_indices.numpy()
    ids=[[int(x) for x in flat[b*per_body:b*per_body+min(c,per_body)]] for b,c in enumerate(body_counts)]
    shapes=contacts.soft_contact_shape.numpy();shape_body=model.shape_body.numpy()
    if total>=capacity or any(int(x)<0 or int(x)>=len(shape_body) for x in shapes[:total]):
        raise ValueError('Saturated or invalid soft-contact stream')
    bodies=[int(shape_body[int(x)]) for x in shapes[:total]]
    layout=check_contact_layout(total_count=total,total_capacity=capacity,body_counts=body_counts,
        body_capacity=per_body,body_indices=ids,record_bodies=bodies)
    wrench=wp.zeros(model.body_count,dtype=wp.spatial_vector,device=model.device)
    invalid=wp.zeros(model.body_count,dtype=int,device=model.device)
    wp.launch(observer_kernel,dim=model.body_count,inputs=[dt_s,s1.particle_q,solver.particle_q_prev,
        model.particle_radius,s1.body_q,body_prev,s1.body_qd,model.body_com,float(solver.friction_epsilon),
        solver.body_particle_contact_penalty_k,solver.body_particle_contact_material_kd,
        solver.body_particle_contact_material_mu,contacts.soft_contact_count,contacts.soft_contact_indices,
        contacts.soft_contact_barycentric,contacts.soft_contact_shape,contacts.soft_contact_body_pos,
        contacts.soft_contact_body_vel,contacts.soft_contact_normal,model.shape_margin,model.shape_body,
        per_body,solver.body_particle_contact_counts,solver.body_particle_contact_indices],
        outputs=[wrench,invalid],device=model.device)
    if any(int(x) for x in invalid.numpy()):raise ValueError('Invalid observer records')
    values=wrench.numpy().tolist()
    if any(not math.isfinite(x) for row in values for x in row):raise ValueError('Nonfinite reaction')
    cadence.mark('observe')
    bundle['state0'],bundle['state1']=s1,s0;cadence.mark('commit')
    return {**cadence.complete(),'spatial_wrench_world_about_com':values,
            'force_convention':'force_then_moment','soft_contact_count':total,
            'layout':layout,'native_physics_pass':False,
            'scope':'solver-derived reaction diagnostic only; no independent contact or energy acceptance'}
