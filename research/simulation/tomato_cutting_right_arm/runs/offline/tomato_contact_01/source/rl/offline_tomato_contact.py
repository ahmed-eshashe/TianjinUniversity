"""Bounded offline contact coupons on refined geometry; no simulator imports."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'runs/offline/tomato_contact_01'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['patch','contact'],required=True)
    p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=8)
    p.add_argument('--steps',type=int,choices=[2400,4800],default=2400)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if not 0<=args.start<47 or not 1<=args.count<=8:p.error('Bounded reference batches only')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Offline contact wall cap')))
    signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        from tomato_contact_reference import wedge_patch_coupon,cut_outline,normal_contact_coupon,containing_cut_triangles
        from tomato_layout import components
        import numpy as np
        manifest=json.loads((EVIDENCE/'manifest.json').read_text());directory=ROOT/manifest['mesh']
        design_file=directory/'surface_design.json';design=json.loads(design_file.read_text())
        if not json.loads((directory/'summary.json').read_text())['preparation_pass']:raise ValueError('Unprepared mesh')
        if args.mode=='patch':
            for patch in design['interface_patches'][args.start:args.start+args.count]:
                if not all(containing_cut_triangles(design,piece,patch['anchor_yz_m']) for piece in design['pieces']):
                    raise ValueError('Patch site outside actual finite cut faces')
            records=[wedge_patch_coupon(design,patch,manifest['blade'],args.steps)
                     for patch in design['interface_patches'][args.start:args.start+args.count]]
            passed=all(r['damage']==1 and r['zero_broken_force_and_damping'] and r['stopped_state_unchanged']
                       and abs(r['work_relative_error'])<.01 and abs(r['damage_energy_relative_error'])<.01
                       and abs(r['blade_virtual_work_j']-r['work_j'])<1e-12 for r in records)
        else:
            assignments=json.loads((directory/'mass_stiffness_assignments.json').read_text())
            a,b=[cut_outline(design,piece) for piece in design['pieces']]
            mass=sum(assignments[0]['node_mass_kg']);records=[]
            for dt in manifest['contact_dt_s']:
                for damage in [0.,.5,1.]:
                    records.append(normal_contact_coupon(a,b,mass,dt,damage=damage))
                records.append(normal_contact_coupon(a,b,mass,dt,gap=0.,initial_velocity=0.,force_scale=0.))
                records.append(normal_contact_coupon(a,b,mass,dt,offset_yz=(1.,0.)))
                # Near-rim contact still overlaps the actual finite polygon, not an infinite plane.
                records.append(normal_contact_coupon(a,b,mass,dt,offset_yz=(float(np.ptp(a[:,0]))-1e-7,0.)))
            for r in records:
                r['passed']=bool((not r['finite_outlines_overlap'] or r['minimum_gap_m']>=-1e-12)
                                 and not r['crossings'] and abs(r['energy_residual_j'])<1e-10
                                 and r['momentum_pair_residual_ns']<1e-12)
            controls=[wedge_patch_coupon(design,design['interface_patches'][0],manifest['blade'],2400,mode=m)
                      for m in ['miss','off_plane','face_rub','partial']]
            cut={b['id'] for b in design['bonds'] if b['kind']=='interface'}
            groups=components(design,cut);one_left=components(design,cut-{min(cut)})
            cell_bridge=any(len({design['nodes'][i]['side'] for i in c})!=1 for assign in assignments for c in assign['integration_cells_global_ids'])
            fixture_ok=all(design['nodes'][i]['side']=='remainder' for i in design['fixture']['node_ids'])
            diagnostic={'contact_cases':records,'negative_controls':controls,
                        'complete_interface_removal_component_sizes':list(map(len,groups)),
                        'one_bond_remaining_component_count':len(one_left),
                        'volume_cells_bridge_cut':cell_bridge,'fixture_remainder_only':fixture_ok,
                        'topology_removal_prescribed_diagnostic':True,
                        'deformable_independent_release_observed':False}
            passed=all(r['passed'] for r in records) and len(groups)==2 and len(one_left)==1 and not cell_bridge and fixture_ok
            passed=passed and all(r['damage']==0 for r in controls[:3]) and 0<controls[3]['damage']<1
            records=diagnostic
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Forbidden simulator imports')
        summary={'mode':args.mode,'steps':args.steps,'records':records,'coupon_checks_passed':passed,
                 'full_deformable_cut_validated':False,'simulator_imports_or_launches':False,'training':False,
                 'design_sha256':hashlib.sha256(design_file.read_bytes()).hexdigest(),
                 'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'rl/tomato_contact_reference.py',ROOT/'rl/tomato_bonds.py']},
                 'runtime_s':time.monotonic()-start,
                 'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                 'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({k:summary[k] for k in ['mode','steps','coupon_checks_passed','runtime_s','peak_rss_bytes']}))
        if not passed:sys.exit(1)


if __name__=='__main__':main()
