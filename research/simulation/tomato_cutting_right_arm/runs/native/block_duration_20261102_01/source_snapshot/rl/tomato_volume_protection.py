"""Offline hybrid spring/volume barrier; no Newton implementation or dynamics."""
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve,eigsh
from tomato_nonlinear_checks import spring_state


class InfeasibleVolume(ValueError):
    pass


class ProtectedModel:
    """One-sided local volume barrier, active below J=0.5, divergent at J=0.1.

    Barrier is C1 at activation, with a Hessian jump. Rest stiffness is unchanged.
    Reference volume cells now generate forces; this is explicitly a hybrid model.
    """
    def __init__(self,points,pairs,rest,stiffness,cells,reference_volumes,
                 modulus_pa=10000.,activation=.5,floor=.1):
        if not (0<floor<activation<1) or not np.isfinite(modulus_pa) or modulus_pa<=0:
            raise ValueError('Invalid protection parameters')
        self.pairs=pairs;self.rest=rest;self.stiffness=stiffness;self.cells=cells
        self.volumes=np.asarray(reference_volumes);self.activation=activation;self.floor=floor;self.modulus=modulus_pa
        if np.any(self.volumes<=0):raise ValueError('Invalid reference cells')

    def evaluate(self,x,*,tangent=False):
        p=np.asarray(x)[self.cells];d=p[:,1:]-p[:,:1]
        ratios=np.linalg.det(d)/(6*self.volumes)
        if not np.isfinite(ratios).all() or np.min(ratios)<=self.floor+1e-12:
            raise InfeasibleVolume('Trial crosses protected material-volume floor')
        state=spring_state(x,self.pairs,self.rest,self.stiffness,tangent=tangent)
        active=ratios<self.activation
        indices=np.flatnonzero(active);barrier_energy=0.
        if len(indices):
            j=ratios[indices];v=self.volumes[indices];r=(j-self.floor)/(self.activation-self.floor)
            phi=-np.log(r)+r-1
            prime=(1-1/r)/(self.activation-self.floor)
            second=1/r**2/(self.activation-self.floor)**2
            inverse=np.linalg.inv(d[indices]);gn=np.empty((len(indices),4,3))
            gn[:,1:]=inverse.transpose(0,2,1);gn[:,0]=-gn[:,1:].sum(axis=1)
            grad_j=j[:,None,None]*gn
            barrier_energy=float(np.sum(self.modulus*v*phi))
            grad=(self.modulus*v*prime)[:,None,None]*grad_j
            np.add.at(state['gradient_n'],self.cells[indices].reshape(-1),grad.reshape(-1,3))
            if tangent:
                hj=j[:,None,None,None,None]*(np.einsum('nai,nbj->naibj',gn,gn)-np.einsum('naj,nbi->naibj',gn,gn))
                g=grad_j.reshape(-1,12)
                h=(self.modulus*v)[:,None,None]*(second[:,None,None]*g[:,:,None]*g[:,None,:]+prime[:,None,None]*hj.reshape(-1,12,12))
                dofs=(3*self.cells[indices,:,None]+np.arange(3)).reshape(-1,12)
                rows=np.broadcast_to(dofs[:,:,None],h.shape).reshape(-1)
                cols=np.broadcast_to(dofs[:,None,:],h.shape).reshape(-1)
                state['tangent_n_m']+=coo_matrix((h.reshape(-1),(rows,cols)),shape=state['tangent_n_m'].shape).tocsr()
        state['spring_energy_j']=state['energy_j'];state['barrier_energy_j']=barrier_energy
        state['energy_j']+=barrier_energy
        state['min_cell_ratio']=float(ratios.min());state['active_volume_cells']=len(indices)
        return state


def feasible_solve(model,points,initial,free,fixed,reference_diagonal,max_iterations=160):
    """Quasi-static descent; inadmissible trials are rejected, never projected."""
    vector=np.asarray(initial).reshape(-1).copy();records=[];escapes=0
    pre=diags(1/np.sqrt(reference_diagonal))
    for iteration in range(max_iterations+1):
        state=model.evaluate(points+vector.reshape(-1,3),tangent=True)
        g=state['gradient_n'].reshape(-1)
        residual=float(np.linalg.norm(g[free])/max(np.linalg.norm(g[fixed]),1e-15))
        records.append({'iteration':iteration,'force_residual_fraction':residual,
                        'min_cell_ratio':state['min_cell_ratio'],'energy_j':state['energy_j']})
        if residual<1e-7:
            scaled=pre@state['tangent_n_m'][free][:,free]@pre
            eigen,basis=eigsh(scaled,k=1,which='SA',tol=1e-5,maxiter=800)
            if eigen[0]>=-1e-6:return vector,records,True
            if escapes>=6:return vector,records,False
            # Seek a lower-energy branch along true negative curvature. This
            # changes a static initial guess, never physical parameters or a trajectory.
            direction=np.asarray(pre@basis[:,0]).reshape(-1)
            direction*=.0001/np.max(np.abs(direction))
            candidates=[]
            for sign in (-1.,1.):
                alpha=1.
                while alpha>1e-8:
                    trial_vector=vector.copy();trial_vector[free]+=sign*alpha*direction
                    try:
                        trial=model.evaluate(points+trial_vector.reshape(-1,3))
                        if trial['energy_j']<state['energy_j']:
                            candidates.append((trial['energy_j'],trial_vector));break
                    except InfeasibleVolume:pass
                    alpha*=.5
            if not candidates:return vector,records,False
            vector=min(candidates,key=lambda item:item[0])[1];escapes+=1
            records[-1]['negative_curvature_escape']=True
            continue
        if iteration==max_iterations:break
        h=state['tangent_n_m'][free][:,free]
        step=spsolve(h,-g[free]);slope=float(g[free]@step)
        if not np.isfinite(step).all() or slope>=0:
            scaled=pre@h@pre
            least=float(eigsh(scaled,k=1,which='SA',return_eigenvectors=False,tol=1e-5,maxiter=800)[0])
            # Numerical direction shift only; exact model energy and tangent are unmodified.
            shift=max(.01,-least+.01)
            step=np.asarray(pre@spsolve(scaled+diags(np.full(len(free),shift)),-(pre@g[free]))).reshape(-1)
            slope=float(g[free]@step)
        alpha=1.
        while alpha>1e-10:
            candidate=vector.copy();candidate[free]+=alpha*step
            try:
                trial=model.evaluate(points+candidate.reshape(-1,3))
                if trial['energy_j']<=state['energy_j']+1e-4*alpha*slope:break
            except InfeasibleVolume:
                pass
            alpha*=.5
        if alpha<=1e-10:return vector,records,False
        vector=candidate
    return vector,records,False
