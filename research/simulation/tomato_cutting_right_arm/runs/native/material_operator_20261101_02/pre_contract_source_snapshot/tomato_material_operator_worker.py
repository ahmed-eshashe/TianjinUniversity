"""Guarded native fixed-frame cohesive operator qualification, no robot/blade."""
import argparse,hashlib,traceback,signal,math
from pathlib import Path
from tomato_isaac_startup_worker import write
from tomato_bonds import CohesiveLaw,DamageState,update_damage
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output
 app=None;passed=False;steps=probes=0;records=[]
 def stop(*args):raise InterruptedError('Material diagnostic stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 def result():return dict(shutdown_requested=app is not None,diagnostic_passed=passed,material_checks_passed=passed,material_cases_completed=len(records),newton_steps=steps,controlled_steps=steps,constitutive_probes=probes,robot_validated=False,material_calibrated=False)
 try:
  write(out,'input_manifest.json',dict(source_sha256={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [Path(__file__),ROOT/'rl/tomato_native_cohesive_operator.py',ROOT/'rl/tomato_bonds.py',ROOT/'rl/tomato_isaac_startup_guard.py']},step_cap=6,scope='One-pair fixed-frame implicit cohesion, synthetic constants, no blade eligibility detector.'))
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import warp as wp
  import newton
  import newton.solvers
  from tomato_native_cohesive_operator import CohesiveVBD,cohesive_blocks
  wp.init();wp.set_device('cuda:0')
  scenarios=[('elastic',.0005,.01,0.,0.,1),('active_softening',.0011,.02,.001,0.,1),('unloading',.001,-.01,.002,2/3,1),('failed',.004,.01,.004,1.,1),('ineligible',.0015,.01,0.,0.,0),('compression',-.0005,-.01,0.,0.,1)]
  law=CohesiveLaw(100.,.01,10.,.02,0.)
  for name,gap,velocity,kappa,damage,eligible in scenarios:
   if (out/'stop.request').exists():raise InterruptedError('Stopped between material cases')
   builder=newton.ModelBuilder(gravity=(0.,0.,0.));builder.add_particle(wp.vec3(0.),wp.vec3(0.),0.)
   builder.add_particle(wp.vec3(.001+gap,0.,0.),wp.vec3(velocity,0.,0.),.001)
   builder.add_spring(0,1,0.,0.,0.);builder.color();model=builder.finalize(device='cuda:0')
   solver=CohesiveVBD(model,iterations=16);sin=model.state();sout=model.state()
   pairs=wp.array([[0,1]],dtype=wp.vec2i);rest=wp.array([[.001,0,0]],dtype=wp.vec3);k=wp.array([[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]],dtype=wp.mat33)
   laws=wp.array([[100.,.001,.004]],dtype=wp.vec3);history=wp.array([[kappa,damage]],dtype=wp.vec2);elig=wp.array([eligible],dtype=int)
   solver.configure_cohesion(pairs,rest,k,laws,history,elig)
   before_p=sin.particle_q.numpy().tolist();before_v=sin.particle_qd.numpy().tolist();mp=float(model.particle_mass.numpy()[1]);actual_rest=rest.numpy().tolist()[0][0]
   q0=before_p[1][0]-actual_rest;vin=before_v[1][0];inertial=q0+DT*vin;masscoeff=mp/DT**2
   # Independent scalar branch solve. No force lag or frozen softening tangent.
   if name=='active_softening':expected=(masscoeff*inertial-100*.001*.004/.003)/(masscoeff-100*.001/.003)
   elif name=='compression':expected=inertial
   else:expected=masscoeff*inertial/(masscoeff+(1-damage)*100)
   old=history.numpy().tolist()
   solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1
   if history.numpy().tolist()!=old:raise ValueError('Trial solve mutated committed damage')
   q=sout.particle_q.numpy().tolist()[1][0]-actual_rest;v=sout.particle_qd.numpy().tolist()[1][0]
   expected_v=(expected-q0)/DT
   if abs(q-expected)>1e-7 or abs(v-expected_v)>2e-5:raise ValueError(f'Implicit material response mismatch {name}: {q=}, {expected=}, {v=}, {expected_v=}')
   solver.commit_cohesion(sout);wp.synchronize();after=history.numpy().tolist()[0]
   ref=update_damage(law,DamageState(*old[0]),q,eligible=bool(eligible))
   if abs(after[0]-ref.kappa_m)>1e-7 or abs(after[1]-ref.damage)>2e-6:raise ValueError('History commit mismatch')
   records.append(dict(id=name,expected_gap_m=expected,measured_gap_m=q,position_error_m=abs(q-expected),velocity_error_m_s=abs(v-expected_v),history_before=old[0],history_after=after,trial_history_immutable=True))
  # Frozen, active, mixed-mode and compression constitutive probes against finite differences.
  probe_gaps=[(.0005,0.,0.),(.002,0.,0.),(.0005,.0004,.0003),(0.,.002,0.),(-.0005,0.,0.),(.0045,0.,0.)]
  from tomato_cohesive_adapter_reference import patch_reference
  from tomato_cohesive_evolution_reference import evolve_patch
  for g in probe_gaps:
   sin.particle_q.assign(wp.array([[0.,0.,0.],[.001+g[0],g[1],g[2]]],dtype=wp.vec3));history.zero_();elig.fill_(1);solver.invalid.zero_()
   forces=wp.zeros(2,dtype=wp.vec3);hess=wp.zeros(2,dtype=wp.mat33)
   for color in range(len(model.particle_color_groups)):
    wp.launch(cohesive_blocks,dim=1,inputs=[color,model.particle_colors,sin.particle_q,pairs,rest,k,laws,history,elig,solver.invalid],outputs=[forces,hess])
   wp.synchronize();probes+=1
   actual_g=sin.particle_q.numpy().tolist()[1];actual_g[0]-=actual_rest
   matrix=[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]];trial=evolve_patch(law,DamageState(),[actual_g],[1.],matrix,eligible=True)['trial_state']
   ref=patch_reference([actual_g],[1.],matrix,trial.damage);observed=forces.numpy().tolist()
   if max(abs(observed[0][j]-ref['force_on_first_n'][0][j]) for j in range(3))>2e-5:raise ValueError('Constitutive force probe mismatch')
   # Independent numerical loading tangent of the trial constitutive force.
   def gradient(x):
    d=evolve_patch(law,DamageState(),[x],[1.],matrix,eligible=True)['trial_state'].damage
    return patch_reference([x],[1.],matrix,d)['gap_gradient_n'][0]
   if actual_g[0]!=0. and g[0] not in (.0045,):
    eps=1e-8;numeric=[[0.]*3 for _ in range(3)]
    for j in range(3):
     plus=actual_g.copy();minus=actual_g.copy();plus[j]+=eps;minus[j]-=eps
     # Compression+shear is intentionally refused, so only test normal column in compression.
     if actual_g[0]<0 and j>0:continue
     a=gradient(plus);b=gradient(minus)
     for i in range(3):numeric[i][j]=(a[i]-b[i])/(2*eps)
    native=hess.numpy().tolist()[1]
    indices=[(i,j) for i in range(3) for j in range(3) if actual_g[0]>=0 or j==0]
    if max(abs(native[i][j]-numeric[i][j]) for i,j in indices)>1e-3:raise ValueError('Algorithmic tangent probe mismatch')
  # Deliberately unsupported compression+shear must reject before committing history.
  sin.particle_q.assign(wp.array([[0.,0.,0.],[.0005,.001,0.]],dtype=wp.vec3));solver.invalid.zero_();history.zero_()
  wp.launch(cohesive_blocks,dim=1,inputs=[0,model.particle_colors,sin.particle_q,pairs,rest,k,laws,history,elig,solver.invalid],outputs=[wp.zeros(2,dtype=wp.vec3),wp.zeros(2,dtype=wp.mat33)])
  wp.synchronize();probes+=1
  try:solver.commit_cohesion(sin)
  except ValueError:pass
  else:raise ValueError('Unsupported mode was committed')
  if history.numpy().tolist()!=[[0.,0.]]:raise ValueError('Rejected trial changed history')
  write(out,'material_operator_measurements.json',dict(cases=records,probes=probes,newton_steps=steps,frame='fixed_x',physical_calibration=False,general_cutting_validated=False))
  if steps!=6 or probes!=7 or len(records)!=6:raise ValueError('Unexpected material counts')
  passed=True
 except BaseException:
  write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',result())
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
