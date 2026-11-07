from pathlib import Path
import sys,json,numpy as np,time
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_partitioned_packet_refresh import refresh_packet
from tomato_gpu_packet_refresh import PacketEvaluator
wp.init();wp.set_device('cuda:0');z=np.load(w/'profile_partition_start.npz');prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');origin=prepared['world_from_sim_translation_m'];x=z['x']+origin;b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());tri=np.array([t for p in d['pieces'] for t in p['triangles']]);R=z['blade_rotation'];t=z['blade_translation']+origin;old={k:z['packet_'+k]for k in ['indices','barycentric','areas']};
start=time.monotonic();p,v,report=refresh_packet(b,np.asarray(solid['cells']),x,tri,prepared['reference_world'],R,t,ref['com_local'],old,padding_m=4e-5);baseline_time=time.monotonic()-start
import tomato_contact_plane_partition as original
from tomato_compiled_plane_partition import partition
original.partition=partition
for attempt in range(2):
 start=time.monotonic();q,vq,rq=refresh_packet(b,np.asarray(solid['cells']),x,tri,prepared['reference_world'],R,t,ref['com_local'],old,padding_m=4e-5);elapsed=time.monotonic()-start
result=dict(force_difference_n=float(np.linalg.norm(v['force_n']-vq['force_n'])),energy_difference_j=float(abs(v['energy_j']-vq['energy_j'])),area_difference_m2=float(abs(p['areas'].sum()-q['areas'].sum())),original_s=baseline_time,compiled_s=elapsed,original_samples=len(p['areas']),compiled_samples=len(q['areas']))
result['passed']=result['force_difference_n']<1e-8 and result['energy_difference_j']<1e-12 and result['area_difference_m2']<1e-16
(w/'compiled_partition_check.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
