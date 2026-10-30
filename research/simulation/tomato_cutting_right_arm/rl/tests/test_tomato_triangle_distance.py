import unittest,math
from tomato_triangle_distance import point_triangle,point_mesh
A=(0.,0.,0.);B=(1.,0.,0.);C=(0.,1.,0.)
class TriangleDistanceTests(unittest.TestCase):
    def test_face_projection(self):
        r=point_triangle((.2,.3,2.),A,B,C);self.assertAlmostEqual(r['distance_m'],2.);self.assertEqual(r['closest_point_m'],(.2,.3,0.));self.assertAlmostEqual(sum(r['barycentric']),1.)
    def test_edge_projection(self):
        r=point_triangle((.4,-.2,0.),A,B,C);self.assertAlmostEqual(r['distance_m'],.2);self.assertEqual(r['closest_point_m'],(.4,0.,0.))
    def test_vertex_projection(self):self.assertAlmostEqual(point_triangle((-1.,-1.,0.),A,B,C)['distance_m'],math.sqrt(2.))
    def test_on_surface(self):self.assertEqual(point_triangle((.25,.25,0.),A,B,C)['distance_m'],0.)
    def test_unsigned_both_sides(self):self.assertEqual(point_triangle((.2,.2,1.),A,B,C)['distance_m'],point_triangle((.2,.2,-1.),A,B,C)['distance_m'])
    def test_rigid_translation(self):
        t=(100.,-20.,5.);shift=lambda p:tuple(a+b for a,b in zip(p,t));self.assertAlmostEqual(point_triangle(shift((.2,.3,2.)),shift(A),shift(B),shift(C))['distance_m'],2.)
    def test_degenerate_refused(self):
        with self.assertRaises(ValueError):point_triangle(A,A,B,(2.,0.,0.))
    def test_mesh_nearest(self):
        vertices=[A,B,C,(0.,0.,3.),(1.,0.,3.),(0.,1.,3.)];r=point_mesh((.2,.2,2.),vertices,[[0,1,2],[3,4,5]]);self.assertEqual(r['triangle_id'],1);self.assertAlmostEqual(r['distance_m'],1.);self.assertFalse(r['inside_outside_classification_supplied'])
    def test_bad_index(self):
        with self.assertRaises(ValueError):point_mesh(A,[A,B,C],[[0,1,9]])
