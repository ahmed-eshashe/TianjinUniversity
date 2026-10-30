import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rolling_contact_control import project_contact_motion
class RollingContactTests(unittest.TestCase):
 def test_preserves_instantaneous_contacts_and_joint_rates(self):
  j=np.array([[1,0,1,0],[0,1,0,1]],float);limits=np.array([.00015,.00015,.001,.001]);d=project_contact_motion(j,[1,-1,.3,.2],limits)
  np.testing.assert_allclose(j@d,[0,0],atol=1e-15);self.assertTrue(np.all(abs(d)<=limits));self.assertGreater(np.linalg.norm(d),0)
 def test_fully_constrained_motion_cannot_advance(self):
  np.testing.assert_allclose(project_contact_motion(np.eye(3),[1,2,3],[.001]*3),[0]*3,atol=1e-15)
 def test_nonfinite_input_is_rejected(self):
  with self.assertRaises(ValueError):project_contact_motion([[float('nan')]], [1],[.001])
