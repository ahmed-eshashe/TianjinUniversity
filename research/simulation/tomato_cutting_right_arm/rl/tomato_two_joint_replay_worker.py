"""Thirty-two actual Newton–PhysX passive-hinge exchanges with natural separation."""
import argparse,hashlib,math,signal,traceback,copy
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_two_joint_sequence_reference import step as reference_step,dynamics,geometry
from tomato_offset_contact_reference import world_point
from tomato_half_step_reaction import collect_reaction
from tomato_wrench_contract import cross
from tomato_two_joint_replay_reference import compare
ROOT=Path(__file__).resolve().parents[1]
DT=1/2400


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;steps=echoes=ns=0;cases=[];reset_cycles=dirty_resets=0;episodes=[];comparisons=[];reset_records=[]
    def stop(signum,frame):raise InterruptedError('Hinge interface diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
        shutdown_completion='supervisor_must_observe_exit',two_joint_replay_checks_passed=passed,two_joint_replay_cases_completed=len(cases),
        controlled_steps=steps,cuda_state_echoes=echoes,newton_steps=ns,min_coast_steps=min((r['coast_steps'] for r in cases),default=0),natural_separation=passed,reset_cycles_completed=reset_cycles,dirty_wrench_resets=dirty_resets,replay_comparisons=len(comparisons),robot_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_two_joint_sequence_reference.py',ROOT/'rl/tomato_two_joint_replay_reference.py',ROOT/'rl/tomato_half_step_reaction.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,controlled_step_cap=66,newton_step_cap=132,dt_s=DT,
            scope='Two passive two-joint chains: baseline 32 steps, reset/replay 2 steps, active-contact reset/replay 32 steps. No robot/blade.'))
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cpu',visualizer=['none']);app=launcher.app
        import torch,warp as wp
        import newton
        import newton.solvers
        from pxr import UsdGeom,UsdPhysics,PhysxSchema,Gf
        import isaaclab.sim as sim_utils
        from isaaclab.assets import Articulation,ArticulationCfg
        from isaaclab_physx.physics import PhysxCfg
        wp.init();wp.set_device('cuda:0')
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=DT,gravity=(0.,0.,0.),
            physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
        stage=sim.stage;assets=[]
        for i,angle in enumerate((0.,math.pi/2)):
            path=f'/World/Hinge{i}';root=UsdGeom.Xform.Define(stage,path)
            rotation=Gf.Quatf(math.cos(angle/2),Gf.Vec3f(0.,0.,math.sin(angle/2)))
            root.AddOrientOp().Set(rotation)
            for name,x,mass in (('base',0.,.01),('link1',.01,.02),('link2',.03,.02)):
                body_prim=UsdGeom.Xform.Define(stage,path+'/'+name)
                body_prim.AddTranslateOp().Set(Gf.Vec3d(x,0.,0.))
                cube=UsdGeom.Cube.Define(stage,path+'/'+name+'/visual');cube.CreateSizeAttr(1.)
                cube.AddScaleOp().Set(Gf.Vec3f(.02,.01,.004))
                prim=body_prim.GetPrim();UsdPhysics.RigidBodyAPI.Apply(prim)
                props=PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
                props.CreateDisableGravityAttr(True);props.CreateLinearDampingAttr(0.);props.CreateAngularDampingAttr(0.)
                props.CreateSleepThresholdAttr(0.);props.CreateStabilizationThresholdAttr(0.)
                mass_api=UsdPhysics.MassAPI.Apply(prim);mass_api.CreateMassAttr(mass)
                mass_api.CreateCenterOfMassAttr(Gf.Vec3f(0.));mass_api.CreateDiagonalInertiaAttr(Gf.Vec3f(.0001))
                mass_api.CreatePrincipalAxesAttr(Gf.Quatf(1.))
            anchor=UsdPhysics.FixedJoint.Define(stage,path+'/anchor');anchor.CreateBody1Rel().SetTargets([path+'/base'])
            anchor.CreateLocalRot0Attr(rotation)
            UsdPhysics.ArticulationRootAPI.Apply(anchor.GetPrim())
            articulation_api=PhysxSchema.PhysxArticulationAPI.Apply(anchor.GetPrim())
            articulation_api.CreateSolverPositionIterationCountAttr(16);articulation_api.CreateSolverVelocityIterationCountAttr(0)
            articulation_api.CreateEnabledSelfCollisionsAttr(False)
            for name,parent,child,pivot in (('hinge1','base','link1',0.),('hinge2','link1','link2',.01)):
                joint=UsdPhysics.RevoluteJoint.Define(stage,path+'/'+name)
                joint.CreateBody0Rel().SetTargets([path+'/'+parent]);joint.CreateBody1Rel().SetTargets([path+'/'+child])
                joint.CreateAxisAttr('Z');joint.CreateLocalPos0Attr(Gf.Vec3f(pivot,0.,0.));joint.CreateLocalPos1Attr(Gf.Vec3f(-.01,0.,0.))
                joint.CreateLocalRot0Attr(Gf.Quatf(1.));joint.CreateLocalRot1Attr(Gf.Quatf(1.))
                PhysxSchema.PhysxJointAPI.Apply(joint.GetPrim()).CreateJointFrictionAttr(0.)
            assets.append(Articulation(ArticulationCfg(prim_path=path,spawn=None,actuators={},
                init_state=ArticulationCfg.InitialStateCfg(rot=(0.,0.,math.sin(angle/2),math.cos(angle/2))))))
        stage.GetRootLayer().Export(str(out/'synthetic_hinges.usda'))
        sim.reset();baseline=int(sim._physics_step_count)
        if 'isaaclab_physx' not in sim.physics_manager.__module__:raise ValueError('Expected CPU PhysX articulation')
        def snapshot(asset,link):return dict(joint_position=asset.data.joint_pos.torch.cpu().tolist()[0],
            joint_velocity=asset.data.joint_vel.torch.cpu().tolist()[0],link_pose=asset.data.body_link_pose_w.torch.cpu().tolist()[0][link],
            link_com_velocity=asset.data.body_com_vel_w.torch.cpu().tolist()[0][link])
        def echo(asset,link,states):
            nonlocal echoes
            packet=snapshot(asset,link)
            pose=wp.array([packet['link_pose']],dtype=wp.transform,device='cpu')
            vel=wp.array([packet['link_com_velocity']],dtype=wp.spatial_vector,device='cpu')
            for state in states:
                wp.copy(state.body_q,pose);wp.copy(state.body_qd,vel)
            wp.synchronize()
            if any(state.body_q.numpy().tolist()[0]!=packet['link_pose'] or state.body_qd.numpy().tolist()[0]!=packet['link_com_velocity'] for state in states):
                raise ValueError('Actual Newton link-state echo mismatch')
            echoes+=1;return packet
        fixtures=[]
        write(out,'hinge_topology.json',dict(assets=[dict(fixed_base=a.is_fixed_base,num_joints=a.num_joints,num_bodies=a.num_bodies,body_names=a.body_names,joint_names=a.joint_names) for a in assets]))
        for i,asset in enumerate(assets):
            if not asset.is_fixed_base or asset.num_joints!=2 or asset.num_bodies!=3:raise ValueError('Expected one passive joint and fixed base')
            link=asset.body_names.index('link2');asset.reset()
            asset.write_joint_stiffness_to_sim_index(stiffness=0.)
            asset.write_joint_damping_to_sim_index(damping=0.)
            asset.write_joint_friction_coefficient_to_sim_index(joint_friction_coeff=torch.zeros((1,2),dtype=torch.float32),joint_dynamic_friction_coeff=torch.zeros((1,2),dtype=torch.float32),joint_viscous_friction_coeff=torch.zeros((1,2),dtype=torch.float32))
            asset.write_joint_state_to_sim_index(position=torch.zeros((1,2)),velocity=torch.zeros((1,2)))
            before=snapshot(asset,link)
            if max(abs(x) for x in before['joint_position']+before['joint_velocity'])>1e-7:raise ValueError('Hinge not initially at rest')
            if asset.joint_names!=['hinge1','hinge2']:raise ValueError('Unexpected joint order')
            mass=float(asset.data.body_mass.torch[0,link]);inertia=float(asset.data.body_inertia.torch[0,link,8])
            local_com=asset.data.body_com_pose_b.torch.cpu().tolist()[0][link][:3]
            if math.hypot(*local_com)>1e-9:raise ValueError('Zero COM-local offset required in this hinge fixture')
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            p=world_point(before['link_pose'],[.004,.004,0.])
            builder.add_particle(wp.vec3(*p),wp.vec3(0.),.01,radius=0.)
            pose=before['link_pose'];proxy=builder.add_body(xform=wp.transform(wp.vec3(*pose[:3]),wp.quat(*pose[3:])),
                com=wp.vec3(0.),mass=mass,inertia=wp.mat33(.0001,0.,0.,0.,.0001,0.,0.,0.,.0001),lock_inertia=True,is_kinematic=True)
            shape=builder.add_shape_box(proxy,hx=.01,hy=.005,hz=.002,
                cfg=newton.ModelBuilder.ShapeConfig(density=0.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.))
            builder.color();model=builder.finalize(device='cuda:0');model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
            sin=model.state();sout=model.state();before=echo(asset,link,(sin,sout))
            solver=newton.solvers.SolverVBD(model,iterations=16,rigid_compliant_alm=True,integrate_with_external_rigid_solver=True,rigid_avbd_beta=0.)
            if solver.rigid_contact_k_start_value!=-1.:raise ValueError('Fixed contact penalty required')
            pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=8,rigid_contact_max=8,
                enable_rigid_soft_full_surface_contact=True)
            contacts=pipeline.contacts();mp=float(model.particle_mass.numpy()[0]);width=float(model.shape_scale.numpy()[shape][1])
            matrix=asset.data.mass_matrix.torch.cpu().tolist()[0];expected_matrix=dynamics([0.,0.],[0.,0.],[0.,0.])[0]
            if max(abs(matrix[a][b]-expected_matrix[a][b]) for a in range(2) for b in range(2))>1e-8:raise ValueError('Coupled mass matrix mismatch')
            initial=dict(q=before['joint_position'],qd=before['joint_velocity'],p=sin.particle_q.numpy().tolist()[0],vp=sin.particle_qd.numpy().tolist()[0])
            record=dict(id='hinge_sequence_identity' if i==0 else 'hinge_sequence_yaw90',link_index=link,yaw=i*math.pi/2,
                initial=initial,initial_link_packet=copy.deepcopy(before),particle_mass_kg=mp,effective_inertia_kg_m2=matrix,half_width_m=width,
                coast_steps=0,contact_steps=0,steps=[])
            cases.append(record);fixtures.append(dict(asset=asset,link=link,model=model,sin=sin,sout=sout,solver=solver,
                pipeline=pipeline,contacts=contacts,record=record,reference_state=initial.copy(),total_effort_impulse=0.,
                total_particle_impulse=[0.]*3,seen_contact=False,seen_clear=False))
        for episode,episode_length in enumerate((32,2,32)):
            if episode:
                if (out/'stop.request').exists():raise InterruptedError('Stopped before jointed reset')
                for f in fixtures:
                    asset=f['asset'];r=f['record'];link=f['link']
                    source_count=int(f['contacts'].soft_contact_count.numpy()[0])
                    if source_count!=(0 if episode==1 else 1):raise ValueError('Must reset once after coast and once during contact')
                    for composer in (asset.instantaneous_wrench_composer,asset.permanent_wrench_composer):
                        composer.set_forces_and_torques_index(forces=torch.tensor([[[99.,-55.,33.]]],dtype=torch.float32),
                            torques=torch.tensor([[[1.,2.,3.]]],dtype=torch.float32),positions=None,body_ids=[link],is_global=True)
                    if not asset.instantaneous_wrench_composer.active or not asset.permanent_wrench_composer.active:
                        raise ValueError('Dirty queue control not established')
                    asset.reset()
                    if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Articulation reset left queued force')
                    asset.write_joint_state_to_sim_index(position=torch.tensor([r['initial']['q']],dtype=torch.float32),
                        velocity=torch.tensor([r['initial']['qd']],dtype=torch.float32))
                    asset.write_data_to_sim()
                    flags=newton.StateFlags.PARTICLE_Q|newton.StateFlags.PARTICLE_QD
                    for state in (f['sin'],f['sout']):
                        old_pose=state.body_q.numpy().tolist();old_velocity=state.body_qd.numpy().tolist()
                        f['solver'].reset(state,flags=flags);state.clear_forces()
                        if state.body_q.numpy().tolist()!=old_pose or state.body_qd.numpy().tolist()!=old_velocity:
                            raise ValueError('Newton reset changed externally owned link state')
                        if state.particle_q.numpy().tolist()[0]!=r['initial']['p'] or state.particle_qd.numpy().tolist()[0]!=r['initial']['vp']:
                            raise ValueError('Particle state not restored exactly')
                    f['pipeline'].reset_contact_matching();f['contacts'].clear()
                    if int(f['contacts'].soft_contact_count.numpy()[0])!=0:raise ValueError('Old active contact prefix survived reset')
                    packet=echo(asset,link,(f['sin'],f['sout']))
                    if packet['joint_position']!=r['initial']['q'] or packet['joint_velocity']!=r['initial']['qd']:
                        raise ValueError('Joint initial state not restored exactly')
                    original=r['initial_link_packet']
                    if math.dist(packet['link_pose'],original['link_pose'])>1e-7 or math.dist(packet['link_com_velocity'],original['link_com_velocity'])>1e-7:
                        raise ValueError('Link initial packet not restored')
                    reset_records.append(dict(episode=episode,id=r['id'],source_contact_count=source_count,
                        joint_defaults_exact=True,particle_defaults_exact=True,link_packet_error=math.dist(packet['link_pose'],original['link_pose']),
                        queues_dirty_before_reset=True,queues_clear_after_reset=True,external_link_state_preserved_by_newton_reset=True,
                        contact_prefix_invalidated=True,same_models_solvers_and_pipeline=True))
                    dirty_resets+=1
                    f['reference_state']=copy.deepcopy(r['initial']);f['total_effort_impulse']=0.;f['total_particle_impulse']=[0.]*3
                    f['seen_contact']=f['seen_clear']=False;r['steps']=[];r['coast_steps']=r['contact_steps']=0
                reset_cycles+=1
            for interval in range(episode_length):
                if (out/'stop.request').exists():raise InterruptedError('Stopped between hinge exchanges')
                write(out,'worker_status.json',dict(stage='hinge_sequence',interval=interval,controlled_steps=steps,newton_steps=ns))
                for f in fixtures:
                    asset=f['asset'];r=f['record'];sin=f['sin'];sout=f['sout'];contacts=f['contacts'];model=f['model']
                    packet=snapshot(asset,f['link'])
                    if any(state.body_q.numpy().tolist()[0]!=packet['link_pose'] or state.body_qd.numpy().tolist()[0]!=packet['link_com_velocity'] for state in (sin,sout)):
                        raise ValueError('Newton proxy not synchronized from prior PhysX step')
                    before=dict(q=packet['joint_position'],qd=packet['joint_velocity'],p=sin.particle_q.numpy().tolist()[0],vp=sin.particle_qd.numpy().tolist()[0])
                    args=(r['yaw'],r['particle_mass_kg'],r['half_width_m'],1750.,DT)
                    ref=reference_step(before,*args,pose=packet['link_pose'])
                    f['pipeline'].collide(sin,contacts);wp.synchronize();count=int(contacts.soft_contact_count.numpy()[0])
                    if count!=int(ref['signed_depth_m']>0.):raise ValueError('Fresh hinge collision count mismatch')
                    arrays={field:getattr(contacts,field).numpy()[:count].tolist() for field in
                        ('soft_contact_indices','soft_contact_barycentric','soft_contact_shape','soft_contact_body_pos','soft_contact_normal')}
                    if count and math.dist(arrays['soft_contact_normal'][0],ref['normal'])>1e-6:raise ValueError('Stale contact normal')
                    f['solver'].step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
                    if sout.body_q.numpy().tolist()[0]!=packet['link_pose'] or sout.body_qd.numpy().tolist()[0]!=packet['link_com_velocity']:
                        raise ValueError('Newton advanced externally owned jointed link')
                    reaction=collect_reaction(model,sout,sin,contacts,f['solver']) if count else None
                    force=reaction['force'][0] if count else [0.]*3;wrench=reaction['wrench'][0] if count else [0.]*6
                    force_error=math.dist(force,ref['force']);torque_error=math.dist(wrench[3:],ref['wrench'][3:])
                    point_error=math.dist(reaction['rigid_point'][0],ref['point']) if count else 0.
                    if force_error>2e-5 or torque_error>2e-7 or point_error>1e-7:raise ValueError('Hinge contact/reference mismatch')
                    if count:
                        if f['seen_clear']:raise ValueError('Unexpected contact reappearance')
                        if reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.:raise ValueError('Unexpected cached material')
                        f['seen_contact']=True;r['contact_steps']+=1
                        asset.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),
                            torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),positions=None,body_ids=[f['link']],is_global=True)
                    else:
                        if not f['seen_contact']:raise ValueError('Missing contact phase')
                        f['seen_clear']=True;r['coast_steps']+=1
                        if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Stale queued hinge wrench')
                    asset.write_data_to_sim()
                    if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Queue not cleared')
                    moment=cross(packet['link_pose'][:3],wrench[:3])[2]+wrench[5]
                    r['steps'].append(dict(interval=interval,before=before,reference=ref,contact_count=count,contact_arrays=arrays,
                        native_contact=reaction,force_n=force,wrench=wrench,effort_nm=ref['effort_nm'],
                        force_error_n=force_error,torque_error_nm=torque_error,point_error_m=point_error,
                        particle_after=sout.particle_q.numpy().tolist()[0],particle_velocity_after=sout.particle_qd.numpy().tolist()[0],
                        no_new_wrench_submitted=count==0))
                write(out,'hinge_sequence_partial.json',dict(cases=cases,controlled_steps=steps,newton_steps=ns))
                if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge PhysX interval')
                sim.step(render=False);steps+=1
                for f in fixtures:
                    asset=f['asset'];r=f['record'];s=r['steps'][-1];asset.update(DT)
                    packet=echo(asset,f['link'],(f['sin'],f['sout']))
                    after=dict(q=packet['joint_position'],qd=packet['joint_velocity'],p=s['particle_after'],vp=s['particle_velocity_after'])
                    s['after']=after;s['after_link_packet']=packet;s['state_echo_exact']=True
                    write(out,'hinge_sequence_partial.json',dict(cases=cases,controlled_steps=steps,newton_steps=ns))
                    mp=r['particle_mass_kg'];inertia=r['effective_inertia_kg_m2'];ref=s['reference']['after'];before=s['before']
                    qe=max(abs(a-b) for a,b in zip(after['q'],ref['q']));qve=max(abs(a-b) for a,b in zip(after['qd'],ref['qd']));pe=math.dist(after['p'],ref['p']);ve=math.dist(after['vp'],ref['vp'])
                    args=(r['yaw'],mp,r['half_width_m'],1750.,DT)
                    trajectory=reference_step(f['reference_state'],*args)['after'];f['reference_state']=trajectory
                    tqe=max(abs(a-b) for a,b in zip(after['q'],trajectory['q']));tqve=max(abs(a-b) for a,b in zip(after['qd'],trajectory['qd']))
                    tpe=math.dist(after['p'],trajectory['p']);tve=math.dist(after['vp'],trajectory['vp'])
                    for j in range(3):f['total_particle_impulse'][j]+=DT*s['force_n'][j]
                    matrix,bias,_=dynamics(before['q'],before['qd'],[0.,0.])
                    joint_impulse_error=max(abs(sum(matrix[i][j]*(after['qd'][j]-before['qd'][j]) for j in range(2))+DT*bias[i]-DT*s['effort_nm'][i]) for i in range(2))
                    particle_impulse_error=math.dist([mp*(after['vp'][j]-r['initial']['vp'][j]) for j in range(3)],f['total_particle_impulse'])
                    total_lz=cross(after['p'],[mp*v for v in after['vp']])[2]+sum(m*v for m,v in zip(dynamics(after['q'],after['qd'],[0.,0.])[0][0],after['qd']))
                    original_lz=cross(r['initial']['p'],[mp*v for v in r['initial']['vp']])[2]+sum(m*v for m,v in zip(dynamics(r['initial']['q'],r['initial']['qd'],[0.,0.])[0][0],r['initial']['qd']))
                    balance_error=abs(total_lz-original_lz)
                    coast_drift=qve if s['contact_count']==0 else 0.
                    if qe>1e-6 or qve>2e-5 or pe>1e-7 or ve>2e-5 or tqe>1e-6 or tqve>2e-5 or tpe>1e-7 or tve>2e-5 or joint_impulse_error>2e-8 or particle_impulse_error>2e-7 or balance_error>2e-8 or coast_drift>2e-6:
                        raise ValueError(f'Hinge sequence mismatch: {qe=}, {qve=}, {tqe=}, {tqve=}, {tpe=}, {tve=}, {joint_impulse_error=}, {balance_error=}, {coast_drift=}')
                    s['checks']=dict(joint_position_error_rad=qe,joint_velocity_error_rad_s=qve,particle_position_error_m=pe,particle_velocity_error_m_s=ve,
                        trajectory_joint_position_error_rad=tqe,trajectory_joint_velocity_error_rad_s=tqve,trajectory_particle_position_error_m=tpe,
                        trajectory_particle_velocity_error_m_s=tve,interval_generalized_impulse_error_nms=joint_impulse_error,
                        cumulative_particle_impulse_error_ns=particle_impulse_error,hinge_axis_angular_balance_error_nms=balance_error,
                        coast_joint_velocity_reference_error_rad_s=coast_drift)
                    f['sin'],f['sout']=f['sout'],f['sin']
                write(out,'hinge_sequence_partial.json',dict(cases=cases,controlled_steps=steps,newton_steps=ns))
            episodes.append(copy.deepcopy(cases))
            if episode:
                for initial_case,replay_case in zip(episodes[0],episodes[-1]):
                    comparisons.append(dict(episode=episode,id=replay_case['id'],assessment=compare(initial_case['steps'],replay_case['steps'])))
            write(out,'hinge_replay_partial.json',dict(episodes=episodes,comparisons=comparisons,reset_records=reset_records,
                controlled_steps=steps,newton_steps=ns))
        for r in cases:
            normals=[s['reference']['normal'] for s in r['steps'] if s['contact_count']]
            r['active_normal_change']=max(math.dist(n,normals[0]) for n in normals)
            if r['coast_steps']<3 or r['active_normal_change']<1e-5:raise ValueError('Insufficient separation/turning coverage')
        if steps!=66 or ns!=132 or echoes!=138 or int(sim._physics_step_count)!=baseline+66 or reset_cycles!=2 or dirty_resets!=4 or len(comparisons)!=4:raise ValueError('Unexpected controlled counts')
        write(out,'two_joint_replay_measurements.json',dict(episodes=episodes,comparisons=comparisons,reset_records=reset_records,cases=cases,controlled_steps=steps,newton_steps=ns,cuda_state_echoes=echoes,dt_s=DT,
            baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),natural_separation=True,
            scope='Two-joint reset and replay after coast and during contact; persistent models, solvers and buffers. No multi-joint robot, general work/energy or real-blade qualification.'))
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
