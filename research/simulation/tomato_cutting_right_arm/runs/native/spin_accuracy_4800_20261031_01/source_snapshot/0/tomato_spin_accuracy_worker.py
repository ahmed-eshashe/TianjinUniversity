"""Fixed-factor full-duration spin accuracy audit, with preserved per-sample failures."""
import argparse,hashlib,math,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_spin_reference import advance,rotate,body_vector,invariants
from tomato_offset_contact_reference import world_point,rotation_vector
ROOT=Path(__file__).resolve().parents[1]
DT=1/1200
PRINCIPAL=[.0001,.0002,.00025]
from tomato_spin_accuracy_audit import LIMITS,violations


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--refinement',type=int,choices=(1,2,4),required=True)
    args=parser.parse_args();out=args.output;factor=args.refinement;dt=DT/factor;cap=16*factor;app=sim=None;passed=False;steps=echoes=0;cases=[];distinguished=False;accuracy=False
    def stop(signum,frame):raise InterruptedError('Spin/coast diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
        shutdown_completion='supervisor_must_observe_exit',spin_cases_completed=len(cases),physx_steps=steps,
        newton_steps=0,cuda_state_echoes=echoes,gyro_control_distinguished=distinguished,physical_accuracy_passed=accuracy,
        audit_cases_completed=len(cases),audit_measurements_completed=passed,refinement=factor,
        robot_validated=False,blade_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),ROOT/'rl/tomato_spin_reference.py',ROOT/'rl/tomato_spin_accuracy_audit.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,physx_step_cap=cap,newton_step_cap=0,dt_s=dt,refinement=factor,
            limits=LIMITS,scope='Torque-free unequal-inertia free spin; two gyro-enabled bodies plus one disabled control. CPU PhysX owns all motion. CUDA Newton state echoes only.'))
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cpu',visualizer=['none']);app=launcher.app
        import torch
        import warp as wp
        import newton
        import isaaclab.sim as sim_utils
        from isaaclab.assets import RigidObject,RigidObjectCfg
        from isaaclab_physx.physics import PhysxCfg
        from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg
        from pxr import PhysxSchema
        wp.init();wp.set_device('cuda:0')
        sim=sim_utils.SimulationContext(sim_utils.SimulationCfg(device='cpu',dt=dt,gravity=(0.,0.,0.),
            physics=PhysxCfg(solver_type=1,enable_external_forces_every_iteration=True),use_fabric=False,use_newton_actuators=False,log_dir=str(out)))
        oblique=[.5/math.sqrt(14),1./math.sqrt(14),1.5/math.sqrt(14),math.sqrt(.75)]
        descriptions=[dict(id='identity_gyro',q=[0.,0.,0.,1.],com=[0.]*3,gyro=True),
            dict(id='oblique_offset_gyro',q=oblique,com=[.002,-.001,.0005],gyro=True),
            dict(id='oblique_offset_no_gyro_control',q=oblique,com=[.002,-.001,.0005],gyro=False)]
        bodies=[]
        for i,d in enumerate(descriptions):
            spawn=sim_utils.CuboidCfg(size=(.02,.02,.004),rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),
                PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,enable_gyroscopic_forces=d['gyro'],
                sleep_threshold=0.,stabilization_threshold=0.,solver_position_iteration_count=16,solver_velocity_iteration_count=0)],
                collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),mass_props=sim_utils.MassCfg(mass=.02,density=0.))
            bodies.append(RigidObject(RigidObjectCfg(prim_path=f'/World/SpinProxy{i}',spawn=spawn,
                init_state=RigidObjectCfg.InitialStateCfg(pos=(0.,.05*i,0.),rot=tuple(d['q'])))))
        sim.reset();baseline=int(sim._physics_step_count)
        if 'isaaclab_physx' not in sim.physics_manager.__module__:raise ValueError('CPU PhysX required')
        scene=PhysxSchema.PhysxSceneAPI(sim.stage.GetPrimAtPath('/physicsScene'))
        if str(scene.GetSolverTypeAttr().Get())!='TGS' or not scene.GetEnableExternalForcesEveryIterationAttr().Get():raise ValueError('Expected TGS force schedule')
        def state(body):return dict(pose=body.data.root_link_pose_w.torch.cpu().tolist()[0],velocity=body.data.root_com_vel_w.torch.cpu().tolist()[0])
        fixtures=[]
        for i,(body,d) in enumerate(zip(bodies,descriptions)):
            api=PhysxSchema.PhysxRigidBodyAPI(sim.stage.GetPrimAtPath(f'/World/SpinProxy{i}'))
            if bool(api.GetEnableGyroscopicForcesAttr().Get())!=d['gyro'] or api.GetSolverPositionIterationCountAttr().Get()!=16 or api.GetSolverVelocityIterationCountAttr().Get()!=0:
                raise ValueError('Spin settings readback mismatch')
            body.reset();body.set_coms_index(coms=torch.tensor([[d['com']+[0.,0.,0.,1.]]],dtype=torch.float32))
            body.set_inertias_index(inertias=torch.tensor([[[PRINCIPAL[0],0.,0.,0.,PRINCIPAL[1],0.,0.,0.,PRINCIPAL[2]]]],dtype=torch.float32))
            pose=state(body)['pose'];world_spin=rotate(pose[3:],[1.,2.,3.])
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.tensor([[.02,-.01,.03]+world_spin],dtype=torch.float32))
            initial=state(body);com=body.data.body_com_pose_b.torch.cpu().tolist()[0][0][:3]
            matrix=body.data.body_inertia.torch[0,0].cpu().tolist();principal=[matrix[0],matrix[4],matrix[8]]
            if math.dist(principal,PRINCIPAL)>1e-10 or math.dist(com,d['com'])>1e-8:raise ValueError('Inertia/COM mismatch')
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            builder.add_body(xform=wp.transform(wp.vec3(*pose[:3]),wp.quat(*pose[3:])),com=wp.vec3(*com),mass=.02,
                inertia=wp.mat33(*matrix),lock_inertia=True,is_kinematic=True)
            model=builder.finalize(device='cuda:0');proxy=model.state()
            r=dict(id=d['id'],gyro_enabled=d['gyro'],initial=initial,com_local=com,principal=principal,
                initial_com_api_world=body.data.root_com_pose_w.torch.cpu().tolist()[0][:3],
                initial_invariants=invariants(pose[3:],initial['velocity'][3:],principal),steps=[])
            cases.append(r);fixtures.append(dict(body=body,proxy=proxy,record=r,
                reference_q=pose[3:],reference_wbody=body_vector(pose[3:],initial['velocity'][3:])))
        write(out,'spin_initial.json',dict(cases=cases,limits=LIMITS))
        for interval in range(cap):
            if (out/'stop.request').exists():raise InterruptedError('Stopped between coast steps')
            write(out,'worker_status.json',dict(stage='torque_free_coast',interval=interval,physx_steps=steps))
            for fixture in fixtures:
                body=fixture['body']
                if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Coast has an active force queue')
                body.write_data_to_sim()
            sim.step(render=False);steps+=1
            for fixture in fixtures:
                body=fixture['body'];r=fixture['record'];body.update(dt);measured=state(body)
                if not all(math.isfinite(v) for v in measured['pose']+measured['velocity']):raise ValueError('Nonfinite native spin state')
                proxy=fixture['proxy'];wp.copy(proxy.body_q,body.data.root_link_pose_w.warp);wp.copy(proxy.body_qd,body.data.root_com_vel_w.warp);wp.synchronize()
                if proxy.body_q.numpy().tolist()[0]!=measured['pose'] or proxy.body_qd.numpy().tolist()[0]!=measured['velocity']:raise ValueError('CUDA Newton state echo mismatch')
                echoes+=1
                ref=advance(fixture['reference_q'],fixture['reference_wbody'],r['principal'],dt)
                fixture['reference_q']=ref['q'];fixture['reference_wbody']=ref['wbody']
                actual=invariants(measured['pose'][3:],measured['velocity'][3:],r['principal']);original=r['initial_invariants']
                momentum_drift=math.dist(actual['angular_momentum'],original['angular_momentum'])/math.hypot(*original['angular_momentum'])
                energy_drift=abs(actual['energy']-original['energy'])/original['energy']
                omega_error=math.dist(measured['velocity'][3:],ref['omega_world'])
                rotation_error=math.hypot(*rotation_vector(ref['q'],measured['pose'][3:]))
                linear_error=math.dist(measured['velocity'][:3],r['initial']['velocity'][:3])
                initial_com=world_point(r['initial']['pose'],r['com_local']);actual_com=world_point(measured['pose'],r['com_local'])
                expected_com=[initial_com[j]+steps*dt*r['initial']['velocity'][j] for j in range(3)]
                com_error=math.dist(actual_com,expected_com)
                api_com=body.data.root_com_pose_w.torch.cpu().tolist()[0][:3]
                api_expected=[r['initial_com_api_world'][j]+steps*dt*r['initial']['velocity'][j] for j in range(3)]
                api_error=math.dist(api_com,api_expected)
                if not all(math.isfinite(v) for v in api_com):raise ValueError('Nonfinite COM API output')
                sample=dict(interval=interval,measured=measured,continuous_reference=ref,invariants=actual,
                    angular_velocity_error_rad_s=omega_error,rotation_error_rad=rotation_error,
                    relative_angular_momentum_drift=momentum_drift,relative_energy_drift=energy_drift,
                    linear_velocity_error_m_s=linear_error,com_position_error_m=com_error,cuda_echo_exact=True,no_input_wrench=True,
                    reconstructed_com_world=actual_com,expected_com_world=expected_com,api_com_world=api_com,
                    api_com_error_m=api_error,api_vs_host_com_difference_m=math.dist(api_com,actual_com))
                sample['accuracy_violations']=violations(sample,r['gyro_enabled'])
                sample['api_com_accuracy_passed']=api_error<=LIMITS['com_position_m']
                r['steps'].append(sample);write(out,'spin_partial.json',dict(cases=cases,physx_steps=steps,cuda_state_echoes=echoes))
        enabled=cases[1]['steps'][-1];disabled=cases[2]['steps'][-1]
        distinguished=disabled['angular_velocity_error_rad_s']>.001 and disabled['angular_velocity_error_rad_s']>10*enabled['angular_velocity_error_rad_s']
        for r in cases[:2]:
            change=math.dist(r['steps'][-1]['measured']['velocity'][3:],r['initial']['velocity'][3:]);r['world_spin_change_rad_s']=change
            if change<.001:raise ValueError('Gyroscopic precession not meaningfully exercised')
        accuracy=all(not sample['accuracy_violations'] and sample['api_com_accuracy_passed'] for r in cases for sample in r['steps'])
        if steps!=cap or echoes!=3*cap or int(sim._physics_step_count)!=baseline+cap:raise ValueError('Unexpected step/echo count')
        write(out,'spin_accuracy_measurements.json',dict(cases=cases,limits=LIMITS,physx_steps=steps,newton_steps=0,cuda_state_echoes=echoes,
            dt_s=dt,refinement=factor,total_simulated_time_s=cap*dt,physical_accuracy_passed=accuracy,baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),
            gyro_control_distinguished=distinguished,
            com_api_provenance='IsaacLab root_com_pose_w is reconstructed via get_root_com_pose_from_root_link_pose, not independent engine COM telemetry.',scope='Short torque-free CPU PhysX unequal-inertia spin. CUDA Newton state transfer only; no Newton contact or solver step in this check.'))
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
