"""Bounded gravity support and active-to-clear contact reset for the mounted scene."""
import json
from pathlib import Path
import numpy as np
import warp as wp
import newton
from scipy.spatial.transform import Rotation
from tomato_native_full_model import registry,build_model,configure_solver
from tomato_exact_blade_coverage import coverage
from tomato_exact_blade_queries import sample
from tomato_mesh_weighted_contact import publish
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]


def check_target(out,tool_pose):
    wp.init();wp.set_device('cuda:0')
    data=registry();data['x']=data['x']+np.array([0.,0.,.002])
    fixture=np.asarray(data['design']['fixture']['node_ids'])
    model=build_model(data,fixed_nodes=fixture,body=True)
    model.set_gravity((0.,0.,-9.81))
    solver=configure_solver(model,data,iterations=32)
    states=[model.state(),model.state()];rest=model.particle_q.numpy().copy()
    traces=[];steps=0
    for episode in range(2):
        solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_()
        for state in states:state.particle_q.assign(rest);state.particle_qd.zero_();state.clear_forces()
        solver.particle_q_prev.assign(rest)
        trace=[]
        for i in range(12):
            if (out/'stop.request').exists():raise InterruptedError('Guard stop during target gravity probe')
            sin,sout=states[i%2],states[1-i%2];sin.clear_forces()
            solver.step(sin,sout,None,None,1/2400);wp.synchronize();solver.commit_cohesion(sout);steps+=1
            x=sout.particle_q.numpy();v=sout.particle_qd.numpy()
            ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
            trace.append(dict(positions=x.tolist(),velocities=v.tolist(),fixture_error_m=float(np.max(np.abs(x[fixture]-rest[fixture]))),
                minimum_board_clearance_m=float(x[:,2].min()),minimum_volume_ratio=float(ratios.min()),
                maximum_displacement_m=float(np.max(np.abs(x-rest)))))
        traces.append(trace)
    # Dirty the actual surface stream by moving the target to intersect the current
    # mounted blade. No force integration is done in this deliberate reset challenge.
    blade=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
    cells=json.loads((ROOT/'work/exact_blade_cells.json').read_text())
    if cells['source_blade_sha256']!=__import__('hashlib').sha256((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_bytes()).hexdigest():raise ValueError('Blade cell source mismatch')
    verts=np.asarray(blade['vertices']);faces=np.asarray(blade['triangles']);rot=Rotation.from_quat(tool_pose[3:]).as_matrix();trans=np.asarray(tool_pose[:3]);world=verts@rot.T+trans
    triangles=np.asarray([tri for piece in data['design']['pieces'] for tri in piece['triangles']])
    midpoint=(world.min(0)+world.max(0))/2
    shift=midpoint-np.array([data['design']['cut_x_m'],0.,.0295])
    dirty=rest+shift
    contact=newton.Contacts(rigid_contact_max=8,soft_contact_max=131072,requires_grad=False,clear_buffers=False,device='cuda:0')
    contact._enable_rigid_soft_full_surface_contact=True
    clipped=coverage(world,np.asarray(cells['cells']),dirty,triangles,reference_positions=rest,quadrature_level=0)
    samples=clipped['samples']
    query=sample(verts,faces,(np.asarray([s['point_m'] for s in samples])-trans)@rot)
    query['normal']=query['normal']@rot.T
    weights,payload=publish(contact,samples,query)
    count=int(contact.soft_contact_count.numpy()[0])
    if count<=0:raise ValueError('Reset challenge must start with generated blade contacts')
    for state in states:
        state.particle_q.assign(dirty);state.particle_qd.fill_(wp.vec3(.1));state.particle_f.fill_(wp.vec3(1.))
    solver.history.fill_(wp.vec2(.003,.75));solver.eligible.fill_(1)
    # Explicit reset of both integrator states and stateful material/contact data.
    for state in states:
        solver.reset(state,flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD)
        state.particle_q.assign(rest);state.particle_qd.zero_();state.clear_forces()
    solver.particle_q_prev.assign(rest);solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_()
    solver.volume_step_fraction.fill_(1.);solver.volume_clip_count.zero_();contact.clear()
    empty=coverage(world,np.asarray(cells['cells']),rest,triangles,reference_positions=rest,quadrature_level=0)
    if empty['samples']:raise ValueError('Reset target must be clear of mounted blade')
    cleared_weights,cleared_payload=publish(contact,[],dict(phi=[],normal=[],closest=[]))
    checks=dict(fixture_holds_under_gravity=all(r['fixture_error_m']==0 for t in traces for r in t),
        target_above_board=all(r['minimum_board_clearance_m']>0 for t in traces for r in t),
        volume_valid=all(r['minimum_volume_ratio']>.1 for t in traces for r in t),
        gravity_replay_exact=traces[0]==traces[1],
        active_contact_challenge=count>0,contact_count_cleared=int(contact.soft_contact_count.numpy()[0])==0 and len(cleared_weights)==0,
        both_states_restored=all(np.array_equal(s.particle_q.numpy(),rest) and np.all(s.particle_qd.numpy()==0) and np.all(s.particle_f.numpy()==0) for s in states),
        material_history_cleared=bool(np.all(solver.history.numpy()==0) and np.all(solver.eligible.numpy()==0)))
    write(out,'mounted_target_checks.json',dict(checks=checks,gravity_m_s2=[0,0,-9.81],simulated_duration_s=.005,episodes=traces,
        newton_steps=steps,dirty_generated_contacts=count,cleared_generated_contacts=int(contact.soft_contact_count.numpy()[0]),
        load_weight_n=float(sum(data['mass'])*9.81),damage_eligibility=False,
        scope='5 ms target gravity-support probe and deliberate generated-contact/material reset. No settled support, cutting-load or post-fracture qualification.'))
    if not all(checks.values()):raise ValueError('Mounted target checks failed: '+str(checks))
    return steps
