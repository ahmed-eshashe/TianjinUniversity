"""Versioned offline contact-set-independent numerical search.

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
        # Build one support-free numerical metric independent of which
        # contact rows are active. Changing an active set must not silently
        # change the quadratic objective at an unchanged position.
        raw=np.abs(H.diagonal());positive=raw[raw>0]
        floor=max(float(np.median(positive))*1e-6 if len(positive) else 0.,1e-6)
        metric_diagonal=np.maximum(raw,floor)
        P=diags(1/np.sqrt(metric_diagonal[free]),format='csr')
        normalized=(P@H[free][:,free]@P).tocsr()
        least=0.;eigen_residual=0.;shift=0.;count=[0]
        if len(free):
            if len(free)<=3:
                values,vectors=np.linalg.eigh(normalized.toarray());least=float(values[0]);mode=vectors[:,0]
            else:
                values,vectors=eigsh(normalized,k=1,which='SA',tol=1e-5,maxiter=1600,ncv=min(80,len(free)),v0=np.ones(len(free)))
                least=float(values[0]);mode=vectors[:,0]
            eigen_residual=float(np.linalg.norm(normalized@mode-least*mode))
            shift=max(0.,1e-4-least+2*eigen_residual)
        search_H=H+diags(shift*metric_diagonal,format='csr')
        h=(T.T@search_H@T).tocsr()
        if h.shape[0]:
            rhs=-np.asarray(T.T@(g+search_H@particular)).ravel()
            d=h.diagonal();lower=tril(h,format='csr');upper=triu(h,format='csr')
            if np.any(d<=0):raise ValueError('Invalid numerical search diagonal')
            def precondition(v):return spsolve_triangular(upper,d*spsolve_triangular(lower,v,lower=True),lower=False)
            def counted(_):count[0]+=1
            step,info=cg(h,rhs,M=LinearOperator(h.shape,matvec=precondition),rtol=1e-9,atol=1e-12,maxiter=2500,callback=counted)
            if info:raise ValueError('Global numerical search did not converge')
            direction=particular+np.asarray(T@step).ravel()
        else:direction=particular
        if not np.isfinite(direction).all() or float(g@direction)>1e-12:
            raise ValueError('Global numerical search did not give descent')
        # The normal multipliers must belong to the SAME numerical quadratic
        # as the direction. The shift here can have an active normal component.
        effective=g+search_H@direction
        loads=lsmr(Af[active].T,effective[free],atol=1e-13,btol=1e-13,maxiter=2500) if active else None
        lam[:]=0.
        if active:lam[active]=loads[0]
        gap=C@x-b;residual=g-C.T@lam
        scale=max(np.linalg.norm(g[ids]),np.linalg.norm(C.T@lam),1e-4)
        relative=float(np.linalg.norm(residual[free])/scale)
        record={'iteration':iteration,'force_residual':relative,'min_gap_m':float(gap.min()),'energy_j':state['energy_j'],
                'search_metric':'global_support_free_search' if shift else 'physical_newton','numerical_search_space':'all_support_free_dofs','search_normalized_least_eigenvalue':least,'search_eigen_residual':eigen_residual,'search_diagonal_shift':shift,'physical_energy_force_tangent_unchanged':True,'min_J':state.get('min_cell_ratio',1.),'active_constraints':len(active),'linear_iterations':count[0],
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
