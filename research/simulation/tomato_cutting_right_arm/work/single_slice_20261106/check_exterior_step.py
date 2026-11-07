from pathlib import Path
import sys,json,time
import numpy as np
from scipy.spatial.transform import Rotation
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent
sys.path.insert(0,str(r/'rl'))
from tomato_live_slice_engine import live_engine
from tomato_exterior_live_slice_engine import live_engine as candidate_engine
checkpoint=w/'live16/checkpoint.npz';z=np.load(checkpoint)
ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
R=z['blade_rotation'];pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(R).as_quat()]
next_pose=pose.copy();next_pose[:3]+=np.array([R[2,2]/R[0,2],0,-1])*.02/2400
states=[];times=[]
for factory in [live_engine,candidate_engine]:
    g=factory(pose,ref['com_local'],checkpoint=checkpoint,padding_m=.001);next(g)
    start=time.perf_counter();states.append(g.send(dict(pose=next_pose,dt=1/2400)));times.append(time.perf_counter()-start);g.close()
a,b=states
result=dict(position_error_m=float(abs(a['x']-b['x']).max()),
    velocity_error_m_s=float(abs(a['v']-b['v']).max()),history_error=float(abs(a['history']-b['history']).max()),
    reaction_error=float(abs(a['wrench']-b['wrench']).max()),baseline_s=times[0],candidate_s=times[1],adopted=False)
result['passed']=result['position_error_m']<1e-12 and result['velocity_error_m_s']<1e-9 and result['history_error']<1e-12 and result['reaction_error']<1e-9
(w/'exterior_step_check.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
