from pathlib import Path
import sys,json,numpy as np,time
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_padded_material_coverage import padded_coverage as old
from tomato_vectorized_material_coverage import padded_coverage as new
from tomato_host_fixed_pressure import evaluate_fixed,packet_from_samples
from tomato_gpu_packet_refresh import PacketEvaluator
wp.init();wp.set_device('cuda:0')
z=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');x=z['x_sim']+z['world_from_sim_translation_m'];ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());tri=np.array([t for p in d['pieces'] for t in p['triangles']]);R=ref['rotation'];t=ref['translation'];vertices=np.asarray(blade['vertices'])@R.T+t
rows=[]
for level in [2,4]:
 args=(vertices,np.array(solid['cells']),x,tri,z['reference_world']);clock=time.monotonic();a=old(*args,level=level);old_s=time.monotonic()-clock;clock=time.monotonic();b=new(*args,level=level);new_s=time.monotonic()-clock
 pa=packet_from_samples(a['samples']);pb=packet_from_samples(b['samples'])
 assert np.array_equal(pa['indices'],pb['indices']) and np.max(abs(pa['barycentric']-pb['barycentric']))<1e-14 and np.max(abs(pa['areas']-pb['areas']))<1e-18
 host=evaluate_fixed(blade,x,pb,R,t,ref['com_local']);gpu=PacketEvaluator(blade,x,R,t,ref['com_local'])(pb)
 errors={k:float(np.max(abs(host[k]-gpu[k]))) for k in ['energy_j','force_n','body_wrench']}
 assert max(errors.values())<1e-10
 rows.append(dict(level=level,samples=len(pb['areas']),old_s=old_s,new_s=new_s,errors=errors));print(rows[-1],flush=True)
(w/'fast_refresh_check.json').write_text(json.dumps(dict(passed=True,rows=rows),indent=2))
