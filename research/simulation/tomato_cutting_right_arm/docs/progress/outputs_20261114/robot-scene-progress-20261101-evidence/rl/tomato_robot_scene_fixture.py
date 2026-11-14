"""Actual target fixture and material-state reset in the rebased scene.

A tensile pulse is a numerical fixture check, not a cutting or gravity-support
qualification. No blade or robot reaction is applied by this routine.
"""
import numpy as np
import warp as wp
from tomato_isaac_startup_worker import write
from tomato_native_full_model import registry, build_model, configure_solver


def check_fixture(out):
    wp.init();wp.set_device('cuda:0')
    data=registry()
    data['x']=data['x']+np.array([0.,0.,.002])
    fixture=np.asarray(data['design']['fixture']['node_ids'],dtype=int)
    model=build_model(data,fixed_nodes=fixture)
    solver=configure_solver(model,data,iterations=32)
    states=[model.state(),model.state()]
    reference=model.particle_q.numpy().copy()
    slice_nodes=np.asarray([n['side']=='slice' for n in data['design']['nodes']])
    force=np.zeros_like(reference)
    force[slice_nodes,0]=-.001/int(slice_nodes.sum())
    traces=[];reset_records=[];steps=0
    for episode in range(2):
        if episode:
            # Both CUDA state buffers, force accumulators, damage and eligibility
            # are dirtied. Reset must restore each, not just visible positions.
            for state in states:
                state.particle_q.assign(reference+.0001)
                state.particle_qd.fill_(wp.vec3(.1))
                state.particle_f.fill_(wp.vec3(1.))
            solver.history.fill_(wp.vec2(.003,.75))
            solver.eligible.fill_(1)
            solver.invalid.fill_(1);solver.volume_invalid.fill_(1)
        solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_()
        solver.volume_step_fraction.fill_(1.);solver.volume_clip_count.zero_()
        for state in states:
            state.particle_q.assign(reference);state.particle_qd.zero_();state.clear_forces()
        solver.particle_q_prev.assign(reference)
        reset_records.append(dict(dirty=bool(episode),position_error_m=max(float(np.max(np.abs(s.particle_q.numpy()-reference))) for s in states),
            velocity_error_m_s=max(float(np.max(np.abs(s.particle_qd.numpy()))) for s in states),
            forces_clear=all(np.all(s.particle_f.numpy()==0) for s in states),
            history_clear=bool(np.all(solver.history.numpy()==0)),eligibility_clear=bool(np.all(solver.eligible.numpy()==0)),
            invalid_clear=bool(np.all(solver.invalid.numpy()==0) and np.all(solver.volume_invalid.numpy()==0))))
        trace=[]
        for i in range(3):
            if (out/'stop.request').exists():raise InterruptedError('Guard stop during fixture test')
            sin,sout=states[i%2],states[1-i%2]
            sin.clear_forces();sin.particle_f.assign(force)
            solver.step(sin,sout,None,None,1/2400);wp.synchronize();steps+=1
            solver.commit_cohesion(sout)
            x=sout.particle_q.numpy();v=sout.particle_qd.numpy()
            ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
            trace.append(dict(positions=x.tolist(),velocities=v.tolist(),history=solver.history.numpy().tolist(),
                fixed_error_m=float(np.max(np.abs(x[fixture]-reference[fixture]))),
                fixed_speed_m_s=float(np.max(np.abs(v[fixture]))),minimum_volume_ratio=float(ratios.min()),
                maximum_displacement_m=float(np.max(np.abs(x-reference)))))
        traces.append(trace)
    checks=dict(all_fixture_nodes_kinematic=bool(np.all(model.particle_mass.numpy()[fixture]==0)),
        slice_unconstrained=bool(np.all(model.particle_mass.numpy()[slice_nodes]>0)),
        fixture_holds=all(r['fixed_error_m']==0 and r['fixed_speed_m_s']==0 for t in traces for r in t),
        free_nodes_respond=max(r['maximum_displacement_m'] for r in traces[0])>0,
        volume_valid=all(r['minimum_volume_ratio']>.1 for t in traces for r in t),
        dirty_material_reset=all(r['position_error_m']==0 and r['velocity_error_m_s']==0 and r['forces_clear'] and r['history_clear'] and r['eligibility_clear'] and r['invalid_clear'] for r in reset_records),
        exact_replay=traces[0]==traces[1])
    write(out,'target_fixture.json',dict(checks=checks,newton_steps=steps,fixture_node_ids=fixture.tolist(),
        reset_records=reset_records,sequences=traces,force_total_n=force.sum(0).tolist(),gravity_m_s2=[0,0,0],
        target_origin_local_m=[0,0,.002],scope='Fixed authored bulk-side support, 0.001 N tensile pulse and dirty material reset/replay. No gravity, grasp, blade contact or cutting qualification.'))
    if not all(checks.values()):raise ValueError('Target fixture or material replay check failed: '+str(checks))
    return steps
