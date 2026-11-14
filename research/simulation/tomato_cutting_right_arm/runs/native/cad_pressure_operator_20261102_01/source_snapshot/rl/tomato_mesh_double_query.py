"""Bounded all-facet float64 closest-point diagnostic; not a contact solver."""


def make_closest_function():
    import warp as wp

    @wp.func
    def closest(a: wp.vec3d, b: wp.vec3d, c: wp.vec3d, p: wp.vec3d):
        # Interior/edge/vertex region formulation differs from the Python
        # plane-and-segment reference. All arithmetic here stays float64.
        zero = wp.float64(0.0)
        one = wp.float64(1.0)
        ab = b-a
        ac = c-a
        ap = p-a
        d1 = wp.dot(ab, ap)
        d2 = wp.dot(ac, ap)
        if d1 <= zero and d2 <= zero:
            return a
        bp = p-b
        d3 = wp.dot(ab, bp)
        d4 = wp.dot(ac, bp)
        if d3 >= zero and d4 <= d3:
            return b
        vc = d1*d4-d3*d2
        if vc <= zero and d1 >= zero and d3 <= zero:
            return a+(d1/(d1-d3))*ab
        cp = p-c
        d5 = wp.dot(ab, cp)
        d6 = wp.dot(ac, cp)
        if d6 >= zero and d5 <= d6:
            return c
        vb = d5*d2-d1*d6
        if vb <= zero and d2 >= zero and d6 <= zero:
            return a+(d2/(d2-d6))*ac
        va = d3*d6-d5*d4
        if va <= zero and (d4-d3) >= zero and (d5-d6) >= zero:
            w = (d4-d3)/((d4-d3)+(d5-d6))
            return b+w*(c-b)
        denominator = one/(va+vb+vc)
        v = vb*denominator
        w = vc*denominator
        return (one-v-w)*a+v*b+w*c

    return closest


def query_all_facets(vertices, triangles, points, *, device='cuda:0'):
    if len(vertices) != 74 or len(triangles) != 144 or len(points) != 562:
        raise ValueError('Fixed authored blade/probe diagnostic sizes required')
    import warp as wp
    import numpy as np
    import time

    closest = make_closest_function()

    @wp.kernel(enable_backward=False)
    def all_facets(v: wp.array(dtype=wp.vec3d), ids: wp.array(dtype=int),
                   p: wp.array(dtype=wp.vec3d), distances: wp.array(dtype=wp.float64),
                   closest_points: wp.array(dtype=wp.vec3d), faces: wp.array(dtype=int)):
        i = wp.tid()
        best = wp.float64(1.0e30)
        best_point = wp.vec3d(wp.float64(0.0))
        best_face = int(-1)
        for face in range(144):
            q = closest(v[ids[3*face]], v[ids[3*face+1]], v[ids[3*face+2]], p[i])
            delta = p[i]-q
            distance2 = wp.dot(delta, delta)
            if distance2 < best:
                best = distance2
                best_point = q
                best_face = face
        distances[i] = wp.sqrt(best)
        closest_points[i] = best_point
        faces[i] = best_face

    v = wp.array(vertices, dtype=wp.vec3d, device=device)
    ids = wp.array([i for face in triangles for i in face], dtype=int, device=device)
    p = wp.array(points, dtype=wp.vec3d, device=device)
    d = wp.zeros(len(points), dtype=wp.float64, device=device)
    q = wp.zeros(len(points), dtype=wp.vec3d, device=device)
    f = wp.zeros(len(points), dtype=int, device=device)
    durations = []
    for _ in range(2):
        start = time.monotonic()
        wp.launch(all_facets, dim=len(points), inputs=[v, ids, p], outputs=[d, q, f], device=device)
        wp.synchronize()
        durations.append(time.monotonic()-start)
    distances, closest_points, faces = d.numpy(), q.numpy(), f.numpy()
    if not np.isfinite(distances).all() or not np.isfinite(closest_points).all() or np.any(faces < 0):
        raise ValueError('Nonfinite or missing all-facet double query')
    return distances, closest_points, faces, durations
