from cohesive_transfer import Transfer,ROOT
from pathlib import Path
import sys,json,time,numpy as np
sys.path.append('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages')
from tomato_collision_embedding import build_embedding
s=Transfer();m=s.mesh;x=m['x'];design=dict(nodes=[dict(position_m=p.tolist()) for p in x],cut_x_m=-.0225,pieces=[])
for side in [-1,1]:
 owned=np.unique(m['tets'][m['tet_side']==side]);faces=m['boundary'][np.all(np.isin(m['boundary'],owned),axis=1)];design['pieces'].append(dict(side='left' if side<0 else 'right',surface_node_ids=np.unique(faces).tolist(),triangles=faces.tolist(),reference_interior_m=x[owned].mean(0).tolist()))
start=time.perf_counter();rows=[];stop='completed'
try:
 e=build_embedding(design,m['tets']);np.savez_compressed(Path(__file__).with_name('closure_embedding.npz'),**{k:v for k,v in e.items() if k!='records'})
 import warp as wp
 from tomato_fast_mollified_contact import FastMollifiedEmbeddedSelfContact
 wp.init();wp.set_device('cuda:0');engine=FastMollifiedEmbeddedSelfContact(dict(design=design,cells=m['tets'],x=x));physical=wp.array(x,dtype=wp.vec3);plus=np.unique(m['tets'][m['tet_side']>0]);minus=np.unique(m['tets'][m['tet_side']<0])
 for name,gap in [('rest',0.),('closure',-1e-5),('open',.001),('reclosure',-1e-5)]:
  q=x.copy();q[plus,0]+=gap;physical.assign(q);engine.invalid.zero_();engine.detect(physical);engine.evaluate(physical,1/2400);wp.synchronize();f=engine.physical_force.numpy();rows.append(dict(name=name,gap_m=gap,net_force_N=float(np.linalg.norm(f.sum(0))),left_force_x_N=float(f[minus,0].sum()),force_norm_N=float(np.linalg.norm(f)),invalid=int(engine.invalid.numpy()[0])))
except Exception as exc:stop=repr(exc)
out=dict(scope='Existing research closure algorithm on new split geometry, prescribed piece translations only',stop=stop,wall_s=time.perf_counter()-start,rows=rows)
out['passed']=bool(stop=='completed' and len(rows)==4 and all(r['invalid']==0 and r['net_force_N']<1e-7 for r in rows) and rows[0]['force_norm_N']<1e-5 and rows[1]['left_force_x_N']<0 and rows[2]['force_norm_N']<1e-5 and abs(rows[1]['left_force_x_N']-rows[3]['left_force_x_N'])<1e-7)
Path(__file__).with_name('closure_fixture_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
