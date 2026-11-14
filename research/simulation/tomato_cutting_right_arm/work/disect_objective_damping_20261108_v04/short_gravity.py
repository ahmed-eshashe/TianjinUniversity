from pathlib import Path
import os,sys,time,json,resource
import numpy as np
w=Path(__file__).resolve().parent;data=w.parent/'disect_mesh_validation_20261108_v02';repo=w/'DiSECt';sys.path[:0]=[str(repo/'meshing'),str(repo)];os.chdir(repo)
import meshio,torch
import ansys.mapdl.reader as reader
sys.modules['pyansys']=reader
torch.set_grad_enabled(False)
from cutting import load_settings,CuttingSim
z=np.load(data/'tomato_fem_mesh.npz');raw=z['x'];x=raw[:,[0,2,1]].copy();x[:,1]+=.002;x[:,2]*=-1;t=z['tets'].copy();# axis transform has determinant +1
meshio.write(w/'tomato_fem.vtk',meshio.Mesh(x,[('tetra',t)]))
s=load_settings('examples/config/ansys_prism.json');s.generator='meshio';s.generators.meshio.filename=str(w/'tomato_fem.vtk');s.geometry.position=[0,0,0];s.geometry.rotation=[0.,0.,1.,0.];s.geometry.scale=1.;s.young=30000.;s.poisson=.25;s.density=float(json.loads((data/'tomato_remesh_result.json').read_text())['density_kg_m3']);s.damping=10.;s.sim_dt=1.5e-7;s.sim_duration=.02;s.initial_y=.3;s.velocity_y=0.;s.cutting.active=False
start=time.perf_counter();sim=CuttingSim(s,adapter='cuda',requires_grad=False,log_folder=str(w/'settle_log'));q0=np.array(sim.builder.particle_q);fixed=z['fixed'];assert np.max(abs(q0-x))<1e-12
sim.setup_free_floating_knife()  # Upstream forward path expects articulation state; knife stays remote, no cut springs/contact.
pre_mass=np.array(sim.builder.particle_mass);assert abs(pre_mass.sum()-z['mass'].sum())<1e-9
for i in fixed:sim.builder.particle_mass[int(i)]=0.
sim.create_model_();sim.init_sim_structures_();sim.state=sim.model.state();sim.state.knife_f=torch.zeros((0,3),device='cuda');torch.cuda.synchronize();setup=time.perf_counter()-start
initial=sim.state.particle_q.cpu().numpy().copy();tt=sim.model.tet_indices.cpu().numpy();iv=np.linalg.det(initial[tt[:,1:]]-initial[tt[:,0]][:,None]);rows=[];start=time.perf_counter();stop='duration_completed'

# Static affine damping control at the same initial state, before integration.
import dflex.adjoint as adj
from dflex.sim import eval_tetrahedra
state=sim.state;state.particle_f.zero_()
def eval_force():
 state.particle_f.zero_();adj.Tape().launch(func=eval_tetrahedra,dim=sim.model.tet_count,inputs=[state.particle_q,state.particle_qd,sim.model.tet_indices,sim.model.tet_poses,sim.model.tet_activations,sim.model.tet_mu,sim.model.tet_lambda,sim.model.tet_damping],outputs=[state.particle_f],adapter='cuda');torch.cuda.synchronize();return state.particle_f.cpu().numpy().copy()
f0=eval_force();vv=-(initial.astype(float)-initial.mean(0))*1.0;state.particle_qd.copy_(torch.tensor(vv,dtype=torch.float32,device='cuda'));actual=eval_force()-f0
dm=sim.model.tet_poses.cpu().numpy().astype(float);kd=sim.model.tet_damping.cpu().numpy();vol=1/np.linalg.det(dm)/6;gg=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);d=initial.astype(float)[tt[:,1:]]-initial.astype(float)[tt[:,0]][:,None];gj123=np.stack([np.cross(d[:,1],d[:,2]),np.cross(d[:,2],d[:,0]),np.cross(d[:,0],d[:,1])],axis=1)*np.linalg.det(dm)[:,None,None];gj=np.concatenate([-gj123.sum(1)[:,None],gj123],axis=1);dfdt=np.einsum('eia,eib->eab',vv[tt],gg);strain=np.einsum('eia,eia->e',gj,vv[tt]);local=-(kd*vol)[:,None,None]*(np.einsum('eab,eib->eia',dfdt,gg)+gj*strain[:,None,None]);pred=np.zeros_like(vv);np.add.at(pred,tt.ravel(),local.reshape(-1,3));relative=float(np.linalg.norm(pred-actual)/np.linalg.norm(pred));affine={'relative_force_error':relative,'reference_force_norm_N':float(np.linalg.norm(pred)),'absolute_force_error_norm_N':float(np.linalg.norm(pred-actual)),'strain_rate_s_inv':1.0,'power_W':float(np.sum(actual*vv)),'passed':bool(relative<.001 and np.sum(actual*vv)<=0)};(w/'affine_control.json').write_text(json.dumps(affine,indent=2));assert affine['passed'],affine
state.particle_qd.zero_();state.particle_f.zero_()

start=time.perf_counter()
for i in range(133334):
 sim.simulation_step()
 if i<10 or (i+1)%1000==0:
  torch.cuda.synchronize();q=sim.state.particle_q.cpu().numpy();v=sim.state.particle_qd.cpu().numpy();ratio=np.linalg.det(q[tt[:,1:]]-q[tt[:,0]][:,None])/iv
  row={'step':i+1,'sim_s':sim.sim_time,'wall_s':time.perf_counter()-start,'finite':bool(np.isfinite(q).all() and np.isfinite(v).all()),'min_volume_ratio':float(ratio.min()),'max_speed_m_s':float(np.linalg.norm(v,axis=1).max()),'board_penetration_m':float(max(0,-q[:,1].min())),'fixed_error_m':float(np.linalg.norm(q[fixed]-initial[fixed],axis=1).max())};rows.append(row);(w/'settle_progress.json').write_text(json.dumps(row))
  if not row['finite'] or row['min_volume_ratio']<=.1 or row['board_penetration_m']>.0001 or row['fixed_error_m']>1e-7:stop='stability_gate_failed';break
end=time.perf_counter();speed=[a['max_speed_m_s'] for a in rows if a['sim_s']>=.018];passed=stop=='duration_completed' and all(a['finite'] and a['min_volume_ratio']>.1 and a['board_penetration_m']<=.0001 and a['fixed_error_m']<=1e-7 for a in rows)
result={'scope':'Short 20 ms unloaded stability diagnostic only; no settling, fracture or contact qualification','setup_wall_s':setup,'stepping_wall_s':end-start,'simulated_s':sim.sim_time,'wall_s_per_sim_s':(end-start)/sim.sim_time,'stop':stop,'passed':passed,'full_settling_passed':False,'dt_s':s.sim_dt,'late_max_speed_m_s':max(speed) if speed else None,'initial_physical_mass_kg':float(pre_mass.sum()),'fixed_node_physical_mass_kg':float(pre_mass[fixed].sum()),'minimum_sampled_volume_ratio':min(a['min_volume_ratio'] for a in rows),'maximum_sampled_board_penetration_m':max(a['board_penetration_m'] for a in rows),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rows':rows}
np.savez(w/'settled_tomato.npz',x=q,v=v,initial_x=initial,tets=tt,fixed=fixed)
(w/'settle_result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
