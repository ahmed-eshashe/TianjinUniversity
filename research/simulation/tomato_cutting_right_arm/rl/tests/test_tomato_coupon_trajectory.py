import unittest
from tomato_coupon_trajectory import audit_closed_surface,trajectory_config,pose_at,R
from tomato_native_coupon import coupon_description
from tomato_wrench_contract import dot


class CouponTrajectoryTests(unittest.TestCase):
    def fixture(self):
        c=coupon_description();return c['positions_m'],c['triangles']

    def config(self):
        p,_=self.fixture();return trajectory_config(p,p)

    def test_known_tetrahedron_volume(self):
        p,t=self.fixture();r=audit_closed_surface(p,t)
        self.assertAlmostEqual(r['signed_volume_m3'],.01**3/6)
        self.assertFalse(r['self_intersection_tested'])

    def test_open_reversed_and_duplicate_surface_rejected(self):
        p,t=self.fixture()
        for faces in [t[:-1],[list(reversed(x)) for x in t],t+[t[0]]]:
            with self.assertRaises(ValueError):audit_closed_surface(p,faces)

    def test_initial_geometry_is_above_coupon(self):
        p,_=self.fixture();c=self.config();pose=pose_at(c,0)
        zmin=min(dot(R[2],x)+pose['translation_m'][2] for x in p)
        self.assertAlmostEqual(zmin-max(x[2] for x in p),.002)

    def test_withdrawal_returns_to_exact_start(self):
        c=self.config();a=pose_at(c,0);b=pose_at(c,1.2)
        self.assertEqual(a['translation_m'],b['translation_m'])
        self.assertEqual(b['linear_velocity_m_s'],(0.,0.,0.))

    def test_indent_and_withdraw_velocities_have_opposite_signs(self):
        c=self.config();self.assertLess(pose_at(c,.3)['linear_velocity_m_s'][2],0)
        self.assertGreater(pose_at(c,.9)['linear_velocity_m_s'][2],0)

    def test_smooth_boundary_velocities_and_bounded_depth(self):
        c=self.config()
        for t in [0,.05,.55,.65,1.15,1.2]:
            self.assertAlmostEqual(pose_at(c,t)['linear_velocity_m_s'][2],0,places=12)
        for t in [i*.01 for i in range(121)]:
            z=pose_at(c,t)['translation_m'][2]
            self.assertGreaterEqual(z,c['end_translation_m'][2]-1e-14)
            self.assertLessEqual(z,c['start_translation_m'][2]+1e-14)

    def test_invalid_time_refused(self):
        for t in [-1,float('nan'),2]:
            with self.assertRaises(ValueError):pose_at(self.config(),t)
