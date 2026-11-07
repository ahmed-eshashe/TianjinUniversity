from pathlib import Path
import sys,json,numpy as np,time
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_adaptive_packet_refresh import refresh_packet
from tomato_host_fixed_pressure import evaluate_fixed,packet_from_samples
from tomato_vectorized_material_coverage import padded_coverage
wp.init();wp.set_device('cuda:0');z=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');x=z['x_sim']+z['world_from_sim_translation_m'];ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());tri=np.array([t for p in d['pieces'] for t in p['triangles']]);R=ref['rotation'];t=ref['translation'];previous={k:ref[k]for k in ['indices','barycentric','areas']};start=time.monotonic();p,v,report=refresh_packet(b,np.asarray(solid['cells']),x,tri,z['reference_world'],R,t,ref['com_local'],previous,padding_m=4e-5);elapsed=time.monotonic()-start
host=evaluate_fixed(b,x,p,R,t,ref['com_local']);error=float(np.max(abs(host['force_n']-v['force_n'])));assert error<1e-10
original=packet_from_samples(padded_coverage(np.array(b['vertices'])@R.T+t,np.array(solid['cells']),x,tri,z['reference_world'],padding_m=1e-5,level=5,capacity=524288)['samples']);truth=evaluate_fixed(b,x,original,R,t,ref['com_local']);fe=float(np.linalg.norm(truth['force_n']-v['force_n']));ee=float(abs(truth['energy_j']-v['energy_j']));assert fe<report['quadrature'][-1]['force_budget_n'] and ee<report['quadrature'][-1]['energy_budget_j']
result=dict(passed=True,samples=len(p['areas']),elapsed_s=elapsed,host_gpu_error=error,independent_uniform_level5_force_difference=fe,independent_uniform_level5_energy_difference=ee,report=report);(w/'adaptive_refresh_check.json').write_text(json.dumps(result,indent=2));print(result)
