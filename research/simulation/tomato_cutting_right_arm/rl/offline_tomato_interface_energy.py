"""Bounded fracture-energy regression for the revised 47 surface patches."""
import argparse,fcntl,json,resource,signal,sys,time
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['opening','shear_y','shear_y_negative','shear_z','shear_z_negative'],required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    started=time.monotonic()
    root=Path(__file__).resolve().parents[1]
    with (root/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_surface_cohesion import SurfaceCohesion,patch_response,update_surface_damage
        from tomato_coupled_contact import cut_pairs
        from tomato_bonds import DamageState
        design=json.loads((root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text())
        model=SurfaceCohesion(design,cut_pairs(design),0.)
        axis=0 if args.mode=='opening' else (1 if 'shear_y' in args.mode else 2)
        direction=np.zeros(3);direction[axis]=-1 if 'negative' in args.mode else 1
        records=[]
        for patch in model.patches:
            law=patch['law'];matrix=patch['stiffness'];weights=patch['weights'];n=len(weights)
            ratio=float(np.sqrt(direction@matrix@direction/law.stiffness_n_m))
            state=DamageState();work=0.;dissipation=0.;previous_force=0.;previous_delta=0.
            for q in np.linspace(0,1.5*law.failure_m,2401):
                delta=float(q/ratio);gaps=np.tile(delta*direction,(n,1))
                new=update_surface_damage(law,state,gaps,weights,matrix,eligible=True)
                undamaged=patch_response(gaps,weights,matrix,0.)
                dissipation+=(new.damage-state.damage)*undamaged['energy_j']
                response=patch_response(gaps,weights,matrix,new.damage)
                force=float(response['gradient_n'].sum(axis=0)@direction)
                work+=.5*(force+previous_force)*(delta-previous_delta)
                state=new;previous_force=force;previous_delta=delta
            target=law.area_m2*law.fracture_energy_j_m2
            record={'patch':patch['id'],'target_j':target,'work_j':work,'fixed_geometry_damage_loss_j':dissipation,
                    'work_relative_error':abs(work/target-1),'damage_loss_relative_error':abs(dissipation/target-1),
                    'final_damage':state.damage,'final_force_n':previous_force}
            record['passed']=max(record['work_relative_error'],record['damage_loss_relative_error'])<.01 and state.damage==1 and previous_force==0.
            records.append(record)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result={'mode':args.mode,'patches':47,'passed':all(r['passed'] for r in records),'max_work_relative_error':max(r['work_relative_error'] for r in records),
                'max_damage_loss_relative_error':max(r['damage_loss_relative_error'] for r in records),'records':records,'forbidden_imports':forbidden,'runtime_s':time.monotonic()-started,
                'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,
                'limits':{'address_space_bytes':512*1024**2,'cpu_s':45,'wall_s':55,'shared_lock':True,'blas_threads':1}}
        args.output.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='records'})
        if not result['passed']:raise ValueError('1% fracture energy gate failed')


if __name__=='__main__':main()
