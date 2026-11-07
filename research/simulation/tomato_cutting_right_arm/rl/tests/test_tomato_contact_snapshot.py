"""Disabled format preview and full-stream reader controls; no native imports."""
import copy
import hashlib
import unittest
from test_tomato_mesh_contact_contract import fixture
from tomato_contact_snapshot import preview_buffers, collect_snapshot_contacts, _digest


class ContactSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.record, self.context = fixture()
        self.identity = {'run_id': 'reference_run', 'episode_id': 'episode0', 'step': 0,
                         'start_s': 0., 'dt_s': 1/1200,
                         'source_sha256': {'reference': hashlib.sha256(b'reference').hexdigest()}}

    def preview(self, records=None):
        return preview_buffers(records if records is not None else [self.record], self.context, self.identity,
                               global_capacity=8, body_capacity=8, observed_dynamic_adjacency=[])

    def collect(self, envelope, identity=None, capacity=8):
        return collect_snapshot_contacts(envelope, identity or self.identity, self.context,
                                         target_body=0, collector_capacity=capacity)

    def resign(self, envelope):
        envelope['sha256'] = _digest(envelope['payload'])
        return envelope

    def test_prescribed_blade_is_read_even_when_solver_adjacency_empty(self):
        envelope = self.preview()
        result = self.collect(envelope)
        self.assertEqual(envelope['payload']['dynamic_adjacency_observed'], [])
        self.assertEqual(result['target_count'], 1)
        self.assertEqual(result['target_records'][0]['global_index'], 0)
        self.assertFalse(result['dynamic_adjacency_used'])
        self.assertFalse(result['reaction_force_evaluated'])
        self.assertFalse(result['solver_launch_enabled'])

    def test_preview_never_reduces_raw_duplicate_events(self):
        envelope = self.preview([self.record, dict(self.record, id='duplicate')])
        self.assertEqual(envelope['payload']['soft_contact_count'], [2])
        self.assertEqual(len(envelope['payload']['reference_duplicate_report']), 1)
        self.assertEqual(self.collect(envelope)['target_count'], 2)

    def test_float32_conversion_reports_error_without_normalization(self):
        self.record.update(barycentric=[1/3, 1/3, 1/3], rigid_barycentric=[1/3, 1/3, 1/3],
                           rigid_surface_body_m=[1/3, 1/3, 0.])
        envelope = self.preview(); result = self.collect(envelope)
        self.assertNotEqual(result['target_records'][0]['barycentric_sum_error'], 0.)
        self.assertGreater(envelope['payload']['conversion_max_absolute_error_by_field']['soft_contact_barycentric'], 0.)
        self.assertFalse(result['conversion_qualified'])

    def test_hash_and_run_episode_step_sources_intervals_reject_stale_data(self):
        envelope = self.preview(); changed = copy.deepcopy(envelope)
        changed['payload']['arrays']['soft_contact_body_pos'][0][2] = .1
        with self.assertRaises(ValueError): self.collect(changed)
        for patch in ({'run_id': 'other'}, {'episode_id': 'reset1'}, {'step': 1},
                      {'start_s': 1.}, {'dt_s': 1/240}, {'source_sha256': {'other': 'a'*64}}):
            identity = copy.deepcopy(self.identity); identity.update(patch)
            with self.assertRaises(ValueError): self.collect(envelope, identity)

    def test_global_and_collector_overflow_refused(self):
        envelope = self.preview()
        with self.assertRaises(ValueError): self.collect(envelope, capacity=1)
        envelope['payload']['soft_contact_count'] = [8]
        with self.assertRaises(ValueError): self.collect(self.resign(envelope))

    def test_truncated_and_nonfinite_vectors_and_wrong_indices_refused(self):
        for mutation in ('truncated', 'nan', 'corner', 'shape', 'particle_view', 'int32_overflow'):
            envelope = self.preview(); arrays = envelope['payload']['arrays']
            if mutation == 'truncated': arrays['soft_contact_normal'] = []
            elif mutation == 'nan': arrays['soft_contact_normal'][0][0] = float('nan')
            elif mutation == 'corner': arrays['soft_contact_indices'][0][1] = -1
            elif mutation == 'shape': arrays['soft_contact_shape'][0] = 99
            elif mutation == 'particle_view': arrays['soft_contact_particle'][0] = 0
            else: envelope['payload']['soft_contact_count'] = [2**31]
            with self.assertRaises(ValueError): self.collect(self.resign(envelope))

    def test_foreign_contacts_are_checked_before_target_filter(self):
        envelope = self.preview([self.record, dict(self.record, id='foreign')]); p = envelope['payload']
        p['shape_body'].append(1); p['arrays']['soft_contact_shape'][1] = 1
        result = self.collect(self.resign(envelope))
        self.assertEqual(result['global_prefix_records_checked'], 2)
        self.assertEqual(result['target_count'], 1)
        p['arrays']['soft_contact_indices'][1][0] = 99
        with self.assertRaises(ValueError): self.collect(self.resign(envelope))

    def test_inactive_tail_not_counted_and_zero_active_count_stays_empty(self):
        envelope = self.preview(); envelope['payload']['soft_contact_count'] = [0]
        result = self.collect(self.resign(envelope))
        self.assertEqual(result['target_count'], 0)
        self.assertEqual(result['global_prefix_records_checked'], 0)

    def test_float32_overflow_cannot_be_serialized(self):
        self.record['rigid_surface_velocity_body_m_s'] = [1e100, 0., 0.]
        with self.assertRaises(ValueError): self.preview()

    def test_invalid_reference_contact_cannot_be_previewed(self):
        self.record['source_kind'] = 'intersection_witness'
        with self.assertRaises(ValueError): self.preview()


if __name__ == '__main__': unittest.main()
