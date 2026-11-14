"""Isolated forward-only float64 adapter for the corrected DiSECt bulk law.
No blade, fracture, articulation, autograd or production replacement is implied.
"""
from pathlib import Path
import time, json, os
import numpy as np
import torch
from torch.utils.cpp_extension import load
W=Path(__file__).resolve().parent
SOURCE=W.parent/'disect_objective_damping_20261108_v04'
ENV=W.parent/'disect_mesh_validation_20261108_v02'
torch.set_grad_enabled(False)
def extension():
    return load(name='disect_double_v05', sources=[str(W/'bindings.cpp'),str(W/'kernels.cu')],extra_cflags=['-O3'],extra_cuda_cflags=['-O3'],verbose=False)
def tensor(a,dtype=torch.float64):return torch.as_tensor(np.ascontiguousarray(a),dtype=dtype,device='cuda')
def load_arrays():
    z=dict(np.load(SOURCE/'initial_audit.npz'));m=np.load(ENV/'tomato_fem_mesh.npz')
    x=m['x'][:,[0,2,1]].copy();x[:,1]+=.002;x[:,2]*=-1
    t=z['tet_indices'];D=(x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1)
    z['x']=x;z['tet_poses']=np.linalg.inv(D)
    # Recompute rest geometry in double, from preserved double original positions.
    # The material coefficients, masses, connectivity and support indices are unchanged.
    return z
class Bulk:
    def __init__(self,z=None):
        self.k=extension();self.z=load_arrays() if z is None else z
        z=self.z;self.x0=tensor(z['x']);self.x=self.x0.clone();self.v=torch.zeros_like(self.x)
        self.t=tensor(z['tet_indices'],torch.int64);self.dm=tensor(z['tet_poses']);self.mu=tensor(z['tet_mu']);self.la=tensor(z['tet_lambda']);self.kd=tensor(z['tet_damping']);self.act=tensor(z['tet_activations']);self.mass=tensor(z['physical_mass'])[:,None];self.inv=tensor(z['particle_inv_mass']);self.free=(self.inv>0)[:,None];self.gravity=tensor(z['gravity']);self.mask=tensor(z['contact_mask'])
        self.weight=self.kd/(6*torch.linalg.det(self.dm));self.g=torch.zeros((len(self.t),4,3),dtype=torch.float64,device='cuda');self.j=torch.zeros_like(self.g);self.f=torch.zeros_like(self.x);self.diag=torch.zeros_like(self.x);self.tmp=torch.zeros_like(self.x);self.guess=torch.zeros_like(self.x)
        # Mass/inverse mass captured separately in v04 have float32 rounding.
        # Integrate with exact reciprocal of the preserved physical masses.
        self.inv=torch.where(self.free[:,0],1/self.mass[:,0],0.)
    def reset(self):
        self.x.copy_(self.x0);self.v.zero_()
        for a in [self.g,self.j,self.f,self.diag,self.tmp,self.guess]:a.zero_()
        if hasattr(self,'graph_max_residual'):self.graph_max_residual.zero_()
        if hasattr(self,'rate'):self.rate.zero_()
        for name in ['cg_scalars','cg_z','cg_ap','cg_y','cg_r','cg_p','cg_d']:
            if hasattr(self,name):getattr(self,name).zero_()
    def geometry(self):
        self.f.zero_();self.diag.zero_();self.k.geom(self.x,self.t,self.dm,self.mu,self.la,self.kd,self.act,self.f,self.g,self.j,self.diag)
        return self.f
    def damping(self,v):
        if hasattr(self,'csr'):
            self.k.gathered_damp(v,self.t,self.j,self.weight,*self.csr,self.rate,self.tmp)
            return self.tmp
        self.tmp.zero_();self.k.damp(v,self.t,self.g,self.j,self.weight,self.tmp)
        return self.tmp
    def enable_gather(self):
        # Exact algebraic reorganization: constant deviatoric part assembled once,
        # current-geometry volumetric part evaluated every invocation.
        from scipy.sparse import coo_matrix
        t=self.z['tet_indices'];dm=self.z['tet_poses'];G=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);weight=self.z['tet_damping']/(6*np.linalg.det(dm))
        local=weight[:,None,None]*(G@G.transpose(0,2,1));L=coo_matrix((local.ravel(),(np.broadcast_to(t[:,:,None],local.shape).ravel(),np.broadcast_to(t[:,None,:],local.shape).ravel())),shape=(len(self.x),len(self.x))).tocsr()
        inc=np.argsort(t.ravel(),kind='stable');ir=np.r_[0,np.cumsum(np.bincount(t.ravel(),minlength=len(self.x)))]
        self.csr=(tensor(L.indptr,torch.int64),tensor(L.indices,torch.int64),tensor(L.data),tensor(ir,torch.int64),tensor(inc,torch.int64));self.rate=torch.zeros(len(t),dtype=torch.float64,device='cuda')
    def material(self):
        self.geometry();return self.f-self.damping(self.v)
    def explicit(self,h):
        self.geometry();self.f.sub_(self.damping(self.v));self.k.ground(self.x,self.v,self.mask,self.f);self.k.step(self.x,self.v,self.f,self.inv,self.gravity,h)
    def implicit(self,h,tol=1e-10,maxiter=256,profile=False):
        tick=time.perf_counter();self.geometry()
        if profile:torch.cuda.synchronize()
        tf=time.perf_counter();self.k.ground(self.x,self.v,self.mask,self.f)
        if profile:torch.cuda.synchronize()
        tg=time.perf_counter()
        # Symmetric mass scaling: A = I+h M^-1/2 C M^-1/2 on free DOFs.
        root=self.mass.sqrt();scale=self.free/root
        b=(root*self.v+h*(self.f/root+root*self.gravity))*self.free
        d=1+h*self.diag/(self.mass)
        def op(p):return p+h*scale*self.damping(scale*p)
        y=root*self.v;r=b-op(y);p=r/d;rz=(r*p).sum();bn=b.norm().item();it=0
        if bn>0:
            for it in range(1,maxiter+1):
                ap=op(p);alpha=rz/(p*ap).sum();y=y+alpha*p;r=r-alpha*ap
                if it%8==0 and r.norm().item()<=tol*bn:break
                zz=r/d;new=(r*zz).sum();p=zz+(new/rz)*p;rz=new
            true_res=(b-op(y)).norm().item()/bn
            if not np.isfinite(true_res) or true_res>1e-9:raise RuntimeError(f'PCG failed: {it} iterations, residual {true_res}')
        else:true_res=0
        if profile:torch.cuda.synchronize()
        ts=time.perf_counter();self.v.copy_(scale*y);self.x.add_(h*self.v);self.guess.copy_(y)
        if profile:torch.cuda.synchronize()
        return {'iterations':it,'relative_residual':true_res,'force_wall_s':tf-tick,'ground_wall_s':tg-tf,'solve_wall_s':ts-tg,'integration_wall_s':time.perf_counter()-ts}
    def arrays(self):return self.x.cpu().numpy().copy(),self.v.cpu().numpy().copy()
    def capture_implicit(self,h,iterations=80,fused=False):
        """Same IMEX equations, fixed PCG cap, GPU-tracked true residual each step.
        CUDA graph removes Python dispatch/synchronization overhead. Does not
        approximate geometry, alter coefficients or skip physical intervals.
        """
        self.graph_max_residual=torch.zeros((),dtype=torch.float64,device='cuda')
        root=self.mass.sqrt();scale=self.free/root
        # External graph inputs MUST keep live Python tensor ownership. Otherwise
        # allocator reuse by sampling can silently overwrite these arrays.
        self.graph_root=root;self.graph_scale=scale
        if fused:
            if not hasattr(self,'csr'):self.enable_gather()
            self.cg_scalars=torch.zeros(4+(self.x.numel()+255)//256,dtype=torch.float64,device='cuda');self.cg_z=torch.zeros_like(self.x);self.cg_ap=torch.zeros_like(self.x)
            # C++ operator expects one scale per coordinate, retain contiguous input.
            self.graph_scale=scale.expand_as(self.x).contiguous();scale=self.graph_scale
        def body():
            self.geometry();self.k.ground(self.x,self.v,self.mask,self.f)
            rhs=(root*self.v+h*(self.f/root+root*self.gravity))*self.free
            d=1+h*self.diag/self.mass
            def op(p):
                if fused:
                    self.k.pcg_op(p,scale,self.t,self.j,self.weight,*self.csr,self.rate,self.cg_ap,h);return self.cg_ap
                return p+h*scale*self.damping(scale*p)
            y=root*self.v;r=rhs-op(y);p=r/d;rz=(r*p).sum()
            if fused:
                self.cg_scalars[0].copy_(rz);self.cg_y=y;self.cg_r=r;self.cg_p=p;self.cg_d=d
                for _ in range(iterations):
                    ap=op(p);self.k.pcg_iteration(y,r,p,ap,d,self.cg_z,self.cg_scalars)
            else:
                for _ in range(iterations):
                    ap=op(p);alpha=rz/(p*ap).sum().clamp_min(1e-300);y=y+alpha*p;r=r-alpha*ap;zz=r/d;new=(r*zz).sum();p=zz+(new/rz.clamp_min(1e-300))*p;rz=new
            residual=(rhs-op(y)).norm()/rhs.norm().clamp_min(1e-300)
            self.graph_max_residual.copy_(torch.maximum(self.graph_max_residual,residual))
            self.v.copy_(scale*y);self.x.add_(h*self.v);self.guess.copy_(y)
        warm=torch.cuda.Stream();warm.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(warm):
            for _ in range(3):body()
        torch.cuda.current_stream().wait_stream(warm);torch.cuda.synchronize();self.reset();self.graph_max_residual.zero_()
        self.graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph):body()
        self.reset();self.graph_max_residual.zero_()
        return self.graph

def numpy_force(z,x,v):
    """Independent vectorized float64 transcription, no CUDA/shared gradients."""
    t=z['tet_indices'];dm=z['tet_poses'];D=(x[t[:,1:]]-x[t[:,0]][:,None]).transpose(0,2,1);Dv=(v[t[:,1:]]-v[t[:,0]][:,None]).transpose(0,2,1);F=D@dm;Fv=Dv@dm;V=1/np.linalg.det(dm)/6
    Ic=np.square(np.diagonal(F,axis1=1,axis2=2)).sum(1)
    P=F*(z['tet_mu']*V*(1-1/(Ic+1)))[:,None,None]+Fv*(z['tet_damping']*V)[:,None,None]
    H=P@dm.transpose(0,2,1)
    dx=D.transpose(0,2,1);j=np.stack([np.cross(dx[:,1],dx[:,2]),np.cross(dx[:,2],dx[:,0]),np.cross(dx[:,0],dx[:,1])],axis=1)*np.linalg.det(dm)[:,None,None]
    s=np.einsum('eia,eia->e',j,(v[t[:,1:]]-v[t[:,0]][:,None]))
    a=1+.75*z['tet_mu']/z['tet_lambda'];vf=(np.linalg.det(F)-a+z['tet_activations'])*z['tet_lambda']*V+s*z['tet_damping']*V
    local=-H.transpose(0,2,1)-j*vf[:,None,None];local=np.concatenate([-local.sum(1)[:,None],local],axis=1)
    out=np.zeros_like(x);np.add.at(out,t.ravel(),local.reshape(-1,3));return out
