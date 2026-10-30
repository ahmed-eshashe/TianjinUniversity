"""Seating feedback must release excess pressure and bound missing-contact preload."""
import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from seating_control import seating_hand_goals,SupportedPinchMonitor
class SeatingControlTests(unittest.TestCase):
 def test_release_and_preload_cap(self):
  s={'q_rad':[0.]*7+[.87,.2,.8,.8,.8,.8], 'contacts':[{'part':'index','on_handle':True,'force_n':5.}]}
  goals=np.array([.87,.3,.85,1.2,1.2,1.2]);r=seating_hand_goals(s,goals)
  self.assertLess(r[2],goals[2]);self.assertLessEqual(r[3],.9);self.assertEqual(r[0],goals[0]);self.assertLessEqual(r[1],.3+1e-10)
 def test_pinch_loss_stops_before_repeated_closing(self):
  m=SupportedPinchMonitor();s={'contacts':[]}
  m.update(s);m.update(s)
  with self.assertRaises(RuntimeError):m.update(s)
  m=SupportedPinchMonitor();m.update(s)
  m.update({'contacts':[{'part':p,'on_handle':True,'force_n':1.} for p in ['thumb','index']]})
  self.assertEqual(m.missing,0)

 def test_thumb_command_stays_below_observed_interference_range(self):
  s={'q_rad':[0.]*7+[.87,.4,.8,.8,.8,.8],'contacts':[]}
  self.assertLessEqual(seating_hand_goals(s,[.87,.5,.8,.8,.8,.8])[1],.38)

 def test_loaded_thumb_preserves_existing_holding_pressure(self):
  s={'q_rad':[0.]*7+[.87,.14,.8,.8,.8,.8], 'contacts':[{'part':'thumb','on_handle':True,'force_n':3.}]}
  self.assertAlmostEqual(seating_hand_goals(s,[.87,.32,.8,.8,.8,.8])[1],.32)

 def test_positive_contact_holds_goal(self):
  s={'q_rad':[0.]*7+[.87,.2,.8,.8,.8,.8], 'contacts':[{'part':'index','on_handle':True,'force_n':2.}]}
  r=seating_hand_goals(s,[.87,.2,.8,.8,.8,.8]);self.assertEqual(r[2],.8);self.assertGreater(r[3],.8)
if __name__=='__main__':unittest.main()
