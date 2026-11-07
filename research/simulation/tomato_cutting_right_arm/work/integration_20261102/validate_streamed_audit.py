"""Read back actual compressed records; refuse missing clocks or budget failures."""
from pathlib import Path
import argparse,gzip,json,hashlib
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.run.resolve();manifest=json.loads((run/'input_manifest.json').read_text());result=json.loads((run/'supervisor_result.json').read_text());report=json.loads((run/'hold_measurements.json').read_text())
if not result['passed']:raise ValueError('Cannot qualify a failed native run')
n=manifest['deformable_steps']//manifest['episodes'];dt=manifest['dt_s'];rows=[];finals=[]
for ep in range(manifest['episodes']):
 path=run/f'episode{ep}_audit.jsonl.gz';count=0;limits={'minimum_volume_ratio':(.1,None),'board_penetration_m':(None,.0001),'energy_increase_j':(None,1e-5),'linear_impulse_residual_ns':(None,1e-4),'angular_impulse_residual_nms':(None,1e-5),'cumulative_absolute_nodal_impulse_residual_ns':(None,1e-4)}
 with gzip.open(path,'rt')as stream:
  for count,line in enumerate(stream,1):
   d=json.loads(line)
   if abs(d['time_s']-count*dt)>1e-12:raise ValueError('Missing/misaligned physics clock')
   for key,(lo,hi)in limits.items():
    value=d[key]
    if not np.isfinite(value)or(lo is not None and value<=lo)or(hi is not None and value>hi):raise ValueError('Saved audit exceeds native acceptance: '+key)
 if count!=n or report['episodes'][ep]['steps']!=n:raise ValueError('Audit step count differs from native result')
 state=np.load(run/f'episode{ep}_final.npz');finals.append((state['x_sim'],state['v']));rows.append(dict(episode=ep,complete_gzip_records=count,final_time_s=d['time_s'],audit_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
pe=ve=None
if len(finals)==2:
 pe=float(abs(finals[0][0]-finals[1][0]).max());ve=float(abs(finals[0][1]-finals[1][1]).max())
 if pe>1e-10 or ve>1e-8:raise ValueError('Independent saved-state replay check failed')
a.output.mkdir(exist_ok=False);out=dict(passed=True,episodes=rows,deformable_steps=sum(x['complete_gzip_records']for x in rows),replay_position_error_m=pe,replay_velocity_error_m_s=ve,scope='Read-back integrity, clocks and unchanged numerical budget checks on actual compressed native output. No additional physics/support/cutting qualification.',validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());(a.output/'measurements.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
