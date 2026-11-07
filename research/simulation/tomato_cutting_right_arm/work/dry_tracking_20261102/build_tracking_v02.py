from pathlib import Path
import json,hashlib
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');w=R/'work/dry_tracking_20261102'
protocol=dict(scope='Focused dry tracking correction only. No target/contact/energy campaign.',baseline='visible_dry_motion_20261102_01',changes=['Use unchanged route waypoints, half-speed clock and linear per-physics-step joint interpolation between consecutive samples; first sample held.','Set right-arm velocity targets to derivative of the interpolated joint path; left arm zero velocity target.','Add native gravity compensation only on arm joints, clipped to unchanged native effort limits. No drive gains, model mass, damping, mount or contact properties changed.'],prospective_tracking_targets=dict(max_tool_position_m=.001,final_tool_position_m=.00025,max_tool_orientation_rad=.002,max_left_arm_deviation_rad=.002),rationale='Provisional dry-controller targets: 1mm maximum is under one sixth of the previous 6mm board clearance, and final0.25mm tests persistent bias. These are explicitly chosen engineering targets, not sensor precision, hardware safety limits or cutting qualification. Original geometric/speed/mount/contact/joint-limit stops retained.',stopping_rule='One full route and independent readback. Preserve any failure; no parameter sweep. Stop before contact.',physics_steps=4091,wall_budget_s=600)
(w/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
s=(R/'rl/tomato_visible_dry_motion_worker.py').read_text()
s=s.replace('One rendered, half-speed version of the verified offset dry route. No target mechanics.','Focused dry controller correction: interpolated commands, desired velocity, arm gravity feedforward.')
s=s.replace("ROOT/'rl/tomato_exported_robot.py']", "ROOT/'rl/tomato_exported_robot.py',ROOT/'work/dry_tracking_20261102/protocol.json']",1)
s=s.replace("controller='Unchanged implicit joint-position drives: arms2500/150, hands3/.15; follower gains0.'", "controller='Same implicit gains/effort limits; per-step interpolated right q and desired qd plus bounded native arm gravity compensation. Hands/followers unchanged.'",1)
s=s.replace("arm_limit_margin_rad=-1e-5)))", "arm_limit_margin_rad=-1e-5,max_tool_tracking_m=.001,final_tool_tracking_m=.00025,max_tool_tracking_angle_rad=.002,max_left_arm_deviation_rad=.002)))",1)
s=s.replace('from pxr import UsdGeom,UsdPhysics,UsdLux','from pxr import UsdGeom,UsdPhysics,UsdLux,Gf',1)
s=s.replace('eye=(1.05,-1.25,.75),target=(.22,0.,.05)', 'eye=(-.8,.85,.8),target=(.28,0.,.18)')
s=s.replace('eye=(.32,-.52,.38),target=(.02,0.,.085)', 'eye=(-.4,.65,.5),target=(.13,.12,.22)')
s=s.replace('  for _ in range(15):sim.render()', "  viewport=get_active_viewport();UsdGeom.Camera(sim.stage.GetPrimAtPath(viewport.camera_path)).GetClippingRangeAttr().Set(Gf.Vec2f(.01,100.))\n  for _ in range(15):sim.render()",1)
s=s.replace('rawqd=[];rawgoal=[]','rawqd=[];rawgoal=[];rawvelocitygoal=[];rawgravity=[];rawrequested=[]',1)
s=s.replace('  physical_start=time.monotonic()', '''  def advance(goal,velocity,sample,sub,phase):
   nonlocal steps
   gravity=r.data.gravity_compensation_forces.torch.clone();limits=r.data.joint_effort_limits.torch
   requested=torch.zeros_like(parked.home);requested[:,arms]=gravity[:,arms]
   feedforward=torch.clamp(requested,min=-limits,max=limits)
   if not torch.isfinite(feedforward).all():raise ValueError('Nonfinite gravity feedforward')
   r.set_joint_position_target_index(target=goal);r.set_joint_velocity_target_index(target=velocity);r.set_joint_effort_target_index(target=feedforward)
   r.write_data_to_sim();parked.probe.write_data_to_sim();sim.step(render=False);steps+=1;r.update(dt);parked.probe.update(dt)
   measure(goal,sample,sub,phase);rawvelocitygoal.append(velocity.cpu().numpy()[0].copy());rawgravity.append(feedforward.cpu().numpy()[0].copy());rawrequested.append(requested.cpu().numpy()[0].copy())
  physical_start=time.monotonic()''',1)
old="""   goal=parked.home.clone();goal[:,parked.ids]=torch.tensor([right],dtype=torch.float32)
   for sub in range(8):
    if (out/'stop.request').exists():raise InterruptedError('Owned guard stop')
    r.set_joint_position_target_index(target=goal);r.write_data_to_sim();parked.probe.write_data_to_sim();sim.step(render=False);steps+=1;r.update(dt);parked.probe.update(dt);measure(goal,i,sub,'route')"""
new="""   start=np.array(plan['right_joint_route_rad'][max(0,i-1)]);end=np.array(right);delta=end-start
   velocity=torch.zeros_like(parked.home);velocity[:,parked.ids]=torch.tensor([delta/(8*dt)],dtype=torch.float32)
   for sub in range(8):
    if (out/'stop.request').exists():raise InterruptedError('Owned guard stop')
    goal=parked.home.clone();goal[:,parked.ids]=torch.tensor([start+((sub+1)/8)*delta],dtype=torch.float32)
    advance(goal,velocity,i,sub,'route')"""
assert old in s;s=s.replace(old,new,1)
old="   r.set_joint_position_target_index(target=parked.home);r.write_data_to_sim();parked.probe.write_data_to_sim();sim.step(render=False);steps+=1;r.update(dt);parked.probe.update(dt);measure(parked.home,480,i,'settle')"
assert old in s;s=s.replace(old,"   advance(parked.home,torch.zeros_like(parked.home),480,i,'settle')",1)
s=s.replace('arm_limits=arm_limits)', 'arm_limits=arm_limits,joint_velocity_commands=np.array(rawvelocitygoal),gravity_feedforward_efforts=np.array(rawgravity),requested_arm_gravity_efforts=np.array(rawrequested),native_effort_limits=r.data.joint_effort_limits.torch[0].cpu().numpy())',1)
s=s.replace('one_initial_joint_state_write_only=True,','no_joint_state_writes_during_executed_motion=True,',1)
s=s.replace('expected_physics_count=steps==4091)',"expected_physics_count=steps==4091,prospective_tool_tracking=max(x['tool_tracking_position_m']for x in rows)<=.001,prospective_final_tracking=rows[-1]['tool_tracking_position_m']<=.00025,prospective_tool_orientation=max(x['tool_tracking_angle_rad']for x in rows)<=.002,prospective_left_arm_hold=max(x['left_arm_tracking_rad']for x in rows)<=.002)",1)
s=s.replace('maximum_tool_tracking_angle_rad=max',"final_tool_tracking_position_m=rows[-1]['tool_tracking_position_m'],maximum_tool_tracking_angle_rad=max",1)
s=s.replace("visible_dry_motion_passed=passed", "dry_tracking_corrected_passed=passed",1)
(R/'rl/tomato_dry_tracking_worker_v02.py').write_text(s)
print('Prepared separate controller version and prospective targets.')
