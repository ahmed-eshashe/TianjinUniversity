"""Native block Cholesky application versus independent CPU solves."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Block-Jacobi check stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from warp import sparse
  from warp.optim.linear import cg
  from tomato_block_preconditioner import BlockJacobi
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');R=Rotation.from_rotvec([.4,-.3,.2]).as_matrix();write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,relative_error_budgets=[1e-10,1e-5,.001],positive_preconditioner_required=True,system_matrix_unchanged_required=True,relative_shift_start=1e-12,normalized_pivot_floor=1e-14,scope='Linear preconditioner only; source system matrix and physical force/energy remain unchanged.'))
  for label,eigen,budget in [('ordinary',[2.,20.,100.],1e-10),('anisotropic',[.01,200.,1e8],1e-5),('regularized',[1e-10,1.,1e18],.001)]:
   H=R@np.diag(eigen)@R.T;A=sparse.bsr_zeros(1,1,block_type=wp.mat33d,device='cuda:0');sparse.bsr_set_from_triplets(A,wp.zeros(1,dtype=int),wp.zeros(1,dtype=int),wp.array([H],dtype=wp.mat33d));before=A.values.numpy().copy();pre=BlockJacobi(A);scale=float(pre.scales.numpy()[0]);shift=float(pre.shifts.numpy()[0]);effective=H+scale*shift*np.eye(3);P=[]
   for axis in range(3):
    unit=np.eye(3)[axis];z=wp.zeros(1,dtype=wp.vec3d);pre.operator.matvec(wp.array([unit],dtype=wp.vec3d),z,z,1.,0.);P.append(z.numpy()[0])
   P=np.array(P).T;expected=np.linalg.solve(effective,np.eye(3));relative=float(np.linalg.norm(P-expected)/np.linalg.norm(expected));symmetry=float(np.linalg.norm(P-P.T)/np.linalg.norm(P));minimum=float(np.linalg.eigvalsh(P).min());unchanged=bool(np.array_equal(before,A.values.numpy()))
   if relative>budget or symmetry>1e-12 or minimum<=0 or not unchanged:raise ValueError((label,relative,budget,symmetry,minimum,unchanged))
   if label!='regularized':
    known=np.array([.3,-.2,.5]);rhs=wp.array([H@known],dtype=wp.vec3d);solution=wp.zeros(1,dtype=wp.vec3d);iterations,residual,tolerance=cg(A,rhs,solution,tol=1e-12,atol=1e-13,maxiter=50,M=pre.operator,check_every=1,use_cuda_graph=True);error=float(np.linalg.norm(solution.numpy()[0]-known)/np.linalg.norm(known))
    if error>1e-5:raise ValueError('Block preconditioned CG failed known solution')
   else:iterations=None;error=None
   cases.append(dict(case=label,relative_inverse_action_error=relative,relative_symmetry_error=symmetry,minimum_preconditioner_eigenvalue=minimum,relative_shift=shift,matrix_unchanged=unchanged,cg_iterations=iterations,cg_solution_relative_error=error))
  if not sources_unchanged(pins):raise ValueError('Preconditioner source changed')
  write(out,'block_preconditioner_measurements.json',dict(cases=cases,scope='Three native Cholesky/positive-regularization/application controls versus CPU solves, unchanged system matrix and known-solution PCG. No target stepping/support/cut qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,block_preconditioner_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
