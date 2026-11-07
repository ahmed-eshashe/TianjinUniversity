import unittest
from tomato_partitioned_reference import reference,assess
from tomato_isaac_startup_guard import worker_passed

class PartitionedReferenceTests(unittest.TestCase):
    def test_contact_and_work_identity(self):
        r=reference(.001,0.,.01,.02,1750.,.002,1/1200)
        a={k:v for k,v in r.items() if k!='force_n'}
        check=assess(.001,0.,.01,.02,1750.,.002,1/1200,a,r['force_n'])
        self.assertLess(check['energy_identity_error_j'],1e-18)
        self.assertGreater(check['partition_splitting_work_j'],0.)
        self.assertLess(a['body_vz'],0.)
    def test_tgs_substeps_work_and_position(self):
        r=reference(.001,0.,.01,.02,1750.,.002,1/1200,body_substeps=16)
        a={k:v for k,v in r.items() if k!='force_n'}
        check=assess(.001,0.,.01,.02,1750.,.002,1/1200,a,r['force_n'],body_substeps=16)
        self.assertAlmostEqual(a['body_z'],(1/1200)*a['body_vz']*17/32)
        self.assertLess(check['energy_identity_error_j'],1e-18)
        with self.assertRaises(ValueError):assess(.001,0.,.01,.02,1750.,.002,1/1200,a,r['force_n'])
    def test_clear_control(self):
        r=reference(.003,0.,.01,.02,1750.,.002,1/1200)
        self.assertEqual(r['force_n'],0.)
        assess(.003,0.,.01,.02,1750.,.002,1/1200,{k:v for k,v in r.items() if k!='force_n'},0.)
    def test_missing_reaction_rejected(self):
        r=reference(.001,0.,.01,.02,1750.,.002,1/1200)
        a={k:v for k,v in r.items() if k!='force_n'};a['body_vz']=0.;a['body_z']=0.
        with self.assertRaises(ValueError):assess(.001,0.,.01,.02,1750.,.002,1/1200,a,r['force_n'])
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):reference(float('nan'),0.,.01,.02,1750.,.002,1/1200)
    def test_guard_scope(self):
        r=dict(diagnostic_passed=True,shutdown_requested=True,feedback_cases_completed=2,newton_steps=2,physx_steps=1,feedback_checks_passed=True)
        self.assertTrue(worker_passed(r,'contact_feedback'))
        for key in ('feedback_cases_completed','newton_steps','physx_steps'):
            self.assertFalse(worker_passed(dict(r,**{key:99}),'contact_feedback'))
        self.assertFalse(worker_passed(dict(r,feedback_checks_passed=False),'contact_feedback'))
