"""Independent derivative, invariance and feasibility tests of the volume term."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_volume_protection import ProtectedModel,InfeasibleVolume,feasible_solve
from tomato_nonlinear_checks import spring_state


class VolumeProtectionTests(unittest.TestCase):
    points=np.array([[0.,0,0],[1.,0,0],[0,1.,0],[0,0,1.]])
    pairs=np.array([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
    def model(self):
        rest=np.linalg.norm(self.points[self.pairs[:,1]]-self.points[self.pairs[:,0]],axis=1)
        return ProtectedModel(self.points,self.pairs,rest,np.full(6,2.),np.array([[0,1,2,3]]),np.array([1/6]))

    def test_rest_stiffness_and_energy_unchanged(self):
        m=self.model();a=m.evaluate(self.points,tangent=True);b=spring_state(self.points,m.pairs,m.rest,m.stiffness,tangent=True)
        self.assertEqual(a['barrier_energy_j'],0.)
        np.testing.assert_array_equal(a['gradient_n'],b['gradient_n'])
        np.testing.assert_array_equal(a['tangent_n_m'].toarray(),b['tangent_n_m'].toarray())

    def test_barrier_force_and_tangent_finite_difference(self):
        m=self.model();x=self.points.copy();x[1,0]=.3
        state=m.evaluate(x,tangent=True);eps=1e-6
        for j in range(x.size):
            delta=np.zeros_like(x);delta.reshape(-1)[j]=eps
            plus=m.evaluate(x+delta);minus=m.evaluate(x-delta)
            self.assertAlmostEqual((plus['energy_j']-minus['energy_j'])/(2*eps),state['gradient_n'].reshape(-1)[j],delta=1e-5)
            column=(plus['gradient_n']-minus['gradient_n']).reshape(-1)/(2*eps)
            np.testing.assert_allclose(column,state['tangent_n_m'].toarray()[:,j],rtol=1e-7,atol=2e-5)

    def test_floor_inversion_and_invalid_parameters_rejected(self):
        m=self.model()
        for j in [.1,0.,-.1]:
            x=self.points.copy();x[1,0]=j
            with self.assertRaises(InfeasibleVolume):m.evaluate(x)
        with self.assertRaises(ValueError):ProtectedModel(self.points,m.pairs,m.rest,m.stiffness,m.cells,m.volumes,floor=.6)

    def test_volume_energy_diverges_near_floor_and_is_zero_at_activation(self):
        m=self.model();energies=[]
        for j in [.5,.3,.15,.101]:
            x=self.points.copy();x[1,0]=j;energies.append(m.evaluate(x)['barrier_energy_j'])
        self.assertEqual(energies[0],0.)
        self.assertTrue(all(a<b for a,b in zip(energies,energies[1:])))

    def test_rotation_force_balance_and_torque_balance(self):
        m=self.model();x=self.points.copy();x[1,0]=.3
        rot=np.array([[0.,-1,0],[1,0,0],[0,0,1]])
        a=m.evaluate(x);b=m.evaluate(x@rot.T+[2,3,4])
        self.assertAlmostEqual(a['energy_j'],b['energy_j'])
        np.testing.assert_allclose(b['gradient_n'],a['gradient_n']@rot.T,atol=1e-9)
        np.testing.assert_allclose(a['gradient_n'].sum(axis=0),0.,atol=1e-10)
        np.testing.assert_allclose(np.cross(x,a['gradient_n']).sum(axis=0),0.,atol=1e-10)

    def test_shear_with_unit_j_adds_no_barrier(self):
        m=self.model();x=self.points.copy();x[:,0]+=.5*x[:,1]
        self.assertEqual(m.evaluate(x)['barrier_energy_j'],0.)

    def test_stationary_saddle_is_not_accepted_as_minimum(self):
        from scipy.sparse import diags
        class DoubleWell:
            def evaluate(self,x,*,tangent=False):
                a,b,c=x[0]
                g=np.zeros_like(x);g[0]=[4*a*(a*a-1),2*b,2*c];g[1,0]=1.
                state={'energy_j':(a*a-1)**2+b*b+c*c,'gradient_n':g,'min_cell_ratio':1.}
                if tangent:state['tangent_n_m']=diags([12*a*a-4,2,2,0,0,0]).tocsr()
                return state
        x,trace,converged=feasible_solve(DoubleWell(),np.zeros((2,3)),np.zeros(6),
                                        np.array([0,1,2]),np.array([3,4,5]),np.ones(3))
        self.assertTrue(converged)
        self.assertAlmostEqual(abs(x[0]),1.,places=6)
        self.assertTrue(any(r.get('negative_curvature_escape') for r in trace))
        self.assertTrue(all(b['energy_j']<=a['energy_j']+1e-14 for a,b in zip(trace,trace[1:])))
        np.testing.assert_array_equal(x[3:],0.)


if __name__=='__main__':unittest.main()
