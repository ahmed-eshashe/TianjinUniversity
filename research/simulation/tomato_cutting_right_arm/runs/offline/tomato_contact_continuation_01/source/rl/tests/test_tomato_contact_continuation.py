"""Optimizer regression checks; exact model/KKT gates are not relaxed."""
import unittest
import numpy as np
from scipy.sparse import csr_matrix,eye
from tomato_contact_continuation import solve_contact_continuation
from test_tomato_triangle_contact import Quadratic

class ContactContinuation(unittest.TestCase):
    def test_weighted_constraint_exact_solution(self):
        C=csr_matrix([[.25,0,0,.75,0,0]])
        x,lam,state,trace,ok,*_=solve_contact_continuation(Quadratic(np.zeros((2,3))),np.zeros((2,3)),{},C,np.array([1.]))
        self.assertTrue(ok);np.testing.assert_allclose(x[:,0],[.4,1.2],atol=1e-8);self.assertAlmostEqual(lam[0],1.6,places=8)
    def test_unilateral_contact_releases(self):
        C=csr_matrix([[.5,0,0,.5,0,0]])
        x,lam,_,_,ok,*_=solve_contact_continuation(Quadratic(np.ones((2,3))),np.zeros((2,3)),{},C,np.array([0.]))
        self.assertTrue(ok);np.testing.assert_allclose(x,1.,atol=1e-8);self.assertAlmostEqual(lam[0],0.)
    def test_dependent_rows_and_fixed_support(self):
        C=csr_matrix([[1.,0,0],[2.,0,0]])
        x,lam,_,_,ok,*_=solve_contact_continuation(Quadratic(np.zeros((1,3))),np.zeros((1,3)),{1:0.,2:0.},C,np.array([1.,2.]))
        self.assertTrue(ok);self.assertAlmostEqual(x[0,0],1.)
    def test_negative_free_curvature_is_removed_by_contact(self):
        class NonconvexNormal:
            def evaluate(self,x,*,tangent=False):
                v=x.ravel();r={'energy_j':float(-.5*v[0]**2+v[0]+.5*(v[1]**2+v[2]**2)),'gradient_n':np.array([[1-v[0],v[1],v[2]]])}
                if tangent:r['tangent_n_m']=csr_matrix(np.diag([-1.,1.,1.]))
                return r
        r=solve_contact_continuation(NonconvexNormal(),np.zeros((1,3)),{},csr_matrix([[1.,0,0]]),np.array([0.]))
        self.assertTrue(r[4]);self.assertAlmostEqual(r[1][0],1.);np.testing.assert_allclose(r[0],0.,atol=1e-12)
    def test_new_blocking_constraint_is_added(self):
        C=csr_matrix([[1.,0,0],[0.,1.,0]])
        x,lam,_,_,ok,*_=solve_contact_continuation(Quadratic(np.array([[-1.,-2.,0.]])),np.array([[1.,2.,0.]]),{},C,np.zeros(2))
        self.assertTrue(ok);np.testing.assert_allclose(x,0.,atol=1e-8);np.testing.assert_allclose(lam,[1.,2.],atol=1e-8)
    def test_resuming_preserves_released_contact_bookkeeping(self):
        C=csr_matrix([[1.,0,0]])
        model=Quadratic(np.array([[1.,0,0]]));initial=np.zeros((1,3));b=np.zeros(1)
        partial=solve_contact_continuation(model,initial,{},C,b,max_iterations=1)
        self.assertFalse(partial[4]);self.assertEqual(partial[3][-1]['optimizer_active_rows'],[])
        resumed=solve_contact_continuation(model,partial[0],{},C,b,max_iterations=4,initial_active=partial[3][-1]['optimizer_active_rows'])
        full=solve_contact_continuation(model,initial,{},C,b,max_iterations=6)
        self.assertTrue(resumed[4]);self.assertTrue(full[4]);np.testing.assert_allclose(resumed[0],full[0],atol=1e-12)
        np.testing.assert_allclose(resumed[1],full[1],atol=1e-12)
    def test_triangle_wrapper_catches_cap_crossing(self):
        from tomato_contact_continuation import solve_triangle_continuation
        from tomato_triangle_contact import triangle_geometry
        z=np.array([0.,.001,.001]);points=np.array([[0.,-.001,z[0]],[0.,.001,z[1]],[0.,0.,z[2]]]*2)
        design={'cut_x_m':0.,'pieces':[{'triangles':[[0,1,2]],'face_tags':['cut']}]};pairs=np.array([[0,3],[1,4],[2,5]])
        geom=triangle_geometry(design,points,pairs,.0005-.008)
        fixed={3*i+j:points[i,j] for i in range(6) for j in [1,2]}
        x,lam,_,_,ok,*_=solve_triangle_continuation(Quadratic(points),points,fixed,geom)
        self.assertTrue(ok);self.assertGreater(lam[geom['base_rows']:].sum(),0.)
        self.assertGreaterEqual((geom['matrix']@x.ravel()-geom['bounds']).min(),-1e-10)
        self.assertTrue(np.all(lam[~geom['active']]==0.))
    def test_future_dependent_inequalities_do_not_become_incompatible_ties(self):
        C=csr_matrix([[1.,0,0],[0,1.,0],[1.,1.,0]])
        x,lam,_,_,ok,*_=solve_contact_continuation(Quadratic(np.zeros((1,3))),np.array([[2.,2.,0.]]),{},C,np.array([1.,1.,3.]))
        self.assertTrue(ok);np.testing.assert_allclose(x,[[1.5,1.5,0.]],atol=1e-8)
        self.assertGreaterEqual(lam.min(),-1e-9);np.testing.assert_allclose(C@x.ravel(),[1.5,1.5,3.],atol=1e-8)
if __name__=='__main__':unittest.main()
