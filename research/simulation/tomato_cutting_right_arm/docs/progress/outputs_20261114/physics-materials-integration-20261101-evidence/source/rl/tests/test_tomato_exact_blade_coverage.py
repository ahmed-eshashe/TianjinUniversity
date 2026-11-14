import unittest
import numpy as np
from tomato_exact_blade_coverage import coverage,verify_cells
class ExactBladeCoverageTests(unittest.TestCase):
 def setUp(self):
  self.vertices=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
  self.cells=np.array([[0,1,2,3]])
  self.soft=np.array([[-1.,-1.,.1],[2.,-1.,.1],[-1.,2.,.1]])
 def test_entire_intersection_with_all_soft_vertices_outside(self):
  c=coverage(self.vertices,self.cells,self.soft,[[0,1,2]])
  self.assertEqual(len(c['samples']),1);self.assertAlmostEqual(c['triangles'][0]['covered_area_m2'],.405)
  np.testing.assert_allclose(c['samples'][0]['point_m'],[.3,.3,.1],atol=1e-14)
 def test_clear_and_capacity_are_not_silent(self):
  self.assertEqual(coverage(self.vertices,self.cells,self.soft+[0,0,2],[[0,1,2]])['samples'],[])
  with self.assertRaises(ValueError):coverage(self.vertices,self.cells,self.soft,[[0,1,2]],capacity=1)
 def test_rigid_transform_and_reversed_soft_order_preserve_area(self):
  r=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]);t=np.array([10.,20.,30.])
  c=coverage(self.vertices@r.T+t,self.cells,self.soft@r.T+t,[[2,1,0]])
  self.assertAlmostEqual(c['triangles'][0]['covered_area_m2'],.405,places=12)
 def test_reference_measure_and_refinement_integrate_degree_two(self):
  values=[]
  for level in [0,1,2]:
   c=coverage(self.vertices,self.cells,self.soft,[[0,1,2]],reference_positions=self.soft*2,quadrature_level=level)
   values.append(sum(s['area_m2']*s['point_m'][0]**2 for s in c['samples']))
   self.assertAlmostEqual(sum(s['area_m2'] for s in c['samples']),4*.405,places=12)
  np.testing.assert_allclose(values,[values[0]]*3,rtol=0,atol=1e-12)
 def test_internal_coplanar_face_is_owned_once(self):
  v=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[0.,0.,-1.]])
  c=coverage(v,[[0,1,2,3],[0,2,1,4]],[[.1,.1,0],[.2,.1,0],[.1,.2,0]],[[0,1,2]])
  self.assertEqual(len(c['samples']),1);self.assertAlmostEqual(c['triangles'][0]['covered_area_m2'],.005)
 def test_oriented_boundary_certificate_detects_corruption(self):
  b=dict(vertices=self.vertices.tolist(),triangles=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
  d=dict(vertices=self.vertices.tolist(),cells=self.cells.tolist())
  self.assertTrue(verify_cells(b,d)['oriented_boundary_identical'])
  with self.assertRaises(ValueError):verify_cells(b,dict(d,cells=[[1,0,2,3]]))
  with self.assertRaises(ValueError):verify_cells(b,dict(d,cells=d['cells']*2))
