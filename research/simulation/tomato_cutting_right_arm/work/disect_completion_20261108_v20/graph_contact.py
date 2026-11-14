from pathlib import Path
import sys,time,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_precontact_20261108_v06/backend'))
from numerics import Bulk,torch
class GraphContactBulk(Bulk):
    """Unchanged force law, viscous FEM and ground friction implicit together."""
    def reset(self):
        super().reset()
        for name in ['last_friction','last_normal','last_force']:
            if hasattr(self,name):getattr(self,name).zero_()
    def implicit(self,h,tol=1e-10,maxiter=256,profile=False):
        start=time.perf_counter();self.geometry();elastic=self.f.clone();fg=torch.zeros_like(self.x);self.k.ground(self.x,torch.zeros_like(self.v),self.mask,fg);self.f.copy_(elastic+fg)
        root=self.mass.sqrt();scale=self.free/root;rhs=(root*self.v+h*(self.f/root+root*self.gravity))*self.free;d0=1+h*self.diag/self.mass
        active=(self.x[:,1]<.001).to(torch.float64)*self.mask;limit=.2*torch.clamp(.001-self.x[:,1],min=0)*1000*self.mask;kf=1000*active
        k=torch.zeros_like(self.x);k[:,0]=kf;k[:,2]=kf;lim=torch.zeros_like(self.x);lim[:,0]=limit;lim[:,2]=limit
        def A(y):return y+h*scale*self.damping(scale*y)
        def friction(y):return torch.clamp(k*(scale*y),min=-lim,max=lim)
        def psi(y):
            vv=torch.abs(scale*y);kk=k.clamp_min(1.);return torch.where(k*vv<=lim,.5*k*vv*vv,lim*vv-.5*lim*lim/kk).sum()
        # Analytic independent-node friction solve is an INITIAL GUESS only.
        # The final velocity must still solve the full coupled equation below.
        ab=torch.abs(self.v);initial=torch.sign(self.v)*torch.maximum(ab/(1+h*k/self.mass),ab-h*lim/self.mass)
        y=root*initial;normalizer=max(rhs.norm().item(),1e-14);cg_total=0;maximum_inner=0.;newton=0;self.contact_trace=[]
        for newton in range(25):
            ay=A(y);g=ay-rhs+h*scale*friction(y);gn=g.norm().item()/normalizer
            self.contact_trace.append({'iteration':newton,'relative_residual':gn})
            if gn<=1e-9:break
            slope=k*(torch.abs(k*scale*y)<=lim);diag=d0+h*slope/self.mass
            def H(p):return A(p)+h*scale*scale*slope*p
            delta,it=self.solve_graph(-g,diag,h*scale*scale*slope,h,tol,maxiter)
            bn=g.norm().item()
            inner=(-g-H(delta)).norm().item()/max(bn,1e-30);maximum_inner=max(maximum_inner,inner);cg_total+=it
            if not np.isfinite(inner) or inner>1e-9:raise RuntimeError(f'Contact PCG residual {inner}')
            ad=A(delta);linear=((ay-rhs)*delta).sum();quad=(delta*ad).sum();descent=(g*delta).sum();oldpsi=psi(y);step=1.
            for ls in range(24):
                trial=y+step*delta;change=step*linear+.5*step*step*quad+h*(psi(trial)-oldpsi)
                if change.item()<=1e-4*step*descent.item()+1e-24:break
                step*=.5
            else:raise RuntimeError('Contact Newton line search failed')
            self.contact_trace[-1]['line_search_step']=step
            y=trial
        else:raise RuntimeError(f'Contact Newton cap; residual {gn}')
        v=scale*y;self.last_friction=-friction(y);self.last_normal=fg;self.last_force=elastic-self.damping(v)+fg+self.last_friction;self.v.copy_(v);self.x.add_(h*v);self.guess.copy_(y)
        return {'iterations':cg_total,'relative_residual':gn,'inner_max_residual':maximum_inner,'newton_iterations':newton,'wall_s':time.perf_counter()-start}

    def solve_graph(self,rhs,diag,extra,h,tol,maxiter):
        if not hasattr(self,'pcg_graph') or self.pcg_h!=h:
            if not hasattr(self,'csr'):self.enable_gather()
            self.pcg_h=h
            self.gs=(self.free/self.mass.sqrt()).expand_as(self.x).contiguous()
            self.gy=torch.zeros_like(self.x);self.gr=torch.zeros_like(self.x);self.gp=torch.zeros_like(self.x)
            self.ga=torch.zeros_like(self.x);self.gz=torch.zeros_like(self.x);self.gd=torch.ones_like(self.x);self.ge=torch.zeros_like(self.x)
            self.gc=torch.zeros(4+(self.x.numel()+255)//256,dtype=torch.float64,device='cuda')
            def body():
                for _ in range(8):
                    self.k.pcg_op(self.gp,self.gs,self.t,self.j,self.weight,*self.csr,self.rate,self.ga,h)
                    self.ga.add_(self.ge*self.gp)
                    self.k.pcg_iteration(self.gy,self.gr,self.gp,self.ga,self.gd,self.gz,self.gc)
            stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(stream):body()
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
            self.pcg_graph=torch.cuda.CUDAGraph()
            with torch.cuda.graph(self.pcg_graph):body()
        self.gy.zero_();self.gr.copy_(rhs);self.gd.copy_(diag);self.ge.copy_(extra)
        self.gp.copy_(rhs/diag);self.gc.zero_();self.gc[0].copy_((self.gr*self.gp).sum())
        bn=rhs.norm().item()
        for it in range(8,maxiter+1,8):
            self.pcg_graph.replay()
            if self.gr.norm().item()<=tol*bn:break
        return self.gy.clone(),it
