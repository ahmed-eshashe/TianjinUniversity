from pathlib import Path
r=Path('rl')
(r/'tomato_two_joint_contact_reference.py').write_text('''"""Initial-rest planar 2R response to an independently predicted contact wrench."""
from tomato_two_joint_reference import reference,check

def expected_response(angle,wrench,dt):
    result=reference(angle,dt)
    effort=[sum(result['jacobian'][k][j]*wrench[k] for k in range(6)) for j in range(2)]
    a,b=result['matrix'][0];_,d=result['matrix'][1];det=a*d-b*b
    acc=[(d*effort[0]-b*effort[1])/det,(a*effort[1]-b*effort[0])/det]
    result.update(wrench=list(wrench),effort=effort,velocity=[dt*x for x in acc],position=[17/32*dt*dt*x for x in acc])
    return result
''')
s=(r/'tomato_hinge_contact_worker.py').read_text()
s=s.replace('"""CPU PhysX passive hinges: prescribed link wrench pulse and zero-input coast."""','"""Actual Newton particle contact driving two passive CPU PhysX joints."""')
s=s.replace('from tomato_hinge_reference import expected_pulse,check','from tomato_two_joint_reference import check\nfrom tomato_two_joint_contact_reference import expected_response')
s=s.replace("ROOT/'rl/tomato_hinge_reference.py'","ROOT/'rl/tomato_two_joint_reference.py',ROOT/'rl/tomato_two_joint_contact_reference.py'")
s=s.replace('hinge_contact_checks_passed','two_joint_contact_checks_passed').replace('hinge_contact_cases_completed','two_joint_contact_cases_completed')
s=s.replace('Two passive hinges driven','Two passive two-joint chains driven')
s=s.replace("('base',0.,.01),('link',.01,.02)","('base',0.,.01),('link1',.01,.02),('link2',.03,.02)")
a=s.index('            joint=UsdPhysics.RevoluteJoint.Define');b=s.index('            assets.append',a)
t=(r/'tomato_two_joint_interface_worker.py').read_text();u=t.index('            for name,parent,child,pivot');v=t.index('            assets.append',u);s=s[:a]+t[u:v]+s[b:]
s=s.replace('asset.num_joints!=1 or asset.num_bodies!=2','asset.num_joints!=2 or asset.num_bodies!=3').replace("asset.body_names.index('link')","asset.body_names.index('link2')").replace('torch.zeros((1,1)','torch.zeros((1,2)')
s=s.replace("if abs(before['joint_position'][0])+abs(before['joint_velocity'][0])>1e-7:","if max(abs(x) for x in before['joint_position']+before['joint_velocity'])>1e-7:")
s=s.replace("            mass=float(asset.data.body_mass", "            if asset.joint_names!=['hinge1','hinge2']:raise ValueError('Unexpected joint order')\n            mass=float(asset.data.body_mass")
s=s.replace("expected=expected_pulse(mass,inertia,before['link_pose'][:3],wrench[:3],wrench[3:],[0.,0.,1.],DT)\n            matrix=float(asset.data.mass_matrix.torch[0,0,0])", "expected=expected_response(i*math.pi/2,reference['wrench'],DT)\n            matrix=asset.data.mass_matrix.torch.cpu().tolist()[0]\n            jac=asset.data.body_com_jacobian_w.torch.cpu().tolist()[0][link-1]")
s=s.replace('expected=expected,mass_matrix_kg_m2=matrix,','expected=expected,mass_matrix_kg_m2=matrix,jacobian=jac,')
s=s.replace("r['mass_matrix_kg_m2'],r['after_pulse']['joint_position'][0],r['after_pulse']['joint_velocity'][0]","r['mass_matrix_kg_m2'],r['jacobian'],r['after_pulse']['joint_position'],r['after_pulse']['joint_velocity']")
s=s.replace("r['mass_matrix_kg_m2']*r['after_pulse']['joint_velocity'][0]","sum(m*v for m,v in zip(r['mass_matrix_kg_m2'][0],r['after_pulse']['joint_velocity']))")
s=s.replace("drift=abs(r['after_coast']['joint_velocity'][0]-r['after_pulse']['joint_velocity'][0])","drift=max(abs(a-b) for a,b in zip(r['after_coast']['joint_velocity'],r['after_pulse']['joint_velocity']))")
s=s.replace('per passive hinge. Natural separation and repeated jointed contact remain unvalidated.','per passive two-joint chain. Natural separation and repeated multi-joint contact remain unvalidated.')
(r/'tomato_two_joint_contact_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text().replace('TWO_JOINT_WORKER =',"TWO_JOINT_CONTACT_WORKER = ROOT / 'rl/tomato_two_joint_contact_worker.py'\nTWO_JOINT_WORKER =",1)
a=s.index("    if mode == 'hinge_contact':");b=s.index("    if mode == 'two_joint_interface':",a)
s=s[:a]+s[a:b].replace("'hinge_contact'","'two_joint_contact'").replace('hinge_contact_checks_passed','two_joint_contact_checks_passed').replace('hinge_contact_cases_completed','two_joint_contact_cases_completed')+s[a:]
s=s.replace("('startup', 'two_joint_interface'","('startup', 'two_joint_contact', 'two_joint_interface'")
s=s.replace("    if mode == 'hinge_contact':\n        worker_path = HINGE_CONTACT_WORKER", "    if mode == 'two_joint_contact':\n        worker_path = TWO_JOINT_CONTACT_WORKER\n    if mode == 'hinge_contact':\n        worker_path = HINGE_CONTACT_WORKER")
s=s.replace("({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |", "({ROOT/'rl/tomato_two_joint_contact_reference.py', ROOT/'rl/tomato_two_joint_reference.py', ROOT/'rl/tomato_hinge_contact_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'two_joint_contact' else set()) |\n                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |")
p.write_text(s)
