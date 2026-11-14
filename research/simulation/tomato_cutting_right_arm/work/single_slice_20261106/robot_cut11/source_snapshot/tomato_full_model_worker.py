"""Protected actual 4032-node spring/barrier/interface assembly qualification."""
import argparse,signal,traceback,hashlib
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=0;records=[];probes=0
 def stop(*args):raise InterruptedError('Full model check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,warp as wp
  from tomato_native_full_model import registry,build_model,configure_solver,volume_blocks,SOURCE
  from tomato_native_group_cohesion import group_blocks
  from tomato_volume_protection import ProtectedModel
  from tomato_surface_cohesion import patch_response
  wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);solver=configure_solver(model,data,iterations=16);sin=model.state();sout=model.state();original=model.particle_q.numpy().copy()
  write(out,'topology.json',dict(nodes=model.particle_count,springs=model.spring_count,triangles=model.tri_count,volume_cells=len(data['cells']),patches=len(data['cohesion'].patches),colors=len(data['colors']),mass_kg=float(sum(data['mass'])),source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'surface_design.json',SOURCE/'mass_stiffness_assignments.json']},same_bulk_law=True,frame='fixed world X normal; no general rotating material frame'))
  solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1
  drift=float(np.max(np.abs(sout.particle_q.numpy()-original)));speed=float(np.max(np.abs(sout.particle_qd.numpy())))
  if drift>1e-7 or speed>2e-5:raise ValueError(f'Full rest drift {drift=}, {speed=}')
  solver.commit_cohesion(sout);records.append(dict(id='actual_model_rest',position_error_m=drift,velocity_error_m_s=speed))
  # Independent offline barrier model; only one tet isolated for a controlled J=.3 contraction.
  tet=data['cells'][0];x=original.copy().astype(float);anchor=x[tet[0]].copy();x[tet[1:]]=anchor+(.3**(1/3))*(x[tet[1:]]-anchor)
  v=data['volumes'][:1];dummy=[i for i in range(len(original)) if i not in tet][:2];reference=ProtectedModel(original,np.array([dummy]),np.array([np.linalg.norm(original[dummy[1]]-original[dummy[0]])]),np.array([1.]),data['cells'][:1],v)
  ref=reference.evaluate(x,tangent=True);sin.particle_q.assign(wp.array(x,dtype=wp.vec3));force=wp.zeros(model.particle_count,dtype=wp.vec3);hess=wp.zeros(model.particle_count,dtype=wp.mat33)
  cell=wp.array(data['cells'][:1],dtype=wp.vec4i);vol=wp.array(v,dtype=float)
  for color in range(len(data['colors'])):wp.launch(volume_blocks,dim=1,inputs=[color,model.particle_colors,sin.particle_q,cell,vol,solver.volume_invalid],outputs=[force,hess])
  wp.synchronize();rounded=sin.particle_q.numpy().astype(float);ref=reference.evaluate(rounded,tangent=True);ferr=float(np.max(np.abs(force.numpy()+ref['gradient_n'])));herr=max(float(np.max(np.abs(hess.numpy()[node]-ref['tangent_n_m'][3*node:3*node+3,3*node:3*node+3].toarray()))) for node in tet)
  probes+=1
  if ferr>1e-5 or herr>1e-3:raise ValueError(f'Bulk barrier mismatch {ferr=}, {herr=}')
  from tomato_native_full_gather import adjacency
  from tomato_nonlinear_checks import spring_state
  old_adjacency=(solver.cell_offsets,solver.cell_ids);solver.cell_offsets,solver.cell_ids=adjacency(data['cells'][:1],model.particle_count)
  for color in range(len(data['colors'])):solver._gather_blocks(color,sin,DT)
  wp.synchronize();bulk=spring_state(rounded,model.spring_indices.numpy().reshape(-1,2),model.spring_rest_length.numpy().astype(float),model.spring_stiffness.numpy().astype(float),tangent=True);cohesive=data['cohesion'].evaluate(rounded,tangent=True);expected_gradient=bulk['gradient_n']+cohesive['gradient_n']+ref['gradient_n'];gather_ferr=float(np.max(np.abs(solver.particle_forces.numpy()+expected_gradient)))
  expected_hessian=bulk['tangent_n_m']+cohesive['tangent_n_m']+ref['tangent_n_m'];gather_herr=max(float(np.max(np.abs(solver.particle_hessians.numpy()[node]-expected_hessian[3*node:3*node+3,3*node:3*node+3].toarray()))) for node in tet)
  solver.cell_offsets,solver.cell_ids=old_adjacency
  if gather_ferr>1e-5 or gather_herr>1e-3:raise ValueError(f'Full bulk/cohesion/barrier gather {gather_ferr=}, {gather_herr=}')
  records.append(dict(id='original_volume_barrier',force_error_n=ferr,hessian_error_n_m=herr,node_gather_force_error_n=gather_ferr,node_gather_hessian_error_n_m=gather_herr,ratio=ref['min_cell_ratio']))
  # Full-patch forces, shared history and one area budget, no hand-selected patch subset.
  right=np.asarray([n['side']=='remainder' for n in data['design']['nodes']]);opening_results=[]
  for opening in (.0005,.002,.0045):
   x=original.copy();x[right,0]+=opening;sin.particle_q.assign(wp.array(x,dtype=wp.vec3));solver.history.zero_();solver.eligible.fill_(1);solver.invalid.zero_();force.zero_();hess.zero_()
   for color in range(len(data['colors'])):wp.launch(group_blocks,dim=len(data['cohesion'].patches),inputs=[color,model.particle_colors,sin.particle_q,solver.pairs,solver.rest,solver.weights,solver.counts,solver.nodes,solver.node_counts,solver.stiffness,solver.law,solver.history,solver.eligible,solver.invalid],outputs=[force,hess])
   wp.synchronize();expected=np.zeros_like(x,dtype=float);gaps=sin.particle_q.numpy()[data['pairs'][:,1]]-sin.particle_q.numpy()[data['pairs'][:,0]]-np.asarray(data['cohesion'].reference_gaps,dtype=np.float32)
   damage=[]
   from tomato_bonds import DamageState,update_damage
   for patch in data['cohesion'].patches:
    ids=patch['indices'];law=patch['law'];u=patch_response(gaps[ids],patch['weights'],patch['stiffness'],0.)['energy_j'];q=(2*u/law.stiffness_n_m)**.5;state=update_damage(law,DamageState(),q,eligible=True);damage.append(state.damage);r=patch_response(gaps[ids],patch['weights'],patch['stiffness'],state.damage)
    np.add.at(expected,data['pairs'][ids,0],r['gradient_n']);np.add.at(expected,data['pairs'][ids,1],-r['gradient_n'])
   error=float(np.max(np.abs(force.numpy()-expected)))
   from tomato_nonlinear_checks import spring_state
   bulk=spring_state(sin.particle_q.numpy().astype(float),model.spring_indices.numpy().reshape(-1,2),model.spring_rest_length.numpy().astype(float),model.spring_stiffness.numpy().astype(float))
   for color in range(len(data['colors'])):solver._gather_blocks(color,sin,DT)
   wp.synchronize();gather_error=float(np.max(np.abs(solver.particle_forces.numpy()-(expected-bulk['gradient_n']))))
   if gather_error>1e-5:raise ValueError(f'Actual node gather differs from independent assembly {gather_error=}')
   solver.commit_cohesion(sin);wp.synchronize();derr=float(np.max(np.abs(solver.history.numpy()[:,1]-damage)));probes+=1
   if error>1e-5 or derr>1e-6:raise ValueError(f'Actual patch registry mismatch {error=}, {derr=}')
   opening_results.append(dict(opening_m=opening,max_force_error_n=error,node_gather_force_error_n=gather_error,max_damage_error=derr,failed_patches=int(sum(solver.history.numpy()[:,1]==1.))))
  if opening_results[-1]['failed_patches']!=47:raise ValueError('Missing actual damage patches')
  records.append(dict(id='all_actual_patches',probes=opening_results))
  baseline=[];replay=[]
  def reset():
   solver.history.zero_();solver.eligible.zero_();solver.invalid.zero_();solver.volume_invalid.zero_();pos=original.copy();pos[right,0]+=.00001
   for state in (sin,sout):state.particle_q.assign(wp.array(pos,dtype=wp.vec3));state.particle_qd.zero_();state.clear_forces()
   solver.particle_q_prev.assign(wp.array(pos,dtype=wp.vec3))
  for episode,trace in enumerate((baseline,replay)):
   reset()
   for i in range(4):
    if (out/'stop.request').exists():raise InterruptedError('Stopped in actual mesh sequence')
    solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1;solver.commit_cohesion(sout)
    x=sout.particle_q.numpy();vel=sout.particle_qd.numpy()
    ratios=np.linalg.det(x[data['cells'][:,1:]]-x[data['cells'][:,:1]])/(6*data['volumes'])
    if not np.isfinite(x).all() or min(ratios)<=.1 or np.max(np.abs(vel))>1.:raise ValueError('Actual mesh integration admissibility failed')
    trace.append(dict(x=x.tolist(),v=vel.tolist(),min_ratio=float(min(ratios))));sin,sout=sout,sin
  replay_errors=dict(position_m=float(np.max(np.abs(np.array([r['x'] for r in baseline])-np.array([r['x'] for r in replay])))),velocity_m_s=float(np.max(np.abs(np.array([r['v'] for r in baseline])-np.array([r['v'] for r in replay])))))
  write(out,'full_model_partial.json',dict(cases=records,replay_errors=replay_errors,baseline=baseline,replay=replay))
  if baseline!=replay:raise ValueError('Deterministic actual mesh reset/replay differs')
  records.append(dict(id='full_mesh_implicit_sequence_and_replay',intervals=4,min_ratio=min(r['min_ratio'] for r in baseline),exact_replay=baseline==replay,replay_errors=replay_errors,history_unchanged=bool(np.all(solver.history.numpy()==0.))))
  write(out,'full_model_measurements.json',dict(cases=records,steps=steps,probes=probes,sequence=baseline,scope='Actual saved spring/barrier/fixed-frame cohesive assembly. No knife, robot, rotating-frame or experiment qualification.'))
  if steps!=9 or probes!=4 or len(records)!=4:raise ValueError('Unexpected full-model check count')
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,full_model_passed=passed,newton_steps=steps,controlled_steps=steps,full_model_cases=len(records),material_probes=probes))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
