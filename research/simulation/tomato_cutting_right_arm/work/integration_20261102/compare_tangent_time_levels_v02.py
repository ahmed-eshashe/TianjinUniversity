"""Matching original registry and physical law, expanded short refinement screen."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--levels',nargs='+',type=int,default=[1,2,4,8,16]);args=p.parse_args();r=Path(__file__).resolve().parents[2];names={1:'tangent_short',2:'tangent_fine_short',4:'tangent_finest_short',8:'tangent_refined8_short',16:'tangent_refined16_short'};rows=[];arrays=[]
for ref in args.levels:
 folder=r/'runs/native'/f'{names[ref]}_20261102_01';supervisor=json.loads((folder/'supervisor_result.json').read_text())
 if not supervisor['passed']:raise ValueError('Failed/incomplete levels cannot supply convergence endpoints')
 data=np.load(folder/'episode0_final.npz');x=data['x_sim'];v=data['v'];arrays.append((x,v));manifest=json.loads((folder/'input_manifest.json').read_text())
 if abs(manifest['dt_s']-1/(2400*ref))>1e-16 or manifest['duration_s']!=.01:raise ValueError('Mismatched physical clocks')
 rows.append(dict(refinement=ref,dt_s=manifest['dt_s'],run=str(folder),passed_native_component=True,endpoint_sha256=hashlib.sha256((folder/'episode0_final.npz').read_bytes()).hexdigest()))
for i in range(len(rows)-1):
 dx=arrays[i][0]-arrays[i+1][0];dv=arrays[i][1]-arrays[i+1][1];pe=float(abs(dx).max());ve=float(abs(dv).max());node,axis=np.unravel_index(abs(dv).argmax(),dv.shape);rows[i].update(next_finer_position_difference_m=pe,next_finer_velocity_difference_m_s=ve,velocity_difference_node=int(node),velocity_difference_axis=int(axis),within_screen=bool(pe<=1e-5 and ve<=.001))
report=dict(passed_finest_pair_screen=rows[-2]['within_screen'],duration_s=.01,position_screen_m=1e-5,velocity_screen_m_s=.001,levels=rows,scope='Unfractured standalone endpoint temporal screen; compare final two valid matched levels. No fit or changed physical parameters. Does not establish sustained support, contact convergence, robot work or cutting qualification.',comparison_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());args.output.mkdir(exist_ok=False);(args.output/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
