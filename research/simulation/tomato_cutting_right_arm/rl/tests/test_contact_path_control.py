import copy,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contact_path_control import synchronized_increment,validated_waypoints,balanced_contact_goals,anchor_translation_correction
class ContactPathTests(unittest.TestCase):
 def test_joint_progress_is_synchronized_and_rate_limited(self):
  d=np.array([.04,-.002,.02]);rates=np.array([.001,.001,.003]);inc=synchronized_increment(d,rates)
  np.testing.assert_allclose(inc/d,np.full(3,.025));self.assertTrue(np.all(abs(inc)<=rates))
  np.testing.assert_allclose(synchronized_increment([.0001,0],[.001,.003]),[.0001,0])
 def plan(self):
  return {'waypoints':[{'hand_root_in_knife_m':[0,0,.001*i],'hand_rotation_in_knife':np.eye(3).tolist(),'joint_rad':[.8,.1,1,1,1,1], 'anchor_error_m':.0001,'normal_error':.1,'min_blade_gap_m':.01,'min_board_gap_m':.01} for i in range(3)]}
 def test_unsafe_paths_refused(self):
  self.assertEqual(len(validated_waypoints(self.plan())),3)
  for key,value in [('anchor_error_m',.001),('min_blade_gap_m',-.001),('normal_error',float('nan'))]:
   p=self.plan();p['waypoints'][1][key]=value
   with self.assertRaises(ValueError):validated_waypoints(p)
  p=self.plan();p['waypoints'][1]['hand_root_in_knife_m'][0]=.1
  with self.assertRaises(ValueError):validated_waypoints(p)
 def test_balanced_thumb_pressure_preserves_load_and_respects_cap(self):
  s={'q_rad':[0]*7+[.8,.14,1,1,1,1],'contacts':[{'part':p,'on_handle':True,'force_n':f} for p,f in [('thumb',3.),('index',4.),('middle',1.),('ring',1.)]]}
  r=balanced_contact_goals(s,[.8,.32,1.1,1.1,1.1,1.1]);self.assertGreater(r[1],.32);self.assertLess(r[2],1.1);self.assertLessEqual(r[1],.38)
 def test_unloaded_fingers_follow_acquisition_pose_instead_of_overcurling(self):
  s={'q_rad':[0]*7+[.8,.14,1,1,1,1],'contacts':[{'part':p,'on_handle':True,'force_n':3.} for p in ['thumb','index']]}
  goals=[.8,.3,1.1,1.2,1.2,1.2];planned=[.8,.3,1.1,.95,.96,1.2]
  r=balanced_contact_goals(s,goals,planned);self.assertEqual(r[3],.95);self.assertEqual(r[4],.96)
 def test_contact_feedback_moves_toward_reference_with_bounded_step(self):
  np.testing.assert_allclose(anchor_translation_correction([[.001,0,0],[.001,0,0]]),[.00015,0,0])
  np.testing.assert_allclose(anchor_translation_correction([[.001,0,0],[-.001,0,0]]),[0,0,0])
  with self.assertRaises(ValueError):anchor_translation_correction([[float('nan'),0,0],[0,0,0]])
 def test_initial_support_pressure_can_be_preserved(self):
  s={'q_rad':[0]*7+[.8,.14,1,1,1,1],'contacts':[{'part':p,'on_handle':True,'force_n':3.3} for p in ['thumb','index']]}
  r=balanced_contact_goals(s,[.8,.3,1.1,1,1,1],index_target=3.);self.assertEqual(r[2],1.1)
  with self.assertRaises(ValueError):balanced_contact_goals(s,[.8,.3,1.1,1,1,1],index_target=20.)
if __name__=='__main__':unittest.main()
