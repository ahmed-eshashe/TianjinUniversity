exec(open(__file__.replace('search_free_stance.py','search_posture.py')).read().split('# Search an elbow')[0])
root0=k.root.copy();results=[]
for yaw in [0,45,-45,90,135,180]:
 rk=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@np.array([[1,0,0],[0,0,-1],[0,1,0]]);rh=rk@m[:3,:3].T
 def residual(q):
  tf=k.transforms(q);hand=tf[k.hand_path];el=next(t[:3,3]for n,t in tf.items()if n.endswith('_link4'));handle=(hand@m)[:3,3]+(hand@m)[:3,:3]@hc
  return np.r_[3*Rotation.from_matrix(rh@hand[:3,:3].T).as_rotvec(),3*(handle[2]-.085),.8*(el[2]-.12),.06*(q-[0,.3,0,1.3,0,0,0]),4*np.maximum(.055-el[2],0)]
 lower=k.lower.copy();upper=k.upper.copy();lower[0]=-.8;upper[0]=.8;lower[5]=-.7;upper[5]=.7
 for _ in range(12):
  k.root=root0.copy();sol=least_squares(residual,rng.uniform(lower,upper),bounds=(lower,upper),max_nfev=220)
  # Exact orientation and target height, retaining preferred posture using low regularization.
  def exact(q):
   tf=k.transforms(q);hand=tf[k.hand_path];tool=hand@m;handle=tool[:3,3]+tool[:3,:3]@hc
   return np.r_[5*Rotation.from_matrix(rh@hand[:3,:3].T).as_rotvec(),5*(handle[2]-.085),.0001*(q-sol.x)]
  fit=least_squares(exact,sol.x,bounds=(lower,upper),max_nfev=200);q=fit.x
  if np.linalg.norm(exact(q)[:4])>1e-4:continue
  tf=k.transforms(q);el=next(t[:3,3]for n,t in tf.items()if n.endswith('_link4'));tool=tf[k.hand_path]@m;handle=tool[:3,3]+tool[:3,:3]@hc
  if el[2]>.24 or el[2]<.055:continue
  shift=np.r_[np.array([.25,.04])-handle[:2],0];root=root0.copy();root[:3,3]+=shift
  overlaps=check(q,left_zero=True,root_matrix=root,hand_values={n:v for n,v in p['home_rad'].items()if 'right_rh_'in n})
  if overlaps:continue
  score=abs(el[2]-.12)+.03*np.linalg.norm(q)+.03*np.linalg.norm(shift);results.append(dict(score=score,q=q.tolist(),rotation=rk.tolist(),origin=(tool[:3,3]+shift).tolist(),handle=[.25,.04,.085],elbow=(el+shift).tolist(),yaw=yaw,root=root.tolist()));print('candidate',yaw,q,el,shift,flush=True)
results.sort(key=lambda x:x['score']);(w/'postures_free.json').write_text(json.dumps(results,indent=2));print('COUNT',len(results))
