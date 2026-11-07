"""Independent unchanged implementation versus immutable-CAD coefficient cache."""
from pathlib import Path
import sys,json,time,numpy as np
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_local_plane_partition import partition as reference
from tomato_cached_local_plane_partition import partition as candidate
from tomato_cached_plane_partition import coefficients
z=np.load(w/'robot_cut13/checkpoints/step_005375.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());G=np.full((3,3),1/6);np.fill_diagonal(G,2/3);ids=z['packet_indices'][::3];leaves=np.linalg.inv(G)@z['packet_barycentric'].reshape(-1,3,3);areas=z['packet_areas'].reshape(-1,3).sum(1);args=(blade,ids,leaves,areas,z['x'],z['blade_rotation'],z['blade_translation'],list(range(len(blade['triangles']))))
start=time.monotonic();a=reference(*args);reference_time=time.monotonic()-start
start=time.monotonic();b=candidate(*args);cold=time.monotonic()-start
start=time.monotonic();c=candidate(*args);warm=time.monotonic()-start
same=[np.array_equal(x,y) for x,y in zip(a[:3],b[:3])];again=[np.array_equal(x,y) for x,y in zip(a[:3],c[:3])]
if not all(same+again):raise ValueError(('Partition changed',same,again))
# A changed CAD vertex must produce a distinct coefficient-cache key.
old=coefficients.cache_info().misses;v=np.asarray(blade['vertices'],dtype=np.float64).copy();v[0,0]+=1e-8;coefficients(v.tobytes(),np.asarray(blade['triangles'],dtype=np.int64).tobytes(),(0,1));assert coefficients.cache_info().misses==old+1
report=dict(passed=True,scope='Exact partition outputs for all saved pressure cells; no physical-model change',indices_bit_identical=same[0],cells_bit_identical=same[1],areas_bit_identical=same[2],reference_s=reference_time,cold_cache_s=cold,warm_cache_s=warm,cache_key_invalidation_checked=True,cache_info=str(coefficients.cache_info()));(w/'static_plane_cache_check.json').write_text(json.dumps(report,indent=2));print(report)
