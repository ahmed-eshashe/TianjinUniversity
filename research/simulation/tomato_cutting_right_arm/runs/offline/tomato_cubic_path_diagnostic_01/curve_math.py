"""Geometry-only candidate curves; never accepts a mechanical trajectory."""
import numpy as np


def hermite(x0,x1,v0,v1):
    x0,x1,v0,v1=map(np.asarray,(x0,x1,v0,v1))
    return np.array([x0,v0,3*(x1-x0)-2*v0-v1,-2*(x1-x0)+v0+v1])


def evaluate(p,t):
    return ((p[3]*t+p[2])*t+p[1])*t+p[0]


def restrict(p,a,b):
    h=b-a
    return np.array([evaluate(p,a),h*(p[1]+2*a*p[2]+3*a*a*p[3]),h*h*(p[2]+3*a*p[3]),h**3*p[3]])


def gap_coefficients(C0,C1,b0,b1,q):
    dc=C1-C0;db=b1-b0
    return np.array([C0@q[0]-b0,C0@q[1]+dc@q[0]-db,C0@q[2]+dc@q[1],C0@q[3]+dc@q[2],dc@q[3]])


def scalar_minimum(c):
    """Endpoints and all resolved real stationary roots on the unit interval.

    Floating-point diagnostic, not a certified interval-arithmetic proof.
    Near-real ambiguous roots and large root residuals fail closed.
    """
    c=np.asarray(c,dtype=float)
    if not np.isfinite(c).all():raise ValueError('Nonfinite polynomial')
    d=np.arange(1,len(c))*c[1:]
    while len(d) and d[-1]==0:d=d[:-1]
    us=[0.,1.]
    if len(d)>1:
        roots=np.polynomial.polynomial.polyroots(d/np.max(np.abs(d)))
        for z in roots:
            if abs(z.imag)<=1e-10:
                u=float(z.real)
                if 0<u<1:
                    residual=abs(np.polynomial.polynomial.polyval(u,d))
                    if residual>1e-8*np.sum(np.abs(d))+1e-25:raise ValueError('Unresolved stationary root')
                    us.append(u)
            elif abs(z.imag)<1e-7 and 0<z.real<1:raise ValueError('Ambiguous nearly-real root')
    vals=[float(np.polynomial.polynomial.polyval(u,c)) for u in us]
    k=int(np.argmin(vals));return vals[k],us[k]
