"""One bounded full-node quasistatic normal-contact endpoint, no simulator."""
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
    p.add_argument('--case',choices=['indentation','reclosure'],required=True)
    p.add_argument('--drive-mm',type=float,required=True)
    p.add_argument('--damage',type=float,choices=[0.,.5,1.],default=0.)
    p.add_argument('--previous',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if abs(args.drive_mm)>.2:p.error('Bounded to 0.2mm coupon motion')
    if args.case=='indentation' and args.damage!=0:p.error('Indentation requires damage disabled/intact')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Offline coupled wall cap')))
    signal.alarm(55);started=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_coupled_contact import (assemble_model,supports,contact_rows,solve_contact,reduced_tangent,cut_pairs,
                                            swept_minimum_volume,proper_surface_intersections)
        directory=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design_file=directory/'surface_design.json';assignment_file=directory/'mass_stiffness_assignments.json'
        design=json.loads(design_file.read_text());assignments=json.loads(assignment_file.read_text())
        if not json.loads((directory/'summary.json').read_text())['preparation_pass']:raise ValueError('Unprepared mesh')
        points,model=assemble_model(design,assignments,args.damage);drive=args.drive_mm/1000
        fixed,back=supports(design,points,args.case,drive)
        a,b,labels=contact_rows(design,points,args.case,drive)
        previous_summary=None
        if args.previous:
            previous_summary=json.loads((args.previous/'summary.json').read_text())
            if not previous_summary['passed'] or previous_summary['case']!=args.case or previous_summary['damage']!=args.damage:raise ValueError('Invalid continuation')
            if previous_summary['design_sha256']!=hashlib.sha256(design_file.read_bytes()).hexdigest():raise ValueError('Changed continuation mesh')
            for file,digest in previous_summary['source_hashes'].items():
                if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=digest:raise ValueError('Changed continuation solver')
            if hashlib.sha256((args.previous/'positions.npy').read_bytes()).hexdigest()!=previous_summary['positions_sha256']:raise ValueError('Changed continuation state')
            initial=np.load(args.previous/'positions.npy')
        else:
            initial=points.copy()
            if args.case=='reclosure':
                initial[[n['id'] for n in design['nodes'] if n['side']=='slice'],0]+=drive
        positions,multipliers,state,trace,converged,active,fixed_ids,free=solve_contact(model,points,initial,fixed,a,b,labels)
        np.save(args.output/'positions.npy',positions)
        np.save(args.output/'multipliers.npy',multipliers)
        np.save(args.output/'fixed_reactions.npy',(state['gradient_n'].reshape(-1)-a.T@multipliers)[fixed_ids])
        gap=a@positions.reshape(-1)-b;flags=[]
        gradient=state['gradient_n'].reshape(-1);residual=gradient-a.T@multipliers
        reaction=state['gradient_n'].reshape(-1)-a.T@multipliers
        scale=max(np.linalg.norm(gradient[fixed_ids]),np.linalg.norm(a.T@multipliers),1e-4)
        force_residual=float(np.linalg.norm(residual[free])/scale)
        if not converged or force_residual>1e-6:flags.append('equilibrium_not_converged')
        if gap.min()< -1e-9:flags.append('nonpenetration_constraint_failed')
        if multipliers.min()< -1e-9:flags.append('attractive_contact_force')
        if state['min_cell_ratio']<.1 or state['min_length_ratio']<.1:flags.append('local_collapse')
        selected=[labels[i] for i in active]
        hr=reduced_tangent(state['tangent_n_m'],selected,fixed,points.size)
        reference=model.evaluate(points,tangent=True)
        href=reduced_tangent(reference['tangent_n_m'],selected,fixed,points.size)
        pre=diags(1/np.sqrt(href.diagonal()))
        least=float(eigsh(pre@hr@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=800)[0])
        if least<1e-6:flags.append('constrained_tangent_not_positive')
        pairs=cut_pairs(design)
        fixed_yz_error=float(np.max(np.abs(positions[pairs.reshape(-1),1:]-points[pairs.reshape(-1),1:])))
        if fixed_yz_error>1e-12:flags.append('matched_cut_geometry_unsupported')
        blade_force=float(sum(multipliers[i] for i,l in enumerate(labels) if l[0]=='blade'))
        cut_force=float(sum(multipliers[i] for i,l in enumerate(labels) if l[0]=='cut'))
        completeness=True
        if args.case=='indentation':
            plane=points[:,0].min()+drive;centre=design['dimensions_m'][2]/2
            included={label[1] for label in labels if label[0]=='blade'}
            for piece in design['pieces']:
                indices=np.asarray(piece['triangles']);f=positions[indices]
                near_ids=indices[np.min(f[:,:,0]-plane,axis=1)<.0001];near=positions[near_ids]
                if len(near) and (np.any(np.abs(near[:,:,1])>=.1325) or np.any(np.abs(near[:,:,2]-centre)>=.025)):completeness=False
                if any(int(i) not in included for i in near_ids.reshape(-1)):completeness=False
        if not completeness:flags.append('finite_blade_edge_contact_unsupported')
        old_drive=previous_summary['drive_mm']/1000 if previous_summary else (min(drive,-.00005) if args.case=='indentation' else drive)
        old_a,old_b,old_labels=contact_rows(design,points,args.case,old_drive)
        if labels!=old_labels:raise ValueError('Unsupported changing contact stencil')
        swept_gap=float(min(np.min(old_a@initial.reshape(-1)-old_b),gap.min()))
        if swept_gap < -1e-9:flags.append('normal_path_crossing')
        swept_j=swept_minimum_volume(model,initial,positions)
        if swept_j < .1:flags.append('swept_local_collapse')
        intersections=[]
        for fraction in [.5,1.]:
            count,candidates=proper_surface_intersections(design,initial+fraction*(positions-initial))
            intersections.append({'path_fraction':fraction,'proper_intersections':count,'candidate_pairs':candidates})
        if any(r['proper_intersections'] for r in intersections):flags.append('opposing_surface_intersection')
        external=np.asarray(a.T@multipliers).reshape(-1,3)
        external.reshape(-1)[fixed_ids]+=residual[fixed_ids]
        force_scale=max(float(np.sum(np.linalg.norm(external,axis=1))),1e-4)
        force_balance=float(np.linalg.norm(external.sum(axis=0))/force_scale)
        torque_balance=float(np.linalg.norm(np.cross(positions,external).sum(axis=0))/(force_scale*.065))
        if max(force_balance,torque_balance)>.01:flags.append('force_or_moment_balance_failed')
        work=None
        if previous_summary:
            old_reactions=np.load(args.previous/'fixed_reactions.npy');old_multipliers=np.load(args.previous/'multipliers.npy')
            support_work=float(.5*(reaction[fixed_ids]+old_reactions)@(positions.reshape(-1)[fixed_ids]-initial.reshape(-1)[fixed_ids]))
            blade_work=float(.5*(multipliers+old_multipliers)@(b-old_b))
            change=state['energy_j']-previous_summary['energy_j'];error=support_work+blade_work-change
            work={'support_work_j':support_work,'blade_work_j':blade_work,'energy_change_j':change,'residual_j':error}
            if abs(error)>.01*max(abs(state['energy_j']),abs(previous_summary['energy_j']),1e-12)+1e-12:flags.append('quasistatic_work_balance_failed')
        # Every cut triangle has the same fixed y/z projection on both sides:
        # positive vertex gaps certify the whole finite triangle, not just particles.
        cut_gap=positions[pairs[:,1],0]-positions[pairs[:,0],0]
        deformation={}
        for side in ['slice','remainder']:
            ids=[n['id'] for n in design['nodes'] if n['side']==side];u=positions[ids]-points[ids]
            deformation[side]={'max_nonrigid_displacement_m':float(np.max(np.linalg.norm(u-u.mean(axis=0),axis=1))),
                               'max_displacement_m':float(np.max(np.linalg.norm(u,axis=1)))}
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Forbidden simulator imports')
        summary={'case':args.case,'drive_mm':args.drive_mm,'damage':args.damage,'damage_evolution':False,
                 'passed':not flags,'flags':flags,'trace':trace,'force_residual':force_residual,
                 'energy_j':state['energy_j'],'barrier_energy_j':state['barrier_energy_j'],
                 'min_J':state['min_cell_ratio'],'min_spring_ratio':state['min_length_ratio'],
                 'minimum_constrained_scaled_tangent_eigenvalue':least,'min_cut_gap_m':float(cut_gap.min()),
                 'min_contact_gap_m':float(gap.min()),'min_multiplier_n':float(multipliers.min()),
                 'blade_force_n':blade_force,'cut_normal_force_n':cut_force,
                 'active_contacts':len(active),'fixed_dofs':len(fixed),'free_dofs':len(free),
                 'back_cap_driven_nodes':back,'deformation':deformation,
                 'active_interface_bonds':model.interface_bonds,'finite_blade_coverage_certificate':completeness,
                 'swept_normal_contact_min_gap_m':swept_gap,'swept_min_J':swept_j,
                 'surface_intersection_screens':intersections,'force_balance_fraction':force_balance,
                 'moment_balance_fraction':torque_balance,'work':work,
                 'positions_sha256':hashlib.sha256((args.output/'positions.npy').read_bytes()).hexdigest(),
                 'contact_scope':'supported fixed-normal facets and matched cut faces, no arbitrary rotations/slip or general CCD',
                 'design_sha256':hashlib.sha256(design_file.read_bytes()).hexdigest(),
                 'source_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'rl/tomato_coupled_contact.py',ROOT/'rl/tomato_volume_protection.py',ROOT/'rl/tomato_nonlinear_checks.py']},
                 'runtime_s':time.monotonic()-started,
                 'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                 'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},
                 'simulator_imports_or_launches':False,'training':False,'full_cut':False}
        (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps({k:summary[k] for k in ['case','drive_mm','passed','flags','force_residual','blade_force_n','cut_normal_force_n','min_J','runtime_s','peak_rss_bytes']}))


if __name__=='__main__':main()
