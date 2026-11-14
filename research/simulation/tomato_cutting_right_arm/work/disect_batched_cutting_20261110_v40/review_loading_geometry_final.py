"""One read-only normal-contact/geometry audit of a saved accepted state.
Static normal forces are labelled separately from full dynamic blade reaction.
"""
from pathlib import Path
import sys,argparse,json,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
for name in ['disect_batched_contact_20261110_v39','disect_precision_sign_20261110_v38','disect_execution_strategy_20261110_v35']:sys.path.insert(0,str(W.parent/name))
from batched_contact import BatchedContact
from precision_query import precise_query
import tomato_compiled_blade_query as backend
import numba
numba.set_num_threads(4);backend._query=precise_query
p=argparse.ArgumentParser();p.add_argument('checkpoint');args=p.parse_args();z=np.load(args.checkpoint);m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');q=z['x'];q0=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];tt=m['tets'];pairs=m['ties'];side=np.zeros(len(q),int);side[tt.ravel()]=np.repeat(m['tet_side'],4)
assert np.all(side[pairs[:,0]]*side[pairs[:,1]]<0)
ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rot=A.T@ref['rotation'];raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());T=z['blade_translation'];vertices=np.array(raw['vertices'])@rot.T+T;faces=np.array(raw['triangles']);c=BatchedContact(m);ev=c.evaluate(q,np.zeros_like(q),vertices,faces,np.zeros(3),T,ke=2e6,kd=0.);ids=ev['ids'];assert np.all(side[ids[:,0]]==side[ids[:,1]])
load=2e6*ev['weights']*np.maximum(-ev['phi'],0);lateral=(abs(ev['normal'][:,0])>.9)&(load>0);bank=side[ids[:,0]];banks={}
for s in [-1,1]:
 k=bank==s;lat=k&lateral;outward=ev['normal'][:,0]*s>0
 banks[str(s)]={'normal_force_vector_N':(load[k,None]*ev['normal'][k]).sum(0).tolist(),'normal_load_sum_N':float(load[k].sum()),'lateral_load_outward_N':float(load[lat&outward].sum()),'lateral_load_inward_N':float(load[lat&~outward].sum()),'lateral_sample_count':int(lat.sum())}
negative=np.where(side[pairs[:,0]]<0,pairs[:,0],pairs[:,1]);positive=np.where(side[pairs[:,0]]>0,pairs[:,0],pairs[:,1]);result=backend.query_mesh(vertices,faces,np.concatenate((q[negative],q[positive])));n=len(pairs);ph=np.column_stack((result['phi'][:n],result['phi'][n:]));normal=np.stack((result['normal'][:n],result['normal'][n:]),axis=1);near=np.max(abs(ph),axis=1)<1e-4;same=(normal[:,0,0]*normal[:,1,0]>0)&(abs(normal[:,:,0]).min(1)>.9);opposed=(normal[:,0,0]<-.9)&(normal[:,1,0]>.9);delta=q[positive]-q[negative]
rest=m['x'];ratio=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/np.linalg.det(rest[tt[:,1:]]-rest[tt[:,0]][:,None]);worst=int(np.argmin(ratio));out={'scope':'Read-only saved geometry and elastic NORMAL contact decomposition on cut-incident physical edges. Not full dynamic force, causality, a path-miss verdict, damage/separation qualification or permission to alter contact.','checkpoint':str(Path(args.checkpoint).resolve()),'sim_s':float(z['step']*z['dt']),'maximum_committed_opening_m':float(z['history'][:,0].max()),'maximum_damage':float(z['history'][:,1].max()),'normal_edge_contact_by_material_bank':banks,'cut_pair_count':n,'pairs_both_within_0_1mm_blade':int(near.sum()),'near_pairs_nearest_same_lateral_face':int((near&same).sum()),'near_pairs_nearest_opposed_lateral_faces':int((near&opposed).sum()),'maximum_raw_twin_distance_m':float(np.linalg.norm(delta,axis=1).max()),'maximum_raw_positive_X_twin_opening_m':float(delta[:,0].max()),'mean_cut_surface_displacement_m':((q[negative]+q[positive]-q0[negative]-q0[positive])/2).mean(0).tolist(),'worst_element':{'id':worst,'nodes':tt[worst].tolist(),'volume_ratio':float(ratio[worst]),'positions_m':q[tt[worst]].tolist(),'vertex_signed_blade_distances_m':backend.query_mesh(vertices,faces,q[tt[worst]])['phi'].tolist()},'no_history_or_geometry_changes':True};(W/'final_loading_geometry_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
