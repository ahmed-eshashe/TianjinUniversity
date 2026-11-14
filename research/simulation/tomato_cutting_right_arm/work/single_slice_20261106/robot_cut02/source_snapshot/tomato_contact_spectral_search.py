"""Versioned offline spectrally safeguarded active-set search.

Not a physical regularization or a physical stability certificate.

Only optimizer directions change. Exact energy, forces, unilateral constraints
and final physical tangent remain those of the supplied model. No time stepping,
physical stiffness shift, damping, damage updates or simulator imports.
"""
import numpy as np
from scipy.sparse import tril,triu,diags
from scipy.sparse.linalg import cg,LinearOperator,spsolve_triangular,lsmr,eigsh
from tomato_linear_contact import affine_space,feasible_guess,independent_rows
from tomato_volume_protection import InfeasibleVolume


def solve_contact_continuation(model,initial,fixed,C,b,max_iterations=30,initial_active=None):
    C=C.tocsr();x=feasible_guess(np.asarray(initial).ravel(),C,b,fixed)
    ids=np.array(sorted(fixed),dtype=int);free=np.setdiff1d(np.arange(x.size),ids)
    Af=C[:,free];trace=[];lam=np.zeros(len(b));success=False
    active=independent_rows(C,np.flatnonzero(C@x-b<=1e-10) if initial_active is None else initial_active,fixed,x.size)
    for iteration in range(max_iterations):
        state=model.evaluate(x.reshape(-1,3),tangent=True);g=state['gradient_n'].ravel();H=state['tangent_n_m']
        offset,T=affine_space(C[active],b[active],fixed,x.size)
        particular=offset+T@(T.T@(x-offset))-x
        physical_h=(T.T@H@T).tocsr()
        # A dimensionless shift changes ONLY the reduced numerical search.
        # Off-diagonal physical coupling is retained. Physical H/E/g are intact.
        diagonal=physical_h.diagonal()
        positive=np.abs(diagonal[diagonal!=0])
        floor=max(float(np.median(positive))*1e-6 if len(positive) else 0.,1e-6)
        scale_vector=1/np.sqrt(np.maximum(np.abs(diagonal),floor))
        P=diags(scale_vector,format='csr');normalized=(P@physical_h@P).tocsr()
        least=0.;eigen_residual=0.;shift=0.;count=[0]
        if len(diagonal):
            if len(diagonal)<=3:
                values,vectors=np.linalg.eigh(normalized.toarray());least=float(values[0]);mode=vectors[:,0]
            else:
                values,vectors=eigsh(normalized,k=1,which='SA',tol=1e-5,maxiter=1600,ncv=min(80,len(diagonal)),v0=np.ones(len(diagonal)))
                least=float(values[0]);mode=vectors[:,0]
            eigen_residual=float(np.linalg.norm(normalized@mode-least*mode))
            shift=max(0.,1e-4-least+2*eigen_residual)
            h=normalized+shift*diags(np.ones(len(diagonal)),format='csr')
            rhs=-np.asarray(P@T.T@(g+H@particular)).ravel()
            d=h.diagonal();lower=tril(h,format='csr');upper=triu(h,format='csr')
            def precondition(v):return spsolve_triangular(upper,d*spsolve_triangular(lower,v,lower=True),lower=False)
            def counted(_):count[0]+=1
            step,info=cg(h,rhs,M=LinearOperator(h.shape,matvec=precondition),rtol=1e-9,atol=1e-12,maxiter=2500,callback=counted)
            if info:raise ValueError('Spectral numerical search did not converge')
            direction=particular+np.asarray(T@(P@step)).ravel()
        else:direction=particular
        if not np.isfinite(direction).all() or float(g@direction)>1e-12:
            raise ValueError('Spectral numerical search did not give descent')
        # Added reduced-space shift has no active normal component. Multiplier
        # prediction uses the original physical tangent; endpoint checks use g.
        effective=g+H@direction
        loads=lsmr(Af[active].T,effective[free],atol=1e-13,btol=1e-13,maxiter=2500) if active else None
        lam[:]=0.
        if active:lam[active]=loads[0]
        gap=C@x-b;residual=g-C.T@lam
        scale=max(np.linalg.norm(g[ids]),np.linalg.norm(C.T@lam),1e-4)
        relative=float(np.linalg.norm(residual[free])/scale)
        record={'iteration':iteration,'force_residual':relative,'min_gap_m':float(gap.min()),'energy_j':state['energy_j'],
                'search_metric':'spectral_reduced_search' if shift else 'physical_newton','search_normalized_least_eigenvalue':least,'search_eigen_residual':eigen_residual,'search_diagonal_shift':shift,'physical_energy_force_tangent_unchanged':True,'min_J':state.get('min_cell_ratio',1.),'active_constraints':len(active),'linear_iterations':count[0],
                'minimum_active_multiplier_n':float(lam[active].min()) if active else 0.}
        trace.append(record)
        if x.size>1000:print(record,flush=True)
        if relative<1e-7 and gap.min()>=-1e-10 and lam.min()>=-1e-9 and np.max(np.abs(lam*gap),initial=0.)<1e-10:
            success=True;break
        # An active normal constraint can push but cannot attract. Drop the
        # attractive constraints before computing the next tangent.
        negative=[i for i in active if lam[i]<-1e-9]
        if negative:
            active=[i for i in active if i not in negative];record['released_constraints']=[int(i) for i in negative];continue
        delta=C@direction;blocking=np.flatnonzero((delta < -1e-14)&(gap+delta < -1e-10))
        alpha=1.;hit=None
        if len(blocking):
            fractions=np.maximum(gap[blocking],0.)/(-delta[blocking]);j=int(np.argmin(fractions));alpha=min(1.,float(fractions[j]));hit=int(blocking[j])
        if alpha<1e-9 and hit is not None:
            new=independent_rows(C,active+[hit],fixed,x.size)
            if len(new)==len(active):raise ValueError('Dependent blocking contact: '+str({'row':hit,'gap':float(gap[hit]),'direction_gap':float(delta[hit]),'active':hit in active}))
            active=new;record['blocking_constraint']=hit;continue
        slope=float(g@direction)
        if slope>1e-12:raise ValueError('Constrained Newton direction is not descent')
        accepted=False
        while alpha>1e-10:
            trial=x+alpha*direction
            try:
                proposed=model.evaluate(trial.reshape(-1,3))
                if (C@trial-b).min()>=-1e-10 and proposed['energy_j']<=state['energy_j']+1e-4*alpha*min(slope,0.)+1e-14:
                    accepted=True;break
            except InfeasibleVolume:pass
            alpha*=.5;hit=None
        if not accepted:record['line_search_failed']=True;break
        x=trial;record['accepted_step_fraction']=alpha
        if hit is not None:active=independent_rows(C,active+[hit],fixed,x.size)
    state=model.evaluate(x.reshape(-1,3),tangent=True)
    if trace:trace[-1]['optimizer_active_rows']=[int(i) for i in active]
    return x.reshape(-1,3),lam,state,trace,success,np.flatnonzero(lam>1e-9).tolist(),ids,free


def solve_triangle_continuation(model,initial,fixed,geometry,*,max_iterations=30,initial_active=None):
    used=np.flatnonzero(geometry['active'])
    result=list(solve_contact_continuation(model,initial,fixed,geometry['matrix'][used],geometry['bounds'][used],max_iterations,initial_active))
    lam=np.zeros(len(geometry['bounds']));lam[used]=result[1];result[1]=lam;result[5]=used[result[5]].tolist()
    return tuple(result)
