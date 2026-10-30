"""Bounded serial constitutive sweeps of actual tomato patch bond geometries.

Standard library only. Prescribed displacements, no time integration or contacts.
"""
import argparse
import fcntl
import hashlib
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MODES={'opening':(1.,0.,0.),'shear_y_positive':(0.,1.,0.),'shear_y_negative':(0.,-1.,0.),
       'shear_z_positive':(0.,0.,1.),'shear_z_negative':(0.,0.,-1.)}


def patch_data(layout, patch):
    """Construct actual vectors, oriented slice -> remainder, without five-bond idealization."""
    from tomato_bonds import CohesiveLaw
    nodes=layout['nodes']; bonds=layout['bonds']; rest=[]
    for bid in patch['bond_ids']:
        b=bonds[bid]; a,c=[nodes[i] for i in b['nodes']]
        if a['side']=='remainder':a,c=c,a
        if a['side']!='slice' or c['side']!='remainder' or b['kind']!='interface':
            raise ValueError('Unregistered or incorrectly classified interface bond')
        rest.append(tuple(y-x for x,y in zip(a['position_m'],c['position_m'])))
    law=CohesiveLaw(4e7*patch['area_m2'],patch['area_m2'],40000.,80.,.2*patch['area_m2']/25e-6)
    # One shared area budget. Normalize the normal tangent, not per-mode fracture energy.
    normal_weight=sum(v[0]**2/sum(x*x for x in v) for v in rest)
    if normal_weight<=0:raise ValueError('No normal interface stiffness')
    stiffness=[law.stiffness_n_m/normal_weight]*len(rest)
    return rest,stiffness,law


def evaluate_patch(layout, patch, mode, steps=2400):
    from tomato_bonds import DamageState,bundle_response,update_bundle_damage
    direction=MODES[mode];rest,stiffness,law=patch_data(layout,patch)
    state=DamageState();work=0.;loss=0.;previous_force=[0.,0.,0.];previous_delta=(0.,0.,0.)
    max_damage_jump=0.;failure_displacement=None
    for i in range(1,steps+1):
        delta=tuple(.012*i/steps*x for x in direction)
        current=[tuple(a+b for a,b in zip(v,delta)) for v in rest]
        new=update_bundle_damage(law,state,rest,current,stiffness,
                                 opening_m=delta[0],shear_m=math.hypot(delta[1],delta[2]),eligible=True)
        # Independent undegraded response for force-work and fixed-geometry energy loss.
        undamaged=bundle_response(rest,current,stiffness,[0.]*len(rest),DamageState())
        force=[(1-new.damage)*f for f in undamaged['force_n']]
        work+=sum(.5*(a+b)*(x-y) for a,b,x,y in zip(previous_force,force,delta,previous_delta))
        loss+=(new.damage-state.damage)*undamaged['stored_energy_j']
        max_damage_jump=max(max_damage_jump,new.damage-state.damage)
        if new.damage==1. and failure_displacement is None:
            failure_displacement=.012*i/steps
        previous_force=force;previous_delta=delta;state=new
        if new.damage==1.:
            break
    # Test complete failure with actual damping and nonzero velocity, not just scaled elastic work.
    final=bundle_response(rest,current,stiffness,[.2]*len(rest),state,velocities=[(1.,2.,3.)]*len(rest))
    target=law.fracture_energy_j_m2*patch['area_m2']; werr=work/target-1;derr=loss/target-1
    zero_residual=state.damage==1. and all(f==0. for f in final['force_n']) and final['stored_energy_j']==0.
    return {'mode':mode,'steps_requested':steps,'steps_evaluated':i,'target_energy_j':target,
            'integrated_work_j':work,'damage_energy_drop_j':loss,'work_relative_error':werr,
            'damage_relative_error':derr,'max_damage_jump':max_damage_jump,
            'failure_displacement_m':failure_displacement,'final_damage':state.damage,
            'zero_post_failure_force_and_damping':zero_residual,
            'passed_unchanged_1_percent_gate':abs(werr)<.01 and abs(derr)<.01 and zero_residual}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--start',type=int,required=True)
    p.add_argument('--count',type=int,default=8)
    p.add_argument('--steps',type=int,default=2400)
    args=p.parse_args()
    if not 0<=args.start<47 or not 1<=args.count<=8 or args.steps not in (2400,4800):p.error('Bounded to 8 patches and 2400/4800 steps')
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    def timeout(signum,frame):raise TimeoutError('Offline wall limit reached')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(45)
    started=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        args.output.mkdir(parents=True,exist_ok=False)
        source=ROOT/'runs/offline/tomato_layout_02/layout.json'
        layout=json.loads(source.read_text())
        from tomato_layout import audit_layout
        if len(layout['interface_patches'])!=47 or not audit_layout(layout)['passed']:raise ValueError('Invalid original layout')
        results=[]
        for patch in layout['interface_patches'][args.start:args.start+args.count]:
            rest,stiffness,law=patch_data(layout,patch)
            result={'patch_id':patch['id'],'material_label':patch['material'],'bond_ids':patch['bond_ids'],
                    'area_m2':patch['area_m2'],'actual_rest_vectors_m':rest,
                    'synthetic_bond_stiffness_n_m':stiffness,
                    'synthetic_reference_stiffness_n_m':law.stiffness_n_m,
                    'cases':[evaluate_patch(layout,patch,mode,args.steps) for mode in MODES]}
            results.append(result)
            (args.output/'partial_results.json').write_text(json.dumps(results,indent=2)+'\n')
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Unexpected simulator modules')
        summary={'scope':'actual patch vectors, isolated prescribed translations; no dynamics/contact',
                 'start':args.start,'count':len(results),'steps':args.steps,'patches':results,
                 'all_cases_pass':all(c['passed_unchanged_1_percent_gate'] for r in results for c in r['cases']),
                 'synthetic_material_only':True,'same_skin_flesh_test_material':True,
                 'physical_separation':False,'simulator_imports_or_launches':False,'training':False,
                 'layout_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [
                     Path(__file__),ROOT/'rl/tomato_bonds.py',ROOT/'rl/tomato_layout.py']},
                 'runtime_s':time.monotonic()-started,
                 'peak_rss_bytes':int(next(line.split()[1] for line in Path('/proc/self/status').read_text().splitlines() if line.startswith('VmHWM:')))*1024,
                 'limits':{'address_space_bytes':256*1024**2,'cpu_s':30,'wall_s':45,'shared_lock':True}}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        signal.alarm(0)
        print(json.dumps({k:v for k,v in summary.items() if k!='patches'},indent=2))
        if not summary['all_cases_pass']:raise SystemExit(1)


if __name__=='__main__':main()
