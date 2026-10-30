"""Reach above the handle of the kitchen's existing knife using bounded joint drives."""
import argparse,json,math,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gui',action='store_true');parser.add_argument('--interactive',action='store_true')
args=parser.parse_args()
status_path=ROOT/'logs/kitchen_reach_status.json'
def status(state,**kw):status_path.write_text(json.dumps({'state':state,**kw},indent=2))
status('starting')
from isaacsim import SimulationApp
app=SimulationApp({'headless':not args.gui,'width':1100,'height':760,'renderer':'RaytracedLighting','anti_aliasing':0})
try:
    import numpy as np
    from scipy.spatial.transform import Rotation
    from pxr import Usd,UsdGeom,UsdPhysics,Gf,UsdLux
    import omni.usd
    from isaacsim.core.api import World
    from isaacsim.core.prims import SingleArticulation,SingleRigidPrim,RigidPrim
    from isaacsim.core.utils.types import ArticulationAction
    from reach_kinematics import ArmKinematics,PALM_OFFSET
    meta=json.loads((ROOT/'work/kitchen_reach_metadata.json').read_text())
    seed=json.loads((ROOT/'work/reach_seed.json').read_text())
    context=omni.usd.get_context();context.open_stage(str(ROOT/'work/kitchen_reach.usda'))
    stage=context.get_stage()
    # Keep runtime edits in a disposable session layer.
    stage.SetEditTarget(stage.GetSessionLayer())
    kin=ArmKinematics(stage)
    home=meta['home_rad'].copy()
    for n,q in zip(kin.names,seed['ready_rad']):home[n]=q
    for n in home:
        if n.startswith('right_rh_') or n.startswith('left_'):home[n]=0.0
        p=stage.GetPrimAtPath('/dual_ar5_o6/Physics/'+n)
        UsdPhysics.DriveAPI(p,'angular').GetTargetPositionAttr().Set(float(np.rad2deg(home[n])))
    knife_prim=stage.GetPrimAtPath(meta['knife_path'])
    xf=UsdGeom.XformCache().GetLocalToWorldTransform(knife_prim)
    scale=np.linalg.norm(np.array(xf)[:3,:3],axis=1)
    handle_local=np.array(meta['knife_handle_local'])*scale
    world=World(stage_units_in_meters=1.,physics_dt=1/120,rendering_dt=1/30,backend='numpy',device='cpu')
    world.scene.add_default_ground_plane(restitution=0.)
    light=UsdLux.DomeLight.Define(stage,'/ReachLight');light.CreateIntensityAttr(1200)
    robot=world.scene.add(SingleArticulation('/dual_ar5_o6',name='robot',reset_xform_properties=False))
    knife=world.scene.add(SingleRigidPrim(meta['knife_path'],name='existing_kitchen_knife',reset_xform_properties=False))
    right_bodies=[str(p.GetPath()) for p in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')) if p.HasAPI(UsdPhysics.RigidBodyAPI) and p.GetName().startswith('right_')]
    contacts=world.scene.add(RigidPrim(right_bodies,name='right_contact_monitor',reset_xform_properties=False,track_contact_forces=True,contact_filter_prim_paths_expr=[[] for _ in right_bodies]))
    world.reset()
    names=robot.dof_names;right=np.array([names.index(n) for n in kin.names]);left=np.array([i for i,n in enumerate(names) if n.startswith('left_')])
    qhome=np.array([home[n] for n in names],dtype=np.float32)
    # Initialization only; every subsequent movement uses motor targets.
    robot.set_joint_positions(qhome);robot.set_joint_velocities(np.zeros(len(names)))
    robot.apply_action(ArticulationAction(joint_positions=qhome))
    hand_index=robot._articulation_view.get_body_index('right_rh_hand_base_link')
    def palm_pose():
        t=robot._articulation_view._physics_view.get_link_transforms()[0,hand_index]
        rot=Rotation.from_quat(t[3:7]).as_matrix()
        return t[:3]+rot@PALM_OFFSET,rot
    def handle_pose():
        pos,quat=knife.get_world_pose();rot=Rotation.from_quat([*quat[1:],quat[0]]).as_matrix()
        return pos+rot@handle_local,rot
    max_contact=0.;max_error=0.;max_left=0.;samples=[]
    def step(q,render=False,check_contact=True):
        global max_contact,max_error,max_left
        robot.apply_action(ArticulationAction(joint_positions=q));world.step(render=render)
        actual=robot.get_joint_positions();vel=robot.get_joint_velocities()
        if not np.isfinite(actual).all() or not np.isfinite(vel).all():raise RuntimeError('Non-finite robot state')
        if np.max(np.abs(vel))>3.:raise RuntimeError('Unexpected robot joint velocity')
        err=float(np.max(np.abs(actual[right]-q[right])));max_error=max(max_error,err)
        max_left=max(max_left,float(np.max(np.abs(actual[left]-qhome[left]))))
        force=float(np.max(np.linalg.norm(contacts.get_net_contact_forces(dt=1/120),axis=-1)));max_contact=max(max_contact,force)
        if check_contact and force>5.:raise RuntimeError(f'Unexpected right-arm contact: {force:.2f} N')
        if err>math.radians(12):raise RuntimeError('Right arm cannot track target; possible obstruction')
    for i in range(360):step(qhome,False,check_contact=i>10)
    actual_palm,_=palm_pose();predicted,_=kin.pose(qhome[right]);fk_error=float(np.linalg.norm(actual_palm-predicted))
    if fk_error>.01:raise RuntimeError(f'Kinematic frame mismatch: {fk_error}')
    handle,knife_rot=handle_pose();knife_initial=knife.get_world_pose()[0].copy()
    if not .82<handle[2]<.92:raise RuntimeError(f'Knife did not settle on the worktop: {handle.tolist()}')
    knife_vel=knife.get_linear_velocity()
    if np.linalg.norm(knife_vel)>.01:raise RuntimeError('Knife has not settled')
    # Keep the open palm 12 cm above the handle; this is a pre-grasp, not a grasp.
    goal=handle+np.array([0,0,.12])
    direction=knife_rot[:,0];direction[2]=0;direction/=np.linalg.norm(direction)
    desired_rotation=np.column_stack(([0,0,-1],direction,np.cross([0,0,-1],direction)))
    if np.linalg.norm(desired_rotation-np.array(seed['orientation']))>2:desired_rotation[:,1:]*=-1
    q=qhome[right].copy();start=kin.pose(q)[0];path=[qhome.copy()]
    errors=[]
    for alpha in np.linspace(0,1,41)[1:]:
        point=start+(goal-start)*alpha
        q,e,a=kin.solve(point,desired_rotation,q)
        if e>.005 or a>.04:raise RuntimeError(f'Unreachable waypoint: {e} m, {a} rad')
        if np.max(np.abs(q-path[-1][right]))>.15:raise RuntimeError('Discontinuous IK solution')
        full=qhome.copy();full[right]=q;path.append(full);errors.append(e)
    # Additional sampled geometric screen against the board plane for distal links.
    for full in path:
        transforms=kin.transforms(full[right])
        for name,t in transforms.items():
            if any(x in name.split('/')[-1] for x in ['link3','link4','link5','link6','link7','hand_base']):
                if t[0,3]<-2.0 and t[2,3]<.94:raise RuntimeError('Arm route is too close to worktop')
    print('REACH_PLAN_READY',json.dumps({'knife':meta['knife_path'],'handle':handle.tolist(),'goal':goal.tolist(),'start':start.tolist(),'fk_error_m':fk_error,'knife_speed':float(np.linalg.norm(knife_vel))}),flush=True)
    if args.gui:
        from omni.kit.viewport.utility import get_active_viewport
        camera=UsdGeom.Camera.Define(stage,'/ReachCamera');camera.CreateClippingRangeAttr((.01,1000));camera.CreateFocalLengthAttr(23)
        mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(-4.0,-3.5,2.0),Gf.Vec3d(-1.95,-1.5,1.0),Gf.Vec3d(0,0,1)).GetInverse()
        UsdGeom.Xformable(camera).AddTransformOp().Set(mat);get_active_viewport().camera_path='/ReachCamera'
    def capture(name):
        if not args.gui:return
        import asyncio
        from omni.kit.viewport.utility import get_active_viewport,capture_viewport_to_file
        for _ in range(8):step(current,True)
        f=asyncio.ensure_future(capture_viewport_to_file(get_active_viewport(),str(ROOT/'logs'/name)).wait_for_result())
        for _ in range(300):
            if f.done():break
            app.update()
        if not f.done():raise RuntimeError('Capture timed out')
        f.result()
    current=qhome.copy()
    capture('kitchen_reach_before.png')
    def execute(route,live=False):
        global current
        for next_q in route:
            begin_q=current.copy()
            steps=max(8,int(math.ceil(np.max(np.abs(next_q-begin_q))/math.radians(6)*120)))
            for i in range(steps):
                tick=time.monotonic();current=begin_q+(next_q-begin_q)*(i+1)/steps
                step(current,args.gui and i%4==0)
                if live:time.sleep(max(0,1/120-(time.monotonic()-tick)))
            if np.linalg.norm(handle_pose()[0]-handle)>.02:raise RuntimeError('Knife moved from the planned target')
        for _ in range(120):step(current,args.gui)
    execute(path[1:],live=args.gui)
    palm,rotation=palm_pose();handle_final,_=handle_pose()
    final_error=float(np.linalg.norm(palm-goal));clearance=float(palm[2]-handle_final[2]);orientation_error=float(np.linalg.norm(Rotation.from_matrix(desired_rotation@rotation.T).as_rotvec()))
    report={'passed':final_error<.01 and max_contact<5 and max_left<math.radians(2),
            'knife_path':meta['knife_path'],'knife_source_stack':meta['knife_source_stack'],'duplicate_knife_created':False,
            'handle_position_m':handle_final.tolist(),'palm_position_m':palm.tolist(),'palm_target_m':goal.tolist(),
            'palm_target_error_m':final_error,'palm_height_above_handle_m':clearance,'orientation_error_deg':math.degrees(orientation_error),
            'max_right_contact_force_n':max_contact,'max_joint_tracking_error_deg':math.degrees(max_error),'max_left_joint_drift_deg':math.degrees(max_left),
            'knife_displacement_m':float(np.linalg.norm(knife.get_world_pose()[0]-knife_initial)),
            'clearance_screen':str(ROOT/'logs/kitchen_reach_clearance.json'),
            'left_arm_initialization':'Parked in zero-joint pose to clear the right-hand approach',
            'fk_validation_error_m':fk_error,'simplified_materials':True,'kitchen_colliders':meta['active_kitchen_colliders'],
            'limitations':['Pre-grasp only; fingers remain open','Self-collision disabled; worktop screen is conservative, not a full collision planner','Only nearby kitchen colliders enabled; original visuals retained with simple materials','Motor gains provisional; simulation only']}
    (ROOT/'logs/kitchen_reach_report.json').write_text(json.dumps(report,indent=2))
    if not report['passed']:raise RuntimeError('Reach acceptance checks failed')
    capture('kitchen_reach_after.png')
    print('REACH_PASSED',json.dumps(report),flush=True);status('passed',report=str(ROOT/'logs/kitchen_reach_report.json'))
    if args.interactive:
        import omni.ui as ui
        pending=[];window=ui.Window('Kitchen knife — right-arm approach',width=420,height=230)
        with window.frame:
            with ui.VStack(spacing=8):
                ui.Label('Existing kitchen knife | open-hand approach')
                ui.Label('Palm stops 12 cm above the handle.')
                label=ui.Label('Approach complete. Holding position.')
                ui.Button('Return to raised ready pose',clicked_fn=lambda:pending.append('return'))
                ui.Button('Reach above knife handle',clicked_fn=lambda:pending.append('reach'))
                ui.Label('Kitchen uses lightweight materials and nearby collisions.')
        print('KITCHEN_INTERACTIVE_READY',flush=True);status('interactive')
        while app.is_running():
            tick=time.monotonic()
            if pending:
                action=pending.pop(0);pending.clear()
                label.text='Moving slowly...'
                if action=='return':
                    if np.max(np.abs(current-qhome))>.01:execute(path[-2::-1],live=True)
                else:
                    if np.max(np.abs(current-qhome))>.01:execute(path[-2::-1],live=True)
                    execute(path[1:],live=True)
                label.text='Holding above the handle.' if action=='reach' else 'Holding raised ready pose.'
            for _ in range(4):step(current)
            world.render();time.sleep(max(0,1/30-(time.monotonic()-tick)))
except BaseException as exc:
    traceback.print_exc();print('REACH_FAILED',str(exc),flush=True);status('failed',error=str(exc))
    raise
finally:
    app.close()
