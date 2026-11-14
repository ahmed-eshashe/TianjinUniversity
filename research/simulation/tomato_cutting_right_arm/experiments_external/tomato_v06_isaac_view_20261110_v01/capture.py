from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
from scipy.spatial.transform import Rotation
W=Path(__file__).parent;B=W.parent/'tomato_cut_integration_20261110_v06';sys.path.insert(0,str(B/'src'))
from integrated_cut import IntegratedCut,IntegratedBody
from reference import block
X=block(8,.0015);plane=.0003;dt=3.90625e-7;duration=.001;outputs={};start=time.monotonic()
def run(kind):
 b=IntegratedCut(X);b.commit(b.propose([0,.006,-.006,.006] if kind=='partial' else [-.006,.006,-.006,.006],plane));left=X[:,0]<plane
 if kind=='full':
  lk,rk=b.split_knots();l=IntegratedBody(lk,X[left]);r=IntegratedBody(rk,X[~left]);r.q=r.q@np.diag([1,.995,1]);rot=Rotation.from_rotvec([.1,.2,.25]).as_matrix();center=r.q.mean(0);r.q=(r.q-center)@rot.T+center+[.008,.001,0];r.vg[:]=[.02,0,0];r.update_state();b.set_full_piece_state(l,r)
 else:
  weight=np.exp(-((X[:,1]-.004)/.002)**2-(X[:,2]/.004)**2);f=np.zeros_like(X);f[~left,0]=.02*weight[~left]/weight[~left].sum();f[left,0]=-.02*weight[left]/weight[left].sum()
 qs=[b.q.copy()];ts=[0.];tic=time.monotonic()
 for i in range(round(duration/dt)):
  if kind=='partial':b.step(dt,f*np.sin(np.pi*i*dt/duration)**2,f*np.sin(np.pi*(i+1)*dt/duration)**2)
  else:b.step(dt)
  if (i+1)%64==0:qs.append(b.q.copy());ts.append(b.time)
  if time.monotonic()-tic>600:raise TimeoutError(kind)
 with np.load(B/'runs/dynamics'/(kind+'.npz'),allow_pickle=False) as old:
  errors={k:float(abs(getattr(b,k)-old[k]).max()) for k in ['q','vg','x','v','F']}
 assert max(errors.values())<1e-10,errors
 np.savez_compressed(W/(kind+'_q_frames.npz'),q=np.array(qs),t=ts,T=b.T.toarray())
 outputs[kind]={'frames':len(ts),'sim_s':duration,'wall_s':time.monotonic()-tic,'endpoint_errors':errors}
 print(kind,outputs[kind],flush=True)
 return b,np.array(qs),np.array(ts)
def surface(knots,side,partial):
 points=[];faces=[];bounds=[(float(t[0]),float(t[-1])) for t in knots];n=17
 for axis in range(3):
  for edge in [0,1]:
   spans=[list(x) for x in bounds];constant=bounds[axis][edge]
   if axis==0 and abs(constant-plane)<1e-12 and partial:spans[1][0]=0.
   other=[i for i in range(3) if i!=axis];a=np.linspace(*spans[other[0]],n);c=np.linspace(*spans[other[1]],n);aa,cc=np.meshgrid(a,c,indexing='ij');p=np.empty((n*n,3));p[:,axis]=constant;p[:,other[0]]=aa.ravel();p[:,other[1]]=cc.ravel();off=len(points);points.extend(p)
   for i in range(n-1):
    for j in range(n-1):
     v=off+i*n+j;faces.extend([[v,v+n,v+1],[v+1,v+n,v+n+1]])
 points=np.array(points);values=[BSpline(t,np.eye(len(t)-3),2)(points[:,i]) for i,t in enumerate(knots)];N=np.einsum('pi,pj,pk->pijk',*values).reshape(len(points),-1)
 return N,np.array(faces,dtype=np.int32)
saved={}
for kind in ['partial','full']:
 b,qs,ts=run(kind);lk,rk=b.split_knots();nleft=np.prod([len(t)-3 for t in lk]);refined=np.einsum('ij,tjk->tik',b.T.toarray(),qs)
 for label,knots,q in [('left',lk,refined[:,:nleft]),('right',rk,refined[:,nleft:])]:
  N,faces=surface(knots,label,kind=='partial');saved[kind+'_'+label+'_points']=np.einsum('pi,tij->tpj',N,q).astype(np.float32);saved[kind+'_'+label+'_faces']=faces
 saved['time']=ts
np.savez_compressed(W/'surfaces.npz',**saved)
result={'verified_capture':True,'source_version':'v06','runs':outputs,'total_wall_s':time.monotonic()-start,'display':'Continuous basis evaluated on tessellated surfaces, actual displacement scale. Playback slows 1ms to 10s; interpolation between recorded frames is for display only.','limits':'Prescribed unit-test cuts. Full case begins with a manufactured 8mm gap. No blade, physical fracture, tomato or robot coupling.'};(W/'capture_result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
