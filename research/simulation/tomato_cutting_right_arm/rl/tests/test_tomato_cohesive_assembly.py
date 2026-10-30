import unittest
from tomato_cohesive_assembly import assemble
from tomato_surface_cohesion import patch_response
from tomato_cohesive_evolution_reference import patch_contact_eligibility

class AssemblyTests(unittest.TestCase):
    def data(self,d=.4):
        return ([[0.,0.,0.],[.001,.002,0.]],[[0,1]],[[0.,0.,0.]],
            [{'id':'p','indices':[0],'weights':[1.],'stiffness':[[100.,0.,0.],[0.,40.,0.],[0.,0.,30.]],'damage':d}])
    def test_original_response_force_sign_and_hessian(self):
        x,pairs,rest,patches=self.data();r=assemble(x,pairs,rest,patches)
        old=patch_response([[.001,.002,0.]],[1.],patches[0]['stiffness'],.4,tangent=True)
        self.assertAlmostEqual(r['energy_j'],old['energy_j'],places=14)
        for j in range(3):self.assertAlmostEqual(r['nodal_force_n'][0][j],old['gradient_n'][0,j],places=14);self.assertEqual(r['nodal_force_n'][0][j],-r['nodal_force_n'][1][j])
        h={(i,j):v for i,j,v in r['frozen_damage_energy_hessian_triplets']}
        for i,j in h:self.assertEqual(h[i,j],h[j,i])
        for i in range(6):
            for axis in range(3):self.assertAlmostEqual(sum(h.get((i,j),0.) for j in [axis,axis+3]),0.)
        self.assertFalse(r['implicit_softening_stability_validated'])
    def test_full_failure_no_mechanical_bridge(self):
        r=assemble(*self.data(1.));self.assertEqual(r['nodal_force_n'],[[0.,0.,0.],[0.,0.,0.]]);self.assertEqual(r['frozen_damage_energy_hessian_triplets'],[])
    def test_duplicate_patch_refused(self):
        x,p,r,patch=self.data();patch.append(patch[0])
        with self.assertRaises(ValueError):assemble(x,p,r,patch)
    def test_eligibility_requires_swept_hit_and_width(self):
        r=patch_contact_eligibility([[0],[1],[2]],[False,True,True],[[1.,0.]]*3,[.1,0.,.1]);self.assertEqual(r,[False,False,True])
    def test_exact_multiplier_threshold(self):
        self.assertEqual(patch_contact_eligibility([[0],[1]],[True,True],[[1e-9,0.],[1.0001e-9,0.]],[.1,.1]),[False,True])
    def test_contact_indices_refused(self):
        with self.assertRaises(ValueError):patch_contact_eligibility([[2]],[True],[[1.,0.]],[.1])
