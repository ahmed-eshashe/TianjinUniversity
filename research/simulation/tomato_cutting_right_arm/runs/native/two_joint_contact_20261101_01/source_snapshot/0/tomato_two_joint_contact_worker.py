"""Actual Newton particle contact driving two passive CPU PhysX joints."""
import argparse,hashlib,math,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_two_joint_reference import check
from tomato_two_joint_contact_reference import expected_response
from tomato_hinge_contact_reference import expected_contact
from tomato_offset_contact_reference import world_point
from tomato_half_step_reaction import collect_reaction
from tomato_wrench_contract import cross
ROOT=Path(__file__).resolve().parents[1]
DT=1/2400


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;steps=echoes=ns=clears=0;cases=[]
    def stop(signum,frame):raise InterruptedError('Hinge interface diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
        shutdown_completion='supervisor_must_observe_exit',two_joint_contact_checks_passed=passed,two_joint_contact_cases_completed=len(cases),
        controlled_steps=steps,cuda_state_echoes=echoes,newton_steps=ns,clear_controls_passed=clears,robot_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_two_joint_reference.py',ROOT/'rl/tomato_two_joint_contact_reference.py',ROOT/'rl/tomato_hinge_contact_reference.py',ROOT/'rl/tomato_half_step_reaction.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,controlled_step_cap=2,newton_step_cap=4,dt_s=DT,
            scope='Two passive two-joint chains driven by actual Newton particle contact; one interval plus explicit outside-particle clear control. No robot/blade.'))
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
            contacts=pipeline.contacts();pipeline.collide(sin,contacts);wp.synchronize()
            if int(contacts.soft_contact_count.numpy()[0])!=1:raise ValueError('One actual generated contact required')
            mp=float(model.particle_mass.numpy()[0]);width=float(model.shape_scale.numpy()[shape][1]);particle=sin.particle_q.numpy().tolist()[0]
            reference=expected_contact(before['link_pose'],particle,mp,width,1750.,DT)
            if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge Newton step')
            solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
            if sout.body_q.numpy().tolist()[0]!=before['link_pose'] or sout.body_qd.numpy().tolist()[0]!=before['link_com_velocity']:
                raise ValueError('Newton moved externally owned hinge proxy')
            reaction=collect_reaction(model,sout,sin,contacts,solver)
            if reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.:raise ValueError('Unexpected actual contact material')
            force=reaction['force'][0];point=reaction['rigid_point'][0];wrench=reaction['wrench'][0]
            force_error=math.dist(force,reference['force']);point_error=math.dist(point,reference['point']);torque_error=math.dist(wrench[3:],reference['wrench'][3:])
            if force_error>2e-5 or point_error>1e-7 or torque_error>2e-7:raise ValueError('Native hinge contact/reference mismatch')
            expected=expected_response(i*math.pi/2,reference['wrench'],DT)
            matrix=asset.data.mass_matrix.torch.cpu().tolist()[0]
            jac=asset.data.body_com_jacobian_w.torch.cpu().tolist()[0][link-1]
            asset.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),
                torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),positions=None,body_ids=[link],is_global=True)
            asset.write_data_to_sim()
            if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Contact wrench queue did not clear')
            record=dict(id='hinge_contact_identity' if i==0 else 'hinge_contact_yaw90',link_index=link,before=before,
                particle_before=particle,particle_after=sout.particle_q.numpy().tolist()[0],particle_velocity_after=sout.particle_qd.numpy().tolist()[0],
                particle_mass_kg=mp,native_contact=reaction,reference=reference,expected=expected,mass_matrix_kg_m2=matrix,jacobian=jac,
                force_error_n=force_error,point_error_m=point_error,torque_error_nm=torque_error,
                contact_arrays={field:getattr(contacts,field).numpy()[:1].tolist() for field in
                    ('soft_contact_indices','soft_contact_barycentric','soft_contact_shape','soft_contact_body_pos','soft_contact_normal')})
            cases.append(record);fixtures.append(dict(asset=asset,link=link,model=model,sin=sin,sout=sout,solver=solver,pipeline=pipeline,contacts=contacts,record=record))
        write(out,'hinge_contact_before_pulse.json',dict(cases=cases))
        if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge reaction step')
        sim.step(render=False);steps+=1
        for f in fixtures:
            asset=f['asset'];r=f['record'];asset.update(DT);r['after_pulse']=echo(asset,f['link'],(f['sin'],f['sout']))
            write(out,'hinge_contact_partial.json',dict(cases=cases,controlled_steps=steps,newton_steps=ns))
            r['pulse_check']=check(r['expected'],r['mass_matrix_kg_m2'],r['jacobian'],r['after_pulse']['joint_position'],r['after_pulse']['joint_velocity'])
            mp=r['particle_mass_kg'];vp=r['particle_velocity_after'];force=r['native_contact']['force'][0]
            impulse_error=math.dist([mp*v for v in vp],[DT*v for v in force])
            position_error=math.dist(r['particle_after'],r['reference']['particle_after'])
            particle_lz=cross(r['particle_after'],[mp*v for v in vp])[2]
            angular_balance=abs(particle_lz+sum(m*v for m,v in zip(r['mass_matrix_kg_m2'][0],r['after_pulse']['joint_velocity'])))
            if impulse_error>2e-7 or position_error>1e-7 or angular_balance>2e-8:raise ValueError('Particle/hinge impulse balance mismatch')
            r['balance_checks']=dict(particle_impulse_error_ns=impulse_error,particle_position_error_m=position_error,
                hinge_axis_angular_momentum_error_nms=angular_balance)
        write(out,'hinge_contact_after_pulse.json',dict(cases=cases))
        for f in fixtures:
            if (out/'stop.request').exists():raise InterruptedError('Stopped before explicit clear control')
            r=f['record'];sin=f['sout'];sout=f['sin'];model=f['model'];contacts=f['contacts']
            clear_p=world_point(r['after_pulse']['link_pose'],[.004,.008,0.])
            for state in (sin,sout):
                state.particle_q.assign(wp.array([clear_p],dtype=wp.vec3,device='cuda:0'));state.particle_qd.zero_();state.clear_forces()
            f['pipeline'].collide(sin,contacts);wp.synchronize()
            if int(contacts.soft_contact_count.numpy()[0])!=0:raise ValueError('Explicit outside-particle control did not clear contacts')
            f['solver'].step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
            if math.hypot(*sout.particle_qd.numpy().tolist()[0])>1e-7:raise ValueError('Cleared particle acquired velocity')
            asset=f['asset']
            if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Stale hinge contact wrench')
            asset.write_data_to_sim()
            r['clear_control']=dict(particle_repositioned_explicitly=True,position_world=clear_p,velocity_reset_explicitly=True,
                regenerated_contact_count=0,new_wrench_submitted=False,particle_velocity_after=sout.particle_qd.numpy().tolist()[0])
        if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge clear-control step')
        sim.step(render=False);steps+=1
        for f in fixtures:
            asset=f['asset'];r=f['record'];asset.update(DT);r['after_coast']=echo(asset,f['link'],(f['sin'],f['sout']))
            drift=max(abs(a-b) for a,b in zip(r['after_coast']['joint_velocity'],r['after_pulse']['joint_velocity']))
            if drift>2e-6:raise ValueError('Stale reaction after explicit contact clearing')
            r['coast_joint_velocity_change_rad_s']=drift;clears+=1
        if steps!=2 or ns!=4 or echoes!=6 or clears!=2 or int(sim._physics_step_count)!=baseline+2:raise ValueError('Unexpected controlled counts')
        write(out,'hinge_contact_measurements.json',dict(cases=cases,controlled_steps=steps,newton_steps=ns,cuda_state_echoes=echoes,dt_s=DT,
            baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),newton_contact_connected=True,
            scope='One contact exchange and explicit outside-particle clear control per passive two-joint chain. Natural separation and repeated multi-joint contact remain unvalidated.'))
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
