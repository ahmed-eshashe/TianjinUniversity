"""Read-only geometric path fit. No material simulation or eligibility mutation.
Uses the production CCD and inward-face condition, omitting current-volume
coverage because only prospective first edge encounters are assessed here.
"""
exec(open(str(__import__('pathlib').Path(__file__).parent/'check_lateral_edge_coverage.py')).read().split('rows=[]')[0])
R0=Rotation.from_quat(pose[3:]).as_matrix();heel=np.array([-.02028,.03,.00105]);local=(heel-pose[:3])@R0
coef=np.load(w/'interface_polynomial_fit.npy');material=e._geometry(world,pose)[1]
def count(poses):
 seen=z['seen'].copy();f0=e._geometry(world,poses[0])[0]
 for p in poses[1:]:
  f1=e._geometry(world,p)[0]
  for row in e.detector.detect(f0,f1,material,material,reg['patch'])['events']:
   i=row['front_face_index'];good=True
   for tri in [f0[i],f1[i]]:
    n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n)
    good=good and np.min((f1[i]-f0[i])@n)>1e-12
   if good:seen[int(row['patch'])]=True
  f0=f1
 return seen
best=None;rows=[]
for amplitude in [.001,.0015,.002,.0025]:
 for phase in [0,np.pi/2,np.pi,3*np.pi/2]:
  slope=0.;rot=Rotation.from_euler('z',np.arctan(slope))*Rotation.from_matrix(R0);poses=[]
  for h in np.linspace(.035,.0015,269):
   hm=h*1000;hf=min(hm,15);a,b,c,_,_=coef;intercept=a+b*hf+c*hf*hf+(hm-hf)*(b+2*c*hf)
   wave=amplitude*np.clip((.015-h)/.003,0,1)*np.sin(2*np.pi*(h-.0015)/.004+phase)
   center=np.array([intercept/1000+wave,0,h]);poses.append(np.r_[center-rot.as_matrix()@local,rot.as_quat()])
  seen=count(poses);row=dict(slope=slope,amplitude_m=amplitude,phase=phase,seen=int(seen.sum()),missing=np.flatnonzero(~seen).tolist());rows.append(row);print(row,flush=True)
  if best is None or row['seen']>best['seen']:best=dict(**row,poses=np.asarray(poses).tolist())
  if seen.all():break
 if best['seen']==47:break
(w/'front_reachable_path_fit.json').write_text(json.dumps(dict(scope=__doc__,rows=rows,best=best),indent=2))
