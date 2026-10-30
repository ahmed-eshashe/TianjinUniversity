"""Independent contact complementarity and constrained-solve references."""
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.sparse import eye,csr_matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tomato_coupled_contact import (constrained_step,solve_contact,swept_minimum_volume,
                                    proper_surface_intersections,assemble_model,cut_pairs)


class Quadratic:
    def __init__(self,force):self.force=force
    def evaluate(self,x,*,tangent=False):
        gradient=np.asarray(x).copy();gradient[0,0]-=self.force
        s={'energy_j':float(.5*np.sum(x*x)-self.force*x[0,0]),'gradient_n':gradient,
           'min_cell_ratio':1.,'min_length_ratio':1.}
        if tangent:s['tangent_n_m']=eye(x.size,format='csr')
        return s


class ConstrainedSolveTests(unittest.TestCase):
    def test_pair_elimination_matches_analytic_quadratic(self):
        x=np.array([-.2,0.,0.,.2,0.,0.]);h=eye(6,format='csr')
        step,_=constrained_step(h,x,x,{},[['cut',0,1]],[0.])
        np.testing.assert_allclose(x+step,0.,atol=1e-12)

    def test_unilateral_contact_complementarity(self):
        a=csr_matrix([[1.,0.,0.]]);points=np.zeros((1,3))
        result=solve_contact(Quadratic(-1.),points,np.array([[.1,0.,0.]]),{},a,np.array([0.]),[['blade',0]])
        x,lam,_,_,success,*_=result
        self.assertTrue(success);self.assertAlmostEqual(x[0,0],0.);self.assertAlmostEqual(lam[0],1.)

    def test_unloading_has_no_attractive_contact(self):
        a=csr_matrix([[1.,0.,0.]]);points=np.zeros((1,3))
        result=solve_contact(Quadratic(1.),points,points,{},a,np.array([0.]),[['blade',0]])
        x,lam,_,_,success,*_=result
        self.assertTrue(success);self.assertAlmostEqual(x[0,0],1.);self.assertEqual(lam[0],0.)


class GeometryCertificates(unittest.TestCase):
    def test_swept_volume_catches_midpath_collapse_with_valid_endpoints(self):
        points=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
        model=type('Cell',(),{'cells':np.array([[0,1,2,3]]),'volumes':np.array([1/6])})()
        rotated=points@np.diag([-1.,-1.,1.])
        self.assertAlmostEqual(swept_minimum_volume(model,points,rotated),0.,places=10)

    def test_rigid_translation_has_unit_swept_volume(self):
        points=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
        model=type('Cell',(),{'cells':np.array([[0,1,2,3]]),'volumes':np.array([1/6])})()
        self.assertAlmostEqual(swept_minimum_volume(model,points,points+[.3,.1,-.2]),1.,places=10)

    def test_proper_surface_crossing_and_separation(self):
        points=np.array([[-1.,-1.,0.],[1.,-1.,0.],[0.,1.,0.],
                         [0.,0.,-1.],[0.,0.,1.],[.5,.5,1.]])
        design={'pieces':[{'triangles':[[0,1,2]]},{'triangles':[[3,4,5]]}]}
        self.assertEqual(proper_surface_intersections(design,points)[0],1)
        points[3:]+=[0.,0.,3.]
        self.assertEqual(proper_surface_intersections(design,points)[0],0)

    def test_coplanar_cut_touch_is_not_a_proper_crossing(self):
        p=np.array([[0.,0.,0.],[0.,1.,0.],[0.,0.,1.]]*2)
        d={'pieces':[{'triangles':[[0,1,2]]},{'triangles':[[5,4,3]]}]}
        self.assertEqual(proper_surface_intersections(d,p)[0],0)


class RefinedAssembly(unittest.TestCase):
    def test_full_model_cohesion_removal_and_rigid_invariance(self):
        import json
        root=Path(__file__).resolve().parents[2]/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((root/'surface_design.json').read_text())
        assignments=json.loads((root/'mass_stiffness_assignments.json').read_text())
        points,intact=assemble_model(design,assignments,0.)
        _,broken=assemble_model(design,assignments,1.)
        self.assertEqual(len(points),4032);self.assertEqual(intact.interface_bonds,403);self.assertEqual(broken.interface_bonds,0)
        self.assertEqual(len(intact.pairs)-len(broken.pairs),403)
        pairs=cut_pairs(design);self.assertEqual(len(pairs),257)
        np.testing.assert_array_equal(points[pairs[:,0]],points[pairs[:,1]])
        for model in [intact,broken]:
            state=model.evaluate(points+[.001,.002,-.003])
            self.assertLess(state['energy_j'],1e-20)
            self.assertLess(np.linalg.norm(state['gradient_n']),1e-8)


if __name__=='__main__':unittest.main()
