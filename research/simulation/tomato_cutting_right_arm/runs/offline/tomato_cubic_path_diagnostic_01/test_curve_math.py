import unittest
import numpy as np
from curve_math import hermite,evaluate,restrict,gap_coefficients,scalar_minimum

class CurveTests(unittest.TestCase):
    def test_endpoints_and_derivatives(self):
        a=np.array([1.,2.]);b=np.array([3.,-2.]);v=np.array([.2,.3]);w=np.array([-.3,1.])
        p=hermite(a,b,v,w)
        np.testing.assert_allclose(evaluate(p,0),a,atol=1e-14)
        np.testing.assert_allclose(evaluate(p,1),b,atol=1e-14)
        np.testing.assert_allclose(p[1],v,atol=1e-14)
        np.testing.assert_allclose(p[1]+2*p[2]+3*p[3],w,atol=1e-14)
    def test_fixed_coordinates(self):
        p=hermite(np.array([2.,1.]),np.array([2.,3.]),np.array([0.,.1]),np.array([0.,.2]))
        for t in np.linspace(0,1,11):self.assertEqual(evaluate(p,t)[0],2.)
    def test_affine_recovery(self):
        p=hermite(np.array([0.]),np.array([2.]),np.array([2.]),np.array([2.]))
        np.testing.assert_allclose(p[:,0],[0,2,0,0])
    def test_restriction(self):
        p=np.arange(12,dtype=float).reshape(4,3);q=restrict(p,.2,.7)
        for u in [0,.13,.5,.9,1]:np.testing.assert_allclose(evaluate(q,u),evaluate(p,.2+.5*u),atol=1e-14)
    def test_gap_coefficients(self):
        p=np.arange(12,dtype=float).reshape(4,3)/10;C=np.array([[1.,2.,0.],[0.,-1.,3.]])
        E=C+.4;b=np.array([.1,.2]);e=b+.2;c=gap_coefficients(C,E,b,e,p)
        for u in [0,.13,.5,.8,1]:
            np.testing.assert_allclose(np.polynomial.polynomial.polyval(u,c),((1-u)*C+u*E)@evaluate(p,u)-((1-u)*b+u*e),atol=1e-14)
    def test_quartic_interior_minimum(self):
        c=np.polynomial.polynomial.polypow([-.37,1.],4);c[0]-=.002
        v,u=scalar_minimum(c);self.assertAlmostEqual(v,-.002,places=12);self.assertAlmostEqual(u,.37,places=4)
    def test_penetration_not_hidden_by_endpoints(self):
        v,u=scalar_minimum([.2,-1.,1.,0,0]);self.assertAlmostEqual(v,-.05);self.assertAlmostEqual(u,.5)
    def test_linear_and_constant_degeneracy(self):
        self.assertEqual(scalar_minimum([2.,0,0,0,0])[0],2.)
        self.assertEqual(scalar_minimum([2.,-1,0,0,0]),(1.,1.))
    def test_activation_split(self):
        # Piecewise gap |t-.3|-.1 reaches a minimum at an activation knot.
        a=scalar_minimum([.2,-.3,0,0,0])[0]
        b=scalar_minimum([-.1,.7,0,0,0])[0]
        self.assertAlmostEqual(min(a,b),-.1)
    def test_nonfinite_fail_closed(self):
        with self.assertRaises(ValueError):scalar_minimum([np.nan,1.])

if __name__=='__main__':unittest.main()
