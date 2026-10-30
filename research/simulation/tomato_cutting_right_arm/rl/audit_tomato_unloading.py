"""Independent saved-state energy, damage and matched-face noncrossing audit."""
import fcntl,hashlib,json,resource,signal,sys
from pathlib import Path


def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    root=Path(__file__).resolve().parents[1];folder=root/'runs/offline/tomato_unloading_01'
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_bonds import DamageState
        from tomato_blade_damage import EvolvingCohesion,wedge_geometry,contact_eligibility,BLADE
        from tomato_coupled_contact import assemble_model,cut_pairs,supports
        from tomato_unloading import ledger,damage_changes
        source=root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assignments=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assignments,0.);pairs=cut_pairs(design);n=len(pairs);model.cohesion=EvolvingCohesion(design,pairs)
        topology=[]
        for piece in design['pieces']:
            topology.append({tuple(sorted(tuple(np.round(points[i,1:],12)) for i in tri)) for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut'})
        assert topology[0]==topology[1] and len(topology[0])==448
        triangles=np.asarray([t for piece in design['pieces'] for t in piece['triangles']]);rest=points[triangles]
        norm0=np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]);area0=np.linalg.norm(norm0,axis=1)
        cached={}
        def read(path):
            s=json.loads((path/'summary.json').read_text());assert s['passed'],(path,s['flags'])
            for file,digest in s['source_hashes'].items():
                if file not in cached:cached[file]=hashlib.sha256((root/file).read_bytes()).hexdigest()
                assert cached[file]==digest,file
            for file,digest in s['state_hashes'].items():assert hashlib.sha256((path/file).read_bytes()).hexdigest()==digest
            return s,np.load(path/'positions.npy'),np.load(path/'multipliers.npy'),np.load(path/'edge_hits.npy')
        seed_path=root/'runs/offline/tomato_blade_damage_01/insertion_refined/08'
        seed,sx,sl,sh=read(seed_path);seed_states=[DamageState(**s) for s in seed['damage_states']]
        model.cohesion.states=seed_states;seed_eval=model.evaluate(sx);seedE=seed_eval['energy_j'];seedR=model.cohesion.dissipation(seed_states)
        seedA,_,_,_,_=wedge_geometry(design,points,pairs,seed['tip_z_m'])
        sf,_=supports(design,points,'indentation',0.);si=np.array(sorted(sf));seed_support=np.zeros(sx.size)
        seed_support[si]=(seed_eval['gradient_n'].ravel()-seedA.T@sl)[si]
        all_records=[];branches={}
        for name,expected in [('coarse',28),('fine',44)]:
            files=sorted((folder/name).glob('*/summary.json'));assert len(files)==expected,(name,len(files))
            old,oldx,oldlam,oldhits=seed,sx,sl,sh;old_support=seed_support;oldE=seedE;oldR=seedR
            cycle_work=0.;cycle_peak=seedE;old_phase=None;phase=None;records=[]
            for file in files:
                s,x,lam,hits=read(file.parent);flags=[]
                states=[DamageState(**v) for v in s['damage_states']];oldstates=[DamageState(**v) for v in old['damage_states']]
                changes=damage_changes(oldstates,states);fromseed=damage_changes(seed_states,states)
                if changes['healed_patches'] or changes['decreased_histories']:flags.append('healing')
                model.cohesion.states=states;state=model.evaluate(x);E=state['energy_j'];R=model.cohesion.dissipation(states)
                A,b,labels,physical,widths=wedge_geometry(design,points,pairs,s['tip_z_m'])
                _,_,_,oldphysical,_=wedge_geometry(design,points,pairs,old['tip_z_m'])
                eligible=contact_eligibility(model.cohesion,hits,lam,widths)
                assert np.flatnonzero(eligible).tolist()==s['eligible_patches']
                for i,(a,z) in enumerate(zip(oldstates,states)):
                    if z.damage>a.damage+1e-9 and not eligible[i]:flags.append('unloaded_damage_growth')
                if np.any(oldhits&~hits):flags.append('lost_edge_history')
                fixed,back=supports(design,points,'reclosure' if s['phase']=='reclosure' else 'indentation',s['drive_mm']/1000)
                ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(x.size),ids)
                residual=state['gradient_n'].ravel()-A.T@lam;support=np.zeros(x.size);support[ids]=residual[ids]
                scale=max(np.linalg.norm(state['gradient_n'].ravel()[ids]),np.linalg.norm(A.T@lam),1e-4)
                force_residual=float(np.linalg.norm(residual[free])/scale)
                saved_support=np.load(file.parent/'support_reactions.npy')
                assert np.max(np.abs(saved_support-support))<1e-8
                if force_residual>1e-6:flags.append('force_residual')
                if np.max(np.abs(x.ravel()[ids]-np.asarray([fixed[i] for i in ids])))>1e-12:flags.append('support_error')
                if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('cut_projection_changed')
                gaps=x[pairs[:,1],0]-x[pairs[:,0],0];oldgaps=oldx[pairs[:,1],0]-oldx[pairs[:,0],0]
                swept=float(min(gaps.min(),oldgaps.min()))
                if swept<-1e-9 or (A@x.ravel()-b).min()<-1e-9 or lam.min()<-1e-9:flags.append('contact_or_crossing')
                if np.max(np.abs(lam[:n][widths>0]),initial=0.)>1e-9:flags.append('redundant_cut_force')
                bw=float(.5*(oldlam+lam)@(physical-oldphysical));sw=float(.5*(old_support+support)@(x-oldx).ravel())
                assert abs(bw-s['increment_blade_work_j'])<1e-12 and abs(sw-s['increment_support_work_j'])<1e-12
                assert abs(E-s['energy_j'])<1e-12 and abs(R-s['fracture_dissipation_j'])<1e-12
                cycle_work+=bw+sw
                cycle=ledger(E,R,cycle_work,initial_energy=seedE,initial_dissipation=seedR,peak_energy=cycle_peak);cycle_peak=cycle['peak_energy_j']
                if old_phase==s['phase']:
                    phase=ledger(E,R,phase['work_j']+bw+sw,initial_energy=phase['initial_energy_j'],initial_dissipation=phase['initial_dissipation_j'],peak_energy=phase['peak_energy_j'])
                else:phase=ledger(E,R,bw+sw,initial_energy=oldE,initial_dissipation=oldR)
                if not cycle['passed'] or not phase['passed']:flags.append('energy_balance')
                assert abs(cycle['residual_j']-s['cycle_ledger']['residual_j'])<1e-12
                assert abs(phase['residual_j']-s['phase_ledger']['residual_j'])<1e-12
                faces=x[triangles];norm=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);area=np.linalg.norm(norm,axis=1)
                area_ratio=float(np.min(area/area0));cosine=float(np.min(np.einsum('ni,ni->n',norm,norm0)/(area*area0)))
                if area_ratio<=0 or cosine<=0 or s['swept_min_J']<.1:flags.append('collapse_or_orientation')
                if s['minimum_stability_eigenvalue'] is None or s['minimum_stability_eigenvalue']<1e-6:flags.append('stability')
                if any(s['surface_intersections']):flags.append('surface_intersection')
                if s['phase']=='reclosure' and widths.any():flags.append('blade_still_present')
                record={'checkpoint':str(file.parent.relative_to(root)),'passed':not flags,'flags':flags,'phase':s['phase'],'depth_mm':s['depth_mm'],'drive_mm':s['drive_mm'],
                    'healed_patches':changes['healed_patches'],'decreased_histories':changes['decreased_histories'],
                    'max_damage':s['max_damage'],'seed_damage_change':fromseed['max_absolute_damage_change'],'seed_history_change_m':fromseed['max_absolute_history_change_m'],
                    'fracture_dissipation_j':R,'energy_j':E,'cycle_ledger':cycle,'phase_ledger':phase,
                    'min_cut_gap_m':float(gaps.min()),'max_cut_gap_m':float(gaps.max()),'swept_min_cut_gap_m':swept,
                    'cut_force_n':float(lam[:n].sum()),'wedge_resistance_n':float(.5*BLADE['max_thickness_m']/BLADE['single_bevel_length_m']*lam[n:].sum()),
                    'support_force_n':float(sum(support[3*i] for i in back)),'force_residual':force_residual,
                    'surface_area_ratio':area_ratio,'surface_normal_cosine':cosine,'swept_min_J':s['swept_min_J'],
                    'minimum_stability_eigenvalue':s['minimum_stability_eigenvalue'],'runtime_s':s['runtime_s'],'peak_rss_bytes':s['peak_rss_bytes']}
                records.append(record);old,oldx,oldlam,oldhits=s,x,lam,hits;old_support=support;oldE=E;oldR=R;old_phase=s['phase']
            closed=[r for r in records if r['phase']=='withdrawal' and r['depth_mm']==0][-1]
            pressed=[r for r in records if r['phase']=='reclosure' and r['drive_mm']==.05][0]
            opened=[r for r in records if r['phase']=='reclosure' and r['drive_mm']==-.05][0]
            assert closed['max_cut_gap_m']<=1e-9 and closed['energy_j']<1e-12
            assert pressed['cut_force_n']>1e-6 and opened['max_cut_gap_m']>1e-6
            assert records[-1]['energy_j']<1e-12 and records[-1]['max_cut_gap_m']<1e-9
            branches[name]={'states':len(records),'passed':all(r['passed'] for r in records),'withdrawal_final':closed,'pressed':pressed,'reopened':opened,'final':records[-1]}
            all_records+=records
        a={round(r['depth_mm'],6):r for r in all_records if '/coarse/' in r['checkpoint'] and r['phase']=='withdrawal'}
        b={round(r['depth_mm'],6):r for r in all_records if '/fine/' in r['checkpoint'] and r['phase']=='withdrawal'}
        force_errors=[]
        for key,x in a.items():
            y=b[key];v,w=x['wedge_resistance_n'],y['wedge_resistance_n']
            if max(abs(v),abs(w))>1e-6:force_errors.append(abs(v-w)/max(abs(v),abs(w)))
            else:assert abs(v-w)<1e-9
        wc=branches['coarse']['withdrawal_final']['phase_ledger']['work_j'];wf=branches['fine']['withdrawal_final']['phase_ledger']['work_j']
        comparisons={'maximum_matched_wedge_force_relative_change':max(force_errors),'recovered_work_relative_change':abs(wc/wf-1)}
        assert max(comparisons.values())<.1
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        summary={'passed':all(r['passed'] for r in all_records),'states':len(all_records),'matched_cut_triangles':448,'fixed_projection_triangle_certificate':True,
            'seed_energy_j':seedE,'retained_fracture_energy_j':seedR,'max_seed_damage_change':max(r['seed_damage_change'] for r in all_records),
            'max_seed_history_change_m':max(r['seed_history_change_m'] for r in all_records),'healing':any(r['healed_patches'] or r['decreased_histories'] for r in all_records),
            'maximum_swept_penetration_m':max(0.,-min(r['swept_min_cut_gap_m'] for r in all_records)),
            'min_J':min(r['swept_min_J'] for r in all_records),'minimum_stability_eigenvalue':min(r['minimum_stability_eigenvalue'] for r in all_records),
            'max_force_residual':max(r['force_residual'] for r in all_records),'peak_rss_bytes':max(r['peak_rss_bytes'] for r in all_records),
            'runtime_s':sum(r['runtime_s'] for r in all_records),'max_worker_runtime_s':max(r['runtime_s'] for r in all_records),
            'maximum_phase_energy_residual_relative':max(r['phase_ledger']['relative_residual'] for r in all_records),
            'branches':branches,'step_comparison':comparisons,'records':all_records,'forbidden_imports':forbidden,'full_cut':False,'simulator':False,'training':False}
        (folder/'audit.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items() if k not in ['branches','records']})


if __name__=='__main__':main()
