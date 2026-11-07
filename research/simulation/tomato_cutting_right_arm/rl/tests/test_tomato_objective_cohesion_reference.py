import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_objective_cohesion_reference import make_patch,response

class ObjectiveCohesionTests(unittest.TestCase):
 def setUp(self):
  self.x=np.array([[[0,y,z],[0,y,z]] for y,z in [(0,0),(.005,0),(0,.005),(.005,.005)]],float)
  self.patch=make_patch(self.x,np.ones(4)/4,np.diag([100.,60.,80.]),(.001,.004,100.))
 def test_rotation_force_and_energy_with_mixed_compression_shear(self):
  for opening in [.0004,-.0004]:
   x=self.x.copy();x[:,1]+=[opening,.0014,.0003]
   a=response(x,self.patch,eligible=True);q=Rotation.from_rotvec([.3,.6,-.2]).as_matrix();b=response(x@q.T+[.2,-.1,.3],self.patch,eligible=True)
   self.assertAlmostEqual(a['stored_energy_j'],b['stored_energy_j'],12);np.testing.assert_allclose(a['force_n']@q.T,b['force_n'],rtol=1e-9,atol=1e-11);np.testing.assert_allclose(a['trial_history'],b['trial_history'],rtol=1e-9)
 def test_no_rigid_motion_force(self):
  q=Rotation.from_rotvec([1.,-.2,.7]).as_matrix();a=response(self.x@q.T+[2,1,3],self.patch,eligible=True)
  self.assertEqual(a['stored_energy_j'],0.);self.assertEqual(a['trial_history'][1],0.);self.assertTrue(np.all(a['force_n']==0))
 def test_exact_gradient_and_internal_moment(self):
  x=self.x.copy();x[:,1]+=[.0004,.0002,0.];x[2,1,2]+=.0002
  a=response(x,self.patch);g=-a['force_n'];h=1e-8
  for i in np.ndindex(x.shape):
   plus=x.copy();minus=x.copy();plus[i]+=h;minus[i]-=h
   fd=(response(plus,self.patch)['stored_energy_j']-response(minus,self.patch)['stored_energy_j'])/(2*h)
   self.assertAlmostEqual(fd,g[i],7)
  np.testing.assert_allclose(a['force_n'].sum(axis=(0,1)),0,atol=1e-12);np.testing.assert_allclose(np.cross(x,a['force_n']).sum(axis=(0,1)),0,atol=1e-12)
 def test_loading_tangent_and_history(self):
  x=self.x.copy();x[:,1]+=[.002,.0002,0.];a=response(x,self.patch,eligible=True,tangent=True);h=1e-8;direction=np.random.default_rng(2).normal(size=x.shape)
  fd=(response(x+h*direction,self.patch,eligible=True)['force_n']-response(x-h*direction,self.patch,eligible=True)['force_n'])/(2*h)
  np.testing.assert_allclose(fd.ravel(),a['force_jacobian_n_m']@direction.ravel(),rtol=1e-6,atol=1e-7)
  b=response(self.x,self.patch,history=a['trial_history'],eligible=True);self.assertEqual(b['trial_history'],a['trial_history'])
 def test_compression_and_failure(self):
  x=self.x.copy();x[:,1,0]-=.0005;a=response(x,self.patch,eligible=True);self.assertEqual(a['trial_history'][1],0.);self.assertEqual(a['stored_energy_j'],0.)
  x=self.x.copy();x[:,1,0]+=.005;a=response(x,self.patch,eligible=True,tangent=True);self.assertEqual(a['trial_history'][1],1.);self.assertTrue(np.all(a['force_n']==0));self.assertTrue(np.all(a['force_jacobian_n_m']==0))
 def test_loading_potential_gradient_and_fracture_budget(self):
  x=self.x.copy();x[:,1]+=[.002,.0002,0.];a=response(x,self.patch,eligible=True);direction=np.random.default_rng(7).normal(size=x.shape);h=1e-8
  derivative=(response(x+h*direction,self.patch,eligible=True)['incremental_potential_j']-response(x-h*direction,self.patch,eligible=True)['incremental_potential_j'])/(2*h)
  self.assertAlmostEqual(derivative,-float(np.sum(a['force_n']*direction)),7)
  failed=self.x.copy();failed[:,1,0]+=.005
  self.assertAlmostEqual(response(failed,self.patch,eligible=True)['incremental_potential_j'],.5*100*.001*.004,12)
 def test_ineligible_and_invalid_frame(self):
  x=self.x.copy();x[:,1,1]+=.003;self.assertEqual(response(x,self.patch)['trial_history'],(0.,0.))
  with self.assertRaises(ValueError):response(np.zeros_like(x),self.patch)
if __name__=='__main__':unittest.main()
