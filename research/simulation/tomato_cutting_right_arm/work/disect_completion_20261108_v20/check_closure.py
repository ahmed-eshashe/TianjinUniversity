from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
import torch,warp as wp
from closure_gpu import ClosureGPU
wp.init();wp.set_device('cuda:0');torch.set_num_threads(1);s=FullSurface(device='cuda');c=ClosureGPU(s);x=s.mesh['x'];plus=np.unique(s.mesh['tets'][s.mesh['tet_side']>0]);rows=[]
for name,shift in [('rest',0),('open',.0002),('closure',-.00001)]:
 q=x.copy();q[plus,0]+=shift
 e,ref=c.reference.energy_force_precise(q)
 qt=torch.tensor(q,device='cuda',dtype=torch.float64)
 with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
  f=c.evaluate(qt)
 torch.cuda.synchronize();f=f.cpu().numpy().copy();energy=float(c.engine.contact_energy.numpy()[0]);invalid=int(c.engine.invalid.numpy()[0]);err=float(np.linalg.norm(f-ref)/max(np.linalg.norm(ref),1e-12))
 rows.append(dict(state=name,force_relative_error=err,energy_error_j=abs(e-energy),invalid=invalid))
# Warmed throughput excludes initial detection allocation/JIT.
with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
 for _ in range(3):c.evaluate(qt)
 torch.cuda.synchronize();start=time.perf_counter()
 for _ in range(30):c.evaluate(qt)
 torch.cuda.synchronize();seconds=(time.perf_counter()-start)/30
out=dict(rows=rows,seconds_per_evaluation=seconds,passed=all(r['force_relative_error']<1e-8 and r['energy_error_j']<1e-10 and r['invalid']==0 for r in rows));(W/'closure_control.json').write_text(json.dumps(out,indent=2));print(out);assert out['passed']
