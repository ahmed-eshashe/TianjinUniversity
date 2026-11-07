from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation,Slerp
from pxr import Usd
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'scripts'))
from reach_kinematics import ArmKinematics,PALM_OFFSET
p=json.loads((r/'work/backward_elbow_20261105/plan.json').read_text());k=ArmKinematics(Usd.Stage.Open(p['scene']));k.upper[5]=.85;k.lower[6]=-.85;mount=np.asarray(p['mount_hand_from_knife']);q=np.asarray(p['approach_routes'][-1][-1]);initial=k.transforms(q)[k.hand_path]@mount
ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');F=Rotation.from_euler('z',-70,degrees=True).as_matrix();rotation=F@ref['rotation'];shift=np.array([0.,-.06,0.]);translation=F@ref['translation']+shift;blade=np.asarray(json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices']);end_z=.001-(blade@rotation.T)[:,2].min();direction=np.array([-ref['rotation'][2,2]/ref['rotation'][0,2],0,1.]);translation=translation-F@direction*.005;rows=[]
orient=Slerp([0,1],Rotation.from_matrix([initial[:3,:3],rotation]));last=q.copy()
for phase,points in [('entry',[(initial[:3,3]*(1-u)+translation*u,orient(u).as_matrix()) for u in np.linspace(0,1,121)]),('cut',[(F@(ref['translation']+direction*(z-ref['translation'][2]))+shift,rotation) for z in np.linspace(ref['translation'][2]+.005,end_z,241)])]:
 for pi,(position,rr) in enumerate(points):
  k.upper[5]=.900001-.050001*(pi/(len(points)-1) if phase=='entry' else 1.)
  hand_rot=rr@mount[:3,:3].T;q,e,a=k.solve(position-hand_rot@mount[:3,3]+hand_rot@PALM_OFFSET,hand_rot,q)
  if e>2e-5 or a>2e-4 or np.max(abs(q-last))>.05:raise ValueError(('IK continuity/accuracy failure',phase,e,a,float(np.max(abs(q-last)))))
  rows.append(dict(phase=phase,q=q.tolist(),tool_origin=position.tolist(),tool_rotation=rr.tolist(),position_error=e,angle_error=a));last=q.copy()
result=dict(passed=True,kinematic_only=True,robot_dynamics_checked=False,collisions_checked=False,full_slice=False,target_rotation=F.tolist(),target_translation=shift.tolist(),stroke_vertical_m=float(ref['translation'][2]-end_z),blade_board_clearance_at_end_m=.001,rows=rows)
(w/'clear_entry_robot_plan_v4.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k!='rows'})
