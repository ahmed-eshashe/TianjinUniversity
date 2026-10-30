import unittest,tempfile,json,copy
from pathlib import Path
from tomato_evidence_bundle import *

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def write(self,name,data):
        p=self.root/name;p.write_text(json.dumps(data));return {'path':name,'sha256':digest(p)}
    def fixture(self):
        (self.root/'auditor.py').write_text('# fixture, not a native audit\n')
        trace={'origin':'synthetic_fixture','episode_id':'e','run_id':'r','stages':[{'stage':'rest','episode_id':'e','start_s':0.,'end_s':1.,'outcome':'completed'}]}
        tr=self.write('trace.json',trace);refs={}
        for kind in AUDITS:
            refs[kind]=self.write(kind+'.json',{'kind':kind,'stage':'rest','run_id':'r','episode_id':'e','trace_sha256':tr['sha256'],'auditor_source_path':'auditor.py','auditor_source_sha256':digest(self.root/'auditor.py'),'outcome':'passed'})
        return {'trace':tr,'source_sha256':{'auditor.py':digest(self.root/'auditor.py')},'audit_refs':{'rest':refs}}
    def test_integrity_is_not_runtime(self):
        r=verify_bundle(self.root,self.fixture());self.assertTrue(r['artifact_integrity_verified']);self.assertFalse(r['native_runtime_validated']);self.assertTrue(r['independent_algorithm_review_required'])
    def test_trace_tamper(self):
        b=self.fixture();(self.root/'trace.json').write_text('{}')
        with self.assertRaises(ValueError):verify_bundle(self.root,b)
    def test_audit_run_splice(self):
        b=self.fixture();a=json.loads((self.root/'contact.json').read_text());a['run_id']='old';b['audit_refs']['rest']['contact']=self.write('other.json',a)
        with self.assertRaises(ValueError):verify_bundle(self.root,b)
    def test_auditor_source_tamper(self):
        b=self.fixture();(self.root/'auditor.py').write_text('different')
        with self.assertRaises(ValueError):verify_bundle(self.root,b)
    def test_missing_audit(self):
        b=self.fixture();del b['audit_refs']['rest']['energy']
        with self.assertRaises(ValueError):verify_bundle(self.root,b)
    def samples(self):return [{'episode_id':'e','tick':i,'finite_state':True} for i in range(10,20)]
    def cover(self,s=None,**kw):
        return release_coverage(self.samples() if s is None else s,episode_id='e',start_tick=10,end_tick=20,tick_s=kw.get('tick_s',.1))
    def test_continuity_not_motion_claim(self):self.assertFalse(self.cover()['native_motion_validated'])
    def test_missing_sample(self):
        with self.assertRaises(ValueError):self.cover(self.samples()[:-1])
    def test_duplicate_tick(self):
        s=self.samples();s[5]['tick']=14
        with self.assertRaises(ValueError):self.cover(s)
    def test_release_splice(self):
        s=self.samples();s[5]['episode_id']='old'
        with self.assertRaises(ValueError):self.cover(s)
    def test_short_observation(self):
        with self.assertRaises(ValueError):self.cover(tick_s=.01)
    def test_nonfinite_state(self):
        s=self.samples();s[2]['finite_state']=False
        with self.assertRaises(ValueError):self.cover(s)
    def test_native_label_cannot_self_authenticate(self):
        b=self.fixture();t=json.loads((self.root/'trace.json').read_text());t['origin']='native_recording'
        b['trace']=self.write('native.json',t)
        # Existing audits bind the old exact trace, so relabeling is refused.
        with self.assertRaises(ValueError):verify_bundle(self.root,b)
