import unittest
from tomato_facet_distance import segment_segment,segment_triangle,triangle_triangle
from tomato_triangle_distance import point_triangle
T=[(-1.,-1.,0.),(1.,-1.,0.),(0.,1.,0.)]
class FacetDistanceTests(unittest.TestCase):
    def test_edge_through_face_all_endpoints_clear(self):
        a=(0.,0.,-1.);b=(0.,0.,1.)
        self.assertGreater(point_triangle(a,*T)['distance_m'],0);self.assertGreater(point_triangle(b,*T)['distance_m'],0)
        r=segment_triangle(a,b,T);self.assertAlmostEqual(r['distance_m'],0.);self.assertEqual(r['feature'],'edge_through_face')
    def test_parallel_faces_separated(self):
        other=[(x,y,z+2) for x,y,z in T];self.assertAlmostEqual(triangle_triangle(T,other)['distance_m'],2.)
    def test_coplanar_contained(self):self.assertAlmostEqual(triangle_triangle(T,[(-.1,-.1,0.),(.1,-.1,0.),(0.,.1,0.)])['distance_m'],0.)
    def test_coplanar_disjoint(self):self.assertGreater(triangle_triangle(T,[(x+5,y,z) for x,y,z in T])['distance_m'],0.)
    def test_skew_edges(self):self.assertAlmostEqual(segment_segment((-1.,0.,0.),(1.,0.,0.),(0.,-1.,1.),(0.,1.,1.))['distance_m'],1.)
    def test_parallel_edges(self):self.assertAlmostEqual(segment_segment((0.,0.,0.),(1.,0.,0.),(0.,1.,0.),(1.,1.,0.))['distance_m'],1.)
    def test_intersecting_triangles(self):
        other=[(0.,0.,-1.),(0.,0.,1.),(2.,0.,1.)];self.assertAlmostEqual(triangle_triangle(T,other)['distance_m'],0.)
    def test_translation_invariance(self):
        a=[(x,y,z+2) for x,y,z in T];shift=lambda tri:[(x+10,y-5,z+3) for x,y,z in tri]
        self.assertAlmostEqual(triangle_triangle(T,a)['distance_m'],triangle_triangle(shift(T),shift(a))['distance_m'])
    def test_zero_edge_refused(self):
        with self.assertRaises(ValueError):segment_segment((0.,0.,0.),(0.,0.,0.),(0.,1.,0.),(1.,1.,0.))
    def test_no_penetration_or_native_claim(self):
        r=triangle_triangle(T,[(x,y,z+2) for x,y,z in T]);self.assertFalse(r['penetration_depth_supplied']);self.assertFalse(r['native_contact_validated'])
