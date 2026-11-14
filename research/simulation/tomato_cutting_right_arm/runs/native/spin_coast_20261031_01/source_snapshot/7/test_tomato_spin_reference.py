import math,unittest
from tomato_spin_reference import advance,invariants,rotate
from tomato_offset_contact_reference import rotation_vector
from tomato_isaac_startup_guard import worker_passed

class SpinReferenceTests(unittest.TestCase):
    def test_invariants_and_refinement(self):
        p=[.0001,.0002,.00025];q=[0.,0.,0.,1.];w=[1.,2.,3.]
        original=invariants(q,w,p)
        a=advance(q,w,p,16/1200,16);b=advance(q,w,p,16/1200,32)
        self.assertLess(math.dist(a['omega_world'],b['omega_world']),1e-10)
        final=invariants(a['q'],a['omega_world'],p)
        self.assertLess(math.dist(final['angular_momentum'],original['angular_momentum']),1e-14)
        self.assertLess(abs(final['energy']-original['energy']),1e-14)
        self.assertGreater(math.dist(a['omega_world'],w),.001)
    def test_principal_axis_spin(self):
        r=advance([0.,0.,0.,1.],[0.,0.,3.],[.0001,.0002,.00025],.01)
        self.assertLess(math.dist(r['omega_world'],[0.,0.,3.]),1e-12)
        self.assertAlmostEqual(rotation_vector([0,0,0,1],r['q'])[2],.03)
    def test_rotational_covariance(self):
        q=[.133630620956,.267261241912,.400891862869,.866025403784];p=[.0001,.0002,.00025];w=[1.,2.,3.]
        a=advance([0,0,0,1],w,p,.01);b=advance(q,w,p,.01)
        self.assertLess(math.dist(rotate(q,a['omega_world']),b['omega_world']),1e-10)
    def test_bad_input(self):
        with self.assertRaises(ValueError):advance([0,0,0,1],[1,2,3],[0,1,1],.01)
    def test_guard_scope(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,spin_checks_passed=True,spin_cases_completed=3,
            physx_steps=16,newton_steps=0,cuda_state_echoes=48,gyro_control_distinguished=True)
        self.assertTrue(worker_passed(r,'spin_coast'))
        for k,v in [('physx_steps',17),('newton_steps',1),('cuda_state_echoes',47),('gyro_control_distinguished',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'spin_coast'))
