from pathlib import Path
r=Path(__file__).resolve().parents[2]
s=(r/'rl/tomato_mounted_target_com_worker.py').read_text()
# Preserve the existing checked construction and provenance preflights verbatim.
s=s[:s.index('  for label in labels:')]
s=s.replace('Short nonfracturing mounted WHOLE-target feedback component screen.','Multirate nonfracturing mounted whole-target initial-velocity fixture.')
s=s.replace("p.add_argument('--refinement',type=int,default=1,choices=[4,8,16,32,64,128,256])", "p.add_argument('--coupling-refinement',type=int,default=1,choices=[1,2,4]);p.add_argument('--direction',choices=['down','up'],default='down')")
s=s.replace("app=robot=None;passed=False;cases=[];steps=0", "app=robot=None;passed=False;cases=[];steps=0")
start=s.index('  dt=1/(9600*a.refinement)');end=s.index('  from isaaclab.app',start)
s=s[:start]+'''  protocol_path=ROOT/'runs/offline/moving_contact_protocol_20261102_01/plan.json';protocol=json.loads(protocol_path.read_text());velocity_path=ROOT/'runs/offline/moving_contact_protocol_20261102_01/initial_velocity.json';velocity_input=json.loads(velocity_path.read_text());parent_closure=json.loads((out/'source_closure.json').read_text());parent_closure['source_sha256'].update(capture_sources(out/'moving_protocol_snapshot',[Path(__file__)],inputs=[protocol_path,velocity_path])['source_sha256'] if False else {})
  # Additional protocol files are explicitly pinned separately before AppLauncher.
  import hashlib
  protocol_pins={str(path):hashlib.sha256(path.read_bytes()).hexdigest()for path in [protocol_path,velocity_path]};write(out,'moving_protocol_pins.json',protocol_pins)
  dt=1/1228800;n=1024;robot_dt=1/(9600*a.coupling_refinement);subcycles=128//a.coupling_refinement;refresh_stride=32;labels=['no_feedback','feedback','replay','clear'];write(out,'input_manifest.json',dict(target_dt_s=dt,robot_dt_s=robot_dt,target_intervals_per_case=n,robot_intervals_per_case=n//subcycles,subcycles=subcycles,coupling_refinement=a.coupling_refinement,direction=a.direction,duration_s=n*dt,cases=labels,contact_refresh_clock_s=1/38400,exchange='Actual PhysX pose held across each block of fine deformable intervals. Sum accepted target impulses/moments and apply the block-average wrench exactly once at knife COM, then advance the real robot. No extrapolated or teleported pose. Explicit coupling delay and end-pose potential jump recorded.',initial_velocity='Native right-seven-joint velocity from pinned static COM Jacobian, nominal 2mm/s down or reversed up. Coasting gravity-compensation diagnostic; no trajectory controller or executed approach.',scope='New multirate, nonfracturing moving-contact diagnostic only. Geometry/material/masses/effort limits unchanged. No live damage/cut/training or automatic 23B qualification.'))
''' +s[end:]
s=s.replace('from tomato_contact_robot_v04 import ContactRobotV04 as ContactRobot','from tomato_moving_contact_robot import MovingContactRobot as ContactRobot')
s=s.replace("robot=ContactRobot(out,plan,dt,waypoint['q_right_rad'])", "robot=ContactRobot(out,plan,robot_dt,waypoint['q_right_rad']);robot.configure_initial_velocity(np.array(velocity_input['joint_velocity_rad_s'])*(1 if a.direction=='down'else -1),np.array(velocity_input['expected_tool_twist_world'])*(1 if a.direction=='down'else -1))")
# Remove an unused generated staging expression; the two additional inputs have
# their own immutable archive and exact hash verification at both boundaries.
s=s.replace(";parent_closure=json.loads((out/'source_closure.json').read_text());parent_closure['source_sha256'].update(capture_sources(out/'moving_protocol_snapshot',[Path(__file__)],inputs=[protocol_path,velocity_path])['source_sha256'] if False else {})",'')
s=s.replace("protocol_pins={str(path):hashlib.sha256(path.read_bytes()).hexdigest()for path in [protocol_path,velocity_path]};write(out,'moving_protocol_pins.json',protocol_pins)","protocol_pins={str(path):hashlib.sha256(path.read_bytes()).hexdigest()for path in [protocol_path,velocity_path]};write(out,'moving_protocol_pins.json',protocol_pins);(out/'moving_protocol_archives').mkdir();[(out/'moving_protocol_archives'/path.name).write_bytes(path.read_bytes())for path in [protocol_path,velocity_path]]")
(r/'rl/tomato_moving_contact_worker.py').write_text(s)
