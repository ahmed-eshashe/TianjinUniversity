from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import Cells
from reference import block
from volume_guard import certificate
X=block(8,.0015);g=Cells(X,np.zeros(len(X),int));checks={};res={};theta=.71;R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
for name,F,expect in [('identity',np.eye(3),True),('rotation',R,True),('affine_compression',np.diag([1,.5,1]),True),('collapsed',np.diag([1,.05,1]),False),('inverted',np.diag([1,-1,1]),False)]:
 r=certificate(g,X@F.T+[.02,.03,-.01]);res[name]=r;checks[name]=r['passed']==expect
cut=np.load(W/'runs/paid_cut/final.npz');res['saved_bad_cut']=certificate(g,cut['x']);checks['saved_bad_cut_rejected']=not res['saved_bad_cut']['passed']
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':res,'scope':'Conservative Jacobian certificate of the declared trilinear material geometry; not correction of the failed bulk/contact update'};(W/'volume_controls.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
