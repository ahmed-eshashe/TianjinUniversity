"""Static precision operators for the rebased candidate; no mechanical steps."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Rebased operator stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  failure_path=ROOT/'runs/native/relative_preflight_20261102_03/first_bad_update.npz';pins=capture_sources(out,[Path(__file__)],inputs=[failure_path])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry
  from tomato_native_full_gather import adjacency
  from tomato_bulk_reference import bulk_reference
  from tomato_double_blocks import double_bulk,determinant_diagnosis
  from tomato_rebased_solver import rebase,solve_double
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];n=len(data['x']);offsets,springrows=adjacency(data['springs'],n);celloffsets,cellrows=adjacency(data['cells'],n);colors=wp.zeros(n,dtype=int);force=wp.zeros(n,dtype=wp.vec3d);blocks=wp.zeros(n,dtype=wp.mat33d);invalid=wp.zeros(1,dtype=int)
  write(out,'input_manifest.json',dict(cases=6,newton_steps=0,controlled_steps=0,bulk_force_budget_n=1e-8,bulk_block_budget_n_m=1e-6,rebase_physical_budget_m=1e-16,rebase_target_budget_m=1e-9,linear_solve_relative_budget=2e-7,tiny_increment_m=3e-14,scope='Static precision controls only. Float64 bulk blocks, rebase invariance, normalized diagonal solves and tiny increment retention; no dynamic support or accuracy claim.'))
  for label,x in [('rest',data['x'].copy()),('affine',data['x']@np.array([[.74,.015,0],[0,.76,.01],[0,0,.85]]).T)]:
   reference=bulk_reference(x,data);wp.launch(double_bulk,dim=n,inputs=[0,colors,wp.array(x,dtype=wp.vec3d),offsets,springrows,wp.array(data['springs'].ravel(),dtype=int),wp.array(np.linalg.norm(data['x'][data['springs'][:,1]]-data['x'][data['springs'][:,0]],axis=1),dtype=wp.float64),wp.array(data['k'],dtype=wp.float64),celloffsets,cellrows,wp.array(data['cells'],dtype=wp.vec4i),wp.array(data['volumes'],dtype=wp.float64)],outputs=[invalid,force,blocks],block_dim=64);fe=float(abs(force.numpy()-reference['force']).max());he=float(abs(blocks.numpy()-reference['blocks']).max())
   if invalid.numpy()[0] or fe>1e-8 or he>1e-6:raise ValueError((label,fe,he))
   cases.append(dict(case=label,force_error_n=fe,block_error_n_m=he))
  failure=np.load(failure_path);failure_x=failure['x'];wp.launch(double_bulk,dim=n,inputs=[0,colors,wp.array(failure_x,dtype=wp.vec3d),offsets,springrows,wp.array(data['springs'].ravel(),dtype=int),wp.array(np.linalg.norm(data['x'][data['springs'][:,1]]-data['x'][data['springs'][:,0]],axis=1),dtype=wp.float64),wp.array(data['k'],dtype=wp.float64),celloffsets,cellrows,wp.array(data['cells'],dtype=wp.vec4i),wp.array(data['volumes'],dtype=wp.float64)],outputs=[invalid,force,blocks],block_dim=64);worst=int(np.argmin(failure['volume_ratios']));nodes=data['cells'][worst];single=wp.zeros(4,dtype=float);double=wp.zeros(4,dtype=wp.float64);wp.launch(determinant_diagnosis,dim=4,inputs=[blocks,wp.array(data['mass'],dtype=wp.float64),wp.array(nodes,dtype=int),wp.float64(failure['dt'][0])],outputs=[single,double]);values=single.numpy().astype(float);double_values=double.numpy();write(out,'captured_failure_block_diagnosis.json',dict(nodes=nodes.tolist(),float32_determinants=[float(v) if np.isfinite(v) else str(v) for v in values],float64_determinants=[float(v) if np.isfinite(v) else str(v)for v in double_values],nonfinite_float32_count=int(np.sum(~np.isfinite(values))),scope='Native postmortem on captured unsafe-to-progress state, not a qualified material/solver state. Determinant finiteness alone does not establish numerical conditioning or an accurate inverse.'));invalid.zero_()
  R=np.array([[.02,-.01,.04],[.03,.02,.06]]);u=np.array([[.005,-.002,.003],[-.004,.001,.002]],dtype=np.float32);physical=R+u.astype(float);origin=physical+np.array([[-.0001,.0002,0],[.0003,0,-.0002]]);target=physical+[1e-5,-2e-5,3e-5];query=physical+[2e-6,3e-6,-1e-6];ra=wp.array(R,dtype=wp.vec3d);ua=wp.array(u,dtype=wp.vec3);previous=wp.zeros(2,dtype=wp.vec3);inertia=wp.zeros(2,dtype=wp.vec3);baseline=wp.zeros(2,dtype=wp.vec3);displacement=wp.zeros(2,dtype=wp.vec3);qlocal=wp.zeros(2,dtype=wp.vec3)
  wp.launch(rebase,dim=2,inputs=[ra,ua,wp.array(origin,dtype=wp.vec3d),wp.array(target,dtype=wp.vec3d),wp.array(query,dtype=wp.vec3d)],outputs=[previous,inertia,baseline,displacement,qlocal]);after=ra.numpy()+ua.numpy().astype(float);pe=float(abs(after-physical).max());te=max(float(abs(ra.numpy()+a.numpy().astype(float)-b).max())for a,b in [(previous,origin),(inertia,target),(qlocal,query)])
  if pe>1e-16 or te>1e-9 or np.any(baseline.numpy()) or np.any(displacement.numpy()):raise ValueError('Rebase changed physical state or targets')
  cases.append(dict(case='rebase_invariance',physical_error_m=pe,target_error_m=te))
  for label,H in [('ordinary',np.diag([2000.,3000.,4000.])),('high_range',np.diag([1e18,2000.,3000.]))]:
   zero=wp.zeros(1,dtype=wp.vec3d);zh=wp.zeros(1,dtype=wp.mat33d);delta=wp.zeros(1,dtype=wp.vec3);fallback=wp.zeros(1,dtype=int);bad=wp.zeros(1,dtype=int);f=np.array([1.,2.,3.]);wp.launch(solve_double,dim=1,inputs=[0,wp.zeros(1,dtype=int),wp.ones(1,dtype=float),zero,zero,wp.float64(1.),wp.array([f],dtype=wp.vec3d),wp.array([H-np.eye(3)],dtype=wp.mat33d),zero,zh,zero,zh,wp.zeros(1,dtype=float),wp.float64(-1.)],outputs=[delta,fallback,bad]);actual=delta.numpy()[0].astype(float);expected=np.linalg.solve(H,f);error=float(np.max(abs(actual-expected)/np.maximum(abs(expected),1e-30)))
   if error>2e-7 or fallback.numpy()[0] or bad.numpy()[0] or actual@f<=0:raise ValueError((label,error,actual,expected))
   cases.append(dict(case=label,relative_solve_error=error,direction_dot_force=float(actual@f)))
  tiny=3e-14;old=float(np.float32(u[0,0])+np.float32(tiny))-float(u[0,0]);new=float(ra.numpy()[0,0]+np.float32(tiny))-physical[0,0]
  if old!=0 or abs(new-tiny)>1e-17:raise ValueError('Tiny update retention control failed')
  cases.append(dict(case='tiny_increment',old_retained_m=old,rebased_retained_m=new))
  if not sources_unchanged(pins):raise ValueError('Operator sources changed')
  write(out,'rebased_operator_measurements.json',dict(cases=cases,scope='Six static controls, zero steps. No complete contact, solver convergence, sustained support, robot coupling, fracture or energy qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,rebased_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
