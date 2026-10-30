"""One capped offline withdrawal or supported reclosure endpoint; no full cut."""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'runs/offline/tomato_blade_damage_01/insertion_refined/08'


def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['withdrawal','reclosure'],required=True)
    p.add_argument('--depth-mm',type=float,default=0.);p.add_argument('--drive-mm',type=float,default=0.)
    p.add_argument('--previous',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output=args.output.resolve()
    if args.previous:args.previous=args.previous.resolve()
    if not 0<=args.depth_mm<=4 or abs(args.drive_mm)>.05:p.error('Only withdrawal <=4mm and reclosure drives <=0.05mm')
    if args.phase=='withdrawal' and args.drive_mm!=0:p.error('No slice clamp during withdrawal')
    if args.phase=='reclosure' and args.depth_mm!=0:p.error('Reclosure only with blade withdrawn')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh,ArpackNoConvergence
        from tomato_bonds import DamageState
        from tomato_coupled_contact import assemble_model,cut_pairs,supports,solve_contact,reduced_tangent,swept_minimum_volume,proper_surface_intersections
        from tomato_blade_damage import EvolvingCohesion,wedge_geometry,edge_history,contact_eligibility,BLADE
        from tomato_unloading import ledger,damage_changes,withdrawal_guess
        source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assignments=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assignments,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        sources=[Path(__file__),*[ROOT/'rl'/n for n in ['tomato_unloading.py','tomato_blade_damage.py','tomato_coupled_contact.py','tomato_surface_cohesion.py','tomato_bonds.py','tomato_contact_reference.py','offline_tomato_patch_sweep.py','tomato_volume_protection.py','tomato_nonlinear_checks.py']],source/'surface_design.json',source/'mass_stiffness_assignments.json']
        hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
        seed=json.loads((SEED/'summary.json').read_text());seed_hash=hashlib.sha256((SEED/'summary.json').read_bytes()).hexdigest()
        assert seed['passed'] and seed['depth_mm']==4 and seed['damaged_patches']==2
        for file,digest in seed['source_hashes'].items():
            if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=digest:raise ValueError('Changed seed source')
        for file,digest in seed['state_hashes'].items():
            if hashlib.sha256((SEED/file).read_bytes()).hexdigest()!=digest:raise ValueError('Changed seed state')
        previous=None;old=seed;directory=SEED
        if args.previous:
            previous=json.loads((args.previous/'summary.json').read_text())
            if not previous['passed'] or previous['source_hashes']!=hashes or previous['seed_summary_sha256']!=seed_hash:raise ValueError('Changed/invalid continuation')
            for file,digest in previous['state_hashes'].items():
                if hashlib.sha256((args.previous/file).read_bytes()).hexdigest()!=digest:raise ValueError('Changed continuation state')
            old=previous;directory=args.previous
        elif args.phase!='withdrawal' or args.depth_mm!=4:raise ValueError('Start by holding the accepted 4mm seed')
        if args.phase=='withdrawal' and previous and (previous['phase']!='withdrawal' or args.depth_mm>previous['depth_mm']+1e-12):raise ValueError('No reinsertion in unloading test')
        if args.phase=='reclosure' and old['depth_mm']!=0:raise ValueError('Withdraw blade completely before supported reclosure')
        if previous and previous['phase']=='reclosure' and abs(args.drive_mm-previous['drive_mm'])>.02500001:raise ValueError('Support drive increment >0.025mm')
        initial=np.load(directory/'positions.npy');old_lam=np.load(directory/'multipliers.npy');old_hits=np.load(directory/'edge_hits.npy')
        committed=[DamageState(**s) for s in old['damage_states']];seed_states=[DamageState(**s) for s in seed['damage_states']]
        model.cohesion.states=list(committed);initial_eval=model.evaluate(initial)
        if abs(initial_eval['energy_j']-old['energy_j'])>1e-10:raise ValueError('Unverified initial elastic energy')
        top=float(points[pairs[:,0],2].max());tip=top-args.depth_mm/1000;old_tip=old['tip_z_m']
        fixed,back=supports(design,points,'reclosure' if args.phase=='reclosure' else 'indentation',args.drive_mm/1000)
        if args.phase=='reclosure' and (not previous or previous['phase']!='reclosure'):
            if args.drive_mm!=0 or np.max(np.abs(initial[back,0]-points[back,0]))>1e-9:raise ValueError('Back-cap support must engage without displacement')
        hits=edge_history(points,pairs,old_tip,tip,old_hits)
        A,b,labels,physical,widths=wedge_geometry(design,points,pairs,tip)
        x=withdrawal_guess(initial,pairs,old_lam,widths,design['cut_x_m']) if args.phase=='withdrawal' else initial.copy()
        flags=[];outer=[];eligible=np.zeros(47,dtype=bool)
        for iteration in range(24):
            print({'stage':'equilibrium_start','iteration':iteration,'elapsed_s':time.monotonic()-start},flush=True)
            x,lam,state,trace,ok,active,fixed_ids,free=solve_contact(model,points,x,fixed,A,b,labels)
            print({'stage':'equilibrium_end','iterations':len(trace),'elapsed_s':time.monotonic()-start},flush=True)
            if not ok:flags.append('contact_equilibrium_failed');break
            eligible=contact_eligibility(model.cohesion,hits,lam,widths)
            trial=model.cohesion.trial_states(x,committed,eligible)
            difference=max(abs(a.damage-b.damage) for a,b in zip(trial,model.cohesion.states))
            outer.append({'iteration':iteration,'max_damage_change':difference,'contact_iterations':len(trace)})
            if difference<=1e-9:model.cohesion.states=trial;break
            model.cohesion.states=trial
        else:flags.append('damage_not_converged')
        states=model.cohesion.states;changes=damage_changes(committed,states);seed_changes=damage_changes(seed_states,states)
        if changes['healed_patches'] or changes['decreased_histories']:flags.append('healing')
        if all(s.damage==1 for s in states):flags.append('full_failure_forbidden')
        g=state['gradient_n'].ravel();residual=g-A.T@lam;scale=max(np.linalg.norm(g[fixed_ids]),np.linalg.norm(A.T@lam),1e-4)
        force_residual=float(np.linalg.norm(residual[free])/scale)
        if force_residual>1e-6:flags.append('force_residual')
        gaps=A@x.ravel()-b;cutgaps=x[pairs[:,1],0]-x[pairs[:,0],0]
        if gaps.min()<-1e-9 or cutgaps.min()<-1e-9 or lam.min()<-1e-9:flags.append('contact_violation')
        if np.max(np.abs(x.ravel()[fixed_ids]-np.array([fixed[i] for i in fixed_ids])))>1e-12:flags.append('support_moved')
        support=np.zeros(x.size);support[fixed_ids]=residual[fixed_ids]
        if previous:old_support=np.load(directory/'support_reactions.npy')
        else:
            oldA,_,_,_,_=wedge_geometry(design,points,pairs,old_tip)
            oldfixed,_=supports(design,points,'indentation',0.);old_ids=np.array(sorted(oldfixed));old_support=np.zeros(x.size)
            old_support[old_ids]=(initial_eval['gradient_n'].ravel()-oldA.T@old_lam)[old_ids]
        _,_,_,old_physical,_=wedge_geometry(design,points,pairs,old_tip)
        blade_work=float(.5*(old_lam+lam)@(physical-old_physical))
        support_work=float(.5*(old_support+support)@(x-initial).ravel())
        incremental_work=blade_work+support_work;diss=model.cohesion.dissipation(states)
        if previous:
            cycle_work=previous['cycle_ledger']['work_j']+incremental_work
            cycle_peak=previous['cycle_ledger']['peak_energy_j']
        else:cycle_work=incremental_work;cycle_peak=seed['energy_j']
        cycle=ledger(state['energy_j'],diss,cycle_work,initial_energy=seed['energy_j'],initial_dissipation=seed['fracture_dissipation_j'],peak_energy=cycle_peak)
        if previous and previous['phase']==args.phase:
            anchor=previous['phase_ledger'];phase_work=anchor['work_j']+incremental_work
            phase=ledger(state['energy_j'],diss,phase_work,initial_energy=anchor['initial_energy_j'],initial_dissipation=anchor['initial_dissipation_j'],peak_energy=anchor['peak_energy_j'])
        else:phase=ledger(state['energy_j'],diss,incremental_work,initial_energy=old['energy_j'],initial_dissipation=old['fracture_dissipation_j'])
        if not cycle['passed'] or not phase['passed']:flags.append('energy_balance')
        dE=state['energy_j']-old['energy_j'];dR=diss-old['fracture_dissipation_j'];increment_error=incremental_work-dE-dR
        if abs(increment_error)>.01*max(abs(incremental_work),abs(state['energy_j']),abs(old['energy_j']),dR,1e-12)+1e-12:flags.append('incremental_energy_balance')
        sweptJ=swept_minimum_volume(model,initial,x)
        if sweptJ<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        swept_gap=float(min(np.min(initial[pairs[:,1],0]-initial[pairs[:,0],0]),cutgaps.min()))
        if swept_gap<-1e-9:flags.append('swept_cut_crossing')
        if widths.max()>=BLADE['max_thickness_m']:flags.append('uncertified_wedge_cap')
        if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('unsupported_cut_projection')
        screens=[proper_surface_intersections(design,initial+t*(x-initial))[0] for t in [.5,1.]]
        if any(screens):flags.append('surface_intersection')
        faces=np.asarray([t for piece in design['pieces'] for t in piece['triangles']]);p0=points[faces];pf=x[faces]
        n0=np.cross(p0[:,1]-p0[:,0],p0[:,2]-p0[:,0]);nf=np.cross(pf[:,1]-pf[:,0],pf[:,2]-pf[:,0])
        area0=np.linalg.norm(n0,axis=1);area=np.linalg.norm(nf,axis=1);area_ratio=float(np.min(area/area0));cosine=float(np.min(np.einsum('ni,ni->n',n0,nf)/(area0*area)))
        if area_ratio<=0 or cosine<=0:flags.append('surface_orientation_change')
        print({'stage':'stability_start','elapsed_s':time.monotonic()-start},flush=True)
        strong=[labels[i] for i in np.flatnonzero(lam>1e-9)]
        h=reduced_tangent(model.cohesion.algorithmic_tangent(x,state['tangent_n_m'],committed,eligible),strong,fixed,points.size)
        ref=reduced_tangent(model.evaluate(points,tangent=True)['tangent_n_m'],strong,fixed,points.size);pre=diags(1/np.sqrt(ref.diagonal()))
        try:
            least=float(eigsh(pre@h@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=1600,ncv=40)[0])
            if least<1e-6:flags.append('stability_not_positive')
        except ArpackNoConvergence:least=None;flags.append('stability_inconclusive')
        external=np.asarray(A.T@lam).reshape(-1,3);external.ravel()[fixed_ids]+=residual[fixed_ids]
        fscale=max(float(np.linalg.norm(external,axis=1).sum()),1e-4);fbalance=float(np.linalg.norm(external.sum(axis=0))/fscale);mbalance=float(np.linalg.norm(np.cross(x,external).sum(axis=0))/(fscale*.065))
        if max(fbalance,mbalance)>.01:flags.append('force_or_moment_balance')
        for name,value in [('positions',x),('multipliers',lam),('edge_hits',hits),('support_reactions',support)]:np.save(args.output/(name+'.npy'),value)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        summary={'passed':not flags,'flags':flags,'phase':args.phase,'depth_mm':args.depth_mm,'drive_mm':args.drive_mm,'tip_z_m':tip,
            'damage_states':[s.__dict__ for s in states],'damage_changes':changes,'seed_damage_changes':seed_changes,
            'damaged_patches':sum(s.damage>0 for s in states),'max_damage':max(s.damage for s in states),'eligible_patches':np.flatnonzero(eligible).tolist(),
            'energy_j':state['energy_j'],'fracture_dissipation_j':diss,'cycle_ledger':cycle,'phase_ledger':phase,
            'increment_blade_work_j':blade_work,'increment_support_work_j':support_work,'increment_energy_residual_j':increment_error,
            'force_residual':force_residual,'min_cut_gap_m':float(cutgaps.min()),'max_cut_gap_m':float(cutgaps.max()),'swept_min_cut_gap_m':swept_gap,
            'min_contact_gap_m':float(gaps.min()),'min_multiplier_n':float(lam.min()),'swept_min_J':sweptJ,'surface_intersections':screens,
            'minimum_surface_area_ratio':area_ratio,'minimum_surface_normal_cosine':cosine,'minimum_stability_eigenvalue':least,
            'cut_contact_force_n':float(lam[:len(pairs)].sum()),'back_cap_nodes':back,'back_cap_force_n':float(sum(support[3*i] for i in back)),
            'force_balance_fraction':fbalance,'moment_balance_fraction':mbalance,'outer_iterations':outer,
            'seed_checkpoint':str(SEED.relative_to(ROOT)),'seed_summary_sha256':seed_hash,'previous_checkpoint':str(directory.relative_to(ROOT)),
            'source_hashes':hashes,'state_hashes':{name:hashlib.sha256((args.output/name).read_bytes()).hexdigest() for name in ['positions.npy','multipliers.npy','edge_hits.npy','support_reactions.npy']},
            'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
            'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},'forbidden_imports':forbidden,'full_cut':False,'simulator':False,'training':False}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:summary[k] for k in ['passed','flags','phase','depth_mm','drive_mm','max_damage','max_cut_gap_m','runtime_s']})


if __name__=='__main__':main()
