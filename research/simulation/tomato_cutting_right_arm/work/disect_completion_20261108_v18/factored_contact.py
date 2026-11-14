from pathlib import Path
import sys,time,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'disect_precontact_20261108_v06/backend'))
from numerics import Bulk,torch
class FactoredContactBulk(Bulk):
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
            r=-g;delta=torch.zeros_like(y);p=self.precondition(r,h);rz=(r*p).sum();bn=r.norm().item()
            for it in range(1,maxiter+1):
                hp=H(p);den=(p*hp).sum();alpha=rz/den;delta=delta+alpha*p;r=r-alpha*hp
                if it%8==0 and r.norm().item()<=tol*bn:break
                zz=self.precondition(r,h);nr=(r*zz).sum();p=zz+(nr/rz)*p;rz=nr
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

    def precondition(self,r,h):
        # Solve the constant deviatoric viscous block exactly. This changes only
        # the linear solver preconditioner, never the evaluated material force.
        from scipy.sparse import coo_matrix,diags
        from scipy.sparse.linalg import splu
        if not hasattr(self,'_factor_h') or self._factor_h!=h:
            z=self.z;t=z['tet_indices'];dm=z['tet_poses'];G=np.concatenate([-dm.sum(1)[:,None],dm],axis=1);weight=z['tet_damping']/(6*np.linalg.det(dm));local=weight[:,None,None]*(G@G.transpose(0,2,1));L=coo_matrix((local.ravel(),(np.broadcast_to(t[:,:,None],local.shape).ravel(),np.broadcast_to(t[:,None,:],local.shape).ravel())),shape=(len(self.x),len(self.x))).tocsc()
            self._factor_free=np.flatnonzero(z['particle_inv_mass']>0);self._factor_mass=z['physical_mass'];free=self._factor_free
            self._factor=splu((diags(self._factor_mass)+h*L)[free][:,free].tocsc());self._factor_h=h
        root=np.sqrt(self._factor_mass)[:,None];rhs=r.cpu().numpy()*root;ans=np.zeros_like(rhs);free=self._factor_free;ans[free]=self._factor.solve(rhs[free]);ans*=root
        return torch.as_tensor(ans,device=r.device,dtype=r.dtype)
