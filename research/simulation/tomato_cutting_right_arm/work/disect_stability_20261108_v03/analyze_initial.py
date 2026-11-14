from pathlib import Path
import numpy as np,json,time
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import eigs,eigsh
w=Path(__file__).resolve().parent;z=np.load(w/'initial_audit.npz');x=z['x'].astype(float);t=z['tet_indices'];dm=z['tet_poses'].astype(float);n=len(x);mass=z['physical_mass'];fixed=z['fixed'];free=np.setdiff1d(np.arange(n),fixed);dofs=(3*free[:,None]+np.arange(3)).ravel();M=np.repeat(mass,3)[dofs];Ds=(x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1);F=Ds@dm;V=1/np.linalg.det(dm)/6
G=np.concatenate([-dm.sum(axis=1)[:,None],dm],axis=1);dot=G@G.transpose(0,2,1);I=np.eye(3);mu=z['tet_mu'];lam=z['tet_lambda'];kd=z['tet_damping'];
C=kd[:,None,None,None,None]*V[:,None,None,None,None]*(dot[:,:,:,None,None]*I+G[:,:,None,:,None]*G[:,None,:,None,:]*np.array([0,1,1,1])[None,None,:,None,None])
K=V[:,None,None,None,None]*(.75*mu[:,None,None,None,None]*(dot[:,:,:,None,None]*I+G[:,None,:,:,None]*G[:,:,None,None,:])+(lam-.625*mu)[:,None,None,None,None]*G[:,:,None,:,None]*G[:,None,:,None,:])
# Element order: i,j,output_component,input_component. Assemble exactly.
ids=(3*t[:,:,None]+np.arange(3)).reshape(len(t),12);rows=np.broadcast_to(ids[:,:,None],(len(t),12,12)).ravel();cols=np.broadcast_to(ids[:,None,:],(len(t),12,12)).ravel()
def assemble(a):return coo_matrix((a.transpose(0,1,3,2,4).reshape(-1),(rows,cols)),shape=(n*3,n*3)).tocsr()[dofs][:,dofs]
CS=assemble(C);KS=assemble(K);inv=diags(1/np.sqrt(M));A=inv@CS@inv;B=inv@KS@inv;rowc=float(abs(A).sum(axis=1).max());rowk=float(abs(B).sum(axis=1).max());start=time.perf_counter();ec=eigs(A,k=1,which='LR',tol=1e-6,maxiter=1000,return_eigenvectors=False)[0];ek=eigsh(B,k=1,which='LA',tol=1e-6,maxiter=1000,return_eigenvectors=False)[0]
# Stable semi-implicit damped oscillator requires dt^2*k + 2*dt*c < 4.
# Row norm is a conservative scale estimate, not proof for noncommuting nonsymmetric matrices.
combined=4/(rowc+np.sqrt(rowc**2+4*rowk));rest=z['rest_force'];a=rest[z['particle_inv_mass']>0]/mass[z['particle_inv_mass']>0,None]
out={'initial_fields_finite':{key:bool(np.isfinite(z[key]).all()) for key in z.files},'mass_kg':float(mass.sum()),'minimum_free_mass_kg':float(mass[free].min()),'max_initial_deformation_gradient_error':float(abs(F-np.eye(3)).max()),'initial_volume_ratio_min':float(np.linalg.det(F).min()),'max_gpu_rest_force_N':float(np.linalg.norm(rest,axis=1).max()),'max_gpu_free_rest_acceleration_m_s2':float(np.linalg.norm(a,axis=1).max()),'damping_row_norm_s_inv':rowc,'elastic_row_norm_s_inv_squared':rowk,'largest_damping_eigenvalue':{'real':float(ec.real),'imag':float(ec.imag)},'largest_elastic_eigenvalue_s_inv_squared':float(ek),'estimated_combined_dt_s':combined,'damping_only_eigen_dt_limit_s':float(2/ec.real),'old_dt_s':1e-5,'old_dt_times_damping_eigenvalue':float(1e-5*ec.real),'elastic_only_dt_limit_s':float(2/np.sqrt(ek)),'eigen_wall_s':time.perf_counter()-start,'scope':'Rest linearization of installed FEM damping/stiffness. Nonsymmetric hydrostatic damping omits vertex0 velocity; bound is diagnostic, not nonlinear stability proof. No dynamics advanced.'}
(w/'initial_analysis.json').write_text(json.dumps(out,indent=2));np.savez(w/'linearized_spectral_values.npz',damping_eigenvalue=ec,elastic_eigenvalue=ek);print(json.dumps(out,indent=2))
