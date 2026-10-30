"""Bounded stdlib layout/coupon runner. Never imports Newton, Isaac or Torch."""
import argparse
import fcntl
import hashlib
import io
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    # Offline ceilings do not replace or modify simulator startup/runtime reserves.
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    def timeout(signum,frame):
        raise TimeoutError('Offline 45-second wall budget exceeded')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(45)
    start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        args.output.mkdir(parents=True,exist_ok=False)
        from tomato_layout import build_layout,audit_layout
        from tomato_bonds import (CohesiveLaw,DamageState,update_damage,scalar_response,
                                  bundle_response,update_bundle_damage)
        layout=build_layout(); layout_checks=audit_layout(layout)
        (args.output/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
        # A second area quadrature only, not a mechanically finer tomato or dynamics.
        refined=build_layout(area_radial=64,area_angular=256)
        area_l1=sum(abs(a['area_m2']-b['area_m2']) for a,b in zip(layout['interface_patches'],refined['interface_patches']))/layout['analytic_cut_area_m2']
        law=CohesiveLaw(1000.,25e-6,40000.,80.,.2)
        rest=[(.005,0.,0.),(.005,.005,0.),(.005,-.005,0.),(.005,0.,.005),(.005,0.,-.005)]
        coupon={'inputs':{'status':'synthetic constitutive engineering test; not tomato calibration','stiffness_n_m':1000.,'area_m2':25e-6,
                          'peak_traction_pa':40000.,'fracture_energy_j_m2':80.,'damping_n_s_m':.2},
                'onset_m':law.onset_m,'failure_m':law.failure_m,'expected_fracture_work_j':law.area_m2*law.fracture_energy_j_m2,
                'scalar_and_bundle_work':{}}
        for mode in ['scalar_opening','bundle_opening','bundle_shear']:
            state=DamageState(); work=0.; damage_drop=0.; last_force=0.; n=12000; h=law.failure_m/n
            for i in range(1,n+1):
                x=i*h
                if mode=='scalar_opening':
                    new=update_damage(law,state,x,eligible=True)
                    energy=scalar_response(law,state,x)['stored_energy_j']
                    response=scalar_response(law,new,x)
                    force=response['force_n']; after=response['stored_energy_j']
                else:
                    opening=x if mode=='bundle_opening' else 0.
                    shear=x if mode=='bundle_shear' else 0.
                    new=update_damage(law,state,opening,shear,eligible=True)
                    delta=(opening,shear,0.)
                    current=[tuple(a+b for a,b in zip(v,delta)) for v in rest]
                    before=bundle_response(rest,current,[1000/3]*5,[.1]*5,state)
                    response=bundle_response(rest,current,[1000/3]*5,[.1]*5,new)
                    force=response['force_n'][0 if mode=='bundle_opening' else 1]
                    energy=before['stored_energy_j']; after=response['stored_energy_j']
                damage_drop+=energy-after; work+=.5*(force+last_force)*h
                state=new; last_force=force
            target=law.area_m2*law.fracture_energy_j_m2
            coupon['scalar_and_bundle_work'][mode]={'integrated_work_j':work,'damage_energy_drop_j':damage_drop,
                'work_relative_error_vs_scalar_target':work/target-1,'damage_relative_error_vs_scalar_target':damage_drop/target-1,
                'final_damage':state.damage,'final_force_n':last_force,
                'energy_target_met_1_percent':abs(work/target-1)<.01 and abs(damage_drop/target-1)<.01}
        corrected={}
        for name,direction in [('opening',(1.,0.,0.)),('shear',(0.,1.,0.)),('mixed',(.6,.8,0.))]:
            state=DamageState(); work=0.; loss=0.; last_force=[0.,0.,0.]; last_delta=(0.,0.,0.)
            n=12000
            for i in range(1,n+1):
                delta=tuple(.012*i/n*v for v in direction)
                current=[tuple(a+b for a,b in zip(v,delta)) for v in rest]
                new=update_bundle_damage(law,state,rest,current,[1000/3]*5,
                                         opening_m=delta[0],shear_m=math.hypot(delta[1],delta[2]),eligible=True)
                before=bundle_response(rest,current,[1000/3]*5,[0.]*5,state)
                response=bundle_response(rest,current,[1000/3]*5,[0.]*5,new)
                loss+=before['stored_energy_j']-response['stored_energy_j']
                work+=sum(.5*(a+b)*(x-y) for a,b,x,y in zip(last_force,response['force_n'],delta,last_delta))
                last_force=response['force_n']; last_delta=delta; state=new
            target=law.area_m2*law.fracture_energy_j_m2
            corrected[name]={'integrated_work_j':work,'damage_energy_drop_j':loss,
                             'work_relative_error':work/target-1,'damage_relative_error':loss/target-1,
                             'final_damage':state.damage,'final_force_n':last_force,
                             'energy_target_met_1_percent':abs(work/target-1)<.01 and abs(loss/target-1)<.01 and state.damage==1.}
        coupon['corrected_patch_work']=corrected
        coupon['law']='energy-equivalent bundle coordinate; legacy scalar-to-bundle results retained for comparison'
        # Equal unit bond stiffness probe identifies directional topology bias only.
        directional={}
        for axis in range(3):
            energy=0.
            for b in layout['bonds']:
                a,c=[layout['nodes'][i]['position_m'] for i in b['nodes']]
                direction=(c[axis]-a[axis])/b['rest_length_m']
                energy+=b['rest_length_m']**2*direction**4
            directional['xyz'[axis]]=energy/layout['analytic_volume_m3']
        anisotropy=max(directional.values())/min(directional.values())
        stream=io.StringIO()
        suite=unittest.defaultTestLoader.discover(str(ROOT/'rl/tests'),pattern='test_tomato_offline.py')
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        (args.output/'tests.txt').write_text(stream.getvalue())
        unexpected=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if unexpected:raise RuntimeError('Unexpected simulator imports: '+str(unexpected))
        summary={'scope':'offline topology and prescribed constitutive evaluation only; no time integration or simulated contact',
                 'layout':layout_checks,'coupon':coupon,'area_quadrature_l1_fraction':area_l1,
                 'equal_unit_stiffness_directional_probe':directional,'topology_anisotropy_ratio':anisotropy,
                 'tests':{'run':result.testsRun,'passed':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors)},
                 'scalar_energy_gate':coupon['scalar_and_bundle_work']['scalar_opening']['energy_target_met_1_percent'],
                 'bundle_energy_calibrated':all(v['energy_target_met_1_percent'] for v in corrected.values()),
                 'calibration_scope':'synthetic five-spring constitutive coupons only, not tomato material or actual layout bundles',
                 'physical_separation':False,'contact_eligibility_validated':False,'simulator_launched':False,'training':False,
                 'runtime_s':time.monotonic()-start,
                 'peak_rss_bytes':int(next(line.split()[1] for line in Path('/proc/self/status').read_text().splitlines() if line.startswith('VmHWM:')))*1024,
                 'memory_measurement':'Linux /proc/self/status VmHWM for this process; excludes inherited pre-exec getrusage high-water',
                 'limits':{'address_space_bytes':256*1024**2,'cpu_s':30,'wall_s':45,'shared_lock':True},
                 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                     ROOT/'rl/tomato_layout.py',ROOT/'rl/tomato_bonds.py',Path(__file__),ROOT/'rl/tests/test_tomato_offline.py']}}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        signal.alarm(0)
        print(json.dumps(summary,indent=2))
        if not result.wasSuccessful() or not layout_checks['passed'] or not summary['scalar_energy_gate'] or not summary['bundle_energy_calibrated']:
            raise SystemExit(1)


if __name__=='__main__':
    main()
