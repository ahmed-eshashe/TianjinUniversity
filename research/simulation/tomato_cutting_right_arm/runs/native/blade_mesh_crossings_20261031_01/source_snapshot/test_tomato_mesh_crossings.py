"""Reference fixture controls; no native imports or physics execution."""
import json
import unittest
from tomato_mesh_crossing_worker import PREP, fixtures


class CrossingFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = fixtures(json.loads((PREP/'blade_export.json').read_text()))

    def test_expected_crossings_and_clearances_match_reference_geometry(self):
        self.assertEqual(len(self.cases), 11)
        for case in self.cases:
            if case['expected_crossing']:
                self.assertLess(case['reference']['distance_m'], 1e-12, case['id'])
            else:
                self.assertGreater(case['reference']['distance_m'], 1e-9, case['id'])
        parallel = next(c for c in self.cases if c['id'] == 'parallel_1um_clear')
        self.assertAlmostEqual(parallel['reference']['distance_m'], 1e-6)

    def test_new_crossings_have_no_inside_soft_vertices(self):
        for identity in ('wide:edge_through_authored_blade_face', 'authored_blade_edge_through_soft_interior'):
            case = next(c for c in self.cases if c['id'] == identity)
            self.assertTrue(case['expected_crossing'])
            self.assertTrue(all(v['reference_signed_distance_m'] > 0 for v in case['vertex_references']))
        old = next(c for c in self.cases if c['id'] == 'historical:edge_through_authored_blade_face')
        self.assertTrue(any(v['reference_signed_distance_m'] < 0 for v in old['vertex_references']))


if __name__ == '__main__':
    unittest.main()
