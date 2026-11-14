"""Analytic geometry controls; no native imports."""
import math
import unittest
from tomato_analytic_contact_worker import box_reference, fixture_cases


class AnalyticBoxReferenceTests(unittest.TestCase):
    def test_inside_and_clear_top_face(self):
        d, n = box_reference([0., 0., .001])
        self.assertAlmostEqual(d, -.001); self.assertEqual(n, [[0., 0., 1.]])
        d, n = box_reference([0., 0., .003])
        self.assertAlmostEqual(d, .001); self.assertEqual(n, [[0., 0., 1.]])

    def test_outside_corner_distance(self):
        d, n = box_reference([.02, .02, .002])
        self.assertAlmostEqual(d, math.sqrt(2)*.01)
        self.assertAlmostEqual(n[0][0], 1/math.sqrt(2))

    def test_equal_nearest_faces_keep_both_normal_options(self):
        d, n = box_reference([.009, 0., .001])
        self.assertAlmostEqual(d, -.001)
        self.assertEqual(len(n), 2)

    def test_edge_and_face_fixtures_have_all_vertices_outside(self):
        cases = fixture_cases(); self.assertEqual(len(cases), 6)
        for case in cases:
            if 'vertices_outside' in case['id']:
                self.assertTrue(all(box_reference(p)[0] > 0 for p in case['points']))


if __name__ == '__main__': unittest.main()
