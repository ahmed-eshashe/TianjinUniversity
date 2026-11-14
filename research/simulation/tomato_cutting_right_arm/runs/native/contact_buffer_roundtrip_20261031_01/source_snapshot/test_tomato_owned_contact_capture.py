"""Read consistency/refusal tests with fake arrays, no native packages."""
import copy
import unittest
from types import SimpleNamespace
from test_tomato_mesh_contact_contract import fixture
from tomato_contact_snapshot import preview_buffers, ARRAY_FIELDS
from tomato_owned_contact_capture import capture_owned_prefix


class FakeArray:
    def __init__(self, values, hook=None):
        self.values = values; self.hook = hook; self.shape = (len(values),)
    def numpy(self):
        if self.hook: self.hook()
        return self
    def tolist(self): return copy.deepcopy(self.values)
    def __getitem__(self, index): return FakeArray(self.values[index])


class OwnedCaptureTests(unittest.TestCase):
    def setUp(self):
        record, self.context = fixture()
        self.identity = dict(run_id='r', episode_id='e', step=0, start_s=0., dt_s=1/1200,
                             source_sha256={'source': 'a'*64})
        p = preview_buffers([record], self.context, self.identity, global_capacity=8, body_capacity=8,
                            observed_dynamic_adjacency=[])['payload']
        self.contacts = SimpleNamespace(contact_generation=FakeArray([0]), soft_contact_count=FakeArray([1]), soft_contact_max=8)
        for field in ARRAY_FIELDS: setattr(self.contacts, field, FakeArray(p['arrays'][field]))
        self.particles = FakeArray(p['particle_q_world_m']); self.mapping = FakeArray([0])
        self.poses = FakeArray([[0., 0., 0., 0., 0., 0., 1.]])

    def capture(self, generation=0, authorized=True):
        return capture_owned_prefix(self.contacts, self.particles, self.mapping, self.poses,
                    self.identity, self.context, expected_generation=generation, native_capture_authorized=authorized)

    def test_explicit_authorization_required(self):
        with self.assertRaises(PermissionError): self.capture(authorized=False)

    def test_snapshot_has_owned_pose_generation_and_disabled_launch(self):
        envelope, context = self.capture()
        self.assertEqual(envelope['payload']['contact_generation'], 0)
        self.assertEqual(context['body_to_world']['translation_m'], (0., 0., 0.))
        self.assertFalse(envelope['payload']['solver_launch_enabled'])

    def test_stale_generation_refused(self):
        with self.assertRaises(ValueError): self.capture(generation=1)

    def test_mid_capture_generation_or_count_change_refused(self):
        for changed in ('contact_generation', 'soft_contact_count'):
            def mutation(): getattr(self.contacts, changed).values[0] += 1
            self.contacts.soft_contact_normal.hook = mutation
            with self.assertRaises(ValueError): self.capture()
            self.setUp()

    def test_saturation_and_truncated_native_field_refused(self):
        self.contacts.soft_contact_count.values = [8]
        with self.assertRaises(ValueError): self.capture()
        self.setUp(); self.contacts.soft_contact_normal = FakeArray([])
        with self.assertRaises(ValueError): self.capture()


if __name__ == '__main__': unittest.main()
