"""Objective force, incremental energy and exact colored tangent native audit."""
import argparse,hashlib,json,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[];columns=0
 def stop(*args):raise InterruptedError('Objective force/tangent audit stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from tomato_native_full_model import registry
  from tomato_objective_cohesion_reference import make_patch,response
  from tomato_native_objective_reference import objective_force,incremental_objective_energy,force_seed,hessian_column
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();patches=data['cohesion'].patches;models=[];n=max(len(p['indices']) for p in patches);pairs=np.zeros((len(patches),n,2),int);weights=np.zeros((len(patches),n));counts=[];anchors=[];sign=[];k=[];laws=[]
  for i,p in enumerate(patches):
   local=data['x'][data['pairs'][p['indices']]];l=p['law'];m=make_patch(local,p['weights'],p['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m));models.append(m);pairs[i,:len(local)]=data['pairs'][p['indices']];weights[i,:len(local)]=p['weights'];counts.append(len(local));anchors.append(m['anchors']);sign.append(m['sign']);k.append(m['local_k']);laws.append([l.stiffness_n_m,l.onset_m,l.failure_m])
  args=[wp.array(pairs,dtype=wp.vec2i),wp.array(counts,dtype=int),wp.array(anchors,dtype=wp.vec3i),wp.array(sign,dtype=wp.float64),wp.array(weights,dtype=wp.float64),wp.array(k,dtype=wp.mat33d),wp.array(laws,dtype=wp.vec3d),wp.zeros(len(patches),dtype=wp.vec2d),wp.ones(len(patches),dtype=int)]
  colors=np.zeros(len(data['x']),int)
  for color,nodes in enumerate(data['colors']):colors[nodes]=color
  for i in range(len(patches)):
   nodes=np.unique(pairs[i,:counts[i]])
   if len(set(colors[nodes]))!=len(nodes):raise ValueError('Hessian seed coloring requires patch cliques')
  gpu_colors=wp.array(colors,dtype=int);q=Rotation.from_rotvec([.3,.6,-.2]).as_matrix();right=np.unique(data['pairs'][:,1]);tangent_reference=np.load(ROOT/'work/integration_20261102/objective_tangent_reference.npz')
  for label,gap,rotate in [('rest',[0,0,0],False),('tensile',[.0005,0,0],False),('mixed_open',[.002,.0003,.0002],False),('mixed_compressed',[-.0002,.002,.0003],False),('rotated_mixed',[.002,.0003,.0002],True),('pure_compression',[-.001,0,0],False)]:
   if (out/'stop.request').exists():raise InterruptedError('Guard stop before objective audit case')
   pos=data['x'].copy();pos[right]+=gap
   if rotate:pos=pos@q.T+[.2,-.1,.3]
   reference=np.zeros_like(pos);potential=[]
   for i,m in enumerate(models):
    ids=pairs[i,:counts[i]];a=response(pos[ids],m,eligible=True);np.add.at(reference,ids.reshape(-1),a['force_n'].reshape(-1,3));potential.append(a['incremental_potential_j'])
   x=wp.array(pos,dtype=wp.vec3d,requires_grad=True);f=wp.zeros(len(pos),dtype=wp.vec3d,requires_grad=True);energy=wp.zeros(len(patches),dtype=wp.float64,requires_grad=True)
   with wp.Tape() as tape:wp.launch(objective_force,dim=len(patches),inputs=[x,*args],outputs=[f])
   with wp.Tape() as etape:wp.launch(incremental_objective_energy,dim=len(patches),inputs=[x,*args],outputs=[energy])
   etape.zero();etape.backward(grads={energy:wp.ones(len(patches),dtype=wp.float64)});native=f.numpy();energy_gradient=-etape.gradients[x].numpy();fe=float(np.max(np.abs(native-reference)));pe=float(np.max(np.abs(energy.numpy()-potential)));ge=float(np.max(np.abs(native-energy_gradient)))
   row=dict(id=label,force_error_n=fe,potential_error_j=pe,incremental_gradient_error_n=ge,net_force_n=float(np.linalg.norm(native.sum(0))),net_moment_nm=float(np.linalg.norm(np.cross(pos,native).sum(0))))
   if fe>1e-8 or pe>1e-12 or ge>1e-8 or row['net_moment_nm']>1e-9:
    np.savez(out/'force_gradient_failure.npz',positions=pos,force=native,gradient_force=energy_gradient,reference=reference)
    raise ValueError('Objective explicit force/potential mismatch '+str(row))
   if label=='mixed_open':
    blocks=wp.zeros(len(pos),dtype=wp.mat33d);seed=wp.zeros(len(pos),dtype=wp.vec3d)
    for color in range(len(data['colors'])):
     for axis in range(3):
      tape.zero();x.grad.zero_();f.grad.zero_();wp.launch(force_seed,dim=len(pos),inputs=[gpu_colors,color,axis],outputs=[seed]);tape.backward(grads={f:seed});wp.launch(hessian_column,dim=len(pos),inputs=[gpu_colors,color,axis,tape.gradients[x]],outputs=[blocks]);columns+=1
    matrix=blocks.numpy();error=float(np.max(np.abs(matrix-tangent_reference['hessians'])));symmetry=float(np.max(np.abs(matrix-matrix.transpose(0,2,1))));row.update(diagonal_tangent_error_n_m=error,diagonal_tangent_symmetry_error_n_m=symmetry)
    if error>1e-5 or symmetry>1e-5:raise ValueError('Objective tangent mismatch '+str(row))
    np.savez(out/'objective_tangent_native.npz',positions=pos,forces=native,hessians=matrix)
   cases.append(row);write(out,'objective_force_partial.json',dict(cases=cases,hessian_columns=columns))
  write(out,'objective_force_measurements.json',dict(cases=cases,hessian_columns=columns,patches=len(patches),scope='Float64 operator: objective explicit force, consistent incremental fracture potential and colored diagonal tangent. No dynamic integration or whole-fruit contact qualification.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_native_objective_reference.py',ROOT/'rl/tomato_objective_cohesion_reference.py',ROOT/'work/integration_20261102/objective_tangent_reference.npz']}));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,objective_force_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases),hessian_columns=columns))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
