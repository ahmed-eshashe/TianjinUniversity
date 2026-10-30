import unittest
from tomato_cohesive_adapter_reference import patch_reference
from tomato_surface_cohesion import patch_response

# Six top-level response evaluations total: original+new for each diagnostic.
class CohesiveAdapterTests(unittest.TestCase):
    def compare(self,gaps,damage):
        w=[.25,.75];k=[[100.,0.,0.],[0.,40.,5.],[0.,5.,30.]]
        a=patch_reference(gaps,w,k,damage);b=patch_response(gaps,w,k,damage,tangent=True)
        self.assertAlmostEqual(a['energy_j'],b['energy_j'],places=14)
        for rows1,rows2 in [(a['gap_gradient_n'],b['gradient_n'].tolist())]:
            for r1,r2 in zip(rows1,rows2):
                for x,y in zip(r1,r2):self.assertAlmostEqual(x,y,places=14)
        for h1,h2 in zip(a['frozen_damage_tangent_n_m'],b['tangent_n_m'].tolist()):
            for r1,r2 in zip(h1,h2):
                for x,y in zip(r1,r2):self.assertAlmostEqual(x,y,places=14)
        for f1,f2 in zip(a['force_on_first_n'],a['force_on_second_n']):
            for x,y in zip(f1,f2):self.assertEqual(x,-y)
        self.assertFalse(a['native_runtime_validated']);return a
    def test_intact_mixed_opening(self):self.compare([[.001,.002,-.001],[.002,-.001,.001]],0.)
    def test_partial_compression_unloading(self):
        a=self.compare([[-.001,0.,0.],[0.,.001,0.]],.4);self.assertEqual(a['gap_gradient_n'][0],[0.,0.,0.])
    def test_full_damage_zero_residual(self):
        a=self.compare([[.001,.002,0.],[.002,0.,.001]],1.);self.assertEqual(a['energy_j'],0.);self.assertTrue(all(x==0 for r in a['gap_gradient_n'] for x in r))
