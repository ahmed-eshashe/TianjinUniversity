"""Isolated CUDA evaluation of fixed v07 topology; CPU preparation is explicit.

All coefficients, quadrature, full mass, supports and material laws come from the
reference. No lumping or order/timestep change. The dense inverse is only an
equivalent way to apply the same full mass solve, and is residual-checked.
"""
from pathlib import Path
import time
import numpy as np
from scipy.sparse import csr_matrix, block_diag
import warp as wp

W = Path(__file__).resolve().parents[1]
wp.config.kernel_cache_dir = str(W/'cache/warp')
wp.config.enable_backward = False
wp.init()
import gpu_kernels as k


def gradient_csr(gradients, weights=None):
    pat = sum(abs(g) for g in gradients)
    if weights is not None:
        pat += abs(weights)
    pat = pat.tocsr(); pat.eliminate_zeros(); pat.sort_indices()
    rows = np.repeat(np.arange(pat.shape[0]), np.diff(pat.indptr))
    grad = np.stack([np.asarray(g[rows,pat.indices]).ravel() for g in gradients],axis=1)
    vals = None if weights is None else np.asarray(weights[rows,pat.indices]).ravel()
    return pat.indptr,pat.indices,grad,vals


class GPUReference:
    def __init__(self, cpu, external=None, mode=0, duration=.001, dt=3.90625e-7):
        begin = time.perf_counter()
        self.cpu = cpu
        self.dt, self.mode, self.duration = dt, mode, duration
        self.time0, self.steps0 = cpu.time, cpu.steps
        self.steps = 0; self.graphs = {}; self.device = 'cuda:0'; self.arrays = []
        pieces = list(cpu.pieces.values()); self.keys = list(cpu.pieces)
        self.offsets = np.r_[0,np.cumsum([len(p.q) for p in pieces])].astype(np.int32)
        self.ng = int(self.offsets[-1]); self.nq = sum(len(p.volumes) for p in pieces)
        self.nobs = sum(len(p.X) for p in pieces)
        A, R = [], []
        self.inverse_residuals = []
        for p in pieces:
            inv = p.factor.solve(np.eye(len(p.q)))
            self.inverse_residuals.append(float(np.linalg.norm(p.M@inv-np.eye(len(p.q)),ord=np.inf)))
            reaction = -p.S.T@p.Hinv@(p.S@inv) if p.Z is not None else np.zeros_like(inv)
            mobility = inv + inv@reaction
            A.append(csr_matrix(mobility)); R.append(csr_matrix(reaction))
        G = [block_diag([p.G[i] for p in pieces],format='csr') for i in range(3)]
        H = [block_diag([p.H[i] for p in pieces],format='csr') for i in range(3)]
        O = block_diag([p.O for p in pieces],format='csr')
        self.force0 = np.zeros_like(cpu.X) if external is None else np.array(external)
        load = np.concatenate([p.O.T@self.force0[p.indices] for p in pieces])
        self.preparation_s = time.perf_counter()-begin
        upload = time.perf_counter()
        def arr(value, dtype):
            a = wp.array(np.ascontiguousarray(value),dtype=dtype,device=self.device)
            self.arrays.append(a); return a
        self.arr = arr
        def gc(gradients,weights=None):
            ptr,ids,g,v = gradient_csr(gradients,weights)
            out = [arr(ptr,int),arr(ids,int),arr(g,wp.vec3d)]
            if weights is not None: out.append(arr(v,wp.float64))
            return out
        def matrix(m):
            m=m.tocsr();return [arr(m.indptr,int),arr(m.indices,int),arr(m.data,wp.float64)]
        self.G = gc(G); self.GT = gc([g.T for g in G]); self.H = gc(H,O)
        self.M = matrix(block_diag([p.M for p in pieces],format='csr'))
        self.A = matrix(block_diag(A,format='csr')); self.R = matrix(block_diag(R,format='csr'))
        self.piece_ptr = arr(self.offsets,int)
        self.q = arr(np.concatenate([p.q for p in pieces]),wp.vec3d)
        self.v = arr(np.concatenate([p.vg for p in pieces]),wp.vec3d)
        self.vol = arr(np.concatenate([p.volumes for p in pieces]),wp.float64)
        self.translation = arr(np.concatenate([p.translation for p in pieces]),wp.float64)
        self.fixed = arr(np.concatenate([p.fixed for p in pieces]).astype(np.int32),int)
        self.load = arr(load,wp.vec3d)
        self.clock = arr(np.array([0],np.int32),int); self.bad = arr(np.array([0],np.int32),int)
        for name in ['a','r','f','impulse','moment']:
            setattr(self,name,arr(np.zeros((self.ng,3)),wp.vec3d))
        for name in ['err','scale']:
            setattr(self,name,arr(np.zeros(self.ng),wp.float64))
        self.P = arr(np.zeros((self.nq,3,3)),wp.mat33d); self.energy = arr(np.zeros(self.nq),wp.float64)
        self.partial_force = arr(np.zeros((self.ng,32,3)),wp.vec3d)
        self.mu,self.lam = pieces[0].mu,pieces[0].lam
        if not all(p.mu==self.mu and p.lam==self.lam for p in pieces):
            raise ValueError('This comparison supports one material')
        self.base_impulse = {key:p.support_impulse.copy() for key,p in cpu.pieces.items()}
        self.base_moment = {key:p.support_moment.copy() for key,p in cpu.pieces.items()}
        wp.synchronize_device(self.device)
        self.upload_s = time.perf_counter()-upload
        self.module_load_s = 0.; self.graph_build_s = 0.
        self.snap = {name:wp.clone(getattr(self,name)) for name in ['q','v','impulse','moment','clock']}

    def launch(self,kernel,n,args):
        wp.launch(kernel,dim=n,inputs=args,device=self.device)

    def evaluate(self,stage=0):
        self.launch(k.stress,self.nq,[*self.G,self.q,self.vol,self.mu,self.lam,self.P,self.energy,self.bad])
        self.launch(k.force_partial,(self.ng,32),[*self.GT,self.P,self.partial_force])
        self.launch(k.force_reduce,self.ng,[self.partial_force,self.load,self.clock,self.dt,self.time0,self.duration,self.mode,stage,self.f])
        self.launch(k.solve,self.ng,[*self.A,*self.R,self.f,self.a,self.r])
        self.launch(k.mass_residual,self.ng,[*self.M,self.a,self.f,self.r,self.err,self.scale])
        self.launch(k.mass_guard,len(self.keys),[self.piece_ptr,self.err,self.scale,self.bad])
        self.launch(k.observation_guard,self.nobs,[*self.H,self.fixed,self.q,self.a,self.bad])

    def one(self):
        self.evaluate(0)
        self.launch(k.drift,self.ng,[self.q,self.v,self.a,self.r,self.translation,self.dt,self.impulse,self.moment,self.bad])
        self.evaluate(1)
        self.launch(k.kick,self.ng,[self.q,self.v,self.a,self.r,self.translation,self.dt,self.impulse,self.moment,self.bad])
        self.launch(k.advance,1,[self.clock,self.bad])

    def graph(self,n):
        if n not in self.graphs:
            start=time.perf_counter();wp.load_module(module=k,device=self.device)
            wp.synchronize_device(self.device);self.module_load_s+=time.perf_counter()-start
            start=time.perf_counter();wp.capture_begin(device=self.device)
            try:
                for _ in range(n):self.one()
            finally:
                graph=wp.capture_end(device=self.device)
            self.graphs[n]=graph;self.graph_build_s+=time.perf_counter()-start
        return self.graphs[n]

    def step(self,n=1,graph=True,block=32):
        if n<=0:raise ValueError('positive steps required')
        graphs=[]
        if graph:
            full,rem=divmod(n,block)
            if full:graphs.extend([self.graph(block)]*full)
            if rem:graphs.append(self.graph(rem))
        for name,saved in self.snap.items():wp.copy(saved,getattr(self,name))
        self.bad.zero_()
        if graph:
            for g in graphs:wp.capture_launch(g)
        else:
            for _ in range(n):self.one()
        code=int(self.bad.numpy()[0])
        if code:
            for name,saved in self.snap.items():wp.copy(getattr(self,name),saved)
            self.bad.zero_();wp.synchronize_device(self.device)
            raise RuntimeError(f'GPU trial rejected (guard {code}); complete chunk restored')
        self.steps+=n

    def export(self):
        q,v,imp,mom=[getattr(self,name).numpy() for name in ['q','v','impulse','moment']]
        for i,(key,p) in enumerate(self.cpu.pieces.items()):
            sl=slice(self.offsets[i],self.offsets[i+1]);p.q=q[sl].copy();p.vg=v[sl].copy()
            p.support_impulse=self.base_impulse[key]+imp[sl].sum(axis=0)
            p.support_moment=self.base_moment[key]+mom[sl].sum(axis=0)
            p.time=self.time0+self.steps*self.dt;p.steps=self.steps0+self.steps;p.update_state()
        self.cpu.time=self.time0+self.steps*self.dt;self.cpu.steps=self.steps0+self.steps
        return self.cpu

    def field_values(self):
        self.bad.zero_();self.evaluate();code=int(self.bad.numpy()[0])
        if code:raise RuntimeError(f'GPU field failed guard {code}')
        return {'force':self.f.numpy(),'acceleration':self.a.numpy(),'reaction':self.r.numpy(),
                'strain_energy':float(self.energy.numpy().sum()),'mass_residual':float(np.sqrt(self.err.numpy().sum()/max(self.scale.numpy().sum(),1e-24)))}

    def memory(self):
        return sum(a.size*wp.types.type_size_in_bytes(a.dtype) for a in self.arrays+list(self.snap.values()))
