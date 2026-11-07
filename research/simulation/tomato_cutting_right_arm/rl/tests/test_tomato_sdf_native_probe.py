"""Analytic controls for independent sign and normal references; no native imports."""
import unittest
from tomato_sdf_native_probe import signed_reference


class SignedMeshReferenceTests(unittest.TestCase):
    vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    triangles = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]

    def test_inside_distance_and_outward_normal(self):
        r = signed_reference([.2, .2, .1], self.vertices, self.triangles)
        self.assertAlmostEqual(r['reference_signed_distance_m'], -.1)
        for actual, expected in zip(r['reference_normal'], [0, 0, -1]):
            self.assertAlmostEqual(actual, expected)

    def test_outside_distance_and_outward_normal(self):
        r = signed_reference([.2, .2, -.1], self.vertices, self.triangles)
        self.assertAlmostEqual(r['reference_signed_distance_m'], .1)
        self.assertAlmostEqual(r['reference_normal'][2], -1)

    def test_winding_sign_independent_of_face_order(self):
        r = signed_reference([.2, .2, .1], self.vertices, [face[::-1] for face in self.triangles])
        self.assertAlmostEqual(r['reference_signed_distance_m'], -.1)

    def test_surface_normal_ambiguity_refused(self):
        with self.assertRaises(ValueError):
            signed_reference([.2, .2, 0], self.vertices, self.triangles)


if __name__ == '__main__':
    unittest.main()
