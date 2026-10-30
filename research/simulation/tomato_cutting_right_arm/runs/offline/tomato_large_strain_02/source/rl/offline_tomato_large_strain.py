"""One bounded quasi-static compression/shear path using saved inactive spring coefficients."""
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
MODES={'compression_x':(0,0),'compression_y':(1,1),'compression_z':(2,2),
       'shear_xy_positive':(0,1),'shear_xy_negative':(0,1),
       'shear_xz_positive':(0,2),'shear_xz_negative':(0,2),
       'shear_yz_positive':(1,2),'shear_yz_negative':(1,2)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--side',choices=['slice','remainder'],required=True)
    parser.add_argument('--mode',choices=MODES,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    def timeout(signum,frame):raise TimeoutError('Offline large-strain wall limit exceeded')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(55);started=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.optimize import minimize
        from scipy.sparse.linalg import eigsh,ArpackNoConvergence
        from tomato_nonlinear_checks import spring_state,cell_ratios,polish_equilibrium
        design_file=ROOT/'runs/offline/tomato_surfaces_03/surface_design.json'
        assignment_file=ROOT/'runs/offline/tomato_surface_mechanics_04/mass_stiffness_assignments.json'
        design=json.loads(design_file.read_text());assignments=json.loads(assignment_file.read_text())
        piece=next(p for p in design['pieces'] if p['side']==args.side)
        assign=next(a for a in assignments if design['nodes'][a['global_node_ids'][0]]['side']==args.side)
        ids=assign['global_node_ids'];mapping={i:j for j,i in enumerate(ids)}
        points=np.array([design['nodes'][i]['position_m'] for i in ids])
        pairs=np.array([[mapping[i] for i in design['bonds'][b]['nodes']] for b in assign['bond_ids']])
        k=np.asarray(assign['bond_stiffness_n_m']);rest=np.linalg.norm(points[pairs[:,1]]-points[pairs[:,0]],axis=1)
        cells=np.array([[mapping[i] for i in c] for c in assign['integration_cells_global_ids']])
        p=points[cells];reference_volumes=np.linalg.det(p[:,1:]-p[:,:1])/6
        if np.any(reference_volumes<=0):raise ValueError('Invalid reference quadrature cells')
        masses=np.asarray(assign['node_mass_kg']);centre=masses@points/masses.sum()
        fixed=np.sort((3*np.array([mapping[i] for i in piece['surface_node_ids']])[:,None]+np.arange(3)).reshape(-1))
        free=np.setdiff1d(np.arange(points.size),fixed)
        reference=spring_state(points,pairs,rest,k,tangent=True)
        energy_scale=30000.*sum(assign['node_volume_m3'])
        scale=np.sqrt(energy_scale/reference['tangent_n_m'].diagonal()[free])
        stages=[];previous=np.zeros(points.size);failure=None
        levels=[.01,.02,.05,.10,.20,.30] if args.mode.startswith('compression') else [.02,.05,.10,.20,.30,.50]
        a,b=MODES[args.mode];sign=-1. if a==b or args.mode.endswith('negative') else 1.
        for amount in levels:
            displacement=previous.reshape(-1,3).copy()
            prescribed=np.zeros_like(points);prescribed[:,a]=sign*amount*(points[:,b]-centre[b])
            flat=displacement.reshape(-1);flat[fixed]=prescribed.reshape(-1)[fixed]
            def objective(y):
                flat[free]=y*scale
                state=spring_state(points+flat.reshape(-1,3),pairs,rest,k)
                return state['energy_j']/energy_scale,state['gradient_n'].reshape(-1)[free]*scale/energy_scale
            result=minimize(objective,previous[free]/scale,jac=True,method='L-BFGS-B',
                            options={'maxiter':800,'maxfun':1600,'ftol':1e-16,'gtol':1e-11,'maxls':30,'maxcor':12})
            flat[free]=result.x*scale
            flat,polish_steps=polish_equilibrium(points,flat,pairs,rest,k,free,fixed)
            current=points+flat.reshape(-1,3)
            state=spring_state(current,pairs,rest,k,tangent=True);g=state['gradient_n'].reshape(-1)
            residual=float(np.linalg.norm(g[free])/max(np.linalg.norm(g[fixed]),1e-15))
            ratios=cell_ratios(current,cells,reference_volumes)
            tangent=state['tangent_n_m'][free][:,free]
            invsqrt=1/np.sqrt(reference['tangent_n_m'].diagonal()[free])
            from scipy.sparse import diags
            scaled=diags(invsqrt)@tangent@diags(invsqrt)
            try:
                least=float(eigsh(scaled,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=800)[0]);eigen_status='converged'
            except ArpackNoConvergence:
                least=None;eigen_status='inconclusive'
            flags=[]
            if residual>1e-6:flags.append('nonlinear_equilibrium_not_converged')
            if np.any(ratios<=0):flags.append('diagnostic_cell_inversion')
            elif np.min(ratios)<.1:flags.append('local_near_collapse')
            if state['min_length_ratio']<.1:flags.append('near_singular_spring')
            if least is None:flags.append('tangent_stability_inconclusive')
            elif least< -1e-6:flags.append('negative_free_tangent_stiffness')
            elif least<1e-6:flags.append('near_zero_free_tangent_mode')
            record={'strain':amount,'optimizer_success':bool(result.success),'optimizer_message':str(result.message),
                    'iterations':int(result.nit),'newton_polish_steps':polish_steps,'force_residual_fraction':residual,
                    'energy_j':state['energy_j'],'min_cell_volume_ratio':float(ratios.min()),
                    'inverted_cell_count':int(np.sum(ratios<=0)),'volume_ratio':float(np.dot(ratios,reference_volumes)/reference_volumes.sum()),
                    'min_spring_length_ratio':state['min_length_ratio'],
                    'least_preconditioned_tangent_eigenvalue':least,'eigen_status':eigen_status,
                    'flags':flags,'passed_static_screen':not flags}
            stages.append(record)
            (args.output/'stages.json').write_text(json.dumps(stages,indent=2)+'\n')
            np.save(args.output/'last_displacement_m.npy',flat.reshape(-1,3))
            previous=flat.copy()
            if flags:
                failure=record;break
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Forbidden simulator import')
        summary={'side':args.side,'mode':args.mode,'scope':'exact finite-length bulk spring static continuation; fully prescribed outer surface; no contact or dynamics',
                 'requested_levels':levels,'stages':stages,'all_requested_levels_passed':failure is None and len(stages)==len(levels),
                 'first_flagged_strain':None if failure is None else failure['strain'],
                 'interface_springs_included':False,'damage_evolution_enabled':False,
                 'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'rl/tomato_nonlinear_checks.py',design_file,assignment_file]},
                 'runtime_s':time.monotonic()-started,
                 'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                 'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},
                 'simulator_imports_or_launches':False,'training':False}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');signal.alarm(0)
        print(json.dumps({key:summary[key] for key in ['side','mode','first_flagged_strain','all_requested_levels_passed','runtime_s','peak_rss_bytes']}))


if __name__=='__main__':main()
