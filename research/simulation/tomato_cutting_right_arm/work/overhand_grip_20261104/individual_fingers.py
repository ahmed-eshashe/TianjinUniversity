exec(open(__file__.replace('individual_fingers.py','fit_handle.py')).read().split('meshes=g.geometry')[0])
f=json.loads((w/'fit_candidates.json').read_text())[0];A=np.array(f['A']);c=np.array(f['center']);kv=(h-hc)@A.T+c;choice={};report={}
for finger in ['index','middle','ring','pinky']:
 opts=[]
 for flex in np.arange(55,85.01,.5):
  ds={}
  for name,v in g.geometry(float(flex),np.rad2deg(.86),np.rad2deg(.49)):
   if finger not in name:continue
   eq=ConvexHull((v[:,None,:]-kv[None,:,:]).reshape(-1,3)).equations;ds[name]=float(max(eq[:,3]))
  if min(ds.values())>=.00045:opts.append((ds['right_rh_'+finger+'_distal'],float(flex),ds))
 best=min(opts);choice[finger]=best[1];report.update(best[2])
f.update(fingers=choice,finger_gaps=report);(w/'final_fit.json').write_text(json.dumps(f,indent=2));print(choice,report)
