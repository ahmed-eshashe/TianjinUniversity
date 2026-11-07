from pathlib import Path
r=Path('rl')
(r/'tomato_bent_origin_reference.py').write_text('''"""Translation-aware wrapper around the unchanged planar contact reference."""
from tomato_two_joint_sequence_reference import step as local_step,geometry
from tomato_offset_contact_reference import world_point

def origin_for(yaw,q):
    pose,_=geometry(yaw,q)
    return [-v for v in world_point(pose,[.004,.004,0.])]

def step(before,yaw,mp,width,k,dt,origin,pose=None):
    local=dict(before,p=[x-o for x,o in zip(before['p'],origin)])
    local_pose=None if pose is None else [x-o for x,o in zip(pose[:3],origin)]+pose[3:]
    result=local_step(local,yaw,mp,width,k,dt,pose=local_pose)
    result['after']['p']=[x+o for x,o in zip(result['after']['p'],origin)]
    result['point']=[x+o for x,o in zip(result['point'],origin)]
    return result
''')
s=(r/'tomato_bent_sequence_worker.py').read_text().replace('from tomato_two_joint_sequence_reference import step as reference_step,dynamics,geometry','from tomato_two_joint_sequence_reference import dynamics,geometry\nfrom tomato_bent_origin_reference import step as reference_step,origin_for')
s=s.replace('bent_sequence_checks_passed','bent_origin_checks_passed').replace('bent_sequence_cases_completed','bent_origin_cases_completed')
s=s.replace("ROOT/'rl/tomato_two_joint_sequence_reference.py'","ROOT/'rl/tomato_two_joint_sequence_reference.py',ROOT/'rl/tomato_bent_origin_reference.py'")
s=s.replace('            root.AddOrientOp().Set(rotation)','            origin=origin_for(angle,INITIAL_Q)\n            root.AddTranslateOp().Set(Gf.Vec3d(*origin))\n            root.AddOrientOp().Set(rotation)')
s=s.replace('            anchor.CreateLocalRot0Attr(rotation)','            anchor.CreateLocalPos0Attr(Gf.Vec3f(*origin))\n            anchor.CreateLocalRot0Attr(rotation)')
s=s.replace('init_state=ArticulationCfg.InitialStateCfg(rot=','init_state=ArticulationCfg.InitialStateCfg(pos=tuple(origin),rot=')
s=s.replace('            expected_pose,_=geometry(i*math.pi/2,INITIAL_Q)','            origin=origin_for(i*math.pi/2,INITIAL_Q)\n            expected_pose,_=geometry(i*math.pi/2,INITIAL_Q)\n            expected_pose[:3]=[x+o for x,o in zip(expected_pose[:3],origin)]')
s=s.replace('initial=initial,particle_mass_kg=mp','origin_world_m=origin,initial=initial,particle_mass_kg=mp')
s=s.replace("r['half_width_m'],1750.,DT)","r['half_width_m'],1750.,DT,r['origin_world_m'])")
s=s.replace("cross(after['p'],[mp*v for v in after['vp']])","cross([p-o for p,o in zip(after['p'],r['origin_world_m'])],[mp*v for v in after['vp']])")
s=s.replace("cross(r['initial']['p'],[mp*v for v in r['initial']['vp']])","cross([p-o for p,o in zip(r['initial']['p'],r['origin_world_m'])],[mp*v for v in r['initial']['vp']])")
s=s.replace('bent_sequence_','bent_origin_').replace('Two initially bent persistent','Whole-fixture-translated initially bent persistent').replace('32 persistent coupled bent-chain exchanges','32 translated persistent coupled bent-chain exchanges')
(r/'tomato_bent_origin_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text().replace('BENT_SEQUENCE_WORKER =',"BENT_ORIGIN_WORKER = ROOT / 'rl/tomato_bent_origin_worker.py'\nBENT_SEQUENCE_WORKER =",1)
a=s.index("    if mode == 'bent_sequence':");b=s.index("    if mode == 'two_joint_sequence':",a)
s=s[:a]+s[a:b].replace("'bent_sequence'","'bent_origin'").replace('bent_sequence_checks_passed','bent_origin_checks_passed').replace('bent_sequence_cases_completed','bent_origin_cases_completed')+s[a:]
s=s.replace("('startup', 'bent_sequence'","('startup', 'bent_origin', 'bent_sequence'")
s=s.replace("    if mode == 'bent_sequence':\n        worker_path = BENT_SEQUENCE_WORKER", "    if mode == 'bent_origin':\n        worker_path = BENT_ORIGIN_WORKER\n    if mode == 'bent_sequence':\n        worker_path = BENT_SEQUENCE_WORKER")
s=s.replace("({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |", "({ROOT/'rl/tomato_bent_origin_reference.py', ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'bent_origin' else set()) |\n                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |")
p.write_text(s)
