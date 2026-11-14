"""Captured full coupled system: tight PCG versus independent sparse CPU LU."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Tight linear reference stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  source=ROOT/'runs/native/block_duration_20261102_01/nonlinear_failure_state.npz';pins=capture_sources(out,[Path(__file__)],inputs=[source])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy import sparse as cpu_sparse
  from scipy.sparse.linalg import splu
  from warp import sparse
  from warp.optim.linear import cg
  from tomato_block_preconditioner import BlockJacobi
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');d=np.load(source);off=d['matrix_offsets'];n=len(off)-1;nn=int(off[-1]);values=d['matrix_values'][:nn];cols=d['matrix_columns'][:nn];cpu=cpu_sparse.bsr_matrix((values,cols,off),shape=(3*n,3*n)).tocsc();lu=splu(cpu);A=sparse.bsr_zeros(n,n,block_type=wp.mat33d,device='cuda:0');rows=np.repeat(np.arange(n,dtype=np.int32),np.diff(off));sparse.bsr_set_from_triplets(A,wp.array(rows,dtype=int),wp.array(cols,dtype=int),wp.array(values,dtype=wp.mat33d));pre=BlockJacobi(A);before=A.values.numpy().copy();known=np.sin(np.arange(3*n)*.173)*1e-7;known[abs(cpu.diagonal()-1.)<1e-15]=0.;write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,captured_nodes=n,captured_block_nnz=nn,cg_relative_tolerance=1e-9,cg_absolute_tolerance_n=1e-16,true_residual_floor_n=1e-15,cpu_solution_absolute_budget_m=1e-10,scope='Captured full-registry linear system only. No dynamics or support pass.'))
  for label,b in [('captured_low_force',d['force'].ravel()),('smaller_force',d['force'].ravel()*.01),('known_coupled_solution',cpu@known)]:
   expected=lu.solve(b);rhs=wp.array(b.reshape(n,3),dtype=wp.vec3d);x=wp.zeros(n,dtype=wp.vec3d);it,recursive,tol=cg(A,rhs,x,tol=1e-9,atol=1e-16,maxiter=1000,M=pre.operator,check_every=10,use_cuda_graph=True);actual=x.numpy().ravel();residual=float(np.linalg.norm(cpu@actual-b));error=float(abs(actual-expected).max());threshold=max(5e-9*float(np.linalg.norm(b)),1e-15)
   if residual>threshold or error>1e-10 or not np.array_equal(before,A.values.numpy()):raise ValueError((label,residual,threshold,error))
   cases.append(dict(case=label,cg_iterations=int(it),rhs_norm_n=float(np.linalg.norm(b)),cpu_evaluated_true_residual_n=residual,maximum_cpu_solution_error_m=error))
  if not sources_unchanged(pins):raise ValueError('Tight linear source changed')
  write(out,'tight_linear_measurements.json',dict(cases=cases,scope='Three independently CPU-referenced tight absolute PCG controls on a captured complete 4032-node coupled matrix. No stepping/support/cut qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,tight_linear_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
