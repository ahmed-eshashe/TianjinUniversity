"""Analytic references and deliberate adapter errors; no simulated contact."""
import math
import unittest
from tomato_wrench_contract import to_world, pair_residual, power, cross

I = ((1,0,0),(0,1,0),(0,0,1))
Q = ((0,-1,0),(1,0,0),(0,0,1))


class WrenchContractTests(unittest.TestCase):
    def test_known_lever_arm(self):
        f, m = to_world((0,10,0),(0,0,0),I,(.1,0,0))
        self.assertEqual(f,(0,10,0))
        self.assertEqual(m,(0,0,1))

    def test_rotate_and_shift_sensor_reference(self):
        f, m = to_world((10,0,0),(0,0,2),Q,(.1,0,0))
        self.assertEqual(f,(0,10,0))
        self.assertEqual(m,(0,0,3))

    def test_shift_back_to_contact_removes_lever_moment(self):
        f, m = to_world((0,10,0),(0,0,1),I,(0,0,0),(.1,0,0))
        self.assertEqual(m,(0,0,0))

    def test_pair_from_different_frames_and_origins(self):
        blade = to_world((10,0,0),(0,0,0),Q,(.1,0,0))
        tomato = to_world((0,-10,0),(0,0,-1),I,(0,0,0))
        self.assertEqual(pair_residual(blade,tomato),
                         {'force_residual_n':0,'moment_residual_nm':0})

    def test_sign_error_is_detected(self):
        w = to_world((0,10,0),(0,0,0),I,(.1,0,0))
        self.assertEqual(pair_residual(w,w)['force_residual_n'],20)

    def test_omitted_moment_shift_is_detected(self):
        w = to_world((0,10,0),(0,0,0),I,(.1,0,0))
        bad = ((0,-10,0),(0,0,0))
        self.assertEqual(pair_residual(w,bad)['moment_residual_nm'],1)

    def test_mm_interpreted_as_metres_is_detected(self):
        w = to_world((0,10,0),(0,0,0),I,(100,0,0))
        other = ((0,-10,0),(0,0,-1))
        self.assertEqual(pair_residual(w,other)['moment_residual_nm'],999)

    def test_power_invariant_when_shifting_reference(self):
        f=(2,3,4);m=(.1,.2,.3);p=(.1,-.2,.3)
        w=(.3,-.2,.1);v0=(.02,.03,.04)
        vp=tuple(a+b for a,b in zip(v0,cross(w,p)))
        fw,mw=to_world(f,m,I,p)
        self.assertAlmostEqual(power(f,m,vp,w),power(fw,mw,v0,w),places=14)

    def test_rotated_power_invariant(self):
        fw,mw=to_world((2,3,4),(.1,.2,.3),Q,(0,0,0))
        self.assertAlmostEqual(power((2,3,4),(.1,.2,.3),(.2,.3,.4),(.1,.2,.3)),
                               power(fw,mw,(-.3,.2,.4),(-.2,.1,.3)))

    def test_reject_nonfinite_inputs(self):
        for x in [math.nan,math.inf,-math.inf]:
            with self.assertRaises(ValueError):to_world((x,0,0),(0,0,0),I,(0,0,0))

    def test_reject_scaled_and_left_handed_axes(self):
        for R in [((1000,0,0),(0,1,0),(0,0,1)),
                  ((-1,0,0),(0,1,0),(0,0,1))]:
            with self.assertRaises(ValueError):to_world((1,0,0),(0,0,0),R,(0,0,0))

    def test_reject_wrong_dimension(self):
        with self.assertRaises(ValueError):to_world((1,2),(0,0,0),I,(0,0,0))


if __name__ == '__main__':
    unittest.main()
