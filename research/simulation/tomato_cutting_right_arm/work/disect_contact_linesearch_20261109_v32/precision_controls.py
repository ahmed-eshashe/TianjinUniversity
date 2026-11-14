from pathlib import Path
from decimal import Decimal,localcontext
import json,math,torch
from stable_potential import unilateral_remainder,ground_remainder
W=Path(__file__).resolve().parent
D=Decimal.from_float
def tensor(x):return torch.tensor(x,dtype=torch.float64)
def q(x):return min(x,Decimal(0))**2/2
rows=[]
with localcontext() as ctx:
    ctx.prec=90
    for g in [-1e-5,-1e-17,0.,1e-17,1e-5]:
        for delta in [-3e-5,-3e-17,-1e-25,0.,1e-25,3e-17,3e-5]:
            exact=q(D(g)+D(delta))-q(D(g))-min(D(g),Decimal(0))*D(delta)
            got=float(unilateral_remainder(tensor(g),tensor(delta)))
            error=abs(got-float(exact));scale=max(abs(float(exact)),1e-24)
            assert error<=1e-10*scale
            rows.append(dict(kind='one_sided',g=g,delta=delta,error=error,normalized_error=error/scale))
    for k,limit in [(1000.,.0012345),(1024.,128.),(0.,0.)]:
        cap=limit/k if k else .1
        def energy(v):
            if k==0:return Decimal(0)
            K,L=D(k),D(limit)
            return K*v*v/2 if abs(K*v)<=L else L*abs(v)-L*L/(2*K)
        def gradient(v):return max(-D(limit),min(D(limit),D(k)*v))
        for v in [-2*cap,-.9*cap,0.,.9*cap,2*cap,cap+1e-16]:
            for delta in [-3*cap,-.1*cap,-2e-16,1e-20,.1*cap,3*cap]:
                exact=energy(D(v)+D(delta))-energy(D(v))-gradient(D(v))*D(delta)
                got=float(ground_remainder(tensor(v),tensor(delta),tensor(k),tensor(limit)))
                error=abs(got-float(exact));scale=max(abs(float(exact)),1e-24)
                assert error<=1e-10*scale
                rows.append(dict(kind='ground_huber',v=v,delta=delta,k=k,limit=limit,error=error,normalized_error=error/scale))
    # A near-stationary scalar normal-contact objective. Direct double
    # subtraction loses the increment; the remainder form matches Decimal.
    h=6.25e-6;ke=2e6;phi=-1e-5;v=.001;a=1.
    gap=phi+h*v;rhs=a*v+h*ke*gap-2e-12
    grad=a*v-rhs+h*ke*gap;H=a+ke*h*h;delta=-grad/H
    def objective(t):return .5*a*t*t-rhs*t+.5*ke*min(phi+h*t,0)**2
    direct=objective(v+delta)-objective(v)
    stable=grad*delta+.5*a*delta*delta+h*(ke/h)*float(unilateral_remainder(tensor(gap),tensor(h*delta)))
    def objective_decimal(t):return D(a)*t*t/2-D(rhs)*t+D(ke)*min(D(phi)+D(h)*t,Decimal(0))**2/2
    exact=objective_decimal(D(v)+D(delta))-objective_decimal(D(v))
    err=abs(stable-float(exact));assert err<1e-29
    example=dict(direct_subtraction_J=direct,stable_increment_J=stable,decimal_increment_J=float(exact),stable_absolute_error_J=err)
out=dict(scope='90-digit independent scalar convex-potential remainder controls; no force law or convergence threshold changes',cases=len(rows),maximum_normalized_error=max(r['normalized_error'] for r in rows),normalization_floor=1e-24,near_stationary_example=example,passed=True,rows=rows)
(W/'precision_controls_result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
