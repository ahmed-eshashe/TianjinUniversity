"""Native operator controls for cancelling errors and fixed reactions."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Local ledger stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)],inputs=[ROOT/'work/integration_20261102/local_residual_contract.json'])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_rebased_ledger import collect_double_external
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');dt=1/4800;mass=np.array([.001,.002,.003]);x=np.array([[.01,0,.02],[0,.02,.03],[0,0,.04]]);gravity=np.tile([0,0,-9.81],(3,1))*mass[:,None]
  for label in ['freefall','cancelling_errors','fixed_reaction']:
   fixed=np.zeros(3,dtype=int);force=np.zeros((3,3));v=np.tile([0,0,-9.81*dt],(3,1)).astype(np.float32)
   if label=='cancelling_errors':force[1,0]=.1;force[2,0]=-.1
   if label=='fixed_reaction':fixed[0]=1;force[0]=[1.,-.2,.3];v[0]=0
   impulse=wp.zeros(3,dtype=wp.vec3d);angular=wp.zeros(3,dtype=wp.vec3d);instant=wp.zeros(3,dtype=wp.vec3d);previous=wp.zeros(3,dtype=wp.vec3d);total=wp.zeros(1,dtype=wp.float64);step=wp.zeros(1,dtype=wp.float64);node=wp.zeros(1,dtype=wp.float64);zero=wp.zeros(3,dtype=wp.vec3d)
   wp.launch(collect_double_external,dim=3,inputs=[wp.array(x,dtype=wp.vec3d),wp.array(v,dtype=wp.vec3),previous,wp.array(mass,dtype=wp.float64),wp.array(fixed,dtype=int),wp.array(force,dtype=wp.vec3d),zero,zero,wp.zeros(3,dtype=float),wp.float64(dt)],outputs=[impulse,angular,instant,total,step,node]);reference=mass[:,None]*v.astype(float)-dt*(force+gravity);reference=reference[fixed==0];expected=float(np.linalg.norm(reference,axis=1).sum());error=float(abs(total.numpy()[0]-expected));global_error=float(np.linalg.norm(reference.sum(0)))
   if error>1e-12 or abs(step.numpy()[0]-expected)>1e-12 or abs(node.numpy()[0]-np.linalg.norm(reference,axis=1).max())>1e-12:raise ValueError('Per-node residual reference mismatch')
   reaction=-(force+gravity)[fixed!=0].sum(0)
   if np.linalg.norm(instant.numpy()[2]-reaction)>1e-12:raise ValueError('Independent fixed reaction mismatch')
   if label=='cancelling_errors' and not (expected>1e-5 and global_error<1e-10):raise ValueError('Cancelling force control missed')
   cases.append(dict(case=label,absolute_nodal_residual_ns=expected,global_residual_ns=global_error,reference_error_ns=error,reaction_n=reaction.tolist()))
  if not sources_unchanged(pins):raise ValueError('Ledger source changed')
  write(out,'local_ledger_measurements.json',dict(cases=cases,scope='Three synthetic native force/impulse operator controls only, zero mechanical steps. Shows why cancelling errors need a local residual audit; no target support or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,local_ledger_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
