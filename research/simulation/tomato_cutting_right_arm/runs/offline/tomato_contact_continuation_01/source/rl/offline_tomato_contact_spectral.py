"""One capped fixed-damage triangle contact endpoint, not a cutting trajectory."""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/'runs/offline/tomato_full_cut_01/insertion/040'

def main():
    p=argparse.ArgumentParser();p.add_argument('--depth-mm',type=float,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--previous',type=Path);p.add_argument('--guess',type=Path,help='Uncommitted positions only; never damage or accepted history');p.add_argument('--resume',type=Path,help='Uncommitted optimizer chunk directory, never physical history');p.add_argument('--newton-steps',type=int,default=10)
    args=p.parse_args()
    if not 0<=args.depth_mm<=8.25:p.error('Contact-only probe <=8.25mm; no full cut')
    if not 1<=args.newton_steps<=30:p.error('Only 1 to 30 Newton steps per capped worker')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_coupled_contact import assemble_model,cut_pairs,supports,proper_surface_intersections
        from tomato_blade_damage import EvolvingCohesion
        from tomato_bonds import DamageState
        from tomato_triangle_contact import triangle_geometry,blade_resistance
        from tomato_contact_continuation import solve_triangle_continuation as solve_triangle_contact
        from tomato_linear_contact import solve_linear_contact,affine_space
        source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        seed=json.loads((SEED/'summary.json').read_text());assert seed['passed']
        for name,h in seed['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
        for name,h in seed['state_hashes'].items():assert hashlib.sha256((SEED/name).read_bytes()).hexdigest()==h
        model.cohesion.states=[DamageState(**s) for s in seed['damage_states']]
        fixed,_=supports(design,points,'indentation',0.);tip=float(points[pairs[:,0],2].max())-args.depth_mm/1000
        geometry=triangle_geometry(design,points,pairs,tip);C,b=geometry['matrix'],geometry['bounds']
        if args.previous:
            old=json.loads((args.previous/'summary.json').read_text());assert old['passed']
            for name,h in old['state_hashes'].items():assert hashlib.sha256((args.previous/name).read_bytes()).hexdigest()==h
            guess=np.load(args.previous/'positions.npy')
        else:
            # Start from the verified 5 mm equilibrium; continuation guesses
            # carry positions only. This is a contact-only frozen-damage test.
            guess=np.load(SEED/'positions.npy')
        if args.guess:
            guess=np.load(args.guess)
            if guess.shape!=points.shape or not np.isfinite(guess).all():raise ValueError('Invalid optimization guess')
        resume_active=None
        if args.resume:
            saved=json.loads((args.resume/'candidate.json').read_text())
            assert saved['optimization_only'] and not saved['passed'] and saved['depth_mm']==args.depth_mm
            for name,digest in saved['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
            assert hashlib.sha256((args.resume/'guess.npy').read_bytes()).hexdigest()==saved['guess_sha256']
            guess=np.load(args.resume/'guess.npy');resume_active=saved['optimizer_active_rows']
        print({'stage':'solve_start','depth_mm':args.depth_mm,'rows':C.shape[0],'elapsed_s':time.monotonic()-start},flush=True)
        x,lam,state,trace,ok,active,ids,free=solve_triangle_contact(model,guess,fixed,geometry,max_iterations=args.newton_steps,initial_active=resume_active)
        print({'stage':'solve_end','ok':ok,'iterations':len(trace),'elapsed_s':time.monotonic()-start},flush=True)
        if not ok:
            np.save(args.output/'guess.npy',x)
            result={'passed':False,'reason':'bounded_optimization_not_equilibrated','optimization_only':True,'depth_mm':args.depth_mm,'iterations':trace,'guess_sha256':hashlib.sha256((args.output/'guess.npy').read_bytes()).hexdigest(),'optimizer_active_rows':trace[-1]['optimizer_active_rows'],'source_hashes':{str(v.relative_to(ROOT)):hashlib.sha256(v.read_bytes()).hexdigest() for v in [Path(__file__),ROOT/'rl/tomato_contact_continuation.py',ROOT/'rl/tomato_triangle_contact.py',ROOT/'rl/tomato_linear_contact.py']},'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,'simulator':False,'training':False}
            (args.output/'candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(result);return
        flags=[]
        if not ok:flags.append('contact_equilibrium')
        residual=state['gradient_n'].ravel()-C.T@lam;scale=max(np.linalg.norm(state['gradient_n'].ravel()[ids]),np.linalg.norm(C.T@lam),1e-4)
        force=float(np.linalg.norm(residual[free])/scale);gap=float((C@x.ravel()-b).min())
        if force>1e-6:flags.append('force_residual')
        if gap<-1e-9 or lam.min()<-1e-9:flags.append('contact')
        if np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids])))>1e-12:flags.append('supports')
        if state['min_cell_ratio']<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('cut_projection')
        screens=proper_surface_intersections(design,x)[0]
        if screens:flags.append('surface_intersections')
        np.save(args.output/'equilibrium_guess.npy',x)  # Uncommitted optimizer output only.
        print({'stage':'stability_start','elapsed_s':time.monotonic()-start},flush=True)
        strong=np.flatnonzero(lam>1e-9);_,T=affine_space(C[strong],b[strong],fixed,points.size)
        h=T.T@state['tangent_n_m']@T;ref=T.T@model.evaluate(points,tangent=True)['tangent_n_m']@T;pre=diags(1/np.sqrt(ref.diagonal()))
        least=float(eigsh(pre@h@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=1600,ncv=80)[0])
        if least<1e-6:flags.append('stability')
        np.save(args.output/'positions.npy',x);np.save(args.output/'multipliers.npy',lam)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        sources=[Path(__file__),*[ROOT/'rl'/n for n in ['tomato_contact_continuation.py','tomato_triangle_contact.py','tomato_linear_contact.py','tomato_coupled_contact.py','tomato_blade_damage.py','tomato_surface_cohesion.py','tomato_bonds.py','tomato_volume_protection.py','tomato_nonlinear_checks.py']],source/'surface_design.json',source/'mass_stiffness_assignments.json']
        summary={'passed':not flags,'flags':flags,'depth_mm':args.depth_mm,'damage_states':seed['damage_states'],'damage_evolution_enabled':False,'seed_checkpoint':str(SEED.relative_to(ROOT)),
            'force_residual':force,'minimum_contact_gap_m':gap,'minimum_cut_gap_m':float(np.min(x[pairs[:,1],0]-x[pairs[:,0],0])),'minimum_multiplier_n':float(lam.min()),'contact_complementarity_n_m':float(np.max(np.abs(lam*(C@x.ravel()-b)))),'min_J':state['min_cell_ratio'],'min_length_ratio':state['min_length_ratio'],'energy_j':state['energy_j'],'blade_resistance_n':blade_resistance(geometry,x,lam),'surface_intersections':screens,'minimum_stability_eigenvalue':least,'iterations':trace,'edge_constraints':len(geometry['cap_rows']),'loaded_edge_constraints':{kind:int(sum(m['kind']==kind and lam[geometry['base_rows']+j]>1e-9 for j,m in enumerate(geometry['cap_rows']))) for kind in ['entry_edge','cap_edge']},
            'source_hashes':{str(v.relative_to(ROOT)):hashlib.sha256(v.read_bytes()).hexdigest() for v in sources},'state_hashes':{n:hashlib.sha256((args.output/n).read_bytes()).hexdigest() for n in ['positions.npy','multipliers.npy']},'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
            'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},'forbidden_imports':forbidden,'trajectory_validated':False,'full_cut':False,'simulator':False,'training':False}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items() if k not in ['damage_states','source_hashes','state_hashes','iterations']})
if __name__=='__main__':main()
