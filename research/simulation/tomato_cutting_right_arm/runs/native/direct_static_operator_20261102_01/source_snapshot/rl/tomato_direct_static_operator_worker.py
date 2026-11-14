"""Captured complete search system, direct solve and known-solution controls."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Direct search controls stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  captured=ROOT/'runs/native/static_preparation_regularized_20261102_01/static_failure_state.npz';source=ROOT/'runs/native/global_gn_operator_20261102_01/rest_reference_inputs.npz';pins=capture_sources(out,[Path(__file__)],inputs=[captured,source])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from warp import sparse
  from tomato_direct_static import direct_direction
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');d=np.load(captured);ref=np.load(source);off=d['matrix_offsets'];n=len(off)-1;nn=int(off[-1]);rows=np.repeat(np.arange(n,dtype=np.int32),np.diff(off));columns=d['matrix_columns'][:nn];original=d['matrix_values'][:nn].copy();write(out,'input_manifest.json',dict(cases=3,newton_steps=0,deformable_steps=0,controlled_steps=0,physical_time_advanced_s=0.,true_residual_relative_budget=5e-9,true_residual_floor_n=1e-15,known_solution_maximum_absolute_budget_m=1e-10,source_nodes=n,source_blocks=nn,weak_regularizer_s=.02,system_matrix_must_remain_unchanged=True,scope='Numerical direct search solve only; no mechanics or equilibrium qualification.'))
  for label,weak,known in [('captured_regularized_rhs',False,False),('weaker_regularization_rhs',True,False),('weaker_known_solution',True,True)]:
   values=original.copy()
   if weak:
    for i in range(n):
     if ref['free'][i]:
      at=int(off[i]+np.flatnonzero(columns[off[i]:off[i+1]]==i)[0]);values[at]+=(ref['mass'][i]/.02**2-ref['mass'][i]/(1/2400)**2)*np.eye(3)
   A=sparse.bsr_zeros(n,n,block_type=wp.mat33d,device='cuda:0');sparse.bsr_set_from_triplets(A,wp.array(rows,dtype=int),wp.array(columns,dtype=int),wp.array(values,dtype=wp.mat33d));before_offsets=A.offsets.numpy().copy();valid_count=int(before_offsets[-1]);before=A.values.numpy()[:valid_count].copy();before_columns=A.columns.numpy()[:valid_count].copy();rhs=wp.array(d['force'],dtype=wp.vec3d);solution=wp.zeros(n,dtype=wp.vec3d);product=wp.zeros(n,dtype=wp.vec3d);expected=None
   if known:
    expected=(np.sin(np.arange(3*n)*.173)*1e-7).reshape(n,3);expected[~ref['free'].astype(bool)]=0;sparse.bsr_mv(A,wp.array(expected,dtype=wp.vec3d),rhs)
   info=direct_direction(A,rhs,solution,product);error=None if expected is None else float(abs(solution.numpy()-expected).max());unchanged=bool(np.array_equal(before_offsets,A.offsets.numpy())and np.array_equal(before_columns,A.columns.numpy()[:valid_count])and np.array_equal(before,A.values.numpy()[:valid_count]))
   if not info['linear_valid']or not unchanged or(error is not None and error>1e-10):raise ValueError((label,info,error,unchanged))
   cases.append(dict(case=label,**info,maximum_known_solution_error_m=error,matrix_unchanged=unchanged))
  if not sources_unchanged(pins):raise ValueError('Direct linear source changed')
  write(out,'direct_static_operator_measurements.json',dict(cases=cases,scope='Three captured full-registry direct search solves with unchanged matrix, independent actual GPU true residual and known solution. No physical steps/equilibrium/support/cutting claim.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,direct_static_operator_passed=passed,physical_time_advanced_s=0.,newton_steps=0,deformable_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
