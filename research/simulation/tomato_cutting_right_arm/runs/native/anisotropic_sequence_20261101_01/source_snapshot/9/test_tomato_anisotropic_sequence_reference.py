import math,unittest
from tomato_anisotropic_sequence_reference import step
from tomato_anisotropic_reference import apply_inertia
from tomato_isaac_startup_guard import worker_passed

class SequenceTests(unittest.TestCase):
    def test_contact_separates_and_keeps_turning(self):
        b=dict(pose=[0,0,0,0,0,0,1],velocity=[0.]*6,p=[.004,.003,.001],vp=[0.]*3);p=[.0001,.0002,.00025];clear=0
        for _ in range(32):
            r=step(b,[0.]*3,.01,.02,p,1750.,.002,1/2400);clear+=r['signed_depth_m']<=0;b=r['after']
        self.assertGreater(clear,3);self.assertGreater(math.hypot(*b['velocity'][3:]),.001)
    def test_isotropic_limit(self):
        from tomato_turning_sequence_reference import step as isotropic
        b=dict(pose=[0,0,0,0,0,0,1],velocity=[0.]*6,p=[.004,.003,.001],vp=[0.]*3)
        a=step(b,[0.]*3,.01,.02,[.0001]*3,1750.,.002,1/2400)
        z=isotropic(b,[0.]*3,.01,.02,.0001,1750.,.002,1/2400)
        self.assertLess(math.dist(a['after']['velocity'],z['after']['velocity']),1e-15)
    def test_guard_contract(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,anisotropic_sequence_checks_passed=True,
            anisotropic_sequence_cases_completed=2,newton_steps=64,physx_steps=32,min_coast_steps=20,normals_updated=True)
        self.assertTrue(worker_passed(r,'anisotropic_sequence'))
        for k,v in [('newton_steps',63),('physx_steps',33),('min_coast_steps',0),('normals_updated',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'anisotropic_sequence'))
