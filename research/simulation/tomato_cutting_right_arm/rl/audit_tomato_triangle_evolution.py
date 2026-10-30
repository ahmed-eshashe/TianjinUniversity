"""Independent recomputation of a saved evolving triangle-contact endpoint."""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from scipy.sparse import diags
        from scipy.sparse.linalg import eigsh
        from tomato_bonds import DamageState
        from tomato_coupled_contact import assemble_model,cut_pairs,supports,swept_minimum_volume,proper_surface_intersections
        from tomato_blade_damage import EvolvingCohesion,edge_history,contact_eligibility,BLADE
        from tomato_triangle_contact import triangle_geometry,blade_resistance,nodal_blade_multipliers,swept_triangle_gap
        from tomato_linear_contact import affine_space
        from tomato_full_cut_checks import material_components
        from audit_tomato_triangle_contact import minimum_polygon_gap
        def read(folder):
            s=json.loads((folder/'summary.json').read_text());assert s['passed'] and s['backend']=='triangle_evolving_v1'
            for name,h in s['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
            for name,h in s['state_hashes'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==h
            return s,np.load(folder/'positions.npy'),np.load(folder/'multipliers.npy'),np.load(folder/'edge_hits.npy')
        s,x,lam,hits=read(a.checkpoint);source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        previous=None;initial=points.copy();oldhits=np.zeros(len(pairs),dtype=bool);oldtip=float(points[pairs[:,0],2].max());committed=list(model.cohesion.states)
        if s['previous_checkpoint']:
            folder=ROOT/s['previous_checkpoint'];previous,initial,oldlam,oldhits=read(folder)
            assert hashlib.sha256((folder/'summary.json').read_bytes()).hexdigest()==s['previous_summary_sha256']
            oldtip=previous['tip_z_m'];committed=[DamageState(**v) for v in previous['damage_states']]
        flags=[];tip=float(points[pairs[:,0],2].max())-s['depth_mm']/1000
        if abs(tip-s['tip_z_m'])>1e-12:flags.append('blade_tip')
        if not np.array_equal(hits,edge_history(points,pairs,oldtip,tip,oldhits)):flags.append('edge_history')
        states=[DamageState(**v) for v in s['damage_states']];model.cohesion.states=states;state=model.evaluate(x,tangent=True)
        geometry=triangle_geometry(design,points,pairs,tip);C,b=geometry['matrix'],geometry['bounds'];nodal=nodal_blade_multipliers(geometry,pairs,lam)
        eligible=contact_eligibility(model.cohesion,hits,nodal,geometry['widths']);trial=model.cohesion.trial_states(x,committed,eligible)
        if np.flatnonzero(eligible).tolist()!=s['eligible_patches']:flags.append('eligibility')
        if max(max(abs(v.damage-w.damage),abs(v.kappa_m-w.kappa_m)) for v,w in zip(states,trial))>1e-9:flags.append('damage_consistency')
        if any(v.damage<w.damage or v.kappa_m<w.kappa_m for v,w in zip(states,committed)):flags.append('healing')
        fixed,_=supports(design,points,'indentation',0.);ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(x.size),ids)
        g=state['gradient_n'].ravel();residual=g-C.T@lam;scale=max(np.linalg.norm(g[ids]),np.linalg.norm(C.T@lam),1e-4)
        force=float(np.linalg.norm(residual[free])/scale);polygon_gap,count=minimum_polygon_gap(design,x,tip,BLADE)
        gap=C@x.ravel()-b;comp=float(np.max(np.abs(lam*gap)));cutgap=float(np.min(x[pairs[:,1],0]-x[pairs[:,0],0]))
        pathgap=swept_triangle_gap(design,points,pairs,initial,x,oldtip,tip)
        if force>1e-6:flags.append('equilibrium')
        if min(float(gap.min()),polygon_gap,cutgap,pathgap)<-1e-9 or lam.min()<-1e-9 or comp>1e-10:flags.append('contact')
        if np.max(np.abs(lam[~geometry['active']]),initial=0.)>0:flags.append('inactive_load')
        if np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids])))>1e-12:flags.append('supports')
        if np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:]))>1e-12:flags.append('projection')
        R=blade_resistance(geometry,x,lam);work=0.
        if previous:
            oldgeometry=triangle_geometry(design,points,pairs,oldtip);oldR=blade_resistance(oldgeometry,initial,oldlam)
            work=.5*(oldR+R)*(oldtip-tip)
        diss=model.cohesion.dissipation(states);old_diss=model.cohesion.dissipation(committed)
        cumulative=(previous['cumulative_blade_work_j'] if previous else 0.)+work
        error=cumulative-state['energy_j']-diss;normalizer=max(abs(cumulative),state['energy_j']+diss,1e-12)
        incerror=work-(state['energy_j']-(previous['energy_j'] if previous else 0.))-(diss-old_diss)
        if abs(error)>.01*normalizer+1e-12:flags.append('work_balance')
        if abs(incerror)>.01*max(abs(work),state['energy_j'],previous['energy_j'] if previous else 0.,diss-old_diss,1e-12)+1e-12:flags.append('increment_work')
        for name,v in [('energy_j',state['energy_j']),('fracture_dissipation_j',diss),('blade_resistance_n',R),('increment_blade_work_j',work),('cumulative_blade_work_j',cumulative)]:
            if abs(s[name]-v)>1e-10:flags.append('recomputation_'+name)
        J=swept_minimum_volume(model,initial,x)
        if J<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        screens=[proper_surface_intersections(design,initial+t*(x-initial))[0] for t in [.5,1.]]
        if any(screens):flags.append('surface_intersection')
        triangles=np.array([t for piece in design['pieces'] for t in piece['triangles']]);rest=points[triangles];faces=x[triangles]
        rn=np.cross(rest[:,1]-rest[:,0],rest[:,2]-rest[:,0]);nn=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);ra=np.linalg.norm(rn,axis=1);na=np.linalg.norm(nn,axis=1)
        if np.min(na/ra)<=0 or np.min(np.einsum('ni,ni->n',nn,rn)/(na*ra))<=0:flags.append('surface_orientation')
        external=np.asarray(C.T@lam).reshape(-1,3);external.ravel()[ids]+=residual[ids];fscale=max(float(np.linalg.norm(external,axis=1).sum()),1e-4)
        if max(float(np.linalg.norm(external.sum(axis=0))/fscale),float(np.linalg.norm(np.cross(x,external).sum(axis=0))/(fscale*.065)))>.01:flags.append('force_moment_balance')
        algorithmic=model.cohesion.algorithmic_tangent(x,state['tangent_n_m'],committed,eligible)
        strong=np.flatnonzero(lam>1e-9);_,T=affine_space(C[strong],b[strong],fixed,points.size)
        H=T.T@algorithmic@T;ref=T.T@model.evaluate(points,tangent=True)['tangent_n_m']@T;pre=diags(1/np.sqrt(ref.diagonal()))
        least=float(eigsh(pre@H@pre,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=1600,ncv=80)[0])
        if least<1e-6:flags.append('softening_stability')
        topology=material_components(design,assign,[p['indices'] for p in model.cohesion.patches],[v.damage for v in states],pairs)
        if topology!=s['topology']:flags.append('topology_recomputation')
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result={'passed':not flags,'flags':flags,'checkpoint':str(a.checkpoint),'depth_mm':s['depth_mm'],'force_residual':force,'independent_polygon_minimum_gap_m':polygon_gap,
            'polygon_vertices':count,'minimum_cut_gap_m':cutgap,'minimum_swept_blade_gap_m':pathgap,'complementarity_n_m':comp,'swept_min_J':J,
            'minimum_softening_stability_eigenvalue':least,'energy_j':state['energy_j'],'fracture_dissipation_j':diss,'cumulative_blade_work_j':cumulative,'relative_energy_residual':abs(error)/normalizer,
            'damage_unchanged_or_irreversible':'healing' not in flags,'topology':topology,'runtime_s':time.monotonic()-start,'forbidden_imports':forbidden,'full_cut':False,'simulator':False,'training':False}
        a.output.write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
