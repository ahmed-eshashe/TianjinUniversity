import math
import unittest
from tomato_physx_bridge_reference import reference_packet


class BridgeReferenceTests(unittest.TestCase):
    def test_pose_is_not_reordered_and_velocity_is_com_velocity(self):
        pose=[1.,2.,3.,0.,0.,0.,1.];velocity=[1.,2.,3.,0.,0.,2.]
        r=reference_packet(pose,velocity,[.5,0.,0.],[0.,0.,-3.],[1.5,3.,3.])
        self.assertEqual(r['newton_pose_xyzw'],pose)
        self.assertEqual(r['newton_velocity_com_world'],velocity)
        self.assertEqual(r['com_world_m'],[1.5,2.,3.])
        self.assertEqual(r['contact_velocity_world_m_s'],[-1.,2.,3.])

    def test_reaction_moment_is_about_com_and_position_is_not_applied_twice(self):
        r=reference_packet([0.,0.,0.,0.,0.,0.,1.],[0.]*6,[1.,0.,0.],[0.,0.,-3.],[1.,2.,0.])
        self.assertEqual(r['physx_wrench']['force_n'],[0.,0.,3.])
        self.assertEqual(r['physx_wrench']['torque_about_com_nm'],[6.,0.,0.])
        self.assertIsNone(r['physx_wrench']['positions'])
        self.assertTrue(r['physx_wrench']['is_global'])

    def test_rotated_nonzero_com_is_transformed_to_world(self):
        s=math.sqrt(.5)
        r=reference_packet([1.,2.,3.,0.,0.,s,s],[0.]*6,[1.,0.,0.],[0.,0.,1.],[1.,3.,3.])
        for a,b in zip(r['com_world_m'],[1.,3.,3.]):self.assertAlmostEqual(a,b)
        self.assertLess(math.hypot(*r['physx_wrench']['torque_about_com_nm']),1e-12)

    def test_force_units_are_newtons_not_impulse(self):
        r=reference_packet([0.,0.,0.,0.,0.,0.,1.],[0.]*6,[0.]*3,[0.,0.,-3.],[0.]*3)
        self.assertEqual(r['physx_wrench']['force_n'][2],3.)
        self.assertFalse(r['native_transfer_enabled'])

    def test_invalid_pose_or_quaternion_refused(self):
        with self.assertRaises(ValueError):reference_packet([0.]*6,[0.]*6,[0.]*3,[0.]*3,[0.]*3)
        with self.assertRaises(ValueError):reference_packet([0.]*7,[0.]*6,[0.]*3,[0.]*3,[0.]*3)


if __name__=='__main__':unittest.main()
