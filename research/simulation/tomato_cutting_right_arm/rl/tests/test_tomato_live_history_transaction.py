import unittest
from types import SimpleNamespace
import numpy as np
import warp as wp
from tomato_live_history_transaction import HistoryTransaction

class HistoryTransactionControls(unittest.TestCase):
    def setUp(self):
        wp.init()
        self.h=SimpleNamespace(
            pairs=wp.array([[[0,1],[2,3],[4,5]]],dtype=wp.vec2i,device='cpu'),
            counts=wp.array([3],dtype=int,device='cpu'),
            objective_anchors=wp.array([[0,1,2]],dtype=wp.vec3i,device='cpu'),
            objective_sign=wp.array([1.],dtype=wp.float64,device='cpu'),
            objective_weights=wp.array([[1/3]*3],dtype=wp.float64,device='cpu'),
            objective_stiffness=wp.array([np.diag([100.,40.,30.])],dtype=wp.mat33d,device='cpu'),
            objective_law=wp.array([[100.,.001,.004]],dtype=wp.vec3d,device='cpu'),
            objective_history=wp.zeros(1,dtype=wp.vec2d,device='cpu'),
            history=wp.zeros(1,dtype=wp.vec2,device='cpu'))
    def positions(self,gap):
        return wp.array([[0,0,0],[gap,0,0],[0,.01,0],[gap,.01,0],[0,0,.01],[gap,0,.01]],dtype=wp.vec3d,device='cpu')
    def transaction(self,gap,eligible=True):
        return HistoryTransaction(self.h,self.positions(gap),np.array([eligible]))
    def test_rejection_and_trial_do_not_damage_material(self):
        t=self.transaction(.005)
        self.assertEqual(t.trial_history[0,1],1.)
        np.testing.assert_array_equal(self.h.objective_history.numpy(),[[0.,0.]])
        t.reject()
        np.testing.assert_array_equal(self.h.history.numpy(),[[0.,0.]])
        with self.assertRaises(RuntimeError):t.commit(audits_passed=True)
    def test_analytic_bilinear_damage_and_no_healing(self):
        t=self.transaction(.002);t.commit(audits_passed=True)
        self.assertAlmostEqual(self.h.objective_history.numpy()[0,1],2/3)
        self.transaction(.0001).commit(audits_passed=True)
        self.assertAlmostEqual(self.h.objective_history.numpy()[0,1],2/3)
        self.transaction(.004).commit(audits_passed=True)
        self.assertEqual(self.h.objective_history.numpy()[0,1],1.)
    def test_no_contact_cannot_create_failure(self):
        self.transaction(.1,False).commit(audits_passed=True)
        np.testing.assert_array_equal(self.h.objective_history.numpy(),[[0.,0.]])
    def test_stale_and_duplicate_commit_rejected(self):
        old=self.transaction(.003);new=self.transaction(.002);new.commit(audits_passed=True)
        with self.assertRaises(RuntimeError):old.commit(audits_passed=True)
        with self.assertRaises(RuntimeError):new.commit(audits_passed=True)
    def test_failed_audit_preserves_both_histories(self):
        t=self.transaction(.005)
        with self.assertRaises(ValueError):t.commit(audits_passed=False)
        np.testing.assert_array_equal(self.h.objective_history.numpy(),[[0.,0.]])
        np.testing.assert_array_equal(self.h.history.numpy(),[[0.,0.]])
    def test_collapsed_active_frame_rejected(self):
        with self.assertRaises(ValueError):HistoryTransaction(self.h,wp.zeros(6,dtype=wp.vec3d,device='cpu'),np.array([True]))

if __name__=='__main__':unittest.main()
