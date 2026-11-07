"""Time-only screen with identical complete native source/input closures."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--levels',nargs='+',type=int,default=[8,16,32]);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=Path(__file__).resolve().parents[2];rows=[];arrays=[];source=None
for ref in a.levels:
 folder=r/'runs/native'/f'fraction_screen{ref}_20261102_01';result=json.loads((folder/'supervisor_result.json').read_text());manifest=json.loads((folder/'input_manifest.json').read_text());closure=json.loads((folder/'source_closure.json').read_text())['source_sha256']
 if not result['passed']or manifest['duration_s']!=.01 or abs(manifest['dt_s']-1/(2400*ref))>1e-16:raise ValueError('Failed component or mismatched clocks')
 if source is None:source=closure
 elif source!=closure:raise ValueError('Source/input closure changed between time levels')
 d=np.load(folder/'episode0_final.npz');arrays.append((d['x_sim'],d['v']));rows.append(dict(refinement=ref,dt_s=manifest['dt_s'],run=str(folder),endpoint_sha256=hashlib.sha256((folder/'episode0_final.npz').read_bytes()).hexdigest()))
for i in range(len(rows)-1):
 dx=arrays[i][0]-arrays[i+1][0];dv=arrays[i][1]-arrays[i+1][1];pe=float(abs(dx).max());ve=float(abs(dv).max());node,axis=np.unravel_index(abs(dv).argmax(),dv.shape);rows[i].update(next_finer_position_difference_m=pe,next_finer_velocity_difference_m_s=ve,velocity_difference_node=int(node),velocity_difference_axis=int(axis),within_screen=bool(pe<=1e-5 and ve<=.001))
report=dict(passed_finest_pair_screen=rows[-2]['within_screen'],duration_s=.01,position_screen_m=1e-5,velocity_screen_m_s=.001,identical_source_and_input_closures=True,levels=rows,scope='Original undamaged full-target endpoint time-only screen, with identical source/input closures. Compare final two valid matched levels. Does not qualify long/contact convergence, sustained settling, robot work, fracture or cutting.',comparison_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());a.output.mkdir(exist_ok=False);(a.output/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
