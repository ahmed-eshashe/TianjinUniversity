"""Native force audit of all saved interface patches; no mechanical time steps."""
import argparse,hashlib,json,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*args):raise InterruptedError('Objective operator check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from tomato_native_full_model import registry
  from tomato_objective_cohesion_reference import make_patch,response
  from tomato_native_objective_reference import objective_energy
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();patches=data['cohesion'].patches;models=[];n=max(len(p['indices']) for p in patches);pairs=np.zeros((len(patches),n,2),int);weights=np.zeros((len(patches),n));counts=[];anchors=[];sign=[];k=[]
  for i,p in enumerate(patches):
   local=data['x'][data['pairs'][p['indices']]];law=p['law'];model=make_patch(local,p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));models.append(model);pairs[i,:len(local)]=data['pairs'][p['indices']];weights[i,:len(local)]=p['weights'];counts.append(len(local));anchors.append(model['anchors']);sign.append(model['sign']);k.append(model['local_k'])
  args=[wp.array(pairs,dtype=wp.vec2i),wp.array(counts,dtype=int),wp.array(anchors,dtype=wp.vec3i),wp.array(sign,dtype=wp.float64),wp.array(weights,dtype=wp.float64),wp.array(k,dtype=wp.mat33d)]
  right=np.asarray(data['design']['pieces'][1]['node_ids']) if 'node_ids' in data['design']['pieces'][1] else np.unique(data['pairs'][:,1])
  # Only interface nodes are perturbed in an operator fixture; no dynamics claim.
  right=np.unique(data['pairs'][:,1]);q=Rotation.from_rotvec([.3,.6,-.2]).as_matrix()
  for label,gap,rotate in [('rest',[0,0,0],False),('tensile',[.0005,0,0],False),('mixed_open',[.002,.0003,.0002],False),('mixed_compressed',[-.0002,.002,.0003],False),('rotated_mixed',[.002,.0003,.0002],True),('pure_compression',[-.001,0,0],False)]:
   if (out/'stop.request').exists():raise InterruptedError('Stop before objective force case')
   pos=data['x'].copy();pos[right]+=gap
   if rotate:pos=pos@q.T+[.2,-.1,.3]
   force=np.zeros_like(pos);energies=[];damage=[]
   for i,model in enumerate(models):
    ids=pairs[i,:counts[i]];r=response(pos[ids],model,eligible=True);damage.append(r['trial_history'][1]);energies.append(r['stored_energy_j']);np.add.at(force,ids.reshape(-1),r['force_n'].reshape(-1,3))
   x=wp.array(pos,dtype=wp.vec3d,requires_grad=True);d=wp.array(damage,dtype=wp.float64);energy=wp.zeros(len(patches),dtype=wp.float64,requires_grad=True)
   with wp.Tape() as tape:wp.launch(objective_energy,dim=len(patches),inputs=[x,*args,d],outputs=[energy],device='cuda:0')
   tape.backward(grads={energy:wp.ones(len(patches),dtype=wp.float64)});native_force=-tape.gradients[x].numpy();native_energy=energy.numpy();ferr=float(np.max(np.abs(native_force-force)));eerr=float(np.max(np.abs(native_energy-energies)));balance=float(np.linalg.norm(native_force.sum(0)));moment=float(np.linalg.norm(np.cross(pos,native_force).sum(0)))
   row=dict(id=label,force_error_n=ferr,energy_error_j=eerr,net_force_n=balance,net_moment_nm=moment,maximum_damage=max(damage),total_energy_j=float(native_energy.sum()));cases.append(row);write(out,'objective_operator_partial.json',dict(cases=cases))
   if ferr>1e-8 or eerr>1e-12 or balance>1e-9 or moment>1e-9:raise ValueError('Objective native/reference force/energy balance mismatch')
  write(out,'objective_operator_measurements.json',dict(cases=cases,patches=len(patches),precision='float64 candidate operator; no float32 production solver integration',scope='All 47 actual patches: moving-frame forces, mixed opening/compression-shear and rotations. No native tangent, damage stepping, self-contact or full-fruit fracture qualification.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_native_objective_reference.py',ROOT/'rl/tomato_objective_cohesion_reference.py']}));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,objective_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
