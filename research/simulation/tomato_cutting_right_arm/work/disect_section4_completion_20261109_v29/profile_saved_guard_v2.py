from pathlib import Path
import sys,json,time,numpy as np
from types import SimpleNamespace
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
import volume_guard as vg
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');old=W.parent/'disect_section4_loading_20261109_v28';state=np.load(old/'coarse0024_final.npz');row=json.loads((old/'coarse0024_result.json').read_text())['rows'][-1]
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation'];T=np.array(row['blade_translation_m']);cad=SimpleNamespace(vertices=np.array(d['vertices']),triangles=np.array(d['triangles']),rotation=rot)
original=vg.certify

def counted(*args,**kwargs):
 start=time.perf_counter();result=original(*args,**kwargs);print(json.dumps(dict(target=kwargs['limit'],measured_wall_s=time.perf_counter()-start,**result)),flush=True);return result
vg.certify=counted
g=vg.WholeVolumeGuard(cad,mesh['tets']);start=time.perf_counter();print('Initial guard',flush=True);a=g.check(state['x'],T)
h=3.125e-6;dq=h*state['v'];dT=h*np.array(row['blade_velocity_m_s']);motion=float(np.linalg.norm(dq,axis=1).max()+np.linalg.norm(dT));print('Pure kinematic prediction only; not a physical solver step',flush=True);b=g.check(state['x']+dq,T+dT,step_motion=motion)
(W/'saved_guard_profile.json').write_text(json.dumps(dict(scope='Read-only guard on saved state and kinematic perturbation; no simulation',wall_s=time.perf_counter()-start,initial=a,prediction=b),indent=2))
