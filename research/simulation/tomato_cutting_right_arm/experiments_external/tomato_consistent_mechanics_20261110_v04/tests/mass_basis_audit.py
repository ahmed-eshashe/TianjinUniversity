from pathlib import Path
import numpy as np,json
from scipy.interpolate import BSpline
W=Path(__file__).resolve().parents[1];records=[]
for n in [8,40]:
 h=.003;s=.0015;L=n*s;x=(np.arange(n)-(n-1)/2)*s;a=-L/2;b=L/2;t=np.r_[np.repeat(a,3),np.arange(a+h,b-h/2,h),np.repeat(b,3)];nb=len(t)-3;basis=BSpline(t,np.eye(nb),2);A=basis(x);G=basis.derivative()(x);q=np.array([np.mean(t[i+1:i+3]) for i in range(nb)]);B=A.T@A;D=G.T@G;inv=np.linalg.inv(B);from scipy.linalg import eigh
 eig=eigh(D,B,eigvals_only=True);records.append({'particles_axis':n,'basis_axis':nb,'mass_cond_1d':np.linalg.cond(B),'mass_cond_3d':np.linalg.cond(B)**3,'partition_error':abs(A.sum(1)-1).max(),'linear_error':abs(A@q-x).max(),'derivative_error':abs(G@q-1).max(),'max_1d_laplacian_eigen':eig.max(),'acoustic_estimate_critical_dt':2/np.sqrt(3*eig.max()*(100000*(1-.4)/((1+.4)*(1-2*.4)))/1000)})
(W/'mass_basis_audit.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
