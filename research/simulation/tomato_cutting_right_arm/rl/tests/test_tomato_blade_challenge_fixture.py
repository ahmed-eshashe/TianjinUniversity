import unittest
from tomato_blade_challenge_fixture import build_fixtures
class BladeFixtureTests(unittest.TestCase):
    def blade(self):
        return {'units':'m','frame':'blade_local','source_sha256':'a'*64,
          'vertices':[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],
          'triangles':[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]}
    def test_positive_intersects_despite_vertex_clearance(self):
        r=build_fixtures(self.blade(),probe_halfspan_m=.001);p=r['cases'][0]
        self.assertTrue(all(x>0 for x in p['vertex_unsigned_clearances_m']));self.assertLess(p['finite_facet_oracle']['distance_m'],1e-12)
    def test_negative_finite_gap(self):
        r=build_fixtures(self.blade(),probe_halfspan_m=.001);self.assertGreater(r['cases'][1]['finite_facet_oracle']['distance_m'],0.)
    def test_original_blade_untouched(self):
        import copy
        b=self.blade();old=copy.deepcopy(b);r=build_fixtures(b,probe_halfspan_m=.001);self.assertEqual(b,old);self.assertFalse(r['blade_geometry_modified'])
    def test_fixture_not_acceptance_or_runtime(self):
        r=build_fixtures(self.blade(),probe_halfspan_m=.001);self.assertFalse(r['fixture_span_is_acceptance_tolerance']);self.assertTrue(all(not c['native_contact_validated'] for c in r['cases']))
    def test_invalid_span(self):
        with self.assertRaises(ValueError):build_fixtures(self.blade(),probe_halfspan_m=0.)
