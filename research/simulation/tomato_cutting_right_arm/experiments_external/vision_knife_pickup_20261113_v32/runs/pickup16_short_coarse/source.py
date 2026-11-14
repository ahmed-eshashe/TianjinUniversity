"""Contact-driven pickup feasibility from a reset pregrasp. State-informed teacher; no learning claim."""
from pathlib import Path
import argparse,json,sys,time,traceback,hashlib
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--shift',type=float,default=-.025);a.add_argument('--goal-force',type=float,default=4.);a.add_argument('--lift',type=float,default=.10);a.add_argument('--grasp',type=Path);a.add_argument('--freeze-lift',action='store_true');a.add_argument('--thumb-force',type=float,default=10.);a.add_argument('--compliant',action='store_true');a.add_argument('--thumb-effort',type=float,default=.14);a.add_argument('--finger-effort',type=float,default=.035);a.add_argument('--hand-damping',type=float,default=.15);a.add_argument('--velocity-iterations',type=int);a.add_argument('--solver',type=int,default=1);a.add_argument('--close-seconds',type=float,default=2.5);a.add_argument('--lift-route',type=Path);a.add_argument('--lift-seconds',type=float,default=4.);a.add_argument('--hold-seconds',type=float,default=4.);a.add_argument('--render',action='store_true');a.add_argument('--scene',type=Path);a.add_argument('--physics-hz',type=int,default=960);a.add_argument('--neutral-start',type=Path);a.add_argument('--dx',type=float,default=0.);a.add_argument('--dy',type=float,default=0.);a.add_argument('--yaw-deg',type=float,default=0.);args=a.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);app=sim=None;records=[];phase='startup';success=False;(out/'source.py').write_text(Path(__file__).read_text())
try:
 import numpy as np,torch
 from scipy.spatial.transform import Rotation,Slerp
 from scipy.spatial import ConvexHull
 from contact_budget import FixedWindowLoads
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=True,enable_cameras=args.render,device='cpu',visualizer=['none']).app
 import isaaclab.sim as su
 from isaaclab_physx.physics import PhysxCfg,PhysxManager
 from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
 from isaaclab.actuators import ImplicitActuatorCfg
 from isaaclab.app.settings_manager import get_settings_manager
 from pxr import Usd,UsdGeom,UsdPhysics,PhysxSchema,Gf
 from reach_kinematics import ArmKinematics,PALM_OFFSET
 c=json.loads((W/'scene_config.json').read_text());criteria=json.loads((W/'pickup_criteria.json').read_text());template=json.loads((R/'runs/rl/phase3/central_grasp_13/before_lift.json').read_text());row=min(json.loads((W/'reports/initial_grasp_reach.json').read_text()),key=lambda x:abs(x['handle_axis_shift_m']-args.shift));relative=np.array(row['hand_from_knife']);pose=np.array(json.loads((W/'runs/camera01/result.json').read_text())['knife_pose'])
 initial_rotation=Rotation.from_quat(pose[3:]).as_matrix();handle_local=np.array([-.0860033812,.0076461609,.001586524]);handle_world=pose[:3]+initial_rotation@handle_local;new_rotation=Rotation.from_euler('z',args.yaw_deg,degrees=True).as_matrix()@initial_rotation;pose[:3]=handle_world-new_rotation@handle_local+[args.dx,args.dy,0.];pose[3:]=Rotation.from_matrix(new_rotation).as_quat()
 if args.grasp:
  row=json.loads(args.grasp.read_text());relative=np.array(row['hand_from_knife'])
 if args.scene:c['scene']=str(args.scene.resolve())
 dt=1/args.physics_hz;sim=su.SimulationContext(su.SimulationCfg(device='cpu',dt=dt,gravity=(0,0,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=args.solver,max_velocity_iteration_count=255 if args.velocity_iterations is None else args.velocity_iterations),log_dir=str(out)));sim.stage.GetRootLayer().subLayerPaths.append(c['scene'])
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/KitchenEnvironment')):
  if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Set(False)
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).GetRigidBodyEnabledAttr().Set(False)
  if prim.IsA(UsdPhysics.Joint):prim.SetActive(False)
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/dual_ar5_o6')):
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
  if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
   api=PhysxSchema.PhysxArticulationAPI.Apply(prim);api.CreateSolverPositionIterationCountAttr(64);api.CreateSolverVelocityIterationCountAttr(16 if args.velocity_iterations is None else args.velocity_iterations)
 refined=[]
 for x in json.loads((R/'work/single_slice_20261106/wrist_collision_shapes.json').read_text()):
  prim=sim.stage.GetPrimAtPath(x['path']);api=PhysxSchema.PhysxConvexDecompositionCollisionAPI.Apply(prim);api.CreateMaxConvexHullsAttr(128);api.CreateHullVertexLimitAttr(64);api.CreateVoxelResolutionAttr(1000000);api.CreateErrorPercentageAttr(1.);api.CreateShrinkWrapAttr(True);api.CreateMinThicknessAttr(.0001);refined.append(x['path'])
 def matrix(p):
  m=np.eye(4);m[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();m[:3,3]=p[:3];return m
 kin=ArmKinematics(sim.stage);K=matrix(pose);contact_T=K@relative;pre=contact_T.copy();pre[2,3]+=.045
 home=dict(c['home_rad']);q,pe,re=kin.solve(pre[:3,3]+pre[:3,:3]@PALM_OFFSET,pre[:3,:3],row['q']);assert pe<.0002 and re<.002
 initialq=q.copy();start_T=pre.copy()
 for n,v in zip(kin.names,q):home[n]=v
 fingers=['index','middle','ring','pinky'];hand_names=['right_rh_thumb_cmc_yaw','right_rh_thumb_cmc_pitch']+['right_rh_'+f+'_mcp_pitch' for f in fingers]
 grasp_hand=np.array(row['hand_joint_rad']) if args.grasp else np.array([template['q_rad'][7],.134,*template['q_rad'][9:]])
 pre_hand=grasp_hand.copy();pre_hand[1]=max(.015,pre_hand[1]-.07);pre_hand[2:]-=.10
 for n,v in zip(hand_names,pre_hand):home[n]=v
 if args.neutral_start:
  neutral=json.loads(args.neutral_start.read_text());initialq=np.array(neutral['arm_joint_rad']);start_T=np.array(neutral['hand_root_world'])
  for n,v in zip(kin.names,initialq):home[n]=v
  for n,v in zip(hand_names,[grasp_hand[0],.015,.1,.1,.1,.1]):home[n]=v
 home['right_rh_thumb_ip']=1.86*home['right_rh_thumb_cmc_pitch']
 for f in fingers:home['right_rh_'+f+'_dip']=.89*home['right_rh_'+f+'_mcp_pitch']
 root=np.array(c['robot_root_world_matrix']);r=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(root[:3,3]),rot=tuple(Rotation.from_matrix(root[:3,:3]).as_quat()),joint_pos=home),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'fingers':ImplicitActuatorCfg(joint_names_expr=['.*_(index|middle|ring|pinky)_mcp_pitch'],stiffness=3.,damping=args.hand_damping,effort_limit_sim=.3),'thumb':ImplicitActuatorCfg(joint_names_expr=['.*_thumb_cmc_(yaw|pitch)'],stiffness=10.,damping=args.hand_damping,effort_limit_sim=1.),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
 knife=RigidObject(RigidObjectCfg(prim_path=c['knife_path'],spawn=None,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(pose[:3]),rot=tuple(pose[3:]))))
 cameras={}
 if args.render:
  from isaaclab.sensors.camera import Camera,CameraCfg
  from isaaclab_physx.renderers import IsaacRtxRendererCfg
  from PIL import Image
  eye=np.array([.38,-1.18,.75]);look=np.array([-.055,-.72,.23]);forward=look-eye;forward/=np.linalg.norm(forward);rightview=np.cross(forward,[0,0,1]);rightview/=np.linalg.norm(rightview);up=np.cross(rightview,forward);C=np.eye(4);C[:3,:3]=np.column_stack([rightview,up,-forward]);C[:3,3]=eye
  UsdGeom.Xform.Define(sim.stage,'/PickupReview');cam=UsdGeom.Camera.Define(sim.stage,'/PickupReview/Camera');cam.AddTransformOp().Set(Gf.Matrix4d(C.T.tolist()));cam.CreateFocalLengthAttr(20.);cam.CreateHorizontalApertureAttr(20.955);cam.CreateVerticalApertureAttr(15.71625);cam.CreateClippingRangeAttr(Gf.Vec2f(.03,3.))
  for key,path,width,height in [('head',c['camera_path'],320,240),('review','/PickupReview/Camera',800,600)]:cameras[key]=Camera(CameraCfg(prim_path=path,spawn=None,width=width,height=height,data_types=['rgb','distance_to_image_plane'],update_period=0.,renderer_cfg=IsaacRtxRendererCfg()))
 def capture(label):
  if not args.render:return
  for _ in range(12):
   sim.render()
   for camera in cameras.values():camera.update(dt,force_recompute=True)
  for key,camera in cameras.items():
   v=camera.data.output['rgb'];v=v.torch.cpu().numpy() if hasattr(v,'torch') else v.numpy();Image.fromarray(v[0,:,:,:3].astype('uint8')).save(out/(label+'_'+key+'.png'))
 sim.reset();r.update(dt);knife.update(dt);get_settings_manager().set_bool('/physics/disableContactProcessing',False)
 target=torch.tensor([[home[n] for n in r.joint_names]],dtype=torch.float32);r.write_joint_state_to_sim_index(position=target,velocity=torch.zeros_like(target));right=[r.joint_names.index(n) for n in kin.names];arms=[i for i,n in enumerate(r.joint_names) if '_AR5_' in n];hids=[r.joint_names.index(n) for n in hand_names];palm_id=r.body_names.index('right_rh_hand_base_link')
 bodies=[str(x.GetPath()) for x in sim.stage.Traverse() if str(x.GetPath()).startswith('/dual_ar5_o6/') and x.HasAPI(UsdPhysics.RigidBodyAPI) and UsdPhysics.RigidBodyAPI(x).GetRigidBodyEnabledAttr().Get()!=False];filters=bodies+[c['board_path'],c['counter_path']];view=PhysxManager.get_physics_sim_view().create_rigid_contact_view(bodies,[filters for _ in bodies],max_contact_data_count=8192);ki=filters.index(c['knife_path']);kb=bodies.index(c['knife_path']);hands=[i for i,n in enumerate(bodies) if '/right_rh_' in n]
 handle=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());blade=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());heq=ConvexHull(handle).equations;beq=ConvexHull(blade).equations;knife_points=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path'])).GetPointsAttr().Get());hc=(handle.min(0)+handle.max(0))/2
 assert not any(p.IsA(UsdPhysics.Joint) and c['knife_path'] in [str(x) for rel in [UsdPhysics.Joint(p).GetBody0Rel(),UsdPhysics.Joint(p).GetBody1Rel()] for x in rel.GetTargets()] for p in sim.stage.Traverse())
 (out/'configuration.json').write_text(json.dumps(dict(args={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},criteria=criteria,pregrasp=q.tolist(),hand_from_knife=relative.tolist(),refined_collision_shapes=refined,source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='State-informed, reset-pregrasp physical component. Not a neutral-pose pickup or learned policy.'),indent=2))
 def arr(x):return x.numpy() if hasattr(x,'numpy') else np.asarray(x)
 material_view=PhysxManager.get_physics_sim_view().create_rigid_body_view([c['knife_path']]);(out/'runtime_knife_materials.json').write_text(json.dumps(arr(material_view.get_material_properties()).tolist()))
 load_window=FixedWindowLoads(args.physics_hz);step=0;hold=0.;reference=None;initial_height=None;lowpass={f:0. for f in ['thumb',*fingers]};last=None;maximum_contact=0.;last_ik=initialq.copy();close_start_s=0.;start=time.monotonic();max_force_seen=0.;max_mimic_error=0.;grip_ready_s=0.
 def observe():
  global maximum_contact
  fp,points,normals,separations,count,starts=[arr(v) for v in view.get_contact_data(dt=dt)];fm=arr(view.get_contact_force_matrix(dt=dt));mag=np.linalg.norm(fm,axis=-1);tp=knife.data.root_pose_w.torch[0].cpu().numpy();T=matrix(tp);hp=r.data.body_link_pose_w.torch[0,palm_id].cpu().numpy();H=matrix(hp);contacts=[];loads={f:0. for f in ['thumb',*fingers]}
  if count.sum()>=8192:raise ValueError('Contact buffer full')
  guard_mag=load_window.update(mag);bad=[]
  for i,j in np.argwhere(guard_mag>.1):
   value=float(guard_mag[i,j]);b,other=bodies[i],filters[j]
   if value>50:bad.append((b,other,value))
   if other==c['knife_path'] and i not in hands and b!=c['knife_path']:bad.append(('Knife touched other robot link',b,value))
   if b!=c['knife_path'] and other in [c['board_path'],c['counter_path']] and value>(10. if '/right_rh_' in b else 5.):bad.append((b,other,value))
  for i in hands:
   name=bodies[i].rsplit('/',1)[-1];part='palm' if name=='right_rh_hand_base_link' else name.removeprefix('right_rh_').split('_')[0]
   for j in range(int(starts[i,ki]),int(starts[i,ki]+count[i,ki])):
    force=float(fp[j,0]);local=(points[j]-tp[:3])@T[:3,:3];onhandle=bool(np.max(heq[:,:3]@local+heq[:,3])<=.003);onblade=bool(np.max(beq[:,:3]@local+beq[:,3])<=.003)
    if force>.05 and ((onblade and not onhandle) or not(onblade or onhandle)):raise ValueError(('Blade/unknown knife contact',part,force,local.tolist()))
    if onhandle and force>.05:
     contacts.append(dict(part=part,force_N=force,point=points[j].tolist(),normal=normals[j].tolist()))
     if part in loads:loads[part]+=force
  if bad:
   (out/'stop_state.json').write_text(json.dumps(dict(sim_s=step*dt,bad=bad,knife_pose=tp.tolist(),q=r.data.joint_pos.torch[0].tolist(),qd=r.data.joint_vel.torch[0].tolist(),contacts=contacts,hand_pose=hp.tolist(),target_q=target[0].tolist()),indent=2));raise ValueError(('Contact stop',bad[:5]))
  qnow=r.data.joint_pos.torch[0].cpu().numpy();limits=r.data.soft_joint_pos_limits.torch[0].cpu().numpy();speed=float(r.data.joint_vel.torch.abs().max())
  if not np.isfinite(qnow).all() or speed>3 or np.any(qnow<limits[:,0]-.005) or np.any(qnow>limits[:,1]+.005):raise ValueError(('Joint state stop',speed))
  hcworld=T[:3,:3]@hc+T[:3,3];world=knife_points@T[:3,:3].T+T[:3,3];support=float(sum(mag[kb,filters.index(p)] for p in [c['board_path'],c['counter_path']]));relative_actual=np.linalg.inv(H)@T;thumb=[x for x in contacts if x['part']=='thumb'];other=[x for x in contacts if x['part'] in fingers];opposed=any(np.dot(t['normal'],f['normal'])<-.5 for t in thumb for f in other)
  return dict(phase=phase,step=step,sim_s=step*dt,knife_pose=tp.tolist(),knife_velocity=knife.data.root_vel_w.torch[0].tolist(),q=qnow.tolist(),hand_pose=hp.tolist(),contacts=contacts,loads=loads,support_N=support,handle_height_m=float(hcworld[2]),minimum_tool_height_m=float(world[:,2].min()),opposed=opposed,relative_tool=relative_actual.tolist(),speed_rad_s=speed,force_max_N=float(guard_mag.max()),raw_step_force_max_N=float(mag.max()),other_contacts=[dict(body=bodies[i],other=filters[j],force_N=float(mag[i,j])) for i,j in np.argwhere(mag>.5) if bodies[i]!=c['knife_path'] and filters[j]!=c['knife_path']],body_names=r.body_names,body_poses=r.data.body_link_pose_w.torch[0].tolist(),minimum_contact_separation_m=float(np.min(separations[:int(count.sum())])) if count.sum() else None)
 def tick(qgoal,pressure=False):
  global step,last,hold,reference,initial_height,max_force_seen,max_mimic_error,grip_ready_s
  target[:,right]=torch.tensor(qgoal,dtype=torch.float32)
  if pressure and not args.compliant and step%4==0 and last is not None:
   for index,part in [(1,'thumb'),(2,'index'),(3,'middle'),(4,'ring'),(5,'pinky')]:
    lowpass[part]=.75*lowpass[part]+.25*last['loads'][part];rate=np.clip(((args.thumb_force if part=='thumb' else args.goal_force)-lowpass[part])*.02,-.08,.08);target[0,hids[index]]+=float(rate*4*dt)
    target[0,hids[index]]=float(np.clip(target[0,hids[index]],.015 if part=='thumb' else .6,min(.315,grasp_hand[index]+.12) if part=='thumb' else min(1.45,grasp_hand[index]+.15)))
  if pressure and args.compliant:
   actual=r.data.joint_pos.torch[0]
   for index,part in [(1,'thumb'),(2,'index'),(3,'middle'),(4,'ring'),(5,'pinky')]:
    stiffness=10. if part=='thumb' else 3.;eff=(args.thumb_effort if part=='thumb' else args.finger_effort)*min(1.,max(0.,(step*dt-close_start_s)/.5))
    target[0,hids[index]]=min(float(actual[hids[index]])+eff/stiffness,float(.315 if part=='thumb' else grasp_hand[index]+.10))
  effort=torch.zeros_like(target);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_position_target_index(target=target);r.set_joint_velocity_target_index(target=torch.zeros_like(target));r.set_joint_effort_target_index(target=effort);r.write_data_to_sim();knife.write_data_to_sim();sim.step(render=False);r.update(dt);knife.update(dt);step+=1
  last=observe();last['target_q']=target[0].tolist();max_force_seen=max(max_force_seen,last['force_max_N'])
  qactual=np.array(last['q']);errors=[abs(qactual[r.joint_names.index('right_rh_thumb_ip')]-1.86*qactual[hids[1]])]+[abs(qactual[r.joint_names.index('right_rh_'+f+'_dip')]-.89*qactual[hids[2+i]]) for i,f in enumerate(fingers)];max_mimic_error=max(max_mimic_error,max(errors))
  grip_ready_s=grip_ready_s+dt if last['opposed'] and last['loads']['thumb']>.3 and max(last['loads'][f] for f in fingers)>.3 else 0.
  if phase=='settle':initial_height=last['handle_height_m']
  ready=last['opposed'] and last['handle_height_m']>=initial_height+.05 and last['minimum_tool_height_m']>.003 and last['support_N']<.05
  if ready:
   rel=np.array(last['relative_tool'])
   if reference is None:reference=rel.copy()
   slip=float(np.linalg.norm(rel[:3,3]-reference[:3,3]));turn=float(Rotation.from_matrix(rel[:3,:3]@reference[:3,:3].T).magnitude());ready=slip<=.01 and turn<=.261799;last.update(slip_m=slip,rotation_drift_rad=turn)
  if ready:hold+=dt
  else:hold=0.;reference=None
  last['hold_s']=hold
  if step%24==0:records.append(last)
  if step%240==0:(out/'progress.json').write_text(json.dumps({k:last[k] for k in ['phase','sim_s','loads','support_N','handle_height_m','minimum_tool_height_m','opposed','hold_s']}))
  if last['handle_height_m']<-.04:raise ValueError('Knife dropped off support')
 def route(Tstart,Tend,seconds,pressure=False,hand_goal=None):
  global last_ik
  duration=round(seconds/dt);hand_start=target[0,hids].clone();knots=[];seed=last_ik.copy();orientations=Slerp([0,1],Rotation.from_matrix([Tstart[:3,:3],Tend[:3,:3]]))
  for u in np.linspace(0,1,81):
   b=u*u*u*(10-15*u+6*u*u);P=Tstart[:3,3]*(1-b)+Tend[:3,3]*b;orientation=orientations(b).as_matrix();seed,pe,re=kin.solve(P+orientation@PALM_OFFSET,orientation,seed)
   if pe>.0003 or re>.003:raise ValueError(('Route IK failure',pe,re))
   knots.append(seed.copy())
  for k in range(duration):
   u=(k+1)/duration*80;i=min(79,int(u));q=knots[i]*(1-(u-i))+knots[i+1]*(u-i)
   if hand_goal is not None:
    v=(k+1)/duration;b=v*v*v*(10-15*v+6*v*v);target[0,hids]=hand_start*(1-b)+torch.tensor(hand_goal,dtype=torch.float32)*b
   tick(q,pressure)
  last_ik=q.copy()
 phase='settle'
 for _ in range(round(.5/dt)):tick(last_ik)
 capture('start')
 if args.neutral_start:
  phase='approach';route(start_T,pre,4.,hand_goal=pre_hand)
 phase='descend';route(pre,contact_T,2.)
 phase='close';close_start_s=step*dt
 for _ in range(round(args.close_seconds/dt)):tick(last_ik,True)
 (out/'before_lift.json').write_text(json.dumps(last,indent=2));capture('grasp')
 if grip_ready_s<.2:raise ValueError(('Opposed handle support not sustained before lift',grip_ready_s))
 phase='lift';end=contact_T.copy();end[2,3]+=args.lift
 if args.lift_route:end=np.array(json.loads(args.lift_route.read_text())['end_hand_world'])
 route(contact_T,end,args.lift_seconds,not args.freeze_lift)
 phase='hold'
 for _ in range(round(args.hold_seconds/dt)):
  tick(last_ik,not args.freeze_lift)
  if hold>=3.:success=True;break
 capture('final')
 (out/'result.json').write_text(json.dumps(dict(success=success,scope='Scripted pickup from a fixed task start; not vision-driven or learned.' if args.neutral_start else 'Secure lift from a reset pregrasp; not neutral-start, vision-based or learned.',last=last,wall_s=time.monotonic()-start,maximum_contact_load_N=max_force_seen,maximum_mimic_error_rad=max_mimic_error),indent=2));print('RESULT',success,flush=True)
except BaseException:
 (out/'failure.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:
 (out/'trajectory.json').write_text(json.dumps(records));
 if sim is not None:sim.stop();sim.clear_instance()
 if app is not None:app.close(exit_code=0 if success else 1)
