exec(open(__file__.replace('search.py','build.py')).read().split('rng=np.random')[0])
target=k.transforms(q0)[k.hand_path];rng=np.random.default_rng(29);res=[]
for guess in [q0]+[rng.uniform(k.lower,k.upper)for _ in range(100)]:
 q,e,a=k.solve(target[:3,3]+target[:3,:3]@PALM_OFFSET,target[:3,:3],guess)
 if e<2e-5 and a<2e-4:
  el=k.transforms(q)[ep][:3,3];res.append(dict(q=q.tolist(),out=float((el-shoulder)@out),el=el.tolist()))
(w/'candidates.json').write_text(json.dumps(res,indent=2));print('shoulder',shoulder,'old',k.transforms(q0)[ep][:3,3]);print(sorted([(x['out'],x['el'],x['q'][3])for x in res]))
