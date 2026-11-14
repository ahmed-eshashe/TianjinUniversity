import faulthandler
faulthandler.enable()
from pathlib import Path
import sys,os,time,json,resource
import numpy as np
w=Path(__file__).resolve().parent;repo=w/'DiSECt';os.chdir(repo);sys.path.insert(0,str(repo));sys.path.insert(0,str(repo/'meshing'))
# Upstream pyansys API moved to ansys.mapdl.reader; preserve the same RST input.
import ansys.mapdl.reader as reader
sys.modules['pyansys']=reader
import torch
torch.set_grad_enabled(False)  # This trial is forward-only; prevent unused motion autograd chains.
from cutting import load_settings,SlicingMotion,CuttingSim
settings=load_settings('examples/config/ansys_prism.json');settings.sim_duration=5.;settings.sim_dt=1e-4;settings.initial_y=.08;settings.velocity_y=-.05
start=time.perf_counter();sim=CuttingSim(settings,experiment_name='upstream_basic_headless',log_folder=str(w/'disect_log'),adapter='cuda',requires_grad=False)
sim.motion=SlicingMotion(initial_pos=torch.tensor([0.,.08,0.],device='cuda'),slicing_frequency=torch.tensor(5.,device='cuda'),slicing_amplitudes=torch.tensor(np.ones(5)*.1,device='cuda',dtype=torch.float32),pressing_velocities=torch.tensor(np.ones(5)*-.05,device='cuda',dtype=torch.float32),slicing_times=np.linspace(0,5.,5),slicing_kernel_width=.5)
sim.cut()
np.savez(w/'mesh_audit_input.npz',particle_x=sim.builder.particle_q,tets=sim.builder.tet_indices,triangles=sim.builder.tri_indices,cut_triangles=sim.builder.cut_tri_indices,virtual_triangles=sim.builder.cut_virtual_tri_indices,above=sim.builder.cut_virtual_tri_indices_above_cut,below=sim.builder.cut_virtual_tri_indices_below_cut,edge_indices=sim.builder.cut_edge_indices,edge_coords=sim.builder.cut_edge_coords,springs=sim.builder.cut_spring_indices)
(w/'mesh_status.json').write_text(json.dumps({'native_success':sim.builder.mesh_cut_success}))
sim.init_sim_structures_();sim.create_model_();sim.state=sim.model.state();initial_x=sim.state.particle_q.detach().cpu().numpy().copy();tet_indices=sim.model.tet_indices.detach().cpu().numpy().copy();torch.cuda.synchronize();setup=time.perf_counter()-start
rows=[];start=time.perf_counter()
for i in range(50000):
 sim.simulation_step()
 if (i+1)%100==0:
  torch.cuda.synchronize();x=sim.state.particle_q.detach().cpu().numpy();k=sim.state.cut_spring_ke.detach().cpu().numpy();f=sim.state.knife_f.detach().cpu().numpy()
  row=dict(step=i+1,sim_s=sim.sim_time,wall_s=time.perf_counter()-start,finite=bool(np.isfinite(x).all() and np.isfinite(f).all()),force_sum_norm=float(np.linalg.norm(f,axis=1).sum()),force_resultant=np.sum(f,axis=0).tolist(),spring_count=int(k.size),zero_stiffness_springs=int((k<=0).sum()),minimum_stiffness=float(k.min()),max_position_m=float(np.abs(x).max()))
  rows.append(row);(w/'forward_progress.json').write_text(json.dumps(row,indent=2))
  if not row['finite'] or row['max_position_m']>10:break
  if time.perf_counter()-start>600:break
end=time.perf_counter();np.savez(w/'forward_final.npz',x=x,initial_x=initial_x,tet_indices=tet_indices,stiffness=k,force=f)
report=dict(example='examples/basic_cutting.py, same settings and slicing motion, headless forward-only',setup_wall_s=setup,wall_s=end-start,simulated_s=sim.sim_time,wall_s_per_sim_s=(end-start)/sim.sim_time,nodes=len(x),tetrahedra=len(sim.model.tet_indices),peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),peak_gpu_reserved_bytes=torch.cuda.max_memory_reserved(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,rows=rows,full_example_completed=(i+1==50000),separation_caveat='Zero-stiffness count is interface damage, not independently verified detached connectivity.')
(w/'forward_result.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
