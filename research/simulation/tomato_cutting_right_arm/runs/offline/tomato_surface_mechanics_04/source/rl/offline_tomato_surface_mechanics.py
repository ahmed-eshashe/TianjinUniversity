"""Bounded offline mass/stiffness and static compression/shear checks."""
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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    def timeout(signum,frame):raise TimeoutError('Offline mechanics 55 s wall ceiling reached')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        from tomato_surface_mechanics import analyse_piece,closed_volume_moments
        source=ROOT/'runs/offline/tomato_surfaces_03/surface_design.json';design=json.loads(source.read_text())
        results=[];assignments=[]
        closed_volumes=[closed_volume_moments(design,p)[0] for p in design['pieces']]
        total_mass=sum(n['mass_kg'] for n in design['nodes'])
        uniform_density=total_mass/sum(closed_volumes)
        for piece in design['pieces']:
            volume=closed_volumes[len(results)]
            record,assignment=analyse_piece(design,piece,density_mass=uniform_density*volume)
            results.append(record);assignments.append(assignment)
            (args.output/'partial_results.json').write_text(json.dumps(results,indent=2)+'\n')
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Unexpected simulator modules: '+str(forbidden))
        from offline_tomato_patch_sweep import patch_data
        interface=[]
        for patch in design['interface_patches']:
            _,stiffness,law=patch_data(design,patch)
            interface.append({'patch_id':patch['id'],'bond_ids':patch['bond_ids'],
                              'bond_stiffness_n_m':stiffness,'source':'unchanged previous patch_data rule',
                              'area_m2':law.area_m2})
        assigned=[i for a in assignments for i in a['bond_ids']]+[i for a in interface for i in a['bond_ids']]
        if sorted(assigned)!=list(range(len(design['bonds']))):raise ValueError('Bond assignment incomplete or duplicated')
        summary={'scope':'synthetic volume-lumped central spring static checks; no simulator or dynamics',
                 'synthetic_young_pa':30000.,'synthetic_poisson_ratio':.25,
                 'material_calibrated':False,'surface_skin_calibrated':False,
                 'interface_law_and_stiffness_unchanged':True,'pieces':results,'passed':all(p['passed'] for p in results),
                 'uniform_synthetic_density_kg_m3':uniform_density,'total_mass_preserved_relative_error':sum(p['mass_kg'] for p in results)/total_mass-1,
                 'per_piece_mass_recomputed_from_closed_volume':True,'all_bonds_assigned_once':True,
                 'surface_design_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'runtime_s':time.monotonic()-start,
                 'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                 'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},
                 'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'rl/tomato_surface_mechanics.py']},
                 'simulator_imports_or_launches':False,'training':False}
        (args.output/'mass_stiffness_assignments.json').write_text(json.dumps(assignments,indent=2)+'\n')
        (args.output/'unchanged_interface_assignments.json').write_text(json.dumps(interface,indent=2)+'\n')
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');signal.alarm(0)
        print(json.dumps(summary,indent=2))
        if not summary['passed']:raise SystemExit(1)


if __name__=='__main__':main()
