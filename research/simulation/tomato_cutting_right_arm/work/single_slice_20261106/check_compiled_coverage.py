"""Compare compiled polygon arithmetic to the unchanged Python geometry."""
from pathlib import Path
import sys,json,time,numpy as np
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_vectorized_material_coverage import padded_coverage as reference
from tomato_compiled_material_coverage import padded_coverage as candidate
from tomato_native_full_model import registry
blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());data=registry();rest=data['x']+np.array([0,0,.002]);tri=np.array([t for piece in data['design']['pieces'] for t in piece['triangles']]);results=[]
for path in [w/'robot_cut13/checkpoints/step_005375.npz',w/'robot_cut14/checkpoints/step_005400.npz']:
 z=np.load(path);x=z['x']+[-.0225,0,.0295];v=np.array(blade['vertices'])@z['blade_rotation'].T+z['blade_translation']+[-.0225,0,.0295];args=(v,solid['cells'],x,tri,rest)
 start=time.monotonic();a=reference(*args,padding_m=.001,level=0);ta=time.monotonic()-start
 start=time.monotonic();b=candidate(*args,padding_m=.001,level=0);tb=time.monotonic()-start
 row=dict(checkpoint=str(path),reference_s=ta,compiled_s=tb,reference_samples=len(a['samples']),compiled_samples=len(b['samples']),area_difference_m2=float(abs(a['reference_area_m2']-b['reference_area_m2'])))
 if len(a['samples'])==len(b['samples']):
  row['corners_identical']=all(q['corners']==p['corners'] for q,p in zip(a['samples'],b['samples']));row['maximum_barycentric_difference']=float(np.max(abs(np.array([p['barycentric']for p in a['samples']])-np.array([p['barycentric']for p in b['samples']]))));row['maximum_sample_area_difference_m2']=float(np.max(abs(np.array([p['area_m2']for p in a['samples']])-np.array([p['area_m2']for p in b['samples']]))))
 row['passed']=bool(row.get('corners_identical',False) and row.get('maximum_barycentric_difference',1)<1e-12 and row.get('maximum_sample_area_difference_m2',1)<1e-16 and row['area_difference_m2']<1e-14)
 results.append(row);print(row,flush=True)
(w/'compiled_coverage_check.json').write_text(json.dumps(dict(passed=all(p['passed']for p in results),scope='Geometry arithmetic only; material replay required before adoption',results=results),indent=2))
