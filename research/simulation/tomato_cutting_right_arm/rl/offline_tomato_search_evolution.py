"""Capped guided triangle/contact damage endpoint with a fresh work ledger.

No simulator or time integration. Tentative numerical chunks are never physical
history. This worker alone cannot certify blade removal or independent release.
"""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--depth-mm',type=float,required=True);p.add_argument('--previous',type=Path)
    p.add_argument('--resume',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if not 0<=a.depth_mm<=48:p.error('Guided insertion diagnostic is restricted to 0..48 mm')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);a.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_bonds import DamageState
        from tomato_coupled_contact import assemble_model,cut_pairs,supports,swept_minimum_volume,proper_surface_intersections
        from tomato_blade_damage import EvolvingCohesion,edge_history,contact_eligibility,BLADE
        from tomato_triangle_contact import triangle_geometry,blade_resistance,nodal_blade_multipliers,swept_triangle_gap
        from tomato_contact_search import solve_triangle_continuation
        from tomato_linear_contact import affine_space
        from tomato_full_cut_checks import material_components
        from audit_tomato_triangle_contact import minimum_polygon_gap
        source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        fixed,_=supports(design,points,'indentation',0.);top=float(points[pairs[:,0],2].max());tip=top-a.depth_mm/1000
        files=[Path(__file__),*[ROOT/'rl'/n for n in ['offline_tomato_triangle_evolution.py','audit_tomato_search_evolution.py','tomato_contact_search.py','tomato_contact_continuation.py','tomato_triangle_contact.py','tomato_linear_contact.py','tomato_coupled_contact.py','tomato_blade_damage.py','tomato_surface_cohesion.py','tomato_bonds.py','tomato_volume_protection.py','tomato_nonlinear_checks.py','tomato_full_cut_checks.py','audit_tomato_triangle_contact.py','audit_tomato_triangle_evolution.py']],source/'surface_design.json',source/'mass_stiffness_assignments.json']
        hashes={str(v.relative_to(ROOT)):digest(v) for v in files}
        old=None;initial=points.copy();committed=list(model.cohesion.states);old_tip=top;oldhits=np.zeros(len(pairs),dtype=bool)
        previous_digest=None
        if a.previous:
            old=json.loads((a.previous/'summary.json').read_text());previous_digest=digest(a.previous/'summary.json')
            assert old['passed'] and old['backend'] in ('triangle_evolving_v1','triangle_search_evolving_v1')
            if old['backend']=='triangle_evolving_v1':
                assert all(hashes.get(n)==h for n,h in old['source_hashes'].items()),'Verified numerical-source transition failed'
            else:assert old['source_hashes']==hashes
            for name,h in old['state_hashes'].items():assert digest(a.previous/name)==h
            if not 0<=a.depth_mm-old['depth_mm']<=.25000001:raise ValueError('Only insertion steps <=0.25 mm are permitted')
            initial=np.load(a.previous/'positions.npy');oldhits=np.load(a.previous/'edge_hits.npy');old_tip=old['tip_z_m'];committed=[DamageState(**s) for s in old['damage_states']]
        elif a.depth_mm!=0:raise ValueError('A new triangle trajectory must start undamaged at zero insertion')
        hits=edge_history(points,pairs,old_tip,tip,oldhits);geometry=triangle_geometry(design,points,pairs,tip);C,b=geometry['matrix'],geometry['bounds']
        x=initial.copy();model.cohesion.states=list(committed);active=None;outer=[]
        if a.resume:
            saved=json.loads((a.resume/'candidate.json').read_text())
            assert saved['optimization_only'] and not saved['passed'] and saved['depth_mm']==a.depth_mm
            assert saved['source_hashes']==hashes and saved['previous_summary_sha256']==previous_digest
            assert digest(a.resume/'guess.npy')==saved['guess_sha256']
            x=np.load(a.resume/'guess.npy');model.cohesion.states=[DamageState(**s) for s in saved['trial_damage_states']];active=saved['optimizer_active_rows']
        def candidate(reason):
            np.save(a.output/'guess.npy',x)
            report={'passed':False,'optimization_only':True,'reason':reason,'depth_mm':a.depth_mm,'previous_summary_sha256':previous_digest,
                'guess_sha256':digest(a.output/'guess.npy'),'trial_damage_states':[s.__dict__ for s in model.cohesion.states],
                'optimizer_active_rows':active,'outer_iterations':outer,'source_hashes':hashes,'runtime_s':time.monotonic()-start,
                'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                'full_cut':False,'simulator':False,'training':False}
            (a.output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k not in ['source_hashes','trial_damage_states','optimizer_active_rows','outer_iterations']},flush=True)
        consistent=False
        for outer_iteration in range(2):
            x,lam,state,trace,ok,_,ids,free=solve_triangle_continuation(model,x,fixed,geometry,max_iterations=6,initial_active=active)
            active=trace[-1]['optimizer_active_rows'];outer.append({'contact_converged':ok,'trace':trace})
            if not ok:candidate('bounded_contact_not_equilibrated');return
            nodal=nodal_blade_multipliers(geometry,pairs,lam);eligible=contact_eligibility(model.cohesion,hits,nodal,geometry['widths'])
            trial=model.cohesion.trial_states(x,committed,eligible)
            difference=max(max(abs(s.damage-t.damage),abs(s.kappa_m-t.kappa_m)) for s,t in zip(trial,model.cohesion.states))
            outer[-1]['maximum_trial_history_difference']=difference
            model.cohesion.states=trial
            if difference<=1e-9:consistent=True;break
        if not consistent:candidate('bounded_damage_not_consistent');return
        # Every physical check below uses the final constitutive state, never
        # the optimizer's approximate tangent or intermediate damage guesses.
        state=model.evaluate(x,tangent=True);flags=[];g=state['gradient_n'].ravel();residual=g-C.T@lam
        scale=max(np.linalg.norm(g[ids]),np.linalg.norm(C.T@lam),1e-4);force=float(np.linalg.norm(residual[free])/scale)
        gaps=C@x.ravel()-b;comp=float(np.max(np.abs(lam*gaps)));polygon_gap,_=minimum_polygon_gap(design,x,tip,BLADE)
        cutgap=float(np.min(x[pairs[:,1],0]-x[pairs[:,0],0]));swept_gap=swept_triangle_gap(design,points,pairs,initial,x,old_tip,tip)
        if force>1e-6:flags.append('force_residual')
        if min(float(gaps.min()),polygon_gap,cutgap,swept_gap)<-1e-9 or lam.min()<-1e-9 or comp>1e-10:flags.append('contact')
        if np.max(np.abs(lam[~geometry['active']]),initial=0.)>0:flags.append('inactive_contact_load')
        if np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids])))>1e-12:flags.append('supports')
        if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('cut_projection')
        states=model.cohesion.states
        if any(s.damage<t.damage or s.kappa_m<t.kappa_m for s,t in zip(states,committed)):flags.append('healing')
        diss=model.cohesion.dissipation(states);old_diss=model.cohesion.dissipation(committed);R=blade_resistance(geometry,x,lam)
        work=0. if old is None else .5*(old['blade_resistance_n']+R)*(a.depth_mm-old['depth_mm'])/1000
        cumulative=(old['cumulative_blade_work_j'] if old else 0.)+work
        error=cumulative-state['energy_j']-diss;normalizer=max(abs(cumulative),state['energy_j']+diss,1e-12)
        increment_error=work-(state['energy_j']-(old['energy_j'] if old else 0.))-(diss-old_diss)
        if abs(error)>.01*normalizer+1e-12:flags.append('cumulative_work_balance')
        if abs(increment_error)>.01*max(abs(work),state['energy_j'],old['energy_j'] if old else 0.,diss-old_diss,1e-12)+1e-12:flags.append('incremental_work_balance')
        J=swept_minimum_volume(model,initial,x)
        if J<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        screens=[proper_surface_intersections(design,initial+t*(x-initial))[0] for t in [.5,1.]]
        if any(screens):flags.append('surface_intersections')
        triangles=np.array([t for piece in design['pieces'] for t in piece['triangles']]);rest=points[triangles];f=x[triangles]
        rn=np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]);nn=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);ra=np.linalg.norm(rn,axis=1);na=np.linalg.norm(nn,axis=1)
        area=float(np.min(na/ra));cosine=float(np.min(np.einsum('ni,ni->n',nn,rn)/(na*ra)))
        if area<=0 or cosine<=0:flags.append('surface_orientation')
        external=np.asarray(C.T@lam).reshape(-1,3);external.ravel()[ids]+=residual[ids];fscale=max(float(np.linalg.norm(external,axis=1).sum()),1e-4)
        fbalance=float(np.linalg.norm(external.sum(axis=0))/fscale);mbalance=float(np.linalg.norm(np.cross(x,external).sum(axis=0))/(fscale*.065))
        if max(fbalance,mbalance)>.01:flags.append('force_moment_balance')
        # Real supported loading-side tangent, not the numerical Newton step.
        algorithmic=model.cohesion.algorithmic_tangent(x,state['tangent_n_m'],committed,eligible)
        strong=np.flatnonzero(lam>1e-9);_,T=affine_space(C[strong],b[strong],fixed,points.size)
        h=T.T@algorithmic@T;ref=T.T@model.evaluate(points,tangent=True)['tangent_n_m']@T;pre=diags(1/np.sqrt(ref.diagonal()))
        print({'stage':'physical_stability','elapsed_s':time.monotonic()-start},flush=True)
        least=float(eigsh(pre@h@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=1600,ncv=80)[0])
        if least<1e-6:flags.append('softening_stability')
        topology=material_components(design,assign,[p['indices'] for p in model.cohesion.patches],[s.damage for s in states],pairs)
        np.save(a.output/'positions.npy',x);np.save(a.output/'multipliers.npy',lam);np.save(a.output/'edge_hits.npy',hits)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        assert all(digest(ROOT/n)==v for n,v in hashes.items())
        summary={'passed':not flags,'flags':flags,'backend':'triangle_search_evolving_v1','numerical_metric_only':True,'depth_mm':a.depth_mm,'tip_z_m':tip,
            'previous_checkpoint':str(a.previous.resolve().relative_to(ROOT)) if a.previous else None,'previous_summary_sha256':previous_digest,
            'damage_states':[s.__dict__ for s in states],'eligible_patches':np.flatnonzero(eligible).tolist(),'damaged_patches':sum(s.damage>0 for s in states),'completely_failed_patches':sum(s.damage==1 for s in states),'max_damage':max(s.damage for s in states),
            'energy_j':state['energy_j'],'fracture_dissipation_j':diss,'blade_resistance_n':R,'increment_blade_work_j':work,'cumulative_blade_work_j':cumulative,
            'energy_residual_j':error,'relative_energy_residual':abs(error)/normalizer,'increment_energy_residual_j':increment_error,
            'force_residual':force,'complementarity_n_m':comp,'independent_polygon_minimum_gap_m':polygon_gap,'swept_blade_minimum_gap_m':swept_gap,'minimum_cut_gap_m':cutgap,
            'minimum_multiplier_n':float(lam.min()),'swept_min_J':J,'min_length_ratio':state['min_length_ratio'],'surface_intersections':screens,'minimum_surface_area_ratio':area,'minimum_surface_normal_cosine':cosine,
            'force_balance_fraction':fbalance,'moment_balance_fraction':mbalance,'minimum_softening_stability_eigenvalue':least,'topology':topology,'outer_iterations':outer,
            'source_hashes':hashes,'state_hashes':{n:digest(a.output/n) for n in ['positions.npy','multipliers.npy','edge_hits.npy']},
            'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
            'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},
            'forbidden_imports':forbidden,'damage_evolution_enabled':True,'independent_release_validated':False,'full_cut':False,'simulator':False,'training':False}
        (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items() if k not in ['source_hashes','state_hashes','outer_iterations','damage_states']},flush=True)
if __name__=='__main__':main()
