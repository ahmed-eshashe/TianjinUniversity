"""Two initially resting unequal-inertia contact impulse fixtures."""
import argparse,hashlib,math,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_contact_feedback_worker import collect_reaction
from tomato_offset_contact_reference import world_point,expected_contact,validate_wrench,rotation_vector
from tomato_anisotropic_reference import apply_inertia,assess_rest_pulse
from tomato_wrench_contract import cross,dot
ROOT=Path(__file__).resolve().parents[1]
DT=1/1200
PRINCIPAL=[.0001,.0002,.00025]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;ns=ps=0;cases=[]
    def stop(signum,frame):raise InterruptedError('Off-centre contact check stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():
        return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
            shutdown_completion='supervisor_must_observe_exit',anisotropic_cases_completed=len(cases),
            newton_steps=ns,physx_steps=ps,anisotropic_checks_passed=passed,world_tensor_exercised=passed,
            robot_validated=False,blade_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [Path(__file__),ROOT/'rl/tomato_offset_contact_reference.py',ROOT/'rl/tomato_anisotropic_reference.py',ROOT/'rl/tomato_contact_feedback_worker.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,newton_step_cap=2,physx_step_cap=1,dt_s=DT,
            scope='Two initially stationary off-centre analytic contacts. Second body obliquely rotated about (1,2,3), with nonzero local COM and unequal principal inertia. Initially at rest; one bounded interval.'))
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
            dict(pose=[0.,.05,0.,.5/math.sqrt(14),1./math.sqrt(14),1.5/math.sqrt(14),math.sqrt(.75)],com=[.002,-.001,.0005])]
        bodies=[]
        for i in range(2):
            spawn=sim_utils.CuboidCfg(size=(.02,.02,.004),
                rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),
                    PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,enable_gyroscopic_forces=True,
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
            if not api.GetEnableGyroscopicForcesAttr().Get():raise ValueError('Gyroscopic force setting must be enabled')
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
            body.set_inertias_index(inertias=torch.tensor([[[PRINCIPAL[0],0.,0.,0.,PRINCIPAL[1],0.,0.,0.,PRINCIPAL[2]]]],dtype=torch.float32))
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32))
            initial=physx_state(body)
            actual_com=body.data.body_com_pose_b.torch.cpu().tolist()[0][0][:3]
            if math.dist(actual_com,local_com)>1e-8:raise ValueError('PhysX COM offset mismatch')
            mp=.01;mass=float(body.data.body_mass.torch[0,0]);inertia=body.data.body_inertia.torch[0,0].cpu().tolist()
            if any(abs(inertia[j]-(PRINCIPAL[j//4] if j in (0,4,8) else 0.))>1e-9 for j in range(9)):
                raise ValueError('Explicit unequal principal inertia required')
            principal=[inertia[0],inertia[4],inertia[8]]
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            point=world_point(initial['pose'],[.004,.003,.001])
            builder.add_particle(wp.vec3(*point),wp.vec3(0.),mp,radius=0.)
            proxy=builder.add_body(xform=wp.transform(wp.vec3(*initial['pose'][:3]),wp.quat(*initial['pose'][3:])),
                com=wp.vec3(*actual_com),mass=mass,inertia=wp.mat33(PRINCIPAL[0],0.,0.,0.,PRINCIPAL[1],0.,0.,0.,PRINCIPAL[2]),
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
            contacts=pipeline.contacts();pipeline.collide(sin,contacts);wp.synchronize()
            if int(contacts.soft_contact_count.numpy()[0])!=1:raise ValueError('Exactly one generated contact required')
            particle_before=sin.particle_q.numpy().tolist()[0];mp=float(model.particle_mass.numpy()[0])
            height=float(model.shape_scale.numpy()[shape][2])
            expected=expected_contact(initial['pose'],actual_com,particle_before,mp,1750.,height,DT)
            write(out,'worker_status.json',dict(stage='offset_contact_soft_step',case=i,newton_steps=ns,physx_steps=ps))
            solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
            if sout.body_q.numpy().tolist()[0]!=initial['pose'] or sout.body_qd.numpy().tolist()[0]!=initial['velocity']:
                raise ValueError('Newton advanced externally owned rigid state')
            reaction=collect_reaction(model,sout,sin,contacts,solver)
            if reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.:raise ValueError('Unexpected native material')
            force=reaction['force'][0];wrench=reaction['wrench'][0]
            check=validate_wrench(expected,force,reaction['rigid_point'][0],wrench)
            if math.hypot(*wrench[3:])<.001:raise ValueError('Nontrivial contact torque required')
            body.instantaneous_wrench_composer.set_forces_and_torques_index(
                forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),
                positions=None,is_global=True)
            body.write_data_to_sim()
            if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:
                raise ValueError('Unexpected retained wrench')
            record=dict(id='identity_anisotropic' if i==0 else 'oblique_anisotropic_offset_com',initial_physx=initial,
                com_local=actual_com,particle_before=particle_before,particle_after=sout.particle_q.numpy().tolist()[0],
                particle_velocity_after=sout.particle_qd.numpy().tolist()[0],particle_mass_kg=mp,body_mass_kg=mass,
                principal_inertia_kg_m2=principal,gyroscopic_forces_enabled=True,expected=expected,native_contact=reaction,wrench_check=check,
                contact_arrays={field:getattr(contacts,field).numpy()[:1].tolist() for field in
                    ('soft_contact_indices','soft_contact_barycentric','soft_contact_shape','soft_contact_body_pos','soft_contact_normal')})
            fixtures.append((body,sin,sout));cases.append(record)
        write(out,'offset_before_physx_step.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
        if (out/'stop.request').exists():raise InterruptedError('Stopped before offset PhysX step')
        sim.step(render=False);ps+=1
        for (body,sin,sout),r in zip(fixtures,cases):
            body.update(DT);final=echo(body,(sin,sout));r['final_physx']=final;r['state_echo_exact']=True
            write(out,r['id']+'_before_final_checks.json',r)
            wrench=r['native_contact']['wrench'][0];force=r['native_contact']['force'][0]
            mp=r['particle_mass_kg'];mass=r['body_mass_kg'];velocity=final['velocity'];vp=r['particle_velocity_after']
            principal=r['principal_inertia_kg_m2']
            r['pulse_check']=assess_rest_pulse(r['initial_physx']['pose'],final['pose'],velocity,wrench[:3],wrench[3:],mass,principal,DT)
            particle_expected=[DT*f/mp for f in r['expected']['soft_force']]
            particle_velocity_error=math.dist(vp,particle_expected)
            particle_position_error=math.dist(r['particle_after'],r['expected']['particle_after'])
            momentum=[mp*vp[j]+mass*velocity[j] for j in range(3)]
            impulse_error=math.dist([mp*v for v in vp],[DT*f for f in force])
            c0=r['expected']['com_world'];c1=world_point(final['pose'],r['com_local'])
            body_expected_com=[c0[j]+DT*DT*wrench[j]/mass*17/32 for j in range(3)]
            com_error=math.dist(c1,body_expected_com)
            angle=rotation_vector(r['initial_physx']['pose'][3:],final['pose'][3:])
            if math.hypot(*angle)>1e-3:raise ValueError('Initial-tensor reference requires small one-interval rotation')
            expected_angle=[DT*w*17/32 for w in r['pulse_check']['initial_tensor_expected_angular_velocity']]
            angle_error=math.dist(angle,expected_angle)
            orbital_p=cross([p-c for p,c in zip(r['particle_after'],c0)],[mp*v for v in vp])
            orbital_b=cross([c-cstart for c,cstart in zip(c1,c0)],[mass*v for v in velocity[:3]])
            spin=r['pulse_check']['final_world_spin']
            angular_balance=[orbital_p[j]+orbital_b[j]+spin[j] for j in range(3)]
            body_work=dot(wrench[:3],[c-cstart for c,cstart in zip(c1,c0)])+dot(wrench[3:],angle)
            body_ke=.5*mass*dot(velocity[:3],velocity[:3])+.5*dot(velocity[3:],spin)
            body_loss=body_ke/16
            work_error=abs(body_ke-body_work+body_loss)
            if (particle_velocity_error>2e-5 or particle_position_error>1e-7 or math.hypot(*momentum)>2e-7
                or impulse_error>2e-7 or com_error>1e-7 or angle_error>1e-6
                or math.hypot(*angular_balance)>2e-8 or work_error>2e-8):
                raise ValueError(f'Offset motion/balance mismatch: {particle_velocity_error=}, {com_error=}, {angle_error=}, {angular_balance=}, {work_error=}')
            r['motion_checks']=dict(particle_velocity_error_m_s=particle_velocity_error,particle_position_error_m=particle_position_error,
                linear_momentum_error_kg_m_s=math.hypot(*momentum),particle_impulse_error_ns=impulse_error,
                com_position_error_m=com_error,world_rotation_increment_rad=angle,expected_rotation_increment_rad=expected_angle,
                rotation_error_rad=angle_error,total_angular_momentum_error_kg_m2_s=math.hypot(*angular_balance),
                body_work_j=body_work,body_kinetic_energy_j=body_ke,tgs_numerical_loss_j=body_loss,body_work_identity_error_j=work_error)
        oblique=cases[1];tau=oblique['native_contact']['wrench'][0][3:];principal=oblique['principal_inertia_kg_m2']
        wrong=[DT*tau[j]/principal[j] for j in range(3)]
        correct=oblique['pulse_check']['initial_tensor_expected_angular_velocity']
        oblique['wrong_world_axes_velocity_difference_rad_s']=math.dist(wrong,correct)
        if math.dist(wrong,correct)<1e-3:raise ValueError('Oblique world tensor not meaningfully exercised')
        if ns!=2 or ps!=1 or int(sim._physics_step_count)!=baseline+1:raise ValueError('Unexpected step count')
        write(out,'anisotropic_contact_measurements.json',dict(cases=cases,newton_steps=ns,physx_steps=ps,dt_s=DT,
            baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),
            scope='Two initially resting off-centre analytic contacts with unequal body-axis principal inertia. Initial world-tensor small-rotation impulse reference; no general anisotropic spin, long-run, articulation or blade qualification.'))
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
