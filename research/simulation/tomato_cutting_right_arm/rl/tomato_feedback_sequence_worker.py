"""Sixteen repeated contact exchanges plus simultaneous clear control, no robot/blade."""
import argparse
import hashlib
import math
from pathlib import Path
import signal
import traceback
from tomato_isaac_startup_worker import write
from tomato_contact_feedback_worker import collect_reaction
from tomato_feedback_sequence_reference import reference,assess
ROOT=Path(__file__).resolve().parents[1]
DT=1/1200
INTERVALS=16


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;ns=ps=0;coast=0;cases=[]
    def stop(signum,frame):raise InterruptedError('Repeated contact feedback stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():
        return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
            shutdown_completion='supervisor_must_observe_exit',sequence_cases_completed=len(cases),
            newton_steps=ns,physx_steps=ps,cleared_contact_coast_steps=coast,sequence_checks_passed=passed,
            robot_validated=False,blade_validated=False,training=False,long_run_stability_validated=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [Path(__file__),ROOT/'rl/tomato_feedback_sequence_reference.py',ROOT/'rl/tomato_contact_feedback_worker.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,newton_step_cap=32,physx_step_cap=16,dt_s=DT,
            scope='Two persistent analytic particle/box fixtures; one starts in contact and separates naturally, one starts clear. Same solver/contact buffers reused; fresh collisions every interval. Zero gravity/damping/friction, COM offsets zero.'))
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
        bodies=[]
        for i in range(2):
            spawn=sim_utils.CuboidCfg(size=(.02,.02,.004),
                rigid_props=[sim_utils.UsdPhysicsRigidBodyCfg(kinematic_enabled=False),
                    PhysxRigidBodyCfg(linear_damping=0.,angular_damping=0.,disable_gravity=True,
                                     sleep_threshold=0.,stabilization_threshold=0.,solver_position_iteration_count=16,solver_velocity_iteration_count=0)],
                collision_props=sim_utils.UsdPhysicsCollisionCfg(collision_enabled=False),
                mass_props=sim_utils.MassCfg(mass=.02,density=0.))
            bodies.append(RigidObject(RigidObjectCfg(prim_path=f'/World/FeedbackProxy{i}',spawn=spawn,
                init_state=RigidObjectCfg.InitialStateCfg(pos=(float(i),0.,0.),rot=(0.,0.,0.,1.)))))
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
        for i,(body,z) in enumerate(zip(bodies,(.001,.003))):
            if (out/'stop.request').exists():raise InterruptedError('Stopped before Newton fixture')
            body.reset()
            body.set_coms_index(coms=torch.tensor([[[0.,0.,0.,0.,0.,0.,1.]]],dtype=torch.float32))
            body.set_inertias_index(inertias=torch.tensor([[[.001,0.,0.,0.,.001,0.,0.,0.,.001]]],dtype=torch.float32))
            body.write_root_com_velocity_to_sim_index(root_velocity=torch.zeros((1,6),dtype=torch.float32))
            builder=newton.ModelBuilder(gravity=(0.,0.,0.))
            builder.add_particle(wp.vec3(float(i),0.,z),wp.vec3(0.),.01,radius=0.)
            proxy=builder.add_body(xform=wp.transform(wp.vec3(float(i),0.,0.),wp.quat_identity()),is_kinematic=True)
            shape=builder.add_shape_box(proxy,hx=.01,hy=.01,hz=.002,
                cfg=newton.ModelBuilder.ShapeConfig(density=12500.,ke=2500.,kd=0.,mu=0.,margin=0.,gap=0.))
            builder.color();model=builder.finalize(device='cuda:0')
            model.soft_contact_ke=1000.;model.soft_contact_kd=0.;model.soft_contact_mu=0.
            if math.dist(model.body_com.numpy().tolist()[0],[0.,0.,0.])>1e-9:raise ValueError('Zero COM fixture required')
            sin=model.state();sout=model.state();initial=echo(body,(sin,sout))
            solver=newton.solvers.SolverVBD(model,iterations=16,rigid_compliant_alm=True,
                integrate_with_external_rigid_solver=True,rigid_avbd_beta=0.)
            if solver.rigid_contact_k_start_value!=-1.:raise ValueError('Fixed contact penalty required')
            pipeline=newton.CollisionPipeline(model,broad_phase='nxn',soft_contact_gap=0.,soft_contact_max=8,
                rigid_contact_max=8,enable_rigid_soft_full_surface_contact=True)
            contacts=pipeline.contacts()
            before=dict(particle_z=float(sin.particle_q.numpy()[0,2]),body_z=initial['pose'][2],
                particle_vz=float(sin.particle_qd.numpy()[0,2]),body_vz=initial['velocity'][2])
            record=dict(id='contact_then_coast' if i==0 else 'clear_control',initial=before,
                particle_mass_kg=float(model.particle_mass.numpy()[0]),body_mass_kg=float(body.data.body_mass.torch[0,0]),
                half_height_m=float(model.shape_scale.numpy()[shape][2]),steps=[])
            cases.append(record)
            fixtures.append(dict(body=body,model=model,sin=sin,sout=sout,solver=solver,pipeline=pipeline,
                contacts=contacts,record=record,reference_state=before.copy(),total_impulse=0.))
        seen_contact=False;seen_clear=False
        for interval in range(INTERVALS):
            if (out/'stop.request').exists():raise InterruptedError('Stopped between exchanges')
            write(out,'worker_status.json',dict(stage='coupled_exchange',interval=interval,newton_steps=ns,physx_steps=ps))
            for fixture in fixtures:
                body=fixture['body'];model=fixture['model'];sin=fixture['sin'];sout=fixture['sout']
                solver=fixture['solver'];contacts=fixture['contacts'];r=fixture['record']
                initial=echo(body,(sin,sout))
                before=dict(particle_z=float(sin.particle_q.numpy()[0,2]),body_z=initial['pose'][2],
                    particle_vz=float(sin.particle_qd.numpy()[0,2]),body_vz=initial['velocity'][2])
                fixture['pipeline'].collide(sin,contacts);wp.synchronize()
                count=int(contacts.soft_contact_count.numpy()[0])
                if count not in (0,1):raise ValueError('Unexpected active contact count')
                depth=r['half_height_m']+before['body_z']-before['particle_z']
                if count!=int(depth>0.):raise ValueError('Fresh collision count inconsistent with head-on geometry')
                solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
                if sout.body_q.numpy().tolist()[0]!=initial['pose'] or sout.body_qd.numpy().tolist()[0]!=initial['velocity']:
                    raise ValueError('Newton moved PhysX-owned proxy')
                if int(contacts.soft_contact_count.numpy()[0])!=count:raise ValueError('Contact stream changed during solve')
                reaction=collect_reaction(model,sout,sin,contacts,solver) if count else None
                if count and (reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.):
                    raise ValueError('Unexpected actual solver contact material')
                soft_force=reaction['force'][0] if count else [0.]*3
                wrench=reaction['wrench'][0] if count else [0.]*6
                if any(abs(v)>1e-7 for v in [*soft_force[:2],*wrench[:2],*wrench[3:]]):raise ValueError('Unexpected transverse wrench')
                if count==0:
                    # No new wrench queued: backend must clear the previously applied force.
                    if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:
                        raise ValueError('Stale wrench composer remained active')
                else:
                    body.instantaneous_wrench_composer.set_forces_and_torques_index(
                        forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),
                        positions=None,is_global=True)
                body.write_data_to_sim()
                if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:
                    raise ValueError('Wrench delivery did not clear')
                step=dict(interval=interval,before=before,contact_count=count,soft_force_n=soft_force,
                    world_com_wrench=wrench,soft_q=sout.particle_q.numpy().tolist()[0],
                    soft_qd=sout.particle_qd.numpy().tolist()[0],reaction_collection=reaction,
                    no_new_wrench_submitted=count==0,proxy_frozen_during_soft_solve=True)
                r['steps'].append(step)
            write(out,'sequence_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
            if (out/'stop.request').exists():raise InterruptedError('Stopped before PhysX interval')
            sim.step(render=False);ps+=1
            for i,fixture in enumerate(fixtures):
                body=fixture['body'];r=fixture['record'];step=r['steps'][-1]
                body.update(DT);final=echo(body,(fixture['sin'],fixture['sout']))
                after=dict(particle_z=step['soft_q'][2],body_z=final['pose'][2],
                    particle_vz=step['soft_qd'][2],body_vz=final['velocity'][2])
                step['after']=after;step['final_physx']=final;step['state_echo_exact']=True
                write(out,'sequence_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
                args=(r['particle_mass_kg'],r['body_mass_kg'],1750.,r['half_height_m'],DT)
                step['assessment']=assess(step['before'],after,*args,step['soft_force_n'][2])
                predicted=reference(fixture['reference_state'],*args)
                fixture['reference_state']={n:v for n,v in predicted.items() if n!='force_n'}
                trajectory_pe=max(abs(after[n]-predicted[n]) for n in ('particle_z','body_z'))
                trajectory_ve=max(abs(after[n]-predicted[n]) for n in ('particle_vz','body_vz'))
                if trajectory_pe>1e-7 or trajectory_ve>2e-5:raise ValueError('Accumulated trajectory reference mismatch')
                fixture['total_impulse']+=DT*step['soft_force_n'][2]
                mp=r['particle_mass_kg'];mb=r['body_mass_kg'];start=r['initial']
                cumulative_impulse_error=max(abs(mp*(after['particle_vz']-start['particle_vz'])-fixture['total_impulse']),
                    abs(mb*(after['body_vz']-start['body_vz'])+fixture['total_impulse']))
                if cumulative_impulse_error>2e-7:raise ValueError('Accumulated impulse mismatch')
                step.update(trajectory_position_error_m=trajectory_pe,trajectory_velocity_error_m_s=trajectory_ve,
                    cumulative_impulse_error_kg_m_s=cumulative_impulse_error,total_contact_impulse_ns=fixture['total_impulse'])
                if any(abs(v)>1e-7 for v in [*step['soft_qd'][:2],*final['velocity'][:2],*final['velocity'][3:]]):
                    raise ValueError('Unexpected off-axis motion')
                if i==0:
                    if step['contact_count']>0:
                        if seen_clear:raise ValueError('Unexpected contact reappearance')
                        seen_contact=True
                    elif seen_contact:
                        seen_clear=True;coast+=1
                        if step['soft_force_n']!=[0.,0.,0.] or not step['no_new_wrench_submitted']:
                            raise ValueError('Stale reaction on cleared contact')
                elif step['contact_count']!=0 or step['soft_force_n']!=[0.,0.,0.]:raise ValueError('Clear fixture generated a force')
                fixture['sin'],fixture['sout']=fixture['sout'],fixture['sin']
            write(out,'sequence_partial.json',dict(cases=cases,newton_steps=ns,physx_steps=ps,cleared_contact_coast_steps=coast))
        if ns!=32 or ps!=16 or int(sim._physics_step_count)!=baseline+16 or coast<3:
            raise ValueError('Controlled sequence count or contact clearing check failed')
        write(out,'feedback_sequence_measurements.json',dict(cases=cases,newton_steps=ns,physx_steps=ps,
            cleared_contact_coast_steps=coast,dt_s=DT,total_simulated_time_s=INTERVALS*DT,
            physx_tgs_position_substeps=16,baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),
            physics_backend=sim.physics_manager.__module__,physical_energy_conservation_expected=False,
            scope='16 intervals, reused states/solvers/contact buffers, fresh collisions. Head-on analytic particle/box only; no rotation/nonzero COM contact or robot/blade/reset qualification.'))
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
