import math,unittest
from tomato_turning_sequence_reference import step
from tomato_offset_contact_reference import world_point,rotation_vector
from tomato_isaac_startup_guard import worker_passed

class TurningSequenceTests(unittest.TestCase):
    def test_rotation_contact_exit_and_coast(self):
        b=dict(pose=[0,0,0,0,0,0,1],velocity=[0.]*6,p=[.004,.003,.001],vp=[0.]*3)
        normal0=None;clear=0
        for _ in range(16):
            r=step(b,[0.]*3,.01,.02,.0001,1750.,.002,1/1200)
            if normal0 is None:normal0=r['normal']
            clear+=r['signed_depth_m']<=0;b=r['after']
        self.assertGreater(clear,3);self.assertGreater(math.dist(r['normal'],normal0),1e-5)
        self.assertGreater(math.hypot(*rotation_vector([0,0,0,1],b['pose'][3:])),1e-5)
    def test_zero_force_retains_spin_and_com_coast(self):
        q=[0,math.sqrt(.5),0,math.sqrt(.5)];com=[.002,-.001,.0005];pose=[0,.05,0]+q
        b=dict(pose=pose,velocity=[.02,.03,-.01,.1,.2,-.1],p=world_point(pose,[.004,.003,.004]),vp=[0.]*3)
        r=step(b,com,.01,.02,.0001,1750.,.002,1/1200)
        self.assertEqual(r['force'],[0.]*3);self.assertEqual(r['after']['velocity'],b['velocity'])
        actual=world_point(r['after']['pose'],com);initial=world_point(pose,com)
        self.assertLess(math.dist(actual,[initial[j]+b['velocity'][j]/1200 for j in range(3)]),1e-15)
    def test_bad_input_rejected(self):
        b=dict(pose=[0,0,0,0,0,0,1],velocity=[0.]*6,p=[.004,.003,.001],vp=[0.]*3)
        with self.assertRaises(ValueError):step(b,[0.]*3,.01,.02,0.,1750.,.002,1/1200)
    def test_guard_scope(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,turning_sequence_checks_passed=True,
            turning_cases_completed=2,newton_steps=32,physx_steps=16,min_coast_steps=8,normals_updated=True)
        self.assertTrue(worker_passed(r,'turning_sequence'))
        for k,v in [('newton_steps',33),('physx_steps',17),('min_coast_steps',0),('normals_updated',False)]:
            self.assertFalse(worker_passed(dict(r,**{k:v}),'turning_sequence'))
