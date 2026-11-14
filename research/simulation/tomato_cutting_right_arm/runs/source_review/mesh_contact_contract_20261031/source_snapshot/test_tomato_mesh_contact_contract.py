"""Reference record failure modes and coordinate consistency; no native imports."""
import copy
import unittest
from tomato_mesh_contact_contract import review_record, review_batch


def fixture():
    identity = {'rotation': [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]], 'translation_m': [0., 0., 0.]}
    context = {'step': 0, 'dt_s': 1/1200, 'shape_id': 0, 'body_id': 0, 'body_motion_type': 'kinematic',
               'body_inv_mass_effective': 0.,
               'particles_world_m': [[0., 0., -.001], [1., 0., -.001], [0., 1., -.001]],
               'particle_radius_m': [0., 0., 0.], 'rigid_vertices_shape_m': [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
               'rigid_triangles': [[0, 1, 2]], 'shape_to_body': copy.deepcopy(identity),
               'body_to_world': copy.deepcopy(identity), 'shape_margin_m': 0.}
    record = {'id': 'face0', 'source_kind': 'signed_surface_reference', 'normal_source': 'outward_rigid_face_reference',
              'step': 0, 'shape_id': 0, 'body_id': 0, 'feature': 'face', 'corners': [0, 1, 2],
              'barycentric': [.25, .25, .5], 'rigid_triangle_id': 0, 'rigid_barycentric': [.25, .25, .5],
              'rigid_surface_body_m': [.25, .5, 0.], 'normal_world': [0., 0., 1.],
              'rigid_surface_velocity_body_m_s': [0., 0., 0.], 'projected_signed_gap_m': -.001}
    return record, context


class MeshContactRecordTests(unittest.TestCase):
    def test_face_penetration_and_force_launch_stays_disabled(self):
        record, context = fixture(); row = review_record(record, context)
        self.assertAlmostEqual(row['reference_penetration_m'], .001)
        self.assertFalse(row['solver_launch_enabled'])

    def test_particle_and_edge_padding_and_max_radius(self):
        record, context = fixture()
        record.update(feature='edge', corners=[0, 1, -1], barycentric=[.5, .5, 0.],
                      rigid_barycentric=[.5, .5, 0.], rigid_surface_body_m=[.5, 0., 0.])
        context['particle_radius_m'] = [.0002, .0004, .1]; context['shape_margin_m'] = .0001
        self.assertAlmostEqual(review_record(record, context)['reference_penetration_m'], .0015)
        record.update(feature='particle', corners=[0, -1, -1], barycentric=[1., 0., 0.],
                      rigid_barycentric=[1., 0., 0.], rigid_surface_body_m=[0., 0., 0.])
        self.assertAlmostEqual(review_record(record, context)['reference_penetration_m'], .0013)

    def test_distinct_shape_and_body_frames(self):
        record, context = fixture()
        context['shape_to_body']['translation_m'] = [2., 0., 0.]
        context['body_to_world'] = {'rotation': [[0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]], 'translation_m': [0., 3., 0.]}
        context['particles_world_m'] = [[-.001, 3., -2.], [-.001, 3., -3.], [-.001, 4., -2.]]
        record['rigid_surface_body_m'] = [2.25, .5, 0.]; record['normal_world'] = [1., 0., 0.]
        row = review_record(record, context)
        self.assertAlmostEqual(row['reference_penetration_m'], .001)

    def test_bad_weights_frames_normals_and_padding_refused(self):
        for update in ({'barycentric': [.2, .2, .2]}, {'barycentric': [-.1, .6, .5]},
                       {'normal_world': [0., 0., -1.]}, {'normal_world': [0., 0., 2.]},
                       {'corners': [0, 0, 2]}, {'rigid_surface_body_m': [.25, .5, .001]},
                       {'projected_signed_gap_m': .001}, {'shape_id': 1}, {'step': 1},
                       {'normal_world': [0., 0., float('nan')]}):
            record, context = fixture(); record.update(update)
            with self.assertRaises(ValueError): review_record(record, context)

    def test_intersection_cannot_be_promoted_to_force_contact(self):
        record, context = fixture(); record['source_kind'] = 'intersection_witness'
        with self.assertRaises(ValueError): review_record(record, context)
        record, context = fixture(); context['particles_world_m'] = context['rigid_vertices_shape_m']; record['projected_signed_gap_m'] = 0.
        self.assertFalse(review_record(record, context)['reference_force_law_active'])

    def test_exact_duplicate_permutations_only(self):
        record, context = fixture(); duplicate = copy.deepcopy(record)
        duplicate.update(id='permuted', corners=[2, 0, 1], barycentric=[.5, .25, .25])
        result = review_batch([record, duplicate], context, global_capacity=4, body_capacity=4, observed_dynamic_adjacency=[])
        self.assertEqual(result['unique_reference_count'], 1)
        self.assertEqual(result['full_stream_observer_indices'], [0, 1])
        self.assertFalse(result['nearby_contact_reduction_defined'])

    def test_same_world_point_different_soft_support_is_retained(self):
        record, context = fixture(); context['particles_world_m'].append([.25, .5, -.001]); context['particle_radius_m'].append(0.)
        particle = dict(record, id='particle', feature='particle', corners=[3, -1, -1], barycentric=[1., 0., 0.])
        result = review_batch([record, particle], context, global_capacity=4, body_capacity=4, observed_dynamic_adjacency=[])
        self.assertEqual(result['unique_reference_count'], 2)

    def test_overflow_is_checked_before_duplicate_reduction(self):
        record, context = fixture(); duplicate = dict(record, id='second')
        with self.assertRaises(ValueError):
            review_batch([record, duplicate], context, global_capacity=2, body_capacity=4, observed_dynamic_adjacency=[])
        context['body_motion_type'] = 'dynamic'
        context['body_inv_mass_effective'] = 1.
        with self.assertRaises(ValueError):
            review_batch([record], context, global_capacity=4, body_capacity=1, observed_dynamic_adjacency=[0])

    def test_kinematic_full_stream_and_dynamic_adjacency_are_distinct(self):
        record, context = fixture()
        result = review_batch([record], context, global_capacity=4, body_capacity=4, observed_dynamic_adjacency=[])
        self.assertTrue(result['kinematic_reactions_require_full_stream'])
        self.assertEqual(result['full_stream_observer_indices'], [0])
        with self.assertRaises(ValueError):
            review_batch([record], context, global_capacity=4, body_capacity=4, observed_dynamic_adjacency=[0])
        context['body_motion_type'] = 'dynamic'
        context['body_inv_mass_effective'] = 1.
        self.assertEqual(review_batch([record], context, global_capacity=4, body_capacity=4,
                                      observed_dynamic_adjacency=[0])['observed_dynamic_adjacency'], [0])

    def test_dynamic_adjacency_order_can_differ_without_losing_contacts(self):
        record, context = fixture(); context.update(body_motion_type='dynamic', body_inv_mass_effective=1.)
        result = review_batch([record, dict(record, id='second')], context, global_capacity=4,
                              body_capacity=4, observed_dynamic_adjacency=[1, 0])
        self.assertEqual(result['observed_dynamic_adjacency'], [1, 0])
        with self.assertRaises(ValueError):
            review_batch([record, dict(record, id='second')], context, global_capacity=4,
                         body_capacity=4, observed_dynamic_adjacency=[0, 0])

    def test_wrong_surface_projection_and_double_applied_margin_refused(self):
        record, context = fixture()
        record.update(rigid_barycentric=[.5, 0., .5], rigid_surface_body_m=[0., .5, 0.])
        with self.assertRaises(ValueError): review_record(record, context)
        record, context = fixture(); context['shape_margin_m'] = .0001
        record['rigid_surface_body_m'][2] = .0001
        with self.assertRaises(ValueError): review_record(record, context)


if __name__ == '__main__': unittest.main()
