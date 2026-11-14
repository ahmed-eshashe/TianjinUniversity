from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_adaptive_contact_20261109_v27'))
import adaptive_contact as ac
mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');old=W.parent/'disect_section4_loading_20261109_v28';state=np.load(old/'coarse0024_final.npz');row=json.loads((old/'coarse0024_result.json').read_text())['rows'][-1]
d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation'];T=np.array(row['blade_translation_m']);verts=np.array(d['vertices'])@rot.T+T;faces=np.array(d['triangles'])
original=ac.query_mesh;start=time.perf_counter();last=start;calls=0;points=0

def counted(*args):
 global calls,points,last
 result=original(*args);calls+=1;points+=len(args[2]);now=time.perf_counter()
 if now-last>5:
  frame=sys._getframe(1);locals_=frame.f_locals
  print(json.dumps(dict(wall_s=now-start,query_calls=calls,query_points=points,caller=frame.f_code.co_name,depth=locals_.get('depth'),interval=[locals_.get('left'),locals_.get('right')])),flush=True);last=now
 return result
ac.query_mesh=counted
c=ac.AdaptiveContact(mesh)
print('Starting pure saved-state contact evaluation; no physical stepping or changed forces',flush=True)
ev=c.evaluate(state['x'],state['v'],verts,faces,np.array(row['blade_velocity_m_s']),T,kd=0.)
out=dict(scope='Single pure CPU evaluation on saved 24 ms state',wall_s=time.perf_counter()-start,query_calls=calls,query_points=points,samples=len(ev['phi']),subintervals=ev['accepted_subintervals'],force_norm_N=float(np.linalg.norm(ev['force'])))
(W/'saved_contact_profile.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
