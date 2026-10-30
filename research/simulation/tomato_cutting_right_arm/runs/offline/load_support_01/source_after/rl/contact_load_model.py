"""Static finite-contact wrench model; offline evidence, not a grasp oracle."""
import numpy as np
from scipy.optimize import linprog


def solve_contact_load(contacts,com,gravity_force,mu=.6,scale=1.,normal_cap=10.,
                       required_parts=(),required_inner=(),torque_caps=None,sides=8,balance_moments=True,minimize_budget_scale=False):
    """Shared per-part budgets prevent adding points from inventing grip force.

    Each input normal points OUT of the object. Forces on the object are -normal
    plus tangential friction. Torque Jacobians map joint rates to hand material
    point velocities in the same object frame. Zero patch torsion is assumed.
    """
    if not contacts or not np.isfinite(mu) or mu<0 or not np.isfinite(scale) or scale<=0 or not isinstance(sides,int) or sides<4 or not np.isfinite(normal_cap) or normal_cap<=0:
        raise ValueError('Invalid finite-contact load problem')
    com=np.asarray(com,dtype=float);gravity=np.asarray(gravity_force,dtype=float)
    if com.shape!=(3,) or gravity.shape!=(3,) or not np.isfinite(com).all() or not np.isfinite(gravity).all():
        raise ValueError('Nonfinite or malformed mass properties')
    rays=[];wrenches=[];torques=[]
    for c in contacts:
        n=np.asarray(c['normal'],dtype=float);p=np.asarray(c['point'],dtype=float)
        if n.shape!=(3,) or p.shape!=(3,) or not np.isfinite(n).all() or not np.isfinite(p).all() or np.linalg.norm(n)<1e-9:
            raise ValueError('Invalid contact point/normal')
        n=n/np.linalg.norm(n);seed=np.eye(3)[np.argmin(abs(n))];u=np.cross(n,seed);u/=np.linalg.norm(u);v=np.cross(n,u)
        for theta in np.arange(sides)*2*np.pi/sides:
            f=-n+mu*(np.cos(theta)*u+np.sin(theta)*v)
            rays.append(f);wrenches.append(np.r_[f,np.cross(p-com,f)])
            if torque_caps is not None:
                j=np.asarray(c['jacobian'])
                if j.shape!=(3,len(torque_caps)) or not np.isfinite(j).all():raise ValueError('Invalid generalized point Jacobian')
                torques.append(j.T@-f)
    parts=sorted({c['part'] for c in contacts});a=[];b=[]
    def group(predicate):
        return np.repeat([float(predicate(c)) for c in contacts],sides)
    for part in parts:
        a.append(group(lambda c:c['part']==part));b.append(normal_cap)
    for part in required_parts:
        a.append(-group(lambda c:c['part']==part));b.append(-.06)
    for part in required_inner:
        a.append(-group(lambda c:c['part']==part and c.get('inner',False)));b.append(-.06)
    if torque_caps is not None:
        torque=np.asarray(torques).T;caps=np.asarray(torque_caps,dtype=float)
        if not np.isfinite(caps).all() or np.any(caps<=0):raise ValueError('Invalid actuator budget')
        a.extend(torque);b.extend(caps);a.extend(-torque);b.extend(caps)
    matrix=np.asarray(wrenches).T;rhs=np.r_[-scale*gravity,[0.,0.,0.]]
    eq=matrix if balance_moments else matrix[:3];eq_rhs=rhs if balance_moments else rhs[:3]
    ub=np.asarray(a);ub_rhs=np.asarray(b);objective=np.ones(len(rays))
    if minimize_budget_scale:
        # A diagnostic relaxation only. All per-part and actuator upper budgets
        # share one scale; required support minima are not relaxed.
        ub=np.c_[ub,np.where(ub_rhs>=0,-ub_rhs,0.)]
        ub_rhs=np.where(ub_rhs>=0,0.,ub_rhs)
        eq=np.c_[eq,np.zeros(len(eq))];objective=np.r_[objective*1e-7,1.]
    fit=linprog(objective,A_eq=eq,b_eq=eq_rhs,A_ub=ub,b_ub=ub_rhs,
                bounds=(0,None),method='highs',options={'time_limit':10.})
    within=bool(fit.success and (not minimize_budget_scale or fit.x[-1]<=1.+1e-7))
    result={'feasible':within,'solver_status':int(fit.status),'solver_message':fit.message,
            'point_count':len(contacts),'mu':mu,'gravity_scale':scale,'shared_normal_cap_per_part_n':normal_cap,
            'friction_sides':sides,'torque_limits_enforced':torque_caps is not None,
            'moments_balanced':balance_moments,
            'budget_scaling_diagnostic':minimize_budget_scale,
            'required_parts':list(required_parts),'required_inner_parts':list(required_inner),
            'scope':'Static hypothetical contact set; no physical settling, no compliance or patch torsion; robot self-weight not allocated'}
    if fit.success:
        weights=fit.x[:-1] if minimize_budget_scale else fit.x
        if minimize_budget_scale:result['required_budget_scale']=float(fit.x[-1])
        lambdas=weights.reshape(-1,sides);forces=np.einsum('ij,ijk->ik',lambdas,np.asarray(rays).reshape(-1,sides,3))
        normal=lambdas.sum(1)
        result.update(normal_force_per_point_n=normal.tolist(),force_per_point_on_object_n=forces.tolist(),
                      normal_force_per_part_n={p:float(sum(normal[i] for i,c in enumerate(contacts) if c['part']==p)) for p in parts},
                      force_balance_residual_n=float(np.linalg.norm((matrix@weights-rhs)[:3])),
                      torque_balance_residual_nm=float(np.linalg.norm((matrix@weights-rhs)[3:])))
        if torque_caps is not None:
            result['generalized_knife_load_torque_nm']=(torque@weights).tolist()
            result['max_actuator_knife_load_fraction']=float(np.max(abs(torque@weights)/caps))
    return result
