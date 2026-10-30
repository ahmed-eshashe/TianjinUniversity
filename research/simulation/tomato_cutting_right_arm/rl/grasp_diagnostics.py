"""Bounded diagnostic data only; no control actions or success decisions."""
import numpy as np
from scipy.spatial.transform import Rotation


def raw_contact_snapshot(force, point, normal, separation, count, start,
                         bodies, filters, knife_path, support_paths, knife_com_world,
                         dt, max_points=96, max_pairs=64):
    """Retain subthreshold points without changing the oracle's contact filter.

    Shape/feature IDs are not returned by this API. Normal and friction points
    are separate manifolds and must not be paired by array index.
    """
    if not np.isfinite(dt) or dt <= 0 or not 1 <= max_points <= 128 or not 1 <= max_pairs <= 64:
        raise ValueError('Invalid diagnostic budget or physics interval')
    count=np.asarray(count);start=np.asarray(start)
    force=np.asarray(force);point=np.asarray(point);normal=np.asarray(normal);separation=np.asarray(separation)
    if count.shape != (len(bodies),len(filters)) or start.shape != count.shape:
        raise ValueError('Contact pair table dimensions do not match names')
    raw=[];pairs=[];total_points=0;total_pairs=0
    for bi,body in enumerate(bodies):
        for fi in np.flatnonzero(count[bi]>0):
            other=filters[int(fi)]
            hand='/right_rh_' in body
            relevant=(hand and (other==knife_path or '/dual_ar5_o6' in other or other in support_paths)) or (body==knife_path and other in support_paths)
            if not relevant:continue
            begin=int(start[bi,fi]);end=begin+int(count[bi,fi])
            if begin<0 or end>len(force) or end>len(point) or end>len(normal) or end>len(separation):
                raise ValueError('Contact count/start exceeds backend array capacity')
            total_pairs+=1;total_points+=end-begin
            scalars=np.asarray(force[begin:end]).reshape(-1)
            vectors=scalars[:,None]*normal[begin:end]
            moments=np.cross(point[begin:end]-np.asarray(knife_com_world),vectors)
            pair={'body_index':bi,'filter_index':int(fi),'raw_count':end-begin,
                  'below_oracle_threshold_count':int(np.count_nonzero(scalars<.05)),
                  'normal_scalar_sum_n':float(scalars.sum()),
                  'normal_vector_sum_backend_n':vectors.sum(0).tolist(),
                  'normal_moment_about_knife_com_backend_nm':moments.sum(0).tolist()}
            if len(pairs)<max_pairs:pairs.append(pair)
            for ci in range(begin,min(end,begin+max(0,max_points-len(raw)))):
                f=float(np.asarray(force[ci]).reshape(-1)[0])
                raw.append({'body_index':bi,'filter_index':int(fi),'force_n':f,'retained_by_oracle_force_filter':f>=.05,
                            'point_world_m':point[ci].tolist(),'normal_world_backend':normal[ci].tolist(),
                            'separation_m_backend':float(np.asarray(separation[ci]).reshape(-1)[0])})
    return {'physics_dt_s':float(dt),'body_names':list(bodies),'filter_names':list(filters),
            'raw_points':raw,'pairs':pairs,'total_relevant_points':total_points,
            'total_relevant_pairs':total_pairs,'points_truncated':total_points>len(raw),'pairs_truncated':total_pairs>len(pairs),
            'shape_feature_identity_available':False,'normal_direction_calibrated':False,
            'separation_sign_calibrated':False,
            'wrench_scope':'Backend normal-force vectors only, about provisional knife COM; no friction or inertial balance claim; reciprocal pairs may duplicate forces.'}


def material_points_world(kin, model, anchors, q):
    q=np.asarray(q);root=kin.transforms(q[:7])[model.root];links=model.transforms(q[7:])
    return np.array([root[:3,3]+root[:3,:3] @
                     (links[a['body']][:3,3]+links[a['body']][:3,:3] @ np.asarray(a['point_local'])) for a in anchors])


def command_motion_diagnostic(kin, model, anchors, previous, desired, applied, actual, knife_rotation):
    """Distinct FK displacements for final targets and current physical state.

    Targets are not physical poses and these norms are not contact-slip speeds.
    """
    def points(q):return material_points_world(kin,model,anchors,q)
    baseline=points(previous);target=points(applied);goal=points(desired);measured=points(actual)
    return {'anchor_bodies':[a['body'] for a in anchors],
            'saved_target_increment_points_knife_m':((target-baseline) @ knife_rotation).tolist(),
            'desired_increment_points_knife_m':((goal-baseline) @ knife_rotation).tolist(),
            'actual_to_target_points_knife_m':((target-measured) @ knife_rotation).tolist(),
            'scope':'FK with authored passive coupling: target increment, desired increment, and preload displacement; measured link poses are logged separately; not contact slip or velocity'}


def friction_snapshot(forces, points, counts, starts, bodies, filters, knife_path, max_points=96):
    if not 1<=max_points<=128:raise ValueError('Invalid friction log budget')
    ki=filters.index(knife_path);records=[];total=0
    for bi,body in enumerate(bodies):
        if '/right_rh_' not in body:continue
        begin=int(starts[bi,ki]);end=begin+int(counts[bi,ki]);total+=end-begin
        if begin<0 or end>len(forces) or end>len(points):raise ValueError('Invalid friction data bounds')
        for ci in range(begin,min(end,begin+max(0,max_points-len(records)))):
            records.append({'body_index':bi,'filter_index':ki,'force_world_backend_n':forces[ci].tolist(),
                            'point_world_m':points[ci].tolist()})
    return {'body_names':list(bodies),'filter_names':list(filters),'points':records,'total_points':total,'truncated':total>len(records),
            'normal_point_correspondence_available':False,'force_direction_calibrated':False}
