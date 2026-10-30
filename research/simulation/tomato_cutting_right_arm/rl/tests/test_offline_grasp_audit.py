"""Analytic geometry cases guard the audit against false feasibility claims."""
import itertools
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from offline_grasp_audit import clip_inner, convex_distance, overlap_radius, minkowski_witness
from refine_inner_wrap import inner_surface_points


def box(lo, hi):
    return np.array(list(itertools.product(*zip(lo, hi))), dtype=float)


class OfflineGeometryTests(unittest.TestCase):
    def test_inner_search_samples_remain_on_original_exterior(self):
        vertices=box([-.005,-.005,0],[.005,.005,.04])
        samples,axis,end=inner_surface_points(vertices,.015)
        self.assertTrue(np.all(samples@axis<=end-.015+1e-10))
        from scipy.spatial import ConvexHull
        eq=ConvexHull(vertices).equations
        # Every sample lies on an original hull face, including intersections
        # with the inner boundary; no centroid on an artificial cut face.
        np.testing.assert_allclose((samples@eq[:,:3].T+eq[:,3]).max(1),0,atol=1e-10)

    def test_independent_minkowski_witness_at_micrometre_gap(self):
        a=box([0,0,0],[.01,.02,.03]);b=a+[.010003,0,0]
        r=Rotation.from_euler('xyz',[13,28,49],degrees=True).as_matrix()
        wa,wb=minkowski_witness(a@r.T,b@r.T)
        self.assertAlmostEqual(np.linalg.norm(wb-wa),.000003,places=10)
        # Both reconstructed witnesses remain inside their original polytopes.
        from scipy.spatial import ConvexHull
        for w,vertices in [(wa,a@r.T),(wb,b@r.T)]:
            eq=ConvexHull(vertices).equations
            self.assertLessEqual(np.max(eq[:,:3]@w+eq[:,3]),1e-10)

    def test_known_face_and_diagonal_distances(self):
        a = box([0, 0, 0], [.01, .01, .01])
        for shift, expected in [([.03, 0, 0], .02), ([.03, .04, 0], np.hypot(.02, .03))]:
            d = convex_distance(a, a + shift)
            self.assertAlmostEqual(d['distance_m'], expected, places=7)
            self.assertLessEqual(d['distance_certificate_gap_m'], 1e-6)

    def test_distance_is_invariant_under_rigid_frame_change(self):
        a = box([0, 0, 0], [.01, .02, .03]); b = a + [.04, .03, 0]
        r = Rotation.from_euler('xyz', [31, 47, -20], degrees=True).as_matrix()
        offset = np.array([-2.2, -1.5, .9])
        self.assertAlmostEqual(convex_distance(a, b)['distance_m'],
                               convex_distance(a @ r.T + offset, b @ r.T + offset)['distance_m'], places=7)

    def test_overlap_is_not_misreported_as_positive_clearance(self):
        a = box([0, 0, 0], [.02, .02, .02]); b = a + [.01, 0, 0]
        self.assertLess(convex_distance(a, b)['distance_m'], 1e-7)
        self.assertAlmostEqual(overlap_radius(a, b), .005, places=7)

    def test_tip_contact_can_coexist_with_large_inner_region_gap(self):
        finger = box([-.005, -.005, 0], [.005, .005, .04])
        handle = box([-.005, -.005, .041], [.005, .005, .05])
        inner = clip_inner(finger, np.array([0, 0, 1.]), .04, .015)
        self.assertAlmostEqual(convex_distance(finger, handle)['distance_m'], .001, places=7)
        self.assertAlmostEqual(convex_distance(inner, handle)['distance_m'], .016, places=7)
        self.assertLessEqual(inner[:, 2].max(), .025 + 1e-10)


if __name__ == '__main__':
    unittest.main()
