"""CPU PhysX passive hinges: prescribed link wrench pulse and zero-input coast."""
import argparse,hashlib,math,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_hinge_reference import expected_pulse,check
ROOT=Path(__file__).resolve().parents[1]
DT=1/2400


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output;app=sim=None;passed=False;steps=echoes=0;cases=[]
    def stop(signum,frame):raise InterruptedError('Hinge interface diagnostic stopped')
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    def result():return dict(diagnostic_passed=passed,shutdown_requested=app is not None,
        shutdown_completion='supervisor_must_observe_exit',hinge_checks_passed=passed,hinge_cases_completed=len(cases),
        controlled_steps=steps,cuda_state_echoes=echoes,newton_steps=0,robot_validated=False,training=False)
    try:
        pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_hinge_reference.py',ROOT/'rl/tomato_isaac_startup_guard.py']}
        write(out,'input_manifest.json',dict(source_sha256=pins,controlled_step_cap=2,dt_s=DT,
            scope='Two local synthetic passive hinges, prescribed world link wrenches only. No Newton contacts, robot, blade or remote asset.'))
        from isaaclab.app import AppLauncher
        launcher=AppLauncher(headless=True,device='cpu',visualizer=['none']);app=launcher.app
        import torch,warp as wp
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
            for name,x,mass in (('base',0.,.01),('link',.01,.02)):
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
            joint=UsdPhysics.RevoluteJoint.Define(stage,path+'/hinge')
            joint.CreateBody0Rel().SetTargets([path+'/base']);joint.CreateBody1Rel().SetTargets([path+'/link'])
            joint.CreateAxisAttr('Z');joint.CreateLocalPos0Attr(Gf.Vec3f(0.));joint.CreateLocalPos1Attr(Gf.Vec3f(-.01,0.,0.))
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
        def echo(asset,link):
            nonlocal echoes
            packet=snapshot(asset,link);pose=wp.array([packet['link_pose']],dtype=wp.transform,device='cpu')
            vel=wp.array([packet['link_com_velocity']],dtype=wp.spatial_vector,device='cpu')
            a=wp.empty(1,dtype=wp.transform,device='cuda:0');b=wp.empty(1,dtype=wp.spatial_vector,device='cuda:0')
            wp.copy(a,pose);wp.copy(b,vel);wp.synchronize()
            if a.numpy().tolist()[0]!=packet['link_pose'] or b.numpy().tolist()[0]!=packet['link_com_velocity']:raise ValueError('Link packet CUDA echo mismatch')
            echoes+=1;return packet
        write(out,'hinge_topology.json',dict(assets=[dict(fixed_base=a.is_fixed_base,num_joints=a.num_joints,num_bodies=a.num_bodies,body_names=a.body_names,joint_names=a.joint_names) for a in assets]))
        for i,asset in enumerate(assets):
            if not asset.is_fixed_base or asset.num_joints!=1 or asset.num_bodies!=2:raise ValueError('Expected one passive joint and fixed base')
            link=asset.body_names.index('link');asset.reset()
            asset.write_joint_stiffness_to_sim_index(stiffness=0.)
            asset.write_joint_damping_to_sim_index(damping=0.)
            asset.write_joint_friction_coefficient_to_sim_index(joint_friction_coeff=torch.zeros((1,1),dtype=torch.float32),joint_dynamic_friction_coeff=torch.zeros((1,1),dtype=torch.float32),joint_viscous_friction_coeff=torch.zeros((1,1),dtype=torch.float32))
            asset.write_joint_state_to_sim_index(position=torch.zeros((1,1)),velocity=torch.zeros((1,1)))
            before=snapshot(asset,link)
            if abs(before['joint_position'][0])+abs(before['joint_velocity'][0])>1e-7:raise ValueError('Hinge not initially at rest')
            mass=float(asset.data.body_mass.torch[0,link]);inertia=float(asset.data.body_inertia.torch[0,link,8])
            lever=before['link_pose'][:3];force=[0.,3.,0.] if i==0 else [-3.,0.,0.];torque=[0.,0.,.0012]
            expected=expected_pulse(mass,inertia,lever,force,torque,[0.,0.,1.],DT)
            matrix=float(asset.data.mass_matrix.torch[0,0,0])
            asset.instantaneous_wrench_composer.set_forces_and_torques_index(forces=torch.tensor([[force]],dtype=torch.float32),
                torques=torch.tensor([[torque]],dtype=torch.float32),positions=None,body_ids=[link],is_global=True)
            asset.write_data_to_sim()
            if asset.instantaneous_wrench_composer.active or asset.permanent_wrench_composer.active:raise ValueError('Articulation wrench composer did not clear')
            cases.append(dict(id='hinge_identity' if i==0 else 'hinge_yaw90',link_index=link,body_names=asset.body_names,
                before=before,force_world_n=force,torque_com_world_nm=torque,expected=expected,mass_matrix_kg_m2=matrix))
        write(out,'hinge_before_pulse.json',dict(cases=cases))
        if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge pulse')
        sim.step(render=False);steps+=1
        for asset,r in zip(assets,cases):
            asset.update(DT);r['after_pulse']=echo(asset,r['link_index'])
            r['pulse_check']=check(r['expected'],r['mass_matrix_kg_m2'],r['after_pulse']['joint_position'][0],r['after_pulse']['joint_velocity'][0])
        write(out,'hinge_after_pulse.json',dict(cases=cases))
        if (out/'stop.request').exists():raise InterruptedError('Stopped before hinge coast')
        for asset in assets:asset.write_data_to_sim()
        sim.step(render=False);steps+=1
        for asset,r in zip(assets,cases):
            asset.update(DT);r['after_coast']=echo(asset,r['link_index'])
            drift=abs(r['after_coast']['joint_velocity'][0]-r['after_pulse']['joint_velocity'][0])
            if drift>2e-6:raise ValueError('Stale hinge wrench or unexpected coast drift')
            r['coast_joint_velocity_change_rad_s']=drift
        if steps!=2 or echoes!=4 or int(sim._physics_step_count)!=baseline+2:raise ValueError('Unexpected controlled step count')
        write(out,'hinge_interface_measurements.json',dict(cases=cases,controlled_steps=steps,cuda_state_echoes=echoes,dt_s=DT,
            baseline_physx_steps=baseline,final_physx_steps=int(sim._physics_step_count),
            newton_contact_connected=False,scope='Prescribed force/torque interface on passive fixed-base hinges only.'))
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
