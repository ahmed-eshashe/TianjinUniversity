from pathlib import Path
import csv,json,hashlib,sys
import numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];w=Path(__file__).resolve().parent;run=r/'work/native_clock_controls_20261104/robot_on01';mechanics=r/'runs/native/robot_energy_operator_v03_20261102_01';sys.path.insert(0,str(r/'rl'))
from tomato_robot_energy_link_reference import kinetic_energy
order=json.loads((run/'ordering.json').read_text());meta=json.loads((mechanics/'robot_energy_measurements.json').read_text());assert meta['passed'];assert meta['cases'][0]['body_names']==order['body_names'];assert meta['cases'][0]['joint_names']==order['joint_names']
with np.load(mechanics/'home_robot_mechanics.npz') as z:mass=z['mass'];inertia=z['inertia_com_link_axes'];armature=z['armature']
assert np.array_equal(armature,np.load(run/'get_dof_armatures.npy')[0][order['user_to_backend_joint']])
closures=[json.loads((p/'source_closure.json').read_text())['source_sha256'] for p in [run,mechanics]]
scene=Path(json.loads((r/'runs/offline/fixed_mount_scene_20261101_01/fixed_mount_plan.json').read_text())['scene']);assert closures[0][str(scene)]==closures[1][str(scene)]==hashlib.sha256(scene.read_bytes()).hexdigest()
markers={x['label']:x['pass_count'] for x in json.loads((run/'trace_boundaries.json').read_text())};drive=np.zeros(120);impulses=np.zeros((120,36));lines=(run/'native_trace.csv').read_text().splitlines();assert lines[-1]=='END count=181440 dropped=0 passes=5040'
for x in csv.DictReader(lines[1:-1]):
 p=int(x['pass']);i=(p-241)//40
 if i<0:continue
 assert markers[f'before_step_{i}']<p<=markers[f'after_step_{i}'];imp=float(x['drive_impulse']);drive[i]+=imp*(float(x['local_velocity_before'])+float(x['local_velocity_after']))/2;impulses[i,int(x['dof'])]+=imp
rows=[]
def energy(z,prefix):
 R=Rotation.from_quat(z[prefix+'body_pose'][:,3:].astype(float)).as_matrix();v=z[prefix+'body_com_velocity'].astype(float);qd=z[prefix+'qd'].astype(float);K=kinetic_energy(mass,R@inertia@R.transpose(0,2,1),v,armature,qd);U=float(np.sum(mass*9.81*z[prefix+'body_com_pose'][:,2].astype(float)));return K,U
for i in range(120):
 with np.load(run/f'interval_{i:03d}.npz') as z:
  kb,ub=energy(z,'before_');ka,ua=energy(z,'after_');tau=z['gravity_feedforward'].astype(float);dq=z['after_q'].astype(float)-z['before_q'].astype(float);v=.5*(z['before_qd'].astype(float)+z['after_qd'].astype(float));ffdisp=float(tau@dq);ffmid=float(tau@v/240)
  rows.append(dict(step=i,delta_kinetic_j=ka-kb,delta_potential_j=ua-ub,local_drive_impulse_work_j=float(drive[i]),feedforward_displacement_estimate_j=ffdisp,feedforward_midpoint_estimate_j=ffmid,unclosed_balance_displacement_j=(ka-kb)+(ua-ub)-drive[i]-ffdisp,unclosed_balance_midpoint_j=(ka-kb)+(ua-ub)-drive[i]-ffmid))
keys=[k for k in rows[0] if k!='step'];totals={k:sum(x[k] for x in rows) for k in keys};result={'status':'descriptive_saved_data_balance_not_qualified','native_runs':0,'intervals':120,'same_scene_hash_and_order_verified':True,'totals':totals,'maximum_interval_unclosed_j':max(abs(x['unclosed_balance_displacement_j']) for x in rows),'feedforward_estimators_difference_j':abs(totals['feedforward_displacement_estimate_j']-totals['feedforward_midpoint_estimate_j']),'motor_work_qualified':False,'missing':['Actual applied external/feedforward stage impulse and corresponding physical generalized velocity','Independent proof that coupled local row work equals system drive work','Effective damping/friction/limits and numerical integration work at matched substeps'],'warning':'Unclosed balance is not attributed to damping or error and is not fitted away. Feedforward estimates are not measured actuator work.'}
(w/'intervals.json').write_text(json.dumps(rows,indent=2)+'\n');(w/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
