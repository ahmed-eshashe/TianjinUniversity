"""Independent stationary contact-law controls, without native imports."""
import unittest
from tomato_analytic_force_worker import stationary_reference


class StationaryForceTests(unittest.TestCase):
    def test_force_reaction_and_off_axis_moment(self):
        f, r, m, h = stationary_reference(.001, [0., 0., 1.], 100., [.02, -.03, 0.], [0., 0., 0.])
        self.assertEqual(f, [0., 0., .1])
        self.assertEqual(r, [0., 0., -.1])
        self.assertAlmostEqual(m[0], .003)
        self.assertAlmostEqual(m[1], .002)
        self.assertEqual(h, [[0., 0., 0.], [0., 0., 0.], [0., 0., 100.]])

    def test_clear_contact_contributes_nothing(self):
        for penetration in (0., -.001):
            f, r, m, h = stationary_reference(penetration, [1., 0., 0.], 100., [1., 2., 3.], [0., 0., 0.])
            self.assertEqual(f, [0., 0., 0.])
            self.assertEqual(m, [0., 0., 0.])
            self.assertTrue(all(v == 0 for row in h for v in row))

    def test_translated_com_preserves_lever_arm(self):
        args = (.001, [1., 0., 0.], 100.)
        self.assertEqual(stationary_reference(*args, [1., 3., 4.], [1., 1., 1.]),
                         stationary_reference(*args, [0., 2., 3.], [0., 0., 0.]))

    def test_invalid_stiffness_rejected(self):
        for k in (-1., float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                stationary_reference(.001, [1., 0., 0.], k, [0., 0., 0.], [0., 0., 0.])


if __name__ == '__main__': unittest.main()
