from pathlib import Path
r=Path('rl')
(r/'tomato_two_joint_sequence_reference.py').write_text('''"""Short-step planar two-link dynamics and partitioned side-contact reference."""
import math
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import dot,cross

def geometry(yaw,q):
    a=yaw+q[0];b=a+q[1]
    p=[.02*math.cos(a)+.01*math.cos(b),.02*math.sin(a)+.01*math.sin(b),0.]
    pose=p+[0.,0.,math.sin(b/2),math.cos(b/2)]
    jac=[[-.02*math.sin(a)-.01*math.sin(b),-.01*math.sin(b)],[.02*math.cos(a)+.01*math.cos(b),.01*math.cos(b)],[0.,0.],[0.,0.],[0.,0.],[1.,1.]]
    return pose,jac

def dynamics(q,qd,effort):
    c=math.cos(q[1]);h=.02*.02*.01*math.sin(q[1])
    matrix=[[.000212+.000008*c,.000102+.000004*c],[.000102+.000004*c,.000102]]
    bias=[-h*(2*qd[0]*qd[1]+qd[1]**2),h*qd[0]**2]
    a,b=matrix[0];_,d=matrix[1];det=a*d-b*b
    u=[effort[i]-bias[i] for i in range(2)]
    return matrix,bias,[(d*u[0]-b*u[1])/det,(a*u[1]-b*u[0])/det]

def step(before,yaw,mp,width,k,dt,pose=None):
    analytic,jac=geometry(yaw,before['q']);pose=analytic if pose is None else pose
    normal=[row[1] for row in quaternion_rotation(pose[3:])]
    depth=width-dot(normal,[p-x for p,x in zip(before['p'],pose[:3])])
    magnitude=k*max(0.,depth-dt*dot(normal,before['vp']))/(1+k*dt*dt/mp) if depth>0 else 0.
    force=[magnitude*n for n in normal];point=[p+depth*n for p,n in zip(before['p'],normal)]
    reaction=[-f for f in force];torque=list(cross([p-c for p,c in zip(point,pose[:3])],reaction));wrench=reaction+torque
    effort=[sum(jac[i][j]*wrench[i] for i in range(6)) for j in range(2)]
    matrix,bias,acc=dynamics(before['q'],before['qd'],effort)
    qd=[v+dt*a for v,a in zip(before['qd'],acc)]
    q=[q+dt*v+17/32*dt*dt*a for q,v,a in zip(before['q'],before['qd'],acc)]
    vp=[v+dt*f/mp for v,f in zip(before['vp'],force)];p=[x+dt*v for x,v in zip(before['p'],vp)]
    return dict(after=dict(q=q,qd=qd,p=p,vp=vp),force=force,point=point,wrench=wrench,effort_nm=effort,matrix=matrix,bias=bias,signed_depth_m=depth,normal=normal)
''')
s=(r/'tomato_hinge_sequence_worker.py').read_text().replace('from tomato_hinge_sequence_reference import step as reference_step','from tomato_two_joint_sequence_reference import step as reference_step,dynamics,geometry').replace('tomato_hinge_sequence_reference.py','tomato_two_joint_sequence_reference.py')
s=s.replace('hinge_sequence_checks_passed','two_joint_sequence_checks_passed').replace('hinge_sequence_cases_completed','two_joint_sequence_cases_completed')
s=s.replace("('base',0.,.01),('link',.01,.02)","('base',0.,.01),('link1',.01,.02),('link2',.03,.02)")
a=s.index('            joint=UsdPhysics.RevoluteJoint.Define');b=s.index('            assets.append',a);t=(r/'tomato_two_joint_interface_worker.py').read_text();u=t.index('            for name,parent,child,pivot');v=t.index('            assets.append',u);s=s[:a]+t[u:v]+s[b:]
s=s.replace('asset.num_joints!=1 or asset.num_bodies!=2','asset.num_joints!=2 or asset.num_bodies!=3').replace("asset.body_names.index('link')","asset.body_names.index('link2')").replace('torch.zeros((1,1)','torch.zeros((1,2)')
s=s.replace("abs(before['joint_position'][0])+abs(before['joint_velocity'][0])","max(abs(x) for x in before['joint_position']+before['joint_velocity'])")
s=s.replace("            mass=float(asset.data.body_mass", "            if asset.joint_names!=['hinge1','hinge2']:raise ValueError('Unexpected joint order')\n            mass=float(asset.data.body_mass")
a=s.index('            matrix=float');b=s.index('            initial=dict',a)
s=s[:a]+'''            matrix=asset.data.mass_matrix.torch.cpu().tolist()[0];expected_matrix=dynamics([0.,0.],[0.,0.],[0.,0.])[0]
            if max(abs(matrix[a][b]-expected_matrix[a][b]) for a in range(2) for b in range(2))>1e-8:raise ValueError('Coupled mass matrix mismatch')
'''+s[b:]
s=s.replace("before['joint_position'][0]","before['joint_position']").replace("before['joint_velocity'][0]","before['joint_velocity']").replace("packet['joint_position'][0]","packet['joint_position']").replace("packet['joint_velocity'][0]","packet['joint_velocity']")
s=s.replace("r['effective_inertia_kg_m2'],",'').replace('mp,inertia,r[','mp,r[')
s=s.replace("effort_nm=moment","effort_nm=ref['effort_nm']")
s=s.replace("qe=abs(after['q']-ref['q']);qve=abs(after['qd']-ref['qd'])","qe=max(abs(a-b) for a,b in zip(after['q'],ref['q']));qve=max(abs(a-b) for a,b in zip(after['qd'],ref['qd']))")
s=s.replace("tqe=abs(after['q']-trajectory['q']);tqve=abs(after['qd']-trajectory['qd'])","tqe=max(abs(a-b) for a,b in zip(after['q'],trajectory['q']));tqve=max(abs(a-b) for a,b in zip(after['qd'],trajectory['qd']))")
s=s.replace("                f['total_effort_impulse']+=DT*s['effort_nm']\n",'')
s=s.replace("joint_impulse_error=abs(inertia*(after['qd']-r['initial']['qd'])-f['total_effort_impulse'])", "matrix,bias,_=dynamics(before['q'],before['qd'],[0.,0.])\n                joint_impulse_error=max(abs(sum(matrix[i][j]*(after['qd'][j]-before['qd'][j]) for j in range(2))+DT*bias[i]-DT*s['effort_nm'][i]) for i in range(2))")
s=s.replace("inertia*after['qd']","sum(m*v for m,v in zip(dynamics(after['q'],after['qd'],[0.,0.])[0][0],after['qd']))").replace("inertia*r['initial']['qd']","sum(m*v for m,v in zip(dynamics(r['initial']['q'],r['initial']['qd'],[0.,0.])[0][0],r['initial']['qd']))")
s=s.replace("coast_drift=abs(after['qd']-before['qd']) if s['contact_count']==0 else 0.","coast_drift=qve if s['contact_count']==0 else 0.")
s=s.replace('cumulative_joint_impulse_error_nms','interval_generalized_impulse_error_nms').replace('coast_joint_velocity_change_rad_s','coast_joint_velocity_reference_error_rad_s')
s=s.replace('Two persistent passive hinges','Two persistent passive two-joint chains').replace('32 persistent coupled hinge exchanges','32 persistent coupled two-joint exchanges')
(r/'tomato_two_joint_sequence_worker.py').write_text(s)
p=r/'tomato_isaac_startup_guard.py';s=p.read_text().replace('TWO_JOINT_CONTACT_WORKER =',"TWO_JOINT_SEQUENCE_WORKER = ROOT / 'rl/tomato_two_joint_sequence_worker.py'\nTWO_JOINT_CONTACT_WORKER =",1)
a=s.index("    if mode == 'hinge_sequence':");b=s.index("    if mode == 'two_joint_contact':",a)
s=s[:a]+s[a:b].replace("'hinge_sequence'","'two_joint_sequence'").replace('hinge_sequence_checks_passed','two_joint_sequence_checks_passed').replace('hinge_sequence_cases_completed','two_joint_sequence_cases_completed')+s[a:]
s=s.replace("('startup', 'two_joint_contact'","('startup', 'two_joint_sequence', 'two_joint_contact'")
s=s.replace("    if mode == 'hinge_sequence':\n        worker_path = HINGE_SEQUENCE_WORKER", "    if mode == 'two_joint_sequence':\n        worker_path = TWO_JOINT_SEQUENCE_WORKER\n    if mode == 'hinge_sequence':\n        worker_path = HINGE_SEQUENCE_WORKER")
s=s.replace("({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |", "({ROOT/'rl/tomato_two_joint_sequence_reference.py', ROOT/'rl/tomato_half_step_reaction.py', ROOT/'rl/tomato_offset_contact_reference.py', ROOT/'rl/tomato_reaction_metadata.py', ROOT/'rl/tomato_wrench_contract.py'} if mode == 'two_joint_sequence' else set()) |\n                                                ({ROOT/'rl/tomato_two_joint_reference.py'} if mode == 'two_joint_interface' else set()) |")
p.write_text(s)
