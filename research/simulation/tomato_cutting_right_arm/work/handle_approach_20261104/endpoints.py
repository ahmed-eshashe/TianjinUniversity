exec(open(__file__.replace('endpoints.py','build.py')).read().split("scene=w/")[0])
blade=np.array(json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())['vertices']);target=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz')['x'];center=(target.min(0)+target.max(0))/2;seed=np.array([closed[n]for n in k.names]);res=[]
for yaw in [0,20,45,60,90,-20]:
 rot=Rotation.from_euler('z',yaw,degrees=True).as_matrix()@np.array([[1.,0,0],[0,0,-1],[0,1,0]]);bc=np.mean(blade@rot.T,axis=0);origin=np.array([center[0]-bc[0],center[1]-bc[1],target[:,2].max()+.04-min((blade@rot.T)[:,2])]);hr=rot@m[:3,:3].T;pos=origin-hr@m[:3,3]+hr@PALM_OFFSET
 for q0 in [seed]+[rng.uniform(k.lower,k.upper)for _ in range(15)]:
  q,e,a=k.solve(pos,hr,q0)
  if e<2e-5 and a<2e-4:res.append(dict(yaw=yaw,q=q.tolist(),score=float(np.linalg.norm(q-seed)),origin=origin.tolist(),rotation=rot.tolist()));print('found',yaw,np.linalg.norm(q-seed),flush=True)
res.sort(key=lambda x:x['score']);(w/'endpoints.json').write_text(json.dumps(res,indent=2));print('count',len(res))
