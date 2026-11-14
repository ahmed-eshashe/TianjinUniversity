from pathlib import Path
import sys,json,time,hashlib,numpy as np,numba
W=Path(__file__).resolve().parent;R=W.parents[1];sys.path.insert(0,str(W.parent/'disect_cut_edge_coverage_20261110_v34'))
from complete_edges import CompleteCutEdges
import tomato_compiled_blade_query as module
from fast_cad_query import fast_query
numba.set_num_threads(4);original=module._query
V=W.parent/'disect_bevel_reference_20261109_v33';source=V/'centered0080_resume_final.npz';sha=hashlib.sha256(source.read_bytes()).hexdigest();z=np.load(source);m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');q=z['x'];ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());v=np.array(raw['vertices'])@(A.T@ref['rotation']).T+z['blade_translation'];f=np.array(raw['triangles']);chunks=[]
# Capture the unchanged candidate sampler's real query sequence. This is a
# static overlapping diagnostic, not a new accepted physical trajectory.
def record(v,f,p):chunks.append(p.copy());return original(v,f,p)
module._query=record;sampler=CompleteCutEdges(m);tic=time.perf_counter();baseline=sampler.evaluate(q,np.zeros_like(q),v,f,np.zeros(3),z['blade_translation'],ke=2e6,kd=0.);capture_s=time.perf_counter()-tic;module._query=original
points=np.concatenate(chunks);np.savez_compressed(W/'query_packet.npz',vertices=v,faces=f,points=points,chunk_sizes=np.array([len(p) for p in chunks]));start=time.perf_counter();fast_query(v,f,points[:16]);compile_s=time.perf_counter()-start
# Declared strict geometry checks, plus contact force/energy/wrench controls.
reference=original(v,f,points);optimized=fast_query(v,f,points);errors={name:float(np.max(abs(a-b))) for name,a,b in zip(['phi_m','normal','closest_m','face_index','winding'],reference,optimized)};sign_equal=bool(np.array_equal(reference[0]<0,optimized[0]<0));assert errors['phi_m']<=1e-12 and errors['normal']<=1e-8 and errors['closest_m']<=1e-12 and errors['winding']<=1e-10 and sign_equal
runs=[]
for name,query in [('reference',original),('candidate',fast_query)]:
 tic=time.perf_counter()
 for p in chunks:query(v,f,p)
 runs.append({'name':name,'same_chunk_query_wall_s':time.perf_counter()-tic})
module._query=fast_query;tic=time.perf_counter();candidate=sampler.evaluate(q,np.zeros_like(q),v,f,np.zeros(3),z['blade_translation'],ke=2e6,kd=0.);candidate_s=time.perf_counter()-tic;module._query=original
force_error=float(np.max(abs(candidate['force']-baseline['force'])));energy_error=abs(candidate['energy_J']-baseline['energy_J']);moment_error=float(np.max(abs(candidate['moment']-baseline['moment'])));assert force_error<=1e-8 and energy_error<=1e-12 and moment_error<=1e-8
# Cache invalidation on actual in-place pose change, not just a new array object.
v2=v.copy();shift=np.array([1e-5,-2e-5,3e-5]);v2+=shift;p2=points[::max(1,len(points)//128)]+shift;old=original(v2,f,p2);new=fast_query(v2,f,p2);cache_error=float(np.max(abs(old[0]-new[0])));assert cache_error<1e-12
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
out={'scope':'One CPU implementation candidate, same CAD, original triangle order and sign/distance formulas, unchanged point sequence and quadrature. Static candidate-contact fixture, not cutting or trajectory qualification.','passed':True,'threads':4,'query_chunks':len(chunks),'query_points':len(points),'compile_wall_s_excluded':compile_s,'errors':errors,'inside_outside_signs_equal':sign_equal,'timing_runs':runs,'same_chunk_query_speedup':runs[0]['same_chunk_query_wall_s']/runs[1]['same_chunk_query_wall_s'],'full_static_contact_reference_wall_s_with_query_capture':capture_s,'full_static_contact_candidate_wall_s':candidate_s,'static_contact_max_force_error_N':force_error,'static_contact_energy_error_J':energy_error,'static_contact_moment_error_Nm':moment_error,'in_place_geometry_cache_invalidation_phi_error_m':cache_error,'source_checkpoint_unchanged':True,'coupled_step_and_fresh_half_step_validation_pending':True,'candidate_not_adopted':True}
(W/'query_benchmark_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
