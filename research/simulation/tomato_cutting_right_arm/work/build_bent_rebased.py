from pathlib import Path
r=Path('rl')
(r/'tomato_bent_rebased_reference.py').write_text('''"""Reference conversion for zero coordinates at the same physical bent rest pose."""
import math
from tomato_two_joint_sequence_reference import dynamics as physical_dynamics
from tomato_bent_origin_reference import step as physical_step,origin_for
REST=[math.pi/6,-math.pi/3]
def physical_angles(q):return [x+r for x,r in zip(q,REST)]
def dynamics(q,qd,effort):return physical_dynamics(physical_angles(q),qd,effort)
def step(before,yaw,mp,width,k,dt,origin,pose=None):
    converted=dict(before,q=physical_angles(before['q']))
    result=physical_step(converted,yaw,mp,width,k,dt,origin,pose=pose)
    result['after']['q']=[x-r for x,r in zip(result['after']['q'],REST)]
    return result
''')
s=(r/'tomato_bent_origin_worker.py').read_text().replace('from tomato_two_joint_sequence_reference import dynamics,geometry','from tomato_two_joint_sequence_reference import geometry').replace('from tomato_bent_origin_reference import step as reference_step,origin_for','from tomato_bent_rebased_reference import step as reference_step,origin_for,dynamics')
s=s.replace('bent_origin_checks_passed','bent_rebased_checks_passed').replace('bent_origin_cases_completed','bent_rebased_cases_completed')
s=s.replace("ROOT/'rl/tomato_bent_origin_reference.py'","ROOT/'rl/tomato_bent_origin_reference.py',ROOT/'rl/tomato_bent_rebased_reference.py'")
s=s.replace("for name,x,mass in (('base',0.,.01),('link1',.01,.02),('link2',.03,.02)):","for name,x,mass in (('base',0.,.01),('link1',.01,.02),('link2',.03,.02)):")
s=s.replace('                body_prim.AddTranslateOp().Set(Gf.Vec3d(x,0.,0.))', '''                a,b=INITIAL_Q[0],sum(INITIAL_Q)
                centre=[0.,0.,0.] if name=='base' else ([.01*math.cos(a),.01*math.sin(a),0.] if name=='link1' else [.02*math.cos(a)+.01*math.cos(b),.02*math.sin(a)+.01*math.sin(b),0.])
                body_angle=0. if name=='base' else (a if name=='link1' else b)
                body_prim.AddTranslateOp().Set(Gf.Vec3d(*centre))
                body_prim.AddOrientOp().Set(Gf.Quatf(math.cos(body_angle/2),Gf.Vec3f(0.,0.,math.sin(body_angle/2))))''')
s=s.replace('                joint.CreateLocalRot0Attr(Gf.Quatf(1.));joint.CreateLocalRot1Attr(Gf.Quatf(1.))', '''                rest_angle=INITIAL_Q[0] if name=='hinge1' else INITIAL_Q[1]
                joint.CreateLocalRot0Attr(Gf.Quatf(math.cos(rest_angle/2),Gf.Vec3f(0.,0.,math.sin(rest_angle/2))))
                joint.CreateLocalRot1Attr(Gf.Quatf(1.))''')
s=s.replace('position=torch.tensor([INITIAL_Q],dtype=torch.float32)','position=torch.zeros((1,2),dtype=torch.float32)')
s=s.replace("max(abs(a-b) for a,b in zip(before['joint_position'],INITIAL_Q))","max(abs(a) for a in before['joint_position'])")
s=s.replace('expected_matrix=dynamics(INITIAL_Q,[0.,0.],[0.,0.])[0]','expected_matrix=dynamics([0.,0.],[0.,0.],[0.,0.])[0]')
s=s.replace('bent_origin_','bent_rebased_')
# Keep the existing translation reference in the source manifest after the output-name replacement.
s=s.replace("ROOT/'rl/tomato_bent_rebased_reference.py',ROOT/'rl/tomato_bent_rebased_reference.py'","ROOT/'rl/tomato_bent_origin_reference.py',ROOT/'rl/tomato_bent_rebased_reference.py'")
s=s.replace('Whole-fixture-translated initially bent persistent','Translated and joint-coordinate-rebased physical bent persistent')
(r/'tomato_bent_rebased_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text().replace('BENT_ORIGIN_WORKER =',"BENT_REBASED_WORKER = ROOT / 'rl/tomato_bent_rebased_worker.py'\nBENT_ORIGIN_WORKER =",1)
a=s.index("    if mode == 'bent_origin':");b=s.index("    if mode == 'bent_sequence':",a)
s=s[:a]+s[a:b].replace("'bent_origin'","'bent_rebased'").replace('bent_origin_checks_passed','bent_rebased_checks_passed').replace('bent_origin_cases_completed','bent_rebased_cases_completed')+s[a:]
s=s.replace("('startup', 'bent_origin'","('startup', 'bent_rebased', 'bent_origin'")
s=s.replace("    if mode == 'bent_origin':\n        worker_path = BENT_ORIGIN_WORKER", "    if mode == 'bent_rebased':\n        worker_path = BENT_REBASED_WORKER\n    if mode == 'bent_origin':\n        worker_path = BENT_ORIGIN_WORKER")
s=s.replace("({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |", "({ROOT/'rl/tomato_bent_rebased_reference.py', ROOT/'rl/tomato_bent_origin_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_rebased' else set()) |\n                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |")
p.write_text(s)
