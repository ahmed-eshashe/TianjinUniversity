"""Bounded USD/numerical grasp audit. Never imports or launches Isaac Sim."""
import hashlib
import itertools
import json
import resource
from pathlib import Path
import sys
import time

import numpy as np
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade
from scipy.optimize import linprog, minimize
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from plan_contact_seating import HandGeometry
from reach_kinematics import PALM_OFFSET

FINGERS = ['index', 'middle', 'ring', 'pinky']
PRESERVE = ['rl/guard_benchmark.py', 'rl/grasp_metrics.py',
            'docs/rl/phase3_grasp_criteria.json', 'docs/rl/contact_seating_plan.json',
            'rl/central_grasp.py', 'rl/contact_evaluator.py', 'rl/contact_path_control.py',
            'rl/rolling_contact_control.py', 'rl/scene/minimal_benchmark.usda',
            'rl/scene/phase3.usda', 'rl/scene/phase3_grasp.usda',
            'assets/robots/Collected_whole_robot_updated/Collected_whole_robot/whole_robot_2.usd']


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PRESERVE}


def hull_data(vertices):
    hull = ConvexHull(vertices)
    return np.asarray(vertices)[hull.vertices], np.unique(np.round(hull.equations, 12), axis=0)


def minkowski_witness(a, b):
    """Closest separated-hull witnesses using triangle geometry, without a QP.

    Used only as a certificate-preserving fallback near grazing configurations.
    Barycentric weights on a Minkowski boundary triangle recover feasible
    witnesses in both input hulls.
    """
    differences=(a[:,None,:]-b[None,:,:]).reshape(-1,3)
    hull=ConvexHull(differences)
    if np.max(hull.equations[:,3])<=0:raise ValueError('Minkowski hull contains the origin')
    ids=hull.simplices;tri=differences[ids];x,y,z=tri[:,0],tri[:,1],tri[:,2]
    u=y-x;v=z-x;n=np.cross(u,v);nn=np.einsum('ij,ij->i',n,n)
    p=n*(np.einsum('ij,ij->i',n,x)/nn)[:,None]
    d00=np.einsum('ij,ij->i',u,u);d01=np.einsum('ij,ij->i',u,v);d11=np.einsum('ij,ij->i',v,v)
    w=p-x;d20=np.einsum('ij,ij->i',w,u);d21=np.einsum('ij,ij->i',w,v);den=d00*d11-d01*d01
    by=(d11*d20-d01*d21)/den;bz=(d00*d21-d01*d20)/den
    weights=np.c_[1-by-bz,by,bz];valid=np.all(weights>=-1e-10,axis=1)
    distance=np.where(valid,np.einsum('ij,ij->i',p,p),np.inf)
    best=int(np.argmin(distance));best_distance=distance[best];best_weights=weights[best]
    for i,j in [(0,1),(1,2),(2,0)]:
        edge=tri[:,j]-tri[:,i]
        alpha=np.clip(-np.einsum('ij,ij->i',tri[:,i],edge)/np.einsum('ij,ij->i',edge,edge),0,1)
        cp=tri[:,i]+alpha[:,None]*edge;dist=np.einsum('ij,ij->i',cp,cp);which=int(np.argmin(dist))
        if dist[which]<best_distance:
            best=which;best_distance=dist[which];best_weights=np.zeros(3);best_weights[i]=1-alpha[which];best_weights[j]=alpha[which]
    best_weights=np.maximum(best_weights,0);best_weights/=best_weights.sum()
    indices=ids[best]
    return best_weights @ a[indices//len(b)],best_weights @ b[indices%len(b)]


def convex_distance(a, b):
    """Closest points between convex envelopes in metres, with feasibility checks.

    Solve a six-variable convex quadratic in mm for numerical conditioning.
    This is a geometric distance, never a contact-force estimate.
    """
    centre = (a.mean(0) + b.mean(0)) / 2
    av, ae = hull_data((a - centre) * 1000)
    bv, be = hull_data((b - centre) * 1000)
    mat = np.zeros((len(ae) + len(be), 6))
    mat[:len(ae), :3] = ae[:, :3]
    mat[len(ae):, 3:] = be[:, :3]
    rhs = -np.r_[ae[:, 3], be[:, 3]]
    def objective(x):
        d = x[:3] - x[3:]
        return .5 * d @ d
    def jac(x):
        d = x[:3] - x[3:]
        return np.r_[d, -d]
    fit = minimize(objective, np.r_[av.mean(0), bv.mean(0)], jac=jac,
                   constraints={'type': 'ineq', 'fun': lambda x: rhs - mat @ x,
                                'jac': lambda x: -mat},
                   method='SLSQP', options={'maxiter': 120, 'ftol': 1e-10})
    violation = float(max(0, np.max(mat @ fit.x - rhs))) / 1000
    separation = fit.x[3:] - fit.x[:3]
    distance = float(np.linalg.norm(separation))
    # A supporting-plane gap is an independent lower bound. Feasible witness
    # distance is an upper bound, so their agreement certifies the result even
    # when SLSQP returns a line-search warning near a constrained optimum.
    lower = 0.
    if distance > 1e-9:
        normal = separation / distance
        lower = max(0., float((bv @ normal).min() - (av @ normal).max()))
    certificate_gap = max(0., distance - lower) / 1000
    if certificate_gap > 1e-6:
        # Near a grazing/overlap configuration, the QP's relative-point normal
        # can be numerically unstable. A feasible common point independently
        # certifies zero distance; never relax the distance certificate itself.
        eq = np.r_[ae, be]
        intersection = linprog([0.,0.,0.], A_ub=eq[:,:3], b_ub=-eq[:,3],
                               bounds=[(None,None)]*3, method='highs')
        if intersection.success and np.max(eq[:,:3]@intersection.x+eq[:,3]) <= 1e-7:
            common=intersection.x/1000+centre
            return {'distance_m':0.,'a_m':common.tolist(),'b_m':common.tolist(),
                    'constraint_violation_m':float(max(0.,np.max(eq[:,:3]@intersection.x+eq[:,3]))/1000),
                    'distance_certificate_gap_m':0.,'certificate_method':'independent feasible intersection'}
        if not intersection.success:
            wa,wb=minkowski_witness(av,bv)
            fit.x=np.r_[wa,wb];separation=wb-wa;distance=float(np.linalg.norm(separation))
            normal=separation/distance
            lower=max(0.,float((bv@normal).min()-(av@normal).max()))
            certificate_gap=max(0.,distance-lower)/1000
            violation=float(max(0,np.max(mat@fit.x-rhs)))/1000
    if violation > 1e-7 or certificate_gap > 1e-6:
        raise RuntimeError(f'Uncertified convex distance: {fit.message}; {violation=}; {certificate_gap=}')
    return {'distance_m': distance / 1000,
            'a_m': (fit.x[:3] / 1000 + centre).tolist(),
            'b_m': (fit.x[3:] / 1000 + centre).tolist(),
            'constraint_violation_m': violation, 'distance_certificate_gap_m': certificate_gap}


def clip_inner(vertices, axis, end, depth):
    """Convex envelope intersected with the frozen PCA inner-contact halfspace."""
    v, _ = hull_data(vertices)
    distances = v @ axis - (end - depth)
    inside = v[distances <= 1e-12].tolist()
    # Every vertex-pair crossing includes every true edge crossing. Extra points
    # remain inside the hull, so they do not enlarge the clipped convex set.
    for i in np.flatnonzero(distances <= 0):
        for j in np.flatnonzero(distances > 0):
            alpha = -distances[i] / (distances[j] - distances[i])
            inside.append((v[i] + alpha * (v[j] - v[i])).tolist())
    if len(inside) < 4:
        return None
    return hull_data(np.array(inside))[0]


def overlap_radius(a, b):
    if np.any(a.max(0) < b.min(0)) or np.any(b.max(0) < a.min(0)):
        return 0.
    _, ea = hull_data(a); _, eb = hull_data(b)
    eq = np.r_[ea, eb]
    fit = linprog([0, 0, 0, -1], A_ub=np.c_[eq[:, :3], np.ones(len(eq))],
                  b_ub=-eq[:, 3], bounds=[(None, None)] * 3 + [(0, None)], method='highs')
    return float(fit.x[3]) if fit.success else 0.


def collider_inventory(stage, model):
    xc = UsdGeom.XformCache(); records = []; geometry = {}
    root = stage.GetPrimAtPath(model.root)
    for p in Usd.PrimRange(root):
        if not p.IsA(UsdGeom.Mesh) or not p.HasAPI(UsdPhysics.CollisionAPI):
            continue
        if not UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get():
            continue
        body = p
        while body and not body.HasAPI(UsdPhysics.RigidBodyAPI):
            body = body.GetParent()
        if not body:
            raise RuntimeError('Collider without rigid body')
        rel = np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T) @ np.array(xc.GetLocalToWorldTransform(p)).T
        mesh = UsdGeom.Mesh(p); v = np.array(mesh.GetPointsAttr().Get())
        v = v @ rel[:3, :3].T + rel[:3, 3]
        approximation = UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get()
        material, _ = UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial('physics')
        rec = {'path': str(p.GetPath()), 'body': body.GetName(),
               'approximation': approximation, 'vertices': len(v),
               'body_bounds_m': [v.min(0).tolist(), v.max(0).tolist()],
               'mesh_to_body': rel.tolist(), 'material': str(material.GetPath()) if material else None,
               'contact_offset_m': p.GetAttribute('physxCollision:contactOffset').Get(),
               'rest_offset_m': p.GetAttribute('physxCollision:restOffset').Get(),
               'torsional_radius_m': p.GetAttribute('physxCollision:torsionalPatchRadius').Get(),
               'minimum_torsional_radius_m': p.GetAttribute('physxCollision:minTorsionalPatchRadius').Get()}
        records.append(rec)
        geometry.setdefault(body.GetName(), []).append((v, approximation))
    return records, geometry


def conditional_load_check(model, links, q, r, t, kr, pose, contacts, handle, arm):
    """Static friction-cone LP under explicitly optimistic contact assumptions.

    Hypothetical contact at up to 4 mm separation is NOT a physical state. Its
    feasibility tests only whether a generous wrench model already rules it out.
    """
    physics = json.loads((ROOT / 'docs/rl/phase3_physics.json').read_text())
    com = np.array(physics['knife_com_local_m'])
    selected = []
    for part in ['palm', 'thumb', *FINGERS]:
        candidates = [c for c in contacts if (c['body'] == 'right_rh_hand_base_link' if part == 'palm'
                     else c['body'].startswith('right_rh_' + part + '_')) and c['distance_m'] <= .004]
        if part in FINGERS and 1.89 * q[2 + FINGERS.index(part)] < np.deg2rad(115):
            continue
        if not candidates: continue
        # Prefer the frozen inner region, with both witnesses retained, when
        # available within the optimistic contact shell.
        inner = [c for c in candidates if c.get('inner_witness') and c['inner_region_distance_m'] <= .004]
        c = min(inner or candidates, key=lambda c: c['inner_region_distance_m'] if inner else c['distance_m'])
        witness = c['inner_witness'] if inner else c
        a = np.array(witness['a_m']); b = np.array(witness['b_m']); normal = a - b
        if np.linalg.norm(normal) < 1e-7:
            # At overlap the closest-point normal is undefined. Do not choose a
            # convenient face normal just to manufacture wrench feasibility.
            return {'status': 'inconclusive: overlapping selected witness has no unique surface normal', 'body': c['body']}
        normal /= np.linalg.norm(normal)
        link = links[c['body']]; br = r @ link[:3, :3]; bp = t + r @ link[:3, 3]
        local = br.T @ (a - bp)
        jhand = []
        for j in range(6):
            changed = q.copy(); changed[j] += 1e-5
            tr = model.transforms(changed)[c['body']]
            ap = t + r @ (tr[:3, 3] + tr[:3, :3] @ local)
            jhand.append((ap - a) / 1e-5)
        # Arm Jacobian at the actual candidate IK solution, hand posture fixed.
        root = model.kin.transforms(arm)[model.root]
        apworld = root[:3, 3] + root[:3, :3] @ (link[:3, 3] + link[:3, :3] @ local)
        jarm = []
        for j in range(7):
            changed = np.array(arm); changed[j] += 1e-5
            tr = model.kin.transforms(changed)[model.root]
            p = tr[:3, 3] + tr[:3, :3] @ (link[:3, 3] + link[:3, :3] @ local)
            jarm.append(kr.T @ ((p - apworld) / 1e-5))
        selected.append({'body': c['body'], 'part': part, 'a': a, 'b': b, 'normal': normal,
                         'gap_m': float(np.linalg.norm(a - b)), 'inner': bool(inner),
                         'jhand': np.array(jhand).T, 'jarm': np.array(jarm).T})
    vectors = []; wrenches = []; torques = []
    for c in selected:
        n = c['normal']; seed = np.eye(3)[np.argmin(abs(n))]
        u = np.cross(n, seed); u /= np.linalg.norm(u); v = np.cross(n, u)
        for theta in np.arange(8) * (2 * np.pi / 8):
            f = -n + .6 * (np.cos(theta) * u + np.sin(theta) * v)
            vectors.append(f); wrenches.append(np.r_[f, np.cross(c['b'] - com, f)])
            torques.append(np.r_[c['jarm'].T @ -f, c['jhand'].T @ -f])
    matrix = np.array(wrenches).T; torque = np.array(torques).T
    force_groups = np.zeros((len(selected), len(vectors)))
    for i in range(len(selected)): force_groups[i, 8*i:8*(i+1)] = 1
    caps = np.r_[[80.] * 7, [1., 1.], [.3] * 4]
    gravity = kr.T @ np.array([0, 0, -float(physics['knife_mass_kg']) * 9.81])
    # Static 25% load margin, zero gravity moment about the provisional COM.
    rhs = np.r_[-1.25 * gravity, [0., 0., 0.]]
    fit = linprog(np.ones(len(vectors)), A_eq=matrix, b_eq=rhs,
                  A_ub=np.r_[torque, -torque, force_groups, -force_groups],
                  b_ub=np.r_[caps, caps, [10.] * len(selected), [-.05] * len(selected)],
                  bounds=(0, None), method='highs')
    result = {'status': 'conditionally feasible' if fit.success else 'infeasible under stated assumptions',
              'assumptions': 'Hypothetical closure of gaps up to 4 mm; rigid point contacts; mu=0.6 inscribed 8-ray friction cone; 0.05..10 N per contact; 1.25x gravity; no board support; hand/arm torque budget entirely allocated to knife load, excluding robot self-weight and drive equilibrium.',
              'physical_feasibility_certified': False,
              'selected': [{'body': c['body'], 'part': c['part'], 'inner': c['inner'], 'gap_m': c['gap_m'],
                            'point_knife_m': c['b'].tolist(), 'outward_normal': c['normal'].tolist()} for c in selected]}
    centre = (handle.min(0) + handle.max(0)) / 2
    axes = np.linalg.svd(handle - centre, full_matrices=False)[2][1:]
    radial = [(c['part'], axes @ (c['b'] - centre)) for c in selected]
    radial = [(part, v / np.linalg.norm(v)) for part, v in radial if np.linalg.norm(v) > 1e-8]
    angles = sorted(float(np.arctan2(v[1], v[0]) % (2 * np.pi)) for _, v in radial)
    maxgap = max(np.diff(angles + [angles[0] + 2 * np.pi])) if angles else 2 * np.pi
    result['selected_point_oracle_geometry'] = {
        'max_cross_section_gap_rad': float(maxgap), 'enclosed': bool(maxgap <= np.pi + .05),
        'opposed': any(float(a @ b) < -.5 for pa, a in radial for pb, b in radial if pa == 'thumb' and pb in FINGERS),
        'scope': 'Selected hypothetical contact witnesses only, not all possible surface contacts'}
    if fit.success:
        result.update(normal_force_n=(force_groups @ fit.x).tolist(), generalized_load_torque_nm=(torque @ fit.x).tolist(),
                      balance_residual=float(np.linalg.norm(matrix @ fit.x - rhs)))
    probes = {}
    for label, scale, with_torque in [('nominal_gravity_with_torque_limits', 1., True),
                                      ('margin_gravity_without_actuator_limits', 1.25, False)]:
        ub = np.r_[torque, -torque, force_groups, -force_groups] if with_torque else np.r_[force_groups, -force_groups]
        bound = np.r_[caps, caps, [10.] * len(selected), [-.05] * len(selected)] if with_torque else np.r_[[10.] * len(selected), [-.05] * len(selected)]
        probe = linprog(np.ones(len(vectors)), A_eq=matrix, b_eq=np.r_[-scale * gravity, [0., 0., 0.]],
                        A_ub=ub, b_ub=bound, bounds=(0, None), method='highs')
        probes[label] = {'feasible': bool(probe.success)}
        if probe.success:
            probes[label]['normal_force_n'] = (force_groups @ probe.x).tolist()
            probes[label]['maximum_actuator_load_fraction'] = float(np.max(abs(torque @ probe.x) / caps))
    result['conditional_probes'] = probes
    return result


def full_robot_self_check(stage, model, arm, hand):
    """Terminal-pose envelope intersections across both arms, torso and hands."""
    physics = json.loads((ROOT / 'docs/rl/phase3_physics.json').read_text())
    values = dict(physics['home_rad']); values.update(zip(model.kin.names, arm))
    values.update({'right_rh_thumb_cmc_yaw': hand[0], 'right_rh_thumb_cmc_pitch': hand[1],
                   'right_rh_thumb_ip': 1.86 * hand[1]})
    for i, f in enumerate(FINGERS):
        values['right_rh_' + f + '_mcp_pitch'] = hand[i+2]
        values['right_rh_' + f + '_dip'] = .89 * hand[i+2]
    xc = UsdGeom.XformCache(); cache = {'/dual_ar5_o6': model.kin.root}
    def transform(path):
        if path in cache: return cache[path]
        if path in model.kin.by_child:
            parent, _, a, b, axis, name = model.kin.by_child[path]
            rot = np.eye(4)
            if axis is not None: rot[:3, :3] = Rotation.from_rotvec(axis * values.get(name, 0.)).as_matrix()
            cache[path] = transform(parent) @ a @ rot @ b
        else:
            p = stage.GetPrimAtPath(path); parent = str(p.GetParent().GetPath())
            local = np.linalg.inv(np.array(xc.GetLocalToWorldTransform(p.GetParent())).T) @ np.array(xc.GetLocalToWorldTransform(p)).T
            cache[path] = transform(parent) @ local
        return cache[path]
    filtered = set(); geometry = []
    for p in Usd.PrimRange(stage.GetPrimAtPath('/dual_ar5_o6')):
        if p.HasAPI(UsdPhysics.FilteredPairsAPI):
            for other in UsdPhysics.FilteredPairsAPI(p).GetFilteredPairsRel().GetTargets():
                filtered.add(frozenset((str(p.GetPath()), str(other))))
        if not p.IsA(UsdGeom.Mesh) or not p.HasAPI(UsdPhysics.CollisionAPI): continue
        if not UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get(): continue
        body = p
        while body and not body.HasAPI(UsdPhysics.RigidBodyAPI): body = body.GetParent()
        if not body: raise RuntimeError('Full-robot collider without body')
        path = str(body.GetPath())
        rel = np.linalg.inv(np.array(xc.GetLocalToWorldTransform(body)).T) @ np.array(xc.GetLocalToWorldTransform(p)).T
        matrix = transform(path) @ rel
        v = np.array(UsdGeom.Mesh(p).GetPointsAttr().Get()); v = v @ matrix[:3, :3].T + matrix[:3, 3]
        geometry.append((path, v, UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get()))
    overlaps = []; tested = 0
    for (pa, a, aa), (pb, b, ab) in itertools.combinations(geometry, 2):
        if pa == pb or frozenset((pa, pb)) in filtered: continue
        tested += 1; radius = overlap_radius(a, b)
        if radius > 1e-6:
            overlaps.append({'a': pa, 'b': pb, 'envelope_intersection_radius_m': radius,
                             'exact_for_authored_convex_hulls': aa == ab == 'convexHull'})
    return {'collision_meshes': len(geometry), 'unfiltered_mesh_pairs_checked': tested,
            'authored_filtered_body_pairs': len(filtered), 'overlaps': overlaps,
            'scope': 'Terminal discrete pose only, left side at Phase 3 home; decomposition enclosed by convex hull; physical contact margins and approach route unverified'}


def geometry_audit(stage, model, inventory, geometry):
    proposal = json.loads((ROOT / 'docs/rl/refined_supported_wrap.json').read_text())
    meta = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    pose = np.array(proposal['supported_sample']['knife_pose_xyzw'])
    kr = Rotation.from_quat(pose[3:]).as_matrix()
    xc = UsdGeom.XformCache(); kp = stage.GetPrimAtPath(meta['knife_path'])
    inv = np.linalg.inv(np.array(xc.GetLocalToWorldTransform(kp)).T)
    def knife_vertices(suffix):
        p = stage.GetPrimAtPath(meta['knife_path'] + suffix)
        rel = inv @ np.array(xc.GetLocalToWorldTransform(p)).T
        v = np.array(UsdGeom.Mesh(p).GetPointsAttr().Get())
        return v @ rel[:3, :3].T + rel[:3, 3]
    handle = knife_vertices('/CollisionHandle'); blade = knife_vertices('/CollisionBlade')
    centre = (handle.min(0) + handle.max(0)) / 2
    neighbours = {frozenset((j[0].rsplit('/', 1)[-1], j[1].rsplit('/', 1)[-1]))
                  for j in model.kin.joints.values() if j[0]}
    criteria = json.loads((ROOT / 'docs/rl/phase3_grasp_criteria.json').read_text())['criteria']
    cases = []
    for ci, c in enumerate(proposal['candidates'][:3]):
        q = np.deg2rad([c['thumb_yaw_deg'], c['thumb_pitch_deg'], *[c['finger_degrees'][f] for f in FINGERS]])
        rw = np.array(c['hand_rotation_world']); r = kr.T @ rw
        t = centre - r @ np.array(c['handle_in_hand_m']); links = model.transforms(q)
        bodies = {}; contacts = []; clearance = []
        for name, meshes in geometry.items():
            link = links[name]; br = r @ link[:3, :3]; bp = t + r @ link[:3, 3]
            bodies[name] = []
            # PCA uses ALL mesh points, matching the present evaluator, before
            # hull reduction. Multiple enabled colliders are preserved as a union.
            all_v = np.concatenate([v for v, _ in meshes]); mean = all_v.mean(0)
            axis = np.linalg.svd(all_v - mean, full_matrices=False)[2][0]
            proj = all_v @ axis
            if abs(proj.min()) > abs(proj.max()): axis = -axis
            end = float((all_v @ axis).max())
            for v, approximation in meshes:
                vv = v @ br.T + bp; bodies[name].append((vv, approximation))
                world = vv @ kr.T + pose[:3]
                clearance.append(float(world[:, 2].min() - meta['board_world_bounds'][1][2]))
                dist = convex_distance(vv, handle); blade_dist = convex_distance(vv, blade)
                inner_dist = None
                inner_witness = None
                if name.endswith('_proximal'):
                    inner_dist = dist['distance_m']
                    inner_witness = dist
                elif name.endswith('_distal'):
                    inner = clip_inner(v, axis, end, criteria['inner_distance_m'])
                    if inner is not None:
                        inner_witness = convex_distance(inner @ br.T + bp, handle)
                        inner_dist = inner_witness['distance_m']
                contacts.append({'body': name, 'approximation': approximation, **dist,
                                 'inner_region_distance_m': inner_dist,
                                 'inner_witness': inner_witness,
                                 'blade_distance_m': blade_dist['distance_m']})
        overlaps = []
        for na, nb in itertools.combinations(bodies, 2):
            if frozenset((na, nb)) in neighbours:
                continue
            for va, aa in bodies[na]:
                for vb, ab in bodies[nb]:
                    radius = overlap_radius(va, vb)
                    if radius > 1e-6:
                        overlaps.append({'a': na, 'b': nb, 'envelope_intersection_radius_m': radius,
                                         'exact_for_authored_convex_hulls': aa == ab == 'convexHull'})
        # Generous 4 mm envelope from the two authored contact offsets. This is
        # only an optimistic proximity screen, not a new success threshold.
        threshold = .004
        inner = []; near = []
        for f in FINGERS:
            if 1.89 * q[2 + FINGERS.index(f)] < criteria['minimum_curl_rad']:
                continue
            fc = [x for x in contacts if x['body'].startswith('right_rh_' + f + '_')]
            if any(x['distance_m'] <= threshold for x in fc): near.append(f)
            if any(x['inner_region_distance_m'] is not None and x['inner_region_distance_m'] <= threshold for x in fc): inner.append(f)
        failures = []
        joint_values = {'right_rh_thumb_cmc_yaw': q[0], 'right_rh_thumb_cmc_pitch': q[1],
                        'right_rh_thumb_ip': 1.86 * q[1]}
        for fi, f in enumerate(FINGERS):
            joint_values['right_rh_' + f + '_mcp_pitch'] = q[fi + 2]
            joint_values['right_rh_' + f + '_dip'] = .89 * q[fi + 2]
        limit_failures = [name for name, value in joint_values.items()
                          if name not in model.kin.limits or not model.kin.limits[name][0] <= value <= model.kin.limits[name][1]]
        if limit_failures: failures.append('joint or follower limit violation')
        if len(near) < criteria['minimum_fingers']: failures.append('fewer than three curled fingers within optimistic contact shell')
        if len(inner) < criteria['minimum_inner_fingers']: failures.append('fewer than two eligible inner finger regions within optimistic contact shell')
        if overlaps: failures.append('nonadjacent convex-envelope self intersections require resolution')
        if min(clearance) < 0: failures.append('support-plane intersection')
        arm, pe, re = model.kin.solve(pose[:3] + kr @ (t + r @ PALM_OFFSET), rw,
                                    proposal['supported_sample']['q_rad'][:7])
        full_self = full_robot_self_check(stage, model, arm, q)
        inconclusive = []
        if any(o['exact_for_authored_convex_hulls'] for o in full_self['overlaps']):
            failures.append('full-robot authored convex-hull self intersection')
        if any(not o['exact_for_authored_convex_hulls'] for o in full_self['overlaps']):
            inconclusive.append('convex envelopes of decomposed arm shapes intersect; cooked parts needed to resolve actual collision')
        load = conditional_load_check(model, links, q, r, t, kr, pose, contacts, handle, arm) if not failures else {'status': 'not attempted: geometric screen failed'}
        cases.append({'candidate_index': ci, 'joint_rad': q.tolist(), 'contact_geometry': contacts,
                      'joint_and_follower_limit_failures': limit_failures,
                      'curled_near_fingers_optimistic': near, 'inner_fingers_optimistic': inner,
                      'minimum_board_plane_clearance_m': min(clearance), 'self_envelope_intersections': overlaps,
                      'full_robot_self_collision': full_self,
                      'arm_ik': {'q_rad': arm.tolist(), 'position_error_m': pe, 'angle_error_rad': re,
                                 'terminal_full_robot_self_envelopes_checked': True,
                                 'arm_environment_and_route_checked': False},
                      'screen_failures': failures, 'screen_inconclusive': inconclusive, 'terminal_feasibility_passed': False,
                      'load_solution': load})
    # Explicit negative is measured evidence, not an invented positive contact.
    from grasp_metrics import GraspEvaluator
    negative = proposal['supported_sample']
    negative_metric = GraspEvaluator(negative['handle_height_m']).update(negative, .05)
    return {'scope': 'Three existing candidates only; convex hull distance is optimistic for decomposition; no global impossibility conclusion',
            'cooked_colliders_available': False, 'optimistic_contact_shell_m': .004,
            'distance_certificate_tolerance_m': 1e-6,
            'measured_fingertip_negative': {'source_run': proposal['source_run'], 'metric': negative_metric,
                                           'contacts': negative['contacts']},
            'handle_dimensions_m': np.ptp(handle, axis=0).tolist(), 'cases': cases}


def trace_audit():
    out = []
    def force(s, part):
        return sum(c['force_n'] for c in s['contacts'] if c['part'] == part and c['on_handle'])
    for n in [1, 2, 3, 4, 5, 7]:
        folder = ROOT / f'runs/rl/phase3/contact_transfer_{n:02d}'
        trace = json.loads((folder / 'seating_substeps.json').read_text())
        events = []
        for before, after in zip(trace, trace[1:]):
            if force(before, 'index') > .3 and force(after, 'index') < .05:
                tips = [c['distance_from_tip_m'] for c in before['contacts'] if c['part'] == 'index' and c['on_handle']]
                events.append({'before_control': before['control_step'], 'before_substep': before['substep_in_control'],
                               'index_before_n': force(before, 'index'), 'index_after_n': force(after, 'index'),
                               'thumb_before_n': force(before, 'thumb'), 'thumb_after_n': force(after, 'thumb'),
                               'commands_identical': before['command_q_rad'] == after['command_q_rad'],
                               'index_tip_distances_m': tips,
                               'separation_recorded': all('separation_m' in c for c in before['contacts'])})
        out.append({'run': folder.name, 'events': events})
    identical = {}
    for name in ['trajectory.json', 'seating_substeps.json', 'rolling_progress.json']:
        paths = [ROOT / f'runs/rl/phase3/contact_transfer_{n:02d}' / name for n in [5, 7]]
        identical[name] = paths[0].read_bytes() == paths[1].read_bytes()
    return {'index_loss_events': out, 'runs_05_07_byte_identical': identical,
            'static_hold_comparison_available': False, 'root_cause_established': False}


def main():
    start = time.monotonic(); before = hashes()
    stage = Usd.Stage.Open(str(ROOT / 'rl/scene/phase3_grasp.usda'))
    model = HandGeometry(stage)
    inventory, geometry = collider_inventory(stage, model)
    meta = json.loads((ROOT / 'rl/scene/manifest.json').read_text())
    supporting_colliders = []
    for base in [meta['knife_path'], meta['board_path'], meta['counter_path']]:
        for p in Usd.PrimRange(stage.GetPrimAtPath(base)):
            if not p.HasAPI(UsdPhysics.CollisionAPI): continue
            supporting_colliders.append({'path': str(p.GetPath()),
                'enabled': UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get(),
                'approximation': UsdPhysics.MeshCollisionAPI(p).GetApproximationAttr().Get() if p.IsA(UsdGeom.Mesh) else None,
                'contact_offset_m': p.GetAttribute('physxCollision:contactOffset').Get(),
                'rest_offset_m': p.GetAttribute('physxCollision:restOffset').Get()})
    # Geometry/collider checks precede the recorded controller investigation.
    geo = geometry_audit(stage, model, inventory, geometry)
    result = {'simulator_launched': False, 'training': False, 'colliders': inventory,
              'knife_and_support_colliders': supporting_colliders,
              'geometry': geo, 'recorded_controller': trace_audit(),
              'preservation_before': before, 'preservation_after': hashes(),
              'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'wall_s': time.monotonic() - start,
              'peak_process_rss_bytes_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}
    if result['preservation_before'] != result['preservation_after']:
        raise RuntimeError('Protected files changed during offline audit')
    path = ROOT / 'docs/rl/offline_grasp_audit.json'
    path.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps({'output': str(path), 'wall_s': result['wall_s'],
                      'cases': [{'candidate': c['candidate_index'], 'inner': c['inner_fingers_optimistic'],
                                 'near': c['curled_near_fingers_optimistic'], 'failures': c['screen_failures']}
                                for c in geo['cases']]}, indent=2))


if __name__ == '__main__':
    main()
