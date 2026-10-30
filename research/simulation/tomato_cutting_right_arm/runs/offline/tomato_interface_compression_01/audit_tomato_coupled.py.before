"""Bounded evidence audit of full-node normal-contact coupons."""
import fcntl
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys


def main():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    root=Path(__file__).resolve().parents[1];folder=root/'runs/offline/tomato_coupled_01'
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_coupled_contact import supports
        from offline_tomato_patch_sweep import patch_data
        from tomato_bonds import DamageState,bundle_response
        source=root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text())
        rest_points=np.asarray([n['position_m'] for n in design['nodes']])
        faces=np.asarray([tri for piece in design['pieces'] for tri in piece['triangles']])
        p0=rest_points[faces];rest_normals=np.cross(p0[:,1]-p0[:,0],p0[:,2]-p0[:,0])
        rest_areas=np.linalg.norm(rest_normals,axis=1);area_min=1.;normal_cos_min=1.
        earlier=json.loads((root/'runs/offline/tomato_slice_refinement_01/cases_half_spacing/bulk5_slice_compression_x/summary.json').read_text())
        inputs={}
        for file in [source/'surface_design.json',source/'mass_stiffness_assignments.json']:
            key=str(file.relative_to(root));digest=hashlib.sha256(file.read_bytes()).hexdigest()
            assert earlier['source_hashes'][key]==digest
            inputs[key]=digest
        (folder/'input_provenance.json').write_text(json.dumps(inputs,indent=2)+'\n')
        expected={'indent_coarse':7,'indent_fine':13,'reclose_broken':13,'reclose_broken_fine':25,'reclose_intact':5,'reclose_partial':5}
        sequences={};all_states=[];rigid_removed={}
        for name,count in expected.items():
            files=sorted((folder/name).glob('*/summary.json'));assert len(files)==count,(name,len(files))
            entries=[json.loads(p.read_text()) for p in files]
            assert all(e['passed'] for e in entries),name
            for p,e in zip(files,entries):
                assert hashlib.sha256((p.parent/'positions.npy').read_bytes()).hexdigest()==e['positions_sha256']
                for source,digest in e['source_hashes'].items():assert hashlib.sha256((root/source).read_bytes()).hexdigest()==digest
                positions=np.load(p.parent/'positions.npy');f=positions[faces]
                normals=np.cross(f[:,1]-f[:,0],f[:,2]-f[:,0]);areas=np.linalg.norm(normals,axis=1)
                area_min=min(area_min,float(np.min(areas/rest_areas)))
                normal_cos_min=min(normal_cos_min,float(np.min(np.einsum('ni,ni->n',normals,rest_normals)/(areas*rest_areas))))
                assert np.all(areas>0) and np.all(np.einsum('ni,ni->n',normals,rest_normals)>0)
            all_states+=entries;sequences[name]=(files,entries)
            peak=max(range(len(entries)),key=lambda i:entries[i]['drive_mm'])
            current=np.load(files[peak].parent/'positions.npy');rigid_removed[name]={}
            for side in ['slice','remainder']:
                ids=[n['id'] for n in design['nodes'] if n['side']==side]
                p=rest_points[ids];q=current[ids];pc=p-p.mean(axis=0);qc=q-q.mean(axis=0)
                u,_,vt=np.linalg.svd(pc.T@qc);rotation=u@vt
                if np.linalg.det(rotation)<0:u[:,-1]*=-1;rotation=u@vt
                residual=qc-pc@rotation
                rigid_removed[name][side]=float(np.max(np.linalg.norm(residual,axis=1)))
        comparisons={}
        for coarse,fine in [('indent_coarse','indent_fine'),('reclose_broken','reclose_broken_fine')]:
            ac=sequences[coarse][1];af=sequences[fine][1]
            field='blade_force_n' if coarse.startswith('indent') else 'cut_normal_force_n'
            def keyed(entries):
                peak=max(range(len(entries)),key=lambda i:entries[i]['drive_mm'])
                return {(i<=peak,round(e['drive_mm'],6)):e for i,e in enumerate(entries)}
            a,b=keyed(ac),keyed(af);errors=[]
            for key,x in a.items():
                y=b[key]
                if max(abs(x[field]),abs(y[field]))>1e-8:errors.append(abs(x[field]/y[field]-1))
                else:assert abs(x[field]-y[field])<1e-9
            def loading_work(entries):
                peak=max(range(len(entries)),key=lambda i:entries[i]['drive_mm'])
                return sum(e['work']['support_work_j']+e['work']['blade_work_j'] for e in entries[1:peak+1])
            wa,wb=loading_work(ac),loading_work(af)
            comparisons[coarse]={'matched_force_max_relative_change':max(errors),'coarse_loading_work_j':wa,
                                 'fine_loading_work_j':wb,'loading_work_relative_change':abs(wa/wb-1)}
            assert max(max(errors),abs(wa/wb-1))<.1
        points=np.asarray([n['position_m'] for n in design['nodes']]);compression=[]
        for name in ['reclose_intact','reclose_partial','reclose_broken']:
            files,entries=sequences[name];index=max(range(len(entries)),key=lambda i:entries[i]['drive_mm']);e=entries[index]
            positions=np.load(files[index].parent/'positions.npy');energy=0.;force=0.
            for patch in design['interface_patches']:
                rest,k,law=patch_data(design,patch);current=[]
                for bid in patch['bond_ids']:
                    i,j=design['bonds'][bid]['nodes']
                    if design['nodes'][i]['side']=='remainder':i,j=j,i
                    current.append(positions[j]-positions[i])
                response=bundle_response(rest,current,k,[0.]*len(k),DamageState(damage=e['damage']))
                energy+=response['stored_energy_j'];force+=response['force_n'][0]
            fixed,back=supports(design,points,'reclosure',e['drive_mm']/1000)
            ids=sorted(fixed);reaction=np.load(files[index].parent/'fixed_reactions.npy');lookup={key:i for i,key in enumerate(ids)}
            back_force=float(sum(reaction[lookup[3*i]] for i in back))
            compression.append({'sequence':name,'damage':e['damage'],'back_cap_actuator_force_n':back_force,
                                'cut_contact_force_n':e['cut_normal_force_n'],'cohesive_force_on_slice_x_n':force,
                                'cohesive_elastic_energy_j':energy,'total_elastic_energy_j':e['energy_j'],
                                'compression_load_fraction_via_cohesion':max(0.,-force)/max(abs(back_force),1e-12),
                                'slice_force_balance_fraction':abs(back_force+force-e['cut_normal_force_n'])/max(abs(back_force),1e-4)})
        summary={'sequences':{key:len(value[1]) for key,value in sequences.items()},'checked_endpoints':len(all_states),
                 'all_endpoints_passed':True,'load_increment_comparisons':comparisons,'compression_branch_audit':compression,
                 'peak_rigid_motion_removed_displacement_m':rigid_removed,
                 'minimum_J':min(e['min_J'] for e in all_states),'minimum_swept_J':min(e['swept_min_J'] for e in all_states),
                 'max_force_residual':max(e['force_residual'] for e in all_states),
                 'minimum_constrained_scaled_tangent_eigenvalue':min(e['minimum_constrained_scaled_tangent_eigenvalue'] for e in all_states),
                 'max_penetration_m':max(0.,-min(e['swept_normal_contact_min_gap_m'] for e in all_states)),
                 'proper_surface_intersections':sum(s['proper_intersections'] for e in all_states for s in e['surface_intersection_screens']),
                 'minimum_surface_area_ratio':area_min,'minimum_surface_normal_cosine':normal_cos_min,
                 'max_force_balance_fraction':max(e['force_balance_fraction'] for e in all_states),
                 'max_moment_balance_fraction':max(e['moment_balance_fraction'] for e in all_states),
                 'runtime_s':sum(e['runtime_s'] for e in all_states),'max_worker_runtime_s':max(e['runtime_s'] for e in all_states),
                 'peak_worker_rss_bytes':max(e['peak_rss_bytes'] for e in all_states),
                 'damage_evolution':False,'full_cut_tested':False,'general_3d_contact_validated':False,
                 'simulator_imports_or_launches':False,'training':False}
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        (folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
