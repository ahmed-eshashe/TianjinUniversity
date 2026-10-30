"""One memory-capped full-node attempted complete wedge insertion endpoint."""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'runs/offline/tomato_blade_damage_01/insertion_refined/08'


def main():
    p=argparse.ArgumentParser();p.add_argument('--depth-mm',type=float,required=True)
    p.add_argument('--mode',choices=['contact','face_rub','miss'],default='contact')
    p.add_argument('--guess',type=Path,help='Uncommitted positions-only optimization guess, never damage/history');p.add_argument('--previous',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not 4<=args.depth_mm<=48:p.error('Full-cut diagnostic continuation must stay between 4 and 48 mm')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_bonds import DamageState
        from tomato_coupled_contact import assemble_model,cut_pairs,supports,solve_contact,reduced_tangent,swept_minimum_volume,proper_surface_intersections
        from tomato_blade_damage import EvolvingCohesion,wedge_geometry,edge_history,contact_eligibility,BLADE
        source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assignments=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assignments,0.);pairs=cut_pairs(design)
        model.cohesion=EvolvingCohesion(design,pairs)
        fixed,_=supports(design,points,'indentation',0.)
        top=float(points[pairs[:,0],2].max());tip=top-args.depth_mm/1000
        sources=[Path(__file__),*[ROOT/'rl'/s for s in ['tomato_blade_damage.py','tomato_coupled_contact.py','tomato_surface_cohesion.py','tomato_bonds.py','tomato_contact_reference.py','offline_tomato_patch_sweep.py','tomato_volume_protection.py','tomato_nonlinear_checks.py']],source/'surface_design.json',source/'mass_stiffness_assignments.json']
        hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
        previous=None;initial=points.copy();old_tip=top;hits=np.zeros(len(pairs),dtype=bool);committed=list(model.cohesion.states)
        if args.previous:
            previous=json.loads((args.previous/'summary.json').read_text())
            if not previous['passed'] or previous['mode']!=args.mode or previous['source_hashes']!=hashes and args.previous.resolve()!=SEED.resolve():raise ValueError('Invalid/changed continuation')
            for name,digest in previous['state_hashes'].items():
                if hashlib.sha256((args.previous/name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed committed state')
            initial=np.load(args.previous/'positions.npy');hits=np.load(args.previous/'edge_hits.npy');old_tip=previous['tip_z_m']
            committed=[DamageState(**s) for s in previous['damage_states']]
        else:raise ValueError('Full-cut attempt requires the verified 4 mm checkpoint or accepted continuation')
        if args.depth_mm < previous['depth_mm'] or args.depth_mm-previous['depth_mm']>.12500001:raise ValueError('Insertion only, increment <=0.125 mm')
        for file,digest in previous['source_hashes'].items():
            if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=digest:raise ValueError('Changed previous source')
        hits=edge_history(points,pairs,old_tip,tip,hits,mode=args.mode)
        A,b,labels,physical,widths=wedge_geometry(design,points,pairs,tip,mode=args.mode)
        model.cohesion.states=list(committed);x=initial.copy()
        if args.guess:
            seed=np.load(args.guess)
            if seed.shape!=points.shape or not np.isfinite(seed).all():raise ValueError('Invalid numerical guess')
            x=seed.copy()  # Only optimization starts here; path/work still start at initial.
        print({'stage':'solve_start','depth_mm':args.depth_mm},flush=True)
        outer=[];flags=[];eligible=np.zeros(47,dtype=bool)
        for iteration in range(24):
            x,lam,state,trace,ok,active,fixed_ids,free=solve_contact(model,points,x,fixed,A,b,labels)
            if not ok:flags.append('contact_equilibrium_failed');break
            print({'stage':'contact_solved','iteration':iteration,'contact_iterations':len(trace),'elapsed_s':time.monotonic()-start},flush=True)
            eligible=contact_eligibility(model.cohesion,hits,lam,widths)
            trial=model.cohesion.trial_states(x,committed,eligible)
            difference=max(abs(a.damage-b.damage) for a,b in zip(trial,model.cohesion.states))
            outer.append({'iteration':iteration,'max_damage_change':difference,'energy_j':state['energy_j'],'contact_iterations':len(trace)})
            if difference<=1e-9:
                model.cohesion.states=trial
                break
            model.cohesion.states=trial
        else:flags.append('staggered_damage_not_converged')
        # Commit only final equilibrium states; no Newton/Picard history is accumulated.
        states=model.cohesion.states
        gap=A@x.ravel()-b;g=state['gradient_n'].ravel();residual=g-A.T@lam
        scale=max(np.linalg.norm(g[fixed_ids]),np.linalg.norm(A.T@lam),1e-4)
        relative=float(np.linalg.norm(residual[free])/scale)
        if relative>1e-6:flags.append('force_residual')
        if gap.min()<-1e-9 or lam.min()<-1e-9:flags.append('contact_complementarity')
        if any(a.damage<b.damage for a,b in zip(states,committed)):flags.append('damage_healing')
        if any(a.kappa_m<b.kappa_m for a,b in zip(states,committed)):flags.append('history_decreased')
        total_diss=model.cohesion.dissipation(states);old_diss=model.cohesion.dissipation(committed)
        work=0.;increment_error=0.;cumulative=0.;balance=0.
        if previous:
            old_lam=np.load(args.previous/'multipliers.npy')
            _,_,_,old_physical,_=wedge_geometry(design,points,pairs,old_tip,mode=args.mode)
            work=float(.5*(lam+old_lam)@(physical-old_physical))
            increment_error=work-(state['energy_j']-previous['energy_j'])-(total_diss-old_diss)
            cumulative=previous['cumulative_blade_work_j']+work
        else:cumulative=0.
        balance=cumulative-state['energy_j']-total_diss
        normalizer=max(abs(cumulative),abs(state['energy_j'])+total_diss,1e-12)
        # 1% total-energy gate + 1e-12 J; no numerical relaxation is hidden as fracture.
        if abs(balance)>.01*normalizer+1e-12:flags.append('fracture_work_balance')
        if previous and abs(increment_error)>.01*max(abs(work),abs(state['energy_j']),abs(previous['energy_j']),total_diss-old_diss,1e-12)+1e-12:flags.append('incremental_fracture_work_balance')
        J=swept_minimum_volume(model,initial,x)
        if J<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        cutgap=x[pairs[:,1],0]-x[pairs[:,0],0]
        if cutgap.min()<-1e-9:flags.append('cut_surface_crossing')
        screens=[proper_surface_intersections(design,initial+t*(x-initial))[0] for t in [.5,1.]]
        if any(screens):flags.append('proper_surface_intersection')
        # Before thickness cap, wedge width is a positive-part affine function:
        # endpoint-feasible linear nodal paths bound its convex interpolant.
        # Exact per-vertex affine-path facet certificate. Width is piecewise
        # affine in depth; include every bevel cap, entry and exit breakpoint.
        # Testing all knots certifies the entire segment without oversampling.
        if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('unsupported_cut_projection')
        fractions={0.,1.}
        if tip!=old_tip:
            for z in points[pairs[:,0],2]:
                for knot in (z,z-BLADE['single_bevel_length_m'],z-BLADE['height_m']):
                    t=(knot-old_tip)/(tip-old_tip)
                    if 0<t<1:fractions.add(float(t))
        path_blade_gap=1.
        for t in sorted(fractions):
            xp=initial+t*(x-initial)
            _,_,_,_,ww=wedge_geometry(design,points,pairs,old_tip+t*(tip-old_tip),mode=args.mode)
            covered=ww>0
            if np.any(covered):
                path_blade_gap=min(path_blade_gap,float(np.min(design['cut_x_m']-ww[covered]/2-xp[pairs[covered,0],0])),float(np.min(xp[pairs[covered,1],0]-design['cut_x_m']-ww[covered]/2)))
        if path_blade_gap < -1e-9:flags.append('swept_blade_crossing')
        if float(np.min(initial[pairs[:,1],0]-initial[pairs[:,0],0])) < -1e-9:flags.append('initial_cut_crossing')
        external=np.asarray(A.T@lam).reshape(-1,3);external.ravel()[fixed_ids]+=residual[fixed_ids]
        fscale=max(float(np.linalg.norm(external,axis=1).sum()),1e-4)
        fbalance=float(np.linalg.norm(external.sum(axis=0))/fscale)
        mbalance=float(np.linalg.norm(np.cross(x,external).sum(axis=0))/(fscale*.065))
        if max(fbalance,mbalance)>.01:flags.append('force_moment_balance')
        # Consistent softening tangent, not merely a frozen-D Hessian.
        strong=[labels[i] for i in np.flatnonzero(lam>1e-9)]
        algorithmic=model.cohesion.algorithmic_tangent(x,state['tangent_n_m'],committed,eligible)
        h=reduced_tangent(algorithmic,strong,fixed,points.size)
        ref=reduced_tangent(model.evaluate(points,tangent=True)['tangent_n_m'],strong,fixed,points.size)
        pre=diags(1/np.sqrt(ref.diagonal()))
        from scipy.sparse.linalg import ArpackNoConvergence
        try:
            least=float(eigsh(pre@h@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=1600,ncv=40)[0])
            if least<1e-6:flags.append('softening_tangent_not_positive')
        except ArpackNoConvergence:
            least=None;flags.append('softening_stability_inconclusive')
        np.save(args.output/'positions.npy',x);np.save(args.output/'multipliers.npy',lam);np.save(args.output/'edge_hits.npy',hits)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        summary={'passed':not flags,'flags':flags,'mode':args.mode,'depth_mm':args.depth_mm,'tip_z_m':tip,
            'damage_states':[s.__dict__ for s in states],'eligible_patches':np.flatnonzero(eligible).tolist(),
            'damaged_patches':sum(s.damage>0 for s in states),'max_damage':max(s.damage for s in states),
            'energy_j':state['energy_j'],'fracture_dissipation_j':total_diss,'cumulative_blade_work_j':cumulative,
            'increment_blade_work_j':work,'increment_energy_residual_j':increment_error,'energy_residual_j':balance,'relative_energy_residual':abs(balance)/normalizer,
            'force_residual':relative,'min_contact_gap_m':float(gap.min()),'min_cut_gap_m':float(cutgap.min()),'min_multiplier_n':float(lam.min()),
            'swept_min_J':J,'surface_intersections':screens,'minimum_softening_tangent_eigenvalue':least,
            'force_balance_fraction':fbalance,'moment_balance_fraction':mbalance,'outer_iterations':outer,
            'optimization_guess_sha256':hashlib.sha256(args.guess.read_bytes()).hexdigest() if args.guess else None,
            'source_hashes':hashes,'state_hashes':{n:hashlib.sha256((args.output/n).read_bytes()).hexdigest() for n in ['positions.npy','multipliers.npy','edge_hits.npy']},
            'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
            'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},
            'forbidden_imports':forbidden,'full_cut_attempt':True,'full_cut_validated':False,'completely_failed_patches':sum(s.damage==1 for s in states),'swept_blade_min_gap_m':path_blade_gap,'simulator':False,'training':False}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:summary[k] for k in ['passed','flags','depth_mm','damaged_patches','max_damage','relative_energy_residual','runtime_s']})


if __name__=='__main__':main()
