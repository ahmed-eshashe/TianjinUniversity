import unittest
from tomato_blade_record_roundtrip_worker import selected_fixtures
from tomato_contact_snapshot import preview_buffers
from tomato_isaac_startup_guard import worker_passed


class BladeRecordRoundtripTests(unittest.TestCase):
    def test_fixed_audited_fixtures_preview_without_native_imports(self):
        cases=selected_fixtures();self.assertEqual([len(c['records']) for c in cases],[1,1,0])
        for c in cases:
            identity={'run_id':'test','episode_id':c['id'],'step':0,'start_s':0.,'dt_s':c['context']['dt_s'],
                      'source_sha256':{'source':'a'*64}}
            result=preview_buffers(c['records'],c['context'],identity,global_capacity=8,body_capacity=8,observed_dynamic_adjacency=[])['payload']
            self.assertEqual(result['soft_contact_count'],[len(c['records'])])
            self.assertTrue(all(p==-1 for p in result['arrays']['soft_contact_particle']))
            self.assertFalse(result['solver_launch_enabled'])

    def test_guard_exact_fixture_and_refusal_scope(self):
        result={'diagnostic_passed':True,'shutdown_requested':True,'blade_record_cases_completed':3,
                'published_selected_records':2,'refusal_controls_passed':16,'mechanical_steps':0,'force_evaluations':0}
        self.assertTrue(worker_passed(result,'blade_record_roundtrip'))
        for key,value in [('published_selected_records',3),('refusal_controls_passed',15),('mechanical_steps',1),('force_evaluations',1)]:
            self.assertFalse(worker_passed(dict(result,**{key:value}),'blade_record_roundtrip'))
        self.assertFalse(worker_passed(result,'contact_roundtrip'))


if __name__=='__main__':unittest.main()
