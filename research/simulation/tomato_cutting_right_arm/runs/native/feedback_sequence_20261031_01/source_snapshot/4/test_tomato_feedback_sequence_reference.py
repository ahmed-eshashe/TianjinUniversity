import unittest
from tomato_feedback_sequence_reference import reference,assess
from tomato_isaac_startup_guard import worker_passed

class SequenceReferenceTests(unittest.TestCase):
    def test_contact_exit_and_coast(self):
        b=dict(particle_z=.001,body_z=0.,particle_vz=0.,body_vz=0.)
        forced=clear=0
        for _ in range(16):
            r=reference(b,.01,.02,1750.,.002,1/1200);a={k:v for k,v in r.items() if k!='force_n'}
            check=assess(b,a,.01,.02,1750.,.002,1/1200,r['force_n'])
            self.assertLess(check['energy_identity_error_j'],1e-18)
            self.assertLess(abs(.01*a['particle_vz']+.02*a['body_vz']),1e-17)
            forced+=r['force_n']>0;clear+=r['force_n']==0;b=a
        self.assertGreater(forced,1);self.assertGreater(clear,3)
    def test_moving_clear_control(self):
        b=dict(particle_z=.003,body_z=0.,particle_vz=.2,body_vz=-.1)
        r=reference(b,.01,.02,1750.,.002,1/1200)
        self.assertEqual(r['force_n'],0.)
        self.assertAlmostEqual(r['body_z'],-.1/1200)
    def test_stale_reaction_refused(self):
        b=dict(particle_z=.003,body_z=0.,particle_vz=.2,body_vz=-.1)
        r=reference(b,.01,.02,1750.,.002,1/1200);a={k:v for k,v in r.items() if k!='force_n'}
        with self.assertRaises(ValueError):assess(b,a,.01,.02,1750.,.002,1/1200,1.)
    def test_bad_values_refused(self):
        b=dict(particle_z=.001,body_z=0.,particle_vz=0.,body_vz=0.)
        with self.assertRaises(ValueError):reference(b,.01,0.,1750.,.002,1/1200)
        with self.assertRaises(ValueError):reference(b,.01,.02,1750.,.002,1/1200,substeps=0)
    def test_exact_bounded_guard_contract(self):
        r=dict(shutdown_requested=True,diagnostic_passed=True,sequence_checks_passed=True,
            sequence_cases_completed=2,newton_steps=32,physx_steps=16,cleared_contact_coast_steps=8)
        self.assertTrue(worker_passed(r,'feedback_sequence'))
        for key,value in [('newton_steps',33),('physx_steps',17),('cleared_contact_coast_steps',0),('sequence_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(r,**{key:value}),'feedback_sequence'))
