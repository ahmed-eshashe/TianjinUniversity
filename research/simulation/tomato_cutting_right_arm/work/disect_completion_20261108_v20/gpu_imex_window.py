"""Bounded assembled conditioning diagnostic, not a settling/fracture pass."""
from pathlib import Path
import sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_completion_20261108_v18'))
from full_surface import FullSurface
from closure_gpu import ClosureGPU
from cohesion_gpu import CohesionGPU
import warp as wp
import sys,time,json,numpy as np
from pathlib import Path
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06/backend'))
from numerics import load_arrays,tensor,torch
sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'))
from contact_numerics import ContactBulk
torch.set_num_threads(1);s=FullSurface(device="cuda");closure=ClosureGPU(s);cohesion=CohesionGPU(s);m=s.mesh;old=load_arrays();x=m['x'];t=m['tets'];fixed=m['fixed'];mass=m['mass'];inv=1/mass;inv[fixed]=0
z=dict(x=x,tet_indices=t,tet_poses=np.linalg.inv((x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)),physical_mass=mass,particle_inv_mass=inv,gravity=old['gravity'],contact_mask=np.ones(len(x)),fixed=fixed)
for name in ['tet_mu','tet_lambda','tet_damping','tet_activations']:
 assert np.all(old[name]==old[name][0])
 z[name]=np.full(len(t),old[name][0])
class Assembled(ContactBulk):
 def geometry(self):
  f=super().geometry()
  with wp.ScopedStream(wp.stream_from_torch(torch.cuda.current_stream())):
   f.add_(cohesion.evaluate(self.x));f.add_(closure.evaluate(self.x))
  return f
import argparse,math
p=argparse.ArgumentParser();p.add_argument('--dt',type=float,required=True);p.add_argument('--duration',type=float,default=.02);p.add_argument('--name',required=True);args=p.parse_args()
b=Assembled(z);b.enable_gather();sub=math.ceil(.001/args.dt);h=.001/sub;rows=[];snap=[];start=time.perf_counter();stop='completed';initial=np.linalg.det(x[t[:,1:]]-x[t[:,0]][:,None]);mapping=dict(np.load(W.parent/'disect_precontact_20261108_v06/board_mapping.npz'));A=tensor(mapping['rotation']);T=tensor(mapping['translation']);H=tensor(mapping['halfspaces']);base=b.mask.clone()
def sample(k):
 q,v=b.arrays();f=(b.geometry()-b.damping(b.v)).cpu().numpy().copy();ratio=np.linalg.det(q[t[:,1:]]-q[t[:,0]][:,None])/initial;world=q@mapping['rotation'].T+mapping['translation'];margin=-np.max(world[:,:2]@mapping['halfspaces'][:,:2].T+mapping['halfspaces'][:,2]);row=dict(sim_s=k*.001,volume_ratio_min=float(ratio.min()),speed_max_m_s=float(np.linalg.norm(v,axis=1).max()),board_penetration_m=float(max(0,-q[:,1].min())),support_error_m=float(abs(q[fixed]-x[fixed]).max()),board_edge_margin_m=float(margin),wall_s=time.perf_counter()-start);row['admissible']=bool(np.isfinite(q).all() and ratio.min()>.1 and row['board_penetration_m']<=.0001 and row['support_error_m']<=1e-7 and margin>=.001);rows.append(row);snap.append((q,v,f));Path(__file__).with_name(args.name+'_progress.json').write_text(json.dumps(row));return row['admissible']
sample(0)
try:
 for k in range(1,round(args.duration/.001)+1):
  for j in range(sub):
   world=b.x@A.T+T;b.mask=base*torch.all(world[:,:2]@H[:,:2].T+H[:,2]<=0,dim=1);info=b.implicit(h)
   if int(cohesion.invalid.numpy()[0]) or int(closure.engine.invalid.numpy()[0]):raise RuntimeError('Invalid cohesion/contact geometry')
  if not sample(k):stop='physical_stop';break
  if time.perf_counter()-start>300:stop='wall_cap';break
except Exception as e:stop=repr(e)
np.savez_compressed(Path(__file__).with_name(args.name+'_trajectory.npz'),x=np.array([v[0] for v in snap]),v=np.array([v[1] for v in snap]),force=np.array([v[2] for v in snap]),t=np.array([v['sim_s'] for v in rows]))
out=dict(scope='Full-surface cohesion plus research cut-face contact, damage disabled; bounded unloaded assembled check',stop=stop,dt_s=h,wall_s=time.perf_counter()-start,rows=rows,component_passed=bool(stop=='completed' and all(r['admissible'] for r in rows)))
Path(__file__).with_name(args.name+'_result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
