"""Read-only integration audit using saved joint endpoint velocities."""
from pathlib import Path
import json,math,struct
ROOT=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');RUN=ROOT/'runs/native/bent_origin_20261101_01'
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def replay(q,v0,v1,substeps=16,fused=False):
    h=f32((1/2400)/substeps)
    for n in range(substeps):
        v=f32(v0+(v1-v0)*(n+1)/substeps)
        q=f32(q+v*h) if fused else f32(q+f32(v*h))
    return q

def audit():
    data=json.loads((RUN/'bent_origin_partial.json').read_text());cases=[]
    for c in data['cases']:
        rows=[];running={mode:list(c['initial']['q']) for mode in ('fused','separate','double')}
        for s in c['steps']:
            if 'after' not in s:continue
            b=s['before'];a=s['after'];dt=1/2400;variants={}
            double=[q+dt*v0+17/32*dt*(v1-v0) for q,v0,v1 in zip(b['q'],b['qd'],a['qd'])]
            for mode in ('fused','separate'):
                local=[replay(q,v0,v1,fused=mode=='fused') for q,v0,v1 in zip(b['q'],b['qd'],a['qd'])]
                running[mode]=[replay(q,v0,v1,fused=mode=='fused') for q,v0,v1 in zip(running[mode],b['qd'],a['qd'])]
                variants[mode]=dict(local_q=local,local_error_rad=max(abs(x-y) for x,y in zip(local,a['q'])),
                    accumulated_q=running[mode].copy(),accumulated_error_rad=max(abs(x-y) for x,y in zip(running[mode],a['q'])))
            running['double']=[q+dt*v0+17/32*dt*(v1-v0) for q,v0,v1 in zip(running['double'],b['qd'],a['qd'])]
            rows.append(dict(interval=s['interval'],contact_count=s['contact_count'],measured_after_q=a['q'],
                measured_velocity_conditioned_double_local_error_rad=max(abs(x-y) for x,y in zip(double,a['q'])),
                measured_velocity_conditioned_double_accumulated_error_rad=max(abs(x-y) for x,y in zip(running['double'],a['q'])),variants=variants))
        cases.append(dict(id=c['id'],assessed_intervals=len(rows),rows=rows))
    return dict(cases=cases,scope='Conditioned on measured endpoint velocities; 16 uniformly spaced acceleration increments hypothesized, no internal substep telemetry.')
if __name__=='__main__':
    d=audit();(ROOT/'work/bent_joint_precision_audit.json').write_text(json.dumps(d,indent=2)+'\n')
    for c in d['cases']:
        print(c['id'],c['assessed_intervals'])
        for mode in ('fused','separate'):
            print(mode,'local',max(r['variants'][mode]['local_error_rad'] for r in c['rows']),'accum',max(r['variants'][mode]['accumulated_error_rad'] for r in c['rows']))
        print('double accumulated',max(r['measured_velocity_conditioned_double_accumulated_error_rad'] for r in c['rows']))
