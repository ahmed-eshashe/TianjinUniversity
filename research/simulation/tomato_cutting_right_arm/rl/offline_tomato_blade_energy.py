"""Bounded surface-law wedge/elastic-support energy references, not full cuts."""
import argparse,fcntl,json,resource,signal,sys,time
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--count',type=int,default=8)
    p.add_argument('--steps',type=int,choices=[2400,4800],required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.start<0 or not 1<=args.count<=8 or args.start+args.count>47:p.error('At most eight of 47 patches')
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    root=Path(__file__).resolve().parents[1]
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_bonds import DamageState
        from tomato_coupled_contact import cut_pairs
        from tomato_surface_cohesion import SurfaceCohesion,patch_response,update_surface_damage
        from tomato_blade_damage import BLADE,fracture_loss
        from tomato_contact_reference import edge_hits_site
        design=json.loads((root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        model=SurfaceCohesion(design,cut_pairs(design),0.);records=[]
        for patch in model.patches[args.start:args.start+args.count]:
            law=patch['law'];weights=patch['weights'];K=patch['stiffness'];n=len(weights)
            site=design['interface_patches'][patch['id']]['anchor_yz_m'];z=site[1]
            state=DamageState();oldq=0.;oldforce=0.;work=0.;toolwork=0.;fixed_loss=0.;peak=0.;hit=False
            # Stabilizing supported local reference, NOT a bulk-model retuning.
            bulkK=.5*law.stiffness_n_m
            path=np.r_[np.linspace(0,.006,args.steps+1),np.linspace(.006,0,args.steps+1)[1:]]
            for q in path:
                depth=q*BLADE['single_bevel_length_m']/BLADE['max_thickness_m']
                oldtip=z-oldq*BLADE['single_bevel_length_m']/BLADE['max_thickness_m']
                tip=z-depth;hit=hit or edge_hits_site(site,oldtip,tip,BLADE)
                gaps=np.tile([q,0.,0.],(n,1))
                before=patch_response(gaps,weights,K,state.damage)
                reaction=bulkK*q+before['gradient_n'][:,0].sum()
                eligible=hit and q>0 and reaction>1e-9
                new=update_surface_damage(law,state,gaps,weights,K,eligible=eligible)
                after=patch_response(gaps,weights,K,new.damage)
                force=float(bulkK*q+after['gradient_n'][:,0].sum())
                work+=.5*(oldforce+force)*(q-oldq)
                slope=BLADE['max_thickness_m']/BLADE['single_bevel_length_m']
                toolwork+=.5*(oldforce+force)*slope*(oldtip-tip)
                fixed_loss+=before['energy_j']-after['energy_j']
                peak=max(peak,force*BLADE['max_thickness_m']/BLADE['single_bevel_length_m'])
                state=new;oldq=float(q);oldforce=force
            target=law.area_m2*law.fracture_energy_j_m2;exact=fracture_loss(law,state)
            record={'patch':patch['id'],'steps':args.steps,'damage':state.damage,'edge_hit':hit,
                'opening_work_j':work,'blade_work_j':toolwork,'virtual_work_error_j':toolwork-work,'final_stored_energy_j':after['energy_j']+.5*bulkK*oldq**2,
                'exact_fracture_dissipation_j':exact,'explicit_fixed_geometry_loss_j':fixed_loss,
                'target_fracture_energy_j':target,'relative_work_error':abs(work/target-1),
                'relative_explicit_loss_error':abs(fixed_loss/target-1),'peak_vertical_blade_reaction_n':peak,
                'final_contact_force_n':force,'damage_healing':False}
            record['passed']=bool(state.damage==1 and abs(work-exact)<.01*target+1e-12 and abs(exact-target)<1e-12 and force==0. and abs(fixed_loss/target-1)<.01 and abs(toolwork-work)<1e-12)
            records.append(record)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        summary={'passed':all(r['passed'] for r in records),'records':records,'forbidden_imports':forbidden,
            'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
            'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1},'full_cut':False}
        args.output.write_text(json.dumps(summary,indent=2)+'\n');print(args.start,args.steps,summary['passed'],summary['runtime_s'])
        if not summary['passed']:raise ValueError('Blade/fracture work gate failed')


if __name__=='__main__':main()
