from pathlib import Path
r=Path('rl')
(r/'tomato_two_joint_reference.py').write_text('''"""Independent planar 2R initial-rest reference; stdlib only."""
import math

def reference(angle=0.,dt=1/2400):
    m=.02;r=.01;l=.02;iz=.0001
    matrix=[[2*iz+m*r*r+m*(l*l+r*r+2*l*r),iz+m*(r*r+l*r)],[iz+m*(r*r+l*r),iz+m*r*r]]
    jac=[[-.03*math.sin(angle),-.01*math.sin(angle)],[.03*math.cos(angle),.01*math.cos(angle)],[0.,0.],[0.,0.],[0.,0.],[1.,1.]]
    wrench=[-3*math.sin(angle),3*math.cos(angle),0.,0.,0.,.0012]
    effort=[sum(jac[k][j]*wrench[k] for k in range(6)) for j in range(2)]
    a,b=matrix[0];_,d=matrix[1];det=a*d-b*b
    assert det>0 and a>0
    acc=[(d*effort[0]-b*effort[1])/det,(a*effort[1]-b*effort[0])/det]
    return dict(matrix=matrix,jacobian=jac,wrench=wrench,effort=effort,velocity=[dt*x for x in acc],position=[17/32*dt*dt*x for x in acc])

def check(ref,matrix,jac,q,qd):
    errors=dict(matrix=max(abs(matrix[i][j]-ref['matrix'][i][j]) for i in range(2) for j in range(2)),
        jacobian=max(abs(jac[i][j]-ref['jacobian'][i][j]) for i in range(6) for j in range(2)),
        position=max(abs(q[i]-ref['position'][i]) for i in range(2)),velocity=max(abs(qd[i]-ref['velocity'][i]) for i in range(2)))
    gates=dict(matrix=1e-8,jacobian=1e-6,position=1e-6,velocity=2e-5)
    if any(errors[k]>gates[k] for k in errors):raise ValueError(f'Two-joint reference mismatch: {errors}')
    return errors
''')
s=(r/'tomato_hinge_interface_worker.py').read_text().replace('from tomato_hinge_reference import expected_pulse,check','from tomato_two_joint_reference import reference,check').replace('tomato_hinge_reference.py','tomato_two_joint_reference.py')
s=s.replace('hinge_checks_passed','two_joint_checks_passed').replace('hinge_cases_completed','two_joint_cases_completed')
s=s.replace("('base',0.,.01),('link',.01,.02)","('base',0.,.01),('link1',.01,.02),('link2',.03,.02)")
a=s.index('            joint=UsdPhysics.RevoluteJoint.Define');b=s.index('            assets.append',a)
s=s[:a]+'''            for name,parent,child,pivot in (('hinge1','base','link1',0.),('hinge2','link1','link2',.01)):
                joint=UsdPhysics.RevoluteJoint.Define(stage,path+'/'+name)
                joint.CreateBody0Rel().SetTargets([path+'/'+parent]);joint.CreateBody1Rel().SetTargets([path+'/'+child])
                joint.CreateAxisAttr('Z');joint.CreateLocalPos0Attr(Gf.Vec3f(pivot,0.,0.));joint.CreateLocalPos1Attr(Gf.Vec3f(-.01,0.,0.))
                joint.CreateLocalRot0Attr(Gf.Quatf(1.));joint.CreateLocalRot1Attr(Gf.Quatf(1.))
                PhysxSchema.PhysxJointAPI.Apply(joint.GetPrim()).CreateJointFrictionAttr(0.)
'''+s[b:]
s=s.replace('asset.num_joints!=1 or asset.num_bodies!=2','asset.num_joints!=2 or asset.num_bodies!=3').replace("asset.body_names.index('link')","asset.body_names.index('link2')").replace('torch.zeros((1,1)','torch.zeros((1,2)')
a=s.index('            mass=float(');b=s.index('            asset.instantaneous',a)
s=s[:a]+'''            if asset.joint_names!=['hinge1','hinge2']:raise ValueError('Unexpected joint order')
            expected=reference(i*math.pi/2,DT)
            force=expected['wrench'][:3];torque=expected['wrench'][3:]
            matrix=asset.data.mass_matrix.torch.cpu().tolist()[0]
            jac=asset.data.body_com_jacobian_w.torch.cpu().tolist()[0][link-1]
'''+s[b:]
s=s.replace('mass_matrix_kg_m2=matrix','mass_matrix_kg_m2=matrix,jacobian=jac')
s=s.replace("r['mass_matrix_kg_m2'],r['after_pulse']['joint_position'][0],r['after_pulse']['joint_velocity'][0]","r['mass_matrix_kg_m2'],r['jacobian'],r['after_pulse']['joint_position'],r['after_pulse']['joint_velocity']")
s=s.replace("drift=abs(r['after_coast']['joint_velocity'][0]-r['after_pulse']['joint_velocity'][0])","drift=max(abs(a-b) for a,b in zip(r['after_coast']['joint_velocity'],r['after_pulse']['joint_velocity']))")
s=s.replace('Two local synthetic passive hinges','Two local synthetic passive two-joint chains').replace('two isolated passive hinges','two isolated passive two-joint chains').replace('on passive fixed-base hinges only','on passive fixed-base two-joint chains only')
(r/'tomato_two_joint_interface_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text();s=s.replace('HINGE_WORKER =',"TWO_JOINT_WORKER = ROOT / 'rl/tomato_two_joint_interface_worker.py'\nHINGE_WORKER =",1)
a=s.index("    if mode == 'hinge_interface':");b=s.index("    if mode == 'anisotropic_sequence':",a)
s=s[:a]+s[a:b].replace("'hinge_interface'","'two_joint_interface'").replace('hinge_checks_passed','two_joint_checks_passed').replace('hinge_cases_completed','two_joint_cases_completed')+s[a:]
s=s.replace("('startup', 'hinge_replay'","('startup', 'two_joint_interface', 'hinge_replay'")
s=s.replace("    if mode == 'hinge_interface':\n        worker_path = HINGE_WORKER", "    if mode == 'two_joint_interface':\n        worker_path = TWO_JOINT_WORKER\n    if mode == 'hinge_interface':\n        worker_path = HINGE_WORKER")
s=s.replace("({ROOT/'rl/tomato_hinge_reference.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_interface' else set()) |", "({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |\n                                                ({ROOT/'rl/tomato_hinge_reference.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'hinge_interface' else set()) |")
p.write_text(s)
