import unittest
from tomato_sdf_diagnostics import *

V=[[x,y,z] for x in (0.,.008) for y in (0.,.016) for z in (0.,.032)]
class SdfTests(unittest.TestCase):
    def test_grid_formula(self):
        r=grid_estimate(V,padding_m=0,max_resolution=32);self.assertEqual(r['grid_dimensions'],[9,17,33]);self.assertEqual(r['cell_size_m'],[.001]*3)
    def test_padding_explicit(self):
        a=grid_estimate(V,padding_m=0,max_resolution=32);b=grid_estimate(V,padding_m=.01,max_resolution=32)
        self.assertGreater(b['cell_size_m'][2],a['cell_size_m'][2])
    def test_no_accuracy_claim(self):self.assertFalse(grid_estimate(V,padding_m=0,max_resolution=32)['spacing_is_distance_error_bound'])
    def test_invalid_resolution(self):
        for n in [0,7,65536]:
            with self.assertRaises(ValueError):grid_estimate(V,padding_m=0,max_resolution=n)
    def probes(self):return surface_probes(V,[[0,1,2]])
    def test_all_feature_types(self):self.assertEqual({p['kind'] for p in self.probes()},{'vertex','edge','face_interior'})
    def test_exact_surface_reference(self):self.assertTrue(all(p['reference_distance_m']==0 for p in self.probes()))
    def test_missing_queries_refused(self):
        with self.assertRaises(ValueError):compare_surface_queries(self.probes(),{},distance_budget_m=.001,budget_status='draft')
    def test_draft_never_qualifies(self):
        p=self.probes();r=compare_surface_queries(p,{x['id']:0 for x in p},distance_budget_m=.001,budget_status='draft');self.assertTrue(r['surface_distance_within_budget']);self.assertFalse(r['qualification_enabled'])
    def test_error_over_budget(self):
        p=self.probes();r=compare_surface_queries(p,{x['id']:.002 for x in p},distance_budget_m=.001,budget_status='frozen');self.assertFalse(r['surface_distance_within_budget'])
    def test_nonfinite_query(self):
        p=self.probes()
        with self.assertRaises(ValueError):compare_surface_queries(p,{x['id']:float('nan') for x in p},distance_budget_m=.001,budget_status='draft')
