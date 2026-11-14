from pathlib import Path
import os,sys,time,json,resource
import numpy as np
w=Path(__file__).resolve().parent;repo=w/'DiSECt';sys.path[:0]=[str(repo/'meshing'),str(repo)];os.chdir(repo)
import meshio,torch
import ansys.mapdl.reader as reader
sys.modules['pyansys']=reader
torch.set_grad_enabled(False)
from cutting import load_settings,CuttingSim
z=np.load(w/'tomato_fem_mesh.npz');raw=z['x'];x=raw[:,[0,2,1]].copy();x[:,1]+=.002;x[:,2]*=-1;t=z['tets'].copy();# axis transform has determinant +1
meshio.write(w/'tomato_fem.vtk',meshio.Mesh(x,[('tetra',t)]))
s=load_settings('examples/config/ansys_prism.json');s.generator='meshio';s.generators.meshio.filename=str(w/'tomato_fem.vtk');s.geometry.position=[0,0,0];s.geometry.rotation=[0.,0.,1.,0.];s.geometry.scale=1.;s.young=30000.;s.poisson=.25;s.density=float(json.loads((w/'tomato_remesh_result.json').read_text())['density_kg_m3']);s.damping=10.;s.sim_dt=1e-5;s.sim_duration=1.;s.initial_y=.3;s.velocity_y=0.;s.cutting.active=False
start=time.perf_counter();sim=CuttingSim(s,adapter='cuda',requires_grad=False,log_folder=str(w/'settle_log'));q0=np.array(sim.builder.particle_q);fixed=z['fixed'];assert np.max(abs(q0-x))<1e-12
sim.setup_free_floating_knife()  # Upstream forward path expects articulation state; knife stays remote, no cut springs/contact.
pre_mass=np.array(sim.builder.particle_mass);assert abs(pre_mass.sum()-z['mass'].sum())<1e-9
for i in fixed:sim.builder.particle_mass[int(i)]=0.
sim.create_model_();sim.init_sim_structures_();sim.state=sim.model.state();sim.state.knife_f=torch.zeros((0,3),device='cuda');torch.cuda.synchronize();setup=time.perf_counter()-start
initial=sim.state.particle_q.cpu().numpy().copy();tt=sim.model.tet_indices.cpu().numpy();iv=np.linalg.det(initial[tt[:,1:]]-initial[tt[:,0]][:,None]);rows=[];start=time.perf_counter();stop='duration_completed'
for i in range(100000):
 sim.simulation_step()
 if (i+1)%100==0:
  torch.cuda.synchronize();q=sim.state.particle_q.cpu().numpy();v=sim.state.particle_qd.cpu().numpy();ratio=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/iv
  row={'step':i+1,'sim_s':sim.sim_time,'wall_s':time.perf_counter()-start,'finite':bool(np.isfinite(q).all() and np.isfinite(v).all()),'min_volume_ratio':float(ratio.min()),'max_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'board_penetration_m':float(max(0,-q[:,1].min())),'fixed_error_m':float(np.linalg.norm(q[fixed]-initial[fixed],axis=1).max())};rows.append(row);(w/'settle_progress.json').write_text(json.dumps(row))
  if not row['finite'] or row['min_volume_ratio']<=.1 or row['board_penetration_m']>.0001 or row['fixed_error_m']>1e-7:stop='stability_gate_failed';break
end=time.perf_counter();speed=[a['max_speed_m_s'] for a in rows if a['sim_s']>=.9];passed=stop=='duration_completed' and bool(speed) and max(speed)<=.001
result={'scope':'Intact bulk FEM unloaded component only; cut interface not yet inserted','setup_wall_s':setup,'stepping_wall_s':end-start,'simulated_s':sim.sim_time,'wall_s_per_sim_s':(end-start)/sim.sim_time,'stop':stop,'passed':passed,'late_max_speed_m_s':max(speed) if speed else None,'initial_physical_mass_kg':float(pre_mass.sum()),'fixed_node_physical_mass_kg':float(pre_mass[fixed].sum()),'minimum_sampled_volume_ratio':min(a['min_volume_ratio'] for a in rows),'maximum_sampled_board_penetration_m':max(a['board_penetration_m'] for a in rows),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rows':rows}
np.savez(w/'settled_tomato.npz',x=q,v=v,initial_x=initial,tets=tt,fixed=fixed)
(w/'settle_result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
