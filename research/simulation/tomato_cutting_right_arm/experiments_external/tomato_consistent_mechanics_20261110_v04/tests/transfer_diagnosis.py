from pathlib import Path
import sys,numpy as np,json,time
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from consistent_reference import ConsistentReference
from reference import block
b=ConsistentReference(block(8,.0015),basis="unbounded_diagnostic");A=b.W.toarray();u,s,vt=np.linalg.svd(A,full_matrices=False);rng=np.random.default_rng(89);raw=rng.normal(size=(len(A),3));null=raw-u@(u.T@raw);null*=.02/np.max(abs(null));b.initialize(velocity=null)
# Varying, fully representable velocity: full-mass projection must leave it unchanged.
c=np.column_stack([.02*np.cos(b.grid[:,1]/.003),.02*np.sin(b.grid[:,0]/.003),.01*np.cos(b.grid[:,2]/.004)]);v=A@c;proj=A@b.factor.solve(b.mass*(A.T@v));p2=A@b.factor.solve(b.mass*(A.T@proj));eig=np.linalg.eigvalsh(b.M.toarray());t=time.monotonic()
# Independent frozen-position APIC transfer, no stresses, no physical time advances.
x=b.X;ids,weights=b.ids,b.weights;grid=b.grid;r=grid[ids]-x[:,None,:];apv=v.copy();C=np.stack([g@c for g in b.G],axis=2);energies=[]
for k in range(101):
 energies.append(float(.5*b.mass*(np.sum(apv**2)+b.h*b.h/4*np.sum(C**2))))
 p=np.zeros_like(grid);m=np.zeros(len(grid));np.add.at(m,ids.ravel(),(b.mass*weights).ravel());np.add.at(p,ids.ravel(),(b.mass*weights[:,:,None]*(apv[:,None,:]+np.einsum('pij,pkj->pki',C,r))).reshape(-1,3));z=(p/m[:,None])[ids];apv=np.sum(weights[:,:,None]*z,axis=1);C=4/b.h**2*np.einsum('pk,pki,pkj->pij',weights,z,r)
res={'particle_count':b.n,'grid_count':b.ng,'mass_condition':float(eig.max()/eig.min()),'null_mode_remaining_fraction':float(np.linalg.norm(b.v)/np.linalg.norm(null)),'resolved_velocity_change':float(np.max(abs(proj-v))),'second_projection_change':float(np.max(abs(p2-proj))),'APIC_frozen_transfer_energy':energies,'APIC_energy_loss_after_100_zero_time_transfers':1-energies[-1]/energies[0],'interpretation':'Frozen-position APIC transfer alone removes energy from a non-affine but grid-representable field. Full-mass projection is idempotent on that field and filters its exact unresolved complement. This isolates transfer behavior, not complete cutting physics.'};checks={'null_filtered':res['null_mode_remaining_fraction']<1e-8,'resolved_preserved':res['resolved_velocity_change']<1e-10,'idempotent':res['second_projection_change']<1e-10};out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'result':res};(W/'transfer_diagnosis.json').write_text(json.dumps(out,indent=2));print(json.dumps({**checks,**{k:v for k,v in res.items() if not isinstance(v,list)}},indent=2))
