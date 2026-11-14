"""Native operator check only; no robot integration or cutting."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);out=parser.parse_args().output;app=None;passed=False;cases=[]
 def stop(*a):raise InterruptedError('Pressure operator check stopped')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  path=ROOT/'runs/offline/physical_pressure_20261102_02/operator_fixtures.npz';pins=capture_sources(out,[Path(__file__)],inputs=[path,ROOT/'runs/offline/physical_pressure_20261102_02/measurements.json'])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch,warp as wp
  from tomato_physical_pressure import pressure_packet,scatter_packet
  torch.set_num_threads(1);wp.init();wp.set_device('cuda:0');fixtures=np.load(path)
  write(out,'input_manifest.json',dict(cases=3,newton_steps=0,controlled_steps=0,force_budget_n=2e-8,hessian_budget_n_m=2e-4,wrench_budget_n_or_nm=1e-12,energy_budget_j=1e-14,scope='Frozen planar packet native assembly versus independent host energy derivatives. Not generated CAD quadrature, a robot run, full-target force/work or separation.'))
  for i in range(3):
   if (out/'stop.request').exists():raise InterruptedError('Pressure stop')
   a={k:fixtures[f'case{i}_{k}']for k in ['x','indices','barycentric','areas','closest_local','normals_local','rotation','translation','com_local','force','diagonal_blocks','body_wrench','energy']};n=len(a['x']);count=len(a['areas']);force=wp.zeros(count,dtype=wp.vec3d);hessian=wp.zeros(count,dtype=wp.mat33d);bf=wp.zeros(count,dtype=wp.vec3d);bt=wp.zeros(count,dtype=wp.vec3d);energy=wp.zeros(count,dtype=wp.float64);indices=wp.array(a['indices'],dtype=wp.vec3i);bary=wp.array(a['barycentric'],dtype=wp.vec3d)
   wp.launch(pressure_packet,dim=count,inputs=[wp.array(a['x'],dtype=wp.vec3d),indices,bary,wp.array(a['areas'],dtype=wp.float64),wp.array(a['closest_local'],dtype=wp.vec3d),wp.array(a['normals_local'],dtype=wp.vec3d),wp.array(a['rotation'][None],dtype=wp.mat33d),wp.array(a['translation'][None],dtype=wp.vec3d),wp.array(a['com_local'][None],dtype=wp.vec3d)],outputs=[force,hessian,bf,bt,energy])
   colors=wp.array(np.arange(n),dtype=int);f=wp.zeros(n,dtype=wp.vec3);h=wp.zeros(n,dtype=wp.mat33);wp.launch(scatter_packet,dim=(count,3),inputs=[-1,colors,indices,bary,force,hessian],outputs=[f,h]);wp.synchronize();fe=float(abs(f.numpy()-a['force']).max());he=float(abs(h.numpy()-a['diagonal_blocks']).max());we=float(abs(np.r_[bf.numpy().sum(0),bt.numpy().sum(0)]-a['body_wrench']).max());ee=float(abs(energy.numpy().sum()-a['energy'][0]));color_error=0.
   for color in range(n):
    cf=wp.zeros(n,dtype=wp.vec3);ch=wp.zeros(n,dtype=wp.mat33);wp.launch(scatter_packet,dim=(count,3),inputs=[color,colors,indices,bary,force,hessian],outputs=[cf,ch]);expected_f=np.zeros((n,3));expected_h=np.zeros((n,3,3));expected_f[color]=f.numpy()[color];expected_h[color]=h.numpy()[color];color_error=max(color_error,float(abs(cf.numpy()-expected_f).max()),float(abs(ch.numpy()-expected_h).max()))
   row=dict(case=i,force_error_n=fe,hessian_error_n_m=he,wrench_error_n_or_nm=we,energy_error_j=ee,color_error=color_error)
   if fe>2e-8 or he>2e-4 or we>1e-12 or ee>1e-14 or color_error!=0:raise ValueError(row)
   cases.append(row)
  if not sources_unchanged(pins):raise ValueError('Pressure source changed')
  write(out,'physical_pressure_measurements.json',dict(cases=cases,source_unchanged=True,scope='Three frozen planar native pressure packets with exact physical soft-point reaction moments; zero mechanical steps. Separate geometry, full-model integration and actual robot work qualification still required.'));passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,physical_pressure_passed=passed,newton_steps=0,controlled_steps=0,cases_completed=len(cases)))
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
