"""Reset/replay persistent turning fixtures after coast and during active contact."""
import argparse,hashlib,math,signal,traceback,copy
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_contact_feedback_worker import collect_reaction
from tomato_offset_contact_reference import world_point,rotation_vector
from tomato_turning_sequence_reference import step as reference_step
from tomato_reset_replay_reference import compare_traces
from tomato_physx_proxy_reference import check_pulse,check_coast
from tomato_wrench_contract import cross,dot
ROOT=Path(__file__).resolve().parents[1]
DT=1/1200
INERTIA=.0001


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;ns=ps=0;cases=[];normals_updated=False;reset_cycles=dirty_resets=0;comparisons=[];episodes=[];reset_records=[]
    def stop(signum,frame):raise InterruptedError('Turning sequence stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():
        return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
            shutdown_completion='supervisor_must_observe_exit',turning_cases_completed=len(cases),
            newton_steps=ns,physx_steps=ps,min_coast_steps=min((r['coast_steps'] for r in cases),default=0),
            normals_updated=normals_updated,reset_checks_passed=passed,reset_cases_completed=len(cases),
            reset_cycles_completed=reset_cycles,replay_comparisons=len(comparisons),dirty_wrench_resets=dirty_resets,
            robot_validated=False,blade_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [Path(__file__),ROOT/'rl/tomato_turning_sequence_reference.py',ROOT/'rl/tomato_reset_replay_reference.py',ROOT/'rl/tomato_contact_feedback_worker.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,newton_step_cap=68,physx_step_cap=34,dt_s=DT,
            scope='Persistent off-centre analytic contacts; identity and Y-rotated offset-COM fixtures; isotropic inertia; no robot/blade.'))
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cpu',visualizer=['none']);app=launcher.app
        import torch
        import warp as wp
        import newton
        import newton.solvers
        import isaaclab.sim as sim_utils
        from isaaclab.assets import RigidObject,RigidObjectCfg
        from isaaclab_physx.physics import PhysxCfg
        from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
        wp.init();wp.set_device('cuda:0')
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=DT,gravity=(0.,0.,0.),
            physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
        descriptors=[dict(pose=[0.,0.,0.,0.,0.,0.,1.],com=[0.,0.,0.]),
            dict(pose=[0.,.05,0.,0.,math.sqrt(.5),0.,math.sqrt(.5)],com=[.002,-.001,.0005])]
        bodies=[]
        for i in range(2):
            spawn=sim_utils.CuboidCfg(size=(.02,.02,.004),
                rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),
                    PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,
                                     sleep_threshold=0.,stabilization_threshold=0.,solver_position_iteration_count=16,solver_velocity_iteration_count=0)],
                collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),
                mass_props=sim_utils.MassCfg(mass=.02,density=0.))
            bodies.append(RigidObject(RigidObjectCfg(prim_path=f'/World/FeedbackProxy{i}',spawn=spawn,
                init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(descriptors[i]['pose'][:3]),rot=tuple(descriptors[i]['pose'][3:])))))
        sim.reset();baseline=int(sim._physics_step_count)
        from pxr import PhysxSchema
        scene=PhysxSchema.PhysxSceneAPI(sim.stage.GetPrimAtPath('/physicsScene'))
        if str(scene.GetSolverTypeAttr().Get())!='TGS' or not scene.GetEnableExternalForcesEveryIterationAttr().Get():
            raise ValueError('TGS with force per internal iteration required')
        for i in range(2):
            api=PhysxSchema.PhysxRigidBodyAPI(sim.stage.GetPrimAtPath(f'/World/FeedbackProxy{i}'))
            if api.GetSolverPositionIterationCountAttr().Get()!=16 or api.GetSolverVelocityIterationCountAttr().Get()!=0:
                raise ValueError('Expected 16 body position iterations, zero velocity iterations')
        if 'isaaclab_physx' not in sim.physics_manager.__module__:raise ValueError('CPU PhysX required')
        def physx_state(body):
            return dict(pose=body.data.root_link_pose_w.torch.cpu().tolist()[0],
                velocity=body.data.root_com_vel_w.torch.cpu().tolist()[0])
        def echo(body,states):
            original=physx_state(body)
            for state in states:
                wp.copy(state.body_q,body.data.root_link_pose_w.warp)
                wp.copy(state.body_qd,body.data.root_com_vel_w.warp)
            wp.synchronize()
            if any(s.body_q.numpy().tolist()[0]!=original['pose'] or s.body_qd.numpy().tolist()[0]!=original['velocity'] for s in states):
                raise ValueError('Newton state echo mismatch')
            return original
        fixtures=[]
        for i,(body,description) in enumerate(zip(bodies,descriptors)):
            if (out/'stop.request').exists():raise InterruptedError('Stopped before offset fixture')
            body.reset();local_com=description['com']
            body.set_coms_index(coms=torch.tensor([[local_com+[0.,0.,0.,1.]]],dtype=torch.float32))
            body.set_inertias_index(inertias=torch.tensor([[[INERTIA,0.,0.,0.,INERTIA,0.,0.,0.,INERTIA]]],dtype=torch.float32))
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32))
            initial=physx_state(body)
            actual_com=body.data.body_com_pose_b.torch.cpu().tolist()[0][0][:3]
            if math.dist(actual_com,local_com)>1e-8:raise ValueError('PhysX COM offset mismatch')
            mp=.01;mass=float(body.data.body_mass.torch[0,0]);inertia=body.data.body_inertia.torch[0,0].cpu().tolist()
            if any(abs(inertia[j]-(INERTIA if j in (0,4,8) else 0.))>1e-9 for j in range(9)):
                raise ValueError('Explicit isotropic inertia required')
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            point=world_point(initial['pose'],[.004,.003,.001])
            builder.add_particle(wp.vec3(*point),wp.vec3(0.),mp,radius=0.)
            proxy=builder.add_body(xform=wp.transform(wp.vec3(*initial['pose'][:3]),wp.quat(*initial['pose'][3:])),
                com=wp.vec3(*actual_com),mass=mass,inertia=wp.mat33(INERTIA,0.,0.,0.,INERTIA,0.,0.,0.,INERTIA),
                lock_inertia=True,is_kinematic=True)
            shape=builder.add_shape_box(proxy,hx=.01,hy=.01,hz=.002,
                cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.))
            builder.color();model=builder.finalize(device='cuda:0')
            model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
            if model.body_com.numpy().tolist()[0]!=actual_com:raise ValueError('Newton/PhysX local COM mismatch')
            sin=model.state();sout=model.state();initial=echo(body,(sin,sout))
            solver=newton.solvers.SolverVBD(model,iterations=16,rigid_compliant_alm=True,
                integrate_with_external_rigid_solver=True,rigid_avbd_beta=0.)
            if solver.rigid_contact_k_start_value!=-1.:raise ValueError('Fixed penalty required')
            pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=8,
                rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True)
            contacts=pipeline.contacts()
            initial_state=dict(pose=initial['pose'],velocity=initial['velocity'],p=sin.particle_q.numpy().tolist()[0],vp=[0.]*3)
            record=dict(id='identity_turning' if i==0 else 'rotated_offset_com_turning',initial=initial_state,
                com_local=actual_com,particle_mass_kg=float(model.particle_mass.numpy()[0]),body_mass_kg=mass,
                height_m=float(model.shape_scale.numpy()[shape][2]),isotropic_inertia_kg_m2=INERTIA,coast_steps=0,steps=[])
            cases.append(record)
            fixtures.append(dict(body=body,model=model,sin=sin,sout=sout,solver=solver,pipeline=pipeline,
                contacts=contacts,record=record,reference_state=initial_state,total_impulse=[0.]*3,
                total_angular_impulse=[0.]*3,seen_contact=False,seen_clear=False))
        for episode,episode_length in enumerate((16,2,16)):
            if episode:
                if (out/'stop.request').exists():raise InterruptedError('Stopped before reset cycle')
                for fixture in fixtures:
                    body=fixture['body'];r=fixture['record'];solver=fixture['solver']
                    previous_count=int(fixture['contacts'].soft_contact_count.numpy()[0])
                    if previous_count!=(0 if episode==1 else 1):raise ValueError('Reset source must exercise coast then active contact')
                    # Dirty both queues deliberately; no simulation step applies these test loads.
                    for composer in (body.instantaneous_wrench_composer,body.permanent_wrench_composer):
                        composer.set_forces_and_torques_index(forces=torch.tensor([[[99.,-55.,33.]]],dtype=torch.float32),
                            torques=torch.tensor([[[1.,2.,3.]]],dtype=torch.float32),positions=None,is_global=True)
                    if not body.instantaneous_wrench_composer.active or not body.permanent_wrench_composer.active:
                        raise ValueError('Dirty-wrench reset control not established')
                    body.reset()
                    if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:
                        raise ValueError('Reset did not clear wrench queues')
                    body.write_root_pose_to_sim_index(root_pose=torch.tensor([r['initial']['pose']],dtype=torch.float32))
                    body.write_root_com_velocity_to_sim_index(root_velocity=torch.tensor([r['initial']['velocity']],dtype=torch.float32))
                    body.write_data_to_sim()
                    flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD
                    for state in (fixture['sin'],fixture['sout']):
                        old_q=state.body_q.numpy().tolist();old_qd=state.body_qd.numpy().tolist()
                        solver.reset(state,flags=flags);state.clear_forces()
                        if state.body_q.numpy().tolist()!=old_q or state.body_qd.numpy().tolist()!=old_qd:
                            raise ValueError('Newton reset mutated externally owned rigid state')
                        if state.particle_q.numpy().tolist()[0]!=r['initial']['p'] or state.particle_qd.numpy().tolist()[0]!=r['initial']['vp']:
                            raise ValueError('Particle defaults not restored')
                    fixture['pipeline'].reset_contact_matching()
                    fixture['contacts'].clear()
                    if int(fixture['contacts'].soft_contact_count.numpy()[0])!=0:raise ValueError('Old contact prefix not invalidated')
                    echo(body,(fixture['sin'],fixture['sout']))
                    restored=physx_state(body)
                    if restored['pose']!=r['initial']['pose'] or restored['velocity']!=r['initial']['velocity']:
                        raise ValueError('Rigid starting state not restored exactly')
                    reset_records.append(dict(episode=episode,id=r['id'],source_contact_count=previous_count,
                        queues_dirty_before_reset=True,queues_clear_after_reset=True,particle_defaults_exact=True,
                        rigid_defaults_exact=True,external_rigid_state_preserved_by_newton_reset=True,
                        fresh_contacts_required=True,same_models_solvers_and_pipeline=True))
                    dirty_resets+=1
                    fixture['reference_state']=copy.deepcopy(r['initial']);fixture['total_impulse']=[0.]*3
                    fixture['total_angular_impulse']=[0.]*3;fixture['seen_contact']=fixture['seen_clear']=False
                    r['steps']=[];r['coast_steps']=0
                reset_cycles+=1
            for interval in range(episode_length):
                if (out/'stop.request').exists():raise InterruptedError('Stopped between turning exchanges')
                write(out,'worker_status.json',dict(stage='turning_exchange',interval=interval,newton_steps=ns,physx_steps=ps))
                for fixture in fixtures:
                    body=fixture['body'];model=fixture['model'];sin=fixture['sin'];sout=fixture['sout'];r=fixture['record']
                    initial=echo(body,(sin,sout));contacts=fixture['contacts'];solver=fixture['solver']
                    before=dict(pose=initial['pose'],velocity=initial['velocity'],p=sin.particle_q.numpy().tolist()[0],vp=sin.particle_qd.numpy().tolist()[0])
                    args=(r['com_local'],r['particle_mass_kg'],r['body_mass_kg'],INERTIA,1750.,r['height_m'],DT)
                    expected=reference_step(before,*args)
                    fixture['pipeline'].collide(sin,contacts);wp.synchronize()
                    count=int(contacts.soft_contact_count.numpy()[0])
                    if count!=int(expected['signed_depth_m']>0.):raise ValueError('Fresh collision count disagrees with finite top-face reference')
                    arrays={field:getattr(contacts,field).numpy()[:count].tolist() for field in
                        ('soft_contact_indices','soft_contact_barycentric','soft_contact_shape','soft_contact_body_pos','soft_contact_normal')}
                    if count and math.dist(arrays['soft_contact_normal'][0],expected['normal'])>1e-6:
                        raise ValueError('Collision normal disagrees with updated body orientation')
                    solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
                    if sout.body_q.numpy().tolist()[0]!=initial['pose'] or sout.body_qd.numpy().tolist()[0]!=initial['velocity']:
                        raise ValueError('Newton advanced externally owned rigid body')
                    reaction=collect_reaction(model,sout,sin,contacts,solver) if count else None
                    force=reaction['force'][0] if count else [0.]*3;wrench=reaction['wrench'][0] if count else [0.]*6
                    force_error=math.dist(force,expected['force']);torque_error=math.dist(wrench[3:],expected['wrench'][3:])
                    point_error=math.dist(reaction['rigid_point'][0],expected['point']) if count else 0.
                    if force_error>2e-5 or torque_error>2e-7 or point_error>1e-7:raise ValueError('Updated contact force/point/COM torque mismatch')
                    if count:
                        if reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.:raise ValueError('Unexpected solver material')
                        if fixture['seen_clear']:raise ValueError('Contact unexpectedly reappeared')
                        fixture['seen_contact']=True
                        body.instantaneous_wrench_composer.set_forces_and_torques_index(
                            forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),positions=None,is_global=True)
                    else:
                        if not fixture['seen_contact']:raise ValueError('Fixture never made contact')
                        fixture['seen_clear']=True;r['coast_steps']+=1
                        if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Stale queued wrench')
                    body.write_data_to_sim()
                    if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Composer failed to clear')
                    r['steps'].append(dict(interval=interval,before=before,contact_count=count,contact_arrays=arrays,
                        native_contact=reaction,force_n=force,wrench=wrench,expected=expected,
                        force_error_n=force_error,torque_error_nm=torque_error,point_error_m=point_error,
                        particle_after=sout.particle_q.numpy().tolist()[0],particle_velocity_after=sout.particle_qd.numpy().tolist()[0],
                        no_new_wrench_submitted=count==0))
                write(out,'turning_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
                if (out/'stop.request').exists():raise InterruptedError('Stopped before PhysX exchange')
                sim.step(render=False);ps+=1
                for fixture in fixtures:
                    body=fixture['body'];r=fixture['record'];s=r['steps'][-1];body.update(DT)
                    final=echo(body,(fixture['sin'],fixture['sout']));s['state_echo_exact']=True
                    after=dict(pose=final['pose'],velocity=final['velocity'],p=s['particle_after'],vp=s['particle_velocity_after']);s['after']=after
                    write(out,'turning_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
                    expected=s['expected']['after'];before=s['before'];mp=r['particle_mass_kg'];mass=r['body_mass_kg'];com=r['com_local']
                    s['pulse_check']=check_pulse(before['velocity'],after['velocity'],s['wrench'][:3],s['wrench'][3:],mass,INERTIA,DT)
                    if not s['contact_count']:s['coast_check']=check_coast(before['velocity'],after['velocity'])
                    pe=max(math.dist(after['p'],expected['p']),math.dist(world_point(after['pose'],com),world_point(expected['pose'],com)))
                    ve=math.dist(after['vp'],expected['vp']);qe=math.hypot(*rotation_vector(expected['pose'][3:],after['pose'][3:]))
                    args=(com,mp,mass,INERTIA,1750.,r['height_m'],DT)
                    trajectory=reference_step(fixture['reference_state'],*args)['after'];fixture['reference_state']=trajectory
                    tpe=max(math.dist(after['p'],trajectory['p']),math.dist(world_point(after['pose'],com),world_point(trajectory['pose'],com)))
                    tve=math.dist(after['vp'],trajectory['vp']);twe=math.dist(after['velocity'][3:],trajectory['velocity'][3:])
                    tqe=math.hypot(*rotation_vector(trajectory['pose'][3:],after['pose'][3:]))
                    for j in range(3):
                        fixture['total_impulse'][j]+=DT*s['force_n'][j]
                        fixture['total_angular_impulse'][j]+=DT*s['wrench'][j+3]
                    impulse_error=max(math.dist([mp*(after['vp'][j]-r['initial']['vp'][j]) for j in range(3)],fixture['total_impulse']),
                        math.dist([mass*(after['velocity'][j]-r['initial']['velocity'][j]) for j in range(3)],[-x for x in fixture['total_impulse']]))
                    angular_impulse_error=math.dist([INERTIA*(after['velocity'][j+3]-r['initial']['velocity'][j+3]) for j in range(3)],fixture['total_angular_impulse'])
                    # Angular momentum increments include the finite TGS translation/force splitting term.
                    c0=world_point(before['pose'],com);c1=world_point(after['pose'],com)
                    def angular(state,center):
                        lp=cross([state['p'][j]-c0[j] for j in range(3)],[mp*x for x in state['vp']])
                        lb=cross([center[j]-c0[j] for j in range(3)],[mass*x for x in state['velocity'][:3]])
                        return [lp[j]+lb[j]+INERTIA*state['velocity'][j+3] for j in range(3)]
                    old_l=angular(before,c0);new_l=angular(after,c1)
                    jp=[DT*x for x in s['force_n']];jb=[-x for x in jp]
                    point=s['native_contact']['rigid_point'][0] if s['contact_count'] else before['p']
                    defect_p=cross([before['p'][j]-point[j] for j in range(3)],jp)
                    defect_b=cross(before['velocity'][:3],jb)
                    expected_defect=[defect_p[j]+DT*15/32*defect_b[j] for j in range(3)]
                    angular_balance_error=math.dist([new_l[j]-old_l[j] for j in range(3)],expected_defect)
                    if pe>1e-7 or ve>2e-5 or qe>1e-6 or tpe>1e-7 or tve>2e-5 or twe>2e-6 or tqe>1e-6 or impulse_error>2e-7 or angular_impulse_error>2e-8 or angular_balance_error>2e-8:
                        raise ValueError(f'Turning motion/impulse mismatch: {pe=}, {ve=}, {qe=}, {tpe=}, {tve=}, {twe=}, {tqe=}, {impulse_error=}, {angular_balance_error=}')
                    s['motion_checks']=dict(position_error_m=pe,particle_velocity_error_m_s=ve,rotation_error_rad=qe,
                        trajectory_position_error_m=tpe,trajectory_particle_velocity_error_m_s=tve,
                        trajectory_angular_velocity_error_rad_s=twe,trajectory_rotation_error_rad=tqe,
                        cumulative_linear_impulse_error_ns=impulse_error,cumulative_angular_impulse_error_nms=angular_impulse_error,
                        angular_balance_error_kg_m2_s=angular_balance_error,expected_angular_split_increment=expected_defect)
                    fixture['sin'],fixture['sout']=fixture['sout'],fixture['sin']
                write(out,'turning_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
            episodes.append(copy.deepcopy(cases))
            if episode:
                for initial_case,replay_case in zip(episodes[0],episodes[-1]):
                    comparisons.append(dict(episode=episode,id=replay_case['id'],
                        assessment=compare_traces(initial_case['steps'],replay_case['steps'])))
            write(out,'reset_replay_partial.json',dict(episodes=episodes,reset_records=reset_records,comparisons=comparisons,
                newton_steps=ns,physx_steps=ps))
        for r in cases:
            normals=[s['expected']['normal'] for s in r['steps'] if s['contact_count']]
            r['active_contact_normal_change']=max(math.dist(n,normals[0]) for n in normals)
            if r['active_contact_normal_change']<1e-5 or r['coast_steps']<3:raise ValueError('Insufficient rotation or contact clearing exercised')
        normals_updated=True
        if ns!=68 or ps!=34 or int(sim._physics_step_count)!=baseline+34 or reset_cycles!=2 or len(comparisons)!=4 or dirty_resets!=4:raise ValueError('Unexpected step count')
        write(out,'reset_replay_measurements.json',dict(episodes=episodes,reset_records=reset_records,comparisons=comparisons,cases=cases,newton_steps=ns,physx_steps=ps,dt_s=DT,
            baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),normals_updated=True,
            scope='Baseline 16 intervals, reset/replay 2 intervals, active-contact reset/replay 16 intervals. Same solver and buffers. No material, robot, anisotropic-inertia or blade qualification.'))
        passed=True
    except BaseException:
        write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
    finally:
        try:
            if sim is not None:sim.stop();sim_utils.SimulationContext.clear_instance()
            write(out,'worker_result.json',result())
            if app is not None:app.close(exit_code=0 if passed else 1)
        except BaseException:
            passed=False;write(out,'close_failure.json',dict(traceback=traceback.format_exc()))
        write(out,'worker_result.json',result())
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
