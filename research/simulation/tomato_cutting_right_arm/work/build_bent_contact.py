from pathlib import Path
r=Path('rl')
(r/'tomato_bent_contact_reference.py').write_text('''"""Bent 2R initial-rest contact response, independent of engine measurements."""
from tomato_two_joint_sequence_reference import geometry,dynamics

def expected_response(yaw,q,wrench,dt):
    pose,jac=geometry(yaw,q)
    effort=[sum(jac[k][j]*wrench[k] for k in range(6)) for j in range(2)]
    matrix,bias,acc=dynamics(q,[0.,0.],effort)
    return dict(matrix=matrix,jacobian=jac,pose=pose,wrench=wrench,effort=effort,velocity=[dt*a for a in acc],position=[x+17/32*dt*dt*a for x,a in zip(q,acc)])

def coast_velocity(q,qd,dt):
    _,_,acc=dynamics(q,qd,[0.,0.])
    return [v+dt*a for v,a in zip(qd,acc)]
''')
s=(r/'tomato_two_joint_contact_worker.py').read_text().replace('from tomato_two_joint_contact_reference import expected_response','from tomato_bent_contact_reference import expected_response,coast_velocity\nfrom tomato_two_joint_sequence_reference import geometry,dynamics')
s=s.replace('DT=1/2400','DT=1/2400\nINITIAL_Q=[math.pi/6,-math.pi/3]')
s=s.replace('two_joint_contact_checks_passed','bent_contact_checks_passed').replace('two_joint_contact_cases_completed','bent_contact_cases_completed')
s=s.replace("ROOT/'rl/tomato_two_joint_contact_reference.py'","ROOT/'rl/tomato_bent_contact_reference.py',ROOT/'rl/tomato_two_joint_sequence_reference.py'")
s=s.replace('position=torch.zeros((1,2))','position=torch.tensor([INITIAL_Q],dtype=torch.float32)')
s=s.replace("if max(abs(x) for x in before['joint_position']+before['joint_velocity'])>1e-7:raise ValueError('Hinge not initially at rest')", "if max(abs(a-b) for a,b in zip(before['joint_position'],INITIAL_Q))>1e-7 or max(abs(v) for v in before['joint_velocity'])>1e-7:raise ValueError('Bent chain not at requested initial rest state')\n            expected_pose,_=geometry(i*math.pi/2,INITIAL_Q)\n            if math.dist(before['link_pose'],expected_pose)>1e-6:raise ValueError('Bent chain forward kinematics mismatch')")
s=s.replace("expected_response(i*math.pi/2,reference['wrench'],DT)","expected_response(i*math.pi/2,INITIAL_Q,reference['wrench'],DT)")
s=s.replace("r['mass_matrix_kg_m2'][0],r['after_pulse']['joint_velocity']","dynamics(r['after_pulse']['joint_position'],r['after_pulse']['joint_velocity'],[0.,0.])[0][0],r['after_pulse']['joint_velocity']")
s=s.replace("drift=max(abs(a-b) for a,b in zip(r['after_coast']['joint_velocity'],r['after_pulse']['joint_velocity']))", "predicted=coast_velocity(r['after_pulse']['joint_position'],r['after_pulse']['joint_velocity'],DT)\n            drift=max(abs(a-b) for a,b in zip(r['after_coast']['joint_velocity'],predicted))\n            r['coast_velocity_reference']=predicted")
s=s.replace('coast_joint_velocity_change_rad_s','coast_joint_velocity_reference_error_rad_s').replace('hinge_contact_','bent_contact_')
s=s.replace('Two passive two-joint chains','Two initially bent passive two-joint chains').replace('per passive two-joint chain. Natural separation and repeated multi-joint contact remain unvalidated.','per initially bent two-joint chain. Repeated bent-chain contact and natural separation are not tested here.')
(r/'tomato_bent_contact_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text().replace('TWO_JOINT_REPLAY_WORKER =',"BENT_CONTACT_WORKER = ROOT / 'rl/tomato_bent_contact_worker.py'\nTWO_JOINT_REPLAY_WORKER =",1)
a=s.index("    if mode == 'two_joint_contact':");b=s.index("    if mode == 'hinge_contact':",a)
s=s[:a]+s[a:b].replace("'two_joint_contact'","'bent_contact'").replace('two_joint_contact_checks_passed','bent_contact_checks_passed').replace('two_joint_contact_cases_completed','bent_contact_cases_completed')+s[a:]
s=s.replace("('startup', 'two_joint_replay'","('startup', 'bent_contact', 'two_joint_replay'")
s=s.replace("    if mode == 'two_joint_contact':\n        worker_path = TWO_JOINT_CONTACT_WORKER", "    if mode == 'bent_contact':\n        worker_path = BENT_CONTACT_WORKER\n    if mode == 'two_joint_contact':\n        worker_path = TWO_JOINT_CONTACT_WORKER")
s=s.replace("({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |", "({ROOT/'rl/tomato_bent_contact_reference.py', ROOT/'rl/tomato_two_joint_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_hinge_contact_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_contact' else set()) |\n                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |")
p.write_text(s)
