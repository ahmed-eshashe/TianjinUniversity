import unittest,copy
from tomato_checkpoint_learning_record import record
class CheckpointRecordTests(unittest.TestCase):
 def fixture(self):return {'clock':1.,'outer_step':1,'robot_state':{'q':[.1],'qd':[.2],'tool_pose':[0,0,0,0,0,0,1],'tool_com_velocity':[0]*6}}
 def test_hidden_truth_does_not_change_actor(self):
  m=self.fixture();before=record(m,['joint']);m.update(damage=[1.],reaction=[999]*6,connectivity='separated');self.assertEqual(before,record(m,['joint']))
 def test_missing_channels_masked_no_action_or_success(self):
  r=record(self.fixture(),['joint']);self.assertEqual(r['observation']['mask'][-10:],[0]*10);self.assertIsNone(r['demonstrated_action']);self.assertFalse(r['successful_demonstration']);self.assertFalse(r['training_enabled'])
 def test_nonfinite_state_rejected(self):
  m=self.fixture();m['robot_state']['q']=[float('nan')]
  with self.assertRaises(ValueError):record(m,['joint'])
 def test_inconsistent_joint_width_rejected(self):
  with self.assertRaises(ValueError):record(self.fixture(),['a','b'])
