"""Conservative unilateral stability audit, allowing weak contacts to open."""
import fcntl
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
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_coupled_contact import assemble_model,supports,contact_rows,reduced_tangent
        source=root/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assignments=json.loads((source/'mass_stiffness_assignments.json').read_text())
        models={};records=[]
        for name in ['indent_coarse','indent_fine','reclose_broken','reclose_broken_fine','reclose_intact','reclose_partial']:
            for file in sorted((folder/name).glob('*/summary.json')):
                summary=json.loads(file.read_text());assert summary['passed']
                damage=summary['damage']
                if damage not in models:
                    points,model=assemble_model(design,assignments,damage)
                    models[damage]=(points,model,model.evaluate(points,tangent=True)['tangent_n_m'])
                points,model,reference=models[damage];positions=np.load(file.parent/'positions.npy')
                multipliers=np.load(file.parent/'multipliers.npy')
                fixed,_=supports(design,points,summary['case'],summary['drive_mm']/1000)
                _,_,labels=contact_rows(design,points,summary['case'],summary['drive_mm']/1000)
                # Only strictly compressive contacts restrict the critical space.
                # Ignoring weak contacts permits their opening, conservatively.
                selected=[labels[i] for i in np.flatnonzero(multipliers>1e-9)]
                h=reduced_tangent(model.evaluate(positions,tangent=True)['tangent_n_m'],selected,fixed,points.size)
                ref=reduced_tangent(reference,selected,fixed,points.size)
                pre=diags(1/np.sqrt(ref.diagonal()))
                value=float(eigsh(pre@h@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=800)[0])
                record={'summary':str(file.relative_to(root)),'strong_contact_count':len(selected),'minimum_scaled_eigenvalue':value,'passed':value>=1e-6}
                records.append(record)
                (folder/'unilateral_stability_partial.json').write_text(json.dumps(records,indent=2)+'\n')
                if value<1e-6:raise ValueError('Unilateral stability screen failed')
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result={'checked_endpoints':len(records),'all_passed':all(r['passed'] for r in records),
                'minimum_scaled_eigenvalue':min(r['minimum_scaled_eigenvalue'] for r in records),
                'weak_contact_force_threshold_n':1e-9,'records':records,'forbidden_imports':forbidden}
        (folder/'unilateral_stability.json').write_text(json.dumps(result,indent=2)+'\n')
        print({k:v for k,v in result.items() if k!='records'})


if __name__=='__main__':main()
