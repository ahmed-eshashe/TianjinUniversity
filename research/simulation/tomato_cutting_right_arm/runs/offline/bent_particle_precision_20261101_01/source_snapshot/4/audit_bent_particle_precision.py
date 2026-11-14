"""Read-only binary32 audit of the preserved five-interval failed run."""
from pathlib import Path
import json,math,struct,hashlib
ROOT=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm')
RUN=ROOT/'runs/native/bent_sequence_20261101_01'
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def ulp32(x):
    bits=struct.unpack('I',struct.pack('f',abs(x)))[0]
    return struct.unpack('f',struct.pack('I',bits+1))[0]-abs(f32(x))
def audit():
    data=json.loads((RUN/'bent_sequence_partial.json').read_text());dt=1/2400;d32=f32(dt);cases=[]
    for c in data['cases']:
        mp=c['particle_mass_kg'];records=[];accum=[0.]*3
        for s in c['steps']:
            p=s['before']['p'];v=s['before']['vp'];pout=s['particle_after'];vout=s['particle_velocity_after'];force=s['force_n']
            recon=[f32(f32(b-a)/d32) for a,b in zip(p,pout)]
            reciprocal=[f32(f32(b-a)*f32(1/d32)) for a,b in zip(p,pout)]
            residual=[mp*(w-u)-dt*f for w,u,f in zip(vout,v,force)]
            for j in range(3):accum[j]+=residual[j]
            variants={}
            for fused in (False,True):
                inertia=[f32(a+u*d32) if fused else f32(a+f32(u*d32)) for a,u in zip(p,v)]
                equilibrium=[a+d32*d32/mp*f for a,f in zip(inertia,force)]
                offset=[b-a for a,b in zip(equilibrium,pout)]
                forward=[mp/dt*(a-b-dt*u) for a,b,u in zip(inertia,p,v)]
                stationary=[mp/dt*(b-a)-dt*f for a,b,f in zip(inertia,pout,force)]
                vround=[mp*(w-(b-a)/dt) for w,a,b in zip(vout,p,pout)]
                identity=[forward[j]+stationary[j]+vround[j] for j in range(3)]
                variants['fused' if fused else 'separate']=dict(inertial_position_prediction=inertia,
                    native_force_equilibrium_position=equilibrium,position_offset_m=offset,
                    position_offset_in_binary32_ulps=[abs(e)/ulp32(b) for e,b in zip(offset,pout)],
                    forward_rounding_impulse_ns=forward,stationarity_impulse_ns=stationary,velocity_rounding_impulse_ns=vround,
                    decomposition_identity_error_ns=math.dist(identity,residual))
            records.append(dict(interval=s['interval'],velocity_reconstruction_error_m_s=math.dist(recon,vout),
                reciprocal_velocity_reconstruction_error_m_s=math.dist(reciprocal,vout),impulse_residual_ns=residual,
                cumulative_impulse_error_ns=math.hypot(*accum),variants=variants))
        cases.append(dict(id=c['id'],steps=records,latest_cumulative_impulse_error_ns=math.hypot(*accum)))
    return dict(failed_run=str(RUN),dt_s=dt,binary32_dt_s=d32,cases=cases,
        source='Preserved positions, velocities and native cached forces; CPU binary32 arithmetic emulation, not a new native run.')
if __name__=='__main__':
    d=audit();(ROOT/'work/bent_particle_precision_audit.json').write_text(json.dumps(d,indent=2)+'\n')
    for c in d['cases']:
        print(c['id'],'impulse',c['latest_cumulative_impulse_error_ns'])
        print('velocity reconstruction',max(s['velocity_reconstruction_error_m_s'] for s in c['steps']))
        print('reciprocal reconstruction',max(s['reciprocal_velocity_reconstruction_error_m_s'] for s in c['steps']))
        for v in ('separate','fused'):
            print(v,'max equilibrium offset/ulp',max(max(s['variants'][v]['position_offset_in_binary32_ulps']) for s in c['steps']))
