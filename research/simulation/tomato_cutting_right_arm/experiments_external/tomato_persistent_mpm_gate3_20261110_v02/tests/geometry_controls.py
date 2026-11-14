from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import CAD,Cells
from reference import block
R=W/'runs/geometry_complete';R.mkdir(exist_ok=False);t=time.monotonic();cad=CAD();X=block(8,.0015);codes=np.zeros(len(X),int);cells=Cells(X,codes);checks={};data={};rng=np.random.default_rng(1120)
local=rng.uniform(cad.vertices.min(0)-.003,cad.vertices.max(0)+.003,(600,3));world=local@cad.rotation.T
cpu=cad.query(world,cpu=True);gpu=cad.query(world);err=abs(cpu['phi']-gpu['phi']);checks['cad_distance']=err.max()<2e-6;checks['cad_sign']=np.all(np.sign(cpu['phi'][abs(cpu['phi'])>2e-6])==np.sign(gpu['phi'][abs(cpu['phi'])>2e-6]));data['cad_max_distance_error_m']=float(err.max());checks['affine_geometry']=cells.affine_error<1e-12 and cells.partition_error<1e-12
# Exact wrench and virtual-power adjoint for arbitrary surface loads.
angle=.47;Rot=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]]);x=X@Rot.T+[.02,.03,-.01];v=rng.normal(size=x.shape)*.01;q=cells.points(x);f=rng.normal(size=q.shape)*.001;fp=cells.pullback(f)
checks['force_pullback']=np.linalg.norm(fp.sum(0)-f.sum(0))<1e-10
checks['moment_pullback']=np.linalg.norm(np.cross(x,fp).sum(0)-np.cross(q,f).sum(0))<1e-10
checks['power_pullback']=abs((fp*v).sum()-(f*(cells.Q@v)).sum())<1e-12
# Knife flat lower edge is initially 0.3mm above the coupon top.
T=np.array([0,.0063,0]);clear=cells.certificate(X,cad,T);shallow=cells.certificate(X,cad,T-[0,.00035,0]);deep=cells.certificate(X,cad,T-[0,.00055,0]);data.update(clear=clear,shallow_50um=shallow,deep_250um=deep);checks['clear_certified']=clear['passed'];checks['shallow_certified']=shallow['passed'];checks['deep_rejected']=not deep['passed']
# Cutter endpoints are clear but a large sweep crosses the body: motion bound rejects.
large=cells.certificate(X,cad,T,motion_bound=.02);data['large_sweep']=large;checks['uncertified_large_sweep_rejected']=not large['passed']
# Exposed cut faces are generated independently for each side; open gap is retained.
cc=np.where(X[:,0]<0,1,2);split=Cells(X,cc);xx=X.copy();xx[:,0]+=.002*np.sign(X[:,0]);left=split.cell[X[:,0]<0];right=split.cell[X[:,0]>0];corn=split.C@xx;gap=float(corn[right].reshape(-1,3)[:,0].min()-corn[left].reshape(-1,3)[:,0].max());data['reconstructed_gap_m']=gap;checks['new_faces_and_gap']=len(split.boundary)>len(cells.boundary) and abs(gap-.004)<1e-10
np.savez_compressed(R/'query.npz',points=world,phi_cpu=cpu['phi'],phi_gpu=gpu['phi']);out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':data,'wall_s':time.monotonic()-t,'scope':'CAD query, conservative whole declared-cell geometry and surface force pullback; no dynamic contact pass'};(W/'geometry_controls.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
