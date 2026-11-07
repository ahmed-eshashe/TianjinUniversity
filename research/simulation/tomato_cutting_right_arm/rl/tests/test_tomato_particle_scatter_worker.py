import unittest
from tomato_particle_scatter_worker import fixture_cases
from tomato_contact_snapshot import preview_buffers
from tomato_isaac_startup_guard import worker_passed


class ScatterFixtureTests(unittest.TestCase):
    def test_six_bounded_fixtures_and_all_support_types(self):
        cases=fixture_cases();self.assertEqual(len(cases),6)
        self.assertEqual([len(c['records']) for c in cases],[1,1,0,1,1,1])
        self.assertEqual({r['feature'] for c in cases for r in c['records']},{'particle','edge','face'})
        for c in cases:
            identity={'run_id':'test','episode_id':c['id'],'step':0,'start_s':0.,'dt_s':c['context']['dt_s'],
                      'source_sha256':{'source':'a'*64}}
            p=preview_buffers(c['records'],c['context'],identity,global_capacity=8,body_capacity=8,observed_dynamic_adjacency=[])['payload']
            self.assertEqual(p['particle_q_world_m'][-1],[2.,2.,2.])
            self.assertTrue(all(len(p['particle_q_world_m'])-1 not in corners for corners in p['arrays']['soft_contact_indices']))

    def test_guard_exact_scope_and_no_integration(self):
        r={'diagnostic_passed':True,'shutdown_requested':True,'particle_scatter_cases_completed':6,
           'particle_scatter_checks_passed':True,'point_force_evaluations':5,'assembly_kernel_launches':18,
           'force_evaluations':18,'mechanical_steps':0}
        self.assertTrue(worker_passed(r,'particle_scatter'))
        for key,value in [('force_evaluations',19),('assembly_kernel_launches',19),('mechanical_steps',1),('particle_scatter_checks_passed',False)]:
            self.assertFalse(worker_passed(dict(r,**{key:value}),'particle_scatter'))
        self.assertFalse(worker_passed(r,'blade_record_forces'))


if __name__=='__main__':unittest.main()
