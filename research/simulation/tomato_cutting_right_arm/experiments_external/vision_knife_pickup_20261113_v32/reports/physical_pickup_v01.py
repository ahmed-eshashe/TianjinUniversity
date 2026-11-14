"""Contact-driven pickup feasibility from a reset pregrasp. State-informed teacher; no learning claim."""
from pathlib import Path
import argparse,json,sys,time,traceback,hashlib
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(R/'scripts'),str(R/'rl')]
a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--shift',type=float,default=-.025);a.add_argument('--goal-force',type=float,default=4.);a.add_argument('--lift',type=float,default=.10);args=a.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True);app=sim=None;records=[];phase='startup';success=False
try:
 import numpy as np,torch
 from scipy.spatial.transform import Rotation
 from scipy.spatial import ConvexHull
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
 import isaaclab.sim as su
 from isaaclab_physx.physics import PhysxCfg,PhysxManager
 from isaaclab.assets import Articulation,ArticulationCfg,RigidObject,RigidObjectCfg
 from isaaclab.actuators import ImplicitActuatorCfg
 from isaaclab.app.settings_manager import get_settings_manager
 from pxr import Usd,UsdGeom,UsdPhysics,PhysxSchema,Gf
 from reach_kinematics import ArmKinematics,PALM_OFFSET
 c=json.loads((W/'scene_config.json').read_text());criteria=json.loads((W/'pickup_criteria.json').read_text());template=json.loads((R/'runs/rl/phase3/central_grasp_13/before_lift.json').read_text());row=min(json.loads((W/'reports/initial_grasp_reach.json').read_text()),key=lambda x:abs(x['handle_axis_shift_m']-args.shift));relative=np.array(row['hand_from_knife']);pose=np.array(json.loads((W/'runs/camera01/result.json').read_text())['knife_pose'])
 dt=1/960;sim=su.SimulationContext(su.SimulationCfg(device='cpu',dt=dt,gravity=(0,0,-9.81),use_fabric=False,use_newton_actuators=False,physics=PhysxCfg(solver_type=1),log_dir=str(out)));sim.stage.GetRootLayer().subLayerPaths.append(c['scene'])
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/KitchenEnvironment')):
  if prim.HasAPI(UsdPhysics.CollisionAPI):UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Set(False)
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):UsdPhysics.RigidBodyAPI(prim).GetRigidBodyEnabledAttr().Set(False)
  if prim.IsA(UsdPhysics.Joint):prim.SetActive(False)
 for prim in Usd.PrimRange(sim.stage.GetPrimAtPath('/dual_ar5_o6')):
  if prim.HasAPI(UsdPhysics.RigidBodyAPI):PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
  if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
   api=PhysxSchema.PhysxArticulationAPI.Apply(prim);api.CreateSolverPositionIterationCountAttr(64);api.CreateSolverVelocityIterationCountAttr(16)
 refined=[]
 for x in json.loads((R/'work/single_slice_20261106/wrist_collision_shapes.json').read_text()):
  prim=sim.stage.GetPrimAtPath(x['path']);api=PhysxSchema.PhysxConvexDecompositionCollisionAPI.Apply(prim);api.CreateMaxConvexHullsAttr(128);api.CreateHullVertexLimitAttr(64);api.CreateVoxelResolutionAttr(1000000);api.CreateErrorPercentageAttr(1.);api.CreateShrinkWrapAttr(True);api.CreateMinThicknessAttr(.0001);refined.append(x['path'])
 def matrix(p):
  m=np.eye(4);m[:3,:3]=Rotation.from_quat(p[3:]).as_matrix();m[:3,3]=p[:3];return m
 kin=ArmKinematics(sim.stage);K=matrix(pose);contact_T=K@relative;pre=contact_T.copy();pre[2,3]+=.045
 home=dict(c['home_rad']);q,pe,re=kin.solve(pre[:3,3]+pre[:3,:3]@PALM_OFFSET,pre[:3,:3],row['q']);assert pe<.0002 and re<.002
 for n,v in zip(kin.names,q):home[n]=v
 fingers=['index','middle','ring','pinky'];hand_names=['right_rh_thumb_cmc_yaw','right_rh_thumb_cmc_pitch']+['right_rh_'+f+'_mcp_pitch' for f in fingers]
 for n,v in zip(hand_names,[template['q_rad'][7],.045,*template['q_rad'][9:]]):home[n]=v
 home['right_rh_thumb_ip']=1.86*home['right_rh_thumb_cmc_pitch']
 for f in fingers:home['right_rh_'+f+'_dip']=.89*home['right_rh_'+f+'_mcp_pitch']
 root=np.array(c['robot_root_world_matrix']);r=Articulation(ArticulationCfg(prim_path='/dual_ar5_o6',spawn=None,init_state=ArticulationCfg.InitialStateCfg(pos=tuple(root[:3,3]),rot=tuple(Rotation.from_matrix(root[:3,:3]).as_quat()),joint_pos=home),actuators={'arm':ImplicitActuatorCfg(joint_names_expr=['.*_AR5_.*'],stiffness=2500.,damping=150.,effort_limit_sim=80.),'fingers':ImplicitActuatorCfg(joint_names_expr=['.*_(index|middle|ring|pinky)_mcp_pitch'],stiffness=3.,damping=.15,effort_limit_sim=.3),'thumb':ImplicitActuatorCfg(joint_names_expr=['.*_thumb_cmc_(yaw|pitch)'],stiffness=10.,damping=.15,effort_limit_sim=1.),'followers':ImplicitActuatorCfg(joint_names_expr=['.*_(dip|thumb_ip)'],stiffness=0.,damping=0.,effort_limit_sim=0.)}))
 knife=RigidObject(RigidObjectCfg(prim_path=c['knife_path'],spawn=None,init_state=RigidObjectCfg.InitialStateCfg(pos=tuple(pose[:3]),rot=tuple(pose[3:]))));sim.reset();r.update(dt);knife.update(dt);get_settings_manager().set_bool('/physics/disableContactProcessing',False)
 target=torch.tensor([[home[n] for n in r.joint_names]],dtype=torch.float32);r.write_joint_state_to_sim_index(position=target,velocity=torch.zeros_like(target));right=[r.joint_names.index(n) for n in kin.names];arms=[i for i,n in enumerate(r.joint_names) if '_AR5_' in n];hids=[r.joint_names.index(n) for n in hand_names];palm_id=r.body_names.index('right_rh_hand_base_link')
 bodies=[str(x.GetPath()) for x in sim.stage.Traverse() if str(x.GetPath()).startswith('/dual_ar5_o6/') and x.HasAPI(UsdPhysics.RigidBodyAPI) and UsdPhysics.RigidBodyAPI(x).GetRigidBodyEnabledAttr().Get()!=False];filters=bodies+[c['board_path'],c['counter_path']];view=PhysxManager.get_physics_sim_view().create_rigid_contact_view(bodies,[filters for _ in bodies],max_contact_data_count=8192);ki=filters.index(c['knife_path']);kb=bodies.index(c['knife_path']);hands=[i for i,n in enumerate(bodies) if '/right_rh_' in n]
 handle=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path']+'/CollisionHandle')).GetPointsAttr().Get());blade=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path']+'/CollisionBlade')).GetPointsAttr().Get());heq=ConvexHull(handle).equations;beq=ConvexHull(blade).equations;knife_points=np.array(UsdGeom.Mesh(sim.stage.GetPrimAtPath(c['knife_path'])).GetPointsAttr().Get());hc=(handle.min(0)+handle.max(0))/2
 assert not any(p.IsA(UsdPhysics.Joint) and c['knife_path'] in [str(x) for rel in [UsdPhysics.Joint(p).GetBody0Rel(),UsdPhysics.Joint(p).GetBody1Rel()] for x in rel.GetTargets()] for p in sim.stage.Traverse())
 (out/'configuration.json').write_text(json.dumps(dict(args=vars(args)|{'output':str(out)},criteria=criteria,pregrasp=q.tolist(),hand_from_knife=relative.tolist(),refined_collision_shapes=refined,source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='State-informed, reset-pregrasp physical component. Not a neutral-pose pickup or learned policy.'),indent=2))
 def arr(x):return x.numpy() if hasattr(x,'numpy') else np.asarray(x)
 step=0;hold=0.;reference=None;initial_height=None;lowpass={f:0. for f in ['thumb',*fingers]};last=None;maximum_contact=0.;last_ik=q.copy();start=time.monotonic()
 def observe():
  global maximum_contact
  fp,points,normals,separations,count,starts=[arr(v) for v in view.get_contact_data(dt=dt)];fm=arr(view.get_contact_force_matrix(dt=dt));mag=np.linalg.norm(fm,axis=-1);tp=knife.data.root_pose_w.torch[0].cpu().numpy();T=matrix(tp);hp=r.data.body_link_pose_w.torch[0,palm_id].cpu().numpy();H=matrix(hp);contacts=[];loads={f:0. for f in ['thumb',*fingers]}
  if count.sum()>=8192:raise ValueError('Contact buffer full')
  bad=[]
  for i,j in np.argwhere(mag>.1):
   value=float(mag[i,j]);b,other=bodies[i],filters[j]
   if value>50:bad.append((b,other,value))
   if b!=c['knife_path'] and other in [c['board_path'],c['counter_path']] and value>(10. if '/right_rh_' in b else 5.):bad.append((b,other,value))
  for i in hands:
   name=bodies[i].rsplit('/',1)[-1];part='palm' if name=='right_rh_hand_base_link' else name.removeprefix('right_rh_').split('_')[0]
   for j in range(int(starts[i,ki]),int(starts[i,ki]+count[i,ki])):
    force=float(fp[j,0]);local=(points[j]-tp[:3])@T[:3,:3];onhandle=bool(np.max(heq[:,:3]@local+heq[:,3])<=.003);onblade=bool(np.max(beq[:,:3]@local+beq[:,3])<=.003)
    if force>.05 and ((onblade and not onhandle) or not(onblade or onhandle)):raise ValueError(('Blade/unknown knife contact',part,force,local.tolist()))
    if onhandle and force>.05:
     contacts.append(dict(part=part,force_N=force,point=points[j].tolist(),normal=normals[j].tolist()))
     if part in loads:loads[part]+=force
  if bad:raise ValueError(('Contact stop',bad[:5]))
  qnow=r.data.joint_pos.torch[0].cpu().numpy();limits=r.data.soft_joint_pos_limits.torch[0].cpu().numpy();speed=float(r.data.joint_vel.torch.abs().max())
  if not np.isfinite(qnow).all() or speed>3 or np.any(qnow<limits[:,0]-.005) or np.any(qnow>limits[:,1]+.005):raise ValueError(('Joint state stop',speed))
  hcworld=T[:3,:3]@hc+T[:3,3];world=knife_points@T[:3,:3].T+T[:3,3];support=float(sum(mag[kb,filters.index(p)] for p in [c['board_path'],c['counter_path']]));relative_actual=np.linalg.inv(H)@T;thumb=[x for x in contacts if x['part']=='thumb'];other=[x for x in contacts if x['part'] in fingers];opposed=any(np.dot(t['normal'],f['normal'])<-.5 for t in thumb for f in other)
  return dict(phase=phase,step=step,sim_s=step*dt,knife_pose=tp.tolist(),knife_velocity=knife.data.root_vel_w.torch[0].tolist(),q=qnow.tolist(),hand_pose=hp.tolist(),contacts=contacts,loads=loads,support_N=support,handle_height_m=float(hcworld[2]),minimum_tool_height_m=float(world[:,2].min()),opposed=opposed,relative_tool=relative_actual.tolist(),speed_rad_s=speed,force_max_N=float(mag.max()))
 def tick(qgoal,pressure=False):
  global step,last,hold,reference,initial_height
  target[:,right]=torch.tensor(qgoal,dtype=torch.float32)
  if pressure and step%4==0 and last is not None:
   for index,part in [(1,'thumb'),(2,'index'),(3,'middle'),(4,'ring'),(5,'pinky')]:
    lowpass[part]=.75*lowpass[part]+.25*last['loads'][part];rate=np.clip((args.goal_force-lowpass[part])*.06,-.15,.20);target[0,hids[index]]+=float(rate*4*dt)
    target[0,hids[index]]=float(np.clip(target[0,hids[index]],.015 if part=='thumb' else .6,.315 if part=='thumb' else 1.45))
  effort=torch.zeros_like(target);effort[:,arms]=r.data.gravity_compensation_forces.torch[:,arms];r.set_joint_position_target_index(target=target);r.set_joint_velocity_target_index(target=torch.zeros_like(target));r.set_joint_effort_target_index(target=effort);r.write_data_to_sim();knife.write_data_to_sim();sim.step(render=False);r.update(dt);knife.update(dt);step+=1
  last=observe()
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
 def route(Tstart,Tend,seconds,pressure=False):
  global last_ik
  duration=round(seconds/dt);knots=[];seed=last_ik.copy()
  for u in np.linspace(0,1,81):
   b=u*u*u*(10-15*u+6*u*u);P=Tstart[:3,3]*(1-b)+Tend[:3,3]*b;seed,pe,re=kin.solve(P+Tend[:3,:3]@PALM_OFFSET,Tend[:3,:3],seed)
   if pe>.0003 or re>.003:raise ValueError(('Route IK failure',pe,re))
   knots.append(seed.copy())
  for k in range(duration):
   u=(k+1)/duration*80;i=min(79,int(u));q=knots[i]*(1-(u-i))+knots[i+1]*(u-i);tick(q,pressure)
  last_ik=q.copy()
 phase='settle'
 for _ in range(480):tick(last_ik)
 phase='descend';route(pre,contact_T,2.)
 phase='close'
 for _ in range(2400):tick(last_ik,True)
 (out/'before_lift.json').write_text(json.dumps(last,indent=2))
 phase='lift';end=contact_T.copy();end[2,3]+=args.lift;route(contact_T,end,4.,True)
 phase='hold'
 for _ in range(3840):
  tick(last_ik,True)
  if hold>=3.:success=True;break
 (out/'result.json').write_text(json.dumps(dict(success=success,scope='Secure lift from a reset pregrasp; not neutral-start, vision-based or learned.',last=last,wall_s=time.monotonic()-start),indent=2));print('RESULT',success,flush=True)
except BaseException:
 (out/'failure.txt').write_text(traceback.format_exc());traceback.print_exc()
finally:
 (out/'trajectory.json').write_text(json.dumps(records));
 if sim is not None:sim.stop();sim.clear_instance()
 if app is not None:app.close(exit_code=0 if success else 1)
