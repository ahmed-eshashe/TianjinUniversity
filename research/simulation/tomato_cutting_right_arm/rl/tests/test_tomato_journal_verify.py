import unittest,tempfile,json,hashlib
from pathlib import Path
from tomato_coupon_segment import SegmentJournal
from tomato_journal_verify import reconcile,allocated_history_candidates

class JournalVerifyTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.j=SegmentJournal(Path(self.t.name)/'segment',run_id='r',episode_id='e',source_sha256={'x':'a'*64})
        self.identity=hashlib.sha256((self.j.root/'identity.json').read_bytes()).hexdigest()
    def verify(self,**kw):return reconcile(self.j.root,expected_identity_sha256=self.identity,**kw)
    def test_valid_anchored_chain(self):
        h=self.j.commit({'step':0});self.j.checkpoint({'x':[1]});r=self.verify(expected_last_record_sha256=h)
        self.assertTrue(r['external_tail_anchor_matches_prefix']);self.assertFalse(r['resume_authorized']);self.assertFalse(r['native_state_recovered'])
    def test_truncated_tail_preserves_prefix(self):
        h=self.j.commit({'step':0});p=self.j.root/'step000001.json';p.write_text('{')
        r=self.verify(expected_last_record_sha256=h);self.assertEqual(r['structurally_consistent_prefix_steps'],1);self.assertEqual(r['issue'],'invalid_or_partial_record');self.assertEqual(p.read_text(),'{')
    def test_unanchored_tail_not_authenticated(self):
        self.j.commit({'step':0});self.assertFalse(self.verify()['external_tail_anchor_matches_prefix'])
    def test_tail_tamper_external_anchor_catches(self):
        h=self.j.commit({'step':0});p=self.j.root/'step000000.json';row=json.loads(p.read_text());row['diagnostic']['changed']=True;p.write_text(json.dumps(row))
        self.assertEqual(self.verify(expected_last_record_sha256=h)['issue'],'external_tail_anchor_mismatch')
    def test_gap(self):
        self.j.commit({'step':0});self.j.commit({'step':1});(self.j.root/'step000000.json').unlink();self.assertEqual(self.verify()['issue'],'missing_or_misnamed_step')
    def test_spliced_episode(self):
        self.j.commit({'step':0});p=self.j.root/'step000000.json';row=json.loads(p.read_text());row['episode_id']='old';p.write_text(json.dumps(row));self.assertEqual(self.verify()['structurally_consistent_prefix_steps'],0)
    def test_checkpoint_false_complete_refused(self):
        self.j.checkpoint({});p=self.j.root/'checkpoint000000.json';row=json.loads(p.read_text());row['restart_supported']=True;p.write_text(json.dumps(row));self.assertEqual(self.verify()['issue'],'invalid_or_partial_checkpoint')
    def test_nonfinite_json(self):
        (self.j.root/'step000000.json').write_text('{"x":NaN}');self.assertIsNotNone(self.verify()['issue'])
    def test_ast_candidate_scope(self):
        r=allocated_history_candidates('class S:\n def f(self):\n  self.history=wp.zeros(3)\n  self.alias=self.history\n')
        self.assertIn('history',r['candidate_attributes']);self.assertNotIn('alias',r['candidate_attributes']);self.assertFalse(r['registry_complete'])
