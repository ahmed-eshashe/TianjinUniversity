"""Prepare one bounded inactive mesh and volume-lumped spring proposal for comparison."""
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
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spacing-mm',type=float,choices=[4,4.5,5,6],required=True)
    p.add_argument('--angular',type=int,choices=[32,64,128],default=64)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    def timeout(signum,frame):raise TimeoutError('Offline mesh preparation wall limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        from tomato_layout import build_layout,audit_layout
        from tomato_surfaces import build_surfaces
        from tomato_surface_conformity import conform_to_bulk
        from offline_tomato_surfaces import inspect_design
        from tomato_surface_mechanics import analyse_piece,closed_volume_moments
        layout=build_layout(spacing_m=args.spacing_mm/1000)
        design=build_surfaces(layout,angular_segments=args.angular)
        design=conform_to_bulk(design,layout)
        geometry=inspect_design(layout,design)
        total_mass=sum(n['mass_kg'] for n in design['nodes'])
        volumes=[closed_volume_moments(design,p)[0] for p in design['pieces']]
        density=total_mass/sum(volumes);assignments=[];mechanics=[]
        for piece,volume in zip(design['pieces'],volumes):
            record,assignment=analyse_piece(design,piece,density_mass=density*volume)
            assignments.append(assignment);mechanics.append(record)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Unexpected simulator modules')
        summary={'spacing_mm':args.spacing_mm,'angular_segments':args.angular,
                 'bulk_nodes':len(layout['nodes']),'total_nodes':len(design['nodes']),'total_bonds':len(design['bonds']),
                 'triangles':sum(len(p['triangles']) for p in design['pieces']),
                 'geometry':geometry,'small_strain_checks':mechanics,
                 'preparation_pass':geometry['passed'] and audit_layout(layout)['passed'] and all(p['passed'] for p in mechanics),
                 'same_synthetic_young_pa':30000.,'same_poisson':.25,'total_mass_kg':total_mass,
                 'runtime_s':time.monotonic()-start,
                 'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                 'simulator_imports_or_launches':False,'training':False,
                 'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}}
        (args.output/'surface_design.json').write_text(json.dumps(design,indent=2)+'\n')
        (args.output/'mass_stiffness_assignments.json').write_text(json.dumps(assignments,indent=2)+'\n')
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');signal.alarm(0)
        print(json.dumps({k:summary[k] for k in ['spacing_mm','angular_segments','bulk_nodes','total_nodes','total_bonds','preparation_pass','runtime_s','peak_rss_bytes']}))


if __name__=='__main__':main()
