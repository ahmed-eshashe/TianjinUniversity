from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference import block
from contact_geometry import CAD,Cells
from contact_law import evaluate
from fragment_contact import FragmentContact
from scipy.sparse.linalg import eigsh
X=block(8,.0015);codes=np.where(X[:,0]<0,1,2);cells=Cells(X,codes);x=X.copy();x[:,0]-=1e-6*np.sign(X[:,0]);c=FragmentContact(cells,x,X[:,0]<0,X[:,0]>0);q=c.QA@x;ev=c.surface.query(q);B=c.surface.matrix(ev);D=c.QA-B;S=D.T@D.multiply((c.K*c.area)[:,None]);largest=float(eigsh(S,k=1,which='LM',return_eigenvectors=False)[0]);omega=np.sqrt(largest/(1000*.0015**3));dt_bound=.025/omega
print('spectral',omega,'bound',dt_bound,flush=True)
cut=np.load(W/'runs/paid_cut/final.npz');dt=1.25e-5;t=float(cut['sim_time']);T=np.array([0,.00605-.0016*.5*(1-np.cos(np.pi*t/.05)),0]);cad=CAD();r=[]
for qs in [.00025,.000125,.0000625]:
 g=Cells(X,np.zeros(len(X),int),qspacing=qs);pts=g.points(cut['x']);v=g.Q@cut['v'];query=cad.query(pts,T);law=evaluate(query['phi'],query['normal'],v,g.area);r.append({'spacing':qs,'points':len(pts),'peak_sample_penetration_m':float(max(0,-query['phi'].min())),'force_N':float(np.linalg.norm(law['force'].sum(0))),'active':int((query['phi']<0).sum()),'edge_active':int(((query['phi']<0)&(query['kind']==1)).sum())});print(r[-1],flush=True)
out={'recontact_full_face_linearized_omega_rad_s':omega,'existing_dt_times_omega':omega*1.25e-5,'accuracy_step_bound_for_dt_omega_0_025':dt_bound,'cut_final_time_s':t,'quadrature_diagnosis':r};(W/'reports/contact_resolution_diagnosis.json').write_text(json.dumps(out,indent=2))
