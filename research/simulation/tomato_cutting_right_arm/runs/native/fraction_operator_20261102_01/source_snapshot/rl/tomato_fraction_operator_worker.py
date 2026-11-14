"""Native cubic-volume fraction-to-boundary controls, no mechanical stepping."""
import argparse,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Volume fraction operator stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  pins=capture_sources(out,[Path(__file__)])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_fraction_boundary import fraction_volume_path
  from tomato_global_implicit import global_volume_path
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');rest=np.vstack([np.zeros(3),np.eye(3)]);cell=wp.array([[0,1,2,3]],dtype=wp.vec4i);V=wp.array([1/6],dtype=wp.float64);bad=wp.zeros(1,dtype=int);old_bad=wp.zeros(1,dtype=int);write(out,'input_manifest.json',dict(cases=5,newton_steps=0,controlled_steps=0,physical_volume_floor=.1,nonlinear_trial_fraction=.8,minimum_retained_current_gap=.2,scope='Numerical path safeguard only. Not a change to the material floor or force/energy.'))
  for label,path,expected in [('translation',[rest,rest+[.3,-.2,.1]],True),('admissible_but_too_close_single_trial',[rest,rest@np.diag([.2,1,1])],False),('safe_single_trial',[rest,rest@np.diag([.6,1,1])],True),('same_close_state_reachable_by_safe_trials',[rest,rest@np.diag([.6,1,1]),rest@np.diag([.3,1,1]),rest@np.diag([.2,1,1])],True),('positive_endpoints_collapsed_middle',[rest,rest@np.diag([-1,-1,1])],False)]:
   native=[];old=[];dense_min=[];gaps=[]
   for a,b in zip(path,path[1:]):
    x=wp.array(a,dtype=wp.vec3d);trial=wp.array(b,dtype=wp.vec3d);bad.zero_();old_bad.zero_();wp.launch(fraction_volume_path,dim=1,inputs=[x,trial,cell,V],outputs=[bad]);wp.launch(global_volume_path,dim=1,inputs=[x,trial,cell,V],outputs=[old_bad]);native.append(not bool(bad.numpy()[0]));old.append(not bool(old_bad.numpy()[0]));points=np.linspace(0,1,1001)[:,None,None]*b+(1-np.linspace(0,1,1001)[:,None,None])*a;J=np.linalg.det(points[:,1:]-points[:,:1]);minimum=float(J.min());threshold=.1+.2*(float(np.linalg.det(a[1:]-a[:1]))-.1);dense_min.append(minimum);gaps.append(threshold)
    if native[-1]and minimum<=threshold-1e-14:raise ValueError('Native safeguard admitted a path outside its claimed retained gap')
   accepted=all(native)
   if accepted!=expected or(label=='admissible_but_too_close_single_trial'and not all(old)):raise ValueError((label,native,old))
   cases.append(dict(case=label,native_segments_accepted=native,old_absolute_floor_segments_accepted=old,dense_path_minimum_J=dense_min,minimum_retained_gap_threshold=gaps))
  if not sources_unchanged(pins):raise ValueError('Fraction safeguard source changed')
  write(out,'fraction_operator_measurements.json',dict(cases=cases,scope='Five native numerical path controls versus dense independent determinant paths. A physically admissible J=.2 state is rejected in one aggressive trial but reachable through three safe trials; physical floor remains .1. Zero mechanical/support/cutting qualification.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,fraction_operator_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
