import unittest,tempfile,json
from pathlib import Path
from tomato_readiness_gates import *
class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.r=Path(self.t.name)
        (self.r/'source.py').write_text('# fixture');(self.r/'config.json').write_text('{}')
    def manifest_with_report(self,origin='native_recording',evidence_class='runtime_measurement'):
        m=draft_manifest();p=self.r/'report.json'
        report={'gate':'resources','outcome':'passed','origin':origin,'evidence_class':evidence_class,
            'run_id':'fixture','source_sha256':{'source.py':digest(self.r/'source.py')},'config_ref':{'path':'config.json','sha256':digest(self.r/'config.json')},'independent_review_status':'pending'}
        p.write_text(json.dumps(report));m['gates'][0].update(status='passed',evidence={'path':'report.json','sha256':digest(p)});return m
    def test_current_all_pending(self):self.assertEqual(assess(self.r,draft_manifest())['next_runtime_gate'],'resources')
    def test_offline_pass_cannot_qualify(self):
        r=assess(self.r,self.manifest_with_report(evidence_class='offline_test'));self.assertEqual(r['reference_consistent_runtime_candidates'],[])
    def test_synthetic_pass_cannot_qualify(self):self.assertEqual(assess(self.r,self.manifest_with_report(origin='synthetic_fixture'))['reference_consistent_runtime_candidates'],[])
    def test_candidate_never_authorization(self):
        r=assess(self.r,self.manifest_with_report());self.assertFalse(r['native_execution_authorized']);self.assertFalse(r['training_authorized']);self.assertEqual(r['next_runtime_gate'],'native_startup')
    def test_dependencies_cannot_skip(self):
        m=draft_manifest();m['gates'][1]['status']='passed';r=assess(self.r,m);self.assertEqual(r['blocked'][1]['reason'],'earlier_gate_not_qualified')
    def test_source_changed(self):
        m=self.manifest_with_report();(self.r/'source.py').write_text('changed')
        with self.assertRaises(ValueError):assess(self.r,m)
    def test_configuration_changed(self):
        m=self.manifest_with_report();(self.r/'config.json').write_text('changed')
        with self.assertRaises(ValueError):assess(self.r,m)
    def test_dependency_edit_refused(self):
        m=draft_manifest();m['gates'][2]['prerequisites']=[]
        with self.assertRaises(ValueError):assess(self.r,m)
