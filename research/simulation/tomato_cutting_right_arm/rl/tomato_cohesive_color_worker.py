"""Color-only cohesive force/GN blocks against independent references."""
import argparse,signal,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_evidence_snapshot import capture_sources,sources_unchanged
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Color cohesive audit stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  reference_path=ROOT/'work/integration_20261102/objective_gn_extended_reference.npz';pins=capture_sources(out,[Path(__file__)],inputs=[reference_path])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_native_full_model import registry,build_model,configure_solver
  from tomato_objective_full_model import configure_objective
  from tomato_objective_cohesion_reference import make_patch,response
  from tomato_objective_gn_compact import objective_gn
  from tomato_cohesive_color_blocks import cohesive_color_blocks
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();model=build_model(data);s=configure_objective(configure_solver(model,data,iterations=1),data);ref=np.load(reference_path);patches=data['cohesion'].patches;models=[]
  for patch in patches:
   l=patch['law'];models.append(make_patch(data['x'][data['pairs'][patch['indices']]],patch['weights'],patch['stiffness'],(l.onset_m,l.failure_m,l.stiffness_n_m)))
  base=['rest','tensile','mixed_open','mixed_compressed','rotated_mixed','pure_compression','nonaffine_open','nonaffine_compressed'];labels=base+['unload_damaged','inactive_mixed','failed_history'];f=wp.zeros(len(data['x']),dtype=wp.vec3d);h=wp.zeros(len(data['x']),dtype=wp.mat33d)
  for label in labels:
   if (out/'stop.request').exists():raise InterruptedError('Stop before color cohesive case')
   geometry=label if label in base else 'tensile' if label=='unload_damaged' else 'mixed_open';pos=ref[geometry+'_positions'];history=np.zeros((len(patches),2));eligible=label!='inactive_mixed'
   if label in ['unload_damaged','failed_history']:
    damage=.8 if label=='unload_damaged' else 1.
    for i,m in enumerate(models):history[i]=[m['onset']*m['failure']/(m['failure']-damage*(m['failure']-m['onset'])),damage]
   s.objective_x.assign(pos);s.objective_history.assign(history);s.eligible.fill_(int(eligible));common=[s.objective_x,s.pairs,s.counts,s.objective_anchors,s.objective_sign,s.objective_weights,s.objective_stiffness,s.objective_law,s.objective_history,s.eligible];f.zero_();h.zero_();wp.launch(cohesive_color_blocks,dim=(len(patches),16),inputs=[-1,model.particle_colors,*common],outputs=[f,h],block_dim=32);wp.synchronize();full_force=f.numpy().copy();full_h=h.numpy().copy();expected_force=np.zeros_like(pos)
   for i,m in enumerate(models):
    ids=data['pairs'][patches[i]['indices']];result=response(pos[ids],m,history=tuple(history[i]),eligible=eligible);np.add.at(expected_force,ids.ravel(),result['force_n'].reshape(-1,3))
   block_reference='independent CPU local-gap Jacobian'
   if label in base:expected_h=ref[geometry+'_blocks']
   elif label=='unload_damaged':expected_h=.2*ref['tensile_blocks']
   elif label=='failed_history':expected_h=np.zeros_like(full_h)
   else:
    legacy=wp.zeros(len(pos),dtype=wp.mat33d);wp.launch(objective_gn,dim=(len(patches),16),inputs=common,outputs=[legacy],block_dim=32);wp.synchronize();expected_h=legacy.numpy();block_reference='previous independently qualified GN operator, with eligibility disabled'
   fe=float(abs(full_force-expected_force).max());he=float(abs(full_h-expected_h).max());f.zero_();h.zero_()
   for color in range(len(data['colors'])):wp.launch(cohesive_color_blocks,dim=(len(patches),16),inputs=[color,model.particle_colors,*common],outputs=[f,h],block_dim=32)
   wp.synchronize();cfe=float(abs(f.numpy()-full_force).max());che=float(abs(h.numpy()-full_h).max());force_balance=float(np.linalg.norm(full_force.sum(0)));moment=float(np.linalg.norm(np.cross(pos,full_force).sum(0)));unchanged=bool(np.array_equal(s.objective_history.numpy(),history));row=dict(id=label,force_reference_error_n=fe,block_reference_error_n_m=he,color_force_error_n=cfe,color_block_error_n_m=che,force_balance_n=force_balance,moment_balance_nm=moment,history_unchanged=unchanged,block_reference=block_reference)
   if fe>1e-8 or he>1e-6 or cfe>1e-8 or che>1e-6 or force_balance>1e-8 or moment>1e-9 or not unchanged:raise ValueError('Color-only cohesive force/block mismatch '+str(row))
   cases.append(row);write(out,'cohesive_color_partial.json',dict(cases=cases))
  if not sources_unchanged(pins):raise ValueError('Color cohesive sources changed')
  write(out,'cohesive_color_measurements.json',dict(cases=cases,source_unchanged=True,scope='Equivalent color-only force and positive GN assembly. Eleven static fixtures, including nonaffine deformation, unloading, ineligible loading and failed history. No dynamic or cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,cohesive_color_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
