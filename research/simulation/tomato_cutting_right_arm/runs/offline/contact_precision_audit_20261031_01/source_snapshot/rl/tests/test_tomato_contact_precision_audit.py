"""Rounding controls independent of any native simulator."""
import unittest
from fractions import Fraction
from tomato_contact_precision_audit import round32, fma32, interpolate32


class PrecisionAuditTests(unittest.TestCase):
    def test_halfway_rounds_to_even(self):
        self.assertEqual(round32(1+Fraction(1, 2**24)), 1.)
        self.assertEqual(round32(1+Fraction(3, 2**24)), 1+2**-22)

    def test_fused_cancellation_keeps_product_residual(self):
        a=1+2**-23; b=1-2**-23
        self.assertEqual(fma32(a,b,-1.), -2**-46)
        self.assertEqual(round32(round32(Fraction(a)*Fraction(b))-1), 0.)

    def test_translation_amplifies_nonunit_weight_sum(self):
        points=[[0.,0.,0.],[1.,0.,0.]]; weights=[.5, .5+2**-23, 0.]
        base=interpolate32(points,[0,1,-1],weights,fused=True)
        moved=interpolate32([[1.,0.,0.],[2.,0.,0.]],[0,1,-1],weights,fused=True)
        self.assertNotEqual(moved[0]-base[0], 1.)

    def test_padding_is_ignored(self):
        self.assertEqual(interpolate32([[1.,2.,3.]],[0,-1,-1],[1.,0.,0.],fused=True),[1.,2.,3.])


if __name__ == '__main__': unittest.main()
