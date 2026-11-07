import unittest
from tomato_blade_ambiguity_audit import audit_point,audit_sampled_minimum


class BladeAmbiguityTests(unittest.TestCase):
    vertices=[[0.,0.,.002],[1.,0.,.002],[0.,1.,.002],
              [0.,0.,-.002],[0.,1.,-.002],[1.,0.,-.002]]
    triangles=[[0,1,2],[3,4,5]]

    def test_medial_plane_opposing_normals_are_tied(self):
        r=audit_point([.25,.25,0.],self.vertices,self.triangles)
        self.assertEqual(r['opposing_normal_distance_gap_m'],0.)
        self.assertTrue(all(b['different_normal_branch_present'] for b in r['bands']))

    def test_off_medial_plane_has_known_distance_gap(self):
        r=audit_point([.25,.25,.0001],self.vertices,self.triangles)
        self.assertAlmostEqual(r['opposing_normal_distance_gap_m'],.0002)
        self.assertFalse(any(b['different_normal_branch_present'] for b in r['bands']))

    def test_coplanar_duplicate_is_not_a_different_normal_branch(self):
        r=audit_point([.25,.25,.0001],self.vertices,[[0,1,2],[0,1,2]])
        self.assertIsNone(r['different_normal_distance_gap_m'])
        self.assertEqual(r['bands'][0]['nearby_facet_count'],2)

    def test_equal_depth_different_locations_are_exposed(self):
        rows=[{'reference_penetration_m':.001,'normal_world':[0.,0.,1.],
               'soft_point_world_m':p} for p in ([0.,0.,0.],[.02,0.,0.])]
        result=audit_sampled_minimum(rows)
        self.assertEqual(result['bands'][0]['maximum_location_spread_m'],.02)
        self.assertFalse(result['global_minimum_certified'])

    def test_nonminimal_opposite_sample_does_not_create_minimum_tie(self):
        rows=[{'reference_penetration_m':d,'normal_world':n,'soft_point_world_m':p}
              for d,n,p in [(.002,[0.,0.,1.],[0.,0.,0.]),(.001,[0.,0.,-1.],[0.,0.,.001])]]
        self.assertTrue(all(b['near_best_sample_count']==1 for b in audit_sampled_minimum(rows)['bands']))

    def test_saturated_sample_stream_refused(self):
        with self.assertRaises(ValueError):audit_sampled_minimum([{}]*2048)


if __name__=='__main__':unittest.main()
