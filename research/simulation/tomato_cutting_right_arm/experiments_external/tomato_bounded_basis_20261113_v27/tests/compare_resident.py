from pathlib import Path
import os,sys,json,numpy as np
from scipy.sparse import coo_matrix
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
base=Path('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25');a=Aggregate(Body.restore(base/'states/tomato_baseline.npz'));b=a.body;X=b.poly_vertices;owner=np.repeat(np.arange(len(b.polys)),np.diff(b.poly_ptr));N=np.einsum('pi,pij->pj',np.c_[np.ones(len(X)),X],b.inv[owner]);Q=(coo_matrix((N.ravel(),(np.repeat(np.arange(len(X)),4),b.ids[owner].ravel())),shape=(len(X),len(b.u)))@a.E).tocsr();reference=W/'runs/tomato_hierarchy_dt25_r2';r=json.loads((reference/'result.json').read_text());z=np.load(reference/'trajectory.npz');q=z['q'][-1];v=z['v'][-1];rows=[]
for name in ['intact_parallel_1_resident_r2','intact_parallel_8_resident_broad']:
 folder=W/'runs'/name;out=json.loads((folder/'result.json').read_text())
 for i in range(out['environments']):
  state=np.load(folder/f'final_state_{i}.npz');pe=float(np.linalg.norm(Q@(state['q']-q),axis=1).max());ve=float(np.linalg.norm(Q@(state['v']-v),axis=1).max());ce=float(abs(np.array([row['force'] for row in out['rows'][i]])-np.array([row['sum_force_N'] for row in r['rows']])).max()/max(1e-4,max(row['sum_force_N'] for row in r['rows'])));we=abs(out['rows'][i][-1]['work']-r['rows'][-1]['tool_work_J'])/max(abs(r['rows'][-1]['tool_work_J']),1e-8);fe=abs(out['rows'][i][-1]['friction']-r['rows'][-1]['friction_J'])/max(abs(r['rows'][-1]['friction_J']),1e-8)
  checks=dict(position=pe<1e-6,velocity=ve<1e-4,force=ce<.05,work=we<.05,friction=fe<.05,complete=out['physical_checks_passed']);rows.append(dict(run=name,environment=i,position_m=pe,velocity_m_s=ve,force_relative=ce,work_relative=we,friction_relative=fe,checks=checks))
result=dict(passed=all(all(x['checks'].values()) for x in rows),scope='Same 13 ms intact contact trajectory and 25us material steps; exact original CAD and per-250us clearance unchanged. Full force history and final material field/work compared. No physical cutting or RL qualification.',rows=rows);(W/'reports/resident_response_comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['passed']
