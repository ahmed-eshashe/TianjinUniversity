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
s=load_settings('examples/config/ansys_prism.json');s.generator='meshio';s.generators.meshio.filename=str(w/'tomato_fem.vtk');s.geometry.position=[0,0,0];s.geometry.rotation=[0.,0.,1.,0.];s.geometry.scale=1.;s.young=30000.;s.poisson=.25;s.density=float(json.loads((data/'tomato_remesh_result.json').read_text())['density_kg_m3']);s.damping=10.;s.sim_dt=1e-5;s.sim_duration=1.;s.initial_y=.3;s.velocity_y=0.;s.cutting.active=False
start=time.perf_counter();sim=CuttingSim(s,adapter='cuda',requires_grad=False,log_folder=str(w/'settle_log'));q0=np.array(sim.builder.particle_q);fixed=z['fixed'];assert np.max(abs(q0-x))<1e-12
sim.setup_free_floating_knife()  # Upstream forward path expects articulation state; knife stays remote, no cut springs/contact.
pre_mass=np.array(sim.builder.particle_mass);assert abs(pre_mass.sum()-z['mass'].sum())<1e-9
for i in fixed:sim.builder.particle_mass[int(i)]=0.
sim.create_model_();sim.init_sim_structures_();sim.state=sim.model.state();sim.state.knife_f=torch.zeros((0,3),device='cuda');torch.cuda.synchronize();setup=time.perf_counter()-start
initial=sim.state.particle_q.cpu().numpy().copy();tt=sim.model.tet_indices.cpu().numpy();iv=np.linalg.det(initial[tt[:,1:]]-initial[tt[:,0]][:,None]);rows=[];start=time.perf_counter();stop='duration_completed'

import dflex as df
from dflex.sim import eval_tetrahedra
state=sim.state;state.particle_f.zero_()
__import__("dflex.adjoint",fromlist=["Tape"]).Tape().launch(func=eval_tetrahedra,dim=sim.model.tet_count,inputs=[state.particle_q,state.particle_qd,sim.model.tet_indices,sim.model.tet_poses,sim.model.tet_activations,sim.model.tet_mu,sim.model.tet_lambda,sim.model.tet_damping],outputs=[state.particle_f],adapter=sim.model.adapter)
torch.cuda.synchronize()
fields={name:getattr(sim.model,name).detach().cpu().numpy().copy() for name in ['particle_mass','particle_inv_mass','tet_indices','tet_poses','tet_activations','tet_mu','tet_lambda','tet_damping','gravity','contact_mask']}
fields.update(x=initial,velocity=state.particle_qd.cpu().numpy().copy(),rest_force=state.particle_f.cpu().numpy().copy(),fixed=fixed,physical_mass=pre_mass)
np.savez(w/'initial_audit.npz',**fields)
print('Initial arrays and zero-velocity FEM force saved without advancing dynamics')

fields_saved=fields
force0=fields['rest_force'].copy();rng=np.random.default_rng(613);vv=rng.normal(size=(len(initial),3))*1e-4;vv[fixed]=0.
controls={}
for name,vel in [('translation',np.tile([0.,-.1,0.],(len(initial),1))),('random',vv),('random_plus_translation',vv+np.array([0.,-.1,0.]))]:
 state.particle_qd.copy_(torch.tensor(vel,dtype=torch.float32,device='cuda'));state.particle_f.zero_()
 __import__("dflex.adjoint",fromlist=["Tape"]).Tape().launch(func=eval_tetrahedra,dim=sim.model.tet_count,inputs=[state.particle_q,state.particle_qd,sim.model.tet_indices,sim.model.tet_poses,sim.model.tet_activations,sim.model.tet_mu,sim.model.tet_lambda,sim.model.tet_damping],outputs=[state.particle_f],adapter=sim.model.adapter)
 torch.cuda.synchronize();controls[name+'_v']=vel;controls[name+'_f']=state.particle_f.cpu().numpy().copy()
np.savez(w/'damping_controls.npz',force0=force0,**controls)
