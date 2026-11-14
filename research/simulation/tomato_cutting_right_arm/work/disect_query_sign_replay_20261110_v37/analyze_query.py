from pathlib import Path
import importlib.util,json,sys,numpy as np,mpmath as mp
W=Path(__file__).resolve().parent;R=W.parents[1];z=np.load(W/'first_uncertain_query.npz');v=z['vertices'];f=z['faces'];p=z['points'];bad=np.flatnonzero(z['errors']);out={'point_count':len(p),'bad_count':len(bad),'bad':[]}
sys.path.insert(0,str(R/'rl'));import tomato_compiled_blade_query as ref
for idx in bad:
 record={'index':int(idx),'point':p[idx].tolist(),'phi_fast_m':float(z['phi'][idx]),'winding_fast':float(z['winding'][idx]),'closest_face':int(z['face'][idx])}
 try:
  vals=ref._query(v,f,p[idx:idx+1]);record['reference_passes']=True;record['reference_phi_m']=float(vals[0][0]);record['reference_winding']=float(vals[4][0])
 except Exception as e:record['reference_passes']=False;record['reference_error']=str(e)
 for precision in [60,100]:
  mp.mp.dps=precision;point=list(map(mp.mpf,p[idx]));total=mp.mpf(0)
  for face in f:
   a,b,c=[[mp.mpf(float(x))-px for x,px in zip(v[j],point)] for j in face];dot=lambda u,w:sum(x*y for x,y in zip(u,w));cross=[b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0]];la,lb,lc=[mp.sqrt(dot(q,q)) for q in [a,b,c]];num=dot(a,cross);den=la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb;total+=2*mp.atan2(num,den)
  record[f'winding_{precision}_digits']=mp.nstr(total/(4*mp.pi),35)
 out['bad'].append(record)
(W/'query_analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
