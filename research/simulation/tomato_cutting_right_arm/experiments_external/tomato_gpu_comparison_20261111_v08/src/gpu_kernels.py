"""Float64 kernels for the unchanged integrated Galerkin equations."""
import warp as wp


@wp.kernel
def stress(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),
           q: wp.array(dtype=wp.vec3d), vol: wp.array(dtype=wp.float64), mu: wp.float64,
           lam: wp.float64, Pvol: wp.array(dtype=wp.mat33d), energy: wp.array(dtype=wp.float64),
           bad: wp.array(dtype=int)):
    p = wp.tid()
    F = wp.mat33d(wp.float64(0.0))
    for e in range(ptr[p], ptr[p+1]):
        F += wp.outer(q[ids[e]], grad[e])
    J = wp.determinant(F)
    if J <= wp.float64(0.1) or J >= wp.float64(10.0) or not wp.isfinite(J):
        wp.atomic_max(bad, 0, 1)
        Pvol[p] = wp.mat33d(wp.float64(0.0))
        energy[p] = wp.float64(0.0)
    else:
        lnJ = wp.log(J)
        Pvol[p] = vol[p] * (mu*F + (lam*lnJ-mu)*wp.transpose(wp.inverse(F)))
        norm2 = wp.float64(0.0)
        for i in range(3):
            for j in range(3):
                norm2 += F[i,j]*F[i,j]
        energy[p] = vol[p]*(wp.float64(0.5)*mu*(norm2-wp.float64(3.0))-mu*lnJ+wp.float64(0.5)*lam*lnJ*lnJ)


@wp.kernel
def force(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),
          Pvol: wp.array(dtype=wp.mat33d), load: wp.array(dtype=wp.vec3d),
          clock: wp.array(dtype=int), dt: wp.float64, start_time: wp.float64, duration: wp.float64,
          mode: int, stage: int, out: wp.array(dtype=wp.vec3d)):
    i = wp.tid()
    f = wp.vec3d(wp.float64(0.0))
    for e in range(ptr[i], ptr[i+1]):
        f -= Pvol[ids[e]]*grad[e]
    amplitude = wp.float64(1.0)
    if mode == 1:
        t = start_time + wp.float64(clock[0]+stage)*dt
        value = wp.sin(wp.float64(3.141592653589793)*t/duration)
        amplitude = value*value
    out[i] = f + amplitude*load[i]


@wp.kernel
def solve(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), values: wp.array(dtype=wp.float64),
          rptr: wp.array(dtype=int), rids: wp.array(dtype=int), rvalues: wp.array(dtype=wp.float64),
          f: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d), r: wp.array(dtype=wp.vec3d)):
    i = wp.tid()
    aa = wp.vec3d(wp.float64(0.0))
    rr = wp.vec3d(wp.float64(0.0))
    for e in range(ptr[i], ptr[i+1]):
        aa += values[e]*f[ids[e]]
    for e in range(rptr[i], rptr[i+1]):
        rr += rvalues[e]*f[rids[e]]
    a[i] = aa
    r[i] = rr


@wp.kernel
def mass_residual(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), values: wp.array(dtype=wp.float64),
                  a: wp.array(dtype=wp.vec3d), f: wp.array(dtype=wp.vec3d), r: wp.array(dtype=wp.vec3d),
                  error2: wp.array(dtype=wp.float64), scale2: wp.array(dtype=wp.float64)):
    i = wp.tid()
    ma = wp.vec3d(wp.float64(0.0))
    for e in range(ptr[i],ptr[i+1]):
        ma += values[e]*a[ids[e]]
    residual = ma-f[i]-r[i]
    error2[i] = wp.dot(residual,residual)
    scale2[i] = wp.dot(f[i]+r[i],f[i]+r[i])


@wp.kernel
def mass_guard(ptr: wp.array(dtype=int), err: wp.array(dtype=wp.float64), scale: wp.array(dtype=wp.float64),
               bad: wp.array(dtype=int)):
    piece = wp.tid()
    e = wp.float64(0.0)
    s = wp.float64(0.0)
    for i in range(ptr[piece],ptr[piece+1]):
        e += err[i]
        s += scale[i]
    if not wp.isfinite(e) or not wp.isfinite(s) or e > wp.float64(1e-14)*wp.max(s,wp.float64(1e-24)):
        wp.atomic_max(bad,0,2)


@wp.kernel
def drift(q: wp.array(dtype=wp.vec3d), v: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d),
          r: wp.array(dtype=wp.vec3d), translation: wp.array(dtype=wp.float64), dt: wp.float64,
          impulse: wp.array(dtype=wp.vec3d), moment: wp.array(dtype=wp.vec3d), bad: wp.array(dtype=int)):
    i = wp.tid()
    if bad[0] == 0:
        impulse[i] += wp.float64(0.5)*dt*translation[i]*r[i]
        moment[i] += wp.float64(0.5)*dt*wp.cross(q[i],r[i])
        v[i] += wp.float64(0.5)*dt*a[i]
        q[i] += dt*v[i]


@wp.kernel
def kick(q: wp.array(dtype=wp.vec3d), v: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d),
         r: wp.array(dtype=wp.vec3d), translation: wp.array(dtype=wp.float64), dt: wp.float64,
         impulse: wp.array(dtype=wp.vec3d), moment: wp.array(dtype=wp.vec3d), bad: wp.array(dtype=int)):
    i = wp.tid()
    if bad[0] == 0:
        v[i] += wp.float64(0.5)*dt*a[i]
        impulse[i] += wp.float64(0.5)*dt*translation[i]*r[i]
        moment[i] += wp.float64(0.5)*dt*wp.cross(q[i],r[i])
        for j in range(3):
            if not wp.isfinite(q[i][j]) or not wp.isfinite(v[i][j]):
                wp.atomic_max(bad,0,3)


@wp.kernel
def observation_guard(ptr: wp.array(dtype=int), ids: wp.array(dtype=int), grad: wp.array(dtype=wp.vec3d),
                      weights: wp.array(dtype=wp.float64), fixed: wp.array(dtype=int),
                      q: wp.array(dtype=wp.vec3d), a: wp.array(dtype=wp.vec3d), bad: wp.array(dtype=int)):
    p = wp.tid()
    F = wp.mat33d(wp.float64(0.0))
    aa = wp.vec3d(wp.float64(0.0))
    for e in range(ptr[p],ptr[p+1]):
        F += wp.outer(q[ids[e]],grad[e])
        aa += weights[e]*a[ids[e]]
    J = wp.determinant(F)
    if J <= wp.float64(0.1) or J >= wp.float64(10.0) or not wp.isfinite(J):
        wp.atomic_max(bad,0,4)
    if fixed[p] != 0:
        for j in range(3):
            if wp.abs(aa[j]) > wp.float64(1e-6) or not wp.isfinite(aa[j]):
                wp.atomic_max(bad,0,5)


@wp.kernel
def advance(clock: wp.array(dtype=int),bad: wp.array(dtype=int)):
    if bad[0] == 0:
        clock[0] += 1
