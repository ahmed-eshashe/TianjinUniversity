"""Full coupled sparse GN operator qualification; zero mechanical steps."""
import argparse,json,signal,subprocess,sys,time,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Global GN operator stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  refscript=ROOT/'rl/tomato_failed_safe_global_cpu_reference.py';failure=ROOT/'runs/native/block_duration_20261102_01/nonlinear_failure_state.npz';pins=capture_sources(out,[Path(__file__),refscript],inputs=[failure])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.sparse import bsr_matrix
  from warp import sparse
  from warp.optim.linear import cg,preconditioner
  from tomato_native_full_model import registry,configure_solver
  from tomato_board_support import nodal_plane_stiffness
  from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
  from tomato_relative_contact import RelativeSurfaceContact
  from tomato_failed_safe_global import FailedSafeFractionCandidate
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();data['x']+=[0,0,.002];fixed=np.array(data['design']['fixture']['node_ids']);model=build_relative_model(data,fixed_nodes=fixed);k=nodal_plane_stiffness(data);s=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k);zero=wp.zeros(model.particle_count,dtype=wp.vec3);e=s.surface_contact=RelativeSurfaceContact(data,s.spatial_reference,margin=.0001,capacity=256);e.physical_colors=model.particle_colors;candidate=FailedSafeFractionCandidate(s,data,fixed);assembler=candidate.assembly;n=len(data['x']);dt=1/4800;vectors=np.zeros((4,n,3));vectors[0]=np.random.default_rng(203).normal(size=(n,3));index=int(np.argmin(np.linalg.norm(data['x'][data['pairs'][:,0],1:]-[0,.0295],axis=1)));pa,pb=data['pairs'][index];vectors[1,[pa,pb],0]=1.;vectors[2,pa,0]=-1.;vectors[2,pb,0]=1.;vectors[3,:,2]=1.;vectors[:,fixed]=0
  write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,maximum_triplets=8388608,matrix_action_relative_budget=1e-7,matrix_action_absolute_budget_n_m=1e-6,symmetry_relative_budget=1e-12,linear_true_residual_relative_budget=2e-8,linear_solution_relative_budget=1e-5,cg_relative_tolerance=1e-10,cg_maximum_iterations=1000,scope='Prepared intact, partial and fully failed history: global force/energy/matrix routing controls with live eligibility disabled. Original physical values; no stepping, support or cutting pass.'))
  cap=np.unique(data['cells'][data['x'][data['cells']].mean(1)[:,0]<data['design']['cut_x_m']]);center=np.array([data['design']['cut_x_m'],0,.0295]);partial=data['x'].copy();partial[cap,0]-=.0005;failed=data['x'].copy();failed[cap]=(failed[cap]-center)@np.diag([1.,-1.,-1.])+center;failed[cap,0]-=.0045;positions=[('intact',data['x'].copy()),('prepared_partial',partial),('prepared_failed_rotation',failed)]
  for label,x in positions:
   if (out/'stop.request').exists():raise InterruptedError('Operator stop')
   history=np.zeros((s.pairs.shape[0],2));law=s.objective_law.numpy()
   if label=='prepared_partial':history[:,0]=.0015;history[:,1]=law[:,2]*(.0015-law[:,1])/(.0015*(law[:,2]-law[:,1]))
   if label=='prepared_failed_rotation':history[:,0]=.0045;history[:,1]=1.
   s.objective_history.assign(history);s.history.assign(history.astype(np.float32));s.eligible.zero_()
   started=time.monotonic();xw=wp.array(x,dtype=wp.vec3d);s.spatial_reference=xw;e.reference=xw;e.invalid.zero_();s.volume_invalid.zero_();e.detect(zero);e.evaluate(zero,dt);candidate.target.assign(x);candidate.force(xw,dt);native_energy=candidate.energy(xw,dt);counts=assembler.assemble(xw,dt);wp.synchronize()
   if e.invalid.numpy()[0] or s.volume_invalid.numpy()[0]:raise ValueError('Invalid source geometry for global operator')
   A=assembler.matrix;offsets=A.offsets.numpy();nnz=int(offsets[-1]);columns=A.columns.numpy()[:nnz];values=A.values.numpy()[:nnz];cpu=bsr_matrix((values,columns,offsets),shape=(3*n,3*n)).tocsr();difference=cpu-cpu.T;sym=float(np.max(abs(difference.data),initial=0)/max(np.max(abs(cpu.data)),1e-30));products=[]
   for v in vectors:
    z=wp.zeros(n,dtype=wp.vec3d);sparse.bsr_mv(A,wp.array(v,dtype=wp.vec3d),z);products.append(z.numpy())
   products=np.array(products);quadratic=np.einsum('kni,kni->k',vectors,products)
   if sym>1e-12 or np.any(quadratic<=0):raise ValueError(('Global matrix symmetry/positivity failed',label,sym,quadratic))
   query_count=int(e.stencil_count.numpy()[0]);reference_path=out/f'{label}_reference_inputs.npz';np.savez(reference_path,source_x=data['x'],target=x,law=s.objective_law.numpy(),native_energy=np.array([native_energy]),x=x,vectors=vectors,matrix_products=products,free=assembler.free.numpy(),mass=data['mass'],dt=np.array([dt]),spring_k=data['k'],spring_rest=s.relative_spring_rest.numpy(),spring_pairs=data['springs'],cells=data['cells'],volumes=data['volumes'],cohesive_pairs=s.pairs.numpy(),cohesive_counts=s.counts.numpy(),anchors=s.objective_anchors.numpy(),sign=s.objective_sign.numpy(),weights=s.objective_weights.numpy(),local_k=s.objective_stiffness.numpy(),history=s.objective_history.numpy(),eligible=s.eligible.numpy(),proxy=e.precise_position.numpy(),endpoint=e.endpoint.numpy()[:query_count],kind=e.kind.numpy()[:query_count],threshold=e.mollifier_threshold.numpy()[:query_count],physical_ids=e.physical_ids.numpy()[:query_count],endpoint_weight=e.endpoint_weight.numpy()[:query_count],radius=np.array([e.margin]),contact_k=np.array([e.model.soft_contact_ke]),board_k=s.board_stiffness.numpy(),board_height=np.array([s.board_height]));reference_output=out/f'{label}_cpu_reference.json'
   with (out/f'{label}_cpu_reference.log').open('w')as log:result=subprocess.run([sys.executable,str(refscript),'--input',str(reference_path),'--output',str(reference_output)],stdout=log,stderr=subprocess.STDOUT,timeout=180,check=False)
   if result.returncode or not json.loads(reference_output.read_text())['passed']:raise ValueError('Independent full coupled matrix action failed: '+label)
   rhs=wp.array(products[0],dtype=wp.vec3d);solution=wp.zeros(n,dtype=wp.vec3d);pc=preconditioner(A,'diag');iterations,residual,tolerance=cg(A,rhs,solution,tol=1e-10,atol=1e-12,maxiter=1000,M=pc,check_every=10,use_cuda_graph=True);true=wp.zeros(n,dtype=wp.vec3d);sparse.bsr_mv(A,solution,true);true_relative=float(np.linalg.norm(true.numpy()-products[0])/np.linalg.norm(products[0]));solution_relative=float(np.linalg.norm(solution.numpy()-vectors[0])/np.linalg.norm(vectors[0]));row=dict(case=label,**counts,nnz_blocks=nnz,relative_symmetry_error=sym,quadratic_forms=quadratic.tolist(),cg_iterations=int(iterations),cg_recursive_residual=float(residual),cg_absolute_tolerance=float(tolerance),cg_true_relative_residual=true_relative,cg_solution_relative_error=solution_relative,wall_s=time.monotonic()-started)
   if true_relative>2e-8 or solution_relative>1e-5:write(out,'linear_failure.json',row);raise ValueError('Global linear solve failed independent true-residual/known-solution gate')
   cases.append(row);write(out,'failed_safe_global_operator_partial.json',dict(cases=cases))
  if not sources_unchanged(pins):raise ValueError('Global operator source changed')
  write(out,'failed_safe_global_operator_measurements.json',dict(cases=cases,scope='Three prepared-history full-registry force/energy/matrix-routing controls, independent CPU values/actions, symmetry/positive forms and known-solution PCG. Failed rotation avoids vanished frames. Zero stepping, no live-fracture/robot/cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,failed_safe_global_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
