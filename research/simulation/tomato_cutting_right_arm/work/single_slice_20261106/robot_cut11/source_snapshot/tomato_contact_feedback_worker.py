"""One contact and one clear fixture: CUDA Newton soft step then CPU PhysX reaction step."""
import argparse
import hashlib
import math
from pathlib import Path
import signal
import traceback
from tomato_isaac_startup_worker import write
from tomato_partitioned_reference import assess

ROOT=Path(__file__).resolve().parents[1]
DT=1/1200

def collect_reaction(model, state, state_in, contacts, solver):
    import warp as wp
    from newton._src.solvers.vbd.rigid_vbd_kernels import _eval_soft_ef_contact
    count = int(contacts.soft_contact_count.numpy()[0])
    if not 0 < count < contacts.soft_contact_max:
        raise ValueError('Nonempty unsaturated contact stream required')
    ke=solver.body_particle_contact_penalty_k
    kd=solver.body_particle_contact_material_kd
    mu=solver.body_particle_contact_material_mu
    previous_particle=solver.particle_q_prev
    previous_body=state_in.body_q

    @wp.kernel(enable_backward=False)
    def evaluate(pos: wp.array[wp.vec3], previous_pos: wp.array[wp.vec3], radius: wp.array[float],
                 body_q: wp.array[wp.transform], body_prev: wp.array[wp.transform],
                 body_qd: wp.array[wp.spatial_vector], body_com: wp.array[wp.vec3],
                 shape_body: wp.array[int], corners: wp.array[wp.vec3i], bary: wp.array[wp.vec3],
                 shapes: wp.array[int], points: wp.array[wp.vec3], velocities: wp.array[wp.vec3],
                 normals: wp.array[wp.vec3], margins: wp.array[float], k: wp.array[float],
                 damping: wp.array[float], friction: wp.array[float], eps: float, dt: float,
                 force: wp.array[wp.vec3], hessian: wp.array[wp.mat33], rigid_point: wp.array[wp.vec3],
                 body_wrench: wp.array[wp.spatial_vector]):
        i = wp.tid()
        f, h, point = _eval_soft_ef_contact(i, corners[i], bary[i], pos, previous_pos, radius,
            k[i], damping[i], friction[i], eps, shape_body, body_q, body_prev, body_qd, body_com,
            shapes, points, velocities, normals, margins, dt)
        body = shape_body[shapes[i]]
        com = wp.transform_point(body_q[body], body_com[body])
        reaction = -f
        force[i] = f; hessian[i] = h; rigid_point[i] = point
        body_wrench[i] = wp.spatial_vector(reaction, wp.cross(point-com, reaction))

    force = wp.zeros(count, dtype=wp.vec3); hessian = wp.zeros(count, dtype=wp.mat33)
    point = wp.zeros(count, dtype=wp.vec3); wrench = wp.zeros(count, dtype=wp.spatial_vector)
    wp.launch(evaluate, dim=count, inputs=[state.particle_q, previous_particle, model.particle_radius,
        state.body_q, previous_body, state.body_qd, model.body_com, model.shape_body,
        contacts.soft_contact_indices, contacts.soft_contact_barycentric, contacts.soft_contact_shape,
        contacts.soft_contact_body_pos, contacts.soft_contact_body_vel, contacts.soft_contact_normal,
        model.shape_margin, ke, kd, mu, solver.friction_epsilon, 1/1200],
        outputs=[force, hessian, point, wrench], device=model.device)
    wp.synchronize()
    return {'ke': ke.numpy().tolist(), 'kd': kd.numpy().tolist(), 'mu': mu.numpy().tolist(),
             'force': force.numpy().tolist(),
            'hessian': hessian.numpy().tolist(), 'rigid_point': point.numpy().tolist(), 'wrench': wrench.numpy().tolist()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;ns=ps=0;cases=[]
    def stop(signum,frame):raise InterruptedError('Contact feedback diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():
        return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
            shutdown_completion='supervisor_must_observe_exit',feedback_cases_completed=len(cases),
            newton_steps=ns,physx_steps=ps,feedback_checks_passed=passed,training=False,
            robot_validated=False,blade_validated=False,long_run_coupling_validated=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
              [Path(__file__),ROOT/'rl/tomato_partitioned_reference.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,newton_step_cap=2,physx_step_cap=1,dt_s=DT,
            schedule='Read PhysX -> echo both Newton body states -> collide/solve soft with frozen proxy -> collect final contact reaction -> apply once to PhysX -> echo updated pose/twist back.',
            scope='Two synthetic head-on fixtures, zero initial velocity, zero COM offset, damping/friction/gravity zero. No blade or robot.'))
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
            contacts=pipeline.contacts();pipeline.collide(sin,contacts);wp.synchronize()
            count=int(contacts.soft_contact_count.numpy()[0])
            if count!=(1 if i==0 else 0):raise ValueError('Unexpected collision count')
            before=sin.particle_q.numpy().tolist()[0]
            write(out,'worker_status.json',dict(stage='newton_soft_step',case=i,newton_steps=ns,physx_steps=ps))
            solver.step(sin,sout,None,contacts,DT);wp.synchronize();ns+=1
            if sout.body_q.numpy().tolist()[0]!=initial['pose'] or sout.body_qd.numpy().tolist()[0]!=initial['velocity']:
                raise ValueError('Newton moved externally owned rigid body')
            if count:
                reaction=collect_reaction(model,sout,sin,contacts,solver)
                if reaction['ke'][0]!=1750. or reaction['kd'][0]!=0. or reaction['mu'][0]!=0.:
                    raise ValueError('Unexpected actual solver material cache')
                soft_force=reaction['force'][0];wrench=reaction['wrench'][0]
            else:
                reaction=None;soft_force=[0.]*3;wrench=[0.]*6
            if any(abs(v)>1e-7 for v in [*soft_force[:2],*wrench[:2],*wrench[3:]]):raise ValueError('Unexpected transverse force or torque')
            body.instantaneous_wrench_composer.set_forces_and_torques_index(
                forces=torch.tensor([[wrench[:3]]],dtype=torch.float32),torques=torch.tensor([[wrench[3:]]],dtype=torch.float32),
                positions=None,is_global=True)
            body.write_data_to_sim()
            if body.instantaneous_wrench_composer.active or body.permanent_wrench_composer.active:raise ValueError('Unexpected queued wrench')
            record=dict(id='contact' if i==0 else 'clear',initial_physx=initial,initial_particle=before,
                soft_after_q=sout.particle_q.numpy().tolist()[0],soft_after_qd=sout.particle_qd.numpy().tolist()[0],
                contact_count=count,contact_arrays={field:getattr(contacts,field).numpy()[:count].tolist() for field in
                    ('soft_contact_indices','soft_contact_barycentric','soft_contact_shape','soft_contact_body_pos','soft_contact_body_vel','soft_contact_normal')},
                reaction_collection=reaction,soft_force_n=soft_force,physx_world_com_wrench=wrench,
                particle_mass_kg=float(model.particle_mass.numpy()[0]),body_mass_kg=float(body.data.body_mass.torch[0,0]),
                half_height_m=float(model.shape_scale.numpy()[shape][2]),proxy_frozen_during_newton=True)
            fixtures.append((body,sin,sout));cases.append(record)
        write(out,'before_physx_step.json',dict(cases=cases,newton_steps=ns,physx_steps=ps))
        if (out/'stop.request').exists():raise InterruptedError('Stopped before PhysX reaction step')
        sim.step(render=False);ps+=1
        for (body,sin,sout),r in zip(fixtures,cases):
            body.update(DT);r['final_physx']=echo(body,(sin,sout));r['updated_proxy_echo_exact']=True
            write(out,r['id']+'_final_before_checks.json',r)
            after=dict(particle_z=r['soft_after_q'][2],particle_vz=r['soft_after_qd'][2],
                body_z=r['final_physx']['pose'][2],body_vz=r['final_physx']['velocity'][2])
            r['assessment']=assess(r['initial_particle'][2],r['initial_physx']['pose'][2],r['particle_mass_kg'],r['body_mass_kg'],
                1750.,r['half_height_m'],DT,after,r['soft_force_n'][2],body_substeps=16)
            if any(abs(v)>1e-7 for v in [*r['soft_after_qd'][:2],*r['final_physx']['velocity'][:2],*r['final_physx']['velocity'][3:]]):
                raise ValueError('Unexpected off-axis motion')
        if ns!=2 or ps!=1 or int(sim._physics_step_count)!=baseline+1:raise ValueError('Unexpected controlled step count')
        write(out,'contact_feedback_measurements.json',dict(cases=cases,newton_steps=ns,physx_steps=ps,
            dt_s=DT,physx_tgs_position_substeps=16,physx_force_per_substep=True,physics_backend=sim.physics_manager.__module__,baseline_physx_steps=baseline,
            final_physx_steps=int(sim._physics_step_count),physical_energy_conservation_expected=False,
            limits='One interval; axis-aligned analytic particle/box; actual contact helper with actual solver caches; no robot/blade or repeated stability claim.'))
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
