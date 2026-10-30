"""The reposition diagnostic commands only a bounded hand arc; knife bounds are measured."""
import sys
from pathlib import Path
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from in_place_motion import tilt_path,knife_motion,relative_command_pose

class InPlaceMotionTests(unittest.TestCase):
    def setUp(self):
        self.pose=np.array([0.,0.,0.,0.,0.,0.,1.])
        self.points=np.array([[-.2,-.01,0.],[.2,.01,.01]])
        self.lo=np.array([-.25,-.1,0.]);self.hi=np.array([.25,.1,.01])

    def test_pitch_is_upward_bounded_and_preserves_pivot_distance(self):
        palm=np.array([-.08,0.,.05]);blade=np.array([[-.4,-.02,0.],[-.2,.02,.01]])
        pivot=np.array([-.34,0.,0.])
        for roll in [0,12,-12]:
            path=list(tilt_path(palm,np.eye(3),self.pose,np.array([-.08,0,0]),blade,roll))
            self.assertEqual(len(path),24)
            for pos,rotation in path:
                self.assertAlmostEqual(np.linalg.norm(pos-pivot),np.linalg.norm(palm-pivot))
                self.assertLessEqual(np.rad2deg(Rotation.from_matrix(rotation).magnitude()),15)
            self.assertGreater(path[-1][0][2],palm[2])
        with self.assertRaises(ValueError):list(tilt_path(palm,np.eye(3),self.pose,palm,blade,13))

    def test_relative_motion_preserves_load_holding_offset(self):
        actual=np.array([1.,2.,3.]);command=actual+np.array([.001,0,.007])
        ar=Rotation.from_euler('x',.02).as_matrix();cr=Rotation.from_euler('y',.01).as_matrix()
        p,r=relative_command_pose(actual,ar,command,cr,actual,ar)
        np.testing.assert_allclose(p,command);np.testing.assert_allclose(r,cr,atol=1e-15)
        p,r=relative_command_pose(actual,ar,command,cr,actual+[0,0,.003],ar)
        np.testing.assert_allclose(p,command+[0,0,.003]);np.testing.assert_allclose(r,cr,atol=1e-15)

    def test_whole_knife_edge_translation_and_rotation_are_checked(self):
        self.assertTrue(knife_motion(self.points,self.pose,self.pose,self.lo,self.hi)['within_bounds'])
        moved=self.pose.copy();moved[0]=.031
        self.assertFalse(knife_motion(self.points,self.pose,moved,self.lo,self.hi)['within_bounds'])
        rotated=self.pose.copy();rotated[3:]=Rotation.from_euler('x',21,degrees=True).as_quat()
        self.assertFalse(knife_motion(self.points,self.pose,rotated,self.lo,self.hi)['within_bounds'])
        moved=self.pose.copy();moved[1]=.095
        self.assertFalse(knife_motion(self.points,self.pose,moved,self.lo,self.hi)['within_bounds'])

if __name__=='__main__':unittest.main()
