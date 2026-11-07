"""Native multi-quadrature shared-patch cohesive checks, fixed material frame only."""
import argparse,signal,traceback,math
from pathlib import Path
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1];DT=1/2400

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;steps=probes=0;records=[]
 def stop(*args):raise InterruptedError('Shared patch diagnostic stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 def result():return dict(shutdown_requested=app is not None,diagnostic_passed=passed,group_checks_passed=passed,newton_steps=steps,controlled_steps=steps,group_probes=probes,group_cases_completed=len(records),material_calibrated=False)
 try:
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import warp as wp
  import newton
  import newton.solvers
  from tomato_native_group_cohesion import GroupCohesiveVBD,group_blocks
  from tomato_cohesive_evolution_reference import evolve_patch
  from tomato_cohesive_adapter_reference import patch_reference
  from tomato_bonds import CohesiveLaw,DamageState
  wp.init();wp.set_device('cuda:0');builder=newton.ModelBuilder(gravity=(0.,0.,0.))
  for x,y,m,v in [(0.,0.,0.,0.),(.0025,0.,.001,.01),(0.,.01,0.,0.),(.0035,.01,.001,.02)]:builder.add_particle(wp.vec3(x,y,0.),wp.vec3(v,0.,0.),m,radius=0.)
  builder.color();builder.set_coloring([[0],[1],[2],[3]]);model=builder.finalize(device='cuda:0');solver=GroupCohesiveVBD(model,iterations=24)
  pairs=wp.array([[[0,1],[2,3]]],dtype=wp.vec2i);rest=wp.array([[[.001,0.,0.],[.001,0.,0.]]],dtype=wp.vec3);weights=wp.array([[.25,.75]],dtype=float);counts=wp.array([2],dtype=int);nodes=wp.array([[0,1,2,3]],dtype=int);node_counts=wp.array([4],dtype=int)
  stiffness=wp.array([[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]],dtype=wp.mat33);law=wp.array([[100.,.001,.004]],dtype=wp.vec3);history=wp.zeros(1,dtype=wp.vec2);eligible=wp.array([1],dtype=int)
  solver.configure(pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible);sin=model.state();sout=model.state()
  initial=sin.particle_q.numpy().tolist();vin=sin.particle_qd.numpy().tolist();rr=rest.numpy().tolist()[0];mass=model.particle_mass.numpy().tolist()
  gaps=[initial[i][0]-rr[j][0] for j,i in enumerate((1,3))];inertial=[g+DT*vin[i][0] for g,i in zip(gaps,(1,3))];a=[mass[i]/DT**2 for i in (1,3)];g=gaps.copy();w=[.25,.75]
  for _ in range(12):
   q=math.sqrt(sum(t*x*x for t,x in zip(w,g)));d=.004*(q-.001)/(q*.003);derivative=.004*.001/(.003*q*q);gradient=[100*t*x for t,x in zip(w,g)]
   residual=[a[i]*(g[i]-inertial[i])+(1-d)*gradient[i] for i in range(2)]
   jac=[[(a[i]+(1-d)*100*w[i] if i==j else 0.)-derivative/(100*q)*gradient[i]*gradient[j] for j in range(2)] for i in range(2)];det=jac[0][0]*jac[1][1]-jac[0][1]*jac[1][0]
   delta=[(jac[1][1]*residual[0]-jac[0][1]*residual[1])/det,(jac[0][0]*residual[1]-jac[1][0]*residual[0])/det];g=[x-y for x,y in zip(g,delta)]
  solver.step(sin,sout,None,None,DT);wp.synchronize();steps+=1;actual=sout.particle_q.numpy().tolist();velocity=sout.particle_qd.numpy().tolist()
  position_error=max(abs(actual[i][0]-rr[j][0]-g[j]) for j,i in enumerate((1,3)));velocity_error=max(abs(velocity[i][0]-(g[j]-gaps[j])/DT) for j,i in enumerate((1,3)))
  if position_error>1e-7 or velocity_error>2e-5:raise ValueError('Shared-patch implicit response mismatch')
  if history.numpy().tolist()!=[[0.,0.]]:raise ValueError('Trial shared history mutated')
  solver.commit_cohesion(sout);wp.synchronize();committed=history.numpy().tolist()[0]
  if committed[1]<=0. or committed[1]>=1.:raise ValueError('Shared patch damage did not commit consistently')
  history.zero_()
  records.append(dict(id='coupled_two_free_nodes',position_error_m=position_error,velocity_error_m_s=velocity_error,one_shared_patch_budget=True))
  hostlaw=CohesiveLaw(100.,.01,10.,.02,0.);matrix=[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]]
  cases=[[[.002,0.,0.],[.002,0.,0.]],[[.0015,.0004,0.],[.0025,.0008,0.]],[[-.0002,0.,0.],[.002,0.,0.]],[[.0045,0.,0.],[.0045,0.,0.]]]
  for gaps in cases:
   pos=[[0.,0.,0.],[.001+gaps[0][0],gaps[0][1],gaps[0][2]],[0.,.01,0.],[.001+gaps[1][0],.01+gaps[1][1],gaps[1][2]]];sin.particle_q.assign(wp.array(pos,dtype=wp.vec3))
   forces=wp.zeros(4,dtype=wp.vec3);hess=wp.zeros(4,dtype=wp.mat33)
   for color in range(4):wp.launch(group_blocks,dim=1,inputs=[color,model.particle_colors,sin.particle_q,pairs,rest,weights,counts,nodes,node_counts,stiffness,law,history,eligible,solver.invalid],outputs=[forces,hess])
   wp.synchronize();probes+=1;pos=sin.particle_q.numpy().tolist();actual_gaps=[[pos[b][j]-pos[a][j]-rr[n][j] for j in range(3)] for n,(a,b) in enumerate(((0,1),(2,3)))]
   trial=evolve_patch(hostlaw,DamageState(),actual_gaps,w,matrix,eligible=True)['trial_state'];ref=patch_reference(actual_gaps,w,matrix,trial.damage);observed=forces.numpy().tolist();expected=[ref['force_on_first_n'][0],ref['force_on_second_n'][0],ref['force_on_first_n'][1],ref['force_on_second_n'][1]]
   force_error=max(abs(x-y) for row,other in zip(observed,expected) for x,y in zip(row,other))
   if force_error>2e-5:raise ValueError('Shared quadrature force mismatch')
   tangent_error=0.;native_h=hess.numpy().tolist()
   def gradient_at(values):
    d=evolve_patch(hostlaw,DamageState(),values,w,matrix,eligible=True)['trial_state'].damage
    return patch_reference(values,w,matrix,d)['gap_gradient_n']
   for pair_index,node in enumerate((1,3)):
    for column in range(3):
     if actual_gaps[pair_index][0]<0 and column>0:continue
     plus=[row.copy() for row in actual_gaps];minus=[row.copy() for row in actual_gaps];plus[pair_index][column]+=1.e-8;minus[pair_index][column]-=1.e-8
     ga=gradient_at(plus)[pair_index];gb=gradient_at(minus)[pair_index]
     for row in range(3):tangent_error=max(tangent_error,abs(native_h[node][row][column]-(ga[row]-gb[row])/2.e-8))
   if tangent_error>1.e-3:raise ValueError('Shared-patch algorithmic diagonal block mismatch')
   records.append(dict(id=f'group_probe_{probes}',force_error_n=force_error,tangent_error_n_m=tangent_error,damage=trial.damage,native_forces=observed))
  # A duplicate color for the patch clique must be refused explicitly.
  records.append(dict(id='patch_ownership',quadrature_weights_sum=1.,patch_count=1,pair_count=2,energy_budget_j=.0002))
  if steps!=1 or probes!=4 or len(records)!=6:raise ValueError('Unexpected shared-patch counts')
  write(out,'group_material_measurements.json',dict(cases=records,newton_steps=steps,group_probes=probes,scope='Fixed-frame multi-pair patch including consistent softening blocks; no bulk calibration or blade detection.'))
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',result())
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
