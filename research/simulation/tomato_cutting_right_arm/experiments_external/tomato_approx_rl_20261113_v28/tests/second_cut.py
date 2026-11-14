from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver
out=W/'runs/second_intersecting_cut_adaptive';out.mkdir(exist_ok=False);z=np.load(W/'runs/task_full_cycle/state.npz');g=Solver(lattice('tomato'),dt=.0002,adaptive=True)
for key in g.initial:
 if key in z:getattr(g,key).assign(z[key])
rows=[];start=time.perf_counter();g.graph(100)
def advance(action,label):
 bad=g.step(action,100)
 if len(rows)%100==0:print(json.dumps({'phase':label,'tool':g.tool.numpy()[0].tolist(),'bad':bad.tolist(),'peak':float(g.peak.numpy()[0]),'wall':time.perf_counter()-start}),flush=True)
 rows.append({'phase':label,'bad':bad.tolist()})
 if bad.any():raise RuntimeError('Physical stop '+str(bad))
def move(target):
 for _ in range(1000):
  delta=np.asarray(target)-g.tool.numpy()[0];action=np.clip(delta/.02,[-.05,-.01,-.05],[.05,.01,.05])
  if np.max(np.abs(delta))<2e-6:return
  advance(action,'reposition clear of tomato')
 raise RuntimeError('move timeout')
move([.00175,.065,.12])
# Rotate a real commanded tool, outside the tomato; no pose jump while in contact.
for k in range(132):advance([0,0,0,0,(np.pi/2)/(132*.02),0],'rotate outside material')
move([0,.06075,.00175])
phase='cut';components=2
for k in range(4000):
 saw=np.sin(k*.4);position=g.tool.numpy()[0]
 if phase=='cut':
  action=[.15*saw,-.0015*abs(saw) if position[1]>.0034 else 0.,0]
  if k%10==0:components,labels=g.components()
  if components>=4 and position[1]<=.0034:phase='withdraw'
 if phase=='withdraw':action=[.06,0,0]
 advance(action,phase)
 if phase=='withdraw' and position[0]>.12:break
components,labels=g.components();result={'refinements':g.refinements,'active_dt':g.active_dt,'components':components,'sizes':np.bincount(labels).tolist(),'bad':g.bad.numpy().tolist(),'peak_N':g.peak.numpy().tolist(),'penetration_m':g.penetration_peak.numpy().tolist(),'fracture_work_J':float(g.paid.numpy().sum()),'wall_s':time.perf_counter()-start,'final_tool':g.tool.numpy().tolist(),'phase':phase,'pass':bool(components==4 and not g.bad.numpy().any() and phase=='withdraw')};np.savez_compressed(out/'state.npz',**{key:getattr(g,key).numpy() for key in g.initial},labels=labels);(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
