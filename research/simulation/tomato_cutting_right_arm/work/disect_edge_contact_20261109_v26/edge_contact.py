"""Experimental oriented material-edge contact. Pure trials; not yet qualified.

One penalty per physical endpoint, never one per incident material edge. On a
fixed active CAD face, E=ke*min(n.(x-a),0)^2/2 and F=-grad(E). The anchor
selects the entry face; it is not an interpolated force application point.
Feature changes need separate continuity qualification before coupled use.
"""
import numpy as np
from numba import njit


@njit(cache=True)
def entries(q, edges, vertices, faces):
    result = np.full((len(edges), 6), np.nan)
    for k in range(len(edges)):
        origin = q[edges[k, 0]]
        endpoint = q[edges[k, 1]]
        direction = endpoint - origin
        best = 2.0
        for fi in range(len(faces)):
            face = faces[fi]
            a = vertices[face[0]]
            e1 = vertices[face[1]] - a
            e2 = vertices[face[2]] - a
            n = np.cross(e1, e2)
            length = np.sqrt(np.dot(n, n))
            if length < 1e-20:
                continue
            n /= length
            # Use the outward CAD normal, never flip a normal to fit a ray.
            if np.dot(n, direction) >= -1e-14:
                continue
            h = np.cross(direction, e2)
            det = np.dot(e1, h)
            if abs(det) < 1e-18:
                continue
            s = origin - a
            u = np.dot(s, h) / det
            cross = np.cross(s, e1)
            v = np.dot(direction, cross) / det
            t = np.dot(e2, cross) / det
            if u < -1e-12 or v < -1e-12 or u+v > 1+1e-12:
                continue
            if t < 0 or t > 1 or t >= best:
                continue
            best = t
            result[k, 0] = t
            result[k, 1] = np.dot(n, endpoint-a)
            result[k, 2:5] = n
            result[k, 5] = fi
    return result


def material_edges(mesh):
    cells = mesh['tets']
    raw = np.concatenate([cells[:, [i,j]] for i in range(4) for j in range(i)])
    raw = np.unique(np.sort(raw, axis=1), axis=0)
    cut = np.unique(mesh['ties'])
    mask = np.zeros(len(mesh['x']), bool)
    mask[cut] = True
    edges = raw[mask[raw[:,0]] != mask[raw[:,1]]].copy()
    swap = mask[edges[:,0]]
    edges[swap] = edges[swap, ::-1]
    return edges


def reference_entries(q, edges, vertices, faces):
    """Independent plane intersection + least-squares triangle coordinates."""
    result = np.full((len(edges),6), np.nan)
    for k,(i,j) in enumerate(edges):
        best = 2.
        for fi, face in enumerate(faces):
            a,b,c = vertices[face]
            normal = np.cross(b-a,c-a)
            norm = np.linalg.norm(normal)
            if norm < 1e-20:
                continue
            normal /= norm
            denominator = normal @ (q[j]-q[i])
            if denominator >= -1e-14:
                continue
            t = (normal @ (a-q[i])) / denominator
            if not 0 <= t <= 1 or t >= best:
                continue
            p = q[i] + t*(q[j]-q[i])
            uv = np.linalg.lstsq(np.column_stack((b-a,c-a)),p-a,rcond=None)[0]
            if min(uv) < -1e-12 or sum(uv) > 1+1e-12:
                continue
            best = t
            result[k] = [t,normal @ (q[j]-a),*normal,fi]
    return result


def endpoint_constraints(q, edges, vertices, faces, reference=False):
    edges = np.unique(np.asarray(edges,dtype=np.int64),axis=0)
    lo,hi = vertices.min(0),vertices.max(0)
    keep = np.all((np.maximum(q[edges[:,0]],q[edges[:,1]]) >= lo) &
                  (np.minimum(q[edges[:,0]],q[edges[:,1]]) <= hi),axis=1)
    edges = edges[keep]
    hits = (reference_entries if reference else entries)(q,edges,vertices,faces)
    gap = np.zeros(len(q))
    normal = np.zeros_like(q)
    face = np.full(len(q),-1,dtype=np.int64)
    anchor = np.full(len(q),-1,dtype=np.int64)
    for (i,j),hit in zip(edges,hits):
        if np.isfinite(hit[0]) and hit[1] < gap[j]:
            gap[j] = hit[1]
            normal[j] = hit[2:5]
            face[j] = int(hit[5])
            anchor[j] = i
    return dict(gap=gap,normal=normal,face=face,anchor=anchor,
                intersecting_edges=int(np.isfinite(hits[:,0]).sum()))


def evaluate(q, v, edges, vertices, faces, tool_velocity, com,
             ke=2000., kd=1., kf=2500., mu=.5, reference=False):
    c = endpoint_constraints(q,edges,vertices,faces,reference=reference)
    normal,gap = c['normal'],c['gap']
    active = gap < 0
    relative = v-tool_velocity
    vn = np.einsum('ij,ij->i',relative,normal)
    tangent = relative-vn[:,None]*normal
    speed = np.linalg.norm(tangent,axis=1)
    elastic = ke*np.maximum(-gap,0)
    ratio = speed/kf
    friction = elastic*(mu*np.tanh(4*ratio)+(.5-mu)*ratio/(.25*ratio**2+.75)**2)
    force = elastic[:,None]*normal - friction[:,None]*tangent/np.maximum(speed[:,None],1e-300)
    force += kd*np.maximum(-vn,0)[:,None]*normal*active[:,None]
    return dict(**c,force=force,energy_J=float(.5*ke*np.dot(gap,gap)),
                reaction=-force.sum(0),moment=-np.cross(q-com,force).sum(0),
                maximum_penetration_m=float(-gap.min()),active_nodes=int(active.sum()))
