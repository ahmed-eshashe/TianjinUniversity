from pathlib import Path
import json,sys,time,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_adaptive_contact_20261109_v27'))
from adaptive_contact import AdaptiveContact,query_mesh,law
old=W.parent/'disect_section4_loading_20261109_v28';state=np.load(old/'coarse0024_final.npz');result=json.loads((old/'coarse0024_result.json').read_text());row=result['rows'][-1];q=state['x'];v=state['v'];T=np.array(row['blade_translation_m']);tv=np.array(row['blade_velocity_m_s'])
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');d=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');rot=np.array([[1,0,0],[0,0,-1],[0,1,0]],float).T@ref['rotation'];verts=np.array(d['vertices']);faces=np.array(d['triangles']);cad_world=verts@rot.T+T;c=AdaptiveContact(m);ev=c.evaluate(q,v,cad_world,faces,tv,T,kd=1.);force=ev['force'].copy()
ids=c.outer;local=(q[ids]-T)@rot;keep=np.all((local>=verts.min(0))&(local<=verts.max(0)),axis=1);ids=ids[keep];query=query_mesh(verts,faces,(q[ids]-T)@rot);normal=query['normal']@rot.T;force[ids]+=law(query['phi'],normal,v[ids],tv,kd=1.)
side=np.zeros(len(q),int)
for sign in [-1,1]:side[np.unique(m['tets'][m['tet_side']==sign])]=sign
rows=[]
for sign in [-1,1]:
 f=force[side==sign];rows.append(dict(material_bank=sign,net_contact_force_N=f.sum(0).tolist(),sum_contact_force_magnitudes_N=float(np.linalg.norm(f,axis=1).sum()),contacted_nodes=int((np.linalg.norm(f,axis=1)>1e-12).sum())))
ties=m['ties'];a,b=ties[:,0],ties[:,1];both=(np.linalg.norm(force[a],axis=1)>1e-12)&(np.linalg.norm(force[b],axis=1)>1e-12)
out=dict(scope='Read-only force-direction audit on actual saved 24 ms state; no changed force model or new simulation',sim_s=.024,banks=rows,reaction_N=(-force.sum(0)).tolist(),saved_reaction_N=row['reaction_N'],reaction_reference_error_N=float(np.linalg.norm(-force.sum(0)-row['reaction_N'])),both_twin_endpoints_contacted=int(both.sum()),twin_pairs_opposed_x_force=int((both&(force[a,0]*force[b,0]<0)).sum()),twin_pairs_same_x_force=int((both&(force[a,0]*force[b,0]>0)).sum()),maximum_eligible_opening_m=row['maximum_opening_m'],damage_max=row['damage_max'],note='Bank net directions diagnose loading, not a force law change or proof of cause. Elastic contact still uses ke=2000 N/m with the approved unit-budget edge integration.')
(W/'saved_bank_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
