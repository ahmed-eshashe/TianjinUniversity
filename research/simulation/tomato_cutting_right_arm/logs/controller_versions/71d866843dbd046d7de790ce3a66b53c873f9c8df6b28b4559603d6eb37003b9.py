"""Physically grasp and lift the kitchen's existing knife with guarded joint drives."""
import argparse,hashlib,json,math,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
controller_source=Path(__file__).read_bytes();controller_sha256=hashlib.sha256(controller_source).hexdigest()
version_dir=ROOT/'logs/controller_versions';version_dir.mkdir(exist_ok=True);(version_dir/(controller_sha256+'.py')).write_bytes(controller_source)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--knife-setup-yaw-deg',type=float,default=0.,help='Rotate the existing knife and board around the handle before physics only')
parser.add_argument('--knife-setup-roll-deg',type=float,default=0.,help='Choose which blade face rests on the board before physics')
parser.add_argument('--post-lift-roll-deg',type=float,default=0.,help='Turn the wrist around the held handle after lifting clear of the board')
parser.add_argument('--require-cutting-orientation',action='store_true')
parser.add_argument('--align-board-to-counter',action='store_true')
parser.add_argument('--deactivate-spare-knife',action='store_true')
parser.add_argument('--pickup-at-counter-edge',action='store_true',help='Move the original board/knife together to the counter edge so fingers can wrap underneath the handle')
parser.add_argument('--inspect-scene-only',action='store_true')
parser.add_argument('--motion-time-scale',type=float,default=1.,help='Arm travel speed multiplier, limited to 1–2; contact and memory stops unchanged')
parser.add_argument('--finish-closure-when-stable',action='store_true',help='End closure after one second of stationary wrapped support; final lift/hold checks remain unchanged')
parser.add_argument('--fingers-first',action='store_true',help='Hold thumb open until the configured number of fingers establish supporting knife contact')
parser.add_argument('--finger-seating-force',type=float,default=1.)
parser.add_argument('--index-close-delay',type=float,default=0.,help='Delay index flexion during initial finger seating so the other fingers can reach the handle together')
parser.add_argument('--finger-support-count',type=int,choices=[1,2,3,4],default=3)
parser.add_argument('--finger-support-force',type=float,default=.2)
parser.add_argument('--finger-support-seconds',type=float,default=.25)
parser.add_argument('--seat-palm',action='store_true',help='After initial finger support, gently move the palm around the board-supported handle before thumb closure')
parser.add_argument('--seat-x',type=float,default=.035)
parser.add_argument('--seat-z',type=float,default=.075)
parser.add_argument('--test-offset-xy',type=float,nargs=2,default=[0.,0.],metavar=('X_M','Y_M'),help='Before physics, translate the existing knife and supporting board in world XY; robot base stays fixed')
parser.add_argument('--align-thumb-yaw',action='store_true',help='Align thumb opposition separately from distal-pad pressure control')
parser.add_argument('--thumb-yaw-force-limit',type=float,default=20.)
parser.add_argument('--require-wrap',action='store_true',help='Require palm support, contact away from the fingertips, opposed thumb and curled fingers in addition to lift stability')
parser.add_argument('--lift-pitch-deg',type=float,default=0.)
parser.add_argument('--approach-axis',choices=['x','y','z'],default='z')
parser.add_argument('--stance-seed',default='work/grasp_stance_seed.json')
parser.add_argument('--pinky-close-deg',type=float)
parser.add_argument('--overhang-edge',type=float,default=.02)
parser.add_argument('--handle-overhang',action='store_true')
parser.add_argument('--seat-distance',type=float,default=0.)
parser.add_argument('--lift-height',type=float,default=.03)
parser.add_argument('--lift-support-close-deg',type=float)
parser.add_argument('--support-fingers',choices=['none','middle','ring','middle-ring'],default='none')
parser.add_argument('--support-close-deg',type=float,default=80.)
parser.add_argument('--pad-stiffness',type=float,default=0.)
parser.add_argument('--pad-damping',type=float,default=30.)
parser.add_argument('--torsional-radius',type=float,default=0.)
parser.add_argument('--thumb-torque',type=float)
parser.add_argument('--thumb-stiffness',type=float)
parser.add_argument('--static-friction',type=float,default=1.2)
parser.add_argument('--dynamic-friction',type=float,default=1.)
parser.add_argument('--air-hand-test',action='store_true')
parser.add_argument('--lift-close-deg',type=float)
parser.add_argument('--inspect-hand',action='store_true')
parser.add_argument('--adjust-stance',action='store_true')
parser.add_argument('--finger-stiffness',type=float,default=5.)
parser.add_argument('--thumb-contact-force',type=float,default=3.)
parser.add_argument('--finger-contact-force',type=float,default=3.)
parser.add_argument('--middle-contact-force',type=float,help='Override the middle finger squeeze target after thumb support; torque limits stay unchanged')
parser.add_argument('--closure-speed',type=float,default=8.)
parser.add_argument('--close-camera',action='store_true')
parser.add_argument('--force-closure',action='store_true')
parser.add_argument('--close-thumb-pitch-deg',type=float)
parser.add_argument('--insert-distance',type=float,default=0.)
parser.add_argument('--prethumb-yaw-deg',type=float,default=0.)
parser.add_argument('--approach-clearance',type=float,default=.08)
parser.add_argument('--finger-torque',type=float,default=.08)
parser.add_argument('--contact-descent',action='store_true')
parser.add_argument('--thumb-pitch-deg',type=float,default=33.)
parser.add_argument('--thumb-yaw-deg',type=float,default=77.)
parser.add_argument('--tilt-deg',type=int,choices=[0,30,45,50,52,55,60],default=0)
parser.add_argument('--palm-height',type=float,default=.06)
parser.add_argument('--finger-offset',type=float,default=.04)
parser.add_argument('--preclose-deg',type=float,default=0.)
parser.add_argument('--handle-offset',type=float,default=0.)
parser.add_argument('--close-deg',type=float,default=75.)
parser.add_argument('--gui',action='store_true');parser.add_argument('--interactive',action='store_true')
args=parser.parse_args()
status_path=ROOT/'logs/kitchen_grasp_status.json'
run_started=time.monotonic();phase_times=[]
def status(state,**kw):
    if not phase_times or phase_times[-1]['state']!=state:phase_times.append({'state':state,'wall_seconds':time.monotonic()-run_started})
    temp=status_path.with_suffix('.tmp')
    temp.write_text(json.dumps({'state':state,'configuration':vars(args),**kw},indent=2));temp.replace(status_path)
status('starting')
class SceneInspectionComplete(Exception):pass
from isaacsim import SimulationApp
app=SimulationApp({'headless':not args.gui,'width':1100,'height':760,'renderer':'RaytracedLighting','anti_aliasing':0})
try:
    import numpy as np
    from scipy.spatial.transform import Rotation
    from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,PhysxSchema,Gf,UsdLux
    import omni.usd
    from isaacsim.core.api import World
    from isaacsim.core.prims import SingleArticulation,SingleRigidPrim,RigidPrim
    from isaacsim.core.utils.types import ArticulationAction
    from reach_kinematics import ArmKinematics,PALM_OFFSET
    meta=json.loads((ROOT/'work/kitchen_reach_metadata.json').read_text())
    seed=json.loads((ROOT/'work/reach_seed.json').read_text())
    if args.adjust_stance:
        seed.update(json.loads((ROOT/args.stance_seed).read_text()))
        args.tilt_deg=seed['tilt_deg']
    elif args.tilt_deg:
        candidate=next(c for c in json.loads((ROOT/'work/grasp_pose_candidates.json').read_text()) if c['tilt_deg']==args.tilt_deg)
        seed.update(candidate)
    context=omni.usd.get_context();context.open_stage(str(ROOT/'work/kitchen_reach.usda'))
    stage=context.get_stage()
    # Keep runtime edits in a disposable session layer.
    stage.SetEditTarget(stage.GetSessionLayer())
    if not 1<=args.motion_time_scale<=2:raise ValueError('Motion time scale must be between 1 and 2')
    scene_setup={'board_alignment_error_deg':None,'spare_knife_deactivated':False}
    if args.deactivate_spare_knife:
        spare=stage.GetPrimAtPath('/Indoor/RZ/SM_kitchen_knife_01')
        if not spare:raise RuntimeError('Expected original spare knife not found')
        spare.SetActive(False);scene_setup['spare_knife_deactivated']=not spare.IsActive()
    if args.fingers_first and (not args.force_closure or args.support_fingers!='none'):
        raise ValueError('Fingers-first requires force closure with no separate support-finger phase')
    if args.seat_palm and not args.fingers_first:raise ValueError('Palm seating requires the fingers-first sequence')
    if not math.isfinite(args.knife_setup_yaw_deg):raise ValueError('Knife setup angle must be finite')
    if args.knife_setup_yaw_deg or args.knife_setup_roll_deg:
        cache=UsdGeom.XformCache();km=np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(meta['knife_path']))).T
        pivot=km[:3,:3]@np.array(meta['knife_handle_local'])+km[:3,3]
        delta=np.eye(4);delta[:3,:3]=Rotation.from_euler('z',args.knife_setup_yaw_deg,degrees=True).as_matrix();delta[:3,3]=pivot-delta[:3,:3]@pivot
        for prim_path in [meta['knife_path'],'/Indoor/RZ/SM_kitchen_Board']:
            if args.align_board_to_counter and prim_path.endswith('SM_kitchen_Board'):continue
            prim=stage.GetPrimAtPath(prim_path);world_matrix=np.array(cache.GetLocalToWorldTransform(prim)).T
            parent_matrix=np.array(cache.GetLocalToWorldTransform(prim.GetParent())).T
            transform=delta.copy()
            if prim_path==meta['knife_path']:
                axis=km[:3,0]/np.linalg.norm(km[:3,0]);transform[:3,:3]=delta[:3,:3]@Rotation.from_rotvec(axis*math.radians(args.knife_setup_roll_deg)).as_matrix();transform[:3,3]=pivot-transform[:3,:3]@pivot
            xf=UsdGeom.Xformable(prim);xf.ClearXformOpOrder();xf.AddTransformOp(opSuffix='cookingSetup').Set(Gf.Matrix4d((np.linalg.inv(parent_matrix)@transform@world_matrix).T.tolist()))
        print('COOKING_SETUP',json.dumps({'existing_knife_yaw_deg':args.knife_setup_yaw_deg,'resting_face_roll_deg':args.knife_setup_roll_deg,'phase':'before physics only','knife_attached':False}),flush=True)
    if args.align_board_to_counter:
        helper_source=(ROOT/'scripts/grasp_scene_geometry.py').read_bytes();helper_hash=hashlib.sha256(helper_source).hexdigest()
        (version_dir/(helper_hash+'.py')).write_bytes(helper_source);scene_setup['geometry_helper_sha256']=helper_hash
        from grasp_scene_geometry import align_board
        cache=UsdGeom.XformCache();board=stage.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');counter=stage.GetPrimAtPath('/Indoor/RZ/SM_YZ_CF_10')
        bm=np.array(cache.GetLocalToWorldTransform(board)).T;tm=np.array(cache.GetLocalToWorldTransform(counter)).T
        bm,error=align_board(np.array(UsdGeom.Mesh(board).GetPointsAttr().Get()),bm,np.array(UsdGeom.Mesh(counter).GetPointsAttr().Get()),tm)
        parent=np.array(cache.GetLocalToWorldTransform(board.GetParent())).T
        xf=UsdGeom.Xformable(board);xf.ClearXformOpOrder();xf.AddTransformOp(opSuffix='counterAligned').Set(Gf.Matrix4d((np.linalg.inv(parent)@bm).T.tolist()))
        scene_setup['board_alignment_error_deg']=error
        if error>.1:raise RuntimeError('Board alignment did not match the countertop')
    print('SCENE_SETUP',json.dumps(scene_setup),flush=True)
    if not np.all(np.isfinite(args.test_offset_xy)) or np.linalg.norm(args.test_offset_xy)>.15:
        raise ValueError('Position tests are limited to finite offsets within 15 cm of the validated setup')
    if np.any(args.test_offset_xy):
        offset=np.array([*args.test_offset_xy,0.]);cache=UsdGeom.XformCache()
        for prim_path in [meta['knife_path'],'/Indoor/RZ/SM_kitchen_Board']:
            prim=stage.GetPrimAtPath(prim_path)
            world_matrix=np.array(cache.GetLocalToWorldTransform(prim)).T
            parent_matrix=np.array(cache.GetLocalToWorldTransform(prim.GetParent())).T
            world_matrix[:3,3]+=offset
            local_matrix=np.linalg.inv(parent_matrix)@world_matrix
            xf=UsdGeom.Xformable(prim);xf.ClearXformOpOrder()
            xf.AddTransformOp(opSuffix='positionTest').Set(Gf.Matrix4d(local_matrix.T.tolist()))
        print('POSITION_TEST_SETUP',json.dumps({'offset_world_xy_m':args.test_offset_xy,'robot_base_fixed_across_tests':True,'support_board_moves_with_knife':True,'phase':'before physics only'}),flush=True)
    if args.adjust_stance:
        root_prim=stage.GetPrimAtPath('/dual_ar5_o6')
        root_matrix=np.array(UsdGeom.XformCache().GetLocalToWorldTransform(root_prim)).T
        root_matrix[:2,3]+=seed.get('root_offset_xy',[0,0])
        root_matrix[:3,:3]=Rotation.from_euler('z',seed['root_yaw_deg'],degrees=True).as_matrix()
        xfroot=UsdGeom.Xformable(root_prim);xfroot.ClearXformOpOrder();xfroot.AddTransformOp(opSuffix='graspStance').Set(Gf.Matrix4d(root_matrix.T.tolist()))
    board_shift=None
    if args.handle_overhang:
        board_prim=stage.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');cache=UsdGeom.XformCache()
        bm=np.array(cache.GetLocalToWorldTransform(board_prim)).T
        km=np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(meta['knife_path']))).T
        h=km[:3,:3]@np.array(meta['knife_handle_local'])+km[:3,3]
        direction=np.array(seed['orientation'])[:,1];direction[2]=0;direction/=np.linalg.norm(direction)
        if args.require_cutting_orientation:
            mesh=UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']));v=np.array(mesh.GetPointsAttr().Get());cnt=np.array(mesh.GetFaceVertexCountsAttr().Get());idx=np.array(mesh.GetFaceVertexIndicesAttr().Get());off=np.r_[0,np.cumsum(cnt)]
            faces=UsdGeom.Subset(stage.GetPrimAtPath(meta['knife_path']+'/Section0')).GetIndicesAttr().Get();used=np.unique(np.concatenate([idx[off[f]:off[f+1]] for f in faces]))
            direction=-(km[:3,:3]@(v[used].mean(0)-np.array(meta['knife_handle_local'])));direction[2]=0;direction/=np.linalg.norm(direction)
        points=np.array(UsdGeom.Mesh(board_prim).GetPointsAttr().Get());lo=points.min(0);hi=points.max(0)
        bi=np.linalg.inv(bm);hl=bi[:3,:3]@h+bi[:3,3];dl=bi[:3,:3]@direction
        edge=min((hi[i]-hl[i])/dl[i] if dl[i]>0 else (lo[i]-hl[i])/dl[i] for i in [0,1] if abs(dl[i])>1e-6)
        board_shift=-direction*max(0.,edge-args.overhang_edge);bm[:3,3]+=board_shift
        bx=UsdGeom.Xformable(board_prim);bx.ClearXformOpOrder();bx.AddTransformOp(opSuffix='graspBoard').Set(Gf.Matrix4d(bm.T.tolist()))
        print('BOARD_SETUP',json.dumps({'existing_board_shift_m':board_shift.tolist(),'handle_axis_edge_m':args.overhang_edge}),flush=True)
    if args.pickup_at_counter_edge:
        if not args.align_board_to_counter:raise ValueError('Counter-edge pickup requires the aligned board')
        cache=UsdGeom.XformCache();counter=stage.GetPrimAtPath('/Indoor/RZ/SM_YZ_CF_10');tm=np.array(cache.GetLocalToWorldTransform(counter)).T
        tv=np.array(UsdGeom.Mesh(counter).GetPointsAttr().Get())@tm[:3,:3].T+tm[:3,3]
        board=stage.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');bm=np.array(cache.GetLocalToWorldTransform(board)).T;bv=np.array(UsdGeom.Mesh(board).GetPointsAttr().Get())@bm[:3,:3].T+bm[:3,3]
        robot_x=float(np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath('/dual_ar5_o6')))[3,0]);near_max=robot_x>(tv[:,0].min()+tv[:,0].max())/2
        shift=np.array([(tv[:,0].max()-.01-bv[:,0].max()) if near_max else (tv[:,0].min()+.01-bv[:,0].min()),0.,0.])
        for prim_path in [meta['knife_path'],'/Indoor/RZ/SM_kitchen_Board']:
            prim=stage.GetPrimAtPath(prim_path);matrix=np.array(cache.GetLocalToWorldTransform(prim)).T;matrix[:3,3]+=shift;parent=np.array(cache.GetLocalToWorldTransform(prim.GetParent())).T
            xf=UsdGeom.Xformable(prim);xf.ClearXformOpOrder();xf.AddTransformOp(opSuffix='counterEdge').Set(Gf.Matrix4d((np.linalg.inv(parent)@matrix).T.tolist()))
        scene_setup['counter_edge_translation_m']=shift.tolist()
        print('COUNTER_EDGE_SETUP',json.dumps(scene_setup),flush=True)
    kin=ArmKinematics(stage)
    if args.tilt_deg and not args.adjust_stance:
        raised=np.array(seed['ready_position'])+np.array([0,0,.06])
        ready,e,a=kin.solve(raised,np.array(seed['orientation']),np.array(seed['ready_rad']))
        if e>.004 or a>.04:raise RuntimeError('Raised initial pose unreachable')
        seed['ready_rad']=ready.tolist()
    home=meta['home_rad'].copy()
    for n,q in zip(kin.names,seed['ready_rad']):home[n]=q
    for n in home:
        if n.startswith('right_rh_') or n.startswith('left_'):home[n]=0.0
        p=stage.GetPrimAtPath('/dual_ar5_o6/Physics/'+n)
        UsdPhysics.DriveAPI(p,'angular').GetTargetPositionAttr().Set(float(np.rad2deg(home[n])))
    # Compound collision follows the knife's actual blade and handle subsets.
    # Both shapes belong to the SAME existing rigid body; no extra knife is spawned.
    original_knife=stage.GetPrimAtPath(meta['knife_path'])
    knife_mesh=UsdGeom.Mesh(original_knife)
    source_points=np.array(knife_mesh.GetPointsAttr().Get())
    source_counts=np.array(knife_mesh.GetFaceVertexCountsAttr().Get())
    source_indices=np.array(knife_mesh.GetFaceVertexIndicesAttr().Get())
    source_offsets=np.r_[0,np.cumsum(source_counts)]
    UsdPhysics.CollisionAPI(original_knife).CreateCollisionEnabledAttr(False)
    for name,sections in [('Handle',['Section2']),('Blade',['Section0','Section1'])]:
        faces=np.concatenate([np.array(UsdGeom.Subset(stage.GetPrimAtPath(meta['knife_path']+'/'+section)).GetIndicesAttr().Get()) for section in sections])
        indices=np.concatenate([source_indices[source_offsets[f]:source_offsets[f+1]] for f in faces])
        used,remap=np.unique(indices,return_inverse=True)
        if name=='Handle':handle_vertices_unscaled=source_points[used].copy()
        if name=='Blade':blade_vector_unscaled=source_points[used].mean(0)-np.array(meta['knife_handle_local'])
        shape=UsdGeom.Mesh.Define(stage,meta['knife_path']+'/GripCollision'+name)
        shape.CreatePointsAttr(source_points[used].tolist());shape.CreateFaceVertexCountsAttr(source_counts[faces].tolist());shape.CreateFaceVertexIndicesAttr(remap.tolist())
        shape.CreateVisibilityAttr('invisible')
        UsdPhysics.CollisionAPI.Apply(shape.GetPrim()).CreateCollisionEnabledAttr(True)
        UsdPhysics.MeshCollisionAPI.Apply(shape.GetPrim()).CreateApproximationAttr('convexHull')
    # Provisional high-friction contact and low-torque finger drives in the session layer.
    from isaacsim.core.api.materials import PhysicsMaterial
    grip_material=PhysicsMaterial('/GripPhysicsMaterial',static_friction=args.static_friction,dynamic_friction=args.dynamic_friction,restitution=0.)
    pad_material=PhysicsMaterial('/FingerPadPhysicsMaterial',static_friction=args.static_friction,dynamic_friction=args.dynamic_friction,restitution=0.)
    if args.pad_stiffness:
        compliant=PhysxSchema.PhysxMaterialAPI.Apply(pad_material.prim)
        compliant.CreateCompliantContactStiffnessAttr(args.pad_stiffness)
        compliant.CreateCompliantContactDampingAttr(args.pad_damping)
    for p in stage.Traverse():
        is_hand=str(p.GetPath()).startswith(kin.hand_path)
        is_knife=str(p.GetPath()).startswith(meta['knife_path'])
        if (is_hand or is_knife) and p.HasAPI(UsdPhysics.RigidBodyAPI):
            PhysxSchema.PhysxRigidBodyAPI.Apply(p).CreateMaxDepenetrationVelocityAttr(.1)
        if (is_hand or is_knife) and p.HasAPI(UsdPhysics.CollisionAPI):
            UsdShade.MaterialBindingAPI.Apply(p).Bind(UsdShade.Material(pad_material.prim if is_hand else grip_material.prim),materialPurpose='physics')
            collision=PhysxSchema.PhysxCollisionAPI.Apply(p)
            collision.CreateContactOffsetAttr(.001);collision.CreateRestOffsetAttr(0.)
            if is_hand and args.torsional_radius:
                collision.CreateTorsionalPatchRadiusAttr(args.torsional_radius)
                collision.CreateMinTorsionalPatchRadiusAttr(args.torsional_radius)
        if p.IsA(UsdPhysics.RevoluteJoint) and p.GetName().startswith('right_rh_'):
            drive=UsdPhysics.DriveAPI(p,'angular')
            follower=p.GetRelationship('newton:mimicJoint').HasAuthoredTargets()
            stiffness=args.thumb_stiffness if 'thumb' in p.GetName() and args.thumb_stiffness is not None else args.finger_stiffness
            torque=args.thumb_torque if 'thumb' in p.GetName() and args.thumb_torque is not None else args.finger_torque
            drive.CreateStiffnessAttr(0. if follower else stiffness)
            drive.CreateDampingAttr(0. if follower else .15)
            drive.CreateMaxForceAttr(0. if follower else torque)
    art=PhysxSchema.PhysxArticulationAPI.Apply(stage.GetPrimAtPath('/dual_ar5_o6'))
    art.CreateSolverPositionIterationCountAttr(32);art.CreateSolverVelocityIterationCountAttr(8)
    preshape=[('right_rh_thumb_cmc_yaw',args.prethumb_yaw_deg),('right_rh_thumb_cmc_pitch',args.thumb_pitch_deg),('right_rh_thumb_ip',1.86*args.thumb_pitch_deg)]
    for finger in ['index','middle','ring','pinky']:
        preshape += [(f'right_rh_{finger}_mcp_pitch',args.pinky_close_deg if finger=='pinky' and args.pinky_close_deg is not None else args.preclose_deg),(f'right_rh_{finger}_dip',.89*(args.pinky_close_deg if finger=='pinky' and args.pinky_close_deg is not None else args.preclose_deg))]
    for name,degrees in preshape:
        home[name]=math.radians(degrees)
        UsdPhysics.DriveAPI(stage.GetPrimAtPath('/dual_ar5_o6/Physics/'+name),'angular').GetTargetPositionAttr().Set(degrees)
    knife_prim=stage.GetPrimAtPath(meta['knife_path'])
    xf=UsdGeom.XformCache().GetLocalToWorldTransform(knife_prim)
    scale=np.linalg.norm(np.array(xf)[:3,:3],axis=1)
    handle_local=np.array(meta['knife_handle_local'])*scale
    blade_vector_local=blade_vector_unscaled*scale
    blade_axis_local=blade_vector_local/np.linalg.norm(blade_vector_local)
    handle_blade_end=float(np.max((handle_vertices_unscaled*scale-handle_local)@blade_axis_local))
    from scipy.spatial import ConvexHull
    handle_hull=ConvexHull(handle_vertices_unscaled*scale).equations
    world=World(stage_units_in_meters=1.,physics_dt=1/240,rendering_dt=1/30,backend='numpy',device='cpu')
    world.scene.add_default_ground_plane(restitution=0.)
    light=UsdLux.DomeLight.Define(stage,'/ReachLight');light.CreateIntensityAttr(1200)
    robot=world.scene.add(SingleArticulation('/dual_ar5_o6',name='robot',reset_xform_properties=False))
    knife=world.scene.add(SingleRigidPrim(meta['knife_path'],name='existing_kitchen_knife',reset_xform_properties=False))
    right_bodies=[str(p.GetPath()) for p in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')) if p.HasAPI(UsdPhysics.RigidBodyAPI) and p.GetName().startswith('right_')]
    contacts=world.scene.add(RigidPrim(right_bodies,name='right_contact_monitor',reset_xform_properties=False,track_contact_forces=True,max_contact_count=256,contact_filter_prim_paths_expr=[[meta['knife_path'],'/Indoor/RZ/SM_kitchen_Board'] for _ in right_bodies]))
    knife_board=world.scene.add(RigidPrim([meta['knife_path']],name='knife_board_monitor',reset_xform_properties=False,track_contact_forces=True,contact_filter_prim_paths_expr=[['/Indoor/RZ/SM_kitchen_Board']]))
    other_bodies=[str(p.GetPath()) for p in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')) if p.HasAPI(UsdPhysics.RigidBodyAPI) and not p.GetName().startswith('right_')]
    body_safety=world.scene.add(RigidPrim(other_bodies,name='body_safety_monitor',reset_xform_properties=False,track_contact_forces=True,contact_filter_prim_paths_expr=[[meta['knife_path']] for _ in other_bodies]))
    from isaacsim.core.simulation_manager import SimulationManager
    print('PHYSICS_ENGINE',SimulationManager.get_active_physics_engine(),flush=True)
    world.reset()
    print('PHYSICS_MATERIALS',json.dumps({'hand_and_arm_unique':np.unique(contacts._physics_view.get_material_properties().reshape(-1,3),axis=0).tolist(),'knife':knife._rigid_prim_view._physics_view.get_material_properties().tolist()}),flush=True)
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
    def points_on_handle(points):
        position,quat=knife.get_world_pose();rotation=Rotation.from_quat([*quat[1:],quat[0]]).as_matrix()
        local=(np.asarray(points)-position)@rotation
        return np.max(local@handle_hull[:,:3].T+handle_hull[:,3],axis=-1)<.003
    def handle_contact_summary():
        forces,points,normals,distances,counts,starts=contacts.get_contact_force_data(dt=1/240)
        mask=points_on_handle(points);on_handle={};on_blade={}
        for bi,body in enumerate(right_bodies):
            begin=int(starts[bi,0]);end=begin+int(counts[bi,0]);valid=mask[begin:end];values=forces[begin:end,0]
            for target,selection in [(on_handle,valid),(on_blade,~valid)]:
                force=float(np.sum(values[selection]))
                if force>.02:target[body.split('/')[-1]]=force
        return on_handle,on_blade
    def cutting_orientation():
        position,rotation=handle_pose();_,hand_rotation=palm_pose()
        blade=rotation@blade_vector_local;blade/=np.linalg.norm(blade)
        away=position[:2]-kin.root[:2,3];away/=np.linalg.norm(away)
        outward=float(blade[:2]@away/np.linalg.norm(blade[:2]))
        thumb_side=float(blade@hand_rotation[:,1])
        return {'blade_exits_thumb_index_side':thumb_side>.85,'blade_points_away_from_robot':outward>.7,'cutting_edge_faces_board':bool(rotation[2,1]>.85),'thumb_side_cosine':thumb_side,'outward_cosine':outward,'blade_direction_world':blade.tolist(),'edge_down_cosine':float(rotation[2,1])}
    max_contact=0.;max_error=0.;max_left=0.;samples=[];grasp_phase=False;grip_feedback=None;lifting=False
    arm_contact_indices=[i for i,p in enumerate(right_bodies) if '/right_rh_' not in p]
    def step(q,render=False,check_contact=True):
        global max_contact,max_error,max_left
        if grip_feedback is not None:grip_feedback(q)
        robot.apply_action(ArticulationAction(joint_positions=q));world.step(render=render)
        actual=robot.get_joint_positions();vel=robot.get_joint_velocities()
        if not np.isfinite(actual).all() or not np.isfinite(vel).all():raise RuntimeError('Non-finite robot state')
        if np.max(np.abs(vel))>3.:raise RuntimeError('Unexpected robot joint velocity')
        err=float(np.max(np.abs(actual[right]-q[right])));max_error=max(max_error,err)
        max_left=max(max_left,float(np.max(np.abs(actual[left]-qhome[left]))))
        force=float(np.max(np.linalg.norm(contacts.get_net_contact_forces(dt=1/240),axis=-1)));max_contact=max(max_contact,force)
        if check_contact:
            if args.require_cutting_orientation and grasp_phase:
                _,blade_contacts=handle_contact_summary()
                if max(blade_contacts.values(),default=0.)>.5:
                    print('BLADE_CONTACT_STOP',json.dumps(blade_contacts),flush=True)
                    raise RuntimeError('Hand contacted the blade outside the handle')
            if max(np.linalg.norm(body_safety.get_net_contact_forces(dt=1/240),axis=-1))>5:raise RuntimeError('Parked body contacted kitchen')
            forces=np.linalg.norm(contacts.get_net_contact_forces(dt=1/240),axis=-1)
            arm_force=float(np.max(forces[arm_contact_indices]))
            board_force=float(np.max(np.linalg.norm(contacts.get_contact_force_matrix(dt=1/240)[:,1,:],axis=-1)))
            if board_force>5:raise RuntimeError(f'Hand contacted board: {board_force:.2f} N')
            if arm_force>5 or force>(60 if grasp_phase else 5):
                print('CONTACT_STOP',json.dumps({'forces':{p.split('/')[-1]:float(f) for p,f in zip(right_bodies,forces) if f>1},'knife_contact_forces':contacts.get_contact_force_matrix(dt=1/240)[:,0,:].tolist(),'palm':palm_pose()[0].tolist(),'knife':handle_pose()[0].tolist(),'finger_actual':{n:float(np.rad2deg(actual[i])) for i,n in enumerate(names) if n.startswith('right_rh_')}}),flush=True)
                raise RuntimeError(f'Contact limit: arm={arm_force:.2f}, maximum={force:.2f} N')
        if err>math.radians(12):raise RuntimeError('Right arm cannot track target; possible obstruction')
    for i in range(720):step(qhome,False,check_contact=i>10)
    if args.require_cutting_orientation:
        settling_positions=[];settling_metrics=None
        for _ in range(12*240):
            step(qhome)
            settling_positions.append(handle_pose()[0]);settling_positions=settling_positions[-240:]
            spread=float(np.linalg.norm(np.ptp(settling_positions,axis=0)));speed=float(np.linalg.norm(knife.get_linear_velocity()))
            if len(settling_positions)==240 and spread<.0005 and speed<.005:
                settling_metrics={'one_second_position_range_m':spread,'speed_m_s':speed};break
        if settling_metrics is None:raise RuntimeError('Knife did not settle stably in the cooking setup')
        print('SETTLING_STABILITY',json.dumps(settling_metrics),flush=True)
    print('SETTLED_SCENE',json.dumps({'handle':handle_pose()[0].tolist(),'knife_rotation_world':handle_pose()[1].tolist(),'knife_speed':float(np.linalg.norm(knife.get_linear_velocity())),'knife_mass':float(knife.get_mass()),'knife_com_local':knife.get_com()[0].tolist()}),flush=True)
    if args.inspect_scene_only:
        (ROOT/'logs/kitchen_scene_probe.json').write_text(json.dumps({'configuration':vars(args),'scene_setup':scene_setup,'handle':handle_pose()[0].tolist(),'knife_rotation_world':handle_pose()[1].tolist()},indent=2))
        raise SceneInspectionComplete
    if args.air_hand_test:
        target=qhome.copy()
        for finger in ['index','middle','ring','pinky']:
            target[names.index('right_rh_'+finger+'_mcp_pitch')]=math.radians(80)
            target[names.index('right_rh_'+finger+'_dip')]=math.radians(71.2)
        target[names.index('right_rh_thumb_cmc_pitch')]=math.radians(33)
        target[names.index('right_rh_thumb_ip')]=math.radians(61.38)
        for i in range(2400):step(qhome+(target-qhome)*min(1.,i/1200))
        material=contacts._physics_view.get_material_properties()
        print('MATERIAL_PROPERTIES',json.dumps({p.split('/')[-1]:mat.tolist() for p,mat in zip(right_bodies,material)}),flush=True)
        print('AIR_HAND_TEST',json.dumps({n:{'target_deg':float(np.rad2deg(target[i])),'actual_deg':float(np.rad2deg(robot.get_joint_positions()[i]))} for i,n in enumerate(names) if n.startswith('right_rh_')}),flush=True)
        raise SystemExit('Air hand test complete')
    if args.inspect_hand:
        actual_values=dict(zip(names,robot.get_joint_positions()))
        links=robot._articulation_view._physics_view.get_link_transforms()[0]
        t=links[hand_index];hand_matrix=np.eye(4);hand_matrix[:3,3]=t[:3];hand_matrix[:3,:3]=Rotation.from_quat(t[3:7]).as_matrix()
        expected={kin.hand_path:hand_matrix}
        def hand_transform(path):
            if path in expected:return expected[path]
            parent,child,a,b,axis,name=kin.by_child[path];motion=np.eye(4)
            if axis is not None:motion[:3,:3]=Rotation.from_rotvec(axis*actual_values[name]).as_matrix()
            expected[path]=hand_transform(parent)@a@motion@b;return expected[path]
        diagnostics=[]
        for body in right_bodies:
            if '/right_rh_' not in body or body==kin.hand_path or 'adapter' in body.split('/')[-1]:continue
            link=links[robot._articulation_view.get_body_index(body.split('/')[-1])];pred=hand_transform(body);actualrot=Rotation.from_quat(link[3:7]).as_matrix()
            diagnostics.append({'body':body,'position_error':float(np.linalg.norm(pred[:3,3]-link[:3])),'rotation_error':float(Rotation.from_matrix(actualrot@pred[:3,:3].T).magnitude()),'actual_position':link[:3].tolist(),'predicted_position':pred[:3,3].tolist()})
        print('HAND_FK_CHECK',json.dumps(diagnostics),flush=True)
        (ROOT/'logs/hand_fk_check.json').write_text(json.dumps(diagnostics,indent=2))
        raise SystemExit('Hand geometry inspection complete')
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
    if args.tilt_deg or args.adjust_stance:
        desired_rotation=np.array(seed['orientation'])
        goal=handle-desired_rotation@np.array([args.palm_height,0,args.finger_offset])+np.array([0,0,args.approach_clearance])
        if args.insert_distance:goal=handle-desired_rotation@np.array([args.palm_height,0,args.finger_offset])-desired_rotation[:,'xyz'.index(args.approach_axis)]*args.insert_distance
        goal+=desired_rotation[:,1]*args.handle_offset
    q=qhome[right].copy();start=kin.pose(q)[0];route_start=start.copy();path=[qhome.copy()]
    errors=[]
    approach_goals=[goal]
    if args.approach_axis=='y':
        # Clear the knife from above, then descend beyond the handle end before axial insertion.
        approach_goals=[goal+np.array([0,0,args.approach_clearance]),goal]
    for approach_goal in approach_goals:
        for alpha in np.linspace(0,1,81 if args.fingers_first else 41)[1:]:
            point=start+(approach_goal-start)*alpha
            q,e,a=kin.solve(point,desired_rotation,q)
            if e>.005 or a>.04:raise RuntimeError(f'Unreachable waypoint: {e} m, {a} rad')
            if np.max(np.abs(q-path[-1][right]))>.15:raise RuntimeError('Discontinuous IK solution')
            full=qhome.copy();full[right]=q;path.append(full);errors.append(e)
        start=approach_goal
    # Screen actual arm/hand-base mesh extents against the countertop top plane.
    # A fixed link-origin height rejected valid deep grasps because it ignored link shape.
    cache=UsdGeom.XformCache()
    table_prim=stage.GetPrimAtPath('/Indoor/RZ/SM_YZ_CF_10')
    tm=np.array(cache.GetLocalToWorldTransform(table_prim)).T
    tv=np.array(UsdGeom.Mesh(table_prim).GetPointsAttr().Get())@tm[:3,:3].T+tm[:3,3]
    table_lo=tv.min(0);table_hi=tv.max(0)
    screened_meshes=[];finger_tip_axes={}
    for prim in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')):
        if not prim.IsA(UsdGeom.Mesh):continue
        body=prim
        while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):body=body.GetParent()
        if not body:continue
        body_path=str(body.GetPath());body_name=body.GetName()
        rel=np.linalg.inv(np.array(cache.GetLocalToWorldTransform(body)).T)@np.array(cache.GetLocalToWorldTransform(prim)).T
        vertices=np.array(UsdGeom.Mesh(prim).GetPointsAttr().Get())@rel[:3,:3].T+rel[:3,3]
        if body_name.startswith('right_rh_') or (body_name.startswith('right_') and any(body_name.endswith(n) for n in ['link3','link4','link5','link6','link7'])):
            screened_meshes.append((body_path,vertices))
        if body_name.startswith('right_rh_') and body_name.endswith('_distal') and 'thumb' not in body_name:
            _,_,_,inv_anchor,_,_=kin.by_child[body_path]
            anchor=np.linalg.inv(inv_anchor)[:3,3]
            _,_,axes=np.linalg.svd(vertices-vertices.mean(0),full_matrices=False);axis=axes[0]
            if np.dot(vertices.mean(0)-anchor,axis)<0:axis=-axis
            tip_projection=vertices@axis;end=float(tip_projection.max());tip=vertices[tip_projection>=end-.0015].mean(0)
            finger_tip_axes[body_name]=(axis,end,tip)
    screen_point=handle-desired_rotation@np.array([args.palm_height,0,args.finger_offset])+desired_rotation[:,1]*args.handle_offset
    screen_q,screen_e,screen_angle=kin.solve(screen_point,desired_rotation,path[-1][right])
    if screen_e>.004 or screen_angle>.04:raise RuntimeError('Final descent pose is unreachable')
    screen_full=path[-1].copy();screen_full[right]=screen_q
    for full in [*path,screen_full]:
        transforms=kin.transforms(full[right])
        values=dict(zip(names,full))
        def hand_frame(path):
            if path in transforms:return transforms[path]
            parent,child,a,b,axis,name=kin.by_child[path];motion=np.eye(4)
            if axis is not None:motion[:3,:3]=Rotation.from_rotvec(axis*values[name]).as_matrix()
            transforms[path]=hand_frame(parent)@a@motion@b;return transforms[path]
        for body_path,vertices in screened_meshes:
            transform=hand_frame(body_path)
            v=vertices@transform[:3,:3].T+transform[:3,3];lo=v.min(0);hi=v.max(0)
            from grasp_scene_geometry import minimum_z_over_counter
            minimum_z=minimum_z_over_counter(v,table_lo,table_hi)
            if minimum_z is not None and minimum_z<table_hi[2]+.001:
                raise RuntimeError(f'Arm mesh is too close to worktop: {body_path.split("/")[-1]}, minimum Z over counter {minimum_z:.4f}')
    print('REACH_PLAN_READY',json.dumps({'knife':meta['knife_path'],'handle':handle.tolist(),'goal':goal.tolist(),'start':route_start.tolist(),'fk_error_m':fk_error,'knife_speed':float(np.linalg.norm(knife_vel))}),flush=True)
    if args.gui:
        from omni.kit.viewport.utility import get_active_viewport
        camera=UsdGeom.Camera.Define(stage,'/ReachCamera');camera.CreateClippingRangeAttr((.01,1000));camera.CreateFocalLengthAttr(23)
        eye=(-2.7,-2.3,1.3) if args.close_camera else (-4.0,-3.5,2.0)
        look=(-2.27,-1.76,.91) if args.close_camera else (-1.95,-1.5,1.0)
        mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*look),Gf.Vec3d(0,0,1)).GetInverse()
        UsdGeom.Xformable(camera).AddTransformOp().Set(mat);get_active_viewport().camera_path='/ReachCamera'
        if args.require_wrap:
            side_camera=UsdGeom.Camera.Define(stage,'/GripSideCamera');side_camera.CreateClippingRangeAttr((.01,1000));side_camera.CreateFocalLengthAttr(36)
            look_at=handle+np.array([0,0,args.lift_height+.01]);eye_at=look_at+np.array([-.38,-.38,.18])
            side_mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye_at),Gf.Vec3d(*look_at),Gf.Vec3d(0,0,1)).GetInverse()
            UsdGeom.Xformable(side_camera).AddTransformOp().Set(side_mat)
            end_camera=UsdGeom.Camera.Define(stage,'/GripEndCamera');end_camera.CreateClippingRangeAttr((.01,1000));end_camera.CreateFocalLengthAttr(36)
            axis=knife_rot[:,0].copy();axis[2]=0;axis/=np.linalg.norm(axis)
            if axis@desired_rotation[:,1]<0:axis=-axis
            end_eye=look_at+axis*.45+np.array([0,0,.12])
            end_mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(*end_eye),Gf.Vec3d(*look_at),Gf.Vec3d(0,0,1)).GetInverse()
            UsdGeom.Xformable(end_camera).AddTransformOp().Set(end_mat)
        if args.require_cutting_orientation:
            cooking_camera=UsdGeom.Camera.Define(stage,'/CookingCamera');cooking_camera.CreateClippingRangeAttr((.01,1000));cooking_camera.CreateFocalLengthAttr(28)
            expected=Rotation.from_rotvec(knife_rot[:,0]*math.radians(args.post_lift_roll_deg)).as_matrix()@knife_rot
            blade_direction=knife_rot@blade_vector_local;blade_direction/=np.linalg.norm(blade_direction)
            cooking_look=handle+blade_direction*.12+np.array([0,0,args.lift_height])
            cooking_eye=cooking_look+expected[:,2]*.65+np.array([0,0,.30])
            cooking_mat=Gf.Matrix4d().SetLookAt(Gf.Vec3d(*cooking_eye),Gf.Vec3d(*cooking_look),Gf.Vec3d(0,0,1)).GetInverse()
            UsdGeom.Xformable(cooking_camera).AddTransformOp().Set(cooking_mat)


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
    capture('kitchen_grasp_before.png')
    def execute(route,live=False):
        global current
        for next_q in route:
            begin_q=current.copy()
            steps=max(8,int(math.ceil(np.max(np.abs(next_q-begin_q))/math.radians(6*args.motion_time_scale)*240)))
            for i in range(steps):
                tick=time.monotonic();current=begin_q+(next_q-begin_q)*(i+1)/steps
                step(current,args.gui and i%8==0)
                if live:time.sleep(max(0,1/240-(time.monotonic()-tick)))
            if np.linalg.norm(handle_pose()[0]-handle)>.02:raise RuntimeError('Knife moved from the planned target')
        for _ in range(240):step(current,args.gui)
    status('approaching')
    execute(path[1:],live=args.gui)
    grasp_phase=True
    fingers=[i for i,n in enumerate(names) if n.startswith('right_rh_')]
    def contact_summary():
        if args.require_cutting_orientation:return handle_contact_summary()[0]
        forces=np.linalg.norm(contacts.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1)
        return {p.split('/')[-1]:float(f) for p,f in zip(right_bodies,forces) if f>.02}
    def pad_contact_details():
        forces,points,normals,distances,counts,starts=contacts.get_contact_force_data(dt=1/240)
        transforms=robot._articulation_view._physics_view.get_link_transforms()[0]
        details=[];inner_fingers=set()
        for bi,body in enumerate(right_bodies):
            name=body.split('/')[-1]
            if not name.startswith('right_rh_'):continue
            transform=transforms[robot._articulation_view.get_body_index(name)]
            rotation=Rotation.from_quat(transform[3:7]).as_matrix()
            for ci in range(int(starts[bi,0]),int(starts[bi,0]+counts[bi,0])):
                if forces[ci,0]<.05:continue
                if args.require_cutting_orientation and not points_on_handle(points[ci:ci+1])[0]:continue
                point_local=rotation.T@(points[ci]-transform[:3])
                tip_distance=None
                if name in finger_tip_axes:
                    axis,end,_=finger_tip_axes[name];tip_distance=float(end-np.dot(point_local,axis))
                inner=name.endswith('_proximal') or (tip_distance is not None and tip_distance>=.015)
                if inner and 'thumb' not in name:inner_fingers.add(name.removeprefix('right_rh_').split('_')[0])
                from_blade=handle_blade_end-float(((points[ci]-handle_pose()[0])@handle_pose()[1])@blade_axis_local)
                details.append({'body':name,'force_n':float(forces[ci,0]),'distance_from_fingertip_m':tip_distance,'distance_along_handle_from_blade_m':from_blade,'inner_finger_contact':inner,'point_in_hand_m':(palm_pose()[1].T@(points[ci]-palm_pose()[0])+PALM_OFFSET).tolist()})
        return sorted(inner_fingers),details
    def finger_enclosure():
        # Measure the curl relative to this handle, not just an actuator-angle threshold.
        links=robot._articulation_view._physics_view.get_link_transforms()[0]
        hand_position,hand_rotation=palm_pose();knife_position,knife_rotation=handle_pose()
        center=hand_rotation.T@(knife_position-hand_position)+PALM_OFFSET
        handle_axis=hand_rotation.T@knife_rotation[:,0];actual=robot.get_joint_positions()
        enclosing=[];details=[]
        for finger in ['index','middle','ring','pinky']:
            name='right_rh_'+finger+'_distal';tip_local=finger_tip_axes[name][2]
            link=links[robot._articulation_view.get_body_index(name)]
            tip_world=link[:3]+Rotation.from_quat(link[3:7]).as_matrix()@tip_local
            tip=hand_rotation.T@(tip_world-hand_position)+PALM_OFFSET
            line_z=float(center[2]+(tip[1]-center[1])*handle_axis[2]/handle_axis[1]) if abs(handle_axis[1])>.5 else float(center[2])
            flex=float(np.rad2deg(actual[names.index('right_rh_'+finger+'_mcp_pitch')]+actual[names.index('right_rh_'+finger+'_dip')]))
            wraps=bool(flex>=115 and tip[2]<=line_z+.003)
            if wraps:enclosing.append(finger)
            details.append({'finger':finger,'total_flex_deg':flex,'tip_in_hand_m':tip.tolist(),'handle_center_z_at_tip_y_m':line_z,'wraps_handle':wraps})
        return enclosing,details
    def grip_friction():
        forces,points,counts,starts=contacts.get_friction_data(dt=1/240)
        return {body.split('/')[-1]:forces[int(starts[i,0]):int(starts[i,0]+counts[i,0])].sum(0).tolist() for i,body in enumerate(right_bodies) if counts[i,0]>0}
    def move_palm(target_position,duration=3.,stop_on_touch=False,touch_finger=None,touch_force=1.5):
        global current
        start=kin.pose(current[right])[0];q=current[right].copy();pivot=handle_pose()[0].copy()
        for wi,a in enumerate(np.linspace(0,1,61)[1:]):
            point=start+(target_position-start)*a;orientation=desired_rotation
            if lifting and args.lift_pitch_deg:
                bias=Rotation.from_rotvec(grip_knife_rotation[:,1]*math.radians(args.lift_pitch_deg)*a).as_matrix()
                orientation=bias@desired_rotation;point=pivot+bias@(start-pivot)+(target_position-start)*a
            q,e,ang=kin.solve(point,orientation,q)
            if e>.004 or ang>.04:raise RuntimeError('Grasp waypoint unreachable')
            endpoint=current.copy();endpoint[right]=q
            if lifting and args.lift_close_deg is not None:
                for finger in ['index','middle','ring','pinky']:
                    value=math.radians(90+(args.lift_close_deg-90)*min(1.,a*2))
                    endpoint[names.index('right_rh_'+finger+'_mcp_pitch')]=value
                    endpoint[names.index('right_rh_'+finger+'_dip')]=.89*value
            if lifting and args.lift_support_close_deg is not None and args.support_fingers!='none':
                for finger in args.support_fingers.split('-'):
                    value=math.radians(args.support_close_deg+(args.lift_support_close_deg-args.support_close_deg)*min(1.,a*2))
                    endpoint[names.index('right_rh_'+finger+'_mcp_pitch')]=value
                    endpoint[names.index('right_rh_'+finger+'_dip')]=.89*value
            count=max(6,int(duration/args.motion_time_scale*240/60),int(np.max(np.abs(endpoint-current))/math.radians(6*args.motion_time_scale)*240))
            initial=current.copy()
            for j in range(count):
                tick=time.monotonic();held_fingers=current[fingers].copy();current=initial+(endpoint-initial)*(j+1)/count
                if grip_feedback is not None:current[fingers]=held_fingers
                step(current,args.gui and j%8==0)
                touch_forces=np.linalg.norm(contacts.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1)
                if touch_finger is not None:touch_forces=touch_forces[[bi for bi,body in enumerate(right_bodies) if body.split('/')[-1].startswith('right_rh_'+touch_finger+'_')]]
                if stop_on_touch and max(touch_forces)>touch_force:
                    current[right]=robot.get_joint_positions()[right]
                    robot.apply_action(ArticulationAction(joint_positions=current))
                    print('CONTACT_DESCENT_STOP',json.dumps({'palm':palm_pose()[0].tolist(),'contacts':contact_summary()}),flush=True)
                    return
                if args.gui:time.sleep(max(0,1/240-(time.monotonic()-tick)))
            if lifting and (wi%10==0 or wi==59):print('LIFT_PROGRESS',json.dumps({'fraction':float(a),'palm':palm_pose()[0].tolist(),'handle':handle_pose()[0].tolist(),'contacts':contact_summary(),'knife_board_force_n':float(np.max(np.linalg.norm(knife_board.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1))),'knife_rotation_vector_deg':np.rad2deg(Rotation.from_matrix(grip_knife_rotation.T@handle_pose()[1]).as_rotvec()).tolist(),'knife_rotation_change_deg':float(np.rad2deg(Rotation.from_matrix(handle_pose()[1]@grip_knife_rotation.T).magnitude())),'friction_forces':grip_friction()}),flush=True)
    # Position the handle across the palm, leaving room for the fingers to curl.
    grasp_point=handle+np.array([0,0,args.palm_height])-desired_rotation[:,2]*args.finger_offset+desired_rotation[:,1]*args.handle_offset
    if args.tilt_deg or args.adjust_stance:grasp_point=handle-desired_rotation@np.array([args.palm_height,0,args.finger_offset])+desired_rotation[:,1]*args.handle_offset
    status('descending')
    move_palm(grasp_point,4.,stop_on_touch=args.contact_descent)
    for _ in range(240):step(current,args.gui)
    print('DESCENDED',json.dumps({'palm':palm_pose()[0].tolist(),'handle':handle_pose()[0].tolist(),'contacts':contact_summary()}),flush=True)
    capture('kitchen_grasp_descended.png')
    if args.seat_distance:
        sideways=desired_rotation[:,0].copy();sideways[2]=0;sideways/=np.linalg.norm(sideways)
        move_palm(kin.pose(current[right])[0]+sideways*args.seat_distance,2.,stop_on_touch=True,touch_finger='index')
        for _ in range(120):step(current,args.gui)
        print('SEATED',json.dumps({'palm':palm_pose()[0].tolist(),'contacts':contact_summary()}),flush=True)
    status('closing')
    closed=current.copy()
    for i in fingers:
        n=names[i]
        degrees={'right_rh_thumb_cmc_yaw':args.thumb_yaw_deg,'right_rh_thumb_cmc_pitch':args.close_thumb_pitch_deg if args.close_thumb_pitch_deg is not None else args.thumb_pitch_deg,'right_rh_thumb_ip':1.86*(args.close_thumb_pitch_deg if args.close_thumb_pitch_deg is not None else args.thumb_pitch_deg)}.get(n,args.close_deg if 'mcp' in n else .89*args.close_deg)
        if n.startswith('right_rh_pinky_') and args.pinky_close_deg is not None:degrees=args.pinky_close_deg if 'mcp' in n else .89*args.pinky_close_deg
        closed[i]=float(np.clip(math.radians(degrees),*kin.limits[n]))
    if args.support_fingers!='none':
        support_start=current.copy();support_end=current.copy()
        for finger in args.support_fingers.split('-'):
            support_end[names.index('right_rh_'+finger+'_mcp_pitch')]=math.radians(args.support_close_deg)
            support_end[names.index('right_rh_'+finger+'_dip')]=math.radians(.89*args.support_close_deg)
        for tick_index in range(720):
            tick=time.monotonic();a=(tick_index+1)/720;current=support_start+(support_end-support_start)*(3*a*a-2*a*a*a)
            step(current,args.gui and tick_index%8==0)
            if args.gui:time.sleep(max(0,1/240-(time.monotonic()-tick)))
        if not args.force_closure:
            for finger in args.support_fingers.split('-'):
                closed[names.index('right_rh_'+finger+'_mcp_pitch')]=support_end[names.index('right_rh_'+finger+'_mcp_pitch')]
                closed[names.index('right_rh_'+finger+'_dip')]=support_end[names.index('right_rh_'+finger+'_dip')]
        print('SUPPORT_CONTACTS',json.dumps(contact_summary()),flush=True)
    start=current.copy()
    closure_motion_deg=float(np.max(np.abs(np.rad2deg(closed[fingers]-start[fingers]))))
    closure_steps=max(2880,int((closure_motion_deg/args.closure_speed+3)*240)) if args.force_closure else 1200
    actuator_ids=[i for i in fingers if 'dip' not in names[i] and names[i]!='right_rh_thumb_ip']
    body_indices={p.split('/')[-1]:i for i,p in enumerate(right_bodies)}
    closure_sequence={'mode':'fingers_then_thumb' if args.fingers_first else 'simultaneous','fingers_established_before_thumb':False,'events':[]}
    finger_stage_ticks=0;finger_support_ticks=0;thumb_enabled=not args.fingers_first
    thumb_force_before_support=0.
    thumb_supported=not args.fingers_first;closure_feedback_ticks=0
    palm_seated=not args.seat_palm;seating_active=False;thumb_closure_allowed=palm_seated
    max_thumb_motion_before_support=0.
    def regulate_grip(target):
        global finger_stage_ticks,finger_support_ticks,thumb_enabled,thumb_force_before_support,thumb_supported,closure_feedback_ticks,max_thumb_motion_before_support
        closure_feedback_ticks+=1
        measured=np.linalg.norm(contacts.get_net_contact_forces(dt=1/240),axis=-1)
        actual=robot.get_joint_positions()
        if not thumb_enabled:
            finger_stage_ticks+=1;knife_forces=contact_summary()
            supporting=[f for f in ['index','middle','ring','pinky'] if sum(knife_forces.get('right_rh_'+f+'_'+part,0.) for part in ['proximal','distal'])>args.finger_support_force]
            thumb_force=sum(v for n,v in knife_forces.items() if n.startswith('right_rh_thumb_'))
            thumb_force_before_support=max(thumb_force_before_support,thumb_force)
            max_thumb_motion_before_support=max(max_thumb_motion_before_support,max(abs(float(np.rad2deg(actual[i]-start[i]))) for i in actuator_ids if 'thumb' in names[i]))
            if supporting and 'first_finger_contact_s' not in closure_sequence:closure_sequence['first_finger_contact_s']=finger_stage_ticks/240
            if len(supporting)>=2 and 'first_two_finger_contacts_s' not in closure_sequence:closure_sequence['first_two_finger_contacts_s']=finger_stage_ticks/240
            if thumb_force>.3 and 'first_thumb_contact_s' not in closure_sequence:
                closure_sequence['first_thumb_contact_s']=finger_stage_ticks/240;closure_sequence['finger_contacts_at_first_thumb_touch']=supporting
            if finger_stage_ticks%240==0:print('FINGER_STAGE_PROGRESS',json.dumps({'time_s':finger_stage_ticks/240,'contacts':knife_forces,'supporting_fingers':supporting}),flush=True)
            finger_support_ticks=finger_support_ticks+1 if len(supporting)>=args.finger_support_count else 0
            if finger_support_ticks>=max(1,int(args.finger_support_seconds*240)):
                thumb_enabled=True
                event={'time_s':closure_feedback_ticks/240,'supporting_fingers':supporting,'thumb_contact_n':thumb_force,'max_thumb_contact_before_support_n':thumb_force_before_support,'thumb_actual_deg':{names[i]:float(np.rad2deg(actual[i])) for i in actuator_ids if 'thumb' in names[i]}}
                fingers_moved_first=closure_sequence.get('first_finger_contact_s',float('inf'))<closure_sequence.get('first_thumb_contact_s',float('inf'))
                closure_sequence.update(fingers_established_before_thumb=bool(max_thumb_motion_before_support<3 and fingers_moved_first),max_thumb_motion_before_support_deg=max_thumb_motion_before_support,method=f'Fingers contact first; thumb closing commands held until {args.finger_support_count} fingers support for {args.finger_support_seconds} s. Incidental contact with the stationary thumb is reported separately.')
                closure_sequence['events'].append(event)
                print('FINGERS_SEATED_THUMB_ENABLED',json.dumps(event),flush=True);status('closing_thumb')
            elif finger_stage_ticks>18*240:raise RuntimeError(f'Fingers did not establish {args.finger_support_count} supporting contacts before thumb closure')
        if thumb_enabled and thumb_closure_allowed and not thumb_supported:
            thumb_force=sum(v for n,v in contact_summary().items() if n.startswith('right_rh_thumb_'))
            yaw_id=names.index('right_rh_thumb_cmc_yaw')
            if thumb_force>.5:
                thumb_supported=True;closure_sequence['thumb_opposed_before_final_squeeze']=True
                event={'time_s':closure_feedback_ticks/240,'thumb_contact_n':thumb_force,'phase':'firm_grip'};closure_sequence['events'].append(event)
                print('THUMB_OPPOSED_FIRM_GRIP',json.dumps(event),flush=True);status('firm_grip')
        for fi in actuator_ids:
            name=names[fi];direction=float(np.sign(closed[fi]-start[fi]))
            if not direction:continue
            prefix=name.removeprefix('right_rh_').split('_')[0]
            if args.fingers_first and not thumb_enabled and prefix=='index' and finger_stage_ticks<args.index_close_delay*240:
                target[fi]=start[fi];continue
            if prefix=='thumb' and (not thumb_enabled or not thumb_closure_allowed):
                target[fi]=start[fi];continue
            force=max(measured[bi] for bn,bi in body_indices.items() if bn.startswith('right_rh_'+prefix+'_'))
            if args.align_thumb_yaw and name=='right_rh_thumb_cmc_yaw':
                proposed=target[fi]+direction*math.radians(args.closure_speed)/240
                if force>args.thumb_yaw_force_limit:proposed=actual[fi]-direction*math.radians(.25)
                target[fi]=np.clip(proposed,min(start[fi],closed[fi]),max(start[fi],closed[fi]))
                continue
            if args.align_thumb_yaw and prefix=='thumb':force=measured[body_indices['right_rh_thumb_distal']]
            force_goal=args.thumb_contact_force if prefix=='thumb' else args.finger_contact_force
            if prefix=='middle' and args.middle_contact_force is not None:force_goal=args.middle_contact_force
            if prefix!='thumb' and not thumb_supported:force_goal=args.finger_seating_force
            if seating_active and prefix!='thumb':force_goal=.3
            speed=math.radians(args.closure_speed)*float(np.clip((force_goal-force)/force_goal,-1,1))
            proposed=target[fi]+direction*speed/240
            if force>2*force_goal:proposed=actual[fi]-direction*math.radians(.25)
            target[fi]=np.clip(proposed,min(start[fi],closed[fi]),max(start[fi],closed[fi]))
        for finger in ['index','middle','ring','pinky']:
            target[names.index('right_rh_'+finger+'_dip')]=.89*target[names.index('right_rh_'+finger+'_mcp_pitch')]
        target[names.index('right_rh_thumb_ip')]=1.86*target[names.index('right_rh_thumb_cmc_pitch')]
    if args.force_closure:grip_feedback=regulate_grip
    if args.fingers_first:
        status('closing_fingers')
        closure_steps+=int((max(abs(args.thumb_yaw_deg-args.prethumb_yaw_deg),abs((args.close_thumb_pitch_deg if args.close_thumb_pitch_deg is not None else args.thumb_pitch_deg)-args.thumb_pitch_deg))/args.closure_speed+9)*240)
    fingers_seated_captured=False;stable_closure_ticks=0
    for i in range(closure_steps):
        tick=time.monotonic()
        if not args.force_closure:
            a=(i+1)/closure_steps;current=start+(closed-start)*(3*a*a-2*a*a*a)
        step(current,args.gui and i%8==0)
        if args.fingers_first and thumb_enabled and not palm_seated:
            seating_active=True;status('seating_palm')
            local=palm_pose()[1].T@(handle_pose()[0]-palm_pose()[0])+PALM_OFFSET
            move_palm(kin.pose(current[right])[0]+desired_rotation[:,2]*(local[2]-args.seat_z),3.,True,'thumb',12.)
            local=palm_pose()[1].T@(handle_pose()[0]-palm_pose()[0])+PALM_OFFSET
            move_palm(kin.pose(current[right])[0]+desired_rotation[:,0]*(local[0]-args.seat_x),3.,True,'thumb',12.)
            local=palm_pose()[1].T@(handle_pose()[0]-palm_pose()[0])+PALM_OFFSET
            closure_sequence['palm_seating']={'actual_handle_in_hand_m':local.tolist(),'target_x_m':args.seat_x,'target_z_m':args.seat_z}
            (ROOT/'logs/kitchen_grasp_palm_seating.json').write_text(json.dumps({'configuration':vars(args),'closure_sequence':closure_sequence,'contacts':contact_summary()},indent=2))
            print('PALM_SEATED',json.dumps(closure_sequence['palm_seating']),flush=True)
            seating_active=False;palm_seated=True;thumb_closure_allowed=True;thumb_enabled=False;finger_stage_ticks=0;finger_support_ticks=0;status('closing_fingers')
        if args.gui and args.fingers_first and thumb_enabled and not fingers_seated_captured:
            fingers_seated_captured=True;capture('kitchen_grasp_fingers_seated.png')
        if args.finish_closure_when_stable and thumb_supported and i%12==0:
            inner,_=pad_contact_details();enclosing,_=finger_enclosure();cc=contact_summary()
            touching=[f for f in enclosing if sum(cc.get('right_rh_'+f+'_'+part,0.) for part in ['proximal','distal'])>.1]
            actual=robot.get_joint_positions();stationary=float(np.max(np.abs(robot.get_joint_velocities()[fingers])))<.05
            supported=len(set(inner)&set(touching))>=2 and len(touching)>=3 and cc.get('right_rh_hand_base_link',0.)>.1 and sum(v for n,v in cc.items() if n.startswith('right_rh_thumb_'))>.1
            opposed=float(np.rad2deg(actual[names.index('right_rh_thumb_cmc_yaw')]))>=min(45,args.thumb_yaw_deg-2)
            stable_closure_ticks=stable_closure_ticks+12 if stationary and supported and opposed else 0
            if stable_closure_ticks>=240:
                closure_sequence['finished_after_stationary_wrapped_support']=True;break
        if args.gui:time.sleep(max(0,1/240-(time.monotonic()-tick)))
    for _ in range(240):step(current,args.gui)
    for _ in range(240):step(current,args.gui)
    closure_sequence['closure_duration_s']=closure_feedback_ticks/240
    print('GRIP_VECTORS',json.dumps({p.split('/')[-1]:f.tolist() for p,f in zip(right_bodies,contacts.get_contact_force_matrix(dt=1/240)[:,0,:]) if np.linalg.norm(f)>.02}),flush=True)
    force_data,point_data,normal_data,distance_data,count_data,start_data=contacts.get_contact_force_data(dt=1/240)
    contact_details=[]
    for bi,body in enumerate(right_bodies):
        for ci in range(int(start_data[bi,0]),int(start_data[bi,0]+count_data[bi,0])):
            if force_data[ci,0]<.02:continue
            contact_details.append({'body':body.split('/')[-1],'force_n':float(force_data[ci,0]),'point_world':point_data[ci].tolist(),'normal':normal_data[ci].tolist(),'relative_to_handle_knife_frame':((point_data[ci]-handle_pose()[0])@handle_pose()[1]).tolist()})
    print('CONTACT_DETAILS',json.dumps(contact_details),flush=True)
    closure_contacts=contact_summary();before_lift=handle_pose()[0].copy();relative_before=palm_pose()[1].T@(before_lift-palm_pose()[0])
    pre_lift={'configuration':vars(args),'contacts':closure_contacts,'palm_world':palm_pose()[0].tolist(),'handle_in_palm_frame_m':relative_before.tolist(),'knife_rotation_world':handle_pose()[1].tolist(),'closure_sequence':closure_sequence,'board_forces':{p.split('/')[-1]:f.tolist() for p,f in zip(right_bodies,contacts.get_contact_force_matrix(dt=1/240)[:,1,:]) if np.linalg.norm(f)>.1},'net_forces':{p.split('/')[-1]:f.tolist() for p,f in zip(right_bodies,contacts.get_net_contact_forces(dt=1/240)) if np.linalg.norm(f)>.1},'handle':before_lift.tolist(),'finger_actual_deg':{names[i]:float(np.rad2deg(robot.get_joint_positions()[i])) for i in fingers}}
    (ROOT/'logs/kitchen_grasp_pre_lift.json').write_text(json.dumps(pre_lift,indent=2));print('GRIP_CLOSED',json.dumps(pre_lift),flush=True)
    if args.require_cutting_orientation:
        inner,_=pad_contact_details();enclosing,_=finger_enclosure()
        pre_lift.update(inner_finger_contacts=inner,enclosing_fingers=enclosing)
        (ROOT/'logs/kitchen_grasp_pre_lift.json').write_text(json.dumps(pre_lift,indent=2))
        if closure_contacts.get('right_rh_hand_base_link',0.)<.1 or len(set(inner)&set(enclosing))<2 or len(enclosing)<3:raise RuntimeError('Handle not seated in a wrapped palm grip; lift not attempted')
    capture('kitchen_grasp_closed.png')
    grip_knife_rotation=handle_pose()[1]
    lifting=True
    status('lifting')
    move_palm(kin.pose(current[right])[0]+np.array([0,0,args.lift_height]),4.)
    if args.post_lift_roll_deg:
        status('turning_wrist')
        pivot,knife_rotation=handle_pose();hand_position,hand_rotation=palm_pose()
        relative=hand_rotation.T@(pivot-hand_position);axis=knife_rotation[:,0]
        duration=max(4.,abs(args.post_lift_roll_deg)/6.)/args.motion_time_scale
        for wi,a in enumerate(np.linspace(0,1,76)[1:]):
            orientation=Rotation.from_rotvec(axis*math.radians(args.post_lift_roll_deg)*a).as_matrix()@hand_rotation
            point=pivot-orientation@relative
            q,e,ang=kin.solve(point,orientation,current[right])
            if e>.004 or ang>.04:raise RuntimeError('Cutting-pose wrist turn is unreachable')
            endpoint=current.copy();endpoint[right]=q;initial=current.copy()
            count=max(6,int(duration*240/75),int(np.max(np.abs(endpoint-current))/math.radians(6*args.motion_time_scale)*240))
            for j in range(count):
                tick=time.monotonic();held_fingers=current[fingers].copy();current=initial+(endpoint-initial)*(j+1)/count;current[fingers]=held_fingers
                step(current,args.gui and j%8==0)
                if float(np.max(np.linalg.norm(knife_board.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1)))>.1:raise RuntimeError('Knife contacted board during wrist turn')
                if args.gui:time.sleep(max(0,1/240-(time.monotonic()-tick)))
        for _ in range(240):step(current,args.gui)
        print('WRIST_TURN_FINISHED',json.dumps(cutting_orientation()),flush=True)
    status('holding')
    hold=[]
    for i in range(720):
        step(current,args.gui and i%8==0)
        if i%30==0:
            inner,_=pad_contact_details();enclosing,_=finger_enclosure();sample_contacts=contact_summary();actual=robot.get_joint_positions()
            enclosing_contacts=[finger for finger in enclosing if sum(sample_contacts.get('right_rh_'+finger+'_'+part,0) for part in ['proximal','distal'])>.1]
            hold.append({'height':float(handle_pose()[0][2]),'contacts':sample_contacts,'board_force_n':float(np.max(np.linalg.norm(knife_board.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1))),
                         'cutting_orientation':cutting_orientation(),'inner_finger_contacts':inner,'enclosing_contact_fingers':enclosing_contacts,'palm_contact_n':sample_contacts.get('right_rh_hand_base_link',0.),'thumb_contact_n':sum(f for n,f in sample_contacts.items() if n.startswith('right_rh_thumb_')),
                         'curled_fingers':sum(float(np.rad2deg(actual[names.index('right_rh_'+finger+'_mcp_pitch')]))>=70 for finger in ['index','middle','ring','pinky'])})
    lifted=handle_pose()[0];relative_after=palm_pose()[1].T@(lifted-palm_pose()[0]);lift=float(lifted[2]-before_lift[2]);slip=float(np.linalg.norm(relative_after-relative_before))
    final_contacts=contact_summary()
    actual_fingers=robot.get_joint_positions()
    proximal_contacts=[f for f in ['index','middle','ring','pinky'] if final_contacts.get('right_rh_'+f+'_proximal',0)>.1]
    finger_contacts=[f for f in ['index','middle','ring','pinky'] if sum(final_contacts.get('right_rh_'+f+'_'+part,0) for part in ['proximal','distal'])>.1]
    curled_fingers=[f for f in ['index','middle','ring','pinky'] if np.rad2deg(actual_fingers[names.index('right_rh_'+f+'_mcp_pitch')])>=70]
    palm_support=final_contacts.get('right_rh_hand_base_link',0)>.1
    thumb_support=sum(v for n,v in final_contacts.items() if n.startswith('right_rh_thumb_'))>.1
    handle_in_hand=palm_pose()[1].T@(lifted-palm_pose()[0])+PALM_OFFSET
    inner_fingers,pad_details=pad_contact_details()
    enclosing_fingers,enclosure_details=finger_enclosure()
    enclosing_contacts=sorted(set(enclosing_fingers)&set(finger_contacts))
    wrap_checks={'palm_contact':palm_support,'thumb_contact':thumb_support,'at_least_two_contacts_away_from_tips':len(set(inner_fingers)&set(enclosing_contacts))>=2,'at_least_three_fingers_contact':len(finger_contacts)>=3,'at_least_three_fingers_wrap_and_contact':len(enclosing_contacts)>=3,'handle_near_palm':bool(0<handle_in_hand[0]<.045 and .055<handle_in_hand[2]<.105)}
    wrap_checks['wrap_retained_during_hold']=all(len(set(x['inner_finger_contacts'])&set(x['enclosing_contact_fingers']))>=2 and x['palm_contact_n']>.1 and x['thumb_contact_n']>.1 and len(x['enclosing_contact_fingers'])>=3 for x in hold)
    wrapped=all(wrap_checks.values())
    wrap_metrics={'passed':wrapped,'method':'Palm and opposed thumb support; three contacting fingers curl past the handle center with >=115 degrees total flexion; two contact proximal links or pads >=15 mm from their tips; retained for 3 s','inner_pad_min_distance_m':.015,'enclosure_center_margin_m':.003,'enclosing_contact_fingers':enclosing_contacts,'finger_enclosure':enclosure_details,'inner_finger_contacts':inner_fingers,'contact_details':pad_details,'checks':wrap_checks,'proximal_contacts':proximal_contacts,'finger_contacts':finger_contacts,'curled_fingers':curled_fingers,'handle_in_hand_m':handle_in_hand.tolist()}
    knife_board_force=float(np.max(np.linalg.norm(knife_board.get_contact_force_matrix(dt=1/240)[:,0,:],axis=-1)))
    passed=knife_board_force<.05 and max(x['board_force_n'] for x in hold)<.05 and lift>.02 and slip<.015 and len(final_contacts)>=2 and (max(x['height'] for x in hold)-min(x['height'] for x in hold))<.01
    lift_passed=passed
    orientation_metrics=cutting_orientation()
    orientation_keys=['blade_exits_thumb_index_side','blade_points_away_from_robot','cutting_edge_faces_board']
    orientation_passed=all(orientation_metrics[k] for k in orientation_keys) and all(all(x['cutting_orientation'][k] for k in orientation_keys) for x in hold)
    sequence_passed=closure_sequence['fingers_established_before_thumb'] and closure_sequence.get('thumb_opposed_before_final_squeeze',False) if args.fingers_first else True
    passed=lift_passed and (wrapped if args.require_wrap else True) and (orientation_passed if args.require_cutting_orientation else True) and sequence_passed
    report={'passed':passed,'lift_passed':lift_passed,'wrap_grasp':wrap_metrics,'controller_sha256':controller_sha256,'controller_type':'Scripted IK and joint-drive targets; no RL training','final_knife_rotation_world':handle_pose()[1].tolist(),'initial_handle_world_m':handle.tolist(),'knife_path':meta['knife_path'],'duplicate_knife_created':False,'grasp_attachment_created':False,'knife_collision':'Separate blade and handle hulls on the existing rigid body',
            'configuration':vars(args),'cutting_orientation':orientation_metrics,'closure_sequence':closure_sequence,'board_shift_m':board_shift.tolist() if board_shift is not None else None,'stance':{key:seed[key] for key in ['root_yaw_deg','root_offset_xy','roll_deg','orientation'] if key in seed},'closure_contact_details':contact_details,'knife_board_force_n':knife_board_force,'lift_m':lift,'relative_slip_m':slip,'relative_slip_frame':'hand','hold_seconds':3,'closure_contacts_n':closure_contacts,'final_contacts_n':final_contacts,'hold_samples':hold,
            'max_contact_n':max_contact,'thumb_pitch_deg':args.thumb_pitch_deg,'thumb_yaw_deg':args.thumb_yaw_deg,'tilt_deg':args.tilt_deg,'palm_height_setting_m':args.palm_height,'finger_offset_setting_m':args.finger_offset,'handle_offset_setting_m':args.handle_offset,
            'finger_torque_limit_nm':args.finger_torque,'mimic_followers_passive':True,'static_friction':args.static_friction,'dynamic_friction':args.dynamic_friction,'knife_mass_kg':.25,
            'limitations':['Provisional rigid-body grip and friction settings; not calibrated to hardware','Robot self-collision disabled','Simplified kitchen materials and nearby kitchen collisions only']}
    index_distances=[x['distance_along_handle_from_blade_m'] for x in pad_details if 'index_' in x['body'] and x['force_n']>.1]
    report.update(scene_setup=scene_setup,index_distance_from_blade_m=min(index_distances) if index_distances else None,timing={'elapsed_wall_seconds':time.monotonic()-run_started,'phase_starts':phase_times})
    (ROOT/'logs/kitchen_grasp_report.json').write_text(json.dumps(report,indent=2))
    capture('kitchen_grasp_lifted.png')
    if args.gui and args.require_wrap:
        get_active_viewport().camera_path='/GripSideCamera';capture('kitchen_grasp_wrapped_side.png')
        get_active_viewport().camera_path='/GripEndCamera';capture('kitchen_grasp_wrapped_end.png')
        get_active_viewport().camera_path='/GripSideCamera'
    if args.gui and args.require_cutting_orientation:
        get_active_viewport().camera_path='/CookingCamera';capture('kitchen_grasp_cooking_pose.png')
    print('GRASP_RESULT',json.dumps(report),flush=True)
    if not passed:raise RuntimeError('Physical grasp/lift acceptance checks did not pass')
    status('passed')
    if args.interactive:
        import omni.ui as ui
        window=ui.Window('Kitchen knife — grip and lift',width=460,height=235 if args.fingers_first else 195)
        with window.frame:
            with ui.VStack(spacing=8):
                ui.Label('Physical finger contact | existing kitchen knife')
                ui.Label(f'Knife lifted {lift*100:.2f} cm. Holding the grip.')
                ui.Label(('Palm-supported wrapped contact' if wrapped else 'Fingertip/pinch grasp; wrapped grasp not validated')+' | handle overhanging board')
                ui.Label('Scripted motion | no trained policy')
                if args.fingers_first:ui.Label('Fingers first, then thumb | blade outward, edge toward board')
                ui.Label('Memory safeguard active.')
        status('interactive');print('GRASP_INTERACTIVE_READY',flush=True)
        hold_frame=0;lost_wrap_checks=0
        while app.is_running():
            tick=time.monotonic()
            for _ in range(8):step(current)
            if handle_pose()[0][2]<before_lift[2]+.015:raise RuntimeError('Grip lost during interactive hold')
            hold_frame+=1
            if args.require_wrap and hold_frame%15==0:
                inner,_=pad_contact_details();enclosing,_=finger_enclosure();live_contacts=contact_summary()
                enclosing_contacts=[finger for finger in enclosing if sum(live_contacts.get('right_rh_'+finger+'_'+part,0) for part in ['proximal','distal'])>.1]
                retained=len(set(inner)&set(enclosing_contacts))>=2 and len(enclosing_contacts)>=3 and live_contacts.get('right_rh_hand_base_link',0)>.1 and sum(f for n,f in live_contacts.items() if n.startswith('right_rh_thumb_'))>.1
                lost_wrap_checks=0 if retained else lost_wrap_checks+1
                if lost_wrap_checks>=2:raise RuntimeError('Wrapped contact lost during interactive hold')
            if args.require_cutting_orientation and hold_frame%15==0:
                live_orientation=cutting_orientation()
                if not all(live_orientation[k] for k in orientation_keys):raise RuntimeError('Cutting orientation lost during interactive hold')
            world.render();time.sleep(max(0,1/30-(time.monotonic()-tick)))
except SceneInspectionComplete:
    status('scene_inspected');print('SCENE_INSPECTION_COMPLETE',flush=True)
except BaseException as exc:
    traceback.print_exc();print('GRASP_FAILED',str(exc),flush=True);status('failed',error=str(exc))
    raise
finally:
    app.close()
