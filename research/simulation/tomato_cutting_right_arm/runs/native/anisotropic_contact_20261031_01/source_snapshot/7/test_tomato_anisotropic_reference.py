import math,unittest
from tomato_anisotropic_reference import apply_inertia,assess_rest_pulse
from tomato_isaac_startup_guard import worker_passed

class AnisotropicReferenceTests(unittest.TestCase):
    def test_identity_axes(self):
        self.assertEqual(apply_inertia([0,0,0,0,0,0,1],[1.,2.,2.5],[1.,2.,3.]),[1.,4.,7.5])
    def test_rotated_inverse_roundtrip_and_offdiagonal(self):
        q=[.133630620956,.267261241912,.400891862869,.866025403784];pose=[0,0,0]+q
        v=[.003,-.005,.004];principal=[.0001,.0002,.00025]
        omega=apply_inertia(pose,principal,v,True)
        self.assertLess(math.dist(apply_inertia(pose,principal,omega),v),1e-16)
        wrong=[v[i]/principal[i] for i in range(3)]
        self.assertGreater(math.dist(wrong,omega),1.)
    def test_bad_principal_moments(self):
        for moments in ([0.,1.,1.],[1.,1.,3.]):
            with self.assertRaises(ValueError):apply_inertia([0,0,0,0,0,0,1],moments,[1,1,1])
    def test_wrong_world_axes_rejected(self):
        pose=[0,0,0,.133630620956,.267261241912,.400891862869,.866025403784]
        torque=[.003,-.005,.004];p=[.0001,.0002,.00025];dt=1/1200
        wrong=[0.,0.,0.]+[dt*torque[i]/p[i] for i in range(3)]
        with self.assertRaises(ValueError):assess_rest_pulse(pose,pose,wrong,[0.]*3,torque,.02,p,dt)
    def test_guard_scope(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,anisotropic_checks_passed=True,
            anisotropic_cases_completed=2,newton_steps=2,physx_steps=1,world_tensor_exercised=True)
        self.assertTrue(worker_passed(r,'anisotropic_contact'))
        self.assertFalse(worker_passed(dict(r,world_tensor_exercised=False),'anisotropic_contact'))
        self.assertFalse(worker_passed(dict(r,physx_steps=2),'anisotropic_contact'))
