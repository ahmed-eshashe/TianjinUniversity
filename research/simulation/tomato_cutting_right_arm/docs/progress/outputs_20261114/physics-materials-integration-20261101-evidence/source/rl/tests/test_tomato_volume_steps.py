import unittest
from tomato_volume_step_reference import fraction
class VolumeStepTests(unittest.TestCase):
 def setUp(self):self.x=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
 def test_rigid_translation_preserves_full_step(self):self.assertEqual(fraction(self.x,[[2.,3.,4.]]*4,1/6)['fraction'],1.)
 def test_single_vertex_inversion_is_stopped_before_floor(self):
  r=fraction(self.x,[[0.,0.,0.],[-2.,0.,0.],[0.,0.,0.],[0.,0.,0.]],1/6)
  self.assertAlmostEqual(r['fraction'],.405);self.assertGreater(r['lower_bound'],.1)
 def test_feasible_endpoint_cannot_hide_infeasible_rotation_path(self):
  r=fraction(self.x,[[0.,0.,0.],[-2.,0.,0.],[0.,-2.,0.],[0.,0.,0.]],1/6)
  self.assertAlmostEqual(sum(r['polynomial']),1.);self.assertLess(r['fraction'],.5)
  for k in range(101):
   a=r['fraction']*k/100;self.assertGreater(sum(c*a**i for i,c in enumerate(r['polynomial'])),.1)
 def test_infeasible_start_refused(self):
  with self.assertRaises(ValueError):fraction([[0,0,0],[.05,0,0],[0,1,0],[0,0,1]],[[0,0,0]]*4,1/6)
