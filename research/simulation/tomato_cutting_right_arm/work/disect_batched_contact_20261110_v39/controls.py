from pathlib import Path
import sys,json,itertools,time,hashlib,numpy as np
from scipy.spatial import ConvexHull
from scipy.integrate import quad_vec
from batched_contact import BatchedContact as CompleteCutEdges
from adaptive_contact import AdaptiveContact
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_execution_strategy_20261110_v35'))
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_precision_sign_20261110_v38'))
import tomato_compiled_blade_query as backend
from precision_query import precise_query
backend._query=precise_query
from tomato_compiled_blade_query import query_mesh
W=Path(__file__).resolve().parent;R=W.parents[1];V=W.parent/'disect_bevel_reference_20261109_v33';m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');start=time.perf_counter();c=CompleteCutEdges(m);old=AdaptiveContact(m)
# Independent Python adjacency enumeration, distinct from the vectorized builder.
cut=set(map(int,m['ties'].ravel()));expected=set();adj={n:set() for n in cut}
for tet in m['tets']:
 for a,b in itertools.combinations(map(int,tet),2):
  if a in cut or b in cut:expected.add(tuple(sorted((a,b))))
  if a in cut:adj[a].add(b)
  if b in cut:adj[b].add(a)
actual={tuple(sorted(map(int,e))) for e in c.edges};assert actual==expected and len(actual)==len(c.edges)
assert (8967,8969) in actual and (8967,8969) not in {tuple(sorted(map(int,e))) for e in old.edges}
weights=np.array([sum(1/len(adj[n]) for n in [int(a),int(b)] if n in cut) for a,b in c.edges]);assert np.max(abs(weights-c.edge_weights))<1e-15
owner_budget=np.array([sum(1/len(adj[n]) for _ in adj[n]) for n in sorted(cut)]);assert np.max(abs(owner_budget-1))<1e-14 and abs(c.edge_weights.sum()-len(cut))<1e-10
side=np.zeros(len(m['x']),int);side[m['tets'].ravel()]=np.repeat(m['tet_side'],4);assert np.all(side[c.edges[:,0]]==side[c.edges[:,1]])
# Independent closed-form normal force and energy for a solid box crossing.
a=1e-5;ke=2e6;weight=2.;vertices=np.array(list(itertools.product([-a,a],[-.001,.001],[-.001,.001])));faces=ConvexHull(vertices).simplices.copy()
for face in faces:
 p=vertices[face]
 if np.dot(np.cross(p[1]-p[0],p[2]-p[0]),p.mean(0))<0:face[[1,2]]=face[[2,1]]
q=np.array([[-2*a,0,0],[2*a,0,0]]);fixture=CompleteCutEdges.__new__(CompleteCutEdges);fixture.edges=np.array([[0,1]]);fixture.edge_weights=np.array([weight]);fixture.force_atol=1e-10;fixture.rtol=1e-6;fixture.max_depth=40
zero=np.zeros_like(q);ev=fixture.evaluate(q,zero,vertices,faces,np.zeros(3),np.zeros(3),ke=ke,kd=0.);L=4*a;energy=ke*weight*a**3/(3*L);force=ke*weight*a**3/(3*L**2);expected_force=np.array([[-force,0,0],[force,0,0]]);ferror=float(np.max(abs(ev['force']-expected_force)));eerror=abs(ev['energy_J']-energy);assert ferror<=1e-10+1e-9*force and eerror<=1e-12
shift=np.array([.003,.007,-.002]);moved=fixture.evaluate(q+shift,zero,vertices+shift,faces,np.zeros(3),shift,ke=ke,kd=0.);rigiderror=float(np.max(abs(moved['force']-ev['force'])));assert rigiderror<1e-8
fixture.edges=np.array([[1,0]]);reverse=fixture.evaluate(q,zero,vertices,faces,np.zeros(3),np.zeros(3),ke=ke,kd=0.);reverseerror=float(np.max(abs(reverse['force']-ev['force'])));assert reverseerror<1e-10
fixture.edges=np.array([[0,1]]);eps=1e-10;energies=[]
for direction in [-1,1]:
 qp=q.copy();qp[0,0]+=direction*eps;energies.append(fixture.evaluate(qp,zero,vertices,faces,np.zeros(3),np.zeros(3),ke=ke,kd=0.)['energy_J'])
graderror=abs((energies[1]-energies[0])/(2*eps)+ev['force'][0,0]);assert graderror<1e-8
# Immutable saved state, missing physical edge only. Independent plane hits +
# SciPy Gauss-Kronrod integration; no GPU, dynamics or history commit.
z=np.load(V/'centered0080_resume_final.npz');q=z['x'];i,j=8967,8969;k=next(k for k,e in enumerate(c.edges) if set(map(int,e))=={i,j});i,j=map(int,c.edges[k]);weight=float(c.edge_weights[k]);fixture.edges=np.array([[i,j]]);fixture.edge_weights=np.array([weight]);raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);vertices=np.array(raw['vertices'])@(A.T@ref['rotation']).T+z['blade_translation'];faces=np.array(raw['triangles']);zero=np.zeros_like(q);ev=fixture.evaluate(q,zero,vertices,faces,np.zeros(3),z['blade_translation'],ke=ke,kd=0.)
delta=q[j]-q[i];hits=[0.,1.]
for face in faces:
 p0,p1,p2=vertices[face];normal=np.cross(p1-p0,p2-p0);den=normal@delta
 if abs(den)<1e-20:continue
 t=float(normal@(p0-q[i])/den)
 if not 0<t<1:continue
 uv=np.linalg.lstsq(np.column_stack((p1-p0,p2-p0)),q[i]+t*delta-p0,rcond=None)[0]
 if min(uv)>=-1e-12 and sum(uv)<=1+1e-12:hits.append(t)
hits=np.unique(np.round(hits,14));reference=np.zeros(7)
def fun(u):
 r=query_mesh(vertices,faces,(q[i]+u*delta)[None]);phi=float(r['phi'][0]);force=ke*max(-phi,0)*r['normal'][0];return weight*np.r_[(1-u)*force,u*force,.5*ke*min(phi,0)**2]
for left,right in zip(hits[:-1],hits[1:]):
 if query_mesh(vertices,faces,(q[i]+.5*(left+right)*delta)[None])['phi'][0]>=0:continue
 integral,error=quad_vec(fun,left,right,epsabs=1e-13,epsrel=1e-10,limit=2000);reference+=integral
caderror=float(np.max(abs(np.r_[ev['force'][i],ev['force'][j]]-reference[:6])));cadenergyerror=abs(ev['energy_J']-reference[6]);assert caderror<1e-8 and cadenergyerror<1e-12
# Full saved-geometry operator comparison, unchanged query and physical inputs.
from complete_edges import CompleteCutEdges as Reference
new=CompleteCutEdges(m);old=Reference(m);comparisons=[]
for version,checkpoint in [('disect_precision_sign_20261110_v38','precise0050_final.npz'),('disect_bevel_reference_20261109_v33','centered0080_resume_final.npz')]:
 saved=np.load(W.parent/version/checkpoint);q=saved['x'];vv=saved['v'];vertices=np.array(raw['vertices'])@(A.T@ref['rotation']).T+saved['blade_translation'];com=saved['blade_translation'];results=[];times=[]
 for op in [old,new]:
  tick=time.perf_counter();results.append(op.evaluate(q,vv,vertices,faces,saved['blade_velocity'],com,ke=ke,kd=0.));times.append(time.perf_counter()-tick)
 aa,bb=results;df=float(np.max(np.abs(aa['force']-bb['force'])));de=abs(aa['energy_J']-bb['energy_J']);assert df<1e-8 and de<1e-12
 comparisons.append(dict(checkpoint=checkpoint,force_error_N=df,energy_error_J=de,reference_wall_s=times[0],batched_wall_s=times[1],speedup=times[0]/times[1],reference_intervals=aa['accepted_subintervals'],batched_intervals=bb['accepted_subintervals']))
out={'saved_full_operator_comparisons':comparisons,'scope':'Independent static component controls for a candidate correction of excluded cut-to-cut physical edges; not adopted in a coupled run, no cutting/separation qualification','passed':True,'old_edge_count':len(old.edges),'candidate_edge_count':len(c.edges),'cut_cut_edges_added':len(c.edges)-len(old.edges),'physical_cut_node_count':len(cut),'contact_sampling_budget_old':float(old.edge_weights.sum()),'contact_sampling_budget_candidate':float(c.edge_weights.sum()),'max_owner_budget_error':float(np.max(abs(owner_budget-1))),'no_cross_bank_edges':True,'box_closed_form_force_error_N':ferror,'box_closed_form_energy_error_J':eerror,'box_rigid_translation_error_N':rigiderror,'edge_reversal_error_N':reverseerror,'box_energy_gradient_error_N':float(graderror),'actual_saved_missing_edge':[i,j],'actual_missing_edge_weight':weight,'actual_edge_independent_force_error_N':caderror,'actual_edge_independent_energy_error_J':cadenergyerror,'detected_sampled_penetration_on_missing_edge_m':float(np.maximum(-ev['phi'],0).max()),'actual_edge_static_force_N':{str(i):ev['force'][i].tolist(),str(j):ev['force'][j].tolist()},'static_overlap_fixture_not_an_admissible_episode':True,'wall_s':time.perf_counter()-start,'coupled_fresh_half_step_validation_pending':True,'whole_volume_guard_still_required':True}
(W/'controls_result.json').write_text(json.dumps(out,indent=2)+'\n');(W/'source_manifest.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).resolve(),W/'batched_contact.py',V/'volume_witness_review.json']},indent=2)+'\n');print(json.dumps(out,indent=2))
