"""Whole-surface proxy contact operator audit; no mechanical integration."""
import argparse,hashlib,json,signal,time,traceback
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--mollified',action='store_true');p.add_argument('--fast',action='store_true');args=p.parse_args();out=args.output;app=None;passed=False;records=[]
 def stop(*args):raise InterruptedError('Embedding contact audit stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from scipy.spatial.transform import Rotation
  from tomato_native_full_model import registry
  from tomato_embedded_self_contact import EmbeddedSelfContact
  from tomato_mollified_self_contact import MollifiedEmbeddedSelfContact
  from tomato_fast_mollified_contact import FastMollifiedEmbeddedSelfContact
  from tomato_collision_embedding import mapped_positions,mapped_force
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');data=registry();x0=data['x'];left=np.unique(data['cells'][x0[data['cells']].mean(1)[:,0]<data['design']['cut_x_m']]);right=np.setdiff1d(np.arange(len(x0)),left);q=Rotation.from_rotvec([.3,.4,-.2]).as_matrix();random_velocity=np.random.default_rng(42).normal(size=x0.shape)*.001
  for margin in [.0001,.00005,.000025]:
   start=time.monotonic();engine=(FastMollifiedEmbeddedSelfContact if args.fast else MollifiedEmbeddedSelfContact if args.mollified else EmbeddedSelfContact)(data,margin=margin);setup_wall=time.monotonic()-start;physical=wp.array(x0,dtype=wp.vec3);colors=wp.zeros(len(x0),dtype=int);base_force=None;compression=[]
   for label,delta,rotated in [('rest',0.,False),('compression1',.1*margin,False),('compression2',.2*margin,False),('open',-.004,False),('rotated_compression',.1*margin,True),('reset_clear',0.,False)]:
    if (out/'stop.request').exists():raise InterruptedError('Guard stop before embedding case')
    pos=x0.copy();pos[left,0]+=delta
    if rotated:pos=pos@q.T+[.01,.02,.03]
    physical.assign(pos);engine.invalid.zero_();engine.detect(physical);wp.synchronize()
    if int(engine.invalid.numpy()[0]):raise ValueError('Contact proxy zero distance or saturated detector')
    engine.evaluate(physical,1/2400);f=wp.zeros(len(x0),dtype=wp.vec3);h=wp.zeros(len(x0),dtype=wp.mat33);engine.scatter(-1,colors,f,h);wp.synchronize();force=f.numpy().astype(float);engine_force=engine.physical_force.numpy().copy();proxy_force=engine.force.numpy().astype(float);proxy_pos=engine.state.particle_q.numpy().astype(float);reference=mapped_force(proxy_force,engine.embedding,len(pos));mapping_error=float(np.max(np.abs(force-reference)));balance=float(np.linalg.norm(force.sum(0)));moment=float(np.linalg.norm(np.cross(pos,force).sum(0)));scale=float(np.linalg.norm(force,axis=1).sum());moment_scale=float(np.linalg.norm(np.cross(pos,force),axis=1).sum());power=abs(float(np.sum(force*random_velocity)-np.sum(proxy_force*mapped_positions(random_velocity,engine.embedding))));net=float(force[left,0].sum());peak=float(np.linalg.norm(force,axis=1).max());info=engine.solver.trimesh_collision_detector.collision_info
    row=dict(margin_m=margin,id=label,net_left_force_x_n=net,peak_nodal_force_n=peak,total_absolute_force_n=scale,force_balance_n=balance,moment_balance_nm=moment,mapping_force_error_n=mapping_error,virtual_power_error_w=power,vertex_triangle_candidates=int(info.vertex_colliding_triangles_count.numpy().sum()),edge_edge_candidates=int(info.edge_colliding_edges_count.numpy().sum()),minimum_physical_motion_bound_m=float(engine.bounds.numpy().min()),maximum_proxy_recession_m=engine.embedding['maximum_recession_m'],local_filters=engine.local_filter_counts,setup_wall_s=setup_wall)
    if not np.isfinite(force).all() or mapping_error>1e-5+1e-6*scale or balance>2e-5+1e-6*scale or moment>2e-6+1e-6*moment_scale or power>1e-8+1e-6*abs(float(np.sum(force*random_velocity))):raise ValueError('Embedding contact force/moment/work mapping failed '+str(row))
    if label in ['rest','open','reset_clear'] and peak>1e-5:raise ValueError('Rest/clear proxy contact preload '+str(row))
    if label.startswith('compression'):
     if net>=-1e-4:raise ValueError('Missing repulsion against physical cut-face closure')
     compression.append(abs(net))
    if label=='compression1':base_force=force.copy()
    if rotated:
     covariance_error=float(np.linalg.norm(force-base_force@q.T));covariance_scale=float(np.linalg.norm(base_force));row['force_rotation_error_n']=covariance_error
     if covariance_error>.01*covariance_scale+1e-4:raise ValueError('Embedding force rotation mismatch '+str(row))
    if args.fast:
     fast_force=engine.physical_force.numpy().copy();fast_blocks=engine.physical_hessian.numpy().copy();fast_energy=float(engine.contact_energy.numpy()[0]);MollifiedEmbeddedSelfContact.evaluate(engine,physical,1/2400);wp.synchronize()
     force_error=float(np.max(abs(fast_force-engine.physical_force.numpy())));block_error=float(np.max(abs(fast_blocks-engine.physical_hessian.numpy())));energy_error=abs(fast_energy-float(engine.contact_energy.numpy()[0]));row['fast_equivalence']=dict(force_error_n=force_error,block_error_n_m=block_error,energy_error_j=energy_error)
     if force_error>1e-8 or block_error>1e-5 or energy_error>1e-12:raise ValueError('Cached contact embedding is not equivalent '+str(row))
     engine.evaluate(physical,1/2400)
    if args.mollified and label=='compression1':
     # Central finite work uses the ACTUAL float32 endpoints, not nominal h*v.
     # Candidate identities remain fixed; closest features and mollifier update.
     derivatives=[]
     for direction in ['normal','tangent','random']:
      velocity=np.zeros_like(pos)
      if direction=='normal':velocity[left,0]=1.
      elif direction=='tangent':velocity[left,1]=1.
      else:velocity=random_velocity/np.max(np.abs(random_velocity))
      for step in [2e-7,1e-7,5e-8]:
       plus=(pos+step*velocity).astype(np.float32);minus=(pos-step*velocity).astype(np.float32)
       energies=[]
       for endpoint in [plus,minus]:
        physical.assign(endpoint);engine.evaluate(physical,1/2400);wp.synchronize();energies.append(float(engine.contact_energy.numpy()[0]))
       predicted=-float(np.sum(engine_force*(plus.astype(float)-minus.astype(float))))
       observed=energies[0]-energies[1];relative=abs(observed-predicted)/max(abs(predicted),abs(observed),1e-12)
       derivatives.append(dict(direction=direction,step_m=step,energy_difference_j=observed,negative_force_work_j=predicted,relative_error=relative))
     row['current_geometry_work_audit']=derivatives
     # Nonsmooth feature transitions can reduce centered convergence order.
     for direction in ['normal','tangent','random']:
      tests=[d for d in derivatives if d['direction']==direction]
      if min(abs(d['energy_difference_j']-d['negative_force_work_j']) for d in tests)>1e-10 and min(d['relative_error'] for d in tests)>.02:raise ValueError('Current contact force is not potential gradient '+str(tests))
     physical.assign(pos);engine.evaluate(physical,1/2400)
    records.append(row);write(out,'embedding_contact_partial.json',dict(cases=records))
   if compression[1]<=compression[0]:raise ValueError('Nonmonotone closing-force control')
  write(out,'embedding_contact_measurements.json',dict(cases=records,physical_mesh_unchanged=True,contact_model='mollified current geometry' if args.mollified else 'frozen stencil',scope='All saved surface triangles and explicit edges: rest, closure, opening, rotation and contact reset at three proxy resolutions. Operator qualification only; no physical integration, blade, fracture or support-duration claim.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'rl/tomato_embedded_self_contact.py',ROOT/'rl/tomato_collision_embedding.py',ROOT/'rl/tomato_collision_local_filters.py',ROOT/'rl/tomato_canonical_self_contact.py',ROOT/'rl/tomato_mollified_self_contact.py',ROOT/'rl/tomato_fast_mollified_contact.py']}));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,embedding_contact_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(records)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
