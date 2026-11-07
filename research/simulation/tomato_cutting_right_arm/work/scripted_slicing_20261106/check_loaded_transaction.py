from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_native_full_model import registry,configure_solver
from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
from tomato_relative_contact import RelativeSurfaceContact
from tomato_live_history_transaction import HistoryTransaction
from tomato_live_fracture_candidate import LiveFractureCandidate
wp.init();wp.set_device('cuda:0');d=registry();d['x']+=[0,0,.002];fixed=np.array(d['design']['fixture']['node_ids']);model=build_relative_model(d,fixed_nodes=fixed);h=configure_relative(configure_solver(model,d,iterations=1,solver_class=RelativeObjectiveVBD),d,board_stiffness=np.zeros(len(d['x'])));h.surface_contact=RelativeSurfaceContact(d,h.spatial_reference,margin=.0001,capacity=256);h.surface_contact.physical_colors=model.particle_colors
# A prescribed opening checks all registered patches against independent scalar
# bilinear expectations; it is NOT a blade-driven cut or a dynamics result.
x=d['x'].copy();pairs=d['pairs'];x[np.unique(pairs[:,1]),0]+=.002
mask=np.ones(h.pairs.shape[0],dtype=bool);before=h.objective_history.numpy();tx=HistoryTransaction(h,wp.array(x,dtype=wp.vec3d),mask);law=h.objective_law.numpy();expected=np.where(.002>=law[:,2],1.,np.where(.002<=law[:,1],0.,law[:,2]*(.002-law[:,1])/(.002*(law[:,2]-law[:,1]))));err=float(np.max(abs(tx.trial_history[:,1]-expected)));assert err<1e-10,err;tx.reject();assert np.array_equal(h.objective_history.numpy(),before)
s=LiveFractureCandidate(h,d,fixed,gravity=(0,0,0),maximum_outer=256);a,b=s.state(),s.state();oldx=b.particle_q.numpy();oldv=b.particle_qd.numpy();rejected=False
try:s.audited_step(a,b,1/38400,eligibility=np.zeros(len(mask),dtype=bool),acceptance_audit=lambda *args:False)
except ValueError as e:rejected='failed external acceptance audit' in str(e)
assert rejected and np.array_equal(oldx,b.particle_q.numpy())and np.array_equal(oldv,b.particle_qd.numpy())and np.array_equal(before,h.objective_history.numpy())
def audit(start,end,old,new,eligible,dt):
 return bool(np.isfinite(end.particle_q.numpy()).all() and np.array_equal(old,new) and not eligible.any())
s.audited_step(a,b,1/38400,eligibility=np.zeros(len(mask),dtype=bool),acceptance_audit=audit)
# Explicit prepared-opening mechanics control, not blade-generated damage.
cap=np.unique(d['cells'][d['x'][d['cells']].mean(1)[:,0]<d['design']['cut_x_m']]);opened=d['x'].copy();opened[cap,0]-=.002;a.particle_q.assign(opened);a.particle_qd.zero_();h.objective_history.zero_();h.history.zero_()
def loaded_audit(start,end,old,new,eligible,dt):
 xx=end.particle_q.numpy();ratios=np.linalg.det(xx[d['cells'][:,1:]]-xx[d['cells'][:,:1]])/(6*d['volumes'])
 return bool(np.isfinite(xx).all()and ratios.min()>.1 and np.all(new>=old)and np.all(new[:,1]>0))
try:s.audited_step(a,b,1/38400,eligibility=np.ones(len(mask),dtype=bool),acceptance_audit=loaded_audit)
except BaseException:
 Path(__file__).with_name('loaded_failure_iterations.json').write_text(json.dumps(s.last_trace,indent=2));raise
result=dict(patch_count=len(mask),loaded_prepared_opening_step=True,history_min=float(h.objective_history.numpy()[:,1].min()),history_max=float(h.objective_history.numpy()[:,1].max()),cutting=False,contact_eligibility_tested=False,work_qualified=False);Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2));print(result)
