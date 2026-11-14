"""Prescribed full-registry history/reclosure fixture; no performed cutting."""
import argparse,hashlib,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('History/reclosure fixture stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_objective_full_model import configure_objective,ObjectiveTomatoVBD
  from tomato_objective_cohesion_reference import make_patch,response
  from tomato_native_objective_reference import objective_force
  from tomato_fast_mollified_contact import FastMollifiedEmbeddedSelfContact
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);solver=configure_objective(configure_solver(model,data,iterations=1,solver_class=ObjectiveTomatoVBD),data);engine=FastMollifiedEmbeddedSelfContact(data,margin=.0001);rest=data['x'];right=np.unique(data['cells'][rest[data['cells']].mean(1)[:,0]>data['design']['cut_x_m']]);left=np.setdiff1d(np.arange(len(rest)),right);patches=data['cohesion'].patches;references=[];old=np.zeros((len(patches),2));state=model.state();physical=wp.array(rest,dtype=wp.vec3)
  for patch in patches:
   l=patch['law'];references.append(make_patch(rest[data['pairs'][patch['indices']]],patch['weights'],patch['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m)))
  solver.eligible.fill_(1);partial_closure=None
  def evaluate_force(pos):
   solver.objective_x.assign(pos);solver.objective_force.zero_();wp.launch(objective_force,dim=len(patches),inputs=[solver.objective_x,solver.pairs,solver.counts,solver.objective_anchors,solver.objective_sign,solver.objective_weights,solver.objective_stiffness,solver.objective_law,solver.objective_history,solver.eligible],outputs=[solver.objective_force]);wp.synchronize();return solver.objective_force.numpy().copy()
  for label,gap in [('partial_load',.0015),('unload',.0005),('partial_reclosure',-.00001),('full_failure',.0045),('failed_reclosure',-.00001),('reset_clear',0.)]:
   if (out/'stop.request').exists():raise InterruptedError('Stop before history fixture case')
   if label=='reset_clear':solver.reset_material();solver.eligible.fill_(1);engine.invalid.zero_();old[:]=0
   pos=rest.copy();pos[right,0]+=gap;pos=pos.astype(np.float32).astype(float);reference_force=np.zeros_like(pos);expected=[]
   for i,m in enumerate(references):
    ids=data['pairs'][patches[i]['indices']];result=response(pos[ids],m,history=tuple(old[i]),eligible=True);np.add.at(reference_force,ids.ravel(),result['force_n'].reshape(-1,3));expected.append(result['trial_history'])
   f=evaluate_force(pos);force_error=float(abs(f-reference_force).max());unchanged=bool(np.array_equal(solver.objective_history.numpy(),old));state.particle_q.assign(pos);solver.commit_cohesion(state);history=solver.objective_history.numpy();history_error=float(abs(history-expected).max());mirror_error=float(abs(solver.history.numpy()-history).max());physical.assign(pos);engine.invalid.zero_();engine.detect(physical);engine.evaluate(physical,1/2400);wp.synchronize();contact=engine.physical_force.numpy();contact_left=float(contact[left,0].sum());peak=float(np.linalg.norm(contact,axis=1).max())
   row=dict(id=label,imposed_gap_m=gap,force_reference_error_n=force_error,history_reference_error=history_error,mirror_error=mirror_error,minimum_damage=float(history[:,1].min()),maximum_damage=float(history[:,1].max()),trial_did_not_commit=unchanged,closure_contact_left_x_n=contact_left,contact_peak_n=peak,contact_invalid=int(engine.invalid.numpy()[0]))
   if force_error>1e-8 or history_error>1e-10 or mirror_error>1e-7 or not unchanged or row['contact_invalid']:raise ValueError('Material history/reference mismatch '+str(row))
   if label=='partial_load':
    saved=history.copy();candidate=rest.copy();candidate[right,0]+=.0045;evaluate_force(candidate)
    row['rejected_failure_trial_preserved_history']=bool(np.array_equal(saved,solver.objective_history.numpy()))
    if not row['rejected_failure_trial_preserved_history']:raise ValueError('Rejected trial damaged committed state')
   if label in ['unload','partial_reclosure'] and not np.allclose(history[:,1],old[:,1],atol=1e-12,rtol=0):raise ValueError('Unloading/compression changed damage')
   if label.endswith('reclosure'):
    if contact_left>=-1e-4 or np.linalg.norm(f)>1e-8:raise ValueError('Compression not carried by closure contact alone')
    if label=='partial_reclosure':partial_closure=contact.copy()
    else:
     row['closure_contact_damage_independence_n']=float(abs(contact-partial_closure).max())
     if row['closure_contact_damage_independence_n']>1e-7:raise ValueError('Failed material disabled reclosure contact')
   if label=='full_failure' and history[:,1].min()!=1:raise ValueError('Prescribed complete material failure missing')
   if label=='reset_clear' and (history.max()!=0 or peak>1e-5):raise ValueError('Material/contact reset left stale state')
   old=history.copy();cases.append(row);write(out,'material_history_partial.json',dict(cases=cases))
  files=[Path(__file__)]+[ROOT/'rl'/name for name in ['tomato_objective_full_model.py','tomato_native_objective_reference.py','tomato_objective_cohesion_reference.py','tomato_fast_mollified_contact.py','tomato_mollified_self_contact.py']];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};snapshot=out/'source_snapshot';snapshot.mkdir(exist_ok=True,parents=True)
  for p in files:(snapshot/p.name).write_bytes(p.read_bytes())
  write(out,'material_history_measurements.json',dict(cases=cases,source_sha256=pins,scope='Full saved material registry under prescribed compatible piece translations and explicit test eligibility. Verifies history, rejected-trial isolation, partial/failed reclosure and reset operators. Zero mechanical steps; no blade eligibility or performed separation claim.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,material_history_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
