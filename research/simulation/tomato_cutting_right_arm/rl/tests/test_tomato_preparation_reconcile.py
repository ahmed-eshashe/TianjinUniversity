import unittest,tempfile,json,datetime as dt,hashlib
from pathlib import Path
from tomato_preparation_reconcile import inspect_active
from tomato_preparation_runner import sha
class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.r=Path(self.t.name);(self.r/'rl').mkdir();(self.r/'rl/tomato_preparation_runner.py').write_text('fixture runner')
        self.e=self.r/'evidence';self.e.mkdir();self.now=dt.datetime(2026,10,27,20,tzinfo=dt.timezone.utc);self.q={'checked_utc':self.now.isoformat(),'windows':[{'usedPercent':19}]}
        snapshot={'rl/tomato_preparation_runner.py':sha(self.r/'rl/tomato_preparation_runner.py')};h=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
        self.p=self.e/'result.json';active={'result_path':str(self.p),'label':'a','id':'integrity','runner_sha256':snapshot['rl/tomato_preparation_runner.py'],'source_snapshot_sha256':h,'quota_before_receipt_sha256':'before'}
        (self.e/'session.json').write_text(json.dumps({'active_task':active}))
        self.report={'label':'a','group':'integrity','runner_sha256':active['runner_sha256'],'source_snapshot':snapshot,'source_snapshot_sha256':h,'quota_before_receipt_sha256':'before','started_utc':self.now.isoformat(),'passed':True,'native_runtime_validated':False,'forbidden_imports':[]}
    def check(self):return inspect_active(self.r,self.e,fresh_quota=self.q,now=self.now)
    def write(self):self.p.write_text(json.dumps(self.report))
    def test_missing_preserved(self):self.assertEqual(self.check()['status'],'missing_result_preserve_active')
    def test_partial_preserved(self):self.p.write_text('{');self.assertEqual(self.check()['status'],'partial_result_preserve_active')
    def test_passed_no_automatic_clear(self):
        self.write();before=(self.e/'session.json').read_bytes();r=self.check();self.assertFalse(r['rerun_authorized']);self.assertEqual(before,(self.e/'session.json').read_bytes())
    def test_failed_requires_review(self):self.report['passed']=False;self.write();self.assertEqual(self.check()['status'],'failed_result_review_required')
    def test_changed_source_refused(self):
        self.write();(self.r/'rl/tomato_preparation_runner.py').write_text('changed')
        with self.assertRaises(ValueError):self.check()
    def test_before_receipt_mismatch_refused(self):
        self.report['quota_before_receipt_sha256']='other';self.write()
        with self.assertRaises(ValueError):self.check()
    def test_quota_threshold_preserves_state(self):
        self.write();self.q['windows'][0]['usedPercent']=45
        with self.assertRaises(ValueError):self.check()
