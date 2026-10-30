"""Independent saved-state/contact/energy audit of the shallow offline test."""
import fcntl,hashlib,json,resource,signal,sys
from pathlib import Path


def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    root=Path(__file__).resolve().parents[1];folder=root/'runs/offline/tomato_blade_damage_01'
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_coupled_contact import assemble_model,cut_pairs,supports
        from tomato_blade_damage import EvolvingCohesion,wedge_geometry,contact_eligibility
        from tomato_bonds import DamageState
        source=root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assignments=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assignments,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        triangles=np.asarray([t for p in design['pieces'] for t in p['triangles']]);rest=points[triangles]
        restnorm=np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]);restarea=np.linalg.norm(restnorm,axis=1)
        records=[];fracture_intervals={}
        def read(path):
            s=json.loads((path/'summary.json').read_text())
            for file,digest in s['source_hashes'].items():assert hashlib.sha256((root/file).read_bytes()).hexdigest()==digest,file
            for file,digest in s['state_hashes'].items():assert hashlib.sha256((path/file).read_bytes()).hexdigest()==digest,file
            return s,np.load(path/'positions.npy'),np.load(path/'multipliers.npy'),np.load(path/'edge_hits.npy')
        for name in ['insertion_final','miss_final','insertion_refined']:
            directory=folder/name
            if not directory.exists():continue
            files=sorted(directory.glob('*/summary.json'));previous=None;baseline=None;energy_errors=[]
            if name=='insertion_refined':
                baseline=json.loads((directory/'baseline.json').read_text());previous=read(root/baseline['checkpoint'])
            for file in files:
                s,x,lam,hits=read(file.parent)
                if not s['passed']:
                    records.append({'checkpoint':str(file.parent.relative_to(root)),'passed':False,'driver_flags':s['flags']});break
                model.cohesion.states=[DamageState(**v) for v in s['damage_states']]
                state=model.evaluate(x)
                assert abs(state['energy_j']-s['energy_j'])<1e-10
                diss=model.cohesion.dissipation(model.cohesion.states);assert abs(diss-s['fracture_dissipation_j'])<1e-12
                A,b,_,physical,width=wedge_geometry(design,points,pairs,s['tip_z_m'],mode=s['mode'])
                eligible=contact_eligibility(model.cohesion,hits,lam,width)
                assert np.flatnonzero(eligible).tolist()==s['eligible_patches']
                fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(x.size),ids)
                residual=state['gradient_n'].ravel()-A.T@lam
                scale=max(np.linalg.norm(state['gradient_n'].ravel()[ids]),np.linalg.norm(A.T@lam),1e-4)
                force_residual=float(np.linalg.norm(residual[free])/scale)
                flags=[]
                if force_residual>1e-6:flags.append('recomputed_force_residual')
                if np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids])))>1e-12:flags.append('fixture_or_guide_changed')
                if (A@x.ravel()-b).min()<-1e-9 or lam.min()<-1e-9:flags.append('recomputed_contact_violation')
                if (x[pairs[:,1],0]-x[pairs[:,0],0]).min()<-1e-9:flags.append('actual_cut_gap_negative')
                f=x[triangles];normal=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);area=np.linalg.norm(normal,axis=1)
                area_ratio=float(np.min(area/restarea));cosine=float(np.min(np.einsum('ni,ni->n',normal,restnorm)/(area*restarea)))
                if area_ratio<=0 or cosine<=0:flags.append('surface_orientation_change')
                work=0.
                if previous:
                    old,oldx,oldlam,oldhits=previous
                    _,_,_,oldphysical,_=wedge_geometry(design,points,pairs,old['tip_z_m'],mode=old['mode'])
                    work=float(.5*(lam+oldlam)@(physical-oldphysical))
                    assert abs(work-s['increment_blade_work_j'])<1e-12
                    oldstates=[DamageState(**v) for v in old['damage_states']]
                    for i,(new,oldstate) in enumerate(zip(model.cohesion.states,oldstates)):
                        if new.damage>oldstate.damage+1e-9 and not eligible[i]:flags.append('damage_without_contact')
                        if new.damage<oldstate.damage:flags.append('healing')
                    if np.any(oldhits&~hits):flags.append('lost_edge_history')
                records.append({'checkpoint':str(file.parent.relative_to(root)),'passed':not flags,'flags':flags,
                    'depth_mm':s['depth_mm'],'damaged_patches':s['damaged_patches'],'max_damage':s['max_damage'],
                    'energy_j':state['energy_j'],'fracture_dissipation_j':diss,'force_residual':force_residual,
                    'minimum_surface_area_ratio':area_ratio,'minimum_surface_normal_cosine':cosine,
                    'min_J':state['min_cell_ratio'],'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']})
                previous=(s,x,lam,hits)
            if name=='insertion_final':
                accepted=[json.loads(p.read_text()) for p in files if json.loads(p.read_text())['passed']]
                zero=[s for s in accepted if s['damaged_patches']==0]
                if accepted and zero and accepted[-1]['damaged_patches']:
                    a,z=accepted[-1],zero[-1];loss=a['fracture_dissipation_j']-z['fracture_dissipation_j']
                    error=(a['cumulative_blade_work_j']-z['cumulative_blade_work_j'])-(a['energy_j']-z['energy_j'])-loss
                    fracture_intervals[name]={'baseline_depth_mm':z['depth_mm'],'energy_residual_j':error,'fracture_dissipation_j':loss,'fracture_normalized_residual':abs(error)/max(loss,1e-12),'passed':abs(error)<=.01*loss+1e-12}
            if name=='insertion_refined' and (directory/'interval_energy.json').exists():fracture_intervals[name]=json.loads((directory/'interval_energy.json').read_text())
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        validated_paths=[name for name,entry in fracture_intervals.items() if entry['passed'] and
                         all(r['passed'] for r in records if ('/'+name+'/') in r['checkpoint'])]
        result={'checked_saved_states':len(records),'all_saved_states_passed':all(r['passed'] for r in records),'records':records,
            'fracture_intervals':fracture_intervals,'coupled_partial_fracture_validated':bool(validated_paths),'validated_fracture_paths':validated_paths,
            'full_cut':False,'simulator':False,'training':False,'forbidden_imports':forbidden}
        (folder/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='records'})


if __name__=='__main__':main()
