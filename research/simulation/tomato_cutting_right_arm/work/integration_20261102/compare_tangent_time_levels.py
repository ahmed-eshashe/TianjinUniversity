"""Matching-source unfractured endpoint screen; never establishes a cut pass."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--duration',action='store_true');p.add_argument('--output',type=Path,required=True);args=p.parse_args();r=Path(__file__).resolve().parents[2];suffix='duration'if args.duration else'short';names=[f'tangent_{suffix}_20261102_01',f'tangent_fine_{suffix}_20261102_01',f'tangent_finest_{suffix}_20261102_01'];rows=[];arrays=[];passed=True
for name in names:
 folder=r/'runs/native'/name;supervisor=json.loads((folder/'supervisor_result.json').read_text())
 if not supervisor['passed']:raise ValueError('A failed/incomplete level cannot supply a convergence endpoint: '+name)
 data=np.load(folder/'episode0_final.npz');arrays.append((data['x_sim']if'x_sim'in data else data['x'],data['v']));rows.append(dict(run=name,passed_native_component=True,endpoint_sha256=hashlib.sha256((folder/'episode0_final.npz').read_bytes()).hexdigest()))
for i in range(2):
 pe=float(abs(arrays[i][0]-arrays[i+1][0]).max());ve=float(abs(arrays[i][1]-arrays[i+1][1]).max());rows[i].update(next_finer_position_difference_m=pe,next_finer_velocity_difference_m_s=ve,within_screen=bool(pe<=1e-5 and ve<=.001))
passed=rows[1]['within_screen'];report=dict(passed_finest_pair_screen=passed,duration_s=.1 if args.duration else .01,position_screen_m=1e-5,velocity_screen_m_s=.001,levels=rows,scope='Matched unfractured standalone endpoint time-refinement screen only. Three valid native levels and comparison of finest two; no fit, material retuning, whole-system robot work, sustained support, fracture or cutting claim. Investigate nonmonotone results and retain all failures.');args.output.mkdir(exist_ok=False);(args.output/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
