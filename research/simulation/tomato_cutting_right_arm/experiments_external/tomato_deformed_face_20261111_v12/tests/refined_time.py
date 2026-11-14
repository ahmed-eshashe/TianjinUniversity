from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from front_system import FrontSystem
from gpu_backend import GPUReference
from multicut import volume_certificates
B=W.parent/'tomato_deformed_front_20261111_v11';checks={};result={};states={};start=time.perf_counter()
for label,dt in [('primary',3.90625e-7/16),('half',3.90625e-7/32)]:
    s=FrontSystem.restore(B/'runs/gpu/initial.npz');f=np.zeros_like(s.X);left=s.X[:,0]<.0003;f[left,0]=-.02/left.sum();f[~left,0]=.02/(~left).sum();x0=s.observations()[0];m0=s.metrics();g=GPUReference(s,f,dt=dt);t=time.perf_counter();g.step(round(.0001/dt));g.export();wall=time.perf_counter()-t
    m=s.metrics();work=float(np.sum(f*(s.observations()[0]-x0)));balance=m['energy']-m0['energy']-work
    checks[label+'_volume']=all(c['passed'] for p in s.pieces.values() for c in volume_certificates(p));checks[label+'_mass']=abs(m['mass']-.001728)<1e-12;checks[label+'_energy']=abs(balance)<max(1e-12,.05*max(abs(work),abs(m0['energy'])))
    s.save(W/'runs'/('time_'+label));states[label]=s;result[label]={'dt_s':dt,'sim_s':.0001,'wall_s':wall,'work_J':work,'energy_residual_J':balance,'GPU_bytes':g.memory()};print(label,result[label],flush=True)
p,h=states['primary'].pieces['root'],states['half'].pieces['root'];dx=float(np.linalg.norm(p.T@(p.q-h.q),axis=1).max());dv=float(np.linalg.norm(p.T@(p.vg-h.vg),axis=1).max());dw=abs(result['primary']['work_J']-result['half']['work_J'])/max(abs(result['half']['work_J']),1e-12)
checks['continuous_position']=dx<.0001;checks['continuous_velocity']=dv<.005;checks['material_work']=dw<.05
result['comparison']={'whole_field_position_bound_m':dx,'whole_field_velocity_bound_m_s':dv,'work_relative':dw}
out={'status':'pass_finer_time_reference' if all(checks.values()) else 'failed_finer_time_reference','checks':checks,'results':result,'wall_s':time.perf_counter()-start,'physical_fracture':False};(W/'time_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
