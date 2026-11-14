from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from integrated_cut import IntegratedCut,RejectedEvent
from continuous_volume import certificate
from reference import block,energy_stress
X=block(8,.0015);R=W/'runs/state';R.mkdir(exist_ok=False);checks={};results={};start=time.monotonic()
# Independently form the original fixed-point quadrature on the same fresh field.
b=IntegratedCut(X);b3=IntegratedCut(X,order=3);b7=IntegratedCut(X,order=7)
Mold=(1000*.0015**3*(b.O.T@b.O)).toarray();M=b.M.toarray()
checks['polynomial_mass_integration']=np.linalg.norm(b3.M.toarray()-M)/np.linalg.norm(M)<1e-12 and np.linalg.norm(b7.M.toarray()-M)/np.linalg.norm(M)<1e-12
b.q[:,0]+=2e-6*np.sin(b.q[:,1]*400)*np.cos(b.q[:,2]*300);b.vg[:,1]=.002*np.sin(b.q[:,0]*250);b.update_state();oldU=.0015**3*energy_stress(b.F,b.mu,b.lam)[0].sum();oldK=.5*1000*.0015**3*np.sum(b.v*b.v);new=b.metrics()
results['fresh_field_comparison']={'base_mass_matrix_relative_change':float(np.linalg.norm(M-Mold)/np.linalg.norm(Mold)),'old_sampled_energy_J':float(oldU+oldK),'new_integrated_energy_J':new['energy'],'energy_relative_change':float((new['energy']-oldU-oldK)/(oldU+oldK)),'note':'Same newly prescribed field; no old loaded checkpoint adopted'}
# Re-evaluate the exact v05 null witness with the now-complete integration.
c=IntegratedCut(X);c.commit(c.propose([-.006,.006,-.006,.006],.0003))
with np.load('/home/omen/Documents/Codex/experiments/tomato_cut_basis_20261110_v05/reports/off_grid_null_witness.npz') as z:mode=z['z'].copy()
dq=np.linalg.solve(c.T.toarray(),mode);inertia=float(dq@(c.M@dq));c.q[:,0]+=dq;c.update_state();u,f=c.energy_force(c.q)
results['old_null_witness']={'integrated_inertia_measure':inertia,'strain_energy_J':u,'sampled_max_displacement_m':float(abs(c.x-X).max()),'generalized_force_norm_N':float(np.linalg.norm(f)),'continuous_volume':certificate(c)}
checks['old_null_mode_resolved']=inertia>1e-25 and u>1e-12 and np.linalg.norm(f)>1e-6 and all(r['passed'] for r in certificate(c))
# Mechanical rest and uniform motion have no spurious self-force.
rest=IntegratedCut(X);uniform=IntegratedCut(X);uniform.vg[:]=[.02,-.01,.005];uniform.update_state();m0=uniform.metrics()
for _ in range(80):rest.step(3.90625e-7);uniform.step(3.90625e-7)
checks['rest_dynamics']=abs(rest.x-X).max()<1e-12 and abs(rest.v).max()<1e-9
checks['translation_dynamics']=abs(uniform.x-(X+uniform.time*np.array([.02,-.01,.005]))).max()<1e-10 and np.linalg.norm(uniform.metrics()['momentum']-m0['momentum'])<1e-9
results['translation']={'position_error_m':float(abs(uniform.x-(X+uniform.time*np.array([.02,-.01,.005]))).max()),'momentum_error_N_s':float(np.linalg.norm(uniform.metrics()['momentum']-m0['momentum'])),'sim_s':uniform.time}
# Insert cuts during supported load, then restore all available state/history.
fixed=X[:,1]==X[:,1].min();b=IntegratedCut(X,fixed=fixed);force=np.zeros_like(X);force[~fixed,0]=.01/(~fixed).sum();transfers=[];records={}
for name,rectangle in [('intact',None),('partial',[0,.006,-.006,.006]),('full',[-.006,.006,-.006,.006])]:
    if rectangle is not None:
        before=b.fingerprint();p=b.propose(rectangle,.0003);assert before==b.fingerprint();transfers.append(p['transfer']);b.commit(p)
    for _ in range(80):b.step(3.90625e-7,force)
    assert all(r['passed'] for r in certificate(b))
    b.save(R/(name+'.npz'));c=IntegratedCut.restore(R/(name+'.npz'))
    checks[name+'_history']=b.history==c.history and b.epoch==c.epoch and b.plane==c.plane and b.keys==c.keys and b.steps==c.steps and b.time==c.time and np.array_equal(b.fixed,c.fixed)
    for _ in range(80):b.step(3.90625e-7,force);c.step(3.90625e-7,force)
    errors={k:float(abs(getattr(b,k)-getattr(c,k)).max()) for k in ['q','vg','x','v','F','support_impulse','support_moment']};checks[name+'_restart']=max(errors.values())<1e-10;records[name]=errors
results['loaded_insertion']=transfers;results['restart_errors']=records
checks['reaction_restored']=np.linalg.norm(c.support_impulse)>1e-12
before=b.fingerprint();p=b.propose([0,.006,-.006,.006],.0003);checks['reversal_no_heal']=p['noop'] and b.fingerprint()==before
try:b.propose([-.006,.006,-.006,.006],.001);checks['capacity_rejected']=False
except RejectedEvent:checks['capacity_rejected']=b.fingerprint()==before
c=IntegratedCut(X);p=c.propose([0,.006,-.006,.006],.0003);c.step(3.90625e-7);before=c.fingerprint()
try:c.commit(p);checks['stale_rejected']=False
except RejectedEvent:checks['stale_rejected']=c.fingerprint()==before
with np.load(R/'full.npz',allow_pickle=False) as z:data={k:z[k].copy() for k in z.files}
meta=json.loads(str(data['metadata']));meta['history']=meta['history'][1:];data['metadata']=np.array(json.dumps(meta));np.savez_compressed(R/'corrupted_history.npz',**data)
try:IntegratedCut.restore(R/'corrupted_history.npz');checks['corrupt_history_rejected']=False
except ValueError:checks['corrupt_history_rejected']=True
fresh=IntegratedCut(X);checks['fresh_reset']=not fresh.history and fresh.keys==[] and fresh.plane is None and abs(fresh.x-X).max()<1e-14
results['loaded_quadrature']=[]
for name in ['intact_load','partial','full']:
    b=IntegratedCut.restore(W/'runs/dynamics'/(name+'.npz'));U,f=b.energy_force(b.q);m=b.metrics()
    for order in [3,7]:
        c=IntegratedCut(X,order=order,fixed=b.fixed)
        for event in b.history:c.commit(c.propose(event['rectangle'],event['plane']))
        c.q=b.q.copy();c.vg=b.vg.copy();c.update_state();Uc,fc=c.energy_force(c.q);mc=c.metrics()
        row={'state':name,'order':order,'energy_relative':float(abs(Uc-U)/max(abs(U),1e-12)),'force_relative':float(np.linalg.norm(fc-f)/max(np.linalg.norm(f),1e-12)),'kinetic_energy_error_J':abs(mc['kinetic_energy']-m['kinetic_energy'])}
        results['loaded_quadrature'].append(row)
        if order==7:checks[name+'_higher_order_force_energy']=row['energy_relative']<1e-6 and row['force_relative']<1e-5
        # Order three is a saved-field diagnostic, not a validated dynamic replacement.
out={'status':'pass_restricted_unit_scope' if all(checks.values()) else 'fail','checks':{k:bool(v) for k,v in checks.items()},'results':results,'wall_s':time.monotonic()-start,'scope':'No contact/fracture state exists. History is prescribed single-plane unit topology.'}
(W/'state_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2,allow_nan=False));assert all(checks.values()),checks
