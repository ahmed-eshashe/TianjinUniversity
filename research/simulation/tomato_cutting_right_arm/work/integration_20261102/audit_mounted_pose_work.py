from pathlib import Path
import json,hashlib,sys,numpy as np
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'));from tomato_wrench_measurements import measured_interval_work,shift_wrench
p=r/'runs/native/mounted_contact_20261102_03/mounted_contact_measurements.json';d=json.loads(p.read_text());cases=[]
for c in d['cases']:
 records=[];feedback=c['label'] in ['passive_feedback','passive_replay','driven_feedback']
 for row in c['records']:
  work=measured_interval_work(row['robot_before']['pose'],row['robot_after']['pose'],d['local_tool_com'],row['wrench_at_tool_com'] if feedback else np.zeros(6));work['particle_contact_work_j']=row['particle_contact_work_j'];records.append(work)
 cases.append(dict(case=c['label'],records=records,actual_robot_contact_work_j=sum(v['work_j']for v in records),particle_contact_work_j=sum(v['particle_contact_work_j']for v in records)))
# Independent rigid-twist origin-invariance control.
w=np.array([2.,-3.,4.,.2,.1,-.3]);v=np.array([.1,.2,-.05]);omega=np.array([.3,-.1,.2]);offset=np.array([.03,-.02,.01]);shifted=shift_wrench(w,np.zeros(3),offset);error=float(abs(w@np.r_[v,omega]-shifted@np.r_[v+np.cross(omega,offset),omega]));assert error<1e-14
by={c['case']:c for c in cases};assert by['passive_feedback']['actual_robot_contact_work_j']==by['passive_replay']['actual_robot_contact_work_j'];assert by['clear']['actual_robot_contact_work_j']==0
out=r/'runs/offline/mounted_pose_work_20261102_01';out.mkdir(exist_ok=True);report=dict(cases=cases,twist_origin_power_error_w=error,scope='Postprocessing actual accepted mounted-robot poses and applied contact wrench. Demonstrates work observability only; no actuator energy, body kinetic energy, base reaction or complete energy closure is claimed.',source_sha256={str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in [p,r/'rl/tomato_wrench_measurements.py',Path(__file__)]});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print([(c['case'],c['actual_robot_contact_work_j'],c['particle_contact_work_j'])for c in cases])
