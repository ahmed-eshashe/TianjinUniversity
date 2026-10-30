"""Finite-difference checks of exact energy derivatives and inversion diagnostics."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_nonlinear_checks import spring_state,cell_ratios,polish_equilibrium


class NonlinearChecks(unittest.TestCase):
    def test_single_spring_force_energy_and_compressed_negative_curvature(self):
        state=spring_state(np.array([[0.,0,0],[.5,0,0]]),np.array([[0,1]]),np.array([1.]),np.array([2.]),tangent=True)
        self.assertAlmostEqual(state['energy_j'],.25)
        np.testing.assert_allclose(state['gradient_n'],[[1,0,0],[-1,0,0]])
        self.assertLess(np.linalg.eigvalsh(state['tangent_n_m'].toarray()).min(),0.)

    def test_gradient_and_hessian_finite_differences(self):
        points=np.array([[0.,0,0],[1.1,.2,-.1],[.3,1.2,.2]])
        pairs=np.array([[0,1],[0,2],[1,2]]);rest=np.array([1.,1.,1.4]);k=np.array([2.,3.,4.])
        state=spring_state(points,pairs,rest,k,tangent=True);eps=1e-6
        for j in range(points.size):
            delta=np.zeros_like(points);delta.reshape(-1)[j]=eps
            plus=spring_state(points+delta,pairs,rest,k);minus=spring_state(points-delta,pairs,rest,k)
            derivative=(plus['energy_j']-minus['energy_j'])/(2*eps)
            self.assertAlmostEqual(derivative,state['gradient_n'].reshape(-1)[j],places=8)
            hcol=(plus['gradient_n']-minus['gradient_n']).reshape(-1)/(2*eps)
            np.testing.assert_allclose(hcol,state['tangent_n_m'].toarray()[:,j],atol=2e-8)

    def test_rigid_motion_preserves_energy_and_rotates_gradient(self):
        points=np.array([[0.,0,0],[1.2,.2,0]])
        rotation=np.array([[0.,-1,0],[1,0,0],[0,0,1]])
        args=(np.array([[0,1]]),np.array([1.]),np.array([2.]))
        a=spring_state(points,*args);b=spring_state(points@rotation.T+[3,4,5],*args)
        self.assertAlmostEqual(a['energy_j'],b['energy_j'])
        np.testing.assert_allclose(b['gradient_n'],a['gradient_n']@rotation.T,atol=1e-12)
        np.testing.assert_allclose(a['gradient_n'].sum(axis=0),0.,atol=1e-12)

    def test_volume_and_inversion_reference(self):
        points=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1.]])
        cells=np.array([[0,1,2,3]])
        self.assertAlmostEqual(cell_ratios(points,cells,[1/6])[0],1.)
        points[[1,2]]=points[[2,1]]
        self.assertAlmostEqual(cell_ratios(points,cells,[1/6])[0],-1.)

    def test_equilibrium_polish_keeps_prescribed_dofs(self):
        points=np.array([[0.,0,0],[1.,0,0]])
        displacement=np.array([[0.,0,0],[.05,0,0]])
        free=np.array([3]);fixed=np.array([0,1,2,4,5])
        result,steps=polish_equilibrium(points,displacement,np.array([[0,1]]),np.array([1.]),np.array([2.]),free,fixed)
        self.assertGreaterEqual(steps,1)
        self.assertLess(abs(result[3]),1e-12)
        np.testing.assert_array_equal(result[fixed],displacement.reshape(-1)[fixed])

    def test_zero_length_rejected(self):
        with self.assertRaises(ValueError):spring_state(np.zeros((2,3)),np.array([[0,1]]),np.array([1.]),np.array([2.]))


if __name__=='__main__':unittest.main()
