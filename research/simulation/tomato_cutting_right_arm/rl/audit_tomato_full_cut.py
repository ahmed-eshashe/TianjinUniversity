"""Independent capped audit of all accepted full-cut-attempt checkpoints."""
import fcntl,hashlib,json,resource,signal,sys
from pathlib import Path

def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    root=Path(__file__).resolve().parents[1];folder=root/'runs/offline/tomato_full_cut_01'
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_coupled_contact import assemble_model,cut_pairs,supports
        from tomato_blade_damage import EvolvingCohesion,wedge_geometry,edge_history,contact_eligibility,BLADE
        from tomato_bonds import DamageState
        from tomato_unloading import damage_changes
        from tomato_full_cut_checks import material_components,cap_contact_witness
        source=root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        top=float(points[pairs[:,0],2].max());bottom=float(points[pairs[:,0],2].min())
        def read(path):
            s=json.loads((path/'summary.json').read_text())
            for name,h in s['source_hashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
            for name,h in s['state_hashes'].items():assert hashlib.sha256((path/name).read_bytes()).hexdigest()==h,name
            return s,np.load(path/'positions.npy'),np.load(path/'multipliers.npy'),np.load(path/'edge_hits.npy')
        seedpath=root/'runs/offline/tomato_blade_damage_01/insertion_refined/08'
        old,oldx,oldlam,oldhits=read(seedpath)
        triangles=[]
        for piece in design['pieces']:
            triangles.append({tuple(sorted(tuple(np.round(points[i,1:],12)) for i in tri)) for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut'})
        assert triangles[0]==triangles[1] and len(triangles[0])==448
        fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(points.size),ids)
        records=[];lastpath=seedpath
        files=[folder/'probe_4p125/summary.json',*sorted((folder/'insertion').glob('*/summary.json'))]
        for file in files:
            raw=json.loads(file.read_text())
            if not raw['passed']:continue
            s,x,lam,hits=read(file.parent);flags=[]
            states=[DamageState(**v) for v in s['damage_states']];olds=[DamageState(**v) for v in old['damage_states']]
            model.cohesion.states=states;state=model.evaluate(x);R=model.cohesion.dissipation(states)
            A,b,labels,physical,widths=wedge_geometry(design,points,pairs,s['tip_z_m'])
            oldA,_,_,oldphys,_=wedge_geometry(design,points,pairs,old['tip_z_m'])
            eligible=contact_eligibility(model.cohesion,hits,lam,widths)
            trial=model.cohesion.trial_states(x,olds,eligible)
            if max(abs(a.damage-z.damage) for a,z in zip(trial,states))>1e-9:flags.append('damage_not_consistent')
            changes=damage_changes(olds,states)
            if changes['healed_patches'] or changes['decreased_histories']:flags.append('healing')
            if not np.array_equal(edge_history(points,pairs,old['tip_z_m'],s['tip_z_m'],oldhits),hits):flags.append('edge_history')
            if np.flatnonzero(eligible).tolist()!=s['eligible_patches']:flags.append('eligibility')
            if any(z.damage>a.damage+1e-9 and not ok for a,z,ok in zip(olds,states,eligible)):flags.append('unloaded_damage')
            if np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids])))>1e-12:flags.append('support_changed')
            if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('projection_changed')
            gap=float(np.min(x[pairs[:,1],0]-x[pairs[:,0],0]));oldgap=float(np.min(oldx[pairs[:,1],0]-oldx[pairs[:,0],0]))
            if min(gap,oldgap)<-1e-9 or (A@x.ravel()-b).min()<-1e-9 or lam.min()<-1e-9:flags.append('crossing_or_contact')
            residual=state['gradient_n'].ravel()-A.T@lam;scale=max(np.linalg.norm(state['gradient_n'].ravel()[ids]),np.linalg.norm(A.T@lam),1e-4)
            force=float(np.linalg.norm(residual[free])/scale)
            if force>1e-6:flags.append('force_residual')
            if abs(state['energy_j']-s['energy_j'])>1e-10 or abs(R-s['fracture_dissipation_j'])>1e-12:flags.append('energy_recomputation')
            work=float(.5*(oldlam+lam)@(physical-oldphys));dR=R-old['fracture_dissipation_j'];dE=state['energy_j']-old['energy_j'];err=work-dE-dR
            if abs(work-s['increment_blade_work_j'])>1e-12:flags.append('work_recomputation')
            if abs(err)>.01*max(abs(work),abs(state['energy_j']),abs(old['energy_j']),dR,1e-12)+1e-12:flags.append('increment_energy')
            cumulative=old['cumulative_blade_work_j']+work;totalerr=cumulative-state['energy_j']-R;totalscale=max(abs(cumulative),abs(state['energy_j'])+R,1e-12)
            if abs(totalerr)>.01*totalscale+1e-12:flags.append('total_energy')
            # Matched triangle gaps are affine in space/time under these guides.
            # Positive-part uncapped wedge is convex and lies below the affine
            # interpolant of its nodal widths. Do not extend proof past cap.
            if widths.max()>=BLADE['max_thickness_m']:flags.append('capped_finite_triangle_unvalidated')
            topology=material_components(design,assign,[p['indices'].tolist() for p in model.cohesion.patches],[z.damage for z in states],pairs.tolist())
            records.append({'checkpoint':str(file.parent.relative_to(root)),'passed':not flags,'flags':flags,'depth_mm':s['depth_mm'],'damaged_patches':s['damaged_patches'],'completely_failed_patches':s['completely_failed_patches'],'max_damage':s['max_damage'],'damage_changes':changes,'minimum_cut_gap_m':gap,'force_residual':force,'relative_total_energy_error':abs(totalerr)/totalscale,'increment_energy_error_j':err,'topology':topology,'peak_rss_bytes':s['peak_rss_bytes'],'runtime_s':s['runtime_s']})
            old,oldx,oldlam,oldhits=s,x,lam,hits;lastpath=file.parent
        # Feasible-at-vertices finite-triangle counterexample for the first
        # checkpoint beyond full bevel embedding; not an observed deformation.
        depth=.008125;tip=top-depth;witnesses=[]
        for tri,tag in zip(design['pieces'][0]['triangles'],design['pieces'][0]['face_tags']):
            if tag=='cut':
                penetration=cap_contact_witness(points[tri,2].tolist(),tip,BLADE['max_thickness_m']/BLADE['single_bevel_length_m'],BLADE['max_thickness_m'])
                if penetration>1e-9:witnesses.append({'triangle':tri,'interior_penetration_m':penetration})
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result={'accepted_checkpoints':len(records),'all_accepted_audits_passed':bool(records) and all(v['passed'] for v in records),'records':records,'last_accepted':str(lastpath.relative_to(root)),
            'cut_face_height_m':top-bottom,'edge_traverse_depth_mm':1000*(top-bottom),'bottom_full_bevel_depth_mm':1000*(top-bottom+BLADE['single_bevel_length_m']),
            'cap_counterexample':{'depth_mm':8.125,'violating_triangles':len(witnesses),'maximum_synthetic_interior_penetration_m':max((v['interior_penetration_m'] for v in witnesses),default=0.),'worst':max(witnesses,key=lambda w:w['interior_penetration_m'],default=None),'is_actual_state':False},
            'full_cut_passed':False,'slice_release_verified':False,'simulator':False,'training':False,'forbidden_imports':forbidden}
        (folder/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='records'})
if __name__=='__main__':main()
