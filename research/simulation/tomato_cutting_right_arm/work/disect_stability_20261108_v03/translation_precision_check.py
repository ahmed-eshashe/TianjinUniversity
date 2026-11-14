from pathlib import Path
import numpy as np,json
w=Path(__file__).resolve().parent;z=np.load(w/'settled_tomato.npz');x=z['initial_x'];t=z['tets'];xf=z['x'];iv=np.linalg.det(x[t[:,1:]].astype(float)-x[t[:,0]].astype(float)[:,None]);ratio=np.linalg.det(xf[t[:,1:]].astype(float)-xf[t[:,0]].astype(float)[:,None])/iv;k=int(np.argmin(ratio));ids=t[k];q=x[ids].copy();q64=q.astype(float);dt=np.float32(2e-7);v=np.float32(0);v64=0.;g=np.float32(-9.80665);rows=[]
for i in range(81000):
 v=np.float32(v+g*dt);q[:,1]=q[:,1]+v*dt;v64+=float(g)*float(dt);q64[:,1]+=v64*float(dt)
 if (i+1)%1000==0:
  j=float(np.linalg.det(q[1:].astype(float)-q[0].astype(float))/iv[k]);j64=float(np.linalg.det(q64[1:]-q64[0])/iv[k]);rows.append({'step':i+1,'volume_ratio_float32':j,'volume_ratio_float64':j64})
out={'scope':'Offline four-node free-fall control. Uniform gravity, no FEM/contact/fixture forces. Exact translation should preserve volume; not an additional native dynamics test.','tet_id':k,'nodes':ids.tolist(),'dt_s':float(dt),'steps':81000,'final_volume_ratio_float32':rows[-1]['volume_ratio_float32'],'minimum_volume_ratio_float32':min(a['volume_ratio_float32'] for a in rows),'final_volume_ratio_float64':rows[-1]['volume_ratio_float64'],'node_y_displacements_float32':(q[:,1]-x[ids,1]).tolist(),'node_y_displacements_float64':(q64[:,1]-x[ids,1]).tolist(),'actual_FEM_final_volume_ratio':float(ratio[k]),'interpretation':'Demonstrates precision-induced non-rigid deformation under uniform translation at the chosen microstep. It does not alone explain every term in the coupled FEM result.','rows':rows}
(w/'translation_precision_check.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
