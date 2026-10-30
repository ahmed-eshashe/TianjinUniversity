import hashlib,json,tempfile,unittest
from pathlib import Path
from tomato_coupon_segment import SegmentJournal
from tomato_segment_collection import collect

class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.r=Path(self.tmp.name)
        self.j=SegmentJournal(self.r/'j',run_id='diagnostic',episode_id='same',source_sha256={'source':'hash'})
        self.tp=self.r/'trajectory.json';self.tp.write_text(json.dumps({'dt_s':.01,'stages':[['rest',.015],['indent',.985]]}))
    def row(self,i):
        d={'step':i,'start_s':i*.01,'dt_s':.01}
        d['endpoint_reaction_metadata']={**d,'temporal_semantics':'end_of_step_force_not_step_average','work_ledger_admissible':False}
        return d
    def call(self,**extra):
        h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        return collect(self.j.root,self.tp,identity_sha256=h(self.j.root/'identity.json'),trajectory_sha256=h(self.tp),**extra)
    def test_empty(self):self.assertEqual(self.call()['evaluator_records'],[])
    def test_short_rest(self):
        self.j.commit(self.row(0));a=self.call();self.assertEqual(a['intervals'][0]['coupon_stages_touched'],['rest']);self.assertFalse(a['native_runtime_validated']);self.assertFalse(a['work_ledger_admissible'])
    def test_straddle(self):
        self.j.commit(self.row(0));self.j.commit(self.row(1));self.assertTrue(self.call()['intervals'][1]['crosses_stage_boundary'])
    def test_bad_timing(self):
        d=self.row(0);d['start_s']=.1;self.j.commit(d)
        with self.assertRaises(ValueError):self.call()
    def test_work_upgrade_refused(self):
        d=self.row(0);d['endpoint_reaction_metadata']['work_ledger_admissible']=True;self.j.commit(d)
        with self.assertRaises(ValueError):self.call()
    def test_partial_prefix_never_stage(self):
        (self.j.root/'step000000.json').write_text('{');a=self.call();self.assertEqual(a['evaluator_records'],[]);self.assertEqual(a['intervals'],[])
    def test_bad_anchor(self):
        a=self.call(tail_sha256='wrong');self.assertEqual(a['intervals'],[]);self.assertIsNotNone(a['journal']['issue'])
    def test_twelve_steps_not_motion_completion(self):
        for i in range(12):self.j.commit(self.row(i))
        a=self.call();self.assertFalse(a['full_prescribed_trajectory_covered']);self.assertEqual(a['evaluator_records'],[])
